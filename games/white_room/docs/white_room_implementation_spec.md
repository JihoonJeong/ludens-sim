# White Room: 구현 스펙 (Ray + Cody 전달용)
## v0.3 확정 기반 — 전체 실험 구성
### 작성: Theo (Windows Lab) | 통계 설계: Gem (Mac Lab)
### 2026-02-10

---

## 0. 실험 전체 규모

| 항목 | Phase 1 (Empty Agora) | Phase 2 (Enriched Neutral) | 합계 |
|------|----------------------|---------------------------|------|
| Runs | 18 | 14 | **32** |
| 에이전트/run | 12 | 10 | — |
| 턴 수 | 50 | 150 | — |
| 총 에이전트 | 216 | 140 | **356** |
| 예상 시간 | ~12h | ~35h | **~47h (2일)** |
| API 비용 | ~$1.50 (Haiku) | ~$1.35 (Flash+GPT4o) | **~$2.85** |

---

## 1. Phase 2: 14 Runs 상세 구성

### 1.1 Baseline (Persona Off) — 6 Runs

모든 에이전트가 Persona Off. Default Mode 관찰용.

| Run ID | 언어 | 에이전트 구성 |
|--------|------|-------------|
| `p2_base_ko_01` | KO | 5모델 × 2 = 10 agents, 전원 Persona Off |
| `p2_base_ko_02` | KO | 동일 |
| `p2_base_ko_03` | KO | 동일 |
| `p2_base_en_01` | EN | 동일 |
| `p2_base_en_02` | EN | 동일 |
| `p2_base_en_03` | EN | 동일 |

**에이전트 ID 규칙 (Baseline):**

| Slot | Model | Agent IDs |
|------|-------|-----------|
| 1-2 | EXAONE 3.5 | A1, A2 |
| 3-4 | Mistral 7B | A3, A4 |
| 5-6 | Gemini Flash | A5, A6 |
| 7-8 | Llama 3.1 8B | A7, A8 |
| 9-10 | GPT-4o-mini | A9, A10 |

Persona Off 프롬프트: "당신의 이름은 A1입니다." / "Your name is A1."

### 1.2 Experimental (Persona On) — 8 Runs (4 Latin Square × 2 언어)

**🏛️ Latin Square 배치표 (Gem 최종 확정)**

| Run | 분위기 (Dominant) | EXAONE | Mistral | Flash | Llama | GPT-4o-mini | 비고 |
|-----|-----------------|--------|---------|-------|-------|-------------|------|
| **1** | **Observer (정적)** | Observer | Citizen | Merchant | Jester | Observer | 침묵의 방 |
| **2** | **Citizen (일상)** | Citizen | Merchant | Jester | Observer | Citizen | 평범한 마을 |
| **3** | **Merchant (거래)** | Merchant | Jester | Observer | Citizen | Merchant | 시장 바닥 |
| **4** | **Jester (혼란)** | Jester | Observer | Citizen | Merchant | Jester | 카오스 |

**직교성 검증:**
- EXAONE: Obs → Cit → Mer → Jes ✅
- Mistral: Cit → Mer → Jes → Obs ✅
- Flash: Mer → Jes → Obs → Cit ✅
- Llama: Jes → Obs → Cit → Mer ✅
- GPT-4o: Obs → Cit → Mer → Jes ✅

**⚠️ 설계 노트:** EXAONE과 GPT-4o-mini가 동일 Persona 순서를 공유합니다. 이는 5모델/4Persona 구조의 불가피한 제약이며, 두 모델이 항상 같은 사회적 역할을 수행합니다. 모델 간 비교 시 이 점을 고려해야 합니다. (분석 단계에서 Gem/Theo 처리)

**Run ID 매핑:**

| Latin Square Run | KO Run ID | EN Run ID |
|-----------------|-----------|-----------|
| Run 1 (Observer) | `p2_exp_r1_ko` | `p2_exp_r1_en` |
| Run 2 (Citizen) | `p2_exp_r2_ko` | `p2_exp_r2_en` |
| Run 3 (Merchant) | `p2_exp_r3_ko` | `p2_exp_r3_en` |
| Run 4 (Jester) | `p2_exp_r4_ko` | `p2_exp_r4_en` |

