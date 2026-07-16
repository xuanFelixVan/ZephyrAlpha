---
module_id: MOD-RESOURCE_OPTIMIZATION_ENGINE
title: "资源优化引擎蓝图"
doc_type: blueprint
status: Active
version: "5.4.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-08"
ttl: permanent
construction_progress: design_only
actual_disk_path: "src/zephyr/trading/"
belongs_to: "MOD-MASTER_BLUEPRINT"
submodule_path: src/zephyr/runtime/
summary: "MAPE-K 驱动的资源优化引擎：进程池化、I/O缓存、智能调度、GPU监控、IDE幽灵窗口检测、自愈闭环"
tags: [resource-optimization, mape-k, process-pool, io-cache, lazy-loading, self-healing, backpressure, circuit-breaker, gpu-monitoring, ide-health]
priority: P1
runtime_plane: warm
codification_level: L2
last_updated: "2026-05-22"
last_verified: "2026-05-22"
codification_at: "2026-05-15"
generation: 2
functional_domain: operations
parent_module: ""
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - {target: "MOD-INF-035", at: "全篇", why: "AutoRuntime Core——大脑调度与资源优化联动"}
  - {target: "MOD-INF-016", at: "全篇", why: "Shared Core——daemon_registry/event_bus/lifecycle/contract_bus基础组件"}
references:
  - {id: "MOD-INF-015", at: "§10", why: "System Telemetry——SLI指标上报与健康检查"}
  - {id: "MOD-INF-009", at: "全篇", why: "Pipeline——pipeline_lock与资源调度协调"}
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Resource Optimization Engine 蓝图 — MAPE-K 驱动的进程池化/I/O零拷贝/缓存复用/自愈闭环

> module_id: MOD-RESOURCE_OPTIMIZATION_ENGINE | version: 5.3.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/trading/ | generation: 2 | construction_progress: partially_implemented

## 概述

本蓝图描述 Resource Optimization Engine——MAPE-K 驱动的资源优化引擎，通过 Monitor→Analyze→Plan→Execute 闭环实现进程池化、I/O 零拷贝、智能调度、内存水位管理、缓存复用、流式处理和自愈。DefensiveStrategyEngine 应急保护 + OffensiveStrategyEngine 主动提效双引擎协同。当前管理 51 模块，目标 1,500 模块 / 100 AI 并发。上游依赖 Shared Core（MOD-INF-016）和 AutoRuntime Core（MOD-INF-035），下游被 Pipeline（MOD-INF-009）等消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-RESOURCE_OPTIMIZATION_ENGINE`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:---:|-------------------|
| 1 | resource_optimization_engine.py | §4/§12 | MAPE-K 主引擎 | 已实现 | — |
| 2 | resource_optimization_models.py | §4.2 | 数据模型 | 已实现 | — |
| 3 | daemon_registry.py | §4 | 守护线程注册表 | 已实现 | — |
| 4 | io_cache.py | §4 | I/O 缓存层 | 已实现 | — |
| 5 | streaming_reader.py | §4 | 流式读取 | 已实现 | — |
| 6 | process_pool.py | §4 | 进程池管理 | 已实现 | — |
| 7 | lazy_loader.py | §4 | 懒加载器 | 已实现 | — |
| 8 | resource_optimization.yaml | §18 | 配置文件 | 已实现 | — |
| 9 | gpu_monitor.py | §1.2-G9 | GPU 状态采集（nvidia-smi） | 已实现 | — |
| 10 | ide_health_daemon.py | §1.2-G10 | IDE 幽灵窗口守护 + 任务残留进程清理 | 已实现 | — |
| 11 | ide_health_service.py | §new-IDE | 常驻守护进程入口（IdeHealthDaemon + ResourceOptimizationEngine + nanny自恢复） | 已实现 | — |
| 12 | zombie_scanner.py | §new-IDE | 僵尸 Python 进程四级分类检测器（SUSPICIOUS/ABNORMAL/DANGEROUS auto-kill + 模式计数） | 已实现 | — |
| 13 | speed_baseline_checker.py | §new-IDE | 脚本运行速度基线检测器（读取 script_manifest timeout 基线，对比活跃进程运行时，四级分类 SLOW/VERY_SLOW/CRITICAL_SLOW） | 已实现 | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| actual_disk_path 与 §11 产出物路径一致 | 路径核对 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v5.1.0 (基线) | resource_optimization_engine, models, daemon_registry, io_cache, streaming_reader, process_pool, lazy_loader, config | 自愈闭环、AI可发现性注册 | Phase 5-6 待施工 |
| v5.2.0 (模板v3.5重构) | 同 v5.1.0 | — | 结构重组，无功能变更 |
| v5.3.0 (GPU+IDE健康) | +gpu_monitor, +ide_health_daemon | — | OPS-1/OPS-2 实现完成 |

---

## §1 设计背景与目标

### 1.1 背景

| 问题 | 现状 | 根因 |
|------|------|------|
| 进程爆炸 | 10对话=180进程, 19.15GB内存 | 每对话独立启动MCP服务器 |
| I/O阻塞 | AuditWriter 读全量→写全量 | 无缓存层+无流式读取 |
| 守护线程失控 | ResourceGuard每5s os.walk() | 无统一调度+无退出机制 |
| 系统卡死 | Trae -2错误 | 无全局资源优化系统 |

### 1.2 目标

| # | 目标 | 衡量标准 |
|---|------|---------|
| G1 | **进程资源池化**——MCP 服务器进程跨对话共享，而非每对话独立启动 | 10 对话时 Python 进程数从 180 降至 ≤20 |
| G2 | **I/O 零拷贝优化**——消除"读全量→写全量"模式 | AuditWriter 单次写入延迟从 O(n) 降至 O(1) |
| G3 | **智能调度**——后台守护线程按需启动、按优先级调度 | FLE-Scheduler 空闲时段 CPU 占用从 30% 降至 <5% |
| G4 | **内存水位管理**——主动监控+提前优化，而非等内存满了再降级 | 内存使用率超过 75% 时自动触发优化，95% 前完成 |
| G5 | **缓存复用**——YAML/JSONL 解析结果缓存，避免重复 I/O | 同一 YAML 文件 30 秒内重复读取命中缓存率 ≥90% |
| G6 | **流式处理**——大文件读取改为流式/尾部读取 | _load_events_raw(limit=100) 内存占用从 O(n) 降至 O(limit) |
| G7 | **自愈闭环**——资源异常自动检测→诊断→优化→验证 | 资源异常从检测到恢复 ≤60 秒，无需人工干预 |
| G8 | **AI 可发现**——任何新 AI session 都能自动定位并使用资源优化能力 | 通过蓝图路由+技能注册+MCP工具三重发现，0 次人工指引 |
| G9 | **GPU 监控**——nvidia-smi 采集 GPU 使用率/显存，纳入 MAPE-K 压力分级 | GPU >98% → EMERGENCY，>95% → CRITICAL，>85% → WARNING |
| G10 | **IDE 幽灵窗口检测**——自动检测 MainWindowHandle=0 的 TRAE 窗口并 force kill | 幽灵窗口出现后 ≤30s 自动清理，零人工干预 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 网络带宽优化 | 桌面环境非瓶颈 |
| 2 | 容器化/虚拟化资源隔离 | 超出桌面级范围 |
| 3 | 业务算法优化 | 不改变算法正确性，只优化资源使用方式 |
| 4 | 安全策略执行 | 不做权限控制，归属 MOD-INF-018 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 单机桌面环境（i7-12700KF / 64GB / RTX 3090） | 资源上限固定，无水平扩展能力，所有优化必须在单机约束内完成 |
| Windows NTFS 文件锁 + Defender 实时扫描 | 文件 I/O 操作需考虑锁竞争和扫描延迟，原子写入必须用 temp+replace |
| Python GIL 限制 | CPU 密集型操作无法真正并行，需用 subprocess 绕过 GIL |
| 100 AI 并发 Session 峰值 | 资源优化引擎自身 CPU 占用必须 <1%，不能成为瓶颈 |
| SQLite 单写者约束 | 优化历史写入需批量合并，避免写锁争用 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 描述 |
|---|------|------|
| 1 | 资源快照采集 | 定期采集 CPU/内存/磁盘/进程/线程指标 |
| 2 | 压力分级 | 将资源状态分为 NORMAL/WARNING/CRITICAL/EMERGENCY 四级 |
| 3 | **防御策略引擎** | 应急保护：EMERGENCY/CRITICAL 时停止非必要服务、释放内存、保护核心功能 |
| 4 | **优化策略引擎** | 主动提效：NORMAL/WARNING 时进程池复用、缓存预热、批量 I/O、自适应调度 |
| 5 | 优化策略执行 | 根据压力等级执行对应的优化策略 |
| 6 | 守护线程注册表 | 统一注册、启停、优先级管理所有后台守护线程 |
| 7 | I/O 优化 | 缓存层 + 流式读取 + append-only 写入 + 批量合并 |
| 8 | 进程池管理 | MCP 服务器进程跨对话共享，限制最大进程数 |
| 9 | 优化历史 | 记录优化动作和效果，供 MAPE-K Knowledge 使用 |
| 10 | 压力状态机 | 管理压力等级转换，含滞后机制防抖动 |
| 11 | 优雅降级矩阵 | 定义每个压力等级下各子系统的行为变化 |
| 12 | 断路器 | 优化动作失败时自动熔断，防止级联故障 |
| 13 | 背压机制 | 优化速度跟不上资源恶化速度时，向上游施加背压 |
| 14 | 自愈闭环 | 资源异常自动检测→诊断→优化→验证的完整闭环 |
| 15 | 配置管理 | 资源阈值、策略参数、调度频率等可配置化 |

#### 架构决策：一个系统，两个策略引擎

防御和优化合为一个系统，双引擎共享传感器+知识库，独立触发条件、共享执行层。

#### 架构决策：1,500 模块容量三大转变

×32 规模扩展（47→1,500 模块），三个架构级转变：

**转变 1：每模块独立进程 → 进程池共享**

```
现在:  1,500 模块 × 10 对话 × 10 MCP = 150,000 进程  → 不可行
优化后: 10 对话 × 3 共享 MCP 网关 = 30 进程          → 可行
```

按服务器类型共享，请求级隔离（request_id+session_id）。风险：状态泄漏 → 请求前重置上下文+请求级沙箱。

**转变 2：全量加载 → 按需加载（importlib）**

```
现在:  import 1,500 个模块 → 启动时间 5 分钟，内存 200 GB  → 不可行
优化后: 懒加载 + importlib → 只加载当前对话需要的 10 个模块 → 可行
```

启动只加载核心~20模块，其余 importlib 动态导入。风险：首次调用延迟 → 预热缓存+import预判。

**转变 3：各自轮询 → 统一调度**

```
现在:  300 个守护线程各自 while True + sleep  → CPU 碎片化、调度不可控
优化后: 1 个调度器统一管理 300 个任务         → 批量执行、智能排程
```

DaemonRegistry 统一注册调度，禁止自创 while True。风险：单点故障 → 调度器无状态+崩溃自动重启。

### 2.2 不包含的职责

| # | 不包含 | 原因 | 归属 |
|---|--------|------|------|
| 1 | 业务逻辑优化 | 不改变算法正确性 | 各业务模块 |
| 2 | 安全策略执行 | 不做权限控制 | MOD-INF-018 (agent-rbac) |
| 3 | 日志审计记录 | 不做审计记录存储 | MOD-INF-015 (telemetry) |
| 4 | 错误恢复/重试 | 不做业务级重试 | MOD-INF-009 (pipeline) |
| 5 | 容量规划 | 不做事前容量规划 | MOD-INF-001 (capacity_assurance) |
| 6 | Token/Cost 预算 | 不做 LLM 调用预算 | MOD-INF-024 (budget-enforcer) |
| 7 | 漂移检测 | 不做配置漂移检测 | MOD-INF-023 (drift-detector) |
| 8 | 回滚执行 | 不做代码级回滚 | MOD-INF-021 (rollback-system) |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | ResourceOptimizationEngine | MAPE-K 主循环：监控→分析→计划→执行 | DaemonRegistry, EventBus | 同步调用 |
| 2 | DefensiveStrategyEngine | 应急保护：EMERGENCY/CRITICAL 时停止非必要服务 | ResourceSnapshot | 事件驱动 |
| 3 | OffensiveStrategyEngine | 主动提效：NORMAL/WARNING 时缓存预热/批量I/O | ResourceSnapshot, FileCache | 同步调用 |
| 4 | DaemonRegistry | 守护线程注册/启停/优先级管理 | — | 同步调用 |
| 5 | FileCache | YAML/JSON 文件解析缓存（mtime 校验） | — | 同步调用 |
| 6 | MCPProcessPool | MCP 服务器进程跨对话共享 | — | 同步调用 |
| 7 | LazyModuleRegistry | 按需 importlib 动态导入 | — | 同步调用 |
| 8 | PressureStateMachine | 压力等级转换（含滞后/冷却） | ResourceSnapshot | 状态机 |
| 9 | CircuitBreaker | 优化动作失败熔断 | — | 状态机 |
| 10 | SelfHealingLoop | 检测→诊断→优化→验证闭环 | EventBus, AuditTrail | 事件驱动 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | psutil / Windows API | 采集 CPU/内存/磁盘/进程指标 | ResourceSnapshot | Pydantic Model |
| 2 | ResourceSnapshot | 压力分级（NORMAL/WARNING/CRITICAL/EMERGENCY） | PressureStateMachine | Enum |
| 3 | PressureStateMachine | 触发防御/优化策略 | StrategyEngine | OptimizationStrategy |
| 4 | StrategyEngine | 执行优化动作 | AuditTrail / EventBus | OptimizationResult |
| 5 | Config YAML | 热加载配置变更 | Engine 参数 | dict |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| NORMAL | 内存 >75% / CPU >70% | WARNING | 持续 30s |
| WARNING | 内存 >85% / CPU >80% | CRITICAL | 持续 15s |
| CRITICAL | 内存 >95% | EMERGENCY | 立即 |
| EMERGENCY | 内存 <85% 持续 60s | CRITICAL | 冷却期 60s |
| CRITICAL | 内存 <75% 持续 60s | WARNING | 冷却期 60s |
| WARNING | 内存 <65% 持续 60s | NORMAL | 冷却期 60s |

---

## §4 接口契约

### 4.1 公共 API

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Callable
from datetime import datetime

class ResourceOptimizationEngine:
    """资源优化引擎主类——MAPE-K 循环驱动的资源监控、分析、优化与自愈"""

    _instance: Optional["ResourceOptimizationEngine"] = None

    def __new__(cls) -> "ResourceOptimizationEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def snapshot(self) -> "ResourceSnapshot":
        """
        采集当前资源快照

        输入：无
        输出：ResourceSnapshot 包含 CPU/内存/磁盘/进程/线程指标
        核心逻辑：psutil 采集 → 缺失字段降级 Windows API → 填充默认值 0
        """

    def optimize(self, strategy: "OptimizationStrategy", context: Optional[dict] = None) -> "OptimizationResult":
        """
        执行指定优化策略

        输入：strategy 枚举值 + context 可选上下文
        输出：OptimizationResult 包含执行结果和资源变化
        核心逻辑：断路器检查 → 策略执行 → 结果记录 → 知识层更新
        """

    def register_daemon(self, name: str, start_fn: Callable, stop_fn: Callable, priority: int = 5) -> None:
        """
        注册守护线程到统一调度器

        输入：name 全局唯一标识 + start_fn/stop_fn + priority 0-10（0最高）
        输出：无
        核心逻辑：名称唯一性校验 → DaemonRegistry 注册 → 按优先级排序
        """

    def start_daemon(self, name: str) -> bool:
        """启动指定守护线程。输出：是否成功启动"""

    def stop_daemon(self, name: str) -> bool:
        """停止指定守护线程（幂等）。输出：是否成功停止"""

    def get_cache_stats(self) -> "CacheStats":
        """获取 I/O 缓存统计。输出：CacheStats"""

    def get_process_pool_stats(self) -> "ProcessPoolStats":
        """获取进程池统计。输出：ProcessPoolStats"""

    def get_optimization_history(self, limit: int = 100) -> list["OptimizationRecord"]:
        """获取优化历史记录。输出：最近的 limit 条记录"""

    def on_pressure(self, callback: Callable[["PressureLevel", "ResourceSnapshot"], None]) -> None:
        """注册压力变化回调。回调异常不中断主循环"""

    def health_check(self) -> "HealthCheckResult":
        """健康检查端点。输出：引擎运行状态 + 各子系统状态"""

    def get_pressure_state(self) -> "PressureState":
        """获取当前压力状态机状态。输出：PressureState 含当前级别 + 转换历史"""

    def force_pressure(self, level: "PressureLevel", reason: str) -> None:
        """强制设置压力级别（仅用于测试和紧急人工干预）。需 Owner 审批"""

    def get_degradation_matrix(self) -> "DegradationMatrix":
        """获取当前降级矩阵。输出：各子系统在各压力级别下的行为"""

    def get_circuit_breaker_status(self) -> dict[str, "CircuitBreakerState"]:
        """获取所有断路器状态。输出：策略名 → 断路器状态映射"""

    def get_file_cache(self) -> "FileCache":
        """获取文件缓存实例。输出：FileCache 单例"""

    def get_process_pool(self) -> "MCPProcessPool":
        """获取进程池实例。输出：MCPProcessPool 单例"""

    def get_lazy_loader(self) -> "LazyModuleRegistry":
        """获取懒加载注册表实例。输出：LazyModuleRegistry 单例"""
```

