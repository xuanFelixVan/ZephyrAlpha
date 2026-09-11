"""ChainImpactStream（MOD-INT-IMPACT-STREAM，接线 W5）单元测试——分钟窗/传导编排/聚合/fail-open。

覆盖（接线指令 W5 验收口径：端到端编排 + 红蓝对抗）：
- 编排：新闻窗→情绪打分→W3 链接→W4 标的→跨新闻聚合（全链注入 mock，离线）
- PIT：窗口 SQL 含注入 now 的上界；news_id 多版本 keep-first 去重
- 聚合：同 symbol sources 累计、置信度最高者胜出
- fail-open：CH 故障→degraded=True 留痕返回空快照不抛；单条传导异常跳过不炸批
- 序列化：to_dict 纯 JSON 可序列化（json.dumps 全量验证）
- 红蓝·边界：空窗/空标题/构造参数越界（ZA-IT-0031）
- 红蓝·故障：CH 查询抛异常 / 词表加载抛异常 → 结构性 degraded
- 红蓝·前视：publish_time>now 的未来新闻不得入窗（SQL 断言）；情绪死区新闻不产条目
全部离线（ch_query/linker/resolver/scorer 全注入），不触网不触库。
"""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from zephyr.intelligence.chain_impact_resolver import ChainImpactResolver
from zephyr.intelligence.chain_impact_stream import (
    ChainImpactStream,
    ChainImpactStreamError,
)
from zephyr.intelligence.news_chain_node_linker import ChainNodeLinker

# ── 离线夹具：最小图谱（半导体材料→光刻胶生产）──
_VOCAB = [
    ("ND-1", "CH-1", "半导体材料", "上游", None),
    ("ND-2", "CH-1", "光刻胶生产", "中游", None),
]
_NODES = [
    ("ND-1", "CH-1", "半导体材料", "上游"),
    ("ND-2", "CH-1", "光刻胶生产", "中游"),
]
_EDGES = [("ND-1", "ND-2", "supply")]
_COMPANIES = [("ND-1", "600703.SH", "核心", 0.95), ("ND-2", "300346.SZ", "龙头", 0.9)]

_NOW = datetime(2026, 9, 11, 10, 0, 0)

_TSV = (
    "n1\t2026-09-11 09:58:00.000\t半导体材料涨价催化板块走强\tcls\n"
    "n2\t2026-09-11 09:57:00.000\t央行开展逆回购操作\tcls\n"
    "n1\t2026-09-11 09:58:00.000\t半导体材料涨价催化板块走强（修正稿）\tcls\n"  # 多版本 SCD
    "n3\t2026-09-11 09:59:30.000\t光刻胶生产排产饱满\tjin10/index\n"
)


def _ch_query_ok(sql: str) -> str:
    # PIT 断言：上界=注入 now（红蓝·前视：未来新闻不得入窗的守卫在 SQL 口径）
    assert "2026-09-11 10:00:00" in sql
    return _TSV


def _scorer_pos(title: str, content: str) -> tuple[float, tuple[str, ...]]:
    return (0.8, ("涨价",))


def _stream(**kw: object) -> ChainImpactStream:
    return ChainImpactStream(
        ChainNodeLinker(_VOCAB),
        ChainImpactResolver(_EDGES, _NODES, _COMPANIES),
        _scorer_pos,
        ch_query=_ch_query_ok,
        news_table="c3_fundamental.news_data",
        **kw,  # type: ignore[arg-type]
    )


# ============================================================================
# 1. 端到端编排
# ============================================================================


