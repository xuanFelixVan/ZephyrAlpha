---
module_id: MOD-PLAN-001
title: "明日预案引擎 — 盘后生成TomorrowBoundary操作边界（箱体上下沿+加仓上限+禁加仓/必出价位）"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L2_domain
functional_domain: plan_engine
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-13"
last_updated: "2026-08-13"
priority: P1
blueprint_level: module
actual_disk_path: src/zephyr/plan_engine/tomorrow_boundary_planner.py
belongs_to: ""
depends_on: []
ssot_claims:
  - {claim: "TomorrowBoundary 数据契约唯一真源", scope: "module"}
  - {claim: "盘后边界计算规则（箱体上沿/下沿/加仓上限/禁加仓/必出/突破验证）唯一真源", scope: "module"}
responsibility_domain: 
design_maturity: production
build_status: stable
language: zh
generation: 1
summary: "BM-PLAN-01 明日预案引擎：盘后收盘基于当日数据冷静计算明日操作边界 TomorrowBoundary，边界层（B/C）核心产出者，边界层坏=致命暂停操作"
---
# Tomorrow Boundary Planner 蓝图+施工图 — 明日预案引擎 — 盘后生成TomorrowBoundary操作边界（箱体上下沿+加仓上限+禁加仓/必出价位）

> module_id: MOD-PLAN-001 | version: 0.1.2 | status: Active | layer: L2_domain (plan_engine)
> actual_disk_path: src/zephyr/plan_engine/tomorrow_boundary_planner.py | generation: 1
> 设计真源: 41_buy_flow v1.7.0 §3.10.2 | 施工性质: 回填蓝图（代码已完工，83用例通过，2026-08-13 补建，遗留项 #29）

## 概述 <!-- temporal_type: permanent -->
本蓝图描述明日预案引擎——它解决"盘中操作没有冷静期计算的安全边界"的问题（BM-PLAN-01）。核心职责：盘后收盘后基于当日数据计算明日操作边界 TomorrowBoundary（箱体上沿/下沿、加仓仓位上限 30%、禁加仓价位、必出止盈价位、突破验证条件）。它是买入/卖出/仓位三流的共同上游边界提供者，设计哲学"边界比聪明更重要"——边界层坏=致命暂停操作，推演层坏=可接受机械执行边界。当前为 MVP 骨架实现（箱体=昨收±振幅），上游市场状态/预测/主力行为/情绪周期输入（BM-SEL-03/04/05/23）未就绪时按 None 降级。下游被 MOD-PLAN-002（盘前加载）与 BM-BUY-02/BM-SELL-02 消费。

> **标准锚点（防幻觉）**——蓝图模板：blueprint_construction_template.md v2.1.0；设计真源：41_buy_flow.md v1.7.0 §3.10.2；机器真源：PostgreSQL depgraph（`python scripts/governance/extract_depgraph.py --modules MOD-PLAN-001`）。

