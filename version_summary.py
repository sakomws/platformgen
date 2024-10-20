import os
from openai import OpenAI

client = OpenAI(api_key="Enter key")

def read_version_updates(file_path="version_updates_tldr.txt"):
    """Read the version updates from the file."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content.split("=" * 80)

#TODO: switch over to 3.2 3B 
def summarize_text(text, max_tokens=150):
    """Summarize the given text using OpenAI's GPT model."""
    prompt = f"Summarize the following text concisely:\n\n{text}\n\nSummary:"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        n=1,
        temperature=0.7,
    )
    
    summary = response.choices[0].message.content.strip()
    return summary

def main():
    # Read version updates
    print("Reading version updates...")
    updates = read_version_updates()
    
    # Summarize updates
    print("Summarizing updates...")
    summaries = []
    for update in updates:
        if update.strip():
            package_info = update.split("\n")[1]  # Get package and version info
            if not package_info.startswith("undefined"):
                summary = summarize_text(update)
                summaries.append(f"{package_info}\n{summary}\n")
    
    # Write summaries to file
    print("Writing summaries to file...")
    with open("new_version_updates_summary.txt", "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(summaries))
    
    print("Summaries have been written to 'new_version_updates_summary.txt'")

if __name__ == "__main__":
    main()