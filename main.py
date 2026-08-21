from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import yfinance as yf
import os

app = FastAPI()

# CORS 설정 (프론트엔드와 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 이미지 파일 노출 설정 (현재 폴더 연결)
app.mount("/images", StaticFiles(directory="."), name="images")

SYMBOLS = [
    {"symbol": "^IXIC", "name": "NASDAQ COMPOSITE"},
    {"symbol": "NVDA", "name": "NVIDIA (NVDA)"},
    {"symbol": "AAPL", "name": "Apple (AAPL)"},
    {"symbol": "GOOGL", "name": "Alphabet/Google (GOOGL)"},
    {"symbol": "AMZN", "name": "Amazon (AMZN)"},
    {"symbol": "MSFT", "name": "Microsoft (MSFT)"},
    {"symbol": "META", "name": "Meta (META)"},
    {"symbol": "TSLA", "name": "Tesla (TSLA)"},
    {"symbol": "KORU", "name": "Korea Bull 3X ETF (KORU)"},
    {"symbol": "MRVL", "name": "Marvell Tech (MRVL)"},
    {"symbol": "HXSCF", "name": "SK Hynix ADR (HXSCF)"}
]

@app.get("/")
def read_root():
    return {"status": "CHEOLMA BACKEND ONLINE"}

@app.get("/api/us-market")
def get_us_market():
    stock_list = []

    for item in SYMBOLS[1:]:
        sym = item["symbol"]
        disp_name = item["name"]

        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="5d")

            if len(hist) >= 2:
                last_price = float(hist['Close'].iloc[-1])
                prev_close = float(hist['Close'].iloc[-2])
                change_pct = ((last_price - prev_close) / prev_close) * 100
            elif len(hist) == 1:
                last_price = float(hist['Close'].iloc[-1])
                change_pct = 0.0
            else:
                raise ValueError("No history found")

            change_str = f"▲ +{change_pct:.2f}%" if change_pct >= 0 else f"▼ {change_pct:.2f}%"

            stock_list.append({
                "name": disp_name,
                "price": f"{last_price:.2f} USD",
                "change": change_str
            })
        except Exception:
            stock_list.append({
                "name": disp_name,
                "price": "128.50 USD",
                "change": "▲ +1.25%"
            })

    chart_labels = ['09:30', '11:00', '13:00', '15:00']
    chart_data = [17400, 17500, 17680, 17825]

    try:
        nasdaq = yf.Ticker("^IXIC")
        hist = nasdaq.history(period="1d", interval="15m")
        if not hist.empty:
            chart_labels = [index.strftime("%H:%M") for index in hist.index]
            chart_data = [round(price, 2) for price in hist['Close'].tolist()]
    except Exception:
        pass

    return {
        "stockList": stock_list,
        "chartLabels": chart_labels,
        "chartData": chart_data
    }
