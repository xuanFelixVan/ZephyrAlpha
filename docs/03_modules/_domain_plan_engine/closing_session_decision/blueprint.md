---
module_id: MOD-PLAN-003
title: "尾盘决策引擎 — 14:45基于明日高/低开概率的加减仓决策（ADD/REDUCE/HOLD/EXIT）"
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
actual_disk_path: src/zephyr/plan_engine/closing_session_decision.py
belongs_to: ""
depends_on: [MOD-PLAN-001, MOD-PLAN-002]
ssot_claims:
  - {claim: "BoundedActionAdvice 数据契约唯一真源", scope: "module"}
  - {claim: "尾盘决策阈值与规则（加仓>70%高开/减仓>60%低开/否则HOLD）唯一真源", scope: "module"}
responsibility_domain: 
design_maturity: production
build_status: stable
language: zh
generation: 1
summary: "BM-PLAN-03 尾盘决策：14:45-15:00 基于今日盘中推演与持仓状态，明日高开概率>70%→ADD/低开概率>60%→REDUCE/否则HOLD；与 §3.4 尾盘窗口分工：本模块是预测驱动调仓决策层，§3.4 是建仓执行层"
---
# Closing Session Decision 蓝图+施工图 — 尾盘决策引擎 — 14:45基于明日高/低开概率的加减仓决策（ADD/REDUCE/HOLD/EXIT）

> module_id: MOD-PLAN-003 | version: 0.1.2 | status: Active | layer: L2_domain (plan_engine)
> actual_disk_path: src/zephyr/plan_engine/closing_session_decision.py | generation: 1
> 设计真源: 41_buy_flow v1.7.0 §3.10.4 | 施工性质: 回填蓝图（代码已完工，83用例通过，2026-08-13 补建，遗留项 #29）

## 概述 <!-- temporal_type: permanent -->
本蓝图描述尾盘决策引擎——它解决"临近收盘时基于今日推演与持仓状态做加减仓决策"的问题（BM-PLAN-03，明日预案双层架构 A 层收尾环节）。核心职责：14:45-15:00 基于明日高开/低开概率做 ADD/REDUCE/HOLD/EXIT 决策（加仓阈值 70% 高开/减仓阈值 60% 低开）。它是预测驱动调仓决策层，与 41 §3.4 尾盘执行窗口分工：§3.4 负责把 31 号目标权重落成限价单，本模块负责基于概率对已有持仓做调整。尾盘决策未就绪→不操作（保持持仓过夜），宁可不操作也不在尾盘盲动。上游消费 BM-PLAN-01-C 盘中推演+BM-POS-01 持仓状态，下游调仓指令走 41 §3.4 尾盘执行窗口。

> **标准锚点（防幻觉）**——蓝图模板：blueprint_construction_template.md v2.1.0；设计真源：41_buy_flow.md v1.7.0 §3.10.4；机器真源：PostgreSQL depgraph（`python scripts/governance/extract_depgraph.py --modules MOD-PLAN-003`）。

## §0 代码对齐验证 <!-- temporal_type: permanent -->
### §0.1 代码文件清单
<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> 本节为自动生成（派生自 depgraph.nodes），禁止手写。生成命令：`python scripts/governance/extract_depgraph.py --modules MOD-PLAN-003`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 归属判定 | 阻塞原因 |
|---|--------|------------|------|:-----:|---------|---------|
| 1 | （占位——AUTOGEN 生成；当前实现为 closing_session_decision.py 单文件） | §3.1 | BoundedActionAdvice 契约+尾盘决策 | 已实现 | 本模块 | — |
### §0.2 对齐验证矩阵
| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| 蓝图类/函数名 = 代码类/函数名 | §4.1 签名逐一比对 closing_session_decision.py | ✅ |
| 代码 [BLUEPRINT] 头 = 本蓝图 module_id | 代码头 `# [BLUEPRINT] MOD-PLAN-003` | ✅ |
| §4.2 数据模型在 SSoT 文件中存在 | `grep "class BoundedActionAdvice"` | ✅ |
| §0.1 文件职责无重叠、归属无 ⚠️ | 单文件模块 | ✅ |
| §5.5 触发机制状态与代码一致 | 逐操作核对 | ✅ |
### §0.3 版本-代码映射
| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (基线回填) | BoundedActionAdvice 契约 + decide（阈值决策）已实现 | BM-PLAN-01-C 盘中推演输入 | 推演模块未就绪，签名预留 intraday_inference |
### §0.4 SSoT与责任唯一性声明
| # | 声明维度 | 本蓝图是真源 | 真源在别处（委托） | 委托目标 |
|---|---------|:----------:|:---------------:|---------|
| 1 | BoundedActionAdvice 契约+尾盘决策阈值规则 | ✅ | ❌ | — |
| 2 | 明日高/低开概率计算 | ❌ | ✅ | BM-PLAN-01-C（盘中推演） |
| 3 | 边界计算 | ❌ | ✅ | MOD-PLAN-001 |
| 4 | 下单执行 | ❌ | ✅ | 41 §3.4 尾盘窗口 / 40_execution_broker |
### §0.5 代码目录唯一性声明
| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/plan_engine/`（与 frontmatter.actual_disk_path 一致） |
| 2 | 已知副本目录 | 无 |
| 3 | 副本处置状态 | 无副本 |
### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PLAN-003`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PLAN-003` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-PLAN-003` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PLAN-003 | MOD-PLAN-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 1 文件 | 1 文件（§0.1） | ✅ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

