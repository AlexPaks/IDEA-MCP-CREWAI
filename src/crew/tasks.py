from crewai import Task

DESIGN_PROMPT_TEMPLATE = """
You are a senior software architect.

INPUT:
- app_idea: "{idea}"

OUTPUT REQUIREMENTS (STRICT):
Return a single JSON object with exactly these keys:
1) "design_markdown": string
2) "issues": array of objects
No extra keys. No markdown fences. No commentary. JSON only.

DESIGN MARKDOWN REQUIREMENTS:
"design_markdown" must be Markdown with headings in this exact order:
# Overview
# Goals
# Non-Goals
# Users & Use Cases
# High-Level Architecture
# Components
# Data Model
# API Design
# Security & Auth
# Deployment
# Observability
# Milestones

ISSUES REQUIREMENTS:
"issues" must contain 15–25 issue objects with fields:
- title, body, labels, priority (P0/P1/P2), order (1..N)
Each body must include:
## Acceptance Criteria
- ...
## Notes
- ...

Do NOT include code. Only architecture and tasks.
"""

def make_design_task(agent, idea: str) -> Task:
    return Task(
        description=DESIGN_PROMPT_TEMPLATE.format(idea=idea.replace('"', '\\"')),
        agent=agent,
        expected_output="JSON with design_markdown + issues[]",
    )

        