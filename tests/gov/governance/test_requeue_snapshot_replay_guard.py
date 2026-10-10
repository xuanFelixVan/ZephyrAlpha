# [TTL] permanent
# [MODULE] tests.gov.governance.test_requeue_snapshot_replay_guard
# [STARTUP] pytest collection only（零生产路径写：全部落 tmp_path fixture）
# [CONSUMERS] 无运行时消费者；本班 T2/T13 验收试件
"""维护二班 T2＋T13 试件（st-maint2-20261011，2026-10-11）。

覆盖两件事，都是"提交队列正门"上的通道病：

T2 —— 死袋重放把"修好的代码"漏在外面。在册判据 `lines_only_in_head`（10-10 由
st-finalclean2-20261010 写进案卷，代码侧零实现）本班落地成
`commit_queue._snapshot_head_regressions`，并据此把 `--from-bag` 形态改成缺省拒绝；
工作区重建分支（在册 D7 修-重试工作流）保持不拦，只量只标。

T13 —— dead-archive 没有属主过滤，只能全量操作 ⇒ 要么误碰他人死信（在册红线：
驱逐他人袋＝归属篡改），要么不敢用。本班加 `--session`＋fail-closed 第二道闸。

pristine 红证（第 12 例）：把 dev 版 commit_queue.py 的字节留在
`docs/_working/maint2_campaign/pristine/commit_queue.py.orig`，断言原始字节里
这些能力**确实不存在**——红来自原始字节，不来自推测。
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path[:0] = [str(Path(__file__).resolve().parents[3])]
from scripts import commit_queue as cq  # noqa: E402

BASELINE_SHA = "cfbebbf8dd49f8b8ae935d186f4fbe7f8cfc6c66"
PRISTINE_REL = "scripts/commit_queue.py"
PRISTINE_SHA256_PREFIX = "55e411f787d5e5cb"


def _pristine_text() -> str:
    """基线 commit 的内容寻址原始字节（不落 .orig 副本：docs/_working 目录契约不允该
    扩展名，且根宪法 §4 全资产净零禁上 MB 级重复件）。二进制读防行尾折叠改字节。"""
    root = Path(__file__).resolve().parents[3]
    proc = subprocess.run(
        ["git", "-C", root.as_posix(), "show", f"{BASELINE_SHA}:{PRISTINE_REL}"],
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, f"基线 blob 取回失败: {proc.stderr[:200]}"
    sha = hashlib.sha256(proc.stdout).hexdigest()
    assert sha[:16] == PRISTINE_SHA256_PREFIX, f"pristine 凭据字节与钉死基线不符（红证失效）：{sha}"
    return proc.stdout.decode("utf-8")


def _git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


@pytest.fixture()
def dev_repo(tmp_path: Path) -> Path:
    """一个真 git 仓，分支名必须是 dev（`_snapshot_head_regressions` 缺省 base_ref=dev）。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "--quiet")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / "a.txt").write_bytes(b"line1\nline2\nline3\n")
    _git(repo, "add", "a.txt")
    _git(repo, "commit", "--quiet", "-m", "seed")
    _git(repo, "branch", "-M", "dev")
    return repo


# ---------------------------------------------------------------------------
# 1. 判据本体：lines_only_in_head（真 git 仓对拍）
# ---------------------------------------------------------------------------


def test_regression_zero_when_snapshot_equals_head(dev_repo: Path) -> None:
    head = (dev_repo / "a.txt").read_bytes()
    assert cq._snapshot_head_regressions(dev_repo, [("a.txt", head)]) == []


def test_regression_counts_head_lines_missing_from_snapshot(dev_repo: Path) -> None:
    # 重放字节＝"line1/line2" 的旧稿：dev 已在册的 line3 不在重放里
    stale = b"line1\nline2\n"
    out = cq._snapshot_head_regressions(dev_repo, [("a.txt", stale)])
    assert len(out) == 1
    assert out[0]["path"] == "a.txt"
    assert out[0]["head_only_lines"] == 1
    assert out[0]["sample"] == ["line3"]


def test_crlf_difference_is_not_counted_as_regression(dev_repo: Path) -> None:
    """行尾是第四把口径：CRLF/LF 之差不得被读成"丢失 N 行"（在册假案形态）。"""
    lf = (dev_repo / "a.txt").read_bytes()
    crlf = lf.replace(b"\n", b"\r\n")
    assert cq._snapshot_head_regressions(dev_repo, [("a.txt", crlf)]) == []


def test_new_file_absent_from_head_is_not_a_regression(dev_repo: Path) -> None:
    assert cq._snapshot_head_regressions(dev_repo, [("brand/new.py", b"whatever\n")]) == []


# ---------------------------------------------------------------------------
# 1b. 三方口径（本班 06:5x 自证抓到的假阳性，反向钉桩）
# ---------------------------------------------------------------------------


