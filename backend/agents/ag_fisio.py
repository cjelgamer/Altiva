# AG-FISIO: Agente Fisiológico
# Monitorea el estado fisiológico del usuario de forma progresiva durante el día

from backend.services.database import daily_states, get_user_profile
from datetime import datetime


def run_ag_fisio(user_id: str, daily_data: dict) -> dict:
    """
    AG-FISIO: Agente determinístico que monitorea estado fisiológico

    Entradas:
    - user_id: ID del usuario
    - daily_data: Datos acumulados del día (agua, sueño, actividad, energía)

    Lógica:
    - Recupera perfil base (AG-INICIAL)
    - Aplica modificadores por altitud (>3500m)
    - Calcula indicadores
    - Genera alertas inmediatas
    - Persiste estado
    """

    # 1. Obtener perfil base del AG-INICIAL
    profile = get_user_profile(user_id)
    if not profile:
        raise ValueError("Perfil de usuario no encontrado. Ejecuta AG-INICIAL primero.")

    # Valores base del AG-INICIAL
    agua_base_ml = profile.get("agua_base_ml", 3000)
    sueno_base_h = profile.get("sueno_base_h", 8)
    altitud = profile.get("altitud", 0)

    # 2. Extraer datos del día actual
    agua_consumida = daily_data.get("agua_consumida_ml", 0)
    horas_sueno = daily_data.get("horas_sueno", 0)
    actividad_minutos = daily_data.get("actividad_minutos", 0)
    nivel_energia = daily_data.get("nivel_energia", 3)  # 1-5
    actividad_mental = daily_data.get("actividad_mental", "No especificada")
    estado_emocional = daily_data.get("estado_emocional", "No especificado")

    # 3. Calcular indicadores fisiológicos con MODIFICADORES DE ALTITUD

    # --- Hidratación ---
    porcentaje_hidratacion = (agua_consumida / agua_base_ml) * 100

    # Sensibilidad a la deshidratación aumenta en altura
    # Si altitud > 3500m, umbral sube a 75% (más estricto)
    umbral_hidratacion = 75 if altitud > 3500 else 70
    deshidratado = porcentaje_hidratacion < umbral_hidratacion

    # --- Sueño ---
    porcentaje_sueno = (horas_sueno / sueno_base_h) * 100

    # Impacto del déficit de sueño aumenta en altura
    # Si altitud > 3500m, umbral sube a 85% (más estricto)
    umbral_sueno = 85 if altitud > 3500 else 80
    falta_sueno = porcentaje_sueno < umbral_sueno

    # --- Actividad ---
    # En altura se reduce el umbral mínimo de actividad para no sobreexigir
    actividad_minima = 20 if altitud > 3500 else 30
    actividad_suficiente = actividad_minutos >= actividad_minima

    # 4. Determinar estado fisiológico (Determinístico)
    # Reglas estrictas sin interpretación

    estado = "NORMAL"

    if deshidratado and falta_sueno:
        estado = "CRÍTICO"
    elif deshidratado or falta_sueno:
        estado = "ALERTA"
    elif nivel_energia <= 2:
        estado = "BAJO"

    # 5. Generar alertas inmediatas
    alertas = []

    if deshidratado:
        msg = f"⚠️ DESHIDRATACIÓN: Has consumido {porcentaje_hidratacion:.0f}% del objetivo."
        if altitud > 3500:
            msg += f" En altura ({altitud}m) necesitas al menos {umbral_hidratacion}% para estar seguro."
        else:
            msg += f" Meta mínima segura: {umbral_hidratacion}%."
        alertas.append(msg)

    if falta_sueno:
        msg = f"😴 FALTA DE SUEÑO: Has completado {porcentaje_sueno:.0f}% de tu descanso base."
        if altitud > 3500:
            msg += (
                f" A {altitud}m, el déficit afecta más. Meta segura: {umbral_sueno}%."
            )
        else:
            msg += f" Meta mínima recomendada: {umbral_sueno}%."
        alertas.append(msg)

    if not actividad_suficiente:
        alertas.append(
            f"🏃 ACTIVIDAD BAJA: Tienes {actividad_minutos} min. Objetivo ajustado a tu altitud: {actividad_minima} min."
        )

    if nivel_energia <= 2:
        alertas.append(
            f"⚡ ENERGÍA BAJA: Nivel {nivel_energia}/5. Monitoriza tu fatiga."
        )

    # 6. Crear estructura de datos persistente
    estado_fisio = {
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "estado": estado,
        "indicadores": {
            "hidratacion_porcentaje": round(porcentaje_hidratacion, 1),
            "agua_consumida_ml": agua_consumida,
            "agua_base_ml": agua_base_ml,
            "sueno_porcentaje": round(porcentaje_sueno, 1),
            "horas_sueno": horas_sueno,
            "sueno_base_h": sueno_base_h,
            "actividad_minutos": actividad_minutos,
            "actividad_minima": actividad_minima,
            "nivel_energia": nivel_energia,
            "altitud": altitud,
        },
        "alertas": alertas,
        "actividad_mental": actividad_mental,
        "estado_emocional": estado_emocional,
        "agent": "AG-FISIO",
    }

    # 7. Persistir en base de datos
    daily_states.insert_one(estado_fisio)

    return estado_fisio
