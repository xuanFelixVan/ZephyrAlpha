# [BLUEPRINT] MOD-INF-063 | docs/03_modules/_domain_infrastructure_runtime/redis_state_layer_ssot/blueprint.md | §
# [MODULE] zephyr.infrastructure.redis_state_layer_ssot
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 13 命名空间三层结构与 TTL 矩阵唯一真源=A9 运维架构 §1.2; 未知命名空间/Key 校验 Fail-Closed; 配置就绪件仅产出草稿文本不执行系统写入
# [MODIFY-GUARD] tests/infrastructure/test_redis_state_layer_ssot.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RedisStateLayerSotError(未登记错误码-申请中)
# [TESTS] tests/infrastructure/test_redis_state_layer_ssot.py
# [A_module] module_id=MOD-INF-063 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Redis 共享状态层 SSOT（MOD-INF-063）——13 命名空间三层结构/TTL 矩阵/混合持久化收口。

真源：A9 运维架构 §1.2（docs/_working/架构图/运维架构.md）+ CAND-H1FS-004（B14-04531）。

职责边界（不替代既有散件）：
  - 连接建连归 MOD-INF-002 redis_config（config/.env.redis 单真源，fail-closed）；
  - H1 业务 Key 构造归 MOD-H1_REDIS_HOT h1_redis_schema（7 类业务 Key）；
  - 通用状态原语归 MOD-INF-016 state_store_redis；
  - 本模块是 A9 五进程（P1~P5）共享状态平面的**参数与契约真源**：
    13 命名空间三层归属、TTL 矩阵（tick=5s/signal=60s/factor=300s）、
    RDB 每小时+AOF everysec 混合持久化、maxmemory 8GB 硬限+volatile-ttl、
    AOF 重放优先混合恢复（纯 AOF ~3min → 混合 <15s）。

硬边界：本模块只产出 redis.conf 配置就绪件草稿文本与恢复 runbook 声明；
系统级应用（写 redis.conf / CONFIG SET / 服务重启）属 Owner 窗口，AI 不执行。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: name 参数
#   fields: 参数 name，类型注解 str
#   code: redis_state_layer_ssot.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: key 参数
#   fields: 参数 key，类型注解 str
#   code: redis_state_layer_ssot.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_namespace
#   name_en: get_namespace
#   intro: 按名取命名空间声明；未知命名空间 Fail-Closed。
#   desc: 按名取命名空间声明；未知命名空间 Fail-Closed。；源码 L351-L356
#   inputs: name
#   outputs: NamespaceSpec
# - id: A2
#   name_zh: ② ttl_for
#   name_en: ttl_for
#   intro: 命名空间静态 TTL（秒）；None=永不过期；未知命名空间 Fail-Closed。
#   desc: 命名空间静态 TTL（秒）；None=永不过期；未知命名空间 Fail-Closed。；源码 L359-L361
#   inputs: name
#   outputs: int | None
# - id: A3
#   name_zh: ③ validate_key
#   name_en: validate_key
#   intro: 校验 Key 属于已登记命名空间，返回命名空间名；未知/畸形 Fail-Closed。
#   desc: 校验 Key 属于已登记命名空间，返回命名空间名；未知/畸形 Fail-Closed。；源码 L364-L372
#   inputs: key
#   outputs: str
# - id: A4
#   name_zh: ④ render_redis_conf_draft
#   name_en: render_redis_conf_draft
#   intro: 产出 redis.conf 配置就绪件草稿文本（仅文本，不执行任何系统写入）。
#   desc: 产出 redis.conf 配置就绪件草稿文本（仅文本，不执行任何系统写入）。 硬边界：实际应用（写 redis.conf / CONFIG SET / 重启 Redis 服务）…；源码 L375-L395
#   inputs: 无参数
#   outputs: str
# - id: A5
#   name_zh: ⑤ recovery_runbook
#   name_en: recovery_runbook
#   intro: AOF 重放优先混合恢复 runbook 步骤（声明；演练执行属 Owner 窗口）。
#   desc: AOF 重放优先混合恢复 runbook 步骤（声明；演练执行属 Owner 窗口）。；源码 L398-L408
#   inputs: 无参数
#   outputs: list[str]
# - id: A6
#   name_zh: ⑥ check_registry_consistency
#   name_en: check_registry_consistency
#   intro: 注册表一致性自检：13 命名空间/三层归属合法/TTL 矩阵完整/Key 前缀无冲突。
#   desc: 注册表一致性自检：13 命名空间/三层归属合法/TTL 矩阵完整/Key 前缀无冲突。；源码 L411-L434
#   inputs: 无参数
#   outputs: dict[str, object]
#   （注：A6 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: NamespaceSpec
#   name_en: NamespaceSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: int | None
#   name_en: int | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Final

