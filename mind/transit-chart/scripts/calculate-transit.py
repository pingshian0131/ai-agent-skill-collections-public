#!/usr/bin/env python3
"""
Calculate today's transit chart, optionally overlaid with a natal chart.
Uses kerykeion (Swiss Ephemeris) — no API needed.
Outputs PNG chart image by default + JSON data.

Usage:
  # Transit only (today's sky) → PNG + JSON
  python calculate-transit.py --lat 25.033 --lon 121.565 --tz "Asia/Taipei"

  # Transit + Natal overlay → double-wheel PNG + JSON
  python calculate-transit.py --lat 25.033 --lon 121.565 --tz "Asia/Taipei" \
    --natal-date 1990-05-15 --natal-time 14:30 --natal-tz "Asia/Taipei" \
    --natal-lat 25.033 --natal-lon 121.565 --natal-name "User"

  # JSON only (no image)
  python calculate-transit.py --lat 25.033 --lon 121.565 --tz "Asia/Taipei" --json-only

  # Custom output path
  python calculate-transit.py --lat 25.033 --lon 121.565 --tz "Asia/Taipei" --out /tmp/chart.png
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone as tz

try:
    from kerykeion import AstrologicalSubject, NatalAspects, SynastryAspects
    from kerykeion import ChartDataFactory, ChartDrawer
except ImportError as e:
    print(json.dumps({"error": f"kerykeion not installed: {e}"}))
    sys.exit(1)

SIGN_FULL = {
    "Ari": "Aries", "Tau": "Taurus", "Gem": "Gemini", "Can": "Cancer",
    "Leo": "Leo", "Vir": "Virgo", "Lib": "Libra", "Sco": "Scorpio",
    "Sag": "Sagittarius", "Cap": "Capricorn", "Aqu": "Aquarius", "Pis": "Pisces",
}

PLANET_ATTRS = [
    "sun", "moon", "mercury", "venus", "mars",
    "jupiter", "saturn", "uranus", "neptune", "pluto",
]

ASPECT_NAMES = {
    0: "conjunction", 30: "semi-sextile", 45: "semi-square",
    60: "sextile", 72: "quintile", 90: "square",
    120: "trine", 135: "sesquiquadrate", 144: "biquintile",
    150: "quincunx", 180: "opposition",
}
ASPECT_ORBS = {"conjunction": 8, "sextile": 6, "square": 7, "trine": 8, "opposition": 8}
HOUSE_ATTRS = [
    "first_house", "second_house", "third_house", "fourth_house",
    "fifth_house", "sixth_house", "seventh_house", "eighth_house",
    "ninth_house", "tenth_house", "eleventh_house", "twelfth_house",
]


def sign(abbr):
    return SIGN_FULL.get(abbr, abbr)


def planet_data(obj):
    return {
        "lon": round(obj.abs_pos, 2),
        "sign": sign(obj.sign),
        "degree": round(obj.position, 2),
        "house": obj.house,
        "retrograde": getattr(obj, "retrograde", False),
    }


def extract_bodies(subject):
    bodies = {}
    for name in PLANET_ATTRS:
        obj = getattr(subject, name, None)
        if obj:
            bodies[name.capitalize()] = planet_data(obj)
    # Lunar nodes (kerykeion v5: true_north_lunar_node is populated; mean may be None)
    node = getattr(subject, "true_north_lunar_node", None) or getattr(subject, "mean_north_lunar_node", None)
    if node:
        bodies["North Node"] = planet_data(node)
    return bodies


def extract_houses(subject):
    cusps = []
    for h in HOUSE_ATTRS:
        obj = getattr(subject, h, None)
        if obj:
            cusps.append(round(obj.abs_pos, 2))
    return {
        "asc": round(subject.first_house.abs_pos, 2),
        "mc": round(subject.tenth_house.abs_pos, 2),
        "cusps": cusps,
    }


def extract_aspects(subject):
    """Extract aspects from a single chart (natal or transit self-aspects)."""
    aspects = []
    try:
        natal_aspects = NatalAspects(subject)
        for a in natal_aspects.all_aspects:
            atype = ASPECT_NAMES.get(a.get("aspect_degrees"), "unknown")
            aspects.append({
                "from": a["p1_name"],
                "to": a["p2_name"],
                "type": atype,
                "orb": round(abs(a["orbit"]), 2),
            })
    except Exception:
        aspects = manual_aspects(subject)
    return aspects


def manual_aspects(subject):
    """Fallback manual aspect calculation."""
    aspects = []
    planets = [(n.capitalize(), getattr(subject, n)) for n in PLANET_ATTRS if getattr(subject, n, None)]
    for i, (n1, p1) in enumerate(planets):
        for n2, p2 in planets[i + 1:]:
            angle = abs(p1.abs_pos - p2.abs_pos)
            if angle > 180:
                angle = 360 - angle
            for target, orb_limit, atype in [
                (0, 8, "conjunction"), (60, 6, "sextile"), (90, 7, "square"),
                (120, 8, "trine"), (180, 8, "opposition"),
            ]:
                orb = abs(angle - target)
                if orb <= orb_limit:
                    aspects.append({"from": n1, "to": n2, "type": atype, "orb": round(orb, 2)})
    return aspects


def cross_aspects(natal_subject, transit_subject):
    """Calculate transit-to-natal aspects (cross-chart)."""
    aspects = []
    try:
        syn = SynastryAspects(natal_subject, transit_subject)
        for a in syn.all_aspects:
            atype = ASPECT_NAMES.get(a.get("aspect_degrees"), "unknown")
            aspects.append({
                "natal": a["p1_name"],
                "transit": a["p2_name"],
                "type": atype,
                "orb": round(abs(a["orbit"]), 2),
            })
    except Exception:
        # Fallback: manual cross-aspect calculation
        natal_planets = [(n.capitalize(), getattr(natal_subject, n)) for n in PLANET_ATTRS if getattr(natal_subject, n, None)]
        transit_planets = [(n.capitalize(), getattr(transit_subject, n)) for n in PLANET_ATTRS if getattr(transit_subject, n, None)]
        for n1, p1 in natal_planets:
            for n2, p2 in transit_planets:
                angle = abs(p1.abs_pos - p2.abs_pos)
                if angle > 180:
                    angle = 360 - angle
                for target, orb_limit, atype in [
                    (0, 8, "conjunction"), (60, 6, "sextile"), (90, 7, "square"),
                    (120, 8, "trine"), (180, 8, "opposition"),
                ]:
                    orb = abs(angle - target)
                    if orb <= orb_limit:
                        aspects.append({"natal": n1, "transit": n2, "type": atype, "orb": round(orb, 2)})
    return aspects


def moon_phase(transit_bodies):
    """Calculate moon phase from Sun-Moon elongation."""
    if "Sun" not in transit_bodies or "Moon" not in transit_bodies:
        return {}
    sun_lon = transit_bodies["Sun"]["lon"]
    moon_lon = transit_bodies["Moon"]["lon"]
    elong = (moon_lon - sun_lon) % 360
    phases = [
        "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
        "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent",
    ]
    return {
        "phase": phases[int(elong / 45) % 8],
        "elongation": round(elong, 2),
        "illumination": round((1 - abs(180 - elong) / 180) * 100, 1),
    }


def generate_chart_image(transit, natal, output_path):
    """Generate chart PNG (or SVG fallback). Returns the saved file path."""
    if natal:
        chart_data = ChartDataFactory.create_transit_chart_data(natal._model, transit._model)
    else:
        chart_data = ChartDataFactory.create_natal_chart_data(transit._model)

    drawer = ChartDrawer(chart_data, theme="dark")

    # Generate SVG string with CSS variables resolved (standalone)
    svg_string = drawer.generate_svg_string(minify=True, remove_css_variables=True)

    # Try PNG conversion via cairosvg
    try:
        import cairosvg
        png_path = output_path if output_path.endswith(".png") else output_path.rsplit(".", 1)[0] + ".png"
        cairosvg.svg2png(bytestring=svg_string.encode("utf-8"), write_to=png_path, scale=2)
        return png_path
    except Exception:
        # Fallback: save as SVG
        svg_path = output_path if output_path.endswith(".svg") else output_path.rsplit(".", 1)[0] + ".svg"
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_string)
        return svg_path


def build_subject(name, date_str, time_str, tz_str, lat, lon):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return AstrologicalSubject(
        name=name, year=dt.year, month=dt.month, day=dt.day,
        hour=dt.hour, minute=dt.minute, city="", lat=lat, lng=lon, tz_str=tz_str,
    )


def main():
    parser = argparse.ArgumentParser(description="Transit chart (+ optional natal overlay)")
    # Transit location (required)
    parser.add_argument("--lat", type=float, required=True, help="Observer latitude")
    parser.add_argument("--lon", type=float, required=True, help="Observer longitude")
    parser.add_argument("--tz", required=True, help="Timezone (e.g. Asia/Taipei)")
    # Optional transit date override (defaults to now)
    parser.add_argument("--date", help="Transit date YYYY-MM-DD (default: today)")
    parser.add_argument("--time", help="Transit time HH:MM (default: now)")
    # Optional natal data for overlay
    parser.add_argument("--natal-date", help="Birth date YYYY-MM-DD")
    parser.add_argument("--natal-time", help="Birth time HH:MM")
    parser.add_argument("--natal-tz", help="Birth timezone")
    parser.add_argument("--natal-lat", type=float, help="Birth latitude")
    parser.add_argument("--natal-lon", type=float, help="Birth longitude")
    parser.add_argument("--natal-name", default="Native", help="Name")
    # Output options
    parser.add_argument("--out", help="Output image path (default: auto-generated in /tmp)")
    parser.add_argument("--json-only", action="store_true", help="JSON output only, no chart image")

    args = parser.parse_args()

    # Determine transit datetime
    now = datetime.now(tz.utc)
    transit_date = args.date or now.strftime("%Y-%m-%d")
    transit_time = args.time or now.strftime("%H:%M")

    try:
        transit = build_subject("Transit", transit_date, transit_time, args.tz, args.lat, args.lon)
    except Exception as e:
        print(json.dumps({"error": f"Failed to build transit chart: {e}"}))
        sys.exit(1)

    transit_bodies = extract_bodies(transit)
    result = {
        "type": "transit",
        "date": transit_date,
        "time": transit_time,
        "timezone": args.tz,
        "meta": {"zodiac": "tropical", "house_system": transit.houses_system_name},
        "transit": {
            "houses": extract_houses(transit),
            "bodies": transit_bodies,
            "aspects": extract_aspects(transit),
        },
        "moon": moon_phase(transit_bodies),
    }

    # Natal overlay
    natal = None
    has_natal = args.natal_date and args.natal_time and args.natal_tz
    if has_natal:
        n_lat = args.natal_lat if args.natal_lat is not None else args.lat
        n_lon = args.natal_lon if args.natal_lon is not None else args.lon
        try:
            natal = build_subject(args.natal_name, args.natal_date, args.natal_time, args.natal_tz, n_lat, n_lon)
            result["type"] = "transit+natal"
            result["natal"] = {
                "houses": extract_houses(natal),
                "bodies": extract_bodies(natal),
            }
            result["transit_to_natal"] = cross_aspects(natal, transit)
        except Exception as e:
            result["natal_error"] = str(e)

    # Generate chart image (default behavior)
    if not args.json_only:
        output_path = args.out or os.path.join(tempfile.gettempdir(), f"transit_{transit_date}.png")
        try:
            image_path = generate_chart_image(transit, natal, output_path)
            result["chart_image"] = image_path
        except Exception as e:
            result["chart_error"] = str(e)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