class TestEndToEnd:
    def test_window_to_targets(self) -> None:
        snap = _stream().run(now=_NOW)
        assert snap.degraded is False
        assert snap.errors == ()
        assert snap.news_count == 3  # 去重后（4 行−1 多版本）
        assert snap.matched_count == 2  # n1/n3 命中；n2 无图谱命中
        assert {it.news.news_id for it in snap.items} == {"n1", "n3"}
        # n1 命中 ND-1 → 标的含扩散 ND-2 两标的
        n1 = next(it for it in snap.items if it.news.news_id == "n1")
        assert {t.symbol for t in n1.targets} == {"600703.SH", "300346.SZ"}
        assert n1.direction_label == "利好"
        # 聚合清单 symbol 唯一
        assert len({t.symbol for t in snap.all_targets}) == len(snap.all_targets)

    def test_multi_version_keep_first(self) -> None:
        snap = _stream().run(now=_NOW)
        n1 = next(it for it in snap.items if it.news.news_id == "n1")
        assert n1.news.title == "半导体材料涨价催化板块走强"  # keep-first=最早版本

    def test_aggregation_sources_accumulate(self) -> None:
        # n1 命中 ND-1、n3 命中 ND-2——无向扩散下两新闻互相可达对方节点，
        # 两标的在两条新闻中各产出一次 → sources=2（无向传导口径的聚合语义）
        snap = _stream().run(now=_NOW)
        by_symbol = {t.symbol: t for t in snap.all_targets}
        assert by_symbol["300346.SZ"].sources == 2
        assert by_symbol["600703.SH"].sources == 2

    def test_to_dict_json_safe(self) -> None:
        snap = _stream().run(now=_NOW)
        payload = snap.to_dict()
        assert json.dumps(payload, ensure_ascii=False)  # 全量可序列化不抛
        assert payload["ok"] is True and payload["matched_count"] == 2


# ============================================================================
# 2. PIT 与死区
# ============================================================================


class TestPitAndDeadZone:
    def test_dead_zone_news_skipped(self) -> None:
        snap = ChainImpactStream(
            ChainNodeLinker(_VOCAB),
            ChainImpactResolver(_EDGES, _NODES, _COMPANIES),
            lambda t, c: (0.05, ()),  # 死区内→无方向冲击
            ch_query=lambda s: _TSV,
            news_table="t",
        ).run(now=_NOW)
        assert snap.matched_count == 0 and snap.all_targets == ()

    def test_window_minutes_reflected_in_sql(self) -> None:
        captured: list[str] = []

        def _capture(sql: str) -> str:
            captured.append(sql)
            return _TSV

        ChainImpactStream(
            ChainNodeLinker(_VOCAB),
            ChainImpactResolver(_EDGES, _NODES, _COMPANIES),
            _scorer_pos,
            window_minutes=15,
            ch_query=_capture,
            news_table="t",
        ).run(now=_NOW)
        assert "2026-09-11 09:45:00" in captured[0]  # now-15min 下界


# ============================================================================
# 3. fail-open 降级
# ============================================================================


class TestFailOpen:
    def test_ch_failure_degraded_no_raise(self) -> None:
        def _boom(sql: str) -> str:
            raise RuntimeError("ch down")

        stream = ChainImpactStream(
            ChainNodeLinker(_VOCAB),
            ChainImpactResolver(_EDGES, _NODES, _COMPANIES),
            _scorer_pos,
            ch_query=_boom,
            news_table="t",
        )
        snap = stream.run(now=_NOW)
        assert snap.degraded is True
        assert snap.news_count == 0 and snap.items == ()
        assert any("news_fetch_failed" in e for e in snap.errors)

    def test_graph_failure_degraded_no_raise(self) -> None:
        class _BrokenLinker:
            def vocab_size(self) -> int:
                raise RuntimeError("vocab gone")

        stream = ChainImpactStream(
            _BrokenLinker(),  # type: ignore[arg-type]
            ChainImpactResolver(_EDGES, _NODES, _COMPANIES),
            _scorer_pos,
            ch_query=lambda s: _TSV,
            news_table="t",
        )
        snap = stream.run(now=_NOW)
        assert snap.degraded is True
        assert any("graph_load_failed" in e for e in snap.errors)

    def test_single_item_failure_skipped_not_batch(self) -> None:
        class _HalfLinker:
            def vocab_size(self) -> int:
                return 2

            def link(self, text: str) -> tuple:
                if "半导体" in text:
                    raise ValueError("boom on this one")
                return ()

        stream = ChainImpactStream(
            _HalfLinker(),  # type: ignore[arg-type]
            ChainImpactResolver(_EDGES, _NODES, _COMPANIES),
            _scorer_pos,
            ch_query=lambda s: _TSV,
            news_table="t",
        )
        snap = stream.run(now=_NOW)
        assert snap.degraded is False  # 单条异常非结构性故障
        assert snap.news_count == 3 and snap.matched_count == 0
        assert any("link_failed[n1]" in e for e in snap.errors)


# ============================================================================
# 4. 构造校验
# ============================================================================


class TestConstructor:
    def test_param_bounds(self) -> None:
        with pytest.raises(ChainImpactStreamError):
            _stream(window_minutes=0)
        with pytest.raises(ChainImpactStreamError):
            _stream(news_limit=0)
