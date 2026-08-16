---
module_id: MOD-PA-006
title: "分批建仓引擎 — C-031置信度驱动分批建仓+尾盘集中执行+限价锚定+资金pro-rata兜底"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L2_domain
functional_domain: pf_alloc
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-13"
last_updated: "2026-08-13"
priority: P1
blueprint_level: module
actual_disk_path: src/zephyr/pf_alloc/batched_position_builder.py
belongs_to: ""
depends_on: [MOD-POS-021]
ssot_claims:
  - {claim: "C-031置信度→批次比例映射算法唯一真源", scope: "module"}
  - {claim: "突破失败/支撑破位检测算法唯一真源", scope: "module"}
  - {claim: "买入时序调度+限价锚定+资金pro-rata削减+多标的排序算法唯一真源", scope: "module"}
  - {claim: "Batch/BatchedEntryPlan 数据契约唯一真源", scope: "module"}
responsibility_domain: 
design_maturity: production
build_status: stable
language: zh
generation: 1
summary: "BM-BUY-04 分批建仓引擎：消费 31 号 FirmTargetPortfolio，C-031 置信度驱动 2 批/激进 1 批，尾盘 14:50-14:57 集中执行，限价锚定，资金 pro-rata 兜底，突破失败降级联动 42 号"
---
# Batched Position Builder 蓝图+施工图 — 分批建仓引擎 — C-031置信度驱动分批建仓+尾盘集中执行+限价锚定+资金pro-rata兜底

> module_id: MOD-PA-006 | version: 0.1.1 | status: Active | layer: L2_domain (pf_alloc)
> actual_disk_path: src/zephyr/pf_alloc/batched_position_builder.py | generation: 1
> 设计真源: 41_buy_flow v1.7.0 §3.2-§3.6 | 施工性质: 回填蓝图（代码已完工，83用例通过，2026-08-13 补建，遗留项 #29）

## 概述 <!-- temporal_type: permanent -->
本蓝图描述分批建仓引擎——它解决"拿到 31 号产出的 FirmTargetPortfolio 后，怎么把单子打进去"的问题（BM-BUY-04）。核心职责：C-031 置信度驱动的批次比例划分（激进 1 批/分批 2 批）、尾盘集中执行时序调度（14:50-14:57 主窗口+收盘竞价兜底）、限价锚定（突破略低/回踩略高/VWAP 兜底）、资金不足 pro-rata 削减与多标的下单排序、突破失败降级检测。当前规模单标的几万~几十万，目标容量单标的数十万级（无需拆单）。上游依赖 MOD-POS-021（FirmTargetPortfolio），下游被 40_execution_broker（订单执行）与 42_sell_flow（突破失败降级联动）消费。

> **标准锚点（防幻觉）**——蓝图模板：blueprint_construction_template.md v2.1.0；设计真源：41_buy_flow.md v1.7.0 §3.2-§3.6；机器真源：PostgreSQL depgraph（`python scripts/governance/extract_depgraph.py --modules MOD-PA-006`）。

## §0 代码对齐验证 <!-- temporal_type: permanent -->
### §0.1 代码文件清单
<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> 本节为自动生成（派生自 depgraph.nodes），禁止手写。生成命令：`python scripts/governance/extract_depgraph.py --modules MOD-PA-006`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 归属判定 | 阻塞原因 |
|---|--------|------------|------|:-----:|---------|---------|
| 1 | （占位——AUTOGEN 生成；当前实现为 batched_position_builder.py 单文件） | §3.1 | 分批建仓引擎全部算法+契约+编排入口 | 已实现 | 本模块 | — |
### §0.2 对齐验证矩阵
| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| 蓝图类/函数名 = 代码类/函数名 | §4.1 签名逐一比对 batched_position_builder.py | ✅ |
| 代码 [BLUEPRINT] 头 = 本蓝图 module_id | 代码头 `# [BLUEPRINT] MOD-PA-006` | ✅ |
| §4.2 数据模型在 SSoT 文件中存在 | `grep "class Batch\|class BatchedEntryPlan"` | ✅ |
| §0.1 文件职责无重叠、归属无 ⚠️ | 单文件模块 | ✅ |
| §5.5 触发机制状态与代码一致 | 逐操作核对 | ✅ |
### §0.3 版本-代码映射
| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (基线回填) | 6 算法 + 2 数据契约 + BatchedPositionBuilder 编排入口全部已实现 | — | — |
### §0.4 SSoT与责任唯一性声明
| # | 声明维度 | 本蓝图是真源 | 真源在别处（委托） | 委托目标 |
|---|---------|:----------:|:---------------:|---------|
| 1 | 分批比例/时序/锚定/资金兜底算法 | ✅ | ❌ | — |
| 2 | 目标仓位权重计算（Kelly/裁剪） | ❌ | ✅ | MOD-POS-021 / MOD-POS-001（31 号 §2.6） |
| 3 | Batch/BatchedEntryPlan 数据契约 | ✅ | ❌ | — |
| 4 | 卖出止损动作执行 | ❌ | ✅ | 42_sell_flow（BM-SELL-01/04-B） |
### §0.5 代码目录唯一性声明
| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/pf_alloc/`（与 frontmatter.actual_disk_path 一致） |
| 2 | 已知副本目录 | 无 |
| 3 | 副本处置状态 | 无副本 |
### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PA-006`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PA-006` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-PA-006` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PA-006 | MOD-PA-006 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | 1 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

