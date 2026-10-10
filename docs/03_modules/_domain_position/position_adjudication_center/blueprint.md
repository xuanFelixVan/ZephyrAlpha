---
blueprint_id: MOD-POS-024
module_id: MOD-POS-024
module_name: position_adjudication_center
domain: D_POSITION
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: H
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_POSITION
path: src/zephyr/position/core/position_adjudication_center.py
granularity: file
responsibility_domain: 
---

# MOD-POS-024 position_adjudication_center 蓝图（C-047 仓位管理唯一裁决中心）

> **module_id**: MOD-POS-024 | **域**: D_POSITION | **优先级**: P1
> **来源**: B1-00194（AUD-DRAFT-001-DIGEST P1 波 W-P1-19，CAND-POS-002，跨域元文档 §功能域模块·D-PORTFOLIO）
> 代码：`src/zephyr/position/core/position_adjudication_center.py`

## 0. 定位

C-047 仓位管理唯一裁决中心：TSV 现状注记"四层构件(sizing/limit/risk_budget/
intraday)已存在但无唯一权威裁决入口，核心交易链需要"。施工形态=四层
（组合/策略/标的/动态）仓位裁决单一入口，汇聚现有 sizing/limit_enforcer/
risk_budget_allocator，产出唯一权威目标仓位并阻断旁路下单。

查重分工（W-P1-19 铁律⑤探查——**编排层缺口，非真源重叠**，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| position_sizing_engine | MOD-POS-001 | 标的层 Kelly+13 约束精裁 | 本中心**标的层委托件**，不重造 |
| position_limit_enforcer | MOD-POS-010 | 硬约束 5 级否决检查 | 本中心**标的层否决委托件**，不重造 |
| position_risk_budget_allocator | MOD-POS-013 | 组合层 ERC 风险预算权重 | 本中心**组合层委托件**，不重造 |
| intraday_position_constraint | MOD-POS-018 | 动态层 T+1/盘中投影约束 | 本中心**动态层委托件**，不重造 |
| strategy_book / firm_risk_aggregator | MOD-POS-020/021 | 策略层粗仓位 / 组合汇总裁剪 | 数据流上游；本中心=交易链**唯一入口**编排 |
| regime_meta_allocator（effective_budget 链） | MOD-PA-007 | 策略预算分配（D_PF_ALLOC 域） | 预算**分配层**，非交易时**裁决层**——层不同不重叠 |

裁决哲学与 strategy_validation_pipeline（MOD-BT-001，"只编排不重造"）同族：
四层判定全部委托注入 callable（装配批接既有件），本中心只做编排、保守收敛
与唯一性令牌。

不做什么：不重造四层判定逻辑、不直接下单（只出 AdjudicatedPositionPlan +
adjudication_id 令牌）、不做预算分配（归 MOD-PA-007 链）。

## 1. 规则（确定性，Fail-Closed）

- **四层裁决**：adjudicate(request) 依序调 组合层→策略层→标的层→动态层
  （注入 callable，各返 LayerVerdict）；任一层 allowed=False → 终审拒绝
  （allowed=False, final_weight=0, 汇聚 violations）；四层全过 →
  final_weight=min(各层 adjusted_weight)（**最保守收敛**）。
- **唯一性令牌**：adjudication_id = sha256(规范化请求) 前 16 hex；同请求幂等
  （重复 adjudicate 返回首份裁决，不重发令牌）；层异常 → 终审拒绝
  （Fail-Closed，不外抛）。
- **旁路阻断**：verify_bypass(request, token) — 令牌缺失/与首发令牌不符 =
  旁路下单嫌疑（bypass=True）；下单链只认本中心首发令牌（装配批接线）。
- Fail-Closed：request 字段非法（weight∉[0,1]/action 非法/空 id）→
  PositionAdjudicationError。

## 2. 接口

```python
class IntendedAction(str, Enum): OPEN / ADD / REDUCE / EXIT
@dataclass(frozen=True)
class AdjudicationRequest: request_id / strategy_id / symbol / action / intended_weight / context
@dataclass(frozen=True)
class LayerVerdict: layer / allowed / adjusted_weight / violations / reason
@dataclass(frozen=True)
class AdjudicatedPositionPlan: adjudication_id / request / allowed / final_weight / layer_verdicts / reason
class PositionAdjudicationCenter: adjudicate(request) / verify_bypass(request, token)
class PositionAdjudicationError(Exception)  # error_code 待登记
```

## 3. 依赖前置

- MOD-POS-001 position_sizing_engine（标的层委托件，node 10619503）。
- MOD-POS-010 position_limit_enforcer（标的层否决委托件，node 10619504）。
- MOD-POS-013 position_risk_budget_allocator（组合层委托件，node 10619513）。
- MOD-POS-018 intraday_position_constraint（动态层委托件，node 10619507）。

## 4. 验收标准

- 单测全绿（四层全过最保守 min 收敛/任一层拒绝即终审拒绝/层异常 Fail-Closed/
  幂等同请求同令牌不重复签发/旁路令牌缺失或不符检测/畸形请求 Fail-Closed）；
  tests/position 零回归。

---

## 5. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