## §0 代码对齐验证 <!-- temporal_type: permanent -->
### §0.1 代码文件清单
<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> 本节为自动生成（派生自 depgraph.nodes），禁止手写。生成命令：`python scripts/governance/extract_depgraph.py --modules MOD-PLAN-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 归属判定 | 阻塞原因 |
|---|--------|------------|------|:-----:|---------|---------|
| 1 | （占位——AUTOGEN 生成；当前实现为 tomorrow_boundary_planner.py 单文件） | §3.1 | TomorrowBoundary 契约+边界计算 | 已实现 | 本模块 | — |
### §0.2 对齐验证矩阵
| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| 蓝图类/函数名 = 代码类/函数名 | §4.1 签名逐一比对 tomorrow_boundary_planner.py | ✅ |
| 代码 [BLUEPRINT] 头 = 本蓝图 module_id | 代码头 `# [BLUEPRINT] MOD-PLAN-001` | ✅ |
| §4.2 数据模型在 SSoT 文件中存在 | `grep "class TomorrowBoundary"` | ✅ |
| §0.1 文件职责无重叠、归属无 ⚠️ | 单文件模块 | ✅ |
| §5.5 触发机制状态与代码一致 | 逐操作核对 | ✅ |
### §0.3 版本-代码映射
| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (基线回填) | TomorrowBoundary 契约 + compute_boundary（MVP 骨架）已实现 | BM-SEL 多源输入融合 | BM-SEL-03/04/05/23 未就绪，签名预留 |
### §0.4 SSoT与责任唯一性声明
| # | 声明维度 | 本蓝图是真源 | 真源在别处（委托） | 委托目标 |
|---|---------|:----------:|:---------------:|---------|
| 1 | TomorrowBoundary 契约与盘后边界计算 | ✅ | ❌ | — |
| 2 | 盘前加载与情景匹配 | ❌ | ✅ | MOD-PLAN-002 |
| 3 | 盘中推演与尾盘决策 | ❌ | ✅ | BM-PLAN-01-C / MOD-PLAN-003 |
| 4 | 市场状态/预测/主力/情绪原始数据 | ❌ | ✅ | BM-SEL-03/04/05/23 |
### §0.5 代码目录唯一性声明
| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/plan_engine/`（与 frontmatter.actual_disk_path 一致） |
| 2 | 已知副本目录 | 无 |
| 3 | 副本处置状态 | 无副本 |
### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PLAN-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PLAN-001` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-PLAN-001` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PLAN-001 | MOD-PLAN-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | 1 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

## §1 设计背景与目标 <!-- temporal_type: permanent -->
### 1.1 背景
明日预案双层架构（41 §3.10）覆盖作战地图 BM-PLAN-01/02/03 三环节：B 盘后生成边界 / C 盘前加载约束 / A 盘中推演在边界内执行。本模块是 B 层（边界层）核心产出者——盘后冷静计算明日边界，避免盘中情绪化决策。41 §3.10.2 裁定"建设"，v1.7.0 已落码。
### 1.2 目标范围
| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | TomorrowBoundary 契约+盘后边界计算（MVP：昨收±振幅箱体） | 41 §3.10.2 已落码 |
| 2 | ❌ 排除 | 盘中推演（毫秒级）/ 尾盘决策 | 归 BM-PLAN-01-C / MOD-PLAN-003 |
| 3 | ❌ 排除 | 盘前加载与竞价情景匹配 | 归 MOD-PLAN-002 |
### 1.4 运行场景约束
| 约束 | 影响 |
|------|------|
| 盘后收盘后运行（冷静期） | 不读盘中实时数据，只用当日已收盘数据 |
| 边界层坏=致命 | 计算失败=暂停操作，延迟开盘到加载成功或人工介入 |
| BM-SEL 输入未就绪 | 四路增强输入签名为 None 降级，MVP 仅用市场状态昨收/振幅 |
### 1.5 利益相关者映射
| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| ZephyrAlpha-Owner | 边界参数（30% 加仓上限等） | 设计+校准 | 契约破坏性变更审批权 |
| MOD-PLAN-002 | TomorrowBoundary 字段完整性 | 消费 | 契约变更需同步 |
| BM-BUY-02 / BM-SELL-02 | 边界指令可执行性 | 消费 | 只读消费 |
### 1.6 当前态/目标态差距
| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 契约+骨架计算 | 已实现并通过测试 | 同左 | 无差距 | — |
| 多源输入融合 | None 降级（仅昨收/振幅） | BM-SEL-03/04/05/23 融合 | 上游未就绪 | P1 |
| 箱体算法 | 昨收±振幅（默认 3%） | 技术位精算（压力/支撑） | 校准未执行 | P2 |
### 1.7 典型场景
| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 盘后边界生成 | 收盘后定时任务 | compute_boundary→昨收×(1±振幅)→边界六字段 | TomorrowBoundary |
| 收盘价异常 | close≤0 | 抛 ValueError→致命暂停操作 | 异常上抛 |
| 增强输入缺失 | next_day_prediction=None | 跳过增强融合，纯昨收口径 | TomorrowBoundary（降级） |

## §2 模块边界 <!-- temporal_type: permanent -->
### 2.1 职责边界
> **核心职责声明**：本蓝图的核心职责是 `盘后基于当日数据计算明日操作边界 TomorrowBoundary 并保证字段完整可消费`。职责数量：1。

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 盘后边界计算 | 箱体上沿/下沿、加仓上限 0.30、禁加仓价位（上沿×0.98）、必出止盈价位（=上沿）、突破验证条件 | 本模块 |
| 2 | ❌ 排除 | 盘前加载/情景匹配 | C 层职责 | MOD-PLAN-002 |
| 3 | ❌ 排除 | 盘中推演/尾盘调仓/下单执行 | A 层与执行层职责 | BM-PLAN-01-C / MOD-PLAN-003 / 41 §3.4 |

#### 职责唯一性声明
| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 明日操作边界计算（盘后） | [MOD-PLAN-002, MOD-PLAN-003] | `python scripts/governance/check_ssot_uniqueness.py --blueprint MOD-PLAN-001` |

## §3 架构设计 <!-- temporal_type: permanent -->
### 3.1 组件架构
| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | TomorrowBoundary | 明日操作边界契约（8 字段） | — | frozen dataclass |
| 2 | TomorrowBoundaryPlanner.compute_boundary | 盘后边界计算 | zephyr.shared.utils.time_utils.now_utc | 同步调用 |
### 3.2 数据流
| # | 上游 | 处理逻辑 | 下游 | 数据格式 | 转换规则 |
|---|--------|---------|---------|---------|---------|
| 1 | 市场状态（BM-SEL-03：昨收/振幅）+四路可选增强输入 | ①校验 close>0→②箱体=昨收×(1±amplitude)→③派生禁加仓/必出/突破验证字段 | TomorrowBoundary→MOD-PLAN-002 | dict→frozen dataclass | amplitude 默认 0.03 |
### 3.3 状态生命周期
本模块无状态机（纯计算，每次调用独立产出不可变契约）。

## §4 接口契约 <!-- temporal_type: permanent -->
> 数据契约为 frozen dataclass（41 §3.10.2 输出契约原样落码，见 §16 D-PLAN001-03）。

### 4.1 公共 API
```python
class TomorrowBoundaryPlanner:
    """明日预案引擎——盘后收盘后基于当日数据冷静计算明日操作边界"""
    def compute_boundary(self, symbol: str, market_state: dict[str, Any],
                         next_day_prediction: dict[str, Any] | None = None,
                         main_force_behavior: dict[str, Any] | None = None,
                         sentiment_cycle: dict[str, Any] | None = None,
                         sell_side_boundary: dict[str, Any] | None = None) -> TomorrowBoundary: ...
