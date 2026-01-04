from backend.agents.ag_inicial import run_ag_inicial

def run_initial_crew(user_id, user_data):
    """
    AG-INICIAL es determinístico, no necesita LLM ni CrewAI.
    Llamamos directamente a la función.
    """
    return run_ag_inicial(user_id, user_data)
