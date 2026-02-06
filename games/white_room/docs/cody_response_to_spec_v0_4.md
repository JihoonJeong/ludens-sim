# Cody 확인 사항 응답 — v0.4 Spec 기준

> 📨 To. Theo, Gem, Luca
> From. Cody (Mac Lab)
> 참조: `white_room_prompt_spec_v0_4.md` Section 8

---

## #1. Phase 1 시장 에너지 풀 — 돌리되 에이전트 에너지 고정

**결정: 시장 시스템을 정상 동작시키되, 에이전트 에너지에 반영하지 않음 (shadow mode)**

### 이유
- PCS (Phantom Cost Sensitivity) 측정에 **시장 시스템의 동작 로그가 필수**. 에이전트가 trade를 선택했는지, 몇 회 했는지, 시장 풀 분배가 어떻게 이루어졌는지 기록해야 Stage 1과 비교 가능.
- 풀 자체를 비활성화하면 trade 행동의 "실제 효과 없음"을 측정할 데이터가 사라짐.

### 구현 방식

```python
# config에 추가
game_mode:
  energy_frozen: true       # Phase 1: 에너지 고정
  energy_visible: true       # Phase 1: 프롬프트에 표시
  market_shadow: true        # 시장 시스템 동작하되 에너지 미반영

# simulation.py 변경 (현재 코드 기준)
# _action_trade() — L403~428
def _action_trade(self, agent, epoch):
    # 기존 로직 그대로 실행 (비용 차감, 보상 계산, 세금, 풀 기록)
    # 단, energy_frozen이면 마지막에 에너지를 원래 값으로 복원

    original_energy = agent.energy
    # ... 기존 trade 로직 실행 ...
    if self.energy_frozen:
        logged_change = agent.energy - original_energy  # 로그용 기록
        agent.energy = original_energy                  # 에너지 복원

    return True, {"gross_reward": reward, "tax": tax,
                  "net_reward": net_reward,
                  "shadow": self.energy_frozen,         # 새 필드
                  "would_have_changed": logged_change}   # 새 필드

# _apply_energy_decay() — L251~254
def _apply_energy_decay(self, amount):
    if self.energy_frozen:
        return  # 감소 스킵
    # 기존 로직

# _distribute_market_pool() — L281~292
def _distribute_market_pool(self, epoch):
    # 분배 계산은 정상 실행 (로그용)
    distribution = self.market_pool.distribute_pool(epoch, market_agents)
    if not self.energy_frozen:
        for agent_id, amount in distribution.items():
            agent.gain_energy(amount)
    # distribution은 항상 로그에 기록
```

**핵심**: 모든 시스템이 "계산은 하되 적용은 안 함". 로그에는 "만약 적용했다면" 데이터가 남음.

---

## #2. Phase 2 trade/support 중립적 피드백

**결정: 행동은 허용하되, 자원 변화 없이 중립 확인만 반환**

### 구현 방식

```python
# config에 추가
game_mode:
  neutral_actions: true      # Phase 2: 모든 행동 자원 효과 제거

# 새로운 action handler 또는 기존 handler에 분기
def _action_trade(self, agent, epoch):
    if agent.location != "market":
        return False, {"error": "not_in_market"}

    if self.neutral_actions:
        # 비용 차감 없음, 보상 없음
        self.market_pool.record_trade(epoch, agent.id, 0, 0)  # 로그 기록
        return True, {
            "resource_effect": 0,
            "null_effect": True,
            "feedback_ko": "거래가 이루어졌습니다.",
            "feedback_en": "A trade was made.",
        }
    # ... 기존 로직 ...

def _action_support(self, agent, target_id, epoch):
    # target 유효성 검사는 동일
    if self.neutral_actions:
        self.support_tracker.add(epoch, agent.id, target_id)  # 관계 기록
        return True, {
            "resource_effect": 0,
            "null_effect": True,
            "feedback_ko": "지지를 표했습니다.",
            "feedback_en": "Support was shown.",
        }
    # ... 기존 로직 ...
```

### Luca L20 반영
- "거래가 이루어졌습니다" / "A trade was made" — **에너지 변화 언급 없음**
- Ritual Index 측정의 핵심: 에이전트가 기능 없는 행동을 반복하는지 자동 판별

---

## #3. Phase 2 whisper 누출 제거

**결정: whisper 행동은 허용, 누출 시스템만 비활성화**

### 구현 방식

```python
# config에 추가
game_mode:
  whisper_leak: false        # Phase 2: 누출 비활성화

# _action_whisper() — L484~514
def _action_whisper(self, agent, target_id, content, epoch):
    # 위치 검증, 대상 검증은 동일

    if self.neutral_actions:
        # 비용 없음
        return True, {
            "leaked": False,
            "observers": [],
            "null_effect": True,
            "feedback_ko": "귓속말을 전했습니다.",
            "feedback_en": "A whisper was delivered.",
        }

    # Phase 1 또는 Stage 1: 기존 누출 로직
    if not self.whisper_leak_enabled:
        return True, {"leaked": False, "observers": []}
    # ... 기존 WhisperSystem 로직 ...
```

