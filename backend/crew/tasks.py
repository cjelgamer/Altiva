from crewai import Task
from backend.agents.ag_inicial import run_ag_inicial
from backend.agents.ag_fisio import run_ag_fisio
from backend.agents.ag_fatiga import run_ag_fatiga
from backend.agents.ag_plan import run_ag_plan
from backend.crew.agents import ag_inicial, ag_fisio, ag_fatiga, ag_plan


def execute_ag_inicial_task(user_id, user_data):
    """
    Ejecuta AG-INICIAL directamente.
    Nota: AG-INICIAL es determinístico, se llama directamente sin CrewAI.
    """
    return run_ag_inicial(user_id, user_data)


def execute_ag_fisio_task(user_id, daily_data):
    """
    Ejecuta AG-FISIO directamente.
    Nota: AG-FISIO es determinístico, se llama directamente sin CrewAI.
    """
    return run_ag_fisio(user_id, daily_data)


def execute_ag_fatiga_task(
    user_id,
    estado_fisio,
    actividad_mental: str | None = None,
    estado_emocional: str | None = None,
):
    """
    Ejecuta AG-FATIGA directamente.
    Nota: AG-FATIGA usa LLM, se llama directamente para mayor control.
    """
    return run_ag_fatiga(user_id, estado_fisio, actividad_mental, estado_emocional)


def execute_ag_plan_task(user_id, analisis_fatiga, historial_dia=None):
    """
    Ejecuta AG-PLAN directamente.
    Nota: AG-PLAN usa LLM, se llama directamente para mayor control.
    """
    return run_ag_plan(user_id, analisis_fatiga, historial_dia)


def create_ag_fisio_task(user_id, daily_data):
    """
    Crea una tarea CrewAI para AG-FISIO (opcional, para compatibilidad).
    """
    return Task(
        description="Monitor user's physiological state and calculate indicators with altitude modifiers",
        expected_output="Structured physiological state with indicators and alerts",
        agent=ag_fisio,
    )


def create_ag_fatiga_task(
    user_id, estado_fisio, actividad_mental=None, estado_emocional=None
):
    """
    Crea una tarea CrewAI para AG-FATIGA (opcional, para compatibilidad).
    """
    return Task(
        description="Analyze accumulated fatigue and calculate Altitude Fatigue Index (IFA)",
        expected_output="Fatigue analysis with level, IFA score and justification",
        agent=ag_fatiga,
    )


def create_ag_plan_task(user_id, analisis_fatiga, historial_dia=None):
    """
    Crea una tarea CrewAI para AG-PLAN (opcional, para compatibilidad).
    """
    return Task(
        description="Generate dynamic recovery and productivity plan based on fatigue analysis and altitude conditions",
        expected_output="Structured plan with immediate recommendations, optimal schedules, active breaks, and altitude-specific advice",
        agent=ag_plan,
    )
