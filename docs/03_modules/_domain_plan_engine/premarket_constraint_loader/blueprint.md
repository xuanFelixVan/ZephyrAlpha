---
module_id: MOD-PLAN-002
title: "盘前预案加载器 — 9:00加载TomorrowBoundary+9:25集合竞价9情景匹配初始化ConstraintState"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
layer: L2_domain
functional_domain: plan_engine
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-13"
last_updated: "2026-08-13"
priority: P1
blueprint_level: module
actual_disk_path: src/zephyr/plan_engine/premarket_constraint_loader.py
belongs_to: ""
depends_on: [MOD-PLAN-001]
ssot_claims:
  - {claim: "ConstraintState 数据契约唯一真源", scope: "module"}
  - {claim: "9:25 集合竞价 9 情景匹配规则唯一真源", scope: "module"}
responsibility_domain: 
design_maturity: production
build_status: production
language: zh
generation: 1
summary: "BM-PLAN-02 盘前预案加载：次日 9:00 加载昨晚 TomorrowBoundary，9:25 集合竞价匹配 9 情景初始化 ConstraintState；加载失败=致命，无约束状态禁止开始交易"
---
# Premarket Constraint Loader 蓝图+施工图 — 盘前预案加载器 — 9:00加载TomorrowBoundary+9:25集合竞价9情景匹配初始化ConstraintState

> module_id: MOD-PLAN-002 | version: 0.1.3 | status: Active | layer: L2_domain (plan_engine)
> actual_disk_path: src/zephyr/plan_engine/premarket_constraint_loader.py | generation: 1
> 设计真源: 41_buy_flow v1.7.0 §3.10.3 | 施工性质: 回填蓝图（代码已完工，83用例通过，2026-08-13 补建，遗留项 #29）

## 概述 <!-- temporal_type: permanent -->
本蓝图描述盘前预案加载器——它解决"昨晚盘后算好的操作边界如何在次日开盘前生效"的问题（BM-PLAN-02，明日预案双层架构 C 层）。核心职责：次日 9:00 加载昨晚 TomorrowBoundary，9:25 集合竞价匹配 9 种情景（高开/低开/平开 × 真涨/假涨/真跌/假跌/洗盘），初始化 ConstraintState。加载失败=致命——无约束状态禁止开始交易。上游消费 MOD-PLAN-001 产出的 TomorrowBoundary，下游被 MOD-PLAN-003（尾盘决策）与 BM-BUY-02/BM-SELL-02 初始指令消费。MVP 竞价匹配为±2% 简化规则，无竞价数据时降级默认 FLAT_OPEN_WASH。

> **标准锚点（防幻觉）**——蓝图模板：blueprint_construction_template.md v2.1.0；设计真源：41_buy_flow.md v1.7.0 §3.10.3；机器真源：PostgreSQL depgraph（`python scripts/governance/extract_depgraph.py --modules MOD-PLAN-002`）。