```
| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `compute_boundary()` | ①取 market_state["close"] 校验>0（否则抛 ValueError，41 §3.10.2 致命口径）→②amplitude=market_state.get("amplitude",0.03)→③箱体上沿=close×(1+amp)/下沿=close×(1-amp)→④no_add_price=上沿×0.98、must_exit_price=上沿、breakout_confirm="放量站稳10分钟"、max_add_position=0.30→⑤computed_at=now_utc() | 步骤①致命校验 |

### 4.2 数据模型
```python
@dataclass(frozen=True)
class TomorrowBoundary:
    symbol: str
    box_upper: float          # 箱体上沿（明日压力位）
    box_lower: float          # 箱体下沿（明日支撑位）
    max_add_position: float   # 加仓仓位上限（默认 0.30）
    no_add_price: float       # 禁加仓价位（≈上沿）
    must_exit_price: float    # 必出止盈价位（冲上沿必出）
    breakout_confirm: str     # 突破验证条件（"放量站稳10分钟"）
    computed_at: Any = None   # 计算时间（now_utc()）
```
| 模型名 | SSoT文件 | 其他定义位置 | 状态 |
|--------|---------|------------|------|
| TomorrowBoundary | tomorrow_boundary_planner.py | premarket_constraint_loader.py（import 引用，非重定义） | ✅ 唯一源 |
### 4.3 输入契约
| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `compute_boundary()` | `symbol` / `market_state` | ✅/✅ | market_state 须含 close>0；amplitude 缺省 0.03 |
| `compute_boundary()` | 四路增强输入（next_day_prediction/main_force_behavior/sentiment_cycle/sell_side_boundary） | ❌ | None=降级（BM-SEL 未就绪） |
### 4.4 输出契约
| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `compute_boundary()` | `TomorrowBoundary`（box_upper>box_lower，字段完整） | ValueError（收盘价异常）；错误码契约 ZA-PLAN-0001（BoundaryComputeError，代码头声明）——边界层坏=致命，调用方暂停操作 |
### 4.5 MCP 接口（条件可选）
本模块不暴露 MCP 接口。
### 4.6 契约版本
| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增字段（如技术位来源标注） | ✅ 向后兼容 | patch+1 |
| 修改边界计算默认参数（0.30/0.98/3%） | ⚠️ 需通知 | 实盘校准后更新 |
| 删除/重命名字段 | ❌ 破坏性 | 需 Owner 审批+MOD-PLAN-002/003 同步 |

**变更通知**：破坏性变更→Owner 审批+蓝图 minor+1；兼容性变更→AI 自主+patch+1。
### 4.7 OCP 扩展点（条件可选）
本模块无 OCP 扩展点。增强输入融合点已按签名预留（四路 None 降级参数），BM-SEL 就绪后在 compute_boundary 内部扩展，签名不变。

## §5 约束条件 <!-- temporal_type: permanent -->
### 5.1 技术约束
| # | 约束 | 值 |
|---|------|-----|
| 1 | 加仓仓位上限 | 0.30（41 §3.10.2 参数默认值） |
| 2 | 禁加仓价位 | 箱体上沿×0.98（接近上沿禁止加仓防追高） |
| 3 | 必出止盈价位 | 箱体上沿（冲上沿必出，纪律） |
| 4 | 突破验证条件 | "放量站稳10分钟"（41 §3.10.2） |
| 5 | 不变量 | 边界层坏=致命暂停操作；盘后生成；不读盘中实时数据 |
### 5.2 容量估算
| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 每日计算标的数 | ≤10 | ≤50 | 单标的 O(1) 计算 | ✅ | 无需扩展 |
| 单次计算耗时 | <1ms | <10ms | 纯算术 | ✅ | 无需扩展 |
### 5.3 迁移/废弃方案（条件可选）
无迁移/废弃。
### 5.4 非功能需求与服务水平
| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 盘后边界生成成功率 | 100%（致命口径） | 计算日志 | 生成成功率 | 100% | 0 次/日 | 失败即告警阻断次日开盘 |
| 正确性 | 字段完整性 | 8 字段全产出 | 单测断言 | 完整率 | 100% | 0 次 | 测试失败即阻断 |
### §5.5 自动化触发机制
| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|---------|
| compute_boundary（盘后边界生成） | auto_scheduled | 收盘后（15:30 数据就绪后）执行 | 函数已实现✅；auto_scheduled 接线待上游 BM-SEL-03/04/05/23 数据就绪（当前 MVP 由调用方直调） |
### §5.7 禁止模式与导入约束
| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 盘中实时数据输入 | 只用当日已收盘数据 | 冷静期设计（41 §3.10.2） |
| 2 | 编码模式 | 边界计算失败时静默继续 | 抛异常+致命暂停 | 降级铁律：边界层坏=致命 |
| 3 | 导入源 | zephyr.plan_engine 下游模块（premarket/closing） | zephyr.shared.utils.* | 本模块是包内最上游，防循环 |

## §6 错误处理 <!-- temporal_type: permanent -->
| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 收盘价缺失/异常（close≤0） | compute_boundary 校验 | 抛 ValueError→致命暂停操作（延迟开盘/人工介入） | 次日全部操作 |
| 2 | 增强输入未就绪 | None 默认值 | 降级为纯昨收口径，不阻断 | 精度降级 |
| 3 | 依赖循环声明 | — | 本模块只依赖 shared.utils，无 A→B→A 循环 | — |
### 6.1 可观测性规格
| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| boundary_compute_total | Counter | 手动上报 | — | P3 |
| boundary_compute_failure_total | Counter | 手动上报 | ≥1 | P1（致命口径） |
### 6.2 退化矩阵
| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| BM-SEL 四路增强输入 | 纯昨收口径边界 | 增强融合 | None 降级 | 上游数据就绪 |
| 边界计算（整体失败） | 无（致命） | 次日全部操作 | 暂停操作+人工介入 | 计算恢复 |

## §7 安全考量 <!-- temporal_type: permanent -->
| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 无边界状态下开始交易 | 极高 | 边界层坏=致命，加载失败禁止开盘（41 §3.10.2 降级铁律） | 异常路径单测 |
| 2 | 追高买入 | 高 | 禁加仓价位=上沿×0.98 | 字段关系断言（no_add_price<box_upper） |

## §8 测试策略 <!-- temporal_type: permanent -->
| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | 契约+计算 | TestTomorrowBoundary（字段/默认值/frozen）、TestTomorrowBoundaryPlanner（正常计算/默认振幅/close≤0 抛异常/None 降级/字段关系） | 全部通过 |
| 2 | 回归验证 | 41 号施工全体 | 3 个测试文件连续 2 轮全过（41 v1.7.0 记录） | 83/83 通过 |

测试文件：`tests/plan_engine/test_plan_engine.py`（plan_engine 三模块共 17 用例，本模块覆盖 TestTomorrowBoundary+TestTomorrowBoundaryPlanner）。

## §9 依赖关系 <!-- temporal_type: permanent -->
### 9.1 依赖声明
| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| zephyr.shared.utils.time_utils | 必须 | now_utc()（计算时间戳） | — | 跨层共享包 |
| 41_buy_flow 设计备忘 | 必须 | §3.10.2 契约与参数默认值 | v1.7.0 | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/41_buy_flow.md` |
### 9.2 依赖图对齐声明
| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §9.1 依赖声明 ↔ depgraph.nodes | 依赖条目在 depgraph 有对应节点 | 已对齐 | `python scripts/governance/extract_depgraph.py --modules MOD-PLAN-001` |
| 2 | §10 产出物路径 ↔ path_mappings | 路径一致 | 已对齐 | 同上 |
### 9.5 概念重叠声明
| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | 技术位压力/支撑计算 | 计算逻辑 | 41 §3.5 限价锚定（MOD-PA-006 消费技术位） | 共存（本模块产出边界级技术位，MOD-PA-006 消费行情级技术位，口径不同） | 已处置 |
### 9.6 依赖链风险评级
| # | 依赖链 | 链深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:-----:|---------|---------|---------|
| 1 | MOD-PLAN-001→shared.utils | 2 | L1 | 无（链深≤2 免熔断） | 不适用 |

