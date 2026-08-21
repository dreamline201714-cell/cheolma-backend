from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory="."), name="images")

# 깃허브 코드에는 키를 적지 않고, 서버 환경 변수에서 가져옴
TOSS_CLIENT_ID = os.getenv("TOSS_CLIENT_ID")
TOSS_CLIENT_SECRET = os.getenv("TOSS_CLIENT_SECRET")
TOSS_BASE_URL = "https://openapi.tossinvest.com"

# 토스증권 OAuth2 액세스 토큰 발급 (시세 전용)
def get_toss_access_token():
    if not TOSS_CLIENT_ID or not TOSS_CLIENT_SECRET:
        print("Toss API Keys are missing in Environment Variables")
        return None

    url = f"{TOSS_BASE_URL}/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": TOSS_CLIENT_ID,
        "client_secret": TOSS_CLIENT_SECRET
    }
    try:
        res = requests.post(url, headers=headers, data=data, timeout=5)
        if res.status_code == 200:
            return res.json().get("access_token")
    except Exception as e:
        print(f"Toss Token Error: {e}")
    return None

@app.get("/api/toss/stock/{symbol}")
def get_toss_stock_price(symbol: str):
    token = get_toss_access_token()
    if not token:
        return {"status": "error", "message": "API Key 인증 실패"}

    url = f"{TOSS_BASE_URL}/api/v1/stocks?symbols={symbol}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {"status": "error", "message": "시세 데이터 요청 실패"}
