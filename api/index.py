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

TOSS_CLIENT_ID = os.getenv("TOSS_CLIENT_ID")
TOSS_CLIENT_SECRET = os.getenv("TOSS_CLIENT_SECRET")
TOSS_BASE_URL = "https://openapi.tossinvest.com"


def get_toss_access_token():
  if not TOSS_CLIENT_ID or not TOSS_CLIENT_SECRET:
    return None

  url = f"{TOSS_BASE_URL}/oauth2/token"
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  data = {
      "grant_type": "client_credentials",
      "client_id": TOSS_CLIENT_ID,
      "client_secret": TOSS_CLIENT_SECRET,
  }
  try:
    res = requests.post(url, headers=headers, data=data, timeout=5)
    if res.status_code == 200:
      return res.json().get("access_token")
  except Exception as e:
    print(f"Token Error: {e}")
  return None


@app.get("/api/toss/stock/{symbol}")
def get_toss_stock_price(symbol: str):
  token = get_toss_access_token()
  if not token:
    return {
        "status": "error",
        "message": "Toss API Key 인증 실패 (환경변수 확인 필요)",
    }

  url = f"{TOSS_BASE_URL}/api/v1/stocks?symbols={symbol}"
  headers = {"Authorization": f"Bearer {token}"}

  try:
    res = requests.get(url, headers=headers, timeout=5)
    if res.status_code == 200:
      return res.json()
  except Exception as e:
    return {"status": "error", "message": str(e)}

  return {"status": "error", "message": "데이터 조회 실패"}


@app.get("/api/health")
def health_check():
  return {"status": "VERCEL BACKEND ONLINE"}
