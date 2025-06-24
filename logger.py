import os
import requests
import datetime
import pytz
import time

# ✅ SETTINGS
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY")
GITHUB_TOKEN = os.environ.get("GH_TOKEN")
REPO_OWNER = "dbarber530"
REPO_NAME = "Logger5.0"
FILE_PATH = "index.html"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ✅ TICKERS (SPLIT A/B)
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "UNH",
    "JNJ", "HD", "PG", "DIS", "BAC", "PFE", "PEP", "KO", "MRK", "T",
    "CSCO", "CMCSA", "NFLX", "ADBE", "INTC", "CRM", "ORCL", "AVGO", "QCOM", "AMD",
    "DE", "GE", "CAT", "MMM", "GS", "RTX", "FDX", "BLK", "USB", "AXP",
    "SBUX", "BKNG", "GM", "F", "CVS", "TGT", "MO", "SPGI", "ABBV", "WMT",
    "ADI", "ADP", "ZTS", "BDX", "GILD", "ISRG", "EW", "VRTX", "REGN", "MRNA",
    "PANW", "SNPS", "NOW", "FTNT", "CRWD", "DDOG", "ZS", "PLTR", "ROKU", "DKNG",
    "RBLX", "U", "TTD", "SHOP", "BILL", "AFRM", "LULU", "DOCU", "COIN", "SQ",
    "NET", "LCID", "RIVN", "LI", "NIO", "XPEV", "SOFI", "HOOD", "ARKK", "ARKW",
    "SPY", "QQQ", "DIA", "IWM", "USVM", "CALM", "NVTS", "CRVW"
]

# ✅ GROUPING
group = tickers[:50] if datetime.datetime.now(pytz.UTC).minute % 10 < 5 else tickers[50:]

# ✅ BUILD HTML
def build_html(data, timestamp_utc):
    html = f"""<html>
<head>
  <meta http-equiv="refresh" content="300">
  <style>
    body {{ background-color: black; color: white; font-family: monospace; }}
    table {{ border-collapse: collapse; }}
    th, td {{ border: 1px solid white; padding: 4px; }}
  </style>
</head>
<body>
<h1>📈 BarberBot Logger 5.0</h1>
<p>Last Updated: {timestamp_utc} UTC</p>
<table>
  <tr><th>Ticker</th><th>Price</th><th>High</th><th>Low</th><th>Prev Close</th><th>Vol</th><th>%Chg</th></tr>"""

    for item in data:
        html += f"<tr><td>{item['ticker']}</td><td>{item['price']}</td><td>{item['high']}</td><td>{item['low']}</td><td>{item['prevClose']}</td><td>{item['volume']}</td><td>{item['percent_change']}%</td></tr>"

    html += "</table></body></html>"
    return html

# ✅ FETCH FROM FINNHUB
def fetch_data(symbols):
    output = []
    for sym in symbols:
        try:
            r = requests.get(f"https://finnhub.io/api/v1/quote?symbol={sym}&token={FINNHUB_API_KEY}")
            d = r.json()
            if "c" in d and d["c"] != 0:
                percent_change = round(((d["c"] - d["pc"]) / d["pc"]) * 100, 2) if d["pc"] else 0
                output.append({
                    "ticker": sym,
                    "price": f"${d['c']:.2f}",
                    "high": f"{d['h']:.2f}",
                    "low": f"{d['l']:.2f}",
                    "prevClose": f"{d['pc']:.2f}",
                    "volume": d.get("v", "N/A"),
                    "percent_change": percent_change
                })
            else:
                output.append({
                    "ticker": sym,
                    "price": "N/A", "high": "N/A", "low": "N/A",
                    "prevClose": "N/A", "volume": "N/A", "percent_change": "N/A"
                })
        except Exception as e:
            output.append({
                "ticker": sym,
                "price": "ERR", "high": "ERR", "low": "ERR",
                "prevClose": "ERR", "volume": "ERR", "percent_change": "ERR"
            })
    return output

# ✅ PUSH TO GITHUB
def push_to_github(content):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

    # Get current SHA
    r = requests.get(url, headers=HEADERS)
    sha = r.json().get("sha")

    message = f"Update index.html at {datetime.datetime.now(pytz.UTC).isoformat()}"
    encoded = content.encode("utf-8")
    import base64
    payload = {
        "message": message,
        "content": base64.b64encode(encoded).decode("utf-8"),
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=HEADERS, json=payload)
    return r.status_code == 200 or r.status_code == 201

# ✅ MAIN LOOP
while True:
    now_utc = datetime.datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
    group_label = 'A' if group == tickers[:50] else 'B'
    print(f"[{now_utc}] Pulling group {group_label}...")

    try:
        data = fetch_data(group)
        html = build_html(data, now_utc)
        success = push_to_github(html)
        status = "✅ Pushed" if success else "❌ Push failed"
    except Exception as e:
        status = f"💥 Error: {e}"

    print(f"[{now_utc}] Group {group_label} | {status}")
    time.sleep(300)  # ⏲️ 5-minute sleep
