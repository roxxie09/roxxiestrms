import json
import re
from pathlib import Path

def extract_events_and_links(text):
    """
    Parse the input text and extract event -> link mappings.
    Assumes lines in the form:
    Event Name: [URL](URL)
    or Event Name: http(s)://...
    Returns an ordered dict of event -> first seen link.
    """
    events = []
    mapping = {}

    # Normalize newlines
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to capture "Event: [link](link)" style
        m = re.match(r'^(.+?):\s*\[(https?://[^\s\]]+)\]', line)
        if m:
            event = m.group(1).strip()
            url = m.group(2).strip()
        else:
            # Try "Event: https://..." style
            m = re.match(r'^(.+?):\s*(https?://\S+)', line)
            if m:
                event = m.group(1).strip()
                url = m.group(2).strip().rstrip(' ,')
            else:
                continue  # skip lines that don't match

        # Deduplicate by keeping the first occurrence
        if event not in mapping:
            mapping[event] = url

    # Preserve insertion order
    return mapping

def main():
    input_path = Path("G:/MY LEGIT EVERYTHING FOLDER/RANDOM/RANDOM/roxxiestrms/events.txt")
    # If the path above doesn't exist on the running system, try a relative path or ask the user.
    if not input_path.exists():
        # Fallback: read a local copy named events.txt in current directory
        alt = Path("events.txt")
        if alt.exists():
            input_path = alt
        else:
            raise SystemExit("Could not find the input file at the expected path.")

    text = input_path.read_text(encoding="utf-8")

    mapping = extract_events_and_links(text)

    # Output JSON
    output = mapping
    print(json.dumps(output, indent=2, ensure_ascii=False))

    # Optional: write to a file
    # Path("events.json").write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    main()
