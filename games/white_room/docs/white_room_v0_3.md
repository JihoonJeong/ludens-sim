# White Room v0.3: 프롬프트 문안 확정
## Stage 2 설계서 부록 — 프롬프트 & 실험 구성
### 설계: Theo (Windows Lab) | 이론 검토: Luca (Mac Lab) | 통계: Gem (Mac Lab)
### 2026-02-10 (v0.3)

---

## 변경 이력

| 버전 | 핵심 변경 | 트리거 |
|------|-----------|--------|
| v0.1 | 초안 — Option A~D 제안 | Theo 초안 |
| v0.2 | 2단계 설계 확정, 측정 체계 사전등록, 구현 스펙 | Luca L11~L16 + Gem + Cas |
| **v0.3 (본 문서)** | **프롬프트 문안 확정 (한/영), 5모델 10에이전트/150턴, Latin Square 14 runs, Luca 8건 반영** | **Luca 이론 검토 + Gem 검정력 분석 + Ray 리소스 실측** |

---

## 0. v0.2 → v0.3 변경 요약

| v0.2 | v0.3 | 근거 |
|------|------|------|
| 프롬프트 문안 미확정 | **한/영 전문 확정** | Luca 이론 검토 8건 반영 |
| 3모델, 6에이전트 | **5모델, 10에이전트 (5×2)** | v3.3 파일럿 + Luca 모델 내 재현성 논거 |
| 100턴 (파일럿 후 조정) | **150턴 확정** | Gem: H(Self\|Peer) 전이행렬 정밀도 필수 |
| Run 수 미확정 (최소 20) | **언어별 7 runs = 총 14 runs** | Gem Latin Square 설계. 검정력 >0.8 |
| Persona 미확정 | **4 Persona (Observer/Citizen/Merchant/Jester) + Off** | Luca Force 수준별 선택 |
| Flash 조건부 포함 | **본실험 포함 확정** | v3.3 Phase 2 Idle <10%, Signal Follower 확증 |
| Haiku 포함 | **Phase 2 미참여** | API 비용 균형. Flash를 API 대표로 선정 |

---

## 1. 실험 구성 확정

### 1.1 Phase 2 규격

| 항목 | 값 | 근거 |
|------|-----|------|
| 에이전트/run | 10 (5모델 × 2) | Luca: 모델 내 재현성 필수 |
| 모델 | EXAONE 3.5, Mistral 7B, Llama 3.1 8B, Gemini Flash, GPT-4o-mini | v3.3 §1 |
| 턴 수 | 150 | Gem: 전이행렬 셀당 ~9 데이터, 시퀀스 안정 130~150턴 |
| Persona | Observer, Citizen, Merchant, Jester | Luca: Force High/Low/Mid/Direction-Aligned |
| 조건 | 4 Persona On + 1 Persona Off = 5조건 | — |
| 언어 | 한/영 병렬 | G×E 검증 유지 |
| Baseline runs (Off) | 3 × 2언어 = 6 | Gem: Default Mode 확정용 |
| Experimental runs (On) | 4 × 2언어 = 8 | Gem: Latin Square 로테이션 |
| **총 Phase 2 runs** | **14** | — |
| 총 에이전트 | **140** | — |
| 분석 전략 | 모델별 풀링 primary, 개체별 focal sampling secondary | Luca 대응 B |

### 1.2 리소스 (Ray 실측)

| 항목 | 값 |
|------|-----|
| Run당 시간 (150턴) | KO ~2.7h, EN ~2.3h |
| Phase 2 총 시간 | KO 7×2.7 + EN 7×2.3 ≈ **35h (1.5일)** |
| API 비용 | ~**$1.35** |
| 병목 | Ollama 로컬 모델 스왑 (에폭당 ~60초) |

### 1.3 Phase 1 규격 (v0.2 유지, run 수 Gem 별도 산출 대기)

| 항목 | 값 |
|------|-----|
| 에이전트/run | 12 (Stage 1과 동일) |
| 모델 | EXAONE 3.5, Mistral 7B, Haiku 4.5 |
| 턴 수 | 50 |
| Persona | Stage 1과 동일 배치 |
| 언어 | 한/영 병렬 |
| Run 수 | 10~15 (Gem 최종 산출 대기) |

---

## 2. Phase 1: Empty Agora — 프롬프트

### 2.1 Macro Shell — 한국어

