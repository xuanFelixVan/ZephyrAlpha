# [A_test] module_id: SRC-TST-2700 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT | docs/03_modules/_domain_governance/blueprint.md | §runtime-violation-snapshot
# [MODULE] tests.governance.audit.test_runtime_violation_snapshot
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_runtime_violation_snapshot.py — runtime_violation_snapshot 模块单测

#ARCH-GOV-CONVERGENCE-META Phase 3.4b（病根1 治本）

测试 zephyr.governance.audit.runtime_violation_snapshot 模块：
- generate_snapshot: 生成快照（mock subprocess 调 dashboard）
- save_snapshot / load_snapshot: 持久化往返
- compute_drift_count: 漂移类别数计算
- is_snapshot_fresh: 新鲜度判断
- compare_baseline_with_live: 完整对比

测试隔离：用 tmp_path + mock subprocess，不触碰生产 data/ 目录。
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.audit.runtime_violation_snapshot import (  # noqa: E402
    _CATEGORY_TO_METRIC,
    compare_baseline_with_live,
    compute_drift_count,
    generate_snapshot,
    is_snapshot_fresh,
    load_snapshot,
    save_snapshot,
)

# ---------------------------------------------------------------------------
# 辅助：构造 baseline YAML（最小化）
# ---------------------------------------------------------------------------

_BASELINE_YAML = """\
baseline_date: '2026-06-26'
trae_rule_id: TRAE-060
trae_rule_version: '1.0.1'
source_section: '§5 prohibitions'
extraction_date: '2026-07-19'
extraction_session: 'test'

violations:
  vocab_hardcode:
    rule: '禁止硬编码词表合法值'
    claimed_count: 64
    claim_text: '64处(2026-06-26)'
    detector_metric_id: M01
    detector_metric_name: '词表硬编码违规数'
    detector_script: check_vocab_hardcode.py
  time_trigger:
    rule: '禁止时间触发'
    claimed_count: 14
    claim_text: '14处(2026-06-26)'
    detector_metric_id: M10
    detector_metric_name: '时间触发残留数'
    detector_script: dashboard.py
  manual_trigger:
    rule: '禁止永久功能仅manual触发'
    claimed_count: 25
    claim_text: '~25处(2026-06-26)'
    detector_metric_id: M02
    detector_metric_name: 'manual-only 永久脚本数'
    detector_script: dashboard.py
  mergeable_clusters:
    rule: '重复簇MUST合并'
    claimed_count: 6
    claim_text: '6簇(2026-06-26)'
    detector_metric_id: M03
    detector_metric_name: '重复簇函数数'
    detector_script: dashboard.py

resolved_evidence: {}
summary:
  total_ongoing_claimed: 109
  total_resolved: 0
  baseline_frozen: true
"""


def _setup_baseline(tmp_path: Path) -> Path:
    """在 tmp_path 下创建 baseline YAML + 目录结构，返回 tmp_path。"""
    snapshot_dir = tmp_path / "data" / "runtime_violation_snapshot"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / "baseline_2026_06_26.yaml").write_text(_BASELINE_YAML, encoding="utf-8")
    return tmp_path


def _make_dashboard_stdout(metric_counts: dict[str, int]) -> str:
    """构造 dashboard --json 的 stdout（含 metrics 列表）。"""
    metrics_list = []
    name_map = {
        "M01": "词表硬编码违规数",
        "M02": "manual-only 永久脚本数",
        "M03": "重复簇函数数",
        "M10": "时间触发残留数",
    }
    for mid, count in metric_counts.items():
        metrics_list.append({
            "metric_id": mid,
            "name": name_map.get(mid, mid),
            "count": count,
            "target": 0,
            "details": [],
            "source": "test",
            "error": "",
        })
    return json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dashboard": "architecture_health",
        "phase": "test",
        "metrics": metrics_list,
        "total_auto": sum(metric_counts.values()),
        "manual_baseline_total": 3193,
        "note": "test mock",
    })


