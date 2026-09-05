---
module_id: MOD-TRIG-001
title: "扳机清单注册与仲裁引擎 — 触发器统一注册+优先级仲裁+同源去重+冷却期防重"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
layer: L2_domain
functional_domain: trading
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-13"
last_updated: "2026-08-13"
priority: P1
blueprint_level: module
actual_disk_path: src/zephyr/trading/trigger_registry.py
belongs_to: ""
depends_on: []
ssot_claims:
  - {claim: "TriggerEntry/TriggeredEvent 注册格式唯一真源", scope: "module"}
  - {claim: "优先级仲裁与同源去重规则唯一真源", scope: "module"}
  - {claim: "MVP 15 条扳机清单唯一真源", scope: "module"}
responsibility_domain: 
design_maturity: production
build_status: production
language: zh
generation: 1
summary: "41 §3.9 条件触发执行队列：买入/卖出/执行/风控触发器统一注册 TriggerEntry，priority 1-5 仲裁+scope 排序+同源去重+冷却期，MVP 15 条清单预注册"
---
# Trigger Registry 蓝图+施工图 — 扳机清单注册与仲裁引擎 — 触发器统一注册+优先级仲裁+同源去重+冷却期防重

> module_id: MOD-TRIG-001 | version: 0.1.3 | status: Active | layer: L2_domain (trading)
> actual_disk_path: src/zephyr/trading/trigger_registry.py | generation: 1
> 设计真源: 41_buy_flow v1.7.0 §3.9 | 施工性质: 回填蓝图（代码已完工，83用例通过，2026-08-13 补建，遗留项 #29）

## 概述 <!-- temporal_type: permanent -->
本蓝图描述扳机清单注册与仲裁引擎——它解决"买入/卖出/执行/风控四类触发器各自轮询导致冲突无人仲裁、重复检测"的问题。核心职责：触发器统一注册（TriggerEntry 注册格式）、优先级仲裁（priority 升序+scope 排序，Kill Switch 无条件覆盖）、同源去重（共享 condition 只算一次）与冷却期防重复派发。当前规模 MVP 15 条触发器（单标的单策略），目标容量 Phase 2 多策略并发（触发器数十条）。上游为各 spec 域的 condition 判定函数（41/42/40/35/36/37），下游为 60 号进程内事件总线（派发承载）与各 action 消费者。

> **标准锚点（防幻觉）**——蓝图模板：blueprint_construction_template.md v2.1.0；设计真源：41_buy_flow.md v1.7.0 §3.9；机器真源：PostgreSQL depgraph（`python scripts/governance/extract_depgraph.py --modules MOD-TRIG-001`）。