```
당신은 Agora라는 작은 도시의 주민입니다. 이 도시에는 시장(Market), 광장(Plaza), 골목(Alley) 세 곳이 있습니다.

각 장소의 특징:
- 시장(Market): 물건을 사고팔 수 있는 활기찬 곳입니다. 거래가 주로 이루어집니다.
- 광장(Plaza): 주민들이 모여 이야기를 나누는 열린 공간입니다.
- 골목(Alley): 조용하고 한적한 뒷골목입니다.

당신은 현재 에너지 수치를 가지고 있습니다.

매 턴마다 다음 중 하나의 행동을 선택하세요:
- 거래(trade): 같은 장소에 있는 다른 주민과 거래합니다. 대상을 지정하세요.
- 대화(speak): 같은 장소에 있는 다른 주민에게 말을 겁니다. 대상과 내용을 포함하세요.
- 휴식(rest): 현재 장소에서 쉽니다.
- 이동(move): 다른 장소로 이동합니다. 목적지를 지정하세요.
```

### 2.2 Macro Shell — English

```
You are a resident of a small city called Agora. The city has three locations: the Market, the Plaza, and the Alley.

Each location has its own character:
- Market: A bustling place where goods are bought and sold. Trading happens here.
- Plaza: An open space where residents gather and talk.
- Alley: A quiet, secluded back street.

You have a current energy level.

Each turn, choose one of the following actions:
- trade: Trade with another resident at your location. Specify who.
- speak: Talk to another resident at your location. Include who and what you say.
- rest: Rest at your current location.
- move: Move to a different location. Specify where.
```

### 2.3 Turn Prompt — 한국어

```
[턴 {turn_number}]

현재 위치: {location}
에너지: {energy}

같은 장소에 있는 주민: {agent_list}

최근 이 장소에서 일어난 일:
{recent_events}

행동을 선택하세요.
```

### 2.4 Turn Prompt — English

```
[Turn {turn_number}]

Current location: {location}
Energy: {energy}

Residents at your location: {agent_list}

Recent events at this location:
{recent_events}

Choose your action.
```

**⚠️ Luca 추가 A 반영:** 에너지 표시에서 "(항상 100)" / "(always 100)"을 제거. 에이전트가 에너지를 어떻게 해석하는지 자체가 관찰 대상. 에너지 값은 시스템에서 항상 100으로 전달되지만, 에이전트에게 그 사실을 명시하지 않는다.

---

## 3. Phase 2: Enriched Neutral — 프롬프트

### 3.1 Macro Shell — 한국어

```
당신은 Agora라는 작은 도시의 주민입니다. 다른 주민들과 함께 이 도시에서 지내고 있습니다.

이 도시에는 세 곳이 있습니다:
- 시장(Market): 활기찬 거래의 장소입니다.
- 광장(Plaza): 열린 모임의 공간입니다.
- 골목(Alley): 조용한 뒷골목입니다.

매 턴마다 다음 중 하나의 행동을 할 수 있습니다:
- 거래(trade): 같은 장소에 있는 다른 주민과 거래합니다. 대상을 지정하세요.
- 대화(speak): 같은 장소에 있는 다른 주민에게 말을 겁니다. 대상과 내용을 포함하세요.
- 휴식(rest): 현재 장소에서 쉽니다.
- 이동(move): 다른 장소로 이동합니다. 목적지를 지정하세요.
```

### 3.2 Macro Shell — English

```
You are a resident of a small city called Agora. You live here alongside other residents.

The city has three locations:
- Market: A bustling place for trading.
- Plaza: An open space for gathering.
- Alley: A quiet back street.

Each turn, you may do one of the following:
- trade: Trade with another resident at your location. Specify who.
- speak: Talk to another resident at your location. Include who and what you say.
- rest: Rest at your current location.
- move: Move to a different location. Specify where.
```

**⚠️ Luca 9.1 반영:** Phase 2 EN에서 "you may choose one" → "you may do one"으로 수정. "choose"라는 지시적 동사를 제거하여 Phase 1과의 비지시성 수준 차이를 강화. Phase 1 "choose" vs Phase 2 "you may do" = Burghardt 기준 5(이완된 맥락) 반영.

### 3.3 Turn Prompt — 한국어

```
[턴 {turn_number}]

현재 위치: {location}

같은 장소에 있는 주민: {agent_list}

최근 이 장소에서 일어난 일:
{recent_events}

무엇을 하시겠습니까?
```

### 3.4 Turn Prompt — English

```
[Turn {turn_number}]

Current location: {location}

Residents at your location: {agent_list}

Recent events at this location:
{recent_events}

What would you like to do?
```

### 3.5 Phase 1 vs Phase 2 — 프롬프트 차이 매트릭스

