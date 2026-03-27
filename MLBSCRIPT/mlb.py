import re
import requests
import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# --- Constants - Adjust as Needed ---
USERNAME = "Marky0416"
PASSWORD = "Integra1994"
M3U_URL = f"http://ahostingportal.com:2095/get.php?username=Marky0416&password=Integra1994&type=m3u"

SLING_M3U_URL = "http://ahostingportal.com:2095/get.php?username=Marky0416&password=Integra1994&type=m3u"

# Folder definitions
DOWNLOADS_FOLDER = Path.home() / "Downloads"
CURRENT_DIR = Path.cwd()

MLB_HTML_FILE = Path(r"G:\\MY LEGIT EVERYTRHING FOLDER\\RANDOM\\rxxiestrms.live\\mlb.html")
OUTPUT_FILE = CURRENT_DIR / "mlb_matched_streams.txt"
FFMPEG_TXT_PATH = CURRENT_DIR / "ffmpeg.txt"

known_team_aliases = {
    'athletics': 'oakland athletics',
    'st. louis cardinals': 'st louis cardinals',
    'st louis cardinals': 'st louis cardinals',
    'the athletics': 'oakland athletics',
    'washington nationals': 'nationals',
    'toronto blue jays': 'blue jays',
    'texas rangers': 'rangers',
    'tampa bay rays': 'rays',
    'new york mets': 'mets',
    'pittsburgh pirates': 'pirates',
    'chicago white sox': 'white sox',
    'milwaukee brewers': 'brewers',
    'los angeles dodgers': 'dodgers',
}

def normalize_team_name(name: str) -> str:
    name = name.lower().replace('.', '').replace('-', ' ')
    if name.startswith('the '):
        name = name[4:]
    return name.strip()

def team_alias_from_name(name: str) -> str:
    alias = normalize_team_name(name).replace(' ', '_').replace('.', '')
    if alias in ('the_athletics', 'athletics'):
        alias = 'athletics'
    if alias == 'st_louis_cardinals':
        alias = 'cardinals'
    return alias

def get_sling_sources(team_norm: str) -> str | None:
    try:
        resp = requests.get(SLING_M3U_URL, timeout=10)
        resp.raise_for_status()
        lines = resp.text.splitlines()

        target = f"US (MLB) {team_norm.title()} (S)"
        for i in range(len(lines) - 1):
            line = lines[i].strip()
            if line.startswith("#EXTINF") and target.lower() in line.lower():
                url = lines[i + 1].strip()
                if url.startswith("http"):
                    print(f"Found Sling source for {team_norm}: {url[:80]}...")
                    return url
    except Exception as e:
        print(f"Error fetching Sling M3U: {e}")

    return None

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
        filepath = folder / (f"{base_name}{ext}" if idx == 1 else f"{base_name} ({idx}){ext}")
        if not filepath.exists():
            filepath.write_text(content, encoding="utf-8")
            return filepath
    raise RuntimeError("Too many playlist files; cannot save new M3U.")

def generate_ffmpeg_txt_separated(home_cmds, away_cmds, output_path: Path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# --- HOME Teams ---\n\n")
        for idx, (match_str, stream_url, team_alias) in enumerate(home_cmds, start=1):
            playlist_name = "mlb.m3u8" if idx == 1 else f"mlb{idx}.m3u8"
            f.write(
                f'while true; do sudo ffmpeg -i "{stream_url}" '
                '-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 '
                '-bsf:a aac_adtstoasc -hls_segment_type mpegts '
                f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                '-hls_list_size 5 -hls_time 4 '
                '-hls_flags delete_segments+append_list+omit_endlist '
                f'/var/www/html/{playlist_name}; done\n\n'
            )

        f.write("# --- AWAY Teams ---\n\n")
        for idx, (match_str, stream_url, team_alias) in enumerate(away_cmds, start=1):
            playlist_name = "mlb.m3u8" if idx == 1 else f"mlb{idx}.m3u8"
            f.write(
                f'while true; do sudo ffmpeg -i "{stream_url}" '
                '-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 '
                '-bsf:a aac_adtstoasc -hls_segment_type mpegts '
                f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                '-hls_list_size 5 -hls_time 4 '
                '-hls_flags delete_segments+append_list+omit_endlist '
                f'/var/www/html/{playlist_name}; done\n\n'
            )

    print(f"ffmpeg commands with HOME and AWAY teams written to {output_path}")

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

    html_matches = []
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 2:
            a_tag = tds[0].find('a')
            if a_tag and 'mlb-streams-' in a_tag.get('href', ''):
                href = a_tag['href']
                num_match = re.search(r'mlb-streams-(\d+)', href)
                if num_match:
                    match_num = int(num_match.group(1))
                    text = a_tag.text.strip()
                    html_matches.append((match_num, text))
    html_matches.sort(key=lambda x: x[0])
    html_matches = [match[1] for match in html_matches]
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

        home_norm = normalize_team_name(home_team_raw)
        home_url = get_sling_sources(home_norm)
        if not home_url and home_norm in known_team_aliases:
            home_url = get_sling_sources(normalize_team_name(known_team_aliases[home_norm]))
        if not home_url:
            home_url = team_streams.get(home_norm)
        if not home_url and home_norm in known_team_aliases:
            home_url = team_streams.get(normalize_team_name(known_team_aliases[home_norm]))
        if not home_url:
            home_url = team_streams.get(home_norm.replace('the ', '').replace('.', '').strip())
        home_alias = team_alias_from_name(home_team_raw)

        away_norm = normalize_team_name(away_team_raw)
        away_url = get_sling_sources(away_norm)
        if not away_url and away_norm in known_team_aliases:
            away_url = get_sling_sources(normalize_team_name(known_team_aliases[away_norm]))
        if not away_url:
            away_url = team_streams.get(away_norm)
        if not away_url and away_norm in known_team_aliases:
            away_url = team_streams.get(normalize_team_name(known_team_aliases[away_norm]))
        if not away_url:
            away_url = team_streams.get(away_norm.replace('the ', '').replace('.', '').strip())
        away_alias = team_alias_from_name(away_team_raw)

        human_readable_results.append(f"{home_team_raw} (Home): {home_url if home_url else 'No stream found'}")
        human_readable_results.append(f"{away_team_raw} (Away): {away_url if away_url else 'No stream found'}")
        human_readable_results.append("-" * 30)

        if home_url:
            home_ffmpeg_cmds.append((match_str, home_url, home_alias))
        if away_url:
            away_ffmpeg_cmds.append((match_str, away_url, away_alias))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for line in human_readable_results:
            f.write(line + "\n")
    print(f"Matching streams written to {OUTPUT_FILE}")

    generate_ffmpeg_txt_separated(home_ffmpeg_cmds, away_ffmpeg_cmds, FFMPEG_TXT_PATH)

if __name__ == "__main__":
    main()