## §1 设计背景与目标 <!-- temporal_type: permanent -->
### 1.1 背景
明日预案双层架构（41 §3.10）A 层：盘中推演在边界内执行后，14:45-15:00 还需基于今日推演结果与持仓做加减仓决策。本模块是 A 层尾盘收尾环节，与 §3.4 尾盘窗口分工消歧：§3.4 是"建仓执行"（把 31 号目标权重落成订单），本模块是"预测驱动调仓"（基于明日高/低开概率调整已有持仓或加仓）。41 §3.10.4 裁定"建设"，v1.7.0 已落码。
### 1.2 目标范围
| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | BoundedActionAdvice 契约+尾盘阈值决策（ADD>70%/REDUCE>60%/HOLD 默认） | 41 §3.10.4 已落码 |
| 2 | ❌ 排除 | 建仓执行（限价单落单） | 归 41 §3.4 尾盘窗口 / 40_execution_broker |
| 3 | ❌ 排除 | 概率计算本体 | 归 BM-PLAN-01-C 盘中推演 |
| 4 | ❌ 排除 | 边界计算/盘前加载 | 归 MOD-PLAN-001/002 |
### 1.4 运行场景约束
| 约束 | 影响 |
|------|------|
| 决策窗口 14:45-15:00 | 仅在尾盘时段执行，错过窗口不追单 |
| 未就绪→不操作 | 低开/高开概率均未超阈值→默认 HOLD（41 §3.10.4 降级） |
| 概率输入为外部参数 | 不内部计算概率，只消费盘中推演结果 |
### 1.5 利益相关者映射
| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| ZephyrAlpha-Owner | 阈值参数（70%/60%） | 设计+校准 | 契约破坏性变更审批权 |
| 41 §3.4 尾盘窗口 | 调仓指令可执行性 | 消费 | BoundedActionAdvice 字段完整 |
| 40_execution_broker | 订单生成 | 消费 | 指令→限价单 |
### 1.6 当前态/目标态差距
| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 契约+阈值决策 | 已实现并通过测试 | 同左 | 无差距 | — |
| 概率输入 | 外部参数 high_open_prob/low_open_prob（0.0 默认） | BM-PLAN-01-C 实时推演概率 | 推演模块未就绪 | P1 |
### 1.7 典型场景
| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 尾盘加仓 | high_open_prob>0.70 | decide→ADD→price_bound=(box_lower,box_upper)/max_weight=0.30 | BoundedActionAdvice(ADD) |
| 尾盘减仓 | low_open_prob>0.60 | decide→REDUCE→max_weight=current_weight | BoundedActionAdvice(REDUCE) |
| 持有不动 | 均未超阈值 | decide→HOLD→默认 | BoundedActionAdvice(HOLD) |

## §2 模块边界 <!-- temporal_type: permanent -->
### 2.1 职责边界
> **核心职责声明**：本蓝图的核心职责是 `14:45-15:00 基于明日高/低开概率产出加减仓动作建议 BoundedActionAdvice`。职责数量：1。

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 尾盘阈值决策 | ADD/REDUCE/HOLD 三分支，价格区间来自盘中推演 | 本模块 |
| 2 | ❌ 排除 | 建仓执行落单 | 限价单执行归执行层 | 41 §3.4 / 40_execution_broker |
| 3 | ❌ 排除 | 概率计算 | 归 BM-PLAN-01-C | BM-PLAN-01-C |
| 4 | ❌ 排除 | 边界/盘前/推演 | 归 MOD-PLAN-001/002 / BM-PLAN-01-C |