@pytest.fixture()
def two_step_repo(tmp_path: Path) -> tuple[Path, str]:
    """base 提交 A（l1,l2）→ dev 前进到 B（l1,l2,l3，别人后落 l3）。返回 (repo, A 的 sha)。"""
    repo = tmp_path / "repo2"
    repo.mkdir()
    _git(repo, "init", "--quiet")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / "a.txt").write_bytes(b"l1\nl2\n")
    _git(repo, "add", "a.txt")
    _git(repo, "commit", "--quiet", "-m", "A base")
    sha_a = _git(repo, "rev-parse", "HEAD")
    (repo / "a.txt").write_bytes(b"l1\nl2\nl3\n")  # 别人把 l3 落进 dev
    _git(repo, "add", "a.txt")
    _git(repo, "commit", "--quiet", "-m", "B dev advanced")
    _git(repo, "branch", "-M", "dev")
    return repo, sha_a


def test_own_legit_line_removal_is_not_a_regression(two_step_repo) -> None:
    """我正当改掉 l2（重写成 l2x）且从未见过 l3 ⇒ 只有 l3 算回归，l2x 那次改写不算。

    这就是本班自己犯过一次又当场改掉的形态：判据若写成两方 `dev_lines − snap_lines`，
    本袋 26 件里误报 17 件，闸被自己的噪声淹掉＝真信号一样看不见。
    """
    repo, sha_a = two_step_repo
    mine = b"l1\nl2x\n"
    three_way = cq._snapshot_head_regressions(repo, [("a.txt", mine)], item_base_head=sha_a)
    assert [r["head_only_lines"] for r in three_way] == [1], three_way
    assert three_way[0]["sample"] == ["l3"], three_way
    assert three_way[0]["base_compared"] is True
    # 对照组：无基底可比时保守取全量（宁可多疑，也不放行一份对不上基底的整档重放）
    coarse = cq._snapshot_head_regressions(repo, [("a.txt", mine)])
    assert coarse[0]["head_only_lines"] == 2 and coarse[0]["base_compared"] is False


def test_replay_carrying_others_landed_line_is_clean(two_step_repo) -> None:
    """重放字节已含别人后落的 l3 ⇒ 零回归（闸不许把"同步过的工作区"也判成旧快照）。"""
    repo, sha_a = two_step_repo
    assert cq._snapshot_head_regressions(repo, [("a.txt", b"l1\nl2\nl3\n")], item_base_head=sha_a) == []


# ---------------------------------------------------------------------------
# 2. requeue 闸：--from-bag fail-closed / 越权留痕 / 工作区分支不拦
# ---------------------------------------------------------------------------


def _make_dead_bag(root: Path, *, qid: str, rel: str, content: bytes, session_id: str = "st-probe") -> dict:
    blob_sha = hashlib.sha256(content).hexdigest()
    blob_dir = root / "blobs" / blob_sha[:2]
    blob_dir.mkdir(parents=True, exist_ok=True)
    blob_ref = f"blobs/{blob_sha[:2]}/{blob_sha}"
    (root / blob_ref).write_bytes(content)
    item = {
        "qid": qid,
        "session_id": session_id,
        "message": "seed bag",
        "base_head": "0" * 40,
        "dead_reason": "GATE:DEMO",
        "dead_at": datetime.now().astimezone().isoformat(),
        "files": [{"path": rel, "blob_ref": blob_ref, "blob_sha256": blob_sha, "action": "modify"}],
        "meta": {},
    }
    (root / "dead").mkdir(parents=True, exist_ok=True)
    (root / "dead" / f"{qid}.json").write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")
    return item


@pytest.fixture()
def off_lane_root() -> Iterator[Path]:
    """队列/工作区根必须落在**车道之外**的系统临时目录。

    实测机理（本班踩到后钉住）：`resolve_queue_root` 的车道感知重定向（修3，Owner 批
    2026-10-05）会把位于 `.aidrafts/.worktrees` 内的显式 queue_root 截断到主仓同构路径。
    本仓 pytest 的 tmp_path 就在 `.runtime/tmp/pytest_*` 里——在它下面建队列，读到的是
    一个不存在的主仓路径，用例会以"archived=0 / qid 不在 dead/"这种误导性形态失败；
    反过来若截断出的主仓路径恰好存在，就是"测试写生产队列"（在册事故：735 条测试污染死信）。
    系统 tmp 目录两者都不犯，也不触生产路径（宪法 §9.6 测试隔离的本意）。
    """
    d = Path(tempfile.mkdtemp(prefix="maint2_queue_"))
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def queue_root(off_lane_root: Path) -> Path:
    root = off_lane_root / "queue"
    (root / "dead").mkdir(parents=True)
    return root


