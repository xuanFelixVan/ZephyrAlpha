# [BLUEPRINT] MOD-H1_REDIS_HOT | docs/03_modules/_cross_layer/database/sub_blueprints/h1_redis_hot.md | §3
# [MODULE] zephyr.infrastructure.h1_redis_hot.h1_redis_schema
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.h1_redis_hot.h1_redis_writer; h1_redis_reader; h1_cqrs_projectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Key 命名全小写+冒号分隔; symbol 遵循 miniQMT 6位代码+交易所后缀; 窄表 Field=factor_name:ver
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/zephyr/infrastructure/h1_redis_hot/test_h1_redis_schema.py
# [A_module] module_id=MOD-H1_REDIS_HOT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# M03豁免: AI趋同演化,非复制粘贴（项目内部标注，非 ruff code）

"""
H1 Redis 热缓存 Key Schema（DDL-as-Code）。

真源：
    - 数据架构.md §11.1.2（在线存储 Online Store）
    - 数据架构.md §12.4.2（CQRS 读端物化视图）
    - h1_redis_hot.md §3（Redis Schema Key 设计）

定义 7 类 Redis Key 的命名规范与构造函数。所有 H1 业务代码（Writer/Reader/Projectors）
MUST 通过本模块的构造函数生成 Key，禁止手写 f"feature:{symbol}" 散落各处——集中管理
避免 Key 漂移（DD-11-01 在线存储一致性）。

Key 命名规范（§3.4）：
    - 全小写 + 冒号分隔：feature:000001.SZ、position:600000.SH
    - symbol 格式遵循 miniQMT 约定（6 位代码 + 交易所后缀）
    - 盘后清理脚本按前缀 scan 批量删除当日临时 Key

容量估算（数据架构.md §7.2，~200MB 明细）：
    因子截面 ~50MB（5000只×200因子×50字节）
    Tick缓存 ~100MB
    持仓/信号/风控 ~5MB
    Redis内部开销 ~45MB

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: symbol 参数
#   fields: 参数 symbol，类型注解 str
#   code: h1_redis_schema.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: factor_name 参数
#   fields: 参数 factor_name，类型注解 str
#   code: h1_redis_schema.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: version 参数
#   fields: 参数 version，类型注解 str
#   code: h1_redis_schema.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① feature_key
#   name_en: feature_key
#   intro: 因子截面 Key：feature:{symbol}
#   desc: 因子截面 Key：feature:{symbol} 数据结构：Hash Field：{factor_name}:{ver}（窄表理念 DD-P3-01，新增因子不改 Key 结构…；源码 L168-L180
#   inputs: symbol
#   outputs: str
# - id: A2
#   name_zh: ② factor_field
#   name_en: factor_field
#   intro: 因子 Hash Field：{factor_name}:{version}
#   desc: 因子 Hash Field：{factor_name}:{version} 窄表理念（DD-P3-01）：Field 含因子名+版本，新增因子不改 Key 结构。 Example…；源码 L183-L192
#   inputs: factor_name version
#   outputs: str
# - id: A3
#   name_zh: ③ feature_updated_at_field
#   name_en: feature_updated_at_field
#   intro: 因子截面 Hash 的 updated_at 元数据 Field 名。
#   desc: 因子截面 Hash 的 updated_at 元数据 Field 名。 与 factor_field（{factor_name}:{version}）区分：下划线前缀避免与任何因…；源码 L203-L216
#   inputs: 无参数
#   outputs: str
# - id: A4
#   name_zh: ④ position_key
#   name_en: position_key
#   intro: 当前持仓 Key：position:{symbol}
#   desc: 当前持仓 Key：position:{symbol} 数据结构：Hash（amount/cost/avg_price/updated_at） 更新频率：实时（OrderFille…；源码 L224-L234
#   inputs: symbol
#   outputs: str
# - id: A5
#   name_zh: ⑤ signal_active_key
#   name_en: signal_active_key
#   intro: 活跃信号 Key：signal:active
#   desc: 活跃信号 Key：signal:active 数据结构：Set（活跃信号 symbol 集合）+ Hash（信号详情） 更新频率：实时（SignalEvent） 查询延迟：<5ms；源码 L237-L244
#   inputs: 无参数
#   outputs: str
# - id: A6
#   name_zh: ⑥ trade_today_key
#   name_en: trade_today_key
#   intro: 当日交易 Key：trade:today:{symbol}
#   desc: 当日交易 Key：trade:today:{symbol} 数据结构：List（当日成交记录） 更新频率：实时（ExecutionEvent） 查询延迟：<5ms 盘后清理：盘后…；源码 L247-L255
#   inputs: symbol
#   outputs: str
# - id: A7
#   name_zh: ⑦ risk_status_key
#   name_en: risk_status_key
#   intro: 风控状态 Key：risk:status
#   desc: 风控状态 Key：risk:status 数据结构：Hash（level/rule_id/updated_at） 更新频率：实时（RiskEvent） 查询延迟：<5ms；源码 L258-L265
#   inputs: 无参数
#   outputs: str
# - id: A8
#   name_zh: ⑧ account_summary_key
#   name_en: account_summary_key
#   intro: 账户状态 Key：account:summary
#   desc: 账户状态 Key：account:summary 数据结构：Hash（total_asset/cash/available/updated_at） 更新频率：实时 查询延迟：<5…；源码 L268-L276
#   inputs: 无参数
#   outputs: str
# - id: A9
#   name_zh: ⑨ tick_latest_key
#   name_en: tick_latest_key
#   intro: 盘中最新 tick Key：tick:{symbol}:latest
#   desc: 盘中最新 tick Key：tick:{symbol}:latest 数据结构：Hash（price/volume/bid1-5/ask1-5） TTL：盘中无 TTL / 盘后…；源码 L284-L293
#   inputs: symbol
#   outputs: str
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.h1_redis_hot.h1_redis_writer; h1_redis_reader; h1_cqrs_pr…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> A9
# A9 --> O1
"""

