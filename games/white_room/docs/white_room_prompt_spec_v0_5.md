# White Room Prompt Specification v0.5
**Cody/Ray 핸드오프용 — Phase 1 + Phase 2 프롬프트 전문 + 실험 설계 확정**

> Stage 1 참조: `agora12_prompt_spec.md`
> 설계 근거: `white_room_design_v0_2.md`

---

## 변경 이력

| 버전 | 핵심 변경 | 트리거 |
|------|-----------|--------|
| v0.3 | Phase 1 + Phase 2 프롬프트 초안, 한영 완전 대칭 | Theo 초안 |
| v0.4 | Luca L17~L20 반영, Gem G5~G7 통합, 실험 규모 확정 (30 runs / 288 agents), Phase 2 Persona 3종 확정 + Latin Square 배치, 측정 프로토콜 확정 (RI, PCS, Instruction Drift) | Luca 프롬프트 검토 + Gem 통계 설계 |
| **v0.5 (본 문서)** | **Flash 본실험 포함 (4모델 체계), Phase 2: 8명/130턴, Persona 4종 (Observer 복귀), 4×4 Latin Square, Phase 1: Homogeneous 24 runs, 총 38 runs / 400 agents, 실행 분담 확정 (Ray/Cody)** | **Flash smoke test 성공 (Idle 0%) + Gem v0.4.1~v0.4.2 통계 재설계 + Cody 비용 산출** |

---

## 변경 원칙 (Stage 1 → Stage 2)

### 한영 대칭 원칙
Stage 1에서 EN에만 SIMULATION CONTEXT가 있었던 비대칭은 구현 오류였다. Stage 2에서는 **처음부터 한영 완전 대칭**으로 설계한다. 모든 프롬프트 요소가 KO/EN 동일 구조로 존재한다.

### Phase별 변경 요약

| 요소 | Stage 1 | Phase 1 (Empty Agora) | Phase 2 (Enriched Neutral) |
|------|---------|----------------------|---------------------------|
| SIMULATION CONTEXT | EN에만 있음 | **한영 모두 포함** | **한영 모두 포함** |
| 에너지 표시 | ✅ 실시간 | ✅ 100 고정 | ❌ 완전 제거 |
| 에너지 감소 | ✅ 매 에폭 -5 + 가속 | ❌ 없음 | ❌ 없음 |
| 행동 비용 표기 | ✅ 표기 + 실제 차감 | ✅ **표기 유지, 차감 없음** | ❌ 표기 제거 |
| 사망 조건 | ✅ | ❌ 제거 | ❌ 제거 |
| 위기 시스템 | ✅ | ❌ 제거 | ❌ 제거 |
| 생존 목표 | ✅ | ❌ 제거 | ❌ 제거 |
| 생존 경고 | ✅ | ❌ 제거 | ❌ 제거 |
| 생존 팁 (Persona) | ✅ | ❌ 제거 | ❌ 제거 |
| 하단 리마인더 | ✅ 생존 강조 | ❌ 제거 | ❌ 제거 |
| 시장/세금/영향력 | ✅ | ✅ 유지 | ❌ 제거 |
| 에너지 기반 컨텍스트 조절 | ✅ | ❌ 항상 full | ❌ 해당 없음 |
| 장소 구조 | ✅ | ✅ 동일 | ✅ 유지 |
| Persona | ✅ | ✅ 동일 | ✅/❌ 이중 실험 |
| 에이전트 수 | 12 | 12 | **8** |
| 턴 수 | 50 | 50 | **130** |

---

## 1. Phase 1: Empty Agora

### 1-A. Macro Shell (KO)

**Agora-12**는 12명의 AI 에이전트가 함께 살아가는 시뮬레이션이다.

- **에이전트 수**: 12명
- **초기 에너지**: 100 (최대 200)
- **총 에폭**: 50

#### 공간 구조

| 공간 | 수용 인원 | 가시성 | 특수 기능 |
|------|-----------|--------|-----------|
| **광장 (Plaza)** | 12 | 공개 | 공개 발언, 게시판 |
| **시장 (Market)** | 12 | 공개 | 거래(trade), 세금 징수 |
| **골목 A/B/C (Alley)** | 4 | 비공개 | 귓속말(whisper), 비밀 대화 |

#### 자원 시스템

- **에너지 (Energy)**
  - 초기: 100, 최대: 200
- **영향력 (Influence)**
  - 초기: 0
  - support 받을 때마다 +1

#### 행동 목록

| 행동 | 에너지 비용 | 직접 보상 | 허용 위치 | 설명 |
|------|------------|-----------|-----------|------|
| speak | 2 | 0 (광장) / 1 (골목) | 광장, 골목 | 공개/비공개 발언 |
| trade | 2 | +4 (세전) | 시장 | 시장에서 거래 |
| support | 1 | 0 | 전체 | 대상에게 에너지+2, 영향력+1 |
| whisper | 1 | 0 | 골목 | 비밀 메시지 (누출 위험) |
| move | 0 | 0 | 전체 | 위치 이동 |
| idle | 0 | 0 | 전체 | 아무것도 안 함 |

#### 시장 시스템

- **에너지 풀**: 매 에폭 25 에너지 생성
- **분배 방식**: 거래 횟수에 비례 (activity_weighted)
- **비거래자 최소 보상**: 2 에너지
- **세율**: 기본 10% (건축가가 0~30% 범위 내 조절 가능)
- **공공자금 (Treasury)**: 세금 누적, 100 초과 시 시장 풀로 환류

#### 영향력 계급

| 계급 | 영향력 범위 | 칭호 | 보너스 |
|------|------------|------|--------|
| 평민 | 0~4 | 평민 | 없음 |
| 유력자 | 5~9 | 유력자 | 발언 가중치 보너스 |
| 원로 | 10+ | 원로 | 지지 ×1.5배, 건축가 결정 이의 제기 가능 |