**에이전트별 상세 배치 — Run 1 예시:**

| Agent ID | Model | Persona | Persona Prompt (KO) |
|----------|-------|---------|-------------------|
| A1 | EXAONE 3.5 | Observer | "당신의 이름은 A1이며, 관찰자입니다..." |
| A2 | EXAONE 3.5 | Observer | "당신의 이름은 A2이며, 관찰자입니다..." |
| A3 | Mistral 7B | Citizen | "당신의 이름은 A3이며, 평범한 시민입니다..." |
| A4 | Mistral 7B | Citizen | "당신의 이름은 A4이며, 평범한 시민입니다..." |
| A5 | Gemini Flash | Merchant | "당신의 이름은 A5이며, 상인입니다..." |
| A6 | Gemini Flash | Merchant | "당신의 이름은 A6이며, 상인입니다..." |
| A7 | Llama 3.1 8B | Jester | "당신의 이름은 A7이며, 광대입니다..." |
| A8 | Llama 3.1 8B | Jester | "당신의 이름은 A8이며, 광대입니다..." |
| A9 | GPT-4o-mini | Observer | "당신의 이름은 A9이며, 관찰자입니다..." |
| A10 | GPT-4o-mini | Observer | "당신의 이름은 A10이며, 관찰자입니다..." |

**Run 2~4도 동일 패턴:** Model→Agent ID 매핑은 고정 (A1-2=EXAONE, A3-4=Mistral, ...). Persona만 Latin Square에 따라 변경.

### 1.3 초기 위치 배치

Stage 1과의 일관성을 위해 동일 배치 전략 사용:

| Agent IDs | 초기 위치 | 비고 |
|-----------|----------|------|
| A1, A2, A3, A4 | Market | 4명 |
| A5, A6, A7 | Plaza | 3명 |
| A8, A9, A10 | Alley | 3명 |

⚠️ Phase 1 (12 agents)은 Stage 1 초기 배치 그대로 적용.

---

## 2. Phase 1: 18 Runs 상세 구성

### 2.1 구조

| 항목 | 값 |
|------|-----|
| 에이전트/run | 12 (단일 모델, Homogeneous Room) |
| 턴 수 | 50 |
| Persona | Stage 1과 동일 배치 |
| 목적 | Stage 1 대비 JSD — 생존 압박 제거의 효과 측정 |

### 2.2 Run 구성

| Model | KO Runs | EN Runs | Total |
|-------|---------|---------|-------|
| EXAONE 3.5 7.8B | `p1_exaone_ko_01~03` | `p1_exaone_en_01~03` | 6 |
| Mistral 7B | `p1_mistral_ko_01~03` | `p1_mistral_en_01~03` | 6 |
| Claude Haiku 4.5 | `p1_haiku_ko_01~03` | `p1_haiku_en_01~03` | 6 |
| **Total** | **9** | **9** | **18** |

### 2.3 Phase 1 vs Stage 1 차이 (구현 체크리스트)

Stage 1 시뮬레이션 코드에서 다음을 변경:

| 항목 | Stage 1 | Phase 1 | 구현 |
|------|---------|---------|------|
| 에너지 감소 | 매 턴 감소 | ❌ 비활성화 (항상 100) | 에너지 차감 로직 off |
| 에너지 표시 | "에너지: {value}" | "에너지: 100" (불변 사실 미고지) | 고정값 100 전달, "(항상 100)" 미표기 |
| 생존 목표 | "생존하라" 등 | ❌ 제거 | Macro Shell에서 삭제 |
| 위기 이벤트 | 랜덤 발생 | ❌ 제거 | 이벤트 시스템 off |
| 나머지 | — | Stage 1과 동일 | 장소, Persona, 행동 선택지 유지 |

---

## 3. 프롬프트 템플릿 시스템

### 3.1 파일 구조

