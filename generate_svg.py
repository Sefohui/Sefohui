#!/usr/bin/env python3
"""
generate_svg.py - Fetches GitHub stats and regenerates profile-card.svg
Run via GitHub Actions daily, or manually.
Requires env var: GITHUB_TOKEN
"""

import os
import json
import urllib.request
import urllib.error
from datetime import date

USERNAME = "Sefohui"

def gh_api(path):
    token = os.environ.get("GITHUB_TOKEN", "")
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USERNAME,
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def fetch_stats():
    # User info
    user = gh_api(f"/users/{USERNAME}")
    repos_data = gh_api(f"/users/{USERNAME}/repos?per_page=100&type=owner")

    stars = sum(r.get("stargazers_count", 0) for r in repos_data)
    public_repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)
    following = user.get("following", 0)

    # Commits: sum up contributions via search
    # (public commits in the last year via events is limited, use search)
    commits = 0
    try:
        result = gh_api(f"/search/commits?q=author:{USERNAME}&per_page=1")
        commits = result.get("total_count", 0)
    except:
        commits = "N/A"

    # Language breakdown across repos
    lang_bytes = {}
    for repo in repos_data:
        if repo.get("fork"):
            continue
        try:
            langs = gh_api(f"/repos/{USERNAME}/{repo['name']}/languages")
            for lang, count in langs.items():
                lang_bytes[lang] = lang_bytes.get(lang, 0) + count
        except:
            pass

    total_bytes = sum(lang_bytes.values()) or 1
    top_langs = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)[:4]
    lang_pcts = [(l, round(b / total_bytes * 100, 1)) for l, b in top_langs]

    return {
        "stars": stars,
        "repos": public_repos,
        "followers": followers,
        "following": following,
        "commits": commits,
        "languages": lang_pcts,
    }

