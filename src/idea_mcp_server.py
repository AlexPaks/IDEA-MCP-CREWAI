import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
import os
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Any, Dict

from crew.crew_runner import run_design_crew

mcp = FastMCP("idea-mcp")

class GenerateDesignInput(BaseModel):
    idea: str = Field(min_length=5, description="An app idea as a plain string")

@mcp.tool()
def generate_design(input: GenerateDesignInput) -> Dict[str, Any]:
    """
    Generates a high-level DESIGN.md (markdown) and a list of GitHub issues from an app idea.
    """
    result = run_design_crew(input.idea)
    # Generate project name (slugified)
    import re
    project_name = re.sub(r'[^a-zA-Z0-9_-]', '-', input.idea.strip().lower())[:30].strip('-')
    # Return plain dict (MCP-friendly)
    return {
        "project_name": project_name,
        "design_markdown": result.design_markdown,
        "issues": [i.model_dump() for i in result.issues],
    }

def slugify(text: str, max_len: int = 30) -> str:
    import re
    return re.sub(r"[^a-zA-Z0-9_-]", "-", text.strip().lower())[:max_len].strip("-")
def close_existing_issues(user: str, repo_name: str, headers: dict):
    import requests

    issues_url = f"https://api.github.com/repos/{user}/{repo_name}/issues"
    params = {
        "state": "open",
        "per_page": 100
    }

    print("Checking for existing open issues...")
    resp = requests.get(issues_url, headers=headers, params=params, timeout=30)

    if resp.status_code != 200:
        print(f"Failed to fetch issues: {resp.status_code}\n{resp.text}")
        return

    issues = resp.json()
    if not issues:
        print("No existing issues found.")
        return

    print(f"Found {len(issues)} existing issues. Closing them...")

    for issue in issues:
        issue_number = issue["number"]
        close_url = f"{issues_url}/{issue_number}"
        patch = requests.patch(
            close_url,
            headers=headers,
            json={"state": "closed"},
            timeout=30
        )
        if patch.status_code == 200:
            print(f"Closed issue #{issue_number}: {issue['title']}")
        else:
            print(f"Failed to close issue #{issue_number}: {patch.status_code}")

def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        idea = input("Enter your app idea: ")
        logging.info(f"User input idea: {idea}")
        if len(idea) < 5:
            print("Idea must be at least 5 characters long.")
            return
        from crew.crew_runner import run_design_crew
        result = run_design_crew(idea)
        repo_name = slugify(idea)
        project_name = repo_name
        logging.info(f"Generated project name: {project_name}")
        print(f"\n--- Project Name ---\n{project_name}")
        print("\n--- DESIGN.md ---\n")
        print(result.design_markdown)
        print("\n--- GitHub Issues ---\n")
        for issue in result.issues:
            logging.info(f"Prepared issue: {issue.title}")
            print(f"#{issue.order} [{issue.priority}] {issue.title}\n{issue.body}\nLabels: {', '.join(issue.labels)}\n")

        # Ask user if they want to create a new GitHub repo and issues
        
        create = input("\nCreate a new GitHub repo and add these issues? (y/n): ").strip().lower()
        logging.info(f"User chose to create repo/issues: {create}")
        if create != "y":
            return

        load_dotenv()
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            logging.error("GITHUB_TOKEN not found in environment.")
            print("GITHUB_TOKEN not found in environment.")
            return

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

        # Get actual username from token

        me = requests.get("https://api.github.com/user", headers=headers, timeout=30)
        if me.status_code != 200:
            logging.error(f"Failed to get user: {me.status_code}\n{me.text}")
            print(f"Failed to get user: {me.status_code}\n{me.text}")
            return
        user = me.json()["login"]

        # Create repo
        repo_api_url = "https://api.github.com/user/repos"
        repo_data = {"name": repo_name, "description": f"Repository for: {idea}", "private": False}

        repo_resp = requests.post(repo_api_url, json=repo_data, headers=headers, timeout=30)
        if repo_resp.status_code == 201:
            logging.info(f"Repository created: https://github.com/{user}/{repo_name}")
            print(f"Repository created: https://github.com/{user}/{repo_name}")
        elif repo_resp.status_code == 422:
            # check if it exists
            check = requests.get(f"https://api.github.com/repos/{user}/{repo_name}", headers=headers, timeout=30)
            if check.status_code == 200:
                logging.warning(f"Repository already exists: https://github.com/{user}/{repo_name}")
                print(f"Repository already exists: https://github.com/{user}/{repo_name}")
                # Close existing issues
                close_existing_issues(user, repo_name, headers) 
            else:
                logging.error(f"Failed to create repository: {repo_resp.status_code}\n{repo_resp.text}")
                print(f"Failed to create repository: {repo_resp.status_code}\n{repo_resp.text}")
                return
        else:
            logging.error(f"Failed to create repository: {repo_resp.status_code}\n{repo_resp.text}")
            print(f"Failed to create repository: {repo_resp.status_code}\n{repo_resp.text}")
            return

        # Create issues
        issues_url = f"https://api.github.com/repos/{user}/{repo_name}/issues"
        for issue in result.issues:
            data = {"title": issue.title, "body": issue.body, "labels": issue.labels}
            resp = requests.post(issues_url, json=data, headers=headers, timeout=30)
            if resp.status_code == 201:
                logging.info(f"Created issue: {issue.title}")
                print(f"Created issue: {issue.title}")
            else:
                logging.error(f"Failed to create issue: {issue.title} (Status: {resp.status_code})\n{resp.text}")
                print(f"Failed to create issue: {issue.title} (Status: {resp.status_code})\n{resp.text}")
    else:
        # stdio transport (VS Code compatible)
        mcp.run()

if __name__ == "__main__":
    main()
