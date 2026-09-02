# [BLUEPRINT] MOD-ML-019 | docs/03_modules/_domain_machine_learning_train/research_data_manager/blueprint.md | §test
# [A_module] module_id=MOD-ML-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-ML-019 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_train.test_research_data_manager
# [TESTS] src/zephyr/ml_train/research_data_manager.py
"""MOD-ML-019 单元测试：research_data_manager 研究数据管理器。

蓝图验收（B13-04336/CAND-MLT-027，A3 D-RESEARCH-01）：
数据集快照（manifest+hash，Git-like 版本链）+ 血缘注入回调 + 质量评分注入
（可选门禁）+ 元数据检索确定性排序 + 保留策略 TTL 裁决（链头恒保留）。
血缘/评分器/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.ml_train.research_data_manager",
    reason="research_data_manager not importable",
)

from zephyr.ml_train.research_data_manager import (  # noqa: E402
    ResearchDataError,
    ResearchDataManager,
)

_T0 = datetime.datetime(2026, 8, 25, 15, 0, 0)
_MANIFEST = {"symbol": "600519.SH", "rows": 1024, "freq": "1d"}


class _Clock:
    """可推进时钟替身。"""

    def __init__(self, t: datetime.datetime) -> None:
        self.t = t

    def __call__(self) -> datetime.datetime:
        return self.t


def _mgr(**kw) -> ResearchDataManager:
    kw.setdefault("clock", lambda: _T0)
    return ResearchDataManager(**kw)


# ──────────────────────────────────────────────────────────────────────────────
# 快照提交（Git-like 版本链）
# ──────────────────────────────────────────────────────────────────────────────


class TestCommit:
    def test_commit_chain_links(self) -> None:
        mgr = _mgr()
        s1 = mgr.commit_snapshot("ds1", _MANIFEST, message="首版")
        s2 = mgr.commit_snapshot("ds1", {**_MANIFEST, "rows": 2048})
        assert s1.version_id == "ds1@v0001"
        assert s1.parent_version is None
        assert s2.version_id == "ds1@v0002"
        assert s2.parent_version == "ds1@v0001"  # 单向链指向前驱

    def test_empty_fields_raise(self) -> None:
        mgr = _mgr()
        with pytest.raises(ResearchDataError):
            mgr.commit_snapshot("", _MANIFEST)
        with pytest.raises(ResearchDataError):
            mgr.commit_snapshot("ds1", {})
        with pytest.raises(ResearchDataError):
            mgr.commit_snapshot("ds1", "not-a-mapping")

    def test_default_hash_deterministic(self) -> None:
        m1 = _mgr()
        m2 = _mgr()
        h1 = m1.commit_snapshot("ds1", _MANIFEST).content_hash
        h2 = m2.commit_snapshot("ds1", _MANIFEST).content_hash
        assert h1 == h2  # 同 manifest 必同 hash
        h3 = m1.commit_snapshot("ds1", {**_MANIFEST, "rows": 9}).content_hash
        assert h3 != h1

    def test_custom_hasher_injected(self) -> None:
        mgr = _mgr(hasher=lambda m: f"h-{len(m)}")
        assert mgr.commit_snapshot("ds1", _MANIFEST).content_hash == "h-3"
        bad = _mgr(hasher=lambda m: "")
        with pytest.raises(ResearchDataError):
            bad.commit_snapshot("ds1", _MANIFEST)


# ──────────────────────────────────────────────────────────────────────────────
# 质量评分注入（复用质量门控）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuality:
    def test_quality_scored(self) -> None:
        mgr = _mgr(quality_scorer=lambda m: 0.87)
        snap = mgr.commit_snapshot("ds1", _MANIFEST)
        assert snap.quality_score == pytest.approx(0.87)
        assert _mgr().commit_snapshot("ds1", _MANIFEST).quality_score is None  # 未注入

    def test_quality_out_of_range_raise(self) -> None:
        mgr = _mgr(quality_scorer=lambda m: 1.5)
        with pytest.raises(ResearchDataError):
            mgr.commit_snapshot("ds1", _MANIFEST)

    def test_min_quality_gate_blocks_commit(self) -> None:
        mgr = _mgr(quality_scorer=lambda m: 0.3, min_quality=0.5)
        with pytest.raises(ResearchDataError):
            mgr.commit_snapshot("ds1", _MANIFEST)
        assert mgr.list_datasets() == ()  # 拒绝入链
        with pytest.raises(ResearchDataError):
            _mgr(min_quality=1.5)  # 门禁自身越界


# ──────────────────────────────────────────────────────────────────────────────
# 血缘回调
# ──────────────────────────────────────────────────────────────────────────────


class TestLineage:
    def test_lineage_events_with_parent(self) -> None:
        events: list[dict] = []
        mgr = _mgr(lineage_sink=lambda e: events.append(dict(e)))
        mgr.commit_snapshot("ds1", _MANIFEST)
        mgr.commit_snapshot("ds1", {**_MANIFEST, "rows": 2})
        assert [e["version_id"] for e in events] == ["ds1@v0001", "ds1@v0002"]
        assert events[1]["parent_version"] == "ds1@v0001"
        assert events[0]["content_hash"]

    def test_sink_exception_not_blocking(self) -> None:
        def _boom(_e) -> None:
            raise RuntimeError("sink 故障")

        mgr = _mgr(lineage_sink=_boom)
        snap = mgr.commit_snapshot("ds1", _MANIFEST)  # 回调异常不阻断
        assert snap.version_id == "ds1@v0001"


# ──────────────────────────────────────────────────────────────────────────────
# 查询 / 元数据检索
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_head_history_get_version(self) -> None:
        mgr = _mgr()
        mgr.commit_snapshot("ds1", _MANIFEST)
        s2 = mgr.commit_snapshot("ds1", {**_MANIFEST, "rows": 2})
        assert mgr.head("ds1") == s2
        assert [s.version_id for s in mgr.history("ds1")] == ["ds1@v0002", "ds1@v0001"]
        assert mgr.get_version("ds1", "ds1@v0001").manifest["rows"] == 1024

    def test_unknown_dataset_or_version_raise(self) -> None:
        mgr = _mgr()
        mgr.commit_snapshot("ds1", _MANIFEST)
        with pytest.raises(ResearchDataError):
            mgr.head("ghost")
        with pytest.raises(ResearchDataError):
            mgr.history("ghost")
        with pytest.raises(ResearchDataError):
            mgr.get_version("ds1", "ds1@v9999")
        with pytest.raises(ResearchDataError):
            mgr.get_version("ghost", "x")

    def test_list_datasets_sorted(self) -> None:
        mgr = _mgr()
        mgr.commit_snapshot("zeta", _MANIFEST)
        mgr.commit_snapshot("alpha", _MANIFEST)
        assert mgr.list_datasets() == ("alpha", "zeta")

    def test_search_match_sorted(self) -> None:
        mgr = _mgr()
        mgr.commit_snapshot("ds1", {**_MANIFEST, "kind": "kline"})
        mgr.commit_snapshot("ds2", {**_MANIFEST, "kind": "kline"})
        mgr.commit_snapshot("ds3", {**_MANIFEST, "kind": "tick"})
        out = mgr.search({"kind": "kline"})
        assert [s.dataset_id for s in out] == ["ds1", "ds2"]
        assert mgr.search({"kind": "ghost"}) == ()
        with pytest.raises(ResearchDataError):
            mgr.search({})


# ──────────────────────────────────────────────────────────────────────────────
# 保留策略（TTL 裁决）
# ──────────────────────────────────────────────────────────────────────────────


class TestRetention:
    def test_ttl_not_declared_fail_closed(self) -> None:
        mgr = _mgr()
        mgr.commit_snapshot("ds1", _MANIFEST)
        with pytest.raises(ResearchDataError):
            mgr.apply_retention()

    def test_invalid_ttl_raise(self) -> None:
        with pytest.raises(ResearchDataError):
            _mgr(retention_ttl=datetime.timedelta(0))

    def test_retention_decisions(self) -> None:
        clock = _Clock(_T0)
        ttl = datetime.timedelta(days=7)
        mgr = ResearchDataManager(clock=clock, retention_ttl=ttl)
        mgr.commit_snapshot("ds1", _MANIFEST)  # v0001 @T0
        clock.t = _T0 + datetime.timedelta(days=3)
        mgr.commit_snapshot("ds1", {**_MANIFEST, "rows": 2})  # v0002 @T0+3d
        clock.t = _T0 + datetime.timedelta(days=10)
        mgr.commit_snapshot("ds1", {**_MANIFEST, "rows": 3})  # v0003 @T0+10d（链头）
        decisions = mgr.apply_retention()
        assert [(d.version_id, d.keep) for d in decisions] == [
            ("ds1@v0001", False),  # 超期非链头
            ("ds1@v0002", True),  # 保留期内
            ("ds1@v0003", True),  # 链头恒保留
        ]
        assert decisions[0].reason.startswith("超过保留期")
