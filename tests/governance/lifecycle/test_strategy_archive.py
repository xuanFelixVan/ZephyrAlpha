# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.lifecycle.test_strategy_archive
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-TEST-GOV-ARCH | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""strategy_archive 归档/取回单元测试（61 号 §3.9 归档四件套第 ④ 条）。

覆盖:
  - 完整归档：manifest + params_snapshot + pnl_curve 三文件落盘，字段齐全
  - 最小归档（仅必填）：仅 manifest，files 清单正确
  - 重复归档 → StrategyArchiveError（只增不改防覆盖）
  - strategy_id 路径穿越/非法字符 → 拒
  - training_run_id / decay_knight 空 → 拒
  - 取回：manifest 字段 + files 清单；归档不存在 → 拒；畸形 manifest → 拒
  - list_archived_strategies：多策略排序；根目录不存在 → 空列表
"""

from __future__ import annotations

import json

import pytest

from zephyr.governance.lifecycle_governance.strategy_archive import (
    StrategyArchiveArtifacts,
    StrategyArchiveError,
    archive_strategy,
    list_archived_strategies,
    retrieve_strategy_archive,
)


def _artifacts(**kw):
    base = dict(
        training_run_id="run-abc-123",
        decay_knight="regime_change",
        reason="Rolling Sharpe < 0 持续 2 窗口，regime 失配",
    )
    base.update(kw)
    return StrategyArchiveArtifacts(**base)


class TestArchive:
    def test_full_archive(self, tmp_path):
        target = archive_strategy(
            "daban_v1",
            _artifacts(
                params_snapshot={"top_n": 10, "max_single": 0.1},
                pnl_curve=[("2026-01-02", 100.0), ("2026-01-05", -50.0)],
                extra={"operator": "night-batch"},
            ),
            archive_root=tmp_path,
        )
        assert target == tmp_path / "daban_v1"
        manifest = json.loads((target / "manifest.json").read_text("utf-8"))
        assert manifest["strategy_id"] == "daban_v1"
        assert manifest["training_run_id"] == "run-abc-123"
        assert manifest["decay_knight"] == "regime_change"
        assert manifest["operator"] == "night-batch"
        assert set(manifest["files"]) == {"manifest.json", "params_snapshot.json", "pnl_curve.csv"}
        params = json.loads((target / "params_snapshot.json").read_text("utf-8"))
        assert params["top_n"] == 10
        pnl_lines = (target / "pnl_curve.csv").read_text("utf-8").strip().splitlines()
        assert pnl_lines[0] == "date,pnl"
        assert len(pnl_lines) == 3

    def test_minimal_archive(self, tmp_path):
        target = archive_strategy("s1", _artifacts(), archive_root=tmp_path)
        manifest = json.loads((target / "manifest.json").read_text("utf-8"))
        assert manifest["files"] == ["manifest.json"]
        assert not (target / "params_snapshot.json").exists()
        assert not (target / "pnl_curve.csv").exists()

    def test_duplicate_archive_rejected(self, tmp_path):
        archive_strategy("s1", _artifacts(), archive_root=tmp_path)
        with pytest.raises(StrategyArchiveError):
            archive_strategy("s1", _artifacts(), archive_root=tmp_path)

    @pytest.mark.parametrize("bad", ["../escape", "a/b", "a\\b", "", "with space", "中文id"])
    def test_invalid_strategy_id(self, tmp_path, bad):
        with pytest.raises(StrategyArchiveError):
            archive_strategy(bad, _artifacts(), archive_root=tmp_path)

    @pytest.mark.parametrize("kw", [{"training_run_id": " "}, {"decay_knight": ""}])
    def test_missing_required_fields(self, tmp_path, kw):
        with pytest.raises(StrategyArchiveError):
            archive_strategy("s1", _artifacts(**kw), archive_root=tmp_path)


class TestRetrieve:
    def test_retrieve_roundtrip(self, tmp_path):
        archive_strategy("s1", _artifacts(params_snapshot={"a": 1}), archive_root=tmp_path)
        out = retrieve_strategy_archive("s1", archive_root=tmp_path)
        assert out["manifest"]["strategy_id"] == "s1"
        assert out["manifest"]["decay_knight"] == "regime_change"
        assert "manifest.json" in out["files"]
        assert "params_snapshot.json" in out["files"]

    def test_retrieve_missing(self, tmp_path):
        with pytest.raises(StrategyArchiveError):
            retrieve_strategy_archive("nope", archive_root=tmp_path)

    def test_retrieve_corrupt_manifest(self, tmp_path):
        target = tmp_path / "s1"
        target.mkdir()
        (target / "manifest.json").write_text("{not json", encoding="utf-8")
        with pytest.raises(StrategyArchiveError):
            retrieve_strategy_archive("s1", archive_root=tmp_path)


class TestList:
    def test_list_multiple_sorted(self, tmp_path):
        archive_strategy("b_strat", _artifacts(), archive_root=tmp_path)
        archive_strategy("a_strat", _artifacts(), archive_root=tmp_path)
        (tmp_path / "no_manifest_dir").mkdir()  # 无 manifest 不计入
        assert list_archived_strategies(archive_root=tmp_path) == ["a_strat", "b_strat"]

    def test_list_root_missing(self, tmp_path):
        assert list_archived_strategies(archive_root=tmp_path / "nonexistent") == []
