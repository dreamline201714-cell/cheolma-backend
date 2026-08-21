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

# 토스증권 API 종목 매핑 (티커/한글 -> 토스 규격 Symbol)
SYMBOL_MAP = {
    "005930": "A005930",
    "삼성전자": "A005930",
    "000660": "A000660",
    "SK하이닉스": "A000660",
    "009150": "A009150",
    "삼성전기": "A009150",
    "NVDA": "NVDA",
    "AAPL": "AAPL",
    "MSFT": "MSFT",
    "TSLA": "TSLA"
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
    except Exception as e:
        print(f"Token Error: {e}")
    return None

@app.get("/api/toss/stock/{query}")
def get_toss_stock_info(query: str):
    token = get_toss_token()
    if not token:
        return {"status": "error", "message": "API 인증 실패"}

    clean_query = query.strip()
    target_symbol = SYMBOL_MAP.get(clean_query, SYMBOL_MAP.get(clean_query.upper(), clean_query))

    url = f"https://openapi.tossinvest.com/api/v1/stocks?symbols={target_symbol}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        res_json = res.json()
        
        # 만약 매핑된 심볼로도 조회가 실패하면 원본 입력값으로 2차 시도
        if not res_json.get("result") and target_symbol != clean_query:
            fallback_url = f"https://openapi.tossinvest.com/api/v1/stocks?symbols={clean_query}"
            res = requests.get(fallback_url, headers=headers, timeout=5)
            res_json = res.json()
            
        return res_json
    except Exception as e:
        return {"status": "error", "message": str(e)}
