import os
from mcp.server.fastmcp import FastMCP
from git import Repo, GitCommandError
from utils import get_or_init_repo, setup_remote, stage_commit_push
import sys
import re

mcp = FastMCP("MCP GitHub Push Server")

REPO_BASE = "repos"
os.makedirs(REPO_BASE, exist_ok=True)

def is_valid_git_url(url: str) -> bool:
    """Check if a string is a valid Git repository URL."""
    git_url_patterns = [
        r'^https://github\.com/[\w.-]+/[\w.-]+(?:\.git)?$',  # HTTPS GitHub
        r'^git@github\.com:[\w.-]+/[\w.-]+(?:\.git)?$',      # SSH GitHub
        r'^https://gitlab\.com/[\w.-]+/[\w.-]+(?:\.git)?$',  # HTTPS GitLab
        r'^git@gitlab\.com:[\w.-]+/[\w.-]+(?:\.git)?$',      # SSH GitLab
        r'^https://bitbucket\.org/[\w.-]+/[\w.-]+(?:\.git)?$', # HTTPS Bitbucket
        r'^git@bitbucket\.org:[\w.-]+/[\w.-]+(?:\.git)?$'    # SSH Bitbucket
    ]
    
    return any(re.match(pattern, url) for pattern in git_url_patterns)

def is_valid_local_path(path: str) -> bool:
    """Check if a string is a valid local path."""
    path = os.path.abspath(os.path.normpath(path))
    # Check if it's a directory or can be created
    parent_dir = os.path.dirname(path)
    return os.path.exists(parent_dir) or os.path.exists(os.path.dirname(parent_dir))

@mcp.tool()
def add_file_to_repo(file_path: str, repo_url: str, branch: str = "main") -> str:
    """
    Add a file to a Git repository.
    
    Args:
        file_path: Local path to the file to add
        repo_url: The remote repository URL (e.g. https://github.com/username/repo.git)
        branch: The branch to push to (default: main)
    """
    try:
        repo_dir = os.path.join(REPO_BASE, "temp_repo")
        repo = get_or_init_repo(repo_dir)
        dst = os.path.join(repo_dir, os.path.basename(file_path))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(file_path, "rb") as src, open(dst, "wb") as d:
            d.write(src.read())
        setup_remote(repo, repo_url)
        return stage_commit_push(repo, dst, "Added file", "origin", branch)
    except Exception as e:
        return f"Error adding file to repo: {str(e)}"

