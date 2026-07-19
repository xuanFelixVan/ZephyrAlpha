# [A_test] module_id: SRC-TST-2703 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_commit_gateway_abuse_monitor | docs/03_modules/_domain_governance/blueprint.md | §ARCH-TOOL-HEALTH-V1 Phase 5b
# [MODULE] tests.governance.audit.test_commit_gateway_abuse_monitor_reconciler
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_commit_gateway_abuse_monitor_reconciler.py — reconciler 单测

ARCH-TOOL-HEALTH-V1 Phase 5b（commit gateway 持续滥用监控）

测试 make_commit_gateway_abuse_monitor_reconciler 工厂函数：
- factory 返回正确 ReconcilerSpec（gate_id, priority=875, callables）
- trigger 永远返回 True（任何 commit 都触发）
- _read_json_reports 按时间窗口过滤 + 跳过损坏 JSON
- _count_emergency_commits 统计 [GW:*:emergency] 标记（mock subprocess）
- _classify_abuse 五维分类纯函数（各维度独立触发 + 多维组合）
- reconcile: clean / warn / critical_warn 判定 + 永不抛异常 + 报告落盘

测试隔离：用 tmp_path + mock，不触碰生产 .runtime/ 目录。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.audit.reconciliation_registry import ReconcilerSpec  # noqa: E402
from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (  # noqa: E402
    _ALLOW_OVERLAP_7D_THRESHOLD,
    _EMERGENCY_24H_THRESHOLD,
    _FORGED_24H_THRESHOLD,
    _GATE_ID,
    _NON_GW_24H_THRESHOLD,
    _PRIORITY,
    _WARN_ONLY_24H_THRESHOLD,
    _classify_abuse,
    _count_emergency_commits,
    _read_json_reports,
    make_commit_gateway_abuse_monitor_reconciler,
)


class _FakeGateway:
    """模拟 GitCommitGateway，仅提供 project_root。"""

    def __init__(self, project_root: Path):
        self.project_root = project_root


def _write_report(repo_root: Path, prefix: str, timestamp: int, data: dict) -> None:
    """写入一个测试报告文件到 .runtime/reconcile_reports/{prefix}_{ts}.json。"""
    rdir = repo_root / ".runtime" / "reconcile_reports"
    rdir.mkdir(parents=True, exist_ok=True)
    path = rdir / f"{prefix}_{timestamp}.json"
    payload = {"timestamp": timestamp, **data}
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


# ============================================================================
# 工厂函数测试
# ============================================================================


