from github import Github, Auth
from fastapi import FastAPI, HTTPException, Header
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import requests
from packaging import version
import logging
from typing import Optional
import random
import string
from fastapi.middleware.cors import CORSMiddleware
import openai
from groq import Groq

# Load environment variables
load_dotenv()

# Create authentication object using an access token
auth = Auth.Token(os.getenv("GITHUB_TOKEN"))
# Initialize GitHub client using token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
github_client = Github(GITHUB_TOKEN)
# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


# Create FastAPI app
app = FastAPI()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL, e.g., "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the Pydantic model for the request body
class RepoInfo(BaseModel):
    owner: str
    repo_name: str
    file_path: Optional[str] = "requirements.txt"

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

class DiffRequest(BaseModel):
    original_requirements: str
    updated_requirements: str

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
def api_parse_requirements(req: RepoInfo):
    try:
        requirements_text = fetch_requirements_from_github(req.owner, req.repo_name, req.file_path)
        dependencies = parse_requirements(requirements_text)
        return {"dependencies": dependencies}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
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

def fetch_requirements_from_github(owner: str, repo_name: str, file_path: str = "requirements.txt"):
    try:
        repo = github_client.get_repo(f"{owner}/{repo_name}")
        file_content = repo.get_contents(file_path).decoded_content.decode("utf-8")
        return file_content
    except Exception as e:
        if "404" in str(e):
            logger.error(f"Failed to fetch file from GitHub: {e}. File path '{file_path}' might be incorrect.")
            raise HTTPException(status_code=404, detail="404: Could not find the specified file in the repository. Please check the file path.")
        else:
            logger.error(f"Error accessing GitHub repository: {e}")
            raise HTTPException(status_code=500, detail="Error accessing the repository or fetching file.")

def parse_requirements(requirements_text: str):
    dependencies = {}
    for line in requirements_text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if "==" in line:
            package, version = line.split("==")
            dependencies[package.strip()] = version.strip()
        else:
            dependencies[line] = None
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


def generate_random_branch_name(prefix="update-dependencies-"):
    # Generate a random alphanumeric string
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}{random_id}"

@app.post("/run_all")
def run_all_actions(repo_info: RepoInfo):
    try:
        # 1. List Repositories (for demo purposes, assume authenticated user)
        user = github_client.get_user()
        repos = [repo.name for repo in user.get_repos()]
        
        # 2. Fetch & Parse requirements.txt
        requirements_text = fetch_requirements_from_github(repo_info.owner, repo_info.repo_name)
        dependencies = parse_requirements(requirements_text)
        
        # 3. Check for Updates
        updates = check_for_updates(dependencies)

        # 4. Generate Updated requirements.txt
        updated_content = generate_updated_requirements(dependencies, updates)

        # 5. Create or Checkout a Random Branch
        repo = github_client.get_repo(f"{repo_info.owner}/{repo_info.repo_name}")
        branch_name = generate_random_branch_name()

        # Check if branch exists, if not, create one
        try:
            repo.get_branch(branch_name)
        except Exception:
            # Get the SHA of the default branch (e.g., main)
            source_branch = repo.get_branch("main")
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source_branch.commit.sha)

        # Commit Changes
        file = repo.get_contents("requirements.txt", ref="main")
        repo.update_file(
            "requirements.txt",
            "Update dependencies",
            updated_content,
            file.sha,
            branch=branch_name
        )
        
        # 6. Create Pull Request
        pr = repo.create_pull(
            title="Update dependencies",
            body="Automated update of dependencies",
            head=branch_name,
            base="main"
        )

        # 7. Generate Diff Summary using OpenAI
        diff_summary = get_diff_summary(
            DiffRequest(
                original_requirements=requirements_text,
                updated_requirements=updated_content
            )
        ).get("summary", "No summary available.")

        # Return the result
        return {
            "repositories": repos,
            "parsed_dependencies": dependencies,
            "updates": updates,
            "updated_requirements": updated_content,
            "diff_summary": diff_summary,
            "pr_link": pr.html_url
        }

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/diff_summary")
def get_diff_summary(diff_request: DiffRequest):
    try:
        # Prepare prompt
        prompt = f"""
        Compare the following two sets of requirements and provide a summary of the differences:
        
        Original Requirements:
        {diff_request.original_requirements}
        
        Updated Requirements:
        {diff_request.updated_requirements}
        
        Summary:
        """

        # 1. Call OpenAI ChatCompletion
        openai_summary = ""
        try:
            openai_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that compares software package requirements. Return a summary of the differences between the original and updated requirements."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.7,
            )
            openai_summary = openai_response.choices[0].message["content"].strip()
        except Exception as e:
            logger.error(f"Failed to generate summary with OpenAI: {e}")
            openai_summary = "Failed to generate summary with OpenAI."

        # 2. Call Groq Llama 3.2 Model
        groq_summary = ""
        try:
            client = Groq()  # Assuming Groq client is already set up
            completion = client.chat.completions.create(
                model="llama-3.2-3b-preview",
                messages=[
                    {"role": "system", "content": "You are an assistant that compares software package requirements. Return a summary of the differences between the original and updated requirements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            # Safely attempt to extract content from Groq response
            if completion.choices and len(completion.choices) > 0:
                groq_summary = getattr(completion.choices[0].message, "content", "").strip()
            else:
                groq_summary = "No response from Groq."
        except Exception as e:
            logger.error(f"Failed to generate summary with Groq: {e}")
            groq_summary = "Failed to generate summary with Groq."

        # Combine OpenAI and Groq summaries
        combined_summary = f"### OpenAI Summary:\n{openai_summary}\n\n### Llama 3.2 Summary:\n{groq_summary}"
        
        return {"summary": combined_summary}

    except Exception as e:
        logger.error(f"Failed to generate diff summary: {e}")
        return {"summary": "Failed to generate summary due to an error."}