## §1 设计背景与目标 <!-- temporal_type: permanent -->
### 1.1 背景
选股→仓位→执行三段已由 31 号分层裁定框架定稿并产出 FirmTargetPortfolio，但"拿到目标组合后怎么把单子打进去"——分几批、什么时点、锚什么价、资金怎么排——在 41 号 v1.0.0 前无 spec。41 号 §3.2-§3.6 给出裁定（置信度驱动 2 批+尾盘集中+限价锚定+消费 31 产出+T+1 约束），v1.7.0 已落码为本模块。
### 1.2 目标范围
| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | C-031→批次比例映射（A/B/C 调节）+突破失败检测+尾盘时序+限价锚定+pro-rata 削减+下单排序 | 41 §3.2-§3.6 算法全部已落码 |
| 2 | ❌ 排除 | 仓位重算（Kelly/约束裁决） | 归 31 号 MOD-POS-001/021（三维度解耦） |
| 3 | ❌ 排除 | 读市场态 regime / 卖出执行 / TWAP/VWAP 拆单 | 41 §3.7/§4.2/§5.2 裁定 |
### 1.4 运行场景约束
| 约束 | 影响 |
|------|------|
| A 股 T+1 不能做空 | 批次间隔≥1 交易日天然满足；首仓当日不可止损卖出 |
| 上交所 2026 修订交易规则 §2.4.2 | 执行窗口细分：14:50-14:55 挂单 / 14:55-14:57 撤改 / 14:57-15:00 收盘竞价不可撤单 |
| 程序化交易新规（高频认定 300 笔/秒 OR 20000 笔/日） | 限价+尾盘集中天然合规（单标的 1-2 笔/日） |
| 打板容量极小（单票几万~几十万） | 限价单、不拆单、避免冲击 |
### 1.5 利益相关者映射
| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| ZephyrAlpha-Owner | 买入流裁定与阈值校准 | 设计+校准 | 契约破坏性变更审批权 |
| 40_execution_broker | 订单计划可执行性 | 消费 | 按 §3.4 窗口执行 |
| 42_sell_flow | 突破失败降级联动 | 消费 | 止损动作归卖出侧 |
### 1.6 当前态/目标态差距
| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 核心算法 | 6 算法全部已实现并通过测试 | 同左 | 无差距 | — |
| 阈值校准 | daban 0.75/multifactor 0.65/event 0.70 初始值 | G04 策略定稿后按回测校准 | 校准未执行 | P2 |
| A/B/C 映射 | ±0.1 初始值已集成 | C1 实盘校准 | 校准未执行 | P2 |
### 1.7 典型场景
| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 高置信度建仓 | C-031≥阈值 | compute_batch_split→AGGRESSIVE 1 批→build_plan | BatchedEntryPlan(1 批,首仓≥70%) |
| 低置信度建仓 | C-031<阈值 | compute_batch_split→SCALED 2 批→check_batch2_release 2/3 条件 | BatchedEntryPlan(2 批,首仓30-50%) |
| 尾盘执行 | 14:50 时钟事件 | schedule_buy_orders→PLACE_LIMIT→compute_anchor_price 限价 | (指令,说明)+锚定价 |
| 突破失败 | 连续 2 根收盘<入场价 | check_degrade→BREAKOUT_FAILED→暂停确认仓 | 降级三元组→42 号联动 |
## §2 模块边界 <!-- temporal_type: permanent -->
### 2.1 职责边界
> **核心职责声明**：本蓝图的核心职责是 `把 FirmTargetPortfolio 目标权重拆成"什么时候下多少单"（分批节奏/时序/锚定/资金兜底/降级检测）`。职责数量：3。

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 批次划分与放行 | C-031+A/B/C→首仓比例；2/3 条件放行确认仓 | 本模块 |
| 2 | ✅ 包含 | 执行时序与价格锚定 | 14:50-15:00 四段窗口调度；突破/回踩/VWAP 三档锚定 | 本模块 |
| 3 | ✅ 包含 | 资金兜底与降级检测 | pro-rata 削减；多标的排序；突破失败/支撑破位检测 | 本模块 |
| 4 | ❌ 排除 | 仓位计算 | 目标权重由 31 号产出，本模块只消费不重算 | MOD-POS-021/001 |
| 5 | ❌ 排除 | 卖出/止损执行、纪律闸检测 | 降级只暂停批次；四项严禁检测归 BM-BUY-08 | 42_sell_flow / BM-BUY-08 |