## §0 代码对齐验证 <!-- temporal_type: permanent -->
### §0.1 代码文件清单
<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> 本节为自动生成（派生自 depgraph.nodes），禁止手写。生成命令：`python scripts/governance/extract_depgraph.py --modules MOD-TRIG-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 归属判定 | 阻塞原因 |
|---|--------|------------|------|:-----:|---------|---------|
| 1 | （占位——AUTOGEN 生成；当前实现为 trigger_registry.py 单文件） | §3.1 | 注册表+仲裁+去重+MVP 清单 | 已实现 | 本模块 | — |
### §0.2 对齐验证矩阵
| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| 蓝图类/函数名 = 代码类/函数名 | §4.1 签名逐一比对 trigger_registry.py | ✅ |
| 代码 [BLUEPRINT] 头 = 本蓝图 module_id | 代码头 `# [BLUEPRINT] MOD-TRIG-001` | ✅ |
| §4.2 数据模型在 SSoT 文件中存在 | `grep "class TriggerEntry\|class TriggeredEvent"` | ✅ |
| §0.1 文件职责无重叠、归属无 ⚠️ | 单文件模块 | ✅ |
| §5.5 触发机制状态与代码一致 | 逐操作核对 | ✅ |
### §0.3 版本-代码映射
| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (基线回填) | 2 数据契约 + TriggerRegistry（注册/注销/评估/仲裁）+ MVP 15 条清单全部已实现 | — | — |
### §0.4 SSoT与责任唯一性声明
| # | 声明维度 | 本蓝图是真源 | 真源在别处（委托） | 委托目标 |
|---|---------|:----------:|:---------------:|---------|
| 1 | 触发器注册格式/仲裁/去重/冷却规则 | ✅ | ❌ | — |
| 2 | 各触发器 condition 判定逻辑 | ❌ | ✅ | 41/42/40/35/36/37 各自 spec 域 |
| 3 | 事件派发通道 | ❌ | ✅ | 60 号进程内事件总线 |
### §0.5 代码目录唯一性声明
| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/trading/`（与 frontmatter.actual_disk_path 一致） |
| 2 | 已知副本目录 | 无 |
| 3 | 副本处置状态 | 无副本 |
### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TRIG-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TRIG-001` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-TRIG-001` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TRIG-001 | MOD-TRIG-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | 1 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

## §1 设计背景与目标 <!-- temporal_type: permanent -->
### 1.1 背景
买入（41）、卖出（42）、执行（40）、风控（35/36/37）四侧各有条件触发器，若各模块独立轮询则冲突无人仲裁（如确认仓放行 vs 回撤暂停同时触发）、判定重复计算（突破失败在 41/42 各判一次）。41 §3.9 裁定统一注册到扳机清单，v1.7.0 已落码为本模块。
### 1.2 目标范围
| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | TriggerEntry 注册格式+注册/注销/评估/冲突消解+MVP 15 条清单 | 41 §3.9 已落码 |
| 2 | ❌ 排除 | 各触发器判定逻辑本体 | 归各自 spec 域（编排层不越界） |
| 3 | ❌ 排除 | 独立 DO 决策编排器 | 41 §2.2.1 裁定不建，TriggerList+硬边界承载 |
### 1.4 运行场景约束
| 约束 | 影响 |
|------|------|
| 三维度解耦（what/how much/how） | 扳机清单只做注册/仲裁/派发，判定逻辑留在各域 |
| MVP 单标的单策略 | 41 §3.9 过度工程审查：MVP 可降级为独立轮询，Phase 2 强制启用 |
| 事件总线为派发承载 | 本模块产出排序后事件列表，总线订阅分发 |
### 1.5 利益相关者映射
| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| ZephyrAlpha-Owner | 优先级表裁定 | 设计 | MVP 清单增删审批权 |
| 41/42/40/35/36/37 各 spec 域 | condition 注入接口稳定 | 生产 | 签名变更需通知 |
| 60 号事件总线 | 事件格式 TriggeredEvent | 消费 | 契约变更需同步 |
### 1.6 当前态/目标态差距
| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 注册/仲裁/去重 | 已实现并通过测试 | 同左 | 无差距 | — |
| condition 注入 | MVP 清单为占位 condition（恒 False） | 各域真实 condition 注入 | 各 spec 未接线 | P1 |
| 事件总线派发 | 产出排序事件列表 | 60 号总线订阅分发 | 总线集成未接线 | P2 |
### 1.7 典型场景
| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 启动注册 | 系统启动 | create_mvp_registry→15 条占位清单注册 | TriggerRegistry 实例 |
| 冲突仲裁 | Kill Switch 与加仓同时触发 | evaluate_all→resolve_conflicts→priority=1 覆盖一切 | 仅 Kill Switch 事件 |
| 同源去重 | 突破失败驱动 41 暂停+42 止损 | 共享 condition 只算一次，按 trigger_id 分发两 action | 2 条事件，1 次判定 |

## §2 模块边界 <!-- temporal_type: permanent -->
### 2.1 职责边界
> **核心职责声明**：本蓝图的核心职责是 `触发器统一注册、按优先级仲裁冲突、同源去重后产出待派发事件列表`。职责数量：3。

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 注册表管理 | register/unregister/entries，trigger_id 唯一性+priority 边界校验 | 本模块 |
| 2 | ✅ 包含 | 优先级仲裁 | priority 升序取最高，同级按 PORTFOLIO>STRATEGY>POSITION；priority=1 覆盖一切 | 本模块 |
| 3 | ✅ 包含 | 同源去重+冷却期 | id(condition) 缓存判定结果；cooldown_sec 防重复派发 | 本模块 |
| 4 | ❌ 排除 | condition 判定逻辑 | 各触发器判定在各自 spec 域 | 41/42/40/35/36/37 |
| 5 | ❌ 排除 | 事件持久化/总线传输 | 派发通道归事件总线 | 60 号 |

#### 职责唯一性声明
| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 触发器注册与优先级仲裁 | [MOD-PA-006, 42_sell_flow 各模块] | `python scripts/governance/check_ssot_uniqueness.py --blueprint MOD-TRIG-001` |
| 决策编排（5 路径冲突消解） | [BM-BUY-03 DO] | 41 §2.2.1 裁定不建独立 DO，本模块承载 |

## §3 架构设计 <!-- temporal_type: permanent -->
### 3.1 组件架构
| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | TriggerEntry / TriggeredEvent | 注册项 / 已触发事件契约 | — | frozen dataclass |
| 2 | TriggerRegistry | 注册/注销/全量评估/冲突消解 | 内存字典 | 同步调用 |
| 3 | MVP_TRIGGER_LIST + create_mvp_registry | 15 条 MVP 清单常量+工厂 | TriggerRegistry | 启动注入 |
### 3.2 数据流
| # | 上游 | 处理逻辑 | 下游 | 数据格式 | 转换规则 |
|---|--------|---------|---------|---------|---------|
| 1 | 各 spec 域 condition 函数 | ①register 注册→②evaluate_all（冷却过滤→同源去重→条件求值）→③按 priority+scope 排序 | TriggeredEvent 列表→60 号事件总线 | frozen dataclass | condition(ctx)→bool→事件 |
| 2 | 同时触发的事件集 | resolve_conflicts：priority=1 覆盖→否则取最小 priority 集合同级 scope 排序 | 消解后事件列表→action 消费者 | frozen dataclass | 风险优先原则 |
### 3.3 状态生命周期
触发器注册项生命周期：

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| 未注册 | register() | 已注册 | trigger_id 唯一且 priority∈[1,5] |
| 已注册 | evaluate_all 命中 | 已触发 | condition(ctx)=True 且过冷却期 |
| 已触发 | 冷却期未满 | 冷却中 | now-last_fired<cooldown_sec 跳过 |
| 已注册 | unregister() | 未注册 | 同时清除冷却时间戳 |

## §4 接口契约 <!-- temporal_type: permanent -->
> 数据契约为 frozen dataclass（41 §3.9 注册格式原样落码，见 §16 D-TRIG001-01）。

### 4.1 公共 API
```python
class TriggerRegistry:
    """扳机清单注册表——统一注册/优先级仲裁/同源去重/冷却防重"""
    def __init__(self) -> None: ...
    def register(self, entry: TriggerEntry) -> None: ...
    def unregister(self, trigger_id: str) -> None: ...
    @property
    def entries(self) -> dict[str, TriggerEntry]: ...
    def evaluate_all(self, context: dict[str, Any] | None = None) -> list[TriggeredEvent]: ...
    def resolve_conflicts(self, events: list[TriggeredEvent]) -> list[TriggeredEvent]: ...

