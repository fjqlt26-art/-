import json

import requests

from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID 환경변수가 설정되지 않았습니다."
        )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def send_telegram_photo_group(photos: list):
    """여러 장의 사진을 텔레그램 앨범(sendMediaGroup)으로 발송.

    photos: [{"filename": str, "data": bytes, "caption": str(optional)}, ...]
    한 번에 최대 10장까지 지원 (텔레그램 API 제한).
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID 환경변수가 설정되지 않았습니다."
        )
    if not photos:
        return None

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMediaGroup"

    media = []
    files = {}
    for photo in photos:
        media.append(
            {
                "type": "photo",
                "media": f"attach://{photo['filename']}",
                "caption": photo.get("caption", ""),
            }
        )
        files[photo["filename"]] = (photo["filename"], photo["data"], "image/png")

    payload = {"chat_id": TELEGRAM_CHAT_ID, "media": json.dumps(media)}
    resp = requests.post(url, data=payload, files=files, timeout=30)
    resp.raise_for_status()
    return resp.json()
