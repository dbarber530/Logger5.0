import os
import requests
import base64
import time
from datetime import datetime, timezone

# Secure keys pulled from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Repo details
REPO = "dbarber530/Logger5.0"
FILE_PATH = "index.html"
API_URL = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Ticker list (100)
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "UNH",
    "JNJ", "HD", "PG", "DIS", "BAC", "PFE", "VZ", "KO", "PEP", "ABBV",
    "MRK", "INTC", "CSCO", "WMT", "T", "ADBE", "CRM", "CMCSA", "NFLX", "ORCL",
    "AVGO", "TXN", "MCD", "AXP", "DHR", "MDT", "NEE", "QCOM", "LLY", "AMGN",
    "UNP", "LOW", "UPS", "CVX", "COP", "XOM", "ACN", "IBM", "GE", "COST",
    "SBUX", "GS", "BLK", "ISRG", "BA", "BKNG", "DE", "CAT", "PLD", "NOW",
    "SPGI", "TMO", "ZTS", "CI", "MMC", "ADP", "SYK", "ELV", "BDX", "ETN",
    "MO", "VRTX", "CB", "DUK", "SO", "PNC", "CL", "ECL", "APD", "SHW",
    "EXC", "AEP", "ES", "PEG", "D", "XEL", "WEC", "FE", "AEE", "LNT",
    "AWK", "ATO", "SRE", "CNP", "NI", "CMS", "ED", "WTRG", "OGE", "IDA"
]

def get_stock_data(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        data = response.json()

        current = data.get("c", "N/A")
        high = data.get("h", "N/A")
        low = data.get("l", "N/A")
        prev = data.get("pc", "N/A")

        if not all(isinstance(v, (int, float)) for v in [current, high, low, prev]):
            return f"<li><b>{symbol}:</b> $N/A (H: N/A, L: N/A, Prev: N/A)</li>"

        return f"<li><b>{symbol}:</b> ${current:.2f} (H: {high:.2f}, L: {low:.2f}, Prev: {prev:.2f})</li>"
    except Exception:
        return f"<li><b>{symbol}:</b> $N/A (H: N/A, L: N/A, Prev: N/A)</li>"

def build_html(group):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [f"<html><head><meta charset='UTF-8'></head><body>",
             f"<h2>Live Ticker Feed (100 Total)</h2>",
             f"<p><b>Updated:</b> {timestamp}</p><ul>"]
    
    for symbol in group:
        lines.append(get_stock_data(symbol))

    lines.append("</ul></body></html>")
    return "\n".join(lines)

def get_current_content_sha():
    r = requests.get(API_URL, headers=HEADERS)
    if r.status_code == 200:
        return r.json().get("sha", None)
    return None

def update_github(content):
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    sha = get_current_content_sha()

    data = {
        "message": "Update index.html from logger.py",
        "content": encoded,
        "branch": "main"
    }

    if sha:
        data["sha"] = sha

    r = requests.put(API_URL, headers=HEADERS, json=data)
    return r.status_code == 200 or r.status_code == 201

def main():
    print("Starting BarberBot Logger 5.0...")

    while True:
        # Switch groups based on even/odd minute
        minute = datetime.utcnow().minute
        group = tickers[:50] if minute % 2 == 0 else tickers[50:]

        html = build_html(group)
        success = update_github(html)

        print(f"[{datetime.utcnow()}] Group: {'A' if group == tickers[:50] else 'B'} | Status: {'✅ Updated' if success else '❌ Failed'}")

        # Delay to avoid GitHub Pages queue overflow
        time.sleep(90)

if __name__ == "__main__":
    main()