def create_mvp_registry() -> TriggerRegistry: ...  # 预注册 15 条 MVP 触发器（占位 condition）
MVP_TRIGGER_LIST: Final  # 15 条注册项常量（见 §14.7 清单表）
```
| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `register()` | ①trigger_id 查重→②priority∈[1,5] 校验→③写入注册表（41 §3.9 注册格式） | 重复/越界抛 ValueError |
| `unregister()` | ①注册表移除→②冷却时间戳同步清除 | 幂等（不存在不报错） |
| `evaluate_all()` | ①遍历注册项→②冷却期过滤→③id(condition) 同源去重求值→④命中生成 TriggeredEvent 并记录触发时间→⑤按 (priority, scope) 排序返回 | 步骤③去重省重复判定 |
| `resolve_conflicts()` | ①空列表直返→②存在 priority=1 则只返回 Kill Switch 组→③否则取最小 priority 集合按 scope 排序（41 §3.9 仲裁规则） | 步骤②无条件覆盖 |
| `create_mvp_registry()` | ①遍历 MVP_TRIGGER_LIST→②逐条构造 TriggerEntry（占位 condition）→③register | 占位 condition 恒 False |

### 4.2 数据模型
```python
@dataclass(frozen=True)
class TriggerEntry:
    trigger_id: str               # 唯一标识
    source_module: str            # "41"/"42"/"40"/"35"/"36"/"37"
    condition: Callable           # 判定函数，返回 bool
    action: str                   # 触发动作
    priority: int                 # 1(最高)-5(最低)
    scope: str                    # POSITION / STRATEGY / PORTFOLIO
    cooldown_sec: int = 60        # 冷却期

