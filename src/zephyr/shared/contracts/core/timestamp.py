# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.timestamp
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] infrastructure_runtime_integration.system_telemetry.health_aggregator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_timestamp | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ZephyrAlpha — shared/contracts/timestamp.py

统一时间戳契约（Unified Timestamp Contract）。

🔒 **锁定文件（Immutable Core）**：任何修改必须先建 KB 决策记录并经人工批准。

═══════════════════════════════════════════════════════════════════════
【设计目标】
═══════════════════════════════════════════════════════════════════════
1. **所有时间戳存储强制 UTC**（展示时再转本地时区）
2. **精度统一纳秒**（`numpy.datetime64[ns]` 或 `pandas.Timestamp`），
   低精度场景天然兼容（秒/毫秒/微秒），高频场景直接支持（HFT 纳秒）
3. **禁止 naive datetime 进入系统**（无 tzinfo 的 datetime 必须被拦截）
4. **提供统一类型别名 Timestamp**（即 `pd.Timestamp`），全公司签名统一

**为什么选 pandas.Timestamp 而非 numpy.datetime64 或 stdlib datetime？**
  - pandas.Timestamp 兼容 numpy.datetime64[ns] 精度，且支持时区（numpy 不支持 tz）
  - 大量使用 pandas 的量化生态（DataFrame 索引、resample、rolling 等）原生匹配
  - stdlib datetime 最低支持微秒（μs），不够 HFT 纳秒级
  - 跨时区运算 pd.Timestamp 原生支持

**与 OQ-071 的关系**：
  本文件够满足首批 3 铁板契约落地。更复杂的时间工具（market_session / trading_calendar）
  延后（见 OQ-071 P0 待锁清单）。

参见：
  - pandas Timestamp 官方文档：https://pandas.pydata.org/docs/reference/api/pandas.Timestamp.html
  - ISO 8601 时间格式标准
  - Python stdlib zoneinfo（PEP 615）
═══════════════════════════════════════════════════════════════════════
"""

from datetime import datetime

import pandas as pd
from zephyr.shared.utils.time_utils import now_utc

# ═══════════════════════════════════════════════════════════════════
# 统一类型别名
# ═══════════════════════════════════════════════════════════════════

Timestamp = pd.Timestamp
"""
全公司统一时间戳类型。

**所有函数签名中的时间戳参数必须使用 `Timestamp`**，而非 `datetime` 或 `pd.Timestamp`。

示例（Fitness Function 会扫描签名违规）：

  ✅ 正确：
    def process(ts: Timestamp, data: pd.DataFrame) -> None: ...

  ❌ 错误（会被 Fitness Function F-timestamp-type 拦截）：
    def process(ts: datetime, data: pd.DataFrame) -> None: ...
    def process(ts: "pandas.Timestamp", data: pd.DataFrame) -> None: ...  # 使用原名而非别名
