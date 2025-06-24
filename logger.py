import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from base64 import b64encode

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "dbarber530"
REPO_NAME = "Logger5.0"
HTML_FILE = "index.html"

# === Group A and B tickers ===
group_a = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "META", "JPM", "UNH", "HD"]
group_b = ["XOM", "V", "PG", "MA", "JNJ", "BAC", "PFE", "KO", "DIS", "PEP"]
groups = [group_a, group_b]
group_index = 0

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def fetch_data(tickers):
    data = []
    for symbol in tickers:
        quote = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}").json()
        if "c" in quote:
            data.append({
                "symbol": symbol,
                "price": quote["c"],
                "high": quote["h"],
                "low": quote["l"],
                "open": quote["o"],
                "prevClose": quote["pc"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    return data

def generate_html(data):
    html = f"<html><head><title>Logger5.0</title></head><body>"
    html += f"<h1>Logger5.0</h1><p>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p><hr>"
    for item in data:
        html += f"""
        <div>
            <strong>{item['symbol']}</strong> | Price: {item['price']} | High: {item['high']} | Low: {item['low']} | Open: {item['open']} | Prev Close: {item['prevClose']}
        </div><br>
        """
    html += "</body></html>"
    return html

def update_github(html_content):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{HTML_FILE}"
    get_response = requests.get(url, headers=headers).json()
    sha = get_response.get("sha", "")

    encoded = b64encode(html_content.encode()).decode()

    payload = {
        "message": "Update index.html with latest data",
        "content": encoded,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    response = requests.put(url, headers=headers, json=payload)
    return response.status_code in [200, 201]

# === Main loop ===
print("Logger started...")
while True:
    tickers = groups[group_index]
    group_index = (group_index + 1) % 2

    stock_data = fetch_data(tickers)
    html = generate_html(stock_data)
    success = update_github(html)

    if success:
        print(f"[{datetime.now()}] index.html updated with Group {group_index + 1}")
    else:
        print(f"[{datetime.now()}] Failed to update GitHub")

    time.sleep(60)