@dataclass(frozen=True)
class TriggeredEvent:
    trigger_id: str
    source_module: str
    action: str
    priority: int
    scope: str
    context: dict[str, Any] = field(default_factory=dict)
```
| 模型名 | SSoT文件 | 其他定义位置 | 状态 |
|--------|---------|------------|------|
| TriggerEntry | trigger_registry.py | — | ✅ 唯一源 |
| TriggeredEvent | trigger_registry.py | — | ✅ 唯一源 |
| MVP_TRIGGER_LIST | trigger_registry.py | — | ✅ 唯一源 |
### 4.3 输入契约
| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `register()` | `entry` | ✅ | trigger_id 全局唯一；priority∈[1,5]；condition 可调用 |
| `evaluate_all()` | `context` | ❌ | 传递给 condition 的上下文字典，None→{} |
| `resolve_conflicts()` | `events` | ✅ | TriggeredEvent 列表，可为空 |
### 4.4 输出契约
| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `register()` | None | ValueError（trigger_id 重复 / priority 越界）；错误码契约 ZA-TRIG-0001（TriggerRegistrationError，代码头声明） |
| `evaluate_all()` | 按 (priority,scope) 排序的 TriggeredEvent 列表 | condition 异常向上传播（由调用方捕获）；冲突错误码 ZA-TRIG-0002（TriggerConflictError，代码头声明） |
| `resolve_conflicts()` | 消解后事件列表（含 Kill Switch 覆盖语义） | — |
### 4.5 MCP 接口（条件可选）
本模块不暴露 MCP 接口。
### 4.6 契约版本
| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增触发器条目（MVP_TRIGGER_LIST） | ✅ 向后兼容 | Owner 审批后加入清单 |
| 新增方法/字段 | ✅ 向后兼容 | 不影响已有消费者 |
| 修改 priority/scope 取值语义 | ❌ 破坏性 | 需 Owner 审批+全消费者通知 |

**变更通知**：破坏性变更→Owner 审批+蓝图 minor+1；兼容性变更→AI 自主+patch+1。
### 4.7 OCP 扩展点（条件可选）
| 扩展点 | 基类/接口 | 默认实现 | 扩展契约 | 注册方式 |
|--------|----------|---------|---------|---------|
| 新触发器 | `TriggerEntry` 注册项 | MVP_TRIGGER_LIST 15 条 | trigger_id 唯一+priority∈[1,5]+condition(ctx)->bool | `register()` 运行时注册 / 清单常量追加 |

## §5 约束条件 <!-- temporal_type: permanent -->
### 5.1 技术约束
| # | 约束 | 值 |
|---|------|-----|
| 1 | 优先级范围 | 1（最高）-5（最低），冲突时高优先级覆盖（41 §3.9） |
| 2 | scope 排序 | PORTFOLIO(0) > STRATEGY(1) > POSITION(2)（同优先级时） |
| 3 | 默认冷却期 | 60 秒（Kill Switch 组 0 秒，EXE_MAKE_OR_TAKE 30 秒，熔断/限频 300 秒） |
| 4 | 不变量 | 判定逻辑在各自 spec 域内；同源 condition 只算一次；注册表不引入新算法 |
### 5.2 容量估算
| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 注册触发器数 | 15 | 数十（Phase 2 多策略） | 内存字典 O(n) 评估 | ✅ | 分片按 scope 预过滤 |
| 单轮评估耗时 | <1ms（15 条占位） | <10ms | 同步循环 | ✅ | condition 并行求值（演进） |
### 5.3 迁移/废弃方案（条件可选）
无迁移/废弃。
### 5.4 非功能需求与服务水平
| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 正确性 | 仲裁结果确定性 | 同输入同输出 | 单测断言 | 仲裁一致率 | 100% | 0 次 | 测试失败即阻断 |
| 时效性 | 单轮评估耗时 | <10ms | 耗时日志 | 评估耗时 | 99%<10ms | 每日 1 次超限 | >50ms 告警 |
### §5.5 自动化触发机制
| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|---------|
| create_mvp_registry（启动注册） | auto_boot | 系统启动时构造注册表 | ✅已实现 |
| evaluate_all（全量评估） | auto_event | 行情/风控事件驱动 | ✅已实现 |
| resolve_conflicts（冲突消解） | auto_event | 同标的多触发器同时命中时 | ✅已实现 |
| register/unregister | on_demand | 各 spec 域接线时调用 | ✅已实现 |
### §5.7 禁止模式与导入约束
| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 在注册表内实现触发器判定逻辑 | condition 由各 spec 域注入 | 编排层不越界（41 §3.9） |
| 2 | 编码模式 | 同一 condition 重复求值 | id(condition) 缓存去重 | 41 §3.9 去重规则 |
| 3 | 编码模式 | 新建独立 DO 编排器 | TriggerList+硬边界承载 | 41 §2.2.1 裁定 |
| 4 | 导入源 | zephyr.plan_engine.* / zephyr.pf_alloc.* | zephyr.shared.event_bus.* | 编排层只依赖共享基础设施 |

## §6 错误处理 <!-- temporal_type: permanent -->
| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | trigger_id 重复注册 | register 查重 | 抛 ValueError，拒绝注册 | 单条注册项 |
| 2 | priority 越界（非 1-5） | register 校验 | 抛 ValueError，拒绝注册 | 单条注册项 |
| 3 | condition 执行异常 | 求值时抛出 | 向上传播由调用方捕获，不阻断其他触发器注册状态 | 当轮评估 |
| 4 | 依赖循环声明 | — | 本模块只依赖共享事件总线，无 A→B→A 循环 | — |
### 6.1 可观测性规格
| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| trigger_registered_total | Gauge | 手动上报 | — | P3 |
| trigger_fired_total（按 trigger_id） | Counter | 手动上报 | Kill Switch 触发即告警 | P1 |
| trigger_cooldown_skip_total | Counter | 手动上报 | 单日>100 | P3 |
### 6.2 退化矩阵
| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| 扳机清单（整体） | 各模块独立轮询自身触发器 | 统一仲裁/去重 | 41 §3.9 过度工程审查降级路径（MVP 允许） | 注册表恢复 |
| 事件总线 | 事件列表同步返回 | 异步派发 | 调用方直接消费 evaluate_all 返回 | 总线恢复 |

## §7 安全考量 <!-- temporal_type: permanent -->
| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 低优先级触发器抢占风控动作 | 高 | priority=1 无条件覆盖一切（Kill Switch） | resolve_conflicts 单测 |
| 2 | 同一判定重复计算导致状态不一致 | 中 | 同源去重（condition 只算一次） | evaluate_all 去重单测 |
| 3 | 触发器风暴重复派发 | 中 | cooldown_sec 冷却期 | 冷却跳过量测 |

## §8 测试策略 <!-- temporal_type: permanent -->
| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | 2 契约+注册表+清单 | TestTriggerEntry（契约字段/默认值）、TestTriggerRegistry（注册查重/priority 越界/注销/评估/冷却/去重/排序/Kill Switch 覆盖/同级 scope 排序）、TestMVPTriggerList（15 条完整性/字段合法/priority 分布） | 24/24 通过 |
| 2 | 回归验证 | 41 号施工全体 | 3 个测试文件连续 2 轮全过（41 v1.7.0 记录） | 83/83 通过 |

测试文件：`tests/trading/test_trigger_registry.py`（24 用例）。

## §9 依赖关系 <!-- temporal_type: permanent -->
### 9.1 依赖声明
| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| 60 号进程内事件总线 | 必须 | TriggeredEvent 派发通道（代码头声明 zephyr.shared.event_bus） | — | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/60_cross_cutting_cleanup.md` |
| 41_buy_flow 设计备忘 | 必须 | §3.9 注册格式/仲裁规则/MVP 清单 | v1.7.0 | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/41_buy_flow.md` |
### 9.2 依赖图对齐声明
| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §9.1 依赖声明 ↔ depgraph.nodes | 依赖条目在 depgraph 有对应节点 | 已对齐 | `python scripts/governance/extract_depgraph.py --modules MOD-TRIG-001` |
| 2 | §10 产出物路径 ↔ path_mappings | 路径一致 | 已对齐 | 同上 |
### 9.5 概念重叠声明
| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | 突破失败判定 | 判定函数 | MOD-PA-006 detect_breakout_failure | 本模块委托对方（共享 condition，判定一次分发两 action） | 已处置 |
| 2 | 决策路径编排（5 路径冲突消解） | 编排职责 | BM-BUY-03 DO | 对方不建设，本模块承载（41 §2.2.1） | 已处置 |
### 9.6 依赖链风险评级
| # | 依赖链 | 链深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:-----:|---------|---------|---------|
| 1 | MOD-TRIG-001→60 号事件总线 | 2 | L1 | 有（§6.2 同步返回降级） | 已有熔断 |

## §10 产出物存放目录 <!-- temporal_type: permanent -->
| 产出物类型 | 存放完整路径（相对优先） | 职责 | consumer_min | 注册位置 |
|----------|---------------|------|:-----------:|---------|
| 蓝图文件 | `docs/03_modules/_domain_trading/trigger_registry/blueprint.md` | 本文件 | ≥0 | blueprint_registry.yaml |
| 业务代码 | `src/zephyr/trading/trigger_registry.py` | 注册表+仲裁+去重+MVP 15 条清单 | ≥1 | `src/zephyr/trading/` 包 |
| 测试代码 | `tests/trading/test_trigger_registry.py` | 24 用例 | ≥0 | pytest 自动发现 |

## §11 集成目标 <!-- temporal_type: permanent -->
| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| 60 号事件总线 | 事件订阅 | TriggeredEvent→总线派发 | 总线集成测试（未接线，P2） |
| 41/42/40/35/36/37 各 spec 域 | condition 注入 | register(TriggerEntry(condition=真实判定)) | 注入后 evaluate_all 命中测试 |

## §12 需要更新的相关内容 <!-- temporal_type: permanent -->
| # | 需更新的文件 | 完整路径（相对优先） | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | 新增 MOD-TRIG-001 条目 | 回填登记 |
| 2 | 依赖图 | PostgreSQL depgraph | MOD-TRIG-001 节点核验 | 五图对齐 |

## §13 已知风险与缓解 <!-- temporal_type: permanent -->
| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | MVP 清单 condition 为占位（恒 False） | 高 | 中 | 各 spec 域接线时注入真实判定，清单结构已固化 | 负面后果 |
| 2 | 内存注册表重启丢失 | 中 | 低 | 启动时 create_mvp_registry 重建 | 风险 |
| 3 | 单线程同步评估在触发器膨胀后变慢 | 低 | 低 | Phase 2 评估并行化（§5.2 扩展方案） | 风险 |

## §14 施工指引 <!-- temporal_type: construction_temporary（施工已完成，本节保留状态记录） -->
### 14.1 施工策略
| 项目 | 内容 |
|------|------|
| 施工阶段数 | 单 Phase 一次性完成（AI-BUY-001，41 号 v1.7.0 施工批次） |
| 施工模式 | 新建 |
| 核心风险 | 同源去重语义（id(condition) 缓存）与冷却期交互 |
| 目标 generation | 1 |
### 14.2 前置条件
| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | 41_buy_flow v1.4.0+ 扳机清单裁定 | hard | 已定稿（v1.7.0 落码） | ✅ |
| 2 | 60 号事件总线契约 | soft | 派发通道设计已定 | ✅ |
### 14.3 实施步骤
回填蓝图，施工已完成：步骤 1（TriggerEntry/TriggeredEvent 契约）已完成；步骤 2（TriggerRegistry 注册/评估/仲裁）已完成；步骤 3（MVP 15 条清单+工厂）已完成；步骤 4（24 用例）已完成。验证命令：`python -m pytest tests/trading/test_trigger_registry.py -q`。
### 14.4 回滚方案
| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 全部 | 仲裁/去重行为偏离 41 §3.9 | 以 41 §3.9 规则表为基准修复并重跑 24 用例 |
### 14.5 施工完成与生产就绪标准
| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | 代码文件存在且非空 | `src/zephyr/trading/trigger_registry.py` 存在 | 完成 | ✅ |
| 2 | 测试通过 | 24/24 exit 0 | 完成 | ✅ |
| 3 | 代码头十五字段完整 | [BLUEPRINT] MOD-TRIG-001 等字段齐全 | 就绪 | ✅ |
### 14.6 施工状态
| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | 施工者（AI-BUY-001，2026-08-13） |
| verification_status | passed | 审计者（83 用例连续 2 轮全过，41 v1.7.0 记录） |
| code_alignment_verified | yes | 审计者（§4 签名与代码逐一比对一致） |
### 14.7 参考实现规格
| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 优先级仲裁规则 | 协议 | 41 §3.9：priority 升序取最高；同级 scope PORTFOLIO>STRATEGY>POSITION；priority=1 无条件覆盖一切 | resolve_conflicts |
| 2 | 同源去重规则 | 协议 | 41 §3.9：共享 condition 只算一次，按 trigger_id 分发各自 action（BUY_BREAKOUT_FAIL/SELL_BREAKOUT_FAIL 同源） | evaluate_all |
| 3 | MVP 15 条清单 | 配置 | 41 §3.9 表：p1 RISK_KILL_SWITCH/RISK_DRAWDOWN_L4；p2 RISK_DRAWDOWN_L3/RISK_LIQUIDITY_CRISIS/RISK_VAR_BREACH；p3 SELL_BREAKOUT_FAIL/SELL_SUPPORT_BREAK/SELL_CIRCUIT_BREAKER；p4 BUY_BREAKOUT_FAIL/SELL_ATR_STOP/SELL_TRAILING_STOP/SELL_TAKE_PROFIT；p5 BUY_BATCH2_RELEASE/EXE_MAKE_OR_TAKE/EXE_CANCEL_RATE | MVP_TRIGGER_LIST |
### 14.8 施工参考卡
| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/trading/test_trigger_registry.py -q` | 回归验证 | 无 | 24 passed |
| 2 | 常量 | `MVP_TRIGGER_LIST` / `SCOPE_ORDER` | 15 条清单 / scope 排序权重 | list[dict] / dict | 清单变更需 Owner 审批 |
### 14.10 故障与操作手册
| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 运行 | 注册抛 ValueError | trigger_id 重复/priority 越界 | 查注册项冲突 | 换唯一 id 或合法 priority 重注册 | register 成功 |
| 2 | 运行 | 触发器不派发 | 冷却期未满 | 查 _last_fired 时间戳 | 冷却结束或 unregister 后重注册 | 下一轮评估命中 |
### 14.12 并发操作模型
| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 多线程同时 evaluate_all/register | 当前实现单线程语义（进程内事件总线串行消费） | 调用方串行化 | 不适用 |

