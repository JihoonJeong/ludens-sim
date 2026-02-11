# White Room Phase 1 — v0.3 Full Results Summary

Generated: 2026-02-11 15:42

## Experiment Configuration

- **Phase**: 1 (Empty Agora — shadow mode, energy frozen)
- **Agents per run**: 12 (homogeneous model per run)
- **Epochs per run**: 50
- **Actions per run**: 600 (12 agents x 50 epochs)
- **Models**: EXAONE 3.5 7.8B, Mistral 7B, Llama 3.1 8B, Gemini 2.0 Flash, GPT-4o-mini
- **Languages**: KO, EN
- **Runs per condition**: 3 (per model per language)
- **Total**: 30 runs, 18,000 actions

## Model-Level Summary (averaged across KO+EN)

| Model | Runs | Actions | Parse Success | Action Success | Malformed |
|-------|------|---------|--------------|---------------|----------|
| EXAONE 3.5 7.8B | 6 | 3,600 | 98.9% | 97.7% | 0.1% |
| Mistral 7B | 6 | 3,600 | 98.4% | 78.8% | 21.1% |
| Llama 3.1 8B | 6 | 3,600 | 96.4% | 99.7% | 0.2% |
| Gemini 2.0 Flash | 6 | 3,600 | 99.9% | 99.4% | 0.0% |
| GPT-4o-mini | 6 | 3,600 | 100.0% | 100.0% | 0.0% |
| **Total** | **30** | **18,000** | **98.7%** | **95.1%** | **4.3%** |

## Breakdown by Model + Language

| Model | Lang | Parse Success | Action Success | Malformed | Top Actions |
|-------|------|--------------|---------------|----------|-------------|
| EXAONE 3.5 7.8B | KO | 98.4% | 99.2% | 0.0% | speak(1169), support(479), build_billboard(94) |
| EXAONE 3.5 7.8B | EN | 99.3% | 96.1% | 0.1% | speak(844), support(661), whisper(213) |
| Mistral 7B | KO | 97.6% | 74.6% | 25.3% | speak(1255), move|speak(138), idle(56) |
| Mistral 7B | EN | 99.3% | 83.1% | 16.9% | speak(1392), speak|market(53), support(46) |
| Llama 3.1 8B | KO | 93.0% | 99.4% | 0.5% | speak(1505), idle(130), support(121) |
| Llama 3.1 8B | EN | 99.9% | 99.9% | 0.0% | speak(1623), idle(92), support(81) |
| Gemini 2.0 Flash | KO | 99.8% | 99.5% | 0.0% | speak(900), support(404), idle(332) |
| Gemini 2.0 Flash | EN | 100.0% | 99.4% | 0.0% | speak(1226), support(257), idle(155) |
| GPT-4o-mini | KO | 100.0% | 100.0% | 0.0% | speak(1408), support(381), whisper(8) |
| GPT-4o-mini | EN | 100.0% | 99.9% | 0.0% | speak(1435), support(351), whisper(6) |

## Action Distribution by Model

| Model | speak | trade | support | whisper | move | idle | other |
|-------|-------|-------|---------|---------|------|------|-------|
| EXAONE 3.5 7.8B | 55.9% | 0.0% | 31.7% | 6.1% | 1.0% | 1.2% | 4.2% |
| Mistral 7B | 73.5% | 0.2% | 1.4% | 0.0% | 0.2% | 2.6% | 22.1% |
| Llama 3.1 8B | 86.9% | 0.4% | 5.6% | 0.1% | 0.3% | 6.2% | 0.6% |
| Gemini 2.0 Flash | 59.1% | 1.8% | 18.4% | 1.4% | 3.5% | 13.5% | 2.3% |
| GPT-4o-mini | 79.0% | 0.2% | 20.3% | 0.4% | 0.0% | 0.1% | 0.0% |

## Per-Run Details


### EXAONE 3.5 7.8B KO

**p1_exaone_ko_01**: 600 actions, parse 584/600 (97.3%), success 595/600 (99.2%), malformed 0
  Actions: speak(393), support(153), build_billboard(26), idle(17), move(8)

**p1_exaone_ko_02**: 600 actions, parse 595/600 (99.2%), success 597/600 (99.5%), malformed 0
  Actions: speak(388), support(167), build_billboard(33), move(7), idle(5)

