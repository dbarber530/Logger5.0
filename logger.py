import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

# Finnhub API key
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# GitHub info
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "dbarber530/Logger5.0"
FILE_PATH = "index.html"

# Tickers list (Group A example: replace or extend to 100)
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK.B", "UNH", "JPM",
    "V", "JNJ", "XOM", "PG", "HD", "MA", "CVX", "LLY", "MRK", "PEP"
]

def fetch_ticker_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "symbol": symbol,
            "price": data.get("c"),
            "change": data.get("d"),
            "percent": data.get("dp")
        }
    else:
        return {"symbol": symbol, "price": "Error", "change": "Error", "percent": "Error"}

def build_html(data_list):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    rows = ""
    for data in data_list:
        rows += f"<tr><td>{data['symbol']}</td><td>{data['price']}</td><td>{data['change']}</td><td>{data['percent']}%</td></tr>\n"

    html = f"""
    <html>
    <head>
        <title>Logger5.0</title>
    </head>
    <body>
        <h2>Logger5.0</h2>
        <p>Updated: {now} UTC</p>
        <table border="1" cellpadding="5">
            <tr><th>Symbol</th><th>Price</th><th>Change</th><th>Percent</th></tr>
            {rows}
        </table>
    </body>
    </html>
    """
    return html

def push_to_github(html):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # Get current file SHA
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha")

    content = html.encode("utf-8")
    content_b64 = content.decode("utf-8").encode("utf-8").hex()
    import base64
    content_b64 = base64.b64encode(content).decode("utf-8")

    payload = {
        "message": "Update index.html with live data",
        "content": content_b64,
        "branch": "main",
        "sha": sha
    }

    put_response = requests.put(url, headers=headers, json=payload)
    print("GitHub update response:", put_response.status_code, put_response.text)

if __name__ == "__main__":
    print("Fetching data for all tickers...")
    all_data = [fetch_ticker_data(ticker) for ticker in TICKERS]
    print("Building HTML...")
    html = build_html(all_data)
    print("Pushing to GitHub Pages...")
    push_to_github(html)
    print("Done.")
