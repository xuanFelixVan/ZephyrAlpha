# [MODULE] zephyr.data.dual_source_guard
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
# [STARTUP] imported
#   （原值 lazy：纯函数，无 IO 无副作用；不挂调度槽，由宿主检查族调用）——GATE-VOCAB 词表归正 imported）
# [CONSUMERS] zephyr.data.consensus_crosscheck（族 1 双源对账，已接线）;
#             待接线（越出本包写域，见本册"缺口"）: zephyr.trading.recon_runner
#             （reconciliation_differences 双源）; score 族宿主（未定位，禁臆指）;
#             tests/data/test_wave3_dual_source_guard.py
# [DEPENDENCIES] 仅 stdlib（禁引 DB/CH——读失败判定由调用方以 raw 载体交进来）
# [INVARIANTS] 三条铁律，任何宿主不得绕过：
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
#              ①读数通道失败（raw is None / probe_ok=False）≠ 零行：必判 read_unavailable；
#              ②双源皆空 ≠ 干净：永不返回 "clean"，只返回 both_empty（宿主必须走红）；
#              ③一源有行另一源空 = one_sided（红），禁按"覆盖差异"降级为 warn；
#              本件不产生告警、不落库、不查 DB——只出判据，避免与宿主抢真源
"""双源（pair-of-sources）判据收敛件（波 3.6）——"空即干净"是假绿的母体。

在册病根（00 册 W-36 / 02 册 X-40）：`reconciliation_differences` 两库皆空
（DuckDB governance.db 与 `c1_market.reconciliation_differences` 各一）被读成
"无差异=干净"；同律病灶在 consensus 双源对账与 score 族。三处共用本件，禁各抄一份。

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/wave3/dual_source_guard.yaml

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

__all__: Final = ["classify_source_pair", "pair_status", "SourceReading", "SOURCE_PAIR_RED"]

#: 非绿状态集合（宿主判 "status in SOURCE_PAIR_RED" 即必红，禁自行放宽）
SOURCE_PAIR_RED = frozenset({"read_unavailable", "both_empty", "one_sided"})

_STATUS: Final = {
    "paired": "ok",
    "read_unavailable": "read_unavailable",
    "both_empty": "both_empty",
    "one_sided": "one_sided",
}


def _readable(raw: Any, probe_ok: bool | None) -> bool:  # noqa: any-abuse  raw为TSV文本/None/哨兵三态判存活性(W-180通道证据),参差类型系判据本体非注型债
    """通道是否真的读成功：显式 probe_ok 优先，否则以 raw is not None 判（CH reader 失败=None）。"""
    if probe_ok is not None:
        return bool(probe_ok)
    return raw is not None


def pair_status(a_rows: int, b_rows: int, *, a_ok: bool, b_ok: bool) -> str:
    """纯判定：返回 paired / read_unavailable / both_empty / one_sided（键无关命名）。"""
    if not a_ok or not b_ok:
        return _STATUS["read_unavailable"]
    if a_rows == 0 and b_rows == 0:
        return _STATUS["both_empty"]
    if (a_rows == 0) != (b_rows == 0):
        return _STATUS["one_sided"]
    return _STATUS["paired"]


@dataclass(frozen=True)
class SourceReading:
    """单源读数参数对象（NO-LONG-PARAM-LIST 整改：classify_source_pair 8 参收口为 2 参）。

    raw/probe_ok: 通道存活证据；probe_ok 给了以显式为准，否则以 `raw is not None` 判
    （W-180：`query()` 返回 None=失败，不是空表）。
    """

    name: str
    rows: int
    raw: Any = "__unset__"
    probe_ok: bool | None = None


def classify_source_pair(a: SourceReading, b: SourceReading) -> dict[str, Any]:
    """双源读数 → 判据 dict（status/detail/counts），红态一律非 "ok"，永不返回 "clean"。

    Args:
        a/b: 两源读数（name 进 detail，禁"某源为空"这类无名指控；rows 调用方负责
            只计真实业务行）。

    Returns:
        {"status": "ok"|"read_unavailable"|"both_empty"|"one_sided",
         "clean": False|True, "detail": str, "a_rows": int, "b_rows": int}
    """
    a_ok = _readable(a.raw, a.probe_ok)
    b_ok = _readable(b.raw, b.probe_ok)
    status = pair_status(a.rows, b.rows, a_ok=a_ok, b_ok=b_ok)
    if status == "read_unavailable":
        dead = [n for n, ok in ((a.name, a_ok), (b.name, b_ok)) if not ok]
        detail = f"读数通道失败源={dead}（禁把读失败当零行；a_rows={a.rows} b_rows={b.rows}）"
    elif status == "both_empty":
        detail = f"双源皆空 a={a.name}:0 b={b.name}:0 —— 空≠干净，须查供数链路后人工定性"
    elif status == "one_sided":
        detail = f"单侧空 a={a.name}:{a.rows} b={b.name}:{b.rows} —— 一源有行一源空即真源分裂"
    else:
        detail = f"双源皆有行 a={a.name}:{a.rows} b={b.name}:{b.rows}"
    return {
        "status": status,
        "clean": status == _STATUS["paired"],
        "detail": detail,
        "a_rows": a.rows,
        "b_rows": b.rows,
    }
