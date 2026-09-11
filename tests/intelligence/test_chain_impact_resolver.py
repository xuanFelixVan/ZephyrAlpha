"""ChainImpactResolver（MOD-INT-CHAIN-IMPACT，接线 W4）单元测试——扩散/方向/标的去重。

覆盖（接线指令 W4 验收口径：N 跳扩散+方向判定；融合口径留痕 + 红蓝对抗）：
- 扩散：无向 BFS N 跳、路径留痕（path[0]=种子）、自环/墓碑端点不入图、visited 防环
- 方向：polarity 死区映射 ±1/0；全跳同向保留（融合口径=INVARIANTS 方向条款）
- 置信度：种子 hit.conf × hop_decay^hop × company_conf，截断 [0,1]
- 标的：ig_node_company 有效行收集；同 symbol 去重取（hop, -conf）最优并计 sources
- 融合口径：event_score surprise_direction 与情绪 polarity 同 [-1,1] 口径直喂
- 红蓝·边界：max_hops=0 / 环形图 / 菱形路径 / hop_decay 越界
- 红蓝·故障：from_pg 连接工厂异常上抛；注入边空端点 fail-closed（ZA-IT-0030）
- 红蓝·前视：polarity 超界值（±5）不产生超界方向；公司 conf>1 截断
全部离线（entries 注入 / conn_factory mock），不触网不触库。
"""

from __future__ import annotations

import pytest

from zephyr.intelligence.chain_impact_resolver import (
    DEFAULT_MAX_HOPS,
    DIRECTION_DEAD_ZONE,
    ChainImpactResolver,
    ChainImpactResolverError,
    ImpactTarget,
    direction_label,
)
from zephyr.intelligence.news_chain_node_linker import ChainNodeHit

# ── 图夹具：链 A（上游→中游→下游）+ 链 B（重名节点，验证扩散不串链）──
_NODES = [
    ("ND-1", "CH-1", "半导体材料", "上游"),
    ("ND-2", "CH-1", "光刻胶生产", "中游"),
    ("ND-3", "CH-1", "面板制造", "下游"),
    ("ND-4", "CH-2", "晶圆制造", "中游"),
]
_EDGES = [
    ("ND-1", "ND-2", "supply"),
    ("ND-2", "ND-3", "structure"),
    ("ND-4", "ND-2", "structure"),  # 跨链边（真实图谱形态）
    ("ND-9", "ND-9", "self"),  # 自环（应剔除）
    ("ND-1", "ND-T", "supply"),  # 墓碑端点（应剔除）
]
_COMPANIES = [
    ("ND-1", "600703.SH", "核心", 0.95),
    ("ND-2", "300346.SZ", "龙头", 0.9),
    ("ND-3", "000725.BJ", "参与", 0.6),
    ("ND-4", "688981.SH", "龙头", 1.0),
    ("ND-T", "999999.SH", "核心", 1.0),  # 墓碑公司映射（隔离不产出）
]


def _hit(node_id: str = "ND-1", name: str = "半导体材料", conf: float = 0.9) -> ChainNodeHit:
    return ChainNodeHit(
        node_id=node_id,
        chain_id="CH-1",
        node_name=name,
        tier="上游",
        match_source="name",
        matched_term=name,
        confidence=conf,
        ambiguous=False,
    )


def _resolver(**kw: object) -> ChainImpactResolver:
    return ChainImpactResolver(_EDGES, _NODES, _COMPANIES, **kw)  # type: ignore[arg-type]


# ============================================================================
# 1. 扩散
# ============================================================================


