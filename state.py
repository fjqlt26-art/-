import json
import os

from src.config import STATE_FILE

DEFAULT_STATE = {
    "fear_greed_extreme_fear_active": False,
    "tickers": {},
    # tickers[ticker] = {
    #   "rsi_oversold_active": bool,
    #   "ma120_touch_active": bool,
    #   "ma200_touch_active": bool,
    # }
}


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return json.loads(json.dumps(DEFAULT_STATE))
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    for key, val in DEFAULT_STATE.items():
        state.setdefault(key, val)
    return state


def save_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_ticker_state(state: dict, ticker: str) -> dict:
    return state["tickers"].setdefault(
        ticker,
        {
            "rsi_oversold_active": False,
            "ma120_touch_active": False,
            "ma200_touch_active": False,
        },
    )
