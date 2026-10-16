---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: D16-S5
excavated: 2026-10-15
ttl: task_bound
---

# D16-S5 撞号墓碑 void（治理立法流终态三·枚举外观测旁支）

## 1. 定义

撞号处置留痕 tombstone——非裁定本体，占号防复用的登记形态（图 D16-S5 note 原文；枚举外观测旁支）。
制度化=裁定#485①（跳号台账）。结构真源：`config/governance_legislation_map.yaml#D16-S5`（terminal=true）。
实例计数：图 counts（2026-10-05）void=2；活投影实读（2026-10-15）void=2——吻合。

## 2. 六向台账

### 2.1 输入面
- 唯一入边 D16-T4：`∅→void`，register(status=void) 随撞号处置批登记；先例=裁定#408。
- 证据：`config/governance_legislation_map.yaml` transitions D16-T4。

### 2.2 输出面
- 终态，无出边。产出物=跳号台账行（裁定#485①）：占号防复用凭据，编号永不回收（laws 第 1 条）。

### 2.3 SSOT 真源
- `config/governance_legislation_map.yaml#D16-S5`；实例=PG 账本 REG-RULING-001 投影册（`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`，void 行 grep 可核）。
- ROOR：REG-MAP-GLM-001 + REG-RULING-001 两行。

### 2.4 代码模块
- `scripts/governance/next_ruling_id.py`（O_EXCL 独占；释放≠可复用；--next 分母感知在途占号）。
- `src/zephyr/governance/registry_ledger/api.py`（CAS 409 CONFLICT_DUPLICATE 拒绝同号异指纹）。

### 2.5 门禁约束
- 禁边 D16-X7：占号转让/复用/回收（跳号永不复用）。
- 禁边 D16-X1：任何态→active 同号就地复活（409 机械拒）。

### 2.6 自动化触发
- CAS 409 拒绝必记事件（D16-N3 意图 API 语义，laws 第 2 条）；无定时器。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | T4+先例#408 在册 |
| 输出面 | pass | 墓碑/跳号台账语义闭环（#485①） |
| SSOT 真源 | pass | 图值 2=活投影 2，零漂移 |
| 代码模块 | pass | next_ruling_id/api 实存 |
| 门禁约束 | pass | X1/X7 双禁边在册 |
| 自动化触发 | pass | 409 事件记录语义在册 |

## 4. 缺口与建议

- 无本态专属缺口。
