import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # ← Add up to 100 tickers here
OWNER = "dbarber530"
REPO = "Logger5.0"
FILE_PATH = "index.html"
TOKEN = os.getenv("GH_TOKEN")

def get_stock_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        data["symbol"] = symbol
        return data
    return None

def build_html(data_list):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    rows = "".join(
        f"""
        <tr>
            <td>{q['symbol']}</td>
            <td>{q.get('c', 0):.2f}</td>
            <td>{q.get('pc', 0):.2f}</td>
            <td>{q.get('h', 0):.2f}</td>
            <td>{q.get('l', 0):.2f}</td>
            <td>{q.get('o', 0):.2f}</td>
            <td>{q.get('t', '')}</td>
        </tr>
        """ for q in data_list
    )

    html = f"""
    <html>
    <head><title>Logger5.0</title></head>
    <body>
    <h2>Logger5.0</h2>
    <p>Updated: {now}</p>
    <table border="1" cellspacing="0" cellpadding="4">
        <tr>
            <th>Symbol</th><th>Current</th><th>Prev Close</th><th>High</th><th>Low</th><th>Open</th><th>Timestamp</th>
        </tr>
        {rows}
    </table>
    </body>
    </html>
    """
    return html

def update_github(html_content):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    get_response = requests.get(url, headers=headers)
    sha = get_response.json().get("sha")

    import base64
    encoded_content = base64.b64encode(html_content.encode()).decode()
    data = {
        "message": "Update index.html with latest data",
        "content": encoded_content,
        "sha": sha
    }
    response = requests.put(url, headers=headers, json=data)
    print("GitHub update status:", response.status_code, response.text)

def main():
    all_data = []
    for ticker in TICKERS:
        q = get_stock_data(ticker)
        if q:
            all_data.append(q)
    html = build_html(all_data)
    update_github(html)

if __name__ == "__main__":
    main()
