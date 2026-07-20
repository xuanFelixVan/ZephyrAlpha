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
import time
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
    _count_allow_overlap_usage,
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
        # 15 个 emergency commit（>10 阈值，裁定 #ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001 R1 过渡期 2026-07-19~2026-08-02）
        result = _classify_abuse(
            post_commit_reports=[],
            audit_reports=[],
            emergency_count=15,
            now_ts=self.NOW_TS,
        )
        assert "emergency_commit_abuse_24h" in result["dimensions_triggered"]
        assert result["metrics"]["emergency_commit_24h"] == 15

    def test_dimension3_allow_overlap_abuse(self):
        # 31 次真实 allow_overlap=True 提交（>30 阈值，7d 窗口，gate 层审计计数）
        result = _classify_abuse(
            post_commit_reports=[],
            audit_reports=[],
            emergency_count=0,
            now_ts=self.NOW_TS,
            allow_overlap_count=31,
        )
        assert "allow_overlap_abuse_7d" in result["dimensions_triggered"]
        assert result["metrics"]["allow_overlap_7d"] == 31

    def test_dimension3_below_threshold_not_triggered(self):
        # gate 层审计计数低于阈值 → 不触发（warn_only 报告数不再影响维度3）
        reports = [
            {"timestamp": self.NOW_TS - 100000, "action": "warn_only",
             "violation": "unregistered_session_id", "gw_env": "1"}
            for _ in range(31)
        ]
        result = _classify_abuse(
            post_commit_reports=reports,
            audit_reports=[],
            emergency_count=0,
            now_ts=self.NOW_TS,
            allow_overlap_count=0,
        )
        assert "allow_overlap_abuse_7d" not in result["dimensions_triggered"]
        assert result["metrics"]["allow_overlap_7d"] == 0

    def test_count_allow_overlap_usage(self, tmp_path):
        # gate 层审计 JSONL 计数：窗口内 2 条 + 窗口外 1 条 + 1 条损坏行
        audit_dir = tmp_path / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True)
        now = int(time.time())
        lines = [
            json.dumps({"timestamp": now - 100, "session_id": "s1", "files_count": 2}),
            json.dumps({"timestamp": now - 200, "session_id": "s2", "files_count": 1}),
            json.dumps({"timestamp": now - 8 * 24 * 3600, "session_id": "s3", "files_count": 1}),
            "{broken json",
        ]
        (audit_dir / "allow_overlap_usage.jsonl").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
        assert _count_allow_overlap_usage(tmp_path, now - 7 * 24 * 3600) == 2

    def test_count_allow_overlap_usage_missing_file(self, tmp_path):
        # 审计文件缺失 → fail-open 返回 0（无审计=无证据，不误报）
        assert _count_allow_overlap_usage(tmp_path, self.NOW_TS - 100) == 0

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
        # 同时触发维度1 + 维度2（emergency_count 15 > 10 阈值）
        reports = [
            {"timestamp": self.NOW_TS - 100, "action": "warn_only",
             "violation": "unregistered_session_id"}
            for _ in range(51)
        ]
        result = _classify_abuse(
            post_commit_reports=reports,
            audit_reports=[],
            emergency_count=15,
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


# ============================================================================
# P1-4 阈值回滚 smoke test（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）
# ============================================================================


class TestEmergencyThresholdRollback:
    """P1-4 治本：emergency_commit 24h 阈值回滚 10→5。

    历史：原阈值 5 → bc3cad107c 放松到 30（掩盖滥用）→ R1 过渡期 10
    → P1-4 治本（2026-07-20）：heartbeat 已落地 + P1-3 scenario 过滤已引入，
    dogfood/test/governance_fix 不再计入 24h 计数，production 场景真实
    emergency_commit 应 < 5/24h。直接回滚到 5（原值）。
    """

    def test_emergency_threshold_is_five(self):
        """阈值必须为 5（治本后原值，R1 过渡期 10 已撤销）。"""
        assert _EMERGENCY_24H_THRESHOLD == 5, (
            f"P1-4 治本：_EMERGENCY_24H_THRESHOLD 应为 5（原值），"
            f"实际为 {_EMERGENCY_24H_THRESHOLD}。"
            f"若值不是 5，说明 R1 过渡期阈值未回滚，或 P1-3 scenario 过滤未生效。"
        )

    def test_emergency_count_six_triggers_abuse(self):
        """6 > 5 阈值 → 触发维度2（验证回滚后阈值边界）。"""
        result = _classify_abuse(
            post_commit_reports=[],
            audit_reports=[],
            emergency_count=6,
            now_ts=1784000000,
        )
        assert "emergency_commit_abuse_24h" in result["dimensions_triggered"]
        assert result["metrics"]["emergency_commit_24h"] == 6

    def test_emergency_count_five_does_not_trigger(self):
        """5 == 5 阈值（不 > 阈值）→ 不触发（边界值验证）。"""
        result = _classify_abuse(
            post_commit_reports=[],
            audit_reports=[],
            emergency_count=5,
            now_ts=1784000000,
        )
        assert "emergency_commit_abuse_24h" not in result["dimensions_triggered"]


# ============================================================================
# P3-1 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
# _load_thresholds_from_yaml YAML 加载 smoke test
# ============================================================================


class TestLoadThresholdsFromYaml:
    """P3-1 治本：阈值从 trae_069 YAML 加载（SSoT 铁律：规则数据真源是 YAML）。

    治本原因：原 5 维阈值散落在代码常量（_WARN_ONLY_24H_THRESHOLD = 50 等），
    修改需改代码 + 重新部署。改为从 YAML 加载（trae_062 SSoT 铁律：规则数据
    真源是 YAML 文件），修改只需改 YAML + sync，无需改代码。

    fail-open：YAML 缺失/解析失败时返回 _DEFAULT_THRESHOLDS（不阻断 reconciler）。
    """

    def test_yaml_file_exists(self):
        """trae_069 YAML 文件必须存在（SSoT 真源铁律）。"""
        from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (
            _THRESHOLDS_YAML_PATH,
        )
        assert _THRESHOLDS_YAML_PATH.exists(), (
            f"P3-1 治本：trae_069 YAML 必须存在（SSoT 真源），"
            f"路径: {_THRESHOLDS_YAML_PATH}"
        )

    def test_load_returns_all_5_dimensions(self):
        """_load_thresholds_from_yaml 返回 5 个维度的阈值。"""
        from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (
            _load_thresholds_from_yaml, _DEFAULT_THRESHOLDS,
        )
        thresholds = _load_thresholds_from_yaml()
        assert set(thresholds.keys()) == set(_DEFAULT_THRESHOLDS.keys()), (
            f"应返回 5 个维度，实际: {set(thresholds.keys())}"
        )
        # 每个维度值必须为非负 int
        for dim, value in thresholds.items():
            assert isinstance(value, int), f"{dim} 应为 int，实际: {type(value)}"
            assert value > 0, f"{dim} 应 > 0，实际: {value}"

    def test_yaml_values_match_code_constants(self):
        """YAML 加载的值必须与代码常量一致（启动时已加载）。"""
        from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (
            _WARN_ONLY_24H_THRESHOLD, _EMERGENCY_24H_THRESHOLD,
            _ALLOW_OVERLAP_7D_THRESHOLD, _FORGED_24H_THRESHOLD,
            _NON_GW_24H_THRESHOLD, _load_thresholds_from_yaml,
        )
        yaml_thresholds = _load_thresholds_from_yaml()
        assert _WARN_ONLY_24H_THRESHOLD == yaml_thresholds["warn_only_sustained_24h"]
        assert _EMERGENCY_24H_THRESHOLD == yaml_thresholds["emergency_commit_abuse_24h"]
        assert _ALLOW_OVERLAP_7D_THRESHOLD == yaml_thresholds["allow_overlap_abuse_7d"]
        assert _FORGED_24H_THRESHOLD == yaml_thresholds["forged_gw_marker_rate_24h"]
        assert _NON_GW_24H_THRESHOLD == yaml_thresholds["non_gw_commit_sustained_24h"]

    def test_default_thresholds_match_p1_values(self):
        """_DEFAULT_THRESHOLDS 必须与 P1 治本后的值一致（回归保护）。"""
        from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (
            _DEFAULT_THRESHOLDS,
        )
        assert _DEFAULT_THRESHOLDS["warn_only_sustained_24h"] == 50
        assert _DEFAULT_THRESHOLDS["emergency_commit_abuse_24h"] == 5  # P1-4 治本
        assert _DEFAULT_THRESHOLDS["allow_overlap_abuse_7d"] == 30
        assert _DEFAULT_THRESHOLDS["forged_gw_marker_rate_24h"] == 3
        assert _DEFAULT_THRESHOLDS["non_gw_commit_sustained_24h"] == 10

    def test_load_fail_open_on_missing_file(self, tmp_path, monkeypatch):
        """YAML 文件缺失 → fail-open 返回默认值（不抛异常）。"""
        from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (
            _load_thresholds_from_yaml, _DEFAULT_THRESHOLDS,
        )
        # mock 路径为不存在的临时目录
        monkeypatch.setattr(
            "zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._THRESHOLDS_YAML_PATH",
            tmp_path / "nonexistent.yaml",
        )
        result = _load_thresholds_from_yaml()
        assert result == _DEFAULT_THRESHOLDS, "YAML 缺失时应返回默认值"

    def test_load_fail_open_on_invalid_yaml(self, tmp_path, monkeypatch):
        """YAML 解析失败 → fail-open 返回默认值（不抛异常）。"""
        from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (
            _load_thresholds_from_yaml, _DEFAULT_THRESHOLDS,
        )
        # 创建一个无效的 YAML 文件
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("{invalid yaml content", encoding="utf-8")
        monkeypatch.setattr(
            "zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._THRESHOLDS_YAML_PATH",
            bad_yaml,
        )
        result = _load_thresholds_from_yaml()
        assert result == _DEFAULT_THRESHOLDS, "YAML 解析失败时应返回默认值"

    def test_load_handles_invalid_threshold_value(self, tmp_path, monkeypatch):
        """YAML 中某维度值无效（非 int 或 < 0）→ 用默认值替换该维度。"""
        from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (
            _load_thresholds_from_yaml, _DEFAULT_THRESHOLDS,
        )
        # 创建一个有无效值的 YAML
        invalid_yaml = tmp_path / "invalid_threshold.yaml"
        invalid_yaml.write_text(
            "thresholds:\n"
            "  warn_only_sustained_24h:\n"
            "    value: -5  # 负值，无效\n"
            "  emergency_commit_abuse_24h:\n"
            "    value: \"not_an_int\"  # 字符串，无效\n"
            "  allow_overlap_abuse_7d:\n"
            "    value: 99  # 有效，保留\n"
            "  forged_gw_marker_rate_24h:\n"
            "    value: 1  # 有效，保留\n"
            "  non_gw_commit_sustained_24h:\n"
            "    value: 5  # 有效，保留\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(
            "zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._THRESHOLDS_YAML_PATH",
            invalid_yaml,
        )
        result = _load_thresholds_from_yaml()
        # 无效维度用默认值替换
        assert result["warn_only_sustained_24h"] == _DEFAULT_THRESHOLDS["warn_only_sustained_24h"]
        assert result["emergency_commit_abuse_24h"] == _DEFAULT_THRESHOLDS["emergency_commit_abuse_24h"]
        # 有效维度保留 YAML 值
        assert result["allow_overlap_abuse_7d"] == 99
        assert result["forged_gw_marker_rate_24h"] == 1
        assert result["non_gw_commit_sustained_24h"] == 5


# ============================================================================
# P1-3 scenario 过滤 smoke test（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）
# ============================================================================


class TestCountEmergencyCommitsScenarioFilter:
    """P1-3 治本：_count_emergency_commits 按 [SCENARIO:production] 过滤。

    治本原因：dogfood/test/governance_fix 场景的 emergency_commit 不应计入
    24h 滥用计数（治本工作本身可能多次 emergency_commit，污染真实滥用信号）。

    过滤规则：
      - 含 [SCENARIO:production] → 计入
      - 不含 [SCENARIO:...] 标记 → 计入（向后兼容旧 commit）
      - 含 [SCENARIO:dogfood] / [SCENARIO:test] / [SCENARIO:governance_fix] → 豁免
    """

    def test_production_scenario_counted(self, tmp_path):
        """含 [SCENARIO:production] 的 emergency_commit 计入。"""
        bodies = [
            "fix: P0\n\n[GW:sess-1:emergency]\n[SCENARIO:production]",
        ]
        mock_output = "\x1f".join(bodies) + "\x1f"
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result
            count = _count_emergency_commits(tmp_path, since_hours=24)
        assert count == 1

    def test_no_scenario_marker_backward_compatible(self, tmp_path):
        """无 [SCENARIO:...] 标记的旧 commit 视为 production（向后兼容）。"""
        bodies = [
            "fix: legacy emergency\n\n[GW:sess-old:emergency]",
            "fix: another legacy\n\n[GW:sess-old2:emergency]",
        ]
        mock_output = "\x1f".join(bodies) + "\x1f"
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result
            count = _count_emergency_commits(tmp_path, since_hours=24)
        assert count == 2, "无 scenario 标记的旧 commit 应计入（向后兼容）"

    def test_dogfood_scenario_exempted(self, tmp_path):
        """[SCENARIO:dogfood] 豁免（治本工作污染防护）。"""
        bodies = [
            "fix: dogfood emergency\n\n[GW:sess-d1:emergency]\n[SCENARIO:dogfood]",
            "fix: another dogfood\n\n[GW:sess-d2:emergency]\n[SCENARIO:dogfood]",
            "fix: real production\n\n[GW:sess-p1:emergency]\n[SCENARIO:production]",
        ]
        mock_output = "\x1f".join(bodies) + "\x1f"
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result
            count = _count_emergency_commits(tmp_path, since_hours=24)
        assert count == 1, "dogfood 应豁免，只统计 1 个 production"

    def test_test_scenario_exempted(self, tmp_path):
        """[SCENARIO:test] 豁免（测试场景不计入生产滥用）。"""
        bodies = [
            "test: emergency path\n\n[GW:sess-t1:emergency]\n[SCENARIO:test]",
            "test: another\n\n[GW:sess-t2:emergency]\n[SCENARIO:test]",
        ]
        mock_output = "\x1f".join(bodies) + "\x1f"
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result
            count = _count_emergency_commits(tmp_path, since_hours=24)
        assert count == 0, "test 场景应豁免"

    def test_governance_fix_scenario_exempted(self, tmp_path):
        """[SCENARIO:governance_fix] 豁免（治理修复工作不计入滥用）。"""
        bodies = [
            "fix: governance repair\n\n[GW:sess-g1:emergency]\n[SCENARIO:governance_fix]",
        ]
        mock_output = "\x1f".join(bodies) + "\x1f"
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result
            count = _count_emergency_commits(tmp_path, since_hours=24)
        assert count == 0, "governance_fix 场景应豁免"

    def test_mixed_scenarios_only_production_counted(self, tmp_path):
        """混合场景：只统计 production，其余豁免。"""
        bodies = [
            "fix: prod\n\n[GW:sess-1:emergency]\n[SCENARIO:production]",
            "fix: dogfood\n\n[GW:sess-2:emergency]\n[SCENARIO:dogfood]",
            "fix: test\n\n[GW:sess-3:emergency]\n[SCENARIO:test]",
            "fix: legacy (no marker)\n\n[GW:sess-4:emergency]",
            "fix: gov_fix\n\n[GW:sess-5:emergency]\n[SCENARIO:governance_fix]",
            "fix: prod2\n\n[GW:sess-6:emergency]\n[SCENARIO:production]",
        ]
        mock_output = "\x1f".join(bodies) + "\x1f"
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_output
            mock_run.return_value = mock_result
            count = _count_emergency_commits(tmp_path, since_hours=24)
        assert count == 3, (
            "应只统计 2 个 production + 1 个 legacy（无标记，向后兼容）= 3"
        )


# ============================================================================
# P1-1 _count_allow_overlap_usage 集成 smoke test
# （#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）
# ============================================================================


class TestReconcileCallsAllowOverlapUsage:
    """P1-1 治本：reconcile 必须调用 _count_allow_overlap_usage 并传入 _classify_abuse。

    治本原因：原实现未调用 _count_allow_overlap_usage，allow_overlap_count 默认 0，
    导致维度3 永远不触发。实际误报来自 warn_only+gw_env=1 反推（94.9% 误报率）。

    现改为：reconcile 读取 gate 层审计 .runtime/gate_audit/allow_overlap_usage.jsonl，
    将真实 allow_overlap=True 计数传入 _classify_abuse。
    """

    def test_reconcile_calls_count_allow_overlap_usage(self, tmp_path):
        """reconcile 必须调用 _count_allow_overlap_usage（验证调用链不缺失）。"""
        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        with patch("zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._count_emergency_commits", return_value=0), \
             patch(
                 "zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._count_allow_overlap_usage",
                 return_value=0,
             ) as mock_count:
            spec.reconcile([], "sess-p1-1")
        # 必须被调用（P1-1 修复点：原实现缺失此调用）
        assert mock_count.called, (
            "P1-1 治本失败：reconcile 未调用 _count_allow_overlap_usage，"
            "维度3 永远不会触发。请检查 commit_gateway_abuse_monitor_reconciler.py L388 附近的调用。"
        )

    def test_reconcile_passes_allow_overlap_count_to_classify(self, tmp_path):
        """reconcile 必须将 _count_allow_overlap_usage 返回值传入 _classify_abuse。

        场景：审计文件有 35 条记录（>30 阈值）→ 维度3 应触发。
        """
        # 准备审计文件（35 条，全部在 7d 窗口内）
        audit_dir = tmp_path / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True)
        now = int(time.time())
        lines = [
            json.dumps({"timestamp": now - 100, "session_id": f"s{i}", "files_count": 1})
            for i in range(35)
        ]
        (audit_dir / "allow_overlap_usage.jsonl").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        with patch("zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._count_emergency_commits", return_value=0), \
             patch("time.time", return_value=now):
            spec.reconcile([], "sess-p1-1-integration")

        # 验证报告落盘且 metrics.allow_overlap_7d = 35（不是 0）
        reports = list((tmp_path / ".runtime" / "reconcile_reports").glob(
            "commit_gateway_abuse_monitor_*.json"
        ))
        assert len(reports) == 1
        data = json.loads(reports[0].read_text(encoding="utf-8"))
        assert data["metrics"]["allow_overlap_7d"] == 35, (
            f"P1-1 治本失败：allow_overlap_7d 应为 35（gate 层审计计数），"
            f"实际为 {data['metrics']['allow_overlap_7d']}（0 = 调用链未生效）。"
        )
        assert "allow_overlap_abuse_7d" in data["dimensions_triggered"], (
            "P1-1 治本失败：35 > 30 阈值应触发维度3，但未触发。"
        )

    def test_reconcile_no_audit_file_no_false_positive(self, tmp_path):
        """审计文件缺失 → allow_overlap_7d=0，不触发维度3（fail-open 不误报）。

        治本前：原实现以 warn_only+gw_env=1 反推，导致 1829/7d 持续误报。
        治本后：无审计=无证据，不触发维度3。
        """
        # 不创建审计文件（模拟新部署或无 allow_overlap 使用）
        gw = _FakeGateway(tmp_path)
        spec = make_commit_gateway_abuse_monitor_reconciler(gw)
        now = int(time.time())
        with patch("zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler._count_emergency_commits", return_value=0), \
             patch("time.time", return_value=now):
            # 即使有 warn_only+gw_env=1 报告，也不应触发维度3（不再反推）
            for i in range(100):
                _write_report(tmp_path, "post_commit_guard", now - 100 - i, {
                    "action": "warn_only",
                    "violation": "unregistered_session_id",
                    "gw_env": "1",
                })
            spec.reconcile([], "sess-p1-1-clean")

        reports = list((tmp_path / ".runtime" / "reconcile_reports").glob(
            "commit_gateway_abuse_monitor_*.json"
        ))
        data = json.loads(reports[0].read_text(encoding="utf-8"))
        assert data["metrics"]["allow_overlap_7d"] == 0, (
            "fail-open：审计文件缺失时 allow_overlap_7d 应为 0"
        )
        assert "allow_overlap_abuse_7d" not in data["dimensions_triggered"], (
            "P1-1 治本失败：无审计文件时不应触发维度3（原 warn_only+gw_env=1 反推已废止）。"
        )
