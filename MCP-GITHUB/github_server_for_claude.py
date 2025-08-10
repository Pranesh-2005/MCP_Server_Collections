import os
from typing import Any
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()
GITHUB_PAT = os.getenv("GITHUB_PAT")
GITHUB_API_BASE = "https://api.github.com"
USER_AGENT = "github-mcp-client/1.0"

# Initialize FastMCP
mcp = FastMCP("GitHub Async Server")

# Helper function for async GitHub API requests
async def make_github_request(
    method: str,
    endpoint: str,
    json: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json"
    }
    if GITHUB_PAT:
        headers["Authorization"] = f"Bearer {GITHUB_PAT}"

    url = f"{GITHUB_API_BASE}{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, headers=headers, json=json, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def github_user_info(username: str) -> str:
    """Get GitHub user information."""
    data = await make_github_request("GET", f"/users/{username}")
    if not data:
        return "Error fetching user info."

    return f"""
User: {data.get('name', 'N/A')} (@{data.get('login')})
Bio: {data.get('bio', 'N/A')}
Public Repos: {data.get('public_repos', 0)}
Followers: {data.get('followers', 0)}
Following: {data.get('following', 0)}
Location: {data.get('location', 'N/A')}
Company: {data.get('company', 'N/A')}
Created: {data.get('created_at', 'N/A')}
""".strip()

@mcp.tool()
async def create_repository(name: str, description: str = "", private: bool = False) -> str:
    """Create a new GitHub repository."""
    payload = {"name": name, "description": description, "private": private}
    data = await make_github_request("POST", "/user/repos", json=payload)

    if not data:
        return "Error creating repository."

    return f"""
Repository created successfully!
Name: {data.get('full_name')}
URL: {data.get('html_url')}
Description: {data.get('description', 'N/A')}
Private: {data.get('private', False)}
""".strip()

@mcp.tool()
async def delete_repository(owner: str, repo: str) -> str:
    """Delete a GitHub repository."""
    data = await make_github_request("DELETE", f"/repos/{owner}/{repo}")
    if data is None:
        return f"Repository {owner}/{repo} was deleted successfully!"
    return "Error deleting repository."

@mcp.tool()
async def create_pull_request(owner: str, repo: str, title: str, head: str, base: str, body: str = "") -> str:
    """Create a pull request."""
    payload = {"title": title, "head": head, "base": base, "body": body}
    data = await make_github_request("POST", f"/repos/{owner}/{repo}/pulls", json=payload)

    if not data:
        return "Error creating pull request."

    return f"""
Pull Request created successfully!
Title: {data.get('title')}
PR #: {data.get('number')}
URL: {data.get('html_url')}
State: {data.get('state')}
""".strip()

@mcp.tool()
async def merge_pull_request(owner: str, repo: str, pull_number: int, commit_message: str = "") -> str:
    """Merge a pull request."""
    payload = {"commit_message": commit_message} if commit_message else {}
    data = await make_github_request("PUT", f"/repos/{owner}/{repo}/pulls/{pull_number}/merge", json=payload)

    if not data:
        return "Error merging pull request."

    return f"""
Pull Request #{pull_number} merged successfully!
Message: {data.get('message')}
SHA: {data.get('sha')}
""".strip()

@mcp.tool()
async def list_repositories(username: str = "") -> str:
    """List repositories for a user."""
    endpoint = f"/users/{username}/repos" if username else "/user/repos"
    repos = await make_github_request("GET", endpoint)

    if not repos:
        return "No repositories found or error occurred."

    repo_list = []
    for repo in repos[:10]:  # limit output
        repo_list.append(f"- {repo.get('full_name')}: {repo.get('description', 'No description')} ({repo.get('html_url')})")

    return "Repositories:\n" + "\n".join(repo_list) + (f"\n\n(Showing 10 of {len(repos)} repositories)" if len(repos) > 10 else "")

@mcp.tool()
async def hello_world(name: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="stdio")
