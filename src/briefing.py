"""매일 오전 9시(KST) 브리핑. 주말(KST 기준)에는 발송하지 않음."""
from datetime import datetime
from zoneinfo import ZoneInfo

from src.chart import generate_ma_chart
from src.config import MA_PERIODS, TICKERS
from src.data_fetch import get_ticker_snapshot
from src.fear_greed import get_fear_greed
from src.market_calendar import is_kst_weekday
from src.telegram_notify import send_telegram_message, send_telegram_photo_group

KST = ZoneInfo("Asia/Seoul")


def _format_ma_lines(ma_info: dict) -> list:
    lines = []
    for period in MA_PERIODS:
        info = ma_info[period]
        if info["position"] == "데이터부족":
            lines.append(f"    {period}일선 데이터부족")
            continue
        sign = "+" if info["gap_pct"] >= 0 else ""
        gap_str = f"{sign}{info['gap_pct']:.1f}%"
        if info["position"] == "아래":
            lines.append(f"    🟢 <b>{period}일선 아래</b> ({gap_str})")
        else:
            lines.append(f"    {period}일선 위 ({gap_str})")
    return lines


WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def build_briefing_text() -> str:
    fg = get_fear_greed()

    snaps = [get_ticker_snapshot(ticker) for ticker in TICKERS]

    now_kst = datetime.now(KST)
    title_date = now_kst.strftime("%y.%m.%d.")
    weekday_kr = WEEKDAY_KR[now_kst.weekday()]
    lines = [
        f"📊 <b>{title_date}({weekday_kr}) 아침 브리핑</b>",
        "",
        f"😨 CNN 탐욕지수: <b>{fg['score']}점 ({fg['rating_kr']})</b>",
        "",
    ]

    for snap in snaps:
        lines.append(f"<b>[{snap['ticker']}]</b> 종가 ${snap['close']:.2f}")
        lines.append(f"  RSI: {snap['rsi']:.1f}")
        lines.append("  이평선:")
        lines.extend(_format_ma_lines(snap["ma_info"]))
        lines.append("")

    return "\n".join(lines).strip()


def run_briefing():
    if not is_kst_weekday():
        print("주말입니다. 브리핑을 건너뜁니다.")
        return

    text = build_briefing_text()
    send_telegram_message(text)
    print("브리핑 텍스트 발송 완료")

    photos = []
    for ticker in TICKERS:
        try:
            img_bytes = generate_ma_chart(ticker)
            photos.append({"filename": f"{ticker}.png", "caption": ticker, "data": img_bytes})
        except Exception as e:
            print(f"{ticker} 차트 생성 실패: {e}")

    for i in range(0, len(photos), 10):
        send_telegram_photo_group(photos[i : i + 10])

    if photos:
        print(f"차트 {len(photos)}장 발송 완료")


if __name__ == "__main__":
    run_briefing()
