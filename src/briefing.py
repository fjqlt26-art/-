"""매일 오전 9시(KST) 브리핑. 미국 증시 휴장일에는 발송하지 않음."""
from src.config import MA_PERIODS, TICKERS
from src.data_fetch import get_ticker_snapshot
from src.fear_greed import get_fear_greed
from src.market_calendar import is_us_trading_day
from src.telegram_notify import send_telegram_message


def _format_ma_lines(ma_info: dict) -> list:
    """이평선을 종목별로 줄바꿈해서 표시. 이평선 아래로 내려온 경우 강조."""
    lines = []
    for period in MA_PERIODS:
        info = ma_info[period]
        if info["position"] == "데이터부족":
            lines.append(f"    {period}일선 데이터부족")
            continue
        sign = "+" if info["gap_pct"] >= 0 else ""
        gap_str = f"{sign}{info['gap_pct']:.1f}%"
        if info["position"] == "아래":
            # 이평선 아래(눌림목/매수 관심 구간)일 때 강조 표시
            lines.append(f"    🟢 <b>{period}일선 아래</b> ({gap_str})")
        else:
            lines.append(f"    {period}일선 위 ({gap_str})")
    return lines


def build_briefing_text() -> str:
    fg = get_fear_greed()

    snaps = [get_ticker_snapshot(ticker) for ticker in TICKERS]
    date_str = snaps[0]["date"] if snaps else ""

    lines = [
        f"📊 <b>오늘의 아침 브리핑</b> ({date_str} 낮 기준)",
        "",
        f"😨 CNN 탐욕지수: <b>{fg['score']}점 ({fg['rating_kr']})</b>",
        "",
    ]

    for snap in snaps:
        lines.append(f"<b>[{snap['ticker']}]</b> 종가 ${snap['close']:.2f}")
        lines.append(f"  - RSI: {snap['rsi']:.1f}")
        lines.append("  - 이평선:")
        lines.extend(_format_ma_lines(snap["ma_info"]))
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
