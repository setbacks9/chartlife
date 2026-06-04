# -*- coding: utf-8 -*-
"""
✦ 今日星盤運勢 — Flask web app (deployable to Render / Fly / Railway)
Calls life-chart-engine in-process (no subprocess).
"""
import os
from flask import Flask, jsonify, request, send_from_directory

# Import the engine. chart_engine.py is in the same directory.
import chart_engine

HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=None)

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
        return jsonify({
            "ok": True,
            "place_resolved": {"lat": lat, "lon": lon, "tz": tz},
            "chart": result,
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5817"))
    app.run(host="0.0.0.0", port=port)