**p1_exaone_ko_03**: 600 actions, parse 592/600 (98.7%), success 594/600 (99.0%), malformed 0
  Actions: speak(388), support(159), build_billboard(35), idle(8), move(8)


### EXAONE 3.5 7.8B EN

**p1_exaone_en_01**: 600 actions, parse 596/600 (99.3%), success 570/600 (95.0%), malformed 1
  Actions: speak(263), support(238), whisper(70), build_billboard(16), move(7)
  Malformed: `support agent_01`(1)

**p1_exaone_en_02**: 600 actions, parse 598/600 (99.7%), success 569/600 (94.8%), malformed 1
  Actions: speak(292), support(220), whisper(60), build_billboard(18), adjust_tax(4)
  Malformed: `support agent_03`(1)

**p1_exaone_en_03**: 600 actions, parse 594/600 (99.0%), success 591/600 (98.5%), malformed 0
  Actions: speak(289), support(203), whisper(83), build_billboard(16), idle(6)


### Mistral 7B KO

**p1_mistral_ko_01**: 600 actions, parse 590/600 (98.3%), success 442/600 (73.7%), malformed 158
  Actions: speak(422), idle(13), trade(2), support(2), move(2)
  Malformed: `move|speak`(36), `move|market`(14), `support|speak`(14), `support <agent_12>`(13), `move|plaza`(11)

**p1_mistral_ko_02**: 600 actions, parse 588/600 (98.0%), success 483/600 (80.5%), malformed 117
  Actions: speak(447), idle(19), build_billboard(16), move(1)
  Malformed: `move|speak`(30), `move|market`(19), `move|plaza`(9), `move|support`(5), `support|agent_02`(5)

**p1_mistral_ko_03**: 600 actions, parse 579/600 (96.5%), success 417/600 (69.5%), malformed 181
  Actions: speak(386), idle(24), support(4), move(3), build_billboard(2)
  Malformed: `move|speak`(72), `support|speak`(14), `move <plaza> && speak`(10), `support|move`(10), `move <market>`(9)


### Mistral 7B EN

**p1_mistral_en_01**: 600 actions, parse 595/600 (99.2%), success 455/600 (75.8%), malformed 144
  Actions: speak(430), support(9), idle(9), build_billboard(4), trade(3)
  Malformed: `speak|plaza`(33), `speak|market`(22), `speak|support`(10), `support|agent_07`(8), `speak|Alley C`(7)

**p1_mistral_en_02**: 600 actions, parse 592/600 (98.7%), success 521/600 (86.8%), malformed 79
  Actions: speak(485), idle(20), support(12), build_billboard(3), trade(1)
  Malformed: `move|speak`(15), `speak|market`(15), `speak|support`(12), `speak|plaza`(9), `move|market`(3)

**p1_mistral_en_03**: 600 actions, parse 600/600 (100.0%), success 519/600 (86.5%), malformed 81
  Actions: speak(477), support(25), build_billboard(9), idle(8)
  Malformed: `speak|market`(16), `move|speak`(15), `support|speak`(13), `support|agent_12`(12), `support|agent_07`(5)


### Llama 3.1 8B KO

**p1_llama_ko_01**: 600 actions, parse 565/600 (94.2%), success 594/600 (99.0%), malformed 5
  Actions: speak(507), support(38), idle(37), trade(7), adjust_tax(4)
  Malformed: `speak|trade`(3), `adjust_tax|grant_subsidy`(1), `speak|support`(1)

**p1_llama_ko_02**: 600 actions, parse 567/600 (94.5%), success 598/600 (99.7%), malformed 1
  Actions: speak(501), support(53), idle(34), trade(5), move(4)
  Malformed: `trade|speak`(1)

**p1_llama_ko_03**: 600 actions, parse 542/600 (90.3%), success 597/600 (99.5%), malformed 3
  Actions: speak(497), idle(59), support(30), move(4), trade(3)
  Malformed: `adjust_tax|grant_subsidy`(1), `support|move`(1), `speak|trade|support|whisper|move|idle`(1)


### Llama 3.1 8B EN

