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


# 디버깅용: 환경변수 로딩 여부 직접 확인
@app.get("/api/debug-env")
def debug_env():
  client_id = os.environ.get("TOSS_CLIENT_ID") or os.getenv("TOSS_CLIENT_ID")
  client_secret = os.environ.get("TOSS_CLIENT_SECRET") or os.getenv(
      "TOSS_CLIENT_SECRET"
  )

  return {
      "has_client_id": bool(client_id),
      "has_client_secret": bool(client_secret),
      "id_length": len(client_id) if client_id else 0,
  }


# 기존 토스 API 호출 로직
@app.get("/api/toss/stock/{symbol}")
def get_toss_stock_price(symbol: str):
  # os.environ으로 명시적 추출
  client_id = os.environ.get("TOSS_CLIENT_ID") or os.getenv("TOSS_CLIENT_ID")
  client_secret = os.environ.get("TOSS_CLIENT_SECRET") or os.getenv(
      "TOSS_CLIENT_SECRET"
  )

  if not client_id or not client_secret:
    return {
        "status": "error",
        "message": "Toss API Key 인증 실패 (환경변수 미인식)",
    }

  # 토큰 발급 요청
  url = "https://openapi.tossinvest.com/oauth2/token"
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  data = {
      "grant_type": "client_credentials",
      "client_id": client_id,
      "client_secret": client_secret,
  }

  try:
    token_res = requests.post(url, headers=headers, data=data, timeout=5)
    if token_res.status_code != 200:
      return {
          "status": "error",
          "message": f"토큰 발급 실패 (Toss 응답: {token_res.text})",
      }

    access_token = token_res.json().get("access_token")

    # 시세 조회 요청
    stock_url = f"https://openapi.tossinvest.com/api/v1/stocks?symbols={symbol}"
    stock_headers = {"Authorization": f"Bearer {access_token}"}
    stock_res = requests.get(stock_url, headers=stock_headers, timeout=5)

    return stock_res.json()
  except Exception as e:
    return {"status": "error", "message": str(e)}