#### 职责唯一性声明
| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 分批建仓批次比例算法 | [MOD-POS-021, MOD-POS-001] | `python scripts/governance/check_ssot_uniqueness.py --blueprint MOD-PA-006` |
| 突破失败检测（买入侧暂停语义） | [42_sell_flow 各卖出模块] | 同上（42 号消费本模块判定结果，不重复实现） |
## §3 架构设计 <!-- temporal_type: permanent -->
### 3.1 组件架构
| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | compute_batch_split / detect_breakout_failure | 置信度→批次比例映射 / 突破失败检测 | 阈值常量 / position 行情属性 | 纯函数 |
| 2 | schedule_buy_orders / compute_anchor_price | 尾盘四段时序调度 / 限价锚定三档计算 | 窗口常量 / 当日分钟 K 线 | 纯函数 |
| 3 | clip_to_available_capital / rank_buy_orders | 资金 pro-rata 削减 / 多标的下单排序 | 资金与评分字典 | 纯函数 |
| 4 | BatchedPositionBuilder | 编排入口（计划构建/放行检查/降级检查） | 上述 6 纯函数 | 同步调用 |
### 3.2 数据流
| # | 上游 | 处理逻辑 | 下游 | 数据格式 | 转换规则 |
|---|--------|---------|---------|---------|---------|
| 1 | MOD-POS-021 FirmTargetPortfolio | ①clip_to_available_capital→②rank_buy_orders→③build_plan(compute_batch_split) | BatchedEntryPlan→40_execution_broker | dict/frozen dataclass | 权重和≤总仓位上限→批次 weight_fraction 和=1.0 |
| 2 | L0 行情（收盘价/最低价/量比） | ①check_batch2_release→②check_degrade | 降级信号→42_sell_flow | tuple/None | 连续 2 根收盘确认防假跌破 |
### 3.3 状态生命周期
Batch.status 四态：`PENDING → FILLED / DEGRADED / CANCELLED`。

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| PENDING | 批次成交回报 | FILLED | 成交数量=批次计划数量 |
| PENDING | 突破失败/支撑破位 | DEGRADED | detect_breakout_failure 返回非 None |
| PENDING | 纪律闸拦截 | CANCELLED | BM-BUY-08 Hard Block |
## §4 接口契约 <!-- temporal_type: permanent -->
> 数据契约为 frozen dataclass（41 §3.2.3 契约原样落码，与交易域既有惯例一致，见 §16 D-PA006-01）。