def uptime():
    birth = date(2000, 8, 27)
    today = date.today()
    years = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    m_total = (today.year - birth.year) * 12 + today.month - birth.month
    months = m_total % 12
    # days since last month-anniversary
    try:
        ann = date(today.year, today.month, birth.day)
        if ann > today:
            import calendar
            prev_month = today.month - 1 or 12
            prev_year = today.year if today.month > 1 else today.year - 1
            ann = date(prev_year, prev_month, birth.day)
        days = (today - ann).days
    except:
        days = 0
    return f"{years} years, {months} months, {days} days"

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def build_svg(stats):
    ascii_art = [
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                 =+                                                 ",
        "                                              ++*##*+++                                             ",
        "                                           #%%##***###**++                                          ",
        "                                          %@##%#%%###%%%#**+                                        ",
        "                                          @@%%%*+=++*#%#*#*                                         ",
        "                                          %%#*++===+**###%+                                         ",
        "                               @@@@%*%===+*%*+=======+###=                                          ",
        "                            #%@:*##%%%====+%%#**#+++=-+++=                                          ",
        "                            %@@@@@*@%%%==-=*##*=+=======+*                                          ",
        "                             %%%@@@@%%%++##=-*#*+*======*#:                                         ",
        "                                @%#***@@%#*=---+=++====-*-:-                                        ",
        "                                 #==--*=+=-#==--++=++===:::::                                       ",
        "                                +***%%#%*%*==-=-%#*+++--:--:-----                                   ",
        "                                +*##+++# +++====+***+-::-------:=::-                                ",
        "                                *+*+==@#++++=====%%=----+--==-------+                               ",
        "                                  %*++*%+==*=-=#*#+**=--====-------:-                               ",
        "                                +%%#+#%#===+%#=::-*=+--====--------::                               ",
        "                               +%%%%%%*===%*--::::-=======-=------=::                               ",
        "                               ======*+*==+=---:::::+====-+-----:-=::                               ",
        "                              +=*===+==*==#==-==-:::-=====---------:-                               ",
        "                              +=-=-=+=*+=+=+===-+-:---=+--------::-:                                ",
        "                              =======++=======-==+:::-++===---------                                ",
        "                              =+====++++==++==-=++-:::=-=-==++==---=                                ",
        "                              +++===+**===++#====+=::----+-:-:====-                                 ",
        "                              *+=+=+=+*===++##*==++----=+-+::--::--                                 ",
        "                               *++==**+===++**+++++-=-==+-=-::----                                  ",
        "                                      +===++=++++=+-====:-=-:::--                                   ",
        "                                     *====+*+==++*+=-===-==----==                                   ",
        "                                     +=+=+=++====+++-====-*----==                                   ",
        "                                    ++===+#=======+++-===-=-----==                                  ",
    ]

    langs = stats["languages"]

    # Info lines: (kind, ...)
    info_lines = [
        ("label", "Sefohui@github"),
        ("sep",   "─────────────────────────────────────────────"),
        ("kv",    "OS",       "Windows 11, MacOS Tahoe"),
        ("kv",    "Uptime",   uptime()),
        ("kv",    "Host",     "None"),
        ("kv",    "Kernel",   "Nobody"),
        ("blank", ""),
        ("kv",    "Languages.Programming", "Python, HTML, CSS, JavaScript"),
        ("kv",    "Languages.Real",        "Swedish, English"),
        ("blank", ""),
        ("kv",    "Hobbies",  "Planes, Web Development,"),
        ("cont",  "          Game Development, Music, Tech"),
        ("blank", ""),
        ("sep2",  "─ GitHub Stats ──────────────────────────────"),
        ("kv",    "Repos",     f"{stats['repos']} (Contributed: {stats['repos']})  |  Stars: {stats['stars']}"),
        ("kv",    "Commits",   str(stats['commits'])),
        ("kv",    "Followers", f"{stats['followers']}"),
        ("blank", ""),
        ("sep2",  "─ Top Languages ─────────────────────────────"),
    ]

    # Language bar lines
    bar_width = 50  # chars
    for lang, pct in langs:
        filled = round(pct / 100 * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        info_lines.append(("lang", lang, pct, bar))

    CH = 7.2
    LH = 16
    PAD_X = 12
    PAD_Y = 14

    max_ascii_width = max(len(l.rstrip()) for l in ascii_art)
    INFO_COLS = 56
    GAP = 20
    INFO_START_X = PAD_X + max_ascii_width * CH + GAP

    CYAN   = "#00e5ff"
    PURPLE = "#c792ea"
    DIM    = "#5c6b7a"
    WHITE  = "#cdd6f4"
    GREEN  = "#a6e3a1"
    BG     = "#0d1117"

    total_rows = max(len(ascii_art), len(info_lines))
    SVG_W = int(INFO_START_X + INFO_COLS * CH + PAD_X)
    SVG_H = PAD_Y * 2 + total_rows * LH + 10

    dense_chars = set("@#$%BNQ0M8WRDgwbd")
    mid_chars   = set("*HAVKpqhkmn+")

    lines_svg = []

    for i, row in enumerate(ascii_art):
        y = PAD_Y + i * LH + LH
        spans = []
        for ch in row.rstrip():
            if ch == ' ':
                spans.append(' ')
            elif ch in dense_chars:
                spans.append(f'<tspan fill="{PURPLE}">{esc(ch)}</tspan>')
            elif ch in mid_chars:
                spans.append(f'<tspan fill="{CYAN}">{esc(ch)}</tspan>')
            else:
                spans.append(f'<tspan fill="{CYAN}" opacity="0.7">{esc(ch)}</tspan>')
        lines_svg.append(f'  <text x="{PAD_X}" y="{y}" xml:space="preserve">{"".join(spans)}</text>')

    for i, item in enumerate(info_lines):
        y = PAD_Y + i * LH + LH
        x = INFO_START_X
        kind = item[0]

        if kind == "label":
            name, rest = item[1].split("@", 1)
            lines_svg.append(
                f'  <text x="{x:.1f}" y="{y}" xml:space="preserve">'
                f'<tspan fill="{CYAN}" font-weight="bold">{esc(name)}</tspan>'
                f'<tspan fill="{DIM}">@</tspan>'
                f'<tspan fill="{PURPLE}" font-weight="bold">{esc(rest)}</tspan>'
                f'</text>'
            )
        elif kind == "sep":
            lines_svg.append(f'  <text x="{x:.1f}" y="{y}" fill="{DIM}" xml:space="preserve">{esc(item[1])}</text>')
        elif kind == "sep2":
            lines_svg.append(f'  <text x="{x:.1f}" y="{y}" fill="{PURPLE}" xml:space="preserve">{esc(item[1])}</text>')
        elif kind == "kv":
            _, key, val = item
            dot_count = max(3, 28 - len(key))
            dots = "." * dot_count
            lines_svg.append(
                f'  <text x="{x:.1f}" y="{y}" xml:space="preserve">'
                f'<tspan fill="{DIM}">. </tspan>'
                f'<tspan fill="{CYAN}">{esc(key)}</tspan>'
                f'<tspan fill="{DIM}">: {esc(dots)} </tspan>'
                f'<tspan fill="{WHITE}">{esc(val)}</tspan>'
                f'</text>'
            )
        elif kind == "cont":
            lines_svg.append(f'  <text x="{x:.1f}" y="{y}" fill="{WHITE}" xml:space="preserve">{esc(item[1])}</text>')
        elif kind == "lang":
            _, lang, pct, bar = item
            lines_svg.append(
                f'  <text x="{x:.1f}" y="{y}" xml:space="preserve">'
                f'<tspan fill="{DIM}">  </tspan>'
                f'<tspan fill="{CYAN}">{esc(lang):<14}</tspan>'
                f'<tspan fill="{PURPLE}">{esc(bar)}</tspan>'
                f'<tspan fill="{DIM}"> {esc(str(pct))}%</tspan>'
                f'</text>'
            )

    divider_x = int(INFO_START_X - GAP / 2)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">
  <rect width="100%" height="100%" fill="{BG}" rx="8"/>
  <style>
    text {{
      font-family: "Courier New", Courier, monospace;
      font-size: 12px;
      fill: {WHITE};
    }}
  </style>
  <line x1="{divider_x}" y1="{PAD_Y}" x2="{divider_x}" y2="{SVG_H - PAD_Y}" stroke="{DIM}" stroke-width="1" stroke-dasharray="4,4" opacity="0.5"/>
{''.join(chr(10) + l for l in lines_svg)}
</svg>'''

    return svg


if __name__ == "__main__":
    print("Fetching GitHub stats...")
    try:
        stats = fetch_stats()
        print(f"Stats: {stats}")
    except Exception as e:
        print(f"Warning: Could not fetch stats ({e}), using placeholders")
        stats = {
            "stars": 0,
            "repos": 0,
            "followers": 0,
            "following": 0,
            "commits": 0,
            "languages": [("Python", 60.0), ("JavaScript", 30.0), ("HTML", 10.0)],
        }

    svg = build_svg(stats)
    out = "profile-card.svg"
    with open(out, "w") as f:
        f.write(svg)
    print(f"Written: {out}")