class TestFactorySpec:
    """make_commit_gateway_abuse_monitor_reconciler 工厂返回值测试。"""

    def test_factory_returns_spec(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        assert isinstance(spec, ReconcilerSpec)
        assert spec.gate_id == _GATE_ID
        assert spec.priority == _PRIORITY

    def test_factory_priority_is_875(self):
        # priority=875: 晚于 git_performance_monitor(870)，早于 remediation_progress(900)
        assert _PRIORITY == 875

    def test_factory_gate_id(self):
        assert _GATE_ID == "GATE-COMMIT-GW-ABUSE-MONITOR"

    def test_trigger_always_true(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        # 任何 commit 都触发——滥用监控是全局关注
        assert spec.trigger([]) is True
        assert spec.trigger(["any/file.py"]) is True
        assert spec.trigger(["unrelated.txt"]) is True


# ============================================================================
# _read_json_reports 测试
# ============================================================================


class TestReadJsonReports:
    """_read_json_reports 时间窗口过滤 + 损坏 JSON 跳过测试。"""

    def test_empty_dir_returns_empty(self, tmp_path):
        # 目录不存在 → 空列表（fail-open）
        result = _read_json_reports(tmp_path, "post_commit_guard", since_ts=0)
        assert result == []

    def test_filters_by_since_ts(self, tmp_path):
        # 写入 3 个报告：1 个旧（ts=100）、2 个新（ts=200, 300）
        _write_report(tmp_path, "post_commit_guard", 100, {"action": "warn_only"})
        _write_report(tmp_path, "post_commit_guard", 200, {"action": "warn_only"})
        _write_report(tmp_path, "post_commit_guard", 300, {"action": "warn_only"})
        result = _read_json_reports(tmp_path, "post_commit_guard", since_ts=150)
        assert len(result) == 2
        timestamps = sorted(r["timestamp"] for r in result)
        assert timestamps == [200, 300]

    def test_skips_corrupted_json(self, tmp_path):
        # 写入 1 个有效 + 1 个损坏 JSON
        _write_report(tmp_path, "post_commit_guard", 100, {"action": "warn_only"})
        rdir = tmp_path / ".runtime" / "reconcile_reports"
        (rdir / "post_commit_guard_200.json").write_text("{invalid json", encoding="utf-8")
        result = _read_json_reports(tmp_path, "post_commit_guard", since_ts=0)
        assert len(result) == 1
        assert result[0]["action"] == "warn_only"

    def test_filters_by_prefix(self, tmp_path):
        # 不同前缀的报告不混读
        _write_report(tmp_path, "post_commit_guard", 100, {"action": "warn_only"})
        _write_report(tmp_path, "commit_gateway_audit", 100, {"violations_count": 5})
        result = _read_json_reports(tmp_path, "post_commit_guard", since_ts=0)
        assert len(result) == 1
        assert "action" in result[0]


# ============================================================================
# _count_emergency_commits 测试
# ============================================================================


class TestCountEmergencyCommits:
    """_count_emergency_commits 统计 [GW:*:emergency] 标记测试。"""

    def test_counts_emergency_markers(self, tmp_path):
        # 模拟 git log 返回 3 个 commit body，2 个含 [GW:*:emergency]
        bodies = [
            "feat: normal commit\n\n[GW:sess-123]",
            "feat: emergency commit\n\n[GW:sess-456:emergency]",
            "feat: another emergency\n\n[GW:sess-789:emergency]",
        ]
        mock_output = "\x1f".join(bodies) + "\x1f"

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result
            count = _count_emergency_commits(tmp_path, since_hours=24)
        assert count == 2

    def test_no_emergency_markers(self, tmp_path):
        bodies = [
            "feat: normal commit\n\n[GW:sess-123]",
            "feat: another normal\n\n[GW:sess-456:worktree]",
        ]
        mock_output = "\x1f".join(bodies) + "\x1f"

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result
            count = _count_emergency_commits(tmp_path, since_hours=24)
        assert count == 0

    def test_git_log_failure_returns_zero(self, tmp_path):
        # git log 失败 → 返回 0（fail-open）
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_run.return_value = mock_result
            count = _count_emergency_commits(tmp_path, since_hours=24)
        assert count == 0

    def test_timeout_returns_zero(self, tmp_path):
        # 超时 → 返回 0（fail-open）
        import subprocess
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=15)):
            count = _count_emergency_commits(tmp_path, since_hours=24)
        assert count == 0


# ============================================================================
# _classify_abuse 测试（纯函数，五维分类）
# ============================================================================