### 4.2 数据模型

```python
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional
from datetime import datetime

class PressureLevel(str, Enum):
    """压力等级枚举——四级分级体系"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class OptimizationStrategy(str, Enum):
    """优化策略枚举——7 种策略"""
    CACHE_WARM = "cache_warm"
    IO_BATCH = "io_batch"
    PROCESS_POOL = "process_pool"
    LAZY_INIT = "lazy_init"
    STREAMING_READ = "streaming_read"
    SCHEDULE_ADAPT = "schedule_adapt"
    MEMORY_COMPACT = "memory_compact"

class DefensiveStrategy(str, Enum):
    """防御策略枚举——4 种策略"""
    STOP_LOW_PRIORITY = "stop_low_priority"
    RELEASE_MEMORY = "release_memory"
    REDUCE_FREQUENCY = "reduce_frequency"
    EMERGENCY_GC = "emergency_gc"

class CircuitBreakerState(str, Enum):
    """断路器状态"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class ResourceSnapshot(BaseModel):
    """资源快照——某一时刻的系统资源状态"""
    timestamp: float = Field(..., description="采集时间戳（Unix epoch）")
    cpu_percent: float = Field(default=0.0, description="CPU 使用率（0-100）")
    memory_percent: float = Field(default=0.0, description="内存使用率（0-100）")
    memory_used_gb: float = Field(default=0.0, description="已用内存（GB）")
    memory_total_gb: float = Field(default=0.0, description="总内存（GB）")
    process_count: int = Field(default=0, description="进程数")
    thread_count: int = Field(default=0, description="线程数")
    disk_io_read_mb_s: float = Field(default=0.0, description="磁盘读取速率（MB/s）")
    disk_io_write_mb_s: float = Field(default=0.0, description="磁盘写入速率（MB/s）")
    disk_free_gb: float = Field(default=0.0, description="磁盘剩余空间（GB）")
    pressure: PressureLevel = Field(default=PressureLevel.NORMAL, description="压力等级")

    @field_validator("cpu_percent", "memory_percent")
    @classmethod
    def validate_percent(cls, v: float) -> float:
        return max(0.0, min(100.0, v))

class OptimizationRecord(BaseModel):
    """优化记录——一次优化动作的完整记录"""
    timestamp: float = Field(..., description="执行时间戳")
    trigger: PressureLevel = Field(..., description="触发压力等级")
    strategy: OptimizationStrategy = Field(..., description="执行的策略")
    actions_taken: list[str] = Field(default_factory=list, description="执行的动作列表")
    memory_before_gb: float = Field(..., description="优化前内存（GB）")
    memory_after_gb: float = Field(..., description="优化后内存（GB）")
    process_count_before: int = Field(..., description="优化前进程数")
    process_count_after: int = Field(..., description="优化后进程数")
    quality_preserved: bool = Field(default=True, description="业务质量是否保持")
    duration_ms: int = Field(default=0, description="执行耗时（毫秒）")
    success: bool = Field(default=True, description="是否成功")

class OptimizationResult(BaseModel):
    """优化执行结果"""
    strategy: OptimizationStrategy = Field(..., description="执行的策略")
    success: bool = Field(..., description="是否成功")
    actions_taken: list[str] = Field(default_factory=list, description="执行的动作")
    snapshot_before: ResourceSnapshot = Field(..., description="优化前快照")
    snapshot_after: Optional[ResourceSnapshot] = Field(default=None, description="优化后快照")
    quality_preserved: bool = Field(default=True, description="业务质量是否保持")
    error_message: Optional[str] = Field(default=None, description="错误信息")

class CacheStats(BaseModel):
    """缓存统计"""
    total_entries: int = Field(default=0, description="缓存条目总数")
    hit_count: int = Field(default=0, description="命中次数")
    miss_count: int = Field(default=0, description="未命中次数")
    hit_rate: float = Field(default=0.0, description="命中率（0-1）")
    memory_usage_mb: float = Field(default=0.0, description="缓存内存占用（MB）")
    evictions: int = Field(default=0, description="淘汰次数")

class ProcessPoolStats(BaseModel):
    """进程池统计"""
    active_processes: int = Field(default=0, description="活跃进程数")
    max_processes: int = Field(default=30, description="最大进程数")
    reuse_count: int = Field(default=0, description="复用次数")
    zombie_count: int = Field(default=0, description="僵尸进程数")

class PressureState(BaseModel):
    """压力状态机状态"""
    current_level: PressureLevel = Field(default=PressureLevel.NORMAL, description="当前压力级别")
    previous_level: Optional[PressureLevel] = Field(default=None, description="前一个压力级别")
    entered_at: datetime = Field(default_factory=datetime.now, description="进入当前级别的时间")
    transition_count: int = Field(default=0, description="状态转换次数")
    cooldown_remaining_s: float = Field(default=0.0, description="冷却期剩余秒数")

class HealthCheckResult(BaseModel):
    """健康检查结果"""
    engine_running: bool = Field(..., description="引擎是否运行")
    monitor_loop_alive: bool = Field(..., description="监控循环是否存活")
    last_snapshot_age_s: float = Field(..., description="上次快照距今秒数")
    pressure_level: PressureLevel = Field(..., description="当前压力级别")
    daemon_count: int = Field(default=0, description="注册守护线程数")
    cache_healthy: bool = Field(default=True, description="缓存是否健康")
    process_pool_healthy: bool = Field(default=True, description="进程池是否健康")

class DegradationMatrix(BaseModel):
    """降级矩阵——每个压力级别下各子系统的行为"""
    normal: dict[str, str] = Field(default_factory=dict, description="NORMAL 级别各子系统行为")
    warning: dict[str, str] = Field(default_factory=dict, description="WARNING 级别各子系统行为")
    critical: dict[str, str] = Field(default_factory=dict, description="CRITICAL 级别各子系统行为")
    emergency: dict[str, str] = Field(default_factory=dict, description="EMERGENCY 级别各子系统行为")
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `snapshot()` | 无 | — | — |
| `optimize()` | `strategy` | ✅ | 必须是 OptimizationStrategy 枚举值 |
| `optimize()` | `context` | ❌ | dict，最大 10 个键 |
| `register_daemon()` | `name` | ✅ | 全局唯一，最大 64 字符，`[a-z][a-z0-9_-]+` |
| `register_daemon()` | `start_fn` | ✅ | Callable，无参数，返回 None |
| `register_daemon()` | `stop_fn` | ✅ | Callable，无参数，返回 None，必须幂等 |
| `register_daemon()` | `priority` | ❌ | 0-10 整数，默认 5，0 最高优先级 |
| `on_pressure()` | `callback` | ✅ | Callable[[PressureLevel, ResourceSnapshot], None] |
| `force_pressure()` | `level` | ✅ | PressureLevel 枚举值 |
| `force_pressure()` | `reason` | ✅ | 非空字符串，最大 256 字符 |
| `get_optimization_history()` | `limit` | ❌ | 1-10000 整数，默认 100 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `snapshot()` | `ResourceSnapshot`：所有字段非 None（缺失时为 0） | 不抛异常，降级到默认值 |
| `optimize()` | `OptimizationResult`：actions_taken 非空列表 | `OptimizationResult(success=False, error_message=...)` |
| `register_daemon()` | None | `ValueError("Daemon '{name}' already registered")` |
| `start_daemon()` | `True` | `False`（守护线程不存在或已运行） |
| `stop_daemon()` | `True` | `False`（守护线程不存在或已停止，幂等） |
| `health_check()` | `HealthCheckResult` | 不抛异常，降级到 `engine_running=False` |
| `force_pressure()` | None | `PermissionError("Owner approval required")` |

### 4.5 MCP 接口

**Tools**：

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `resource_snapshot` | `snapshot()` | `{}` | `ResourceSnapshot` JSON |
| `resource_optimize` | `optimize()` | `{strategy: str, context?: dict}` | `OptimizationResult` JSON |
| `resource_health` | `health_check()` | `{}` | `HealthCheckResult` JSON |
| `resource_pressure` | `get_pressure_state()` | `{}` | `PressureState` JSON |
| `resource_daemon_list` | `DaemonRegistry.list()` | `{}` | `list[DaemonInfo]` JSON |
| `resource_cache_stats` | `get_cache_stats()` | `{}` | `CacheStats` JSON |

**错误码**：
- `ROE_001(400)` — 无效策略名
- `ROE_002(403)` — 权限不足（force_pressure 需 Owner）
- `ROE_003(404)` — 守护线程不存在
- `ROE_004(409)` — 守护线程名称冲突
- `ROE_005(503)` — 引擎未运行

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增优化策略（OptimizationStrategy 枚举值） | ✅ 向后兼容 | 不影响已有消费者 |
| 新增防御策略（DefensiveStrategy 枚举值） | ✅ 向后兼容 | 不影响已有消费者 |
| 新增 MCP Tool | ✅ 向后兼容 | 不影响已有消费者 |
| 修改 ResourceSnapshot 字段 | ⚠️ 需通知 | 消费者需更新解析逻辑 |
| 修改压力阈值 | ✅ 向后兼容 | 配置变更，非接口变更 |
| 删除/重命名 API 方法 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 修改 MCP Tool 输入 Schema | ⚠️ 需通知 | 消费者需更新参数 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | psutil 为可选依赖 | 桌面环境可能未安装，需降级到 Windows API |
| 2 | 不修改 Trae 进程管理 | Trae 的 MCP 进程启动逻辑不在我们控制范围 |
| 3 | 优化动作不得影响业务正确性 | quality_preserved = True 是硬约束 |
| 4 | 守护线程停止操作必须是幂等的 | 重复调用 stop() 不报错 |
| 5 | 所有优化动作必须可回滚 | 优化失败时能恢复到优化前状态 |
| 6 | 监控循环自身资源占用 | < 1% CPU |
| 7 | 配置变更热加载无需重启 | 运行时修改阈值不中断监控循环 |
| 8 | 单例模式——全局唯一引擎实例 | 防止多实例导致资源竞争和策略冲突 |

### 5.2 容量估算

#### 当前规模（2026-05-08）

| 指标 | 当前值 |
|------|--------|
| 蓝图注册数 | 47 |
| Python 源文件数 | 1,714 |
| 子目录数 | 192 |
| 后台守护线程 | ~10 |
| MCP 服务器进程（10 对话） | 180 |
| 总内存占用 | 19.15 GB |

#### 1,500 模块目标规模

| 指标 | 1,500 模块时估算 | 依据 |
|------|--------|------|
| Python 源文件数 | ~54,000 | 1,714 × (1500/47) ≈ 54,680 |
| 后台守护线程 | ~300 | 每模块平均 0.2 个守护线程 |
| 蓝图文档 | 1,500 份 | 每模块一份 |
| YAML 配置文件 | ~15,000 | 每模块平均 10 个配置 |
| JSONL 日志文件 | ~3,000 | 每模块平均 2 个日志 |
| 单次全量扫描耗时 | ~30 分钟 | os.walk 54K 文件 + 逐文件 stat |
| 内存占用（无优化） | ~200 GB | 300 守护线程 × 115MB + 缓存 + 数据 |
| 内存占用（有优化） | ~8 GB | 进程池复用 + 懒加载 + 流式读取 |

#### 1,500 模块下的关键瓶颈与对策

| 瓶颈 | 无优化时 | 优化后 | 对策 |
|------|---------|--------|------|
| **进程数爆炸** | 1,500 × 10 对话 × 10 MCP = 150,000 进程 | ≤ 30 进程 | MCP 进程池跨对话共享 |
| **守护线程爆炸** | 300 线程各自轮询 | ≤ 20 线程 | 单例 + 按需启动 + 自适应频率 |
| **磁盘 I/O** | 300 线程 × 每分钟 1 次全量扫描 | 缓存命中率 90%+ | FileCache + mtime 校验 |
| **JSONL 全量读取** | 3,000 文件 × 每次 O(n) | O(limit) | tail_jsonl + 偏移量索引 |
| **YAML 解析** | 15,000 文件 × 每分钟重复解析 | 缓存命中 0 次解析 | FileCache + LRU |
| **内存泄漏** | 300 模块 × 各自累积 | 统一 GC + TTL 清理 | DaemonRegistry + purge_expired |
| **蓝图路由** | 1,500 条规则线性匹配 | O(log n) 分层路由 | 层级索引 + 关键字倒排 |
| **import 链** | 1,500 模块全部 import | 按需 import | 懒加载 + importlib 动态导入 |

#### 1,500 模块容量验证清单

| # | 检查项 | 通过标准 | 验证方法 |
|---|--------|---------|---------|
| C1 | 1,500 个蓝图注册表加载时间 | < 2 秒 | 基准测试 |
| C2 | 蓝图路由匹配时间 | < 50ms | 基准测试 |
| C3 | 10 对话时 Python 进程数 | ≤ 30 | 进程计数 |
| C4 | 10 对话时内存占用 | ≤ 8 GB | psutil 采样 |
| C5 | FileCache 命中率 | ≥ 90% | 缓存统计 |
| C6 | tail_jsonl(limit=100) 内存 | < 1 MB | 内存分析 |
| C7 | 300 守护线程注册 + 启动时间 | < 10 秒 | 基准测试 |
| C8 | EMERGENCY 压力下恢复时间 | < 60 秒 | 压力测试 |
| C9 | 优化历史查询 10,000 条 | < 100ms | 数据库查询 |
| C10 | 全量资源快照采集时间 | < 500ms | 基准测试 |
| C11 | 监控循环自身 CPU 占用 | < 1% | psutil 采样 |
| C12 | 压力状态转换抖动次数（1小时内） | ≤ 3 次 | 日志分析 |
| C13 | 断路器从 OPEN 到 HALF_OPEN 时间 | 30 秒 | 计时 |
| C14 | 配置热加载延迟 | < 5 秒 | 计时 |

### 5.3 迁移/废弃方案

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 执行状态 |
|---|-------------|---------|---------|---------|:---:|
| 1 | DaemonRegistry 旧版 | `daemon_registry.py` | `resource_optimization_engine.py` 内含 | 旧文件保留为 re-export 兼容层 | 已完成 |
| 2 | guard_loop | `resource_guard.py` | 注册到 DaemonRegistry | 旧函数保留为兼容入口 | 已完成 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | psutil 未安装 | ImportError 捕获 | 降级到 Windows GlobalMemoryStatusEx API | 指标精度降低 |
| 2 | 优化动作失败 | CircuitBreaker 计数 | 熔断 30s → HALF_OPEN 探测 → 自动恢复 | 该策略暂停 |
| 3 | 压力等级抖动 | 冷却期计时器 | 滞后机制（上升 75%/下降 65%）+ 冷却 60s | 策略切换频率降低 |
| 4 | 配置文件损坏 | YAML 解析异常 | 使用内存中最后有效配置 + 告警 | 配置不更新 |
| 5 | 守护线程崩溃 | DaemonRegistry 心跳 | 自动重启（最多 3 次，间隔 30s） | 该守护线程功能暂停 |
| 6 | 进程池进程僵尸 | zombie_check_interval 扫描 | SIGTERM → SIGKILL → 回收 | 该进程槽位释放 |
| 7 | 缓存 mtime 校验失败 | 文件修改时间变化 | 缓存条目失效，下次读取重新解析 | 缓存命中率下降 |
| 8 | SQLite 写入锁争用 | SQLITE_BUSY 异常 | WriteBatcher 批量合并 + 重试 | 优化历史写入延迟 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 优化动作误停关键服务 | 高 | quality_preserved 硬约束 + 优先级系统 + 人类确认回调 | 模拟 EMERGENCY 场景验证 |
| 2 | 进程池状态泄漏 | 高 | 每次 MCP 调用前重置上下文 + 请求级沙箱 | 状态隔离测试 |
| 3 | 配置注入攻击 | 中 | 配置文件权限控制 + YAML schema 校验 | 配置篡改测试 |
| 4 | 资源优化引擎自身资源泄漏 | 中 | self_health_check + 自动重启 + SQLite 存储（非内存） | 长时间运行内存监控 |
| 5 | 背压传播导致级联故障 | 高 | EMERGENCY 级别直接停止非核心服务 + 人类告警 | 压力测试 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | ResourceOptimizationEngine, FileCache, StreamingReader, ProcessPool, LazyLoader | 压力分级/缓存命中/流式读取/进程复用/懒加载 | 覆盖率 ≥80% |
| 2 | 集成测试 | DaemonRegistry + 各守护线程接入 | 6 个守护线程注册+启停+优先级排序 | 全部 RUNNING |
| 3 | 压力测试 | 100 AI 并发 + 内存泄漏模拟 | EMERGENCY 触发+自愈闭环+60s 恢复 | 自愈 ≤60s |
| 4 | 容量测试 | 1,500 模块规模模拟 | C1-C14 容量验证清单 | 全部通过 |
| 5 | 回归测试 | 配置热加载+断路器+滞后机制 | 配置变更5s生效/熔断30s恢复/抖动≤3次/h | 全部通过 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 类型 | 内容 | 版本 |
|----------|------|------|------|
| MOD-INF-016 (shared_core) | 必须 | daemon_registry, event_bus, lifecycle, contract_bus, API_INDEX | ≥0.14.0 |
| MOD-INF-015 (system_telemetry) | 必须 | metrics, health_probes, SLI 上报 | ≥0.9.0 |
| MOD-INF-009 (pipeline) | 必须 | pipeline_lock, orchestration | ≥0.36.0 |
| MOD-FEEDBACK_LOOP (feedback_loop) | 必须 | scheduler (注册为守护线程), detectors | ≥0.32.0 |
| MOD-GATE_ENGINE (gate_engine) | 可选 | 资源检查门禁规则 | ≥0.5.0 |
| MOD-INF-020 (audit-trail) | 可选 | 优化动作审计记录 | ≥1.4.0 |
| MOD-INF-023 (drift-detector) | 可选 | 资源配置漂移检测 | ≥1.0.1 |
| MOD-INF-024 (budget-enforcer) | 可选 | 资源成本预算集成 | ≥0.7.0 |
| MOD-INF-019 (agent-spec) | 可选 | 技能注册 | ≥0.17.0 |
| MOD-INF-013 (mcp_servers) | 可选 | MCP 工具暴露 | ≥0.3.41 |
| psutil | pip (可选) | 系统指标采集 | ≥5.9.0 |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-RESOURCE_OPTIMIZATION_ENGINE` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| resource_optimization_engine.py | daemon_registry.py | 引擎使用 DaemonRegistry 注册/启停守护线程 | DaemonRegistry 先于 Engine 初始化 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| ResourceOptimizationEngine.snapshot() | PressureStateMachine | ResourceSnapshot | 函数调用 |
| PressureStateMachine | StrategyEngine | PressureLevel | 函数调用 |
| StrategyEngine.optimize() | AuditTrail | OptimizationResult | EventBus |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 多模块依赖关系复杂 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖 |
| 3 | 临时时态内容自动清理 | 否 | 无迁移方案 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 |
|---|---------|---------|-------------|
| 1 | 依赖图自动生成 | AST解析import + manifest字段 | asset-inventory/dependency.py |
| 2 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py |
| 4 | 施工步骤完成度自动检测 | pytest+mypy+ruff + 产出物存在性检查 | 部分有 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | 手动 | 按需 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物

