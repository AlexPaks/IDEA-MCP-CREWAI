from crewai import Agent

def make_architect_agent() -> Agent:
    return Agent(
        role="Software Architect",
        goal="Produce a high-level design document and actionable GitHub issues for an app idea.",
        backstory=(
            "You are a pragmatic senior software architect. "
            "You create buildable designs and issue breakdowns."
        ),
        verbose=True,
    )
