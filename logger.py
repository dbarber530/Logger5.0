import requests
import time
import os
from datetime import datetime
import pytz
import base64

# === Environment & GitHub Setup ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "dbarber530/Logger5.0"
FILE_PATH = "index.html"
GH_HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# === Finnhub Setup ===
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
FINNHUB_URL = "https://finnhub.io/api/v1/quote"
FH_HEADERS = {"X-Finnhub-Token": FINNHUB_API_KEY}

# === Ticker Groups ===
group_a = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL", "NFLX", "AMD", "INTC",
           "BA", "BABA", "DIS", "T", "VZ", "WMT", "KO", "PEP", "MCD", "SBUX",
           "JNJ", "PFE", "MRNA", "UNH", "ABBV", "XOM", "CVX", "BP", "F", "GM",
           "RIVN", "LCID", "PLTR", "SNOW", "SHOP", "SQ", "PYPL", "AFRM", "COIN", "HOOD",
           "CRSP", "ARKK", "QQQ", "SPY", "DIA", "IWM", "VTI", "USVM", "CALM", "CRVW"]

group_b = ["BIDU", "JD", "NIO", "LI", "TSMC", "ASML", "INTU", "ADBE", "ORCL", "CRM",
           "CSCO", "QCOM", "TXN", "MU", "AVGO", "LRCX", "KLAC", "AMAT", "IBM", "HPQ",
           "AAL", "UAL", "DAL", "LUV", "CCL", "RCL", "NCLH", "Z", "OPEN", "RDFN",
           "ZIM", "FRO", "TNK", "SBLK", "GOGL", "TRMD", "KMI", "OKE", "WMB", "ET",
           "SOFI", "ALLY", "DFS", "AXP", "V", "MA", "BAC", "WFC", "C", "JPM"]

# === Pull Quote Data ===
def get_stock_data(ticker):
    try:
        response = requests.get(FINNHUB_URL, params={"symbol": ticker}, headers=FH_HEADERS)
        data = response.json()
        if response.status_code != 200 or "c" not in data:
            print(f"[Error] {ticker}: Status {response.status_code} | Data: {data}")
            return None
        return {
            "ticker": ticker,
            "price": data["c"],
            "high": data["h"],
            "low": data["l"],
            "open": data["o"],
            "prevClose": data["pc"],
            "change": round(((data["c"] - data["pc"]) / data["pc"]) * 100, 2) if data["pc"] else 0
        }
    except Exception as e:
        print(f"[Exception] {ticker}: {e}")
        return None

# === HTML Generator ===
def generate_html(group_a_data, group_b_data, timestamp):
    def build_table(data, group_name):
        rows = ""
        for stock in data:
            rows += f"<tr><td>{stock['ticker']}</td><td>${stock['price']}</td><td>{stock['change']}%</td><td>${stock['high']}</td><td>${stock['low']}</td><td>${stock['open']}</td><td>${stock['prevClose']}</td></tr>"
        return f"""
        <h2>{group_name}</h2>
        <table border="1" cellspacing="0" cellpadding="4">
        <tr>
            <th>Ticker</th><th>Price</th><th>% Change</th><th>High</th><th>Low</th><th>Open</th><th>Prev Close</th>
        </tr>
        {rows}
        </table><br>
        """

    return f"""
    <html>
    <head><title>BarberBot Logger</title></head>
    <body>
        <h1>BarberBot Live Logger</h1>
        <p><b>Last Updated:</b> {timestamp} UTC</p>
        {build_table(group_a_data, "Group A")}
        {build_table(group_b_data, "Group B")}
    </body>
    </html>
    """

# === GitHub Push Helpers ===
def get_file_sha():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    r = requests.get(url, headers=GH_HEADERS)
    return r.json().get("sha")

def push_to_github(content):
    encoded = base64.b64encode(content.encode()).decode()
    sha = get_file_sha()
    payload = {
        "message": "Auto-update index.html",
        "content": encoded,
        "branch": "main",
        "sha": sha
    }
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    r = requests.put(url, headers=GH_HEADERS, json=payload)
    print(f"[GitHub] Status {r.status_code}: {r.json().get('commit', {}).get('sha', 'No SHA')}")

# === Main Loop ===
while True:
    tz = pytz.timezone("UTC")
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Logger] Updating at {now} UTC...")

    group_a_data = [get_stock_data(t) for t in group_a]
    group_b_data = [get_stock_data(t) for t in group_b]
    group_a_data = [s for s in group_a_data if s]
    group_b_data = [s for s in group_b_data if s]

    html_content = generate_html(group_a_data, group_b_data, now)
    push_to_github(html_content)

    print("[Logger] Sleep 5 min...\n")
    time.sleep(300)