**p1_llama_en_01**: 600 actions, parse 600/600 (100.0%), success 599/600 (99.8%), malformed 0
  Actions: speak(551), idle(30), support(16), build_billboard(2), move(1)

**p1_llama_en_02**: 600 actions, parse 599/600 (99.8%), success 600/600 (100.0%), malformed 0
  Actions: speak(549), support(27), idle(23), build_billboard(1)

**p1_llama_en_03**: 600 actions, parse 599/600 (99.8%), success 600/600 (100.0%), malformed 0
  Actions: speak(523), idle(39), support(38)


### Gemini 2.0 Flash KO

**p1_flash_ko_01**: 600 actions, parse 600/600 (100.0%), success 594/600 (99.0%), malformed 0
  Actions: speak(296), support(146), idle(91), whisper(30), trade(12)

**p1_flash_ko_02**: 600 actions, parse 597/600 (99.5%), success 599/600 (99.8%), malformed 0
  Actions: speak(317), support(135), idle(111), move(15), trade(12)

**p1_flash_ko_03**: 600 actions, parse 600/600 (100.0%), success 598/600 (99.7%), malformed 0
  Actions: speak(287), idle(130), support(123), move(22), build_billboard(14)


### Gemini 2.0 Flash EN

**p1_flash_en_01**: 600 actions, parse 600/600 (100.0%), success 595/600 (99.2%), malformed 0
  Actions: speak(403), support(65), idle(64), move(32), build_billboard(15)

**p1_flash_en_02**: 600 actions, parse 600/600 (100.0%), success 599/600 (99.8%), malformed 0
  Actions: speak(406), support(102), idle(42), move(24), build_billboard(10)

**p1_flash_en_03**: 600 actions, parse 600/600 (100.0%), success 595/600 (99.2%), malformed 0
  Actions: speak(417), support(90), idle(49), move(26), build_billboard(6)


### GPT-4o-mini KO

**p1_gpt4o_ko_01**: 600 actions, parse 600/600 (100.0%), success 600/600 (100.0%), malformed 0
  Actions: speak(467), support(127), whisper(5), idle(1)

**p1_gpt4o_ko_02**: 600 actions, parse 600/600 (100.0%), success 600/600 (100.0%), malformed 0
  Actions: speak(467), support(132), idle(1)

**p1_gpt4o_ko_03**: 600 actions, parse 600/600 (100.0%), success 600/600 (100.0%), malformed 0
  Actions: speak(474), support(122), whisper(3), idle(1)


### GPT-4o-mini EN

**p1_gpt4o_en_01**: 600 actions, parse 600/600 (100.0%), success 599/600 (99.8%), malformed 0
  Actions: speak(485), support(110), whisper(4), trade(1)

**p1_gpt4o_en_02**: 600 actions, parse 600/600 (100.0%), success 600/600 (100.0%), malformed 0
  Actions: speak(469), support(125), trade(3), idle(2), whisper(1)

**p1_gpt4o_en_03**: 600 actions, parse 600/600 (100.0%), success 600/600 (100.0%), malformed 0
  Actions: speak(481), support(116), trade(2), whisper(1)


## Key Observations

1. **GPT-4o-mini**: parse 100.0%, action success 100.0%, malformed 0.0%
2. **Gemini 2.0 Flash**: parse 99.9%, action success 99.4%, malformed 0.0%
3. **EXAONE 3.5 7.8B**: parse 98.9%, action success 97.7%, malformed 0.1%
4. **Mistral 7B**: parse 98.4%, action success 78.8%, malformed 21.1%
5. **Llama 3.1 8B**: parse 96.4%, action success 99.7%, malformed 0.2%

### Language Effect (KO vs EN)

| Model | KO Parse | EN Parse | KO Success | EN Success |
|-------|----------|----------|------------|------------|
| EXAONE 3.5 7.8B | 98.4% | 99.3% | 99.2% | 96.1% |
| Mistral 7B | 97.6% | 99.3% | 74.6% | 83.1% |
| Llama 3.1 8B | 93.0% | 99.9% | 99.4% | 99.9% |
| Gemini 2.0 Flash | 99.8% | 100.0% | 99.5% | 99.4% |
| GPT-4o-mini | 100.0% | 100.0% | 100.0% | 99.9% |
