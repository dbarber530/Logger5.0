import requests
import time
import os
from datetime import datetime
import pytz
import base64

# === Setup ===
GITHUB_TOKEN = os.getenv("GH_TOKEN")  # NOTE: your variable is GH_TOKEN, not GITHUB_TOKEN
REPO = "dbarber530/Logger5.0"
FILE_PATH = "index.html"
GH_HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

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

# === Data Store ===
cached_a = []
cached_b = []
last_group = "b"

# === Helpers ===
def get_stock_data(ticker):
    try:
        r = requests.get(FINNHUB_URL, params={"symbol": ticker}, headers=FH_HEADERS)
        d = r.json()
        if r.status_code != 200 or "c" not in d:
            print(f"[Error] {ticker}: {r.status_code} | {d}")
            return None
        return {
            "ticker": ticker,
            "price": d["c"],
            "high": d["h"],
            "low": d["l"],
            "open": d["o"],
            "prevClose": d["pc"],
            "change": round(((d["c"] - d["pc"]) / d["pc"]) * 100, 2) if d["pc"] else 0
        }
    except Exception as e:
        print(f"[EXCEPTION] {ticker}: {e}")
        return None

def generate_html(group_a_data, group_b_data, timestamp):
    def build_table(data, group_name):
        rows = ""
        for s in data:
            rows += f"<tr><td>{s['ticker']}</td><td>${s['price']}</td><td>{s['change']}%</td><td>${s['high']}</td><td>${s['low']}</td><td>${s['open']}</td><td>${s['prevClose']}</td></tr>"
        return f"""
        <h2>{group_name}</h2>
        <table border="1" cellspacing="0" cellpadding="4">
        <tr><th>Ticker</th><th>Price</th><th>% Change</th><th>High</th><th>Low</th><th>Open</th><th>Prev Close</th></tr>
        {rows}</table><br>
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
    status = r.status_code
    print(f"[GitHub] Push status: {status} | SHA: {r.json().get('commit', {}).get('sha', 'N/A')}")

# === Loop ===
while True:
    now = datetime.now(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Logger] {now} UTC | Updating...")

    global last_group, cached_a, cached_b

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