__all__: Final = [
    "NAMESPACE_TTL_MATRIX",
    "REDIS_NAMESPACE_REGISTRY",
    "REDIS_PERSISTENCE_PROFILE",
    "NamespaceSpec",
    "PersistenceProfile",
    "RedisStateLayerSotError",
    "check_registry_consistency",
    "get_namespace",
    "recovery_runbook",
    "render_redis_conf_draft",
    "ttl_for",
    "validate_key",
]


class RedisStateLayerSotError(RuntimeError):
    """Redis 状态层 SSOT 校验失败（未知命名空间/Key 畸形/矩阵缺项，Fail-Closed）。"""


# ============================================================================
# 三层结构（A9 §1.2 唯一真源图）
# ============================================================================

LAYER_REALTIME_DATA: Final[str] = "realtime_data"  # 实时数据层（TTL 驱动）
LAYER_STATE_COORDINATION: Final[str] = "state_coordination"  # 状态协调层（持久化）
LAYER_OPS_CONTROL: Final[str] = "ops_control"  # 运维控制层（Pub/Sub+配置）

_VALID_LAYERS: Final[frozenset[str]] = frozenset({LAYER_REALTIME_DATA, LAYER_STATE_COORDINATION, LAYER_OPS_CONTROL})

_HB_TTL_BUFFER_SECONDS: Final[int] = 30  # hb TTL = 进程超时阈值 + 30s 缓冲（§1.2 表注）


@dataclass(frozen=True)
class NamespaceSpec:
    """单个 Redis 命名空间声明（A9 §1.2.1 表行为唯一真源）。"""

    name: str  # 命名空间名（如 tick / market_state）
    layer: str  # 三层归属（realtime_data/state_coordination/ops_control）
    key_pattern: str  # Key 模式（如 tick:{symbol}）
    producer: str  # 生产者进程（P1~P5）
    consumers: tuple[str, ...]  # 消费者进程
    ttl_seconds: int | None  # 静态 TTL；None=永不过期（hb 走 dynamic_ttl）
    structure: str  # Redis 数据结构（Hash/Sorted Set/String/List）
    purpose: str  # 用途
    dynamic_ttl: Callable[[int], int] | None = field(default=None, compare=False)
    # dynamic_ttl(process_timeout_seconds) -> TTL；仅 hb 使用（超时阈值+30s 缓冲）


@dataclass(frozen=True)
class PersistenceProfile:
    """Redis 7.x 单实例混合持久化参数声明（A9 §1.2 框图唯一真源）。"""

    rdb_save_rules: tuple[tuple[str, str], ...]  # (seconds, min_changes) 基线规则
    aof_enabled: bool
    aof_fsync: str  # everysec（交易时段）
    maxmemory_gb: int  # 8GB 硬限（OOM 防护，稳态≈4GB）
    maxmemory_policy: str  # volatile-ttl
    recovery_strategy: str  # aof_first_hybrid（AOF 重放优先+RDB 基线加速）
    recovery_target_seconds: int  # 混合恢复目标 <15s（纯 AOF ~3min）


# ============================================================================
# 13 命名空间注册表（A9 §1.2.1 表逐行收口）
# ============================================================================

