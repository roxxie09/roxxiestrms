import re
import requests
import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# --- M3U sources (full URLs with credentials embedded) ---
M3U_URLS = [
    "http://madjokersqaud.nl:8080/get.php?username=Flathern2020&password=Sports&type=m3u",
    "http://madjokersqaud.nl:8080/get.php?username=6588574444&password=7405892934&type=m3u",
    "http://madjokersqaud.nl:8080/get.php?username=JACQUELINETAYLOR09&password=783cnZVH2D&type=m3u",
    "http://madjokersqaud.nl:8080/get.php?username=Lakergirl&password=froggie&type=m3u",
]

# Use this M3U for 60fps-preferred teams
M3U_60FPS_URL = "http://madjokersqaud.nl:8080/get.php?username=6588574444&password=7405892934&type=m3u"

DOWNLOADS_FOLDER = Path.home() / "Downloads"
CURRENT_DIR = Path.cwd()
NBA_HTML_FILE = Path(r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nba.html")
OUTPUT_FILE = CURRENT_DIR / "nba_matched_streams.txt"
FFMPEG_TXT_PATH = CURRENT_DIR / "nba_ffmpeg.txt"

# Known text typos to normalize
correct_names = {
    'dever nuggets': 'denver nuggets',
    'tornoto raptors': 'toronto raptors',
    'washington wizard': 'washington wizards',
}

# Teams that should prefer 60fps links
fps_60_teams = {
    "miami heat",
    "minnesota timberwolves",
    "sacramento kings",
    "cleveland cavaliers",
}

def normalize_team_name(name: str) -> str:
    name = name.lower().replace('.', '').replace('-', ' ')
    if name.startswith('the '):
        name = name[4:]
    return name.strip()

def correct_team_name(name: str) -> str:
    name_norm = normalize_team_name(name)
    return correct_names.get(name_norm, name_norm)

def team_alias_from_name(name: str) -> str:
    alias = normalize_team_name(name).replace(' ', '_').replace('.', '')
    return alias

def download_and_parse_m3u(url: str) -> dict:
    r = requests.get(url)
    r.raise_for_status()
    content = r.text
    team_streams = {}
    lines = content.splitlines()
    for i in range(len(lines)):
        line = lines[i].strip()
        m = re.search(r"USA *\| *NBA ([\w\s.'-]+?)\s*\(HD\)", line, re.IGNORECASE)
        if m and (i + 1) < len(lines):
            team_name_raw = m.group(1).strip()
            team_name_raw = re.sub(r'\s*\(.*\)$', '', team_name_raw)
            key = normalize_team_name(team_name_raw)
            url_line = lines[i + 1].strip()
            team_streams[key] = url_line
    return team_streams

def main():
    print("Parsing nba.html for matchups and stream links...")
    if not NBA_HTML_FILE.exists():
        print(f"nba.html not found at {NBA_HTML_FILE}. Exiting.")
        return

    html_content = NBA_HTML_FILE.read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')

    # Collect (match_number, matchup_text)
    html_matches = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.text.strip()
        if 'nba-streams-' in href and ' vs ' in text:
            match_number_search = re.search(r"nba-streams-(\d+)", href)
            if match_number_search:
                match_number = int(match_number_search.group(1))
                html_matches.append((match_number, text))

    html_matches.sort(key=lambda x: x[0])
    print(f"Found {len(html_matches)} NBA matchups in HTML.")

    # Preload 60fps playlist once
    print("Downloading 60fps M3U...")
    team_streams_60 = download_and_parse_m3u(M3U_60FPS_URL)

    chunk_size = 3  # Rotate main M3U source every 3 games

    outputs = []
    ffmpeg_cmds_by_game = {}

    for idx, (match_number, match_str) in enumerate(html_matches):
        # Select which normal M3U URL to use based on chunk index
        url_index = idx // chunk_size
        if url_index >= len(M3U_URLS):
            url_index = len(M3U_URLS) - 1  # clamp to last URL

        current_m3u_url = M3U_URLS[url_index]

        # Download & cache per URL to avoid repeated downloads
        if url_index != getattr(main, "last_url_index", None):
            print(f"Downloading normal M3U from: {current_m3u_url}")
            main.team_streams = download_and_parse_m3u(current_m3u_url)
            main.last_url_index = url_index

        team_streams = main.team_streams

        teams = [t.strip() for t in match_str.split(' vs ')]
        if len(teams) != 2:
            outputs.append(f"{match_str}: Unexpected format - skipping")
            continue

        home_team_raw, away_team_raw = teams
        home_norm = correct_team_name(home_team_raw)
        away_norm = correct_team_name(away_team_raw)

        # Default URLs from the normal playlist
        home_url = team_streams.get(home_norm)
        away_url = team_streams.get(away_norm)

        # Flags for 60fps usage
        home_60_used = False
        away_60_used = False

        # Try override with 60fps where applicable
        if home_norm in fps_60_teams:
            url_60 = team_streams_60.get(home_norm)
            if url_60:
                home_url = url_60
                home_60_used = True

        if away_norm in fps_60_teams:
            url_60 = team_streams_60.get(away_norm)
            if url_60:
                away_url = url_60
                away_60_used = True

        home_alias = team_alias_from_name(home_team_raw)
        away_alias = team_alias_from_name(away_team_raw)

        # Human-readable file with 60fps note
        home_note = " (60fps)" if home_60_used else ""
        away_note = " (60fps)" if away_60_used else ""

        outputs.append(f"Game {match_number} (nba-streams-{match_number}):")
        outputs.append(f"{home_team_raw} (Home): {home_url if home_url else 'No stream found'}{home_note}")
        outputs.append(f"{away_team_raw} (Away): {away_url if away_url else 'No stream found'}{away_note}")
        outputs.append("-" * 30)

        # Playlist naming per game
        playlist_name = "nba.m3u8" if match_number == 1 else f"nba{match_number}.m3u8"

        cmds = []

        # Logic for ffmpeg: if any 60fps side exists, ONLY add that side.
        # If both are 60fps, add both; if neither is 60fps, add both normal sides if present.

        if home_60_used or away_60_used:
            # At least one side is 60fps
            if home_60_used and home_url:
                cmds.append((
                    f"{home_team_raw} (Home) - {match_str}",
                    home_url,
                    home_alias,
                    playlist_name,
                    True  # is_60fps
                ))
            if away_60_used and away_url:
                cmds.append((
                    f"{away_team_raw} (Away) - {match_str}",
                    away_url,
                    away_alias,
                    playlist_name,
                    True
                ))
        else:
            # No 60fps side: add whatever is available (home/away normal)
            if home_url:
                cmds.append((
                    f"{home_team_raw} (Home) - {match_str}",
                    home_url,
                    home_alias,
                    playlist_name,
                    False
                ))
            if away_url:
                cmds.append((
                    f"{away_team_raw} (Away) - {match_str}",
                    away_url,
                    away_alias,
                    playlist_name,
                    False
                ))

        ffmpeg_cmds_by_game[match_number] = cmds

    # Write human-readable matches
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for line in outputs:
            f.write(line + "\n")
    print(f"Matching NBA streams written to {OUTPUT_FILE}")

    # Write ffmpeg commands, tagging 60fps in the comment
    with open(FFMPEG_TXT_PATH, 'w', encoding='utf-8') as f:
        for match_number in sorted(ffmpeg_cmds_by_game.keys()):
            for match_str, stream_url, team_alias, playlist_name, is_60fps in ffmpeg_cmds_by_game[match_number]:
                fps_tag = " (60fps)" if is_60fps else ""
                f.write(f"# nba-streams-{match_number} - playlist {playlist_name} - team_alias {team_alias}{fps_tag}\n")
                f.write(
                    f'while true; do sudo ffmpeg -i "{stream_url}" '
                    '-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 '
                    '-bsf:a aac_adtstoasc -hls_segment_type mpegts '
                    f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                    '-hls_list_size 5 -hls_time 4 '
                    '-hls_flags delete_segments+append_list+omit_endlist '
                    f'/var/www/html/{playlist_name}; done\n\n'
                )
    print(f"ffmpeg commands written to {FFMPEG_TXT_PATH}")

if __name__ == "__main__":
    main()
