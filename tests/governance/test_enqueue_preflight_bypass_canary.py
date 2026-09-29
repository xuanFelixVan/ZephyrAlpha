# [TTL] permanent
# [STARTUP] manual
# [CONSUMERS] commit_queue 预检漏斗（红证 canary，pytest 收集执行）
"""红证 canary（波 1B 包 1.7）：入队预检旁路必须被同一道闸拦下。

判据出处：`docs/_working/total_command_closeout/10_wave_plan.md:54`
（红证=直调旁路投一件缺 creation_token 的新文件→必被拦）。
本件不跑真门禁链（CREATE-GUARD 全树 git grep 分钟级且写审计），只把**权威判定函数**
`commit_preflight.run_preflight` 换成注定阻断的替身，从而确定性地证明：预检结果一旦
是阻断，三条入队通道（enqueue_item 直调 / requeue / 裸 CLI）无处可绕。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.commit_queue as cq
import zephyr.gov_enforcement.rule_bridge.commit_preflight as commit_preflight

_NEW_FILE = "src/zephyr/brand_new_never_tokened.py"
_PRESCRIPTION = "入队预检拦截——CREATE-GUARD 处方：新建件缺 creation_token，先登记再入队"


class _BlockingPreflight:
    """注定阻断的 run_preflight 替身（只替权威判定，不改预检挂线本身）。"""

    def __init__(self) -> None:
        self.seen: list[list[str]] = []

    def __call__(self, gateway, files, session_id, **kwargs) -> _BlockingPreflight:
        self.seen.append(list(files))
        return self

    @property
    def blocking(self) -> bool:
        return True

    @property
    def degraded(self) -> tuple[()] | list[str]:
        return []

    def render_report(self, session_id: str) -> str:
        return _PRESCRIPTION


@pytest.fixture()
def blocking_preflight(monkeypatch) -> _BlockingPreflight:
    stub = _BlockingPreflight()
    monkeypatch.setattr(commit_preflight, "run_preflight", stub)
    return stub


@pytest.fixture()
def git_like_root(tmp_path: Path) -> Path:
    """伪 git 工作区根（预检根判据只看 .git 实存；不跑真 git）。"""
    (tmp_path / ".git").mkdir()
    return tmp_path


def _options(root: Path, **kw) -> cq.EnqueueOptions:
    return cq.EnqueueOptions(preflight_root=str(root), **kw)


def test_direct_enqueue_item_call_is_not_a_bypass(tmp_path: Path, git_like_root: Path, blocking_preflight) -> None:
    """红证①：直调 enqueue_item 投缺 token 新文件 ⇒ QueueReject（旧形态=静默入袋）。"""
    with pytest.raises(cq.QueueReject) as boom:
        cq.enqueue_item(
            "canary17",
            "new file without creation_token",
            [(_NEW_FILE, b"print('x')\n")],
            queue_root=tmp_path / "q",
            options=_options(git_like_root),
        )
    assert "CREATE-GUARD" in str(boom.value)
    assert blocking_preflight.seen, "预检根本没被调用＝旁路仍在"
    assert _NEW_FILE in blocking_preflight.seen[0]
    assert list((tmp_path / "q" / "pending").glob("q-*.json")) == []  # 未落袋


def test_bypass_closes_only_when_root_declared_and_git(tmp_path: Path, blocking_preflight) -> None:
    """正向路径：未声明预检根 / 根非 git 工作区 ⇒ 不扫（tmp 隔离测试与 API 直调零变更）。"""
    item = cq.enqueue_item(
        "canary17",
        "no preflight root",
        [(_NEW_FILE, b"print('x')\n")],
        queue_root=tmp_path / "q1",
        options=cq.EnqueueOptions(),
    )
    assert item["qid"]
    non_git = tmp_path / "not_git"
    non_git.mkdir()
    item2 = cq.enqueue_item(
        "canary17",
        "root is not a git worktree",
        [(_NEW_FILE, b"print('x')\n")],
        queue_root=tmp_path / "q2",
        options=_options(non_git),
    )
    assert item2["qid"]
    assert blocking_preflight.seen == []


def test_explicit_skip_is_the_only_legitimate_optout(tmp_path: Path, git_like_root: Path, blocking_preflight) -> None:
    """skip 位唯一合法用途=调用方已自跑预检（landing reroute 通道），且必须显式声明。"""
    item = cq.enqueue_item(
        "canary17",
        "already scanned upstream",
        [(_NEW_FILE, b"print('x')\n")],
        queue_root=tmp_path / "q",
        options=cq.EnqueueOptions(preflight_root=str(git_like_root), enqueue_preflight="skip"),
    )
    assert item["qid"]
    assert blocking_preflight.seen == []


def _seed_dead_item(root: Path, qid: str, *, session: str = "canary17b") -> Path:
    dead_dir = root / "dead"
    dead_dir.mkdir(parents=True, exist_ok=True)
    payload = b"print('brand new')\n"
    item = {
        "qid": qid,
        "session_id": session,
        "created_at": "2026-09-26T00:00:00+00:00",
        "branch": "dev",
        "base_head": None,
        "files": [{"path": _NEW_FILE, "blob_sha256": "0" * 64, "blob_ref": "", "action": "modify"}],
        "message": "dead letter awaiting requeue",
        "meta": {},
        "dead_reason": "CREATE-GUARD: missing creation_token",
        "dead_at": "2026-09-26T00:01:00+00:00",
    }
    (dead_dir / f"{qid}.json").write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8", newline="\n")
    return dead_dir


def test_requeue_path_runs_the_same_preflight(tmp_path: Path, blocking_preflight) -> None:
    """红证②（点名旁路）：requeue_dead_item 直调重投同一件缺 token 新文件 ⇒ 必被拦。"""
    queue_root = tmp_path / "q"
    wt = tmp_path / "wt"
    (wt / "src" / "zephyr").mkdir(parents=True)
    (wt / ".git").mkdir()
    (wt / _NEW_FILE).write_bytes(b"print('brand new')\n")
    qid = "q-20260926-canary17b-0001"
    _seed_dead_item(queue_root, qid)

    with pytest.raises(cq.QueueReject) as boom:
        cq.requeue_dead_item(qid, queue_root=queue_root, worktree_root=wt)
    assert "CREATE-GUARD" in str(boom.value)
    assert blocking_preflight.seen, "requeue 仍绕过预检＝旁路未封"
    # 被拦即不得有新袋落入 pending（原死信项留 dead/ 只标注不删除）
    assert list((queue_root / "pending").glob("q-*.json")) == []