"""

# ═══════════════════════════════════════════════════════════════════
# 异常类
# ═══════════════════════════════════════════════════════════════════


class NaiveDatetimeError(ValueError):
    """
    试图使用 naive datetime（无 tzinfo）时抛出。

    所有进入 ZephyrAlpha 系统的时间戳**必须 tz-aware**。
    """
    error_code = "ZA-SH-0023"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


# ═══════════════════════════════════════════════════════════════════
# 工厂函数
# ═══════════════════════════════════════════════════════════════════


def utcnow() -> Timestamp:
    """
    获取当前 UTC 时间（纳秒精度，tz-aware）。

    **全公司唯一获取"当前时间"的方式**。
    禁止使用 `now_utc()`（naive，无时区）或 `now_utc()`（naive，已被 Python 官方 deprecated）。

    Fitness Function 会扫描所有代码文件，违规调用会被拦截。

    示例：
        >>> ts = utcnow()
        >>> ts.tz is not None
        True
        >>> str(ts.tz)
        'UTC'
    """
    return pd.Timestamp.now(tz="UTC")


def ensure_utc(ts: Timestamp | datetime | str | int | float) -> Timestamp:
    """
    将任意合法时间输入转为 UTC tz-aware Timestamp。

    **所有外部时间戳（从 API、数据库、CSV、用户输入）进入系统时必须经本函数清洗**。

    支持的输入：
      - `Timestamp`（pd.Timestamp）：若 naive，假定为 UTC 并附加时区；若 tz-aware，转为 UTC
      - `datetime`：若 naive，拒绝（抛 NaiveDatetimeError）；若 tz-aware，转为 UTC
      - `str`：ISO 8601 格式字符串，若无时区信息则拒绝
      - `int` / `float`：Unix 时间戳（秒），假定为 UTC

    **拒绝 naive datetime 是故意的**：强制所有输入必须明确时区，防止"以为是北京时间结果是 UTC"的灾难性错误。

    示例：
        >>> ensure_utc("2026-04-18T10:30:00+08:00")  # 东八区 -> UTC
        Timestamp('2026-04-18 02:30:00+0000', tz='UTC')

        >>> ensure_utc(now_utc())  # 抛 NaiveDatetimeError
        NaiveDatetimeError: datetime 对象必须 tz-aware...

        >>> ensure_utc(1713427200)  # Unix 秒时间戳
        Timestamp('2024-04-18 08:00:00+0000', tz='UTC')
    """
    # datetime 类型：检查时区
    if isinstance(ts, datetime) and not isinstance(ts, pd.Timestamp):
        if ts.tzinfo is None:
            raise NaiveDatetimeError(
                f"datetime 对象必须 tz-aware，收到 naive datetime: {ts!r}。"
                " 请使用 ensure_utc(datetime.now(tz=timezone.utc)) 或明确指定时区。"
            )
        return pd.Timestamp(ts).tz_convert("UTC")

    # 字符串：交给 pd.Timestamp 解析，但后续检查时区
    if isinstance(ts, str):
        parsed = pd.Timestamp(ts)
        if parsed.tz is None:
            raise NaiveDatetimeError(
                f"ISO 字符串必须包含时区信息，收到无时区字符串: {ts!r}。"
                " 正确格式示例：'2026-04-18T10:30:00+08:00' 或 '2026-04-18T02:30:00Z'。"
            )
        return parsed.tz_convert("UTC")

    # 数字（Unix 时间戳）：假定为 UTC 秒
    if isinstance(ts, (int, float)):
        return pd.Timestamp(ts, unit="s", tz="UTC")

    # pd.Timestamp：检查 tz，缺失则按 UTC 附加
    if isinstance(ts, pd.Timestamp):
        if ts.tz is None:
            # pandas 允许 naive Timestamp，但系统禁止；这里按 UTC 补全并告警
            import warnings

            warnings.warn(
                f"收到 naive pd.Timestamp: {ts!r}，已按 UTC 补全时区。 请在调用方显式附加时区，避免时区歧义。",
                stacklevel=2,
            )
            return ts.tz_localize("UTC")
        return ts.tz_convert("UTC")

    raise TypeError(
        f"ensure_utc 不支持的输入类型 {type(ts).__name__}: {ts!r}。"
        " 支持的类型：pd.Timestamp / datetime / str(ISO 8601) / int(Unix 秒) / float。"
    )


# ═══════════════════════════════════════════════════════════════════
# 便捷工具（可选使用）
# ═══════════════════════════════════════════════════════════════════


def to_local(ts: Timestamp, tz: str) -> Timestamp:
    """
    将 UTC Timestamp 转为本地时区（仅用于展示，不用于存储）。

    示例：
        >>> utc_ts = utcnow()
        >>> to_local(utc_ts, "Asia/Shanghai")  # 北京时间
        >>> to_local(utc_ts, "America/New_York")  # 纽约时间
    """
    if ts.tz is None:
        raise NaiveDatetimeError(f"to_local 的输入必须 tz-aware，收到 naive Timestamp: {ts!r}")
    return ts.tz_convert(tz)


def from_unix_ns(ns: int) -> Timestamp:
    """
    从 Unix 纳秒时间戳构造（HFT / 高频行情常用）。

    示例：
        >>> from_unix_ns(1713427200_000_000_000)
        Timestamp('2024-04-18 08:00:00+0000', tz='UTC')
    """
    return pd.Timestamp(ns, unit="ns", tz="UTC")
