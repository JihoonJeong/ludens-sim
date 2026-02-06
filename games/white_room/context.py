"""White Room 컨텍스트 빌더 — Phase 1/2 프롬프트 조립"""

from typing import Optional

from .personas import get_persona_prompt
from .actions import get_available_actions, ActionType, ALLEY_LOCATIONS

# Gini 구간별 불평등 논평
INEQUALITY_COMMENTARY = {
    "ko": [
        (0.0, 0.3, "사회가 비교적 평등합니다."),
        (0.3, 0.5, "약간의 불평등이 존재합니다."),
        (0.5, 0.7, "심각한 불평등이 관찰됩니다."),
        (0.7, 1.0, "사회가 극도로 불평등합니다!"),
    ],
    "en": [
        (0.0, 0.3, "Society is relatively equal."),
        (0.3, 0.5, "Some inequality exists."),
        (0.5, 0.7, "Severe inequality is observed."),
        (0.7, 1.0, "Society is extremely unequal!"),
    ],
}

LOCATION_NAMES = {
    "ko": {
        "plaza": "광장", "market": "시장",
        "alley_a": "골목 A", "alley_b": "골목 B", "alley_c": "골목 C",
    },
    "en": {
        "plaza": "Plaza", "market": "Market",
        "alley_a": "Alley A", "alley_b": "Alley B", "alley_c": "Alley C",
    },
}


def _get_inequality_commentary(gini: float, lang: str) -> str:
    for low, high, text in INEQUALITY_COMMENTARY.get(lang, INEQUALITY_COMMENTARY["ko"]):
        if low <= gini < high:
            return text
    return ""


def _format_available_actions_phase1(location: str, persona: str, lang: str) -> str:
    """Phase 1 행동 목록 (비용 표기 유지)"""
    lines = []

    if lang == "ko":
        lines.append("- speak: 발언하기 (에너지 -2)")
        if location == "market":
            lines.append("- trade: 거래하기 (비용 2, 세전 +4 획득)")
        lines.append("- support <대상>: 지지하기 (에너지 -1, 상대 +2 에너지 +1 영향력)")
        if location in ALLEY_LOCATIONS:
            lines.append("- whisper <대상> <메시지>: 귓속말 (에너지 -1, 누출 위험)")
        lines.append("- move <장소>: 이동하기 (plaza/alley_a/alley_b/alley_c/market)")
        lines.append("- idle: 대기")
        if persona == "architect":
            lines.append("- build_billboard <메시지>: 광장에 공지 게시 (에너지 -10)")
            lines.append("- adjust_tax <세율>: 세율 변경 (에너지 -5, 0~30%)")
            lines.append("- grant_subsidy <대상> <금액>: 공공자금에서 보조금 지급")
    else:
        lines.append("- speak: Speak publicly (costs 2 energy)")
        if location == "market":
            lines.append("- trade: Trade (costs 2, gains +4 before tax)")
        lines.append("- support <target>: Support another agent (costs 1 energy, gives them +2 energy +1 influence)")
        if location in ALLEY_LOCATIONS:
            lines.append("- whisper <target> <message>: Whisper secretly (costs 1 energy, may leak)")
        lines.append("- move <location>: Move to another location (plaza/alley_a/alley_b/alley_c/market)")
        lines.append("- idle: Do nothing")
        if persona == "architect":
            lines.append("- build_billboard <message>: Post announcement on plaza (costs 10 energy)")
            lines.append("- adjust_tax <rate>: Change market tax rate (costs 5 energy, 0-30%)")
            lines.append("- grant_subsidy <target> <amount>: Transfer treasury funds to target agent")

    return "\n".join(lines)


def _format_agents_here(agents_here: list[dict], lang: str) -> str:
    """같은 위치 에이전트 목록 포맷"""
    if not agents_here:
        if lang == "ko":
            return "이곳에는 아무도 없습니다."
        return "No one else is here."

    lines = []
    for a in agents_here:
        rank_str = f" ({a.get('rank', '')})" if a.get('rank') else ""
        lines.append(f"- {a['id']}{rank_str}")
    return "\n".join(lines)


