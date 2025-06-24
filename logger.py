import requests
import base64
import os
from datetime import datetime, timedelta
import pytz
import time

# Constants
API_KEY = os.getenv('FINNHUB_API_KEY')
GH_TOKEN = os.getenv('GH_TOKEN')
REPO = 'dbarber530/Logger5.0'
FILEPATH = 'index.html'
HEADERS = {'Authorization': f'token {GH_TOKEN}'}

# Group A and B tickers
GROUP_A = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "UNH",
    "HD", "MA", "XOM", "PFE", "JNJ", "PEP", "KO", "WMT", "BAC", "LLY",
    "NFLX", "ABT", "AVGO", "COST", "MCD", "VZ", "ADBE", "MRK", "T", "INTC",
    "CVX", "CRM", "TMO", "DIS", "WFC", "NKE", "TXN", "LIN", "SBUX", "QCOM",
    "HON", "BA", "GE", "IBM", "GS", "AMD", "NOW", "MDT", "NEE", "PYPL"
]

GROUP_B = [
    "PLTR", "SHOP", "UBER", "SNOW", "ROKU", "CRWD", "F", "GM", "DKNG", "RIVN",
    "UAL", "DAL", "LUV", "SOFI", "AFRM", "TWLO", "SQ", "ZM", "BABA", "NIO",
    "TSM", "ARM", "CCL", "LVS", "WYNN", "CHPT", "LCID", "RIOT", "MARA", "IQ",
    "UAL", "UAL", "UAL", "UAL", "UAL", "UAL", "UAL", "UAL", "UAL", "UAL", 
    "CRVW", "USVM", "CALM", "NVTS", "AXP", "TGT", "LOW", "FDX", "DE", "ETSY"
]

def get_active_group():
    now = datetime.now(pytz.timezone('US/Eastern'))
    return GROUP_A if now.minute % 10 < 5 else GROUP_B

def get_stock_data(symbol):
    url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}'
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return {
            'symbol': symbol,
            'price': data.get('c'),
            'high': data.get('h'),
            'low': data.get('l'),
            'open': data.get('o'),
            'previous_close': data.get('pc'),
            'volume': data.get('v'),
            'timestamp': datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')
        }
    return None

def format_entry(entry):
    return f"<div><b>{entry['symbol']}</b> - Price: {entry['price']} | High: {entry['high']} | Low: {entry['low']} | Open: {entry['open']} | Prev Close: {entry['previous_close']} | Volume: {entry['volume']} | Time: {entry['timestamp']}</div>"

def get_html():
    url = f'https://api.github.com/repos/{REPO}/contents/{FILEPATH}'
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

def update_file(new_data):
    file_info = get_html()
    old_content = base64.b64decode(file_info['content']).decode('utf-8')
    
    updated_content = f"{new_data}\n<hr>\n{old_content}"

    message = f"Update {datetime.now(pytz.timezone('US/Eastern')).isoformat()}"
    data = {
        "message": message,
        "content": base64.b64encode(updated_content.encode("utf-8")).decode("utf-8"),
        "sha": file_info['sha']
    }
    r = requests.put(f'https://api.github.com/repos/{REPO}/contents/{FILEPATH}', headers=HEADERS, json=data)
    r.raise_for_status()

def main():
    group = get_active_group()
    entries = []
    for symbol in group:
        stock = get_stock_data(symbol)
        if stock:
            entries.append(format_entry(stock))
        time.sleep(0.25)  # Respect API rate limit

    html_block = "\n".join(entries)
    update_file(html_block)

if __name__ == "__main__":
    main()
