"""매일 오전 9시(KST) 브리핑. 미국 증시 휴장일에는 발송하지 않음."""
from src.config import MA_PERIODS, TICKERS
from src.data_fetch import get_ticker_snapshot
from src.fear_greed import get_fear_greed
from src.market_calendar import is_us_trading_day
from src.telegram_notify import send_telegram_message


def _format_ma_line(ma_info: dict) -> str:
    parts = []
    for period in MA_PERIODS:
        info = ma_info[period]
        if info["position"] == "데이터부족":
            parts.append(f"{period}일선 데이터부족")
        else:
            sign = "+" if info["gap_pct"] >= 0 else ""
            parts.append(f"{period}일선 {info['position']} ({sign}{info['gap_pct']:.1f}%)")
    return " / ".join(parts)


def build_briefing_text() -> str:
    fg = get_fear_greed()
    lines = [
        "📊 <b>오늘의 아침 브리핑</b>",
        "",
        f"😨 CNN 탐욕지수: <b>{fg['score']}점 ({fg['rating_kr']})</b>",
        "",
    ]

    for ticker in TICKERS:
        snap = get_ticker_snapshot(ticker)
        lines.append(f"<b>[{ticker}]</b> 전일 종가 ${snap['close']:.2f} ({snap['date']} 기준)")
        lines.append(f"  RSI: {snap['rsi']:.1f}")
        lines.append(f"  이평선: {_format_ma_line(snap['ma_info'])}")
        lines.append("")

    return "\n".join(lines).strip()


def run_briefing():
    if not is_us_trading_day():
        print("오늘은 미국 증시 휴장일입니다. 브리핑을 건너뜁니다.")
        return
    text = build_briefing_text()
    send_telegram_message(text)
    print("브리핑 발송 완료")


if __name__ == "__main__":
    run_briefing()
