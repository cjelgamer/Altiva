
from crewai import Task
from backend.agents.ag_inicial import run_ag_inicial
from backend.crew.agents import ag_inicial

def create_ag_inicial_task(user_id, user_data):
    return Task(
        description="Initialize user physiological profile",
        expected_output="User profile stored in database",
        agent=ag_inicial,
        function=lambda: run_ag_inicial(user_id, user_data)
    )
