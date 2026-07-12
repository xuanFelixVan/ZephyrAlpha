# [A_test] module_id: SRC-TST-2224 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-perm_trigger_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_perm_trigger_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_perm_trigger_gate.py — PERM-TRIGGER 门禁单测

权威依据：perm_trigger_gate.py（make_perm_trigger_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestPermanentTtl: _has_permanent_ttl 纯函数（命中/安全/大小写）
- TestDetectTrigger: _detect_time_trigger / _detect_event_registration AST 检测
- TestGatewayIntegration: mock gateway 流程
  - permanent + while True 无事件订阅 → 阻断 (passed=False)
  - permanent + while True + 事件订阅 → 放行
  - 非 permanent → 放行
  - tests/ 豁免
  - fail-open on git diff 失败/异常
  - fail-open on AST 解析失败（SyntaxError）

测试隔离：MagicMock 模拟 gateway._run_git，tmp_path 创建真实 .py 文件。
"""
from __future__ import annotations

import ast
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.perm_trigger_gate import (  # noqa: E402
    _decorator_name,
    _detect_event_registration,
    _detect_time_trigger,
    _has_permanent_ttl,
    make_perm_trigger_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(tmp_path, staged_files=None, added_files=None,
                  diff_fails=False, diff_raises=False):
    """构造 mock gateway：--diff-filter=AM 返回文件列表；--diff-filter=A 返回新增集；
    --show-toplevel 返回 tmp_path。added_files 默认与 staged_files 相同（全为新增）。"""
    gw = MagicMock()
    gw.project_root = str(tmp_path)

    if diff_raises:
        def _raise(*a, **k):
            raise RuntimeError("git not found")
        gw._run_git = _raise
        return gw

    if added_files is None:
        added_files = staged_files

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            if "--diff-filter=A" in cmd:
                return _MockResult(0, "\n".join(added_files or []))
            return _MockResult(0, "\n".join(staged_files or []))
        if "rev-parse" in cmd and "--show-toplevel" in cmd:
            return _MockResult(0, str(tmp_path))
        return _MockResult(0, "")

    gw._run_git = _run_git
    return gw


def _write_file(tmp_path, rel_path, content):
    """在 tmp_path 下创建 rel_path 文件，返回相对路径（正斜杠）。"""
    rel = rel_path.replace("\\", "/")
    full = tmp_path / rel.replace("/", os.sep)
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    return rel


@pytest.fixture(autouse=True)
def _shadow_open(monkeypatch):
    """源文件用 open(path).read() 未关闭文件句柄（ResourceWarning）。
    注入 shadow open：read() 后立即关闭真实 fd。"""
    import builtins
    _real_open = builtins.open

    class _AutoClose:
        def __init__(self, fp):
            self._fp = fp

        def read(self, *a, **k):
            try:
                return self._fp.read(*a, **k)
            finally:
                self._fp.close()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            self._fp.close()

        def __getattr__(self, name):
            return getattr(self._fp, name)

    def _shadow(file, mode="r", *args, **kwargs):
        return _AutoClose(_real_open(file, mode, *args, **kwargs))

    import zephyr.governance.commit_gates.perm_trigger_gate as mod
    monkeypatch.setattr(mod, "open", _shadow, raising=False)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_perm_trigger_gate(), GateSpec)

    def test_gate_id(self):
        assert make_perm_trigger_gate().gate_id == "PERM-TRIGGER"

    def test_priority(self):
        assert make_perm_trigger_gate().priority == 82


# ---------------------------------------------------------------------------
# TestPermanentTtl — _has_permanent_ttl
# ---------------------------------------------------------------------------
class TestPermanentTtl:
    def test_permanent_header_detected(self):
        content = "# [TTL] permanent\nimport time\n"
        assert _has_permanent_ttl(content)

    def test_case_insensitive(self):
        content = "# [ttl] PERMANENT\nimport time\n"
        assert _has_permanent_ttl(content)

    def test_no_permanent_header(self):
        content = "# [TTL] task_bound\nimport time\n"
        assert not _has_permanent_ttl(content)

    def test_no_ttl_header(self):
        content = "import time\nwhile True:\n    pass\n"
        assert not _has_permanent_ttl(content)


# ---------------------------------------------------------------------------
# TestDetectTrigger — AST 检测纯函数
# ---------------------------------------------------------------------------
class TestDetectTrigger:
    def test_while_true_detected(self):
        tree = ast.parse("while True:\n    pass\n")
        assert _detect_time_trigger(tree)

    def test_time_sleep_detected(self):
        tree = ast.parse("import time\ntime.sleep(1)\n")
        assert _detect_time_trigger(tree)

    def test_schedule_detected(self):
        tree = ast.parse("import schedule\nschedule.every()\n")
        assert _detect_time_trigger(tree)

    def test_apscheduler_detected(self):
        # BackgroundScheduler 作为 Name 节点（构造调用）才被检测；
        # from-import 产生 alias 节点，不被 _detect_time_trigger 检测。
        tree = ast.parse("sched = BackgroundScheduler()\n")
        assert _detect_time_trigger(tree)

    def test_no_trigger_safe(self):
        tree = ast.parse("def foo():\n    return 1\n")
        assert not _detect_time_trigger(tree)

    def test_event_subscribe_detected(self):
        tree = ast.parse("event_bus.subscribe('topic', handler)\n")
        assert _detect_event_registration(tree)

    def test_event_decorator_detected(self):
        tree = ast.parse("@subscriber\ndef on_x(e):\n    pass\n")
        assert _detect_event_registration(tree)

    def test_no_event_registration_safe(self):
        tree = ast.parse("def foo():\n    return 1\n")
        assert not _detect_event_registration(tree)

    def test_decorator_name_extraction(self):
        # @foo.bar 形式
        dec = ast.parse("@foo.bar\ndef f(): pass\n").body[0].decorator_list[0]
        assert _decorator_name(dec) == "bar"


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_perm_trigger_blocked(self, tmp_path):
        red = "src/zephyr/trading/daemon.py"
        content = (
            "# [TTL] permanent\n"
            "import time\n"
            "while True:\n"
            "    time.sleep(1)\n"
        )
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_perm_trigger_gate().check(gw, [])
        assert not passed
        assert "PERM-TRIGGER" in msg or "永久系统" in msg

    def test_perm_trigger_with_event_passes(self, tmp_path):
        blue = "src/zephyr/trading/daemon.py"
        content = (
            "# [TTL] permanent\n"
            "import time\n"
            "event_bus.subscribe('topic', handler)\n"
            "while True:\n"
            "    time.sleep(1)\n"
        )
        _write_file(tmp_path, blue, content)
        gw = _make_gateway(tmp_path, staged_files=[blue])
        passed, msg = make_perm_trigger_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_non_perm_passes(self, tmp_path):
        blue = "src/zephyr/trading/daemon.py"
        content = (
            "# [TTL] task_bound\n"
            "import time\n"
            "while True:\n"
            "    time.sleep(1)\n"
        )
        _write_file(tmp_path, blue, content)
        gw = _make_gateway(tmp_path, staged_files=[blue])
        passed, msg = make_perm_trigger_gate().check(gw, [])
        assert passed  # 非 permanent 不检测
        assert msg == ""

    def test_perm_with_subscriber_decorator_passes(self, tmp_path):
        blue = "src/zephyr/trading/handler.py"
        content = (
            "# [TTL] permanent\n"
            "while True:\n"
            "    pass\n"
            "@subscriber\n"
            "def on_event(e):\n"
            "    process(e)\n"
        )
        _write_file(tmp_path, blue, content)
        gw = _make_gateway(tmp_path, staged_files=[blue])
        passed, msg = make_perm_trigger_gate().check(gw, [])
        assert passed  # 有 @subscriber 事件订阅
        assert msg == ""

    def test_tests_dir_exempt(self, tmp_path):
        red = "tests/governance/test_daemon.py"
        content = (
            "# [TTL] permanent\n"
            "while True:\n"
            "    pass\n"
        )
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_perm_trigger_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_fails=True)
        passed, msg = make_perm_trigger_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_raises=True)
        passed, msg = make_perm_trigger_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_syntax_error(self, tmp_path):
        red = "src/zephyr/trading/daemon.py"
        content = (
            "# [TTL] permanent\n"
            "while True(\n"  # 语法错误
            "    pass\n"
        )
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_perm_trigger_gate().check(gw, [])
        assert passed  # fail-open
        assert msg == ""