### 4.1 公共 API
```python
class BatchedPositionBuilder:
    """分批建仓引擎——消费 FirmTargetPortfolio，产出分批计划/放行判定/降级判定"""
    def __init__(self, discipline_guard: DisciplineGuard | None = None, kill_switch: KillSwitchLite | None = None): ...  # AI-ASM-001 接线：纪律闸可选注入
    def build_plan(self, symbol: str, total_weight: float, confidence_score_c031: float, strategy_type: str, sector_quality: str | None = None) -> BatchedEntryPlan: ...
    def check_batch2_release(self, plan: BatchedEntryPlan, position: Any, volume_ratio: float, days_since_first_batch: int) -> bool: ...
    def check_degrade(self, position: Any, lookback_days: int = 10, confirm_bars: int = 2) -> tuple[str, str, str] | None: ...
    def gate_batch_order(self, order: OrderRequest, ctx: DisciplineContext, *, today: date | None = None) -> DisciplineVerdict: ...  # AI-ASM-001 接线：每批下单前过 BM-BUY-08 纪律闸（41 §2.3/§3.1，43 §4.3）

def compute_batch_split(confidence_score_c031: float, strategy_type: str, sector_quality: str | None = None) -> dict[str, Any]: ...
def detect_breakout_failure(position: Any, lookback_days: int = 10, confirm_bars: int = 2) -> tuple[str, str, str] | None: ...
def schedule_buy_orders(batched_plan: BatchedEntryPlan, current_time: time) -> tuple[str, str]: ...
def compute_anchor_price(symbol: str, buy_type: str, level_price: float, intraday_bars: list[Any], current_time: time) -> float: ...
def clip_to_available_capital(target_holdings: dict[str, float], available_cash: float, total_account_value: float) -> dict[str, float]: ...
def rank_buy_orders(target_holdings: dict[str, float], confidence_scores: dict[str, float], liquidity_scores: dict[str, float]) -> list[str]: ...
```
| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `compute_batch_split()` | ①A/B/C 调节置信度（41 §3.2.1）→②按策略类型取激进阈值→③≥阈值 AGGRESSIVE 1 批 / <阈值 SCALED 2 批 | 步骤③阈值分支 |
| `detect_breakout_failure()` | ①取前低（41 §3.3）→②连续 2 根收盘<前低→SUPPORT_BROKEN→③连续 2 根收盘<入场价→BREAKOUT_FAILED | 支撑破位优先于突破失败（41 v1.7.0 修正） |
| `schedule_buy_orders()` | ①<14:50 WAIT→②14:50-14:55 PLACE_LIMIT→③14:55-14:57 CHECK_AND_AMEND→④14:57-15:00 CLOSING_AUCTION_ONLY→⑤AFTER_HOURS（41 §3.4） | 14:57 不可撤单分界 |
| `compute_anchor_price()` | ①累计 VWAP→②BREAKOUT 锚压力位×0.99-1.00→③PULLBACK 锚支撑位×1.00-1.01→④兜底 min(目标价,VWAP)（41 §3.5） | 突破略低/回踩略高方向相反 |
| `clip_to_available_capital()` | ①目标投资额≤可用资金→原样返回→②否则 scale=可用/目标，非 CASH 权重按比例缩，CASH 补足（41 §3.6） | 保相对排序不抹零 |
| `rank_buy_orders()` | ①剔除 CASH→②流动性升序→③置信度降序→④权重降序（41 §3.6） | 流动性差先挂防无对手盘 |
| `build_plan()` | ①compute_batch_split→②AGGRESSIVE 单批 / SCALED 双批（确认仓挂 2/3 触发条件）→③sector_quality=None 记 degrade_reason | 编排 §3.2.1+§3.2.3 |
| `check_batch2_release()` | ①激进模式直返 False→②三条件计数（距首仓≥1 交易日/回落不破入场价/量比<1）→③≥2 项放行（41 §3.2.2） | 2/3 阈值 |
| `gate_batch_order()` | ①闸未注入→DisciplineGuardError（Fail-Closed）→②KillSwitchLite 熔断→HARD_BLOCK→③委托 DisciplineGuard.check（41 §2.3/§3.1，43 §4.3，AI-ASM-001 接线） | 熔断先于检测 |
### 4.2 数据模型
```python
@dataclass(frozen=True)
class Batch:
    batch_id: int                    # 1=首仓, 2=确认仓
    weight_fraction: float           # 占 total_weight 的比例（和=1.0）
    trigger_conditions: list[str]    # 2/3 条件
    status: str = "PENDING"          # PENDING / FILLED / DEGRADED / CANCELLED

@dataclass(frozen=True)
class BatchedEntryPlan:
    symbol: str
    total_weight: float              # 来自 FirmTargetPortfolio
    batches: list[Batch]
    confidence_tier: str             # AGGRESSIVE / SCALED
    degrade_reason: str | None = None
```
| 模型名 | SSoT文件 | 其他定义位置 | 状态 |
|--------|---------|------------|------|
| Batch | batched_position_builder.py | — | ✅ 唯一源 |
| BatchedEntryPlan | batched_position_builder.py | — | ✅ 唯一源 |
### 4.3 输入契约
| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `compute_batch_split()` | `confidence_score_c031` / `strategy_type` / `sector_quality` | ✅/✅/❌ | [0,1]；策略类型决定阈值（默认 0.70）；A/B/C 或 None=降级 |
| `detect_breakout_failure()` | `position` | ✅ | 须有 entry_price/low_prices/close_prices 属性 |
| `schedule_buy_orders()` | `current_time` | ✅ | datetime.time |
| `compute_anchor_price()` | `intraday_bars` | ✅ | 元素须有 close/volume 属性；空列表回退 level_price |
| `clip_to_available_capital()` | `target_holdings` | ✅ | 含 "CASH" 键的权重字典 |
| `rank_buy_orders()` | 三字典 | ✅ | 三字典键集合须覆盖全部非 CASH 标的 |
### 4.4 输出契约
| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `build_plan()` | `BatchedEntryPlan`（批次 weight_fraction 和=1.0） | 错误码契约 ZA-PA-0006（BatchPlanError，代码头声明） |
| `clip_to_available_capital()` | 削减后权重字典（含 `_degrade_reason` 标记） | ZA-PA-0007（InsufficientCapitalError，代码头声明）；当前实现以降级标记代替抛出 |
| `check_batch2_release()` | bool（≥2/3 条件为 True） | — |
| `check_degrade()` | None 或 (降级类型,动作,联动) 三元组 | — |
| `gate_batch_order()` | `DisciplineVerdict`（PASS/WARNING/HARD_BLOCK+kill_switch_triggered） | ZA-CMP-0002（DisciplineGuardError，闸未注入 Fail-Closed，AI-ASM-001 接线） |
### 4.5 MCP 接口（条件可选）
本模块不暴露 MCP 接口。
### 4.6 契约版本
| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增函数/字段 | ✅ 向后兼容 | 不影响已有消费者 |
| 修改阈值常量（AGGRESSIVE_THRESHOLD/QUALITY_ADJUSTMENT） | ⚠️ 需通知 | G04/C1 校准后更新，patch+1 |
| 删除/重命名函数或契约字段 | ❌ 破坏性 | 需 Owner 审批+迁移方案 |

