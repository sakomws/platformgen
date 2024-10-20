import os
import re
import argparse
import tempfile
import shutil
from pathlib import Path
import subprocess

def clone_repository(url, target_path):
    """Clone a Git repository to the specified path."""
    try:
        subprocess.run(["git", "clone", url, target_path], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return False
    return True

def find_dependency_file(directory="."):
    """Search for requirements.txt or pyproject.toml in the given directory."""
    for file in ["requirements.txt", "pyproject.toml"]:
        file_path = Path(directory) / file
        if file_path.exists():
            return file_path
    return None

def parse_requirements_txt(file_path):
    """Parse dependencies from requirements.txt file."""
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip() and not line.startswith("#")]

def parse_pyproject_toml(file_path):
    """Parse dependencies from pyproject.toml file."""
    with open(file_path, "r") as file:
        content = file.read()
        dependencies = re.findall(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if dependencies:
            return [dep.strip().strip('"\'') for dep in dependencies[0].split(",") if dep.strip()]
    return []

def format_dependencies(dependencies):
    """Format and deduplicate dependencies."""
    unique_deps = sorted(set(dependencies))
    return "\n".join(dep for dep in unique_deps)

def write_dependencies_to_file(formatted_deps):
    """Write formatted dependencies to a new file."""
    with open("project_dep", "w") as file:
        file.write(formatted_deps)

def main(repo_url):
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Cloning repository: {repo_url}")
        if not clone_repository(repo_url, temp_dir):
            return

        dependency_file = find_dependency_file(temp_dir)
        if not dependency_file:
            print("No dependency file found in the repository.")
            return

        if dependency_file.name == "requirements.txt":
            dependencies = parse_requirements_txt(dependency_file)
        else:  # pyproject.toml
            dependencies = parse_pyproject_toml(dependency_file)

        formatted_deps = format_dependencies(dependencies)
        write_dependencies_to_file(formatted_deps)
        print(f"Dependencies found in {dependency_file.name} and written to project_dep file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse dependencies from a GitHub repository.")
    parser.add_argument("repo_url", help="URL of the GitHub repository")
    args = parser.parse_args()

    main(args.repo_url)