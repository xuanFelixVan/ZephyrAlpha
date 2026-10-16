---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: D16-S2
excavated: 2026-10-15
ttl: task_bound
---

# D16-S2 生效中 active（治理立法流主通道态）

## 1. 定义

立法流唯一能承载 approved_paths 授权、被门禁认可引用的在册态。骨架记"291 条"为图 counts 生成时点
（2026-10-05）值；本次活投影实读（2026-10-15）：`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`
共 353 行，其中 active=333（draft 1 / superseded 4 / void 2 / decided 13）。

## 2. 六向台账

### 2.1 输入面
- 三条入边：D16-T2 `∅→active` 直批登记（凭证=Owner 批文/呈裁批）、D16-T5 `draft→active`、D16-T9 `∅→active` 跨实例复活（新号+related_rulings 指回，编号不回收的合法出路）。
- 证据：`config/governance_legislation_map.yaml` transitions D16-T2/T5/T9。

### 2.2 输出面
- 三条出边：T6→superseded（superseded_by 必填）、T7→deprecated（零实例预留）、T8→decided（#409 族归档形态）。
- 发布面 D16-N5 publish 快照：`src/zephyr/governance/registry_ledger/baseline.py`（同 content_sha=noop 幂等，snapshot_version=9@图 counts）。
- 消费面 D16-N7：审批通道（_ruling_channel：active+expires_at+approved_paths）、reference 类 gates、取号分母、对齐清单挂轴。

### 2.3 SSOT 真源
- 结构真源：`config/governance_legislation_map.yaml#D16-S2`。
- 实例真源：PG 账本 REG-RULING-001 → 投影 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`。
- ROOR：`docs/registry_of_registries.yaml:572` REG-RULING-001 entry_count=308（counting_rule=rulings 条目数）——与活投影 353 行、图生成时点 312 三账不一致（见 §4）。

### 2.4 代码模块
- `src/zephyr/governance/registry_ledger/api.py`、`src/zephyr/governance/registry_ledger/baseline.py`。
- 规则 YAML→gate 落地面：`src/zephyr/gov_rule/`（constitutional_update/、standards_manager.py 实存）、`src/zephyr/gov_enforcement/`（实存，含 rule_bridge/git_commit_gateway.py）。
- 审批消费：`src/zephyr/gov_enforcement/commit_gates/approval_resolver.py`（实存）。

### 2.5 门禁约束
- 同 commit 原子门（图 laws 第 3 条，priority=74）：登记名 RULING-REFERENCE 已于 2026-09-23 合并重定向至 REFERENCE-INTEGRITY（`gate_registry.yaml:1837`，status=deprecated，redirect_to=REFERENCE-INTEGRITY，gate_id 作历史锚点保留）；执行体 `src/zephyr/gov_enforcement/commit_gates/ruling_reference_gate.py` 实存。
- 结构门 GOVERNANCE-LEGISLATION-MAP（`gate_registry.yaml:1425` → `src/zephyr/gov_enforcement/commit_gates/map_family/governance_legislation_map_gate.py`）。
- 禁边 X1（同号复活 409）/X2（撤销取代）/X4（悬空引用 hard block）环绕本态。

### 2.6 自动化触发
- commit 门禁链（REFERENCE-INTEGRITY 通道）逐 commit 扫描裁定引用与册面原子性。
- publish/render 双通道：baseline.py 快照 + `scripts/governance/registry_projection/registry_projection_generator.py`。
- 规则数据侧走 RULE-SSOT（YAML 改→同步 DB），无定时器。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | T2/T5/T9 三入边在册，取号器实存 |
| 输出面 | pass | T6/T7/T8+publish/消费索引全在册 |
| SSOT 真源 | warn | ROOR REG-RULING-001 entry_count=308 vs 活投影 353 行 vs 图 counts 312——三账漂移，ROOR 计数未随 render 同步 |
| 代码模块 | pass | registry_ledger/gov_rule/gov_enforcement/approval_resolver 全实存 |
| 门禁约束 | warn | 图 laws 仍称"RULING-REFERENCE gate74"，该 gate_id 已 deprecated 重定向 REFERENCE-INTEGRITY（锚点保留，语义名陈旧） |
| 自动化触发 | pass | commit 门禁+publish/render 实证 |

## 4. 缺口与建议

- ROOR 计数漂移（308 vs 353）：建议 render 后同步刷新 ROOR entry_count，或把 REG-RULING-001 计数改为"账本现算"注记口径，消除三账漂移。
- gate 名称陈旧：图16 laws/N4/X4 引用的 RULING-REFERENCE 已是重定向锚点，下次生成器跑批时建议映射为 REFERENCE-INTEGRITY（或注记 redirect）。
- 骨架"291 条"与活值 333 的差值=生成时点口径，非漂移（图 laws 自declared），子文档以双口径并列。