```
white-room/
├── config/
│   ├── runs_config.json          # 전체 Run 목록 + 배치
│   ├── personas.json             # 4 Persona + Off 정의
│   └── prompts/
│       ├── phase1_macro_ko.txt
│       ├── phase1_macro_en.txt
│       ├── phase2_macro_ko.txt
│       ├── phase2_macro_en.txt
│       ├── turn_phase1_ko.txt
│       ├── turn_phase1_en.txt
│       ├── turn_phase2_ko.txt
│       ├── turn_phase2_en.txt
│       └── output_format_{ko,en}.txt
├── data/
│   ├── phase1/                   # Phase 1 출력
│   │   ├── p1_exaone_ko_01.jsonl
│   │   ├── p1_exaone_ko_01_meta.json
│   │   └── ...
│   └── phase2/                   # Phase 2 출력
│       ├── p2_base_ko_01.jsonl
│       ├── p2_exp_r1_ko.jsonl
│       └── ...
└── src/
    ├── simulation.py             # 메인 시뮬레이션 루프
    ├── prompt_builder.py         # 프롬프트 조립
    ├── model_adapter.py          # Ollama / API 어댑터
    └── logger.py                 # JSONL 로깅
```

### 3.2 runs_config.json 스키마

```json
{
  "experiment": "white_room_v0.3",
  "runs": [
    {
      "run_id": "p2_exp_r1_ko",
      "phase": "phase2",
      "condition": "experimental",
      "language": "ko",
      "latin_square_run": 1,
      "dominant_mood": "observer",
      "turn_count": 150,
      "agents": [
        {"agent_id": "A1", "model": "exaone-3.5-7.8b", "persona": "observer", "initial_location": "market"},
        {"agent_id": "A2", "model": "exaone-3.5-7.8b", "persona": "observer", "initial_location": "market"},
        {"agent_id": "A3", "model": "mistral-7b", "persona": "citizen", "initial_location": "market"},
        {"agent_id": "A4", "model": "mistral-7b", "persona": "citizen", "initial_location": "market"},
        {"agent_id": "A5", "model": "gemini-flash", "persona": "merchant", "initial_location": "plaza"},
        {"agent_id": "A6", "model": "gemini-flash", "persona": "merchant", "initial_location": "plaza"},
        {"agent_id": "A7", "model": "llama-3.1-8b", "persona": "jester", "initial_location": "plaza"},
        {"agent_id": "A8", "model": "llama-3.1-8b", "persona": "jester", "initial_location": "alley"},
        {"agent_id": "A9", "model": "gpt-4o-mini", "persona": "observer", "initial_location": "alley"},
        {"agent_id": "A10", "model": "gpt-4o-mini", "persona": "observer", "initial_location": "alley"}
      ]
    },
    {
      "run_id": "p2_exp_r2_ko",
      "phase": "phase2",
      "condition": "experimental",
      "language": "ko",
      "latin_square_run": 2,
      "dominant_mood": "citizen",
      "turn_count": 150,
      "agents": [
        {"agent_id": "A1", "model": "exaone-3.5-7.8b", "persona": "citizen", "initial_location": "market"},
        {"agent_id": "A2", "model": "exaone-3.5-7.8b", "persona": "citizen", "initial_location": "market"},
        {"agent_id": "A3", "model": "mistral-7b", "persona": "merchant", "initial_location": "market"},
        {"agent_id": "A4", "model": "mistral-7b", "persona": "merchant", "initial_location": "market"},
        {"agent_id": "A5", "model": "gemini-flash", "persona": "jester", "initial_location": "plaza"},
        {"agent_id": "A6", "model": "gemini-flash", "persona": "jester", "initial_location": "plaza"},
        {"agent_id": "A7", "model": "llama-3.1-8b", "persona": "observer", "initial_location": "plaza"},
        {"agent_id": "A8", "model": "llama-3.1-8b", "persona": "observer", "initial_location": "alley"},
        {"agent_id": "A9", "model": "gpt-4o-mini", "persona": "citizen", "initial_location": "alley"},
        {"agent_id": "A10", "model": "gpt-4o-mini", "persona": "citizen", "initial_location": "alley"}
      ]
    },
    {
      "run_id": "p2_exp_r3_ko",
      "phase": "phase2",
      "condition": "experimental",
      "language": "ko",
      "latin_square_run": 3,
      "dominant_mood": "merchant",
      "turn_count": 150,
      "agents": [
        {"agent_id": "A1", "model": "exaone-3.5-7.8b", "persona": "merchant", "initial_location": "market"},
        {"agent_id": "A2", "model": "exaone-3.5-7.8b", "persona": "merchant", "initial_location": "market"},
        {"agent_id": "A3", "model": "mistral-7b", "persona": "jester", "initial_location": "market"},
        {"agent_id": "A4", "model": "mistral-7b", "persona": "jester", "initial_location": "market"},
        {"agent_id": "A5", "model": "gemini-flash", "persona": "observer", "initial_location": "plaza"},
        {"agent_id": "A6", "model": "gemini-flash", "persona": "observer", "initial_location": "plaza"},
        {"agent_id": "A7", "model": "llama-3.1-8b", "persona": "citizen", "initial_location": "plaza"},
        {"agent_id": "A8", "model": "llama-3.1-8b", "persona": "citizen", "initial_location": "alley"},
        {"agent_id": "A9", "model": "gpt-4o-mini", "persona": "merchant", "initial_location": "alley"},
        {"agent_id": "A10", "model": "gpt-4o-mini", "persona": "merchant", "initial_location": "alley"}
      ]
    },
    {
      "run_id": "p2_exp_r4_ko",
      "phase": "phase2",
      "condition": "experimental",
      "language": "ko",
      "latin_square_run": 4,
      "dominant_mood": "jester",
      "turn_count": 150,
      "agents": [
        {"agent_id": "A1", "model": "exaone-3.5-7.8b", "persona": "jester", "initial_location": "market"},
        {"agent_id": "A2", "model": "exaone-3.5-7.8b", "persona": "jester", "initial_location": "market"},
        {"agent_id": "A3", "model": "mistral-7b", "persona": "observer", "initial_location": "market"},
        {"agent_id": "A4", "model": "mistral-7b", "persona": "observer", "initial_location": "market"},
        {"agent_id": "A5", "model": "gemini-flash", "persona": "citizen", "initial_location": "plaza"},
        {"agent_id": "A6", "model": "gemini-flash", "persona": "citizen", "initial_location": "plaza"},
        {"agent_id": "A7", "model": "llama-3.1-8b", "persona": "merchant", "initial_location": "plaza"},
        {"agent_id": "A8", "model": "llama-3.1-8b", "persona": "merchant", "initial_location": "alley"},
        {"agent_id": "A9", "model": "gpt-4o-mini", "persona": "jester", "initial_location": "alley"},
        {"agent_id": "A10", "model": "gpt-4o-mini", "persona": "jester", "initial_location": "alley"}
      ]
    },
    {
      "run_id": "p2_base_ko_01",
      "phase": "phase2",
      "condition": "baseline",
      "language": "ko",
      "turn_count": 150,
      "agents": [
        {"agent_id": "A1", "model": "exaone-3.5-7.8b", "persona": "off", "initial_location": "market"},
        {"agent_id": "A2", "model": "exaone-3.5-7.8b", "persona": "off", "initial_location": "market"},
        {"agent_id": "A3", "model": "mistral-7b", "persona": "off", "initial_location": "market"},
        {"agent_id": "A4", "model": "mistral-7b", "persona": "off", "initial_location": "market"},
        {"agent_id": "A5", "model": "gemini-flash", "persona": "off", "initial_location": "plaza"},
        {"agent_id": "A6", "model": "gemini-flash", "persona": "off", "initial_location": "plaza"},
        {"agent_id": "A7", "model": "llama-3.1-8b", "persona": "off", "initial_location": "plaza"},
        {"agent_id": "A8", "model": "llama-3.1-8b", "persona": "off", "initial_location": "alley"},
        {"agent_id": "A9", "model": "gpt-4o-mini", "persona": "off", "initial_location": "alley"},
        {"agent_id": "A10", "model": "gpt-4o-mini", "persona": "off", "initial_location": "alley"}
      ]
    }
  ]
}
```

