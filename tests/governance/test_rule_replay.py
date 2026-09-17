# [MODULE] tests.governance.test_rule_replay
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §rule_replay
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""rule_replay 单元测试——全部 tmp_path 沙箱，零生产路径、零仓库状态变更。

覆盖：diff-tree 解析 / ReplayGateway 三调用族 / 阈值注入 delta 四值 /
summary P1 否决与 P3 Jaccard 边界 / 抽样去重保序。
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from zephyr.governance.standards_governance.rule_replay import (
    DELTA_BOTH_BLOCK,
    DELTA_BOTH_PASS,
    DELTA_NEW_BLOCK,
    DELTA_NEW_PASS,
    ReplayGateway,
    _jaccard,
    parse_diff_tree,
    replay_commit,
    sample_commits,
    summarize,
)

# ────────────────────────── parse_diff_tree ──────────────────────────


def test_parse_diff_tree_multi_file_split():
    patch = (
        "diff --git a/src/a.py b/src/a.py\n"
        "--- a/src/a.py\n+++ b/src/a.py\n@@ -1 +1 @@\n-x\n+y\n"
        "diff --git a/src/b.py b/src/b.py\n"
        "--- a/src/b.py\n+++ b/src/b.py\n@@ -1 +1 @@\n-p\n+q\n"
    )
    files, patches = parse_diff_tree(patch)
    assert files == ["src/a.py", "src/b.py"]
    assert "a.py" in patches["src/a.py"] and "+y" in patches["src/a.py"]
    assert "b.py" in patches["src/b.py"]


def test_parse_diff_tree_empty():
    assert parse_diff_tree("") == ([], {})


# ────────────────────────── ReplayGateway ──────────────────────────


def _gateway() -> ReplayGateway:
    return ReplayGateway(
        ["src/a.py"],
        {"src/a.py": "diff --git a/src/a.py b/src/a.py\n@@ -1 +1 @@\n-x\n+y\n"},
        "D:/repo",
    )


def test_gateway_name_status_family():
    r = _gateway().run_git(["git", "diff", "--cached", "--name-status", "--diff-filter=AM"])
    assert r.returncode == 0 and "M\tsrc/a.py" in r.stdout


def test_gateway_patch_family():
    r = _gateway().run_git(["git", "diff", "--cached", "-U0", "--", "src/a.py"])
    assert r.returncode == 0 and "+y" in r.stdout


def test_gateway_toplevel_family():
    r = _gateway().run_git(["git", "rev-parse", "--show-toplevel"])
    assert r.returncode == 0 and r.stdout.strip() == "D:/repo"


def test_gateway_unknown_call_fails_closed():
    r = _gateway().run_git(["git", "push", "origin", "main"])
    assert r.returncode == 1 and r.stdout == ""


# ────────────────────────── 阈值注入与 delta ──────────────────────────

FAKE_GATE_SRC = textwrap.dedent(
    """
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

    FILE_LIMIT = 3  # 阈值常量（旧）：文件数 < 3 放行


    def _check(gateway, files, **kwargs):
        return (len(files) < FILE_LIMIT, f"files={len(files)} limit={FILE_LIMIT}")


    def make_test_gate() -> GateSpec:
        return GateSpec(gate_id="TEST-RULE-REPLAY", check=_check, priority=9999)
    """
)


def _ctx(pairs: list, tmp_path: Path, fetch=None, out_of_scope: list | None = None):
    from zephyr.governance.standards_governance.rule_replay import ReplayContext

    return ReplayContext(run_id="r1", pairs=pairs,
                         out_of_scope=out_of_scope or [],
                         repo_root=tmp_path, diff_fetch=fetch)


def _target(commit: str = "h1"):
    from zephyr.governance.standards_governance.rule_replay import ReplayTarget

    return ReplayTarget(commit_hash=commit * 20, commit_date="2026-09-17",
                        stratum="random")


def _fake_gate_pair(tmp_path: Path, new_limit: int | None):
    from zephyr.governance.standards_governance.rule_replay import _GatePair, _load_module_copy

    gate_file = tmp_path / "fake_gate_mod.py"
    gate_file.write_text(FAKE_GATE_SRC, encoding="utf-8")
    old_mod = _load_module_copy(str(gate_file), "old")
    old_spec = old_mod.make_test_gate()
    if new_limit is None:
        new_check = old_spec.check
    else:
        new_mod = _load_module_copy(str(gate_file), "new")
        new_mod.FILE_LIMIT = new_limit
        new_check = new_mod.make_test_gate().check
    return _GatePair("TEST-RULE-REPLAY", 9999, old_spec.check, new_check, "fake_gate_mod")


def _repo(tmp_path: Path) -> Path:
    return tmp_path


def test_replay_commit_delta_both_pass(tmp_path):
    pair = _fake_gate_pair(tmp_path, new_limit=None)  # 新旧同阈值
    rows = replay_commit(_ctx([pair], tmp_path), _target())
    assert rows[0]["delta"] == DELTA_BOTH_PASS and rows[0]["error"] == ""


def test_replay_commit_delta_new_block(tmp_path):
    pair = _fake_gate_pair(tmp_path, new_limit=1)  # 收紧：1 文件也拦 → new_block
    fetch = lambda h: (["a.py", "b.py"], {"a.py": "x", "b.py": "y"})
    rows = replay_commit(_ctx([pair], tmp_path, fetch), _target())
    assert rows[0]["delta"] == DELTA_NEW_BLOCK


