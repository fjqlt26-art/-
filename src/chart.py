import io

import matplotlib

matplotlib.use("Agg")  # GitHub Actions 등 화면 없는 환경에서 렌더링하기 위한 백엔드
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

from src.config import MA_PERIODS

# 이평선별 차트 색상
MA_COLORS = {20: "#4C9AFF", 60: "#36B37E", 120: "#FFAB00", 200: "#FF5630"}


def generate_ma_chart(ticker: str, display_days: int = 130) -> bytes:
    """종가 + 이평선(20/60/120/200) 차트를 PNG 바이트로 생성."""
    hist = yf.download(
        ticker, period="18mo", interval="1d", progress=False, auto_adjust=False
    )
    if hist.empty:
        raise ValueError(f"{ticker}: 차트용 데이터를 가져오지 못했습니다")

    close = hist["Close"].dropna()
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    ma_series = {period: close.rolling(period).mean() for period in MA_PERIODS}

    plot_close = close.iloc[-display_days:]
    plot_index = plot_close.index

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    ax.plot(plot_index, plot_close.values, label="Close", color="#222222", linewidth=1.6)

    for period in MA_PERIODS:
        ma_plot = ma_series[period].reindex(plot_index)
        ax.plot(
            plot_index,
            ma_plot.values,
            label=f"MA{period}",
            color=MA_COLORS.get(period, "#888888"),
            linewidth=1.2,
        )

    ax.set_title(ticker, fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, ncol=5, frameon=False)
    ax.grid(alpha=0.25)
    ax.tick_params(axis="x", rotation=30, labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
