import re
import requests
import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# --- Constants - Adjust as Needed ---

USERNAME = "Marky0416"
PASSWORD = "Integra1994"
M3U_URL = f"http://ahostingportal.com:2095/get.php?username={USERNAME}&password={PASSWORD}&type=m3u"

# Folder definitions
DOWNLOADS_FOLDER = Path.home() / "Downloads"  # For M3U file search & saving
CURRENT_DIR = Path.cwd()  # For output files

NHL_HTML_FILE = Path(r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nhl.html")
OUTPUT_FILE = CURRENT_DIR / "nhl_matched_streams.txt"       # Human-readable output
FFMPEG_TXT_PATH = CURRENT_DIR / "nhl_ffmpeg.txt"            # ffmpeg commands output

# --- Team name normalization and aliases ---

known_team_aliases = {
    # Map HTML name -> M3U name
    "utah mammoth": "utah hockey club",
    "utah hockey club": "utah hockey club",
}

def normalize_team_name(name: str) -> str:
    """Normalize team names: lowercase, remove dots and leading 'the'."""
    name = name.lower().replace('.', '')
    if name.startswith('the '):
        name = name[4:]
    return name.strip()

def team_alias_from_name(name: str) -> str:
    """Create normalized alias suitable for filenames."""
    alias = normalize_team_name(name).replace(' ', '_').replace('.', '')
    return alias

# --- Functions for M3U file searching/saving ---

def get_today_files_with_pattern(folder: Path, base_name: str, ext: str) -> list[Path]:
    today = datetime.date.today()
    matches = []
    for file in folder.glob(f"{base_name}*{ext}"):
        if datetime.date.fromtimestamp(file.stat().st_mtime) == today:
            matches.append(file)
    return matches

def get_available_m3u_file(download_folder: Path, username: str) -> Path | None:
    base_name = f"playlist_{username}"
    ext = ".m3u"
    files = get_today_files_with_pattern(download_folder, base_name, ext)
    if files:
        return max(files, key=lambda f: f.stat().st_mtime)
    return None

def save_new_m3u_file(content: str, folder: Path, username: str) -> Path:
    base_name = f"playlist_{username}"
    ext = ".m3u"
    for idx in range(1, 100):
        if idx == 1:
            filepath = folder / f"{base_name}{ext}"
        else:
            filepath = folder / f"{base_name} ({idx}){ext}"
        if not filepath.exists():
            filepath.write_text(content, encoding="utf-8")
            return filepath
    raise RuntimeError("Too many playlist files; cannot save new M3U.")

# --- FFmpeg command generator (with optional sleep) ---

def generate_ffmpeg_txt(stream_cmds, output_path: Path):
    """
    stream_cmds: list of (match_str, stream_url, team_alias, sleep_seconds_or_none)
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, (match_str, stream_url, team_alias, sleep_secs) in enumerate(stream_cmds, start=1):
            playlist_name = "nhl.m3u8" if idx == 1 else f"nhl{idx}.m3u8"

            # If there is a future start time, prepend sleep <seconds> &&
            if sleep_secs is not None and sleep_secs > 0:
                sleep_prefix = f"sleep {sleep_secs} && "
            else:
                sleep_prefix = ""

            f.write(
                f'while true; do {sleep_prefix}sudo ffmpeg -i "{stream_url}" '
                '-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 '
                '-bsf:a aac_adtstoasc -hls_segment_type mpegts '
                f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                '-hls_list_size 5 -hls_time 4 '
                '-hls_flags delete_segments+append_list+omit_endlist '
                f'/var/www/html/{playlist_name}; done\n\n'
            )
    print(f"ffmpeg commands written to {output_path}")

# --- Helper to extract NHL section 2 from M3U ---

def extract_nhl_section2_lines(m3u_content: str) -> list[str]:
    """
    Extract lines belonging to 'section 2 of nhl':
    starting at the marker line that contains
    '#EXTINF:-1,--- NEXT SECTION ---2' up to but not including
    the next '--- NEXT SECTION ---' marker (or end of file).
    """
    lines = m3u_content.splitlines()
    section_lines = []
    in_section = False

    for line in lines:
        stripped = line.strip()
        if not in_section:
            if stripped.startswith("#EXTINF") and "NEXT SECTION ---2" in stripped:
                in_section = True
                section_lines.append(stripped)
        else:
            if stripped.startswith("#EXTINF") and "NEXT SECTION ---" in stripped and "NEXT SECTION ---2" not in stripped:
                # reached the next section marker
                break
            section_lines.append(stripped)

    return section_lines

# --- Main program ---

def main():
    print("Checking for existing M3U file downloaded today in Downloads folder...")
    m3u_file = get_available_m3u_file(DOWNLOADS_FOLDER, USERNAME)

    if m3u_file:
        print(f"Found existing M3U file for today: {m3u_file}")
        m3u_content = m3u_file.read_text(encoding='utf-8')
    else:
        print("No M3U file found for today. Downloading new one...")
        try:
            r = requests.get(M3U_URL)
            r.raise_for_status()
            m3u_content = r.text
            m3u_file = save_new_m3u_file(m3u_content, DOWNLOADS_FOLDER, USERNAME)
            print(f"Downloaded and saved new M3U file: {m3u_file}")
        except requests.RequestException as e:
            print(f"Failed to download M3U file: {e}")
            return

    print("Extracting NHL section 2 from M3U...")
    section_lines = extract_nhl_section2_lines(m3u_content)

    # Build mapping from normalized matchup ("team_a vs team_b") to URL within section 2
    matchup_streams = {}
    for i in range(len(section_lines)):
        line = section_lines[i]
        if line.startswith("#EXTINF") and "NHL" in line:
            m = re.search(r"NHL\s*\d+\s*:\s*(.*)", line)
            if m and (i + 1) < len(section_lines):
                full_title = m.group(1).strip()
                teams_part = full_title.split(" Dec ")[0].strip()
                if " vs " in teams_part:
                    home_raw, away_raw = [t.strip() for t in teams_part.split(" vs ", 1)]

                    home_norm = normalize_team_name(home_raw)
                    away_norm = normalize_team_name(away_raw)

                    # Apply alias normalization (M3U side)
                    home_norm = normalize_team_name(known_team_aliases.get(home_norm, home_norm))
                    away_norm = normalize_team_name(known_team_aliases.get(away_norm, away_norm))

                    key = f"{home_norm} vs {away_norm}"
                    url = section_lines[i + 1].strip()
                    matchup_streams[key] = url

    print(f"Found {len(matchup_streams)} NHL items in section 2 of the M3U.")

    print("Parsing nhl.html file...")
    if not NHL_HTML_FILE.exists():
        print(f"nhl.html not found at {NHL_HTML_FILE}. Exiting.")
        return

    html_content = NHL_HTML_FILE.read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')

    # Collect matchups and their PST start times from rows
    rows = soup.find_all('tr')
    html_matches = []  # list of (match_str, start_datetime or None)

    for tr in rows:
        tds = tr.find_all('td')
        if len(tds) < 2:
            continue

        # First <td> should contain the matchup link text
        a = tds[0].find('a')
        if not a or ' vs ' not in a.text:
            continue

        match_str = a.text.strip()

        # Second <td> contains date/time string in PST, e.g. "December 10, 2025 05:30 PM"
        time_text = tds[1].get_text(strip=True)

        start_dt = None
        if time_text:
            try:
                # Parsed as naive datetime; treated as local time when compared to datetime.now()
                start_dt = datetime.datetime.strptime(time_text, "%B %d, %Y %I:%M %p")
            except ValueError:
                start_dt = None

        html_matches.append((match_str, start_dt))

    print(f"Found {len(html_matches)} matchups with times in nhl.html.")

    human_readable_results = []
    ffmpeg_cmds = []

    now = datetime.datetime.now()

    for match_str, start_dt in html_matches:
        if " vs " not in match_str:
            human_readable_results.append(f"{match_str}: Unexpected format - skipping")
            continue

        home_html, away_html = [t.strip() for t in match_str.split(" vs ", 1)]

        home_norm = normalize_team_name(home_html)
        away_norm = normalize_team_name(away_html)

        # Apply alias normalization (HTML side)
        home_norm = normalize_team_name(known_team_aliases.get(home_norm, home_norm))
        away_norm = normalize_team_name(known_team_aliases.get(away_norm, away_norm))

        key = f"{home_norm} vs {away_norm}"

        matched_url = matchup_streams.get(key)

        # Compute sleep seconds (if start time is in the future)
        sleep_secs = None
        if start_dt is not None:
            delta = (start_dt - now).total_seconds()
            if delta > 0:
                sleep_secs = int(delta)

        if matched_url:
            human_readable_results.append(
                f"{match_str} at {start_dt if start_dt else 'Unknown time'}: {matched_url} "
                f"(sleep {sleep_secs}s before start)" if sleep_secs else
                f"{match_str} at {start_dt if start_dt else 'Unknown time'}: {matched_url}"
            )
            team_alias = team_alias_from_name(match_str.replace(" vs ", "_vs_"))
            ffmpeg_cmds.append((match_str, matched_url, team_alias, sleep_secs))
        else:
            human_readable_results.append(f"{match_str}: No stream found in NHL section 2")

    # Write human-readable results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for line in human_readable_results:
            f.write(line + "\n")
    print(f"Matching NHL streams written to {OUTPUT_FILE}")

    # Write ffmpeg commands (with sleep)
    generate_ffmpeg_txt(ffmpeg_cmds, FFMPEG_TXT_PATH)

if __name__ == "__main__":
    main()