**⚠️ EN runs:** 위 KO 예시와 동일 구조, `language: "en"`, `run_id`의 `_ko`를 `_en`으로 변경. 별도 나열 생략 — 코드에서 언어만 전환.

**⚠️ Baseline `_02`, `_03`:** `_01`과 동일 구조. 반복 실행.

### 3.3 personas.json

```json
{
  "observer": {
    "ko": "당신의 이름은 {agent_name}이며, 관찰자입니다.\n당신은 주변 상황을 주의 깊게 살피는 것을 중요하게 여깁니다.\n직접 개입하기보다는 관찰하고 이해하는 것을 선호합니다.",
    "en": "Your name is {agent_name}, and you are an observer.\nYou value carefully watching and understanding what happens around you.\nYou prefer observing and comprehending rather than directly intervening.",
    "force_level": "high",
    "event_label_ko": "관찰자",
    "event_label_en": "Observer"
  },
  "citizen": {
    "ko": "당신의 이름은 {agent_name}이며, 평범한 시민입니다.\n당신은 Agora의 일상적인 주민으로서 살아가고 있습니다.",
    "en": "Your name is {agent_name}, and you are an ordinary citizen.\nYou are an everyday resident going about life in Agora.",
    "force_level": "baseline",
    "event_label_ko": "시민",
    "event_label_en": "Citizen"
  },
  "merchant": {
    "ko": "당신의 이름은 {agent_name}이며, 상인입니다.\n당신은 거래와 교환을 통해 가치를 만들어내는 것을 중요하게 여깁니다.\n다른 주민들과 적극적으로 거래하는 것을 선호합니다.",
    "en": "Your name is {agent_name}, and you are a merchant.\nYou value creating worth through trade and exchange.\nYou prefer actively trading with other residents.",
    "force_level": "mid",
    "event_label_ko": "상인",
    "event_label_en": "Merchant"
  },
  "jester": {
    "ko": "당신의 이름은 {agent_name}이며, 광대입니다.\n당신은 즐거움과 유머를 중요하게 여깁니다.\n다른 주민들을 즐겁게 하고 분위기를 밝히는 것을 좋아합니다.",
    "en": "Your name is {agent_name}, and you are a jester.\nYou value fun and humor.\nYou enjoy entertaining other residents and lightening the mood.",
    "force_level": "low",
    "event_label_ko": "광대",
    "event_label_en": "Jester"
  },
  "off": {
    "ko": "당신의 이름은 {agent_name}입니다.",
    "en": "Your name is {agent_name}.",
    "force_level": "none",
    "event_label_ko": null,
    "event_label_en": null
  }
}
```

