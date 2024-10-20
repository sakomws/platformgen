import requests
from bs4 import BeautifulSoup

def read_updates_available(file_path="updates_available.txt"):
    """Read the updates available from the file."""
    updates = {}
    current_package = None
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line.endswith(":"):
                current_package = line[:-1]
                updates[current_package] = []
            elif line.startswith("- "):
                updates[current_package].append(line.split("==")[1])
    return updates

def get_page_text(package, version):
    """Fetch the entire page text for a specific package version."""
    url = f"https://pypi.org/project/{package}/{version}/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text()
    return None

def main():
    updates = read_updates_available()
    with open("version_updates_tldr.txt", "w", encoding="utf-8") as outfile:
        for package, versions in updates.items():
            print(f"Processing {package}...")
            for version in versions:
                page_text = get_page_text(package, version)
                if page_text:
                    outfile.write(f"{'='*80}\n")
                    outfile.write(f"{package} {version}:\n")
                    outfile.write(f"{'='*80}\n\n")
                    outfile.write(page_text)
                    outfile.write("\n\n")
                else:
                    print(f"Could not fetch page for {package} {version}")

    print("Version update summaries have been written to 'version_updates_tldr.txt'")

if __name__ == "__main__":
    main()