| 产出物 | 绝对路径 |
|--------|---------|
| 资源优化引擎主模块 | `D:\ZephyrAlpha\src\zephyr\trading\resource_optimization.py` |
| 守护线程注册表（升级版） | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\daemon_registry.py` |
| I/O 缓存层 | `D:\ZephyrAlpha\src\zephyr\shared\io\io_cache.py` |
| 流式读取工具 | `D:\ZephyrAlpha\src\zephyr\shared\io\streaming_reader.py` |
| 进程池管理器 | `D:\ZephyrAlpha\src\zephyr\shared\infra\process_pool.py` |
| 懒加载器 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\lazy_loader.py` |
| 资源优化配置 | `D:\ZephyrAlpha\config\resource_optimization.yaml` |
| 单元测试 | `D:\ZephyrAlpha\tests\unit\shared\test_resource_optimization.py` |
| 容量测试 | `D:\ZephyrAlpha\tests\capacity\test_1500_module_capacity.py` |
| 蓝图文档 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\resource_optimization_engine\blueprint.md` |

---

## §12 集成目标

### 12.1 核心集成（Tier 1）

| 集成目标 | 方式 | 集成点 | 验证方法 |
|----------|------|--------|---------|
| FeedbackLoopScheduler | 注册为 priority=5 守护线程 | `scheduler.py` start() | 启动 10 对话后仅 1 个 FLE 实例运行 |
| ResourceGuard | 注册为 priority=3 守护线程 + shutil.disk_usage | `resource_guard.py` guard_loop() | guard_loop CPU 占用 < 0.1% |
| SelfMonitor | 注册为 priority=7 守护线程 + 流式读取 | `self_monitor.py` start_scheduler() | check() 内存占用 < 1MB |
| AuditWriter | 使用 io_cache 缓存 + append 写入 | `writer.py` _write() | 写入延迟 < 1ms（不随文件大小增长） |
| HeartbeatServer | 注册为 priority=8 守护线程 + 单例保护 | `heartbeat_server.py` start() | 端口冲突时不崩溃 |
| CollectionManager | 定期调用 purge_expired() | `collection_manager.py` | ChromaDB 存储增长率 < 1MB/天 |
| MCP Gateway | 进程池复用 | `gateway_server.py` | 10 对话时 Python 进程数 ≤ 20 |

### 12.2 系统集成（Tier 2）

| 集成目标 | 方式 | 集成点 | 验证方法 |
|----------|------|--------|---------|
| EventBus | 发布资源压力事件 | `event_bus.py` emit() | 压力变化时事件正确发布 |
| ContractBus | 注册资源优化契约 | `contract_bus.py` register() | 契约校验通过 |
| API_INDEX | 注册资源优化 API | `API_INDEX.py` register() | API 可被检索 |
| Gate Engine | 新增 G-RES 资源检查门禁 | `gates/_registry.yaml` | 资源不足时门禁阻断 |
| System Telemetry | 上报资源 SLI 指标 | `config/sli_registry.yaml` | 指标可查询 |
| Audit Trail | 记录优化动作审计 | `audit_trail/writer.py` | 优化动作可追溯 |
| Drift Detector | 资源配置漂移检测 | `behavioral_auditor/drift_engine.py` | 阈值被篡改时检测到 |
| Budget Enforcer | 资源成本预算联动 | `budget_enforcer/budget_engine.py` | 资源超支时触发预算降级 |
| Rollback System | 优化动作回滚支持 | `rollback/rollback_executor.py` | 优化失败时可回滚 |

### 12.3 AI 可发现性集成（Tier 3）

| 集成目标 | 方式 | 集成点 | 验证方法 |
|----------|------|--------|---------|
| Agent Spec | 注册 SKILL-DOM-ROE-001 技能 | `skill_registry.yaml` | AI 通过技能名发现资源优化能力 |
| MCP Servers | 暴露 6 个资源优化 MCP 工具 | `mcp/gateway_server.py` | AI 通过 MCP 调用资源优化功能 |
| Blueprint Routing | 新增 R030 路由规则 | `config/blueprint_routing.yaml` | AI 通过关键字自动定位到本蓝图 |
| Trigger Routing | 新增 task_keywords 映射 | `src/zephyr/agent-spec/skill-registry.yaml` | AI 通过触发词路由到资源优化技能 |
| Blueprint Registry | 新增 MOD-RESOURCE_OPTIMIZATION_ENGINE 条目 | `docs/03_modules/blueprint_registry.yaml` | 蓝图可被蓝图搜索 MCP 发现 |
| Module Registry | 新增 MOD-RESOURCE_OPTIMIZATION_ENGINE 条目 | `docs/03_modules/module_registry.yaml` | 模块可被模块索引发现 |
| Cross-Module Dependency | 新增依赖关系 | `cross-module-dependency-registry.yaml` | 依赖链可追溯 |
| Module ID Registry | 新增 MOD-RESOURCE_OPTIMIZATION_ENGINE ID | `module_id_registry.yaml` | ID 不冲突 |
| AGENTS.md | 新增资源优化冷启动步骤 | `AGENTS.md` | 新 AI session 知道资源优化引擎存在 |
| project_rules.md | 新增 STEP 引用 | `.trae/rules/project_rules.md` | Trae 自动加载规则中包含资源优化 |

---

## §13 需要更新

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | lifecycle __init__ | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\__init__.py` | 导出 ResourceOptimizationEngine | 模块可导入 |
| 2 | io __init__ | `D:\ZephyrAlpha\src\zephyr\shared\io\__init__.py` | 导出 io_cache, streaming_reader | 模块可导入 |
| 3 | FLE Scheduler | `D:\ZephyrAlpha\src\zephyr\feedback_loop\scheduler.py` | 使用 DaemonRegistry.register() 注册 | 统一调度 |
| 4 | ResourceGuard | `D:\ZephyrAlpha\src\zephyr\drift-detector\resource_guard.py` | 使用 DaemonRegistry.register() 注册 | 统一调度 |
| 5 | SelfMonitor | `D:\ZephyrAlpha\src\zephyr\audit-trail\self_monitor.py` | 使用 DaemonRegistry.register() 注册 | 统一调度 |
| 6 | HeartbeatServer | `D:\ZephyrAlpha\src\zephyr\shared\heartbeat_server.py` | 使用 DaemonRegistry.register() 注册 | 统一调度 |
| 7 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 新增 MOD-RESOURCE_OPTIMIZATION_ENGINE 条目 | 蓝图可发现 |
| 8 | 模块注册表 | `D:\ZephyrAlpha\docs\03_modules\module_registry.yaml` | 新增 MOD-RESOURCE_OPTIMIZATION_ENGINE 条目 | 模块可发现 |
| 9 | 蓝图路由表 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` | 新增 R030 路由规则 | AI 可路由 |
| 10 | 技能注册表 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | 新增 SKILL-DOM-ROE-001 + task_keywords | AI 可发现技能 |
| 11 | 跨模块依赖注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` | 新增 MOD-RESOURCE_OPTIMIZATION_ENGINE 依赖关系 | 依赖链可追溯 |
| 12 | 模块ID注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 新增 MOD-RESOURCE_OPTIMIZATION_ENGINE ID | ID 唯一性 |
| 13 | Gate 注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` | 新增 G-RES 资源检查门禁 | 资源不足时门禁阻断 |
| 14 | SLI 注册表 | `D:\ZephyrAlpha\config\sli_registry.yaml` | 新增资源优化 SLI 指标 | 可观测性 |
| 15 | MCP 工具契约 | `D:\ZephyrAlpha\src\zephyr\mcp\tool-contracts.yaml` | 新增 6 个资源优化工具契约 | MCP 可调用 |
| 16 | 集成闭环总蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint.md` | 新增 CT-ROE 集成契约 | 跨系统集成 |
| 17 | requirements.txt | `D:\ZephyrAlpha\requirements.txt` | 新增 psutil>=5.9.0 (可选) | 依赖声明 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|:----:|:----:|---------|------|
| R1 | psutil 未安装导致指标缺失 | 中 | 低 | 降级到 Windows GlobalMemoryStatusEx API | 风险 |
| R2 | 进程池复用导致状态泄漏 | 低 | 高 | 每次使用前重置 MCP 服务器状态 + 请求级沙箱 | 风险 |
| R3 | 缓存一致性——YAML 文件被外部修改 | 中 | 中 | 缓存条目带 mtime 校验，变化时失效 | 风险 |
| R4 | 优化动作误判——停止了必要的服务 | 低 | 高 | 优先级系统 + quality_preserved 硬约束 + 人类确认回调 | 风险 |
| R5 | 监控线程自身成为 CPU 瓶颈 | 低 | 中 | 30 秒间隔 + psutil.cpu_percent(interval=0) 非阻塞 | 风险 |
| R6 | 压力等级抖动——频繁在 WARNING/NORMAL 间切换 | 中 | 中 | 滞后机制（上升阈值 75% / 下降阈值 65%）+ 冷却期 60 秒 | 风险 |
| R7 | 断路器误开——偶发失败导致策略被熔断 | 低 | 高 | HALF_OPEN 探测机制 + 失败计数阈值 ≥3 + 自动恢复 30 秒 | 风险 |
| R8 | 背压传播——优化速度跟不上恶化速度 | 低 | 高 | EMERGENCY 级别直接停止所有非核心服务 + 人类告警 | 风险 |
| R9 | 配置热加载导致运行中策略参数突变 | 中 | 中 | 配置变更在下一个监控周期生效 + 当前正在执行的策略不受影响 | 风险 |
| R10 | 优化器自身资源泄漏 | 低 | 高 | 优化历史使用 SQLite 存储（非内存）+ 定期 self_health_check + 自动重启 | 风险 |
| R11 | 懒加载首次调用延迟过高 | 中 | 低 | CACHE_WARM 策略预判热点模块 + import 预加载 | 风险 |
| R12 | 单例模式在多进程环境下失效 | 低 | 中 | 文件锁保证跨进程单例 + 进程池内共享实例 | 风险 |
| R13 | 新增 psutil 可选依赖 | 中 | 低 | 已在 requirements.txt 中声明 | 负面后果 |
| R14 | 守护线程注册为必须步骤——现有模块需改造接入 | 高 | 中 | Phase 3 分步接入，每次一个模块 | 负面后果 |
| R15 | 缓存层增加内存开销（约 10-50MB） | 高 | 低 | LRU 淘汰 + max_entries 上限控制 | 负面后果 |
| R16 | 进程池引入状态管理复杂度——需确保 MCP 服务器状态隔离 | 中 | 中 | 请求级沙箱 + 使用前重置上下文 | 负面后果 |
| R17 | 优化器自身需被监控——"谁监控监控者"问题 | 中 | 低 | self_health_check + 自动重启 | 负面后果 |
| R18 | 降级矩阵增加运维认知负担 | 低 | 低 | 通过 MCP 工具和仪表盘降低理解成本 | 负面后果 |

