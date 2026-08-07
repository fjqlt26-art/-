import os

# ---- Telegram ----
# GitHub Actions Secrets 에서 주입됩니다. (Settings > Secrets and variables > Actions)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ---- 추적 종목 ----
TICKERS = ["SPY", "QQQ", "SOXQ", "SMH", "GOOGL"]

# ---- 지표 설정 ----
RSI_PERIOD = 14
MA_PERIODS = [20, 60, 120, 200]

# ---- 실시간 알림 임계값 ----
RSI_OVERSOLD = 30
MA_TOUCH_PERIODS = [120, 200]  # 실시간 터치 알림 대상 이평선

# ---- 상태 파일 (GitHub Actions가 매 실행 후 커밋해서 유지) ----
STATE_FILE = "state.json"
