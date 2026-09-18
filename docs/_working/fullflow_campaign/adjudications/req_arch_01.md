---
ttl: task_bound
completes_when: 总包对本案卷车道四项登记作出裁定/转派
---

# 车道申请书 req_arch_01（st-ff-arch-20260918 · #ARCH-338..356 案卷车道）

按 `COORDINATION_LEDGER.md` §4：车道不自取裁定号，只交申请书 + 请总包回写 §6 待裁表，然后继续（未停等）。
本车道案卷全文=`lanes/arch_338_356_dossiers.md`（19 条逐条实测）。以下四项**越出本车道写权限或需总包/Max 裁**：

## A1 · 分包11 任务3 测试隔离缺陷（机械修，非本车道写域）
- 现象（亲验）：`pytest tests/rule/test_rule_red_blue.py::TestRedBlueReport::test_generate_report` 独立跑 FAIL（`got 0`），整文件跑 PASS。
- 根因：`_results`（模块级 list，:41）由兄弟测试 TestTRAE001-009 的 `_record()` 累积；`test_generate_report`（:411-431）直接读全局并 `assert total>=9` → **非自包含**（依赖跨用例顺序/同进程）。非数据/日期/路径三查。
- 修法（纯机械，无翻案）：为 `TestRedBlueReport` 加 autouse fixture 调可独立调用的 `_run_all_recordings()`（把 TRAE001-009 记录逻辑抽成函数供 fixture 跑）；验收=单独跑该节点必 PASS 且 total>=9。
- 请求：`tests/rule/**` 不在本案卷车道写域 → 请总包派 rule 车道或自落（CONSTRUCTION_DISCIPLINE §"纯机械修可直落"）。

## A2 · 注册表 #ARCH-338/339/343 headline 口径更正（触注册表，非本车道写域）
- 实测反证三条 headline 措辞与代码现状不符，**核心缺陷仍成立**，仅归因口径需修（防后人按错口径"退役"真在跑的件）：
  - #ARCH-338 "process_fill/ExecutionEngine 零生产接线" → 实有调用/装配点（`aggregate_root_manager.py:125`、`risk_validation_bridge.py:81`）；真断点是 process_fill JSONL→对账出口断链、Saga 孤儿。
  - #ARCH-339 "K03 StopGate 生产零调用" → `auto_runtime_core.py:137` 已实例化；真问题是"会话质量闸非交易闸，未接交易动作"（重分类）。
  - #ARCH-343 "pf_alloc 7 件仅 W03 真接线" → W01/W04/W05 有 in-pkg importer（生产可达性待 z-land3 定）。
- 请求：`architecture_issue_registry.yaml` 非本车道写域（热文件+CAS），请总包按 R-019"回写普查该行"同法更正三行 title/adjudication 措辞。

## A3 · BRK-021 paper_hedge_leg 标的件仍未落 HEAD（催落地）
- 实测：`src/zephyr/risk/paper_hedge_leg.py`(30720B) + `config/paper_hedge.yaml`(3316B) 在盘但 untracked，`git log` 无记录。
- 请求：R-020 落地权=z-land2，请总包确认其队列项存活/催办（本案卷时点未落）。

## A4 · #ARCH-343 pf_alloc 生产可达性 trace 请求（派 z-land3）
- 本车道 import 层测得 W01/W04/W05 有 importer，但"in-pkg importer ≠ orchestrator 可达"。整域"接线/退役"终判须从 allocation orchestrator 入口做 DFS。
- 请求：R-K12 落地权=z-land3，请转派其出"pf_alloc 各件生产可达性 trace"再批裁。
