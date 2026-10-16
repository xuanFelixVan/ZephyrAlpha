---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: D16-S4
excavated: 2026-10-15
ttl: task_bound
---

# D16-S4 已废弃 deprecated（治理立法流终态二·结构性预留）

## 1. 定义

四值枚举内预留的废弃位，当前零实例（结构性预留，非自造——图 D16-S4 note 原文）。
结构真源：`config/governance_legislation_map.yaml#D16-S4`（terminal=true）。
实例计数：图 counts（2026-10-05）与活投影实读（2026-10-15）均为 deprecated=0。

## 2. 六向台账

### 2.1 输入面
- 唯一入边 D16-T7：`active→deprecated`（update 废弃，枚举预留位，零实例）。
- 证据：`config/governance_legislation_map.yaml` transitions D16-T7。

### 2.2 输出面
- 终态墓碑，无出边。与 D16-S5 void 墓碑的区别：deprecated=语义废弃（枚举内），void=撞号处置留痕（枚举外观测旁支）。

### 2.3 SSOT 真源
- `config/governance_legislation_map.yaml#D16-S4`。
- 枚举口径注记：投影册头部注释（ruling_registry.yaml #4）写"status 四值：active/superseded/deprecated/draft"，而图 states 为六态——void/decided 为枚举外观测旁支（图 D16-S5/S6 note 自declared），deprecated 在四值枚举内。两处口径由图 boundary 与 note 显式调和，无冲突。

### 2.4 代码模块
- `src/zephyr/governance/registry_ledger/api.py`（update 通道承载状态翻转）。
- `src/zephyr/gov_enforcement/commit_gates/approval_resolver.py`（仅 active 放行，deprecated 天然失效）。

### 2.5 门禁约束
- 结构门 GOVERNANCE-LEGISLATION-MAP；无本态专属禁边（X 族均跨态）。

### 2.6 自动化触发
- 零实例零专属触发（图 laws 第 6 条：无持久落点的零计数属源缺口非零触发——本态属设计内预留，非缺口）。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | T7 在册（预留） |
| 输出面 | pass | 终态语义清晰，与 void 判异 |
| SSOT 真源 | pass | 图/册/枚举注释三处口径自洽 |
| 代码模块 | pass | api/approval_resolver 实存 |
| 门禁约束 | pass | 结构门覆盖 |
| 自动化触发 | pass | 零实例=设计内预留，非源缺口 |

## 4. 缺口与建议

- 建议：保持预留不主动制造实例；若未来启用 deprecated，应优先考虑与 superseded 的语义边界复查（同终态双出口的判重，w5_1 内收判据"同域重复簇→收敛唯一"候观察名单，暂不动）。
