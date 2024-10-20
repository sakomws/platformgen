from github import Github, Auth
from fastapi import FastAPI, HTTPException, Header
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import requests
from packaging import version
import logging

# Load environment variables
load_dotenv()

# Create authentication object using an access token
auth = Auth.Token(os.getenv("GITHUB_TOKEN"))

# Create FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request bodies
class RequirementsText(BaseModel):
    requirements_text: str

class PackageName(BaseModel):
    package_name: str

class DependenciesModel(BaseModel):
    dependencies: dict

class UpdatesModel(BaseModel):
    dependencies: dict
    updates: dict

class CommitInfo(BaseModel):
    owner: str
    repo_name: str
    branch_name: str
    file_path: str
    updated_content: str
    original_sha: str

class PullRequestInfo(BaseModel):
    owner: str
    repo_name: str
    branch_name: str

@app.get("/repos")
async def list_repos():
    # Check if the token is loaded correctly
    if not auth.token:
        raise HTTPException(status_code=500, detail="GitHub token is not loaded. Please check your .env file.")

    # Create a GitHub instance
    g = Github(auth=auth)

    try:
        # Retrieve and return repository names
        repos = [repo.name for repo in g.get_user().get_repos()]
        return {"repositories": repos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Ensure the connection is closed
        g.close()


# API Endpoints

@app.post("/parse_requirements")
def api_parse_requirements(req: RequirementsText):
    try:
        dependencies = parse_requirements(req.requirements_text)
        return {"dependencies": dependencies}
    except Exception as e:
        logger.error(f"Error parsing requirements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_latest_version")
def api_get_latest_version(pkg: PackageName):
    try:
        latest_version = get_latest_version(pkg.package_name)
        if latest_version:
            return {"package_name": pkg.package_name, "latest_version": latest_version}
        else:
            raise HTTPException(status_code=404, detail="Package not found")
    except Exception as e:
        logger.error(f"Error fetching latest version: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_for_updates")
def api_check_for_updates(deps: DependenciesModel):
    try:
        updates = check_for_updates(deps.dependencies)
        return {"updates": updates}
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_updated_requirements")
def api_generate_updated_requirements(data: UpdatesModel):
    try:
        updated_requirements = generate_updated_requirements(
            data.dependencies, data.updates)
        return {"updated_requirements": updated_requirements}
    except Exception as e:
        logger.error(f"Error generating updated requirements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/commit_changes")
def api_commit_changes(info: CommitInfo, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header missing")
    try:
        token = authorization.split(" ")[1]
        g = Github(token)
        repo = g.get_repo(f"{info.owner}/{info.repo_name}")
        commit_changes(
            repo,
            info.branch_name,
            info.file_path,
            info.updated_content,
            info.original_sha
        )
        return {"message": "Changes committed successfully"}
    except Exception as e:
        logger.error(f"Error committing changes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_pull_request")
def api_create_pull_request(pr_info: PullRequestInfo, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header missing")
    try:
        token = authorization.split(" ")[1]
        g = Github(token)
        repo = g.get_repo(f"{pr_info.owner}/{pr_info.repo_name}")
        pr = create_pull_request(repo, pr_info.branch_name)
        return {"message": "Pull request created", "pull_request_url": pr.html_url}
    except Exception as e:
        logger.error(f"Error creating pull request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Function Definitions

def parse_requirements(requirements_text):
    dependencies = {}
    for line in requirements_text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            if "==" in line:
                name, current_version = line.split("==")
                dependencies[name.strip()] = current_version.strip()
            else:
                dependencies[line.strip()] = None
    return dependencies

def get_latest_version(package_name):
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    if response.ok:
        data = response.json()
        return data["info"]["version"]
    else:
        logger.error(f"Failed to fetch version for {package_name}")
        return None

def check_for_updates(dependencies):
    updates = {}
    for package, current_version in dependencies.items():
        latest_version = get_latest_version(package)
        if latest_version:
            if current_version is None or version.parse(latest_version) > version.parse(current_version):
                updates[package] = {
                    "current": current_version,
                    "latest": latest_version
                }
    return updates

def generate_updated_requirements(dependencies, updates):
    updated_lines = []
    for package, current_version in dependencies.items():
        if package in updates:
            new_version = updates[package]["latest"]
            updated_lines.append(f"{package}=={new_version}")
        elif current_version:
            updated_lines.append(f"{package}=={current_version}")
        else:
            updated_lines.append(package)
    return "\n".join(updated_lines)

def commit_changes(repo, branch_name, file_path, updated_content, original_sha):
    base = repo.get_branch(repo.default_branch)
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base.commit.sha)
    logger.info(f"Created new branch {branch_name}")
    repo.update_file(
        path=file_path,
        message="Update dependencies",
        content=updated_content,
        sha=original_sha,
        branch=branch_name
    )
    logger.info(f"Committed changes to {file_path} on branch {branch_name}")

def create_pull_request(repo, branch_name):
    pr = repo.create_pull(
        title="Update dependencies to latest versions",
        body="This PR updates the dependencies to their latest versions.",
        head=branch_name,
        base=repo.default_branch
    )
    logger.info(f"Created pull request {pr.html_url}")
    return pr