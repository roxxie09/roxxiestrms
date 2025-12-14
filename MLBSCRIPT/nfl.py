import re
import requests
from bs4 import BeautifulSoup

# URL to download the full M3U playlist
M3U_URL = "http://ahostingportal.com:2095/get.php?username=Marky0416&password=Integra1994&type=m3u"

# Local paths – adjust if needed
NFL_HTML_PATH = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nfl.html"  # your source file
OUTPUT_HTML_PATH = "nfl_with_streams.html"  # output with replaced links

# Fix naming quirks between HTML and M3U
TEAM_NORMALIZATION_MAP = {
    # HTML text : canonical M3U-style text
    "new york vs jacksonville jaguars": "new york jets vs jacksonville jaguars",
    "washington commanders vs new york": "washington commanders vs new york giants",
    "los angeles rams vs kansas city chiefs": "los angeles chargers vs kansas city chiefs",
    "new york vs jacksonville jaguars": "new york jets vs jacksonville jaguars",
}

def normalize_matchup(text: str) -> str:
    """Normalize matchup text so HTML and M3U can be matched reliably."""
    cleaned = " ".join(text.split()).strip().lower()
    # apply special fixes
    if cleaned in TEAM_NORMALIZATION_MAP:
        return TEAM_NORMALIZATION_MAP[cleaned]
    return cleaned

def simplify_team_name(text: str) -> str:
    """
    Turn 'Seattle Seahawks vs Atlanta Falcons' into something safe like 'seattle_seahawks_atlanta_falcons'
    for filenames.
    """
    cleaned = " ".join(text.split()).strip().lower()
    # keep letters, numbers, underscore only
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    cleaned = cleaned.strip("_")
    return cleaned

def parse_m3u_nfl_sd_section(m3u_text: str):
    """
    Parse the M3U and extract (title, url) pairs from NFL 01–16 section
    (starts at first NFL 01: entry, ends at --- NEXT SECTION ---).
    """
    lines = [line.strip() for line in m3u_text.splitlines() if line.strip()]
    pairs = []
    current_title = None
    in_nfl_sd = False
    
    for line in lines:
        if line.startswith("#EXTINF"):
            title_part = line.split(",", 1)[1] if "," in line else ""
            
            # FIXED: Trigger on ANY NFL 01:
            if "NFL 01:" in title_part:
                in_nfl_sd = True
            
            # Stop at next section
            if "--- NEXT SECTION ---" in title_part and in_nfl_sd:
                in_nfl_sd = False
            
            current_title = title_part if in_nfl_sd else None
            
        elif not line.startswith("#") and current_title and in_nfl_sd:
            # This line is the URL corresponding to the previous EXTINF
            pairs.append((current_title, line))
            current_title = None
    
    return pairs

def build_matchup_to_url(m3u_text: str):
    """
    Build a dict: normalized 'team a vs team b' -> stream URL
    using only entries from that NFL SD block.
    """
    section_pairs = parse_m3u_nfl_sd_section(m3u_text)
    mapping = {}
    
    for title, url in section_pairs:
        lower = title.lower()
        if " vs " not in lower:
            continue
        
        # Drop the 'NFL 02:' etc., keep just the matchup + date
        matchup_part = lower.split(":", 1)[-1].strip()
        
        # Remove date/time part like 'dec 07 01:00 pm (fox)'
        if " dec " in matchup_part:
            matchup_part = matchup_part.split(" dec ")[0].strip()
        
        key = normalize_matchup(matchup_part)
        mapping[key] = url
    
    return mapping

def extract_nfl_index_from_href(href: str) -> int:
    """
    Given 'https://roxiestreams.live/nfl-streams-4', return 4.
    If it's just '.../nfl-streams-1' or '.../redzone' with no number, treat that as 1.
    """
    m = re.search(r"nfl-streams-(\d+)", href)
    if m:
        return int(m.group(1))
    # default to 1 if no explicit number (like redzone)
    return 1

def build_ffmpeg_command(stream_url: str, display_name: str, nfl_index: int) -> str:
    """
    Build the while-true ffmpeg command string for this game.
    """
    team_token = simplify_team_name(display_name)
    
    # segment filename, e.g. index_seattle_seahawks_vs_atlanta_falcons%d.js
    segment_pattern = f'/var/www/html/index_{team_token}%d.js'
    
    # output playlist, e.g. nfl.m3u8, nfl2.m3u8, nfl4.m3u8
    if nfl_index == 1:
        m3u8_name = "nfl.m3u8"
    else:
        m3u8_name = f"nfl{nfl_index}.m3u8"
    
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
    # 1) Download the M3U
    print("Downloading M3U...")
    resp = requests.get(M3U_URL, timeout=20)
    resp.raise_for_status()
    m3u_text = resp.text
    
    # 2) Build matchup -> stream URL mapping
    matchup_to_url = build_matchup_to_url(m3u_text)
    print(f"Found {len(matchup_to_url)} NFL matchups in M3U")
    for key in matchup_to_url:
        print(f"  {key} -> {matchup_to_url[key]}")
    
    # 3) Load your nfl.html
    with open(NFL_HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    # 4) Walk the table rows IN ORDER
    ordered_entries = []
    ffmpeg_commands = []
    
    for a in soup.select("#eventsTable tbody tr td a"):
        text = a.get_text(strip=True)
        href = a.get("href", "")
        
        # Skip non-game rows (like 'NFL RedZone')
        if " vs " not in text.lower():
            continue
        
        key = normalize_matchup(text)
        stream_url = matchup_to_url.get(key)
        
        if not stream_url:
            print(f"No match for HTML: '{text}' -> normalized: '{key}'")
            continue
        
        print(f"MATCHED: {text} -> {stream_url}")
        
        # Update the HTML link to the IPTV URL
        a["href"] = stream_url
        
        # Determine nfl index from original href (nfl-streams-X)
        nfl_index = extract_nfl_index_from_href(href)
        
        # Store for txt map
        ordered_entries.append((text, stream_url))
        
        # Build ffmpeg command for this game
        ffmpeg_cmd = build_ffmpeg_command(stream_url, text, nfl_index)
        ffmpeg_commands.append(ffmpeg_cmd)
    
    # 5) Write mapping to a text file
    with open("nfl_streams_map.txt", "w", encoding="utf-8") as f:
        for display_name, url in ordered_entries:
            f.write(f"{display_name} = {url}\n")
    
    # 6) Write all ffmpeg commands to a shell script file
    with open("nfl_ffmpeg_commands.txt", "w", encoding="utf-8") as f:
        for cmd in ffmpeg_commands:
            f.write(cmd + "\n\n")
    
    print(f"\nWrote {len(ffmpeg_commands)} FFmpeg commands to nfl_ffmpeg_commands.txt")
    
    # 7) Write out the updated HTML
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(str(soup))
    
    print("Done! Check nfl_ffmpeg_commands.txt and nfl_with_streams.html")

if __name__ == "__main__":
    main()