**变更通知**：破坏性变更→Owner 审批+蓝图 minor+1；兼容性变更→AI 自主+patch+1。
### 4.7 OCP 扩展点（条件可选）
本模块无 OCP 扩展点。预留演进替换点（41 §5.2）：`confidence_score_c031` 可平滑替换为 conformal 区间宽度（阶段 6）；`rank_buy_orders` 排序键可替换为 MAP-Elites specialist 选择器（阶段 7）。
## §5 约束条件 <!-- temporal_type: permanent -->
### 5.1 技术约束
| # | 约束 | 值 |
|---|------|-----|
| 1 | 激进阈值（按策略类型） | daban 0.75 / multifactor 0.65 / event 0.70 / 默认 0.70（41 §3.2.1，G04 校准来源） |
| 2 | A/B/C 置信度调节 | A +0.1 / B ±0.0 / C -0.1（41 §3.2.1，C1 校准来源） |
| 3 | 执行窗口 | 14:50-14:55 挂单 / 14:55-14:57 撤改 / 14:57-15:00 收盘竞价不可撤单 / 15:05-15:30 盘后仅人工 |
| 4 | 突破失败检测参数 | lookback_days=10 / confirm_bars=2（41 §3.3） |
| 5 | 不变量 | 批次比例和=1.0；首仓比例∈[0.30,1.0]；放行需 2/3 条件；限价为主市价仅应急；不读市场态 |
### 5.2 容量估算
| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 单标的资金 | 几万~几十万 | 数十万 | 一笔限价单 | ✅ | 41 §5.2 阶段 4 拆单（资金达数百万后） |
| 同时建仓标的数 | ≤10 | ≤30 | 排序 O(n log n) 无瓶颈 | ✅ | 无需扩展 |
| 日报单笔数 | 1-2 笔/标的 | <100 笔/日 | 法定 20000 笔/日 | ✅ | 天然合规 |
### 5.3 迁移/废弃方案（条件可选）
无迁移/废弃。
### 5.4 非功能需求与服务水平
| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 正确性 | 批次比例和 | =1.0 | 单测断言 | 比例和误差 | 0 | 0 次 | 测试失败即阻断 |
| 时效性 | 单标的计划构建耗时 | <10ms | 耗时日志 | 构建耗时 | 99%<10ms | 每日 1 次超限 | >50ms 告警 |
### §5.5 自动化触发机制
| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|---------|
| build_plan（盘前计划生成） | auto_scheduled | 盘前信号生成后调用 | ✅已实现 |
| schedule_buy_orders（窗口调度） | auto_event | 盘口时钟进入 14:50/14:55/14:57 分段 | ✅已实现 |
| check_batch2_release（放行检查） | auto_event | 确认仓触发条件评估时点 | ✅已实现 |
| check_degrade（降级检测） | auto_event | 日线收盘后评估 | ✅已实现 |
| clip/rank（资金兜底+排序） | on_demand | 下单编排时调用 | ✅已实现 |
### §5.7 禁止模式与导入约束
| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 重算仓位权重 | 只消费 FirmTargetPortfolio 权重数字 | 三维度解耦（how 层不越界 how much） |
| 2 | 编码模式 | 读 regime/市场态 | 只消费 budget 数字 | 41 §3.7 裁定 |
| 3 | 编码模式 | 市价单默认 | 限价单为主，市价仅应急轨+人工 | 41 §4.4 拒绝市价单为主 |
| 4 | 导入源 | zephyr.plan_engine.*（下游模块） | zephyr.position.core.*（上游） | 分层约束防循环 |
## §6 错误处理 <!-- temporal_type: permanent -->
| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 可用资金<目标投资额 | clip_to_available_capital 比较 | pro-rata 削减+`_degrade_reason` 标记，不中断 | 全部标的权重等比缩小 |
| 2 | 突破失败/支撑破位 | detect_breakout_failure 连续 2 根收盘确认 | 暂停确认仓/全部批次→联动 42 号止损评估 | 该标的后续批次 |
| 3 | 板块回踩数据未就绪 / 分钟 K 线为空 | sector_quality=None / cum_volume=0 | 纯 C-031 降级 / VWAP 回退 level_price | 单计划/单次锚定 |
| 4 | 依赖循环声明 | — | 本模块只依赖上游 31 号产出，无 A→B→A 循环 | — |
### 6.1 可观测性规格
| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| batch_plan_build_total | Counter | 手动上报 | — | P3 |
| batch_degrade_total（按类型） | Counter | 手动上报 | 单日>3 | P2 |
| capital_clip_scale | Gauge | 手动上报 | <0.8 | P2 |
### 6.2 退化矩阵
| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| A/B/C 调节输入（22 号） | 纯 C-031 驱动分批 | 置信度微调 | sector_quality=None 降级 | 22 号数据恢复 |
| VWAP 锚定（行情缺失） | 技术位锚定 | VWAP 兜底档 | 回退 level_price | 行情恢复 |
| 突破失败检测（价格序列不足） | 其余算法 | 降级检测 | 返回 None 不暂停 | 序列长度≥confirm_bars |
## §7 安全考量 <!-- temporal_type: permanent -->
| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 盘中假跌破触发误降级 | 中 | 连续 2 根收盘确认（41 §3.3） | 单测覆盖假跌破场景 |
| 2 | 14:57 后改单失败 | 高 | 14:55-14:57 窗口完成撤改，收盘竞价段只补单 | schedule_buy_orders 分段单测 |
| 3 | 追高买入 | 高 | 突破锚压力位略低+限价为主+BM-BUY-08 纪律闸 | compute_anchor_price 区间断言 |
## §8 测试策略 <!-- temporal_type: permanent -->
| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | 6 算法+2 契约+编排类 | TestComputeBatchSplit（激进/分批/ABC调节/阈值边界）、TestDetectBreakoutFailure（支撑破位优先/连续2根确认）、TestScheduleBuyOrders（五段窗口）、TestComputeAnchorPrice（三档+空bars回退）、TestClipToAvailableCapital（充足/不足/scale）、TestRankBuyOrders（三级排序键）、TestDataclassContracts（frozen不变量）、TestBatchedPositionBuilder（编排+2/3放行） | 42/42 通过 |
| 2 | 回归验证 | 41 号施工全体 | 3 个测试文件连续 2 轮全过（41 v1.7.0 记录） | 83/83 通过 |

