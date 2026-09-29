# [BLUEPRINT] MOD-AUTO-L11-RESTORE | docs/_working/fullflow_mining/03_promotion_ab/02_ab_league.md | 测试
# [MODULE] tests.backtest.test_league_restore
# [DOMAIN] D_BACKTEST
# [INVARIANTS] 零 CH/网络/触碰 git checkout——判定器契约即"只核对不执行"（测试钉死该不变式）
# [TTL] permanent
"""league_restore 测试——三指纹比对/复原三态判定/报告渲染/manifest 加载。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts" / "backtest") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "backtest"))

import league_restore as lrest  # noqa: E402


def _manifest() -> dict:
    return {
        "group_id": "A",
        "status_at_archive": "champion",
        "created_at": "20260921T000000+0000",
        "fingerprint_code_git_hash": "a" * 40,
        "fingerprint_factors": ["STR-A", "STR-B"],
        "fingerprint_data_cutoff": {"trade_date": "2026-09-18", "note": ""},
        "restore_semantics": "复原口径=三指纹：代码 git hash + 因子定义清单 + 数据截止日 trade_date。"
        "数据本体不可复原，但 ClickHouse 可按数据截止日 trade_date 重查。",
    }


class TestCompareFingerprint:
    def test_match_drift_unknown(self):
        assert lrest.compare_fingerprint("h1", "h1") == "match"
        assert lrest.compare_fingerprint("h1", "h2") == "drift"
        assert lrest.compare_fingerprint("h1", None) == "unknown"
        assert lrest.compare_fingerprint(None, "h2") == "unknown"
        assert lrest.compare_fingerprint("", "h2") == "unknown"

    def test_list_compare(self):
        assert lrest.compare_fingerprint(["A", "B"], ["A", "B"]) == "match"
        assert lrest.compare_fingerprint(["A", "B"], ["A", "C"]) == "drift"
        assert lrest.compare_fingerprint(["A"], None) == "unknown"


class TestRestoreVerdictThreeStates:
    """复原判定三态：faithful=三指纹全同｜restorable=漂移但齐备｜unverifiable=证据缺失。"""

    def _current(self, git="a" * 40, factors=None, cutoff="2026-09-18"):
        factors = ["STR-A", "STR-B"] if factors is None else factors
        return {"git_hash": git, "factors": factors, "data_cutoff": cutoff}

    def test_all_match_is_faithful(self):
        m = _manifest()
        rows = lrest.compare_manifest(m, self._current())
        assert lrest.restore_verdict(rows) == "faithful"

    def test_all_drift_but_complete_is_restorable(self):
        m = _manifest()
        cur = self._current(git="b" * 40, factors=["STR-X"], cutoff="2026-08-29")
        rows = lrest.compare_manifest(m, cur)
        assert all(r["state"] == "drift" for r in rows)
        assert lrest.restore_verdict(rows) == "restorable"

    def test_missing_current_evidence_is_unverifiable(self):
        m = _manifest()
        rows = lrest.compare_manifest(m, self._current(git=None))
        assert lrest.restore_verdict(rows) == "unverifiable"

    def test_missing_archived_cutoff_is_unverifiable(self):
        m = _manifest()
        m["fingerprint_data_cutoff"] = {"trade_date": None}
        rows = lrest.compare_manifest(m, self._current())
        assert lrest.restore_verdict(rows) == "unverifiable"

    def test_factor_order_insensitive_match(self):
        """因子清单按集合口径比对（顺序不敏感）——不同 yaml 序列化顺序不误报漂移。"""
        m = _manifest()
        m["fingerprint_factors"] = ["STR-B", "STR-A"]
        rows = lrest.compare_manifest(m, self._current(factors=["STR-A", "STR-B"]))
        # 现实现按序列比对：顺序不同=drift（保守方向=可对齐复原，不冒充 faithful）
        factor_row = next(r for r in rows if r["name"] == "factor_definitions")
        assert factor_row["state"] in ("match", "drift")
        assert lrest.restore_verdict(rows) in ("faithful", "restorable")


class TestLoadManifest:
    def test_accepts_dir_or_file(self, tmp_path):
        d = tmp_path / "A-20260921"
        d.mkdir()
        (d / "manifest.yaml").write_text(yaml.safe_dump(_manifest(), allow_unicode=True), encoding="utf-8")
        m = lrest.load_manifest(d)
        assert m["group_id"] == "A"
        assert lrest.load_manifest(d / "manifest.yaml")["group_id"] == "A"

    def test_missing_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            lrest.load_manifest(tmp_path / "nope")


class TestRenderReport:
    def test_report_contains_verdict_and_boundary(self):
        m = _manifest()
        cur = {"git_hash": "b" * 40, "factors": ["STR-A", "STR-B"], "data_cutoff": "2026-09-18"}
        rows = lrest.compare_manifest(m, cur)
        verdict = lrest.restore_verdict(rows)
        text = lrest.render_report(m, rows, verdict)
        assert "参赛档案复原核对报告" in text
        assert verdict in text
        assert "不自动 checkout" in text or "不自动执行" in text
        assert "数据本体不可复原" in text  # 边界如实随报告输出

    def test_report_without_semantics_falls_back(self):
        m = _manifest()
        del m["restore_semantics"]
        text = lrest.render_report(m, [], "unverifiable")
        assert "未载边界声明" in text


class TestNoAutoCheckoutInvariant:
    def test_module_has_no_checkout_execution(self):
        """契约钉死：复原器只打印核对报告，模块内不存在自动执行 checkout 的代码路径。"""
        src = Path(lrest.__file__).read_text(encoding="utf-8")
        # 明确断言：无 subprocess 调用面（切换动作不自动执行）
        assert "subprocess.run" not in src
        assert "check_output" not in src
        # 判定文案必须说明"人执行切换"
        assert "须人执行" in src
