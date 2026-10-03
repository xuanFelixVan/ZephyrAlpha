# [A_test] module_id: MOD-GOV_commit_queue_backfill_lane | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_commit_queue_backfill_lane
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; subprocess; sqlite3; scripts.commit_queue
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_backfill_lane.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根 + tmp task_board DB，绝不碰主仓 .runtime 与真实 dev）；
#              每条尺既红且绿（阳性=缺基底必回填/第 3 版必喊人，阴性=dry-run 零写/已有值跳过/不同路径不融合）
# [MODIFY-GUARD] 车道 C 回归闸（2026-10-03）：摘掉 backfill-base-head 子命令或车道复发告警即红
# [STABILITY] volatile
# [SAFETY] L
# [TTL] permanent
"""车道 C 回归尺（2026-10-03）：

① backfill-base-head：F-AUDIT-QUEUE-04 修正前入袋的 103 只死袋缺 base_head ⇒
   史实归因结构性失效（落地器只能走 _legacy_base_drift_reason 时间基底判定）。
   回填两分支：blob 史证（精确）优先，created_at 时间基底（rev-list --before dev）兜底。
② 车道复发告警：同一 (session_id, 死因族, 首个文件路径) 组合被同一道门禁反复挡回
   （生产实测 11 版）无告警——第 3 版当场喊人，alerted 位幂等一次。
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from pathlib import Path

import pytest

import scripts.commit_queue as cq

REPO_ROOT = Path(__file__).resolve().parents[2]

#: 三档受控提交时刻（+08:00 与生产 created_at 同偏移——rev-list --before/时间过滤都吃它）
D1 = "2026-09-20T10:00:00+08:00"
D2 = "2026-09-21T10:00:00+08:00"
D3 = "2026-09-22T10:00:00+08:00"
D4 = "2026-09-23T10:00:00+08:00"  # 袋 created_at（晚于全部提交）


def _git(cwd: Path, *args: str, committer_date: str | None = None) -> str:
    env = {**os.environ}
    if committer_date:
        env["GIT_COMMITTER_DATE"] = committer_date
    r = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=120,
    )
    assert r.returncode == 0, f"git {' '.join(args)} -> {r.stderr[:300]}"
    return r.stdout.strip()


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """tmp 真 git 仓（dev 分支）——零生产写入，口径同 test_commit_queue_base_head.repo。"""
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "dev")
    _git(r, "config", "user.email", "probe@local")
    _git(r, "config", "user.name", "probe")
    _git(r, "config", "core.autocrlf", "false")
    return r


def _commit(repo: Path, path: str, text: str, date: str, msg: str) -> str:
    """受控时刻提交（author+committer 双 date——rev-list --before 按 committer date）。"""
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    _git(repo, "add", "--", path)
    _git(repo, "commit", "-qm", msg, "--date", date, committer_date=date)
    return _git(repo, "rev-parse", "HEAD")


def _bag(qid: str, session: str, created_at: str, files: list[dict], **extra) -> dict:
    return {
        "qid": qid,
        "session_id": session,
        "created_at": created_at,
        "branch": "dev",
        "base_head": None,
        "message": "probe",
        "files": files,
        **extra,
    }


def _put_dead(qroot: Path, bag: dict) -> Path:
    dead = qroot / "dead"
    dead.mkdir(parents=True, exist_ok=True)
    path = dead / f"{bag['qid']}.json"
    path.write_text(json.dumps(bag, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# ① 分支一：base_blob 史证（精确优先）
# ---------------------------------------------------------------------------


def test_backfill_blob_branch_single_file(repo: Path, tmp_path: Path) -> None:
    """blob 史证取「树中该 blob 且早于 created_at」的 commit——晚于的树改动不采信。"""
    c1 = _commit(repo, "x.md", "v1\n", D1, "c1 seed")
    _commit(repo, "x.md", "v2\n", D2, "c2 same path drifts")  # 同路径后续改动，树中 blob 已非 v1
    blob_v1 = _git(repo, "rev-parse", f"{c1}:x.md")
    qroot = tmp_path / "queue"
    _put_dead(
        qroot,
        _bag(
            "q-20260924-sessA-0001",
            "sessA",
            D4,
            [
                {"path": "x.md", "blob_sha256": "h", "base_blob": blob_v1, "action": "modify"},
            ],
        ),
    )
    result = cq.backfill_base_heads(qroot, repo_root=repo, execute=True)
    assert len(result["backfilled"]) == 1 and not result["failed"], result
    assert result["backfilled"][0]["base_head"] == c1, "blob 史证必须指到 v1 所在的 c1，而非同路径后来的 c2"
    assert result["backfilled"][0]["method"] == "base_blob"


def test_backfill_blob_branch_multi_file_consensus(repo: Path, tmp_path: Path) -> None:
    """多文件袋取能命中最多文件的候选——单文件各自最优时仍取共识命中最大者。"""
    c1 = _commit(repo, "a.md", "a1\n", D1, "c1 build a")  # c1 树：仅 a=a1
    c2 = _commit(repo, "b.md", "b1\n", D2, "c2 build b")  # c2 树：a=a1, b=b1
    _commit(repo, "a.md", "a2\n", D3, "c3 drift a")  # c3 树：a=a2, b=b1
    blob_a1 = _git(repo, "rev-parse", f"{c1}:a.md")
    blob_b1 = _git(repo, "rev-parse", f"{c2}:b.md")
    qroot = tmp_path / "queue"
    _put_dead(
        qroot,
        _bag(
            "q-20260924-sessB-0001",
            "sessB",
            D4,
            [
                {"path": "a.md", "blob_sha256": "h", "base_blob": blob_a1, "action": "modify"},
                {"path": "b.md", "blob_sha256": "h", "base_blob": blob_b1, "action": "modify"},
            ],
        ),
    )
    result = cq.backfill_base_heads(qroot, repo_root=repo, execute=True)
    assert result["backfilled"][0]["base_head"] == c2, "c2 同时命中 a/b 两个文件（c1 只命中 a）——多文件共识必须取 c2"


def test_backfill_blob_all_candidates_after_created_at_falls_to_time(repo: Path, tmp_path: Path) -> None:
    """blob 候选全晚于 created_at ⇒ 分支①不可证，落②时间基底兜底（不造史）。"""
    c0 = _commit(repo, "seed.md", "s\n", D1, "c0 dev early seed")
    _commit(repo, "y.md", "v1\n", D2, "c1 y born after bag")  # y.md 的全部历史都晚于袋创建
    blob_v1 = _git(repo, "rev-parse", "HEAD:y.md")
    qroot = tmp_path / "queue"
    # 袋创建于 D1 与 D2 之间：y.md 上不存在早于袋的树匹配（blob 史证不可证）
    _put_dead(
        qroot,
        _bag(
            "q-20260924-sessC-0001",
            "sessC",
            "2026-09-20T12:00:00+08:00",
            [
                {"path": "y.md", "blob_sha256": "h", "base_blob": blob_v1, "action": "modify"},
            ],
        ),
    )
    result = cq.backfill_base_heads(qroot, repo_root=repo, execute=True)
    assert result["backfilled"][0]["method"] == "created_at", result
    assert result["backfilled"][0]["base_head"] == c0, "时间基底=袋创建时点的 dev HEAD（c0）"


# ---------------------------------------------------------------------------
# ② 分支二：created_at 时间基底 + 失败面
# ---------------------------------------------------------------------------


def test_backfill_time_branch_uses_dev_head_before_created_at(repo: Path, tmp_path: Path) -> None:
    """无 base_blob ⇒ rev-list --before=<created_at> dev 取当时 dev HEAD（+08:00 原样传 git）。"""
    _commit(repo, "a.md", "a1\n", D1, "c1")
    c2 = _commit(repo, "b.md", "b1\n", D2, "c2")
    _commit(repo, "c.md", "c1\n", D3, "c3")
    qroot = tmp_path / "queue"
    # created_at 落在 D2 与 D3 之间 → 当时 dev HEAD = c2
    _put_dead(
        qroot,
        _bag(
            "q-20260924-sessD-0001",
            "sessD",
            "2026-09-21T12:00:00+08:00",
            [
                {"path": "d.md", "blob_sha256": "h", "base_blob": None, "action": "modify"},
            ],
        ),
    )
    result = cq.backfill_base_heads(qroot, repo_root=repo, execute=True)
    assert result["backfilled"][0]["base_head"] == c2
    assert result["backfilled"][0]["method"] == "created_at"


def test_backfill_no_dev_commit_before_created_at_fails_with_reason(repo: Path, tmp_path: Path) -> None:
    """dev 无早于袋创建的 commit ⇒ 两分支皆不可证，失败并给出原因（不猜基底）。"""
    _commit(repo, "a.md", "a1\n", D2, "only late commit")
    qroot = tmp_path / "queue"
    _put_dead(
        qroot,
        _bag(
            "q-20260924-sessE-0001",
            "sessE",
            D1,
            [
                {"path": "a.md", "blob_sha256": "h", "base_blob": None, "action": "modify"},
            ],
        ),
    )
    result = cq.backfill_base_heads(qroot, repo_root=repo, execute=True)
    assert not result["backfilled"] and len(result["failed"]) == 1
    assert "时间基底" in result["failed"][0]["reason"], result["failed"][0]


def test_backfill_unparseable_created_at_fails(repo: Path, tmp_path: Path) -> None:
    """created_at 缺失/坏值 ⇒ 两分支都依赖时序约束，整袋失败报原因。"""
    qroot = tmp_path / "queue"
    _put_dead(
        qroot,
        _bag(
            "q-20260924-sessF-0001",
            "sessF",
            "not-a-date",
            [
                {"path": "a.md", "blob_sha256": "h", "base_blob": None, "action": "modify"},
            ],
        ),
    )
    result = cq.backfill_base_heads(qroot, repo_root=repo, execute=True)
    assert len(result["failed"]) == 1 and "created_at" in result["failed"][0]["reason"]


# ---------------------------------------------------------------------------
# ③ 安全哲学：dry-run 默认 / execute 写回 / 幂等 / 只动 base_head
# ---------------------------------------------------------------------------


def test_backfill_dry_run_default_execute_writes_and_idempotent(repo: Path, tmp_path: Path) -> None:
    """缺省 dry-run 零写盘；--execute 才写；再跑全 skip（幂等，重跑零变化）。"""
    c1 = _commit(repo, "x.md", "v1\n", D1, "c1")
    blob_v1 = _git(repo, "rev-parse", f"{c1}:x.md")
    qroot = tmp_path / "queue"
    bag_path = _put_dead(
        qroot,
        _bag(
            "q-20260924-sessG-0001",
            "sessG",
            D4,
            [
                {"path": "x.md", "blob_sha256": "h", "base_blob": blob_v1, "action": "modify"},
            ],
        ),
    )
    original = bag_path.read_text(encoding="utf-8")

    dry = cq.backfill_base_heads(qroot, repo_root=repo, execute=False)
    assert len(dry["backfilled"]) == 1 and dry["execute"] is False
    assert bag_path.read_text(encoding="utf-8") == original, "dry-run 不得有任何盘面变化"

    wet = cq.backfill_base_heads(qroot, repo_root=repo, execute=True)
    assert len(wet["backfilled"]) == 1
    landed = json.loads(bag_path.read_text(encoding="utf-8"))
    assert landed["base_head"] == c1

    # 幂等：已有 base_head 的袋跳过且值不被改写
    again = cq.backfill_base_heads(qroot, repo_root=repo, execute=True)
    assert again["backfilled"] == [] and again["skipped"] == [bag_path.stem], again
    assert json.loads(bag_path.read_text(encoding="utf-8"))["base_head"] == c1


def test_backfill_only_touches_base_head_field(repo: Path, tmp_path: Path) -> None:
    """写回只改 base_head 一个字段——其余字段（含嵌套 meta/files）逐值保留。"""
    c1 = _commit(repo, "x.md", "v1\n", D1, "c1")
    blob_v1 = _git(repo, "rev-parse", f"{c1}:x.md")
    qroot = tmp_path / "queue"
    bag = _bag(
        "q-20260924-sessH-0001",
        "sessH",
        D4,
        [
            {"path": "x.md", "blob_sha256": "h", "base_blob": blob_v1, "action": "modify"},
        ],
    )
    bag["meta"] = {"priority": 7, "task_id": "T-KEEP", "supersedes": ["q-old"]}
    bag["dead_reason"] = "conflict: probe"
    bag_path = _put_dead(qroot, bag)
    cq.backfill_base_heads(qroot, repo_root=repo, execute=True)
    after = json.loads(bag_path.read_text(encoding="utf-8"))
    after["base_head"] = None
    assert after == bag, "除 base_head 外任何字段被改动即违例"


def test_cli_backfill_smoke(repo: Path, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """CLI 子命令挂线：dry-run 计划面 + --json 机器可读输出。"""
    c1 = _commit(repo, "x.md", "v1\n", D1, "c1")
    blob_v1 = _git(repo, "rev-parse", f"{c1}:x.md")
    qroot = tmp_path / "queue"
    _put_dead(
        qroot,
        _bag(
            "q-20260924-sessI-0001",
            "sessI",
            D4,
            [
                {"path": "x.md", "blob_sha256": "h", "base_blob": blob_v1, "action": "modify"},
            ],
        ),
    )
    rc = cq.main(
        [
            "--queue-root",
            str(qroot),
            "backfill-base-head",
            "--repo-root",
            str(repo),
            "--json",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "BACKFILL-BASE-HEAD: backfilled=1" in out
    payload = json.loads(out[out.index("{") :])
    assert payload["backfilled"][0]["base_head"] == c1


# ---------------------------------------------------------------------------
# ④ 车道复发告警：同 (session, 死因族, 首路径) 第 3 次当场喊人
# ---------------------------------------------------------------------------


@pytest.fixture()
def board_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """task_board 隔离 DB（绝不碰生产板）。"""
    db = tmp_path / "task_board.db"
    monkeypatch.setenv("ZEPHYR_TASK_BOARD_DB", str(db))
    return db


def _seal_dead(qroot: Path, qid: str, session: str, path: str, reason: str) -> dict:
    item = {
        "qid": qid,
        "session_id": session,
        "created_at": D1,
        "dead_reason": reason,
        "dead_at": D2,
        "files": [{"path": path, "blob_sha256": "h", "base_blob": None, "action": "modify"}],
    }
    cq._seal_dead_letter(qroot, item)
    return item


def _lane_state(qroot: Path) -> dict:
    return json.loads((qroot / "dead" / "_recurrence_state.json").read_text(encoding="utf-8"))


def _deadletter_tag(db: Path) -> dict:
    conn = sqlite3.connect(str(db))
    try:
        row = conn.execute(
            "SELECT metadata_json FROM tasks WHERE task_id=?",
            (cq._DEADLETTER_WATCH_TASK_ID,),
        ).fetchone()
    finally:
        conn.close()
    assert row is not None, "挂载点专 task 应被幂等自建"
    return json.loads(row[0])["deadletter"]


def test_lane_alert_fires_on_third_once_and_stops(tmp_path: Path, board_db: Path) -> None:
    """阳性：第 3 次死亡当场告警（task_board 打标）；第 4 次不再重复（alerted 幂等位）。"""
    qroot = tmp_path / "queue"
    for i in range(1, 5):
        _seal_dead(qroot, f"q-20260924-sessL-{i:04d}", "sessL", "a.md", "CREATE-GUARD: blocked")
    state = _lane_state(qroot)
    entry = state["session_lanes"]["sessL|other|a.md"]
    assert entry["count"] == 4, entry
    assert entry["alerted"] is True, "第 3 次告警成功后必须置位"
    tag = _deadletter_tag(board_db)
    assert tag["qid"] == "q-20260924-sessL-0003", (
        f"告警样本 qid 应停在第 3 袋（第 4 次不得重复打标），实得 {tag['qid']}"
    )
    assert "session_lane_stall" in tag["reason"] and "sessL" in tag["reason"]
    # 签名复发键面（signatures）不被车道键面（session_lanes）覆盖——合并写互不吞
    assert state["signatures"], "合并写破裂：session_lanes 写入抹掉了 signatures 键面"


def test_lane_alert_counts_only_below_threshold(tmp_path: Path, board_db: Path) -> None:
    """阴性：第 1/2 次只计数不告警（阈值 3=首次达到才喊，不是每次都喊）。"""
    qroot = tmp_path / "queue"
    _seal_dead(qroot, "q-20260924-sessM-0001", "sessM", "a.md", "CREATE-GUARD: blocked")
    _seal_dead(qroot, "q-20260924-sessM-0002", "sessM", "a.md", "CREATE-GUARD: blocked")
    entry = _lane_state(qroot)["session_lanes"]["sessM|other|a.md"]
    assert entry["count"] == 2 and entry["alerted"] is False
    if board_db.exists():  # 板未被触碰时连 DB 文件都不落（零副作用强于空表）
        conn = sqlite3.connect(str(board_db))
        try:
            rows = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        finally:
            conn.close()
        assert rows == 0, "未达阈值不得碰 task_board"


def test_lane_alert_different_paths_not_fused(tmp_path: Path, board_db: Path) -> None:
    """阴性：同会话同死因但不同文件路径 ⇒ 不同车道，互不累计、不误告。"""
    qroot = tmp_path / "queue"
    for i in range(1, 4):
        _seal_dead(qroot, f"q-20260924-sessN-{i:04d}", "sessN", "a.md", "CREATE-GUARD: blocked")
    _seal_dead(qroot, "q-20260924-sessN-0004", "sessN", "z.md", "CREATE-GUARD: blocked")
    lanes = _lane_state(qroot)["session_lanes"]
    assert lanes["sessN|other|a.md"]["count"] == 3
    assert lanes["sessN|other|z.md"]["count"] == 1, "不同路径是独立车道（z.md 一次不触发告警）"
    tag = _deadletter_tag(board_db)
    assert "a.md" in tag["reason"] and "z.md" not in tag["reason"], "告警必须只针对 a.md 车道"


def test_lane_alert_board_unreachable_fail_open(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """板不可达（父路径是文件）⇒ 封印主流程照常、alerted 不置位（下次复发补告）。"""
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv("ZEPHYR_TASK_BOARD_DB", str(blocker / "task_board.db"))
    qroot = tmp_path / "queue"
    for i in range(1, 4):
        _seal_dead(qroot, f"q-20260924-sessP-{i:04d}", "sessP", "a.md", "CREATE-GUARD: blocked")
    entry = _lane_state(qroot)["session_lanes"]["sessP|other|a.md"]
    assert entry["count"] == 3, "板不可达不得阻断封印与计数（fail-open，宁漏不误）"
    assert entry["alerted"] is False, "打标未送达不得置位——否则告警被幂等位吞掉"


def test_lane_alert_via_drain_dead_exit(tmp_path: Path, board_db: Path) -> None:
    """集成：drain 真死信出口三轮（enqueue→死→再 enqueue 同键袋）第 3 袋触发告警。

    三袋须分三轮入队：同 session 同 path 的 pending 袋会被 compaction 合并，
    串行"死一只补一只"恰是生产 11 版反复挡回的真实形态。
    """
    qroot = tmp_path / "queue"

    def _fail_landing(item: dict, root: Path) -> cq.LandingResult:
        return cq.LandingResult(ok=False, reason="CREATE-GUARD: probe gate blocked")

    for i in range(1, 4):
        cq.enqueue_item("sessQ", f"probe {i}", [("a.md", f"body {i}\n".encode())], queue_root=qroot)
        stats = cq.drain_queue(qroot, landing=_fail_landing)
        assert stats["dead"] == 1, f"第 {i} 轮应恰好死一只（实得 {stats}）"
    state = _lane_state(qroot)
    entry = state["session_lanes"]["sessQ|other|a.md"]
    assert entry["count"] == 3 and entry["alerted"] is True, entry
    tag = _deadletter_tag(board_db)
    assert "sessQ" in tag["reason"], "第 3 版必须当场喊人（drain 出口→封印→车道告警链路接通）"
