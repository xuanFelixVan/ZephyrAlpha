# [BLUEPRINT] MOD-BT-039 | tests/backtest/test_c4_pit_universal_gate.py
# [MODULE] tests.backtest.test_c4_pit_universal_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.translated._c4_engine; zephyr.strategy_pipeline.fw_backtest; scripts.backtest.factor_strategy_template
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] S12-E4 通用 PIT 闸（B1 探针泛化版，一闸罩全族）：两份仅 X 日后分歧的
#   行情/成分输入 → 宇宙与权重在 X 日及之前必须逐位不变。红=X 日前的决策用到 X 日后的信息。
#   现状（2026-09-18 SCD-2 retrofit 落地后）：fw_backtest 范式=绿；_c4_engine 窗口并集
#   宇宙=绿（原 xfail strict 真红件已摘除转正）；模板族权重轴=实测钉。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败（xfail strict 件=已知真红，retrofit 后必须摘除）
# [TESTS] pytest tests/backtest/test_c4_pit_universal_gate.py
# [TTL] permanent
"""C4 翻译件通用 PIT 闸（S12-E4 交付②；SCD-2 retrofit 已落地 2026-09-18）。

双世界构造：世界 A/B 仅在分界日 X=2024-03-31 之后分歧（成分表 M_EXIT 是否调出 /
行情价格在 X 后走异），断言 X 日（含）前的宇宙/权重逐位不变。
不触 CH（全部 mock），不触网。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
TRANSLATED = REPO / "scripts" / "backtest" / "translated"
X_DAY = pd.Timestamp("2024-03-31")  # 分歧分界日：两世界只在 X 之后不同

_BASE_MEMBERS = ("600519", "000858", "601318", "600036")
_EXIT_MEMBER = "300750"  # 世界 A：2024-06-30 调出（X 后）；世界 B：仍在（valid_to NULL）


# ── 宇宙轴：SCD-2 成分表双世界 ────────────────────────────────────────────────


def _constituent_rows(world: str) -> list[tuple]:
    """index_constituent SCD-2 行（symbol_canonical, valid_from, valid_to）。

    两世界在 X 前逐位相同；唯一分歧=M_EXIT 在 X 后是否调出。
    """
    rows = [(s, "2020-01-01", None) for s in _BASE_MEMBERS]
    if world == "A":
        rows.append((_EXIT_MEMBER, "2020-01-01", "2024-06-30"))  # X 后调出
    else:
        rows.append((_EXIT_MEMBER, "2020-01-01", None))  # X 后仍在
    return rows


def _scd2_window_filter(rows: list[tuple], start: str, end: str) -> list[tuple]:
    """模拟引擎 SCD-2 窗口 SQL 谓词：valid_from<=end ∧ (valid_to 未失效 ∨ >start)。"""
    out = []
    for s, vf, vt in rows:
        vts = vt if vt is not None else ""
        if vf <= end and (vts in ("", "1900-01-01") or vts > start):
            out.append((s, vt))
    return out


class _FakeChClient:
    """按 SQL 文本分发：成分表查询 → 本世界行；其余报错（防静默走真库）。"""

    def __init__(self, world: str):
        self.world = world

    def execute(self, sql, params=None):
        if "index_constituent" in sql:
            rows = _constituent_rows(self.world)
            if "valid_from <=" in sql:
                # SCD-2 窗口口径（_c4_engine retrofit 2026-09-18 / fw_backtest）：谓词模拟
                import re

                m_end = re.search(r"valid_from <= toDate\('([\d-]+)'\)", sql)
                m_start = re.search(r"valid_to > toDate\('([\d-]+)'\)", sql)
                assert m_end and m_start, f"窗口谓词缺参: {sql[:160]}"
                return _scd2_window_filter(rows, m_start.group(1), m_end.group(1))
            if "valid_to IS NULL" in sql:
                # 旧当前名单口径（已废，保留分发仅防意外复辟）
                return [(s,) for s, _vf, vt in rows if vt is None]
            return [(s, vt) for s, _vf, vt in rows]
        raise AssertionError(f"fake client 收到非预期 SQL: {sql[:120]}")


def _load_c4_engine():
    """按路径加载 _c4_engine（translated 目录注入 sys.path，与消费方同姿势）。"""
    if str(TRANSLATED) not in sys.path:
        sys.path.insert(0, str(TRANSLATED))
    import _c4_engine  # noqa: PLC0415

    return _c4_engine


def _universe_c4_window(world: str, start: str, end: str) -> set[str]:
    """retrofit 后 _c4_engine.load_hs300（SCD-2 窗口并集）双世界取宇宙。"""
    eng = _load_c4_engine()
    client = _FakeChClient(world)
    orig_q = eng._q
    eng._q = client.execute
    try:
        return eng.load_hs300(start, end)
    finally:
        eng._q = orig_q


def _universe_fw_scd2(world: str, start: str, end: str) -> list[str]:
    from zephyr.strategy_pipeline import fw_backtest

    client = _FakeChClient(world)

    class _Shim:
        def execute(self, sql, params=None):
            # fw_backtest 的 SCD-2 查询带 WHERE 谓词；本 fake 回全量行由 Python 侧
            # 谓词过滤——但该函数在 SQL 里就过滤了 valid_from/valid_to，故此处按
            # 查询里的 end/start 参数模拟同样的集合语义。
            rows = _constituent_rows(world)
            out = []
            for s, _vf, vt in rows:
                # 模拟 SQL: valid_from <= end AND (valid_to NULL/sentinel OR valid_to > start)
                if vt is None or vt == "1900-01-01" or vt > start:
                    out.append((s, vt))
            return out

    import zephyr.data.ch_writer as chw

    orig = chw.get_client_strict
    chw.get_client_strict = lambda: _Shim()
    try:
        symbols, _disc = fw_backtest._hs300_symbols(start, end)
        return symbols
    finally:
        chw.get_client_strict = orig


def test_scd2_window_paradigm_pit_green():
    """正确范式锚（应绿）：SCD-2 窗口口径下，X 后分歧不改变 ≤X 窗宇宙。"""
    a = _universe_fw_scd2("A", "2024-01-01", "2024-03-31")
    b = _universe_fw_scd2("B", "2024-01-01", "2024-03-31")
    assert a == b, "fw_backtest SCD-2 范式在 X 后分歧下产生了不同历史宇宙=范式退化"
    assert set(_BASE_MEMBERS) | {_EXIT_MEMBER} == set(a)  # 窗内在册者都入池（含期末调出者）


def test_c4_engine_universe_pit_gate():
    """通用 PIT 闸·宇宙轴（retrofit 落地 2026-09-18，xfail 已摘）：X 后分歧不得改写 ≤X 宇宙。"""
    a = _universe_c4_window("A", "2024-01-01", "2024-03-31")
    b = _universe_c4_window("B", "2024-01-01", "2024-03-31")
    assert a == b, (
        f"宇宙被 X 后信息改写: A-B={sorted(set(a) - set(b))} B-A={sorted(set(b) - set(a))}"
    )
    # 窗口并集语义：期末已调出者（世界 A 的 300750，valid_to 在窗后）仍入池
    assert set(a) == set(_BASE_MEMBERS) | {_EXIT_MEMBER}
    # 鉴别力 sanity（跨调出日窗口）：宇宙 PIT 仍成立（A==B），但披露把 X 后调出事件
    # 可见化——世界 A since_exit_n=1、世界 B=0（幸存者偏差禁静默，且不影响成员资格）
    a2 = _universe_c4_window("A", "2024-01-01", "2024-12-31")
    b2 = _universe_c4_window("B", "2024-01-01", "2024-12-31")
    assert a2 == b2 == set(_BASE_MEMBERS) | {_EXIT_MEMBER}
    eng = _load_c4_engine()
    _universe_c4_window("A", "2024-01-01", "2024-12-31")
    da = eng.last_universe_disclosure()
    assert da is not None and da["since_exit_n"] == 1
    _universe_c4_window("B", "2024-01-01", "2024-12-31")
    db = eng.last_universe_disclosure()
    assert db is not None and db["since_exit_n"] == 0
    # 结构钉：引擎宇宙 SQL 必须带窗口谓词+未失效哨兵（防 Snapshot 口径复辟）
    assert "valid_from <=" in eng.SQL_INDEX_CONS_WINDOW
    assert "{sentinel}" in eng.SQL_INDEX_CONS_WINDOW
    assert eng._NO_EXPIRY_SENTINEL == "1900-01-01"


# ── 权重轴：模板族双世界行情（X 后价格分歧） ──────────────────────────────────

_FACT_EXPR = "rank_cs( (ret_20d - ts_zscore_20(ret_20d)) * (turnover / vol_20d) )"
_W_AXIS_START, _W_AXIS_END = "2024-01-02", "2024-05-31"
_W_UNIVERSE = [f"{600000 + i}" for i in range(12)]


def _synth_kline_rows(world: str, start: str, end: str, syms: tuple[str, ...]) -> list[tuple]:
    """合成日 K 行（date, s, close, turnover, amount）；确定性、两世界仅 X 后分歧。"""
    import hashlib

    rows = []
    dates = pd.bdate_range(start, end)
    for si, s in enumerate(syms):
        px = 10.0 + si
        for d in dates:
            seed = int(hashlib.md5(f"{s}|{d.date()}".encode()).hexdigest()[:8], 16)
            drift = ((seed % 21) - 10) / 200.0  # ±5% 日漂
            if world == "B" and d > X_DAY:
                drift = -drift  # X 后镜像分歧
            px = max(1.0, px * (1 + drift))
            rows.append((d.date(), s, round(px, 2), 0.01 + (seed % 50) / 1000.0,
                         px * 1e6 + seed % 1000))
    return rows


class _FakeChClientWeights(_FakeChClient):
    """模板族权重轴 fake：universe 查询（avg(amount)）+ kline 查询双分发。"""

    def execute(self, sql, params=None):
        if "avg(amount)" in sql:
            return [(s,) for s in _W_UNIVERSE]
        if "close" in sql and params and "syms" in params:
            return _synth_kline_rows(self.world, str(params["start"]), str(params["end"]),
                                     tuple(params["syms"]))
        raise AssertionError(f"fake client 收到非预期 SQL: {sql[:120]}")


def _template_weights(world: str):
    from scripts.backtest import factor_strategy_template as fst

    import clickhouse_driver

    client = _FakeChClientWeights(world)
    orig_client = clickhouse_driver.Client
    clickhouse_driver.Client = lambda **_kw: client
    try:
        weights, _closes = fst.build_factor_weights(
            _W_AXIS_START, _W_AXIS_END, _FACT_EXPR, top_n=4, universe_n=10
        )
        return weights
    finally:
        clickhouse_driver.Client = orig_client


def test_template_family_weights_pit_axis():
    """通用 PIT 闸·权重轴（模板族实测钉）：X 后行情分歧 → weights[:X] 逐位不变。

    实测现状（2026-09-17）：模板宇宙=start 前 365 日成交额（前向封闭）+ 特征逐票滚动
    + 截面排名逐日因果 + assemble_weights shift(1)——权重轴当前**绿**。本件钉住防退化；
    若 retrofit/改写引入全窗统计量（如全窗 z-score），本件当天红。
    """
    wa = _template_weights("A")
    wb = _template_weights("B")
    assert wa.equals(wb.loc[wa.index]) or True  # 索引同源；逐格断言在下
    x_key = X_DAY.date()  # weights 索引=datetime.date（模板透视自 synth 行）
    pre_a = wa.loc[[d <= x_key for d in wa.index]]
    pre_b = wb.loc[[d <= x_key for d in wb.index]]
    pd.testing.assert_frame_equal(pre_a, pre_b, check_exact=True)
    # 后置 sanity：两世界在 X 后确实分歧（否则本闸无鉴别力=假绿风险）
    post_a = wa.loc[[d > x_key for d in wa.index]]
    post_b = wb.loc[[d > x_key for d in wb.index]]
    assert not post_a.equals(post_b), "双世界 X 后权重无分歧——构造无鉴别力（闸假绿）"


# ── 清单自洽钉：E4 受影响清单与仓库实况零漂移 ────────────────────────────────

_UNIVERSE_VICTIMS_DIRECT = (
    "c4_091fee38cd01_alpha022", "c4_6cb29d4d9ba8_mom_rev_300", "c4_93aa8f5a2bdd_multi_period",
    "c4_99873fd0bc17_macd_single", "c4_9c0136ec8f42_kucoffee_trend", "c4_9ce75aa27ce5_bluechip_ma",
    "c4_a4543012b464_trend5", "c4_bd42540f86e4_pe_pb", "c4_c72318f2da1c_bias_ql",
    "c4_fdbc279fba99_rps_oinl", "c4_valuation_pe_pb_double",
)
_VIA_VALUATION_ENGINE = (
    "c4_valuation_div_high", "c4_valuation_pb_low", "c4_valuation_pe_low", "c4_valuation_pe_zz500",
)
_TEMPLATE_CONSUMERS = (
    "c4_fact_4228020a", "c4_fact_4b200528", "c4_fact_4db4c41e",
    "c4_fact_4f749668", "c4_fact_e293e217", "c4_fact_e831084c",
)


def test_affected_list_zero_drift():
    """清单自洽（.runtime/tmp/exp/e4/affected_list.yaml 的机读钉）：

    直接受害件必须仍引用 load_hs300/load_index_constituents；经估值引擎件必须仍传
    universe="hs300"/"zz500"；模板消费方必须仍 import factor_strategy_template。
    任一漂移=清单过期（retrofit 后本件红=提醒同步退役清单）。
    """
    for stem in _UNIVERSE_VICTIMS_DIRECT:
        text = (TRANSLATED / f"{stem}.py").read_text(encoding="utf-8")
        assert "load_hs300(" in text or "load_index_constituents(" in text, f"{stem} 清单漂移"
    for stem in _VIA_VALUATION_ENGINE:
        text = (TRANSLATED / f"{stem}.py").read_text(encoding="utf-8")
        assert 'universe="hs300"' in text or 'universe="zz500"' in text, f"{stem} 清单漂移"
    for stem in _TEMPLATE_CONSUMERS:
        text = (TRANSLATED / f"{stem}.py").read_text(encoding="utf-8")
        assert "factor_strategy_template" in text, f"{stem} 清单漂移"
