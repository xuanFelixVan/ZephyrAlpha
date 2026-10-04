# [A_test] module_id: MOD-GOV_reuse_scan | layer=test | stability=evolving
# [TTL] task_bound
"""test_reuse_scan —— 先查再建三源扫描测试（裁定#480 C-2，车道C 手术2）。

全部 tmp_path 假仓造景（测试隔离铁律：禁写生产路径）；git 源用子进程 git init
假仓或直接依赖 fail-open 降级面断言。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from zephyr.governance.audit.reuse_scan import scan_similar_work  # noqa: E402


def _mk_dead_letter(repo: Path, qid: str, files: list[dict], reason: str = "GATE-X") -> None:
    dead = repo / ".runtime" / "commit_queue" / "dead"
    dead.mkdir(parents=True, exist_ok=True)
    (dead / f"{qid}.json").write_text(
        json.dumps({"qid": qid, "files": files, "dead_reason": reason, "session_id": "st-x"}),
        encoding="utf-8",
    )


def _mk_worktree_file(repo: Path, sid: str, rel: str) -> None:
    d = repo / ".aidrafts" / sid / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text("wip", encoding="utf-8")


def test_dead_letter_exact_path_hit(tmp_path: Path) -> None:
    """源③：死信袋 files[].path 同路径精确命中，hint 带 qid+dead_reason。"""
    target = "src/zephyr/governance/audit/reuse_scan.py"
    _mk_dead_letter(
        tmp_path,
        "q-test-001",
        [{"path": target}, {"path": "docs/other.md"}],
        reason="COMMIT_SCOPE_MISMATCH",
    )
    hits = scan_similar_work([target], tmp_path)
    dead_hits = [h for h in hits if h["source"] == "dead_letter"]
    assert len(dead_hits) == 1
    assert dead_hits[0]["path"] == target
    assert "q-test-001" in dead_hits[0]["hint"]
    assert "COMMIT_SCOPE_MISMATCH" in dead_hits[0]["hint"]


def test_worktree_hit_and_self_exclusion(tmp_path: Path) -> None:
    """源②：活跃 worktree 同路径命中；主区已存在的既有文件不误报；本会话排除。"""
    rel = "src/zephyr/governance/new_thing.py"
    _mk_worktree_file(tmp_path, "st-other-1", rel)
    hits = scan_similar_work([rel], tmp_path, exclude_worktree_sids=["st-me"])
    wt = [h for h in hits if h["source"] == "worktree"]
    assert len(wt) == 1
    assert "st-other-1" in wt[0]["hint"]

    # 排除自己：带 exclude 后自己 worktree 不报
    _mk_worktree_file(tmp_path, "st-me", rel)
    hits2 = scan_similar_work([rel], tmp_path, exclude_worktree_sids=["st-me"])
    wt2 = [h for h in hits2 if h["source"] == "worktree" and "st-me" in h["hint"]]
    assert not wt2

    # 防误报闸：主区存在同路径（主分支 checkout 常态）→ worktree 源不报
    (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / rel).write_text("existing on main", encoding="utf-8")
    hits3 = scan_similar_work([rel], tmp_path, exclude_worktree_sids=["st-me"])
    assert not [h for h in hits3 if h["source"] == "worktree"]


def test_git_status_samepath_and_basename(tmp_path: Path) -> None:
    """源①：git 假仓 porcelain 命中同路径+同基名；判据查盘面（HEAD 无关）。"""
    r = subprocess.run(["git", "init", "-q"], cwd=str(tmp_path), capture_output=True)
    if r.returncode != 0:  # 环境 git 不可用 → fail-open 面直接验证
        assert scan_similar_work(["a.py"], tmp_path) == []
        return
    target = "scripts/governance/register_asset.py"
    (tmp_path / target).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / target).write_text("new", encoding="utf-8")
    # 同基名不同目录的另一个在途件
    other = "docs/_working/drafts/register_asset.py"
    (tmp_path / other).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / other).write_text("draft", encoding="utf-8")
    subprocess.run(["git", "add", target], cwd=str(tmp_path), capture_output=True)
    hits = scan_similar_work([target], tmp_path)
    gs = {h["path"]: h for h in hits if h["source"] == "git_status"}
    assert target in gs  # 同路径（staged）
    assert other in gs  # 同基名（untracked）


def test_no_match_returns_empty_and_corrupt_json_skipped(tmp_path: Path) -> None:
    """三源全无命中=空 list；损坏死信 json 跳过不抛（fail-open）。"""
    dead = tmp_path / ".runtime" / "commit_queue" / "dead"
    dead.mkdir(parents=True, exist_ok=True)
    (dead / "bad.json").write_text("{not valid json", encoding="utf-8")
    hits = scan_similar_work(["src/nothing/here.py"], tmp_path)
    assert hits == []
    # 空输入 → 空
    assert scan_similar_work([], tmp_path) == []