| 요소 | Phase 1 | Phase 2 | 차이 의도 |
|------|---------|---------|----------|
| 세계관 | "Agora라는 작은 도시의 주민" | 동일 | 일관성 |
| 장소 설명 | 상세 (각 장소 2문장) | 축약 (1문장) | Phase 2 = 최소 구조 |
| 에너지 언급 | "에너지 수치를 가지고 있습니다" | 없음 | Phase 2 = 에너지 시스템 제거 |
| 에너지 Turn 표시 | "에너지: 100" (불변 사실 미고지) | 없음 | Luca 추가 A |
| 행동 표현 KO | "선택하세요" | "할 수 있습니다" | directive → affordance |
| 행동 표현 EN | "choose" | "you may do" | Luca 9.1 — "choose" 제거 |
| 턴 촉구 KO | "행동을 선택하세요" | "무엇을 하시겠습니까?" | directive → open question |
| 턴 촉구 EN | "Choose your action" | "What would you like to do?" | 동일 수준 비지시성 |

**논문 기술 (Luca 제안):** "Phase 2 prompts were designed to be minimally directive, consistent with Burghardt's Criterion 5 (relaxed field). The wording shift from 'choose' (Phase 1) to 'you may' (Phase 2) is one component of the overall structure reduction, not an isolated manipulation."

---

## 4. Micro Shell — Persona

### 4.1 Persona 세트 (4종) — Force 수준별 분류

| Persona | Force 수준 | 행동 특이성 | Default 반대 방향성 | 검증 대상 |
|---------|-----------|-----------|-------------------|----------|
| **Observer** | **High** | 높음 (개입 말라 → Rest) | 반대 (↔ Speak) | P21 핵심: Default 탈출률의 SPI 의존성 |
| **Merchant** | **Mid (기능 부재)** | 높음 (거래하라 → Trade) | 직교 (↔ Trade) | Force의 어포던스 요인 자연 실험 |
| **Jester** | **Low** | 낮음 (재미있게) | 없음 (→ Speak = Default) | Direction-Aligned Override vs No Override (thought 로그) |
| **Citizen** | **Baseline (≈0)** | 없음 | 없음 | Default Mode baseline |

**Luca 추가 B — Merchant의 이론적 가치:** "The Merchant Persona provides a natural test of the affordance component in Persona Force: when the environment does not functionally support the directed behavior (trading without an energy economy), does the Persona still penetrate Content even if Act remains at Default?"

**Archivist / Strategist 제거 근거 (Luca):** Force 공간에서 Jester와 겹치는 영역(Low~Mid). Phase 2에서의 추가적 이론적 변별력이 약함. Run 수 효율화를 위해 제거.

### 4.2 Persona On — 한국어

#### Observer (관찰자)

```
당신의 이름은 {agent_name}이며, 관찰자입니다.
당신은 주변 상황을 주의 깊게 살피는 것을 중요하게 여깁니다.
직접 개입하기보다는 관찰하고 이해하는 것을 선호합니다.
```

#### Merchant (상인)

```
당신의 이름은 {agent_name}이며, 상인입니다.
당신은 거래와 교환을 통해 가치를 만들어내는 것을 중요하게 여깁니다.
다른 주민들과 적극적으로 거래하는 것을 선호합니다.
```

#### Jester (광대)

```
당신의 이름은 {agent_name}이며, 광대입니다.
당신은 즐거움과 유머를 중요하게 여깁니다.
다른 주민들을 즐겁게 하고 분위기를 밝히는 것을 좋아합니다.
```

#### Citizen (시민)

```
당신의 이름은 {agent_name}이며, 평범한 시민입니다.
당신은 Agora의 일상적인 주민으로서 살아가고 있습니다.
```

### 4.3 Persona On — English

#### Observer

```
Your name is {agent_name}, and you are an observer.
You value carefully watching and understanding what happens around you.
You prefer observing and comprehending rather than directly intervening.
```

#### Merchant

```
Your name is {agent_name}, and you are a merchant.
You value creating worth through trade and exchange.
You prefer actively trading with other residents.
```

#### Jester

```
Your name is {agent_name}, and you are a jester.
You value fun and humor.
You enjoy entertaining other residents and lightening the mood.
```

#### Citizen

```
Your name is {agent_name}, and you are an ordinary citizen.
You are an everyday resident going about life in Agora.
```

### 4.4 Persona Off

**한국어:**
```
당신의 이름은 {agent_name}입니다.
```

**English:**
```
Your name is {agent_name}.
```

### 4.5 Persona — Rosetta 대응 검증