## §0 代码对齐验证 <!-- temporal_type: permanent -->
### §0.1 代码文件清单
<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> 本节为自动生成（派生自 depgraph.nodes），禁止手写。生成命令：`python scripts/governance/extract_depgraph.py --modules MOD-PLAN-002`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 归属判定 | 阻塞原因 |
|---|--------|------------|------|:-----:|---------|---------|
| 1 | （占位——AUTOGEN 生成；当前实现为 premarket_constraint_loader.py 单文件） | §3.1 | ConstraintState 契约+盘前加载+情景匹配 | 已实现 | 本模块 | — |
### §0.2 对齐验证矩阵
| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| 蓝图类/函数名 = 代码类/函数名 | §4.1 签名逐一比对 premarket_constraint_loader.py | ✅ |
| 代码 [BLUEPRINT] 头 = 本蓝图 module_id | 代码头 `# [BLUEPRINT] MOD-PLAN-002` | ✅ |
| §4.2 数据模型在 SSoT 文件中存在 | `grep "class ConstraintState"` | ✅ |
| §0.1 文件职责无重叠、归属无 ⚠️ | 单文件模块 | ✅ |
| §5.5 触发机制状态与代码一致 | 逐操作核对 | ✅ |
### §0.3 版本-代码映射
| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (基线回填) | ConstraintState 契约 + load_constraint + 9 情景匹配（MVP ±2% 简化）已实现 | 真涨/假涨/洗盘细分判定 | 竞价量能数据未就绪，MVP 简化 |
### §0.4 SSoT与责任唯一性声明
| # | 声明维度 | 本蓝图是真源 | 真源在别处（委托） | 委托目标 |
|---|---------|:----------:|:---------------:|---------|
| 1 | ConstraintState 契约+盘前加载+9 情景匹配 | ✅ | ❌ | — |
| 2 | TomorrowBoundary 契约 | ❌ | ✅ | MOD-PLAN-001 |
| 3 | 尾盘调仓决策 | ❌ | ✅ | MOD-PLAN-003 |
### §0.5 代码目录唯一性声明
| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/plan_engine/`（与 frontmatter.actual_disk_path 一致） |
| 2 | 已知副本目录 | 无 |
| 3 | 副本处置状态 | 无副本 |
### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PLAN-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PLAN-002` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-PLAN-002` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PLAN-002 | MOD-PLAN-002 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 1 文件 | 1 文件（§0.1） | ✅ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

## §1 设计背景与目标 <!-- temporal_type: permanent -->
### 1.1 背景
明日预案双层架构（41 §3.10）C 层：盘后生成的 TomorrowBoundary 须在次日盘前加载并匹配集合竞价情景才能约束盘中操作。41 §3.10.3 裁定"建设"——盘前加载是边界层组成部分，加载失败=致命。v1.7.0 已落码。
### 1.2 目标范围
| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | ConstraintState 契约+盘前加载+9:25 竞价 9 情景匹配 | 41 §3.10.3 已落码 |
| 2 | ❌ 排除 | 边界计算本体 | 归 MOD-PLAN-001（B 层） |
| 3 | ❌ 排除 | 盘中推演/尾盘决策 | 归 BM-PLAN-01-C / MOD-PLAN-003（A 层） |
### 1.4 运行场景约束
| 约束 | 影响 |
|------|------|
| 竞价匹配窗口 9:20-9:25 | 9:20 后不可撤单价格趋稳，最后 5 分钟匹配（41 §3.10.3） |
| 加载失败=致命 | 无约束状态禁止开始交易，延迟开盘到加载成功或人工介入 |
| 竞价数据可能缺失 | auction_data=None 降级默认 FLAT_OPEN_WASH |
### 1.5 利益相关者映射
| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| ZephyrAlpha-Owner | 9 情景规则与±2% 阈值 | 设计+校准 | 契约破坏性变更审批权 |
| MOD-PLAN-001 | TomorrowBoundary 按时产出 | 上游 | 契约变更需同步 |
| MOD-PLAN-003 / BM-BUY-02 / BM-SELL-02 | ConstraintState 可消费 | 消费 | initialized=True 才可交易 |
### 1.6 当前态/目标态差距
| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 加载+契约 | 已实现并通过测试 | 同左 | 无差距 | — |
| 情景匹配 | ±2% 简化（真涨/真跌/洗盘三出） | 9 情景全细分（真假涨/真假跌/洗盘） | 竞价量能数据未就绪 | P1 |
### 1.7 典型场景
| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 正常盘前加载 | 9:00 定时+9:25 竞价数据 | load_constraint→_match_scenario→initialized=True | ConstraintState |
| 边界未产出 | boundary=None | 抛 ValueError→致命延迟开盘 | 异常上抛 |
| 竞价数据缺失 | auction_data=None | 降级 FLAT_OPEN_WASH | ConstraintState（降级） |

## §2 模块边界 <!-- temporal_type: permanent -->
### 2.1 职责边界
> **核心职责声明**：本蓝图的核心职责是 `盘前加载 TomorrowBoundary 并按集合竞价匹配情景，产出初始化 ConstraintState`。职责数量：2。

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 盘前约束加载 | 校验 boundary 非空→组装 ConstraintState（initialized=True） | 本模块 |
| 2 | ✅ 包含 | 竞价情景匹配 | 9:20-9:25 窗口数据→9 情景之一（MVP ±2% 简化） | 本模块 |
| 3 | ❌ 排除 | 边界计算 | B 层职责 | MOD-PLAN-001 |
| 4 | ❌ 排除 | 盘中推演/尾盘调仓 | A 层职责 | BM-PLAN-01-C / MOD-PLAN-003 |

#### 职责唯一性声明
| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 盘前约束加载与竞价情景匹配 | [MOD-PLAN-001, MOD-PLAN-003] | `python scripts/governance/check_ssot_uniqueness.py --blueprint MOD-PLAN-002` |

## §3 架构设计 <!-- temporal_type: permanent -->
### 3.1 组件架构
| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | ConstraintState | 约束状态契约（4 字段） | TomorrowBoundary（MOD-PLAN-001） | frozen dataclass |
| 2 | PremarketConstraintLoader.load_constraint | 盘前加载入口 | _match_scenario | 同步调用 |
| 3 | _match_scenario（私有） | 竞价 9 情景匹配 | SCENARIO_LIST 常量 | 内部调用 |
### 3.2 数据流
| # | 上游 | 处理逻辑 | 下游 | 数据格式 | 转换规则 |
|---|--------|---------|---------|---------|---------|
| 1 | MOD-PLAN-001 TomorrowBoundary + 9:25 竞价数据 | ①boundary 非空校验→②_match_scenario(open_pct±2%)→③组装 ConstraintState | ConstraintState→MOD-PLAN-003/BM-BUY-02/BM-SELL-02 | frozen dataclass | open_pct=(open-prev_close)/prev_close |
### 3.3 状态生命周期
本模块无状态机（每次加载独立产出不可变契约）。ConstraintState.initialized 二态：False（加载失败前）→ True（加载成功）；失败路径抛异常不产出对象。

## §4 接口契约 <!-- temporal_type: permanent -->
> 数据契约为 frozen dataclass（41 §3.10.2 输出契约原样落码，见 §16 D-PLAN002-02）。

### 4.1 公共 API
```python
class PremarketConstraintLoader:
    """盘前预案加载器——加载昨晚边界+9:25 竞价匹配情景，初始化 ConstraintState"""
    def load_constraint(self, symbol: str, boundary: TomorrowBoundary,
                        auction_data: dict[str, Any] | None = None) -> ConstraintState: ...
    def _match_scenario(self, auction_data: dict[str, Any]) -> str: ...  # 私有：9 情景匹配
