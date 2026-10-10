---
blueprint_id: MOD-PF-012
module_id: MOD-PF-012
module_name: strategy_capacity_estimator
domain: D_PF_CORE
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_PF_CORE
path: src/zephyr/pf_core/core/strategy_capacity_estimator.py
granularity: file
responsibility_domain: 
---

# MOD-PF-012 strategy_capacity_estimator 蓝图（PC-08 Strategy Capacity Estimator 策略容量估算器）

> **module_id**: MOD-PF-012 | **域**: D_PF_CORE | **优先级**: P1
> **来源**: B3-05544（AUD-DRAFT-001-DIGEST P1 波 W-P1-21，CAND-PF004-005，D-PF-CORE §1.2）
> 代码：`src/zephyr/pf_core/core/strategy_capacity_estimator.py`

## 0. 定位

策略容量估算：ADV/参与率上限/换手率/冲击成本容忍度四约束合成策略容量
（AUM 上限），输出容量利用率 + 80% 预警线告警 + 扩容建议。

查重分工（W-P1-21 铁律⑤，TSV onsite=无）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| multifactor_constraint_arbitration | MOD-PF-002(族) | C5 单票 ≤ 日成交 5% **裁决常量**（C5_ADV_PARTICIPATION_MAX） | 单票硬约束常量；本件=策略级容量**估算器**（四约束合成+利用率+建议） |
| default_tca_engine | MOD-L07-001 | 事后交易成本分析（含 market_impact 桶） | 事后度量≠事前容量估算 |
| liquidity_crisis_manager | MOD-RK 族 | 盘中流动性危机处置 | 应急处置≠容量估算 |

## 1. 规则（确定性纯函数，数据全注入）

- **参与率约束**：AUM ≤ Σ_s adv_value(s) × participation_max / daily_turnover
  （日换手所需成交 ≤ 可参与成交额）。
- **冲击成本容忍**：平方根冲击模型 impact_bps = coef_bps × √participation
  （coef 默认 50，即 100% 参与率≈50bps 量级）；要求 impact ≤ tolerance_bps →
  participation ≤ (tolerance/coef)²；effective_participation =
  min(participation_max, 冲击上限)。
- **容量**：capacity = Σ adv × effective_participation / daily_turnover；
  binding_constraint ∈ {PARTICIPATION, IMPACT_TOLERANCE}。
- **利用率与预警**：utilization = current_aum / capacity；≥ warn_ratio（默认
  0.8）→ WARNING；≥ 1.0 → BREACH。
- **扩容建议（结构化枚举）**：binding=IMPACT_TOLERANCE → {REDUCE_TURNOVER,
  RELAX_IMPACT_TOLERANCE}；binding=PARTICIPATION → {EXPAND_UNIVERSE,
  REDUCE_TURNOVER}；BREACH 追加 DELEVERAGE。
- Fail-Closed：空 adv 表/非正 adv/非正 turnover/越界参与率/非有限值 →
  CapacityEstimationError。

## 2. 接口

- `CapacityConfig`（frozen）/ `CapacityAlertLevel` / `ExpansionAdvice`（枚举）
  / `StrategyCapacityReport`（frozen）
- `StrategyCapacityEstimator(config=None)`
  - `estimate(adv_values, daily_turnover, current_aum=0.0,
    participation_max=None, impact_tolerance_bps=None) -> StrategyCapacityReport`

## 3. 不做什么

不做事后 TCA（MOD-L07-001）、不做单票成交约束裁决（C5 常量）、不取行情
（ADV 注入）、不产交易指令。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 4.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §4（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
