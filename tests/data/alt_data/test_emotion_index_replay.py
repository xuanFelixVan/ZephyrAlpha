"""emotion_index_replay 单元测试（合成 CH 注入，零生产写路径）。

核心断言：切片缓存 reader 与真（合成）窄窗查询字节一致；回放行与冻结 builder 直调
逐位相等（PIT 纯求值）；落库只写非撞键行且 source='replay'。
"""

from __future__ import annotations

import datetime
import json

import pytest

import zephyr.alt_data.emotion_index_builder as eib
import zephyr.alt_data.emotion_index_replay as eir

_CAL_START = datetime.date(2024, 1, 1)
_CAL_END = datetime.date(2026, 9, 22)


def _calendar() -> list[str]:
    days: list[str] = []
    d = _CAL_START
    while d <= _CAL_END:
        if d.weekday() < 5:
            days.append(d.isoformat())
        d += datetime.timedelta(days=1)
    return days


_CAL = _calendar()


def _val(d: str, salt: int) -> float:
    return ((int(d.replace("-", "")) * 2654435761 + salt) % 9973) / 9973


class SyntheticCH:
    """合成 CH：解析 BETWEEN 界按界生成确定性行（宽窗/窄窗同源=切片可证基准）。

    返回串带尾换行，复刻真 CH TSV 输出形态（防切片侧尾换行差异在测试里失明）。
    """

    @staticmethod
    def _pack(rows: list[str]) -> str:
        return "\n".join(rows) + "\n" if rows else ""

    def query(self, sql: str) -> str:
        import re

        m = re.search(r"BETWEEN '(\d{4}-\d{2}-\d{2})' AND '(\d{4}-\d{2}-\d{2})'", sql)
        lo, hi = (m.group(1), m.group(2)) if m else ("1900-01-01", "2999-12-31")
        days = [d for d in _CAL if lo <= d <= hi]
        if "AS max_consec" in sql:
            return self._pack(
                [f"{d}\t{80 + int(_val(d, 1) * 60)}\t{60 + int(_val(d, 2) * 40)}\t{int(_val(d, 3) * 8)}" for d in days]
            )
        if "AS promo" in sql:
            return self._pack([f"{d}\t{_val(d, 4):.4f}" for d in days])
        if "AS med_turn" in sql:
            return self._pack(
                [f"{d}\t{_val(d, 5):.6f}\t{2e8 + _val(d, 6) * 1e9:.0f}\t{1.5 + _val(d, 7):.4f}" for d in days]
            )
        if "symbol = '000300'" in sql:
            return self._pack([f"{d}\t{4000 + _val(d, 8) * 100:.2f}" for d in days])
        if "AS bal" in sql:
            return self._pack([f"{d}\t{18000e8 + _val(d, 9) * 1e9:.0f}" for d in days])
        if "scope = 'market'" in sql:
            return self._pack([f"{d}\t{0.5 - _val(d, 10):.4f}" for d in days])
        if "DISTINCT trade_date" in sql:
            return self._pack(_CAL[-10:])
        return ""