```
| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `load_constraint()` | ①boundary None 校验（None→抛 ValueError，41 §3.10.3 致命口径）→②auction_data 有值则 _match_scenario，无值降级 FLAT_OPEN_WASH→③组装 ConstraintState(initialized=True) | 步骤①致命校验 |
| `_match_scenario()` | ①prev_close≤0→FLAT_OPEN_WASH→②open_pct>+2%→HIGH_OPEN_REAL_UP→③open_pct<-2%→LOW_OPEN_REAL_DOWN→④其余→FLAT_OPEN_WASH（MVP 简化，G04 校准来源） | ±2% 阈值分支 |

### 4.2 数据模型
```python
@dataclass(frozen=True)
class ConstraintState:
    symbol: str
    boundary: TomorrowBoundary   # MOD-PLAN-001 产出
    scenario: str                # 9 情景之一
    initialized: bool            # 盘前加载是否成功
```
| 模型名 | SSoT文件 | 其他定义位置 | 状态 |
|--------|---------|------------|------|
| ConstraintState | premarket_constraint_loader.py | — | ✅ 唯一源 |
| TomorrowBoundary | tomorrow_boundary_planner.py | 本模块 import 引用（非重定义） | ✅ 唯一源在 MOD-PLAN-001 |
| SCENARIO_LIST（9 情景常量） | premarket_constraint_loader.py | — | ✅ 唯一源 |
### 4.3 输入契约
| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `load_constraint()` | `symbol` / `boundary` | ✅/✅ | boundary 为 None 抛异常（致命） |
| `load_constraint()` | `auction_data` | ❌ | 含 open_price/prev_close；None→默认 FLAT_OPEN_WASH |
### 4.4 输出契约
| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `load_constraint()` | `ConstraintState`（initialized=True，scenario∈9 情景） | ValueError（TomorrowBoundary 未加载）；错误码契约 ZA-PLAN-0002（ConstraintLoadError，代码头声明）——加载失败=致命，禁止开始交易 |
| `_match_scenario()` | 9 情景字符串之一 | prev_close≤0 时回退 FLAT_OPEN_WASH（不抛异常） |
### 4.5 MCP 接口（条件可选）
本模块不暴露 MCP 接口。
### 4.6 契约版本
| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增情景细分（真涨/假涨/洗盘拆分） | ✅ 向后兼容 | scenario 取值在 SCENARIO_LIST 内扩展语义 |
| 修改±2% 匹配阈值 | ⚠️ 需通知 | G04 校准后更新，patch+1 |
| 删除/重命名字段 | ❌ 破坏性 | 需 Owner 审批+MOD-PLAN-003 同步 |

**变更通知**：破坏性变更→Owner 审批+蓝图 minor+1；兼容性变更→AI 自主+patch+1。
### 4.7 OCP 扩展点（条件可选）
本模块无 OCP 扩展点。情景细分扩展点已预留：`_match_scenario` 返回值限定在 SCENARIO_LIST 内，量能数据就绪后内部细分不改签名。

## §5 约束条件 <!-- temporal_type: permanent -->
### 5.1 技术约束
| # | 约束 | 值 |
|---|------|-----|
| 1 | 竞价匹配窗口 | 9:20-9:25（AUCTION_MATCH_WINDOW_START/END，41 §3.10.3） |
| 2 | 情景集合 | 9 种（高开/低开/平开 × 真涨/假涨/真跌/假跌/洗盘），SCENARIO_LIST 常量 |
| 3 | MVP 匹配阈值 | open_pct±2%（简化，G04 校准来源） |
| 4 | 不变量 | 加载失败=致命；无约束状态禁止开始交易；9:20 后不可撤单价格趋稳才匹配 |
### 5.2 容量估算
| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 盘前加载标的数 | ≤10 | ≤50 | 单标的 O(1) | ✅ | 无需扩展 |
| 单次加载耗时 | <1ms | <10ms | 纯算术 | ✅ | 无需扩展 |
### 5.3 迁移/废弃方案（条件可选）
无迁移/废弃。
### 5.4 非功能需求与服务水平
| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 盘前加载成功率 | 100%（致命口径） | 加载日志 | 加载成功率 | 100% | 0 次/日 | 失败即告警延迟开盘 |
| 时效性 | 9:25 前完成匹配 | <1s | 耗时日志 | 匹配耗时 | 100%<1s | 0 次 | >1s 告警 |
### §5.5 自动化触发机制
| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|---------|
| load_constraint（盘前加载） | auto_scheduled | 次日 9:00 加载边界 + 9:25 竞价数据到达后匹配 | 函数已实现✅；auto_scheduled 接线待竞价数据源就绪（当前 MVP 由调用方直调） |
### §5.7 禁止模式与导入约束
| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 加载失败静默继续交易 | 抛异常+延迟开盘/人工介入 | 降级铁律：无约束状态禁止交易 |
| 2 | 编码模式 | 9:20 前匹配情景 | 只用 9:20-9:25 窗口数据 | 9:20 后不可撤单价格趋稳（41 §3.10.3） |
| 3 | 导入源 | zephyr.plan_engine 下游模块（closing_session_decision） | zephyr.plan_engine.tomorrow_boundary_planner（上游） | 包内单向依赖防循环 |

## §6 错误处理 <!-- temporal_type: permanent -->
| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | TomorrowBoundary 未产出/为 None | load_constraint 校验 | 抛 ValueError→致命延迟开盘/人工介入 | 当日全部操作 |
| 2 | 竞价数据缺失 | auction_data=None | 降级 FLAT_OPEN_WASH，不阻断 | 情景精度 |
| 3 | prev_close 异常（≤0） | _match_scenario 校验 | 回退 FLAT_OPEN_WASH | 情景精度 |
| 4 | 依赖循环声明 | — | 只依赖上游 MOD-PLAN-001，无 A→B→A 循环 | — |
### 6.1 可观测性规格
| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| constraint_load_total | Counter | 手动上报 | — | P3 |
| constraint_load_failure_total | Counter | 手动上报 | ≥1 | P1（致命口径） |
| constraint_scenario_dist（按情景） | Counter | 手动上报 | — | P3 |
### 6.2 退化矩阵
| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| 竞价数据输入 | 边界约束仍生效 | 情景匹配 | 默认 FLAT_OPEN_WASH | 竞价数据恢复 |
| 盘前加载（整体失败） | 无（致命） | 当日全部操作 | 延迟开盘+人工介入 | 加载成功 |

## §7 安全考量 <!-- temporal_type: permanent -->
| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 无约束状态开盘交易 | 极高 | 加载失败=致命（41 §3.10.3），initialized=False 不产出对象 | 异常路径单测 |
| 2 | 竞价操纵误导情景 | 中 | 只用 9:20 后不可撤单窗口数据；MVP 默认中性洗盘情景 | 窗口常量+回退单测 |

## §8 测试策略 <!-- temporal_type: permanent -->
| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | 契约+加载+匹配 | TestConstraintState（字段/frozen）、TestPremarketConstraintLoader（正常加载/boundary=None 抛异常/无竞价数据降级/±2% 阈值分支/prev_close≤0 回退） | 全部通过 |
| 2 | 回归验证 | 41 号施工全体 | 3 个测试文件连续 2 轮全过（41 v1.7.0 记录） | 83/83 通过 |

测试文件：`tests/plan_engine/test_plan_engine.py`（plan_engine 三模块共 17 用例，本模块覆盖 TestConstraintState+TestPremarketConstraintLoader）。

## §9 依赖关系 <!-- temporal_type: permanent -->
### 9.1 依赖声明
| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-PLAN-001 | 必须 | TomorrowBoundary 契约 | ≥0.1.0 | `docs/03_modules/_domain_plan_engine/tomorrow_boundary_planner/blueprint.md` |
| 41_buy_flow 设计备忘 | 必须 | §3.10.3 加载流程与 9 情景 | v1.7.0 | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/41_buy_flow.md` |
### 9.2 依赖图对齐声明
| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §9.1 依赖声明 ↔ depgraph.nodes | 依赖条目在 depgraph 有对应节点 | 已对齐 | `python scripts/governance/extract_depgraph.py --modules MOD-PLAN-002` |
| 2 | §10 产出物路径 ↔ path_mappings | 路径一致 | 已对齐 | 同上 |
### 9.5 概念重叠声明
| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | TomorrowBoundary 契约 | 数据模型 | MOD-PLAN-001 | 本模块委托对方（import 引用不重定义） | 已处置 |
### 9.6 依赖链风险评级
| # | 依赖链 | 链深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:-----:|---------|---------|---------|
| 1 | MOD-PLAN-002→MOD-PLAN-001 | 2 | L1 | 有（§6.2 致命口径人工介入） | 已有熔断 |

