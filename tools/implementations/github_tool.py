import os
import logging
from typing import Dict, Any
try:
    from github import Github
except ImportError:
    Github = None

logger = logging.getLogger("mintuu.tools.github")

class GitHubTool:
    """Real GitHub integration tool."""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.client = Github(self.token) if self.token and Github else None
        
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        if not self.client:
            return {"error": "GitHub token not configured or PyGithub not installed."}
            
        try:
            if action == "get_repo":
                repo = self.client.get_repo(kwargs.get("repo_name"))
                return {
                    "name": repo.name,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "open_issues": repo.open_issues_count
                }
            elif action == "create_issue":
                repo = self.client.get_repo(kwargs.get("repo_name"))
                issue = repo.create_issue(
                    title=kwargs.get("title"),
                    body=kwargs.get("body", "")
                )
                return {"issue_url": issue.html_url, "issue_number": issue.number}
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"GitHub tool error: {e}")
            return {"error": str(e)}
