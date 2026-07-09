---
module_id: MOD-INF-038
activation_phase: requires_100ai
submodule_path: src/zephyr/shared
title: "State Machine Engine 蓝图 — 通用状态机引擎·全项目状态机实例治理"
doc_type: blueprint
status: Draft
version: "0.1.0"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: human_plus_agent
date: "2026-05-16"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: src/zephyr/shared/state_machine.py
last_updated: "2026-05-16"
last_verified: "2026-05-16"
generation: 1
functional_domain: infra
summary: 通用状态机VO基类+全项目11+状态机实例统一治理+命名冲突消除+DDD聚合根持有模式
template_for: blueprint
tags: [state-machine, infrastructure, governance, naming-convention]
priority: P1
runtime_plane: warm
belongs_to: MOD-MASTER_BLUEPRINT
parent_module: ""
rule_form: structural
scope: global
stability: evolving
verifiability: automated
depends_on:
  - target: MOD-INF-016
    at: §10
    why: 共享核心提供基类宿主目录(src/zephyr/shared/)和公共工具
  - target: MOD-DATABASE
    at: §10
    why: 数据库层提供持久化支持
references:
  - path: docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md
    section: §3.3
    why: 任务系统状态机(10状态/19转换)是最大消费者
  - path: docs/01_policies_and_standards/governance/engineering/code-construction-standards.md
    section: §7
    why: 十五字段防幻觉头部规范
ssot_claims:
  - claim: "全项目状态机实例的唯一注册中心"
    scope: global
  - claim: "通用StateMachine[S]泛型基类的唯一真源"
    scope: global
responsibility_domain: 
build_status: generated
design_maturity: prototype
---

## 概述