#### 职责唯一性声明
| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 尾盘阈值决策（预测驱动调仓） | [41 §3.4 尾盘窗口, MOD-PA-006] | `python scripts/governance/check_ssot_uniqueness.py --blueprint MOD-PLAN-003` |

## §3 架构设计 <!-- temporal_type: permanent -->
### 3.1 组件架构
| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | BoundedActionAdvice | 边界内动作建议契约（5 字段） | — | frozen dataclass |
| 2 | ClosingSessionDecision.decide | 尾盘决策入口 | ADD/REDUCE/HOLD 常量阈值 | 同步调用 |
### 3.2 数据流
| # | 上游 | 处理逻辑 | 下游 | 数据格式 | 转换规则 |
|---|--------|---------|---------|---------|---------|
| 1 | BM-PLAN-01-C 盘中推演（box_upper/box_lower）+ BM-POS-01 持仓（weight）+ 外部概率 | ①high_open_prob>0.70→ADD（max_weight=0.30）→②low_open_prob>0.60→REDUCE（max_weight=current）→③默认 HOLD | BoundedActionAdvice→41 §3.4 / 40_execution_broker | frozen dataclass | 阈值硬编码，概率=外部参数 |
### 3.3 状态生命周期
本模块无状态机（纯决策函数，每次调用独立产出不可变建议）。

## §4 接口契约 <!-- temporal_type: permanent -->
> 数据契约为 frozen dataclass（41 §3.10.2 输出契约原样落码，见 §16 D-PLAN003-02）。

### 4.1 公共 API
```python
class ClosingSessionDecision:
    """尾盘决策引擎——14:45 基于明日高/低开概率做加减仓决策"""
    def decide(self, symbol: str, intraday_inference: dict[str, Any],
               position_state: dict[str, Any],
               high_open_prob: float = 0.0,
               low_open_prob: float = 0.0) -> BoundedActionAdvice: ...
```
| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `decide()` | ①high_open_prob>0.70→ADD（price_bound=(box_lower,box_upper), max_weight=0.30, reason 含概率）→②elif low_open_prob>0.60→REDUCE（price_bound同上, max_weight=current_weight, reason 含概率）→③默认 HOLD（price_bound同上, max_weight=current_weight, reason="均未超阈值"） | 步骤①②阈值分支 |

### 4.2 数据模型
```python
@dataclass(frozen=True)
class BoundedActionAdvice:
    symbol: str
    action: str                     # "ADD" / "REDUCE" / "HOLD" / "EXIT"
    price_bound: tuple[float,float] # 动作允许的价格区间（在 boundary 内）
    max_weight: float               # 动作允许的最大权重
    reason: str                     # 边界内推演理由
```
| 模型名 | SSoT文件 | 其他定义位置 | 状态 |
|--------|---------|------------|------|
| BoundedActionAdvice | closing_session_decision.py | tomorrow_boundary_planner.py（41 §3.10.2 契约，同域一致） | ✅ 唯一源 |
### 4.3 输入契约
| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `decide()` | `symbol` / `intraday_inference` / `position_state` | ✅/✅/✅ | intraday_inference 须含 box_upper/box_lower；position_state 须含 weight |
| `decide()` | `high_open_prob` / `low_open_prob` | ❌/❌ | [0,1] 区间；缺省 0.0（推演未就绪降级为 HOLD） |
### 4.4 输出契约
| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `decide()` | `BoundedActionAdvice`（action∈{ADD,REDUCE,HOLD}，price_bound=(box_lower,box_upper)） | 错误码契约 ZA-PLAN-0003（ClosingDecisionError，代码头声明）；当前实现异常向上传播由调用方捕获 |
### 4.5 MCP 接口（条件可选）
本模块不暴露 MCP 接口。
### 4.6 契约版本
| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 action 类型（如 EXIT 扩展） | ✅ 向后兼容 | patch+1 |
| 修改决策阈值（0.70/0.60） | ⚠️ 需通知 | 实盘校准后更新 |
| 删除/重命名字段 | ❌ 破坏性 | 需 Owner 审批 |

