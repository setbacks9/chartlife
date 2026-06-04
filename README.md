# ✦ 今日星盤運勢

西洋本命星盤 + 人類圖 + 紫微斗數一次算齊，根據出生資料給今日條列建議。
完全離線計算，不需要任何 API key。

## 線上版

部署在 Render 後可分享網址給朋友。

## 本機跑

```bash
pip install -r requirements.txt
python app.py
```

開啟 http://127.0.0.1:5817

## 部署到 Render（免費）

1. 把這個資料夾推到 GitHub（建立新 repo）
2. 到 [render.com](https://render.com) → New + → Web Service
3. 連結你的 GitHub repo
4. Render 會自動偵測 `render.yaml`，按 **Create Web Service**
5. 等 5-10 分鐘第一次建置完成（要編譯 swisseph）
6. 拿到網址後給朋友

**注意**：Render 免費方案閒置 15 分鐘會休眠，第一次喚醒要等 ~30 秒。

## 致謝與授權

這個專案使用 [life-chart-engine](https://github.com/zhenheco/life-chart-engine)（AGPL-3.0）作為計算核心：
- 西洋星盤：Swiss Ephemeris (Moshier)
- 人類圖：基於本命盤的衍生計算
- 紫微斗數：py-iztro

本專案依 AGPL-3.0 授權釋出，原始碼公開於本 repo。

## 檔案結構

```
.
├── app.py              # Flask 伺服器
├── chart_engine.py     # 來自 life-chart-engine 的計算核心
├── index.html          # 前端 UI
├── requirements.txt    # Python 依賴
├── runtime.txt         # Python 3.12（必要，py-iztro 需要）
├── render.yaml         # Render 部署設定
└── README.md
```