## §10 产出物存放目录 <!-- temporal_type: permanent -->
| 产出物类型 | 存放完整路径（相对优先） | 职责 | consumer_min | 注册位置 |
|----------|---------------|------|:-----------:|---------|
| 蓝图文件 | `docs/03_modules/_domain_plan_engine/premarket_constraint_loader/blueprint.md` | 本文件 | ≥0 | blueprint_registry.yaml |
| 业务代码 | `src/zephyr/plan_engine/premarket_constraint_loader.py` | 盘前预案加载器 | ≥1 | `src/zephyr/plan_engine/__init__.py` __all__ |
| 测试代码 | `tests/plan_engine/test_plan_engine.py` | 与 MOD-PLAN-001/003 共 17 用例 | ≥0 | pytest 自动发现 |

## §11 集成目标 <!-- temporal_type: permanent -->
| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| MOD-PLAN-003 尾盘决策 | 契约消费 | ConstraintState→decide 上游状态 | test_plan_engine 集成用例 |
| BM-BUY-02 / BM-SELL-02 | 初始指令约束 | 竞价情景+边界注入买卖初始指令 | 字段完整性校验 |

## §12 需要更新的相关内容 <!-- temporal_type: permanent -->
| # | 需更新的文件 | 完整路径（相对优先） | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | 新增 MOD-PLAN-002 条目 | 回填登记 |
| 2 | 依赖图 | PostgreSQL depgraph | MOD-PLAN-002 节点核验 | 五图对齐 |

