import re
from pathlib import Path

# Define abbreviation to canonical full name mapping here.
ABBREVIATION_MAP = {
    "rockets": "houston rockets",
    "thunder": "oklahoma city thunder",
    "warriors": "golden state warriors",
    "lakers": "los angeles lakers",
    # Add other abbreviations as needed
    "olympiakos": "olympiakos piraeus",
    "atlético": "atlético madrid",
    "atletico": "atlético madrid",
    "union sg": "union saint-gilloise",
    "man city": "manchester city",
    "mazatlan": "mazatlán",
    "juarez": "juárez",
}

def extract_events_and_links(text):
    events = {}
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(.+?):\s*\[(https?://[^\s\]]+)\]', line)
        if m:
            event = m.group(1).strip()
            url = m.group(2).strip()
        else:
            m = re.match(r'^(.+?):\s*(https?://\S+)', line)
            if m:
                event = m.group(1).strip()
                url = m.group(2).strip().rstrip(' ,')
            else:
                continue
        if event not in events:
            events[event] = url
    return events

def normalize_team_name(name):
    low = name.lower()
    # Check abbreviation map first
    if low in ABBREVIATION_MAP:
        return ABBREVIATION_MAP[low]
    else:
        return low

def parse_teams_from_event(event):
    for sep in [' vs ', ' @ ', ' vs. ', ' at ']:
        if sep in event.lower():
            sides = event.lower().split(sep)
            return [normalize_team_name(s.strip()) for s in sides]
    # Single team event e.g. "WWE NXT"
    return [normalize_team_name(event)]

def generate_roxie_js(events_dict):
    entries = []
    all_teams = set()
    for event, url in events_dict.items():
        teams = parse_teams_from_event(event)
        teams_sorted = sorted(teams)
        title = " vs ".join(teams_sorted)
        entries.append(f'{{title: "{title}", url: "{url}"}}')
        all_teams.update(teams)
    roxie_js = "const roxieStreamsCached = [\n  " + ",\n  ".join(entries) + "\n];"
    return roxie_js, all_teams

def generate_teammap_js(all_teams):
    mapping_entries = []
    # Canonical names map to themselves
    for team in sorted(all_teams):
        mapping_entries.append(f'"{team}": "{team}"')
    # Add abbreviation mappings only if canonical exists
    for abbr, full_name in ABBREVIATION_MAP.items():
        if full_name in all_teams:
            mapping_entries.append(f'"{abbr}": "{full_name}"')
    team_map_js = "const teamNameMap = {\n  " + ",\n  ".join(mapping_entries) + "\n};"
    return team_map_js

def replace_js_block(js_text, block_name_pattern, new_block_text):
    pattern = re.compile(
        rf'{block_name_pattern}\s*=\s*\[[^\]]*\];' if 'Cached' in block_name_pattern else
        rf'{block_name_pattern}\s*=\s*\{{[^\}}]*\}};',
        re.DOTALL
    )
    if pattern.search(js_text):
        return pattern.sub(new_block_text, js_text)
    else:
        # If block not found, append new block at end
        return js_text + "\n\n" + new_block_text + "\n"

def main():
    events_path = Path("events.txt")
    js_path = Path("watchsport.txt")

    if not events_path.exists():
        raise SystemExit("events.txt not found.")
    if not js_path.exists():
        raise SystemExit("watchsport.txt not found.")

    events_text = events_path.read_text(encoding='utf-8')
    js_text = js_path.read_text(encoding='utf-8')

    events = extract_events_and_links(events_text)
    roxie_js, all_teams = generate_roxie_js(events)
    team_map_js = generate_teammap_js(all_teams)

    updated_js = replace_js_block(js_text, r'const\s+roxieStreamsCached', roxie_js)
    updated_js = replace_js_block(updated_js, r'const\s+teamNameMap', team_map_js)

    js_path.write_text(updated_js, encoding='utf-8')
    print("watchsport.txt updated with latest events and enhanced team abbreviation mappings.")

if __name__ == "__main__":
    main()
