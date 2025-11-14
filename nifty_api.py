import ta
import yfinance as yf
import requests
import time
import os
import pandas_ta as ta
from flask import Flask, jsonify,request
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from bs4 import BeautifulSoup
app = Flask(__name__)
CORS(app)
db_config = {
    'host': '192.168.3.53',
    'user': 'ajtitan',
    'password': '1432',
    'database': 'my_stocks'
}
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

def fetch_transcript(video_id):
    url = f"https://youtubetotranscript.com/transcript?v={video_id}"
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'lxml')

    news_post = soup.find("p", {"class": "inline NA text-primary-content"}).find_all("span")
    ans = []
    for row in news_post:
        text = row.get_text(strip=True)
        clean_text = " ".join(text.split())
        ans.append(clean_text)

    return ans
@app.route('/portfolio', methods=['POST'])
def portfolio():
    import traceback, json
    try:
        data = request.get_json()
        user_id = data.get('user') if data else None
        if not user_id:
            return jsonify({"error": "user parameter missing"}), 400

        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor(dictionary=True, buffered=True) as cursor:
                cursor.execute("SELECT data FROM json_files WHERE id = %s", (user_id,))
                row = cursor.fetchone()

        if not row:
            return jsonify({"error": "No portfolio found"}), 404

        portfolio_data = json.loads(row['data'])
        return jsonify(portfolio_data)

    except Exception as e:
        print("ERROR in /portfolio route:\n", traceback.format_exc())
        return jsonify({"error": str(e)}), 500



@app.route("/senti", methods=["GET"])
def google_finance_news():
    symbol = request.args.get("symbol")
    url = f"https://news.google.com/search?q={symbol}&hl=en-IN&gl=IN&ceid=IN:en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    news_list = []
    for item in soup.find_all("a", class_="JtKRv"):
        title = item.text.strip()
        # link = "https://news.google.com/" + item.get("href") if item else None
        news_list.append({"title": title})

    return news_list
@app.route("/transcript", methods=["GET"])
def transcript():
    video_id = request.args.get("video_id")
    if not video_id:
        return jsonify({"error": "Missing video_id parameter"}), 400
    try:
        transcript_data = fetch_transcript(video_id)
        return jsonify({"video_id": video_id, "transcript": transcript_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ipo", methods=['GET'])
def scrape_ipo():
    url = "https://www.screener.in/ipo/recent/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        req = requests.get(url, headers=headers, timeout=10)
        req.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch IPO data", "details": str(e)}), 500

    soup = BeautifulSoup(req.content, 'lxml')
    table = soup.find("table", {"class": "data-table"})

    news_post = table.find("tbody").find_all("tr")
    result = {}

    for idx, row in enumerate(news_post, start=1):
        try:
            company = row.find("span", {"class": "ink-900"}).get_text(strip=True)
            link = "https://www.screener.in" + row.find("a")["href"]
            tds = row.find_all("td")
            date = tds[1].get_text(strip=True)
            IPO_Mcap = tds[2].get_text(strip=True)
            IPO_Price = tds[3].get_text(strip=True)
            Current_Price = tds[4].get_text(strip=True)
            Change_in_price = tds[5].get_text(strip=True)
        except Exception:
            continue


        result[company] = {
            "Company": company,
            "Date": date,
            "IPO_Mcap": IPO_Mcap,
            "IPO_Price": IPO_Price,
            "Current_Price": Current_Price,
            "Change_in_price": Change_in_price,
            "Link": link
        }

    return jsonify(result)







@app.route("/current",methods=["POST"])
def current_price():
    input_data = request.json
    charts_input = input_data.get("symbols")
    res = {}

    for t in charts_input:
        try:
            ticker = yf.Ticker(t)
            last_price = ticker.fast_info["last_price"]
            res[t] = {"price": last_price}
        except Exception as e:
            res[t] = {"error": str(e)}

    return jsonify(res)
@app.route("/history", methods=["GET"])
def history():
    symbol = request.args.get("symbol")
    period = request.args.get("period", "1y")   # default 5 years

    if not symbol:
        return jsonify({"error": "symbol is required"}), 400

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        df = df[["Close"]].reset_index()

        history_list = [
            {
                "date": row["Date"].strftime("%Y-%m-%d"),
                "close": float(row["Close"])
            }
            for _, row in df.iterrows()
        ]

        return jsonify({
            "symbol": symbol,
            "period": period,
            "data": history_list
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API_KEY = "ZZDN7JPqai1OdM4Ixh3Pla3zquqBpTch5H5SF16W"
# API_KEY = "5TbuCu0JHb2QfoTywCXES8rGaE0R85bm8KlLtd7U"
API_KEY = "W2isNTOku79Okd1HAn96z53rPOQleB0eaGSvYui8"
@app.route("/chart", methods=["GET"])
def chart_url():
    # Get symbols from query parameter ?q=NASDAQ:CMCSA,NASDAQ:PFE
    q = request.args.get("q", "")
    if not q:
        return jsonify({"error": "No symbols provided in query parameter 'q'"}), 400

    symbols = [s.strip() for s in q.split(",") if s.strip()]
    if not symbols:
        return jsonify({"error": "No valid symbols found"}), 400

    result = []

    for symbol in symbols:
        payload = {
            "symbol": symbol,
            "theme": "dark",
            "interval": "1D",
            "studies": [
                {"name": "Volume"},
                {"name": "Relative Strength Index"},
                {"name": "MACD"}
            ]
        }

        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}

        chart_link = None
        error_msg = None

        try:
            resp = requests.post(
                "https://api.chart-img.com/v2/tradingview/advanced-chart/storage",
                headers=headers,
                json=payload,
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                chart_link = data.get("url")
            else:
                error_msg = f"Storage failed {resp.status_code}"
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
        except ValueError:
            error_msg = "Empty or invalid JSON returned"

        result.append({"symbol": symbol, "chart_url": chart_link, "error": error_msg})
        time.sleep(0.5)  # avoid 429 errors

    return jsonify({"charts": result})






if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500)




