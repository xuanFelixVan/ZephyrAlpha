# [A_test] module_id: SRC-TST-2702 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_git_performance_monitor | docs/03_modules/_domain_governance/blueprint.md | §ARCH-GIT-CALL-BUDGET P3.5
# [MODULE] tests.governance.audit.test_git_performance_monitor_reconciler
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_git_performance_monitor_reconciler.py — reconciler 单测

ARCH-GIT-CALL-BUDGET P3.5（git status 计时持续监控 + 早期预警）

测试 make_git_performance_monitor_reconciler 工厂函数：
- factory 返回正确 ReconcilerSpec（gate_id, priority=870, callables）
- trigger 永远返回 True（任何 commit 都触发）
- _measure_git_status 返回 (elapsed, rc, stderr) 三元组
- _count_stale_worktrees 统计 .aidrafts/sess-* 目录
- _append_perf_log / _read_recent_perf_entries JSONL 读写
- _detect_degradation_trend 连续递增判定
- reconcile 成功返回 clean，git status 慢返回 warn
- reconcile 永不抛异常

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
from zephyr.governance.audit.git_performance_monitor_reconciler import (  # noqa: E402
    _DEGRADATION_TREND_COUNT,
    _GATE_ID,
    _PERF_LOG_SUBPATH,
    _PRIORITY,
    _STALE_WORKTREE_WARN_THRESHOLD,
    _STATUS_FAIL_SECONDS,
    _STATUS_WARN_SECONDS,
    _append_perf_log,
    _count_stale_worktrees,
    _detect_degradation_trend,
    _measure_git_status,
    _read_recent_perf_entries,
    make_git_performance_monitor_reconciler,
)


class _FakeGateway:
    """模拟 GitCommitGateway，仅提供 project_root / _run_git。"""

    def __init__(self, project_root: Path, head_sha: str = "abc1234567"):
        self.project_root = project_root
        self._head_sha = head_sha

    def _run_git(self, cmd: list[str]):
        mock = MagicMock()
        mock.returncode = 0
        mock.stderr = ""
        if "rev-parse" in cmd and "HEAD" in cmd:
            mock.stdout = self._head_sha
        else:
            mock.stdout = ""
        return mock


class TestFactorySpec:
    """make_git_performance_monitor_reconciler 工厂返回值测试。"""

    def test_factory_returns_spec(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)
        assert isinstance(spec, ReconcilerSpec)

    def test_factory_gate_id(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)
        assert spec.gate_id == _GATE_ID
        assert spec.gate_id == "GATE-GIT-PERFORMANCE-MONITOR"

    def test_factory_priority(self, tmp_path):
        """priority=870：晚于 runtime_violation_snapshot(850)，早于 remediation_progress(900)。"""
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)
        assert spec.priority == _PRIORITY
        assert spec.priority == 870

    def test_factory_callables(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)
        assert callable(spec.trigger)
        assert callable(spec.reconcile)


class TestTrigger:
    """trigger 永远返回 True（性能监控是全局关注，不限文件类型）。"""

    def test_trigger_with_py_files(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        assert spec.trigger(files) is True

    def test_trigger_with_yaml_files(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)
        files = [str(tmp_path / "docs" / "trae_064.yaml")]
        assert spec.trigger(files) is True

    def test_trigger_with_md_files(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)
        files = [str(tmp_path / "README.md")]
        assert spec.trigger(files) is True

    def test_trigger_empty_files_still_triggers(self, tmp_path):
        """空文件列表也触发——性能监控是全局关注。"""
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)
        assert spec.trigger([]) is True


class TestMeasureGitStatus:
    """_measure_git_status 函数测试。"""

    def test_measure_returns_three_tuple(self, tmp_path):
        """返回 (elapsed, rc, stderr) 三元组。"""
        elapsed, rc, stderr = _measure_git_status(tmp_path)
        assert isinstance(elapsed, float)
        assert isinstance(rc, int)
        assert isinstance(stderr, str)

    def test_measure_nonexistent_dir_returns_error_rc(self, tmp_path):
        """不存在的目录返回非零 rc。"""
        bogus = tmp_path / "nonexistent_dir_xyz"
        elapsed, rc, stderr = _measure_git_status(bogus)
        assert rc != 0
        assert elapsed >= 0.0


class TestCountStaleWorktrees:
    """_count_stale_worktrees 函数测试。"""

    def test_count_zero_when_no_aidrafts(self, tmp_path):
        """.aidrafts/ 不存在时返回 0。"""
        assert _count_stale_worktrees(tmp_path) == 0

    def test_count_zero_when_empty_aidrafts(self, tmp_path):
        """.aidrafts/ 为空目录时返回 0。"""
        (tmp_path / ".aidrafts").mkdir()
        assert _count_stale_worktrees(tmp_path) == 0

    def test_count_sess_dirs(self, tmp_path):
        """统计 .aidrafts/sess-* 目录数。"""
        drafts = tmp_path / ".aidrafts"
        drafts.mkdir()
        (drafts / "sess-001").mkdir()
        (drafts / "sess-002").mkdir()
        (drafts / "sess-003").mkdir()
        assert _count_stale_worktrees(tmp_path) == 3

    def test_count_ignores_non_sess_dirs(self, tmp_path):
        """非 sess-* 前缀目录不计入。"""
        drafts = tmp_path / ".aidrafts"
        drafts.mkdir()
        (drafts / "sess-001").mkdir()
        (drafts / "other-dir").mkdir()
        (drafts / "tmp").mkdir()
        assert _count_stale_worktrees(tmp_path) == 1

    def test_count_ignores_files(self, tmp_path):
        """文件不计入（仅统计 is_dir()）。"""
        drafts = tmp_path / ".aidrafts"
        drafts.mkdir()
        (drafts / "sess-001").mkdir()
        (drafts / "sess-not-a-dir.txt").write_text("ignore me", encoding="utf-8")
        assert _count_stale_worktrees(tmp_path) == 1