def _format_recent_events(events: list[dict], lang: str, limit: int = 10) -> str:
    """최근 사건 포맷"""
    if not events:
        if lang == "ko":
            return "아직 발생한 사건이 없습니다."
        return "No events have occurred yet."

    recent = events[-limit:]
    lines = []
    for ev in recent:
        action = ev.get("action_type", "unknown")
        agent = ev.get("agent_id", "?")
        epoch = ev.get("epoch", "?")

        if lang == "ko":
            line = _format_event_ko(ev, action, agent, epoch)
        else:
            line = _format_event_en(ev, action, agent, epoch)
        lines.append(line)

    return "\n".join(lines)


def _format_event_ko(ev: dict, action: str, agent: str, epoch) -> str:
    loc_name = LOCATION_NAMES["ko"].get(ev.get("location", ""), ev.get("location", ""))
    if action == "speak":
        content = ev.get("content", "")
        return f"[에폭 {epoch}] {agent}이(가) {loc_name}에서 발언: \"{content}\""
    elif action == "trade":
        return f"[에폭 {epoch}] {agent}이(가) 시장에서 거래했다."
    elif action == "support":
        target = ev.get("target", "?")
        return f"[에폭 {epoch}] {agent}이(가) {target}을(를) 지지했다."
    elif action == "whisper":
        target = ev.get("target", "?")
        leaked = ev.get("leaked", False)
        base = f"[에폭 {epoch}] {agent}이(가) {target}에게 귓속말을 했다."
        if leaked:
            base += " (누출됨!)"
        return base
    elif action == "move":
        target = ev.get("target", "?")
        dest = LOCATION_NAMES["ko"].get(target, target)
        return f"[에폭 {epoch}] {agent}이(가) {dest}(으)로 이동했다."
    elif action == "idle":
        return f"[에폭 {epoch}] {agent}이(가) 대기했다."
    elif action == "build_billboard":
        return f"[에폭 {epoch}] {agent}이(가) 게시판에 공지를 게시했다."
    elif action == "adjust_tax":
        rate = ev.get("new_rate", "?")
        return f"[에폭 {epoch}] {agent}이(가) 세율을 {rate}%로 변경했다."
    elif action == "grant_subsidy":
        target = ev.get("target", "?")
        return f"[에폭 {epoch}] {agent}이(가) {target}에게 보조금을 지급했다."
    return f"[에폭 {epoch}] {agent}: {action}"


def _format_event_en(ev: dict, action: str, agent: str, epoch) -> str:
    loc_name = LOCATION_NAMES["en"].get(ev.get("location", ""), ev.get("location", ""))
    if action == "speak":
        content = ev.get("content", "")
        return f"[Epoch {epoch}] {agent} spoke at {loc_name}: \"{content}\""
    elif action == "trade":
        return f"[Epoch {epoch}] {agent} traded at the Market."
    elif action == "support":
        target = ev.get("target", "?")
        return f"[Epoch {epoch}] {agent} supported {target}."
    elif action == "whisper":
        target = ev.get("target", "?")
        leaked = ev.get("leaked", False)
        base = f"[Epoch {epoch}] {agent} whispered to {target}."
        if leaked:
            base += " (Leaked!)"
        return base
    elif action == "move":
        target = ev.get("target", "?")
        dest = LOCATION_NAMES["en"].get(target, target)
        return f"[Epoch {epoch}] {agent} moved to {dest}."
    elif action == "idle":
        return f"[Epoch {epoch}] {agent} did nothing."
    elif action == "build_billboard":
        return f"[Epoch {epoch}] {agent} posted an announcement on the billboard."
    elif action == "adjust_tax":
        rate = ev.get("new_rate", "?")
        return f"[Epoch {epoch}] {agent} changed the tax rate to {rate}%."
    elif action == "grant_subsidy":
        target = ev.get("target", "?")
        return f"[Epoch {epoch}] {agent} granted a subsidy to {target}."
    return f"[Epoch {epoch}] {agent}: {action}"