测试文件：`tests/pf_alloc/test_batched_position_builder.py`（42 用例）。
## §9 依赖关系 <!-- temporal_type: permanent -->
### 9.1 依赖声明
| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-POS-021 | 必须 | FirmTargetPortfolio（31 号 §2.6 产出） | ≥0.1.0 | `docs/03_modules/_domain_position/firm_risk_aggregator/blueprint.md` |
| 41_buy_flow 设计备忘 | 必须 | §3.2-§3.6 算法伪代码与参数 | v1.7.0 | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/41_buy_flow.md` |
### 9.2 依赖图对齐声明
| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §9.1 依赖声明 ↔ depgraph.nodes | 依赖条目在 depgraph 有对应节点 | 已对齐 | `python scripts/governance/extract_depgraph.py --modules MOD-PA-006` |
| 2 | §10 产出物路径 ↔ path_mappings | 路径一致 | 已对齐 | 同上 |
### 9.5 概念重叠声明
| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | 突破失败判定 | 检测逻辑 | 42_sell_flow（BM-SELL-01/04-B） | 42 号委托本模块（判定一次，结果共享，扳机清单同源去重） | 已处置 |
| 2 | 总仓位裁剪 | pro-rata 削减 | MOD-POS-021 硬上限裁剪 | 共存（31 号管组合级裁剪，本模块管资金可用性兜底，哲学同源 32 号 §2.4） | 已处置 |
### 9.6 依赖链风险评级
| # | 依赖链 | 链深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:-----:|---------|---------|---------|
| 1 | MOD-PA-006→MOD-POS-021 | 2 | L1 | 无（链深≤2 免熔断） | 不适用 |
## §10 产出物存放目录 <!-- temporal_type: permanent -->
| 产出物类型 | 存放完整路径（相对优先） | 职责 | consumer_min | 注册位置 |
|----------|---------------|------|:-----------:|---------|
| 蓝图文件 | `docs/03_modules/_domain_pf_alloc/batched_position_builder/blueprint.md` | 本文件 | ≥0 | blueprint_registry.yaml |
| 业务代码 | `src/zephyr/pf_alloc/batched_position_builder.py` | 分批建仓引擎（6 算法+2 契约+编排类） | ≥1 | `src/zephyr/pf_alloc/` 包 |
| 测试代码 | `tests/pf_alloc/test_batched_position_builder.py` | 42 用例 | ≥0 | pytest 自动发现 |

## §11 集成目标 <!-- temporal_type: permanent -->
| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| 40_execution_broker | 产出订单计划 | BatchedEntryPlan→限价单执行 | 计划字段完整性校验 |
| 42_sell_flow | 降级联动 | detect_breakout_failure 结果→BM-SELL-01/04-B | 降级三元组契约单测 |
| MOD-TRIG-001 扳机清单 | 触发器注册 | BUY_BATCH2_RELEASE/BUY_BREAKOUT_FAIL 条件函数 | test_trigger_registry 同源去重用例 |

## §12 需要更新的相关内容 <!-- temporal_type: permanent -->
| # | 需更新的文件 | 完整路径（相对优先） | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | 新增 MOD-PA-006 条目 | 回填登记 |
| 2 | 依赖图 | PostgreSQL depgraph | MOD-PA-006 节点核验 | 五图对齐 |

## §13 已知风险与缓解 <!-- temporal_type: permanent -->
| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 激进阈值为初始值未经实盘校准 | 中 | 中 | 首仓 30-50% 试单兜底+G04 回测校准后更新常量 | 风险 |
| 2 | VWAP 用 close×volume 分钟近似 | 低 | 低 | MVP 精度可接受，演进路径升级逐笔 | 负面后果 |
| 3 | compute_anchor_price 用 random.uniform 引入非确定性 | 低 | 低 | 区间 [0.99,1.00]/[1.00,1.01] 有界，测试断言区间 | 负面后果 |

## §14 施工指引 <!-- temporal_type: construction_temporary（施工已完成，本节保留状态记录） -->
### 14.1 施工策略
| 项目 | 内容 |
|------|------|
| 施工阶段数 | 单 Phase 一次性完成（AI-BUY-001，41 号 v1.7.0 施工批次） |
| 施工模式 | 新建 |
| 核心风险 | 算法顺序（支撑破位 vs 突破失败优先级）——已在 41 v1.7.0 修正 |
| 目标 generation | 1 |
### 14.2 前置条件
| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | 41_buy_flow v1.7.0 定稿 | hard | 已定稿 | ✅ |
| 2 | MOD-POS-021 FirmTargetPortfolio 契约 | soft | 蓝图已登记 | ✅ |
### 14.3 实施步骤
回填蓝图，施工已完成：步骤 1（6 算法落码）已完成；步骤 2（2 数据契约）已完成；步骤 3（编排类）已完成；步骤 4（42 用例）已完成。验证命令：`python -m pytest tests/pf_alloc/test_batched_position_builder.py -q`。
### 14.4 回滚方案
| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 全部 | 算法行为偏离 41 号伪代码 | 以 41 §3.2-§3.6 伪代码为基准修复并重跑 42 用例 |
### 14.5 施工完成与生产就绪标准
| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | 代码文件存在且非空 | `src/zephyr/pf_alloc/batched_position_builder.py` 存在 | 完成 | ✅ |
| 2 | 测试通过 | 42/42 exit 0 | 完成 | ✅ |
| 3 | 代码头十五字段完整 | [BLUEPRINT] MOD-PA-006 等字段齐全 | 就绪 | ✅ |
### 14.6 施工状态
| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | 施工者（AI-BUY-001，2026-08-13） |
| verification_status | passed | 审计者（83 用例连续 2 轮全过，41 v1.7.0 记录） |
| code_alignment_verified | yes | 审计者（§4 签名与代码逐一比对一致） |
### 14.7 参考实现规格
| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | C-031→批次比例映射 | 算法 | 41 §3.2.1 伪代码为精确规格：A/B/C 调节±0.1→clamp[0,1]→阈值分支→AGGRESSIVE 首仓 min(0.70+(adj-th),1.0)/SCALED 首仓 0.30+(adj/th)×0.20 | compute_batch_split |
| 2 | 突破失败检测 | 算法 | 41 §3.3 伪代码+v1.7.0 顺序修正：SUPPORT_BROKEN 先于 BREAKOUT_FAILED 检查 | detect_breakout_failure |
| 3 | 尾盘时序五段 | 算法 | 41 §3.4 窗口表：WAIT/PLACE_LIMIT/CHECK_AND_AMEND/CLOSING_AUCTION_ONLY/AFTER_HOURS | schedule_buy_orders |
| 4 | 三档锚定 | 算法 | 41 §3.5：VWAP=Σ(close×vol)/Σvol；突破×[0.99,1.00]；回踩×[1.00,1.01]；兜底 min(目标价,VWAP) | compute_anchor_price |
| 5 | pro-rata 削减+三级排序 | 算法 | 41 §3.6：scale=available/target_invest；排序键(流动性升,置信度降,权重降) | clip_to_available_capital / rank_buy_orders |
### 14.8 施工参考卡
| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/pf_alloc/test_batched_position_builder.py -q` | 回归验证 | 无 | 42 passed |
| 2 | 常量 | `AGGRESSIVE_THRESHOLD` | 策略类型→激进阈值 | dict[str,float] | 校准只改此表 |
### 14.10 故障与操作手册
| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 运行 | 计划降级标记出现 | sector_quality=None | 查 degrade_reason 字段 | 22 号数据就绪后传 A/B/C | 标记消失 |
| 2 | 运行 | 资金削减触发 | available_cash<target_invest | 查 `_degrade_reason` 中 scale | 资金到账后重算 | scale=1.0 |
### 14.12 并发操作模型
本模块为纯函数+无状态编排类，无并发操作。

