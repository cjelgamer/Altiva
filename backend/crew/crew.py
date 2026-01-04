from backend.agents.ag_inicial import run_ag_inicial
from backend.agents.ag_fisio import run_ag_fisio
from backend.agents.ag_fatiga import run_ag_fatiga
from backend.agents.ag_plan import run_ag_plan


def run_initial_crew(user_id, user_data):
    """
    AG-INICIAL es determinístico, no necesita LLM ni CrewAI.
    Llamamos directamente a la función.
    """
    return run_ag_inicial(user_id, user_data)


def run_fisio_crew(user_id, daily_data):
    """
    AG-FISIO es determinístico, no necesita LLM ni CrewAI.
    Llamamos directamente a la función.
    """
    return run_ag_fisio(user_id, daily_data)


def run_fatiga_crew(
    user_id, estado_fisio, actividad_mental=None, estado_emocional=None
):
    """
    AG-FATIGA usa LLM, llamamos directamente para mayor control.
    """
    return run_ag_fatiga(user_id, estado_fisio, actividad_mental, estado_emocional)


def run_plan_crew(user_id, analisis_fatiga, historial_dia=None):
    """
    AG-PLAN usa LLM, llamamos directamente para mayor control.
    """
    return run_ag_plan(user_id, analisis_fatiga, historial_dia)


def run_complete_crew(user_id, user_data=None, daily_data=None):
    """
    Ejecuta el flujo completo del sistema ALTIVA.
    Si se proporcionan user_data y daily_data, ejecuta todo el flujo.
    """
    results = {}

    # 1. AG-INICIAL (solo si se proporcionan datos)
    if user_data:
        results["perfil"] = run_initial_crew(user_id, user_data)

    # 2. AG-FISIO (solo si se proporcionan datos diarios)
    if daily_data:
        results["estado_fisio"] = run_fisio_crew(user_id, daily_data)

        # 3. AG-FATIGA (depende de AG-FISIO)
        results["analisis_fatiga"] = run_fatiga_crew(user_id, results["estado_fisio"])

        # 4. AG-PLAN (depende de AG-FATIGA)
        results["plan_recuperacion"] = run_plan_crew(
            user_id, results["analisis_fatiga"]
        )

    return results