class TestExpand:
    def test_two_hop_reach_and_path(self) -> None:
        targets = _resolver().resolve([_hit()], 0.8)
        by_symbol = {t.symbol: t for t in targets}
        # ND-4（晶圆制造，跨链边 ND-4↔ND-2）经无向扩散同样可达（hop2）
        assert set(by_symbol) == {"600703.SH", "300346.SZ", "000725.BJ", "688981.SH"}
        assert by_symbol["600703.SH"].hop == 0
        assert by_symbol["300346.SZ"].hop == 1
        assert by_symbol["300346.SZ"].path == ("ND-1", "ND-2")
        assert by_symbol["000725.BJ"].hop == 2
        assert by_symbol["000725.BJ"].path == ("ND-1", "ND-2", "ND-3")
        assert by_symbol["688981.SH"].path == ("ND-1", "ND-2", "ND-4")

    def test_max_hops_bounds_reach(self) -> None:
        targets = _resolver(max_hops=1).resolve([_hit()], 0.8)
        assert {t.symbol for t in targets} == {"600703.SH", "300346.SZ"}

    def test_zero_hops_seed_only(self) -> None:
        targets = _resolver(max_hops=0).resolve([_hit()], 0.8)
        assert [t.symbol for t in targets] == ["600703.SH"]
        assert targets[0].hop == 0

    def test_cycle_graph_no_infinite_loop(self) -> None:
        r = ChainImpactResolver(
            [("A", "B", "structure"), ("B", "C", "structure"), ("C", "A", "structure")],
            [("A", "CH", "环节A", ""), ("B", "CH", "环节B", ""), ("C", "CH", "环节C", "")],
            [("A", "000001.SZ", "龙头", 1.0), ("B", "000002.SZ", "龙头", 1.0), ("C", "000003.SZ", "龙头", 1.0)],
            max_hops=10,
        )
        targets = r.resolve([_hit("A", "环节A")], 0.8)
        assert len(targets) == 3  # visited 防环，有限收敛

    def test_diamond_shortest_hop_wins(self) -> None:
        # 菱形：A→B→D 与 A→C→D 等长——D 唯一入 reach（visited 先到先得，路径确定）
        r = ChainImpactResolver(
            [("A", "B", "s"), ("A", "C", "s"), ("B", "D", "s"), ("C", "D", "s")],
            [("A", "CH", "A", ""), ("B", "CH", "B", ""), ("C", "CH", "C", ""), ("D", "CH", "D", "")],
            [("D", "000004.SH", "龙头", 1.0)],
        )
        targets = r.resolve([_hit("A", "A")], 0.8)
        assert len(targets) == 1 and targets[0].hop == 2


# ============================================================================
# 2. 方向与融合口径
# ============================================================================


class TestDirection:
    def test_bullish_propagates_same_sign(self) -> None:
        targets = _resolver().resolve([_hit()], 0.8)
        assert all(t.direction == 1 for t in targets)
        assert all(t.direction_label == "利好" for t in targets)

    def test_bearish_propagates_same_sign(self) -> None:
        targets = _resolver().resolve([_hit()], -0.7)
        assert all(t.direction == -1 for t in targets)
        assert all(direction_label(t.direction) == "利空" for t in targets)

    def test_dead_zone_neutral_empty(self) -> None:
        assert _resolver().resolve([_hit()], DIRECTION_DEAD_ZONE - 0.01) == ()

    def test_event_score_surprise_direction_fusion(self) -> None:
        # 融合口径：event_score surprise_direction（[-1,1]）与情绪 polarity 同口径直喂
        targets = _resolver().resolve([_hit()], -0.5)
        assert targets[0].direction == -1

    def test_direction_label_map(self) -> None:
        assert direction_label(1) == "利好"
        assert direction_label(-1) == "利空"
        assert direction_label(0) == "中性"
        assert direction_label(42) == "中性"  # 非法值兜底


# ============================================================================
# 3. 置信度与标的去重
# ============================================================================


