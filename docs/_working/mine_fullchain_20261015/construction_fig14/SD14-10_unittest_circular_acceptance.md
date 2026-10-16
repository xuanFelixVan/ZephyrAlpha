---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-10
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-5-单元测试--循环验收 + 附录 D 锚块
---

# SD14-10 单元测试与循环验收（policy Step 5）

## 1. 定义

Step 4 落码完成后触发：循环验收协议——运行验收命令→记录错误数 E1→修复→重跑→直到连续 2 轮 0 错误才算 COMPLETED（CIRCULAR_ACCEPTANCE_ROUNDS=2，代码常量强制）；3 轮修复仍无法归零→标 FAILED 升级 Owner。配套：pre-commit 增量守门（只查 staged 新增，全仓扫描移 stages:[manual]）、测试面清单纪律（批量施工先罗列受影响测试全集+全量 pytest+留存清单文件）、状态词表出厂纪律（新模块状态输出引官方词表）。图 B9 自环=循环验收真自环，轮次由代码常量定（max_rounds_ref 符号锚）。wiring=partial。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 已落码（D14-09 产物）；任务卡验收命令集（有卡形态） | 政策 L413-455；`docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml#task_card` |
| 输出面 | 测试报告（对话内）+测试面清单文件（`.runtime/tmp/<批次>_tests.txt`）+任务卡 COMPLETED 终态（有卡） | 政策 L437-440（测试面清单纪律）；`src/zephyr/governance/persistence/task_repo.py` |
| SSOT 真源 | `trae_035_task_construction_verification.yaml#task_003_circular_acceptance` + `trae_084_precommit_incremental_discipline.yaml` + `trae_071#test_residue_reclaim` + 词表两件 `docs/_working/vocab_legislation/01_official_state_vocabulary.md`/`02_state_vocabulary_mapping_register.md` | 各件在册；词表模块已复活（R-08 闭合） |
| 代码模块 | `src/zephyr/governance/persistence/task_repo.py`（module_id=MOD-TASK_SYSTEM；`CIRCULAR_ACCEPTANCE_ROUNDS: Final[int] = 2` L667 本批实证+循环函数）；词表模块 `src/zephyr/shared/vocab/market_state.py`（在盘实证——D14-G10 幽灵断言已按 invalidation 条款作废） | 三件实证 |
| 门禁约束 | `TEST-SOURCE-CONSISTENCY`（防测试漂移）+`TEST-RESIDUE-SSOT`（防测试残留前缀硬编码）——双册在册（本批 grep 实证）；GATE-RUNTIME-CLEANUP reconciler 兜底测试残留 | 两册+政策 L449-455 |
| 自动化触发 | 循环验收在任务卡转 COMPLETED/VERIFIED 终态且验收命令集非空时由代码强制；测试残留双层清理（conftest.py pytest_sessionfinish 源头清+post-commit reconciler） | 图 YAML #D14-10 note 原文 |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 落码/任务卡两路输入明确 |
| 输出面 | warn | 无卡施工形态无验收终态留痕（簿02 X-16 待裁）；测试面清单文件留 .runtime/tmp 可查 |
| SSOT 真源 | pass | 四组真源在册；R-08 已闭合（词表复活，本批实证 market_state.py 在盘） |
| 代码模块 | pass | CIRCULAR_ACCEPTANCE_ROUNDS=2 代码常量实证（非散文计数） |
| 门禁约束 | pass | 两台 gate 双册实证 |
| 自动化触发 | warn | 循环验收是真执行但触发条件依赖任务卡形态——无卡施工永不相触（结构性盲区） |

## 4. 缺口与建议

- 缺口1（WJ-R-19）：无任务卡的施工（如本挖矿批）不受循环验收强制。建议：总包裁定"无卡施工"的等价验收面（X-16）——最低成本方案=会话收尾自报 pytest 汇总行进 handoff 包。
- 缺口2：max_rounds_ref 符号锚脆弱（常量改名即判红，invalidation 条款自述）。建议：锚块校验器加符号存在性预检（重命名时提前告警而非事后判红）。
- 缺口3：3 轮 FAILED 升级 Owner 的升级动作无登记面。建议：并入 handoff 交接包 warnings 字段（现有结构，零新建）。
