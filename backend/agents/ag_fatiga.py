# AG-FATIGA: Agente Predictor de Fatiga
# Analiza la fatiga acumulada utilizando razonamiento contextual con LLM

from backend.services.openai_service import analyze_with_llm
from backend.services.database import daily_states
from datetime import datetime
import json
import re


def run_ag_fatiga(
    user_id: str,
    estado_fisio: dict,
    actividad_mental: str | None = None,
    estado_emocional: str | None = None,
) -> dict:
    """
    AG-FATIGA: Agente con LLM que analiza fatiga acumulada y genera alertas

    Entradas:
    - user_id: ID del usuario
    - estado_fisio: Output de AG-FISIO (estado fisiológico)
    - actividad_mental: Descripción de actividad mental (estudio/trabajo) - opcional
    - estado_emocional: Estado emocional del usuario - opcional

    Salidas:
    - Nivel de fatiga (Bajo / Medio / Alto)
    - Índice de Fatiga en Altura (IFA 0-100)
    - Justificación textual del análisis
    - Alertas activas con tiempos recomendados
    - Contadores de hidratación, descanso y actividad
    """

    # 1. Extraer datos relevantes del estado fisiológico
    indicadores = estado_fisio.get("indicadores", {})
    alertas = estado_fisio.get("alertas", [])
    estado = estado_fisio.get("estado", "DESCONOCIDO")
    altitud = indicadores.get("altitud", 0)

    # 1.1. Obtener datos históricos del usuario para análisis temporal
    from datetime import datetime, timedelta

    hoy_inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    historial_reciente = list(
        daily_states.find(
            {
                "user_id": user_id,
                "agent": "AG-FATIGA",
                "timestamp": {"$gte": hoy_inicio - timedelta(days=7)},  # Últimos 7 días
            }
        )
        .sort("timestamp", -1)
        .limit(10)
    )

    # 1.2. Analizar tendencia de fatiga
    tendencia_fatiga = "Estable"
    if len(historial_reciente) >= 2:
        ifa_recientes = [h.get("ifa", 50) for h in historial_reciente[:3]]
        if len(ifa_recientes) >= 2:
            if ifa_recientes[0] > ifa_recientes[-1] + 10:
                tendencia_fatiga = "Empeorando"
            elif ifa_recientes[0] < ifa_recientes[-1] - 10:
                tendencia_fatiga = "Mejorando"

    # 1.3. Calcular frecuencia de actualización de datos
    ultima_actualizacion = datetime.utcnow()
    if historial_reciente:
        ultima_actualizacion = historial_reciente[0].get("timestamp", datetime.utcnow())

    # 2. Construir prompt estructurado para el LLM con alertas y temporizadores
    prompt = f"""Analiza el siguiente estado fisiológico de un usuario en altura y determina su nivel de fatiga, además de generar alertas y recomendaciones con tiempos específicos.

CONTEXTO DE ALTITUD:
- Altitud actual: {altitud} metros sobre el nivel del mar
- {"⚠️ ALTURA EXTREMA (>3500m): Mayor sensibilidad a deshidratación y déficit de sueño" if altitud > 3500 else "Altitud moderada"}

ESTADO FISIOLÓGICO ACTUAL:
- Estado general: {estado}
- Hidratación: {indicadores.get("hidratacion_porcentaje", 0):.1f}% (consumió {indicadores.get("agua_consumida_ml", 0)} ml de {indicadores.get("agua_base_ml", 0)} ml recomendados)
- Sueño: {indicadores.get("sueno_porcentaje", 0):.1f}% (durmió {indicadores.get("horas_sueno", 0)} h de {indicadores.get("sueno_base_h", 0)} h recomendadas)
- Actividad física: {indicadores.get("actividad_minutos", 0)} minutos (mínimo recomendado: {indicadores.get("actividad_minima", 30)} min)
- Nivel de energía subjetivo: {indicadores.get("nivel_energia", 3)}/5

HISTORIAL Y TENDENCIAS:
- Tendencia de fatiga: {tendencia_fatiga}
- Análisis de últimos días: {len(historial_reciente)} registros disponibles
- Última actualización: {ultima_actualizacion.strftime("%Y-%m-%d %H:%M") if historial_reciente else "Primera vez"}

ALERTAS ACTIVAS:
{chr(10).join(f"- {alerta}" for alerta in alertas) if alertas else "- Sin alertas"}

INFORMACIÓN ADICIONAL:
- Actividad mental: {actividad_mental if actividad_mental else "No especificada"}
- Estado emocional: {estado_emocional if estado_emocional else "No especificado"}

INSTRUCCIONES:
Analiza estos datos y proporciona tu respuesta EXACTAMENTE en el siguiente formato JSON (sin markdown, solo JSON puro):

{{
  "nivel_fatiga": "Bajo|Medio|Alto",
  "ifa": <número entre 0 y 100>,
  "justificacion": "<explicación detallada en 2-3 oraciones que justifique el nivel de fatiga y el IFA, considerando el contexto de altitud>",
  "alertas": [
    {{
      "tipo": "hidratacion|descanso|actividad|energia",
      "prioridad": "alta|media|baja",
      "mensaje": "<mensaje específico y conciso para el usuario>",
      "tiempo_recomendado": "<en X horas/minutos, cada X horas, ahora>",
      "accion_sugerida": "<acción específica que debe tomar>"
    }}
  ],
  "contadores": {{
    "hidratacion": {{
      "consumido_ml": {indicadores.get("agua_consumida_ml", 0)},
      "objetivo_ml": {indicadores.get("agua_base_ml", 0)},
      "faltante_ml": <calculado>,
      "siguiente_toma_ml": <cantidad recomendada>,
      "frecuencia_horas": <frecuencia recomendada>
    }},
    "descanso": {{
      "ultimo_descanso_hace": "<tiempo desde último descanso>",
      "proxima_pausa_en": "<cuándo debería tomar la próxima pausa>",
      "duracion_recomendada_min": <minutos de descanso recomendados>
    }},
    "actividad": {{
      "realizado_min": {indicadores.get("actividad_minutos", 0)},
      "objetivo_min": {indicadores.get("actividad_minima", 30)},
      "faltante_min": <calculado>,
      "proxima_sesion_en": "<cuándo debería hacer actividad física>"
    }}
  }}
}}

CRITERIOS:
- IFA 0-33: Fatiga Baja
- IFA 34-66: Fatiga Media
- IFA 67-100: Fatiga Alta
- Considera que en altura (>3500m) los efectos de deshidratación y falta de sueño se amplifican
- Genera alertas específicas basadas en los déficits actuales y tendencias
- Para hidratación: recomienda tomas cada 1-2 horas en altura
- Para descanso: recomienda pausas cada 2 horas de trabajo
- Para actividad: recomienda ejercicio ligero si IFA es bajo, descanso si IFA es alto
- Los tiempos deben ser específicos y accionables
- CONSIDERA LA TENDENCIA: Si está empeorando, genera alertas más urgentes
- Si la tendencia es estable o mejorando, ajusta la prioridad de las alertas
- GENERA AL MENOS 2 ALERTAS ESPECÍFICAS basadas en los datos actuales
"""

    # 3. Llamar al LLM
    try:
        respuesta_llm = analyze_with_llm(
            prompt, temperature=0.3
        )  # Baja temperatura para consistencia

        # 4. Parsear la respuesta JSON
        # Limpiar markdown si existe
        respuesta_limpia = respuesta_llm.strip()
        if respuesta_limpia.startswith("```"):
            respuesta_limpia = re.sub(r"^```json?\s*", "", respuesta_limpia)
            respuesta_limpia = re.sub(r"\s*```$", "", respuesta_limpia)

        analisis = json.loads(respuesta_limpia)

        # Validar campos requeridos
        nivel_fatiga = analisis.get("nivel_fatiga", "Medio")
        ifa = int(analisis.get("ifa", 50))
        justificacion = analisis.get("justificacion", "Análisis no disponible")
        alertas = analisis.get("alertas", [])
        contadores = analisis.get("contadores", {})

        # Validar rangos
        if nivel_fatiga not in ["Bajo", "Medio", "Alto"]:
            nivel_fatiga = "Medio"
        if not (0 <= ifa <= 100):
            ifa = max(0, min(100, ifa))

        # Validar y completar contadores si vienen vacíos
        if not contadores:
            agua_consumida = indicadores.get("agua_consumida_ml", 0)
            agua_base = indicadores.get("agua_base_ml", 2000)
            actividad_realizada = indicadores.get("actividad_minutos", 0)
            actividad_minima = indicadores.get("actividad_minima", 30)

            contadores = {
                "hidratacion": {
                    "consumido_ml": agua_consumida,
                    "objetivo_ml": agua_base,
                    "faltante_ml": max(0, agua_base - agua_consumida),
                    "siguiente_toma_ml": 250,
                    "frecuencia_horas": 2,
                },
                "descanso": {
                    "ultimo_descanso_hace": "Desconocido",
                    "proxima_pausa_en": "Cada 2 horas",
                    "duracion_recomendada_min": 15,
                },
                "actividad": {
                    "realizado_min": actividad_realizada,
                    "objetivo_min": actividad_minima,
                    "faltante_min": max(0, actividad_minima - actividad_realizada),
                    "proxima_sesion_en": "Hoy"
                    if actividad_realizada < actividad_minima
                    else "Mañana",
                },
            }

        # Validar alertas si vienen vacías
        if not alertas:
            alertas = []
            agua_consumida = indicadores.get("agua_consumida_ml", 0)
            agua_base = indicadores.get("agua_base_ml", 2000)

            if agua_consumida < agua_base * 0.8:
                alertas.append(
                    {
                        "tipo": "hidratacion",
                        "prioridad": "alta"
                        if agua_consumida < agua_base * 0.5
                        else "media",
                        "mensaje": "Necesitas beber más agua para mantenerte hidratado en altura",
                        "tiempo_recomendado": "Ahora mismo",
                        "accion_sugerida": f"Bebe {min(250, agua_base - agua_consumida)}ml de agua",
                    }
                )

    except Exception as e:
        # Fallback en caso de error del LLM
        print(f"Error al procesar respuesta del LLM: {e}")
        nivel_fatiga = "Medio"
        ifa = 50
        justificacion = f"Error en el análisis automático. Estado fisiológico: {estado}"

        # Generar alertas y contadores básicos en fallback
        agua_consumida = indicadores.get("agua_consumida_ml", 0)
        agua_base = indicadores.get("agua_base_ml", 2000)
        actividad_realizada = indicadores.get("actividad_minutos", 0)
        actividad_minima = indicadores.get("actividad_minima", 30)

        alertas = []
        if agua_consumida < agua_base * 0.8:
            alertas.append(
                {
                    "tipo": "hidratacion",
                    "prioridad": "alta"
                    if agua_consumida < agua_base * 0.5
                    else "media",
                    "mensaje": "Necesitas beber más agua para mantenerte hidratado en altura",
                    "tiempo_recomendado": "Ahora mismo",
                    "accion_sugerida": f"Bebe {min(250, agua_base - agua_consumida)}ml de agua",
                }
            )

        contadores = {
            "hidratacion": {
                "consumido_ml": agua_consumida,
                "objetivo_ml": agua_base,
                "faltante_ml": max(0, agua_base - agua_consumida),
                "siguiente_toma_ml": 250,
                "frecuencia_horas": 2,
            },
            "descanso": {
                "ultimo_descanso_hace": "Desconocido",
                "proxima_pausa_en": "Cada 2 horas",
                "duracion_recomendada_min": 15,
            },
            "actividad": {
                "realizado_min": actividad_realizada,
                "objetivo_min": actividad_minima,
                "faltante_min": max(0, actividad_minima - actividad_realizada),
                "proxima_sesion_en": "Hoy"
                if actividad_realizada < actividad_minima
                else "Mañana",
            },
        }

    # 5. Crear resultado del análisis con alertas y contadores
    resultado_fatiga = {
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "nivel_fatiga": nivel_fatiga,
        "ifa": ifa,
        "justificacion": justificacion,
        "alertas": alertas,
        "contadores": contadores,
        "estado_fisio_referencia": {
            "estado": estado,
            "alertas_count": len(alertas),
            "altitud": altitud,
        },
        "actividad_mental": actividad_mental,
        "estado_emocional": estado_emocional,
        "agent": "AG-FATIGA",
    }

    # 6. Persistir en base de datos
    daily_states.insert_one(resultado_fatiga)

    return resultado_fatiga