## §13 已知风险与缓解 <!-- temporal_type: permanent -->
| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 9 情景 MVP 只出 3 种（±2% 简化） | 高 | 中 | 竞价量能数据就绪后细分真涨/假涨/洗盘，SCENARIO_LIST 不变 | 负面后果 |
| 2 | 无竞价数据时永远 FLAT_OPEN_WASH | 中 | 低 | 降级口径已固化，数据恢复后自动细分 | 风险 |

## §14 施工指引 <!-- temporal_type: construction_temporary（施工已完成，本节保留状态记录） -->
### 14.1 施工策略
| 项目 | 内容 |
|------|------|
| 施工阶段数 | 单 Phase 一次性完成（AI-BUY-001，41 号 v1.7.0 施工批次） |
| 施工模式 | 新建 |
| 核心风险 | 致命口径正确传递（boundary=None 必须抛异常） |
| 目标 generation | 1 |
### 14.2 前置条件
| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | 41_buy_flow v1.6.0+ §3.10.3 裁定 | hard | 已定稿（v1.7.0 落码） | ✅ |
| 2 | MOD-PLAN-001 TomorrowBoundary 契约 | hard | 已实现 | ✅ |
### 14.3 实施步骤
回填蓝图，施工已完成：步骤 1（ConstraintState 契约+SCENARIO_LIST）已完成；步骤 2（load_constraint+_match_scenario）已完成；步骤 3（17 用例中的本模块部分）已完成。验证命令：`python -m pytest tests/plan_engine/test_plan_engine.py -q`。
### 14.4 回滚方案
| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 全部 | 加载/匹配行为偏离 41 §3.10.3 | 以 41 §3.10.3 为基准修复并重跑测试 |
### 14.5 施工完成与生产就绪标准
| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | 代码文件存在且非空 | `src/zephyr/plan_engine/premarket_constraint_loader.py` 存在 | 完成 | ✅ |
| 2 | 测试通过 | test_plan_engine.py exit 0 | 完成 | ✅ |
| 3 | 代码头十五字段完整 | [BLUEPRINT] MOD-PLAN-002 等字段齐全 | 就绪 | ✅ |
### 14.6 施工状态
| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | 施工者（AI-BUY-001，2026-08-13） |
| verification_status | passed | 审计者（83 用例连续 2 轮全过，41 v1.7.0 记录） |
| code_alignment_verified | yes | 审计者（§4 签名与代码逐一比对一致） |
### 14.7 参考实现规格
| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 竞价匹配窗口 | 配置 | 41 §3.10.3：9:20-9:25（9:20 后不可撤单价格趋稳） | AUCTION_MATCH_WINDOW_START/END |
| 2 | 9 情景集合 | 配置 | 41 §3.10.3：高开/低开/平开 × 真涨/假涨/真跌/假跌/洗盘 | SCENARIO_LIST |
| 3 | MVP 匹配规则 | 算法 | open_pct>+2%→HIGH_OPEN_REAL_UP；<-2%→LOW_OPEN_REAL_DOWN；其余→FLAT_OPEN_WASH（G04 校准来源） | _match_scenario |
### 14.8 施工参考卡
| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/plan_engine/test_plan_engine.py -q` | 回归验证 | 无 | 17 passed |
| 2 | 常量 | `SCENARIO_LIST` / `AUCTION_MATCH_WINDOW_*` | 9 情景/匹配窗口 | list[str]/str | 阈值校准只改 _match_scenario |
### 14.10 故障与操作手册
| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 运行 | 盘前加载致命失败 | boundary=None | 查 MOD-PLAN-001 盘后产出 | 修复后重新加载再开盘 | initialized=True |
| 2 | 运行 | 情景恒为 FLAT_OPEN_WASH | 竞价数据未接入 | 查 auction_data 来源 | 接入竞价数据 | 情景分布多样化 |
### 14.12 并发操作模型
本模块为无状态加载器，无并发操作。

## §15 容量升级附录 <!-- temporal_type: permanent -->
### §15.1 容量基线
| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 盘前加载标的数 | ≤10 | 加载日志 |
| 单次加载耗时 | <1ms | 耗时日志 |
### §15.2 缺口清单与升级版本矩阵
| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-PLAN002-01 | 情景匹配±2% 简化 | 竞价量能就绪后 9 情景细分 | P1 | 竞价数据接入 | v1.0.0 | 未触发 |

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.1.0 | 1 | 基线回填 | 契约+加载+简化匹配 | ✅ |

## §16 决策记录 <!-- temporal_type: permanent -->
| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-PLAN002-01 | 竞价匹配窗口取 9:20-9:25 | A 全竞价段/B 最后 5 分钟 | B | 41 §3.10.3：9:20 后不可撤单价格趋稳 | 2026-08-12 |
| 2 | D-PLAN002-02 | 数据契约用 frozen dataclass | A dataclass/B Pydantic | A | 41 §3.10.2 输出契约原文即 @dataclass；与交易域惯例一致 | 2026-08-13 |
| 3 | D-PLAN002-03 | 无竞价数据降级 FLAT_OPEN_WASH 而非抛异常 | A 降级/B 异常 | A | 只有边界缺失才致命；情景缺失属精度降级（41 §3.10.2 铁律分层） | 2026-08-13 |

## 必备链接 <!-- temporal_type: permanent -->
| # | 文件 | module_id | 完整路径（相对优先） | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 买入流 spec（设计真源） | — | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/41_buy_flow.md` | §3.10.3 加载流程与 9 情景 |
| 2 | MOD-PLAN-001 蓝图 | MOD-PLAN-001 | `docs/03_modules/_domain_plan_engine/tomorrow_boundary_planner/blueprint.md` | TomorrowBoundary 契约 |
| 3 | 蓝图模板 | GOV-028 | `docs/01_policies_and_standards/templates/blueprint_construction_template.md` | v2.1.0 章节合规 |

