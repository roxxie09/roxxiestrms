import re
import requests
from bs4 import BeautifulSoup

# URL to download the full M3U playlist
M3U_URL = "http://ahostingportal.com:2095/get.php?username=Marky0416&password=Integra1994&type=m3u"

# Local paths – adjust if needed
NFL_HTML_PATH = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nfl.html"
OUTPUT_HTML_PATH = "nfl_with_streams.html"

# Fix naming quirks between HTML and M3U
TEAM_NORMALIZATION_MAP = {
    "dallas cowboys vs new york": "dallas cowboys vs new york giants",
    "new york vs buffalo bills": "new york jets vs buffalo bills",
    "los angeles rams vs denver broncos": "los angeles chargers vs denver broncos",
    "new york vs jacksonville jaguars": "new york jets vs jacksonville jaguars",
    # Add more as needed based on your logs
}

def normalize_matchup(text: str) -> str:
    """Normalize matchup text so HTML and M3U can be matched reliably."""
    cleaned = " ".join(text.split()).strip().lower()
    # Fix special cases
    if cleaned in TEAM_NORMALIZATION_MAP:
        return TEAM_NORMALIZATION_MAP[cleaned]
    # Clean up punctuation, extra spaces
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()

def extract_teams_from_display(text: str) -> str:
    """Extract stable 'team a vs team b' key from display text."""
    cleaned = text.strip()
    # Find " vs " and split into two teams
    idx = cleaned.lower().find(" vs ")
    if idx == -1:
        return ""
    
    parts = cleaned.split(" vs ", 1)
    if len(parts) != 2:
        return ""
    
    team1 = parts[0].strip()
    team2 = parts[1].strip()
    
    # Remove any trailing date/time from team2
    team2 = re.sub(r'\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec).*', '', team2, flags=re.IGNORECASE)
    team2 = team2.strip()
    
    key = f"{team1} vs {team2}"
    return normalize_matchup(key)

def simplify_team_name(text: str) -> str:
    """Turn 'Seattle Seahawks vs Atlanta Falcons' into safe filename."""
    cleaned = " ".join(text.split()).strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    return cleaned.strip("_")

def parse_m3u_nfl_section(m3u_text: str):
    """Parse M3U and extract (title, url) pairs from NFL section."""
    lines = [line.strip() for line in m3u_text.splitlines() if line.strip()]
    pairs = []
    current_title = None
    in_nfl_section = False
    
    for line in lines:
        if line.startswith("#EXTINF"):
            title_part = line.split(",", 1)[1] if "," in line else ""
            
            # Start NFL section on first NFL numbered entry
            if re.search(r'nfl\s+\d{1,2}:', title_part, re.IGNORECASE):
                in_nfl_section = True
            
            # Stop at next section marker
            if "--- NEXT SECTION ---" in title_part.upper() and in_nfl_section:
                break
                
            if in_nfl_section:
                current_title = title_part
        elif not line.startswith("#") and current_title and in_nfl_section:
            pairs.append((current_title, line))
            current_title = None
    
    return pairs

def build_matchup_to_url(m3u_text: str):
    """Build dict: normalized 'team a vs team b' -> stream URL."""
    section_pairs = parse_m3u_nfl_section(m3u_text)
    mapping = {}
    
    for title, url in section_pairs:
        # Extract matchup from title like "NFL 03: New Orleans Saints vs Atlanta Falcons Jan 04 01:00 PM (FOX)"
        lower_title = title.lower()
        
        # Skip non-matchup titles
        if " vs " not in lower_title:
            continue
            
        # Remove NFL numbering prefix
        if ":" in lower_title:
            matchup_part = lower_title.split(":", 1)[-1].strip()
        else:
            matchup_part = lower_title
        
        # Remove date/time/network suffix aggressively
        # Remove anything after month names
        matchup_part = re.sub(r'\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec).*?$', '', matchup_part, flags=re.IGNORECASE)
        # Remove network in parens
        matchup_part = re.sub(r'\s*\([^)]*\)$', '', matchup_part)
        
        key = normalize_matchup(matchup_part)
        if key and " vs " in key:
            mapping[key] = url
    
    return mapping

def extract_nfl_index_from_href(href: str) -> int:
    """Extract NFL index from href like 'nfl-streams-4'."""
    m = re.search(r"nfl-streams-(\d+)", href)
    return int(m.group(1)) if m else 1

def build_ffmpeg_command(stream_url: str, display_name: str, nfl_index: int) -> str:
    """Build ffmpeg command for this game."""
    team_token = simplify_team_name(display_name)
    segment_pattern = f'/var/www/html/index_{team_token}%d.js'
    
    m3u8_name = "nfl.m3u8" if nfl_index == 1 else f"nfl{nfl_index}.m3u8"
    output_playlist = f"/var/www/html/{m3u8_name}"
    
    cmd = (
        f'while true; do sudo ffmpeg -i "{stream_url}" '
        f'-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 -bsf:a aac_adtstoasc '
        f'-hls_segment_type mpegts '
        f'-hls_segment_filename "{segment_pattern}" '
        f'-hls_list_size 5 -hls_time 4 '
        f'-hls_flags delete_segments+append_list+omit_endlist '
        f'{output_playlist}; done'
    )
    return cmd

def main():
    print("Downloading M3U...")
    resp = requests.get(M3U_URL, timeout=20)
    resp.raise_for_status()
    m3u_text = resp.text
    
    matchup_to_url = build_matchup_to_url(m3u_text)
    print(f"Found {len(matchup_to_url)} NFL matchups in M3U")
    for key, url in matchup_to_url.items():
        print(f"  {key} -> {url}")
    
    with open(NFL_HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    ordered_entries = []
    ffmpeg_commands = []
    unmatched_count = 0
    
    print("\nMatching HTML games to streams...")
    for a in soup.select("#eventsTable tbody tr td a"):
        text = a.get_text(strip=True)
        href = a.get("href", "")
        
        # Skip non-game rows
        if " vs " not in text.lower():
            continue
        
        # Extract stable matchup key
        key = extract_teams_from_display(text)
        if not key:
            key = normalize_matchup(text)
        
        stream_url = matchup_to_url.get(key)
        
        if stream_url:
            print(f"  ✓ MATCHED: '{text}' -> {stream_url}")
            a["href"] = stream_url
            nfl_index = extract_nfl_index_from_href(href)
            ordered_entries.append((text, stream_url))
            ffmpeg_cmd = build_ffmpeg_command(stream_url, text, nfl_index)
            ffmpeg_commands.append(ffmpeg_cmd)
        else:
            print(f"  ✗ NO MATCH: '{text}' -> normalized: '{key}'")
            unmatched_count += 1
    
    print(f"\nMatched {len(ffmpeg_commands)} games, {unmatched_count} unmatched")
    
    # Write outputs
    with open("nfl_streams_map.txt", "w", encoding="utf-8") as f:
        for display_name, url in ordered_entries:
            f.write(f"{display_name} = {url}\n")
    
    with open("nfl_ffmpeg_commands.txt", "w", encoding="utf-8") as f:
        for cmd in ffmpeg_commands:
            f.write(cmd + "\n\n")
    
    print(f"Wrote {len(ffmpeg_commands)} FFmpeg commands to nfl_ffmpeg_commands.txt")
    
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(str(soup))
    
    print("Done! Check nfl_ffmpeg_commands.txt and nfl_with_streams.html")

if __name__ == "__main__":
    main()
