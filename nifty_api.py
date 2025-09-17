from flask import Flask, jsonify
import yfinance as yf

app = Flask(__name__)

# Full list of NIFTY 50 tickers on Yahoo Finance
tickers = [
    "ADANIENT.NS","ASIANPAINT.NS","AXISBANK.NS","BAJAJ-AUTO.NS","BAJFINANCE.NS",
    "BAJAJFINSV.NS","BPCL.NS","BRITANNIA.NS","CIPLA.NS","COALINDIA.NS",
    "DIVISLAB.NS","DRREDDY.NS","EICHERMOT.NS","GRASIM.NS","HCLTECH.NS",
    "HDFC.NS","HDFCBANK.NS","HDFCLIFE.NS","HEROMOTOCO.NS","HINDALCO.NS",
    "HINDUNILVR.NS","ICICIBANK.NS","ITC.NS","INDUSINDBK.NS","INFY.NS",
    "JSWSTEEL.NS","KOTAKBANK.NS","LT.NS","MARUTI.NS","NESTLEIND.NS",
    "NTPC.NS","ONGC.NS","POWERGRID.NS","RELIANCE.NS","SBILIFE.NS",
    "SBIN.NS","SHREECEM.NS","SUNPHARMA.NS","TATACONSUM.NS","TATAMOTORS.NS",
    "TATASTEEL.NS","TECHM.NS","TITAN.NS","ULTRACEMCO.NS","UPL.NS",
    "WIPRO.NS","MARICO.NS","BHARTIARTL.NS","HINDPETRO.NS","INDIGO.NS"
]

@app.route('/nifty')
def nifty_data():
    result = {}
    for t in tickers:
        try:
            # Download latest 5-min data for today
            data = yf.download(t, period="1d", interval="5m")
            if not data.empty:
                last = data.iloc[-1]
                # Calculate % change from previous candle
                prev = data.iloc[-2] if len(data) > 1 else last
                pct_change = ((last['Close'] - prev['Close']) / prev['Close']) * 100
                
                result[t] = {
                    'Open': float(last['Open']),
                    'High': float(last['High']),
                    'Low': float(last['Low']),
                    'Close': float(last['Close']),
                    'Volume': int(last['Volume']),
                    'PctChange': round(pct_change, 2)
                }
            else:
                result[t] = {'error': 'No data available'}
        except Exception as e:
            result[t] = {'error': str(e)}
    return jsonify(result)

# For local testing
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5500, debug=True)