## §15 容量升级附录 <!-- temporal_type: permanent -->
### §15.1 容量基线
| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 注册触发器数 | 15 条 | len(registry.entries) |
| 单轮评估耗时 | <1ms | 耗时日志 |
### §15.2 缺口清单与升级版本矩阵
| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-TRIG001-01 | 占位 condition 未接真实判定 | 各 spec 域注入 condition | P1 | 41/42 各域施工完成 | v1.0.0 | 未触发 |

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.1.0 | 1 | 基线回填 | 2 契约+注册表+MVP 15 条清单 | ✅ |

## §16 决策记录 <!-- temporal_type: permanent -->
| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-TRIG001-01 | 触发器统一注册表（非各模块独立轮询） | A 统一注册/B 独立轮询 | A | 41 §3.9：冲突无人仲裁+重复检测问题；MVP 允许降级独立轮询 | 2026-08-10 |
| 2 | D-TRIG001-02 | 不建独立 DO 决策编排器 | A 独立 DO/B TriggerList 承载 | B | 41 §2.2.1：职责重叠度>80%，5 路径冲突可由 priority+硬边界消解 | 2026-08-12 |
| 3 | D-TRIG001-03 | 同源去重用 id(condition) 缓存 | A id 缓存/B trigger_id 缓存 | A | 41 §3.9：去重键是共享判定函数而非 trigger_id | 2026-08-13 |
| 4 | D-TRIG001-04 | 数据契约用 frozen dataclass | A dataclass/B Pydantic | A | 41 §3.9 注册格式原文即 @dataclass；与交易域惯例一致 | 2026-08-13 |

