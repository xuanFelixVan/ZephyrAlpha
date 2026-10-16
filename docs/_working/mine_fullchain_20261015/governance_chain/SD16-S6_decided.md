---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: D16-S6
excavated: 2026-10-15
ttl: task_bound
---

# D16-S6 已决归档 decided（治理立法流终态四·枚举外观测旁支）

## 1. 定义

战役代裁/呈裁执行完毕的归档态，不再构成活授权（图 D16-S6 note 原文；枚举外观测旁支）。
结构真源：`config/governance_legislation_map.yaml#D16-S6`（terminal=true）。
实例计数：图 counts（2026-10-05）decided=13；活投影实读（2026-10-15）decided=13——吻合。

## 2. 六向台账

### 2.1 输入面
- 双入边：D16-T3 `∅→decided` register(status=decided) 随批即决（战役代裁形态；先例=裁定#404/#407）；D16-T8 `active→decided` update 执行完毕归档（先例=#409 族归档形态）。
- 证据：`config/governance_legislation_map.yaml` transitions D16-T3/T8。

### 2.2 输出面
- 终态账本行，无出边。不再进入审批通道（approval_resolver 仅认 active）。

### 2.3 SSOT 真源
- `config/governance_legislation_map.yaml#D16-S6`；实例=PG 账本 REG-RULING-001 投影册。
- 呈报判据真源（boundary 显式外置，本图只存指针）：`docs/01_policies_and_standards/sop/governance_sop/deep_adjudication_method_policy.md`（实存核验）。

### 2.4 代码模块
- `src/zephyr/governance/registry_ledger/api.py`（register/update 双通道）。
- `src/zephyr/gov_enforcement/commit_gates/approval_resolver.py`（decided 排除）。

### 2.5 门禁约束
- 结构门 GOVERNANCE-LEGISLATION-MAP；引用门（REFERENCE-INTEGRITY 通道，原 gate74）对 decided 引用不产生授权语义。

### 2.6 自动化触发
- commit 门禁链 + render 投影（registry_projection_generator.py）。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | T3/T8 双入边+三先例（#404/#407/#409）在册 |
| 输出面 | pass | 终态归档语义闭环 |
| SSOT 真源 | pass | 图值 13=活投影 13；呈报判据指针实存 |
| 代码模块 | pass | api/approval_resolver 实存 |
| 门禁约束 | pass | 结构门+审批排除 |
| 自动化触发 | pass | commit 门禁+render |

## 4. 缺口与建议

- 结构性缺口（归骨架 §3 缺口批第 12 条，不在本环节发明）：裁定路由全半程未成图——`docs/01_policies_and_standards/sop/governance_sop/adjudication_routing_policy.md`（实存）的八类路由+生死两轨无链路图承载；图16 立法流只覆盖"裁定→规则→gate"半程。建议立 issue 走缺口批。
