# [A_module] module_id=MOD-INT_timestamp_utils | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.timestamp_utils
# [INVARIANTS] 所有时间戳强制UTC;Timestamp类型别名统一为pd.Timestamp
# [MODIFY-GUARD] zephyr.integration.shared_08.contracts.core.timestamp
# [CONSUMERS] zephyr.integration.shared_08.contracts.core.timestamp
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError on missing pandas
# [TESTS]
from datetime import datetime

import pandas as pd

Timestamp = pd.Timestamp


class NaiveDatetimeError(ValueError):
    pass


def utcnow() -> Timestamp:
    return pd.Timestamp.now(tz="UTC")


def ensure_utc(ts: Timestamp | datetime | str | int | float) -> Timestamp:
    if isinstance(ts, datetime) and not isinstance(ts, pd.Timestamp):
        if ts.tzinfo is None:
            raise NaiveDatetimeError(
                f"datetime 对象必须 tz-aware，收到 naive datetime: {ts!r}。"
                " 请使用 ensure_utc(datetime.now(tz=timezone.utc)) 或明确指定时区。"
            )
        return pd.Timestamp(ts).tz_convert("UTC")

    if isinstance(ts, str):
        parsed = pd.Timestamp(ts)
        if parsed.tz is None:
            raise NaiveDatetimeError(
                f"ISO 字符串必须包含时区信息，收到无时区字符串: {ts!r}。"
                " 正确格式示例：'2026-04-18T10:30:00+08:00' 或 '2026-04-18T02:30:00Z'。"
            )
        return parsed.tz_convert("UTC")

    if isinstance(ts, (int, float)):
        return pd.Timestamp(ts, unit="s", tz="UTC")

    if isinstance(ts, pd.Timestamp):
        if ts.tz is None:
            import warnings

            warnings.warn(
                f"收到 naive pd.Timestamp: {ts!r}，已按 UTC 补全时区。请在调用方显式附加时区，避免时区歧义。",
                stacklevel=2,
            )
            return ts.tz_localize("UTC")
        return ts.tz_convert("UTC")

    raise TypeError(
        f"ensure_utc 不支持的输入类型 {type(ts).__name__}: {ts!r}。"
        " 支持的类型：pd.Timestamp / datetime / str(ISO 8601) / int(Unix 秒) / float。"
    )


def to_local(ts: Timestamp, tz: str) -> Timestamp:
    if ts.tz is None:
        raise NaiveDatetimeError(f"to_local 的输入必须 tz-aware，收到 naive Timestamp: {ts!r}")
    return ts.tz_convert(tz)


def from_unix_ns(ns: int) -> Timestamp:
    return pd.Timestamp(ns, unit="ns", tz="UTC")


__all__ = ["NaiveDatetimeError", "Timestamp", "ensure_utc", "from_unix_ns", "to_local", "utcnow"]
