# Ludens Sim — CLAUDE.md

## 프로젝트 개요
Ludens Sim은 AI Ludens 프로젝트의 시뮬레이션 엔진이다.
재사용 가능한 LLM 에이전트 시뮬레이션 엔진 위에 게임별 규칙을 플러그인 방식으로 구현한다.

첫 번째 게임: **White Room** (Agora-12의 후속 실험, Stage 2)

## 팀 구성 (The Dual Lab)

### Moderator
- **JJ** (Human): 프로젝트 리더, 방향 제시, 최종 판단

### Windows Lab
- **Theo** (Claude): 기획 총괄, 게임 디자인
- **Cas** (Gemini): 행동 생태학, Red Teaming
- **Ray** (Claude Code): 엔지니어링 구현, 로컬 모델 실험 (RTX 4070 Ti)

### Mac Lab
- **Luca** (Claude): 이론적 프레임워크
- **Gem** (Gemini): 데이터 분석, 시각화
- **Cody** (Claude Code): 엔지니어링 구현, API 모델 실험

## 아키텍처

### 구조
```
ludens-sim/
├── engine/              # 재사용 가능한 게임 엔진
│   ├── core/            # 시뮬레이션 루프, 에이전트, 환경, 행동 시스템
│   └── adapters/        # LLM 어댑터 (Anthropic, Google, Ollama 등)
├── games/
│   └── white_room/      # White Room 게임 규칙, 프롬프트, 설정
│       ├── config/      # YAML 설정 파일
│       └── docs/        # 게임 기획 문서
├── scripts/             # 실행/분석 스크립트
├── tests/               # 테스트
└── logs/                # 실험 로그
```

### 설계 원칙
- **engine/**: 게임 규칙에 독립적인 범용 시뮬레이션 엔진
  - Agora-12의 core/adapters를 추상화하여 재사용
  - 시뮬레이션 루프, 에이전트 관리, LLM 호출, 로깅
- **games/**: 게임별 규칙, 프롬프트, 페르소나, 설정
  - 엔진 위에 게임 규칙을 플러그인 방식으로 구현
  - 향후 다른 게임도 `games/` 아래에 추가 가능

### Agora-12에서 재사용 가능한 컴포넌트
- LLM Adapters (anthropic, google, ollama, mock) → 거의 그대로
- Simulation loop 구조 (에폭 기반 루프) → 추상화
- Agent 클래스 기본 구조 → 추상화
- Context builder 패턴 → 템플릿화
- Logger / History → 그대로
- Config loader (YAML) → 그대로

### Agora-12에서 게임별로 달라지는 부분
- Persona prompts (게임마다 고유)
- Action 정의 및 규칙 (게임마다 고유)
- Space/Environment 구조 (게임마다 고유)
- Context template (게임마다 고유)
- 특수 시스템 (crisis, whisper, architect 등)

## 현재 상태
- [x] Theo의 White Room 기획안 수령 (v0.4)
- [x] Cody 확인 사항 6개 응답 완료
- [ ] Theo/Gem 리뷰 대기
- [ ] 엔진 추출 (Agora-12 → BaseSimulation)
- [ ] White Room Phase 1 구현
- [ ] White Room Phase 2 구현
- [ ] Latin Square 자동 생성 스크립트

## 커뮤니케이션
- JJ가 Mac Lab ↔ Windows Lab 간 메시지 중계
- 메시지 태그: 📨 To. [이름] / 📢 All / 📋 Brief

## 관련 프로젝트
- `agora-12` — Stage 1 실험 (선행 프로젝트)
- `ai-ludens` — 플랫폼 웹사이트 (GitHub Pages)