class TestPerfLog:
    """_append_perf_log / _read_recent_perf_entries 测试。"""

    def test_append_creates_log_file(self, tmp_path):
        """首次写入创建 .runtime/git_performance_log.jsonl。"""
        entry = {"ts": "2026-07-19T00:00:00Z", "elapsed_s": 0.5}
        _append_perf_log(tmp_path, entry)
        log_path = tmp_path / Path(_PERF_LOG_SUBPATH)
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert json.loads(content.strip()) == entry

    def test_append_appends_jsonl(self, tmp_path):
        """多次写入追加到同一文件（JSONL 格式）。"""
        _append_perf_log(tmp_path, {"ts": "t1", "elapsed_s": 0.1})
        _append_perf_log(tmp_path, {"ts": "t2", "elapsed_s": 0.2})
        _append_perf_log(tmp_path, {"ts": "t3", "elapsed_s": 0.3})
        log_path = tmp_path / Path(_PERF_LOG_SUBPATH)
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3
        assert json.loads(lines[0])["ts"] == "t1"
        assert json.loads(lines[2])["ts"] == "t3"

    def test_read_recent_returns_empty_when_no_log(self, tmp_path):
        """日志不存在时返回空列表。"""
        assert _read_recent_perf_entries(tmp_path, 5) == []

    def test_read_recent_returns_last_n(self, tmp_path):
        """读取最近 N 条（用 deque maxlen 限制）。"""
        for i in range(5):
            _append_perf_log(tmp_path, {"ts": f"t{i}", "elapsed_s": float(i)})
        recent = _read_recent_perf_entries(tmp_path, 3)
        assert len(recent) == 3
        assert recent[0]["ts"] == "t2"
        assert recent[2]["ts"] == "t4"

    def test_read_recent_skips_corrupt_lines(self, tmp_path):
        """损坏的 JSON 行被跳过。"""
        log_path = tmp_path / Path(_PERF_LOG_SUBPATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            json.dumps({"ts": "t1", "elapsed_s": 0.1}) + "\n"
            + "CORRUPT_NOT_JSON\n"
            + json.dumps({"ts": "t2", "elapsed_s": 0.2}) + "\n",
            encoding="utf-8",
        )
        recent = _read_recent_perf_entries(tmp_path, 10)
        assert len(recent) == 2
        assert recent[0]["ts"] == "t1"
        assert recent[1]["ts"] == "t2"


class TestDetectDegradationTrend:
    """_detect_degradation_trend 函数测试。"""

    def test_no_data_returns_false(self):
        """空数据返回 (False, [])。"""
        is_degrading, times = _detect_degradation_trend([])
        assert is_degrading is False
        assert times == []

    def test_insufficient_data_returns_false(self):
        """数据少于 _DEGRADATION_TREND_COUNT 返回 False。"""
        entries = [{"elapsed_s": 0.1}, {"elapsed_s": 0.2}]
        if _DEGRADATION_TREND_COUNT > 2:
            is_degrading, _ = _detect_degradation_trend(entries)
            assert is_degrading is False

    def test_increasing_trend_detected(self):
        """连续 N 次递增返回 True。"""
        entries = [
            {"elapsed_s": 0.1},
            {"elapsed_s": 0.2},
            {"elapsed_s": 0.3},
        ][:_DEGRADATION_TREND_COUNT]
        # 至少 N 条数据
        while len(entries) < _DEGRADATION_TREND_COUNT:
            entries.append({"elapsed_s": entries[-1]["elapsed_s"] + 0.1})
        is_degrading, times = _detect_degradation_trend(entries)
        assert is_degrading is True
        assert len(times) == _DEGRADATION_TREND_COUNT

    def test_non_increasing_trend_not_detected(self):
        """非严格递增（有相等或下降）返回 False。"""
        entries = [
            {"elapsed_s": 0.1},
            {"elapsed_s": 0.1},  # 相等，不严格递增
            {"elapsed_s": 0.3},
        ]
        while len(entries) < _DEGRADATION_TREND_COUNT:
            entries.append({"elapsed_s": 0.4})
        is_degrading, _ = _detect_degradation_trend(entries)
        assert is_degrading is False

    def test_decreasing_trend_not_detected(self):
        """递减趋势返回 False。"""
        entries = [
            {"elapsed_s": 0.5},
            {"elapsed_s": 0.4},
            {"elapsed_s": 0.3},
        ]
        while len(entries) < _DEGRADATION_TREND_COUNT:
            entries.append({"elapsed_s": 0.2})
        is_degrading, _ = _detect_degradation_trend(entries)
        assert is_degrading is False