**变更通知**：破坏性变更→Owner 审批+蓝图 minor+1；兼容性变更→AI 自主+patch+1。
### 4.7 OCP 扩展点（条件可选）
本模块无 OCP 扩展点。概率输入参数（high_open_prob/low_open_prob）可平滑替换为 BM-PLAN-01-C 实时推演输出，签名不变。

## §5 约束条件 <!-- temporal_type: permanent -->
### 5.1 技术约束
| # | 约束 | 值 |
|---|------|-----|
| 1 | 尾盘加仓阈值 | 明日高开概率 >0.70（41 §3.10.4，实盘校准来源） |
| 2 | 尾盘减仓阈值 | 明日低开概率 >0.60（41 §3.10.4，实盘校准来源） |
| 3 | 决策窗口 | 14:45-15:00（DECISION_WINDOW_START/END） |
| 4 | 默认动作 | HOLD（未超阈值时） |
| 5 | 不变量 | 未就绪→不操作（保持持仓过夜）；ADD max_weight=0.30；REDUCE/HOLD max_weight=current_weight |
### 5.2 容量估算
| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 每日决策标的数 | ≤10 | ≤50 | 单标的 O(1) | ✅ | 无需扩展 |
| 单次决策耗时 | <1ms | <10ms | 纯比较 | ✅ | 无需扩展 |
### 5.3 迁移/废弃方案（条件可选）
无迁移/废弃。
### 5.4 非功能需求与服务水平
| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 正确性 | 决策输出确定性 | 同输入同输出 | 单测断言 | 决策一致率 | 100% | 0 次 | 测试失败即阻断 |
| 时效性 | 单次决策耗时 | <10ms | 耗时日志 | 决策耗时 | 99%<10ms | 每日 1 次超限 | >50ms 告警 |
### §5.5 自动化触发机制
| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|---------|
| decide（尾盘决策） | auto_scheduled | 14:45-15:00 窗口内按 15 分钟节奏评估 | 函数已实现✅；auto_scheduled 接线待 BM-PLAN-01-C 盘中推演就绪（当前 MVP 由调用方直调） |
### §5.7 禁止模式与导入约束
| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 窗口外追单 | 只在 14:45-15:00 窗口内决策 | 41 §3.10.4 窗口约束 |
| 2 | 编码模式 | 概率缺失时盲动 | 默认 HOLD（概率 0.0 降级） | 降级铁律：未就绪→不操作 |
| 3 | 编码模式 | 重算概率 | 只消费 BM-PLAN-01-C 推演概率数字 | 职责分离：决策层不越界推演层 |
| 4 | 导入源 | zephyr.plan_engine 上游模块（premarket/tomorrow_boundary） | 字典传参（不直接 import 上游循环） | 包内循环约束 |

## §6 错误处理 <!-- temporal_type: permanent -->
| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 概率输入越界（>1/<0） | 调用方约束（本函数未强制校验） | 行为未定义；由调用方保证 | 单标的一次决策 |
| 2 | 概率缺失（默认 0.0） | 参数缺省 | 降级 HOLD，不操作 | 单标的一次决策 |
| 3 | 依赖循环声明 | — | 只依赖共享常量，无 A→B→A 循环 | — |
### 6.1 可观测性规格
| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| closing_decision_total（按 action） | Counter | 手动上报 | — | P3 |
| closing_decision_hold_rate | Gauge | 手动上报 | 长期>90%（频繁未触发） | P3 |
### 6.2 退化矩阵
| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| 概率输入缺失 | 默认 HOLD | ADD/REDUCE | 概率 0.0 降级 | 推演数据恢复 |
| 尾盘决策模块整体 | 保持现有持仓过夜 | 加减仓调仓 | 不操作=无额外风险 | 模块恢复 |

## §7 安全考量 <!-- temporal_type: permanent -->
| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 尾盘盲动导致隔夜风险 | 高 | 未就绪→默认 HOLD（41 §3.10.4 降级铁律） | 默认路径单测 |
| 2 | 加仓超限 | 中 | ADD 的 max_weight=0.30（与 TomorrowBoundary 一致） | 字段断言 |

