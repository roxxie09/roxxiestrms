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
            start_display = dt_pacific.strftime("%B %d, %Y %I:%M %p")
            start_pst_formatted = dt_pacific.strftime("%Y-%m-%d %H:%M:%S")
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

def update_nhl_date_section(html_content, games, target_date_str):
    if not games:
        return html_content, False

    pretty_date = datetime.strptime(target_date_str, "%Y%m%d").strftime("%A, %B %d, %Y")
    date_header_text = pretty_date.replace(",", r"\,").replace(" ", r"\s+")
    
    # Check if date header already exists
    if re.search(rf'<td colspan="3"><strong>{date_header_text}</strong></td>', html_content, re.IGNORECASE):
        print(f"⚠️  Date '{pretty_date}' already exists - updating games with correct links...")
        updated = True
    else:
        print(f"✓ Adding new date: {pretty_date}")
        updated = True

    # Remove existing games for this date (anything after date header until next date header or tbody end)
    # First find all date headers
    date_headers = re.findall(r'<tr style="background-color:\s*#333[^>]*>\s*<td colspan="3"><strong>([^<]+)</strong></td>\s*</tr>', html_content, re.IGNORECASE | re.DOTALL)
    
    tbody_match = re.search(r'(<tbody[^>]*>)(.*?)(</tbody>)', html_content, re.DOTALL | re.IGNORECASE)
    if not tbody_match:
        return html_content, False

    before = html_content[:tbody_match.start(2)]
    tbody_content = tbody_match.group(2)
    after = html_content[tbody_match.end(2):]

    # Create new section for this date
    date_header = f'''
        <tr style="background-color: #333; color: white;">
            <td colspan="3"><strong>{pretty_date}</strong></td>
        </tr>'''
    
    new_rows = ""
    for i, game in enumerate(games, 1):
        new_rows += f'''
        <tr>
            <td><a href="https://roxiestreams.live/nhl-streams-{i}">{game["matchup"]}</a></td>
            <td>{game["time_display"]}</td>
            <td><span class="countdown-timer" data-end="{game["end_pst"]}" data-start="{game["start_pst"]}"></span></td>
        </tr>'''

    # Replace or append the section
    new_section = date_header + new_rows
    if re.search(rf'<strong>{date_header_text}</strong>', tbody_content, re.IGNORECASE):
        # Replace existing section for this date
        tbody_content = re.sub(
            rf'<tr style="background-color:?\s*#333[^>]*>.*?<strong>{date_header_text}</strong>.*?(?=<tr style="background-color:?\s*#333|<tr|<tbody|$)',
            new_section,
            tbody_content,
            flags=re.DOTALL | re.IGNORECASE
        )
    else:
        # Append to end
        tbody_content += new_section

    html_content = before + tbody_content + after
    return html_content, updated

if __name__ == "__main__":
    date_input = sys.argv[1] if len(sys.argv) > 1 else None
    api_date = parse_date_arg(date_input)
    pretty_date = datetime.strptime(api_date, "%Y%m%d").strftime("%m-%d-%Y")
    
    print(f"Fetching NHL games for {pretty_date}...")
    games = get_nhl_games(api_date)
    
    if not os.path.exists(HTML_PATH):
        print(f"Error: {HTML_PATH} not found!")
        sys.exit(1)
    
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    updated_content, changed = update_nhl_date_section(content, games, api_date)
    
    if changed and games:
        with open(HTML_PATH, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"✓ Updated {len(games)} NHL games for {pretty_date}")
        print(f"  Links fixed: nhl-streams-1 through nhl-streams-{len(games)}")
    else:
        print("No changes needed")
