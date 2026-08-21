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


def get_toss_token():
  client_id = os.environ.get("TOSS_CLIENT_ID") or os.getenv("TOSS_CLIENT_ID")
  client_secret = os.environ.get("TOSS_CLIENT_SECRET") or os.getenv(
      "TOSS_CLIENT_SECRET"
  )
  if not client_id or not client_secret:
    return None

  url = "https://openapi.tossinvest.com/oauth2/token"
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  data = {
      "grant_type": "client_credentials",
      "client_id": client_id,
      "client_secret": client_secret,
  }
  try:
    res = requests.post(url, headers=headers, data=data, timeout=5)
    if res.status_code == 200:
      return res.json().get("access_token")
  except Exception as e:
    print(f"Token Error: {e}")
  return None


# 1. 종목 검색 / 기본 정보 조회 API
@app.get("/api/toss/stock/{symbol}")
def get_toss_stock_info(symbol: str):
  token = get_toss_token()
  if not token:
    return {"status": "error", "message": "API 인증 실패"}

  url = f"https://openapi.tossinvest.com/api/v1/stocks?symbols={symbol}"
  headers = {"Authorization": f"Bearer {token}"}
  try:
    res = requests.get(url, headers=headers, timeout=5)
    return res.json()
  except Exception as e:
    return {"status": "error", "message": str(e)}


# 2. Vercel Outbound IP 확인용
@app.get("/api/debug-env")
def debug_env():
  client_id = os.environ.get("TOSS_CLIENT_ID") or os.getenv("TOSS_CLIENT_ID")
  return {
      "has_client_id": bool(client_id),
      "vercel_outbound_ip": requests.get("https://api.ipify.org").text,
  }