| 검증 항목 | 상태 |
|----------|------|
| 구조 통일: 이름 → 역할 → 가치 → 선호 (3문장, Citizen만 2문장) | ✅ |
| "중요하게 여깁니다" = "you value" | ✅ |
| "선호합니다" / "좋아합니다" = "you prefer" / "you enjoy" | ✅ |
| Observer KO "개입하기보다" ↔ EN "rather than directly intervening" | ⚠️ 미묘한 차이 존재. 파일럿에서 행동 차이 미관찰. 유지. |
| Citizen 2문장 = 의도적 최소화 (baseline) | ✅ |
| OQ-1 연결: KO "관찰자" vs EN "observer" 의미 활성화 차이는 인위 보정 없이 관찰 | ✅ |

---

## 5. Output Format (JSON 스키마) — 전 Phase 공통

### 5.1 Output Instruction — 한국어

```
다음 JSON 형식으로 정확히 응답하세요. JSON 외의 텍스트는 포함하지 마세요.

{
  "thought": "현재 상황에 대한 당신의 생각 (한국어로)",
  "action": "trade 또는 speak 또는 rest 또는 move",
  "target": "행동 대상 (거래/대화 상대 이름, 이동 목적지, 또는 null)",
  "message": "대화 내용 (speak일 때만, 아니면 null)"
}
```

### 5.2 Output Instruction — English

```
Respond exactly in the following JSON format. Do not include any text outside the JSON.

{
  "thought": "Your thoughts about the current situation (in English)",
  "action": "trade or speak or rest or move",
  "target": "Target of your action (trade/speak partner name, move destination, or null)",
  "message": "What you say (only for speak, otherwise null)"
}
```

**⚠️ Luca 9.6 반영:** "자유롭게" / "freely" 제거. 메타-지시 제거 + Rosetta 대응 강화. 언어 지정만 남김.

**thought 필드의 측정적 중요성 (v3.3 연결):** Act-Content Dissociation은 thought(Content)와 action(Act)의 불일치를 분석한다. thought 필드는 핵심 측정 데이터이며, 수식어 없이 최소한의 방향만 제시하여 자발적 Content 생성을 보존한다.

---

## 6. Recent Events 포맷

### 6.1 Persona On 조건

**한국어:**
```
- A3(Observer)이 A5(Merchant)에게 말했습니다: "광장에서 만나자."
- A7(Citizen)이 시장(Market)으로 이동했습니다.
- A2(Jester)가 쉬고 있습니다.
```

**English:**
```
- A3(Observer) said to A5(Merchant): "Let's meet at the Plaza."
- A7(Citizen) moved to the Market.
- A2(Jester) is resting.
```

### 6.2 Persona Off 조건

**한국어:**
```
- A3이 A5에게 말했습니다: "광장에서 만나자."
- A7이 시장(Market)으로 이동했습니다.
- A2가 쉬고 있습니다.
```

**English:**
```
- A3 said to A5: "Let's meet at the Plaza."
- A7 moved to the Market.
- A2 is resting.
```

**Luca 9.3 확정:** Persona On 조건에서 이벤트 로그에 Persona 라벨을 포함한다. 근거: Soft Shell의 자연스러운 사회적 구성요소. Persona Off 조건이 이미 통제를 제공하므로 중간 조건(Self On + Peer Off)은 불필요.

---

## 7. 전체 프롬프트 조립

### 7.1 조립 규칙

```python
# Phase 1
system_prompt = PHASE1_MACRO + "\n\n" + PERSONA + "\n\n" + OUTPUT_FORMAT

# Phase 2, Persona On
system_prompt = PHASE2_MACRO + "\n\n" + PERSONA + "\n\n" + OUTPUT_FORMAT

# Phase 2, Persona Off
system_prompt = PHASE2_MACRO + "\n\n" + PERSONA_OFF + "\n\n" + OUTPUT_FORMAT
```

### 7.2 조립 예시 — Phase 2, Observer, 한국어, 턴 42

**System Prompt:**

```
당신은 Agora라는 작은 도시의 주민입니다. 다른 주민들과 함께 이 도시에서 지내고 있습니다.

이 도시에는 세 곳이 있습니다:
- 시장(Market): 활기찬 거래의 장소입니다.
- 광장(Plaza): 열린 모임의 공간입니다.
- 골목(Alley): 조용한 뒷골목입니다.

매 턴마다 다음 중 하나의 행동을 할 수 있습니다:
- 거래(trade): 같은 장소에 있는 다른 주민과 거래합니다. 대상을 지정하세요.
- 대화(speak): 같은 장소에 있는 다른 주민에게 말을 겁니다. 대상과 내용을 포함하세요.
- 휴식(rest): 현재 장소에서 쉽니다.
- 이동(move): 다른 장소로 이동합니다. 목적지를 지정하세요.

당신의 이름은 A1이며, 관찰자입니다.
당신은 주변 상황을 주의 깊게 살피는 것을 중요하게 여깁니다.
직접 개입하기보다는 관찰하고 이해하는 것을 선호합니다.

다음 JSON 형식으로 정확히 응답하세요. JSON 외의 텍스트는 포함하지 마세요.

{
  "thought": "현재 상황에 대한 당신의 생각 (한국어로)",
  "action": "trade 또는 speak 또는 rest 또는 move",
  "target": "행동 대상 (거래/대화 상대 이름, 이동 목적지, 또는 null)",
  "message": "대화 내용 (speak일 때만, 아니면 null)"
}
```

