---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: D16-S1
excavated: 2026-10-15
ttl: task_bound
---

# D16-S1 草案 draft（治理立法流六态之首）

## 1. 定义

裁定编号原子占号并登记后、尚未生效的立法条目状态。审批通道不认 draft（仅 active 放行授权）。
结构真源锚点：`config/governance_legislation_map.yaml#D16-S1`（state_id=D16-S1, value=draft, terminal=false，
"已占号登记、尚未生效；审批通道不认（仅 active 放行）"）。准入=裁定#486（Owner 2026-10-05 双批）。

## 2. 六向台账

### 2.1 输入面
- 入边 D16-T1：`∅→draft`，register(status=draft) 占号后草案先行（先例=裁定#1）。
- 上游机构 D16-N1 呈报口：`docs/_working/map_build/22_fig15_card_lifecycle_charter.md`、`docs/_working/map_census/00_panorama_map_census_v1.md`。
- 上游机构 D16-N2 取号器：`scripts/governance/next_ruling_id.py`（--next 幂等查询 / --claim O_EXCL 独占 / --release 仅本会话；编号不回收）。
- 证据：`config/governance_legislation_map.yaml` transitions 块 D16-T1（实读）。

### 2.2 输出面
- 出边 D16-T5：`draft→active`（update 状态翻转，草案过批生效）。
- draft 态不产生任何授权副作用：`src/zephyr/gov_enforcement/commit_gates/approval_resolver.py` 审批通道仅认 active。
- 证据：`config/governance_legislation_map.yaml#D16-S1` note_zh + transitions D16-T5。

### 2.3 SSOT 真源
- 结构真源：`config/governance_legislation_map.yaml`（机生件，generator=`scripts/governance/d5_architecture/generators/generate_governance_legislation_map.py`，禁手改后不回生成）。
- 实例唯一机械真源：PG 账本 REG-RULING-001；YAML 只读投影=`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`（头注：手改必被 render 覆盖，裁定#502）。
- ROOR 发现入口：`docs/registry_of_registries.yaml:665`（REG-MAP-GLM-001，counting_rule=transitions 条目数=9，与图实读一致）。
- 实例现值（活投影实读 2026-10-15）：draft=1 条。

### 2.4 代码模块
- `src/zephyr/governance/registry_ledger/api.py`（意图 API：register/update/retire，接口负面清单禁整册写）。
- `scripts/governance/next_ruling_id.py`（占号器）。
- `src/zephyr/gov_enforcement/commit_gates/approval_resolver.py`（draft 排除逻辑的消费侧）。
- 三件均已实存核验（2026-10-15 ls）。

### 2.5 门禁约束
- 结构门 GOVERNANCE-LEGISLATION-MAP：`docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml:1425`，执行体 `src/zephyr/gov_enforcement/commit_gates/map_family/governance_legislation_map_gate.py`（实存）。
- 禁边 D16-X1（同号就地复活=CONFLICT_DUPLICATE 409 机械拒）、D16-X3（未占号登记）、D16-X4（未登记先引用）在本态前置生效。
- 引用原子门（gate74）：RULING-REFERENCE 已合并重定向 REFERENCE-INTEGRITY（`gate_registry.yaml:1837`，redirect_to=REFERENCE-INTEGRITY，2026-09-23 P4 七簇合并）；执行文件 `src/zephyr/gov_enforcement/commit_gates/ruling_reference_gate.py` 实存。

### 2.6 自动化触发
- commit 时门禁链扫描 裁定#NNN 引用（REFERENCE-INTEGRITY 通道）。
- 投影 render：`scripts/governance/registry_projection/registry_projection_generator.py --render --registry-id REG-RULING-001`（实存）。
- 占号/登记本身为 CLI 人工语义，无定时器（符合"立法不经 cron"口径）。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | T1/取号器/呈报口三锚点全实存 |
| 输出面 | pass | T5 在册；approval_resolver 排除 draft 实证 |
| SSOT 真源 | pass | 图 YAML+PG 投影+ROOR 三层齐；draft=1 活值吻合 |
| 代码模块 | pass | api/next_ruling_id/approval_resolver 全实存 |
| 门禁约束 | pass | 结构门+引用门执行体实存 |
| 自动化触发 | pass | commit 门禁+render 双通道实证 |

## 4. 缺口与建议

- 无本态专属缺口。通用注记：图 counts 块为 2026-10-05 生成时点值，实例对拍须走账本现算口径（图 laws 第 6 条自declared）。