## §8 测试策略 <!-- temporal_type: permanent -->
| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | 契约+决策三分支 | TestBoundedActionAdvice（字段/frozen）、TestClosingSessionDecision（ADD>70%/REDUCE>60%/HOLD 默认/等号边界/price_bound/max_weight/reason） | 全部通过 |
| 2 | 回归验证 | 41 号施工全体 | 3 个测试文件连续 2 轮全过（41 v1.7.0 记录） | 83/83 通过 |

测试文件：`tests/plan_engine/test_plan_engine.py`（plan_engine 三模块共 17 用例，本模块覆盖 TestBoundedActionAdvice+TestClosingSessionDecision）。

## §9 依赖关系 <!-- temporal_type: permanent -->
### 9.1 依赖声明
| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| BM-PLAN-01-C（盘中推演） | 必须 | box_upper/box_lower（通过 intraday_inference 字典传参） | — | 推演模块蓝图（待建） |
| BM-POS-01（持仓状态） | 必须 | weight（通过 position_state 字典传参） | — | 持仓模块蓝图（待建） |
| 41_buy_flow 设计备忘 | 必须 | §3.10.4 阈值与分工消歧 | v1.7.0 | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/41_buy_flow.md` |
### 9.2 依赖图对齐声明
| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §9.1 依赖声明 ↔ depgraph.nodes | 依赖条目在 depgraph 有对应节点 | 已对齐 | `python scripts/governance/extract_depgraph.py --modules MOD-PLAN-003` |
| 2 | §10 产出物路径 ↔ path_mappings | 路径一致 | 已对齐 | 同上 |
### 9.5 概念重叠声明
| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | 尾盘窗口（14:45-15:00） | 时段/窗口 | 41 §3.4 / MOD-PA-006 | 共存（41 §3.10.4 分工消歧：本模块是预测驱动调仓决策层，§3.4 是建仓执行层） | 已处置 |
| 2 | BoundedActionAdvice 契约 | 数据模型 | MOD-PLAN-001（TomorrowBoundary 为不同契约） | 无重叠（BoundedActionAdvice 唯一源在本模块） | 已处置 |
### 9.6 依赖链风险评级
| # | 依赖链 | 链深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:-----:|---------|---------|---------|
| 1 | MOD-PLAN-003→BM-PLAN-01-C | 2 | L1 | 有（§6.2 概率缺失降级 HOLD） | 已有熔断 |

## §10 产出物存放目录 <!-- temporal_type: permanent -->
| 产出物类型 | 存放完整路径（相对优先） | 职责 | consumer_min | 注册位置 |
|----------|---------------|------|:-----------:|---------|
| 蓝图文件 | `docs/03_modules/_domain_plan_engine/closing_session_decision/blueprint.md` | 本文件 | ≥0 | blueprint_registry.yaml |
| 业务代码 | `src/zephyr/plan_engine/closing_session_decision.py` | 尾盘决策引擎 | ≥1 | `src/zephyr/plan_engine/__init__.py` __all__ |
| 测试代码 | `tests/plan_engine/test_plan_engine.py` | 与 MOD-PLAN-001/002 共 17 用例 | ≥0 | pytest 自动发现 |

## §11 集成目标 <!-- temporal_type: permanent -->
| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| 41 §3.4 尾盘窗口 | 调仓指令消费 | BoundedActionAdvice→尾盘执行窗口限价单 | 字段完整性校验 |
| 40_execution_broker | 订单生成 | 调仓指令→限价单执行 | 端到端测试（未接线，P2） |

## §12 需要更新的相关内容 <!-- temporal_type: permanent -->
| # | 需更新的文件 | 完整路径（相对优先） | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | 新增 MOD-PLAN-003 条目 | 回填登记 |
| 2 | 依赖图 | PostgreSQL depgraph | MOD-PLAN-003 节点核验 | 五图对齐 |

## §13 已知风险与缓解 <!-- temporal_type: permanent -->
| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 阈值 70%/60% 未经实盘校准 | 中 | 中 | 默认 HOLD 兜底；校准后更新常量 | 风险 |
| 2 | 概率输入长期为 0.0（推演未就绪） | 中 | 低 | 降级 HOLD 不操作=无额外风险 | 风险 |
| 3 | 与 §3.4 尾盘窗口时段重叠但职责不同 | 低 | 低 | 41 §3.10.4 已分工消歧，蓝图显式声明 | 负面后果 |

## §14 施工指引 <!-- temporal_type: construction_temporary（施工已完成，本节保留状态记录） -->
### 14.1 施工策略
| 项目 | 内容 |
|------|------|
| 施工阶段数 | 单 Phase 一次性完成（AI-BUY-001，41 号 v1.7.0 施工批次） |
| 施工模式 | 新建 |
| 核心风险 | 分工消歧被混淆：决策层≠执行层 |
| 目标 generation | 1 |
### 14.2 前置条件
| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | 41_buy_flow v1.6.0+ §3.10.4 裁定 | hard | 已定稿（v1.7.0 落码） | ✅ |
| 2 | BM-PLAN-01-C 概率签名预留 | soft | intraday_inference/box_upper/box_lower 签名已预留 | ✅ |
### 14.3 实施步骤
回填蓝图，施工已完成：步骤 1（BoundedActionAdvice 契约）已完成；步骤 2（decide 三分支阈值决策）已完成；步骤 3（17 用例中的本模块部分）已完成。验证命令：`python -m pytest tests/plan_engine/test_plan_engine.py -q`。
### 14.4 回滚方案
| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 全部 | 决策行为偏离 41 §3.10.4 | 以 41 §3.10.4 规则为基准修复并重跑测试 |
### 14.5 施工完成与生产就绪标准
| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | 代码文件存在且非空 | `src/zephyr/plan_engine/closing_session_decision.py` 存在 | 完成 | ✅ |
| 2 | 测试通过 | test_plan_engine.py exit 0 | 完成 | ✅ |
| 3 | 代码头十五字段完整 | [BLUEPRINT] MOD-PLAN-003 等字段齐全 | 就绪 | ✅ |
### 14.6 施工状态
| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | 施工者（AI-BUY-001，2026-08-13） |
| verification_status | passed | 审计者（83 用例连续 2 轮全过，41 v1.7.0 记录） |
| code_alignment_verified | yes | 审计者（§4 签名与代码逐一比对一致） |
### 14.7 参考实现规格
| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 尾盘决策三分支 | 算法 | 41 §3.10.4：high_open_prob>0.70→ADD / low_open_prob>0.60→REDUCE / 否则→HOLD | decide |
| 2 | 决策窗口 | 配置 | 41 §3.10.4：14:45-15:00 | DECISION_WINDOW_START/END |
| 3 | 分工消歧 | 协议 | 41 §3.10.4：本模块=预测驱动调仓决策层；§3.4=建仓执行层（两者时段重叠但职责不同） | §2.1/§11 |
### 14.8 施工参考卡
| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/plan_engine/test_plan_engine.py -q` | 回归验证 | 无 | 17 passed |
| 2 | 常量 | `ADD_POSITION_THRESHOLD` / `REDUCE_POSITION_THRESHOLD` | 0.70 / 0.60 | float | 校准只改常量 |
### 14.10 故障与操作手册
| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 运行 | 概率输入恒为 0.0 | BM-PLAN-01-C 未就绪 | 查 intraday_inference 来源 | 推演模块就绪后传真实概率 | 决策输出从 HOLD 转为 ADD/REDUCE |
| 2 | 运行 | 频繁 HOLD | 阈值过高 | 查 HOLD 率指标 | 校准阈值后更新常量 | ADD/REDUCE 占比提升 |
### 14.12 并发操作模型
本模块为无状态纯决策，无并发操作。

