import os
import requests
from datetime import datetime, timezone
import base64

# ==== CONFIG ====
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "dbarber530/Logger5.0"
FILE_PATH = "index.html"
TICKERS = ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN", "GOOGL", "META", "NFLX", "AMD", "CRM"]
FINNHUB_TOKEN = os.getenv("FINNHUB_TOKEN")
# ================

def fetch_prices():
    prices = []
    for symbol in TICKERS:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_TOKEN}"
        try:
            response = requests.get(url)
            data = response.json()
            price = data.get("c")
            change = data.get("d")
            time = datetime.now().strftime("%H:%M:%S")
            if price:
                prices.append((symbol, price, change, time))
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    return prices

def format_rows(prices):
    rows = ""
    for symbol, price, change, time in prices:
        change_str = f"{change:+.2f}" if change is not None else "N/A"
        rows += f"<tr><td>{symbol}</td><td>${price:.2f}</td><td>{change_str}</td><td>{time}</td></tr>\n"
    return rows

def update_html(prices):
    with open("index.html", "r") as f:
        html = f.read()
    rows = format_rows(prices)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    html = html.replace("<!-- LOGGER_INSERT -->", rows)
    html = html.replace("<!-- LOGGER_TIMESTAMP -->", timestamp)
    with open("index.html", "w") as f:
        f.write(html)

def push_to_github():
    api_url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    with open(FILE_PATH, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    get_res = requests.get(api_url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    sha = get_res.json().get("sha")

    payload = {
        "message": "Update index.html with latest data",
        "content": content,
        "sha": sha
    }

    put_res = requests.put(api_url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }, json=payload)

    if put_res.status_code == 200 or put_res.status_code == 201:
        print("✅ GitHub update successful")
    else:
        print(f"❌ GitHub update failed: {put_res.status_code}")
        print(put_res.text)

if __name__ == "__main__":
    prices = fetch_prices()
    update_html(prices)
    push_to_github()