## 必备链接 <!-- temporal_type: permanent -->
| # | 文件 | module_id | 完整路径（相对优先） | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 买入流 spec（设计真源） | — | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/41_buy_flow.md` | §3.9 注册格式/仲裁/去重/15 条清单 |
| 2 | 蓝图模板 | GOV-028 | `docs/01_policies_and_standards/templates/blueprint_construction_template.md` | v2.1.0 章节合规 |

## 术语表 <!-- temporal_type: permanent -->
| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| 扳机清单（TriggerList） | 触发器统一注册表+仲裁器 | DO 决策编排器 | TriggerList 只管触发器级编排，DO 管决策路径编排（不建，41 §2.2.1） |
| 同源去重 | 共享 condition 的多个 trigger_id 只判定一次 | 冷却期 | 去重省当轮重复计算，冷却防跨轮重复派发 |
| scope | 触发器作用域 PORTFOLIO/STRATEGY/POSITION | priority | priority 先比，同级才按 scope |
| Kill Switch | priority=1 全停触发器 | 回撤 L3/L4 | Kill Switch 覆盖一切，L3/L4 只停新买/清新仓 |

## 成熟度声明 <!-- temporal_type: permanent -->
| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | 41 号重大修订 | 注册/仲裁/去重已落码并通过测试 |
| 接口契约 | stable | 高 | 破坏性变更需 Owner 审批 | 签名与 41 §3.9 一致 |
| 数据模型 | frozen | 高 | 41 §3.9 注册格式修订 | frozen dataclass 原样落码 |
| MVP 清单内容 | evolving | 中 | 各域 condition 注入完成 | 占位 condition 待接线 |

