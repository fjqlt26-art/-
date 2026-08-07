# 주식 알림봇 (Telegram)

미국 증시 관련 지표를 매일 아침 9시(KST)에 브리핑하고, 특정 조건 도달 시 실시간으로
텔레그램 알림을 보내주는 봇입니다. 여러분의 컴퓨터를 켜둘 필요 없이 **GitHub Actions**
(무료 클라우드 스케줄러)에서 자동으로 돌아갑니다.

## 기능

### 1. 아침 브리핑 (매일 09:00 KST, 미국 증시 휴장일엔 발송 안 함)
- CNN 탐욕지수 (극단적공포/공포/중립/탐욕/극단적탐욕)
- SPY, QQQ, SOXQ, SMH, GOOGL 전일 종가 기준
  - RSI(14)
  - 20/60/120/200일 이평선 위/아래 + 이격도(%)

### 2. 실시간 알림 (정규장 시간 중 15분 간격 체크)
아래 4가지 중 하나라도 "새로" 발생하면 즉시 알림:
1. CNN 탐욕지수 극단적 공포 진입
2. 관심종목 RSI 30 이하 진입
3. 관심종목 120일선 터치(종가가 이평선 이하로 진입)
4. 관심종목 200일선 터치(종가가 이평선 이하로 진입)

**쿨다운 규칙**: 한 번 알림이 온 조건은 계속 유지되는 동안 다시 알림이 오지 않습니다.
조건에서 벗어났다가(예: RSI가 30 위로 회복) 다시 조건에 진입하면(다시 30 이하로 하락)
그때 다시 알림이 옵니다. 별도의 "다음날 9시까지 무조건 쿨다운" 타이머가 아니라,
조건 자체가 유지되는 동안만 억제되는 방식이라 말씀하신 예시(저녁에 RSI 29 알림 →
다음날 9시 브리핑에도 29로 유지 → 30 회복 전까지 계속 알림 없음)와 정확히 일치합니다.

## 사전 준비: 텔레그램 봇 만들기

1. 텔레그램에서 **@BotFather** 검색 후 대화 시작
2. `/newbot` 입력 → 봇 이름/아이디 설정 → **Bot Token** 발급 (예: `123456:ABC-DEF...`)
3. 만든 봇과 대화창을 열고 아무 메시지나 전송 (예: "hi")
4. 브라우저에서 아래 주소 접속 (TOKEN을 방금 발급받은 값으로 교체)
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. 응답 JSON에서 `"chat":{"id": 123456789, ...}` 의 숫자가 **Chat ID** 입니다.

## 설치 방법

1. 이 폴더 전체를 **새 GitHub 저장소**에 업로드합니다. (Public 저장소 권장 — Actions
   실행 시간이 무제한이라 비용 걱정이 없습니다. 코드에 개인정보는 없고, 토큰은
   아래처럼 Secrets로 별도 관리하니 Public이어도 안전합니다.)

2. 저장소 **Settings > Secrets and variables > Actions > New repository secret**
   에서 다음 2개를 등록합니다.
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

3. 저장소 **Settings > Actions > General > Workflow permissions** 에서
   **"Read and write permissions"** 로 변경 후 저장합니다.
   (실시간 체크 워크플로우가 `state.json`을 커밋하기 위해 필요합니다.)

4. 저장소 **Actions** 탭에서 `Morning Briefing`, `Realtime Alert Check` 워크플로우를
   각각 열고 **Run workflow** 버튼으로 수동 실행해 정상 동작하는지 확인합니다.

5. 이후에는 별도 조작 없이 자동으로:
   - 매일 09:00 KST에 브리핑
   - 미국 정규장 시간 중 15분마다 실시간 조건 체크

## 종목/임계값 변경

`src/config.py` 파일에서 수정합니다.
```python
TICKERS = ["SPY", "QQQ", "SOXQ", "SMH", "GOOGL"]  # 추적 종목
RSI_OVERSOLD = 30                                  # RSI 실시간 알림 기준
MA_TOUCH_PERIODS = [120, 200]                      # 실시간 터치 알림 대상 이평선
MA_PERIODS = [20, 60, 120, 200]                     # 브리핑에 표시할 이평선
```

## 로컬에서 테스트하기 (선택)

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
python -m src.briefing        # 브리핑 테스트
python -m src.realtime_check  # 실시간 체크 테스트
```

## 알아두면 좋은 점 (한계 및 설계 결정)

- **CNN 탐욕지수**는 공식 API가 없어 CNN 웹페이지가 내부적으로 사용하는 비공식
  엔드포인트를 사용합니다. CNN이 구조를 바꾸면 동작하지 않을 수 있습니다 —
  이 경우 `src/fear_greed.py` 수정이 필요할 수 있어요.
- **"실시간"은 완전 실시간이 아니라 15분 간격 폴링**입니다. 무료 시세 API 특성상
  완전한 실시간 체결가 스트리밍은 지원하지 않습니다.
- **이평선 "터치"는 "종가가 이평선 이하로 내려온 상태"로 정의**했습니다.
  (장중 저가가 이평선에 살짝 닿았다가 종가는 위로 마감한 경우는 감지하지 않음.
  더 민감하게 하시려면 `src/realtime_check.py`의 `touched_now` 조건을 조정하면 됩니다.)
- GitHub Actions의 스케줄 실행은 시스템 부하에 따라 몇 분 정도 지연될 수 있습니다
  (정시 실행을 100% 보장하지 않음 — GitHub 공식 정책).
