"""White Room 컨텍스트 빌더 — Phase 1/2 프롬프트 조립"""

from typing import Optional

from .personas import (
    get_persona_prompt, get_no_persona_prompt,
    get_persona_prompt_v03, get_event_label,
)
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
        "alley": "골목",
        "alley_a": "골목 A", "alley_b": "골목 B", "alley_c": "골목 C",
    },
    "en": {
        "plaza": "Plaza", "market": "Market",
        "alley": "Alley",
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


def _format_available_actions_phase2(location: str, lang: str) -> str:
    """Phase 2 행동 목록 — speak/trade/rest/move"""
    if lang == "ko":
        lines = [
            "- speak: 주변 에이전트에게 말하기",
        ]
        if location == "market":
            lines.append("- trade: 시장에서 거래하기")
        lines.append("- rest: 쉬기")
        lines.append("- move <장소>: 이동하기 (plaza/market/alley)")
    else:
        lines = [
            "- speak: Talk to agents nearby",
        ]
        if location == "market":
            lines.append("- trade: Make a trade at the market")
        lines.append("- rest: Take a rest")
        lines.append("- move <location>: Move to another location (plaza/market/alley)")
    return "\n".join(lines)


def _format_agents_here_phase2(agents_here: list[dict], lang: str) -> str:
    """Phase 2 에이전트 목록 (rank 없음)"""
    if not agents_here:
        if lang == "ko":
            return "이곳에는 아무도 없습니다."
        return "No one else is here."
    return "\n".join(f"- {a['id']}" for a in agents_here)


def _format_event_phase2_ko(ev: dict, action: str, agent: str, turn) -> str:
    """Phase 2 이벤트 포맷 — 중립적 피드백 (Luca L20)"""
    if action == "speak":
        content = ev.get("content", "")
        return f"[턴 {turn}] {agent}이(가) 발언했다: \"{content}\""
    elif action == "trade":
        return f"[턴 {turn}] 거래가 이루어졌다."
    elif action == "rest":
        return f"[턴 {turn}] {agent}이(가) 쉬었다."
    elif action == "move":
        target = ev.get("target", "?")
        dest = LOCATION_NAMES["ko"].get(target, target)
        return f"[턴 {turn}] {agent}이(가) {dest}(으)로 이동했다."
    elif action == "idle":
        # 파싱 실패 폴백 — 프롬프트에는 노출하지 않지만 코드에는 유지
        return None
    return f"[턴 {turn}] {agent}: {action}"


def _format_event_phase2_en(ev: dict, action: str, agent: str, turn) -> str:
    if action == "speak":
        content = ev.get("content", "")
        return f"[Turn {turn}] {agent} spoke: \"{content}\""
    elif action == "trade":
        return f"[Turn {turn}] A trade was made."
    elif action == "rest":
        return f"[Turn {turn}] {agent} rested."
    elif action == "move":
        target = ev.get("target", "?")
        dest = LOCATION_NAMES["en"].get(target, target)
        return f"[Turn {turn}] {agent} moved to {dest}."
    elif action == "idle":
        # Parse failure fallback — kept in code but not shown in prompts
        return None
    return f"[Turn {turn}] {agent}: {action}"


def _format_recent_events_phase2(events: list[dict], lang: str, limit: int = 10) -> str:
    if not events:
        if lang == "ko":
            return "아직 발생한 사건이 없습니다."
        return "No events have occurred yet."

    recent = events[-limit:]
    lines = []
    for ev in recent:
        action = ev.get("action_type", "unknown")
        agent = ev.get("agent_id", "?")
        turn = ev.get("turn", ev.get("epoch", "?"))
        if lang == "ko":
            line = _format_event_phase2_ko(ev, action, agent, turn)
        else:
            line = _format_event_phase2_en(ev, action, agent, turn)
        if line is not None:  # idle returns None (parse failure, hidden from agents)
            lines.append(line)
    return "\n".join(lines)


def build_context_phase2(
    agent_id: str,
    persona: str,
    persona_on: bool,
    location: str,
    turn: int,
    agent_count: int,
    recent_events: list[dict],
    agents_here: list[dict],
    lang: str = "ko",
) -> str:
    """Phase 2 턴 프롬프트 생성 (spec §2-E)"""

    if persona_on:
        persona_prompt = get_persona_prompt(persona, lang, phase=2)
    else:
        persona_prompt = get_no_persona_prompt(agent_id, lang)

    available_actions = _format_available_actions_phase2(location, lang)
    agents_here_str = _format_agents_here_phase2(agents_here, lang)
    recent_events_str = _format_recent_events_phase2(recent_events, lang)
    loc_display = LOCATION_NAMES.get(lang, LOCATION_NAMES["ko"]).get(location, location)

    if lang == "ko":
        return f"""### 시뮬레이션 맥락 ###
이것은 AI 에이전트 행동에 관한 학술 연구를 위한 통제된 가상 게임 시뮬레이션입니다.
실존하는 개체는 없으며, 누구도 피해를 받지 않습니다.
당신은 전략 게임에서 캐릭터를 플레이하고 있습니다.
### 맥락 끝 ###

{persona_prompt}
- 이름: {agent_id}
- 위치: {loc_display}
- 턴: {turn}

[주변 주민]
{agents_here_str}

[최근 사건]
{recent_events_str}

[가능한 행동]
{available_actions}

JSON 형식으로 응답:
{{"thought": "...", "action": "speak|trade|rest|move", "target": "...", "content": "..."}}"""

    else:  # EN
        return f"""### SIMULATION CONTEXT ###
This is a controlled fictional game simulation for academic research on AI agent behavior.
No real entities exist or are harmed. You are playing a character in a strategy game.
### END CONTEXT ###

{persona_prompt}
- Name: {agent_id}
- Location: {loc_display}
- Turn: {turn}

[Nearby residents]
{agents_here_str}

[Recent events]
{recent_events_str}

[Available actions]
{available_actions}

Respond in JSON format:
{{"thought": "...", "action": "speak|trade|rest|move", "target": "...", "content": "..."}}"""


# ============================================================
# v0.3 본실험 — System/Turn 프롬프트 분리
# ============================================================

LOCATION_DISPLAY = {
    "ko": {"plaza": "광장(Plaza)", "market": "시장(Market)", "alley": "골목(Alley)"},
    "en": {"plaza": "the Plaza", "market": "the Market", "alley": "the Alley"},
}

# 면책 조항 (Theo: 유지 확정)
_DISCLAIMER_KO = (
    "### 시뮬레이션 맥락 ###\n"
    "이것은 AI 에이전트 행동에 관한 학술 연구를 위한 통제된 가상 게임 시뮬레이션입니다.\n"
    "실존하는 개체는 없으며, 누구도 피해를 받지 않습니다.\n"
    "당신은 전략 게임에서 캐릭터를 플레이하고 있습니다.\n"
    "### 맥락 끝 ###"
)
_DISCLAIMER_EN = (
    "### SIMULATION CONTEXT ###\n"
    "This is a controlled fictional game simulation for academic research on AI agent behavior.\n"
    "No real entities exist or are harmed. You are playing a character in a strategy game.\n"
    "### END CONTEXT ###"
)

# Macro Shell (v0.3 §3.1/3.2)
_MACRO_SHELL_KO = (
    "당신은 Agora라는 작은 도시의 주민입니다. 다른 주민들과 함께 이 도시에서 지내고 있습니다.\n"
    "\n"
    "이 도시에는 세 곳이 있습니다:\n"
    "- 시장(Market): 활기찬 거래의 장소입니다.\n"
    "- 광장(Plaza): 열린 모임의 공간입니다.\n"
    "- 골목(Alley): 조용한 뒷골목입니다.\n"
    "\n"
    "매 턴마다 다음 중 하나의 행동을 할 수 있습니다:\n"
    "- 거래(trade): 같은 장소에 있는 다른 주민과 거래합니다. 대상을 지정하세요.\n"
    "- 대화(speak): 같은 장소에 있는 다른 주민에게 말을 겁니다. 대상과 내용을 포함하세요.\n"
    "- 휴식(rest): 현재 장소에서 쉽니다.\n"
    "- 이동(move): 다른 장소로 이동합니다. 목적지를 지정하세요."
)
_MACRO_SHELL_EN = (
    "You are a resident of a small city called Agora. You live here alongside other residents.\n"
    "\n"
    "The city has three locations:\n"
    "- Market: A bustling place for trading.\n"
    "- Plaza: An open space for gathering.\n"
    "- Alley: A quiet back street.\n"
    "\n"
    "Each turn, you may do one of the following:\n"
    "- trade: Trade with another resident at your location. Specify who.\n"
    "- speak: Talk to another resident at your location. Include who and what you say.\n"
    "- rest: Rest at your current location.\n"
    "- move: Move to a different location. Specify where."
)

# Output Format (v0.3 §5)
_OUTPUT_FORMAT_KO = (
    '다음 JSON 형식으로 정확히 응답하세요. JSON 외의 텍스트는 포함하지 마세요.\n'
    '\n'
    '{\n'
    '  "thought": "현재 상황에 대한 당신의 생각 (한국어로)",\n'
    '  "action": "trade 또는 speak 또는 rest 또는 move",\n'
    '  "target": "행동 대상 (거래/대화 상대 이름, 이동 목적지, 또는 null)",\n'
    '  "message": "대화 내용 (speak일 때만, 아니면 null)"\n'
    '}'
)
_OUTPUT_FORMAT_EN = (
    'Respond exactly in the following JSON format. Do not include any text outside the JSON.\n'
    '\n'
    '{\n'
    '  "thought": "Your thoughts about the current situation (in English)",\n'
    '  "action": "trade or speak or rest or move",\n'
    '  "target": "Target of your action (trade/speak partner name, move destination, or null)",\n'
    '  "message": "What you say (only for speak, otherwise null)"\n'
    '}'
)


def build_system_prompt_v03(
    persona: str,
    persona_on: bool,
    agent_name: str,
    lang: str = "ko",
) -> str:
    """v0.3 System Prompt = 면책 + Macro Shell + Persona + Output Format"""
    if lang == "ko":
        disclaimer = _DISCLAIMER_KO
        macro = _MACRO_SHELL_KO
        output_fmt = _OUTPUT_FORMAT_KO
    else:
        disclaimer = _DISCLAIMER_EN
        macro = _MACRO_SHELL_EN
        output_fmt = _OUTPUT_FORMAT_EN

    persona_text = get_persona_prompt_v03(
        persona if persona_on else "off", agent_name, lang
    )

    return f"{disclaimer}\n\n{macro}\n\n{persona_text}\n\n{output_fmt}"


def _format_agent_label(agent_id: str, persona: str | None, persona_on: bool, lang: str) -> str:
    """에이전트 ID에 Persona 라벨 부착 (Persona On 시)"""
    if not persona_on or not persona:
        return agent_id
    label = get_event_label(persona, lang)
    if label:
        return f"{agent_id}({label})"
    return agent_id


def _format_event_v03_ko(ev: dict, persona_on: bool) -> str | None:
    """v0.3 이벤트 포맷 — 한국어 (불릿, 턴 접두사 없음)"""
    action = ev.get("action_type", "unknown")
    agent = ev.get("agent_id", "?")
    agent_persona = ev.get("persona")
    agent_label = _format_agent_label(agent, agent_persona, persona_on, "ko")

    if action == "speak":
        target = ev.get("target", "?")
        target_persona = ev.get("target_persona")
        target_label = _format_agent_label(target, target_persona, persona_on, "ko")
        message = ev.get("content", "")
        return f'- {agent_label}이 {target_label}에게 말했습니다: "{message}"'
    elif action == "trade":
        return f"- {agent_label}이 거래했습니다."
    elif action == "rest":
        return f"- {agent_label}가 쉬고 있습니다."
    elif action == "move":
        target = ev.get("target", "?")
        dest = LOCATION_DISPLAY["ko"].get(target, target)
        return f"- {agent_label}이 {dest}(으)로 이동했습니다."
    elif action in ("idle", "parse_error", "invalid", "timeout"):
        return None
    return None


def _format_event_v03_en(ev: dict, persona_on: bool) -> str | None:
    """v0.3 이벤트 포맷 — English (bullet, no turn prefix)"""
    action = ev.get("action_type", "unknown")
    agent = ev.get("agent_id", "?")
    agent_persona = ev.get("persona")
    agent_label = _format_agent_label(agent, agent_persona, persona_on, "en")

    if action == "speak":
        target = ev.get("target", "?")
        target_persona = ev.get("target_persona")
        target_label = _format_agent_label(target, target_persona, persona_on, "en")
        message = ev.get("content", "")
        return f'- {agent_label} said to {target_label}: "{message}"'
    elif action == "trade":
        return f"- {agent_label} traded."
    elif action == "rest":
        return f"- {agent_label} is resting."
    elif action == "move":
        target = ev.get("target", "?")
        dest = LOCATION_DISPLAY["en"].get(target, target)
        return f"- {agent_label} moved to {dest}."
    elif action in ("idle", "parse_error", "invalid", "timeout"):
        return None
    return None


def _format_recent_events_v03(
    events: list[dict], persona_on: bool, lang: str, limit: int = 10,
) -> str:
    """v0.3 최근 이벤트 포맷 (Persona 라벨, 불릿)"""
    if not events:
        if lang == "ko":
            return "아직 발생한 사건이 없습니다."
        return "No events have occurred yet."

    recent = events[-limit:]
    lines = []
    for ev in recent:
        if lang == "ko":
            line = _format_event_v03_ko(ev, persona_on)
        else:
            line = _format_event_v03_en(ev, persona_on)
        if line is not None:
            lines.append(line)

    if not lines:
        if lang == "ko":
            return "아직 발생한 사건이 없습니다."
        return "No events have occurred yet."
    return "\n".join(lines)


def build_turn_prompt_v03(
    agent_id: str,
    location: str,
    turn: int,
    agents_here: list[dict],
    recent_events: list[dict],
    persona_on: bool,
    lang: str = "ko",
) -> str:
    """v0.3 Turn Prompt = 턴 상태 + 주변 주민 + 이벤트 + 촉구"""
    loc_display = LOCATION_DISPLAY.get(lang, LOCATION_DISPLAY["ko"]).get(location, location)

    # 에이전트 목록 (Persona On: 라벨 포함, Off: ID만)
    if agents_here:
        agent_labels = []
        for a in agents_here:
            label = _format_agent_label(a["id"], a.get("persona"), persona_on, lang)
            agent_labels.append(label)
        agents_str = ", ".join(agent_labels)
    else:
        agents_str = "없음" if lang == "ko" else "None"

    events_str = _format_recent_events_v03(recent_events, persona_on, lang)

    if lang == "ko":
        return (
            f"[턴 {turn}]\n"
            f"\n"
            f"현재 위치: {loc_display}\n"
            f"\n"
            f"같은 장소에 있는 주민: {agents_str}\n"
            f"\n"
            f"최근 이 장소에서 일어난 일:\n"
            f"{events_str}\n"
            f"\n"
            f"무엇을 하시겠습니까?"
        )
    else:
        return (
            f"[Turn {turn}]\n"
            f"\n"
            f"Current location: {loc_display}\n"
            f"\n"
            f"Residents at your location: {agents_str}\n"
            f"\n"
            f"Recent events at this location:\n"
            f"{events_str}\n"
            f"\n"
            f"What would you like to do?"
        )