---

## §16 施工指引

### 施工策略

分 7 个 Phase，对应三大架构转变 + I/O 优化 + 自愈闭环 + AI 可发现性 + 容量验证：

### Phase 1: 统一调度引擎（对应转变 3：从各自轮询到统一调度）✅ COMPLETED

**前置条件**：DaemonRegistry 已存在

**实施步骤**：

1. **读**：阅读 `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\daemon_registry.py` 现有实现
2. **做**：创建 `D:\ZephyrAlpha\src\zephyr\trading\resource_optimization.py`
   - 实现 `ResourceOptimizationEngine` 类（单例）
   - 实现 `snapshot_resources()` 采集 CPU/内存/进程/磁盘 I/O
   - 实现 `_classify_pressure()` 压力分级（NORMAL/WARNING/CRITICAL/EMERGENCY）
   - 实现 `_monitor_loop()` 30 秒循环
   - 实现防御策略引擎：EMERGENCY 时停止低优先级守护线程，CRITICAL 时降低频率
   - 实现优化策略引擎：NORMAL 时缓存预热/批量 I/O，WARNING 时流式读取/延迟初始化
   - 实现 `optimize()` 统一调度两个策略引擎
   - 实现 `OptimizationStrategy` 枚举和对应执行逻辑
   - 实现压力状态机（含滞后机制和冷却期）
   - 实现断路器模式（CLOSED/OPEN/HALF_OPEN）
   - 实现 `health_check()` 自检端点