class TestConfidenceAndDedup:
    def test_confidence_decay_formula(self) -> None:
        targets = _resolver(hop_decay=0.5).resolve([_hit(conf=0.9)], 0.8)
        by_symbol = {t.symbol: t for t in targets}
        assert by_symbol["600703.SH"].confidence == pytest.approx(0.9 * 0.95)  # hop0
        assert by_symbol["300346.SZ"].confidence == pytest.approx(0.9 * 0.5 * 0.9)
        assert by_symbol["000725.BJ"].confidence == pytest.approx(0.9 * 0.25 * 0.6)

    def test_role_confidence_none_defaults_one(self) -> None:
        r = ChainImpactResolver([], [("ND-Z", "CH", "环节Z", "")], [("ND-Z", "600000.SH", None, None)])
        targets = r.resolve([_hit("ND-Z", "环节Z")], 0.5)
        assert targets[0].confidence == pytest.approx(0.9)
        assert targets[0].role == ""

    def test_same_symbol_multi_node_dedup_best(self) -> None:
        # 同 symbol 映射到两个节点（ND-1 hop0 与 ND-2 hop1）→ 取 hop 最优 + sources=2
        r = ChainImpactResolver(
            [("ND-1", "ND-2", "supply")],
            [("ND-1", "CH", "环节一", ""), ("ND-2", "CH", "环节二", "")],
            [("ND-1", "600001.SH", "核心", 1.0), ("ND-2", "600001.SH", "参与", 1.0)],
        )
        targets = r.resolve([_hit("ND-1", "环节一")], 0.5)
        assert len(targets) == 1
        assert targets[0].hop == 0 and targets[0].sources == 2

    def test_sorting_deterministic(self) -> None:
        targets = _resolver().resolve([_hit()], 0.8)
        keys = [(t.hop, -t.confidence, t.symbol) for t in targets]
        assert keys == sorted(keys)


# ============================================================================
# 4. 构造校验与 fail-open
# ============================================================================


class TestConstructor:
    def test_empty_hits_fail_open(self) -> None:
        assert _resolver().resolve([], 0.8) == ()

    def test_empty_graph_fail_open(self) -> None:
        assert ChainImpactResolver().resolve([_hit()], 0.8) == ()

    def test_param_bounds(self) -> None:
        with pytest.raises(ChainImpactResolverError):
            _resolver(max_hops=-1)
        with pytest.raises(ChainImpactResolverError):
            _resolver(hop_decay=0.0)
        with pytest.raises(ChainImpactResolverError):
            _resolver(hop_decay=1.5)

    def test_malformed_rows_fail_closed(self) -> None:
        with pytest.raises(ChainImpactResolverError):
            ChainImpactResolver([("", "ND-2", "supply")])
        with pytest.raises(ChainImpactResolverError):
            ChainImpactResolver(company_rows=[("ND-1", "", "核心", 1.0)])


# ============================================================================
# 5. 红蓝对抗（边界/故障/前视）
# ============================================================================


class TestRedBlue:
    """红蓝对抗 ≥3 手法留痕：边界 / 故障 / 前视。"""

    def test_rb_boundary_tombstone_isolated(self) -> None:
        # 边界：墓碑节点不入扩散图——其公司映射永不产出
        targets = _resolver(max_hops=5).resolve([_hit()], 0.9)
        assert all(t.symbol != "999999.SH" for t in targets)

    def test_rb_fault_pg_unreachable_raises(self) -> None:
        # 故障：PG 不可达 → from_pg 显式上抛（W5 流层降级）
        def _boom() -> object:
            raise RuntimeError("pg down")

        with pytest.raises(RuntimeError):
            ChainImpactResolver.from_pg(_boom)

    def test_rb_lookahead_extreme_polarity_stable(self) -> None:
        # 前视：超界 polarity（±5）方向稳定 ±1，不产生超界 direction/confidence
        for pol in (5.0, -5.0):
            targets = _resolver().resolve([_hit()], pol)
            assert {t.direction for t in targets} == {1 if pol > 0 else -1}
            assert all(0.0 <= t.confidence <= 1.0 for t in targets)

    def test_rb_lookahead_company_conf_above_one_capped(self) -> None:
        # 前视：脏数据 company confidence>1 → 乘积截断 [0,1]
        r = ChainImpactResolver([], [("ND-Z", "CH", "环节Z", "")], [("ND-Z", "600001.SH", "核心", 2.5)])
        targets = r.resolve([_hit("ND-Z", "环节Z", conf=0.9)], 0.9)
        assert targets[0].confidence == pytest.approx(1.0)

    def test_rb_boundary_default_params(self) -> None:
        # 边界：默认参数生产口径（2 跳/0.6 衰减）
        assert DEFAULT_MAX_HOPS == 2
