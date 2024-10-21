# FastAPI Application for Managing Python Package Dependencies

This FastAPI application provides several API endpoints to manage Python package dependencies in GitHub repositories. It allows you to parse `requirements.txt`, check for updates, generate updated requirements, commit changes to a repository, and create pull requests.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [API Endpoints](#api-endpoints)
  - [GET /repos](#get-repos)
  - [POST /parse_requirements](#post-parse_requirements)
  - [POST /get_latest_version](#post-get_latest_version)
  - [POST /check_for_updates](#post-check_for_updates)
  - [POST /generate_updated_requirements](#post-generate_updated_requirements)
  - [POST /commit_changes](#post-commit_changes)
  - [POST /create_pull_request](#post-create_pull_request)
- [Running the Application](#running-the-application)
- [Examples Using curl](#examples-using-curl)
- [Important Notes](#important-notes)
- [Additional Information](#additional-information)
- [License](#license)
- [Contact](#contact)

## Prerequisites
- Python 3.7 or higher
- GitHub Personal Access Token with appropriate permissions
- pip installed packages:
  - `fastapi`
  - `uvicorn`
  - `python-dotenv`
  - `PyGithub`
  - `requests`
  - `packaging`

## Setup
1. Clone the repository or copy the code into a directory.
2. Install the required packages:
   ```bash
   pip install fastapi uvicorn python-dotenv PyGithub requests packaging

3. Create a .env file in the root directory and add your GitHub token:
```
GITHUB_TOKEN=your_github_personal_access_token
```

API Endpoints
1. GET list of user repos:
Description: Retrieves a list of repositories associated with the authenticated GitHub user.
```
curl -X GET "http://127.0.0.1:8000/repos"
```

2. Parse requirements:
``` 
curl -X POST "http://127.0.0.1:8000/parse_requirements" \
     -H "Content-Type: application/json" \
     -d '{
           "owner": "sakomws",
           "repo_name": "aiproxy"
         }'
```

3. Get latest version:
```
curl -X POST "http://127.0.0.1:8000/get_latest_version" \
     -H "Content-Type: application/json" \
     -d '{"package_name": "fastapi"}'
```

4. Check for updates:
```
curl -X POST "http://127.0.0.1:8000/check_for_updates" \
     -H "Content-Type: application/json" \
     -d '{"dependencies":{"fastapi":null,"uvicorn":null,"openai":null,"python-dotenv":null,"typing_extensions":null,"requests":"2.32.2","pandas":null,"numpy":null,"textgrad":null,"asyncio":null,"together":null,"fire":null,"loguru":null,"datasets":null,"typer":null,"rich":null,"pydantic":null,"groq":null,"langchain_groq":null,"llama_parse":null,"langchain":null,"nest_asyncio":null,"fastembed":null,"unstructured":null,"markdown":null,"langchain_community":null,"arize-phoenix[evals]":null,"mem0ai":null}}'
```
5. Generate updated file:
```
curl -X POST "http://127.0.0.1:8000/generate_updated_requirements" \
     -H "Content-Type: application/json" \
     -d '{"dependencies":{"fastapi":null,"uvicorn":null,"openai":null,"python-dotenv":null,"typing_extensions":null,"requests":"2.32.2","pandas":null,"numpy":null,"textgrad":null,"asyncio":null,"together":null,"fire":null,"loguru":null,"datasets":null,"typer":null,"rich":null,"pydantic":null,"groq":null,"langchain_groq":null,"llama_parse":null,"langchain":null,"nest_asyncio":null,"fastembed":null,"unstructured":null,"markdown":null,"langchain_community":null,"arize-phoenix[evals]":null,"mem0ai":null}},
           {"updates":{"fastapi":{"current":null,"latest":"0.115.2"},"uvicorn":{"current":null,"latest":"0.32.0"},"openai":{"current":null,"latest":"1.52.0"},"python-dotenv":{"current":null,"latest":"1.0.1"},"typing_extensions":{"current":null,"latest":"4.12.2"},"requests":{"current":"2.32.2","latest":"2.32.3"},"pandas":{"current":null,"latest":"2.2.3"},"numpy":{"current":null,"latest":"2.1.2"},"textgrad":{"current":null,"latest":"0.1.5"},"asyncio":{"current":null,"latest":"3.4.3"},"together":{"current":null,"latest":"1.3.3"},"fire":{"current":null,"latest":"0.7.0"},"loguru":{"current":null,"latest":"0.7.2"},"datasets":{"current":null,"latest":"3.0.1"},"typer":{"current":null,"latest":"0.12.5"},"rich":{"current":null,"latest":"13.9.2"},"pydantic":{"current":null,"latest":"2.9.2"},"groq":{"current":null,"latest":"0.11.0"},"langchain_groq":{"current":null,"latest":"0.2.0"},"llama_parse":{"current":null,"latest":"0.5.10"},"langchain":{"current":null,"latest":"0.3.4"},"nest_asyncio":{"current":null,"latest":"1.6.0"},"fastembed":{"current":null,"latest":"0.3.6"},"unstructured":{"current":null,"latest":"0.16.0"},"markdown":{"current":null,"latest":"3.7"},"langchain_community":{"current":null,"latest":"0.3.3"},"mem0ai":{"current":null,"latest":"0.1.21"}}}
         }'
```
6. Commit changes:
```
curl -X POST "http://127.0.0.1:8000/commit_changes" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer X" \
     -d '{
           "owner": "sakomws",
           "repo_name": "platformgen",
           "branch_name": "update-dependencies",
           "file_path": "requirements.txt",
           "updated_content": "requests==2.31.0\nfastapi==0.95.2\nnumpy==1.24.3",
           "original_sha": "original_file_sha"
         }'
```

7. Create PR:
```
curl -X POST "http://127.0.0.1:8000/create_pull_request" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <GITHUB_TOKEN>" \
     -d '{
           "owner": "your_github_username",
           "repo_name": "your_repository_name",
           "branch_name": "update-dependencies"
         }'
```


curl -X POST "http://127.0.0.1:8000/run_all" \
     -H "Content-Type: application/json" \
     -d '{
           "owner": "sakomws",
           "repo_name": "aiproxy"
         }'





source venv/bin/activate