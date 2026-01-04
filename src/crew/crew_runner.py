import json
from crewai import Crew
from crew.agents import make_architect_agent
from crew.tasks import make_design_task
from common.models import DesignResult

def run_design_crew(idea: str) -> DesignResult:
    agent = make_architect_agent()
    task = make_design_task(agent, idea)

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )

    raw = crew.kickoff()

    # CrewAI may return a string. We expect strict JSON.
    if isinstance(raw, str):
        data = json.loads(raw)
    else:
        # Some versions return objects; fallback to string conversion
        data = json.loads(str(raw))

    return DesignResult.model_validate(data)
