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
    AG-FATIGA: Agente con LLM que analiza fatiga acumulada

    Entradas:
    - user_id: ID del usuario
    - estado_fisio: Output de AG-FISIO (estado fisiológico)
    - actividad_mental: Descripción de actividad mental (estudio/trabajo) - opcional
    - estado_emocional: Estado emocional del usuario - opcional

    Salidas:
    - Nivel de fatiga (Bajo / Medio / Alto)
    - Índice de Fatiga en Altura (IFA 0-100)
    - Justificación textual del análisis
    """

    # 1. Extraer datos relevantes del estado fisiológico
    indicadores = estado_fisio.get("indicadores", {})
    alertas = estado_fisio.get("alertas", [])
    estado = estado_fisio.get("estado", "DESCONOCIDO")
    altitud = indicadores.get("altitud", 0)

    # 2. Construir prompt estructurado para el LLM
    prompt = f"""Analiza el siguiente estado fisiológico de un usuario en altura y determina su nivel de fatiga.

CONTEXTO DE ALTITUD:
- Altitud actual: {altitud} metros sobre el nivel del mar
- {"⚠️ ALTURA EXTREMA (>3500m): Mayor sensibilidad a deshidratación y déficit de sueño" if altitud > 3500 else "Altitud moderada"}

ESTADO FISIOLÓGICO ACTUAL:
- Estado general: {estado}
- Hidratación: {indicadores.get("hidratacion_porcentaje", 0):.1f}% (consumió {indicadores.get("agua_consumida_ml", 0)} ml de {indicadores.get("agua_base_ml", 0)} ml recomendados)
- Sueño: {indicadores.get("sueno_porcentaje", 0):.1f}% (durmió {indicadores.get("horas_sueno", 0)} h de {indicadores.get("sueno_base_h", 0)} h recomendadas)
- Actividad física: {indicadores.get("actividad_minutos", 0)} minutos (mínimo recomendado: {indicadores.get("actividad_minima", 30)} min)
- Nivel de energía subjetivo: {indicadores.get("nivel_energia", 3)}/5

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
  "justificacion": "<explicación detallada en 2-3 oraciones que justifique el nivel de fatiga y el IFA, considerando el contexto de altitud>"
}}

CRITERIOS:
- IFA 0-33: Fatiga Baja
- IFA 34-66: Fatiga Media
- IFA 67-100: Fatiga Alta
- Considera que en altura (>3500m) los efectos de deshidratación y falta de sueño se amplifican
- Un estado CRÍTICO debe resultar en IFA alto (>70)
- Un estado ALERTA debe resultar en IFA medio-alto (50-75)
- Un estado BAJO debe resultar en IFA medio (40-60)
- Un estado NORMAL debe resultar en IFA bajo (<40)
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

        # Validar rangos
        if nivel_fatiga not in ["Bajo", "Medio", "Alto"]:
            nivel_fatiga = "Medio"
        if not (0 <= ifa <= 100):
            ifa = max(0, min(100, ifa))

    except Exception as e:
        # Fallback en caso de error del LLM
        print(f"Error al procesar respuesta del LLM: {e}")
        nivel_fatiga = "Medio"
        ifa = 50
        justificacion = f"Error en el análisis automático. Estado fisiológico: {estado}"

    # 5. Crear resultado del análisis
    resultado_fatiga = {
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "nivel_fatiga": nivel_fatiga,
        "ifa": ifa,
        "justificacion": justificacion,
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