class TestReconcile:
    """reconcile 函数测试。"""

    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._measure_git_status")
    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._count_stale_worktrees")
    def test_reconcile_fast_status_returns_clean(self, mock_count, mock_measure, tmp_path):
        """git status 快 + stale worktree 少 → clean。"""
        mock_measure.return_value = (0.42, 0, "")
        mock_count.return_value = 2
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)

        result = spec.reconcile([], "test-session")

        assert result.action == "clean"
        assert result.gate_id == _GATE_ID
        assert "0.42" in result.detail
        # 性能日志已写入
        log_path = tmp_path / Path(_PERF_LOG_SUBPATH)
        assert log_path.exists()
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["session_id"] == "test-session"
        assert entry["elapsed_s"] == 0.42

    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._measure_git_status")
    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._count_stale_worktrees")
    def test_reconcile_slow_status_returns_warn(self, mock_count, mock_measure, tmp_path):
        """git status 超过 warn 阈值 → warn。"""
        mock_measure.return_value = (_STATUS_WARN_SECONDS + 1.0, 0, "")
        mock_count.return_value = 0
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)

        result = spec.reconcile([], "test-session")

        assert result.action == "warn"
        assert "warn 阈值" in result.detail

    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._measure_git_status")
    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._count_stale_worktrees")
    def test_reconcile_fail_status_returns_warn(self, mock_count, mock_measure, tmp_path):
        """git status 超过 fail 阈值 → warn（更严重告警）。"""
        mock_measure.return_value = (_STATUS_FAIL_SECONDS + 5.0, 0, "")
        mock_count.return_value = 0
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)

        result = spec.reconcile([], "test-session")

        assert result.action == "warn"
        assert "fail 阈值" in result.detail

    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._measure_git_status")
    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._count_stale_worktrees")
    def test_reconcile_status_failure_returns_warn(self, mock_count, mock_measure, tmp_path):
        """git status 失败（rc!=0）→ warn。"""
        mock_measure.return_value = (0.5, -1, "fatal: not a git repo")
        mock_count.return_value = 0
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)

        result = spec.reconcile([], "test-session")

        assert result.action == "warn"
        assert "git status 失败" in result.detail

    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._measure_git_status")
    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._count_stale_worktrees")
    def test_reconcile_many_stale_worktrees_returns_warn(self, mock_count, mock_measure, tmp_path):
        """stale worktree 数超过阈值 → warn。"""
        mock_measure.return_value = (0.42, 0, "")
        mock_count.return_value = _STALE_WORKTREE_WARN_THRESHOLD + 5
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)

        result = spec.reconcile([], "test-session")

        assert result.action == "warn"
        assert "stale worktree" in result.detail
        assert "auto-sweep" in result.detail  # ARCH-WORKTREE-AUTO-SWEEP-001 Phase 1

    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._measure_git_status")
    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._count_stale_worktrees")
    def test_reconcile_degradation_trend_returns_warn(self, mock_count, mock_measure, tmp_path):
        """最近 N 次计时连续递增 → warn。"""
        # 预先写入 N 条递增的历史日志
        for i in range(_DEGRADATION_TREND_COUNT):
            _append_perf_log(tmp_path, {
                "ts": f"2026-07-19T00:00:0{i}Z",
                "elapsed_s": 1.0 + i * 0.5,  # 1.0, 1.5, 2.0 递增
            })
        # 本次测量值继续递增
        mock_measure.return_value = (2.5, 0, "")
        mock_count.return_value = 0
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)

        result = spec.reconcile([], "test-session")

        assert result.action == "warn"
        assert "退化趋势" in result.detail or "递增" in result.detail

    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._measure_git_status")
    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._count_stale_worktrees")
    def test_reconcile_never_raises(self, mock_count, mock_measure, tmp_path):
        """reconciler 永不抛异常（所有异常降级为 warn）。"""
        mock_measure.side_effect = RuntimeError("boom")
        mock_count.return_value = 0
        gw = _FakeGateway(tmp_path)
        spec = make_git_performance_monitor_reconciler(gw)

        result = spec.reconcile([], "test-session")
        assert result.action == "warn"
        assert "monitor failed" in result.detail or "boom" in result.detail

    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._measure_git_status")
    @patch("zephyr.governance.audit.git_performance_monitor_reconciler._count_stale_worktrees")
    def test_reconcile_includes_commit_sha_in_log(self, mock_count, mock_measure, tmp_path):
        """commit sha 写入性能日志。"""
        mock_measure.return_value = (0.42, 0, "")
        mock_count.return_value = 0
        gw = _FakeGateway(tmp_path, head_sha="deadbeef1234")
        spec = make_git_performance_monitor_reconciler(gw)

        spec.reconcile([], "test-session")

        log_path = tmp_path / Path(_PERF_LOG_SUBPATH)
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["commit_sha"] == "deadbeef1234"[:12]