# ---------------------------------------------------------------------------
# 测试：generate_snapshot
# ---------------------------------------------------------------------------

class TestGenerateSnapshot:
    """generate_snapshot 函数测试。"""

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_generate_snapshot_basic_structure(self, mock_run, tmp_path):
        """生成快照包含所有必需字段。"""
        _setup_baseline(tmp_path)
        mock_run.return_value = (0, _make_dashboard_stdout({
            "M01": 0, "M02": 0, "M03": 3, "M10": 0
        }), "")

        snapshot = generate_snapshot(tmp_path, session_id="test-sess", commit_sha="abc123")

        assert snapshot["generated_by"] == "GATE-RUNTIME-VIOLATION-SNAPSHOT"
        assert snapshot["session_id"] == "test-sess"
        assert snapshot["commit_sha"] == "abc123"
        assert snapshot["trae_rule_id"] == "TRAE-060"
        assert snapshot["trae_rule_version"] == "1.0.1"
        assert len(snapshot["violations"]) == 4
        assert "summary" in snapshot

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_generate_snapshot_drift_calculation(self, mock_run, tmp_path):
        """drift = detected - claimed（负值表示已修复）。"""
        _setup_baseline(tmp_path)
        # claimed: vocab=64, time=14, manual=25, merge=6
        # detected: vocab=0, time=0, manual=0, merge=3
        mock_run.return_value = (0, _make_dashboard_stdout({
            "M01": 0, "M02": 0, "M03": 3, "M10": 0
        }), "")

        snapshot = generate_snapshot(tmp_path)

        vmap = {v["category"]: v for v in snapshot["violations"]}
        assert vmap["vocab_hardcode"]["drift"] == -64  # 0 - 64
        assert vmap["time_trigger"]["drift"] == -14  # 0 - 14
        assert vmap["manual_trigger"]["drift"] == -25  # 0 - 25
        assert vmap["mergeable_clusters"]["drift"] == -3  # 3 - 6

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_generate_snapshot_drift_count(self, mock_run, tmp_path):
        """drift_count = |drift|>0 的类别数。"""
        _setup_baseline(tmp_path)
        mock_run.return_value = (0, _make_dashboard_stdout({
            "M01": 64, "M02": 25, "M03": 6, "M10": 14
        }), "")  # 完全匹配，drift=0

        snapshot = generate_snapshot(tmp_path)
        assert snapshot["summary"]["drift_count"] == 0

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_generate_snapshot_new_violations(self, mock_run, tmp_path):
        """drift 正值表示新增违规。"""
        _setup_baseline(tmp_path)
        mock_run.return_value = (0, _make_dashboard_stdout({
            "M01": 100, "M02": 25, "M03": 6, "M10": 14
        }), "")  # vocab 新增 36 处

        snapshot = generate_snapshot(tmp_path)
        vmap = {v["category"]: v for v in snapshot["violations"]}
        assert vmap["vocab_hardcode"]["drift"] == 36  # 100 - 64
        assert snapshot["summary"]["drift_count"] == 1

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_generate_snapshot_dashboard_failure(self, mock_run, tmp_path):
        """dashboard 调用失败时降级为 detected=0 + error。"""
        _setup_baseline(tmp_path)
        mock_run.return_value = (-1, "", "dashboard not found")

        snapshot = generate_snapshot(tmp_path)

        # 所有 detected=0，drift = -claimed
        for v in snapshot["violations"]:
            assert v["detected_count"] == 0
            assert v["drift"] == -v["claimed_count"]
            assert v["detector_error"]  # 非空

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_generate_snapshot_baseline_missing(self, mock_run, tmp_path):
        """baseline 文件不存在时，claimed=0，drift=detected。"""
        # 不创建 baseline
        mock_run.return_value = (0, _make_dashboard_stdout({
            "M01": 5, "M02": 0, "M03": 0, "M10": 0
        }), "")

        snapshot = generate_snapshot(tmp_path)

        vmap = {v["category"]: v for v in snapshot["violations"]}
        assert vmap["vocab_hardcode"]["claimed_count"] == 0
        assert vmap["vocab_hardcode"]["detected_count"] == 5
        assert vmap["vocab_hardcode"]["drift"] == 5
        assert snapshot["trae_rule_version"] == "unknown"

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_generate_snapshot_never_raises(self, mock_run, tmp_path):
        """generate_snapshot 永不抛异常（fail-open）。"""
        _setup_baseline(tmp_path)
        mock_run.side_effect = RuntimeError("unexpected error")

        # 不应抛异常
        snapshot = generate_snapshot(tmp_path)
        assert "violations" in snapshot