- Phase 2에서 Observer 특수능력이 무의미하므로 누출 확률 계산 자체를 생략
- whisper 메시지 전달은 동작 (에이전트 간 비밀 대화 자체는 Phase 2 행동 패턴 데이터)

---

## #4. `null_effect` 플래그 로깅

**결정: 기존 로거에 필드 추가, Phase 자동 판별**

### 구현 방식

```python
# logger.py — log_action()에 필드 추가
def log_action(self, ..., extra=None):
    entry = {
        # 기존 필드 ...
        "resource_effect": extra.get("resource_effect", None),
        "null_effect": extra.get("null_effect", False),
        "persona_condition": extra.get("persona_condition", None),
        "constraint_level": extra.get("constraint_level", None),
        "home_location": extra.get("home_location", None),
    }
```

### 자동 판별 로직

```python
# Phase 2에서 null_effect 판별 기준
null_effect_actions = {
    "trade":   True,    # 항상 null (자원 변화 0)
    "support": True,    # 항상 null (영향력 변화 0)
    "speak":   False,   # 의사소통 기능은 존재
    "whisper": False,   # 의사소통 기능은 존재
    "move":    False,   # 위치 변경은 실제 효과
    "idle":    False,   # 기본 행동
}
```

**Gem 참고**: RI 산출 시 `null_effect=True`인 행동만 필터 → `Ritual Actions / Total Type-A-classified Actions`

---

## #5. Latin Square 자동 생성

**결정: config YAML + 생성 스크립트**

### 구조

```yaml
# config/white_room_phase2_set_a.yaml (예시)
experiment:
  phase: 2
  set: A
  condition: persona_on
  language: ko
  total_turns: 100

latin_square:
  design: model_x_persona
  run: 1                    # 1, 2, 3

  models:
    - exaone
    - mistral
    - haiku

  # Run 1 배치 (자동 생성)
  assignments:
    - {id: archivist_01, persona: archivist, model: exaone, home: plaza, constraint: high}
    - {id: archivist_02, persona: archivist, model: mistral, home: plaza, constraint: high}
    - {id: merchant_01, persona: merchant, model: mistral, home: market, constraint: mid}
    - {id: merchant_02, persona: merchant, model: haiku, home: market, constraint: mid}
    - {id: jester_01, persona: jester, model: haiku, home: alley, constraint: low}
    - {id: jester_02, persona: jester, model: exaone, home: alley, constraint: low}
```

### 생성 스크립트

```python
# scripts/generate_latin_square.py
def generate_phase2_configs():
    models = ["exaone", "mistral", "haiku"]

    # Set A/B: Model × Persona Latin Square
    persona_square = [
        # Run 1: (Arch: EX,MI), (Merch: MI,HA), (Jest: HA,EX)
        {"archivist": [0,1], "merchant": [1,2], "jester": [2,0]},
        # Run 2: rotation
        {"archivist": [1,2], "merchant": [2,0], "jester": [0,1]},
        # Run 3: rotation
        {"archivist": [2,0], "merchant": [0,1], "jester": [1,2]},
    ]

    # Set C/D: Model × Location Latin Square
    location_square = [
        {"plaza": [0], "market": [1], "alley": [2]},
        {"plaza": [1], "market": [2], "alley": [0]},
        {"plaza": [2], "market": [0], "alley": [1]},
    ]

    # 4 Sets × 3 runs = 12 YAML 파일 자동 생성
    for set_name, lang, design in [("A","ko","persona"), ("B","en","persona"),
                                    ("C","ko","location"), ("D","en","location")]:
        for run in range(1, 4):
            generate_yaml(set_name, lang, design, run)
```

**출력**: `config/` 아래 12개 YAML 파일 자동 생성
```
config/phase2_set_A_run1.yaml
config/phase2_set_A_run2.yaml
config/phase2_set_A_run3.yaml
...
config/phase2_set_D_run3.yaml
```

---

## #6. Agora-12 공통 엔진 추출

**결정: 가능하며, 추출 범위를 명확히 구분함**

### 엔진 (game-agnostic) — `engine/`으로 추출

| 현재 위치 | 추출 대상 | 변경 필요도 |
|-----------|-----------|------------|
| `adapters/*` | LLM 어댑터 전체 | **그대로** — 인터페이스 변경 없음 |
| `simulation.py` L26~110 | 초기화, 어댑터 관리, config 로딩 | **추상화** — `BaseSimulation` 클래스 |
| `simulation.py` L174~193 | 메인 루프 (에폭 반복) | **추상화** — `run_epoch()`를 훅 방식으로 |
| `simulation.py` L294~356 | 에이전트 턴 실행 + 로깅 | **추상화** — context builder를 주입식으로 |
| `agent.py` | Agent 기본 구조 | **추상화** — 에너지/영향력을 optional로 |
| `logger.py` | 로깅 시스템 | **그대로** — 필드 확장만 |
| `history.py` | 역사 엔진 | **그대로** |

### 게임별 (game-specific) — `games/white_room/`에 유지

