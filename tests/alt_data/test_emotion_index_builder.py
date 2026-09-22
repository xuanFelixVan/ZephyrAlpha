"""emotion_index_builder 单元测试（fake reader 注入，同构 cohort 测试口径）。

零生产写路径：builder 纯计算，reader 全 fake 注入；断言契约行/分位数学/insufficient
降级/等权重分配/stage 语义（PIT：pre_open C1-C4 复用 T-1）。
"""

from __future__ import annotations

import datetime
import json

import pytest

import zephyr.alt_data.emotion_index_builder as eib


class FakeReader:
    """按 SQL 子串路由返回预制 TSV（同 cohort fake reader 口径）。"""

    def __init__(self, routes: dict[str, str]):
        self.routes = routes
        self.calls: list[str] = []

    def query(self, sql: str) -> str:
        self.calls.append(sql)
        for key, tsv in self.routes.items():
            if key in sql:
                return tsv
        return ""


# 统一 40+ 观测窗（日频 TSV：日期递增、值可判分位），末行=当日。
def _daily_tsv(n: int, value_fmt) -> str:
    base = datetime.date(2026, 9, 22)
    lines = []
    for i in range(n, 0, -1):
        d = base - datetime.timedelta(days=i)
        lines.append(f"{d.isoformat()}\t{value_fmt(n - i)}")
    lines.append(f"{base.isoformat()}\t{value_fmt(n)}")
    return "\n".join(lines)


def _ok_reader() -> FakeReader:
    """六成分全量就绪窗：daban/晋级/广度量能/指数/两融(35观测)/新闻。"""
    return FakeReader(
        {
            "_SQL_LIMITUP_DAILY"[:22]: _daily_tsv(40, lambda i: f"{100 + i}\t{90 + i}\t{i % 7}"),
            "consec_limit >= 1": _daily_tsv(40, lambda i: f"{5 + i}"),
            "promo": _daily_tsv(40, lambda i: f"{0.2 + 0.01 * (i % 5):.4f}"),
            "up_ratio": _daily_tsv(
                400, lambda i: f"{0.5 + 0.001 * (i % 100):.6f}\t{2e8 + i * 1e6:.0f}\t{1.5 + 0.01 * (i % 50):.4f}"
            ),
            "symbol = '000300'": _daily_tsv(400, lambda i: f"{4000 + i}"),
            "margin_balance": _daily_tsv(35, lambda i: f"{18000e8 + i * 1e8:.0f}"),
            "sentiment_index": _daily_tsv(200, lambda i: f"{0.01 * (i % 30):.4f}"),
        }
    )


def _poor_reader() -> FakeReader:
    """daban 全空（C1/C2 missing）+ 两融 100 观测（C5 insufficient）+ C3/C4/C6 ok。"""
    return FakeReader(
        {
            "up_ratio": _daily_tsv(400, lambda i: f"{0.5:.6f}\t{2e8:.0f}\t{1.5:.4f}"),
            "symbol = '000300'": _daily_tsv(400, lambda i: f"{4000 + i}"),
            "margin_balance": _daily_tsv(100, lambda i: f"{18000e8 + i * 1e8:.0f}"),
            "sentiment_index": _daily_tsv(200, lambda i: f"{0.01 * (i % 30):.4f}"),
        }
    )


def test_contract_row_close_final():
    """契约行字段齐+版本+ts=当日15:10 Asia/Shanghai+components 六成分 JSON 可序列化。"""
    row = eib.build_emotion_index("2026-09-22", reader=_ok_reader())
    assert row is not None
    assert row["trade_date"] == datetime.date(2026, 9, 22)
    assert row["stage"] == "close_final"
    assert row["version"] == "v0.1.0"
    assert row["ts"].isoformat().startswith("2026-09-22T15:10:00+08:00")
    assert 0.0 <= row["emotion_index"] <= 1.0
    assert len(row["components"]) == 6
    assert {c["name"] for c in row["components"]} == {
        "C1_limitup_temp",
        "C2_promotion",
        "C3_breadth",
        "C4_volume",
        "C5_margin",
        "C6_news",
    }
    json.dumps(row["components"], ensure_ascii=False)  # 契约：components 可 JSON 序列化


def test_pre_open_pit_semantics():
    """pre_open：ts=09:15，C1-C4 asof=T-1（复用收盘态），C5/C6 asof=T。"""
    row = eib.build_emotion_index("2026-09-22", stage=eib.STAGE_PRE_OPEN, reader=_ok_reader())
    assert row is not None and row["ts"].isoformat().startswith("2026-09-22T09:15:00+08:00")
    by_name = {c["name"]: c for c in row["components"]}
    assert by_name["C1_limitup_temp"]["asof"] == "2026-09-21"
    assert by_name["C3_breadth"]["asof"] == "2026-09-21"
    assert by_name["C5_margin"]["asof"] == "2026-09-22"
    assert by_name["C6_news"]["asof"] == "2026-09-22"


def test_insufficient_weight_redistribution():
    """daban 空窗+两融观测不足：C1/C2/C5 不出分位，等权 1/3 分配至 C3/C4/C6。"""
    row = eib.build_emotion_index("2026-09-22", reader=_poor_reader())
    assert row is not None
    by_name = {c["name"]: c for c in row["components"]}
    assert by_name["C1_limitup_temp"]["status"] == "missing"
    assert by_name["C2_promotion"]["status"] == "missing"
    assert by_name["C5_margin"]["status"] == "insufficient"
    ok_names = ["C3_breadth", "C4_volume", "C6_news"]
    for n in ok_names:
        assert by_name[n]["weight"] == pytest.approx(1 / 3, abs=1e-4)
        assert by_name[n]["status"] == "ok"
    assert by_name["C5_margin"]["weight"] == 0.0
    w = round(1.0 / 3, 6)  # 镜像 builder：等权重先 round(·,6) 再求和
    expect = sum(by_name[n]["percentile"] * w for n in ok_names)
    assert row["emotion_index"] == pytest.approx(round(expect, 6), abs=1e-9)


def test_all_missing_returns_none():
    """全成分不可产 → None（禁拍假值）。"""
    reader = FakeReader({})
    assert eib.build_emotion_index("2026-09-22", reader=reader) is None


def test_percentile_math():
    """秩分位定义：值在序列中 ≤ 计数/总数（末窗裁剪语义）。"""
    s = __import__("pandas").Series([1.0, 2.0, 3.0, 4.0, 5.0])
    assert eib._pctl(s, 3.0) == (0.6, 5)
    assert eib._pctl(s, None) == (None, 5)
    assert eib._pctl(s, float("nan"))[0] is None


def test_unknown_stage_rejected():
    with pytest.raises(ValueError):
        eib.build_emotion_index("2026-09-22", stage="auction_v99", reader=_ok_reader())
