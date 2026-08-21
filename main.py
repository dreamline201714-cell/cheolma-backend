from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# M7 + 쿠팡(CPNG), 마벨(MRVL), SK하이닉스 ADR(HXSCF) 및 나스닥 지수(^IXIC)
SYMBOLS = [
    {"symbol": "^IXIC", "name": "NASDAQ INDEX"},
    # M7 (Magnificent 7)
    {"symbol": "MSFT", "name": "Microsoft (MSFT)"},
    {"symbol": "AAPL", "name": "Apple (AAPL)"},
    {"symbol": "GOOGL", "name": "Alphabet/Google (GOOGL)"},
    {"symbol": "AMZN", "name": "Amazon (AMZN)"},
    {"symbol": "NVDA", "name": "NVIDIA (NVDA)"},
    {"symbol": "META", "name": "Meta (META)"},
    {"symbol": "TSLA", "name": "Tesla (TSLA)"},
    # 주요 개별주 & ADR
    {"symbol": "CPNG", "name": "Coupang (CPNG)"},
    {"symbol": "MRVL", "name": "Marvell Tech (MRVL)"},
    {"symbol": "HXSCF", "name": "SK Hynix ADR (HXSCF)"}
]

@app.get("/api/us-market")
def get_us_market():
    stock_list = []
    
    for item in SYMBOLS[1:]:
        sym = item["symbol"]
        disp_name = item["name"]
        
        try:
            ticker = yf.Ticker(sym)
            info = ticker.fast_info
            
            last_price = info.get("last_price", 0)
            prev_close = info.get("previous_close", 0)
            
            change_pct = ((last_price - prev_close) / prev_close * 100) if prev_close else 0
            change_str = f"▲ +{change_pct:.2f}%" if change_pct >= 0 else f"▼ {change_pct:.2f}%"
            
            stock_list.append({
                "name": disp_name,
                "price": f"{last_price:.2f} USD",
                "change": change_str
            })
        except Exception:
            stock_list.append({
                "name": disp_name,
                "price": "N/A",
                "change": "0.00%"
            })

    # 나스닥 지수 차트 수집
    chart_labels = []
    chart_data = []
    try:
        nasdaq = yf.Ticker("^IXIC")
        hist = nasdaq.history(period="1d", interval="15m")
        chart_labels = [index.strftime("%H:%M") for index in hist.index]
        chart_data = [round(price, 2) for price in hist['Close'].tolist()]
    except Exception:
        chart_labels = ['09:30', '11:00', '13:00', '15:00']
        chart_data = [17400, 17500, 17680, 17825]

    return {
        "stockList": stock_list,
        "chartLabels": chart_labels,
        "chartData": chart_data
    }