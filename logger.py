import requests
import time
import pytz
from datetime import datetime
import base64

API_KEY = "YOUR_FINNHUB_API_KEY"
REPO = "dbarber530/Logger5.0"
BRANCH = "main"
API_URL = f"https://api.github.com/repos/{REPO}/contents/"
HEADERS = {
    "Authorization": "Bearer YOUR_GITHUB_TOKEN",
    "Accept": "application/vnd.github.v3+json"
}

# Define tickers
TICKERS = [
    # Group A
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "JPM", "UNH", "HD", "BAC",
    "XOM", "JNJ", "PFE", "VZ", "KO", "PEP", "ABBV", "MRK", "INTC", "CSCO",
    "WMT", "T", "ADBE", "CRM", "CMCSA", "NFLX", "ORCL", "ABT", "AVGO", "COST",
    "CVX", "ACN", "DHR", "MCD", "MDT", "NEE", "UPS", "TXN", "HON", "LIN",
    "SBUX", "ADI", "ADP", "ZTS", "BDX", "BAX", "GILD", "ISRG", "EW", "VRTX",

    # Group B
    "REGN", "MRNA", "PANW", "SNPS", "FTNT", "CRWD", "DDOG", "ZS", "PLTR", "ROKU",
    "DKNG", "RBLX", "U", "TTD", "SHOP", "BILL", "AFRM", "LULU", "DOCU", "COIN",
    "SQ", "NET", "LCID", "RIVN", "NIO", "LI", "XPEV", "SOFI", "HOOD", "ARKK",
    "ARKW", "SPY", "QQQ", "DIA", "IWM", "USVM", "CALM", "NVTS", "CRVW", "TMO",
    "LLY", "NOW", "WDAY", "TEAM", "SNOW", "MDB", "OKTA", "TTWO", "FSLY", "WFC"
]

GROUP_A = TICKERS[:50]
GROUP_B = TICKERS[50:]
GROUP_FLAG = True  # Toggle

# Stores all known data
cached_data = {}

def get_stock_data(ticker):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={API_KEY}"
        quote = requests.get(url).json()
        if "c" not in quote or quote["c"] == 0:
            return None

        return {
            "ticker": ticker,
            "price": quote.get("c"),
            "high": quote.get("h"),
            "low": quote.get("l"),
            "open": quote.get("o"),
            "prev_close": quote.get("pc"),
            "volume": quote.get("v", "None")
        }
    except:
        return None

def build_html(all_data, timestamp):
    html = "<html><head><meta http-equiv='refresh' content='60'><style>body{background:black;color:white;font-family:monospace;} table{border-collapse:collapse;} td,th{border:1px solid gray;padding:4px;}</style></head><body>"
    html += "<h2>📈 BarberBot Logger 5.0</h2>"
    html += f"<p>Last Updated: {timestamp} UTC</p>"
    html += "<table><tr><th>Ticker</th><th>Price</th><th>High</th><th>Low</th><th>Prev Close</th><th>Vol</th><th>%Chg</th></tr>"

    for ticker in TICKERS:
        data = all_data.get(ticker)
        if data:
            pct = f"{((data['price'] - data['prev_close']) / data['prev_close']) * 100:.2f}%" if data['prev_close'] else "N/A"
            html += (
                f"<tr><td>{ticker}</td><td>{data['price']}</td><td>{data['high']}</td>"
                f"<td>{data['low']}</td><td>{data['prev_close']}</td><td>{data['volume']}</td><td>{pct}</td></tr>"
            )
        else:
            html += f"<tr><td>{ticker}</td>" + "<td>N/A</td>" * 6 + "</tr>"

    html += "</table></body></html>"
    return html

def upload_to_github(file_path, content, message):
    url = f"{API_URL}{file_path}"
    get_response = requests.get(url, headers=HEADERS)
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": message,
        "content": encoded,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    return requests.put(url, headers=HEADERS, json=payload)

def main():
    global GROUP_FLAG
    while True:
        current_group = GROUP_A if GROUP_FLAG else GROUP_B
        GROUP_FLAG = not GROUP_FLAG

        for ticker in current_group:
            result = get_stock_data(ticker)
            if result:
                cached_data[ticker] = result

        utc_time = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        html = build_html(cached_data, utc_time)

        upload_to_github("index.html", html, f"Auto update {utc_time}")
        print(f"Updated HTML @ {utc_time} UTC with {len(current_group)} new entries.")

        time.sleep(300)  # 5-minute interval

if __name__ == "__main__":
    main()