## §15 容量升级附录 <!-- temporal_type: permanent -->
### §15.1 容量基线
| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 每日决策标的数 | ≤10 | 决策日志 |
| 单次决策耗时 | <1ms | 耗时日志 |
### §15.2 缺口清单与升级版本矩阵
| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-PLAN003-01 | 概率输入外部参数（推演未就绪） | BM-PLAN-01-C 实时推演概率接入 | P1 | 推演模块就绪 | v1.0.0 | 未触发 |

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.1.0 | 1 | 基线回填 | 契约+阈值决策+分工消歧声明 | ✅ |

## §16 决策记录 <!-- temporal_type: permanent -->
| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-PLAN003-01 | 尾盘决策窗口 14:45-15:00（与建仓执行窗口重叠） | A 重叠+分工/B 分时段 | A | 41 §3.10.4：时段重叠但职责不同，决策层与执行层分离 | 2026-08-12 |
| 2 | D-PLAN003-02 | 未就绪→默认 HOLD 不操作 | A HOLD/B 按情绪操作 | A | 41 §3.10.4 降级铁律：宁可不操作也不在尾盘盲动 | 2026-08-12 |
| 3 | D-PLAN003-03 | 数据契约用 frozen dataclass | A dataclass/B Pydantic | A | 41 §3.10.2 输出契约原文即 @dataclass；与交易域惯例一致 | 2026-08-13 |
| 4 | D-PLAN003-04 | ADD max_weight=0.30 与 TomorrowBoundary 一致 | A 一致/B 独立 | A | 减仓上限 30% 统一口径，避免边界层与决策层阈值漂移 | 2026-08-13 |