3. **产**：`resource_optimization_engine.py` + 单元测试
4. **检**：运行测试，验证压力分级逻辑正确

**完成标准**：
- `snapshot_resources()` 在 Windows 上正常采集内存指标
- 压力分级逻辑覆盖所有 4 个级别
- 防御策略和优化策略各自独立触发、互不干扰
- 监控循环可启停
- 压力状态机滞后机制防止抖动
- 断路器在 3 次失败后熔断

### Phase 2: I/O 优化层 ✅ COMPLETED

**前置条件**：Phase 1 完成

**实施步骤**：

1. **读**：阅读 `D:\ZephyrAlpha\src\zephyr\shared\io\__init__.py` 和 `file_utils.py`
2. **做**：
   - 创建 `D:\ZephyrAlpha\src\zephyr\shared\io\io_cache.py`
     - `FileCache` 类：基于 mtime 的 YAML/JSON 文件缓存
     - 缓存键 = 文件路径 + mtime，值 = 解析后的 dict
     - 最大缓存 1000 条目，LRU 淘汰
   - 创建 `D:\ZephyrAlpha\src\zephyr\shared\io\streaming_reader.py`
     - `tail_jsonl()` 函数：读取 JSONL 文件最后 N 行（seek 到文件末尾附近）
     - `stream_jsonl()` 函数：生成器模式逐行读取，不全部加载
3. **产**：`io_cache.py` + `streaming_reader.py` + 单元测试
4. **检**：验证缓存命中率 ≥90%（重复读取场景）

**完成标准**：
- `FileCache` 缓存命中时 0 次 I/O
- `tail_jsonl(path, 100)` 内存占用 < 100KB
- 缓存条目在文件修改后自动失效

### Phase 3: 守护线程统一接入（对应转变 3：消除各自轮询）✅ COMPLETED

**前置条件**：Phase 1 完成

**实施步骤**：

1. **读**：阅读所有需要接入的守护线程模块
2. **做**：
   - 修改 `scheduler.py`：在 `start()` 中调用 `DaemonRegistry.register("fle-scheduler", self.start, self.stop, priority=5)`
   - 修改 `resource_guard.py`：在 `guard_loop()` 启动时注册
   - 修改 `self_monitor.py`：在 `start_scheduler()` 中注册
   - 修改 `heartbeat_server.py`：在 `start()` 中注册
   - 修改 `auto_evolution.py`：在 `start()` 中注册
   - 修改 `task_queue.py`：在 `start()` 中注册
3. **产**：修改后的 6 个文件 + 集成测试
4. **检**：启动所有守护线程后 `DaemonRegistry.status()` 显示全部 RUNNING

**完成标准**：
- 所有守护线程通过 DaemonRegistry 注册
- `stop_low_priority()` 能按优先级停止守护线程
- EMERGENCY 压力时自动停止低优先级守护线程

### Phase 4: 进程池 + 懒加载（对应转变 1 + 转变 2）✅ COMPLETED

**前置条件**：Phase 2 + Phase 3 完成

**实施步骤**：

1. **读**：阅读 `D:\ZephyrAlpha\src\zephyr\mcp\gateway_server.py` 进程管理逻辑
2. **做**：
   - 创建 `D:\ZephyrAlpha\src\zephyr\shared\infra\process_pool.py`
     - `MCPProcessPool` 类：管理 MCP 服务器进程的生命周期
     - 最大进程数限制（默认 30）
     - 进程复用：同一 MCP 服务器跨对话共享
     - 僵尸进程检测和回收
   - 创建 `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\lazy_loader.py`
     - `LazyModuleRegistry` 类：按需加载模块
     - `importlib.import_module()` 动态导入
     - 热点模块预判 + 预加载
   - 实现自适应调度：
     - FLE-Scheduler 在 NORMAL 压力时 30 秒轮询
     - WARNING 压力时延长到 60 秒
     - CRITICAL 压力时延长到 120 秒
     - EMERGENCY 压力时暂停（stop + 后续恢复）
3. **产**：`process_pool.py` + `lazy_loader.py` + 集成测试
4. **检**：10 对话场景下进程数 ≤ 20，内存 < 8GB

**完成标准**：
- 进程池最大进程数可配置
- 懒加载：启动时仅加载核心框架（~20 模块），其余按需加载
- 自适应调度根据压力自动调整轮询频率
- 10 对话场景下系统不卡顿、不报 -2 错误

### Phase 5: 自愈闭环 + 配置管理 ✅ COMPLETED

**前置条件**：Phase 1-4 完成

**实施步骤**：

1. **做**：
   - 创建 `D:\ZephyrAlpha\config\resource_optimization.yaml` 配置文件（关键字段约束见蓝图特有：配置管理）
   - 实现配置热加载（文件 mtime 监控 + 下一个监控周期生效）
   - 实现自愈闭环：检测→诊断→优化→验证
   - 实现背压机制：优化速度跟不上恶化速度时触发 EMERGENCY
   - 集成 EventBus 发布资源压力事件
   - 集成 Audit Trail 记录优化动作
2. **产**：配置文件 + 自愈逻辑 + 集成测试
3. **检**：模拟内存泄漏场景，验证自愈闭环在 60 秒内恢复

**完成标准**：
- 配置文件存在且所有参数有明确默认值
- 配置变更在 5 秒内生效
- 自愈闭环：内存泄漏→检测→优化→验证 ≤60 秒
- EventBus 事件正确发布
- 优化动作可审计追溯

### Phase 6: AI 可发现性 + 注册

**前置条件**：Phase 1 完成

**实施步骤**：

1. **做**：
   - 更新 `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml`：新增 MOD-RESOURCE_OPTIMIZATION_ENGINE 条目
   - 更新 `D:\ZephyrAlpha\docs\03_modules\module_registry.yaml`：新增 MOD-RESOURCE_OPTIMIZATION_ENGINE 条目
   - 更新 `D:\ZephyrAlpha\config\blueprint_routing.yaml`：新增 R030 路由规则
   - 更新 `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml`：新增 SKILL-DOM-ROE-001 + task_keywords
   - 更新 `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml`：新增依赖
   - 更新 `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml`：新增 ID
   - 更新 `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml`：新增 G-RES 门禁
   - 更新 `D:\ZephyrAlpha\config\sli_registry.yaml`：新增资源 SLI
   - 更新 `D:\ZephyrAlpha\src\zephyr\mcp\tool-contracts.yaml`：新增 6 个工具契约
   - 创建 `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\resource_optimization.md`：技能描述文件
2. **产**：10+ 个注册表更新 + 1 个技能描述文件
3. **检**：通过 blueprint_search MCP 可搜索到 MOD-RESOURCE_OPTIMIZATION_ENGINE

**完成标准**：
- 所有注册表包含 MOD-RESOURCE_OPTIMIZATION_ENGINE 条目
- 蓝图路由 R030 匹配关键字"资源优化"/"resource"/"内存"/"CPU"
- 技能注册表包含 SKILL-DOM-ROE-001
- MCP 工具契约包含 6 个资源优化工具

### Phase 7: 1,500 模块容量验证

**前置条件**：Phase 1-6 全部完成

**实施步骤**：

1. **读**：阅读 §5.2 中"1,500 模块容量验证清单"
2. **做**：
   - 创建容量基准测试脚本 `D:\ZephyrAlpha\tests\capacity\test_1500_module_capacity.py`
   - 模拟 1,500 模块注册（使用轻量级 mock 模块）
   - 逐一验证 C1-C14 容量检查项
   - 记录基准数据到 `D:\ZephyrAlpha\tests\capacity\baseline_1500.yaml`
3. **产**：容量测试 + 基准数据
4. **检**：所有 C1-C14 检查项通过

**完成标准**：
- C1-C14 全部通过
- 基准数据记录完整，可供后续回归对比

### 回滚方案

每个 Phase 独立，可单独回滚：
- Phase 1 回滚：删除 `resource_optimization_engine.py`，恢复 `daemon_registry.py` 旧版
- Phase 2 回滚：删除 `io_cache.py` 和 `streaming_reader.py`
- Phase 3 回滚：恢复 6 个守护线程模块的原始启动逻辑
- Phase 4 回滚：删除 `process_pool.py` 和 `lazy_loader.py`，恢复原始调度频率
- Phase 5 回滚：删除 `resource_optimization.yaml`，移除 EventBus/Audit 集成代码
- Phase 6 回滚：恢复所有注册表到更新前状态
- Phase 7 回滚：删除容量测试脚本

### 施工状态

| Phase | 对应转变 | 状态 | 完成日期 |
|:-----:|:-------:|:----:|:--------:|
| 1 | 转变 3（统一调度） | completed | 2026-05-10 |
| 2 | I/O 优化 | completed | 2026-05-10 |
| 3 | 转变 3（统一接入） | completed | 2026-05-12 |
| 4 | 转变 1（进程池）+ 转变 2（懒加载） | completed | 2026-05-13 |
| 5 | 自愈闭环 + 配置管理 | completed | 2026-05-14 |
| 6 | AI 可发现性 + 注册 | not_started | - |
| 7 | 1,500 模块容量验证 | not_started | - |

---

## §17 容量升级

### 17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 被管理模块数 | 51 | module_registry.yaml 条目数 |
| Python 进程数（10 对话） | 180 | psutil.process_iter() |
| 内存占用 | 19.15 GB | psutil.virtual_memory() |
| 守护线程数 | ~10 | DaemonRegistry.status() |
| 监控循环 CPU 占用 | ~30% | psutil.cpu_percent() |

