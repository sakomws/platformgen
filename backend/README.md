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
           "repo_name": "platformgen"
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
     -d '{
           "dependencies": {
             "requests": "2.25.1",
             "fastapi": "0.70.0",
             "numpy": null
           }
         }'
```
5. Generate updated file:
```
curl -X POST "http://127.0.0.1:8000/generate_updated_requirements" \
     -H "Content-Type: application/json" \
     -d '{
           "dependencies": {
             "requests": "2.25.1",
             "fastapi": "0.70.0",
             "numpy": null
           },
           "updates": {
             "requests": {
               "current": "2.25.1",
               "latest": "2.31.0"
             },
             "fastapi": {
               "current": "0.70.0",
               "latest": "0.95.2"
             },
             "numpy": {
               "current": null,
               "latest": "1.24.3"
             }
           }
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