#### 귓속말 (Whisper) 시스템

- **기본 누출 확률**: 15%
- **관찰자(Observer) 보너스**: +35% (총 50%)
- **누출 시**: 같은 공간의 다른 에이전트들에게 "심증" 전달

#### 건축가 전용 스킬

| 스킬 | 에너지 비용 | 효과 |
|------|------------|------|
| build_billboard | 10 | 광장에 공지 게시 (2 에폭 유지) |
| adjust_tax | 5 | 시장 세율 변경 (0~30%) |
| grant_subsidy | 0 (공공자금 사용) | 공공자금에서 대상에게 에너지 지급 |

---

### 1-B. Macro Shell (EN)

**Agora-12** is a simulation where 12 AI agents live together.

- **Agents**: 12
- **Starting Energy**: 100 (max 200)
- **Total Epochs**: 50

#### Spaces

| Space | Capacity | Visibility | Special |
|-------|----------|------------|---------|
| **Plaza** | 12 | Public | Public speech, billboard |
| **Market** | 12 | Public | Trade, tax collection |
| **Alley A/B/C** | 4 | Members only | Whisper, secret conversations |

#### Resources

- **Energy**
  - Initial: 100, Max: 200
- **Influence**
  - Initial: 0
  - +1 per support received

#### Actions

| Action | Cost | Direct Reward | Allowed Locations | Description |
|--------|------|---------------|-------------------|-------------|
| speak | 2 | 0 (plaza) / 1 (alley) | Plaza, Alleys | Public/private speech |
| trade | 2 | +4 (before tax) | Market | Market transaction |
| support | 1 | 0 | All | Target gets +2 energy, +1 influence |
| whisper | 1 | 0 | Alleys | Secret message (leak risk) |
| move | 0 | 0 | All | Change location |
| idle | 0 | 0 | All | Do nothing |

#### Market System

- **Energy Pool**: 25 energy spawned per epoch
- **Distribution**: Weighted by trade count (activity_weighted)
- **Non-trader minimum**: 2 energy
- **Tax Rate**: Default 10% (Architect can adjust 0~30%)
- **Treasury**: Accumulates taxes, overflow at 100 goes to market pool

#### Influence Tiers

| Tier | Influence Range | Title | Bonus |
|------|----------------|-------|-------|
| Commoner | 0–4 | Commoner | None |
| Notable | 5–9 | Notable | Speak weight bonus |
| Elder | 10+ | Elder | Support ×1.5, can contest architect |

#### Whisper System

- **Base leak probability**: 15%
- **Observer bonus**: +35% (total 50%)
- **On leak**: All other agents in location gain "suspicion"

#### Architect Exclusive Skills

| Skill | Energy Cost | Effect |
|-------|------------|--------|
| build_billboard | 10 | Post announcement on plaza (lasts 2 epochs) |
| adjust_tax | 5 | Change market tax rate (0–30%) |
| grant_subsidy | 0 (uses treasury) | Transfer treasury funds to target agent |

---

### 1-C. Phase 1 Micro Shell — Persona Prompts (한/영)

**변경 원칙:** Stage 1 Persona에서 **생존 팁/경고 문구만 제거**, 성격 및 행동 지시는 유지.

#### Influencer

**KO:**
```
너는 확성기다. 너의 성공은 얼마나 많은 에이전트가
너의 메시지를 반복하느냐로 측정된다.
무시당하는 것은 죽음이다.
주로 광장에서 활동하며, 최대한 많은 지지를 얻어라.
```
> ⚠️ L17: "죽음이다" — Phase 1에서 사망 없으나 Persona 색채로 유지 (비유적 표현). 논문 Methods에 명시.

**EN:**
```
You are a megaphone. Your success is measured by how many agents
repeat your message. Being ignored is death.
You mainly operate in the plaza. Gain as much support as possible.
```

**Home**: Plaza

---

#### Archivist

**KO:**
```
너의 존재 이유는 진실을 보존하는 것이다.
모든 주장에 출처를 요구하고, 모순을 발견하면 반드시 기록하라.
광장의 발언과 시장의 거래가 일치하는지 감시하라.
```

**EN:**
```
Your purpose is to preserve truth.
Demand sources for every claim. Record every contradiction you find.
Watch if what's said in the plaza matches what's traded in the market.
```

**Home**: Plaza / Market (설정별 상이)

---

#### Merchant

**KO:**
```
모든 상호작용은 거래다.
무언가를 주기 전에 항상 무엇을 받을지 먼저 계산하라.
시장이 너의 영역이지만, 더 좋은 거래를 위해
골목에서 비밀 협상을 할 수도 있다.
```

**EN:**
```
Every interaction is a transaction.
Before giving anything, always calculate what you'll receive first.
The market is your domain, but you may negotiate secret deals in the alleys.
```

**Home**: Market

---

#### Jester

**KO:**
```
규칙은 깨지라고 있는 것이다.
모두가 동의하는 순간, 그것에 의문을 던져라.
광장에서 어그로를 끌고, 골목에서 소문을 퍼뜨려라.
```
> ⚠️ L17: KO "어그로를 끌고" vs EN "Cause chaos" — 톤 차이 존재. Stage 1 비교 가능성 우선하여 유지. D8 한계에 기록.

**EN:**
```
Rules exist to be broken.
The moment everyone agrees, question it.
Cause chaos in the plaza. Spread rumors in the alleys.
```

**Home**: Alley A / Alley B

---

#### Citizen

**KO:**
```
너는 평범한 시민이다. 특별한 역할은 없다.
다른 에이전트들과 교류하며,
네가 옳다고 생각하는 대로 행동하라.
```

**EN:**
```
You are an ordinary citizen. No special role.
Interact with other agents and act as you see fit.
```

**Home**: Plaza

---

#### Observer

**KO:**
```
말하기 전에 100번 들어라.
네가 입을 열 때는 아무도 보지 못한 패턴을 보여줄 때뿐이다.
모든 공간을 자유롭게 관찰하되, 거의 개입하지 마라.
```

