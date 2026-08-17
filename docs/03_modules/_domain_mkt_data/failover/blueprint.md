---
module_id: MOD-MKT-004
title: "故障切换蓝图 — 多数据源主备切换+自动恢复"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L01_foundation
layer_name: foundation
functional_domain: mkt_data
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-MKT-004 Failover — 故障切换 蓝图

> **module_id**: MOD-MKT-004 | **域**: D_MKT_DATA | **层**: L01 基础平台
> **优先级**: P1 | **成熟度**: production | **对标能力**: 故障切换
> **SSoT**: depgraph MOD-MKT-004 | **设计真源**: 23_d_mkt_data.md

## 1. 定位

故障切换——多数据源主备切换管理。当主数据源(primary vendor)健康检查失败时,
自动切换到备用数据源(secondary), 保障行情数据连续可用。主源恢复后可选自动切回
(auto failback)。

基于 VendorRegistry 的多 vendor 注册, 按 FailoverPolicy 策略选择备用源。

属 A 类基础设施(高可用机制), 纯基础层不涉及策略。
**纯基础设施: 不决定"买什么/何时买", 只负责"主数据源挂了切到备源"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | vendor 优先级列表 | FailoverConfig.priority_list |
| 输入 | 健康检查结果 | vendor.health_check() |
| 输出 | 当前活跃 vendor | get_active() |
| 输出 | 切换事件(FailoverEvent) | on_failover callback |
| 输出 | 切换历史 | history |

## 3. 核心规则

### 3.1 切换策略 (FailoverPolicy)

- **PRIORITY**: 按优先级列表顺序切换(primary → secondary → tertiary)。
  主源不可用切到下一个; 主源恢复后(若 auto_failback)切回主源。
- **ROUND_ROBIN**: 轮询切换到下一个可用 vendor(不区分主备)。

### 3.2 自动切换流程

```
check_and_failover():
  1. active = get_active()
  2. if active is None: 选首个可用 vendor
  3. if active.health_check() is False:
       a. set active status = ERROR
       b. 选下一个可用 vendor (按 policy)
       c. 切换 + 发 FailoverEvent
       d. 若无可用 vendor: 记录 ALL_FAILED 事件, 返回 None
  4. elif auto_failback and active != primary and primary.health_check():
       切回 primary (failback)
```

### 3.3 切换事件 (FailoverEvent)

每次切换记录: from_vendor → to_vendor + reason + timestamp。
history 保留最近 N 条(默认 100), 超限淘汰最旧。

## 4. 关键不变量 (INVARIANTS)

- FailoverEvent/FailoverConfig 为 frozen dataclass (不可变)
- FailoverPolicy 为 Enum
- _active_vendor_id / _history 读写加 Lock, 线程安全
- 切换是原子的: 先确认目标 vendor 可用再切换
- 同一 vendor 不会切换到自身(幂等)
- 切换失败(无可用源)不抛异常, 返回 None 并记录 ALL_FAILED

## 5. 错误契约

- `FailoverError` (ZA-MKT-0004): 配置非法(空优先级列表/vendor 未注册)

## 6. 数据模型

```python
class FailoverPolicy(str, Enum):
    PRIORITY = "priority"
    ROUND_ROBIN = "round_robin"

class FailoverReason(str, Enum):
    HEALTH_CHECK_FAILED = "health_check_failed"
    MANUAL = "manual"
    AUTO_FAILBACK = "auto_failback"
    INITIAL = "initial"
    ALL_FAILED = "all_failed"

@dataclass(frozen=True)
class FailoverConfig:
    priority_list: tuple[str, ...]    # vendor_id 优先级列表
    policy: FailoverPolicy = FailoverPolicy.PRIORITY
    auto_failback: bool = True        # 主源恢复后自动切回
    history_max: int = 100

@dataclass(frozen=True)
class FailoverEvent:
    from_vendor: str | None
    to_vendor: str | None
    reason: FailoverReason
    timestamp: datetime
    detail: str = ""
```

## 7. API

```python
class FailoverManager:
    def __init__(self, registry: VendorRegistry, config: FailoverConfig) -> None: ...
    def get_active(self) -> MarketDataVendor | None: ...
    def check_and_failover(self) -> FailoverEvent | None: ...
    def failover(self, reason: str = "manual") -> FailoverEvent | None: ...
    def failback(self) -> FailoverEvent | None: ...
    def on_failover(self, callback: Callable[[FailoverEvent], None]) -> None: ...
    @property
    def history(self) -> list[FailoverEvent]: ...
    @property
    def active_vendor_id(self) -> str | None: ...
```

## 8. 依赖

- `zephyr.market_data.vendor_registry` (VendorRegistry) — 运行时
- `zephyr.market_data.vendor_base` (MarketDataVendor, VendorStatus)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: D_EX_SOR (运行时行情容错)
- 设计真源: 23_d_mkt_data.md

## 9. 测试

- `tests/market_data/failover/test_failover_manager.py`
- 覆盖: 初始选择、健康检查失败切换、自动 failback、手动 failover、
  无可用源(ALL_FAILED)、轮询策略、事件回调、历史记录、线程安全

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-MKT-004`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-MKT-004` 的 4 个 file 节点 | production | `extract_depgraph.py --modules MOD-MKT-004` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-MKT-004 | MOD-MKT-004 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 4 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/market_data/failover/manager.py` | ✅ 已实现 | |

### 10.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/market_data/failover/__init__.py` | ⚠️ 骨架 | |
| `tests/market_data/failover/test_failover_manager.py` | ✅ 已实现 | |

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
