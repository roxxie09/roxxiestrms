import re
import requests
import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# --- Constants - Adjust as Needed ---
USERNAME = "Marky0416"
PASSWORD = "Integra1994"
M3U_URL = f"http://ahostingportal.com:2095/get.php?username={USERNAME}&password={PASSWORD}&type=m3u"
# Use current working directory for output files
CURRENT_DIR = Path.cwd()
MLB_HTML_FILE = Path(r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\RANDOM\roxxiestrms\mlb.html")
OUTPUT_FILE = CURRENT_DIR / "mlb_matched_streams.txt"  # Human-readable output file
FFMPEG_TXT_PATH = CURRENT_DIR / "ffmpeg.txt"  # Generated ffmpeg commands file

# --- Team Aliases and Normalization ---
known_team_aliases = {
    'athletics': 'oakland athletics',
    'st. louis cardinals': 'st louis cardinals',
    'st louis cardinals': 'st louis cardinals',
    'the athletics': 'oakland athletics',
    # Add more aliases as needed here if you find mismatches
}

def normalize_team_name(name: str) -> str:
    """Normalize team names by lowercasing, removing dots and leading 'the'."""
    name = name.lower()
    name = name.replace('.', '')
    if name.startswith('the '):
        name = name[4:]
    return name.strip()

def team_alias_from_name(name: str) -> str:
    """Create a normalized alias suitable for filenames (no spaces, no dots)."""
    alias = normalize_team_name(name).replace(' ', '_').replace('.', '')
    # Customize for special cases
    if alias in ('the_athletics', 'athletics'):
        alias = 'athletics'
    if alias == 'st_louis_cardinals':
        alias = 'cardinals'
    return alias

# --- M3U File Handling ---
def get_today_files_with_pattern(folder: Path, base_name: str, ext: str) -> list[Path]:
    """
    Returns a list of files in 'folder' matching base_name*ext that were modified today.
    """
    today = datetime.date.today()
    matching_files = []
    for file in folder.glob(f"{base_name}*{ext}"):
        mtime = datetime.date.fromtimestamp(file.stat().st_mtime)
        if mtime == today:
            matching_files.append(file)
    return matching_files

def get_available_m3u_file(download_folder: Path, username: str) -> Path | None:
    """
    Checks for today's downloaded M3U playlist file(s):
    playlist_<username>.m3u or playlist_<username> (n).m3u
    Returns the most recent or None if none found.
    """
    base_name = f"playlist_{username}"
    ext = ".m3u"
    files = get_today_files_with_pattern(download_folder, base_name, ext)
    if files:
        return max(files, key=lambda f: f.stat().st_mtime)
    return None

def save_new_m3u_file(content: str, folder: Path, username: str) -> Path:
    """
    Saves M3U content in folder as playlist_<username>.m3u,
    adding (2), (3), ... if file exists. Returns the saved file path.
    """
    base_name = f"playlist_{username}"
    ext = ".m3u"
    for idx in range(1, 100):  # Arbitrary limit to prevent infinite loop
        if idx == 1:
            file_path = folder / f"{base_name}{ext}"
        else:
            file_path = folder / f"{base_name} ({idx}){ext}"
        if not file_path.exists():
            file_path.write_text(content, encoding='utf-8')
            return file_path
    raise RuntimeError("Too many playlist files with suffixes, cannot save new M3U.")

# --- FFmpeg Command Generation with HOME and AWAY separated and playlist restart ---
def generate_ffmpeg_txt_separated(home_commands, away_commands, output_path: Path):
    """
    Generate ffmpeg.txt with HOME and AWAY team sections.
    Playlist numbering restarts at mlb.m3u8 for AWAY teams.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# --- HOME Teams ---\n\n")

        # HOME teams playlist numbering: mlb.m3u8, mlb2.m3u8, ...
        for idx, (match_str, stream_url, team_alias) in enumerate(home_commands, start=1):
            playlist_name = "mlb.m3u8" if idx == 1 else f"mlb{idx}.m3u8"
            f.write(f'while true; do sudo ffmpeg -i "{stream_url}" '
                    '-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 '
                    '-bsf:a aac_adtstoasc -hls_segment_type mpegts '
                    f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                    '-hls_list_size 5 -hls_time 4 '
                    '-hls_flags delete_segments+append_list+omit_endlist '
                    f'/var/www/html/{playlist_name}; done\n\n')

        f.write("# --- AWAY Teams ---\n\n")

        # AWAY teams playlist numbering: restart starting at mlb.m3u8
        for idx, (match_str, stream_url, team_alias) in enumerate(away_commands, start=1):
            playlist_name = "mlb.m3u8" if idx == 1 else f"mlb{idx}.m3u8"
            f.write(f'while true; do sudo ffmpeg -i "{stream_url}" '
                    '-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 '
                    '-bsf:a aac_adtstoasc -hls_segment_type mpegts '
                    f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                    '-hls_list_size 5 -hls_time 4 '
                    '-hls_flags delete_segments+append_list+omit_endlist '
                    f'/var/www/html/{playlist_name}; done\n\n')

    print(f"ffmpeg commands with HOME and AWAY teams written to {output_path}")

# --- Main Logic ---
def main():
    # Step 1: Check for existing M3U downloaded today or download a new one
    print("Checking for existing M3U file downloaded today...")
    m3u_file = get_available_m3u_file(CURRENT_DIR, USERNAME)

    if m3u_file:
        print(f"Found existing M3U downloaded today: {m3u_file}")
        m3u_content = m3u_file.read_text(encoding='utf-8')
    else:
        print("No M3U file found for today, downloading new one...")
        try:
            response = requests.get(M3U_URL)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            m3u_content = response.text
            m3u_file = save_new_m3u_file(m3u_content, CURRENT_DIR, USERNAME)
            print(f"Downloaded and saved M3U as: {m3u_file}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading M3U file: {e}")
            print("Cannot proceed without M3U file. Exiting.")
            return

    # Step 2: Parse M3U file content to get team streams mapping
    print("Parsing M3U file...")
    m3u_lines = m3u_content.splitlines()
    team_streams = {} # Dictionary to store normalized_team_name -> stream_url
    for i in range(len(m3u_lines)):
        line = m3u_lines[i].strip()
        if line.startswith("#EXTINF"):
            match = re.search(r"MLB[ -:] *(.*)", line)
            if match:
                team_name_raw = match.group(1).strip()
                team_name_normalized = normalize_team_name(team_name_raw)
                if i + 1 < len(m3u_lines):
                    url = m3u_lines[i + 1].strip()
                    team_streams[team_name_normalized] = url
    print(f"Found {len(team_streams)} team streams in M3U.")

    # Step 3: Parse mlb.html for matchups
    print("Parsing mlb.html file...")
    if not MLB_HTML_FILE.exists():
        print(f"Error: mlb.html file not found at {MLB_HTML_FILE}. Cannot proceed.")
        return

    html_content = MLB_HTML_FILE.read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')

    html_matches = [] # List of strings like "Team A vs Team B"
    for td in soup.find_all('td'):
        a_tag = td.find('a')
        if a_tag and ' vs ' in a_tag.text:
            html_matches.append(a_tag.text.strip())
    print(f"Found {len(html_matches)} matches in mlb.html.")

    # Step 4: Match home and away team names to stream URLs, using aliases
    print("Matching teams to streams and preparing ffmpeg commands...")
    human_readable_results = []
    home_ffmpeg_cmds = []
    away_ffmpeg_cmds = []

    for match_str_html in html_matches:
        teams = [t.strip() for t in match_str_html.split(' vs ')]
        if len(teams) != 2:
            human_readable_results.append(f"{match_str_html}: Unexpected format - skipping")
            continue

        home_team_raw, away_team_raw = teams[0], teams[1]

        # Home team lookup
        home_team_norm = normalize_team_name(home_team_raw)
        home_url = team_streams.get(home_team_norm)
        if not home_url and home_team_norm in known_team_aliases:
            alias_lookup = known_team_aliases[home_team_norm]
            home_url = team_streams.get(normalize_team_name(alias_lookup))
        if not home_url:
            home_url = team_streams.get(home_team_norm.replace('the ', '').replace('.', '').strip())

        home_team_alias = team_alias_from_name(home_team_raw)

        # Away team lookup
        away_team_norm = normalize_team_name(away_team_raw)
        away_url = team_streams.get(away_team_norm)
        if not away_url and away_team_norm in known_team_aliases:
            alias_lookup = known_team_aliases[away_team_norm]
            away_url = team_streams.get(normalize_team_name(alias_lookup))
        if not away_url:
            away_url = team_streams.get(away_team_norm.replace('the ', '').replace('.', '').strip())

        away_team_alias = team_alias_from_name(away_team_raw)

        # Append human-readable lines
        human_readable_results.append(f"{home_team_raw} (Home): {home_url if home_url else 'No stream found'}")
        human_readable_results.append(f"{away_team_raw} (Away): {away_url if away_url else 'No stream found'}")
        human_readable_results.append("-" * 30)

        # Append ffmpeg command lists
        if home_url:
            home_ffmpeg_cmds.append((match_str_html, home_url, home_team_alias))
        if away_url:
            away_ffmpeg_cmds.append((match_str_html, away_url, away_team_alias))

    # Step 5: Write human-readable matched streams
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for line in human_readable_results:
            f.write(line + "\n")
    print(f"Matching streams written to {OUTPUT_FILE}")

    # Step 6: Generate ffmpeg.txt commands file with separated home and away teams and playlist restart
    generate_ffmpeg_txt_separated(home_ffmpeg_cmds, away_ffmpeg_cmds, FFMPEG_TXT_PATH)

if __name__ == "__main__":
    main()
