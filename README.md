# Trade Backtesting System

**Trade Backtesting System**은 주식 트레이딩 전략을 시뮬레이션하고 분석하기 위한 모듈식 Python 프레임워크입니다.

## ✨ 주요 기능

- **강력한 추세 추종 전략**: 이중 이동평균선(SMA150, SMA200) 필터와 20일 고가 돌파(Breakout)를 결합한 전략을 기본 탑재했습니다.
- **리스크 관리**:
  - **Trailing Stop**: 최고가 대비 20% 하락 시 이익 실현 및 손실 제한.
- **모듈식 아키텍처**: 데이터(`data`), 전략(`strategies`), 실행(`backtest`)이 명확히 분리되어 있어 확장성이 뛰어납니다.
- **자동 데이터 관리**: `yfinance`를 통해 데이터를 자동으로 다운로드하고 캐싱하여 반복 실행 속도를 높입니다.

## 📂 프로젝트 구조

업계 표준(Canonical) Python 프로젝트 구조를 따릅니다.

```
src/trade/           # 핵심 패키지
├── core/            # 공용 모델 (Position, 상수 등)
├── data/            # 데이터 로딩 및 캐싱 서비스
├── strategies/      # 트레이딩 전략 로직 (매수/매도 시그널 산출)
├── backtest/        # 백테스트 실행 엔진 (시뮬레이션 담당)
│   ├── single.py    # 단일 종목 엔진
└── main.py          # 통합 CLI 진입점 (Entry Point)

outputs/             # 백테스트 결과물 (로그, 리포트)
```

## 🚀 설치 및 실행

### 필수 요건

- Python 3.8 이상
- 패키지 설치:

```bash
pip install -e .
```

### 실행 방법

소스 코드가 `src` 디렉토리에 위치합니다. 패키지를 설치하면 `trade` 명령어를 어디서든 사용할 수 있습니다.

#### 1. 단일 종목 백테스트

특정 종목의 매매 타점과 수익률을 상세히 분석합니다.

```bash
# 기본 실행 (QQQ)
trade single

# 특정 종목 지정 (여러 개 가능)
trade single --ticker AAPL TSLA
```

- **결과 확인**: `outputs/single/{TICKER}_backtest.log`

## 📊 전략 상세 (Trend Strategy)

기본 탑재된 `trade.strategies.trend` 모듈은 다음 로직을 따릅니다.

- **진입 조건 (Entry)**:
  - **추세 필터**: SMA150 < 현재가, SMA200 < 현재가
  - **모멘텀**: SMA150과 SMA200이 모두 상승 기울기일 것
  - **트리거**: 최근 20일 종가(Close) 기준 고가 돌파
- **청산 조건 (Exit)**:
  - **추세 이탈**: 가격이 SMA150 또는 SMA200 아래로 하락
  - **Trailing Stop**: 진입 후 기록한 최고가 대비 **20%** 이상 하락 시 전량 매도

---

_Created by Antigravity_