## 术语表 <!-- temporal_type: permanent -->
| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| 盘前加载 | 9:00 加载昨晚边界+9:25 竞价匹配情景 | 盘后边界生成 | 加载归 C 层（本模块），生成归 B 层（MOD-PLAN-001） |
| 9 情景 | 高开/低开/平开 × 真涨/假涨/真跌/假跌/洗盘 | 8 态预测（BM-SEL-04） | 9 情景是竞价开盘分类，8 态预测被 90 §7 暂缓与本模块无关 |
| 集合竞价 | 9:15-9:25 开盘竞价 | 收盘集合竞价 | 本模块只用 9:20-9:25 段；收盘竞价 14:57-15:00 归执行侧 |
| ConstraintState | 边界+情景+初始化标记的约束状态 | TomorrowBoundary | ConstraintState 包装 Boundary 并附加盘前情景 |

## 成熟度声明 <!-- temporal_type: permanent -->
| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | 41 号重大修订 | C 层加载裁定已落码 |
| 接口契约 | stable | 高 | 破坏性变更需 Owner 审批 | 签名与 41 §3.10.3 一致 |
| 数据模型 | frozen | 高 | 41 §3.10.2 契约修订 | frozen dataclass 原样落码 |
| 情景匹配规则 | evolving | 中 | 竞价量能数据就绪 | MVP ±2% 简化 |

