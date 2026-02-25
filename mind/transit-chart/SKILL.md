---
name: transit-chart
description: "Generate transit chart PNG image and data using kerykeion (Swiss Ephemeris). Supports transit-only and transit+natal double-wheel overlay. No API key needed. Use when asked for transit chart, today's sky, planetary positions, transit aspects, transit-to-natal aspects, daily celestial weather, or horoscope chart image."
---

# Transit Chart

Generate transit chart images (PNG) and structured data. Supports single-wheel (transit only) and double-wheel (transit + natal overlay). All local via Swiss Ephemeris.

## Script

```bash
# Transit only — single wheel PNG + JSON
python3 .claude/skills/transit-chart/scripts/calculate-transit.py \
  --lat 25.033 --lon 121.565 --tz "Asia/Taipei"

# Transit + Natal — double wheel PNG + JSON
python3 .claude/skills/transit-chart/scripts/calculate-transit.py \
  --lat 25.033 --lon 121.565 --tz "Asia/Taipei" \
  --natal-date 1990-05-15 --natal-time 14:30 --natal-tz "Asia/Taipei" \
  --natal-lat 25.033 --natal-lon 121.565 --natal-name "User"

# Custom transit date
python3 .claude/skills/transit-chart/scripts/calculate-transit.py \
  --lat 25.033 --lon 121.565 --tz "Asia/Taipei" --date 2026-03-20 --time 12:00

# JSON data only (no image)
python3 .claude/skills/transit-chart/scripts/calculate-transit.py \
  --lat 25.033 --lon 121.565 --tz "Asia/Taipei" --json-only

# Custom output path
python3 .claude/skills/transit-chart/scripts/calculate-transit.py \
  --lat 25.033 --lon 121.565 --tz "Asia/Taipei" --out /tmp/my_chart.png
```

## Output

JSON to stdout. Key fields:

| Field | Description |
|-------|-------------|
| `chart_image` | Path to generated PNG (default: `/tmp/transit_{date}.png`) |
| `transit.bodies` | Planet positions: longitude, sign, degree, house, retrograde |
| `transit.houses` | ASC, MC, 12 cusps |
| `transit.aspects` | Transit self-aspects |
| `moon` | Phase, elongation, illumination % |
| `natal` | (overlay mode) Natal houses + bodies |
| `transit_to_natal` | (overlay mode) Cross-chart aspects |

When sending to Telegram, use `chart_image` path to send the PNG as a photo. After the image is successfully sent, delete the file immediately (`rm <path>`) to avoid accumulating files on the server.

## Dependencies

- **kerykeion** — `pip install kerykeion`
- **cairosvg** — `pip install cairosvg` (for PNG; falls back to SVG if unavailable)
- System **libcairo2** (already in openclaw Docker image)
