---
module_id: MOD-SELL-008
title: "买卖冲突仲裁器蓝图 — 卖出优先保守原则+冲突分级"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: design
build_status: deprecated
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

# MOD-SELL-008 | Sell Conflict Arbitrator 买卖冲突仲裁器

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P0 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: stable | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-008

## 1. 模块定位

买卖冲突仲裁器——同标的同时存在买入信号与卖出信号时, 按"卖出优先(保守原则)"仲裁, 并对冲突分级(强冲突立即执行 / 弱冲突延迟观察), 产出可审计的仲裁结果。

插入位置: D-SELL-DECISION 融合仲裁层(第三层), 消费 SELL-01 的 SellSignal + 上游买入信号, 产出 E-SELL-02 SellArbitrated 事件。

依据: `D:\临时工作区\依赖图\31-D-SELL-DECISION-卖出决策域.md` §1.4 SELL-08, §4 E-SELL-02, §8 CTR-SELL-001

## 2. 不变量 (INVARIANTS)

- **卖出优先铁律**: 同标的买卖冲突时, 永远裁定卖出方胜出(防御优先于进攻)
- **强冲突立即执行**: 卖出信号来自主力出货/突破失败/风控强制 → verdict=SELL_PRIORITY, 不延迟
- **弱冲突延迟观察**: 卖出信号来自止盈/技术面/相对强弱 → verdict=DELAYED_OBSERVE, 延迟 ≤1 Tick
- **审计可追溯**: 每次仲裁产出 ArbitrationResult, 含冲突双方详情+裁决理由+胜出方
- **无冲突直通**: 同标的无买卖重叠 → verdict=NO_CONFLICT, 不阻断后续流程
- **隔离故障**: 单标的仲裁异常不阻断其他标的

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| InvalidArbitrationInputError | ZA-SELL-0008 | 输入信号列表含非法值(空symbol/confidence越界) |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 消费 | MOD-SELL-001 SellSignalCollector | SellSignal | 卖出信号(8类, 含signal_type) |
| 消费 | D-PF-CORE / D-SIGNAL | BuySignal(本模块定义轻量契约) | 买入信号, 后续对接跨域契约 |
| 消费(设计态) | MOD-SELL-007 融合引擎 | FusedSellDecision(后建时接入) | 当前基于SellSignal工作, SELL-007建好后增强 |
| 产出 | D-EX-CORE | E-SELL-02 SellArbitrated | 仲裁结果→执行 |
| 产出 | MOD-SELL-009 紧迫度评分器 | ArbitrationResult | 紧迫度参考冲突等级 |
| 产出 | D-GOVERNANCE | SellAuditReport | 审计追溯 |

## 5. 冲突分级规则

| 冲突等级 | 卖出信号来源(signal_type) | 仲裁动作 | 延迟 |
|---------|-------------------------|---------|------|
| STRONG | MAIN_FORCE_DISTRIBUTION(主力出货/弃庄) | SELL_PRIORITY 立即执行 | 0 |
| STRONG | BREAKOUT_FAILURE(突破失败/第K次K≥3强制清仓) | SELL_PRIORITY 立即执行 | 0 |
| STRONG | source 含 "RISK" 标识(风控强制卖出) | SELL_PRIORITY 立即执行 | 0 |
| WEAK | OPPORTUNITY_COST(止盈/置换) | DELAYED_OBSERVE 延迟观察 | 1 Tick |
| WEAK | TECHNICAL / RELATIVE_STRENGTH / VOLUME_PRICE_DIVERGENCE / FUNDAMENTAL / TIME_STOP | DELAYED_OBSERVE 延迟观察 | 1 Tick |
| NONE | 无买入信号或无卖出信号 | NO_CONFLICT 直通 | — |

**仲裁优先级**(D-SELL §1.4 约束, SELL-08 在链中位置):
风控 > C-047仓位上限 > 市场状态 > **卖出决策引擎(SELL-08)** > T+1预测 > ... > 买入决策

## 6. 接口

### 输入
```python
arbitrator.arbitrate(
    sell_signals: list[SellSignal],   # 来自 SELL-01
    buy_signals: list[BuySignal],     # 来自 D-PF-CORE/D-SIGNAL
    now: datetime | None = None,
) -> list[ArbitrationResult]          # 每个有冲突或信号的标的一条
```

### 输出数据模型
```python
@dataclass(frozen=True)
class ArbitrationResult:
    symbol: str
    verdict: ArbitrationVerdict       # SELL_PRIORITY / DELAYED_OBSERVE / NO_CONFLICT
    conflict_level: ConflictLevel     # STRONG / WEAK / NONE
    winning_side: Side                # SELL / BUY / NONE
    delay_ticks: int                  # 延迟观察tick数(强冲突0, 弱冲突1, 无冲突0)
    sell_signals: list[SellSignal]    # 涉及的卖出信号
    buy_signals: list[BuySignal]      # 涉及的买入信号
    reason: str                       # 人类可读裁决理由
    timestamp: datetime
```

## 7. 事件

| 事件ID | 事件名 | 触发条件 | 消费者 |
|--------|--------|---------|--------|
| E-SELL-02 | SellArbitrated | 买卖冲突仲裁完成(卖出优先/延迟观察) | D-EX-CORE, D-PF-CORE |

## 8. 设计决策

| 决策 | 理由 |
|------|------|
| 卖出优先(保守原则) | 防御永远优先于进攻, 卖比买紧急(§16仲裁优先级) |
| 强冲突基于 signal_type 判定 | MAIN_FORCE_DISTRIBUTION/BREAKOUT_FAILURE 是明确的强制卖出信号 |
| 弱冲突延迟1 Tick | 止盈/技术面卖出可观察确认, 避免误杀 |
| BuySignal 本模块定义轻量契约 | SELL-08 独立可测, 后续 D-PF-CORE 跨域契约就绪后替换 |
| 基于 SellSignal 而非 FusedSellDecision | SELL-07 未建, 接口先行; SELL-07 建好后增强消费融合意愿 |
| 审计字段内嵌 ArbitrationResult | 满足 D-GOVERNANCE 审计追溯要求, 无需额外审计模块 |

## 9. 测试计划

- 无冲突直通(NO_CONFLICT)
- 强冲突→SELL_PRIORITY 立即执行(主力出货/突破失败/风控)
- 弱冲突→DELAYED_OBSERVE 延迟1 Tick(止盈/技术面)
- 卖出优先铁律(冲突时永远卖出方胜出)
- 多标的混合(部分冲突部分无冲突)
- 输入校验(空symbol/confidence越界抛错)
- 单标的异常隔离(不阻断其他标的)
- 事件发布(E-SELL-02)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SELL-008`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SELL-008` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-SELL-008` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SELL-008 | MOD-SELL-008 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | deprecated | deprecated | ✅ |
| file_count | 2 文件 | N/A | — |

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
| — | — | 本模块尚无已实现代码 |

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


