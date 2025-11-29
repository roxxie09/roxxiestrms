import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

M3U_URLS = [
    "http://madjokersqaud.nl:8080/get.php?username=Flathern2020&password=Sports&type=m3u",
    "http://madjokersqaud.nl:8080/get.php?username=6588574444&password=7405892934&type=m3u",
    "http://madjokersqaud.nl:8080/get.php?username=JACQUELINETAYLOR09&password=783cnZVH2D&type=m3u",
    "http://madjokersqaud.nl:8080/get.php?username=Lakergirl&password=froggie&type=m3u",
]

NBA_HTML_FILE = Path(r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nba.html")
CURRENT_DIR = Path.cwd()
OUTPUT_FILE = CURRENT_DIR / "nba_matched_streams.txt"
FFMPEG_TXT_PATH = CURRENT_DIR / "nba_ffmpeg.txt"

correct_names = {
    'dever nuggets': 'denver nuggets',
    'tornoto raptors': 'toronto raptors',
    'washington wizard': 'washington wizards',
}

fps_60_teams = {
    "miami heat", "minnesota timberwolves", "sacramento kings",
    "cleveland cavaliers", "denver nuggets", "new york knicks",
}

def parse_game_time(game_time_str):
    """Parse game time with multiple format attempts"""
    current_year = datetime.now().year
    formats = [
        f"{game_time_str}, {current_year}",
        f"{game_time_str} {current_year}",
        game_time_str
    ]
    for fmt in formats:
        try:
            if "PM" in fmt.upper() or "AM" in fmt.upper():
                return datetime.strptime(fmt.strip(), "%B %d, %Y %I:%M %p")
            else:
                return datetime.strptime(fmt.strip(), "%B %d, %Y %I:%M")
        except ValueError:
            continue
    print(f"⚠️  Could not parse time: '{game_time_str}'")
    return None

def calculate_delay_seconds(current_time, game_time):
    if not game_time:
        return 0
    delta = game_time - current_time
    return max(0, int(delta.total_seconds()))

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
            game_num_match = re.search(r"NBA (\d+)", info)
            teams_match = re.search(r"\|\s*([^@]+)@([^|]+)\|", info)
            if teams_match and game_num_match:
                team1 = normalize_team_name(teams_match.group(1).strip())
                team2 = normalize_team_name(teams_match.group(2).strip())
                game_num = int(game_num_match.group(1))
                streams[game_num] = {"teams": (team1, team2), "url": url, "info": info}
    return streams

def main():
    if not NBA_HTML_FILE.exists():
        print(f"nba.html not found at {NBA_HTML_FILE}")
        return

    print(f"📁 Reading {NBA_HTML_FILE}")
    html_content = NBA_HTML_FILE.read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')

    # DEBUG: Find ALL table rows to understand structure
    print("🔍 Scanning HTML table structure...")
    html_matches = []
    game_times = {}
    
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 2:
            a_tag = tds[0].find('a')
            time_td = tds[1]
            if a_tag and 'nba-streams-' in a_tag.get('href', ''):
                href = a_tag['href']
                text = a_tag.text.strip()
                time_text = time_td.get_text(strip=True)
                
                match_num = int(re.search(r"nba-streams-(\d+)", href).group(1))
                
                print(f"  Game {match_num}: '{text}' | Time text: '{time_text}'")
                
                game_time = parse_game_time(time_text)
                game_times[match_num] = game_time
                
                html_matches.append((match_num, text))

    html_matches.sort(key=lambda x: x[0])
    print(f"✅ Found {len(html_matches)} matches")

    current_time = datetime.now()
    print(f"🕐 Current PC time: {current_time.strftime('%I:%M %p PST')}")

    # Rest of M3U parsing logic (unchanged)
    chunk_size = 3
    outputs = []
    ffmpeg_cmds_by_game = {}
    last_url_index = -1
    matches_on_current_m3u = 0
    all_streams = {}
    fps_60_norm = set(normalize_team_name(t) for t in fps_60_teams)

    for idx, (match_number, match_str) in enumerate(html_matches):
        if matches_on_current_m3u == 0 or matches_on_current_m3u >= chunk_size:
            url_index = (last_url_index + 1) if last_url_index + 1 < len(M3U_URLS) else 0
            current_m3u_url = M3U_URLS[url_index]
            print(f"📥 Downloading M3U: {current_m3u_url}")
            m3u_content = requests.get(current_m3u_url).text
            all_streams = parse_full_m3u(m3u_content)
            last_url_index = url_index
            matches_on_current_m3u = 0

        matches_on_current_m3u += 1

        teams = [t.strip().lower() for t in match_str.split(" vs ")]
        if len(teams) != 2:
            continue

        home_norm, away_norm = map(correct_team_name, teams)
        stream_info = all_streams.get(match_number, None)

        if not stream_info:
            for sinfo in all_streams.values():
                s_team1, s_team2 = sinfo["teams"]
                if {home_norm, away_norm} == {s_team1, s_team2}:
                    stream_info = sinfo
                    break

        if stream_info:
            stream_url = stream_info["url"]
            s_team1, s_team2 = stream_info["teams"]
            contains_60fps = s_team1 in fps_60_norm or s_team2 in fps_60_norm
        else:
            stream_url = None
            contains_60fps = False

        # CRITICAL: Calculate delay for NON-60fps games
        game_time = game_times.get(match_number)
        delay_seconds = calculate_delay_seconds(current_time, game_time) if not contains_60fps else 0

        print(f"Game {match_number}: 60fps={contains_60fps}, delay={delay_seconds}s ({delay_seconds//60}m)")

        home_alias = team_alias_from_name(home_norm)
        away_alias = team_alias_from_name(away_norm)

        # Human readable output
        time_info = f" | {game_time.strftime('%I:%M %p') if game_time else 'No time'} | Delay: {delay_seconds//60}m" if delay_seconds else ""
        outputs.append(f"Game {match_number}:{time_info}")
        outputs.append(f"{home_norm.title()} vs {away_norm.title()}: {stream_url or 'No stream'}{' (60fps)' if contains_60fps else ''}")
        outputs.append("")

        playlist_name = "nba.m3u8" if match_number == 1 else f"nba{match_number}.m3u8"
        
        if stream_url:
            # ALWAYS add sleep for non-60fps
            cmds = []
            if contains_60fps:
                # 60fps: no sleep
                cmds.append((f"{home_norm.title()} - {match_str}", stream_url, home_alias, playlist_name, True, 0))
            else:
                # Non-60fps: ADD SLEEP
                cmds.append((f"{home_norm.title()} - {match_str}", stream_url, home_alias, playlist_name, False, delay_seconds))
            
            ffmpeg_cmds_by_game[match_number] = cmds

    # Write outputs
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(outputs))
    print(f"📄 Wrote {OUTPUT_FILE}")

    # FIXED FFMPEG OUTPUT WITH SLEEP
    with open(FFMPEG_TXT_PATH, 'w', encoding='utf-8') as f:
        for match_number in sorted(ffmpeg_cmds_by_game.keys()):
            for match_str, stream_url, team_alias, playlist_name, is_60fps, delay_seconds in ffmpeg_cmds_by_game[match_number]:
                fps_tag = " (60fps)" if is_60fps else ""
                delay_tag = f" (sleep {delay_seconds//60}m)" if delay_seconds > 0 else ""
                
                f.write(f"# Game {match_number} - {team_alias}{fps_tag}{delay_tag}\n")
                
                # ADD SLEEP FOR NON-60FPS
                if delay_seconds > 0 and not is_60fps:
                    f.write(f'sleep {delay_seconds} && ')
                
                f.write(
                    f'sudo ffmpeg -i "{stream_url}" '
                    '-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 '
                    '-bsf:a aac_adtstoasc -hls_segment_type mpegts '
                    f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                    '-hls_list_size 5 -hls_time 4 '
                    '-hls_flags delete_segments+append_list+omit_endlist '
                    f'/var/www/html/{playlist_name} &\n\n'
                )
    print(f"✅ FIXED: Wrote ffmpeg with sleep commands to {FFMPEG_TXT_PATH}")

if __name__ == "__main__":
    main()
