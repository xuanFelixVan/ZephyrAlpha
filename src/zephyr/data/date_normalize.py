# [MODULE] zephyr.data.date_normalize
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
#       长期资产（两计算核 + 后续任何日期窗口比较点复用），非一次性件——退役须先迁尽调用方
# [STARTUP] imported
#   （原值 lazy：纯函数，无导入副作用；调用方按需 import，不挂任何调度槽）——GATE-VOCAB 词表归正 imported）
# [CONSUMERS] zephyr.data.implementations.consensus_daily_compute（build_consensus_rows
#             窗口/发布日比较键）; zephyr.data.implementations.financial_derived_compute
#             （run_compute announce_date 窗口过滤）; tests/data/test_wave3_date_normalize.py
# [DEPENDENCIES] 仅 stdlib datetime（禁引 CH/DB/第三方）
# [INVARIANTS] 归一唯一口径=ISO 日历日字符串（`YYYY-MM-DD`）：str/date/datetime 三类入参
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [DOMAIN] D_DATA
# [MATURITY] draft
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 外部依赖失败必抛并点名，禁把异常吞成空值/空表（假绿源）
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
#              归一后必须两两可比且同值同序；归一失败必抛（禁静默返回 None/""/原值——
#              失败即数据面污染，让调用方崩在写入口比崩在下游游标便宜）；
#              本模块**不**替代 provider 侧入站报文归一（akshare_provider._norm_date_str 等
#              是"源报文列 → 表列"归一，对象不同，按内收铁律「跨域不同对象→不并」保留）；
#              本模块吸收的是原先散在两个计算核里的内联字符串窗口比较（替代其内联写法）
"""日期窗口比较键归一（波 3.1）——把 ISO 字符串与 date 归一到同一类型后再比较。

病根（实测案卷 dossier_G_business_chain.md 第 7 条 / 02 册 X-40）：
  * `consensus_daily_build` FAILED 2026-09-18T22:30:20Z
    `'>' not supported between instances of 'str' and 'datetime.date'`
  * `financial_derived_build` FAILED 2026-09-25T21:32:12Z（5 次尝试）
    `'<' not supported between instances of 'str' and 'datetime.date'`
两处都是"窗口边界参数（str 或 date 看调用方）"与"行内日期（date 或 str 看源表通道）"
混型直比。归一后两侧同为 ISO 日字符串，比较结果与类型无关。

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/wave3/date_normalize.yaml

"""

from __future__ import annotations

from datetime import date, datetime
from typing import Final

__all__: Final = ["as_date_obj", "as_iso_day", "in_window", "iso_window_bound"]

_UNBOUNDED = ""  # 沿用两计算核既有"空串=不限"哨兵口径，不另立第二套


def as_iso_day(value: object, *, field: str = "date") -> str:
    """任意日期载体 → ISO 日历日字符串 `YYYY-MM-DD`（比较键唯一真源）。

    Args:
        value: `date` / `datetime` / ISO 字符串（容忍 `T`/空格 时间后缀与 `/` 分隔）
               / 具备 `.date()` 的鸭子对象（pandas Timestamp 等）。
        field: 出错消息里的字段名（点名用，禁吞异常）。

    Raises:
        TypeError: None 或非日期载体（调用方必须知道自己喂了什么）。
        ValueError: 字符串无法按 ISO 解析。
    """
    if value is None:
        raise TypeError(f"{field} 为 None，无法归一为 ISO 日（窗口比较禁 None 静默通过）")
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        s = value.strip().replace("/", "-")
        if not s:
            raise ValueError(f"{field} 为空字符串，无法归一为 ISO 日")
        head = s[:10]
        try:
            return date.fromisoformat(head).isoformat()
        except ValueError as exc:  # 点名原值，禁静默降级
            raise ValueError(f"{field} 非 ISO 日期字符串: {value!r}") from exc
    to_date = getattr(value, "date", None)
    if callable(to_date):
        return as_iso_day(to_date(), field=field)
    raise TypeError(f"{field} 类型 {type(value).__name__} 不支持日期归一")


def as_date_obj(value: object, *, field: str = "date") -> date:
    """任意日期载体 → `datetime.date`（需要做 timedelta 算术时用，比较一律走 as_iso_day）。"""
    return date.fromisoformat(as_iso_day(value, field=field))


def iso_window_bound(value: object, *, field: str = "bound") -> str:
    """窗口边界归一：None → 空串（=不限，沿用调用方既有哨兵），其余同 as_iso_day。"""
    if value is None:
        return _UNBOUNDED
    return as_iso_day(value, field=field)


def in_window(value: object, start: object = None, end: object = None, *, field: str = "date") -> bool:
    """`value` 是否落在闭区间 [start, end]（三端各自可 str 可 date，混型合法）。"""
    day = as_iso_day(value, field=field)
    lo = iso_window_bound(start, field="start")
    hi = iso_window_bound(end, field="end")
    if lo and day < lo:
        return False
    if hi and day > hi:
        return False
    return True