class TestClassifyAbuse:
    """_classify_abuse 五维分类纯函数测试。"""

    NOW_TS = 1784000000

    def test_no_abuse_returns_empty(self):
        # 所有指标都低于阈值
        result = _classify_abuse(
            post_commit_reports=[],
            audit_reports=[],
            emergency_count=0,
            now_ts=self.NOW_TS,
        )
        assert result["dimensions_triggered"] == []
        assert result["details"] == []
        assert result["metrics"]["warn_only_24h"] == 0

    def test_dimension1_warn_only_sustained(self):
        # 51 个 warn_only 事件（>50 阈值）
        reports = [
            {"timestamp": self.NOW_TS - 100, "action": "warn_only",
             "violation": "unregistered_session_id"}
            for _ in range(51)
        ]
        result = _classify_abuse(
            post_commit_reports=reports,
            audit_reports=[],
            emergency_count=0,
            now_ts=self.NOW_TS,
        )
        assert "warn_only_sustained_24h" in result["dimensions_triggered"]
        assert result["metrics"]["warn_only_24h"] == 51

    def test_dimension2_emergency_abuse(self):
        # 21 个 emergency commit（>20 阈值，R2 2026-07-20 #ARCH-ASYNC-MERGE-RECONCILE-001）
        result = _classify_abuse(
            post_commit_reports=[],
            audit_reports=[],
            emergency_count=21,
            now_ts=self.NOW_TS,
        )
        assert "emergency_commit_abuse_24h" in result["dimensions_triggered"]
        assert result["metrics"]["emergency_commit_24h"] == 21

    def test_dimension3_allow_overlap_abuse(self):
        # 501 个 gw_env=1 warn_only 事件（>500 阈值，7d 窗口，R2 2026-07-20 #ARCH-ASYNC-MERGE-RECONCILE-001）
        reports = [
            {"timestamp": self.NOW_TS - 100000, "action": "warn_only",
             "violation": "unregistered_session_id", "gw_env": "1"}
            for _ in range(501)
        ]
        result = _classify_abuse(
            post_commit_reports=reports,
            audit_reports=[],
            emergency_count=0,
            now_ts=self.NOW_TS,
        )
        assert "allow_overlap_abuse_7d" in result["dimensions_triggered"]
        assert result["metrics"]["allow_overlap_7d"] == 501

    def test_dimension4_forged_gw_marker(self):
        # 4 个 forged_gw_marker（>3 阈值）
        reports = [
            {"timestamp": self.NOW_TS - 100, "violation": "forged_gw_marker"}
            for _ in range(4)
        ]
        result = _classify_abuse(
            post_commit_reports=reports,
            audit_reports=[],
            emergency_count=0,
            now_ts=self.NOW_TS,
        )
        assert "forged_gw_marker_rate_24h" in result["dimensions_triggered"]
        assert result["metrics"]["forged_gw_marker_24h"] == 4

    def test_dimension5_non_gw_commit_sustained(self):
        # audit 报告 violations[].hash distinct = 11（>10 阈值）
        # P3 (2026-07-20, bc3cad107c): 改用 violations[].hash distinct 计数，
        # 替代旧 sum(violations_count)（避免多报告覆盖同一 commit 导致膨胀）。
        audit_reports = [
            {"timestamp": self.NOW_TS - 100,
             "violations": [{"hash": f"h{i}"} for i in range(5)]},
            {"timestamp": self.NOW_TS - 200,
             "violations": [{"hash": f"h{i}"} for i in range(5, 11)]},
        ]
        result = _classify_abuse(
            post_commit_reports=[],
            audit_reports=audit_reports,
            emergency_count=0,
            now_ts=self.NOW_TS,
        )
        assert "non_gw_commit_sustained_24h" in result["dimensions_triggered"]
        assert result["metrics"]["non_gw_commit_24h"] == 11

    def test_multiple_dimensions_triggered(self):
        # 同时触发维度1 + 维度2（R2 2026-07-20: emergency_count 6→21 适配新阈值 20）
        reports = [
            {"timestamp": self.NOW_TS - 100, "action": "warn_only",
             "violation": "unregistered_session_id"}
            for _ in range(51)
        ]
        result = _classify_abuse(
            post_commit_reports=reports,
            audit_reports=[],
            emergency_count=21,
            now_ts=self.NOW_TS,
        )
        assert len(result["dimensions_triggered"]) == 2
        assert "warn_only_sustained_24h" in result["dimensions_triggered"]
        assert "emergency_commit_abuse_24h" in result["dimensions_triggered"]

    def test_thresholds_in_metrics(self):
        # metrics 中包含所有阈值
        result = _classify_abuse([], [], 0, self.NOW_TS)
        thresholds = result["metrics"]["thresholds"]
        assert thresholds["warn_only_24h"] == _WARN_ONLY_24H_THRESHOLD
        assert thresholds["emergency_commit_24h"] == _EMERGENCY_24H_THRESHOLD
        assert thresholds["allow_overlap_7d"] == _ALLOW_OVERLAP_7D_THRESHOLD
        assert thresholds["forged_gw_marker_24h"] == _FORGED_24H_THRESHOLD
        assert thresholds["non_gw_commit_24h"] == _NON_GW_24H_THRESHOLD


# ============================================================================
# reconcile 集成测试
# ============================================================================


