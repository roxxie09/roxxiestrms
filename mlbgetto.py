import requests
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
import platform
import json

def fetch_mlb_games_for_today():
    today = datetime.now().strftime('%Y-%m-%d')
    url = f'http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={today}'

    response = requests.get(url)
    data = response.json()
    games = data.get('dates', [])

    pacific = pytz.timezone('US/Pacific')
    games_list = []

    if not games:
        return games_list

    if platform.system() == 'Windows':
        day_format = '%#d'
    else:
        day_format = '%-d'

    for game_date in games:
        for game in game_date.get('games', []):
            teams = game['teams']
            home_team = teams['home']['team']['name']
            away_team = teams['away']['team']['name']
            game_time_utc_str = game['gameDate']
            game_time_utc = datetime.strptime(game_time_utc_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)
            game_time_pdt = game_time_utc.astimezone(pacific)
            display_time = game_time_pdt.strftime(f'%B {day_format}, %Y %I:%M %p')
            data_start = game_time_pdt.strftime(f'%B {day_format}, %Y %H:%M:%S')
            data_end_time = game_time_pdt + timedelta(hours=12)
            data_end = data_end_time.strftime(f'%B {day_format}, %Y %H:%M:%S')

            games_list.append({
                'teams': f'{away_team} vs {home_team}',
                'display_time': display_time,
                'data_start': data_start,
                'data_end': data_end,
            })
    return games_list

def update_mlb_html(input_file='mlb.html', output_file='mlb.html'):
    with open(input_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    games = fetch_mlb_games_for_today()
    if not games:
        print("No games found for today.")
        return

    tbody = soup.find('tbody')
    if not tbody:
        print("No <tbody> found in HTML.")
        return
    rows = tbody.find_all('tr')

    for i, row in enumerate(rows):
        if i >= len(games):
            break
        game = games[i]
        tds = row.find_all('td')
        if len(tds) < 3:
            continue

        event_td = tds[0]
        a_tag = event_td.find('a')
        if not a_tag:
            a_tag = soup.new_tag('a', href='#')
            event_td.clear()
            event_td.append(a_tag)
        a_tag.string = game['teams']

        tds[1].string = game['display_time']

        countdown_span = tds[2].find('span', class_='countdown-timer')
        if countdown_span:
            countdown_span['data-start'] = game['data_start']
            countdown_span['data-end'] = game['data_end']

    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write(str(soup))

    print(f"Updated MLB schedule written to {output_file}")

def write_mlb_games_to_txt(filename='text.txt'):
    games = fetch_mlb_games_for_today()
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(games, indent=4))
    print(f"Fetched and wrote MLB games to {filename}")

if __name__ == '__main__':
    # Uncomment the one you want to use:
    write_mlb_games_to_txt()         # Writes games JSON to text.txt
    #update_mlb_html()               # Updates HTML (requires 'mlb.html')
