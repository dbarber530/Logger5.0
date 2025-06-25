import requests
import base64
import json
import time
from datetime import datetime
import pytz
import os

# ============ CONFIG ============
REPO = "Logger5.0"
OWNER = "dbarber530"
FILE_PATH = "index.html"
BRANCH = "main"

TICKERS = [
    # 100 tickers total
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "BRK.B", "V", "JPM",
    "UNH", "MA", "XOM", "HD", "LLY", "CVX", "PG", "JNJ", "MRK", "ABBV",
    "PEP", "KO", "BAC", "AVGO", "ADBE", "TMO", "COST", "NFLX", "PFE", "ABT",
    "CSCO", "ACN", "MCD", "DHR", "TXN", "WMT", "QCOM", "NEE", "LIN", "WFC",
    "NKE", "BMY", "MS", "UNP", "LOW", "INTC", "AMGN", "RTX", "MDT", "UPS",
    "CRM", "ORCL", "BA", "GE", "IBM", "GS", "BLK", "AXP", "T", "SPGI",
    "ELV", "CVS", "SCHW", "AMT", "ADI", "CI", "ISRG", "C", "ZTS", "DE",
    "USB", "LMT", "PLD", "MO", "SYK", "MMC", "MDLZ", "ADP", "GILD", "PNC",
    "CAT", "SO", "BDX", "CB", "TJX", "ITW", "DUK", "GM", "ETN", "PGR",
    "F", "CL", "APD", "TGT", "AON", "ECL", "ICE", "PSX", "EMR", "HUM"
]

# Split into two groups
group_a = TICKERS[:50]
group_b = TICKERS[50:]

# ============ API KEYS ============
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
GH_TOKEN = os.getenv("GH_TOKEN")

# ============ GLOBAL STATE ============
last_group = "b"
cached_a = []
cached_b = []

# ============ DATA FETCH ============
def get_stock_data(ticker):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
        r = requests.get(url).json()
        return {
            "ticker": ticker,
            "price": r["c"],
            "prevClose": r["pc"],
            "changePercent": round(((r["c"] - r["pc"]) / r["pc"]) * 100, 2) if r["pc"] else 0
        }
    except Exception as e:
        print(f"[Error] {ticker}: {e}")
        return None

# ============ HTML GENERATOR ============
def generate_html(group_a_data, group_b_data, timestamp):
    combined = group_a_data + group_b_data
    combined.sort(key=lambda x: x["ticker"])
    rows = "".join(
        f"<tr><td>{d['ticker']}</td><td>${d['price']:.2f}</td><td>{d['changePercent']}%</td></tr>"
        for d in combined
    )
    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="60">
            <style>
                body {{ font-family: Arial; background: #0d1117; color: #c9d1d9; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #30363d; }}
                th {{ background: #161b22; }}
            </style>
        </head>
        <body>
            <h2>Live Ticker Logger | Updated {timestamp} UTC</h2>
            <table>
                <tr><th>Ticker</th><th>Price</th><th>% Change</th></tr>
                {rows}
            </table>
        </body>
    </html>
    """

# ============ GITHUB PUSH ============
def push_to_github(content):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    get_res = requests.get(url, headers=headers)
    sha = get_res.json().get("sha", "")

    payload = {
        "message": "Update index.html",
        "content": base64.b64encode(content.encode()).decode(),
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    put_res = requests.put(url, headers=headers, data=json.dumps(payload))
    if put_res.status_code == 200 or put_res.status_code == 201:
        print("[GitHub] index.html updated.")
    else:
        print(f"[GitHub] Failed with code {put_res.status_code}: {put_res.text}")

# ============ LOOP ============
while True:
    now = datetime.now(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Logger] {now} UTC | Updating...")

    if last_group == "b":
        print("[Logger] Pulling Group A...")
        group_a_data = [get_stock_data(t) for t in group_a]
        cached_a = [s for s in group_a_data if s]
        last_group = "a"
    else:
        print("[Logger] Pulling Group B...")
        group_b_data = [get_stock_data(t) for t in group_b]
        cached_b = [s for s in group_b_data if s]
        last_group = "b"

    html = generate_html(cached_a, cached_b, now)
    push_to_github(html)

    print("[Logger] Sleeping 5 minutes...\n")
    time.sleep(300)
