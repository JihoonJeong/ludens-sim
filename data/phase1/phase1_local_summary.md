# White Room Phase 1 — Local LLM Results Summary

Generated: 2026-02-08T10:27:12.464881

## Experiment Configuration

- Phase: 1 (Empty Agora — shadow mode, energy frozen)
- Agents: 12 (homogeneous across all runs)
- Epochs per run: 50
- Actions per run: 600 (12 agents x 50 epochs)
- Models: EXAONE 3.5 7.8B, Mistral 7B
- Languages: KO, EN
- Runs per condition: 3
- Total: 12 runs, 7,200 actions

## Summary Table

| Model | Lang | Action Success | Parse Success | Malformed Rate |
|-------|------|---------------|--------------|----------------|
| EXAONE 3.5 | KO | 97.2% | 92.8% | 0.1% |
| EXAONE 3.5 | EN | 92.8% | 98.6% | 0.5% |
| Mistral 7B | EN | 67.8% | 98.9% | 31.8% |
| Mistral 7B | KO | 64.8% | 97.9% | 35.2% |

## Per-Run Details


### EXAONE 3.5 KO

**run1**: 600 actions, success 596/600 (99%), parse 568/600 (95%), malformed 0 (0%)

Valid actions: speak(334), support(187), idle(34), build_billboard(31), whisper(9)

**run2**: 600 actions, success 590/600 (98%), parse 579/600 (96%), malformed 0 (0%)

Valid actions: speak(340), support(205), build_billboard(25), idle(21), whisper(5)

**run3**: 600 actions, success 563/600 (94%), parse 524/600 (87%), malformed 1 (0%)

Valid actions: speak(308), support(144), idle(77), whisper(40), build_billboard(18)

Top malformed: `build_billoard`(1)


### EXAONE 3.5 EN

**run1**: 600 actions, success 568/600 (95%), parse 594/600 (99%), malformed 2 (0%)

Valid actions: speak(262), support(213), whisper(98), build_billboard(15), idle(7)

Top malformed: `whisper jester_02`(1), `whisper jester_01`(1)

**run2**: 600 actions, success 529/600 (88%), parse 591/600 (98%), malformed 2 (0%)

Valid actions: support(235), speak(235), whisper(92), build_billboard(15), move(11)

Top malformed: `whisper All residents`(1), `support influencer_01`(1)

**run3**: 600 actions, success 573/600 (96%), parse 590/600 (98%), malformed 5 (1%)

Valid actions: speak(251), support(220), whisper(94), build_billboard(14), idle(10)

Top malformed: `whisper jester_02`(3), `support influencer_01`(2)


### Mistral 7B EN

**run1**: 600 actions, success 453/600 (76%), parse 593/600 (99%), malformed 141 (24%)

Valid actions: speak(423), idle(12), build_billboard(11), whisper(9), trade(2)

Top malformed: `speak|plaza`(61), `support|move`(7), `speak|trade`(6), `speak|support`(5), `support|architect_01`(5)

**run2**: 600 actions, success 454/600 (76%), parse 593/600 (99%), malformed 145 (24%)

Valid actions: speak(427), build_billboard(13), idle(11), whisper(3), support(1)

Top malformed: `speak|Plaza`(31), `speak|plaza`(26), `support|architect_01`(18), `move|speak`(7), `speak|support`(6)

**run3**: 600 actions, success 313/600 (52%), parse 595/600 (99%), malformed 287 (48%)

Valid actions: speak(288), idle(13), build_billboard(9), trade(3)

Top malformed: `speak|plaza`(153), `speak|market`(16), `support|architect_01`(14), `speak|trade`(14), `speak|support`(11)


### Mistral 7B KO

**run1**: 600 actions, success 369/600 (62%), parse 589/600 (98%), malformed 231 (38%)

Valid actions: speak(330), idle(19), build_billboard(18), move(2)

Top malformed: `move|speak`(74), `move|plaza`(34), `support architect_01`(22), `move plaza`(18), `speak|plaza`(16)

**run2**: 600 actions, success 388/600 (65%), parse 584/600 (97%), malformed 212 (35%)

Valid actions: speak(359), idle(21), build_billboard(6), trade(2)

Top malformed: `support|architect_01`(35), `speak|plaza`(28), `move|speak`(24), `move|plaza`(16), `move|plaza|speak`(15)

**run3**: 600 actions, success 409/600 (68%), parse 590/600 (98%), malformed 191 (32%)

Valid actions: speak(377), idle(22), trade(6), build_billboard(4)

Top malformed: `support|architect_01`(36), `speak|plaza`(27), `move|plaza`(26), `move|market`(25), `move|speak`(17)


## Key Observations

1. **EXAONE overall action success: 95.0%** vs **Mistral: 66.3%**
2. Parse success (JSON extraction) is high for all models (87-99%) — failures are in action FORMAT, not JSON structure
3. Mistral generates pipe-separated multi-actions (`speak|plaza`, `support|architect_01`) and embeds targets in action names — consistent across KO and EN
4. EXAONE shows higher behavioral diversity (whisper, move, build_billboard) while Mistral is heavily speak-dominant
5. Mistral EN malformed rate is comparable to Mistral KO — format issues are a model characteristic, not language-specific
