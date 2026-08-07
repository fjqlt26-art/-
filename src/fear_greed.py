import requests

# CNN이 자사 웹페이지에서 사용하는 비공식 데이터 엔드포인트입니다.
# 공식 API가 아니므로 CNN 측 사정으로 URL/응답 형식이 바뀌면 동작하지 않을 수 있습니다.
CNN_FNG_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

RATING_KR = {
    "extreme fear": "극단적 공포",
    "fear": "공포",
    "neutral": "중립",
    "greed": "탐욕",
    "extreme greed": "극단적 탐욕",
}


def get_fear_greed() -> dict:
    resp = requests.get(CNN_FNG_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    current = data["fear_and_greed"]
    score = round(float(current["score"]))
    rating = str(current["rating"]).lower()
    return {
        "score": score,
        "rating_en": rating,
        "rating_kr": RATING_KR.get(rating, rating),
    }
