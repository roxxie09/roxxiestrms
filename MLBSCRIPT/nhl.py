import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import sys
import os
import re

PACIFIC_TZ = ZoneInfo("America/Los_Angeles")
HTML_PATH = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nhl.html"

def parse_date_arg(date_str=None):
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%m-%d-%y")
            return dt.strftime("%Y%m%d")
        except ValueError:
            print(f"Invalid date format '{date_str}'. Use MM-DD-YY like 12-8-25.")
            sys.exit(1)
    return datetime.now().strftime("%Y%m%d")

def get_nhl_games(date_ymd):
    url = f"https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?dates={date_ymd}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except:
        url = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    games = []
    for event in data.get("events", []):
        competitions = event.get("competitions", [])
        if not competitions:
            continue
        comp = competitions[0]
        competitors = comp.get("competitors", [])
        if len(competitors) != 2:
            continue

        home = next((c for c in competitors if c.get("homeAway") == "home"), None)
        away = next((c for c in competitors if c.get("homeAway") == "away"), None)
        if not home or not away:
            continue

        home_team = home["team"].get("displayName") or home["team"].get("shortDisplayName")
        away_team = away["team"].get("displayName") or away["team"].get("shortDisplayName")

        start_str = event.get("date")
        try:
            if start_str.endswith('Z'):
                dt_utc = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            else:
                dt_utc = datetime.fromisoformat(start_str)
            
            dt_pacific = dt_utc.astimezone(PACIFIC_TZ)
            
            # Display time: full date + time
            start_display = dt_pacific.strftime("%B %d, %Y %I:%M %p")
            
            # data-start = PST time in YYYY-MM-DD HH:MM:SS format
            start_pst_formatted = dt_pacific.strftime("%Y-%m-%d %H:%M:%S")
            # data-end = start + 1 day
            end_pst = dt_pacific + timedelta(days=1)
            end_pst_formatted = end_pst.strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            print(f"Time parse error for {away_team} vs {home_team}: {e}")
            start_display = "TBD"
            start_pst_formatted = end_pst_formatted = ""

        games.append({
            "matchup": f"{away_team} vs {home_team}",
            "time_display": start_display,
            "start_pst": start_pst_formatted,
            "end_pst": end_pst_formatted
        })
    return games

def replace_soccer_with_nhl(html_content, games):
    if not games:
        return html_content.replace(
            r'<tbody>.*?</tbody>',
            '<tbody><tr><td colspan="3">No NHL games today</td></tr></tbody>',
            1, re.DOTALL | re.IGNORECASE
        )
    
    html_content = re.sub(
        r'<h2[^>]*Upcoming NHL Events[^<]*</h2>',
        '<h2 class="m-0" style="font-family: Kanit, sans-serif; font-weight: bold;">Today\'s NHL Games</h2>',
        html_content, flags=re.IGNORECASE | re.DOTALL
    )
    
    # NHL rows with EMPTY countdown-timer spans
    rows = ""
    for i, game in enumerate(games, 1):
        rows += f'''
        <tr>
            <td><a href="https://roxiestreams.live/nhl-streams-{i}">{game["matchup"]}</a></td>
            <td>{game["time_display"]}</td>
            <td><span class="countdown-timer" data-end="{game["end_pst"]}" data-start="{game["start_pst"]}"></span></td>
        </tr>'''
    
    html_content = re.sub(
        r'<tbody>.*?</tbody>',
        f'<tbody>{rows}</tbody>',
        html_content, 
        flags=re.DOTALL | re.IGNORECASE
    )
    
    return html_content

if __name__ == "__main__":
    date_input = sys.argv[1] if len(sys.argv) > 1 else None
    api_date = parse_date_arg(date_input)
    pretty_date = datetime.strptime(api_date, "%Y%m%d").strftime("%m-%d-%Y")
    
    print(f"Fetching NHL games for {pretty_date}...")
    games = get_nhl_games(api_date)
    
    if not os.path.exists(HTML_PATH):
        print(f"Error: {HTML_PATH} not found!")
        sys.exit(1)
    
    print(f"Updating nhl.html with {len(games)} NHL games...")
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    updated_content = replace_soccer_with_nhl(content, games)
    
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    print(f"✓ Updated! Countdown spans are now empty (JS will fill them)")
    print("Examples:")
    for game in games[:3]:
        print(f"  {game['matchup']} → <span data-end=\"{game['end_pst']}\" data-start=\"{game['start_pst']}\"></span>")