## 版本演进路线图 <!-- temporal_type: permanent -->
| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 基线回填（代码先行，蓝图后补，遗留项 #29） | — | 已完成 |
| v1.0.0 | 真实 condition 注入+事件总线派发接线 | v0.1.0 | 未施工 |

## 已知问题与盲点登记 <!-- temporal_type: permanent -->
| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | MVP 清单 condition 为占位（恒 False） | 中 | 各 spec 域未施工完成 | 各域施工后注入真实 condition | §5.5 | 未解决 |

## 自检与闭合清单 <!-- temporal_type: permanent -->
| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口执行流程引用 41 号节号 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §8 有对应测试 | 仲裁/去重/冷却→24 用例 | ✅ |
| 4 | 设计 | §0.1 代码文件在 §10 有对应产出物路径 | 单文件核对 | ✅ |
| 5 | 后 | 临时时态内容已清理 | 施工已完成，§14.3 仅留状态 | ✅ |

## 项目中已有类似功能 <!-- temporal_type: permanent -->
| # | 已有模块/文件 | 完整路径（相对优先） | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | 60 号进程内事件总线 | `src/zephyr/shared/event_bus.py` | 事件分发 | 总线是传输通道，不做触发器条件评估与优先级仲裁 |
| 2 | MOD-PA-006 分批建仓引擎 | `src/zephyr/pf_alloc/batched_position_builder.py` | 突破失败判定 | 该模块提供 condition 判定，注册/仲裁归本模块 |

