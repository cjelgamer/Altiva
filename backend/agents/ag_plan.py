# AG-PLAN: Agente Planificador de Recuperación
# Genera planes dinámicos de recuperación y productividad basados en el análisis de fatiga

from backend.services.openai_service import analyze_with_llm
from backend.services.database import daily_states, get_user_profile
from datetime import datetime
import json
import re


def run_ag_plan(
    user_id: str, analisis_fatiga: dict, historial_dia: list | None = None
) -> dict:
    """
    AG-PLAN: Agente con LLM que genera planes dinámicos de recuperación y productividad

    Entradas:
    - user_id: ID del usuario
    - analisis_fatiga: Output completo de AG-FATIGA (nivel_fatiga, ifa, justificacion)
    - historial_dia: Lista de estados previos del día (opcional)

    Salidas:
    - Plan estructurado con recomendaciones inmediatas, horarios óptimos, pausas activas y consejos por altitud
    - Persistido en daily_states
    """

    # 1. Validar datos de entrada
    if not analisis_fatiga:
        raise ValueError("Análisis de fatiga es requerido")

    # 2. Extraer datos relevantes del análisis de fatiga
    nivel_fatiga = analisis_fatiga.get("nivel_fatiga", "Medio")
    ifa = analisis_fatiga.get("ifa", 50)
    justificacion = analisis_fatiga.get("justificacion", "")

    # 3. Obtener perfil base del usuario para contexto de altitud
    profile = get_user_profile(user_id)
    if not profile:
        raise ValueError("Perfil de usuario no encontrado. Ejecuta AG-INICIAL primero.")

    altitud = profile.get("altitud", 0)
    agua_base_ml = profile.get("agua_base_ml", 3000)
    sueno_base_h = profile.get("sueno_base_h", 8)

    # 4. Obtener historial del día si no se proporciona
    if not historial_dia:
        historial_dia = list(
            daily_states.find(
                {
                    "user_id": user_id,
                    "timestamp": {
                        "$gte": datetime.utcnow().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        )
                    },
                }
            ).sort("timestamp", -1)
        )

    # 5. Extraer estado fisiológico más reciente del historial
    estado_fisio_reciente = None
    for estado in historial_dia:
        if estado.get("agent") == "AG-FISIO":
            estado_fisio_reciente = estado
            break

    # 6. Construir prompt estructurado para el LLM
    prompt = f"""Genera un plan de recuperación y productividad personalizado basado en el siguiente análisis:

CONTEXTO DEL USUARIO:
- Altitud actual: {altitud} metros sobre el nivel del mar
- {"⚠️ ALTURA EXTREMA (>3500m): Requiere cuidados especiales" if altitud > 3500 else "Altitud moderada"}
- Agua diaria base: {agua_base_ml} ml
- Sueño base recomendado: {sueno_base_h} horas

ANÁLISIS DE FATIGA ACTUAL:
- Nivel de fatiga: {nivel_fatiga}
- Índice de Fatiga en Altura (IFA): {ifa}/100
- Justificación: {justificacion}

ESTADO FISIOLÓGICO RECIENTE:
{f"- Estado general: {estado_fisio_reciente.get('estado', 'No disponible')}" if estado_fisio_reciente else "- Sin datos fisiológicos recientes"}
{f"- Hidratación: {estado_fisio_reciente.get('indicadores', {}).get('hidratacion_porcentaje', 0):.1f}%" if estado_fisio_reciente else ""}
{f"- Sueño: {estado_fisio_reciente.get('indicadores', {}).get('sueno_porcentaje', 0):.1f}%" if estado_fisio_reciente else ""}
{f"- Actividad: {estado_fisio_reciente.get('indicadores', {}).get('actividad_minutos', 0)} minutos" if estado_fisio_reciente else ""}
{f"- Nivel de energía: {estado_fisio_reciente.get('indicadores', {}).get('nivel_energia', 3)}/5" if estado_fisio_reciente else ""}
{f"- Alertas activas: {len(estado_fisio_reciente.get('alertas', []))}" if estado_fisio_reciente else ""}

HISTORIAL DEL DÍA:
- Registros previos: {len(historial_dia)} estados guardados
- Evolución: {"Mejorando" if len(historial_dia) > 3 else "Estable" if len(historial_dia) > 1 else "Insuficiente datos"}

INSTRUCCIONES:
Genera tu respuesta EXACTAMENTE en el siguiente formato JSON (sin markdown, solo JSON puro):

{{
  "recomendaciones_inmediatas": [
    "<recomendación 1 específica y accionable>",
    "<recomendación 2 específica y accionable>",
    "<recomendación 3 específica y accionable>"
  ],
  "horarios_optimos": {{
    "estudio": "<rango horario con justificación>",
    "trabajo": "<rango horario con justificación>",
    "descanso": "<rango horario con justificación>"
  }},
  "pausas_activas": [
    "<actividad 1 específica con duración>",
    "<actividad 2 específica con duración>",
    "<actividad 3 específica con duración>"
  ],
  "consejos_altitud": [
    "<consejo 1 específico para la altitud actual>",
    "<consejo 2 específico para la altitud actual>",
    "<consejo 3 específico para la altitud actual>"
  ]
}}

DIRECTRICES ESPECÍFICAS:
- Si IFA > 70 (Fatiga Alta): Priorizar descanso e hidratación inmediata
- Si IFA 34-66 (Fatiga Media): Balancear actividad con pausas frecuentes
- Si IFA < 34 (Fatiga Baja): Optimizar horarios de máxima productividad
- Si altitud > 3500m: Enfatizar hidratación y evitar esfuerzo extremo
- Las recomendaciones deben ser específicas, medibles y accionables
- Los horarios deben considerar el nivel de energía actual
- Incluir siempre consejos específicos para la altitud del usuario
"""

    # 7. Llamar al LLM
    try:
        respuesta_llm = analyze_with_llm(
            prompt, temperature=0.4
        )  # Temperatura moderada para creatividad controlada

        # 8. Parsear la respuesta JSON
        respuesta_limpia = respuesta_llm.strip()
        if respuesta_limpia.startswith("```"):
            respuesta_limpia = re.sub(r"^```json?\s*", "", respuesta_limpia)
            respuesta_limpia = re.sub(r"\s*```$", "", respuesta_limpia)

        plan = json.loads(respuesta_limpia)

        # Validar estructura básica
        claves_requeridas = [
            "recomendaciones_inmediatas",
            "horarios_optimos",
            "pausas_activas",
            "consejos_altitud",
        ]
        for clave in claves_requeridas:
            if clave not in plan:
                plan[clave] = []

    except Exception as e:
        # Fallback en caso de error del LLM
        print(f"Error al procesar respuesta del LLM: {e}")
        plan = {
            "recomendaciones_inmediatas": [
                f"Beber 500ml de agua en las próximas 2 horas (IFA: {ifa})",
                f"Tomar un descanso de 15 minutos para recuperar energía",
                "Monitorizar tus niveles de energía y fatiga",
            ],
            "horarios_optimos": {
                "estudio": "14:00-16:00 (mejor concentración después del descanso)",
                "trabajo": "09:00-11:00 (energía matutina estable)",
                "descanso": "12:00-13:00 y después de las 17:00",
            },
            "pausas_activas": [
                "Caminata de 5 minutos cada hora",
                "Ejercicios de respiración profunda (2 minutos)",
                "Estiramientos suaves de cuello y espalda (3 minutos)",
            ],
            "consejos_altitud": [
                f"Priorizar hidratación constante a {altitud}m de altitud",
                "Evitar esfuerzo intenso después de las 17:00 en altura",
                "Descansar adicional si sientes síntomas de soroche",
            ],
        }

    # 9. Crear resultado del plan
    resultado_plan = {
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "tipo": "plan_recuperacion",
        "ifa_referencia": ifa,
        "nivel_fatiga": nivel_fatiga,
        "justificacion_fatiga": justificacion,
        "altitud": altitud,
        "plan": plan,
        "metadata": {
            "historial_registros": len(historial_dia),
            "estado_fisio_disponible": estado_fisio_reciente is not None,
            "perfil_completo": profile is not None,
        },
        "agent": "AG-PLAN",
    }

    # 10. Persistir en base de datos
    daily_states.insert_one(resultado_plan)

    return resultado_plan
