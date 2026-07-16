"""test_pure_assertion_gate.py — pure_assertion_gate.py 闭包测试。"""
from unittest.mock import MagicMock, patch
from zephyr.gov_enforcement.commit_gates.pure_assertion_gate import make_pure_assertion_gate


def _make_gateway(staged_md=None, wt_root="/fake"):
    gw = MagicMock()
    calls = {"diff": staged_md or []}

    def _run_git(cmd):
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        r = R()
        if cmd[0:4] == ["git", "diff", "--cached", "--name-only"]:
            r.stdout = "\n".join(calls["diff"])
        elif cmd[0:2] == ["git", "rev-parse"] and "--show-toplevel" in cmd:
            r.stdout = wt_root
        return r
    gw._run_git = _run_git
    gw.project_root = wt_root
    return gw


def test_pass_no_staged_md():
    gw = _make_gateway(staged_md=[])
    gate = make_pure_assertion_gate()
    passed, detail = gate.check(gw, [])
    assert passed is True


def test_pass_all_excluded():
    gw = _make_gateway(staged_md=["docs/_working/temp.md"])
    gate = make_pure_assertion_gate()
    passed, _ = gate.check(gw, ["docs/_working/temp.md"])
    assert passed is True


@patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.subprocess.run")
def test_block_added_violation(mock_run):
    """staged .md added 行含违规 → block。"""
    mock_run.return_value = MagicMock(returncode=1, stderr="AGENTS.md: line 5: [已废止/已废弃/已弃用] 已废止的规则", stdout="")
    gw = _make_gateway(staged_md=["AGENTS.md"], wt_root="/fake")
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.isfile", return_value=True):
        with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.exists", return_value=True):
            gate = make_pure_assertion_gate()
            passed, detail = gate.check(gw, ["AGENTS.md"])
    assert passed is False
    assert "PURE_ASSERTION" in detail


@patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.subprocess.run")
def test_pass_clean_exit0(mock_run):
    """checker exit 0 → pass。"""
    mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")
    gw = _make_gateway(staged_md=["AGENTS.md"], wt_root="/fake")
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.isfile", return_value=True):
        gate = make_pure_assertion_gate()
        passed, _ = gate.check(gw, ["AGENTS.md"])
    assert passed is True


@patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.subprocess.run")
def test_failopen_exit2(mock_run):
    """checker exit 2 → fail-open。"""
    mock_run.return_value = MagicMock(returncode=2, stderr="script error", stdout="")
    gw = _make_gateway(staged_md=["AGENTS.md"], wt_root="/fake")
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.isfile", return_value=True):
        gate = make_pure_assertion_gate()
        passed, _ = gate.check(gw, ["AGENTS.md"])
    assert passed is True


@patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.subprocess.run")
def test_failopen_timeout(mock_run):
    """checker 超时 → fail-open。"""
    import subprocess as sp
    mock_run.side_effect = sp.TimeoutExpired(cmd="check", timeout=60)
    gw = _make_gateway(staged_md=["AGENTS.md"], wt_root="/fake")
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.isfile", return_value=True):
        gate = make_pure_assertion_gate()
        passed, _ = gate.check(gw, ["AGENTS.md"])
    assert passed is True


def test_failopen_script_missing():
    """checker 脚本缺失 → fail-open。"""
    gw = _make_gateway(staged_md=["AGENTS.md"], wt_root="/fake")
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.isfile", return_value=False):
        gate = make_pure_assertion_gate()
        passed, _ = gate.check(gw, ["AGENTS.md"])
    assert passed is True


def test_gate_priority_and_id():
    gate = make_pure_assertion_gate()
    assert gate.gate_id == "PURE-ASSERTION"
    assert gate.priority == 69
