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
    "dever nuggets": "denver nuggets",
    "tornoto raptors": "toronto raptors",
    "washington wizard": "washington wizards",
}

# Teams you want to treat as 60fps priority (will try to use dedicated team channel first)
fps_60_teams = {
    "miami heat",
    "minnesota timberwolves",
    "sacramento kings",
    "cleveland cavaliers",
    "denver nuggets",
    "new york knicks",
    "detroit pistons",
}

def parse_game_time(game_time_str: str):
    current_year = datetime.now().year
    candidates = [
        game_time_str.strip(),
        f"{game_time_str.strip()}, {current_year}",
        f"{game_time_str.strip()} {current_year}",
    ]
    for cand in candidates:
        try:
            return datetime.strptime(cand, "%B %d, %Y %I:%M %p")
        except ValueError:
            continue
    print(f"Could not parse time: '{game_time_str}'")
    return None

def calculate_delay_seconds(current_time, game_time):
    if not game_time:
        return 0
    delta = game_time - current_time
    return max(0, int(delta.total_seconds()))

def normalize_team_name(name: str) -> str:
    name = name.lower().replace(".", "").replace("-", " ")
    if name.startswith("the "):
        name = name[4:]
    return name.strip()

def correct_team_name(name: str) -> str:
    name_norm = normalize_team_name(name)
    return correct_names.get(name_norm, name_norm)

def team_alias_from_name(name: str) -> str:
    alias = normalize_team_name(name).replace(" ", "_").replace(".", "")
    return alias

def parse_m3u_for_games_and_teams(m3u_content: str):
    """
    Returns:
      game_streams: {game_num: {"teams": (team1, team2), "url": game_url, "info": info_str}}
      team_60fps_urls: {team_name_norm: url} for lines like "USA | NBA Detroit Pistons (HD)"
    """
    game_streams = {}
    team_60fps_urls = {}

    lines = m3u_content.splitlines()
    for i in range(len(lines) - 1):
        line = lines[i].strip()
        if not line.startswith("#EXTINF"):
            continue

        info = line.split(",", 1)[1] if "," in line else ""
        url = lines[i + 1].strip()

        # Pattern 1: Game entries like "NBA 01 | ATLANTA HAWKS @ DETROIT PISTONS | ..."
        game_num_match = re.search(r"NBA\s+(\d+)", info, re.IGNORECASE)
        teams_match = re.search(r"\|\s*([^@]+)@\s*([^|]+)\|", info)
        if game_num_match and teams_match:
            game_num = int(game_num_match.group(1))
            team1 = normalize_team_name(teams_match.group(1).strip())
            team2 = normalize_team_name(teams_match.group(2).strip())
            game_streams[game_num] = {
                "teams": (team1, team2),
                "url": url,
                "info": info,
            }
            continue

        # Pattern 2: Dedicated team HD channels like "USA | NBA Detroit Pistons (HD)"
        # This tries to capture "... NBA Detroit Pistons (HD)" or similar.
        if "USA" in info.upper() and "NBA" in info.upper() and "(HD" in info.upper():
            # crude extraction: look for "NBA " then take rest until "(HD"
            m = re.search(r"NBA\s+(.+?)\s*\(HD", info, re.IGNORECASE)
            if m:
                team_name_raw = m.group(1).strip()
                team_norm = normalize_team_name(team_name_raw)
                team_60fps_urls[team_norm] = url

    return game_streams, team_60fps_urls