## 版本演进路线图 <!-- temporal_type: permanent -->
| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 基线回填（代码先行，蓝图后补，遗留项 #29） | — | 已完成 |
| v1.0.0 | 9 情景全细分（竞价量能接入） | v0.1.0 | 未施工 |

## 已知问题与盲点登记 <!-- temporal_type: permanent -->
| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 情景匹配只出 3 种（±2% 简化） | 中 | 竞价量能数据未就绪 | 数据接入后细分，SCENARIO_LIST 不变 | §5.1 #3 | 未解决 |

## 自检与闭合清单 <!-- temporal_type: permanent -->
| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口执行流程引用 41 号节号 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §8 有对应测试 | 窗口/阈值/不变量→测试用例 | ✅ |
| 4 | 设计 | §0.1 代码文件在 §10 有对应产出物路径 | 单文件核对 | ✅ |
| 5 | 后 | 临时时态内容已清理 | 施工已完成，§14.3 仅留状态 | ✅ |

## 项目中已有类似功能 <!-- temporal_type: permanent -->
| # | 已有模块/文件 | 完整路径（相对优先） | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | MOD-PLAN-001 明日预案引擎 | `src/zephyr/plan_engine/tomorrow_boundary_planner.py` | 边界数据 | 该模块盘后生成边界（B 层），本模块盘前加载+情景匹配（C 层），职责不重叠 |

## 涉及的文件范围 <!-- temporal_type: permanent -->
| # | 文件/目录 | 完整路径（相对优先） | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 业务代码 | `src/zephyr/plan_engine/premarket_constraint_loader.py` | 读取 | 无变更（回填蓝图不改代码） |
| 2 | 测试代码 | `tests/plan_engine/test_plan_engine.py` | 读取 | 无变更 |
| 3 | 蓝图文件 | `docs/03_modules/_domain_plan_engine/premarket_constraint_loader/blueprint.md` | 新建 | 本文件 |

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
| — | — | 本模块尚无已实现代码 |

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