def _sample_days(n: int = 6) -> list[str]:
    step = max(1, len(_CAL) // (n + 1))
    return [_CAL[len(_CAL) - 1 - i * step] for i in range(n)][::-1]


def test_slice_reader_byte_equivalence():
    """切片回放 vs 真窄窗查询：白名单形状逐字节一致。"""
    src = SyntheticCH()
    r = eir.ReplaySliceReader(src)
    for d in _sample_days(8):
        for tbl, marker in (
            (eib._TBL_DABAN, eib._SQL_LIMITUP_DAILY),
            (eib._TBL_KLINE_DAILY, eib._SQL_AD_DAILY),
            (eib._TBL_KLINE_INDEX, eib._SQL_INDEX_CLOSE),
            (eib._TBL_MARGIN, eib._SQL_MARGIN_BAL),
            (eib._TBL_NSW, eib._SQL_NEWS_MEAN),
        ):
            wide = marker.format(tbl=tbl, start=eir.GLOBAL_START, day=eir._today())
            narrow = eir._window_bounds_sql(
                wide,
                (datetime.date.fromisoformat(d) - datetime.timedelta(days=590)).isoformat(),
                d,
            )
            assert r.query(narrow) == src.query(narrow), f"{d} {marker[:40]}"
    assert r.stats["wide_fetch"] == 5


def test_join_shape_bypasses_slice():
    """白名单外（PROMOTION 自 JOIN）→ 真查询直通并按 (start,day) 缓存。"""
    src = SyntheticCH()
    calls = {"n": 0}

    class Counting(SyntheticCH):
        def query(self, sql: str) -> str:
            if "AS promo" in sql:
                calls["n"] += 1
            return super().query(sql)

    cs = Counting()
    r = eir.ReplaySliceReader(cs)
    sql1 = eib._SQL_PROMOTION.format(tbl=eib._TBL_DABAN, start="2026-01-01", day="2026-03-01")
    sql2 = eib._SQL_PROMOTION.format(tbl=eib._TBL_DABAN, start="2026-01-01", day="2026-03-01")
    assert r.query(sql1) == cs.query(sql1)
    first = calls["n"]
    r.query(sql2)
    assert calls["n"] == first  # 缓存命中不再打源


def test_replay_rows_bit_identical_to_builder():
    """回放行 vs 冻结 builder 真数据面直调：emotion_index 与 components 逐位相等。"""
    src = SyntheticCH()
    days = _sample_days(5)
    rep = eir.replay_history(days[0], days[-1], source_reader=src)
    by_day = {r["trade_date"].isoformat(): r for r in rep["rows"]}
    for d in days:
        direct = eib.build_emotion_index(d, stage=eib.STAGE_CLOSE_FINAL, reader=src)
        row = by_day[d]
        assert row is not None and direct is not None
        assert row["emotion_index"] == direct["emotion_index"]
        assert json.dumps(row["components"], sort_keys=True) == json.dumps(direct["components"], sort_keys=True)


def test_replay_skips_none_days():
    """全成分不可产日如实跳过（skipped 计数，禁拍假值）。"""
    src = SyntheticCH()
    rep = eir.replay_history("2024-01-02", "2024-03-01", source_reader=src)
    for d in rep["skipped"]:
        assert eib.build_emotion_index(d, reader=src) is None
    assert len(rep["rows"]) + len(rep["skipped"]) == len(rep["days"])


def test_partition_chunks_respects_cap():
    """跨 424 月分区的行集必须聚成多块，且块内分区数 ≤ 上限（CH Code 252 红证）。"""
    rows = []
    d = datetime.date(1991, 6, 1)
    while d < datetime.date(2026, 10, 1):
        rows.append((d, "close_final", None, 0.5, "[]", "v0.1.0", "replay"))
        d = d + datetime.timedelta(days=7)  # 每 ~1 个月一行
    parts = {eir._partition_of(r[0]) for r in rows}
    assert len(parts) > eir._MAX_PARTITIONS_PER_BLOCK
    blocks = eir.partition_chunks(sorted(rows, key=lambda r: eir._partition_of(r[0])))
    assert len(blocks) >= 5
    for b in blocks:
        assert len({eir._partition_of(r[0]) for r in b}) <= eir._MAX_PARTITIONS_PER_BLOCK
    assert sum(len(b) for b in blocks) == len(rows)


def test_write_replay_rows_chunks_executes():
    """落库路径按块多次 execute（单块一次 execute 会被 CH 拒 Code 252）。"""
    calls: list[int] = []

    class FakeClient:
        def execute(self, sql: str, data: list[tuple]) -> None:
            calls.append(len({eir._partition_of(r[0]) for r in data}))

    src = SyntheticCH()
    # 造 200 个跨月行（>90 分区），全部避开活键（活键=近 10 交易日）
    rows = []
    d = datetime.date(2000, 1, 5)
    for i in range(200):
        dd = d + datetime.timedelta(days=31 * i)
        rows.append(
            {
                "trade_date": dd,
                "stage": "close_final",
                "ts": datetime.datetime(dd.year, dd.month, dd.day, 15, 10),
                "emotion_index": 0.5,
                "components": [],
                "version": "v0.1.0",
            }
        )
    out = eir.write_replay_rows(rows, source_reader=src, client=FakeClient())
    assert out["written"] == 200
    assert len(calls) >= 3 and all(c <= eir._MAX_PARTITIONS_PER_BLOCK for c in calls)


def test_write_replay_rows_skips_live_keys():
    """撞活键行跳过；写入行 source='replay' 且列序=INSERT_COLUMNS+source。"""
    captured: dict[str, object] = {}

    class FakeClient:
        def execute(self, sql: str, data: list[tuple]) -> None:
            captured["sql"] = sql
            captured["data"] = data

    src = SyntheticCH()
    rep = eir.replay_history("2026-08-03", "2026-09-10", source_reader=src)
    rows = rep["rows"]
    assert rows
    # 活键注入：SyntheticCH 的 DISTINCT 路由返回 _CAL[-10:]（近 10 个交易日），
    # 取一个必然撞键的日与一个不撞的日分别验证。
    hit = rows[-1]
    assert hit["trade_date"].isoformat() in src.query(
        "SELECT DISTINCT trade_date FROM t FINAL WHERE stage = 'close_final'"
    )
    out = eir.write_replay_rows([hit], source_reader=src, client=FakeClient())
    assert out["written"] == 0 and out["skipped_live_keys"] == 1
    miss = [r for r in rows if r["trade_date"].isoformat() not in src.query("SELECT DISTINCT trade_date FROM t")]
    assert miss
    out2 = eir.write_replay_rows(miss[:1], source_reader=src, client=FakeClient())
    assert out2["written"] == 1
    assert "source" in captured["sql"]
    assert captured["data"][0][-1] == "replay"
    assert captured["data"][0][4] == json.dumps(miss[0]["components"], ensure_ascii=False)


def test_verify_equivalence_red_signal():
    """等价自证红信号：源对窄窗返回被篡改字节 → RuntimeError fail-visible。"""

    class Tampered(SyntheticCH):
        def query(self, sql: str) -> str:
            out = super().query(sql)
            if "AS bal" in sql and "BETWEEN" in sql:
                return out + "\n9999-12-31\t0"
            return out

    src = Tampered()
    r = eir.ReplaySliceReader(src)
    with pytest.raises(RuntimeError, match="形状等价自证失败"):
        eir.verify_slice_equivalence(r, _sample_days(2), src)


def test_pit_live_value_check_green_and_red():
    """10 天活值对拍：同源绿；数据面被改一行即红（禁拍假值）。"""
    src = SyntheticCH()
    days = _sample_days(4)
    res = eir.pit_live_value_check(days[0], days[-1], days, source_reader=src)
    assert res["all_match"] and res["sampled"] == len(days)

    class Drifted(SyntheticCH):
        def query(self, sql: str) -> str:
            if "AS med_turn" in sql and eir.GLOBAL_START not in sql:
                return ""  # 活直调窄窗数据面缺失→成分不对称→必须红
            return super().query(sql)

    ds = Drifted()
    with pytest.raises(RuntimeError, match="PIT 活值对拍失败"):
        eir.pit_live_value_check(days[0], days[-1], days, source_reader=ds)


def test_empty_wide_fetch_fail_visible():
    """宽窗抓取空（ch 静默失败防线）→ fail-visible，不产假绿空回放。"""

    class EmptyKline(SyntheticCH):
        def query(self, sql: str) -> str:
            if "AS med_turn" in sql and eir.GLOBAL_START in sql:
                return ""
            return super().query(sql)

    with pytest.raises(RuntimeError, match="宽窗抓取为空"):
        eir.replay_history("2026-08-01", "2026-09-01", source_reader=EmptyKline())
