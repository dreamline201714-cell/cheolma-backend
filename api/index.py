import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# CORS 완벽 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 한글 종목명 -> 티커 매핑 테이블 (필요시 추가 가능)
KOREAN_STOCK_MAP = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "삼성전기": "009150",
    "현대차": "005380",
    "NAVER": "035420",
    "카카오": "035720",
    "엔비디아": "NVDA",
    "애플": "AAPL",
    "마이크로소프트": "MSFT",
    "테슬라": "TSLA"
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

@app.get("/api/toss/stock/{symbol_or_name}")
def get_toss_stock_info(symbol_or_name: str):
    token = get_toss_token()
    if not token:
        return {"status": "error", "message": "API 인증 실패"}

    # 한글 검색어 입력 시 종목 코드로 변환
    target_symbol = KOREAN_STOCK_MAP.get(symbol_or_name.strip(), symbol_or_name.strip().upper())

    url = f"https://openapi.tossinvest.com/api/v1/stocks?symbols={target_symbol}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}
