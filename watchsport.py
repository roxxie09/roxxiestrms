import re
from pathlib import Path

ABBREVIATION_MAP = {
    # NBA abbreviations and canonical full names (partial list for brevity)
    "hawks": "atlanta hawks",
    "celtics": "boston celtics",
    "hornets": "charlotte hornets",
    "bulls": "chicago bulls",
    "cavaliers": "cleveland cavaliers",
    "mavericks": "dallas mavericks",
    "nuggets": "denver nuggets",
    "pistons": "detroit pistons",
    "warriors": "golden state warriors",
    "rockets": "houston rockets",
    # ... add more abbreviations as before ...
}

def extract_events_and_links(text):
    events = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(.+?):\s*\[(https?://[^\s\]]+)\]', line)
        if m:
            event = m.group(1).strip()
            url = m.group(2).strip()
        else:
            m = re.match(r'^(.+?):\s*(https?://\S+)', line)
            if m:
                event = m.group(1).strip()
                url = m.group(2).strip().rstrip(' ,')
            else:
                continue
        if event not in events:
            events[event] = url
    return events

def normalize_team_name(name):
    low = name.lower()
    return ABBREVIATION_MAP.get(low, low)

def parse_teams_from_event(event):
    for sep in [' vs ', ' @ ', ' vs. ', ' at ']:
        if sep in event.lower():
            sides = event.lower().split(sep)
            return [normalize_team_name(s.strip()) for s in sides]
    return [normalize_team_name(event)]

def generate_roxie_js(events):
    entries = []
    all_teams = set()
    for event, url in events.items():
        teams = parse_teams_from_event(event)
        teams_sorted = sorted(teams)
        title = " vs ".join(teams_sorted)
        entries.append(f'{{title: "{title}", url: "{url}"}}')
        all_teams.update(teams)
    return "const roxieStreamsCached = [\n  " + ",\n  ".join(entries) + "\n];", all_teams

def generate_teammap_js(all_teams):
    lines = [f'"{team}": "{team}"' for team in sorted(all_teams)]
    for abbr, full_name in ABBREVIATION_MAP.items():
        if full_name in all_teams and abbr not in all_teams:
            lines.append(f'"{abbr}": "{full_name}"')
    return "const teamNameMap = {\n  " + ",\n  ".join(lines) + "\n};"

def generate_full_js(team_map_js, roxie_js):
    return f"""(async () => {{
  if (!window.Fuse) {{
    await new Promise((resolve, reject) => {{
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/fuse.js@7.0.0';
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    }});
  }}

  {team_map_js}

  {roxie_js}

  function normalizeTeamName(name) {{
    return teamNameMap[name.toLowerCase().trim()] || name.toLowerCase().trim();
  }}

  function normalizeTitle(title) {{
    let t = title.toLowerCase().replace(/@/g, 'vs').trim();
    if (!t.includes('vs')) {{
      return normalizeTeamName(t);
    }}
    let teams = t.split('vs').map(s => normalizeTeamName(s.trim()));
    teams.sort();
    return teams.join(' vs ');
  }}

  const normalizedCache = roxieStreamsCached.map(item => ({{
    title: normalizeTitle(item.title),
    url: item.url
  }}));

  const fuse = new Fuse(normalizedCache, {{
    keys: ['title'],
    threshold: 0.3,
    includeScore: true,
    distance: 50,
    ignoreLocation: true,
  }});

  function findBestMatch(eventTitle) {{
    const lowerTitle = eventTitle.toLowerCase();
    if (lowerTitle.includes("ufc")) return "https://roxiestreams.cc/ufc";
    if (lowerTitle.includes("grand prix")) return "https://roxiestreams.cc/f1-streams";

    let teams = [];
    if (lowerTitle.includes("@")) {{
      teams = lowerTitle.split("@").map(t => normalizeTeamName(t.trim()));
    }} else if (lowerTitle.includes("vs")) {{
      teams = lowerTitle.split("vs").map(t => normalizeTeamName(t.trim()));
    }} else {{
      teams = [normalizeTeamName(lowerTitle.trim())];
    }}

    if (teams.length === 0) return 'https://roxiestreams.cc/missing';

    for (const entry of normalizedCache) {{
      for (const team of teams) {{
        if (entry.title.includes(team)) return entry.url;
      }}
    }}
    return 'https://roxiestreams.cc/missing';
  }}

  function getEventTitleFromListDiv(listDiv) {{
    if (!listDiv) return '';
    let titleText = '';
    listDiv.childNodes.forEach(node => {{
      if (node.nodeType === Node.TEXT_NODE) {{
        const trimmed = node.textContent.trim();
        if (trimmed) titleText += trimmed + ' ';
      }}
    }});
    return titleText.trim();
  }}

  function autofillHandler(e) {{
    const gameId = e.currentTarget.getAttribute('data-target');
    const listDiv = e.currentTarget.closest('.list');
    const eventTitle = getEventTitleFromListDiv(listDiv);
    console.log('Extracted event title:', eventTitle, 'for gameId:', gameId);

    // Get league/channel name from .league span; exclude if starts with digit (likely year)
    let channelName = '';
    const leagueSpan = listDiv ? listDiv.querySelector('span.league') : null;
    if (leagueSpan) {{
      const leagueText = leagueSpan.textContent.trim();
      if (!/^\\d/.test(leagueText)) {{
        channelName = leagueText;
      }}
    }}

    setTimeout(() => {{
      const form = document.querySelector(`#form-${{gameId}}`);
      if (!form) {{
        console.warn('Form not found for gameId:', gameId);
        return;
      }}
      const streamUrl = findBestMatch(eventTitle);
      form.querySelector('#site').value = 'RoxieStreams';
      form.querySelector('#url').value = streamUrl;
      form.querySelector('#channel').value = channelName || 'Main';
      form.querySelector('#fps').value = '60';

      const bitrateInput = form.querySelector('#bitrate') || form.querySelector('input[name="bitrate"]');
      if (bitrateInput) bitrateInput.value = '7000';

      const adsInput = form.querySelector('#ads') || form.querySelector('input[name="ads"]') || form.querySelector('input[name="numAds"]');
      if (adsInput) adsInput.value = '0';

      form.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = true);
      console.log(`Autofilled URL: ${{streamUrl}} and channel: ${{channelName}} with bitrate 7000 and ads 0`);
    }}, 300);
  }}

  function attachAutofill() {{
    document.querySelectorAll('button.add.modal-trigger').forEach(button => {{
      button.removeEventListener('click', autofillHandler);
      button.addEventListener('click', autofillHandler);
    }});
  }}

  attachAutofill();
}})();
"""

def main():
    events_path = Path("events.txt")
    js_path = Path("watchsport.txt")
    if not events_path.exists():
        raise SystemExit("events.txt not found.")
    if not js_path.exists():
        raise SystemExit("watchsport.txt not found.")

    events_text = events_path.read_text(encoding='utf-8')
    js_text = js_path.read_text(encoding='utf-8')

    events = extract_events_and_links(events_text)
    roxie_js, all_teams = generate_roxie_js(events)
    team_map_js = generate_teammap_js(all_teams)

    full_js_code = generate_full_js(team_map_js, roxie_js)

    js_path.write_text(full_js_code, encoding='utf-8')
    print("watchsport.txt updated with channel autofill excluding year-leading names.")

if __name__ == "__main__":
    main()
