import os
from dotenv import load_dotenv
import requests
from mcp.server.fastmcp import FastMCP
import sys
import logging
import uvicorn

logging.basicConfig(level=logging.INFO)

load_dotenv()
GITHUB_PAT = os.getenv("GITHUB_PAT")

mcp = FastMCP("GitHub Server")

@mcp.tool(name="github_user_info", description="Get information about a GitHub user")
def get_user_info(username: str) -> str:
    """Get GitHub user information"""
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        response = requests.get(
            f"https://api.github.com/users/{username}",
            headers=headers
        )
        response.raise_for_status()
        user_data = response.json()
        
        return f"""
User: {user_data.get('name', 'N/A')} (@{user_data.get('login')})
Bio: {user_data.get('bio', 'N/A')}
Public Repos: {user_data.get('public_repos', 0)}
Followers: {user_data.get('followers', 0)}
Following: {user_data.get('following', 0)}
Location: {user_data.get('location', 'N/A')}
Company: {user_data.get('company', 'N/A')}
Created: {user_data.get('created_at', 'N/A')}
        """.strip()
    except requests.RequestException as e:
        return f"Error fetching user info: {str(e)}"

@mcp.tool(name="create_repository", description="Create a new GitHub repository")
def create_repository(name: str, description: str = "", private: bool = False) -> str:
    """Create a new GitHub repository for the authenticated user"""
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        payload = {
            "name": name,
            "description": description,
            "private": private
        }
        response = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        repo_data = response.json()
        
        return f"""
Repository created successfully!
Name: {repo_data.get('full_name')}
URL: {repo_data.get('html_url')}
Description: {repo_data.get('description', 'N/A')}
Private: {repo_data.get('private', False)}
        """.strip()
    except requests.RequestException as e:
        return f"Error creating repository: {str(e)}"

@mcp.tool(name="delete_repository", description="Delete a GitHub repository")
def delete_repository(owner: str, repo: str) -> str:
    """Delete a GitHub repository (requires appropriate permissions)"""
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        response = requests.delete(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers
        )
        response.raise_for_status()
        
        return f"Repository {owner}/{repo} was deleted successfully!"
    except requests.RequestException as e:
        return f"Error deleting repository: {str(e)}"

@mcp.tool(name="create_pull_request", description="Create a pull request")
def create_pull_request(owner: str, repo: str, title: str, head: str, base: str, body: str = "") -> str:
    """Create a pull request in a repository"""
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        payload = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        response = requests.post(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        pr_data = response.json()
        
        return f"""
Pull Request created successfully!
Title: {pr_data.get('title')}
PR #: {pr_data.get('number')}
URL: {pr_data.get('html_url')}
State: {pr_data.get('state')}
        """.strip()
    except requests.RequestException as e:
        return f"Error creating pull request: {str(e)}"

@mcp.tool(name="merge_pull_request", description="Merge a pull request")
def merge_pull_request(owner: str, repo: str, pull_number: int, commit_message: str = "") -> str:
    """Merge an open pull request"""
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        payload = {}
        if commit_message:
            payload["commit_message"] = commit_message
            
        response = requests.put(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/merge",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        merge_data = response.json()
        
        return f"""
Pull Request #{pull_number} merged successfully!
Message: {merge_data.get('message')}
SHA: {merge_data.get('sha')}
        """.strip()
    except requests.RequestException as e:
        return f"Error merging pull request: {str(e)}"

@mcp.tool(name="list_repositories", description="List repositories for a user")
def list_repositories(username: str = "") -> str:
    """List repositories for the specified user or authenticated user if not specified"""
    headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}
    
    try:
        url = f"https://api.github.com/users/{username}/repos" if username else "https://api.github.com/user/repos"
        response = requests.get(
            url,
            headers=headers
        )
        response.raise_for_status()
        repos = response.json()
        
        if not repos:
            return "No repositories found."
        
        repo_list = []
        for repo in repos[:10]:  # Limit to 10 repos to avoid large responses
            repo_list.append(f"- {repo.get('full_name')}: {repo.get('description', 'No description')} ({repo.get('html_url')})")
        
        return "Repositories:\n" + "\n".join(repo_list) + (f"\n\n(Showing 10 of {len(repos)} repositories)" if len(repos) > 10 else "")
    except requests.RequestException as e:
        return f"Error listing repositories: {str(e)}"

@mcp.tool(name="hello_world", description="A simple test tool")
def hello_world(name: str = "World") -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # For local development with `mcp dev`
    print("Starting GitHub MCP server...")
    
    # With proper host and port configuration to avoid conflicts
    if "mcp dev" in " ".join(sys.argv):
        mcp.serve(host="127.0.0.1", port=5000)
    else:
        # Standard serve for regular use
        mcp.serve()