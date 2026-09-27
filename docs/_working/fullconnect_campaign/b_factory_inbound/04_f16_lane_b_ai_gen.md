---
ttl: task_bound
title: F16 车道B·AI 生成（NL→假说量产）——L02 接线矿道案卷
session: zc-l02-20260927
---

# F16 · 车道B-AI生成（lane_b_idea_generator）

> 挖矿基册=01_strategy_factory/04_f16_lane_b_ai_gen.md（SF-A）。本卷=独立复核+09-26/27 增量（含 3 条 pass 候选新去向实证）。

## 一、六向台账
| 向 | 实证锚点 |
|----|------|
| 上游 | SEED_THEMES 12 主题种子+OllamaChat(qwen3:8b) 经 LSG（lane_b_idea_generator.py:133-135）；temperature 0.4；确定性 prompt（:66-75） |
| 下游 | lane_b_candidates.csv（09-27 复测 **4 行**，mtime 09-16 02:33 未动）→E2：CH 批 E2-20260914-070511（1 pass/3 reject）+E2-20260916-021246（**3 pass/8 reject=11 行**，09-27 CH 复查互证）→E3：09-26 translator 班取 3 条 B pass（translated_manifest 0926 三行，birth_channel=B） |
| 自动触发 | 无常驻；编排 with-lane-b 可选旗或手工 CLI；零计划任务（schtasks 09-27） |
| 真源注册表 | MOD-BT-150=path_ownership_map.yaml:16012,35472；图 9 FAC-E1B partial；tests/backtest/test_lane_b_idea_generator.py 在盘；QuantCode-Bench 警示（70-76%）在图 9 algo_note |
| 门禁质量尺 | 出生证三件套机器写入（:106-117）；id=CAND-md5(E1B:全文) 内容寻址跨批去重（:100-103）；台账损坏按空集重写不误删（:120-128）；LSG fail-closed |
| 运行状态 | **红（台账完整性）+黄（Ollama 断供）**。蒸发 11 行未重建（csv 仍 4 行）；09-16 后零新班；09-26 翻译班证明下游对 B pass 有消费动作但 **llm_error:ConnectionError 三连**（Ollama 11434 断供，inventory §2.3-4 Owner 门） |

## 二、子模块三级枚举
1. **代码面**：run_generation :131-184｜parse_ideas :78-97（G 车道委托复用）｜load_existing_ids :120-128。无第三件。
2. **注册表/文档面**：path_ownership_map:16012；FAC-E1B（store_refs=lane_b_candidates.csv）；图 9 design_refs=Vibe-Trading/QuantCode-Bench。
3. **数据面**：lane_b_candidates.csv 4 行（蒸发前应 15）；CH 侧蒸发存证=c1_backtest.hypothesis_precheck 批 E2-20260916-021246 11 行含 hypothesis_zh 原文+birth 三件套（重建数据源完备）。

## 三、接线四态独立复核
- 图 9 四态 partial → **维持 partial**。
- **骨架勘误/增量**：SF-A 断点④记"09-16 批 3 条 B pass 被翻译班永久错过"——**09-26 已部分翻案**：翻译班 09-26 10:29 确实取到这 3 条（LIMIT-N SQL prechecked_at DESC 语义下 B 批 09-16 为最新），但因 Ollama 断供全部 llm_error 入阴性档；叠加 translated_manifest 幂等按 candidate_id 全集跳过（hypothesis_translator.py:122-129），**3 条 B pass 现被 llm_error 阴性行占坑、无自动重试路径**——错过的性质从"时间窗错过"升级为"台账占坑死锁"（详见 10_f22 卷缺口②）。
- 蒸发 11 行实证复核：CH 批行数 11（3+8）与 csv 现存 4 行（09-14 批）差集成立，事故维持未处置。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 【P0 维持】进货台账 11 行蒸发未重建 | csv 4 行 vs CH 批 E2-20260916-021246 11 行；mtime 09-16 02:33 | 施工：CH 重建 11 行（0.5 天）+csv↔CH 对账校验器挂 E2 前置（1 天）+台账写入走 safe_write CAS | P0 |
| 2 | 3 条 B pass 被 llm_error 阴性行占坑 | translated_manifest 0926 三行 translatable=false refusal=llm_error:ConnectionError | 施工（F22 侧主导）：幂等跳过排除 llm_error 行或重试队列 | P1 |
| 3 | 产出停滞：09-16 后零新班 | csv 无新批；Ollama 断供 | 挂起+解锁：Ollama 11434 恢复=Owner 显令（inventory §2.3-4）；后随 F14 触发器 | P1 |
| 4 | 12 主题固定种子多样性天花板 | 同 prompt 重复班撞内容寻址去重 | P2 设计项：主题轮换（改一处共享防双真源） | P2 |

## 五、自审闸三态
- **三态：partial**。沿用基册+复核有增量：P0 蒸发维持；新增断点=3 条 pass 占坑死锁（§三）；Ollama 断供为停滞直接根因之一（基册归因触发缺位，本卷补齐两因）。

## 六、复跑命令
```bash
python -c "import csv;rs=list(csv.DictReader(open('data/strategy_intake/lane_b_candidates.csv',encoding='utf-8-sig')));print(len(rs),[r['birth_batch'] for r in rs])"
python -c "import csv;[print(r['candidate_id'],r['translatable'],r['refusal_reason']) for r in csv.DictReader(open('data/strategy_intake/translated_manifest.csv',encoding='utf-8-sig')) if r['translated_at'].startswith('2026-09-26')]"
python scripts/backtest/hypothesis_precheck.py status   # total=63；E2-20260916-021246 蒸发存证
python -m pytest tests/backtest/test_lane_b_idea_generator.py -q
```