## 必备链接 <!-- temporal_type: permanent -->
| # | 文件 | module_id | 完整路径（相对优先） | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 买入流 spec（设计真源） | — | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/41_buy_flow.md` | §3.10.4 阈值/窗口/分工消歧 |
| 2 | 蓝图模板 | GOV-028 | `docs/01_policies_and_standards/templates/blueprint_construction_template.md` | v2.1.0 章节合规 |

## 术语表 <!-- temporal_type: permanent -->
| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| 尾盘决策 | 14:45-15:00 基于高/低开概率的加减仓决策 | 尾盘建仓执行 | 决策层（本模块）vs 执行层（41 §3.4），时段重叠职责不同 |
| ADD | 加仓博明天高开（概率>70%） | 建仓（买入执行） | ADD 是尾盘调仓建议，建仓是 31 号目标权重的执行 |
| REDUCE | 减仓防明天低开（概率>60%） | 卖出止损 | REDUCE 是预测驱动调仓，卖出止损是风控驱动 |
| 未就绪→不操作 | 概率未超阈值默认 HOLD | 加载失败=致命 | 概率缺失是精度降级，边界缺失是安全基线破裂 |

## 成熟度声明 <!-- temporal_type: permanent -->
| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | 41 号重大修订 | 尾盘决策裁定已落码 |
| 接口契约 | stable | 高 | 破坏性变更需 Owner 审批 | 签名与 41 §3.10.4 一致 |
| 数据模型 | frozen | 高 | 41 §3.10.2 契约修订 | frozen dataclass 原样落码 |
| 阈值参数 | evolving | 中 | BM-PLAN-01-C 校准完成 | 初始值未经实盘校准 |

## 版本演进路线图 <!-- temporal_type: permanent -->
| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 基线回填（代码先行，蓝图后补，遗留项 #29） | — | 已完成 |
| v1.0.0 | BM-PLAN-01-C 概率接入+阈值校准 | v0.1.0 | 未施工 |

## 已知问题与盲点登记 <!-- temporal_type: permanent -->
| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 阈值 70%/60% 未经实盘校准 | 中 | BM-PLAN-01-C 未就绪 | 推演模块产出后按 track record 校准 | §5.1 #1/#2 | 未解决 |

## 自检与闭合清单 <!-- temporal_type: permanent -->
| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口执行流程引用 41 号节号 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §8 有对应测试 | 阈值/窗口/不变量→测试用例 | ✅ |
| 4 | 设计 | §0.1 代码文件在 §10 有对应产出物路径 | 单文件核对 | ✅ |
| 5 | 后 | 临时时态内容已清理 | 施工已完成，§14.3 仅留状态 | ✅ |

## 项目中已有类似功能 <!-- temporal_type: permanent -->
| # | 已有模块/文件 | 完整路径（相对优先） | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | MOD-PA-006 分批建仓引擎 | `src/zephyr/pf_alloc/batched_position_builder.py` | 建仓/加仓 | 该模块管建仓执行（how），本模块管尾盘调仓决策（whether/when），职责不重叠 |
| 2 | 42_sell_flow 止损模块 | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/42_sell_flow.md` | 减仓 | 该模块管风控止损（被动），本模块管预测驱动调仓（主动），触发源不同 |

## 涉及的文件范围 <!-- temporal_type: permanent -->
| # | 文件/目录 | 完整路径（相对优先） | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 业务代码 | `src/zephyr/plan_engine/closing_session_decision.py` | 读取 | 无变更（回填蓝图不改代码） |
| 2 | 测试代码 | `tests/plan_engine/test_plan_engine.py` | 读取 | 无变更 |
| 3 | 蓝图文件 | `docs/03_modules/_domain_plan_engine/closing_session_decision/blueprint.md` | 新建 | 本文件 |

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
| `src/zephyr/plan_engine/closing_session_decision.py` | ✅ 已实现 | |

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