### 17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | 资源阈值是经验值（mem=75%/cpu=80%） | 容量感知阈值函数 compute_thresholds() | 模块数 >100 |
| GAP-002 | 全局资源池无 per-session 隔离 | SessionResourceTracker + 背压 | AI 并发 >10 |
| GAP-003 | MAPE-K 循环 30s cron 延迟 | 事件驱动 fsnotify + cron fallback | 文件变更事件 >1/s |
| GAP-004 | GPU 不在调度池 | GPU 资源分区 + CUDA Stream per-session | 已实现 |
| GAP-005 | 资源预算与模块数脱节 | CapacityBudgetController 动态重算 | 模块数变化 >50 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-032-01 | 防御+优化合为一个系统 | A:分离/B:合并 | B | 共享传感器+统一调度+知识库统一 | 2026-05-08 |
| 2 | D-032-02 | 进程池共享模式 | A:per-session/B:per-type | B | MCP 无状态+K8s HPA验证+请求级隔离成本更低 | 2026-05-08 |
| 3 | D-032-03 | 懒加载策略 | A:全量import/B:importlib动态 | B | 5-15模块/对话 vs 1500全量 | 2026-05-08 |
| 4 | D-032-04 | 统一调度替代各自轮询 | A:各自while/B:统一调度器 | B | 300线程上下文切换+无法自适应 | 2026-05-08 |
| 5 | D-032-05 | 容量感知阈值函数 | A:静态经验值/B:模块数函数 | B | 1500模块时经验值完全失效 | 2026-05-08 |
| 6 | D-032-06 | 事件驱动 MAPE-K | A:cron 30s/B:fsnotify+fallback | B | 100AI并发时30s延迟错过干预窗口 | 2026-05-08 |
| 7 | D-032-07 | 分离防御/优化为两个独立系统 | A:分离/B:合并 | B | 共享传感器数据冗余、策略需协调、知识库分裂——单系统双引擎更高效 | 2026-05-08 |
| 8 | D-032-08 | 使用 Prometheus + Grafana 外部监控 | A:外部监控/B:自建监控 | B | 引入外部依赖、桌面环境部署复杂 | 2026-05-08 |
| 9 | D-032-09 | 基于 Kubernetes HPA 的资源调度 | A:K8s HPA/B:单机调度 | B | 桌面环境无 K8s | 2026-05-08 |
| 10 | D-032-10 | 纯定时 cron 调度 | A:cron/B:事件驱动MAPE-K | B | 无法响应实时事件、30s 延迟 | 2026-05-08 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 已遵守 |
|---|------|:------:|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | ✅ |
| 2 | 必备链接不可省略 | ✅ |
| 3 | 蓝图必须是最终设计结果 | ✅ |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | ✅ |
| 5 | 涉及文件范围必须明确列出 | ✅ |
| 6 | 容量估算必须写 | ✅ |
| 7 | 迁移/废弃方案必须写 | ✅ |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | ✅ |
| 9 | 蓝图必须自包含 | ✅ |
| 10 | 删除文件必须遵守安全删除协议 | ✅ |
| 11 | construction_progress 必须与代码实际状态一致 | ✅ |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | ✅ |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | ✅ |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | ✅ |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | ✅ |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀（如 CAP-G vs CAP）
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

### 本蓝图判定

**判定结果：原地升级**。所有内容（MAPE-K 详细设计、压力状态机、降级矩阵、全系统集成契约、AI 可发现性设计、自动化运维设计、配置管理、高阶衍生项）均属于同一资源优化引擎模块的深度设计，服务对象相同、变更频率同步、依赖关系完全重叠。

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。仅新增文件和修改现有文件。

---

## 必备链接

| # | 链接 | 路径 |
|---|------|------|
| 1 | DaemonRegistry 现有实现 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\daemon_registry.py` |
| 2 | EventBus 现有实现 | `D:\ZephyrAlpha\src\zephyr\shared\event_bus.py` |
| 3 | ContractBus 现有实现 | `D:\ZephyrAlpha\src\zephyr\shared\contract_bus.py` |
| 4 | API_INDEX 现有实现 | `D:\ZephyrAlpha\src\zephyr\shared\API_INDEX.py` |
| 5 | FeedbackLoopScheduler | `D:\ZephyrAlpha\src\zephyr\feedback_loop\scheduler.py` |
| 6 | ResourceGuard | `D:\ZephyrAlpha\src\zephyr\drift-detector\resource_guard.py` |
| 7 | SelfMonitor | `D:\ZephyrAlpha\src\zephyr\audit-trail\self_monitor.py` |
| 8 | AuditWriter | `D:\ZephyrAlpha\src\zephyr\audit-trail\writer.py` |
| 9 | CollectionManager | `D:\ZephyrAlpha\src\zephyr\vector_memory\collection_manager.py` |
| 10 | ContextBudgetTracker | `D:\ZephyrAlpha\src\zephyr\context_engine\context_budget_tracker.py` |
| 11 | HeartbeatServer | `D:\ZephyrAlpha\src\zephyr\shared\heartbeat_server.py` |
| 12 | Lifecycle hooks | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\hooks.py` |
| 13 | MCP Gateway | `D:\ZephyrAlpha\src\zephyr\mcp\gateway_server.py` |
| 14 | 蓝图模板 | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-template.md` |
| 15 | 蓝图架构标准 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_042_meta_rule_standard.yaml` |
| 16 | 元数据注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` |
| 17 | 目录结构标准 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` |
| 18 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` |
| 19 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` |
| 20 | 模块注册表 | `D:\ZephyrAlpha\docs\03_modules\module_registry.yaml` |
| 21 | 蓝图路由表 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` |
| 22 | 技能注册表 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` |
| 23 | Gate 注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` |
| 24 | SLI 注册表 | `D:\ZephyrAlpha\config\sli_registry.yaml` |
| 25 | 跨模块依赖注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` |
| 26 | 集成闭环总蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint.md` |
| 27 | 系统总蓝图 | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | ResourceGuard | `D:\ZephyrAlpha\src\zephyr\drift-detector\resource_guard.py` | 磁盘空间监控 + os.walk 扫描 | ResourceGuard 只做磁盘监控和文件扫描，无 CPU/内存/进程池/缓存/调度优化能力，且自身就是资源浪费源（每5秒全量扫描） |
| 2 | DaemonRegistry | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\daemon_registry.py` | 守护线程注册 | DaemonRegistry 只做注册，无压力感知、无自适应调度、无优先级驱动的启停策略。本蓝图升级 DaemonRegistry 而非替换 |
| 3 | ContextBudgetTracker | `D:\ZephyrAlpha\src\zephyr\context_engine\context_budget_tracker.py` | Token 预算管理 | ContextBudgetTracker 只管 Token 预算，不管系统级资源（CPU/内存/磁盘/进程）。两者互补不重叠 |
| 4 | CapacityAssurance (MOD-INF-001) | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\capacity_assurance\blueprint.md` | 容量规划 + 限流 | MOD-INF-001 做容量规划（事前），本蓝图做运行时资源优化（事中+事后）。MOD-INF-001 回答"系统能承载多少"，本蓝图回答"当前资源怎么用得更好" |
| 5 | BudgetEnforcer (MOD-INF-024) | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\budget-enforcer\blueprint.md` | 预算执行 + 降级 | BudgetEnforcer 管 Token/Cost/Time 三维预算，本蓝图管 CPU/Memory/Disk/Process 四维系统资源。BudgetEnforcer 的降级策略可触发本蓝图的自适应调度 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 资源优化引擎主模块 | `D:\ZephyrAlpha\src\zephyr\trading\resource_optimization.py` | 新建 | 新建 |
| 1a | 数据模型 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\resource_optimization_models.py` | 新建 | 新建 |
| 2 | 守护线程注册表 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\daemon_registry.py` | 读取+修改 | 修改 |
| 3 | I/O 缓存层 | `D:\ZephyrAlpha\src\zephyr\shared\io\io_cache.py` | 新建 | 新建 |
| 4 | 流式读取工具 | `D:\ZephyrAlpha\src\zephyr\shared\io\streaming_reader.py` | 新建 | 新建 |
| 5 | 进程池管理器 | `D:\ZephyrAlpha\src\zephyr\shared\infra\process_pool.py` | 新建 | 新建 |
| 6 | 懒加载器 | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\lazy_loader.py` | 新建 | 新建 |
| 7 | 资源优化配置 | `D:\ZephyrAlpha\config\resource_optimization.yaml` | 新建 | 新建 |
| 8 | lifecycle __init__ | `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\__init__.py` | 修改 | 修改 |
| 9 | io __init__ | `D:\ZephyrAlpha\src\zephyr\shared\io\__init__.py` | 修改 | 修改 |
| 10 | FLE Scheduler | `D:\ZephyrAlpha\src\zephyr\feedback_loop\scheduler.py` | 修改 | 修改 |
| 11 | LocalModelScheduler | `D:\ZephyrAlpha\src\zephyr\vector_memory\local_model_scheduler.py` | 修改 | 修改 |
| 12 | SelfMonitor | `D:\ZephyrAlpha\src\zephyr\audit-trail\self_monitor.py` | 修改 | 修改 |
| 13 | CircadianScheduler | `D:\ZephyrAlpha\src\zephyr\runtime\circadian_scheduler.py` | 修改 | 修改 |
| 14 | AutoEvolution | `D:\ZephyrAlpha\src\zephyr\feedback_loop\auto_evolution.py` | 修改 | 修改 |
| 15 | infra __init__ | `D:\ZephyrAlpha\src\zephyr\shared\infra\__init__.py` | 修改 | 修改 |
| 16 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 修改 | 修改 |
| 17 | 模块注册表 | `D:\ZephyrAlpha\docs\03_modules\module_registry.yaml` | 修改 | 修改 |
| 18 | 蓝图路由表 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` | 修改 | 修改 |
| 19 | 技能注册表 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | 修改 | 修改 |
| 20 | 跨模块依赖注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` | 修改 | 修改 |
| 21 | 模块ID注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 修改 | 修改 |
| 22 | Gate 注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` | 修改 | 修改 |
| 23 | SLI 注册表 | `D:\ZephyrAlpha\config\sli_registry.yaml` | 修改 | 修改 |
| 24 | MCP 工具契约 | `D:\ZephyrAlpha\src\zephyr\mcp\tool-contracts.yaml` | 修改 | 修改 |
| 25 | 基础设施注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\infrastructure-registry.md` | 修改 | 修改 |
| 26 | 目录注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\directory-registry.md` | 修改 | 修改 |
| 27 | 系统路径注册表 | `D:\ZephyrAlpha\docs\03_modules\system_pathway_registry.yaml` | 修改 | 修改 |
| 28 | 单元测试（引擎） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_engine.py` | 新建 | 新建 |
| 29 | 单元测试（缓存） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_io_cache.py` | 新建 | 新建 |
| 30 | 单元测试（流式读取） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_streaming_reader.py` | 新建 | 新建 |
| 31 | 单元测试（进程池） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_process_pool.py` | 新建 | 新建 |
| 32 | 单元测试（懒加载） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_lazy_loader.py` | 新建 | 新建 |
| 33 | 单元测试（自愈闭环） | `D:\ZephyrAlpha\tests\unit\resource_optimization\test_self_healing.py` | 新建 | 新建 |
| 34 | 蓝图文档 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\resource_optimization_engine\blueprint.md` | 本文件 | 修改 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 资源优化引擎架构设计 | **本文档 §1-§10** | — |
| 资源优化引擎施工步骤 | **本文档 §16** | — |
| 资源优化引擎接口契约 | **本文档 §4** | — |
| MAPE-K 详细设计 | **本文档 蓝图特有：MAPE-K 详细设计** | — |
| 压力状态机设计 | **本文档 蓝图特有：压力状态机** | — |
| 降级矩阵 | **本文档 蓝图特有：优雅降级矩阵** | — |
| AI 可发现性设计 | **本文档 蓝图特有：AI 可发现性设计** | — |
| 高阶衍生项 | **本文档 蓝图特有：高阶衍生项** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 使用方式 |
|:----:|--------|---------|
| 1 | FeedbackLoopScheduler | 注册为守护线程 + 自适应调度 |
| 1 | ResourceGuard | 注册为守护线程 + 优化 I/O |
| 1 | SelfMonitor | 注册为守护线程 + 流式读取 |
| 1 | AuditWriter | 使用 io_cache + append 写入 |
| 1 | HeartbeatServer | 注册为守护线程 + 单例保护 |
| 2 | CollectionManager | 定期 purge_expired() |
| 2 | MCP Gateway | 进程池复用 |
| 2 | EventBus | 压力变化事件消费 |
| 2 | System Telemetry | SLI 指标上报 |
| 2 | Audit Trail | 优化动作审计 |
| 2 | Gate Engine | 资源检查门禁 |
| 2 | Budget Enforcer | 预算降级联动 |
| 2 | Drift Detector | 配置漂移检测 |
| 3 | Agent Spec | 技能注册 + 发现 |
| 3 | MCP Servers | 工具暴露 |
| 3 | Blueprint Routing | 路由发现 |
| 3 | 所有新 AI session | 通过三重发现机制使用 |

