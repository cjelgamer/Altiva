from crewai import Agent, Task, Crew
from backend.agents.ag_inicial import run_ag_inicial
from backend.agents.ag_fisio import run_ag_fisio
from backend.agents.ag_fatiga import run_ag_fatiga
from backend.agents.ag_plan import run_ag_plan
from backend.services.openai_service import analyze_with_llm
import json


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


# Definir agentes CrewAI
ag_fisio_agent = Agent(
    role="Agente Fisiológico",
    goal="Monitorear y analizar el estado fisiológico del usuario en altura",
    backstory="""Eres un especialista en fisiología humana enfocado en los efectos de la altitud.
    Monitoreas indicadores vitales como hidratación, sueño, actividad y energía para detectar
    patrones y alertar sobre riesgos potenciales. Tu análisis es preciso y basado en evidencia.""",
    verbose=True,
    allow_delegation=False,
)

ag_fatiga_agent = Agent(
    role="Analista de Fatiga y Productividad",
    goal="Analizar fatiga acumulada y capacidad de productividad en altura",
    backstory="""Eres un experto en neurociencia y rendimiento humano en ambientes de alta altitud.
    Evalúas cómo los factores fisiológicos afectan la capacidad cognitiva y productividad del usuario.
    Generas alertas precisas y recomiendas horarios óptimos para estudio/trabajo.""",
    verbose=True,
    allow_delegation=False,
)

ag_plan_agent = Agent(
    role="Planificador de Recuperación y Productividad",
    goal="Crear planes personalizados de recuperación y optimización productiva",
    backstory="""Eres un estratega del bienestar y productividad que entiende los desafíos de la altura.
    Diseñas planes integrales que equilibran descanso, actividad y rendimiento óptimo.
    Tus recomendaciones son prácticas, específicas y adaptadas a las condiciones individuales.""",
    verbose=True,
    allow_delegation=False,
)


# Definir tareas CrewAI
def create_fisio_task(user_id, daily_data):
    return Task(
        description=f"""Analizar el estado fisiológico del usuario {user_id} con los siguientes datos: {json.dumps(daily_data)}.
        
        Evalúa:
        1. Estado de hidratación (consumido vs objetivo)
        2. Calidad y cantidad del sueño
        3. Nivel de actividad física
        4. Nivel de energía subjetivo
        5. Impacto de la altitud en el estado general
        
        Genera un análisis completo y detecta posibles alertas.""",
        agent=ag_fisio_agent,
        expected_output="Análisis fisiológico detallado con indicadores y alertas específicas",
    )


def create_fatiga_task(estado_fisio, contexto_productividad=None):
    return Task(
        description=f"""Analizar la fatiga y productividad basado en el estado fisiológico: {json.dumps(estado_fisio)}.
        
        Contexto de productividad: {contexto_productividad if contexto_productividad else "No especificado"}
        
        Evalúa:
        1. Nivel de fatiga actual (Bajo/Medio/Alto)
        2. Índice de Fatiga en Altura (IFA 0-100)
        3. Capacidad productiva actual (horas óptimas de estudio/trabajo)
        4. Tiempos recomendados para pausas y descanso
        5. Alertas específicas con tiempos sugeridos
        
        Justifica tu análisis considerando el contexto de altitud y productividad.""",
        agent=ag_fatiga_agent,
        expected_output="Análisis de fatiga con IFA, nivel productivo y alertas temporizadas",
    )


def create_plan_task(analisis_fatiga, historial=None):
    return Task(
        description=f"""Crear un plan de recuperación y productividad basado en: {json.dumps(analisis_fatiga)}.
        
        Historial relevante: {historial if historial else "No disponible"}
        
        Genera:
        1. Plan inmediato de acción (próximas 2-4 horas)
        2. Horarios óptimos para estudio/trabajo hoy
        3. Pausas activas específicas para el nivel de fatiga
        4. Consejos adaptados a la altitud actual
        5. Estrategias de optimización productiva
        
        El plan debe ser práctico, específico y accionable.""",
        agent=ag_plan_agent,
        expected_output="Plan integral de recuperación y productividad con horarios y acciones específicas",
    )


def run_collaborative_crew(user_id, daily_data, contexto_productividad=None):
    """
    Ejecuta el flujo colaborativo completo usando CrewAI.
    AG-FISIO → AG-FATIGA → AG-PLAN
    """
    # Crear tareas secuenciales
    fisio_task = create_fisio_task(user_id, daily_data)
    fatiga_task = create_fatiga_task(
        None, contexto_productividad
    )  # Se actualizará con resultado de AG-FISIO
    plan_task = create_plan_task(
        None, None
    )  # Se actualizará con resultado de AG-FATIGA

    # Crear el crew
    crew = Crew(
        agents=[ag_fisio_agent, ag_fatiga_agent, ag_plan_agent],
        tasks=[fisio_task, fatiga_task, plan_task],
        verbose=2,
        process="sequential",  # Ejecución secuencial: FISIO → FATIGA → PLAN
    )

    # Ejecutar el crew
    try:
        result = crew.kickoff()

        # Procesar y estructurar resultados
        results = {
            "estado_fisio": None,
            "analisis_fatiga": None,
            "plan_recuperacion": None,
            "crew_execution": "completed",
        }

        return results

    except Exception as e:
        print(f"Error en ejecución CrewAI: {e}")
        # Fallback a ejecución individual
        return run_fallback_crew(user_id, daily_data, contexto_productividad)


def run_fallback_crew(user_id, daily_data, contexto_productividad=None):
    """
    Ejecución individual como fallback si CrewAI falla.
    """
    results = {}

    try:
        # 1. AG-FISIO
        results["estado_fisio"] = run_fisio_crew(user_id, daily_data)

        # 2. AG-FATIGA
        results["analisis_fatiga"] = run_fatiga_crew(
            user_id, results["estado_fisio"], contexto_productividad
        )

        # 3. AG-PLAN
        results["plan_recuperacion"] = run_plan_crew(
            user_id, results["analisis_fatiga"]
        )

        results["crew_execution"] = "fallback"

    except Exception as e:
        print(f"Error en fallback: {e}")
        results["crew_execution"] = "failed"
        results["error"] = str(e)

    return results


def run_complete_crew(
    user_id, user_data=None, daily_data=None, contexto_productividad=None
):
    """
    Ejecuta el flujo completo del sistema ALTIVA.
    Prioriza CrewAI colaborativo, con fallback a ejecución individual.
    """
    results = {}

    # 1. AG-INICIAL (solo si se proporcionan datos)
    if user_data:
        results["perfil"] = run_initial_crew(user_id, user_data)

    # 2. Flujo colaborativo (solo si se proporcionan datos diarios)
    if daily_data:
        try:
            collaborative_results = run_collaborative_crew(
                user_id, daily_data, contexto_productividad
            )
            results.update(collaborative_results)
        except Exception as e:
            print(f"Error en flujo colaborativo, usando fallback: {e}")
            fallback_results = run_fallback_crew(
                user_id, daily_data, contexto_productividad
            )
            results.update(fallback_results)

    return results
