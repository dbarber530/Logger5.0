import os
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Environment variables
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
GH_TOKEN = os.getenv("GH_TOKEN")

# GitHub Repo Info
REPO_OWNER = "dbarber530"
REPO_NAME = "Logger5.0"
FILE_PATH = "index.html"

HEADERS = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Split 100 tickers into two groups
GROUP_A = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "UNH",
           "JNJ", "HD", "PG", "MA", "DIS", "BAC", "PFE", "VZ", "KO", "PEP",
           "ABBV", "MRK", "INTC", "WMT", "T", "ADBE", "CSCO", "CRM", "CMCSA", "NFLX",
           "ORCL", "ABT", "XOM", "CVX", "COST", "ACN", "DHR", "AVGO", "TXN", "MCD",
           "MDT", "NEE", "QCOM", "LLY", "AMGN", "UNP", "LOW", "MS", "PM", "UPS"]

GROUP_B = ["IBM", "SBUX", "RTX", "BA", "AMAT", "TMO", "INTU", "AMD", "LMT", "BKNG",
           "CAT", "ISRG", "BLK", "SYK", "SPGI", "ADI", "DE", "AXP", "ZTS", "NOW",
           "GILD", "EL", "MMC", "MO", "ADP", "CB", "CI", "GE", "MDLZ", "USB",
           "REGN", "BDX", "VRTX", "FISV", "PLD", "CME", "FDX", "APD", "GM", "HCA",
           "TGT", "CSX", "EW", "SO", "DUK", "PSX", "BK", "KMB", "HUM", "MET"]

def get_ticker_data(ticker):
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        current = data.get("c", "N/A")
        high = data.get("h", "N/A")
        low = data.get("l", "N/A")
        prev = data.get("pc", "N/A")
        return f"<b>{ticker}</b>: ${current} (H: {high}, L: {low}, Prev: {prev})"
    except Exception as e:
        return f"<b>{ticker}</b>: Error fetching data"

def get_current_group():
    return GROUP_A if datetime.utcnow().minute % 2 == 0 else GROUP_B

def fetch_current_data():
    tickers = get_current_group()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    output = f"<h2>Updated: {timestamp}</h2>\n<ul>\n"
    for ticker in tickers:
        output += f"<li>{get_ticker_data(ticker)}</li>\n"
    output += "</ul>\n<hr>\n"
    return output

def get_existing_index():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        content = res.json()
        return content["content"], content["sha"]
    else:
        return "", ""

def push_to_github(new_content, sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    message = f"Auto update {datetime.utcnow().isoformat()}"
    encoded = base64.b64encode(new_content.encode()).decode()
    payload = {
        "message": message,
        "content": encoded,
        "sha": sha
    }
    res = requests.put(url, headers=HEADERS, json=payload)
    return res.status_code in [200, 201]

def main():
    html_head = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Logger5.0</title></head><body>
<h1>Live Ticker Feed (100 Total)</h1>
<div id="latest">
"""
    html_tail = """
</div><details><summary><b>Historical Data</b></summary><div id="history">
<!-- Older data inserted here -->
</div></details></body></html>"""

    current_block = fetch_current_data()
    existing_content, sha = get_existing_index()

    if existing_content:
        decoded = base64.b64decode(existing_content).decode()
        if "<div id=\"history\">" in decoded:
            parts = decoded.split("<div id=\"latest\">")[1].split("</div><details>")
            history_block = decoded.split("<div id=\"history\">")[1].split("</div></details>")[0]
            updated_html = html_head + current_block + "</div><details>" + decoded.split("</div><details>")[1].split("<div id=\"history\">")[0] + "<div id=\"history\">" + current_block + history_block + "</div></details></body></html>"
        else:
            updated_html = html_head + current_block + html_tail
    else:
        updated_html = html_head + current_block + html_tail

    push_to_github(updated_html, sha)

if __name__ == "__main__":
    main()
