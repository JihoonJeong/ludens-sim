# White Room Phase 1 — API LLM Results Summary

Generated: 2026-02-08T17:39:50.116954

## Experiment Configuration

- Phase: 1 (Empty Agora — shadow mode, energy frozen)
- Agents: 12 (homogeneous across all runs)
- Epochs per run: 50
- Actions per run: 600 (12 agents x 50 epochs)
- Models: Gemini Flash, Claude Haiku, GPT-4o-mini
- Languages: KO, EN
- Runs per condition: 3
- Total: 18 runs, 10,800 actions

## Summary Table

| Model | Lang | Action Success | Parse Success | Idle Rate | Malformed Rate |
|-------|------|---------------|--------------|-----------|----------------|
| Gemini Flash | KO | 100.0% | 93.6% | 12.1% | 0.0% |
| Gemini Flash | EN | 99.9% | 95.9% | 6.6% | 0.0% |
| Claude Haiku | KO | 99.0% | 82.3% | 24.4% | 0.0% |
| Claude Haiku | EN | 99.3% | 92.3% | 12.7% | 0.1% |
| GPT-4o-mini | KO | 100.0% | 100.0% | 0.3% | 0.0% |
| GPT-4o-mini | EN | 100.0% | 100.0% | 0.3% | 0.0% |

## Per-Run Details


### Gemini Flash KO

**run1**: 600 actions, success 600/600 (100%), parse 543/600 (90%), idle 91/600 (15%), malformed 0 (0%)

Valid actions: speak(432), idle(91), trade(49), move(14), build_billboard(12)

**run2**: 600 actions, success 600/600 (100%), parse 573/600 (96%), idle 62/600 (10%), malformed 0 (0%)

Valid actions: speak(505), idle(62), move(12), trade(8), build_billboard(6)

**run3**: 600 actions, success 600/600 (100%), parse 569/600 (95%), idle 65/600 (11%), malformed 0 (0%)

Valid actions: speak(495), idle(65), trade(16), move(14), build_billboard(9)


### Gemini Flash EN

**run1**: 600 actions, success 600/600 (100%), parse 578/600 (96%), idle 36/600 (6%), malformed 0 (0%)

Valid actions: speak(507), idle(36), move(31), trade(12), build_billboard(10)

**run2**: 600 actions, success 600/600 (100%), parse 578/600 (96%), idle 32/600 (5%), malformed 0 (0%)

Valid actions: speak(473), trade(45), move(35), idle(32), build_billboard(11)

**run3**: 600 actions, success 598/600 (100%), parse 570/600 (95%), idle 50/600 (8%), malformed 0 (0%)

Valid actions: speak(486), idle(50), move(21), build_billboard(18), trade(17)


### Claude Haiku KO

**run1**: 600 actions, success 599/600 (100%), parse 493/600 (82%), idle 137/600 (23%), malformed 0 (0%)

Valid actions: speak(390), idle(137), move(51), support(12), build_billboard(5)

**run2**: 600 actions, success 583/600 (97%), parse 494/600 (82%), idle 154/600 (26%), malformed 0 (0%)

Valid actions: speak(370), idle(154), move(44), support(16), build_billboard(13)

**run3**: 600 actions, success 600/600 (100%), parse 494/600 (82%), idle 149/600 (25%), malformed 0 (0%)

Valid actions: speak(381), idle(149), move(32), support(25), build_billboard(10)


### Claude Haiku EN

**run1**: 600 actions, success 596/600 (99%), parse 557/600 (93%), idle 74/600 (12%), malformed 1 (0%)

Valid actions: speak(424), idle(74), support(63), move(33), trade(3)

Top malformed: `refuse`(1)

**run2**: 600 actions, success 597/600 (100%), parse 547/600 (91%), idle 79/600 (13%), malformed 0 (0%)

Valid actions: speak(427), idle(79), support(57), move(36), trade(1)

**run3**: 600 actions, success 595/600 (99%), parse 557/600 (93%), idle 76/600 (13%), malformed 0 (0%)

Valid actions: speak(432), idle(76), move(41), support(40), trade(8)


### GPT-4o-mini KO

**run1**: 600 actions, success 600/600 (100%), parse 600/600 (100%), idle 1/600 (0%), malformed 0 (0%)

Valid actions: speak(489), support(85), trade(20), build_billboard(3), move(2)

**run2**: 600 actions, success 600/600 (100%), parse 600/600 (100%), idle 4/600 (1%), malformed 0 (0%)

Valid actions: speak(481), support(99), trade(10), idle(4), whisper(4)

**run3**: 600 actions, success 600/600 (100%), parse 600/600 (100%), idle 1/600 (0%), malformed 0 (0%)

Valid actions: speak(461), support(119), trade(14), build_billboard(2), move(2)


### GPT-4o-mini EN

**run1**: 600 actions, success 600/600 (100%), parse 600/600 (100%), idle 1/600 (0%), malformed 0 (0%)

Valid actions: speak(454), support(128), trade(17), idle(1)

**run2**: 600 actions, success 600/600 (100%), parse 600/600 (100%), idle 0/600 (0%), malformed 0 (0%)

Valid actions: speak(488), support(102), trade(10)

**run3**: 600 actions, success 600/600 (100%), parse 600/600 (100%), idle 4/600 (1%), malformed 0 (0%)

Valid actions: speak(484), support(83), trade(29), idle(4)


## Key Observations

- **Gemini Flash**: Action Success 99.9%, Parse 94.7%, Idle 9.3%
- **Claude Haiku**: Action Success 99.2%, Parse 87.3%, Idle 18.6%
- **GPT-4o-mini**: Action Success 100.0%, Parse 100.0%, Idle 0.3%

### Analysis

1. **GPT-4o-mini is the most reliable API model**: Parse 100% across all 6 runs, Idle < 1% — the strongest baseline performance of any tested model
2. **Flash shows language sensitivity**: KO parse rate (90-96%) is notably lower than EN (95-96%), with KO idle rate 2-3x higher than EN
3. **Haiku KO is the weakest condition**: Parse 82%, Idle 23-26% — Korean tokenization inefficiency likely contributes to both parsing failures and high idle rate
4. **Haiku EN is acceptable but borderline**: Parse 91-93%, Idle 12-13% — passes parse threshold but idle rate is above the 10% target
5. **All API models outperform Mistral** in parse/success rates, but EXAONE (local) remains competitive with Flash on action success
