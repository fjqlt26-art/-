from datetime import datetime
from zoneinfo import ZoneInfo

import pandas_market_calendars as mcal

NYSE = mcal.get_calendar("NYSE")
ET = ZoneInfo("America/New_York")


def is_us_trading_day(date=None) -> bool:
    """오늘(미국 동부시간 기준)이 미국 증시 개장일인지 확인 (휴장일/주말 포함 판별)"""
    if date is None:
        date = datetime.now(ET).date()
    schedule = NYSE.schedule(start_date=date, end_date=date)
    return not schedule.empty


def is_market_open_now() -> bool:
    """지금 이 순간이 미국 정규장 시간(보통 9:30-16:00 ET) 내인지 확인"""
    now_et = datetime.now(ET)
    schedule = NYSE.schedule(start_date=now_et.date(), end_date=now_et.date())
    if schedule.empty:
        return False
    open_time = schedule.iloc[0]["market_open"].tz_convert(ET)
    close_time = schedule.iloc[0]["market_close"].tz_convert(ET)
    return open_time <= now_et <= close_time