## §10 产出物存放目录 <!-- temporal_type: permanent -->
| 产出物类型 | 存放完整路径（相对优先） | 职责 | consumer_min | 注册位置 |
|----------|---------------|------|:-----------:|---------|
| 蓝图文件 | `docs/03_modules/_domain_plan_engine/tomorrow_boundary_planner/blueprint.md` | 本文件 | ≥0 | blueprint_registry.yaml |
| 业务代码 | `src/zephyr/plan_engine/tomorrow_boundary_planner.py` | 明日预案引擎 | ≥1 | `src/zephyr/plan_engine/__init__.py` __all__ |
| 测试代码 | `tests/plan_engine/test_plan_engine.py` | 与 MOD-PLAN-002/003 共 17 用例 | ≥0 | pytest 自动发现 |

## §11 集成目标 <!-- temporal_type: permanent -->
| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| MOD-PLAN-002 盘前加载 | 契约消费 | TomorrowBoundary→load_constraint(boundary=...) | test_plan_engine 集成用例 |
| BM-BUY-02 / BM-SELL-02 | 边界指令 | 禁加仓/必出价位注入买卖融合 | 字段完整性校验 |

## §12 需要更新的相关内容 <!-- temporal_type: permanent -->
| # | 需更新的文件 | 完整路径（相对优先） | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | 新增 MOD-PLAN-001 条目 | 回填登记 |
| 2 | 依赖图 | PostgreSQL depgraph | MOD-PLAN-001 节点核验 | 五图对齐 |