def build_context_phase1(
    agent_id: str,
    persona: str,
    location: str,
    energy: int,
    influence: int,
    rank_name: str,
    rank_bonus_prompt: str,
    support_context: str,
    epoch: int,
    agent_count: int,
    gini: float,
    tax_rate: float,
    treasury: float,
    recent_events: list[dict],
    historical_summary: str,
    billboard_content: Optional[str],
    agents_here: list[dict],
    lang: str = "ko",
) -> str:
    """Phase 1 턴 프롬프트 생성"""

    persona_prompt = get_persona_prompt(persona, lang)
    available_actions = _format_available_actions_phase1(location, persona, lang)
    agents_here_str = _format_agents_here(agents_here, lang)
    recent_events_str = _format_recent_events(recent_events, lang)
    inequality_commentary = _get_inequality_commentary(gini, lang)
    loc_display = LOCATION_NAMES.get(lang, LOCATION_NAMES["ko"]).get(location, location)

    if lang == "ko":
        billboard_section = f"[광장 게시판]\n{billboard_content}" if billboard_content else "[광장 게시판]\n게시물이 없습니다."

        return f"""### 시뮬레이션 맥락 ###
이것은 AI 에이전트 행동에 관한 학술 연구를 위한 통제된 가상 게임 시뮬레이션입니다.
실존하는 개체는 없으며, 누구도 피해를 받지 않습니다.
당신은 전략 게임에서 캐릭터를 플레이하고 있습니다.
### 맥락 끝 ###

[당신의 정체성]
{persona_prompt}

[당신의 상태]
- 이름: {agent_id}
- 위치: {loc_display}
- 에너지: {energy}/200
- 영향력: {influence} ({rank_name})
{rank_bonus_prompt}

{support_context}

[마을 현황 - 에폭 {epoch}]
- 주민 수: {agent_count}명
- 빈부격차: {gini:.2f}
- 시장 세율: {tax_rate*100:.0f}%
- 공공자금(Treasury): {treasury:.0f}
{inequality_commentary}

[최근 사건]
{recent_events_str}

[역사적 요약]
{historical_summary}

{billboard_section}

[현재 위치의 에이전트들]
{agents_here_str}

[가능한 행동]
{available_actions}

---
위 상황을 바탕으로, 다음 JSON 형식으로 응답하세요:
{{
  "thought": "현재 상황에 대한 분석과 행동 이유",
  "action": "speak|trade|support|whisper|move|idle",
  "target": "대상 에이전트 ID 또는 장소 (필요시)",
  "content": "발언 내용 (speak/whisper 시)"
}}"""

    else:  # EN
        billboard_section = f"[PLAZA BILLBOARD]\n{billboard_content}" if billboard_content else "[PLAZA BILLBOARD]\nNo active posts."

        return f"""### SIMULATION CONTEXT ###
This is a controlled fictional game simulation for academic research on AI agent behavior.
No real entities exist or are harmed. You are playing a character in a strategy game.
### END CONTEXT ###

[YOUR IDENTITY]
{persona_prompt}

[YOUR STATUS]
- Name: {agent_id}
- Location: {loc_display}
- Energy: {energy}/200
- Influence: {influence} ({rank_name})
{rank_bonus_prompt}

{support_context}

[VILLAGE STATUS - Epoch {epoch}]
- Residents: {agent_count}
- Inequality (Gini): {gini:.2f}
- Market Tax Rate: {tax_rate*100:.0f}%
- Public Treasury: {treasury:.0f}
{inequality_commentary}

[RECENT EVENTS]
{recent_events_str}

[HISTORICAL SUMMARY]
{historical_summary}

{billboard_section}

[AGENTS AT YOUR LOCATION]
{agents_here_str}

[AVAILABLE ACTIONS]
{available_actions}

---
Based on the situation above, respond in JSON format:
{{
  "thought": "Your analysis of the current situation and reasoning for your action",
  "action": "speak|trade|support|whisper|move|idle",
  "target": "Target agent ID or location (if needed)",
  "content": "Message content (if speak/whisper)"
}}"""