def main():
    if not NBA_HTML_FILE.exists():
        print(f"nba.html not found at {NBA_HTML_FILE}")
        return

    html_content = NBA_HTML_FILE.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")

    html_matches = []
    game_times = {}

    # Parse NBA games and times from the table
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 2:
            a_tag = tds[0].find("a")
            time_td = tds[1]
            if a_tag and "nba-streams-" in a_tag.get("href", ""):
                href = a_tag["href"]
                text = a_tag.text.strip()
                time_text = time_td.get_text(strip=True)

                num_match = re.search(r"nba-streams-(\d+)", href)
                if not num_match:
                    continue
                match_num = int(num_match.group(1))

                game_time = parse_game_time(time_text)
                game_times[match_num] = game_time
                html_matches.append((match_num, text))

    html_matches.sort(key=lambda x: x[0])
    print(f"Found {len(html_matches)} matches")

    current_time = datetime.now()
    print(f"Current PC time: {current_time.strftime('%I:%M %p PST')}")

    chunk_size = 3
    outputs = []
    ffmpeg_cmds_by_game = {}

    last_url_index = -1
    matches_on_current_m3u = 0
    game_streams = {}
    team_60fps_urls = {}
    fps_60_norm = set(normalize_team_name(t) for t in fps_60_teams)

    for idx, (match_number, match_str) in enumerate(html_matches):
        # Rotate M3U every chunk_size games
        if matches_on_current_m3u == 0 or matches_on_current_m3u >= chunk_size:
            url_index = (last_url_index + 1) if last_url_index + 1 < len(M3U_URLS) else 0
            current_m3u_url = M3U_URLS[url_index]
            print(f"Downloading M3U: {current_m3u_url}")
            m3u_content = requests.get(current_m3u_url).text
            game_streams, team_60fps_urls = parse_m3u_for_games_and_teams(m3u_content)
            last_url_index = url_index
            matches_on_current_m3u = 0

        matches_on_current_m3u += 1

        teams = [t.strip().lower() for t in match_str.split(" vs ")]
        if len(teams) != 2:
            continue

        home_norm, away_norm = map(correct_team_name, teams)

        # Get game-level URL (NBA 01, 02 etc.)
        stream_info = game_streams.get(match_number, None)
        game_url = stream_info["url"] if stream_info else None

        # Per-team 60fps URLs if they exist
        home_team_60_url = team_60fps_urls.get(home_norm)
        away_team_60_url = team_60fps_urls.get(away_norm)

        # Decide if this matchup has any 60fps-capable team (per your set)
        home_is_60_team = home_norm in fps_60_norm
        away_is_60_team = away_norm in fps_60_norm

        game_time = game_times.get(match_number)
        delay_seconds = calculate_delay_seconds(current_time, game_time)

        home_alias = team_alias_from_name(home_norm)
        away_alias = team_alias_from_name(away_norm)

        time_info = ""
        if game_time:
            time_info = f" | {game_time.strftime('%I:%M %p')} | Delay: {delay_seconds//60}m {delay_seconds%60}s"
        outputs.append(f"Game {match_number}{time_info}")
        outputs.append(
            f"{home_norm.title()} vs {away_norm.title()}: "
            f"{game_url or 'No game URL'}"
        )
        outputs.append("")

        playlist_name = "nba.m3u8" if match_number == 1 else f"nba{match_number}.m3u8"

        # Build ffmpeg command entries for this game
        cmds = []

        # Priority logic:
        # 1) If team has a dedicated 60fps URL (USA | NBA Team (HD)) and is in fps_60_teams, use that URL, no sleep.
        # 2) If no dedicated URL, but team is in fps_60_teams, still treat as 60fps and use game_url, no sleep.
        # 3) If neither side is 60fps, use game_url for both sides with sleep.
        # Note: Only add commands when there is some URL.

        if home_is_60_team:
            url_for_home = home_team_60_url or game_url
            if url_for_home:
                cmds.append((url_for_home, home_alias, playlist_name, True, 0))

        if away_is_60_team:
            url_for_away = away_team_60_url or game_url
            if url_for_away:
                cmds.append((url_for_away, away_alias, playlist_name, True, 0))

        # If no 60fps team at all in this matchup, both teams use the game_url with delay
        if not home_is_60_team and not away_is_60_team and game_url:
            cmds.append((game_url, home_alias, playlist_name, False, delay_seconds))
            cmds.append((game_url, away_alias, playlist_name, False, delay_seconds))

        if cmds:
            ffmpeg_cmds_by_game[match_number] = cmds

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(outputs))
    print(f"Wrote matched streams to {OUTPUT_FILE}")

    # Write ffmpeg commands with while-true; sleep only for non-60fps
    with open(FFMPEG_TXT_PATH, "w", encoding="utf-8") as f:
        for match_number in sorted(ffmpeg_cmds_by_game.keys()):
            for stream_url, team_alias, playlist_name, is_60fps, delay_seconds in ffmpeg_cmds_by_game[match_number]:
                fps_tag = " (60fps)" if is_60fps else ""
                delay_tag = f" (sleep {delay_seconds//60}m)" if delay_seconds > 0 and not is_60fps else ""
                f.write(f"# Game {match_number} - {team_alias}{fps_tag}{delay_tag}\n")

                core_cmd = (
                    f'while true; do sudo ffmpeg -i "{stream_url}" '
                    "-c:v copy -c:a aac -ar 44100 -ab 320k -ac 2 "
                    "-bsf:a aac_adtstoasc -hls_segment_type mpegts "
                    f'-hls_segment_filename "/var/www/html/index_{team_alias}%d.js" '
                    "-hls_list_size 5 -hls_time 4 "
                    "-hls_flags delete_segments+append_list+omit_endlist "
                    f"/var/www/html/{playlist_name}; done"
                )

                if delay_seconds > 0 and not is_60fps:
                    f.write(f"sleep {delay_seconds} && {core_cmd}\n\n")
                else:
                    f.write(f"{core_cmd}\n\n")

    print(f"Wrote ffmpeg commands to {FFMPEG_TXT_PATH}")

if __name__ == "__main__":
    main()
