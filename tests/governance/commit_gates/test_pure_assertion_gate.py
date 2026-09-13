# [BLUEPRINT] MOD-GOV_COMMIT_GATES | (auto-injected by S4 reconciler) | §
# [TTL] permanent
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

    gw.run_git = _run_git
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
    mock_run.return_value = MagicMock(
        returncode=1, stderr="AGENTS.md: line 5: [已废止/已废弃/已弃用] 已废止的规则", stdout=""
    )
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


def _make_ownscope_gateway(staged_md, wt_root):
    """own-scope 测试专用：真实 tmp_path 文件 + registry=None（scope=files-only）。"""
    gw = _make_gateway(staged_md=staged_md, wt_root=wt_root)
    gw._registry = None
    return gw


def test_foreign_staged_violation_downgraded_not_blocks(tmp_path):
    """外来 staged .md 不进 checker、不阻断，降级 warn+审计（2026-09-13 夜路障实例）。"""
    (tmp_path / "own.md").write_text("# ok\n", encoding="utf-8")
    (tmp_path / "foreign_archive.md").write_text("archive\n", encoding="utf-8")
    gw = _make_ownscope_gateway(["own.md", "foreign_archive.md"], str(tmp_path))
    seen = {}

    def fake_checker(cmd, **kwargs):
        seen["cmd"] = list(cmd)
        return MagicMock(returncode=0, stdout="", stderr="")

    gate = make_pure_assertion_gate()
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.run_subprocess_hidden", side_effect=fake_checker):
        passed, _ = gate.check(gw, ["own.md"], session_id="sess-a")
    assert passed is True
    assert "foreign_archive.md" not in " ".join(seen["cmd"])
    assert str(tmp_path / "own.md") in seen["cmd"]
    audit = tmp_path / ".runtime" / "gate_audit" / "pure_assertion_foreign_staged.jsonl"
    assert audit.exists()
    assert "foreign_archive.md" in audit.read_text(encoding="utf-8")


def test_own_violation_still_blocks_after_scope_filter(tmp_path):
    """own-scope 过滤后本 session 自身违规仍硬阻断。"""
    (tmp_path / "own.md").write_text("已废止的规则\n", encoding="utf-8")
    (tmp_path / "foreign.md").write_text("x\n", encoding="utf-8")
    gw = _make_ownscope_gateway(["own.md", "foreign.md"], str(tmp_path))
    gate = make_pure_assertion_gate()
    with patch(
        "zephyr.gov_enforcement.commit_gates.pure_assertion_gate.run_subprocess_hidden",
        return_value=MagicMock(returncode=1, stdout="", stderr="own.md: line 1: [已废止] 过渡文本"),
    ):
        passed, detail = gate.check(gw, ["own.md"], session_id="sess-a")
    assert passed is False
    assert "PURE_ASSERTION" in detail


def test_own_scope_none_falls_back_to_full_scan(tmp_path):
    """无 files 无 session（历史直调）→ own_scope=None 退化全量扫描。"""
    (tmp_path / "a.md").write_text("a\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("b\n", encoding="utf-8")
    gw = _make_ownscope_gateway(["a.md", "b.md"], str(tmp_path))
    seen = {}

    def fake_checker(cmd, **kwargs):
        seen["cmd"] = list(cmd)
        return MagicMock(returncode=0, stdout="", stderr="")

    gate = make_pure_assertion_gate()
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.run_subprocess_hidden", side_effect=fake_checker):
        passed, _ = gate.check(gw, [], session_id=None)
    assert passed is True
    joined = " ".join(seen["cmd"])
    assert "a.md" in joined and "b.md" in joined
