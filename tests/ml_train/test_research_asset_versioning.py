# [BLUEPRINT] MOD-ML-022 | docs/03_modules/_domain_machine_learning_train/research_asset_versioning/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ML-022 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_train.test_research_asset_versioning
# [TESTS] src/zephyr/ml_train/research_asset_versioning.py
"""MOD-ML-022 单元测试：research_asset_versioning 研究资产版本化管理器。

蓝图验收（B13-04341/CAND-MLT-030，A3 D-RESEARCH-18）：
因子/模型/策略三类统一 SemVer 校验 + 不可变版本记录（重复登记拒绝）+
资产/版本/指标三维复用索引（确定性排序）+ 跨项目复用登记。
时钟注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.ml_train.research_asset_versioning",
    reason="research_asset_versioning not importable",
)

from zephyr.ml_train.research_asset_versioning import (  # noqa: E402
    AssetKind,
    AssetVersionError,
    ResearchAssetVersioning,
)

_T0 = datetime.datetime(2026, 8, 25, 15, 0, 0)
_METRICS = {"ic": 0.083, "sharpe": 1.62}


def _reg(**kw) -> ResearchAssetVersioning:
    kw.setdefault("clock", lambda: _T0)
    return ResearchAssetVersioning(**kw)


def _factor(reg: ResearchAssetVersioning, version: str = "1.0.0", **kw):
    return reg.register_version(AssetKind.FACTOR, "mom20", version, dict(_METRICS), "proj-alpha", **kw)


# ──────────────────────────────────────────────────────────────────────────────
# 版本登记（三类统一 SemVer + 不可变记录）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_all_kinds(self) -> None:
        reg = _reg()
        f = _factor(reg)
        m = reg.register_version(AssetKind.MODEL, "qnn2s", "0.1.0", {"crps": 0.04}, "proj-alpha")
        s = reg.register_version(AssetKind.STRATEGY, "t0_band", "2.3.1", {"sharpe": 2.0}, "proj-beta")
        assert (f.kind, m.kind, s.kind) == (AssetKind.FACTOR, AssetKind.MODEL, AssetKind.STRATEGY)
        assert f.semver == (1, 0, 0)
        assert reg.list_assets() == ("mom20", "qnn2s", "t0_band")

    def test_bad_kind_raise(self) -> None:
        reg = _reg()
        with pytest.raises(AssetVersionError):
            reg.register_version("alpha", "mom20", "1.0.0", {}, "p")  # 词表外类别

    def test_empty_fields_raise(self) -> None:
        reg = _reg()
        with pytest.raises(AssetVersionError):
            reg.register_version(AssetKind.FACTOR, "", "1.0.0", {}, "p")
        with pytest.raises(AssetVersionError):
            reg.register_version(AssetKind.FACTOR, "mom20", "1.0.0", {}, "")

    @pytest.mark.parametrize("bad", ["1.2", "1.2.3.4", "v1.2.3", "1.2.x", "", "01.2.3", "1.2.3-rc1"])
    def test_invalid_semver_raise(self, bad: str) -> None:
        reg = _reg()
        with pytest.raises(AssetVersionError):
            reg.register_version(AssetKind.FACTOR, "mom20", bad, {}, "p")

    def test_edge_semver_ok(self) -> None:
        reg = _reg()
        assert _factor(reg, version="0.0.0").semver == (0, 0, 0)
        assert _factor(reg, version="1.20.3").semver == (1, 20, 3)

    def test_metrics_validation_raise(self) -> None:
        reg = _reg()
        with pytest.raises(AssetVersionError):
            reg.register_version(AssetKind.FACTOR, "mom20", "1.0.0", {"ic": "high"}, "p")
        with pytest.raises(AssetVersionError):
            reg.register_version(AssetKind.FACTOR, "mom20", "1.0.0", {"": 0.1}, "p")
        with pytest.raises(AssetVersionError):
            reg.register_version(AssetKind.FACTOR, "mom20", "1.0.0", {"ic": True}, "p")

    def test_duplicate_version_immutable(self) -> None:
        reg = _reg()
        _factor(reg)
        with pytest.raises(AssetVersionError):
            _factor(reg)  # 写后不可改：重复登记拒绝
        _factor(reg, version="1.0.1")  # 新版本号可登记
        assert len(reg.versions_of("mom20")) == 2

    def test_metrics_snapshot_isolated(self) -> None:
        reg = _reg()
        metrics = dict(_METRICS)
        rec = reg.register_version(AssetKind.FACTOR, "mom20", "1.0.0", metrics, "p")
        metrics["ic"] = 9.9  # 入参后续变异不影响记录
        assert rec.metrics["ic"] == 0.083


# ──────────────────────────────────────────────────────────────────────────────
# 三维复用索引（资产/版本/指标）
# ──────────────────────────────────────────────────────────────────────────────


class TestIndex:
    def test_get_and_unknown_raise(self) -> None:
        reg = _reg()
        _factor(reg)
        assert reg.get_version("mom20", "1.0.0").metrics["sharpe"] == 1.62
        with pytest.raises(AssetVersionError):
            reg.get_version("mom20", "9.9.9")
        with pytest.raises(AssetVersionError):
            reg.get_version("ghost", "1.0.0")

    def test_versions_of_semver_desc(self) -> None:
        reg = _reg()
        _factor(reg, version="1.2.0")
        _factor(reg, version="1.10.0")  # 数字序非字典序
        _factor(reg, version="1.0.0")
        assert [r.version for r in reg.versions_of("mom20")] == ["1.10.0", "1.2.0", "1.0.0"]
        assert reg.latest("mom20").version == "1.10.0"

    def test_latest_unknown_raise(self) -> None:
        with pytest.raises(AssetVersionError):
            _reg().latest("ghost")

    def test_list_assets_kind_filter(self) -> None:
        reg = _reg()
        _factor(reg)
        reg.register_version(AssetKind.MODEL, "qnn2s", "0.1.0", {}, "p")
        assert reg.list_assets(AssetKind.FACTOR) == ("mom20",)
        assert reg.list_assets(AssetKind.STRATEGY) == ()
        with pytest.raises(AssetVersionError):
            reg.list_assets("factor")  # 非法类别过滤

    def test_search_by_metric_range_and_order(self) -> None:
        reg = _reg()
        _factor(reg, version="1.0.0")  # ic 0.083
        reg.register_version(AssetKind.FACTOR, "mom20", "1.1.0", {"ic": 0.12}, "p")
        reg.register_version(AssetKind.FACTOR, "rev5", "1.0.0", {"ic": 0.05}, "p")
        reg.register_version(AssetKind.FACTOR, "noic", "1.0.0", {"sharpe": 1.0}, "p")
        out = reg.search_by_metric("ic", min_value=0.05, max_value=0.12)
        assert [(r.asset_id, r.version) for r in out] == [
            ("mom20", "1.1.0"),
            ("mom20", "1.0.0"),
            ("rev5", "1.0.0"),
        ]  # 指标降序

    def test_search_by_metric_invalid_raise(self) -> None:
        reg = _reg()
        with pytest.raises(AssetVersionError):
            reg.search_by_metric("")
        with pytest.raises(AssetVersionError):
            reg.search_by_metric("ic")  # 至少一端界
        with pytest.raises(AssetVersionError):
            reg.search_by_metric("ic", min_value=0.2, max_value=0.1)  # 区间非法
        assert reg.search_by_metric("ghost", min_value=0.0) == ()


# ──────────────────────────────────────────────────────────────────────────────
# 跨项目复用登记
# ──────────────────────────────────────────────────────────────────────────────


class TestReuse:
    def test_register_reuse_ok(self) -> None:
        reg = _reg()
        _factor(reg)
        reuse = reg.register_reuse("mom20", "1.0.0", "proj-alpha", "proj-beta", note="迁移")
        assert reuse.reuse_id == "reuse-0001"  # 确定性序号
        assert reuse.note == "迁移"

    def test_reuse_invalid_raise(self) -> None:
        reg = _reg()
        _factor(reg)
        with pytest.raises(AssetVersionError):
            reg.register_reuse("mom20", "9.9.9", "proj-alpha", "proj-beta")  # 未知版本
        with pytest.raises(AssetVersionError):
            reg.register_reuse("mom20", "1.0.0", "proj-ghost", "proj-beta")  # 来源项目不符
        with pytest.raises(AssetVersionError):
            reg.register_reuse("mom20", "1.0.0", "proj-alpha", "proj-alpha")  # 同项目
        with pytest.raises(AssetVersionError):
            reg.register_reuse("mom20", "1.0.0", "proj-alpha", "")  # 空目标

    def test_reuses_of_order_and_filter(self) -> None:
        reg = _reg()
        _factor(reg, version="1.0.0")
        _factor(reg, version="1.1.0")
        reg.register_reuse("mom20", "1.1.0", "proj-alpha", "proj-beta")
        reg.register_reuse("mom20", "1.0.0", "proj-alpha", "proj-gamma")
        reg.register_reuse("mom20", "1.0.0", "proj-alpha", "proj-delta")
        all_reuses = reg.reuses_of("mom20")
        assert [r.reuse_id for r in all_reuses] == ["reuse-0001", "reuse-0002", "reuse-0003"]
        v10 = reg.reuses_of("mom20", version="1.0.0")
        assert [r.to_project for r in v10] == ["proj-gamma", "proj-delta"]
        assert reg.reuses_of("ghost") == ()