# ---------------------------------------------------------------------------
# 测试：save_snapshot / load_snapshot
# ---------------------------------------------------------------------------

class TestSnapshotPersistence:
    """save_snapshot / load_snapshot 持久化测试。"""

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_save_and_load_roundtrip(self, mock_run, tmp_path):
        """保存后加载应得到相同数据。"""
        _setup_baseline(tmp_path)
        mock_run.return_value = (0, _make_dashboard_stdout({
            "M01": 1, "M02": 2, "M03": 3, "M10": 4
        }), "")

        snapshot = generate_snapshot(tmp_path, session_id="roundtrip-test")
        latest_path = save_snapshot(snapshot, tmp_path)

        assert latest_path.is_file()
        assert latest_path.name == "latest.json"

        loaded = load_snapshot(tmp_path)
        assert loaded["session_id"] == "roundtrip-test"
        assert loaded["summary"]["total_detected"] == 10
        assert len(loaded["violations"]) == 4

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_save_snapshot_creates_archive(self, mock_run, tmp_path):
        """save_snapshot 同时创建时间戳归档文件。"""
        _setup_baseline(tmp_path)
        mock_run.return_value = (0, _make_dashboard_stdout({
            "M01": 0, "M02": 0, "M03": 0, "M10": 0
        }), "")

        snapshot = generate_snapshot(tmp_path)
        save_snapshot(snapshot, tmp_path)

        archive_dir = tmp_path / "data" / "runtime_violation_snapshot"
        archives = list(archive_dir.glob("snapshot_*.json"))
        assert len(archives) >= 1

    def test_load_snapshot_missing_file(self, tmp_path):
        """latest.json 不存在时返回空 dict。"""
        result = load_snapshot(tmp_path)
        assert result == {}


# ---------------------------------------------------------------------------
# 测试：compute_drift_count
# ---------------------------------------------------------------------------

class TestComputeDriftCount:
    """compute_drift_count 测试。"""

    def test_zero_drift(self):
        """所有类别 drift=0 时返回 0。"""
        snapshot = {
            "summary": {"drift_count": 0},
            "violations": [
                {"category": "a", "drift": 0},
                {"category": "b", "drift": 0},
            ],
        }
        assert compute_drift_count(snapshot) == 0

    def test_nonzero_drift(self):
        """有 drift 的类别数。"""
        snapshot = {
            "summary": {"drift_count": 2},
            "violations": [
                {"category": "a", "drift": -5},
                {"category": "b", "drift": 0},
                {"category": "c", "drift": 3},
            ],
        }
        assert compute_drift_count(snapshot) == 2

    def test_empty_snapshot(self):
        """空 snapshot 返回 0。"""
        assert compute_drift_count({}) == 0
        assert compute_drift_count(None) == 0  # type: ignore[arg-type]

    def test_fallback_recount(self):
        """summary 无 drift_count 时从 violations 重算。"""
        snapshot = {
            "violations": [
                {"category": "a", "drift": -5},
                {"category": "b", "drift": 0},
            ],
        }
        assert compute_drift_count(snapshot) == 1