MOD-INF-038 提供通用状态机引擎，解决全项目 11+ 个独立状态机实例零复用、4 个同名 `InvalidTransitionError`、2 个同名 `SessionState` 的命名冲突问题。采用 DDD Value Object 组合模式：通用 `StateMachine[S]` 基类 + 各领域专用定义 + 聚合根持有实例。

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-038`

| 文件 | 职责 | 状态 |
|------|------|:----:|
| `src/zephyr/shared/state_machine.py` | 通用 StateMachine[S] 泛型基类 | 已实现（零消费者） |
| `src/zephyr/shared/_state-machine-registry.yaml` | 状态机实例注册表 | 待创建 |

### §0.4 SSoT与责任唯一性

| SSoT 声明 | 真源 | 冲突检测 |
|-----------|------|---------|
| 通用状态机基类 | `src/zephyr/shared/state_machine.py` | 蓝图 frontmatter ssot_claims |
| 状态机实例注册 | `src/zephyr/shared/_state-machine-registry.yaml` | REG-SM-001 |

### §0.5 代码目录唯一性

`src/zephyr/shared/` — MOD-INF-016 共享核心目录。状态机引擎作为共享核心的子模块，不独占目录。

## §1 设计背景与目标

### §1.1 背景

全项目存在 11+ 个独立状态机实现，零复用，存在以下问题：

| 问题 | 量化 |
|------|------|
| 同名 `InvalidTransitionError` | 4 处独立定义 |
| 同名 `SessionState` | 2 处独立定义 |
| 状态机实现无统一基类 | 11+ 处各自实现 |
| 状态转换逻辑分散 | 每个模块独立维护 |
| 未来 1500 模块扩展 | 每个都可能需要状态机 |

### §1.2 目标范围

| 目标 | 优先级 |
|------|:------:|
| 通用 `StateMachine[S]` 泛型基类 | P0 |
| 统一 `InvalidTransitionError` 命名空间 | P0 |
| 状态机实例注册表 REG-SM-001 | P0 |
| 11+ 现有状态机迁移到通用基类 | P1 |
| 状态转换副作用绑定框架 | P1 |
| 状态机命名冲突自动检测 | P2 |

### §1.5 利益相关者

| 角色 | 关注点 |
|------|--------|
| MOD-TASK_SYSTEM 任务系统 | 10 状态 / 19 转换 / 7 绑定字段 |
| MOD-INF-023 漂移检测器 | 10 状态 / 14 转换 |
| MOD-INF-021 回滚系统 | 4 状态 + 6 状态验证器 |
| MOD-INF-019 Agent规格 | 4 状态 / 5 转换 Skill 生命周期 |
| MOD-INF-025 A2A协议 | 9 状态 / 8 转换 |
| MOD-INF-018 Agent RBAC | 5 状态 / 9 转换 |
| MOD-RESOURCE_OPTIMIZATION_ENGINE 资源优化引擎 | 4 状态 / 6 转换压力状态机 |
| MOD-INF-015 系统遥测 | CircuitBreaker 3 状态 / 4 转换 |

### §1.6 差距

| 差距 | 当前状态 | 目标状态 |
|------|---------|---------|
| 状态机基类 | 无 | `StateMachine[S]` 泛型基类 |
| 命名冲突 | 4×InvalidTransitionError, 2×SessionState | 统一命名空间 |
| 实例注册 | 无 | REG-SM-001 |
| 副作用框架 | 各自实现 | 统一 on_enter/on_exit/on_transition |

## §2 模块边界

### §2.1 职责边界

| 本模块负责 | 本模块不负责 |
|-----------|------------|
| 通用状态机泛型基类 | 各领域状态/转换的业务语义 |
| 状态转换守卫框架 | 具体守卫逻辑实现 |
| 副作用绑定接口 | 具体副作用实现 |
| 状态机实例注册 | 业务流程编排 |
| 命名冲突检测 | 已有代码的自动迁移 |

## §3 架构设计

### §3.1 组件架构

```
StateMachine[S] (泛型基类, Generic[S])
├── StateDefinition[S] — 状态定义(名称/是否终态/元数据)
├── Transition[S] — 转换定义(源/目标/守卫/副作用)
├── TransitionGuard[S] — 转换守卫协议
├── SideEffect[S] — 副作用协议(on_enter/on_exit/on_transition)
├── StateMachineConfig[S] — 配置(状态集/转换集/初始状态)
└── StateMachineRegistry — 实例注册(REG-SM-001)
```

DDD 持有模式：

```
聚合根 (如 TaskRepository)
  └── 持有 StateMachine[TaskStatus] 实例
       └── 状态转换由聚合根委托
           └── 守卫/副作用由聚合根控制
```

### §3.3 状态生命周期

状态机引擎自身生命周期：

| 阶段 | 描述 |
|------|------|
| 定义 | `StateMachineConfig[S]` 声明状态集和转换集 |
| 注册 | `StateMachineRegistry.register(config)` → REG-SM-001 |
| 实例化 | 聚合根创建 `StateMachine[S]` 实例 |
| 运行 | `instance.transition(target_state)` 触发守卫→转换→副作用 |
| 销毁 | 聚合根释放实例引用 |

## §4 接口契约

### §4.1 公共 API

```python
class StateMachine(Generic[S]):
    def __init__(self, config: StateMachineConfig[S], initial: S): ...
    def can_transition(self, target: S) -> bool: ...
    def transition(self, target: S, context: dict | None = None) -> S: ...
    @property
    def current_state(self) -> S: ...
    @property
    def available_transitions(self) -> list[S]: ...

class StateMachineConfig(Generic[S]):
    def __init__(self, fsm_id: str, states: list[StateDefinition[S]],
                 transitions: list[Transition[S]], initial: S): ...

class StateMachineRegistry:
    def register(self, config: StateMachineConfig[S]) -> str: ...
    def get(self, fsm_id: str) -> StateMachineConfig[S]: ...
    def list_all(self) -> list[str]: ...
    def detect_conflicts(self) -> list[ConflictReport]: ...