@pytest.fixture()
def stub_enq(monkeypatch):
    """把 enqueue_item 与两个副作用尾巴换成记录桩（本试件测的是闸，不是入队本体）。"""
    calls: list[dict] = []

    def fake_enqueue(session_id, message, payload, *, queue_root=None, options=None, **kw):
        calls.append({"payload": payload, "options": options})
        return {"qid": "q-20261011-st-probe-0001", "session_id": session_id, "files": []}

    monkeypatch.setattr(cq, "enqueue_item", fake_enqueue)
    monkeypatch.setattr(cq, "_notify_task_board_requeued", lambda *a, **k: None)
    return calls


def test_from_bag_with_regression_is_refused(queue_root: Path, stub_enq, off_lane_root: Path) -> None:
    _make_dead_bag(queue_root, qid="q-20261011-st-probe-0001", rel="a.txt", content=b"old only\n")
    wt = off_lane_root / "lane"
    wt.mkdir()
    monkey_target = "_snapshot_head_regressions"
    orig = getattr(cq, monkey_target)
    setattr(cq, monkey_target, lambda w, payload, **kw: [{"path": "a.txt", "head_only_lines": 3, "sample": ["x"]}])
    try:
        with pytest.raises(cq.RequeueError) as exc:
            cq.requeue_dead_item(
                "q-20261011-st-probe-0001", queue_root=queue_root, worktree_root=str(wt), from_bag=True
            )
    finally:
        setattr(cq, monkey_target, orig)
    assert "快照重放禁用于已修复袋" in str(exc.value)
    assert stub_enq == []  # 拒绝发生在入队之前：零新袋
    # 原死信项保持原样（不被标 requeued，不被动过）
    dead = json.loads((queue_root / "dead" / "q-20261011-st-probe-0001.json").read_text(encoding="utf-8"))
    assert "requeued" not in dead


def test_from_bag_override_marks_meta_and_lands(queue_root: Path, stub_enq, off_lane_root: Path) -> None:
    _make_dead_bag(queue_root, qid="q-20261011-st-probe-0002", rel="a.txt", content=b"old only\n")
    wt = off_lane_root / "lane2"
    wt.mkdir()
    orig = cq._snapshot_head_regressions
    cq._snapshot_head_regressions = lambda w, payload, **kw: [{"path": "a.txt", "head_only_lines": 3, "sample": ["x"]}]
    try:
        result = cq.requeue_dead_item(
            "q-20261011-st-probe-0002",
            queue_root=queue_root,
            worktree_root=str(wt),
            from_bag=True,
            allow_snapshot_replay=True,
        )
    finally:
        cq._snapshot_head_regressions = orig
    meta = stub_enq[0]["options"].meta_extra
    assert meta["snapshot_regressions_count"] == 1
    assert meta["snapshot_replay_allowed"] is True
    assert result["snapshot_regressions"][0]["path"] == "a.txt"


def test_worktree_branch_is_not_blocked_but_is_annotated(queue_root: Path, stub_enq, off_lane_root: Path) -> None:
    """在册 D7 修-重试工作流不许被硬拦（令卡红线：只标注不破坏）——但同一把尺必须量出来。"""
    wt = off_lane_root / "lane3"
    wt.mkdir()
    (wt / "a.txt").write_bytes(b"fixed content\n")
    _make_dead_bag(queue_root, qid="q-20261011-st-probe-0003", rel="a.txt", content=b"old only\n")
    orig = cq._snapshot_head_regressions
    cq._snapshot_head_regressions = lambda w, payload, **kw: [{"path": "a.txt", "head_only_lines": 2, "sample": []}]
    try:
        result = cq.requeue_dead_item("q-20261011-st-probe-0003", queue_root=queue_root, worktree_root=str(wt))
    finally:
        cq._snapshot_head_regressions = orig
    assert stub_enq, "工作区分支应照常入队（不拦）"
    assert result["snapshot_regressions"][0]["head_only_lines"] == 2
    assert stub_enq[0]["options"].meta_extra["snapshot_regressions_count"] == 1
    assert "snapshot_replay_allowed" not in stub_enq[0]["options"].meta_extra  # 未越权，不打越权标


def test_from_bag_without_regression_passes(queue_root: Path, stub_enq, off_lane_root: Path) -> None:
    """反向钉桩：干净重放（无回归）不得被新闸误伤——防我把"补防"做成"一律拒"。"""
    wt = off_lane_root / "lane4"
    wt.mkdir()
    _make_dead_bag(queue_root, qid="q-20261011-st-probe-0004", rel="a.txt", content=b"same as head\n")
    result = cq.requeue_dead_item(
        "q-20261011-st-probe-0004", queue_root=queue_root, worktree_root=str(wt), from_bag=True
    )
    assert result["snapshot_regressions"] == []
    assert stub_enq
    assert "snapshot_regressions_count" not in stub_enq[0]["options"].meta_extra