# ---------------------------------------------------------------------------
# 测试：is_snapshot_fresh
# ---------------------------------------------------------------------------

class TestIsSnapshotFresh:
    """is_snapshot_fresh 测试。"""

    def test_fresh_snapshot(self):
        """刚生成的快照是 fresh。"""
        now = datetime.now(timezone.utc).isoformat()
        snapshot = {"generated_at": now}
        assert is_snapshot_fresh(snapshot) is True

    def test_stale_snapshot(self):
        """超过 24h 的快照是 stale。"""
        old = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
        snapshot = {"generated_at": old}
        assert is_snapshot_fresh(snapshot) is False

    def test_no_generated_at(self):
        """无 generated_at 字段返回 False。"""
        assert is_snapshot_fresh({}) is False
        assert is_snapshot_fresh({"generated_at": ""}) is False

    def test_invalid_timestamp(self):
        """无效时间戳返回 False。"""
        snapshot = {"generated_at": "not-a-timestamp"}
        assert is_snapshot_fresh(snapshot) is False

    def test_custom_threshold(self):
        """自定义阈值。"""
        recent = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()
        snapshot = {"generated_at": recent}
        assert is_snapshot_fresh(snapshot, max_age_seconds=60) is True
        assert is_snapshot_fresh(snapshot, max_age_seconds=10) is False


# ---------------------------------------------------------------------------
# 测试：compare_baseline_with_live
# ---------------------------------------------------------------------------

class TestCompareBaselineWithLive:
    """compare_baseline_with_live 测试。"""

    def test_missing_snapshot(self, tmp_path):
        """latest.json 不存在时返回 drift=0 + error。"""
        _setup_baseline(tmp_path)
        result = compare_baseline_with_live(tmp_path)
        assert result["drift_count"] == 0
        assert result["fresh"] is False
        assert "not found" in result["error"]

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_fresh_with_drift(self, mock_run, tmp_path):
        """fresh 快照有 drift 时正确报告。"""
        _setup_baseline(tmp_path)
        mock_run.return_value = (0, _make_dashboard_stdout({
            "M01": 0, "M02": 0, "M03": 3, "M10": 0
        }), "")

        snapshot = generate_snapshot(tmp_path)
        save_snapshot(snapshot, tmp_path)

        result = compare_baseline_with_live(tmp_path)
        assert result["fresh"] is True
        assert result["drift_count"] == 4
        assert len(result["violations"]) == 4
        assert result["error"] == ""

    @patch("zephyr.governance.audit.runtime_violation_snapshot._run_dashboard")
    def test_stale_snapshot_reported(self, mock_run, tmp_path):
        """stale 快照（>24h）在 error 中报告。"""
        _setup_baseline(tmp_path)
        mock_run.return_value = (0, _make_dashboard_stdout({
            "M01": 0, "M02": 0, "M03": 0, "M10": 0
        }), "")

        snapshot = generate_snapshot(tmp_path)
        old = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
        snapshot["generated_at"] = old
        save_snapshot(snapshot, tmp_path)

        result = compare_baseline_with_live(tmp_path)
        assert result["fresh"] is False
        assert "stale" in result["error"]


# ---------------------------------------------------------------------------
# 测试：_CATEGORY_TO_METRIC 映射完整性
# ---------------------------------------------------------------------------

class TestCategoryMetricMapping:
    """类别 → metric_id 映射完整性测试。"""

    def test_all_four_categories_present(self):
        """4 类违规全部有映射。"""
        assert set(_CATEGORY_TO_METRIC.keys()) == {
            "vocab_hardcode", "time_trigger", "manual_trigger", "mergeable_clusters"
        }

    def test_metric_ids_valid(self):
        """映射的 metric_id 都是 dashboard 已有的。"""
        valid_ids = {"M01", "M02", "M03", "M10"}
        assert set(_CATEGORY_TO_METRIC.values()).issubset(valid_ids)
