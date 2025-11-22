import re
import requests
import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# List of multiple M3U username/password accounts to rotate through
M3U_ACCOUNTS = [
    {"username": "Flathern2020", "password": "Sports"},
    {"username": "6588574444", "password": "7405892934"},
    {"username": "JACQUELINETAYLOR09", "password": "783cnZVH2D"},
    {"username": "Darren362", "password": "Muffy8816"},
    {"username": "Lakergirl", "password": "froggie"},
    # Add more as needed
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

def get_m3u_content_for_account(account):
    url = f"http://madjokersqaud.nl:8080/get.php?username={account['username']}&password={account['password']}&type=m3u"
    r = requests.get(url)
    r.raise_for_status()
    return r.text

def parse_m3u_content(m3u_content):
    team_streams = {}
    lines = m3u_content.splitlines()
    for i in range(len(lines)):
        line = lines[i].strip()
        m = re.search(r"USA *\| *NBA ([\w\s.'-]+?)\s*\(HD\)", line, re.IGNORECASE)
        if m and (i + 1) < len(lines):
            team_name_raw = m.group(1).strip()
            team_name_raw = re.sub(r'\s*\(.*\)$', '', team_name_raw)
            key = normalize_team_name(team_name_raw)
            url = lines[i + 1].strip()
            team_streams[key] = url
    return team_streams

def main():
    print("Parsing nba.html file for stream links and matchups...")
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
            match_number_search = re.search(r"nba-streams-(\d+)", href)
            if match_number_search:
                match_number = int(match_number_search.group(1))
                html_matches.append((match_number, text))

    html_matches.sort(key=lambda x: x[0])
    print(f"Found {len(html_matches)} NBA matchups in HTML.")

    chunk_size = 3  # Number of matches per M3U account before switching
    outputs = []
    ffmpeg_cmds_by_game = {}

    for idx, (match_number, match_str) in enumerate(html_matches):
        account_index = idx // chunk_size
        account = M3U_ACCOUNTS[account_index % len(M3U_ACCOUNTS)]

        if idx % chunk_size == 0:
            print(f"Downloading M3U for account {account_index + 1}: {account['username']}")
            m3u_content = get_m3u_content_for_account(account)
            team_streams = parse_m3u_content(m3u_content)

        teams = [t.strip() for t in match_str.split(' vs ')]
        if len(teams) != 2:
            outputs.append(f"{match_str}: Unexpected format - skipping")
            continue

        home_team_raw, away_team_raw = teams
        home_norm = correct_team_name(home_team_raw)
        away_norm = correct_team_name(away_team_raw)
        home_url = team_streams.get(home_norm)
        away_url = team_streams.get(away_norm)
        home_alias = team_alias_from_name(home_team_raw)
        away_alias = team_alias_from_name(away_team_raw)

        outputs.append(f"Game {match_number} (nba-streams-{match_number}):")
        outputs.append(f"{home_team_raw} (Home): {home_url if home_url else 'No stream found'}")
        outputs.append(f"{away_team_raw} (Away): {away_url if away_url else 'No stream found'}")
        outputs.append("-" * 30)

        playlist_name = "nba.m3u8" if match_number == 1 else f"nba{match_number}.m3u8"
        cmds = []
        if home_url:
            cmds.append((f"{home_team_raw} (Home) - {match_str}", home_url, home_alias, playlist_name))
        if away_url:
            cmds.append((f"{away_team_raw} (Away) - {match_str}", away_url, away_alias, playlist_name))
        ffmpeg_cmds_by_game[match_number] = cmds

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for line in outputs:
            f.write(line + "\n")
    print(f"Matching NBA streams written to {OUTPUT_FILE}")

    with open(FFMPEG_TXT_PATH, 'w', encoding='utf-8') as f:
        for match_number in sorted(ffmpeg_cmds_by_game.keys()):
            for match_str, stream_url, team_alias, playlist_name in ffmpeg_cmds_by_game[match_number]:
                f.write(f"# nba-streams-{match_number} - playlist {playlist_name} - team_alias {team_alias}\n")
                f.write(f'while true; do sudo ffmpeg -i "{stream_url}" '
                        '-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 '
                        '-bsf:a aac_adtstoasc -hls_segment_type mpegts '
                        f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                        '-hls_list_size 5 -hls_time 4 '
                        '-hls_flags delete_segments+append_list+omit_endlist '
                        f'/var/www/html/{playlist_name}; done\n\n')
    print(f"ffmpeg commands written to {FFMPEG_TXT_PATH}")

if __name__ == "__main__":
    main()