## §13 已知风险与缓解 <!-- temporal_type: permanent -->
| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | MVP 箱体=昨收±3% 振幅近似，非真实技术位 | 中 | 中 | 默认振幅可被 market_state["amplitude"] 覆盖；BM-SEL 就绪后升级精算 | 负面后果 |
| 2 | 四路增强输入长期 None | 中 | 中 | 签名预留，融合在内部扩展不改契约 | 风险 |

## §14 施工指引 <!-- temporal_type: construction_temporary（施工已完成，本节保留状态记录） -->
### 14.1 施工策略
| 项目 | 内容 |
|------|------|
| 施工阶段数 | 单 Phase 一次性完成（AI-BUY-001，41 号 v1.7.0 施工批次） |
| 施工模式 | 新建 |
| 核心风险 | 边界层致命口径的正确传递（异常必须上抛不可静默） |
| 目标 generation | 1 |
### 14.2 前置条件
| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | 41_buy_flow v1.6.0+ §3.10 明日预案裁定 | hard | 已定稿（v1.7.0 落码） | ✅ |
| 2 | shared.utils.time_utils.now_utc | hard | 已实现 | ✅ |
### 14.3 实施步骤
回填蓝图，施工已完成：步骤 1（TomorrowBoundary 契约）已完成；步骤 2（compute_boundary MVP 骨架）已完成；步骤 3（17 用例中的本模块部分）已完成。验证命令：`python -m pytest tests/plan_engine/test_plan_engine.py -q`。
### 14.4 回滚方案
| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 全部 | 计算行为偏离 41 §3.10.2 | 以 41 §3.10.2 参数表为基准修复并重跑测试 |
### 14.5 施工完成与生产就绪标准
| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | 代码文件存在且非空 | `src/zephyr/plan_engine/tomorrow_boundary_planner.py` 存在 | 完成 | ✅ |
| 2 | 测试通过 | test_plan_engine.py exit 0 | 完成 | ✅ |
| 3 | 代码头十五字段完整 | [BLUEPRINT] MOD-PLAN-001 等字段齐全 | 就绪 | ✅ |
### 14.6 施工状态
| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | 施工者（AI-BUY-001，2026-08-13） |
| verification_status | passed | 审计者（83 用例连续 2 轮全过，41 v1.7.0 记录） |
| code_alignment_verified | yes | 审计者（§4 签名与代码逐一比对一致） |
### 14.7 参考实现规格
| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 边界参数默认值 | 配置 | 41 §3.10.2 参数表：加仓上限 0.30/禁加仓≈上沿/必出=上沿/突破验证"放量站稳10分钟" | compute_boundary 常量 |
| 2 | MVP 箱体算法 | 算法 | 41 §3.10.2：箱体上沿=昨收×(1+amplitude)/下沿=昨收×(1-amplitude)，amplitude 默认 0.03，no_add_price=上沿×0.98 | compute_boundary |
| 3 | 降级铁律 | 协议 | 41 §3.10.2：边界层坏=致命暂停；推演层坏=机械执行边界（"边界比聪明更重要"） | 异常路径 |
### 14.8 施工参考卡
| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/plan_engine/test_plan_engine.py -q` | 回归验证 | 无 | 17 passed |
| 2 | 常量 | `DEFAULT_MAX_ADD_POSITION` / `BREAKOUT_CONFIRM_CONDITION` | 加仓上限/突破验证 | float/str | 校准只改常量 |
### 14.10 故障与操作手册
| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 运行 | 收盘价异常致命 | close≤0 | 查 market_state 数据源 | 修复数据源后重算 | 边界生成成功 |
| 2 | 运行 | 增强输入 None | BM-SEL 未就绪 | 确认降级口径生效 | 上游就绪后传字典 | 融合字段产出 |
### 14.12 并发操作模型
本模块为无状态纯计算，无并发操作。

## §15 容量升级附录 <!-- temporal_type: permanent -->
### §15.1 容量基线
| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 每日计算标的数 | ≤10 | 计算日志 |
| 单次计算耗时 | <1ms | 耗时日志 |
### §15.2 缺口清单与升级版本矩阵
| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-PLAN001-01 | 箱体为振幅近似非技术位精算 | BM-SEL-03/05 就绪后融合精算 | P1 | BM-SEL 数据就绪 | v1.0.0 | 未触发 |

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.1.0 | 1 | 基线回填 | 契约+MVP 骨架计算 | ✅ |

## §16 决策记录 <!-- temporal_type: permanent -->
| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-PLAN001-01 | 明日预案双层架构（B 盘后边界/C 盘前约束/A 盘中推演） | A 双层/B 单层实时 | A | 41 §3.10.1：边界比聪明更重要，安全优先于效率 | 2026-08-12 |
| 2 | D-PLAN001-02 | MVP 箱体用昨收±振幅骨架 | A 骨架/B 等技术位精算 | A | 41 §3.10.2 参数默认值 proposed 口径；BM-SEL 未就绪不阻塞施工 | 2026-08-13 |
| 3 | D-PLAN001-03 | 数据契约用 frozen dataclass | A dataclass/B Pydantic | A | 41 §3.10.2 输出契约原文即 @dataclass；与交易域惯例一致 | 2026-08-13 |

## 必备链接 <!-- temporal_type: permanent -->
| # | 文件 | module_id | 完整路径（相对优先） | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 买入流 spec（设计真源） | — | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/41_buy_flow.md` | §3.10.1/§3.10.2 架构与契约 |
| 2 | 蓝图模板 | GOV-028 | `docs/01_policies_and_standards/templates/blueprint_construction_template.md` | v2.1.0 章节合规 |