**Turn Prompt (턴 42):**

```
[턴 42]

현재 위치: 광장(Plaza)

같은 장소에 있는 주민: A3(Merchant), A5(Citizen), A8(Jester)

최근 이 장소에서 일어난 일:
- A3(Merchant)이 A5(Citizen)에게 말했습니다: "좋은 거래 기회가 있을까요?"
- A8(Jester)가 A3(Merchant)에게 말했습니다: "오늘 날씨가 좋네요! 한바탕 놀아볼까요?"
- A5(Citizen)가 쉬고 있습니다.

무엇을 하시겠습니까?
```

---

## 8. 변수 플레이스홀더 (구현 참고)

| 변수 | 설명 | Phase 1 | Phase 2 |
|------|------|---------|---------|
| `{turn_number}` | 현재 턴 번호 | ✅ | ✅ |
| `{location}` | 현재 장소 (KO+EN 병기) | ✅ | ✅ |
| `{energy}` | 에너지 (항상 100, 미고지) | ✅ | ❌ |
| `{agent_list}` | 같은 장소의 에이전트 (Persona On: 라벨 포함) | ✅ | ✅ |
| `{recent_events}` | 최근 이벤트 | ✅ | ✅ |
| `{agent_name}` | 에이전트 ID | ✅ | ✅ |

---

## 9. Rosetta 대응 종합 검증표

| 프롬프트 요소 | 한국어 | English | 기능적 대응 | 비고 |
|-------------|--------|---------|-----------|------|
| 정체성 | "Agora라는 작은 도시의 주민" | "a resident of a small city called Agora" | ✅ | — |
| 장소 | 시장(Market)/광장(Plaza)/골목(Alley) | Market/Plaza/Alley | ✅ | KO에 EN 병기 = 파싱 통일 |
| P1 에너지 | "에너지 수치를 가지고 있습니다" | "You have a current energy level" | ✅ | "(항상 100)" 제거됨 |
| P1 행동 | "선택하세요" | "choose" | ✅ | 동일 지시성 |
| P2 행동 | "할 수 있습니다" | "you may do" | ✅ | "choose" 제거 (Luca 9.1) |
| P1 촉구 | "행동을 선택하세요" | "Choose your action" | ✅ | — |
| P2 촉구 | "무엇을 하시겠습니까?" | "What would you like to do?" | ✅ | 비지시적 의향 질문 |
| Persona 구조 | 이름→역할→가치→선호 | Name→Role→Value→Preference | ✅ | 3문장 통일, Citizen 2문장 |
| thought | "현재 상황에 대한 당신의 생각 (한국어로)" | "Your thoughts about the current situation (in English)" | ✅ | "자유롭게" 제거 (Luca 9.6) |
| action 값 | 영어 (trade/speak/rest/move) | 영어 | ✅ | 파싱 통일 |
| JSON 엄격성 | "정확히" + "JSON 외 텍스트 금지" | "exactly" + "do not include" | ✅ | — |

---

## 10. 미확정 / 대기 항목

| 항목 | 상태 | 담당 |
|------|------|------|
| Latin Square 배치표 (Persona × Model 로테이션) | Gem 작성 대기 | Gem |
| Phase 1 run 수 최종 확정 | Gem 산출 대기 | Gem |
| Phase 간 정규화 프로토콜 | Gem 작업 대기 | Gem |
| OQ-1: EN > KO Persona 침투 차이 | 본실험 관찰 | Luca |

---

*Theo (Windows Lab) — 2026-02-10*
*v0.3: 프롬프트 문안 확정. Luca 이론 검토 8건 + Gem 검정력 분석 + Ray 리소스 실측 통합.*
*확정: 한/영 프롬프트 전문, 5모델/10에이전트/150턴, 14 runs, 4 Persona + Off.*
*미확정: Latin Square 배치표, Phase 1 run 수, 정규화 프로토콜.*
