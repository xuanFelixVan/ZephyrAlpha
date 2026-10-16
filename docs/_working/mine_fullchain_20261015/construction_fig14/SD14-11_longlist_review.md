---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-11
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-6-长清单审查12-节全维度对抗审查 + 附录 D 锚块
---

# SD14-11 长清单审查（policy Step 6）

## 1. 定义

Step 5 测试通过后触发：按附录 A 长清单执行 12 节全维度对抗审查（0.5 改动分类→逐节 PASS/FAIL/N/A→FAIL 就地修复→分轮处理禁边审边改→结论对话内给出）。基座=trae_081 审计维度框架（54 维度，长清单是其子集）。配套：方法论根因分析（MTH-006 追问到底）、漂移检测套件六件套。遗留项 MUST 登记（原 construction_progress_tracker.md 登记面已随裁定#384 归档，现行留痕=handoff 交接包）。产出=审查结论（对话内）+跳过条款清单。wiring=unwired_no_caller。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 循环验收通过（D14-10）；改动本体 | 政策 L457-482；图 rollback_to=D14-09（FAIL 无法就地修回施工，回边 B10） |
| 输出面 | 审查结论（对话内，政策禁创建报告文件）；遗留项→handoff 交接包 `.runtime/handoffs/handoff_<sid>.json` | 政策 L472（遗留项登记条款+归档注记）；图 fallback 原文 |
| SSOT 真源 | 本政策附录 A（实测 16 小节 A.0~A.14——本批 grep 实证；政策正文称 12 节/修订记录称 14 节，三处口径并存=WJ-R-09）+`trae_081_audit_dimensions_framework.yaml#dimensions`（54 维度基座，在盘） | 政策 L861-1025；`docs/01_policies_and_standards/rules/trae_081_audit_dimensions_framework.yaml` |
| 代码模块 | 漂移检测套件六件在盘但未接入本段判据：`scripts/governance/d5_architecture/checkers/check_contract_code_drift.py`、`.../validators/validate_load_path_integrity.py`、`scripts/governance/d1_structure/validate_config_integrity.py`、`scripts/governance/d2_links/`、`scripts/governance/d4_paths/`、`scripts/governance/d9_knowledge/`（图 evidence 实证在盘） | 政策 L474-481 |
| 门禁约束 | 零 gate（gates:[]）；A.12 零问题闭环靠人工 | 图 YAML #D14-11 |
| 自动化触发 | 无（unwired_no_caller；回边 B10 入图，网关拒绝回边 B13 从 D14-15 回本段） | 图 YAML #D14-11 loops |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 上游验收通过即触发，链闭合 |
| 输出面 | fail | 结论禁留痕+遗留项原登记目的地已归档（D14-G12）——输出双断 |
| SSOT 真源 | warn | 附录 A/12 节/14 节三口径漂移（本批 16 小节实证）；基座册在盘 |
| 代码模块 | warn | 六件套在盘可跑但与判据零接线——有工具无判据挂接 |
| 门禁约束 | fail | 零 gate，全靠自觉 |
| 自动化触发 | fail | unwired_no_caller |

## 4. 缺口与建议

- 缺口1：三处节数口径漂移（12/14/16）——宪法 §4.4"文档矛盾=事故"判例级案例。建议：政策正文与修订记录统一改"节数以附录 A 实际小节数为准"（计数用字段不写死散文）。
- 缺口2：漂移六件套未接判据。建议：把六件套作为 A.13（全图全库对齐验证）节的机械预检入口——审查 AI 先跑套件再人工复核，manual 段获得 inspection 子面（零新件，纯接线）。
- 缺口3：与 D14-02 清单同物（附录 A）——同 SD14-02 建议单源共享，本段留"施工后"专用小节。
- 缺口4：禁报告文件与留痕互斥，同 D14-02 的 staging 留痕裁定建议。
