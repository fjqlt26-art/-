"""15분 간격으로 실행되는 실시간 알림 체크
1) CNN 탐욕지수 극단적 공포 진입
2) 관심종목 RSI 30 이하 진입
3) 관심종목 120일선 터치(종가가 이평선 이하로 진입)
4) 관심종목 200일선 터치(종가가 이평선 이하로 진입)

쿨다운 로직:
- 조건이 처음 발생(active: False -> True)했을 때만 알림을 보낸다.
- 조건이 유지되는 동안(active=True)은 알림을 재전송하지 않는다.
  (예: 저녁에 RSI 29로 알림이 간 뒤, 다음날 9시 브리핑에도 RSI가 30 이하로 유지되고 있다면
   조건이 계속 active 상태이므로 그 사이에는 실시간 알림이 다시 오지 않는다.)
- 조건에서 벗어나면(active: True -> False) 다음에 다시 조건에 진입할 때 알림이 재전송된다.
"""
from src.config import MA_TOUCH_PERIODS, RSI_OVERSOLD, TICKERS
from src.data_fetch import get_ticker_snapshot
from src.fear_greed import get_fear_greed
from src.market_calendar import is_market_open_now, is_us_trading_day
from src.state import get_ticker_state, load_state, save_state
from src.telegram_notify import send_telegram_message


def check_fear_greed(state: dict, messages: list):
    fg = get_fear_greed()
    is_extreme_fear = fg["rating_en"] == "extreme fear"
    was_active = state["fear_greed_extreme_fear_active"]

    if is_extreme_fear and not was_active:
        messages.append(
            f"🚨 CNN 탐욕지수 극단적 공포 진입! ({fg['score']}점, {fg['rating_kr']})"
        )
    state["fear_greed_extreme_fear_active"] = is_extreme_fear


def check_ticker(ticker: str, state: dict, messages: list):
    snap = get_ticker_snapshot(ticker)
    t_state = get_ticker_state(state, ticker)

    # 1) RSI 30 이하
    rsi_oversold_now = snap["rsi"] <= RSI_OVERSOLD
    if rsi_oversold_now and not t_state["rsi_oversold_active"]:
        messages.append(f"🚨 [{ticker}] RSI {snap['rsi']:.1f} - 과매도 구간({RSI_OVERSOLD} 이하) 진입")
    t_state["rsi_oversold_active"] = rsi_oversold_now

    # 2) 120일선 / 200일선 터치
    for period in MA_TOUCH_PERIODS:
        info = snap["ma_info"].get(period)
        key = f"ma{period}_touch_active"
        if not info or info["value"] is None:
            continue
        touched_now = snap["close"] <= info["value"]
        if touched_now and not t_state[key]:
            messages.append(
                f"🚨 [{ticker}] {period}일 이동평균선 터치 "
                f"(현재가 ${snap['close']:.2f} / {period}일선 ${info['value']:.2f})"
            )
        t_state[key] = touched_now


def run_realtime_check():
    if not is_us_trading_day():
        print("휴장일 - 실시간 체크 건너뜀")
        return
    if not is_market_open_now():
        print("정규장 시간 외 - 실시간 체크 건너뜀")
        return

    state = load_state()
    messages = []

    check_fear_greed(state, messages)
    for ticker in TICKERS:
        check_ticker(ticker, state, messages)

    if messages:
        send_telegram_message("\n".join(messages))
        print(f"{len(messages)}건 알림 발송")
    else:
        print("발송할 알림 없음")

    save_state(state)


if __name__ == "__main__":
    run_realtime_check()