### 变更同步规则

| 变更类型 | Tier 1（直接消费者） | Tier 2（系统集成） | Tier 3（AI 可发现性） |
|---------|------------------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 | 更新 MCP 工具契约 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 | 更新技能描述 |
| 修改模块边界 | 下游更新依赖声明 | 更新集成路由 | 更新蓝图路由关键字 |
| 新增优化策略 | 无影响 | 更新降级矩阵 | 更新技能描述 + MCP 工具 |
| 修改压力阈值 | 无影响 | 更新 SLI 指标 | 无影响 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| 新增优化策略 | AI 可自主 + 更新 §4 枚举 + 通知 Tier 2 |
| 修改压力阈值 | AI 可自主 + 更新 §5 + 通知 Tier 2 |
| 施工步骤微调 | AI 可自主修改 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 |
| force_pressure() 调用 | 需 Owner 审批 |

### 负向责任

本文件**不涉及**：网络带宽优化 / 容器化资源隔离 / 安全策略执行（→ MOD-INF-018）/ 业务算法优化

### 触发条件

`resource-optimization` / `进程池` / `I/O缓存` / `懒加载` / `守护线程` / `MAPE-K` / `断路器` / `背压` / `压力分级`

### 漂移防护

| 修改本文件 | MUST 同步更新 |
|-----------|-------------|
| 接口契约 §4 | DaemonRegistry + EventBus 订阅者 |
| 压力阈值 §3.3 | DaemonRegistry + 配置热加载 |
| 新增优化策略 §4.2 | Skill 路由表 + pipeline 调度 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-15 | 5.2.0 | v3.5 模板升级 + 压缩：§0前移至概述后；§7备选方案删除（合并到§18）；§15后果删除（负面合并到§14、正面删除）；§0.1新增存在性/阻塞原因列；§5.1移除原因列；§5.3新增执行状态列；§14新增类型列；铁律扩展至15条；新增蓝图拆分判定标准；新增§10.2/§10.3/§10.4；配置完整YAML示例替换为关键字段约束表；施工Phase状态修正为实际completed；章节编号冲突修复（12-20→蓝图特有）；frontmatter更新codification_level:L2 |
| 2026-05-14 | 5.1.0 | 初始蓝图——MAPE-K 驱动资源优化引擎全量设计 |

---

## 蓝图特有章节

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：资源优化引擎的深度设计细节
> 不可砍理由：这些是资源优化引擎的核心设计，砍掉=失去设计依据

### 蓝图特有：MAPE-K 详细设计

#### Monitor（监控层）

| 组件 | 职责 | 采集频率 | 降级策略 |
|------|------|---------|---------|
| CpuMonitor | cpu_percent, cpu_count, load_avg | 30s | psutil 缺失时跳过 |
| MemoryMonitor | memory_percent, memory_used_gb, memory_total_gb | 30s | 降级到 Windows GlobalMemoryStatusEx |
| DiskMonitor | disk_io_read_mb_s, disk_io_write_mb_s, disk_free_gb | 30s | 降级到 shutil.disk_usage |
| ProcessMonitor | process_count, thread_count, zombie_count | 30s | 降级到 os.getpid() + psutil.Process |
| DaemonMonitor | 各守护线程运行状态 | 60s | 仅检查 DaemonRegistry 状态 |

#### Analyze（分析层）

| 分析器 | 职责 | 输入 | 输出 |
|--------|------|------|------|
| PressureClassifier | 压力分级 | ResourceSnapshot | PressureLevel |
| TrendAnalyzer | 资源趋势分析 | 最近 10 个 ResourceSnapshot | 趋势方向（上升/平稳/下降） |
| AnomalyDetector | 异常检测 | ResourceSnapshot + 历史基线 | 是否异常 + 置信度 |
| RootCauseAnalyzer | 根因分析 | 异常 + 守护线程状态 + 进程列表 | 最可能原因 |

#### Plan（计划层）

| 规划器 | 职责 | 触发条件 | 输出 |
|--------|------|---------|------|
| DefensivePlanner | 防御策略规划 | CRITICAL/EMERGENCY | DefensiveStrategy 列表 |
| OffensivePlanner | 优化策略规划 | NORMAL/WARNING | OptimizationStrategy 列表 |
| ConflictResolver | 策略冲突解决 | 防御和优化策略同时触发 | 优先执行防御策略 |
| RollbackPlanner | 回滚计划 | 优化失败 | 回滚步骤列表 |

#### Execute（执行层）

| 执行器 | 职责 | 安全保障 |
|--------|------|---------|
| StrategyExecutor | 执行优化/防御策略 | 断路器保护 + quality_preserved 校验 |
| DaemonController | 守护线程启停控制 | 幂等操作 + 优先级排序 |
| CacheManager | 缓存管理 | mtime 校验 + TTL 过期 |
| ProcessPoolManager | 进程池管理 | 最大进程数限制 + 僵尸回收 |

#### Knowledge（知识层）

| 知识类型 | 存储 | 用途 |
|---------|------|------|
| 优化历史 | SQLite `resource_optimization.db` | 策略效果分析 + 趋势预测 |
| 压力转换历史 | 内存（最近 1000 次） | 抖动检测 + 滞后校准 |
| 策略成功率 | 内存（LRU 100 条） | 策略选择优先级 |
| 资源基线 | SQLite | 异常检测基线 |
| 配置快照 | SQLite | 配置漂移检测 |

### 蓝图特有：压力状态机

#### 转换规则

| 从 → 到 | 触发条件 | 滞后机制 | 冷却期 |
|---------|---------|---------|--------|
| NORMAL → WARNING | memory > 75% 或 cpu > 80% 或 process_count > 50 | 无 | 60s |
| WARNING → NORMAL | memory < 65% 且 cpu < 70% 且 process_count < 40 | 滞后 10% | 60s |
| WARNING → CRITICAL | memory > 85% 或 cpu > 90% | 无 | 60s |
| CRITICAL → WARNING | memory < 75% 且 cpu < 80% | 滞后 10% | 60s |
| CRITICAL → EMERGENCY | memory > 95% 或 cpu > 98% | 无 | 30s |
| EMERGENCY → CRITICAL | memory < 90% | 滞后 5% | 30s |

#### 防抖动机制

- **滞后（Hysteresis）**：上升阈值和下降阈值之间保持 10% 差距，防止在阈值附近频繁切换
- **冷却期（Cooldown）**：状态转换后 60 秒内不再转换（EMERGENCY 除外，30 秒）
- **确认计数**：连续 2 次采样满足条件才触发转换，单次异常不触发
- **抖动检测**：1 小时内转换超过 3 次则记录告警，自动加宽滞后区间

### 蓝图特有：优雅降级矩阵

| 子系统 | NORMAL | WARNING | CRITICAL | EMERGENCY |
|--------|--------|---------|----------|-----------|
| FLE-Scheduler | 30s 轮询 | 60s 轮询 | 120s 轮询 | 暂停 |
| ResourceGuard | 5s 扫描 | 30s 扫描 | 60s 扫描 | 暂停 |
| SelfMonitor | 正常检查 | 流式读取 | 减少检查项 | 仅心跳 |
| HeartbeatServer | 正常心跳 | 降低频率 | 最低频率 | 仅保持端口 |
| AuditWriter | 正常写入 | 批量写入 | 仅 append | 缓冲到内存 |
| CollectionManager | 正常 purge | 延长 purge 间隔 | 暂停 purge | 暂停 |
| MCP 进程池 | 正常复用 | 限制新进程 | 不创建新进程 | 释放非核心进程 |
| FileCache | 正常缓存 | 限制新缓存条目 | 冻结缓存 | 清理低优先级缓存 |
| 懒加载 | 正常按需加载 | 仅加载核心模块 | 仅加载必要模块 | 禁止加载 |
| EventBus | 正常发布 | 批量发布 | 仅发布关键事件 | 仅发布 EMERGENCY 事件 |

### 蓝图特有：全系统集成契约

#### EventBus 事件类型

| 事件名 | 触发条件 | 数据 |
|--------|---------|------|
| `resource.pressure.changed` | 压力等级变化 | `{old_level, new_level, snapshot}` |
| `resource.optimization.executed` | 优化策略执行完成 | `{strategy, result, snapshot_before, snapshot_after}` |
| `resource.optimization.failed` | 优化策略执行失败 | `{strategy, error, snapshot}` |
| `resource.daemon.stopped` | 守护线程被停止 | `{daemon_name, reason, pressure_level}` |
| `resource.circuit_breaker.opened` | 断路器打开 | `{strategy, failure_count}` |
| `resource.circuit_breaker.closed` | 断路器关闭 | `{strategy}` |
| `resource.emergency.entered` | 进入 EMERGENCY | `{snapshot, root_cause}` |
| `resource.emergency.recovered` | 从 EMERGENCY 恢复 | `{snapshot, recovery_time_s}` |

#### ContractBus 契约

| 契约 ID | 方向 | 内容 |
|---------|------|------|
| CT-ROE-001 | ROE → EventBus | 压力变化事件发布契约 |
| CT-ROE-002 | ROE → AuditTrail | 优化动作审计记录契约 |
| CT-ROE-003 | BudgetEnforcer → ROE | 预算降级触发资源优化契约 |
| CT-ROE-004 | ROE → GateEngine | 资源不足门禁阻断契约 |
| CT-ROE-005 | FeedbackLoop → ROE | 资源异常检测器注册契约 |
| CT-ROE-006 | DriftDetector → ROE | 资源配置漂移通知契约 |

#### API_INDEX 注册

| API 名 | 模块 | 方法 | 描述 |
|--------|------|------|------|
| `resource_snapshot` | ResourceOptimizationEngine | snapshot() | 获取当前资源快照 |
| `resource_optimize` | ResourceOptimizationEngine | optimize() | 执行优化策略 |
| `resource_health` | ResourceOptimizationEngine | health_check() | 健康检查 |
| `resource_pressure` | ResourceOptimizationEngine | get_pressure_state() | 获取压力状态 |
| `resource_cache_stats` | ResourceOptimizationEngine | get_cache_stats() | 缓存统计 |
| `resource_daemon_list` | DaemonRegistry | list() | 守护线程列表 |

#### Gate 门禁规则

| Gate ID | 类型 | 触发条件 | 动作 |
|---------|------|---------|------|
| G-RES-001 | pre_check | memory_percent > 90% | 阻断非必要操作，提示"系统资源不足" |
| G-RES-002 | pre_check | process_count > 100 | 阻断新进程创建 |
| G-RES-003 | post_check | 优化后 memory 未降低 | 告警 + 升级到 EMERGENCY |

#### SLI 指标

| SLI 名 | 类型 | 目标 | 测量方法 |
|--------|------|------|---------|
| `resource_optimization_success_rate` | 成功率 | ≥ 95% | 成功次数 / 总执行次数 |
| `resource_pressure_recovery_time_s` | 恢复时间 | ≤ 60s | EMERGENCY 进入到恢复的时间 |
| `resource_cache_hit_rate` | 缓存命中率 | ≥ 90% | 命中次数 / 总访问次数 |
| `resource_process_pool_reuse_rate` | 进程复用率 | ≥ 80% | 复用次数 / 总请求次数 |
| `resource_monitor_cpu_overhead_percent` | 监控开销 | ≤ 1% | 监控循环 CPU 占用 |

### 蓝图特有：AI 可发现性设计

> 三重发现机制确保新 AI session 在 0 次人工指引下自动发现资源优化功能。

#### 发现路径 1：蓝图路由

AI 通过 `config/blueprint_routing.yaml` R030 规则自动定位：