REDIS_NAMESPACE_REGISTRY: Final[tuple[NamespaceSpec, ...]] = (
    NamespaceSpec(
        name="tick",
        layer=LAYER_REALTIME_DATA,
        key_pattern="tick:{symbol}",
        producer="P1",
        consumers=("P2", "P3"),
        ttl_seconds=5,
        structure="Hash",
        purpose="最新行情快照",
    ),
    NamespaceSpec(
        name="signal",
        layer=LAYER_REALTIME_DATA,
        key_pattern="signal:{strategy_id}:{date}",
        producer="P2",
        consumers=("P3",),
        ttl_seconds=60,
        structure="Sorted Set",
        purpose="信号队列(按时间排序)",
    ),
    NamespaceSpec(
        name="factor",
        layer=LAYER_REALTIME_DATA,
        key_pattern="factor:{factor_id}:{date}",
        producer="P2",
        consumers=("P2", "P5"),
        ttl_seconds=300,
        structure="Hash",
        purpose="因子值缓存",
    ),
    NamespaceSpec(
        name="position",
        layer=LAYER_STATE_COORDINATION,
        key_pattern="position:{account}",
        producer="P3",
        consumers=("P2", "P3"),
        ttl_seconds=None,
        structure="Hash",
        purpose="实时持仓",
    ),
    NamespaceSpec(
        name="order",
        layer=LAYER_STATE_COORDINATION,
        key_pattern="order:{order_id}",
        producer="P3",
        consumers=("P3", "P4"),
        ttl_seconds=None,
        structure="Hash",
        purpose="订单状态",
    ),
    NamespaceSpec(
        name="strategy",
        layer=LAYER_STATE_COORDINATION,
        key_pattern="strategy:{strategy_id}:state",
        producer="P2",
        consumers=("P3", "P4"),
        ttl_seconds=None,
        structure="Hash",
        purpose="策略状态机",
    ),
    NamespaceSpec(
        name="market_state",
        layer=LAYER_REALTIME_DATA,
        key_pattern="market:state:current",
        producer="P2",
        consumers=("P2", "P3"),
        ttl_seconds=None,
        structure="String",
        purpose="当前市场状态",
    ),
    NamespaceSpec(
        name="hb",
        layer=LAYER_STATE_COORDINATION,
        key_pattern="hb:{process_name}",
        producer="各进程",
        consumers=("P4",),
        ttl_seconds=None,
        structure="String(+EX)",
        purpose="进程心跳",
        dynamic_ttl=lambda process_timeout_s: process_timeout_s + _HB_TTL_BUFFER_SECONDS,
    ),
    NamespaceSpec(
        name="cmd",
        layer=LAYER_OPS_CONTROL,
        key_pattern="cmd:{target_process}",
        producer="P4",
        consumers=("目标进程",),
        ttl_seconds=60,
        structure="List",
        purpose="运维命令通道",
    ),
    NamespaceSpec(
        name="alert",
        layer=LAYER_OPS_CONTROL,
        key_pattern="alert:{level}:{id}",
        producer="P4",
        consumers=("P4", "通知"),
        ttl_seconds=3600,
        structure="Hash",
        purpose="告警记录",
    ),
    NamespaceSpec(
        name="config",
        layer=LAYER_OPS_CONTROL,
        key_pattern="config:{module}",
        producer="P4",
        consumers=("各进程",),
        ttl_seconds=None,
        structure="Hash",
        purpose="运行时配置",
    ),
    NamespaceSpec(
        name="degrade",
        layer=LAYER_OPS_CONTROL,
        key_pattern="degrade:level",
        producer="P4",
        consumers=("各进程",),
        ttl_seconds=None,
        structure="String",
        purpose="当前降级等级",
    ),
    NamespaceSpec(
        name="gpu",
        layer=LAYER_OPS_CONTROL,
        key_pattern="gpu:allocation",
        producer="P5",
        consumers=("P4", "P5"),
        ttl_seconds=None,
        structure="Hash",
        purpose="GPU资源分配表",
    ),
)

# TTL 矩阵（A9 §1.2：tick=5s, signal=60s, factor=300s, 其余永不过期；
# hb 按进程动态计算不入静态矩阵）
NAMESPACE_TTL_MATRIX: Final[dict[str, int | None]] = {spec.name: spec.ttl_seconds for spec in REDIS_NAMESPACE_REGISTRY}

REDIS_PERSISTENCE_PROFILE: Final[PersistenceProfile] = PersistenceProfile(
    rdb_save_rules=(("3600", "1"),),  # RDB 每小时基线
    aof_enabled=True,
    aof_fsync="everysec",
    maxmemory_gb=8,
    maxmemory_policy="volatile-ttl",
    recovery_strategy="aof_first_hybrid",
    recovery_target_seconds=15,
)

_REGISTRY_BY_NAME: Final[dict[str, NamespaceSpec]] = {spec.name: spec for spec in REDIS_NAMESPACE_REGISTRY}

# Key 首段 → 命名空间名（market_state 的 Key 首段是 market，特判）
_KEY_PREFIX_TO_NAMESPACE: Final[dict[str, str]] = {
    "tick": "tick",
    "signal": "signal",
    "factor": "factor",
    "position": "position",
    "order": "order",
    "strategy": "strategy",
    "market": "market_state",
    "hb": "hb",
    "cmd": "cmd",
    "alert": "alert",
    "config": "config",
    "degrade": "degrade",
    "gpu": "gpu",
}


def get_namespace(name: str) -> NamespaceSpec:
    """按名取命名空间声明；未知命名空间 Fail-Closed。"""
    spec = _REGISTRY_BY_NAME.get(name)
    if spec is None:
        raise RedisStateLayerSotError(f"未知 Redis 命名空间: {name!r}（13 命名空间真源=A9 §1.2，禁止临时发明）")
    return spec


