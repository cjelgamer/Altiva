from crewai import Agent

ag_inicial = Agent(
    role="Initial Configuration Agent",
    goal="Create a valid user physiological profile based on city and personal data",
    backstory="You initialize the system with clean, deterministic data.",
    verbose=True,
    allow_delegation=False,
)

ag_fisio = Agent(
    role="Physiological Monitoring Agent",
    goal="Monitor and analyze user's physiological state progressively throughout the day",
    backstory="You are a deterministic physiological monitoring specialist. You track hydration, sleep, activity and energy levels, applying altitude-specific modifiers to determine the user's current physiological state.",
    verbose=True,
    allow_delegation=False,
)

ag_fatiga = Agent(
    role="Fatigue Analysis Agent",
    goal="Analyze accumulated fatigue using contextual reasoning and altitude considerations",
    backstory="You are an AI specialist in fatigue analysis for high-altitude environments. You use contextual reasoning to determine fatigue levels and calculate the Altitude Fatigue Index (IFA) considering how altitude amplifies physiological effects.",
    verbose=True,
    allow_delegation=False,
)

ag_plan = Agent(
    role="Recovery Planning Agent",
    goal="Generate dynamic recovery and productivity plans based on fatigue analysis",
    backstory="You are a specialized recovery and productivity expert for high-altitude environments. You analyze fatigue indicators and create personalized recommendations considering altitude effects on human physiology.",
    verbose=True,
    allow_delegation=False,
)

ag_plan = Agent(
    role="Recovery Planning Agent",
    goal="Generate dynamic recovery and productivity plans based on fatigue analysis",
    backstory="You are a specialized recovery and productivity expert for high-altitude environments. You analyze fatigue indicators and create personalized recommendations considering altitude effects on human physiology.",
    verbose=True,
    allow_delegation=False,
)
