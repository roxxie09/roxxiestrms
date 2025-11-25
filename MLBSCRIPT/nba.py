import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup

M3U_URLS = [
    "http://madjokersqaud.nl:8080/get.php?username=Flathern2020&password=Sports&type=m3u",
    "http://madjokersqaud.nl:8080/get.php?username=6588574444&password=7405892934&type=m3u",
    "http://madjokersqaud.nl:8080/get.php?username=JACQUELINETAYLOR09&password=783cnZVH2D&type=m3u",
    "http://madjokersqaud.nl:8080/get.php?username=Lakergirl&password=froggie&type=m3u",
]

DOWNLOADS_FOLDER = Path.home() / "Downloads"
CURRENT_DIR = Path.cwd()
NBA_HTML_FILE = Path(r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nba.html")
OUTPUT_FILE = CURRENT_DIR / "nba_matched_streams.txt"
FFMPEG_TXT_PATH = CURRENT_DIR / "nba_ffmpeg.txt"

correct_names = {
    'dever nuggets': 'denver nuggets',
    'tornoto raptors': 'toronto raptors',
    'washington wizard': 'washington wizards',
}

fps_60_teams = {
    "miami heat",
    "minnesota timberwolves",
    "sacramento kings",
    "cleveland cavaliers",
    "denver nuggets",
    "new york knicks",
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

def parse_full_m3u(m3u_content):
    streams = {}
    lines = m3u_content.splitlines()
    for i in range(len(lines) - 1):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            info = line.split(',', 1)[1] if ',' in line else ''
            url = lines[i + 1].strip()
            m = re.search(r"\|\s*([^@]+)@([^|]+)\|", info)
            if m:
                team1 = normalize_team_name(m.group(1).strip())
                team2 = normalize_team_name(m.group(2).strip())
                key1 = f"{team1} vs {team2}"
                key2 = f"{team2} vs {team1}"
                # Map both directions
                streams[key1] = url
                streams[key2] = url
    return streams

def main():
    if not NBA_HTML_FILE.exists():
        print(f"nba.html not found at {NBA_HTML_FILE}. Exiting.")
        return

    html_content = NBA_HTML_FILE.read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')

    html_matches = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.text.strip()
        if 'nba-streams-' in href and ' vs ' in text:
            match_num = int(re.search(r"nba-streams-(\d+)", href).group(1))
            html_matches.append((match_num, text))

    html_matches.sort(key=lambda x: x[0])
    print(f"Found {len(html_matches)} games in html")

    chunk_size = 3
    outputs = []
    ffmpeg_cmds_by_game = {}

    last_url_index = -1
    matches_on_current_m3u = 0
    all_streams = {}

    # Pre-normalize 60fps teams set
    fps_60_teams_norm = set(normalize_team_name(t) for t in fps_60_teams)

    for idx, (match_number, match_str) in enumerate(html_matches):
        if matches_on_current_m3u == 0 or matches_on_current_m3u >= chunk_size:
            url_index = (last_url_index + 1) if last_url_index + 1 < len(M3U_URLS) else 0
            current_m3u_url = M3U_URLS[url_index]
            print(f"Downloading M3U: {current_m3u_url}")
            m3u_content = requests.get(current_m3u_url).text
            all_streams = parse_full_m3u(m3u_content)
            last_url_index = url_index
            matches_on_current_m3u = 0

        matches_on_current_m3u += 1

        teams = [t.strip() for t in match_str.lower().split(' vs ')]
        if len(teams) != 2:
            outputs.append(f"{match_str}: Unexpected format - skipping")
            continue

        home_norm, away_norm = teams

        # Check 60fps team presence
        contains_60fps = (home_norm in fps_60_teams_norm or away_norm in fps_60_teams_norm)

        # Extract stream URL from parsed playlist
        stream_url = all_streams.get(f"{home_norm} vs {away_norm}") or all_streams.get(f"{away_norm} vs {home_norm}")

        # Decide which teams to add: priority to 60fps teams
        home_60_used = home_norm in fps_60_teams_norm and contains_60fps
        away_60_used = away_norm in fps_60_teams_norm and contains_60fps

        home_url = stream_url if home_60_used or not contains_60fps else None
        away_url = stream_url if away_60_used or not contains_60fps else None

        home_alias = team_alias_from_name(home_norm)
        away_alias = team_alias_from_name(away_norm)

        home_note = " (60fps)" if home_60_used else ""
        away_note = " (60fps)" if away_60_used else ""

        outputs.append(f"Game {match_number} (nba-streams-{match_number}):")
        outputs.append(f"{home_norm.title()} (Home): {home_url if home_url else 'No stream found'}{home_note}")
        outputs.append(f"{away_norm.title()} (Away): {away_url if away_url else 'No stream found'}{away_note}")
        outputs.append("-" * 30)

        playlist_name = "nba.m3u8" if match_number == 1 else f"nba{match_number}.m3u8"
        cmds = []

        # For 60fps games add only those teams; else both if available
        if contains_60fps:
            if home_60_used and home_url:
                cmds.append((f"{home_norm.title()} (Home) - {match_str}", home_url, home_alias, playlist_name, True))
            if away_60_used and away_url:
                cmds.append((f"{away_norm.title()} (Away) - {match_str}", away_url, away_alias, playlist_name, True))
        else:
            if home_url:
                cmds.append((f"{home_norm.title()} (Home) - {match_str}", home_url, home_alias, playlist_name, False))
            if away_url:
                cmds.append((f"{away_norm.title()} (Away) - {match_str}", away_url, away_alias, playlist_name, False))

        ffmpeg_cmds_by_game[match_number] = cmds

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(outputs))
    print(f"Wrote matched streams to {OUTPUT_FILE}")

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
    print(f"Wrote ffmpeg commands to {FFMPEG_TXT_PATH}")

if __name__ == "__main__":
    main()
