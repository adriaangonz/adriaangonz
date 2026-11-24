#!/usr/bin/env python3
"""Genera los SVG del perfil de GitHub de @adriaangonz:
- assets/header-dark.svg y assets/header-light.svg (cabecera estilo terminal Arch/Hyprland)
- assets/commit-invaders-dark.svg y assets/commit-invaders-light.svg (Space Invaders sobre contribuciones reales)
"""
import json
import os
import subprocess
import urllib.request
from pathlib import Path

USERNAME = os.environ.get("GITHUB_USER", "adriaangonz")
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)


def get_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token
    res = subprocess.run(["gh", "auth", "token"], check=True, capture_output=True, text=True)
    return res.stdout.strip()


def fetch_contributions(username: str, token: str) -> dict:
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                weekday
              }
            }
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "commit-invaders-generator",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "errors" in data:
        raise RuntimeError(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def level_for_count(count: int, max_count: int) -> int:
    if count <= 0:
        return 0
    if max_count <= 4:
        return min(count, 4)
    ratio = count / max_count
    if ratio <= 0.25:
        return 1
    if ratio <= 0.50:
        return 2
    if ratio <= 0.75:
        return 3
    return 4


def fmt(n: float) -> str:
    return f"{n:.5f}".rstrip("0").rstrip(".") or "0"


def build_header_svg(theme: str) -> str:
    dark = theme == "dark"
    bg = "#0d1117" if dark else "#ffffff"
    topbar = "#161b22" if dark else "#f6f8fa"
    border = "#30363d" if dark else "#d0d7de"
    text_main = "#e6edf3" if dark else "#1f2328"
    text_muted = "#8b949e" if dark else "#59636e"
    accent = "#58a6ff" if dark else "#0969da"
    accent2 = "#39d353" if dark else "#1a7f37"
    prompt_user = "#39d353" if dark else "#1a7f37"
    glow_bg = "#161b22" if dark else "#f3f6fa"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 232" width="880" height="232" role="img" aria-label="Adrián González - Perfil de GitHub">
  <defs>
    <linearGradient id="accentLine-{theme}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent}"/>
      <stop offset="50%" stop-color="{accent2}"/>
      <stop offset="100%" stop-color="{accent}"/>
    </linearGradient>
    <style>
      .mono {{ font-family: ui-monospace, 'SFMono-Regular', 'JetBrains Mono', Menlo, Consolas, monospace; }}
      .sans {{ font-family: system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; }}
      @keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
      .cursor {{ animation: blink 1.1s steps(1, end) infinite; }}
      @keyframes pulseGlyph {{ 0%, 100% {{ opacity: 0.92; }} 50% {{ opacity: 1; }} }}
      .glyph {{ animation: pulseGlyph 4s ease-in-out infinite; }}
    </style>
  </defs>

  <!-- Window frame -->
  <rect x="1" y="1" width="878" height="230" rx="12" fill="{bg}" stroke="{border}" stroke-width="1.5"/>
  <!-- Top bar -->
  <path d="M13 1.75 H867 A11.25 11.25 0 0 1 878.25 13 V36 H1.75 V13 A11.25 11.25 0 0 1 13 1.75 Z" fill="{topbar}"/>
  <line x1="1" y1="36" x2="879" y2="36" stroke="{border}" stroke-width="1"/>
  <rect x="1" y="35" width="878" height="1.5" fill="url(#accentLine-{theme})" opacity="0.55"/>

  <!-- Window dots + title -->
  <circle cx="22" cy="19" r="5" fill="#ff5f56"/>
  <circle cx="39" cy="19" r="5" fill="#ffbd2e"/>
  <circle cx="56" cy="19" r="5" fill="#27c93f"/>
  <text x="440" y="23" text-anchor="middle" class="mono" font-size="12" fill="{text_muted}">adrian@arch — hyprland — zsh</text>

  <!-- Left badge / geometric Arch-inspired monogram -->
  <rect x="28" y="56" width="164" height="152" rx="10" fill="{glow_bg}" stroke="{border}" stroke-width="1"/>
  <g class="glyph" transform="translate(110, 122)">
    <!-- Minimalist stylized A / peak -->
    <polygon points="0,-46 42,34 26,34 15,12 -15,12 -26,34 -42,34" fill="none" stroke="{accent}" stroke-width="3.2" stroke-linejoin="round"/>
    <polygon points="0,-24 10,0 -10,0" fill="{accent2}" opacity="0.88"/>
    <line x1="-22" y1="22" x2="22" y2="22" stroke="{accent}" stroke-width="2" opacity="0.5"/>
  </g>
  <text x="110" y="191" text-anchor="middle" class="mono" font-size="11.5" font-weight="600" fill="{text_muted}">@adriaangonz</text>

  <!-- Right terminal content -->
  <g transform="translate(220, 74)">
    <text x="0" y="0" class="mono" font-size="13.5"><tspan fill="{prompt_user}" font-weight="700">adrian@arch</tspan><tspan fill="{text_muted}">:</tspan><tspan fill="{accent}" font-weight="700">~</tspan><tspan fill="{text_muted}">$ </tspan><tspan fill="{text_main}">fastfetch --profile </tspan><tspan fill="{accent}" class="cursor">█</tspan></text>

    <line x1="0" y1="14" x2="626" y2="14" stroke="{border}" stroke-width="1" stroke-dasharray="3 3"/>

    <text x="0" y="39" class="mono" font-size="13.5" fill="{accent}" font-weight="700">nombre</text>
    <text x="82" y="39" class="mono" font-size="13.5" fill="{text_muted}">::</text>
    <text x="108" y="39" class="mono" font-size="13.5" fill="{text_main}" font-weight="600">Adrián González</text>

    <text x="0" y="63" class="mono" font-size="13.5" fill="{accent}" font-weight="700">estudios</text>
    <text x="82" y="63" class="mono" font-size="13.5" fill="{text_muted}">::</text>
    <text x="108" y="63" class="mono" font-size="13.5" fill="{text_main}">2.º DAM · Desarrollo de Aplicaciones Multiplataforma</text>

    <text x="0" y="87" class="mono" font-size="13.5" fill="{accent}" font-weight="700">zona</text>
    <text x="82" y="87" class="mono" font-size="13.5" fill="{text_muted}">::</text>
    <text x="108" y="87" class="mono" font-size="13.5" fill="{text_main}">Cantabria, España</text>

    <text x="0" y="111" class="mono" font-size="13.5" fill="{accent}" font-weight="700">entorno</text>
    <text x="82" y="111" class="mono" font-size="13.5" fill="{text_muted}">::</text>
    <text x="108" y="111" class="mono" font-size="13.5" fill="{text_main}">Arch Linux · Hyprland · Docker · Git</text>

    <text x="0" y="135" class="mono" font-size="13.5" fill="{accent}" font-weight="700">enfoque</text>
    <text x="82" y="135" class="mono" font-size="13.5" fill="{text_muted}">::</text>
    <text x="108" y="135" class="mono" font-size="13.5" fill="{text_main}">Apps multiplataforma, backend, bases de datos y automatización</text>
  </g>
</svg>
'''


def build_invaders_svg(calendar: dict, theme: str) -> str:
    dark = theme == "dark"
    bg = "#0d1117" if dark else "#ffffff"
    panel = "#161b22" if dark else "#f6f8fa"
    border = "#30363d" if dark else "#d0d7de"
    text_main = "#e6edf3" if dark else "#1f2328"
    text_muted = "#8b949e" if dark else "#59636e"
    ship_main = "#58a6ff" if dark else "#0969da"
    ship_core = "#e6edf3" if dark else "#ffffff"
    laser_col = "#39d353" if dark else "#1a7f37"
    flash_col = "#ffffff" if dark else "#0969da"
    spark_col = "#58a6ff" if dark else "#2da44e"

    if dark:
        palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
        empty_stroke = "#21262d"
    else:
        palette = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
        empty_stroke = "#e1e4e8"

    weeks = calendar["weeks"]
    total_commits = calendar["totalContributions"]

    # Grid layout
    num_cols = len(weeks)
    cell_size = 12
    gap = 3
    step = cell_size + gap  # 15px
    grid_w = num_cols * step - gap
    svg_w = 880
    svg_h = 224
    grid_x = (svg_w - grid_w) / 2.0
    grid_y = 46.0
    ship_y = 172.0

    max_count = 0
    cells = []
    for col_idx, week in enumerate(weeks):
        for day in week["contributionDays"]:
            c = day["contributionCount"]
            if c > max_count:
                max_count = c
            cells.append((col_idx, day["weekday"], c, day["date"]))

    # Active targets ordered left-to-right, bottom-to-top (like Space Invaders!)
    active = [item for item in cells if item[2] > 0]
    active.sort(key=lambda item: (item[0], -item[1]))

    # Cap animated shots cleanly if user ever has huge commit counts (pick evenly spread <= 90)
    if len(active) > 90:
        stride = len(active) / 90.0
        targets = [active[int(i * stride)] for i in range(90)]
    else:
        targets = active

    # Compute animation timeline
    # Each target has: travel_time + aim_pause + laser_flight + post_delay
    n_targets = len(targets)
    if n_targets == 0:
        # Fallback demo sweep if 0 commits
        total_dur = 8.0
    else:
        # Target total loop ~18s..26s depending on density
        per_slot = min(0.72, max(0.24, 18.0 / n_targets))
        total_dur = max(12.0, n_targets * per_slot + 2.6)

    ship_times = []
    ship_xs = []
    shot_events = []  # (col, row, cx, cy, t_fire, t_hit)

    start_x = grid_x + 12.0
    cur_x = start_x
    cur_t = 0.5
    ship_times.append(0.0)
    ship_xs.append(start_x)

    for idx, (col, row, count, _date) in enumerate(targets):
        tx = grid_x + col * step + cell_size / 2.0
        ty = grid_y + row * step + cell_size / 2.0
        dist = abs(tx - cur_x)

        if n_targets > 0:
            slot = (total_dur - 2.4) / n_targets
        else:
            slot = 0.5

        travel = min(slot * 0.55, max(0.06, dist / 900.0))
        arrive_t = cur_t + travel
        fire_t = arrive_t + slot * 0.12
        flight = min(0.18, slot * 0.25)
        hit_t = fire_t + flight

        ship_times.append(cur_t / total_dur)
        ship_xs.append(cur_x)
        ship_times.append(arrive_t / total_dur)
        ship_xs.append(tx)
        ship_times.append(hit_t / total_dur)
        ship_xs.append(tx)

        shot_events.append((col, row, tx, ty, fire_t / total_dur, hit_t / total_dur))
        cur_x = tx
        cur_t = hit_t + slot * 0.08

    # Return ship smoothly to start during respawn window
    respawn_t = min(0.95, (cur_t + 0.5) / total_dur)
    ship_times.append(respawn_t)
    ship_xs.append(cur_x)
    ship_times.append(0.995)
    ship_xs.append(start_x)
    ship_times.append(1.0)
    ship_xs.append(start_x)

    # Deduplicate/monotonicize keyTimes safely
    clean_kt = []
    clean_val = []
    prev_k = -1.0
    for k, x in zip(ship_times, ship_xs):
        k = max(0.0, min(1.0, k))
        if k <= prev_k + 1e-5:
            k = min(1.0, prev_k + 0.0001)
        clean_kt.append(fmt(k))
        clean_val.append(f"{x:.1f} {ship_y:.1f}")
        prev_k = k
    clean_kt[0] = "0"
    clean_kt[-1] = "1"

    hit_map = {(c, r): t_hit for (c, r, _tx, _ty, _tf, t_hit) in shot_events}

    # Build grid rects
    grid_parts = []
    for col, row, count, _date in cells:
        x = grid_x + col * step
        y = grid_y + row * step
        lvl = level_for_count(count, max_count)
        fill = palette[lvl]
        if lvl == 0:
            grid_parts.append(
                f'    <rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" rx="2.5" '
                f'fill="{fill}" stroke="{empty_stroke}" stroke-width="0.6"/>'
            )
        else:
            t_hit = hit_map.get((col, row))
            if t_hit is not None:
                t_pre = max(0.0001, t_hit - 0.002)
                t_after = min(0.985, t_hit + 0.006)
                t_resp1 = min(0.992, max(t_after + 0.002, respawn_t))
                grid_parts.append(
                    f'    <rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{fill}">'
                    f'<animate attributeName="opacity" values="1;1;0.14;0.14;1" '
                    f'keyTimes="0;{fmt(t_pre)};{fmt(t_after)};{fmt(t_resp1)};1" '
                    f'dur="{total_dur:.2f}s" repeatCount="indefinite"/>'
                    f'</rect>'
                )
            else:
                grid_parts.append(
                    f'    <rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{fill}"/>'
                )

    # Build lasers + hit flashes + pixel sparks
    fx_parts = []
    for _col, _row, tx, ty, t_fire, t_hit in shot_events:
        # Laser bolt traveling upward from ship nose (ship_y - 12) to ty
        t_f0 = max(0.0001, t_fire - 0.001)
        t_h1 = min(0.998, t_hit + 0.002)
        y_start = ship_y - 14.0
        y_end = ty - 4.0
        fx_parts.append(
            f'    <rect x="{tx - 1.5:.1f}" y="{y_start:.1f}" width="3" height="12" rx="1.5" fill="{laser_col}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="0;{fmt(t_f0)};{fmt(t_fire)};{fmt(t_hit)};{fmt(t_h1)};1" '
            f'dur="{total_dur:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{y_start:.1f};{y_start:.1f};{y_end:.1f};{y_end:.1f}" '
            f'keyTimes="0;{fmt(t_fire)};{fmt(t_hit)};1" '
            f'dur="{total_dur:.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )

        # Brief impact flash square
        t_fl_pre = max(0.0001, t_hit - 0.001)
        t_fl_peak = min(0.995, t_hit + 0.003)
        t_fl_end = min(0.998, t_hit + 0.015)
        fx_parts.append(
            f'    <rect x="{tx - 6:.1f}" y="{ty - 6:.1f}" width="12" height="12" rx="2.5" fill="{flash_col}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.95;0;0" '
            f'keyTimes="0;{fmt(t_fl_pre)};{fmt(t_fl_peak)};{fmt(t_fl_end)};1" '
            f'dur="{total_dur:.2f}s" repeatCount="indefinite"/>'
            f'</rect>'
        )

        # 4 pixel sparks bursting diagonally
        t_sp_end = min(0.999, t_hit + 0.022)
        for dx, dy in ((-8, -8), (8, -8), (-8, 8), (8, 8)):
            fx_parts.append(
                f'    <rect x="{tx - 1.5:.1f}" y="{ty - 1.5:.1f}" width="3" height="3" rx="0.5" fill="{spark_col}" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;1;0;0" '
                f'keyTimes="0;{fmt(t_fl_pre)};{fmt(t_hit)};{fmt(t_sp_end)};1" '
                f'dur="{total_dur:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="x" values="{tx - 1.5:.1f};{tx - 1.5:.1f};{tx + dx - 1.5:.1f};{tx + dx - 1.5:.1f}" '
                f'keyTimes="0;{fmt(t_hit)};{fmt(t_sp_end)};1" '
                f'dur="{total_dur:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y" values="{ty - 1.5:.1f};{ty - 1.5:.1f};{ty + dy - 1.5:.1f};{ty + dy - 1.5:.1f}" '
                f'keyTimes="0;{fmt(t_hit)};{fmt(t_sp_end)};1" '
                f'dur="{total_dur:.2f}s" repeatCount="indefinite"/>'
                f'</rect>'
            )

    # Legend squares
    legend_parts = []
    lx0 = svg_w - 118
    for i, col in enumerate(palette):
        legend_parts.append(
            f'<rect x="{lx0 + i * 14}" y="17" width="10" height="10" rx="2" fill="{col}" stroke="{border}" stroke-width="0.5"/>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}" role="img" aria-label="Commit Invaders - Actividad real de {USERNAME}">
  <defs>
    <style>
      .hud {{ font-family: ui-monospace, 'SFMono-Regular', 'JetBrains Mono', Menlo, Consolas, monospace; }}
      @keyframes thruster {{ 0%, 100% {{ opacity: 0.95; }} 50% {{ opacity: 0.35; }} }}
      .flame {{ animation: thruster 0.25s steps(2, end) infinite; }}
    </style>
  </defs>

  <!-- Frame -->
  <rect x="1" y="1" width="{svg_w - 2}" height="{svg_h - 2}" rx="12" fill="{bg}" stroke="{border}" stroke-width="1.5"/>

  <!-- Top HUD -->
  <g transform="translate(24, 15)">
    <!-- Tiny pixel invader icon -->
    <rect x="2" y="0" width="2" height="2" fill="{laser_col}"/>
    <rect x="10" y="0" width="2" height="2" fill="{laser_col}"/>
    <rect x="4" y="2" width="6" height="2" fill="{laser_col}"/>
    <rect x="2" y="4" width="10" height="2" fill="{laser_col}"/>
    <rect x="0" y="6" width="14" height="3" fill="{laser_col}"/>
    <rect x="3" y="6" width="2" height="2" fill="{bg}"/>
    <rect x="9" y="6" width="2" height="2" fill="{bg}"/>
    <rect x="0" y="9" width="2" height="2" fill="{laser_col}"/>
    <rect x="12" y="9" width="2" height="2" fill="{laser_col}"/>
    <rect x="3" y="11" width="3" height="2" fill="{laser_col}"/>
    <rect x="8" y="11" width="3" height="2" fill="{laser_col}"/>
  </g>
  <text x="48" y="26" class="hud" font-size="12" font-weight="700" fill="{text_main}" letter-spacing="1.2">COMMIT INVADERS</text>
  <text x="200" y="26" class="hud" font-size="11" fill="{text_muted}">·  {total_commits} contribuciones  ·  {len(active)} días activos</text>

  <text x="{lx0 - 10}" y="26" text-anchor="end" class="hud" font-size="10" fill="{text_muted}">Menos</text>
  {"".join(legend_parts)}
  <text x="{lx0 + 74}" y="26" class="hud" font-size="10" fill="{text_muted}">Más</text>

  <!-- Contribution grid -->
  <g id="grid">
{chr(10).join(grid_parts)}
  </g>

  <!-- Lasers and impacts -->
  <g id="fx">
{chr(10).join(fx_parts)}
  </g>

  <!-- Horizon line -->
  <line x1="24" y1="194" x2="{svg_w - 24}" y2="194" stroke="{border}" stroke-width="1" stroke-dasharray="4 4"/>

  <!-- Pixel Starfighter -->
  <g id="ship">
    <animateTransform
      attributeName="transform"
      type="translate"
      values="{";".join(clean_val)}"
      keyTimes="{";".join(clean_kt)}"
      dur="{total_dur:.2f}s"
      repeatCount="indefinite"/>
    <!-- Cannon barrel -->
    <rect x="-1.5" y="-12" width="3" height="5" fill="{laser_col}"/>
    <!-- Cockpit & hull -->
    <rect x="-4" y="-7" width="8" height="4" fill="{ship_main}"/>
    <rect x="-2" y="-6" width="4" height="3" fill="{ship_core}"/>
    <!-- Wings -->
    <rect x="-10" y="-3" width="20" height="5" rx="1" fill="{ship_main}"/>
    <rect x="-12" y="0" width="24" height="4" rx="1" fill="{ship_main}"/>
    <rect x="-12" y="-5" width="3" height="5" fill="{ship_main}"/>
    <rect x="9" y="-5" width="3" height="5" fill="{ship_main}"/>
    <!-- Thrusters -->
    <rect x="-6" y="4" width="3" height="4" fill="{laser_col}" class="flame"/>
    <rect x="3" y="4" width="3" height="4" fill="{laser_col}" class="flame"/>
  </g>

  <!-- Footer -->
  <text x="24" y="211" class="hud" font-size="10" fill="{text_muted}">PLAYER 1: @{USERNAME}</text>
  <text x="{svg_w - 24}" y="211" text-anchor="end" class="hud" font-size="10" fill="{text_muted}">AUTO-ACTUALIZADO CON GITHUB ACTIONS</text>
</svg>
'''


def main():
    token = get_token()
    calendar = fetch_contributions(USERNAME, token)

    for theme in ("dark", "light"):
        (ASSETS / f"header-{theme}.svg").write_text(build_header_svg(theme), encoding="utf-8")
        (ASSETS / f"commit-invaders-{theme}.svg").write_text(build_invaders_svg(calendar, theme), encoding="utf-8")

    print(f"SVGs generados en {ASSETS} ({calendar['totalContributions']} contribuciones)")


if __name__ == "__main__":
    main()
