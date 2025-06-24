import os
import requests
import time
from datetime import datetime, timedelta
import pytz

# === CONFIG ===
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "dbarber530/Logger5.0"
BRANCH = "main"
FILE_PATH = "index.html"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
BASE_URL = "https://finnhub.io/api/v1/quote"
GROUP_A = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'JNJ', 'UNH',
           'HD', 'PG', 'MA', 'V', 'PEP', 'KO', 'DIS', 'MCD', 'VZ', 'CSCO',
           'WMT', 'PFE', 'XOM', 'CVX', 'NKE', 'ORCL', 'ABT', 'INTC', 'CRM', 'QCOM',
           'BAC', 'T', 'ADBE', 'CMCSA', 'TMO', 'AVGO', 'LLY', 'ACN', 'COST', 'MDT',
           'DHR', 'AMGN', 'HON', 'TXN', 'UNP', 'UPS', 'NEE', 'MS', 'LOW', 'LIN']
GROUP_B = ['AMD', 'BA', 'BLK', 'BKNG', 'C', 'CAT', 'DE', 'DUK', 'ETN', 'F',
           'FDX', 'GE', 'GM', 'GS', 'IBM', 'ISRG', 'LMT', 'MMM', 'MO', 'MRK',
           'NFLX', 'NOW', 'PLD', 'PYPL', 'RTX', 'SBUX', 'SCHW', 'SO', 'SPGI', 'SYK',
           'TDG', 'TGT', 'TMUS', 'TRV', 'USB', 'WBA', 'ZTS', 'ZBRA', 'WELL', 'REGN',
           'ADP', 'APD', 'AXP', 'BDX', 'BIIB', 'BK', 'BSX', 'CB', 'CI', 'CRVW']

# === FUNCTIONS ===

def fetch_quote(symbol):
    try:
        res = requests.get(BASE_URL, params={"symbol": symbol, "token": FINNHUB_API_KEY})
        data = res.json()
        return {
            "symbol": symbol,
            "price": data.get("c", "N/A"),
            "high": data.get("h", "N/A"),
            "low": data.get("l", "N/A"),
            "open": data.get("o", "N/A"),
            "prevClose": data.get("pc", "N/A"),
            "volume": data.get("v", "N/A")
        }
    except:
        return {"symbol": symbol, "price": "Err", "high": "Err", "low": "Err", "open": "Err", "prevClose": "Err", "volume": "Err"}

def build_table(quotes, title):
    now = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    html = f"<h2>{title} (Last Updated: {now})</h2><table border='1'><tr><th>Ticker</th><th>Price</th><th>High</th><th>Low</th><th>Open</th><th>Prev Close</th><th>Volume</th></tr>"
    for q in quotes:
        html += f"<tr><td>{q['symbol']}</td><td>{q['price']}</td><td>{q['high']}</td><td>{q['low']}</td><td>{q['open']}</td><td>{q['prevClose']}</td><td>{q['volume']}</td></tr>"
    html += "</table><br>"
    return html

def get_existing_html():
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{FILE_PATH}"
    r = requests.get(url)
    return r.text if r.status_code == 200 else ""

def update_github(content):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    existing = requests.get(url, headers=HEADERS).json()
    encoded = content.encode("utf-8")
    import base64
    data = {
        "message": "Auto update ticker data",
        "content": base64.b64encode(encoded).decode("utf-8"),
        "sha": existing.get("sha")
    }
    res = requests.put(url, headers=HEADERS, json=data)
    if res.status_code == 200 or res.status_code == 201:
        print("✅ GitHub updated successfully.")
    else:
        print("❌ GitHub update failed:", res.text)

# === MAIN LOOP ===
is_a = True
while True:
    print("⏳ Fetching ticker data...")
    group = GROUP_A if is_a else GROUP_B
    quotes = [fetch_quote(sym) for sym in group]
    section_html = build_table(quotes, f"Group {'A' if is_a else 'B'}")

    full_html = get_existing_html()

    if is_a:
        start = full_html.find("<h2>Group A")
        end = full_html.find("<h2>Group B")
        before = full_html[:start] if start != -1 else ""
        after = full_html[end:] if end != -1 else ""
        full_html = before + section_html + after
    else:
        start = full_html.find("<h2>Group B")
        before = full_html[:start] if start != -1 else full_html
        full_html = before + section_html

    update_github(full_html)
    is_a = not is_a
    print("✅ Update complete. Sleeping 5 minutes.\n")
    time.sleep(300)