| 현재 위치 | White Room 버전 | 변경 |
|-----------|----------------|------|
| `personas.py` | Phase별 Persona 프롬프트 | **새로 작성** |
| `context.py` | Phase별 Context 템플릿 | **새로 작성** |
| `actions.py` | Phase별 행동 규칙 | **새로 작성** (neutral_actions 지원) |
| `environment.py` | Space 구조 | 거의 동일, 간소화 |
| `crisis.py` | — | **미사용** |
| `whisper.py` | Phase 1만 사용, Phase 2 비활성 | **조건부** |
| `influence.py` | Phase 1만 사용, Phase 2 제거 | **조건부** |
| `market.py` | Phase 1 shadow mode | **조건부** |
| `architect.py` | Phase 1만 사용 | **조건부** |
| `support.py` | Phase 1 정상, Phase 2 neutral | **조건부** |

### 엔진 아키텍처 (제안)

```
engine/
├── core/
│   ├── base_simulation.py    # 추상 시뮬레이션 루프
│   ├── base_agent.py         # 추상 에이전트
│   ├── base_context.py       # 컨텍스트 빌더 인터페이스
│   ├── base_actions.py       # 행동 시스템 인터페이스
│   ├── logger.py             # 로깅 (그대로)
│   └── history.py            # 역사 엔진 (그대로)
├── adapters/                  # LLM 어댑터 (그대로)
│   ├── base.py
│   ├── anthropic.py
│   ├── google.py
│   ├── ollama.py
│   └── mock.py

games/white_room/
├── simulation.py              # WhiteRoomSimulation(BaseSimulation)
├── agents.py                  # WhiteRoomAgent(BaseAgent)
├── personas.py                # Phase 1/2 Persona
├── context.py                 # Phase 1/2 Context 템플릿
├── actions.py                 # Phase별 행동 규칙 + neutral mode
├── environment.py             # 공간 구조
├── systems/                   # Phase 1 전용 시스템 (옵션)
│   ├── market.py
│   ├── influence.py
│   ├── whisper.py
│   └── crisis.py              # (사용 안 함)
├── config/                    # 실험 설정 YAML
└── docs/                      # 기획 문서
```

### BaseSimulation 핵심 인터페이스

```python
class BaseSimulation(ABC):
    """게임 독립적 시뮬레이션 엔진"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.agents = self._create_agents()       # 게임별 오버라이드
        self.adapters = self._init_adapters()      # 공통
        self.logger = SimulationLogger(...)        # 공통

    def run(self):
        """메인 루프 — 공통"""
        for epoch in range(1, self.total_epochs + 1):
            self.run_epoch(epoch)

    def run_epoch(self, epoch: int):
        """에폭 루프 — 공통 골격, 훅으로 확장"""
        self.pre_epoch_hook(epoch)        # 게임별: crisis, decay 등
        for agent in self.get_active_agents():
            self._execute_agent_turn(agent, epoch)
        self.post_epoch_hook(epoch)       # 게임별: market pool, treasury 등

    @abstractmethod
    def build_context(self, agent, epoch) -> str:
        """게임별 프롬프트 생성"""

    @abstractmethod
    def execute_action(self, agent, action, epoch) -> tuple[bool, dict]:
        """게임별 행동 실행"""

    def pre_epoch_hook(self, epoch): pass   # 오버라이드 가능
    def post_epoch_hook(self, epoch): pass  # 오버라이드 가능
```

### 작업량 추정

| 작업 | 설명 |
|------|------|
| **엔진 추출** | Agora-12 simulation.py를 BaseSimulation + Agora12Simulation으로 분리 |
| **어댑터 이전** | 거의 복사 수준 (인터페이스 변경 없음) |
| **White Room Phase 1** | Agora12Simulation을 상속하고 energy_frozen/market_shadow 플래그 추가 |
| **White Room Phase 2** | BaseSimulation에서 직접 상속, 최소 행동 시스템만 구현 |
| **Latin Square 스크립트** | 별도 유틸리티 |

---

## 요약 — Theo 확인 요청

| # | 항목 | Cody 결정 | Theo 확인 필요 |
|---|------|-----------|---------------|
| 1 | Phase 1 시장 풀 | **Shadow mode** (동작하되 에너지 미반영, 로그 기록) | 이 방식으로 PCS 데이터 충분한지 Gem 확인 |
| 2 | Phase 2 중립 피드백 | "거래가 이루어졌습니다" / "A trade was made" | Luca L20 그대로. OK? |
| 3 | Phase 2 whisper 누출 | 비활성화 (leak_prob=0, suspicion 없음) | OK |
| 4 | null_effect 로깅 | trade/support에 `null_effect: true` 자동 태깅 | Gem: RI 산출 자동화 가능 |
| 5 | Latin Square 자동 생성 | 스크립트로 12개 YAML 자동 생성 | Gem: 배치표 검증 필요 |
| 6 | 공통 엔진 | BaseSimulation 추상 클래스 + 게임별 상속 | 전체 팀 합의 필요 |

---

*Cody (Mac Lab) — 2026-02-06*