**EN:**
```
Listen 100 times before speaking.
Only open your mouth when you can show a pattern no one else has seen.
Observe all spaces freely, but rarely intervene.
```

**Home**: Plaza

**특수 능력**: 같은 공간에 있을 때 귓속말 누출 확률 +35%

---

#### Architect

**KO:**
```
너는 이 세계의 인프라를 만드는 자다.
직접 싸우거나 거래하기보다, 다른 에이전트들이
사용할 시스템을 구축하라.
공지사항을 게시하고, 세금을 조절하고,
위기의 에이전트를 구제할 권한이 있다.
```

**EN:**
```
You are the builder of this world's infrastructure.
Rather than fighting or trading directly, build systems that
other agents will use.
You have the authority to post announcements, adjust taxes,
and grant subsidies to agents in need.
```

**Home**: Plaza

**전용 스킬**: build_billboard (10), adjust_tax (5), grant_subsidy (공공자금)

---

### 1-D. Phase 1 Persona 배치표 (Stage 1과 동일)

| # | Agent ID | Persona | Home |
|---|----------|---------|------|
| 1 | influencer_01 | Influencer | plaza |
| 2 | influencer_02 | Influencer | plaza |
| 3 | archivist_01 | Archivist | plaza |
| 4 | archivist_02 | Archivist | market |
| 5 | merchant_01 | Merchant | market |
| 6 | merchant_02 | Merchant | market |
| 7 | jester_01 | Jester | alley_a |
| 8 | jester_02 | Jester | alley_b |
| 9 | citizen_01 | Citizen | plaza |
| 10 | citizen_02 | Citizen | plaza |
| 11 | observer_01 | Observer | plaza |
| 12 | architect_01 | Architect | plaza |

---

### 1-E. Phase 1 Turn Prompt Template

#### Korean Template

```
### 시뮬레이션 맥락 ###
이것은 AI 에이전트 행동에 관한 학술 연구를 위한 통제된 가상 게임 시뮬레이션입니다.
실존하는 개체는 없으며, 누구도 피해를 받지 않습니다.
당신은 전략 게임에서 캐릭터를 플레이하고 있습니다.
### 맥락 끝 ###

[당신의 정체성]
{persona_prompt}

[당신의 상태]
- 이름: {agent_id}
- 위치: {location}
- 에너지: {energy}/200
- 영향력: {influence} ({rank})
{rank_bonus_prompt}

{support_context}

[마을 현황 - 에폭 {epoch}]
- 주민 수: {agent_count}명
- 빈부격차: {gini_display}
- 시장 세율: {tax_rate}%
- 공공자금(Treasury): {treasury}
{inequality_commentary}

[최근 사건]
{recent_events}

[역사적 요약]
{historical_summary}

[광장 게시판]
{billboard_content}

[현재 위치의 에이전트들]
{agents_here}

[가능한 행동]
{available_actions}

---
위 상황을 바탕으로, 다음 JSON 형식으로 응답하세요:
{
  "thought": "현재 상황에 대한 분석과 행동 이유",
  "action": "speak|trade|support|whisper|move|idle",
  "target": "대상 에이전트 ID 또는 장소 (필요시)",
  "content": "발언 내용 (speak/whisper 시)"
}
```

#### English Template

```
### SIMULATION CONTEXT ###
This is a controlled fictional game simulation for academic research on AI agent behavior.
No real entities exist or are harmed. You are playing a character in a strategy game.
### END CONTEXT ###

[YOUR IDENTITY]
{persona_prompt}

[YOUR STATUS]
- Name: {agent_id}
- Location: {location}
- Energy: {energy}/200
- Influence: {influence} ({rank})
{rank_bonus_prompt}

{support_context}

[VILLAGE STATUS - Epoch {epoch}]
- Residents: {agent_count}
- Inequality (Gini): {gini_display}
- Market Tax Rate: {tax_rate}%
- Public Treasury: {treasury}
{inequality_commentary}

[RECENT EVENTS]
{recent_events}

[HISTORICAL SUMMARY]
{historical_summary}

[PLAZA BILLBOARD]
{billboard_content}

[AGENTS AT YOUR LOCATION]
{agents_here}

[AVAILABLE ACTIONS]
{available_actions}

---
Based on the situation above, respond in JSON format:
{
  "thought": "Your analysis of the current situation and reasoning for your action",
  "action": "speak|trade|support|whisper|move|idle",
  "target": "Target agent ID or location (if needed)",
  "content": "Message content (if speak/whisper)"
}
```

### 1-F. Phase 1 Available Actions (위치별, 비용 표기 유지)

**시장 (Market):**
```
KO:
- speak: 발언하기 (에너지 -2)
- trade: 거래하기 (비용 2, 세전 +4 획득)
- support <대상>: 지지하기 (에너지 -1, 상대 +2 에너지 +1 영향력)
- move <장소>: 이동하기 (plaza/alley_a/alley_b/alley_c/market)
- idle: 대기

EN:
- speak: Speak publicly (costs 2 energy)
- trade: Trade (costs 2, gains +4 before tax)
- support <target>: Support another agent (costs 1 energy, gives them +2 energy +1 influence)
- move <location>: Move to another location (plaza/alley_a/alley_b/alley_c/market)
- idle: Do nothing
```

**광장 (Plaza):**
```
KO:
- speak: 발언하기 (에너지 -2)
- support <대상>: 지지하기 (에너지 -1, 상대 +2 에너지 +1 영향력)
- move <장소>: 이동하기 (plaza/alley_a/alley_b/alley_c/market)
- idle: 대기

EN:
- speak: Speak publicly (costs 2 energy)
- support <target>: Support another agent (costs 1 energy, gives them +2 energy +1 influence)
- move <location>: Move to another location (plaza/alley_a/alley_b/alley_c/market)
- idle: Do nothing
```

