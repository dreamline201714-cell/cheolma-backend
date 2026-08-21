from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

# 프론트엔드 브라우저 접속 허용 (CORS 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 미국 주요 심볼 목록 (나스닥 지수, 엔비디아, 애플, 테슬라 등)
SYMBOLS = ["^IXIC", "NVDA", "AAPL", "TSLA", "MSFT"]

@app.get("/api/us-market")
def get_us_market():
    stock_list = []
    
    # 1. 미국 주식 실시간/최근 시세 수집
    for symbol in SYMBOLS[1:]:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        
        last_price = info.get("last_price", 0)
        prev_close = info.get("previous_close", 0)
        
        # 변동률 계산
        change_pct = ((last_price - prev_close) / prev_close * 100) if prev_close else 0
        change_str = f"▲ +{change_pct:.2f}%" if change_pct >= 0 else f"▼ {change_pct:.2f}%"
        
        stock_list.append({
            "name": f"{symbol}",
            "price": f"{last_price:.2f} USD",
            "change": change_str
        })

    # 2. 나스닥 지수(^IXIC) 1일 차트 데이터 수집
    nasdaq = yf.Ticker("^IXIC")
    hist = nasdaq.history(period="1d", interval="15m")
    
    chart_labels = [index.strftime("%H:%M") for index in hist.index]
    chart_data = [round(price, 2) for price in hist['Close'].tolist()]
    latest_nasdaq_price = chart_data[-1] if chart_data else 0

    return {
        "stockList": stock_list,
        "nasdaqPrice": f"{latest_nasdaq_price:,.2f} pt",
        "chartLabels": chart_labels,
        "chartData": chart_data
    }