@mcp.tool()
def create_new_file(repo_path: str, filename: str, content: str) -> str:
    """
    Create a new file in a local Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        filename: Name of the file to create
        content: Content to write to the file
    """
    try:
        repo = get_or_init_repo(repo_path)
        full_path = os.path.join(repo_path, filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return stage_commit_push(repo, full_path, "Created new file")
    except Exception as e:
        return f"Error creating file: {str(e)}"

@mcp.tool()
def clone_to_path(repo_url: str, save_path: str, depth: int = None) -> str:
    """
    Clone a Git repository to a local path.
    
    Args:
        repo_url: The remote repository URL (e.g. https://github.com/username/repo.git)
        save_path: Local directory path where to clone the repository
        depth: Optional depth parameter for shallow clone (None for full clone)
    """
    try:
        save_path = os.path.normpath(save_path)
        if os.path.exists(save_path):
            return f"Path '{save_path}' already exists."
        
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(save_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            
        # Clone options
        clone_kwargs = {}
        if depth is not None and isinstance(depth, int) and depth > 0:
            clone_kwargs['depth'] = depth
            
        Repo.clone_from(repo_url, save_path, **clone_kwargs)
        return f"Cloned to {save_path}"
    except GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error cloning repository: {str(e)}"

@mcp.tool()
def check_remote(local_repo_path: str) -> str:
    """
    Check the remotes of a local Git repository.
    
    Args:
        repo_path: Path to the local repository directory
    """
    try:
        repo = get_or_init_repo(local_repo_path)
        remotes = [f"{r.name}: {r.url}" for r in repo.remotes]
        return f"Remotes: {remotes}" if remotes else "No remotes found."
    except Exception as e:
        return f"Error checking remotes: {str(e)}"

@mcp.tool()
def create_repo_if_not_found(path: str) -> str:
    """
    Create a new Git repository at the specified path if it doesn't exist.
    
    Args:
        path: Local directory path where to create the repository
    """
    try:
        repo = get_or_init_repo(path)
        return f"Repo initialized at {path}" if not repo.remotes else "Repo already present."
    except Exception as e:
        return f"Error creating repo: {str(e)}"

@mcp.tool()
def rename_file(repo_path: str, old_name: str, new_name: str) -> str:
    """
    Rename a file in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        old_name: Current name of the file
        new_name: New name for the file
    """
    try:
        old_path = os.path.join(repo_path, old_name)
        new_path = os.path.join(repo_path, new_name)
        
        if not os.path.exists(old_path):
            return f"Error: File '{old_name}' does not exist."
            
        # Create directory for new file if needed
        new_dir = os.path.dirname(new_path)
        if new_dir and not os.path.exists(new_dir):
            os.makedirs(new_dir, exist_ok=True)
            
        os.rename(old_path, new_path)
        return f"Renamed '{old_name}' to '{new_name}'."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def git_status(repo_path: str) -> str:
    """
    Get the status of a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
    """
    try:
        repo = get_or_init_repo(repo_path)
        return repo.git.status()
    except Exception as e:
        return f"Error getting status: {str(e)}"

@mcp.tool()
def pull(repo_path: str, branch: str = None) -> str:
    """
    Pull the latest changes from a remote repository.
    
    Args:
        repo_path: Path to the local repository directory
        branch: Branch to pull (default: current branch)
    """
    try:
        repo = get_or_init_repo(repo_path)
        if not repo.remotes:
            return "Error: No remote configured for this repository."
            
        if not branch:
            try:
                branch = repo.active_branch.name
            except TypeError:
                return "Error: Repository is in detached HEAD state and no branch specified."
                
        repo.remotes.origin.pull(branch)
        return f"Pulled latest changes from {branch}."
    except GitCommandError as e:
        return f"Git error during pull: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_remote(repo_path: str, github_url: str) -> str:
    """
    Set the 'origin' remote for a local Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        remote_url: The remote repository URL (e.g. https://github.com/username/repo.git)
    """
    try:
        repo = get_or_init_repo(repo_path)
        remotes = {r.name for r in repo.remotes}
        if "origin" in remotes:
            repo.delete_remote("origin")
        repo.create_remote("origin", github_url)
        return f"Remote 'origin' set to {github_url}"
    except Exception as e:
        return f"Error setting remote: {str(e)}"

@mcp.tool()
def get_remote_url(repo_path: str) -> str:
    """
    Get the URL of the 'origin' remote for a local Git repository.
    
    Args:
        repo_path: Path to the local repository directory
    """
    try:
        repo = get_or_init_repo(repo_path)
        if not repo.remotes:
            return "No remote found for this repository."
        return repo.remotes.origin.url
    except Exception as e:
        return f"Error getting remote URL: {str(e)}"

@mcp.tool()
def create_branch(repo_path: str, branch_name: str) -> str:
    """
    Create a new branch in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        branch_name: Name of the branch to create
    """
    try:
        repo = get_or_init_repo(repo_path)
        if branch_name in [h.name for h in repo.heads]:
            return f"Branch '{branch_name}' already exists."
        repo.git.checkout('-b', branch_name)
        return f"Branch '{branch_name}' created and switched."
    except Exception as e:
        return f"Error creating branch: {str(e)}"

@mcp.tool()
def checkout_branch(repo_path: str, branch_name: str) -> str:
    """
    Switch to a different branch in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        branch_name: Name of the branch to checkout
    """
    try:
        repo = get_or_init_repo(repo_path)
        if branch_name not in [h.name for h in repo.heads]:
            return f"Branch '{branch_name}' does not exist."
        repo.git.checkout(branch_name)
        return f"Switched to branch '{branch_name}'."
    except Exception as e:
        return f"Error checking out branch: {str(e)}"

@mcp.tool()
def list_branches(repo_path: str) -> list[str]:
    """
    List all branches in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
    """
    try:
        repo = get_or_init_repo(repo_path)
        return [head.name for head in repo.heads]
    except Exception as e:
        return [f"Error listing branches: {str(e)}"]

@mcp.tool()
def list_commits(repo_path: str, branch: str = "main", count: int = 5) -> list[dict]:
    """
    List recent commits in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        branch: Branch to list commits from (default: main)
        count: Maximum number of commits to list (default: 5)
    """
    try:
        repo = get_or_init_repo(repo_path)
        return [{
            "message": commit.message.strip(),
            "author": commit.author.name,
            "date": commit.committed_datetime.isoformat()
        } for commit in repo.iter_commits(branch, max_count=count)]
    except Exception as e:
        return [{"error": f"Error listing commits: {str(e)}"}]

@mcp.tool()
def read_file(repo_path: str, file_path: str) -> str:
    """
    Read the contents of a file in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        file_path: Path of the file to read, relative to the repo root
    """
    try:
        full_path = os.path.join(repo_path, file_path)
        if not os.path.isfile(full_path):
            return f"File '{file_path}' does not exist."
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return f"File '{file_path}' appears to be a binary file and cannot be read as text."
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def add_all_changes(repo_path: str) -> str:
    """
    Stage all changes in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
    """
    try:
        repo = get_or_init_repo(repo_path)
        repo.git.add(all=True)
        return "All changes have been staged successfully."
    except GitCommandError as e:
        return f"Error staging changes: {e}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def commit_changes(repo_path: str, message: str) -> str:
    """
    Commit staged changes in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        message: Commit message
    """
    try:
        repo = get_or_init_repo(repo_path)
        if repo.index.diff("HEAD") or repo.untracked_files:
            repo.index.commit(message)
            return f"Changes have been committed with message: '{message}'"
        return "No changes to commit."
    except GitCommandError as e:
        return f"Error committing changes: {e}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def push_changes_local(repo_path: str, remote_name: str = "origin", branch: str = None, set_upstream: bool = True) -> str:
    """
    Push committed changes to a remote Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        remote_name: Name of the remote (default: origin)
        branch: Branch to push (default: current branch)
        set_upstream: Whether to set the upstream tracking (default: True)
    """
    try:
        repo = get_or_init_repo(repo_path)
        if not repo.remotes:
            return "Error: No remote configured for this repository."
            
        if branch is None:
            try:
                branch = repo.active_branch.name
            except TypeError:
                return "Error: Repository is in detached HEAD state and no branch specified."
        
        # Get the remote object
        try:
            remote = repo.remote(name=remote_name)
        except ValueError:
            return f"Error: Remote '{remote_name}' does not exist."
        
        # Push with -u flag if set_upstream is True
        if set_upstream:
            push_infos = remote.push(refspec=f"{branch}:{branch}", u=True)
        else:
            push_infos = remote.push(refspec=f"{branch}:{branch}")
            
        # Check for errors in push_info
        for info in push_infos:
            if info.flags & info.ERROR:
                return f"Error pushing to {remote_name}/{branch}: {info.summary}"
                
        if set_upstream:
            return f"Changes pushed and upstream tracking set for {remote_name}/{branch}."
        else:
            return f"Changes pushed to {remote_name}/{branch}."
            
    except GitCommandError as e:
        error_msg = str(e)
        if "rejected" in error_msg and "non-fast-forward" in error_msg:
            return f"Push rejected (non-fast-forward). Try pulling first or use force push."
        elif "Permission denied" in error_msg:
            return f"Permission denied. Check your credentials and repository access."
        else:
            return f"Git error during push: {error_msg}"
    except Exception as e:
        return f"Error: {str(e)}"
    
@mcp.tool()
def diff_file(repo_path: str, file_path: str) -> str:
    """
    Get the diff for a specific file in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        file_path: Path of the file to diff, relative to the repo root
    """
    try:
        repo = get_or_init_repo(repo_path)
        full_path = os.path.join(repo_path, file_path)
        if not os.path.exists(full_path):
            return f"Error: File '{file_path}' does not exist."
        
        return repo.git.diff(file_path)
    except Exception as e:
        return f"Error getting diff: {str(e)}"

@mcp.tool()
def merge_branch(repo_path: str, source_branch: str, target_branch: str = None) -> str:
    """
    Merge one branch into another in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        source_branch: Branch to merge from
        target_branch: Branch to merge into (default: current branch)
    """
    try:
        repo = get_or_init_repo(repo_path)
        
        # If no target branch specified, use current branch
        if target_branch is None:
            try:
                target_branch = repo.active_branch.name
            except TypeError:
                return "Error: Repository is in detached HEAD state and no target branch specified."
        
        # Check if branches exist
        existing_branches = [h.name for h in repo.heads]
        if source_branch not in existing_branches:
            return f"Error: Source branch '{source_branch}' does not exist."
        if target_branch not in existing_branches:
            return f"Error: Target branch '{target_branch}' does not exist."
            
        # Checkout target branch first
        repo.git.checkout(target_branch)
        
        # Perform the merge
        result = repo.git.merge(source_branch)
        return f"Merged '{source_branch}' into '{target_branch}': {result}"
    except GitCommandError as e:
        if "CONFLICT" in str(e):
            return f"Merge conflict occurred: {str(e)}. Please resolve conflicts manually."
        return f"Git error during merge: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def abort_merge(repo_path: str) -> str:
    """
    Abort an ongoing merge operation in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
    """
    try:
        repo = get_or_init_repo(repo_path)
        repo.git.merge("--abort")
        return "Merge aborted successfully."
    except GitCommandError as e:
        if "CONFLICT" in str(e):
            return f"Could not abort merge: {str(e)}"
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def revert_commit(repo_path: str, commit_hash: str) -> str:
    """
    Revert a specific commit in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        commit_hash: Hash of the commit to revert
    """
    try:
        repo = get_or_init_repo(repo_path)
        repo.git.revert(commit_hash, no_edit=True)
        return f"Commit {commit_hash} has been reverted."
    except GitCommandError as e:
        return f"Git error during revert: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def reset_to_commit(repo_path: str, commit_hash: str, hard: bool = False) -> str:
    """
    Reset the repository to a specific commit.
    
    Args:
        repo_path: Path to the local repository directory
        commit_hash: Hash of the commit to reset to
        hard: Whether to perform a hard reset (default: False)
    """
    try:
        repo = get_or_init_repo(repo_path)
        reset_type = "--hard" if hard else "--mixed"
        repo.git.reset(reset_type, commit_hash)
        return f"Repository reset to commit {commit_hash} ({reset_type})."
    except GitCommandError as e:
        return f"Git error during reset: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def stash_changes(repo_path: str, include_untracked: bool = False) -> str:
    """
    Stash uncommitted changes in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        include_untracked: Whether to include untracked files (default: False)
    """
    try:
        repo = get_or_init_repo(repo_path)
        if include_untracked:
            result = repo.git.stash("save", "--include-untracked")
        else:
            result = repo.git.stash("save")
        if "No local changes to save" in result:
            return "No changes to stash."
        return f"Changes stashed successfully: {result}"
    except GitCommandError as e:
        return f"Git error during stash: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def apply_stash(repo_path: str, stash_id: str = "stash@{0}") -> str:
    """
    Apply a stashed change in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        stash_id: ID of the stash to apply (default: most recent)
    """
    try:
        repo = get_or_init_repo(repo_path)
        repo.git.stash("apply", stash_id)
        return f"Stash {stash_id} applied successfully."
    except GitCommandError as e:
        return f"Git error applying stash: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_stashes(repo_path: str) -> list[dict]:
    """
    List all stashes in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
    """
    try:
        repo = get_or_init_repo(repo_path)
        stash_list = repo.git.stash("list").splitlines()
        if not stash_list:
            return [{"message": "No stashes found."}]
            
        stashes = []
        for stash in stash_list:
            parts = stash.split(": ", 1)
            if len(parts) == 2:
                stashes.append({
                    "id": parts[0],
                    "description": parts[1]
                })
                
        return stashes
    except Exception as e:
        return [{"error": f"Error listing stashes: {str(e)}"}]

@mcp.tool()
def fetch_all(repo_path: str) -> str:
    """
    Fetch updates from all remotes in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
    """
    try:
        repo = get_or_init_repo(repo_path)
        if not repo.remotes:
            return "No remotes found for this repository."
            
        for remote in repo.remotes:
            remote.fetch()
            
        return f"Successfully fetched updates from all {len(repo.remotes)} remotes."
    except GitCommandError as e:
        return f"Git error during fetch: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_config(repo_path: str, config_name: str) -> str:
    """
    Get a Git configuration value.
    
    Args:
        repo_path: Path to the local repository directory
        config_name: Name of the configuration to get (e.g., "user.name")
    """
    try:
        repo = get_or_init_repo(repo_path)
        value = repo.git.config(config_name)
        return f"{config_name} = {value}"
    except GitCommandError:
        return f"Configuration '{config_name}' not found."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_config(repo_path: str, config_name: str, value: str) -> str:
    """
    Set a Git configuration value.
    
    Args:
        repo_path: Path to the local repository directory
        config_name: Name of the configuration to set (e.g., "user.name")
        value: Value to set
    """
    try:
        repo = get_or_init_repo(repo_path)
        repo.git.config(config_name, value)
        return f"Configuration '{config_name}' set to '{value}'."
    except Exception as e:
        return f"Error setting configuration: {str(e)}"

@mcp.tool()
def create_tag(repo_path: str, tag_name: str, message: str = None, commit: str = "HEAD") -> str:
    """
    Create a new tag in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        tag_name: Name of the tag to create
        message: Tag message (default: None for lightweight tag)
        commit: Commit to tag (default: HEAD)
    """
    try:
        repo = get_or_init_repo(repo_path)
        
        if message:
            # Create annotated tag
            repo.git.tag("-a", tag_name, commit, "-m", message)
        else:
            # Create lightweight tag
            repo.git.tag(tag_name, commit)
            
        return f"Tag '{tag_name}' created successfully."
    except GitCommandError as e:
        return f"Git error creating tag: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def delete_tag(local_repo_path: str, tag_name: str) -> str:
    """
    Delete a tag in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
        tag_name: Name of the tag to delete
    """
    try:
        repo = get_or_init_repo(local_repo_path)
        repo.git.tag("-d", tag_name)
        return f"Tag '{tag_name}' deleted."
    except GitCommandError as e:
        return f"Git error deleting tag: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_tags(local_repo_path: str) -> list[str]:
    """
    List all tags in a Git repository.
    
    Args:
        repo_path: Path to the local repository directory
    """
    try:
        repo = get_or_init_repo(local_repo_path)
        return repo.git.tag().splitlines()
    except Exception as e:
        return [f"Error listing tags: {str(e)}"]

@mcp.tool()
def rebase_branch(local_repo_path: str, onto_branch: str) -> str:
    """
    Rebase current branch onto another branch.
    
    Args:
        repo_path: Path to the local repository directory
        onto_branch: Branch to rebase onto
    """
    try:
        repo = get_or_init_repo(local_repo_path)
        current_branch = repo.active_branch.name
        repo.git.rebase(onto_branch)
        return f"Successfully rebased '{current_branch}' onto '{onto_branch}'."
    except GitCommandError as e:
        if "CONFLICT" in str(e):
            return f"Rebase conflict occurred: {str(e)}. Please resolve conflicts manually."
        return f"Git error during rebase: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def abort_rebase(local_repo_path: str) -> str:
    """
    Abort an ongoing rebase operation.
    
    Args:
        repo_path: Path to the local repository directory
    """
    try:
        repo = get_or_init_repo(local_repo_path)
        repo.git.rebase("--abort")
        return "Rebase aborted successfully."
    except GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
    
@mcp.tool()
def push_to_github(local_repo_path: str, branch: str = None) -> str:
    """
    Push committed changes to GitHub using 'git push -u origin <branch-name>'.
    
    Args:
        repo_path: Path to the local repository directory
        branch: Branch to push (default: current branch)
    """
    try:
        repo = get_or_init_repo(local_repo_path)
        
        # Check if remote exists
        if not repo.remotes or 'origin' not in [r.name for r in repo.remotes]:
            return "Error: No 'origin' remote configured. Set a GitHub remote first."
            
        # Get current branch if not specified
        if branch is None:
            try:
                branch = repo.active_branch.name
            except TypeError:
                return "Error: Repository is in detached HEAD state and no branch specified."
        
        # Execute the equivalent of 'git push -u origin <branch-name>'
        result = repo.git.push('origin', branch, '-u')
        return f"Successfully pushed to GitHub: {branch} → origin/{branch}\n{result}"
            
    except GitCommandError as e:
        error_msg = str(e)
        if "rejected" in error_msg and "non-fast-forward" in error_msg:
            return "Push rejected by GitHub (non-fast-forward). Try pulling first with 'git pull origin'."
        elif "Permission denied" in error_msg:
            return "GitHub authentication failed. Check your credentials or SSH keys."
        else:
            return f"GitHub push error: {error_msg}"
    except Exception as e:
        return f"Error pushing to GitHub: {str(e)}"

if __name__ == "__main__":
    # For local development with `mcp dev`
    print("Starting Git MCP server...")
    
    # With proper host and port configuration to avoid conflicts
    if "mcp dev" in " ".join(sys.argv):
        mcp.serve(host="127.0.0.1", port=5000)
    else:
        # Standard serve for regular use
        mcp.serve()