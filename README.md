# Trade Backtesting System

**Trade Backtesting System**은 주식 트레이딩 전략을 시뮬레이션하고 분석하기 위한 견고한 Python 프레임워크입니다.
추세 추종(Trend Following) 전략을 중심으로 설계되었으며, 확장이 용이한 모듈식 구조를 갖추고 있습니다.

## ✨ 주요 기능

- **추세 추종 전략 특화**: 장기 이동평균선(SMA150, SMA200)과 모멘텀을 결합한 돌파 매매(Breakout) 전략을 기본 탑재했습니다.
- **리스크 관리**:
  - **Trailing Stop**: 진입 후 최고가 대비 **20%** 하락 시 자동 청산하여 수익을 보존하고 손실을 제한합니다.
- **모듈식 아키텍처**: 데이터(`data`), 전략(`strategies`), 실행(`backtest`) 계층이 명확히 분리되어 있어 유지보수와 확장이 용이합니다.
- **효율적인 데이터 관리**: `yfinance`를 기반으로 데이터를 수집하며, 로컬 캐싱을 지원하여 반복 테스트 시 효율성을 높였습니다.

## 📂 프로젝트 구조

```
.
├── pyproject.toml       # 프로젝트 의존성 및 설정 (Ruff 등)
├── README.md            # 프로젝트 문서
├── outputs/             # 백테스트 로그 및 결과 리포트 저장소
└── src/
    └── trade/           # 메인 패키지
        ├── core/        # 공용 데이터 모델 및 상수
        ├── data/        # 데이터 수집 및 로더
        ├── strategies/  # 매매 전략 로직 (Trend 등)
        ├── backtest/    # 백테스트 실행 엔진
        └── main.py      # CLI 진입점
```

## 🚀 설치 및 실행

### 필수 요건

- Python 3.8 이상
- `pip` 패키지 매니저

### 설치

```bash
# 프로젝트 루트에서 실행 (개발 모드 설치)
pip install -e .
```

### 실행 방법

설치가 완료되면 `trade` 명령어를 터미널에서 바로 사용할 수 있습니다.

#### 단일 종목 백테스트 (`single`)

특정 종목에 대해 전략 시뮬레이션을 수행합니다.

```bash
# 기본 실행 (기본값: QQQ)
trade single

# 특정 종목 지정 실행 (다중 지정 가능)
trade single --ticker AAPL TSLA NVDA
```

- **결과 확인**: `outputs/single/{TICKER}_backtest.log` 파일에 상세 거래 내역과 수익률 분석 결과가 저장됩니다.

## 📊 전략 알고리즘 (Trend Strategy)

기본 탑재된 `trade.strategies.trend` 모듈은 고전적인 추세 추종 원칙을 현대적으로 구현했습니다.

### 1. 진입 (Entry)

아래의 **모든 조건**이 만족될 때 매수합니다 (AND 조건).

- **장기 추세 필터**: 현재가가 **SMA150** 및 **SMA200** 위에 위치해야 합니다.
- **모멘텀 확인**: SMA150과 SMA200이 모두 **상승 기울기**여야 합니다.
- **돌파(Breakout)**: 종가가 최근 **20일간의 최고가**를 갱신(돌파)해야 합니다.

### 2. 청산 (Exit)

다음 중 **하나라도** 발생하면 즉시 전량 매도합니다 (OR 조건).

- **추세 이탈**: 종가가 SMA150 또는 SMA200 아래로 하락할 경우.
- **Trailing Stop**: 진입 이후 기록한 최고가(Highest High) 대비 **20%** 이상 하락할 경우.

## 🛠 개발 환경

코드 품질 유지를 위해 **Ruff**를 사용하고 있습니다.

```bash
# 린트 검사
ruff check .

# 코드 포맷팅
ruff format .
```

## 🤖 자동화 도구

프로젝트 유지보수 및 일일 트레이딩을 돕는 스크립트가 `scripts/` 디렉토리에 포함되어 있습니다.

### 1. 일일 신호 분석 (`daily_scan.py`)

주요 관심 종목(QQQ, SPY, TSLA 등)의 현재 추세와 매매 신호를 분석하여 출력합니다.

```bash
python scripts/daily_scan.py
```

**출력 예시:**

```text
Ticker   Price      Trend      Action (No Pos)    Action (Holding)
-----------------------------------------------------------------
QQQ      622.72     UP 🟢       WAIT               HOLD
MSFT     465.95     DOWN 🔴     WAIT               SELL ⚠️
```

### 2. 코드 품질 검사 (`verify_quality.sh`)

린트(`ruff check`)와 포맷팅(`ruff format`)을 한 번에 수행합니다.

```bash
./scripts/verify_quality.sh
```

---

_Created by Antigravity_