```

### §4.2 数据模型

```python
@dataclass(frozen=True)
class StateDefinition(Generic[S]):
    state: S
    is_terminal: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Transition(Generic[S]):
    source: S
    target: S
    guard: TransitionGuard[S] | None = None
    side_effects: list[SideEffect[S]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
```

### §4.6 契约版本

| 版本 | 变更 |
|:----:|------|
| v1 | 初始 API：StateMachine[S] + Config + Registry |

## §5 约束条件

### §5.1 技术约束

| 约束 | 原因 |
|------|------|
| Python 3.11+ Generic 语法 | 类型安全 |
| 状态枚举 MUST 为 `StrEnum` 或 `Enum` | 可序列化+可比较 |
| 线程安全 | 多 Agent 并发转换 |
| 零外部依赖 | 共享核心不允许引入新依赖 |

### §5.7 禁止模式与导入约束

| 禁止 | 原因 |
|------|------|
| 在 StateMachine 基类中硬编码任何领域状态 | 通用基类必须领域无关 |
| 绕过 Registry 直接创建未注册的状态机 | RULE-TWO 反孤儿 |
| 在 guard/side_effect 中执行 I/O 操作 | 状态转换必须同步完成 |

## §6 错误处理

### §6.1 可观测性

| 事件 | 日志级别 |
|------|:-------:|
| 状态转换成功 | INFO |
| 转换被守卫拒绝 | WARNING |
| 非法转换尝试 | ERROR |
| 命名冲突检测 | ERROR |

### §6.2 退化矩阵

| 故障 | 退化策略 |
|------|---------|
| Registry 不可用 | 降级为本地实例，启动时告警 |
| 守卫执行异常 | 阻止转换，保持当前状态 |
| 副作用执行异常 | 转换完成但记录异常，不回滚 |

## §9 测试策略

| 测试类型 | 覆盖 |
|---------|------|
| 单元测试 | StateMachine[S] 转换/守卫/副作用 |
| 集成测试 | Registry 注册/查询/冲突检测 |
| 迁移测试 | 各领域状态机迁移后行为等价 |
| 并发测试 | 多线程同时转换 |

## §10 依赖关系

### §10 依赖

| 依赖 | 方向 | 原因 |
|------|------|------|
| MOD-INF-016 共享核心 | 038→016 | 基类宿主目录+公共工具 |
| MOD-DATABASE 数据库 | 016→012 | 持久化(间接) |

依赖链：`038→016→012`，深度=1，风险=✅

### §10.5 概念重叠声明

| 概念 | 本模块 | MOD-TASK_SYSTEM | 关系 |
|------|--------|-------------|------|
| 任务状态机 | 通用基类 | 领域消费者 | 006 使用 038 基类 |
| 状态转换副作用 | 框架接口 | 业务实现 | 006 实现具体副作用 |

### §10.6 依赖链风险评级

深度=1，低风险。唯一风险：MOD-INF-016 变更可能影响基类兼容性。

## §11 产出物

| 产出物 | 路径 | 状态 |
|--------|------|:----:|
| 通用状态机基类 | `src/zephyr/shared/state_machine.py` | 待创建 |
| 状态机注册表 | `src/zephyr/shared/_state-machine-registry.yaml` | 待创建 |
| 单元测试 | `tests/test_state_machine.py` | 待创建 |

## §12 集成目标

| 消费者 | 集成方式 | 优先级 |
|--------|---------|:------:|
| MOD-TASK_SYSTEM 任务系统 | `StateMachine[TaskStatus]` 替换内建状态机 | P1 |
| MOD-INF-023 漂移检测器 | `StateMachine[DriftState]` | P1 |
| MOD-INF-021 回滚系统 | `StateMachine[RollbackStepState]` + `StateMachine[OrderState]` | P1 |
| MOD-INF-019 Agent规格 | `StateMachine[SkillState]` | P2 |
| MOD-INF-025 A2A协议 | `StateMachine[A2ATaskState]` | P2 |
| MOD-INF-018 Agent RBAC | `StateMachine[SessionState]` | P2 |
| MOD-RESOURCE_OPTIMIZATION_ENGINE 资源优化引擎 | `StateMachine[PressureState]` | P2 |
| MOD-INF-015 系统遥测 | `StateMachine[CircuitState]` | P2 |

## §13 需要更新

修改本蓝图时 MUST 同步更新：

| 文件 | 同步内容 |
|------|---------|
| `src/zephyr/shared/_state-machine-registry.yaml` | 实例注册 |
| `docs/registry_of_registries.yaml` | REG-SM-001 entry_count |
| `docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md` | §5/§10 |
| `docs/03_modules/blueprint_registry.yaml` | 版本/状态 |

## §14 风险

| 风险 | 概率 | 影响 | 缓解 |
|------|:----:|:----:|------|
| 迁移破坏现有行为 | 中 | 高 | 迁移测试：行为等价性验证 |
| 泛型基类过度设计 | 低 | 中 | YAGNI：只实现已验证的需求 |
| 命名冲突迁移遗漏 | 中 | 中 | REG-SM-001 自动冲突检测 |

## §16 施工指引

### §16.8 施工参考卡

```
STEP 1: 创建 src/zephyr/shared/state_machine.py — StateMachine[S] 泛型基类
STEP 2: 创建 src/zephyr/shared/_state-machine-registry.yaml — 注册表种子
STEP 3: 创建 tests/test_state_machine.py — 单元测试
STEP 4: 迁移 MOD-TASK_SYSTEM 任务系统状态机（最大消费者，验证基类可用性）
STEP 5: 迁移 MOD-INF-023 漂移检测器状态机
STEP 6: 迁移 MOD-INF-021 回滚系统状态机
STEP 7: 迁移剩余 8 个状态机实例
STEP 8: 删除各模块内建的重复 InvalidTransitionError/SessionState
STEP 9: 更新 REG-SM-001 entry_count
```

## §18 决策记录

| 日期 | 决策 | 原因 |
|------|------|------|
| 2026-05-16 | 状态机独立为 MOD-INF-038 蓝图 | 未来 1500 模块都需要状态机，不应绑定在任务系统蓝图内 |
| 2026-05-16 | 采用 DDD VO 组合模式 | 聚合根持有状态机实例，状态机不独立为聚合 |
| 2026-05-16 | 基类放在 `src/zephyr/shared/` | 共享核心目录，零外部依赖 |

## 术语表

| 术语 | 定义 |
|------|------|
| StateMachine[S] | 以状态枚举类型 S 参数化的泛型状态机 |
| 聚合根 | DDD 中控制状态转换的实体 |
| VO 组合模式 | 状态机作为 Value Object 被聚合根持有 |
| REG-SM-001 | 状态机实例注册表 ID |

## 已知问题

| ID | 描述 | 状态 |
|----|------|------|
| SM-001 | 11+ 状态机迁移需逐模块验证行为等价性 | 待施工 |

## 自检与闭合清单

- [x] 依赖图已更新（dependency_path_panorama.md §5/§10）
- [x] 模块注册表已更新（blueprint_registry.yaml）
- [x] 蓝图注册表已更新（blueprint_registry.yaml）
- [x] 中央注册表已更新（registry_of_registries.yaml REG-SM-001）
- [x] 通用基类代码已创建
- [ ] 至少一个消费者已迁移（task_repo.py 不存在，零消费者）
- [x] REG-SM-001 已注册 task-lifecycle（entry_count: 1）
- [ ] 单元测试已创建（tests/test_state_machine.py）
- [ ] 剩余 10 个状态机实例迁移

## 成熟度

| 维度 | 等级 | 说明 |
|------|:----:|------|
| API 稳定性 | T0 | 初始设计 |
| 测试覆盖 | T0 | 待创建 |
| 消费者数量 | T0 | 0（待迁移） |
| 文档完整度 | T1 | 蓝图完成 |

## 版本演进路线图

| 版本 | 里程碑 | 关键交付 |
|:----:|--------|---------|
| v0.1.0 | 基类+注册表 | StateMachine[S] + REG-SM-001 |
| v0.2.0 | 首批迁移 | MOD-TASK_SYSTEM/023/021 迁移完成 |
| v1.0.0 | 全量迁移 | 11+ 状态机迁移完成 + 命名冲突消除 |