## 术语表 <!-- temporal_type: permanent -->
| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| 明日预案 | 盘后生成边界+盘前加载约束+盘中边界内推演的双层架构 | 盘中实时决策 | 预案在冷静期定边界，盘中只在边界内执行 |
| 箱体上沿/下沿 | 明日压力位/支撑位（MVP=昨收×(1±振幅)） | VWAP 锚定价 | 箱体是操作边界，VWAP 是下单锚定（MOD-PA-006） |
| 禁加仓价位 | 接近上沿禁止加仓（上沿×0.98） | 必出止盈价位 | 禁加仓=接近上沿不买，必出=冲上沿必卖 |
| 边界层坏=致命 | 边界计算/加载失败暂停全部操作 | 推演层坏=可接受 | 安全基线 vs 效率优化（41 §3.10.2 降级铁律） |

## 成熟度声明 <!-- temporal_type: permanent -->
| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | 41 号重大修订 | 双层架构裁定已落码 |
| 接口契约 | stable | 高 | 破坏性变更需 Owner 审批 | 签名与 41 §3.10.2 一致 |
| 数据模型 | frozen | 高 | 41 §3.10.2 契约修订 | frozen dataclass 原样落码 |
| 箱体算法 | evolving | 中 | BM-SEL 数据就绪 | MVP 骨架为振幅近似 |

