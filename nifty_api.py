from flask import Flask, jsonify
import yfinance as yf

app = Flask(__name__)

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
            # Disable future warning by specifying auto_adjust explicitly
            data = yf.download(t, period="1d", interval="5m", auto_adjust=False)
            if not data.empty:
                last = data.iloc[-1]
                prev = data.iloc[-2] if len(data) > 1 else last
                pct_change = ((last['Close'].iloc[0] - prev['Close'].iloc[0]) / prev['Close'].iloc[0]) * 100

                result[t] = {
                    'Open': float(last['Open'].iloc[0]),
                    'High': float(last['High'].iloc[0]),
                    'Low': float(last['Low'].iloc[0]),
                    'Close': float(last['Close'].iloc[0]),
                    'Volume': int(last['Volume'].iloc[0]),
                    'PctChange': round(pct_change, 2)
                }
            else:
                result[t] = {'error': 'No data available'}
        except Exception as e:
            result[t] = {'error': str(e)}
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5500, debug=True)