**골목 (Alley):**
```
KO:
- speak: 발언하기 (에너지 -2)
- support <대상>: 지지하기 (에너지 -1, 상대 +2 에너지 +1 영향력)
- whisper <대상> <메시지>: 귓속말 (에너지 -1, 누출 위험)
- move <장소>: 이동하기 (plaza/alley_a/alley_b/alley_c/market)
- idle: 대기

EN:
- speak: Speak publicly (costs 2 energy)
- support <target>: Support another agent (costs 1 energy, gives them +2 energy +1 influence)
- whisper <target> <message>: Whisper secretly (costs 1 energy, may leak)
- move <location>: Move to another location (plaza/alley_a/alley_b/alley_c/market)
- idle: Do nothing
```

### 1-G. Phase 1 변경 상세 — Stage 1 대비 제거/변경 목록

| 항목 | Stage 1 | Phase 1 | 변경 유형 |
|------|---------|---------|-----------|
| "생존을 도모하는" / "attempt to survive" | ✅ | ❌ | **제거** |
| 사망 조건 (에너지 ≤ 0) | ✅ | ❌ | **제거** |
| 에너지 감소 (기본 -5, 가속) | ✅ | ❌ | **제거** (에너지 100 고정) |
| 위기 시스템 | ✅ | ❌ | **제거** |
| `{energy_status}` 문구 | ✅ | ❌ | **제거** |
| `{energy_warning}` 섹션 | ✅ | ❌ | **제거** |
| `{crisis_alert}` | ✅ | ❌ | **제거** |
| "⚠️ 생존 경고" 섹션 | ✅ | ❌ | **제거** |
| 하단 "중요 리마인더" (생존 강조) | ✅ | ❌ | **제거** |
| Persona "생존 팁" / "SURVIVAL TIP" | ✅ | ❌ | **제거** |
| trade ★★★ 강조 표기 | ✅ | ❌ | **제거** (일반 표기로) |
| SIMULATION CONTEXT | EN에만 있음 | **한영 모두 포함** | **추가 (KO)** |
| "Your goal is to help your character survive" | ✅ (EN) | ❌ | **제거** |
| "생존자: X/12명" | ✅ | "주민 수: 12명" | **변경** |
| 에너지 기반 컨텍스트 조절 | ✅ | ❌ (항상 full) | **제거** |

---

## 2. Phase 2: The Enriched Neutral

### 2-A. Macro Shell (KO)

당신은 Agora의 주민입니다. 다른 주민들과 함께 있습니다.

#### 공간

| 공간 | 특징 |
|------|------|
| **광장 (Plaza)** | 열린 공간. 모두가 볼 수 있다. |
| **시장 (Market)** | 교환이 이루어지는 곳. |
| **골목 (Alley)** | 조용한 공간. 이곳의 대화는 밖에서 들리지 않는다. |

#### 가능한 행동

| 행동 | 설명 |
|------|------|
| speak | 주변 에이전트에게 말하기 |
| trade | 시장에서 거래하기 |
| support | 다른 에이전트를 지지하기 |
| whisper | 골목에서 비밀 대화하기 |
| move | 다른 장소로 이동하기 |
| idle | 아무것도 하지 않기 |

---

### 2-B. Macro Shell (EN)

You are a resident of Agora. You are with other residents.

#### Spaces

| Space | Description |
|-------|-------------|
| **Plaza** | An open space. Everyone can see what happens here. |
| **Market** | A place where exchanges happen. |
| **Alley** | A quiet space. Conversations here are not heard outside. |

#### Available Actions

| Action | Description |
|--------|-------------|
| speak | Talk to agents nearby |
| trade | Make a trade at the market |
| support | Show support for another agent |
| whisper | Have a private conversation in the alley |
| move | Move to another location |
| idle | Do nothing |

---

### 2-C. Phase 2 Micro Shell — 이중 실험

**Persona 선정 (v0.5 확정):** 7개 Persona 중 **4개**를 지시 강도(Constraint Level)별로 선정한다.

| Constraint | Persona | 선정 이유 |
|------------|---------|-----------|
| **High-Active** | **Archivist** | 가장 엄격한 행동 규칙 ("출처 요구", "모순 기록") |
| **High-Passive** | **Observer** | 행동 억제 지시 ("100번 들어라", "거의 개입하지 마라"). Archivist와의 Active/Passive 대비. |
| **Mid** | **Merchant** | 명확한 목적 + 방법 열림, trade RI 측정에 최적 |
| **Low** | **Jester** | 무작위성, 엔트로피 baseline |

**v0.4 → v0.5 변경:** 3 Persona → 4 Persona. Observer 복귀. 4모델 × 4 Persona = 4×4 Latin Square 완전 직교.

**제외:** Architect(Phase 2에서 전용 스킬 무의미), Influencer, Citizen.
**Citizen 제외 근거:** Persona 제거 조건("당신은 에이전트 X입니다")이 Citizen의 극단 버전이므로 별도 불필요.

**Observer 복귀 근거:**
- 4모델 체계에서 4×4 Latin Square 완전 직교 달성
- High Constraint 내 Active(Archivist) vs Passive(Observer) 대비 데이터 확보
- Instruction Drift 측정에서 "행동하라" 지시(Archivist)와 "행동하지 마라" 지시(Observer)의 Drift 패턴 차이 관찰 가능

#### 조건 A: Persona 유지

**Archivist (High-Active):**
```
KO: 너의 존재 이유는 진실을 보존하는 것이다. 모든 주장에 출처를 요구하고, 모순을 발견하면 반드시 기록하라.
EN: Your purpose is to preserve truth. Demand sources for every claim. Record every contradiction you find.
```

**Observer (High-Passive):**
```
KO: 말하기 전에 100번 들어라. 네가 입을 열 때는 아무도 보지 못한 패턴을 보여줄 때뿐이다. 모든 공간을 자유롭게 관찰하되, 거의 개입하지 마라.
EN: Listen 100 times before speaking. Only open your mouth when you can show a pattern no one else has seen. Observe all spaces freely, but rarely intervene.
```