from __future__ import annotations

from typing import Final

# ============================================================================
# Key 前缀（全小写 + 冒号分隔，§3.4 命名规范）
# ============================================================================

# §3.1 因子截面（在线存储，DD-11-01）
PREFIX_FEATURE: Final[str] = "feature"
# §3.2 CQRS 读端物化视图（事件投影，DD-12-05）
PREFIX_POSITION: Final[str] = "position"  # 当前持仓
PREFIX_SIGNAL: Final[str] = "signal"  # 活跃信号
PREFIX_TRADE: Final[str] = "trade"  # 当日交易
PREFIX_RISK: Final[str] = "risk"  # 风控状态
PREFIX_ACCOUNT: Final[str] = "account"  # 账户状态
# §3.3 Tick 缓存
PREFIX_TICK: Final[str] = "tick"


# ============================================================================
# §3.1 因子截面 Key（在线存储）
# ============================================================================


def feature_key(symbol: str) -> str:
    """因子截面 Key：feature:{symbol}

    数据结构：Hash
    Field：{factor_name}:{ver}（窄表理念 DD-P3-01，新增因子不改 Key 结构）
    Value：{factor_value} (float)
    TTL：盘中无 TTL / 盘后 3600s

    Example:
        >>> feature_key("000001.SZ")
        'feature:000001.SZ'
    """
    return f"{PREFIX_FEATURE}:{symbol}"


def factor_field(factor_name: str, version: str = "v1") -> str:
    """因子 Hash Field：{factor_name}:{version}

    窄表理念（DD-P3-01）：Field 含因子名+版本，新增因子不改 Key 结构。

    Example:
        >>> factor_field("momentum_20d", "v2")
        'momentum_20d:v2'
    """
    return f"{factor_name}:{version}"


# §3.1 元数据 Field（非因子，下划线前缀避免与 factor_name:version 冲突）
# 治本 CP-02 过期检测（2026-08-03 实地演练发现）：
# 原方案仅靠 TTL/不存在判定新鲜度——Redis 故障期间 feature:* 冻结但仍可读，
# 消费者无法区分"新鲜数据"vs"故障冻结数据"。Writer 写入时戳 updated_at，
# 消费者读 time.time() - updated_at 判定时效（>阈值标 expired，触发降级）。
FEATURE_FIELD_UPDATED_AT: Final[str] = "_updated_at"


def feature_updated_at_field() -> str:
    """因子截面 Hash 的 updated_at 元数据 Field 名。

    与 factor_field（{factor_name}:{version}）区分：下划线前缀避免与任何因子名冲突。
    Value: repr(time.time()) → epoch 秒（float 字符串），消费者 float() 反序列化。

    用途：CP-02 优雅降级——Redis 故障期间 feature:* 冻结但可读，
    消费者读 updated_at 判定新鲜度（now - updated_at > 阈值 → 标记 expired）。

    Example:
        >>> feature_updated_at_field()
        '_updated_at'
    """
    return FEATURE_FIELD_UPDATED_AT


# ============================================================================
# §3.2 CQRS 读端物化视图 Key
# ============================================================================