class TestReconcile:
    """reconcile 闭包集成测试（clean / warn / critical_warn 判定 + 报告落盘）。"""

    def test_reconcile_clean_no_abuse(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        with patch("zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._count_emergency_commits", return_value=0):
            result = spec.reconcile([], "sess-test")
        assert result.action == "clean"
        assert result.gate_id == _GATE_ID
        # 报告应落盘
        reports = list((tmp_path / ".runtime" / "reconcile_reports").glob("commit_gateway_abuse_monitor_*.json"))
        assert len(reports) == 1

    def test_reconcile_warn_single_dimension(self, tmp_path):
        # 触发 1 个维度 → warn
        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        # 写入 51 个 warn_only 报告
        now_ts = 1784000000
        with patch("time.time", return_value=now_ts), \
             patch("zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._count_emergency_commits", return_value=0):
            for i in range(51):
                _write_report(tmp_path, "post_commit_guard", now_ts - 100 - i, {
                    "action": "warn_only", "violation": "unregistered_session_id",
                })
            result = spec.reconcile([], "sess-test")
        assert result.action == "warn"
        # detail 含人类可读消息（含数值），dimensions_triggered 在报告文件中
        assert "51/24h" in result.detail
        reports = list((tmp_path / ".runtime" / "reconcile_reports").glob("commit_gateway_abuse_monitor_*.json"))
        data = json.loads(reports[0].read_text(encoding="utf-8"))
        assert "warn_only_sustained_24h" in data["dimensions_triggered"]

    def test_reconcile_critical_warn_three_dimensions(self, tmp_path):
        # 触发 3 个维度 → critical_warn
        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        now_ts = 1784000000
        with patch("time.time", return_value=now_ts), \
             patch("zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._count_emergency_commits", return_value=6):
            # 维度1: 51 warn_only
            for i in range(51):
                _write_report(tmp_path, "post_commit_guard", now_ts - 100 - i, {
                    "action": "warn_only", "violation": "unregistered_session_id",
                })
            # 维度3: 31 allow_overlap (gw_env=1)
            for i in range(31):
                _write_report(tmp_path, "post_commit_guard", now_ts - 200000 - i, {
                    "action": "warn_only", "violation": "unregistered_session_id", "gw_env": "1",
                })
            # 维度4: 4 forged_gw_marker
            for i in range(4):
                _write_report(tmp_path, "post_commit_guard", now_ts - 300 - i, {
                    "violation": "forged_gw_marker",
                })
            result = spec.reconcile([], "sess-test")
        assert result.action == "critical_warn"
        assert "ABUSE DETECTED" in result.detail

    def test_reconcile_critical_warn_forged_only(self, tmp_path):
        # 仅 forged_gw_marker 触发（4 个 > 3 阈值）→ critical_warn（forged 任何数量都 serious）
        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        now_ts = 1784000000
        with patch("time.time", return_value=now_ts), \
             patch("zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._count_emergency_commits", return_value=0):
            for i in range(4):
                _write_report(tmp_path, "post_commit_guard", now_ts - 100 - i, {
                    "violation": "forged_gw_marker",
                })
            result = spec.reconcile([], "sess-test")
        assert result.action == "critical_warn"
        # detail 含人类可读消息（含数值），dimensions_triggered 在报告文件中
        assert "4/24h" in result.detail
        reports = list((tmp_path / ".runtime" / "reconcile_reports").glob("commit_gateway_abuse_monitor_*.json"))
        data = json.loads(reports[0].read_text(encoding="utf-8"))
        assert "forged_gw_marker_rate_24h" in data["dimensions_triggered"]

    def test_reconcile_never_throws(self, tmp_path):
        # 异常 → 降级为 warn，不抛出
        # 注意：不能 mock time.time（logging 模块内部也调 time.time 做日志时间戳，
        # 会让 except 块的 logger.warning 也抛异常）。改 mock _read_json_reports 抛异常。
        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        with patch(
            "zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._read_json_reports",
            side_effect=OSError("disk full"),
        ):
            result = spec.reconcile([], "sess-test")
        assert result.action == "warn"
        assert "monitor failed" in result.detail

    def test_reconcile_writes_report_with_metrics(self, tmp_path):
        # 报告落盘并包含完整 metrics
        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        with patch("zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._count_emergency_commits", return_value=0):
            spec.reconcile([], "sess-test-123")
        reports = list((tmp_path / ".runtime" / "reconcile_reports").glob("commit_gateway_abuse_monitor_*.json"))
        assert len(reports) == 1
        data = json.loads(reports[0].read_text(encoding="utf-8"))
        assert data["gate_id"] == _GATE_ID
        assert data["session_id"] == "sess-test-123"
        assert "metrics" in data
        assert "thresholds" in data["metrics"]