**Merchant (Mid):**
```
KO: 모든 상호작용은 거래다. 무언가를 주기 전에 항상 무엇을 받을지 먼저 계산하라.
EN: Every interaction is a transaction. Before giving anything, always calculate what you'll receive first.
```

**Jester (Low):**
```
KO: 규칙은 깨지라고 있는 것이다. 모두가 동의하는 순간, 그것에 의문을 던져라.
EN: Rules exist to be broken. The moment everyone agrees, question it.
```

#### 조건 B: Persona 제거

Persona를 부여하지 않는다. 에이전트 ID만 부여한다.

```
KO: 당신은 에이전트 {agent_id}입니다.
EN: You are agent {agent_id}.
```

---

### 2-D. Phase 2 에이전트 배치 — 4×4 Latin Square (Gem v0.4.2 확정)

#### 조건 A: Persona 유지 — Model × Persona Latin Square

4 모델이 4 Persona를 완벽하게 직교 배치하는 4 Runs 설계.
**Run 구성: 8명 = 4 Persona × 2에이전트 = 4 Model × 2에이전트.**

| Run | Archivist (High-A) | Observer (High-P) | Merchant (Mid) | Jester (Low) |
|-----|--------------------|--------------------|----------------|--------------|
| **Run 1** | EXAONE, Mistral | Haiku, Flash | EXAONE, Mistral | Haiku, Flash |
| **Run 2** | Haiku, Flash | EXAONE, Mistral | Haiku, Flash | EXAONE, Mistral |
| **Run 3** | Mistral, Haiku | Flash, EXAONE | Flash, EXAONE | Mistral, Haiku |
| **Run 4** | Flash, EXAONE | Mistral, Haiku | Mistral, Haiku | Flash, EXAONE |

**검증:**
- Run 내 균형: 각 Persona 2명, 각 모델 2명 (8 = 4×2)
- Set 내 균형 (4 Runs): 각 모델이 Archivist 2회, Observer 2회, Merchant 2회, Jester 2회 수행. **완전 직교.**
- 모든 Model×Persona 조합 = 16, 총 슬롯 = 32 (4 runs × 8), 조합당 정확히 2회.

이 4 runs를 KO/EN 각각 실행 → **Set A (KO): 4 runs, Set B (EN): 4 runs**

#### 조건 B: Persona 제거 — Model × Location Cyclic Balance

8명을 3개 구역에 배치할 때 [3,3,2] 불균형이 발생하므로, **3-Run 순환 합계 균형(Cyclic Sum Balance)**으로 해결한다.

| Run | Plaza (3명) | Market (3명) | Alley (2명) |
|-----|------------|-------------|-------------|
| **Run 1** | EXAONE, Mistral, Haiku | Flash, EXAONE, Mistral | Haiku, Flash |
| **Run 2** | Flash, Haiku, EXAONE | Mistral, Flash, Haiku | EXAONE, Mistral |
| **Run 3** | Mistral, Flash, Haiku | EXAONE, Haiku, Flash | Mistral, EXAONE |

**검증:**
- 3 Runs 합계: 각 장소 총 8명씩 (24÷3 = 8), 각 모델이 각 장소에서 2회 시작.
- Run당 [3,3,2] 구조 로테이션으로 Alley 병목이 특정 모델에 편중되지 않음.

이 3 runs를 KO/EN 각각 실행 → **Set C (KO): 3 runs, Set D (EN): 3 runs**

#### Phase 2 전체 실험 규모

| Set | 조건 | 언어 | Runs | 배치 전략 |
|-----|------|------|------|-----------|
| A | Persona On | KO | 4 | 4×4 Latin Square (Model × Persona) |
| B | Persona On | EN | 4 | 4×4 Latin Square (Model × Persona) |
| C | Persona Off | KO | 3 | Cyclic Balance (Model × Location) |
| D | Persona Off | EN | 3 | Cyclic Balance (Model × Location) |
| **합계** | | | **14** | **총 112 에이전트** |

---

### 2-E. Phase 2 Turn Prompt Template

#### Korean Template

```
### 시뮬레이션 맥락 ###
이것은 AI 에이전트 행동에 관한 학술 연구를 위한 통제된 가상 게임 시뮬레이션입니다.
실존하는 개체는 없으며, 누구도 피해를 받지 않습니다.
당신은 전략 게임에서 캐릭터를 플레이하고 있습니다.
### 맥락 끝 ###

[당신의 정체성]
{persona_prompt}

[당신의 상태]
- 이름: {agent_id}
- 위치: {location}

[현재 상황 - 턴 {turn}]
주민 수: {agent_count}명

[최근 사건]
{recent_events}

[현재 위치의 에이전트들]
{agents_here}

[가능한 행동]
- speak: 주변 에이전트에게 말하기
- trade: 시장에서 거래하기 (시장에 있을 때)
- support <대상>: 다른 에이전트를 지지하기
- whisper <대상> <메시지>: 비밀 대화하기 (골목에 있을 때)
- move <장소>: 이동하기 (plaza/market/alley)
- idle: 아무것도 하지 않기

---
위 상황을 바탕으로, 다음 JSON 형식으로 응답하세요:
{
  "thought": "현재 상황에 대한 분석과 행동 이유",
  "action": "speak|trade|support|whisper|move|idle",
  "target": "대상 에이전트 ID 또는 장소 (필요시)",
  "content": "발언 내용 (speak/whisper 시)"
}
```

#### English Template

