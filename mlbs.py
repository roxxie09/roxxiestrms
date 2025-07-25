import requests
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
import platform

def fetch_mlb_games_for_today():
    today = datetime.now().strftime('%Y-%m-%d')
    url = f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}'

    response = requests.get(url)
    data = response.json()
    games = data.get('dates', [])

    pacific = pytz.timezone('US/Pacific')
    games_list = []

    if not games:
        return games_list

    # Determine day format specifier based on OS
    if platform.system() == 'Windows':
        day_format = '%#d'   # Windows: no leading zero
    else:
        day_format = '%-d'   # Unix-like: no leading zero

    for game_date in games:
        for game in game_date.get('games', []):
            teams = game['teams']
            home_team = teams['home']['team']['name']
            away_team = teams['away']['team']['name']
            game_time_utc_str = game['gameDate']
            # Parse game start UTC datetime
            game_time_utc = datetime.strptime(game_time_utc_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)
            # Convert to PDT
            game_time_pdt = game_time_utc.astimezone(pacific)
            # Format for display: 'Month Day, Year HH:MM PM' (per your example)
            display_time = game_time_pdt.strftime(f'%B {day_format}, %Y %H:%M') + ' PM'
            # For countdown timers: use format 'Month Day, Year HH:MM:SS'
            data_start = game_time_pdt.strftime(f'%B {day_format}, %Y %H:%M:%S')
            data_end_time = game_time_pdt + timedelta(hours=12)  # 12 hours later for countdown end
            data_end = data_end_time.strftime(f'%B {day_format}, %Y %H:%M:%S')

            games_list.append({
                'teams': f'{away_team} vs {home_team}',
                'display_time': display_time,
                'data_start': data_start,
                'data_end': data_end,
            })
    return games_list

def update_mlb_html(input_file='mlb.html', output_file='mlb.html'):
    # Load the HTML file
    with open(input_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Fetch MLB games data
    games = fetch_mlb_games_for_today()
    if not games:
        print("No games found for today.")
        return

    # Find table body rows (<tbody><tr>...</tr></tbody>)
    tbody = soup.find('tbody')
    if not tbody:
        print("No <tbody> found in HTML.")
        return
    rows = tbody.find_all('tr')

    # Iterate rows and update with game info sequentially
    for i, row in enumerate(rows):
        if i >= len(games):
            break  # No more games to update

        game = games[i]
        tds = row.find_all('td')
        if len(tds) < 3:
            continue  # Unexpected structure, skip row

        # Update Event cell:
        event_td = tds[0]
        a_tag = event_td.find('a')
        if not a_tag:
            # Create <a> tag with placeholder href if none exists
            a_tag = soup.new_tag('a', href='#')
            event_td.clear()
            event_td.append(a_tag)
        # Replace link text with matchup team names
        a_tag.string = game['teams']

        # Update Start Time cell with formatted date/time
        tds[1].string = game['display_time']

        # Update countdown-timer span attributes in 3rd cell
        countdown_span = tds[2].find('span', class_='countdown-timer')
        if countdown_span:
            countdown_span['data-start'] = game['data_start']
            countdown_span['data-end'] = game['data_end']

    # Write updated content to output_file
    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write(str(soup))

    print(f"Updated MLB schedule written to {output_file}")

if __name__ == '__main__':
    update_mlb_html()