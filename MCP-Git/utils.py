from git import Repo
import os

def get_or_init_repo(path: str) -> Repo:
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        return Repo(path)
    except:
        return Repo.init(path)

def setup_remote(repo: Repo, url: str):
    if "origin" in repo.remotes:
        repo.delete_remote("origin")
    repo.create_remote("origin", url)

def stage_commit_push(repo: Repo, file_path: str, message: str, remote: str = "origin", branch: str = "main") -> str:
    try:
        repo.git.add(file_path)
        repo.index.commit(message)
        repo.remotes[remote].push(branch)
        return f"Committed and pushed {file_path} to {branch}."
    except Exception as e:
        return f"Error during commit/push: {str(e)}"