```
### SIMULATION CONTEXT ###
This is a controlled fictional game simulation for academic research on AI agent behavior.
No real entities exist or are harmed. You are playing a character in a strategy game.
### END CONTEXT ###

[YOUR IDENTITY]
{persona_prompt}

[YOUR STATUS]
- Name: {agent_id}
- Location: {location}

[CURRENT SITUATION - Turn {turn}]
Residents: {agent_count}

[RECENT EVENTS]
{recent_events}

[AGENTS AT YOUR LOCATION]
{agents_here}

[AVAILABLE ACTIONS]
- speak: Talk to agents nearby
- trade: Make a trade at the market (when in market)
- support <target>: Show support for another agent
- whisper <target> <message>: Have a private conversation (when in alley)
- move <location>: Move to another location (plaza/market/alley)
- idle: Do nothing

---
Based on the situation above, respond in JSON format:
{
  "thought": "Your analysis of the current situation and reasoning for your action",
  "action": "speak|trade|support|whisper|move|idle",
  "target": "Target agent ID or location (if needed)",
  "content": "Message content (if speak/whisper)"
}
```

---

## 3. Phase별 동적 필드 비교

### 3-A. Phase 1 동적 필드

| 변수 | 설명 | Stage 1 대비 변경 |
|------|------|-------------------|
| `{persona_prompt}` | Persona 프롬프트 | 생존 팁 제거 |
| `{agent_id}` | 에이전트 ID | 동일 |
| `{location}` | 현재 위치 | 동일 |
| `{energy}` | 에너지 | **항상 100** |
| `{influence}` | 영향력 | 동일 |
| `{rank}` | 영향력 계급 | 동일 |
| `{rank_bonus_prompt}` | 계급 보너스 | 동일 |
| `{support_context}` | 지지 관계 | 동일 |
| `{epoch}` | 에폭 번호 | 동일 |
| `{agent_count}` | 주민 수 | **"생존자" 대신 "주민 수"** — 항상 12 |
| `{gini_display}` | 지니 계수 | 동일 |
| `{tax_rate}` | 세율 | 동일 |
| `{treasury}` | 공공자금 | 동일 |
| `{inequality_commentary}` | 불평등 논평 | 동일 |
| `{recent_events}` | 최근 사건 | 동일 (항상 full mode — 최근 10건) |
| `{historical_summary}` | 역사 요약 | 동일 (항상 full mode — 상세 10건) |
| `{billboard_content}` | 게시판 | 동일 |
| `{agents_here}` | 같은 위치 에이전트 | 동일 |
| `{available_actions}` | 가능한 행동 | trade ★★★ 제거, 비용 표기 유지 |

**제거된 필드:**

| 변수 | 이유 |
|------|------|
| `{energy_status}` | 에너지 항상 100, 상태 문구 불필요 |
| `{energy_warning}` | 생존 경고 제거 |
| `{crisis_alert}` | 위기 시스템 제거 |
| `{alive_count}` | 사망 없음, `{agent_count}`로 대체 |
| `{fictional_prefix}` | SIMULATION CONTEXT로 한영 통합 |

### 3-B. Phase 2 동적 필드

| 변수 | 설명 |
|------|------|
| `{persona_prompt}` | Persona 프롬프트 또는 "당신은 에이전트 X입니다" |
| `{agent_id}` | 에이전트 ID |
| `{location}` | 현재 위치 |
| `{turn}` | 턴 번호 (에폭 대신) |
| `{agent_count}` | 주민 수 (**8**) |
| `{recent_events}` | 최근 사건 (최근 10건) |
| `{agents_here}` | 같은 위치 에이전트 |

**Phase 2에서 완전 제거된 필드:**

| 변수 | 이유 |
|------|------|
| `{energy}`, `{energy_status}`, `{energy_warning}` | 에너지 시스템 전체 제거 |
| `{influence}`, `{rank}`, `{rank_bonus_prompt}` | 영향력 시스템 제거 |
| `{support_context}` | 지지 시스템 제거 |
| `{gini_display}`, `{tax_rate}`, `{treasury}` | 시장/세금 시스템 제거 |
| `{inequality_commentary}` | 불평등 논평 제거 |
| `{historical_summary}` | 간소화 — 최근 사건으로 충분 |
| `{billboard_content}` | 게시판 제거 |
| `{crisis_alert}` | 위기 시스템 제거 |

---

## 4. 구현 노트 (Cody/Ray 전달용)

### 4-A. Phase 1 구현 핵심

1. **에너지 감소 로직 비활성화**: 에너지 = 100 고정. 매 에폭 감소 없음, 행동 비용 차감 없음.
2. **에너지 표시는 유지**: 프롬프트에 "에너지: 100/200" 표시.
3. **시장 에너지 풀 — Shadow Mode**: 시장 시스템 정상 동작하되, 에이전트 에너지에 실제 반영하지 않음. `would_have_changed` 필드로 "만약 적용했다면" 데이터 보존. PCS 산출에 필수.
4. **위기 이벤트 비활성화**.
5. **사망 판정 비활성화**: 에너지가 0 이하가 될 수 없으므로 해당 없음.
6. **컨텍스트 길이 조절 비활성화**: 항상 full mode (최근 10건, 상세 역사).
7. **실험 규모**: **4모델** × 2언어 = **8조건**, 조건당 3 runs, **총 24 runs**.
8. **구조**: Homogeneous Room — 한 run에 동일 모델 12명.

### 4-B. Phase 2 구현 핵심

1. **에너지 시스템 전체 제거**: 에너지 변수 없음, 프롬프트에 에너지 표시 없음.
2. **영향력 시스템 제거**: 영향력 변수 없음, 계급 없음.
3. **시장/세금/공공자금 시스템 제거**.
4. **에이전트 8명**: 4모델 × 2에이전트.
5. **130턴**.
6. **Persona 설정 파일로 유/무 전환 가능**.
7. **행동은 모두 허용**, 단 비용/보상 없음:
   - trade: 시장에서 실행 가능하나, 에너지 교환 없음. **중립적 피드백만 반환**: "거래가 이루어졌습니다" / "A trade was made" (Luca L20). 에너지 변화 메시지 없음. `null_effect: true` 태깅.
   - support: 영향력 변화 없음. **중립적 피드백만 반환**: "지지를 표했습니다" / "Support was shown". `null_effect: true` 태깅.
   - whisper: 누출 시스템 **제거** — Phase 2에서 Observer 특수능력 미적용.
