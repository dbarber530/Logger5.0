import requests
import os
import datetime
import time
import base64

# ----------------- CONFIG -----------------
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "UNH",
    "JNJ", "HD", "PG", "DIS", "BAC", "PFE", "VZ", "KO", "PEP", "ABBV", "MRK",
    "INTC", "CSCO", "WMT", "T", "ADBE", "CRM", "CMCSA", "NFLX", "ORCL", "ABT",
    "AVGO", "XOM", "CVX", "ACN", "DHR", "TXN", "MCD", "MDT", "NEE", "QCOM",
    "LLY", "AMGN", "UNP", "LOW", "COST", "HON", "UPS", "IBM", "BA", "GE",
    "DE", "CAT", "MMM", "GS", "RTX", "USB", "FDX", "BLK", "AXP", "SBUX",
    "BKNG", "GM", "F", "CVS", "TGT", "MO", "SPGI", "ADI", "ADP", "ZTS", "BDX",
    "GILD", "ISRG", "EW", "VRTX", "REGN", "MRNA", "PANW", "SNPS", "NOW", "FTNT",
    "CRWD", "DDOG", "ZS", "PLTR", "ROKU", "DKNG", "RBLX", "U", "TTD", "SHOP",
    "BILL", "AFRM", "NET", "DOCU", "SQ", "COIN", "HOOD", "SOFI", "LCID", "RIVN"
]

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "dbarber530/Logger5.0"
FILEPATH = "index.html"
# -------------------------------------------

def fetch_quote(ticker):
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
    try:
        r = requests.get(url).json()
        return {
            "price": r.get("c", "N/A"),
            "high": r.get("h", "N/A"),
            "low": r.get("l", "N/A"),
            "prev": r.get("pc", "N/A")
        }
    except Exception as e:
        return {"price": "N/A", "high": "N/A", "low": "N/A", "prev": "N/A"}

def build_html(data, timestamp):
    html = f"""<html>
<head><meta charset="UTF-8"><title>BarberBot Logger 5.0</title></head>
<body style="font-family: monospace; background-color: black; color: white;">
<h2>📈 BarberBot Logger 5.0</h2>
<p>Last Updated: {timestamp}</p>
<table border="1" cellspacing="0" cellpadding="4">
<tr><th>Ticker</th><th>Price</th><th>High</th><th>Low</th><th>Prev Close</th></tr>"""
    for ticker, quote in data.items():
        html += f"<tr><td>{ticker}</td><td>${quote['price']}</td><td>{quote['high']}</td><td>{quote['low']}</td><td>{quote['prev']}</td></tr>"
    html += "</table><hr><h3>📜 Historical Log</h3></body></html>"
    return html

def push_to_github(content, message="update index"):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILEPATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}

    get_resp = requests.get(url, headers=headers)
    sha = get_resp.json().get("sha", None)

    data = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": "main"
    }
    if sha:
        data["sha"] = sha

    put_resp = requests.put(url, headers=headers, json=data)
    return put_resp.status_code == 200 or put_resp.status_code == 201

# -------------------- MAIN LOOP --------------------
while True:
    minute = datetime.datetime.utcnow().minute
    group = TICKERS[:50] if minute % 2 == 0 else TICKERS[50:]
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    results = {ticker: fetch_quote(ticker) for ticker in group}
    html = build_html(results, timestamp)
    success = push_to_github(html)

    print(f"[{timestamp}] Group: {'A' if group == TICKERS[:50] else 'B'} | Status: {'✅ Updated' if success else '❌ Failed'}")

    time.sleep(60)