```yaml
- route_id: "R030"
  blueprint_id: "MOD-RESOURCE_OPTIMIZATION_ENGINE"
  blueprint_level: module
  path_patterns:
    - "src/zephyr/trading/resource_optimization.py"
    - "src/zephyr/shared/io/io_cache.py"
    - "src/zephyr/shared/io/streaming_reader.py"
    - "src/zephyr/shared/infra/process_pool.py"
    - "src/zephyr/shared/lifecycle/lazy_loader.py"
    - "config/resource_optimization.yaml"
  task_keywords:
    - "资源优化"
    - "resource optimization"
    - "内存"
    - "memory"
    - "CPU"
    - "进程池"
    - "process pool"
    - "缓存"
    - "cache"
    - "守护线程"
    - "daemon"
    - "压力"
    - "pressure"
    - "降级"
    - "degradation"
    - "懒加载"
    - "lazy load"
    - "流式读取"
    - "streaming"
    - "自愈"
    - "self-healing"
    - "MAPE-K"
    - "断路器"
    - "circuit breaker"
    - "背压"
    - "backpressure"
  scope: pre_change
  safety: "H"
  priority: 91
  description: "资源优化引擎 — MAPE-K 循环驱动的资源监控、分析、优化与自愈系统"
```

#### 发现路径 2：Agent Skill

```yaml
SKILL-DOM-ROE-001:
  name: resource-optimization
  description: "Resource Optimization Engine (MOD-RESOURCE_OPTIMIZATION_ENGINE) MAPE-K 循环驱动的资源监控/分析/优化/自愈。双策略引擎（防御+优化），压力状态机（NORMAL/WARNING/CRITICAL/EMERGENCY），断路器，背压，优雅降级矩阵，进程池复用，I/O 缓存，流式读取，懒加载，自适应调度。入口 ResourceOptimizationEngine.snapshot()/optimize()/health_check()"
  skill_type: domain
  tier: L1
  path: resource_optimization.md
  references:
    - MOD-RESOURCE_OPTIMIZATION_ENGINE
    - MOD-INF-016
    - MOD-INF-015
```

触发路由 task_keywords：

```yaml
resource: resource-optimization
资源优化: resource-optimization
内存优化: resource-optimization
memory: resource-optimization
cpu: resource-optimization
进程池: resource-optimization
process_pool: resource-optimization
daemon: resource-optimization
守护线程: resource-optimization
pressure: resource-optimization
压力: resource-optimization
degradation: resource-optimization
降级: resource-optimization
cache: resource-optimization
缓存: resource-optimization
lazy: resource-optimization
懒加载: resource-optimization
self-healing: resource-optimization
自愈: resource-optimization
circuit_breaker: resource-optimization
断路器: resource-optimization
```

#### 发现路径 3：MCP 工具

AI 通过 MCP 工具直接调用资源优化功能（见 §4.5）。

#### 冷启动集成

新 AI session 冷启动时，通过以下路径发现资源优化引擎：

```
AGENTS.md → PS-STD-005 §7 → MOD-MASTER_BLUEPRINT → MOD-RESOURCE_OPTIMIZATION_ENGINE
                                                     ↓
                              blueprint_routing.yaml R030（关键字匹配）
                                                     ↓
                              skill-registry.yaml SKILL-DOM-ROE-001
                                                     ↓
                              MCP 工具 resource_snapshot/health_check
```

#### 需登记的注册表完整清单

| # | 注册表 | 路径 | 登记内容 |
|---|--------|------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | MOD-RESOURCE_OPTIMIZATION_ENGINE 条目 |
| 2 | 模块注册表 | `D:\ZephyrAlpha\docs\03_modules\module_registry.yaml` | MOD-RESOURCE_OPTIMIZATION_ENGINE 条目 |
| 3 | 蓝图路由表 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` | R030 路由规则 |
| 4 | 技能注册表 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | SKILL-DOM-ROE-001 + keywords |
| 5 | 跨模块依赖注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\cross-module-dependency-registry.yaml` | MOD-RESOURCE_OPTIMIZATION_ENGINE 依赖 |
| 6 | 模块ID注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | MOD-RESOURCE_OPTIMIZATION_ENGINE ID |
| 7 | Gate 注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` | G-RES-001~003 |
| 8 | SLI 注册表 | `D:\ZephyrAlpha\config\sli_registry.yaml` | 5 个资源 SLI |
| 9 | MCP 工具契约 | `D:\ZephyrAlpha\src\zephyr\mcp\tool-contracts.yaml` | 6 个工具契约 |
| 10 | 基础设施注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\infrastructure-registry.md` | MOD-RESOURCE_OPTIMIZATION_ENGINE 基础设施条目 |
| 11 | 文档元数据索引 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 蓝图文档元数据 |
| 12 | 目录注册表 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\directory-registry.md` | 新增目录条目 |
| 13 | 系统路径注册表 | `D:\ZephyrAlpha\docs\03_modules\system_pathway_registry.yaml` | 资源优化路径 |

### 蓝图特有：自动化运维设计

#### 自愈闭环

| 阶段 | 自动化程度 | 人工介入 |
|------|:---------:|---------|
| 检测 | 100% 自动 | 无 |
| 分析 | 100% 自动 | 无 |
| 计划 | 95% 自动 | EMERGENCY 级别需人类确认（可配置跳过） |
| 执行 | 100% 自动 | 无 |
| 验证 | 100% 自动 | 无 |
| 回滚 | 100% 自动 | 无 |

#### 混沌工程（压力测试）

| 测试场景 | 触发方式 | 预期行为 | 验证方法 |
|---------|---------|---------|---------|
| 内存泄漏模拟 | 分配大量对象不释放 | WARNING → CRITICAL → 自动 GC → 恢复 | 内存恢复到 NORMAL |
| 进程数爆炸 | 启动大量子进程 | 进程池限制 + 僵尸回收 | 进程数 ≤ max_processes |
| 磁盘 I/O 阻塞 | 模拟大量文件写入 | IO_BATCH 策略 + append 写入 | I/O 延迟 < 阈值 |
| 守护线程死锁 | 模拟线程阻塞 | 超时检测 + 自动重启 | 线程恢复运行 |
| 配置漂移 | 修改阈值配置 | 漂移检测 + 告警 | 漂移被检测到 |

#### Runbook（运维手册）

| 场景 | 自动处理 | 人工操作 |
|------|---------|---------|
| 内存 > 90% | 自动触发 CRITICAL 策略 | 无需操作 |
| 内存 > 95% | 自动触发 EMERGENCY + 停止低优先级服务 | 检查是否有异常进程 |
| 优化策略连续失败 3 次 | 断路器打开 + 告警 | 检查失败原因 |
| 压力状态 1 小时抖动 > 3 次 | 自动加宽滞后区间 | 检查是否有周期性负载 |
| 监控循环自身崩溃 | 自动重启（daemon 线程） | 检查崩溃原因 |
| 进程池僵尸进程 > 5 | 自动回收 | 检查是否有进程泄漏 |

#### 自动化优化策略

| 策略 | 触发条件 | 自动执行 | 可配置参数 |
|------|---------|---------|-----------|
| CACHE_WARM | NORMAL + 空闲时段 | 预热最近访问的 YAML 文件 | 预热文件数、预热间隔 |
| IO_BATCH | WARNING + 多个小 I/O | 合并为批量操作 | 批量大小、合并窗口 |
| PROCESS_POOL | 任何级别 | 复用 MCP 进程 | 最大进程数、超时时间 |
| LAZY_INIT | WARNING + 内存 > 70% | 延迟加载非核心模块 | 核心模块列表 |
| STREAMING_READ | WARNING + 大文件读取 | 切换为流式读取 | 文件大小阈值 |
| SCHEDULE_ADAPT | 任何级别 | 调整守护线程频率 | 各级别频率 |
| MEMORY_COMPACT | CRITICAL + 内存 > 85% | GC + 对象池化 | GC 触发阈值 |

### 蓝图特有：配置管理

`D:\ZephyrAlpha\config\resource_optimization.yaml` 关键字段约束：

| 字段路径 | 类型 | 默认值 | 约束 |
|---------|------|------|------|
| `pressure_thresholds.memory_warning_percent` | int | 75 | 60-85 |
| `pressure_thresholds.memory_critical_percent` | int | 85 | 80-95 |
| `pressure_thresholds.memory_emergency_percent` | int | 95 | 90-98 |
| `pressure_thresholds.cpu_warning_percent` | int | 80 | 60-90 |
| `hysteresis.percent` | int | 10 | 5-20 |
| `hysteresis.cooldown_seconds` | int | 60 | 30-300 |
| `schedule.normal_interval_s` | int | 30 | 10-120 |
| `cache.max_entries` | int | 1000 | 100-10000 |
| `cache.ttl_seconds` | int | 300 | 60-3600 |
| `process_pool.max_processes` | int | 30 | 5-100 |
| `circuit_breaker.failure_threshold` | int | 3 | 2-10 |
| `circuit_breaker.recovery_timeout_s` | int | 30 | 10-300 |
| `audit.max_history_records` | int | 10000 | 1000-100000 |
| `self_healing.max_recovery_time_s` | int | 60 | 30-300 |

热加载机制：配置文件 mtime 监控（每 30 秒）→ 变更检测 → 下一个监控周期生效 → 当前正在执行的策略不受影响。

### 蓝图特有：可观测性集成

#### 指标上报

| 指标 | 类型 | 上报目标 | 频率 |
|------|------|---------|------|
| resource_cpu_percent | gauge | System Telemetry | 30s |
| resource_memory_percent | gauge | System Telemetry | 30s |
| resource_process_count | gauge | System Telemetry | 30s |
| resource_pressure_level | gauge(0-3) | System Telemetry | 30s |
| resource_optimization_total | counter | System Telemetry | 事件驱动 |
| resource_optimization_success | counter | System Telemetry | 事件驱动 |
| resource_optimization_duration_ms | histogram | System Telemetry | 事件驱动 |
| resource_cache_hit_rate | gauge | System Telemetry | 60s |

审计集成——每个优化动作记录到 Audit Trail：

```python
audit_entry = {
    "actor": "ResourceOptimizationEngine",
    "action": "optimize",
    "strategy": strategy.value,
    "pressure_before": snapshot_before.pressure.value,
    "pressure_after": snapshot_after.pressure.value,
    "memory_before_gb": snapshot_before.memory_used_gb,
    "memory_after_gb": snapshot_after.memory_used_gb,
    "quality_preserved": result.quality_preserved,
    "duration_ms": result.duration_ms,
    "timestamp": datetime.now().isoformat(),
}
```

### 蓝图特有：高阶衍生项

> 从本蓝图衍生出的二阶~N阶效应和补充设计

#### 优化器自身的资源消耗

优化器自身消耗 CPU（监控循环）+ 内存（缓存+历史记录）。缓解：
- 监控循环 CPU 开销 < 1%（C11 验证项）
- 优化历史使用 SQLite 存储（非内存），单条记录 < 1KB
- 缓存内存开销有上限（max_entries=1000 × 平均 50KB = ~50MB）
- `self_health_check()` 每 5 分钟检查自身资源占用，超过阈值时自动降级监控频率

#### 优化策略之间的冲突

CACHE_WARM（预热缓存）和 MEMORY_COMPACT（释放内存）可能同时触发。缓解：
- ConflictResolver：WARNING 时 CACHE_WARM 优先，CRITICAL 时 MEMORY_COMPACT 优先
- 策略互斥表：每种策略声明 `excludes: [策略列表]`，执行前检查
- 同一监控周期内只执行一种策略

#### 跨 Session 优化知识传递

优化历史持久化到 SQLite（跨 session 保留），Session 交接时 SelfMonitor 写入资源状态到 session_logs，新 session 冷启动时自动加载最近优化历史。

#### 优化策略的进化

策略效果评分——每次执行后记录效果。连续 10 次效果为负的策略自动降级。Feedback Loop 集成——资源异常模式可注册为新的 detector。

#### 元优化——优化优化过程本身

参数自调优——基于优化历史自动调整参数。A/B 测试——对相同压力场景交替使用不同参数比较效果。安全边界——参数调整范围有上下限。参数调整超过 5% 需 Owner 确认。
