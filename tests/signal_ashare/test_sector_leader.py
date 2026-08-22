"""MOD-SIG-062 板块龙头识别器（SEC-04）单元测试（22号 §3.1⑦ 落码，合成梯队 _FakeCH 注入不触库）"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, timedelta

import pytest

from zephyr.signal_ashare import sector_leader as mod
from zephyr.signal_ashare.sector_leader import (
    SectorLeaderConfig,
    identify_sector_leaders,
)

D_END = date(2026, 8, 21)  # 合成数据日（周五）
N_DAYS = 25  # 窗口天数（覆盖 ret_20d 21 行门槛）


class _FakeCH:
    """鸭子类型 ch_client：按 SQL 子串路由返回合成行（不触库）。"""

    def __init__(
        self,
        kline_rows=None,
        limit_rows=None,
        constituent_rows=None,
        exc_on: str | None = None,
    ):
        self._kline = kline_rows or []
        self._limit = limit_rows or []
        self._constituent = constituent_rows or []
        self._exc_on = exc_on
        self.calls: list[tuple[str, dict]] = []

    def execute(self, sql, params=None):
        self.calls.append((sql, params or {}))
        if self._exc_on and self._exc_on in sql:
            raise RuntimeError(f"合成故障: {self._exc_on}")
        if "max(trade_date)" in sql:
            return [(D_END,)]
        if "sector_constituent" in sql:
            rows = list(self._constituent)
            sector = (params or {}).get("sector")
            if sector is not None:
                rows = [r for r in rows if r[0] == sector]
            return rows
        if "stk_limit" in sql:
            return list(self._limit)
        if "kline_daily" in sql:
            return list(self._kline)
        return []


def _days(n: int = N_DAYS) -> list[date]:
    """连续自然日序列当交易日用（模块不校验周末），末日=D_END。"""
    return [D_END - timedelta(days=n - 1 - i) for i in range(n)]


def _closes(trend: str, final_pct: float) -> list[float]:
    """合成收盘序列：trend 控 ret_20d 方向，末日=前日×(1+final_pct/100)（涨幅由相邻收盘推导）。"""
    if trend == "up":
        closes = [10.0 + i * 0.1 for i in range(N_DAYS)]  # ret_20d>0 趋势上涨
    else:
        closes = [13.0 - i * 0.1 for i in range(N_DAYS)]  # ret_20d<0 趋势下跌
    closes[-1] = closes[-2] * (1.0 + final_pct / 100.0)
    return closes


def _mk_stock(
    sym: str,
    *,
    trend: str = "up",
    final_pct: float = 1.0,
    amount: float = 1e8,
    turnover: float = 3.0,
    limit_tail: int = 0,
) -> tuple[list[tuple], list[tuple]]:
    """合成单股 kline+stk_limit 行（kline 5 列：symbol/date/close/amount/turnover）。

    limit_tail: 末尾连续封板天数（当日收盘=涨停价）；其余日 limit_up=close×1.1（非封板）。
    返回 (kline_rows, limit_rows)，列序对齐模块 SQL SELECT。
    """
    closes = _closes(trend, final_pct)
    klines: list[tuple] = []
    limits: list[tuple] = []
    for i, d in enumerate(_days()):
        c = closes[i]
        is_last = i == N_DAYS - 1
        klines.append((sym, d, c, amount if is_last else amount * 0.5, turnover))
        sealed = i >= N_DAYS - limit_tail
        limits.append((sym, d, c if sealed else c * 1.1))
    return klines, limits


def _universe() -> tuple[list[tuple], list[tuple], list[tuple]]:
    """合成四板块梯队宇宙（S1 四档齐 / S2 中位股 / S3 无龙头 / S4 并列）。

    返回 (kline_rows, limit_rows, constituent_rows)。
    """
    klines: list[tuple] = []
    limits: list[tuple] = []
    cons: list[tuple] = []

    def add(sector: str, sym: str, **kw):
        k, l = _mk_stock(sym, **kw)
        klines.extend(k)
        limits.extend(l)
        cons.append((sector, sym))

    # S1：四档齐——A 3连板龙头 / B 大成交额中军 / C 小涨跟风 / D 阴跌无特征
    add("881001.SH", "000001.SZ", trend="up", final_pct=10.0, amount=5e8, limit_tail=3)
    add("881001.SH", "000002.SZ", trend="up", final_pct=1.5, amount=1e10, limit_tail=0)
    add("881001.SH", "000003.SZ", trend="down", final_pct=2.0, amount=1e8, limit_tail=0)
    add("881001.SH", "000004.SZ", trend="down", final_pct=-3.0, amount=5e7, limit_tail=0)
    # S2：中位股——F 5板龙头 / G 4板非龙头（∈[3,5] 禁区）/ H 跟风
    add("881002.SH", "000005.SZ", trend="up", final_pct=10.0, amount=2e9, limit_tail=5)
    add("881002.SH", "000006.SZ", trend="up", final_pct=10.0, amount=1e9, limit_tail=4)
    add("881002.SH", "000007.SZ", trend="down", final_pct=1.0, amount=1e8, limit_tail=0)
    # S3：无龙头——J 首板（<2 不封龙）/ K 平盘跟风
    add("881003.SH", "000008.SZ", trend="up", final_pct=10.0, amount=5e8, limit_tail=1)
    add("881003.SH", "000009.SZ", trend="down", final_pct=0.5, amount=1e8, limit_tail=0)
    # S4：边界并列——L/M 同 3 连板，L 成交额更高封龙，M 落中位股
    add("881004.SH", "000010.SZ", trend="up", final_pct=10.0, amount=6e8, limit_tail=3)
    add("881004.SH", "000011.SZ", trend="up", final_pct=10.0, amount=5e8, limit_tail=3)
    return klines, limits, cons


def _run(**kw):
    klines, limits, cons = _universe()
    return identify_sector_leaders(trade_date=D_END, ch_client=_FakeCH(klines, limits, cons), **kw)


def _group(board, code: str):
    return next(g for g in board.sectors if g.sector_code == code)


# ---------- 四档划分（合成梯队正确性） ----------


class TestRoleAssignment:
    def test_full_ladder_sector(self):
        """S1：3连板 A=龙头(×1.5)、大成交额 B=中军(×1.2)、小涨 C=跟风(×0.8)、阴跌 D=neutral(×0)。"""
        board = _run()
        assert board.degraded is False
        g = _group(board, "881001.SH")
        assert g.leader is not None and g.leader.symbol == "000001.SZ"
        assert g.leader.consec_limit == 3
        assert g.leader.weight == pytest.approx(1.5)
        assert [b.symbol for b in g.backbones] == ["000002.SZ"]
        assert g.backbones[0].weight == pytest.approx(1.2)
        assert any("中军" in r and "Top3" in r for r in g.backbones[0].reasons)
        assert [f.symbol for f in g.followers] == ["000003.SZ"]
        assert g.followers[0].weight == pytest.approx(0.8)
        assert [n.symbol for n in g.neutrals] == ["000004.SZ"]
        assert g.neutrals[0].weight == pytest.approx(0.0)
        assert g.annotation is None

    def test_mid_zone_neutral(self):
        """S2：4板非龙头 G → 中位股禁区（×0，reasons 留痕死亡区域）。"""
        g = _group(_run(), "881002.SH")
        assert g.leader is not None and g.leader.symbol == "000005.SZ"
        assert g.leader.consec_limit == 5
        assert [n.symbol for n in g.neutrals] == ["000006.SZ"]
        assert "中位股禁区" in g.neutrals[0].reasons[0]
        assert [f.symbol for f in g.followers] == ["000007.SZ"]

    def test_no_leader_sector(self):
        """S3：最高 1 板 <2 门槛 → leader 档空+中文注解（不强行封龙），首板 J 归跟风。"""
        g = _group(_run(), "881003.SH")
        assert g.leader is None
        assert g.annotation is not None and "无龙头板块" in g.annotation
        assert "1 板" in g.annotation
        assert {f.symbol for f in g.followers} == {"000008.SZ", "000009.SZ"}

    def test_tie_break_by_amount(self):
        """S4：L/M 同 3 连板并列 → 成交额高者 L 封龙，M 落中位股（边界并列定序确定性）。"""
        g = _group(_run(), "881004.SH")
        assert g.leader is not None and g.leader.symbol == "000010.SZ"
        assert [n.symbol for n in g.neutrals] == ["000011.SZ"]

    def test_weights_from_config_override(self):
        """四档权重走 config：覆盖 weight_leader=2.0 后龙头条目透传 2.0。"""
        board = _run(config=SectorLeaderConfig(weight_leader=2.0))
        g = _group(board, "881001.SH")
        assert g.leader is not None and g.leader.weight == pytest.approx(2.0)


# ---------- 评分（五维 MVP 前三维） ----------


class TestScoring:
    def test_score_range_and_leader_top(self):
        """评分 0-100 且龙头分为板块内最高（连板+涨幅+成交额三维分位均领先）。"""
        g = _group(_run(), "881001.SH")
        entries = [g.leader, *g.backbones, *g.followers, *g.neutrals]
        entries = [e for e in entries if e is not None]
        assert all(0.0 <= e.score <= 100.0 for e in entries)
        assert g.leader is not None
        assert g.leader.score == max(e.score for e in entries)

    def test_score_deterministic(self):
        """同输入同输出（纯函数评分可复算）。"""
        a = _group(_run(), "881001.SH")
        b = _group(_run(), "881001.SH")
        assert a.leader is not None and b.leader is not None
        assert a.leader.score == b.leader.score


# ---------- 连板高度推导 ----------


class TestConsecLimit:
    def test_consec_heights(self):
        """连板高度：A=3 / F=5 / G=4 / J=1 / 中军 B=0（当日未封板归零）。"""
        board = _run()
        got = {
            e.symbol: e.consec_limit
            for g in board.sectors
            for e in [g.leader, *g.backbones, *g.followers, *g.neutrals]
            if e is not None
        }
        assert got["000001.SZ"] == 3
        assert got["000005.SZ"] == 5
        assert got["000006.SZ"] == 4
        assert got["000008.SZ"] == 1
        assert got["000002.SZ"] == 0

    def test_stk_limit_missing_degrades(self):
        """stk_limit 全缺 → 连板维度降级：全宇宙 0 连板+各板块无龙头注解+notes 留痕。"""
        klines, _, cons = _universe()
        board = identify_sector_leaders(
            trade_date=D_END, ch_client=_FakeCH(klines, [], cons)
        )
        assert board.degraded is False
        assert any("stk_limit" in n for n in board.notes)
        assert all(g.leader is None for g in board.sectors)
        assert all(g.annotation and "无龙头板块" in g.annotation for g in board.sectors)


# ---------- 降级与契约 ----------


class TestDegradation:
    def test_kline_query_exception_degraded(self):
        _, _, cons = _universe()
        board = identify_sector_leaders(
            trade_date=D_END, ch_client=_FakeCH(constituent_rows=cons, exc_on="kline_daily")
        )
        assert board.degraded is True

    def test_constituent_empty_degraded(self):
        klines, limits, _ = _universe()
        board = identify_sector_leaders(
            trade_date=D_END, ch_client=_FakeCH(klines, limits, [])
        )
        assert board.degraded is True

    def test_sector_filter(self):
        """单板块过滤：仅返回该板块分组，SQL 走参数化 sector 过滤。"""
        client_rows = _universe()
        client = _FakeCH(*client_rows)
        board = identify_sector_leaders(
            trade_date=D_END, sector="881001.SH", ch_client=client
        )
        assert board.degraded is False
        assert [g.sector_code for g in board.sectors] == ["881001.SH"]
        const_call = next(c for c in client.calls if "sector_constituent" in c[0])
        assert const_call[1].get("sector") == "881001.SH"

    def test_constituent_duplicates_deduped(self):
        """成分表预合并重复行（无 FINAL 通道）→ 同股在同板块清单只出现一次。"""
        klines, limits, cons = _universe()
        cons_dup = cons + [("881001.SH", "000002.SZ")]  # 模拟 ReplacingMergeTree 预合并重复
        board = identify_sector_leaders(
            trade_date=D_END, ch_client=_FakeCH(klines, limits, cons_dup)
        )
        g = _group(board, "881001.SH")
        assert [b.symbol for b in g.backbones] == ["000002.SZ"]  # 不重复

    def test_trade_date_none_uses_latest(self):
        """trade_date=None → 取 kline_daily 最新数据日。"""
        klines, limits, cons = _universe()
        board = identify_sector_leaders(ch_client=_FakeCH(klines, limits, cons))
        assert board.trade_date == D_END.isoformat()

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            identify_sector_leaders(trade_date="2026/08/21", ch_client=_FakeCH())

    def test_client_unavailable_degraded(self, monkeypatch):
        """ch_client 未注入且默认客户端不可用 → degraded 空榜不炸。"""
        monkeypatch.setattr(mod, "_default_client", lambda: None)
        board = identify_sector_leaders(trade_date=D_END)
        assert board.degraded is True

    def test_asdict_json_serializable(self):
        """frozen dataclass asdict 可 JSON 序列化。"""
        json.dumps(asdict(_run()), ensure_ascii=False)
