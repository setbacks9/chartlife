# -*- coding: utf-8 -*-
"""
✦ 今日星盤運勢 — Flask web app (deployable to Render / Fly / Railway)
Calls life-chart-engine in-process (no subprocess).
"""
import os
from flask import Flask, jsonify, request, send_from_directory

# Import the engine. chart_engine.py is in the same directory.
import chart_engine
import swisseph as swe

HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=None)

# ---- Transit computation (today's sky) ----
TRANSIT_PLANETS = {
    "太陽": swe.SUN, "月亮": swe.MOON, "水星": swe.MERCURY, "金星": swe.VENUS,
    "火星": swe.MARS, "木星": swe.JUPITER, "土星": swe.SATURN,
    "天王星": swe.URANUS, "海王星": swe.NEPTUNE, "冥王星": swe.PLUTO,
}
SIGNS = ['牡羊','金牛','雙子','巨蟹','獅子','處女','天秤','天蠍','射手','摩羯','水瓶','雙魚']
ASPECT_DEFS = {0: ('合相', 7), 60: ('六分', 5), 90: ('四分', 6),
               120: ('三分', 6), 180: ('對分', 7)}


def compute_transits(target_date_str, tz_offset=0.0):
    """target_date_str: 'YYYY-MM-DD'. Compute planet positions at noon local time."""
    y, m, d = map(int, target_date_str.split('-'))
    jd = swe.julday(y, m, d, 12.0 - tz_offset, swe.GREG_CAL)
    flg = swe.FLG_MOSEPH | swe.FLG_SPEED
    out = {}
    for name, body in TRANSIT_PLANETS.items():
        r = swe.calc_ut(jd, body, flg)
        lon = r[0][0] % 360
        speed = r[0][3]
        sign_idx = int(lon // 30)
        deg = lon - sign_idx * 30
        dd = int(deg)
        mm = int(round((deg - dd) * 60))
        if mm == 60: mm = 0; dd += 1
        out[name] = {
            "lon": round(lon, 4),
            "sign": SIGNS[sign_idx],
            "deg": dd, "min": mm,
            "label": f"{SIGNS[sign_idx]} {dd:02d}°{mm:02d}'",
            "retrograde": speed < 0,
        }
    return out


def compute_transit_aspects(transits, natal_planets):
    """Find aspects between today's transit planets and natal planets."""
    results = []
    for tname, tdata in transits.items():
        tlon = tdata["lon"]
        for natal in natal_planets:
            nname = natal["name"]
            nlon = natal["lon"]
            diff = abs(tlon - nlon) % 360
            if diff > 180:
                diff = 360 - diff
            for target_angle, (atype, orb_limit) in ASPECT_DEFS.items():
                orb = abs(diff - target_angle)
                if orb <= orb_limit:
                    results.append({
                        "transit": tname,
                        "type": atype,
                        "natal": nname,
                        "orb": round(orb, 2),
                        "exact": orb < 1.5,
                    })
                    break
    results.sort(key=lambda x: x["orb"])
    return results

# ---- city lookup (lat, lon, tz_offset) ----
CITIES = {
    # 台灣
    "台北": (25.0330, 121.5654, 8.0), "taipei": (25.0330, 121.5654, 8.0),
    "新北": (25.0120, 121.4657, 8.0),
    "台中": (24.1477, 120.6736, 8.0), "taichung": (24.1477, 120.6736, 8.0),
    "高雄": (22.6273, 120.3014, 8.0), "kaohsiung": (22.6273, 120.3014, 8.0),
    "台南": (22.9999, 120.2270, 8.0), "tainan": (22.9999, 120.2270, 8.0),
    "桃園": (24.9936, 121.3010, 8.0),
    "新竹": (24.8138, 120.9675, 8.0),
    # 亞洲
    "東京": (35.6762, 139.6503, 9.0), "tokyo": (35.6762, 139.6503, 9.0),
    "大阪": (34.6937, 135.5023, 9.0), "osaka": (34.6937, 135.5023, 9.0),
    "首爾": (37.5665, 126.9780, 9.0), "seoul": (37.5665, 126.9780, 9.0),
    "北京": (39.9042, 116.4074, 8.0), "beijing": (39.9042, 116.4074, 8.0),
    "上海": (31.2304, 121.4737, 8.0), "shanghai": (31.2304, 121.4737, 8.0),
    "廣州": (23.1291, 113.2644, 8.0),
    "深圳": (22.5431, 114.0579, 8.0),
    "香港": (22.3193, 114.1694, 8.0), "hong kong": (22.3193, 114.1694, 8.0), "hk": (22.3193, 114.1694, 8.0),
    "澳門": (22.1987, 113.5439, 8.0), "macau": (22.1987, 113.5439, 8.0),
    "新加坡": (1.3521, 103.8198, 8.0), "singapore": (1.3521, 103.8198, 8.0),
    "曼谷": (13.7563, 100.5018, 7.0), "bangkok": (13.7563, 100.5018, 7.0),
    "吉隆坡": (3.1390, 101.6869, 8.0), "kuala lumpur": (3.1390, 101.6869, 8.0),
    "馬尼拉": (14.5995, 120.9842, 8.0), "manila": (14.5995, 120.9842, 8.0),
    # 歐美
    "倫敦": (51.5074, -0.1278, 0.0), "london": (51.5074, -0.1278, 0.0),
    "巴黎": (48.8566, 2.3522, 1.0), "paris": (48.8566, 2.3522, 1.0),
    "柏林": (52.5200, 13.4050, 1.0), "berlin": (52.5200, 13.4050, 1.0),
    "羅馬": (41.9028, 12.4964, 1.0), "rome": (41.9028, 12.4964, 1.0),
    "馬德里": (40.4168, -3.7038, 1.0), "madrid": (40.4168, -3.7038, 1.0),
    "紐約": (40.7128, -74.0060, -5.0), "new york": (40.7128, -74.0060, -5.0), "nyc": (40.7128, -74.0060, -5.0),
    "洛杉磯": (34.0522, -118.2437, -8.0), "los angeles": (34.0522, -118.2437, -8.0), "la": (34.0522, -118.2437, -8.0),
    "舊金山": (37.7749, -122.4194, -8.0), "san francisco": (37.7749, -122.4194, -8.0),
    "芝加哥": (41.8781, -87.6298, -6.0), "chicago": (41.8781, -87.6298, -6.0),
    "西雅圖": (47.6062, -122.3321, -8.0), "seattle": (47.6062, -122.3321, -8.0),
    "多倫多": (43.6532, -79.3832, -5.0), "toronto": (43.6532, -79.3832, -5.0),
    "溫哥華": (49.2827, -123.1207, -8.0), "vancouver": (49.2827, -123.1207, -8.0),
    "雪梨": (-33.8688, 151.2093, 10.0), "sydney": (-33.8688, 151.2093, 10.0),
    "墨爾本": (-37.8136, 144.9631, 10.0), "melbourne": (-37.8136, 144.9631, 10.0),
}


def lookup_city(name):
    key = (name or "").strip().lower()
    if key in CITIES:
        return CITIES[key]
    for k, v in CITIES.items():
        if k in key or key in k:
            return v
    return CITIES["台北"]


@app.route("/")
def index():
    return send_from_directory(HERE, "index.html")


@app.route("/api/chart", methods=["POST"])
def chart():
    try:
        data = request.get_json(force=True) or {}
        birth_date = data["birthDate"]      # "YYYY-MM-DD"
        birth_time = data["birthTime"]      # "HH:MM"
        place = data.get("birthPlace", "台北")
        target = data.get("target") or birth_date

        lat, lon, tz = lookup_city(place)
        y, m, d = map(int, birth_date.split("-"))
        hh, mi = map(int, birth_time.split(":"))

        inp = {
            "name": "anonymous",
            "gender": "女",
            "date": (y, m, d),
            "time": (hh, mi),
            "tz_offset": float(tz),
            "lat": float(lat),
            "lon": float(lon),
            "target": target,
        }
        result = chart_engine.build_json(inp)
        # Compute today's transits + aspects to natal
        transits = compute_transits(target, tz_offset=float(tz))
        t_aspects = compute_transit_aspects(transits, result["western"]["planets"])
        return jsonify({
            "ok": True,
            "place_resolved": {"lat": lat, "lon": lon, "tz": tz},
            "chart": result,
            "transits": transits,
            "transit_aspects": t_aspects,
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5817"))
    app.run(host="0.0.0.0", port=port)