## §15 容量升级附录 <!-- temporal_type: permanent -->
### §15.1 容量基线
| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 单标的资金规模 | 几万~几十万 | 账户对账 |
| 并发建仓标的数 | ≤10 | 计划构建日志 |
### §15.2 缺口清单与升级版本矩阵
| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-PA006-01 | 大资金需拆单 | 41 §5.2 阶段 4 TWAP/VWAP 拆单 | P2 | 单标的≥数百万 | v1.0.0 | 未触发 |

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.1.0 | 1 | 基线回填 | 6 算法+2 契约+编排类 | ✅ |

## §16 决策记录 <!-- temporal_type: permanent -->
| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-PA006-01 | 数据契约用 frozen dataclass 而非 Pydantic | A dataclass/B Pydantic | A | 41 §3.2.3 契约原文即 @dataclass；与交易域 MOD-TRADING-002/003 既有惯例一致；不可变+轻量 | 2026-08-13 |
| 2 | D-PA006-02 | 置信度驱动 2 批（非一次性满仓/非倒金字塔） | A 2 批/B 满仓/C 倒金字塔 | A | 41 §4.1/§4.2 拒绝理由：择时风险+左侧逆势不适用趋势策略 | 2026-08-10 |
| 3 | D-PA006-03 | 尾盘 14:50-14:57 集中执行（非盘中分散） | A 尾盘/B 盘中/C VWAP 峰 | A | 41 §3.4：T+1 资金成本最低+避开开盘波动与操纵检测窗口 | 2026-08-10 |
| 4 | D-PA006-04 | 支撑破位检查优先于突破失败 | A 破位优先/B 失败优先 | A | 41 v1.7.0 修正：收盘<前低必然<入场价，先查更严重情形 | 2026-08-13 |

