import os
import requests
from flask import Flask, request, render_template_string
from datetime import datetime
import pytz

# Setup
app = Flask(__name__)
API_KEY = os.environ.get("FINNHUB_API_KEY")

# Define tickers
group_a = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 'UNH', 'XOM', 'JPM',
           'V', 'JNJ', 'LLY', 'AVGO', 'HD', 'MRK', 'MA', 'PEP', 'ABBV', 'PG',
           'COST', 'CVX', 'ADBE', 'BAC', 'KO', 'CRM', 'WMT', 'MCD', 'ACN', 'TMO', 'PFE',
           'NFLX', 'ORCL', 'INTC', 'CSCO', 'ABT', 'DHR', 'VZ', 'QCOM', 'LIN', 'TXN',
           'AMGN', 'NEE', 'HON', 'UPS', 'PM', 'MS', 'RTX', 'IBM', 'BA', 'GE']

group_b = ['NOW', 'AMD', 'SPGI', 'ISRG', 'INTU', 'CAT', 'GS', 'AMAT', 'BKNG', 'MDT',
           'ADI', 'VRTX', 'BLK', 'T', 'MU', 'ZTS', 'DE', 'REGN', 'CI', 'PANW',
           'SYK', 'BDX', 'GILD', 'MO', 'FISV', 'CSX', 'ELV', 'MMC', 'WM', 'NSC',
           'EW', 'SO', 'HCA', 'USB', 'SCHW', 'LRCX', 'ETN', 'ADP', 'PGR', 'PLD',
           'FDX', 'APD', 'C', 'EOG', 'AJG', 'PSX', 'EMR', 'ITW', 'AON', 'CB']

def get_stock_data(tickers):
    data = []
    for ticker in tickers:
        quote_url = f'https://finnhub.io/api/v1/quote?symbol={ticker}&token={API_KEY}'
        r = requests.get(quote_url)
        if r.status_code == 200:
            quote = r.json()
            data.append({
                'ticker': ticker,
                'price': quote.get('c', 'N/A'),
                'change': quote.get('d', 'N/A'),
                'percent': quote.get('dp', 'N/A'),
                'volume': quote.get('v', 'N/A')
            })
        else:
            data.append({'ticker': ticker, 'price': 'N/A', 'change': 'N/A', 'percent': 'N/A', 'volume': 'N/A'})
    return data

@app.route('/')
def index():
    group = request.args.get('group', 'A')
    tickers = group_a if group == 'A' else group_b
    stocks = get_stock_data(tickers)

    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern).strftime('%Y-%m-%d %I:%M:%S %p ET')

    html = f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="300">
        <title>BarberBot Logger</title>
        <style>
            body {{ font-family: Arial; background-color: #121212; color: #fff; }}
            h1 {{ color: #4CAF50; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px; text-align: center; border-bottom: 1px solid #333; }}
            tr:hover {{ background-color: #333; }}
        </style>
    </head>
    <body>
        <h1>BarberBot Logger - Group {group}</h1>
        <p>Updated: {now}</p>
        <table>
            <tr>
                <th>Ticker</th>
                <th>Price</th>
                <th>Change</th>
                <th>%</th>
                <th>Volume</th>
            </tr>
            {''.join(f"<tr><td>{s['ticker']}</td><td>{s['price']}</td><td>{s['change']}</td><td>{s['percent']}%</td><td>{s['volume']}</td></tr>" for s in stocks)}
        </table>
        <br>
        <a href='/?group={"B" if group == "A" else "A"}' style='color: #4CAF50;'>Switch to Group {"B" if group == "A" else "A"}</a>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
