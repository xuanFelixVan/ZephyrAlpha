---
module_id: MOD-SELL-009
title: "卖出紧迫度评分器蓝图 — 信号→紧迫度→执行策略映射"
doc_type: blueprint
status: Active
version: "0.1.2"
design_maturity: production
build_status: stable
ttl: permanent
layer: L03_sell_decision
layer_name: sell_decision
functional_domain: sell_decision
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
---

# MOD-SELL-009 | Sell Urgency Scorer 卖出紧迫度评分器

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P0 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: stable | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-009

## 1. 模块定位

卖出紧迫度评分器——基于卖出信号来源类型映射紧迫度(0~1), 并匹配执行策略(市价单/限价单+时间限制/限价单+耐心), 消费 SELL-08 仲裁结果增强(强冲突提升紧迫度)。

插入位置: D-SELL-DECISION 融合仲裁层(第三层), 与 SELL-08 并列(都消费 SellSignal), 额外消费 SELL-08 的 ArbitrationResult 做冲突增强。

依据: `D:\临时工作区\依赖图\31-D-SELL-DECISION-卖出决策域.md` §1.4 SELL-09

## 2. 不变量 (INVARIANTS)

- **最紧急决定原则**: 多信号取最大紧迫度(最紧急的信号决定整体紧迫度)
- **紧迫度∈[0,1]**: 0=最从容, 1=最紧急
- **风控优先**: 风控强制卖出(source含RISK/metadata.risk_force)→紧迫度=1.0
- **执行策略匹配**: urgency>0.8→市价单; 0.5~0.8→限价+时间限制; <0.5→限价+耐心
- **冲突增强**: 强冲突(STRONG)仲裁结果→urgency提升至≥0.9
- **隔离故障**: 单标的评分异常不阻断其他标的

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidUrgencyInputError | ZA-SELL-0009 | 输入信号列表为空或含非法值 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 消费 | MOD-SELL-001 SellSignalCollector | SellSignal | 卖出信号(含 signal_type) |
| 消费 | MOD-SELL-008 SellConflictArbitrator | ArbitrationResult | 仲裁结果(冲突等级增强紧迫度) |
| 产出 | D-EX-CORE | SellUrgencyScore | 执行策略选择依据 |
| 产出 | MOD-SELL-007 融合引擎(后建) | SellUrgencyScore | 融合参考 |
| 产出 | D-POSITION | SellUrgencyScore | 仓位状态联动 |

## 5. 紧迫度映射规则

| signal_type | 紧迫度 | 等级 | 说明 |
|-------------|:------:|------|------|
| MAIN_FORCE_DISTRIBUTION | 1.0 | URGENT | 主力弃庄→紧急清仓 |
| BREAKOUT_FAILURE | 1.0 | URGENT | 第K次挑战失败K≥3→强制清仓 |
| FUNDAMENTAL | 0.6 | MODERATE | 基本面恶化→中等 |
| TECHNICAL | 0.6 | MODERATE | 技术面卖出→中等 |
| VOLUME_PRICE_DIVERGENCE | 0.6 | MODERATE | 量价背离→中等 |
| RELATIVE_STRENGTH | 0.6 | MODERATE | 相对强弱→中等 |
| OPPORTUNITY_COST | 0.3 | RELAXED | 止盈/置换→从容 |
| TIME_STOP | 0.3 | RELAXED | 时间止损→从容 |
| source含RISK/metadata.risk_force | 1.0 | URGENT | 风控强制→紧急 |

## 6. 执行策略匹配

| 紧迫度范围 | 执行策略 | 说明 |
|-----------|---------|------|
| > 0.8 | MARKET_FAST | 市价单快速执行(紧急清仓) |
| 0.5 ~ 0.8 | LIMITED_TIME | 限价单+时间限制(中等) |
| <= 0.5 | PATIENT_LIMIT | 限价单+耐心等待(从容) |

## 7. 接口

### 输入
```python
scorer.score(
    sell_signals: list[SellSignal],
    arbitration_results: list[ArbitrationResult] | None = None,  # 来自 SELL-08
    now: datetime | None = None,
) -> list[SellUrgencyScore]
```

### 输出数据模型
```python
@dataclass(frozen=True)
class SellUrgencyScore:
    symbol: str
    urgency: float                    # [0,1]
    level: UrgencyLevel               # URGENT/MODERATE/RELAXED
    strategy: ExecutionStrategy       # MARKET_FAST/LIMITED_TIME/PATIENT_LIMIT
    dominant_signal_type: SellSignalType  # 主导信号类型(最紧急的)
    contributing_count: int           # 贡献信号数
    conflict_enhanced: bool           # 是否经冲突增强
    reason: str
    timestamp: datetime
```

## 8. 设计决策

| 决策 | 理由 |
|------|------|
| 基于 signal_type 映射紧迫度 | 信号来源类型直接反映紧急程度(主力弃庄>技术面>止盈) |
| 多信号取最大紧迫度 | 最紧急的信号决定执行节奏, 避免被从容信号拖累 |
| 消费 SELL-08 仲裁结果增强 | 强冲突(风控/主力)应提升紧迫度, 与仲裁分级一致 |
| 执行策略三档 | 匹配 D-EX-CORE 执行能力: 市价(快)/限价+时限(中)/限价+耐心(慢) |
| 紧迫度映射可配置 | 不同策略类型止损范式不同(SELL-14), 阈值需可调 |

## 9. 测试计划

- 单信号紧迫度映射(8类 signal_type 各档)
- 风控信号→1.0
- 多信号取最大紧迫度
- 执行策略三档匹配
- 冲突增强(STRONG→urgency≥0.9, WEAK不增强)
- 无仲裁结果时正常评分
- 多标的混合
- 输入校验(空列表抛错)
- 单标的异常隔离
- 紧迫度映射可配置

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-009`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-009` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SELL-009` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-009 | MOD-SELL-009 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/sell_decision/core/sell_urgency_scorer.py` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


