# AG-FATIGA: Agente Predictor de Fatiga
# Analiza la fatiga acumulada utilizando razonamiento contextual con LLM

from backend.services.openai_service import analyze_with_llm
from backend.services.database import daily_states
from datetime import datetime
from pytz import timezone
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

    # 1.1. Obtener datos de contexto
    actividad_mental = estado_fisio.get("actividad_mental", "No especificada")
    estado_emocional = estado_fisio.get("estado_emocional", "Normal y estable")

    # 1.1. Calcular factores de altitud (CORREGIDO)
    if altitud > 4500:
        factor_altitud = 1.25  # +25% impacto muy alto
        nivel_altitud = "Muy alta"
    elif altitud > 4000:
        factor_altitud = 1.20  # +20% impacto alto
    elif altitud > 3500:
        factor_altitud = 1.15  # +15% impacto significativo
    elif altitud > 3000:
        factor_altitud = 1.10  # +10% impacto moderado
    elif altitud > 2500:
        factor_altitud = 1.05  # +5% impacto leve
    else:
        factor_altitud = 1.00  # Sin impacto

    # 1.2. Calcular factores de contexto
    # Factores de actividad mental
    if actividad_mental:
        actividad_mental_str = str(actividad_mental).lower()
        if "intensamente" in actividad_mental_str:
            factor_actividad = 1.20  # +20% impacto
        elif "trabajando" in actividad_mental_str:
            factor_actividad = 1.10  # +10% impacto
        elif "aprendiendo" in actividad_mental_str:
            factor_actividad = 1.15  # +15% impacto (aprendizaje requiere más energía)
        elif "tareas administrativas" in actividad_mental_str:
            factor_actividad = (
                1.05  # +5% impacto (tareas administrativas son menos demandante)
            )
        elif (
            "revisando material" in actividad_mental_str
            or "descansando mentalmente" in actividad_mental_str
        ):
            factor_actividad = 0.95  # -5% (revisar material es más descanso)
        else:
            factor_actividad = 1.00  # Normal
    else:
        factor_actividad = 1.00

    # Factores de estado emocional
    if estado_emocional:
        estado_emocional_str = str(estado_emocional).lower()
        if "muy motivado" in estado_emocional_str:
            factor_emocional = 1.20  # +20% (muy motivado puede generar sobrecarga)
        elif "desmotivado" in estado_emocional_str:
            factor_emocional = 1.15  # +15% (desmotivación reduce capacidad)
        elif "ansioso" in estado_emocional_str or "estresado" in estado_emocional_str:
            factor_emocional = 1.25  # +25% (estrés agota rendimiento)
        elif "un poco cansado" in estado_emocional_str:
            factor_emocional = 1.10  # +10% (cansa afecta rendimiento)
        else:
            factor_emocional = 1.00  # Normal y estable
    else:
        factor_emocional = 1.00  # Por defecto si no hay datos

    # Factor global combinado para IFA
    factor_global = factor_altitud * factor_actividad * factor_emocional

    # 1.1. Obtener datos históricos del usuario para análisis temporal
    from datetime import datetime, timedelta
    from pytz import timezone

    # Usar hora peruana para el inicio del día
    peru_tz = timezone("America/Lima")
    hoy_inicio_peru = datetime.now(peru_tz).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    hoy_inicio_utc = hoy_inicio_peru.astimezone(timezone("UTC"))

    historial_reciente = list(
        daily_states.find(
            {
                "user_id": user_id,
                "agent": "AG-FATIGA",
                "timestamp": {
                    "$gte": hoy_inicio_utc - timedelta(days=7)
                },  # Últimos7 días
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

    # 1.3. Calcular frecuencia de actualización de datos (usar hora peruana)
    peru_tz = timezone("America/Lima")
    ultima_actualizacion = datetime.now(peru_tz)
    if historial_reciente:
        timestamp_historial = historial_reciente[0].get(
            "timestamp", datetime.now(peru_tz)
        )
        # Convertir a hora peruana si está en UTC
        if hasattr(timestamp_historial, "astimezone"):
            ultima_actualizacion = timestamp_historial.astimezone(peru_tz)
        else:
            ultima_actualizacion = timestamp_historial

    # 2. Construir prompt estructurado para el LLM con alertas y temporizadores
    prompt = f"""Analiza el siguiente estado fisiológico de un usuario en altura y determina su nivel de fatiga, además de generar alertas y recomendaciones con tiempos específicos.

CONTEXTO DE ALTITUD Y FACTORES CRÍTICOS:
- Altitud actual: {altitud} metros sobre el nivel del mar
- {"⚠️ ALTURA EXTREMA (>3500m): +15% impacto en fatiga" if altitud > 3500 else "Altitud moderada (+5% impacto)"}
- {"🏔️ GRAN ALTITUD (>4000m): +20% impacto en fatiga" if altitud > 4000 else "Altitud alta (+10% impacto)"}
- {"🏔️ ALTURA EXTREMA (>4500m): +25% impacto en fatiga" if altitud > 4500 else "Altitud muy alta (+15% impacto)"}

ESTADO FISIOLÓGICO ACTUAL:
- Estado general: {estado}
- Hidratación: {indicadores.get("hidratacion_porcentaje", 0):.1f}% (consumió {indicadores.get("agua_consumida_ml", 0)} ml de {indicadores.get("agua_base_ml", 0)} ml recomendados)
- Sueño: {indicadores.get("sueno_porcentaje", 0):.1f}% (durmió {indicadores.get("horas_sueno", 0)} h de {indicadores.get("sueno_base_h", 0)} h recomendadas)
- Actividad física: {indicadores.get("actividad_minutos", 0)} minutos (mínimo recomendado: {indicadores.get("actividad_minima", 30)} min)
- Nivel de energía subjetivo: {indicadores.get("nivel_energia", 3)}/5

CONTEXTO DE PRODUCTIVIDAD:
- Actividad mental actual: {actividad_mental if actividad_mental else "No especificada"}
- Estado emocional: {estado_emocional if estado_emocional else "No especificado"}
- Tendencia de fatiga: {tendencia_fatiga}

HISTORIAL RECIENTE:
- Registros previos: {len(historial_reciente)} estados guardados
- Evolución: {"Mejorando" if len(historial_reciente) > 3 else "Estable" if len(historial_reciente) > 1 else "Insuficiente datos"}

INSTRUCCIONES:
Analiza estos datos y proporciona tu respuesta EXACTAMENTE en el siguiente formato JSON (sin markdown, solo JSON puro):

{{
  "nivel_fatiga": "Bajo|Medio|Alto",
  "ifa": <número entre 0 y 100>,
  "justificacion": "<explicación detallada en 2-3 oraciones que justifique el nivel de fatiga y el IFA, considerando el contexto de altitud y productividad>",
  "alertas": [
    {{
      "tipo": "hidratacion|descanso|actividad|energia|productividad",
      "prioridad": "alta|media|baja",
      "mensaje": "<mensaje específico y conciso para el usuario>",
      "tiempo_recomendado": "<en X horas/minutos, cada X horas, ahora>",
      "accion_sugerida": "<acción específica que debe tomar>"
    }}
  ],
  "productividad": {{
    "capacidad_actual": <porcentaje 0-100>,
    "horas_optimas_estudio": <número de horas recomendadas>,
    "mejor_horario_inicio": "<hora recomendada para empezar>",
    "intervalos_concentracion": <minutos de concentración óptima>,
    "tiempo_descanso_estudio": <minutos de descanso entre sesiones>,
    "productividad_relativa": "<Baja/Media/Alta según análisis>",
    "factor_altitud": "<factor numérico que impacta el rendimiento>",
    "estado_productivo": "<estado actual del usuario>"
  }},
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
    }},
    "energia": {{
      "nivel_actual": {indicadores.get("nivel_energia", 3)}/5,
      "estado": "bajo|normal|alto|agotado"
    }}
  }}
}}

CRITERIOS ESPECÍFICOS PARA CÁLCULO DE IFA:
- IFA BASE = ((nivel_energia_ponderado * 0.4) + (sueño_puntuacion * 0.3) + (hidratacion_puntuacion * 0.3)) * factor_altitud
- Nivel energía ponderado: (5 - nivel_energia) / 5 * 100
- Sueño puntuación: (horas_sueno / sueno_base_h) * 100, max 100
- Hidratación puntuación: (agua_consumida_ml / agua_base_ml) * 100, max 100
- Factor altitud: 1.15 si altitud < 3500m, 1.25 si 3500-4000m, 1.35 si altitud > 4000m
- FACTORES ADICIONALES PARA PRODUCTIVIDAD:
  * Estudio intensivo: -15% capacidad productiva
  * Estrés/ansiedad: -20% capacidad productiva
  * Energía baja (1-2): -30% capacidad productiva
  * Estados negativos compuestos: hasta -40% capacidad productiva
- IFA > 60: Reducción progresiva de capacidad (5-IFA)% 

FÓRMULAS DE CÁLCULO:
- IFA_ajustado = IFA_BASE + factores_adicionales
- Capacidad_productiva = (100 - IFA_ajustado) * (1 - reduccion_actividad_mental)
- Si IFA_ajustado > 100, se limita a 100
- Si capacidad_productiva < 0, se establece en 10%
- alertas prioritarias si IFA > 60 o capacidad_productiva < 40%
- INCLUYE ANÁLISIS DE HORARIOS ÓPTIMOS para estudio/trabajo según el estado actual
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

        # Extraer productividad si existe
        productividad = analisis.get("productividad", {})

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

        # Validar y completar productividad si viene vacía
        if not productividad:
            # Calcular capacidad productiva basada en factores
            energia = indicadores.get("nivel_energia", 3)
            sueño_pct = indicadores.get("sueno_porcentaje", 100)
            hidratacion_pct = indicadores.get("hidratacion_porcentaje", 100)

            # Fórmula de productividad considerando altitud
            factor_altitud = 0.85 if altitud > 3500 else 0.95  # Reducción por altitud
            productividad_capacidad = (
                (
                    (energia / 5) * 0.4  # 40% peso a energía
                    + (sueño_pct / 100) * 0.3  # 30% peso a sueño
                    + (hidratacion_pct / 100) * 0.3  # 30% peso a hidratación
                )
                * factor_altitud
                * 100
            )

            # Determinar horas óptimas de estudio
            if productividad_capacidad > 80:
                horas_estudio = 6
                mejor_horario = "09:00 - 12:00 y 14:00 - 17:00"
                intervalo = 50
                descanso = 10
                productividad_rel = "Alta"
            elif productividad_capacidad > 60:
                horas_estudio = 4
                mejor_horario = "10:00 - 12:00 y 15:00 - 17:00"
                intervalo = 35
                descanso = 15
                productividad_rel = "Media"
            else:
                horas_estudio = 2
                mejor_horario = "10:00 - 12:00"
                intervalo = 25
                descanso = 20
                productividad_rel = "Baja"

            productividad = {
                "capacidad_actual": round(productividad_capacidad, 1),
                "horas_optimas_estudio": horas_estudio,
                "mejor_horario_inicio": mejor_horario,
                "intervalos_concentracion": intervalo,
                "tiempo_descanso_estudio": descanso,
                "productividad_relativa": productividad_rel,
            }

        # Validar alertas si vienen vacías
        if not alertas:
            alertas = []
            agua_consumida = indicadores.get("agua_consumida_ml", 0)
            agua_base = indicadores.get("agua_base_ml", 2000)

            # Altitud-specific hydration alerts
            if agua_consumida < agua_base * 0.8:
                if altitud > 4000:
                    mensaje = f"⚠️ ALTURA EXTREMA ({altitud}m): Hidratación crítica - bebe más agua para evitar el mal de altura"
                    prioridad = "alta"
                    accion = f"Bebe {min(300, agua_base - agua_consumida)}ml de agua inmediatamente"
                    tiempo = "Ahora mismo (cada 2 horas)"
                elif altitud > 3500:
                    mensaje = f"🏔️ GRAN ALTITUD ({altitud}m): Aumenta tu consumo de agua para adaptarte a la altura"
                    prioridad = "media" if agua_consumida < agua_base * 0.6 else "baja"
                    accion = f"Bebe {min(250, agua_base - agua_consumida)}ml de agua"
                    tiempo = "En los próximos 30 minutos"
                else:
                    mensaje = "Necesitas beber más agua para mantenerte hidratado"
                    prioridad = "media" if agua_consumida < agua_base * 0.5 else "baja"
                    accion = f"Bebe {min(200, agua_base - agua_consumida)}ml de agua"
                    tiempo = "Cuando puedas"

                alertas.append(
                    {
                        "tipo": "hidratacion",
                        "prioridad": prioridad,
                        "mensaje": mensaje,
                        "tiempo_recomendado": tiempo,
                        "accion_sugerida": accion,
                    }
                )

            # Altitud-specific energy alerts
            energia = indicadores.get("nivel_energia", 3)
            if energia <= 2:
                if altitud > 4000:
                    alertas.append(
                        {
                            "tipo": "energia",
                            "prioridad": "alta",
                            "mensaje": f"🚨 ALERTA DE ALTURA: Tu nivel de energía ({energia}/5) es peligroso bajo a {altitud}m",
                            "tiempo_recomendado": "Inmediatamente - descanso obligatorio",
                            "accion_sugerida": "Descansa 20-30 minutos, respira profundamente y considera bajar de altitud",
                        }
                    )
                elif altitud > 3500:
                    alertas.append(
                        {
                            "tipo": "energia",
                            "prioridad": "media",
                            "mensaje": f"⚡ Baja energía ({energia}/5) a {altitud}m - riesgo de fatiga por altura",
                            "tiempo_recomendado": "Cada 1-2 horas",
                            "accion_sugerida": "Toma pausas cortas de 10 minutos con ejercicios de respiración",
                        }
                    )

            # Altitud-specific productivity alerts
            if actividad_mental and "intensamente" in actividad_mental.lower():
                if altitud > 4000:
                    alertas.append(
                        {
                            "tipo": "productividad",
                            "prioridad": "media",
                            "mensaje": f"🧠 REDUCE INTENSIDAD: Estudio intensivo a {altitud}m puede acelerar la fatiga",
                            "tiempo_recomendado": "Cada 25 minutos (técnica Pomodoro)",
                            "accion_sugerida": "Alternan 25 min estudio con 5 min descanso activo",
                        }
                    )
                elif altitud > 3500:
                    alertas.append(
                        {
                            "tipo": "productividad",
                            "prioridad": "baja",
                            "mensaje": f"💡 AJUSTA RITMO: A {altitud}m tu cerebro trabaja un 15% más lento",
                            "tiempo_recomendado": "Cada 45 minutos",
                            "accion_sugerida": "Reduce sesión a 45 min con 10 min descanso",
                        }
                    )

    except Exception as e:
        # Fallback en caso de error del LLM
        print(f"Error al procesar respuesta del LLM: {e}")
        nivel_fatiga = "Medio"
        ifa = min(100, 45 + (factor_global - 1.0) * 20)  # IFA basado en factor_global
        justificacion = f"Error en el análisis automático. Estado fisiológico: {estado} (Factor altitud: {factor_global:.2f})"

        # Generar alertas, contadores y productividad básicos en fallback
        agua_consumida = indicadores.get("agua_consumida_ml", 0)
        agua_base = indicadores.get("agua_base_ml", 2000)
        actividad_realizada = indicadores.get("actividad_minutos", 0)
        actividad_minima = indicadores.get("actividad_minima", 30)
        energia = indicadores.get("nivel_energia", 3)

        alertas = []

        # Altitud-specific hydration alerts en fallback
        if agua_consumida < agua_base * 0.8:
            if altitud > 4000:
                mensaje = f"🚨 CRÍTICO ({altitud}m): Hidratación insufiente para altitud extrema"
                prioridad = "alta"
            elif altitud > 3500:
                mensaje = (
                    f"⚠️ ALTURA ({altitud}m): Aumenta consumo de agua por la altitud"
                )
                prioridad = "media"
            else:
                mensaje = "Necesitas beber más agua para mantenerte hidratado"
                prioridad = "media"

            alertas.append(
                {
                    "tipo": "hidratacion",
                    "prioridad": prioridad,
                    "mensaje": mensaje,
                    "tiempo_recomendado": "Ahora mismo",
                    "accion_sugerida": f"Bebe {min(250, agua_base - agua_consumida)}ml de agua",
                }
            )

        # Altitud-specific energy alerts en fallback
        if energia <= 2:
            if altitud > 4000:
                alertas.append(
                    {
                        "tipo": "energia",
                        "prioridad": "alta",
                        "mensaje": f"🚨 PELIGRO: Energía crítica ({energia}/5) a {altitud}m - riesgo de mal de altura",
                        "tiempo_recomendado": "Inmediato",
                        "accion_sugerida": "Descansar y considerar descender a menor altitud",
                    }
                )
            elif altitud > 3500:
                alertas.append(
                    {
                        "tipo": "energia",
                        "prioridad": "media",
                        "mensaje": f"⚡ Baja energía ({energia}/5) a {altitud}m - fatiga por altura",
                        "tiempo_recomendado": "Cada 2 horas",
                        "accion_sugerida": "Tomar pausas frecuentes con respiración profunda",
                    }
                )

        # Productividad fallback
        productividad_capacidad = (energia / 5) * 70  # Estimación conservadora
        horas_estudio = 4 if productividad_capacidad > 50 else 2

        productividad = {
            "capacidad_actual": productividad_capacidad,
            "horas_optimas_estudio": horas_estudio,
            "mejor_horario_inicio": "10:00 - 12:00 y 15:00 - 17:00",
            "intervalos_concentracion": 30,
            "tiempo_descanso_estudio": 15,
            "productividad_relativa": "Media"
            if productividad_capacidad > 50
            else "Baja",
        }

        # Generar alertas, contadores y productividad básicos en fallback
        agua_consumida = indicadores.get("agua_consumida_ml", 0)
        agua_base = indicadores.get("agua_base_ml", 2000)
        actividad_realizada = indicadores.get("actividad_minutos", 0)
        actividad_minima = indicadores.get("actividad_minima", 30)
        energia = indicadores.get("nivel_energia", 3)

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

        # Productividad fallback
        productividad_capacidad = (energia / 5) * 70  # Estimación conservadora
        horas_estudio = 4 if productividad_capacidad > 50 else 2

        productividad = {
            "capacidad_actual": productividad_capacidad,
            "horas_optimas_estudio": horas_estudio,
            "mejor_horario_inicio": "10:00 - 12:00 y 15:00 - 17:00",
            "intervalos_concentracion": 30,
            "tiempo_descanso_estudio": 15,
            "productividad_relativa": "Media"
            if productividad_capacidad > 50
            else "Baja",
        }

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

        # Validar y completar productividad si viene vacía
        if not productividad:
            # Calcular capacidad productiva basada en factores
            energia = indicadores.get("nivel_energia", 3)
            sueño_pct = indicadores.get("sueno_porcentaje", 100)
            hidratacion_pct = indicadores.get("hidratacion_porcentaje", 100)

            # Fórmula de productividad considerando altitud
            factor_altitud = 0.85 if altitud > 3500 else 0.95  # Reducción por altitud
            productividad_capacidad = (
                (
                    (energia / 5) * 0.4  # 40% peso a energía
                    + (sueño_pct / 100) * 0.3  # 30% peso a sueño
                    + (hidratacion_pct / 100) * 0.3  # 30% peso a hidratación
                )
                * factor_altitud
                * 100
            )

            # Determinar horas óptimas de estudio
            if productividad_capacidad > 80:
                horas_estudio = 6
                mejor_horario = "09:00 - 12:00 y 14:00 - 17:00"
                intervalo = 50
                descanso = 10
                productividad_rel = "Alta"
            elif productividad_capacidad > 60:
                horas_estudio = 4
                mejor_horario = "10:00 - 12:00 y 15:00 - 17:00"
                intervalo = 35
                descanso = 15
                productividad_rel = "Media"
            else:
                horas_estudio = 2
                mejor_horario = "10:00 - 12:00"
                intervalo = 25
                descanso = 20
                productividad_rel = "Baja"

            productividad = {
                "capacidad_actual": round(productividad_capacidad, 1),
                "horas_optimas_estudio": horas_estudio,
                "mejor_horario_inicio": mejor_horario,
                "intervalos_concentracion": intervalo,
                "tiempo_descanso_estudio": descanso,
                "productividad_relativa": productividad_rel,
            }

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

    # 5. Crear resultado del análisis con alertas, contadores y productividad
    resultado_fatiga = {
        "user_id": user_id,
        "timestamp": datetime.now(timezone("America/Lima")),
        "nivel_fatiga": nivel_fatiga,
        "ifa": ifa,
        "justificacion": justificacion,
        "alertas": alertas,
        "productividad": productividad,
        "contadores": contadores,
        "tendencia_fatiga": tendencia_fatiga,
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