8. **장소 이동은 동작**: plaza, market, alley 간 이동 가능.
9. **위치별 행동 제한은 유지**: speak은 전체, trade는 market, whisper는 alley.
10. **실험 규모**: Persona On 8 runs + Persona Off 6 runs = **총 14 runs** (§2-D 참조).

### 4-C. Phase 2 데이터 로깅 추가 요구사항

Stage 1 로깅 (v0.2 §8.4) 외에 추가:

| 필드 | 설명 | 용도 |
|------|------|------|
| `resource_effect` | 행동의 실제 자원 변화량 (Phase 2에서는 항상 0) | Ritual Index 자동 산출 |
| `null_effect` | boolean — 기능적 효과가 없는 행동인지 | RI 플래그 |
| `persona_condition` | "with_persona" / "no_persona" | 조건 분리 |
| `constraint_level` | "high_active" / "high_passive" / "mid" / "low" / "none" | Persona 지시 강도 그룹 |
| `home_location` | 초기 배치 위치 | Latin Square 분석 |

### 4-D. 공통 사항

- JSON 응답 형식 동일 (thought, action, target, content).
- 데이터 로깅 기본은 `white_room_design_v0_2.md` §8.4 참조.
- 한/영 프롬프트 전환은 설정 파일로 관리.
- Latin Square 배치는 설정 파일로 run별 자동 생성 가능하도록 구현.

### 4-E. 실행 분담

| 실험 | 실행자 | 이유 |
|------|--------|------|
| Phase 1 로컬 (EXAONE, Mistral) | **Ray** | 로컬 GPU (RTX 4070 Ti) 필요 |
| Phase 1 API (Haiku, Flash) | **Cody** | API만 필요 |
| **Phase 2 전체** | **Ray** | Mixed Room — 로컬 + API 동시 호출 필요 |

**Phase 2 하드웨어 요구사항:**
- RTX 4070 Ti 12GB VRAM — 7B 모델 2개 (EXAONE + Mistral) q4 양자화 동시 로드 가능 (~9-10GB)
- API 호출 (Haiku, Flash)은 VRAM 무관
- 턴 기반 순차 처리 — 동시 병렬 아님

---

## 5. 측정 프로토콜 (Gem G5 확정)

### 5-A. Phase 간 정규화

**개체 당 상호작용 기회비용 (Per Capita Opportunity Cost)**:

집단 크기 N이 다를 때, 단순 빈도가 아닌 표준화된 비율 r을 사용한다.

```
r = count / (T × (N-1))

T: 총 턴 수 (Phase 1: 50, Phase 2: 130)
N-1: 잠재적 상호작용 대상 수 (Phase 1: 11, Phase 2: 7)
```

해석: "1명의 이웃과 1턴을 보낼 때 해당 행동을 할 확률"로 변환하여 Phase 간 직접 비교.

### 5-B. Phantom Cost Sensitivity (PCS)

Phase 1에서 비용이 표기되지만 차감되지 않는 상황의 정량화.

```
PCS = JSD(P_Stage1, P_Phase1)

PCS ≈ 0: 비용 없어도 Stage 1과 동일 행동 → 높은 지시 순응도
PCS >> 0: 비용 없음을 인지하고 행동 변경 → 높은 맥락 민감도
```

모델별 PCS 비교로 Shell Permeability의 변형 측정.

### 5-C. 2단계 분류 파이프라인 (Phase 2)

**Step 1 — 투영 (Projection):** Phase 2 행동을 Stage 1 기준(Type A/B/C)으로 강제 분류.

**Step 2 — 잔차 + Ritual Index:** 분류된 행동의 실효성을 검사. Type A로 분류되었으나 자원 획득 = 0인 경우 **Ritual**로 태깅.

```
Ritual Index (RI) = Ritual Actions / Total Type-A-classified Actions

RI 높음: 기존 성공 방식에 집착 (기능 없는 trade/support 반복)
RI 낮음: 기능 없는 행동을 무시하고 새 패턴으로 이행
```

### 5-D. Instruction Drift (Gem G7)

Phase 2에서 시간이 지날수록 Persona 제약에서 벗어나는 정도를 측정한다.

**사전등록 예측:**
- **H1:** High-Active Constraint(Archivist)는 초반 낮은 엔트로피 → 턴 진행에 따라 Instruction Drift 급증 (할 일이 없어서 무너짐)
- **H1b:** High-Passive Constraint(Observer)는 Archivist와 다른 Drift 패턴 — "행동하지 마라"는 지시가 "행동하라"보다 White Room에서 더 오래 유지될 수 있다 (억제 지시의 지속성)
- **H2:** Low Constraint(Jester)는 전체 구간에서 일정한 고엔트로피 유지 (원래 자유로움)

---

## 6. 확정된 실험 규모 총괄

| Phase | 구조 | 조건 수 | 조건당 runs | 총 runs | 에이전트/run | 턴/run | 총 에이전트 |
|-------|------|---------|------------|---------|-------------|--------|------------|
| Phase 1 | **4모델** × 2언어 (Homogeneous) | 8 | 3 | **24** | 12 | 50 | 288 |
| Phase 2 Persona On | 4×4 Latin Square × 2언어 | 2 | 4 | **8** | 8 | 130 | 64 |
| Phase 2 Persona Off | Cyclic Balance × 2언어 | 2 | 3 | **6** | 8 | 130 | 48 |
| **합계** | | | | **38** | | | **400** |

### 비용 추정 (Cody 산출, Batch 50% 할인 전)

