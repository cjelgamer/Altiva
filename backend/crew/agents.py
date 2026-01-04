from crewai import Agent

ag_inicial = Agent(
    role="Initial Configuration Agent",
    goal="Create a valid user physiological profile based on city and personal data",
    backstory="You initialize the system with clean, deterministic data.",
    verbose=True,
    allow_delegation=False
)