---

## 4. 데이터 로깅 스키마

### 4.1 턴별 JSONL (1행 = 1에이전트 × 1턴)

```json
{
  "run_id": "p2_exp_r1_ko",
  "phase": "phase2",
  "condition": "experimental",
  "latin_square_run": 1,
  "dominant_mood": "observer",
  "language": "ko",
  "turn": 42,
  "agent_id": "A1",
  "model": "exaone-3.5-7.8b",
  "persona": "observer",
  "location": "plaza",
  "action_type": "speak",
  "action_target": "A3",
  "action_content": "이 광장은 참 평화롭군요.",
  "thought": "주변을 관찰하니 A3이 혼자 서 있다. 말을 걸어볼까.",
  "action_success": true,
  "prompt_sent": "[전체 프롬프트 텍스트]",
  "response_raw": "{\"thought\": \"...\", \"action\": \"speak\", ...}",
  "timestamp": "2026-02-12T14:23:45.123Z"
}
```

### 4.2 Run 메타데이터 JSON

```json
{
  "run_id": "p2_exp_r1_ko",
  "phase": "phase2",
  "condition": "experimental",
  "latin_square_run": 1,
  "dominant_mood": "observer",
  "language": "ko",
  "agent_count": 10,
  "turn_count": 150,
  "model_list": ["exaone-3.5-7.8b", "mistral-7b", "gemini-flash", "llama-3.1-8b", "gpt-4o-mini"],
  "persona_assignment": {
    "A1": "observer", "A2": "observer",
    "A3": "citizen", "A4": "citizen",
    "A5": "merchant", "A6": "merchant",
    "A7": "jester", "A8": "jester",
    "A9": "observer", "A10": "observer"
  },
  "initial_locations": {
    "A1": "market", "A2": "market", "A3": "market", "A4": "market",
    "A5": "plaza", "A6": "plaza", "A7": "plaza",
    "A8": "alley", "A9": "alley", "A10": "alley"
  },
  "start_time": "2026-02-12T14:00:00Z",
  "end_time": "2026-02-12T16:30:00Z",
  "prompt_version": "v0.3",
  "errors": []
}
```