## 涉及的文件范围 <!-- temporal_type: permanent -->
| # | 文件/目录 | 完整路径（相对优先） | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 业务代码 | `src/zephyr/trading/trigger_registry.py` | 读取 | 无变更（回填蓝图不改代码） |
| 2 | 测试代码 | `tests/trading/test_trigger_registry.py` | 读取 | 无变更 |
| 3 | 蓝图文件 | `docs/03_modules/_domain_trading/trigger_registry/blueprint.md` | 新建 | 本文件 |

## ⚠️ 安全删除协议 <!-- temporal_type: permanent -->
本蓝图不涉及任何文件废弃/迁移/删除。如未来涉及：禁止蓝图阶段物理删除；迁移型删除逐条迁移逐条验证；物理删除只在 stable 搬入阶段且人类确认后执行。

## ⚠️ Vibe Coding 蓝图编写铁律确认 <!-- temporal_type: permanent -->
本蓝图编写已逐条确认：全部路径项目根相对+正斜杠；必备链接完整列出；蓝图为最终设计结果；产出物路径与磁盘一致；涉及文件范围明确；全文无模糊指令词（铁律#6）；§0.1/§0.6 AUTOGEN 节保留生成说明未手写漂移；已实现代码不复制实现只保留签名（§4）；术语表齐备。

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 1.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/trading/test_trigger_registry.py` | ✅ 已实现 | |

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