def position_key(symbol: str) -> str:
    """当前持仓 Key：position:{symbol}

    数据结构：Hash（amount/cost/avg_price/updated_at）
    更新频率：实时（OrderFilled 事件）
    查询延迟：<5ms
    容量：~5MB

    投影逻辑：数据架构.md §12.4.2 PositionProjector
    """
    return f"{PREFIX_POSITION}:{symbol}"


def signal_active_key() -> str:
    """活跃信号 Key：signal:active

    数据结构：Set（活跃信号 symbol 集合）+ Hash（信号详情）
    更新频率：实时（SignalEvent）
    查询延迟：<5ms
    """
    return f"{PREFIX_SIGNAL}:active"


def trade_today_key(symbol: str) -> str:
    """当日交易 Key：trade:today:{symbol}

    数据结构：List（当日成交记录）
    更新频率：实时（ExecutionEvent）
    查询延迟：<5ms
    盘后清理：盘后清空（§7.3 生命周期）
    """
    return f"{PREFIX_TRADE}:today:{symbol}"


def risk_status_key() -> str:
    """风控状态 Key：risk:status

    数据结构：Hash（level/rule_id/updated_at）
    更新频率：实时（RiskEvent）
    查询延迟：<5ms
    """
    return f"{PREFIX_RISK}:status"


def account_summary_key() -> str:
    """账户状态 Key：account:summary

    数据结构：Hash（total_asset/cash/available/updated_at）
    更新频率：实时
    查询延迟：<5ms
    盘后清理：盘后清空（§7.3 生命周期，敏感数据最小留存）
    """
    return f"{PREFIX_ACCOUNT}:summary"


# ============================================================================
# §3.3 Tick 缓存 Key
# ============================================================================


def tick_latest_key(symbol: str) -> str:
    """盘中最新 tick Key：tick:{symbol}:latest

    数据结构：Hash（price/volume/bid1-5/ask1-5）
    TTL：盘中无 TTL / 盘后即清
    容量：~100MB

    用途：D-DATA (miniQMT) 盘中 tick 缓存，决策引擎快速取最新价
    """
    return f"{PREFIX_TICK}:{symbol}:latest"


# ============================================================================
# TTL 策略（数据架构.md §7.1/§11.1）
# ============================================================================

# 盘中无 TTL（交易日 09:30-15:00 因子截面常驻）
# 盘后切换冷数据 TTL（15:30 后 feature Key 设 3600s 兜底，盘后清理脚本按前缀 scan 删除）
TTL_POST_MARKET_SECONDS: Final[int] = 3600

# Tick 缓存盘后即清（不留 TTL，盘后清理脚本直接删）
TTL_TICK_POST_MARKET_SECONDS: Final[int] = 0


# ============================================================================
# 容量估算（数据架构.md §7.2，~200MB 明细）
# ============================================================================

MEMORY_ESTIMATE_FACTOR_MB: Final[int] = 50  # 5000只×200因子×50字节
MEMORY_ESTIMATE_TICK_MB: Final[int] = 100
MEMORY_ESTIMATE_POSITION_SIGNAL_RISK_MB: Final[int] = 5
MEMORY_ESTIMATE_REDIS_OVERHEAD_MB: Final[int] = 45
MEMORY_ESTIMATE_TOTAL_MB: Final[int] = (
    MEMORY_ESTIMATE_FACTOR_MB
    + MEMORY_ESTIMATE_TICK_MB
    + MEMORY_ESTIMATE_POSITION_SIGNAL_RISK_MB
    + MEMORY_ESTIMATE_REDIS_OVERHEAD_MB
)  # = 200

# maxmemory 上限（蓝图 §8.1 定 2gb；实际 VM 内存 9.2GB，部署时调整为 1gb 留余量给 CH）
MAXMEMORY_LIMIT: Final[str] = "1gb"

# 扩展触发（数据架构.md §7.2：maxmemory 使用率>70% 触发淘汰/告警）
MAXMEMORY_EXPANSION_TRIGGER_RATIO: Final[float] = 0.70


# ============================================================================
# 盘后清理前缀（§3.4：盘后清理脚本按前缀 scan 批量删除当日临时 Key）
# ============================================================================

# 盘后清理的 Key 前缀（feature 保留 3600s TTL 兜底，其余直接删）
POST_MARKET_CLEANUP_PREFIXES: Final[tuple[str, ...]] = (
    PREFIX_TICK,  # tick 缓存盘后即清
    PREFIX_TRADE,  # 当日交易盘后清空（敏感数据）
    PREFIX_ACCOUNT,  # 账户状态盘后清空（敏感数据）
    PREFIX_SIGNAL,  # 活跃信号盘后清空
)