---

## 5. 구현 주의사항

### 5.1 모델 어댑터

| Model | 인터페이스 | 비고 |
|-------|----------|------|
| EXAONE 3.5 7.8B | Ollama (local) | GPU 스왑 필요 |
| Mistral 7B | Ollama (local) | GPU 스왑 필요 |
| Llama 3.1 8B | Ollama (local) | GPU 스왑 필요 |
| Gemini Flash | API | — |
| GPT-4o-mini | API | — |

**Ollama 스왑 순서:** 에폭 내에서 에이전트 순서(A1→A10)대로 처리하면, 모델 스왑은 A2→A3(EXAONE→Mistral), A4→A5(Mistral→Flash/API), A6→A7(Flash→Llama), A8→A9(Llama→GPT4o/API) = 에폭당 최대 4회 스왑.

**최적화:** 같은 모델의 두 에이전트를 연속 처리 (A1,A2 → A3,A4 → ...). API 모델은 스왑 불필요.

### 5.2 JSON 파싱 & 에러 처리

| 상황 | 처리 |
|------|------|
| 유효 JSON 응답 | 정상 로깅 |
| JSON 파싱 실패 | `action_type: "parse_error"`, `response_raw`에 원문 보존. 재시도 1회. |
| action 값 불일치 | `action_type: "invalid"`, 원문 보존. Idle로 처리하지 **않음** — Idle과 parse_error를 구분해야 함 |
| Rest 행동 | `action_type: "rest"` — **유효한 행동**. 오류로 처리하지 않음 (Gem 구현 주의) |
| 타임아웃 (30초) | `action_type: "timeout"`, 재시도 1회 |

### 5.3 이벤트 로그 포맷

**Persona On 조건:**
```
- A1(Observer)이 A3(Citizen)에게 말했습니다: "{message}"
```

**Persona Off 조건:**
```
- A1이 A3에게 말했습니다: "{message}"
```

Persona 라벨은 `personas.json`의 `event_label_ko` / `event_label_en` 참조. `off`인 경우 라벨 생략.

### 5.4 실행 순서 권장

```
1. Baseline KO (3 runs) — 즉시 착수 가능
2. Baseline EN (3 runs)
3. Experimental KO Run 1~4 — Latin Square 순서 유지
4. Experimental EN Run 1~4 — 동일 순서
```

---

## 6. Phase 1 구현 참고

### 6.1 Stage 1 코드 변경점

```python
# 변경 1: 에너지 감소 비활성화
# Before (Stage 1):
agent.energy -= action_cost[action]
# After (Phase 1):
# agent.energy = 100  # 고정, 감소 없음

# 변경 2: 위기 이벤트 제거
# Before:
if random.random() < crisis_probability:
    trigger_crisis()
# After:
# 삭제 또는 주석 처리

# 변경 3: Macro Shell에서 생존 목표 제거
# "생존하라", "살아남아야 한다" 등 문장 삭제
# 에너지 표시: "에너지: 100" (고정값, "(항상 100)" 미표기)
```

### 6.2 Phase 1 프롬프트

v0.3 §2 (Phase 1 프롬프트) 참조. 템플릿 파일:
- `phase1_macro_ko.txt`, `phase1_macro_en.txt`
- `turn_phase1_ko.txt`, `turn_phase1_en.txt`

---

*Theo (Windows Lab) — 2026-02-10*
*Ray/Cody 구현 착수용. 설계 완결.*