def ttl_for(name: str) -> int | None:
    """命名空间静态 TTL（秒）；None=永不过期；未知命名空间 Fail-Closed。"""
    return get_namespace(name).ttl_seconds


def validate_key(key: str) -> str:
    """校验 Key 属于已登记命名空间，返回命名空间名；未知/畸形 Fail-Closed。"""
    if not key or ":" not in key:
        raise RedisStateLayerSotError(f"Redis Key 畸形（缺命名空间分隔符）: {key!r}")
    prefix = key.split(":", 1)[0]
    namespace = _KEY_PREFIX_TO_NAMESPACE.get(prefix)
    if namespace is None:
        raise RedisStateLayerSotError(f"Redis Key 命中未登记命名空间: {key!r}（13 命名空间真源=A9 §1.2）")
    return namespace


def render_redis_conf_draft() -> str:
    """产出 redis.conf 配置就绪件草稿文本（仅文本，不执行任何系统写入）。

    硬边界：实际应用（写 redis.conf / CONFIG SET / 重启 Redis 服务）属 Owner 窗口。
    """
    p = REDIS_PERSISTENCE_PROFILE
    save_lines = "\n".join(f"save {seconds} {changes}" for seconds, changes in p.rdb_save_rules)
    return (
        "# ============================================================\n"
        "# ZephyrAlpha Redis 7.x 单实例配置就绪件草稿（MOD-INF-063 生成）\n"
        "# 真源: A9 运维架构 §1.2 | 仅供 Owner 窗口审阅应用，AI 不执行系统写入\n"
        "# ============================================================\n"
        "# --- 混合持久化: RDB 每小时基线 + AOF everysec 增量（交易时段） ---\n"
        f"{save_lines}\n"
        f"appendonly {'yes' if p.aof_enabled else 'no'}\n"
        f"appendfsync {p.aof_fsync}\n"
        "aof-use-rdb-preamble yes  # 混合持久化：AOF 重放优先+RDB 基线加速（<15s）\n"
        "# --- 内存硬限与淘汰 ---\n"
        f"maxmemory {p.maxmemory_gb}gb\n"
        f"maxmemory-policy {p.maxmemory_policy}\n"
    )


def recovery_runbook() -> list[str]:
    """AOF 重放优先混合恢复 runbook 步骤（声明；演练执行属 Owner 窗口）。"""
    p = REDIS_PERSISTENCE_PROFILE
    return [
        "1. 确认 Redis 进程停止；备份 data 目录现有 appendonlydir 与 dump.rdb（保命面先保现场）",
        "2. 校验 AOF 完整性：redis-check-aof --fix 仅在截断损坏时使用（修复动作属 Owner 窗口）",
        "3. 以混合持久化配置启动：AOF 重放优先（aof-use-rdb-preamble yes，RDB 基线内嵌加速）",
        f"4. 恢复耗时核验：目标 <{p.recovery_target_seconds}s（纯 AOF ~3min → 混合 <15s），超时升级",
        "5. 一致性校验：position:*/order:*/strategy:* 键抽样比对最近审计快照，hb:* 待各进程自然重建",
        "6. 恢复完成后启动五进程 Supervisor（P1→P3→P2→P4→P5 升序），P3 恢复前禁接单",
    ]


def check_registry_consistency() -> dict[str, object]:
    """注册表一致性自检：13 命名空间/三层归属合法/TTL 矩阵完整/Key 前缀无冲突。"""
    issues: list[str] = []
    names = [spec.name for spec in REDIS_NAMESPACE_REGISTRY]
    if len(names) != 13:
        issues.append(f"命名空间数量 {len(names)} != 13")
    if len(set(names)) != len(names):
        issues.append("命名空间重名")
    for spec in REDIS_NAMESPACE_REGISTRY:
        if spec.layer not in _VALID_LAYERS:
            issues.append(f"{spec.name} 层归属非法: {spec.layer}")
        if spec.name not in NAMESPACE_TTL_MATRIX:
            issues.append(f"{spec.name} 缺 TTL 矩阵项")
        if spec.name == "hb" and spec.dynamic_ttl is None:
            issues.append("hb 缺 dynamic_ttl（超时阈值+30s 缓冲）")
    prefixes = [spec.key_pattern.split(":", 1)[0] for spec in REDIS_NAMESPACE_REGISTRY]
    # market_state 与 market:* 首段唯一映射；其余首段不得碰撞
    if len(set(prefixes)) != len(prefixes):
        issues.append("Key 前缀碰撞")
    return {
        "ok": not issues,
        "namespace_count": len(names),
        "issues": issues,
    }