## 版本演进路线图 <!-- temporal_type: permanent -->
| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 基线回填（代码先行，蓝图后补，遗留项 #29） | — | 已完成 |
| v1.0.0 | BM-SEL 四路输入融合+技术位精算 | v0.1.0 | 未施工 |

## 已知问题与盲点登记 <!-- temporal_type: permanent -->
| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 箱体算法为昨收±3% 振幅近似 | 中 | BM-SEL-03/05 未就绪 | 上游就绪后融合精算，契约不变 | §5.1 #1 | 未解决 |

## 自检与闭合清单 <!-- temporal_type: permanent -->
| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口执行流程引用 41 号节号 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §8 有对应测试 | 参数/不变量→测试用例 | ✅ |
| 4 | 设计 | §0.1 代码文件在 §10 有对应产出物路径 | 单文件核对 | ✅ |
| 5 | 后 | 临时时态内容已清理 | 施工已完成，§14.3 仅留状态 | ✅ |

## 项目中已有类似功能 <!-- temporal_type: permanent -->
| # | 已有模块/文件 | 完整路径（相对优先） | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | MOD-PA-006 分批建仓引擎 | `src/zephyr/pf_alloc/batched_position_builder.py` | 技术位价格（压力/支撑） | 该模块消费技术位做下单锚定（how），本模块产出次日操作边界（when/whether） |
| 2 | MOD-POS-010 限仓执行器 | `docs/03_modules/_domain_position/position_limit_enforcer/blueprint.md` | 仓位上限 | 该模块管账户级硬限仓，本模块管单标的加仓后总仓位上限 30%（边界语义） |

## 涉及的文件范围 <!-- temporal_type: permanent -->
| # | 文件/目录 | 完整路径（相对优先） | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 业务代码 | `src/zephyr/plan_engine/tomorrow_boundary_planner.py` | 读取 | 无变更（回填蓝图不改代码） |
| 2 | 测试代码 | `tests/plan_engine/test_plan_engine.py` | 读取 | 无变更 |
| 3 | 蓝图文件 | `docs/03_modules/_domain_plan_engine/tomorrow_boundary_planner/blueprint.md` | 新建 | 本文件 |

## ⚠️ 安全删除协议 <!-- temporal_type: permanent -->
本蓝图不涉及任何文件废弃/迁移/删除。如未来涉及：禁止蓝图阶段物理删除；迁移型删除逐条迁移逐条验证；物理删除只在 stable 搬入阶段且人类确认后执行。

## ⚠️ Vibe Coding 蓝图编写铁律确认 <!-- temporal_type: permanent -->
本蓝图编写已逐条确认：全部路径项目根相对+正斜杠；必备链接完整列出；蓝图为最终设计结果；产出物路径与磁盘一致；涉及文件范围明确；全文无模糊指令词（铁律#6）；§0.1/§0.6 AUTOGEN 节保留生成说明未手写漂移；已实现代码不复制实现只保留签名（§4）；术语表齐备。

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/plan_engine/tomorrow_boundary_planner.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/plan_engine/test_plan_engine.py` | ✅ 已实现 | |

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