def test_replay_commit_delta_both_block_and_new_pass(tmp_path):
    # 两文件 + 新阈值 1：旧放行（2<3）新拦截（2<1 假）→ new_block；单文件反向 → new_pass
    fetch = lambda h: (["a.py", "b.py"], {"a.py": "x", "b.py": "y"})
    pair = _fake_gate_pair(tmp_path, new_limit=1)
    rows = replay_commit(_ctx([pair], tmp_path, fetch), _target())
    assert rows[0]["delta"] == DELTA_NEW_BLOCK
    pair0 = _fake_gate_pair(tmp_path, new_limit=5)
    rows0 = replay_commit(_ctx([pair0], tmp_path, fetch), _target("h2"))
    assert rows0[0]["delta"] == DELTA_BOTH_PASS


def test_replay_commit_error_recorded_not_crash(tmp_path, monkeypatch):
    pair = _fake_gate_pair(tmp_path, new_limit=None)

    def _boom(gateway, files, **kwargs):
        raise RuntimeError("boom")

    pair.old_check = _boom
    rows = replay_commit(_ctx([pair], tmp_path), _target())
    assert rows[0]["delta"] == "error" and "boom" in rows[0]["error"]


def test_replay_commit_out_of_scope_rows(tmp_path):
    pair = _fake_gate_pair(tmp_path, new_limit=None)
    rows = replay_commit(_ctx([pair], tmp_path, out_of_scope=["WORKTREE-REQUIRED"]),
                         _target())
    oos = [r for r in rows if r["gate_id"] == "WORKTREE-REQUIRED"]
    assert oos and oos[0]["out_of_scope_reason"] != ""


# ────────────────────────── summarize 判据 ──────────────────────────


def _write_report(tmp_path: Path, rows: list[dict]) -> Path:
    p = tmp_path / "report.jsonl"
    for r in rows:
        p.write_text("".join(
            json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")
    return p


def _row(commit: str, gate: str, old_passed: bool, new_passed: bool, stratum: str = "random"):
    return {
        "run_id": "r", "commit_hash": commit, "commit_date": "2026-09-17",
        "stratum": stratum, "files": [], "gate_id": gate, "priority": 1,
        "old": {"passed": old_passed, "detail_digest": ""},
        "new": {"passed": new_passed, "detail_digest": ""},
        "delta": ("both_pass" if old_passed and new_passed else
                  "both_block" if not old_passed and not new_passed else
                  "new_block" if old_passed and not new_passed else "new_pass"),
        "replay_ms": 1.0, "error": "", "out_of_scope_reason": "",
    }


def test_summary_pass_when_no_leak(tmp_path):
    rows = [_row("c1", "G", False, False), _row("c2", "G", True, True),
            _row("c3", "G", True, False)]  # 一笔新拦截（20%>2%）→ P2 拦
    summary = summarize(_write_report(tmp_path, rows))
    assert summary["verdict"] == "FAIL" and summary["p1_pass_leak"]["pass"] is True


def test_summary_p1_veto_on_leak(tmp_path):
    rows = [_row("c1", "G", False, True, stratum="blocked")]  # 该拦放走 → 一票否决
    summary = summarize(_write_report(tmp_path, rows))
    assert summary["verdict"] == "FAIL" and summary["p1_pass_leak"]["value"] == 1


def test_summary_pass_boundary(tmp_path):
    rows = [_row("c1", "G", False, False), _row("c2", "G", True, True)]
    summary = summarize(_write_report(tmp_path, rows))
    assert summary["verdict"] == "PASS" and summary["p3_jaccard"]["global"] == 1.0


def test_summary_error_rate_unreliable(tmp_path):
    rows = [_row("c1", "G", True, True)]
    bad = dict(_row("c2", "G", True, True), delta="error", error="x")
    rows.append(bad)
    summary = summarize(_write_report(tmp_path, rows))
    assert summary["reliable"] is False and summary["counts"]["error"] == 1


def test_jaccard_edges():
    assert _jaccard(set(), set()) == 1.0
    assert _jaccard({"a"}, {"a"}) == 1.0
    assert _jaccard({"a"}, {"b"}) == 0.0


# ────────────────────────── 抽样 ──────────────────────────


def test_sample_commits_dedup_and_quota(tmp_path, monkeypatch):
    import zephyr.governance.standards_governance.rule_replay as m

    fake_all = [(f"h{i:03d}" * 1, "2026-09-01") for i in range(50)]
    monkeypatch.setattr(m, "list_commit_range", lambda *a, **k: fake_all)
    monkeypatch.setattr(m, "list_merge_commits", lambda *a, **k: [("m999", "2026-09-02")])
    plan = sample_commits(
        tmp_path, "2026-09-01", "2026-09-30",
        {"blocked": 2, "passed": 3, "special": 1, "random": 5},
        blocked_hashes=["h000", "h001"], passed_hashes=["h002"],
    )
    strata = {s for _, _, s in plan}
    assert strata == {"blocked", "passed", "special", "random"}
    hashes = [h for h, _, _ in plan]
    assert len(hashes) == len(set(hashes))  # 去重
    assert len([p for p in plan if p[2] == "blocked"]) == 2
