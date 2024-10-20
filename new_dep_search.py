import requests
import re
from packaging import version

def read_dependencies(file_path="project_dep"):
    """Read dependencies from the project_dep file."""
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

def search_brave(query):
    """Search for the newest version of a dependency using Brave Search API."""
    api_key = "Enter key"  # Replace with your actual Brave Search API key
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"X-Subscription-Token": api_key}
    params = {"q": f"{query} all versions pypi"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json().get("web", {}).get("results", [])
        if results:
            # Extract all versions from the first result's title or description
            version_matches = re.findall(r'\d+(\.\d+)+', results[0].get("title", "") + results[0].get("description", ""))
            if version_matches:
                # Filter out invalid versions before parsing
                valid_versions = []
                for v in version_matches:
                    try:
                        version.parse(v)
                        valid_versions.append(v)
                    except version.InvalidVersion:
                        continue
                return sorted(set(valid_versions), key=version.parse, reverse=True)
    return None

def write_to_file(filename, content):
    """Write content to a file."""
    with open(filename, "w") as file:
        file.write(content)

def main():
    dependencies = read_dependencies()
    up_to_date = []
    updates_available = {}

    for dep in dependencies:
        parts = dep.split("==")
        if len(parts) == 2:
            name, current_version = parts
            all_versions = search_brave(name)
            
            if all_versions:
                latest_version = all_versions[0]
                if version.parse(current_version) == version.parse(latest_version):
                    up_to_date.append(dep)
                else:
                    updates_available[name] = [v for v in all_versions if version.parse(v) > version.parse(current_version)]
        else:
            # Handle dependencies without version specification
            name = dep
            all_versions = search_brave(name)
            if all_versions:
                updates_available[name] = all_versions

    # Write up-to-date dependencies to a file
    if up_to_date:
        up_to_date_content = "Dependencies up to date:\n" + "\n".join(f"- {dep}" for dep in up_to_date)
        write_to_file("up_to_date_dependencies.txt", up_to_date_content)

    # Write updates available to a file
    if updates_available:
        updates_content = "Updates available:\n"
        for name, versions in updates_available.items():
            updates_content += f"{name}:\n"
            for ver in versions:
                updates_content += f"- {name}=={ver}\n"
            updates_content += "\n"
        write_to_file("updates_available.txt", updates_content)

    print("Results have been written to 'up_to_date_dependencies.txt' and 'updates_available.txt'.")

if __name__ == "__main__":
    main()