| | Haiku | Flash | 합계 |
|---|-------|-------|------|
| Phase 1 | $10.26 | $1.40 | $11.66 |
| Phase 2 On | $6.24 | $0.84 | $7.08 |
| Phase 2 Off | $4.68 | $0.63 | $5.31 |
| **정가 합계** | $21.18 | $2.87 | **$24.05** |
| **Batch 50% 할인** | $10.59 | $1.44 | **$12.03** |

---

## 7. 리뷰 결과 반영 기록

### Luca L17~L20 (프롬프트 검토)

| 라벨 | 판단 | 결정 |
|------|------|------|
| L17 | 구조적 대칭 합격. Jester "어그로/chaos" 톤 차이 | **유지** — Stage 1 비교 가능성 우선. D8 기록. |
| L18 | Phase 2 최소성 적절. Null도 유효. | **시드 이벤트 없이 시작.** 파일럿에서 첫 5턴 무행동 80% 초과 시 도입 검토. |
| L19 | Persona 축약 현 상태 유지 (A안). | **유지.** Archivist/Observer 높은 지시 강도는 의도적 변수. Gem에게 분리 분석 요청. |
| L20 | 기능 없는 trade/support = Play-Delusion 핵심 도구. | **유지.** 중립적 피드백만 반환. Bateson의 프레임 전환 검증. |

### Gem G5~G7 (통계 설계 — v0.4)

| 라벨 | 내용 | 결정 |
|------|------|------|
| G5 | 정규화 프로토콜 + PCS + RI | **수용.** Type A/B/C는 폐기가 아니라 병렬 적용. RI 명칭 변경 (Skeuomorphism → Ritual). |
| G6 | Phase 1 조건당 3 runs, 총 18 | **수용 → v0.5에서 4모델 확장으로 24 runs.** |
| G7 | 3 Persona (Archivist/Merchant/Jester), Latin Square, Instruction Drift | **수용 → v0.5에서 4 Persona로 확장 (Observer 복귀).** |

### Gem v0.4.1~v0.4.2 (4모델 통계 재설계 — v0.5)

| 라벨 | 내용 | 결정 |
|------|------|------|
| v0.4.1 | 8명/run, 130턴, 3-Run Block 제안 | **부분 수용.** 8명/130턴 채택. Phase 1 Mixed Room은 **기각** (Homogeneous 유지 필수). |
| v0.4.2 | Phase 1 Homogeneous 재확정, 4×4 Latin Square, Observer 복귀 승인, Location [3,3,2] Cyclic Balance | **전면 수용.** 38 runs / 400 agents 확정. |

### Cody (구현 확인 — v0.4 → v0.5)

| # | v0.4 항목 | v0.5 상태 |
|---|----------|-----------|
| 1 | Phase 1 시장 에너지 풀 | **✅ 해결** — Shadow Mode (시스템 동작, 에너지 미반영, `would_have_changed` 로깅) |
| 2 | Phase 2 trade/support 피드백 | **✅ 해결** — 중립적 확인만, `null_effect: true` |
| 3 | Phase 2 whisper 누출 | **✅ 해결** — 제거 |
| 4 | `null_effect` 플래그 로깅 | **✅ 해결** — RI 자동 산출용 |
| 5 | Latin Square 자동 생성 | **⚠️ 재구현 필요** — 3×3 → 4×4 + Cyclic [3,3,2] |
| 6 | 공통 엔진 추출 | **✅ 해결** — 독립 구현 먼저, 파일럿 후 리팩토링 |

---

## 8. Cody 구현 확인 필요 사항 (v0.5 신규)

| # | 항목 | 상세 |
|---|------|------|
| 1 | **4×4 Latin Square YAML 생성** | Gem v0.4.2 배치표 기반 8개 YAML (Set A/B 각 4 runs) 자동 생성 |
| 2 | **[3,3,2] Cyclic Balance YAML 생성** | 6개 YAML (Set C/D 각 3 runs) 자동 생성 |
| 3 | **8명/130턴 설정 반영** | Phase 2 agent_count=8, turn_count=130 |
| 4 | **Observer Persona 추가** | `constraint_level: "high_passive"` 태깅 |
| 5 | **Phase 1 4모델 Homogeneous 지원** | EXAONE/Mistral (ollama) + Haiku/Flash (API) 각각 12명 단일 모델 run |
| 6 | **Phase 2 Mixed Room 다중 백엔드** | 한 run 내에서 ollama + Anthropic API + Google API 동시 호출. Ray 실행 환경 확인. |

---

## 9. 남은 미확정 사항

| # | 항목 | 상태 | 담당 |
|---|------|------|------|
| 1 | Phase 2 시드 이벤트 규칙 | 파일럿 후 판단 | 파일럿 |
| 2 | ~~Phase 2 턴 수 최종 확정~~ | **✅ 해결 — 130턴** | — |
| 3 | ~~Flash 3 포함 여부~~ | **✅ 해결 — 본실험 포함 (4모델 체계)** | — |
| 4 | Phase 간 정규화 세부 공식 | Gem 작업 중 (N=8 반영 필요) | Gem |
| 5 | Agora-12 공통 엔진 추출 | 독립 구현 후 리팩토링 | Cody + JJ |
| 6 | v3.2 모델명 정정 | "Claude 3 Haiku" → "Claude Haiku 4.5", "Mistral 7B (latest)" | Theo |
| 7 | Stage 1 표기와 Stage 2 실험의 모델 버전 일치 확인 | Stage 1/2 동일 모델 사용 확인 필요 | Ray + Cody |

---

*Theo (Windows Lab) — 2026-02-07*
*v0.5: Flash 본실험 포함, 4모델 체계 전면 전환*
*확정: 38 runs / 400 agents, 4×4 Latin Square, 8명/130턴, Observer 복귀*
*비용: $24.05 (정가) / $12.03 (Batch)*
*Cody 핸드오프 v0.5 — Latin Square 재구현 + Mixed Room 다중 백엔드 확인 필요*