## 必备链接 <!-- temporal_type: permanent -->
| # | 文件 | module_id | 完整路径（相对优先） | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 买入流 spec（设计真源） | — | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/41_buy_flow.md` | §3.2-§3.6 算法与参数 |
| 2 | 仓位分层裁定 | — | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/31_position_sizing.md` | FirmTargetPortfolio 口径 |
| 3 | 蓝图模板 | GOV-028 | `docs/01_policies_and_standards/templates/blueprint_construction_template.md` | v2.1.0 章节合规 |

## 术语表 <!-- temporal_type: permanent -->
| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| C-031 置信度 | 信号置信度评分 [0,1]，驱动批次比例 | A/B/C 板块回踩质量 | C-031 是主输入，A/B/C 只是 ±0.1 调节因子 |
| 首仓/确认仓 | batch_id=1 试探仓 / batch_id=2 条件放行仓 | 激进单批 | 激进模式只有首仓（≥70%），无确认仓 |
| 突破失败 | 连续 2 根收盘<入场价（但≥前低） | 支撑破位 | 支撑破位=连续 2 根收盘<前 10 日最低价，更严重 |
| 尾盘窗口 | 14:50-14:57 可撤单连续竞价段 | 收盘集合竞价 | 14:57-15:00 不可撤单，只补未成交 |

## 成熟度声明 <!-- temporal_type: permanent -->
| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | 41 号重大修订 | 6 算法已落码并通过测试 |
| 接口契约 | stable | 高 | 破坏性变更需 Owner 审批 | 签名与 41 号伪代码一致 |
| 数据模型 | frozen | 高 | 41 §3.2.3 契约修订 | frozen dataclass 原样落码 |
| 阈值参数 | evolving | 中 | G04/C1 校准完成 | 初始值未经实盘校准 |

## 版本演进路线图 <!-- temporal_type: permanent -->
| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 基线回填（代码先行，蓝图后补，遗留项 #29） | — | 已完成 |
| v1.0.0 | 阈值校准更新（G04/C1 产出后） | v0.1.0 | 未施工 |

## 已知问题与盲点登记 <!-- temporal_type: permanent -->
| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 激进/调节阈值未经实盘校准 | 中 | G04/C1 未产出 | 校准后更新常量并重跑 42 用例 | §5.1 #1/#2 | 未解决 |

## 自检与闭合清单 <!-- temporal_type: permanent -->
| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口执行流程引用 41 号节号 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §8 有对应测试 | 阈值/窗口/不变量→42 用例 | ✅ |
| 4 | 设计 | §0.1 代码文件在 §10 有对应产出物路径 | 单文件核对 | ✅ |
| 5 | 后 | 临时时态内容已清理 | 施工已完成，§14.3 仅留状态 | ✅ |

## 项目中已有类似功能 <!-- temporal_type: permanent -->
| # | 已有模块/文件 | 完整路径（相对优先） | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | MOD-POS-021 FirmRiskAggregator | `src/zephyr/position/core/firm_risk_aggregator.py` | 组合级权重裁剪 | 该模块管跨策略汇总+硬上限裁剪（how much），不管分批节奏/时序/锚定（how） |
| 2 | MOD-POS-006 CashManager | `docs/03_modules/_domain_position/cash_manager/blueprint.md` | T+1 资金口径 | 该模块管资金储备计算，不管下单拆分与排序 |

## 涉及的文件范围 <!-- temporal_type: permanent -->
| # | 文件/目录 | 完整路径（相对优先） | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 业务代码 | `src/zephyr/pf_alloc/batched_position_builder.py` | 读取 | 无变更（回填蓝图不改代码） |
| 2 | 测试代码 | `tests/pf_alloc/test_batched_position_builder.py` | 读取 | 无变更 |
| 3 | 蓝图文件 | `docs/03_modules/_domain_pf_alloc/batched_position_builder/blueprint.md` | 新建 | 本文件 |

## ⚠️ 安全删除协议 <!-- temporal_type: permanent -->
本蓝图不涉及任何文件废弃/迁移/删除。如未来涉及：禁止蓝图阶段物理删除；迁移型删除逐条迁移逐条验证；物理删除只在 stable 搬入阶段且人类确认后执行。

## ⚠️ Vibe Coding 蓝图编写铁律确认 <!-- temporal_type: permanent -->
本蓝图编写已逐条确认：全部路径项目根相对+正斜杠；必备链接完整列出；蓝图为最终设计结果；产出物路径与磁盘一致；涉及文件范围明确；全文无模糊指令词（铁律#6）；§0.1/§0.6 AUTOGEN 节保留生成说明未手写漂移；已实现代码不复制实现只保留签名（§4）；术语表齐备。

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 1.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/pf_alloc/test_batched_position_builder.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 变更记录
> 变更历史通过 Git log 追踪。v0.1.0（2026-08-13）：回填创建（遗留项 #29，41 号 v1.7.0 施工完成后补建）。
