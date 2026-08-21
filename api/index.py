import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYMBOL_MAP = {
    "005930": "A005930", "삼성전자": "A005930",
    "000660": "A000660", "SK하이닉스": "A000660",
    "009150": "A009150", "삼성전기": "A009150",
    "NVDA": "NVDA", "AAPL": "AAPL", "MSFT": "MSFT", "TSLA": "TSLA"
}

# 1. IP 및 환경변수 상태 진단용 API
@app.get("/api/debug-env")
def debug_env():
    client_id = os.environ.get("TOSS_CLIENT_ID") or os.getenv("TOSS_CLIENT_ID")
    client_secret = os.environ.get("TOSS_CLIENT_SECRET") or os.getenv("TOSS_CLIENT_SECRET")
    
    outbound_ip = "확인 불가"
    try:
        outbound_ip = requests.get("https://api.ipify.org", timeout=5).text
    except Exception as e:
        outbound_ip = str(e)
        
    return {
        "has_client_id": bool(client_id),
        "has_client_secret": bool(client_secret),
        "vercel_outbound_ip": outbound_ip
    }

def get_toss_token():
    client_id = os.environ.get("TOSS_CLIENT_ID") or os.getenv("TOSS_CLIENT_ID")
    client_secret = os.environ.get("TOSS_CLIENT_SECRET") or os.getenv("TOSS_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        return None
        
    url = "https://openapi.tossinvest.com/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        res = requests.post(url, headers=headers, data=data, timeout=5)
        if res.status_code == 200:
            return res.json().get("access_token")
        else:
            print("Toss Token Res Error:", res.text)
    except Exception as e:
        print(f"Token Error: {e}")
    return None

def toss_get_request(path: str, params: str = ""):
    token = get_toss_token()
    if not token:
        return {"status": "error", "message": "API 인증 실패 (환경변수/IP 등록 상태 확인 필요)"}

    url = f"https://openapi.tossinvest.com{path}"
    if params:
        url += f"?{params}"
        
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/toss/prices/{query}")
def get_prices(query: str):
    symbol = SYMBOL_MAP.get(query.strip(), SYMBOL_MAP.get(query.strip().upper(), query.strip()))
    return toss_get_request("/api/v1/prices", f"symbols={symbol}")

@app.get("/api/toss/candles/{query}")
def get_candles(query: str):
    symbol = SYMBOL_MAP.get(query.strip(), SYMBOL_MAP.get(query.strip().upper(), query.strip()))
    return toss_get_request("/api/v1/candles", f"symbol={symbol}&interval=1m")

@app.get("/api/toss/orderbook/{query}")
def get_orderbook(query: str):
    symbol = SYMBOL_MAP.get(query.strip(), SYMBOL_MAP.get(query.strip().upper(), query.strip()))
    return toss_get_request("/api/v1/orderbook", f"symbols={symbol}")

@app.get("/api/toss/stock/{query}")
def get_stock_info(query: str):
    symbol = SYMBOL_MAP.get(query.strip(), SYMBOL_MAP.get(query.strip().upper(), query.strip()))
    return toss_get_request("/api/v1/stocks", f"symbols={symbol}")

@app.get("/api/toss/investor-trading/{query}")
def get_investor_trading(query: str):
    symbol = SYMBOL_MAP.get(query.strip(), SYMBOL_MAP.get(query.strip().upper(), query.strip()))
    return toss_get_request(f"/api/v1/stocks/{symbol}/investor-trading")

@app.get("/api/toss/exchange-rate")
def get_exchange_rate():
    return toss_get_request("/api/v1/exchange-rate")

@app.get("/api/toss/rankings")
def get_rankings():
    return toss_get_request("/api/v1/rankings")
