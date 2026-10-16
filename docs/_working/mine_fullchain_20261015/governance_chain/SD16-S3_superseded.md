---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: D16-S3
excavated: 2026-10-15
ttl: task_bound
---

# D16-S3 被取代 superseded（治理立法流终态一）

## 1. 定义

新裁定取代旧裁定后的终态。superseded_by 必填且单向不可逆（裁定#20-D 铁律9）。
结构真源：`config/governance_legislation_map.yaml#D16-S3`（terminal=true）。
实例计数：图 counts（2026-10-05）superseded=4，superseded_by_chains=5；活投影实读（2026-10-15）superseded=4——吻合。

## 2. 六向台账

### 2.1 输入面
- 唯一入边 D16-T6：`active→superseded`（update + superseded_by 必填 + reason+审计）。
- 证据：`config/governance_legislation_map.yaml` transitions D16-T6。

### 2.2 输出面
- 终态，无出边。取代链 D16-N8：superseded_by 单向指针 + related_rulings 双向关联（议题-裁定互溯，#20-D 铁律9/10）。
- 证据：`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` 条目字段 superseded_by/related_rulings（sample keys 实读）。

### 2.3 SSOT 真源
- `config/governance_legislation_map.yaml#D16-S3`；实例=PG 账本 REG-RULING-001 投影册。
- ROOR：REG-MAP-GLM-001（`docs/registry_of_registries.yaml:665`）+ REG-RULING-001（`:572`）。

### 2.4 代码模块
- `src/zephyr/governance/registry_ledger/api.py`（update 强制 superseded_by；retire 强制 authority_ref）。
- `scripts/governance/next_ruling_id.py`（复活=新号+related_rulings 指回，旧号状态不变）。

### 2.5 门禁约束
- 禁边 D16-X2：superseded→active 撤销取代=伪造授权，update 须 reason+审计，机械拒。
- 结构门 GOVERNANCE-LEGISLATION-MAP（`src/zephyr/gov_enforcement/commit_gates/map_family/governance_legislation_map_gate.py` 实存）。

### 2.6 自动化触发
- commit 门禁链 + render 投影（`scripts/governance/registry_projection/registry_projection_generator.py` 实存）。
- 取号器 --next 分母含在途占号（X3 防线）。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | T6 单入边+铁律9 语义在册 |
| 输出面 | pass | 取代链 N8 双指针字段投影册实证 |
| SSOT 真源 | pass | 图值 4=活投影 4，零漂移 |
| 代码模块 | pass | api/next_ruling_id 实存 |
| 门禁约束 | pass | X2+结构门实存 |
| 自动化触发 | pass | commit 门禁+render 双通道 |

## 4. 缺口与建议

- 无本态专属缺口。superseded_by_chains=5 与条目级 superseded_by 字段的一致性由账本现算保证，无需额外对账件。
