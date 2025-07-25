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
DOWNLOADS_FOLDER = Path.home() / "Downloads"          # For M3U file search & saving
CURRENT_DIR = Path.cwd()                              # For output files (mlb_matched_streams.txt, ffmpeg.txt)

MLB_HTML_FILE = Path(r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\RANDOM\roxxiestrms\mlb.html")
OUTPUT_FILE = CURRENT_DIR / "mlb_matched_streams.txt"  # Human-readable output
FFMPEG_TXT_PATH = CURRENT_DIR / "ffmpeg.txt"           # ffmpeg commands output

# --- Team Aliases and Normalization ---
known_team_aliases = {
    'athletics': 'oakland athletics',
    'st. louis cardinals': 'st louis cardinals',
    'st louis cardinals': 'st louis cardinals',
    'the athletics': 'oakland athletics',
    # Add more aliases as needed here
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
    # Special cases
    if alias in ('the_athletics', 'athletics'):
        alias = 'athletics'
    if alias == 'st_louis_cardinals':
        alias = 'cardinals'
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

# --- FFmpeg command generator with HOME/AWAY separation ---
def generate_ffmpeg_txt_separated(home_cmds, away_cmds, output_path: Path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# --- HOME Teams ---\n\n")
        for idx, (match_str, stream_url, team_alias) in enumerate(home_cmds, start=1):
            playlist_name = "mlb.m3u8" if idx == 1 else f"mlb{idx}.m3u8"
            f.write(f'while true; do sudo ffmpeg -i "{stream_url}" '
                    '-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 '
                    '-bsf:a aac_adtstoasc -hls_segment_type mpegts '
                    f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                    '-hls_list_size 5 -hls_time 4 '
                    '-hls_flags delete_segments+append_list+omit_endlist '
                    f'/var/www/html/{playlist_name}; done\n\n')

        f.write("# --- AWAY Teams ---\n\n")
        for idx, (match_str, stream_url, team_alias) in enumerate(away_cmds, start=1):
            playlist_name = "mlb.m3u8" if idx == 1 else f"mlb{idx}.m3u8"
            f.write(f'while true; do sudo ffmpeg -i "{stream_url}" '
                    '-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 '
                    '-bsf:a aac_adtstoasc -hls_segment_type mpegts '
                    f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                    '-hls_list_size 5 -hls_time 4 '
                    '-hls_flags delete_segments+append_list+omit_endlist '
                    f'/var/www/html/{playlist_name}; done\n\n')

    print(f"ffmpeg commands with HOME and AWAY teams written to {output_path}")

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

    print("Parsing M3U file...")
    m3u_lines = m3u_content.splitlines()
    team_streams = {}
    for i in range(len(m3u_lines)):
        line = m3u_lines[i].strip()
        if line.startswith("#EXTINF"):
            match = re.search(r"MLB[ -:] *(.*)", line)
            if match and (i + 1) < len(m3u_lines):
                team_name_raw = match.group(1).strip()
                key = normalize_team_name(team_name_raw)
                url = m3u_lines[i + 1].strip()
                team_streams[key] = url
    print(f"Found {len(team_streams)} streams in M3U.")

    print("Parsing mlb.html file...")
    if not MLB_HTML_FILE.exists():
        print(f"mlb.html not found at {MLB_HTML_FILE}. Exiting.")
        return

    html_content = MLB_HTML_FILE.read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')

    html_matches = [a.text.strip() for td in soup.find_all('td') for a in td.find_all('a') if ' vs ' in a.text]
    print(f"Found {len(html_matches)} matchups in HTML.")

    human_readable_results = []
    home_ffmpeg_cmds = []
    away_ffmpeg_cmds = []

    for match_str in html_matches:
        teams = [t.strip() for t in match_str.split(' vs ')]
        if len(teams) != 2:
            human_readable_results.append(f"{match_str}: Unexpected format - skipping")
            continue
        
        home_team_raw, away_team_raw = teams

        # Find home team stream URL
        home_norm = normalize_team_name(home_team_raw)
        home_url = team_streams.get(home_norm)
        if not home_url and home_norm in known_team_aliases:
            home_url = team_streams.get(normalize_team_name(known_team_aliases[home_norm]))
        if not home_url:
            home_url = team_streams.get(home_norm.replace('the ', '').replace('.', '').strip())
        home_alias = team_alias_from_name(home_team_raw)

        # Find away team stream URL
        away_norm = normalize_team_name(away_team_raw)
        away_url = team_streams.get(away_norm)
        if not away_url and away_norm in known_team_aliases:
            away_url = team_streams.get(normalize_team_name(known_team_aliases[away_norm]))
        if not away_url:
            away_url = team_streams.get(away_norm.replace('the ', '').replace('.', '').strip())
        away_alias = team_alias_from_name(away_team_raw)

        # Append human-readable output
        human_readable_results.append(f"{home_team_raw} (Home): {home_url if home_url else 'No stream found'}")
        human_readable_results.append(f"{away_team_raw} (Away): {away_url if away_url else 'No stream found'}")
        human_readable_results.append("-" * 30)

        # Record for ffmpeg commands
        if home_url:
            home_ffmpeg_cmds.append((match_str, home_url, home_alias))
        if away_url:
            away_ffmpeg_cmds.append((match_str, away_url, away_alias))

    # Write human-readable results to current working directory
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for line in human_readable_results:
            f.write(line + "\n")
    print(f"Matching streams written to {OUTPUT_FILE}")

    # Generate ffmpeg commands file in current directory
    generate_ffmpeg_txt_separated(home_ffmpeg_cmds, away_ffmpeg_cmds, FFMPEG_TXT_PATH)

if __name__ == "__main__":
    main()
