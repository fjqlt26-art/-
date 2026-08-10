from datetime import datetime
from zoneinfo import ZoneInfo

import pandas_market_calendars as mcal

NYSE = mcal.get_calendar("NYSE")
ET = ZoneInfo("America/New_York")
KST = ZoneInfo("Asia/Seoul")


def is_kst_weekday(date=None) -> bool:
    """오늘(한국시간 기준)이 평일(월~금)인지 확인.

    브리핑은 한국시간 09:00에 발송되는데, 이 시각은 미국 동부시간으로는
    '전날 저녁'에 해당한다. 따라서 미국 동부시간 날짜로 개장일을 체크하면
    (예: 월요일 09:00 KST = 일요일 저녁 ET) 정상적인 평일 브리핑까지
    휴장일로 오판하는 문제가 생긴다. 브리핑은 최신 종가를 그대로 보여주면
    되므로(공휴일이면 yfinance가 자동으로 직전 거래일 데이터를 반환),
    한국시간 기준 평일 여부만 확인한다.
    """
    if date is None:
        date = datetime.now(KST).date()
    return date.weekday() < 5  # 0=월요일 ... 4=금요일, 5=토, 6=일


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