# ---------------------------------------------------------------------------
# 3. T13：dead-archive 属主过滤
# ---------------------------------------------------------------------------


def test_session_filter_gate_is_fail_closed() -> None:
    cq._assert_session_filter_closed({"st-a"}, "st-a", "q-20261011-st-a-0001")  # 集内＝放行
    with pytest.raises(cq.DeadArchiveError) as exc:
        cq._assert_session_filter_closed({"st-a"}, "st-b", "q-20261011-st-b-0001")
    assert "零 mv" in str(exc.value)
    with pytest.raises(cq.DeadArchiveError):
        cq._assert_session_filter_closed({"st-a"}, "", "q-20261011-unknown-0001")  # 空属主也拒


def _dead_letter(root: Path, qid: str, sid: str) -> Path:
    p = root / "dead" / f"{qid}.json"
    p.write_text(
        json.dumps(
            {
                "qid": qid,
                "session_id": sid,
                "dead_at": (datetime.now().astimezone() - timedelta(days=30)).isoformat(),
                "dead_reason": "GATE:DEMO",
                "files": [],
                "meta": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return p


@pytest.fixture()
def archive_root(queue_root: Path) -> Path:
    for i, sid in enumerate(["st-a", "st-a", "st-b"], start=1):
        _dead_letter(queue_root, f"q-20260901-{sid}-000{i}", sid)
    return queue_root


def test_dead_archive_session_filter_moves_only_requested_owner(archive_root: Path) -> None:
    result = cq.dead_archive_letters(
        archive_root,
        days=7,
        execute=True,
        landed_checker=lambda path, sha: True,
        sessions={"st-a"},
    )
    assert len(result["archived"]) == 2
    assert all(q.startswith("q-20260901-st-a") for q in result["archived"])
    assert result["kept"]["other_session"] == 1
    assert (archive_root / "dead" / "q-20260901-st-b-0003.json").exists(), "他人死信必须原地不动"
    bags = list(archive_root.glob("dead_archive_*"))
    assert len(bags) == 1
    lines = [json.loads(x) for x in (bags[0] / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(lines) == 2 and all("st-a" in l["qid"] for l in lines)


def test_dead_archive_without_sessions_keeps_legacy_full_sweep(archive_root: Path) -> None:
    """向后兼容：不给 sessions＝旧全量行为（不得静默变成"什么都不做"）。"""
    result = cq.dead_archive_letters(
        archive_root,
        days=7,
        execute=True,
        landed_checker=lambda path, sha: True,
    )
    assert len(result["archived"]) == 3
    assert result["kept"]["other_session"] == 0


def test_cli_parser_accepts_the_two_new_flags(tmp_path_factory) -> None:
    """新旗必须真在 CLI 上（--help 实测面），否则处方又是一条假指引。"""
    script = Path(__file__).resolve().parents[3] / "scripts" / "commit_queue.py"
    proc = subprocess.run(
        [sys.executable, str(script), "requeue", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "--allow-snapshot-replay" in proc.stdout
    proc2 = subprocess.run(
        [sys.executable, str(script), "dead-archive", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc2.returncode == 0, proc2.stderr
    assert "--session" in proc2.stdout


def test_prescriptions_no_longer_name_a_flag_that_does_not_exist() -> None:
    """死信处方不得把 `--adopt-prior-work` 写成 requeue 的命令旗（同门连环死的传导面）。

    判据口径＝**命令形态**命中才算违规：`requeue` 与该旗之间只允许 qid/空白/尖括号。
    更正文案里以说明口吻提到该旗（"…是 git_commit.py 的旗，requeue 无此旗"）属解释
    而非指引，不计违规——否则这条尺会把"更正本身"判成问题，逼我把说明删掉。
    """
    text = (
        Path(__file__).resolve().parents[3] / "scripts" / "governance" / "wave1b" / "dead_letter_prescriptions.py"
    ).read_text(encoding="utf-8")
    offending = re.findall(r"requeue(?:\s+(?:<qid>|qid))?\s+--adopt-prior-work", text)
    assert offending == [], f"处方仍在教 requeue 不存在的旗：{offending[:3]}"


# ---------------------------------------------------------------------------
# 4. pristine 红证：原始字节里这些能力确实不存在（红来自字节，不来自推测）
# ---------------------------------------------------------------------------


def test_pristine_dev_bytes_lack_the_two_capabilities() -> None:
    text = _pristine_text()
    assert "_snapshot_head_regressions" not in text, "dev 版应查无该判据（在册未落地判据，本班才落地）"
    assert "allow_snapshot_replay" not in text
    assert "snapshot_regressions_count" not in text
    assert '"--session",\n        action="append"' not in text  # dead-archive 的 --session 是新增
    assert "other_session" not in text
