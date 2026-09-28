# [BLUEPRINT] MOD-GOV_ENFORCEMENT | docs/03_modules/_domain_governance/blueprint.md | §coordination_state_board
# [MODULE] tests.governance.test_coordination_state_board
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.coordination_state_board; zephyr.security.access_control.session_concurrency (SessionRegistry); stdlib (subprocess/pathlib/time)
# [CONSUMERS] pytest tests/governance/test_coordination_state_board.py
# [STARTUP] manual / pre-commit gate 自家测试
# [MATURITY] candidate
# [INVARIANTS] 全件在 tmp_path 自建 git 仓上跑——零生产 data/、零热册、零真实 registry；红测必真红（向上解析陷阱/未提交面/新鲜度/会话等值性四证各自断言反向情形）
# [MODIFY-GUARD] 断言的旗标词表与 reason 码是 coordination_state_board 的行为契约
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git 不可用→整体 skip（非静默通过）
# [TESTS] tests/governance/test_coordination_state_board.py
# [A_test] module_id=MOD-GOV_ENFORCEMENT | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""施工公告牌红证四件套（st-p11-board）。

覆盖：①向上解析重复计数陷阱被结构拦下 + 父子几何红旗；②车道"只改不提交"必上板；
③陈旧 generated_at 必判 stale；④公告牌 session 集 == 注册表活跃集等值性。
"""

from __future__ import annotations

import shutil
import subprocess
import time
from datetime import timedelta
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge.coordination_state_board import (
    _self_check,
    build_board,
    freshness_of,
    list_worktrees,
    load_board,
    render_markdown,
    scan_lane,
    session_ids_of,
    write_board,
)
from zephyr.security.access_control.session_concurrency import SessionRegistry
from zephyr.shared.utils.time_utils import now_utc

_HAS_GIT = shutil.which("git") is not None

pytestmark = pytest.mark.skipif(not _HAS_GIT, reason="git 不可用则本套件无意义")


def _git(root: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", *args], cwd=str(root), capture_output=True, text=True, check=True,
    )
    return (r.stdout or "").strip()


def _init_repo(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-b", "main", ".")
    _git(root, "config", "user.email", "t@example.invalid")
    _git(root, "config", "user.name", "t")
    _git(root, "config", "commit.gpgsign", "false")
    (root / "a.txt").write_text("one\n", encoding="utf-8")
    (root / "b.md").write_text("keep\n", encoding="utf-8")
    _git(root, "add", "a.txt", "b.md")
    _git(root, "commit", "-m", "seed")
    return root


@pytest.fixture()
def fleet(tmp_path: Path) -> dict:
    """主仓 + 一条真车道 worktree + 一个非 worktree 假车道目录（陷阱本体）。"""
    main = _init_repo(tmp_path / "repo")
    lane = main / ".worktrees" / "lane-real"
    lane.parent.mkdir(parents=True, exist_ok=True)
    _git(main, "worktree", "add", "-b", "lane-real", str(lane))
    fake = main / ".worktrees" / "lane-not-a-worktree"
    fake.mkdir(parents=True, exist_ok=True)
    (fake / "scratch.txt").write_text("draft only, never committed\n", encoding="utf-8")
    return {"main": main, "lane": lane, "fake": fake}


# ── 证一：向上解析陷阱 ───────────────────────────────────────────────────────


def test_fake_lane_dir_is_rejected_not_counted_as_lane(fleet: dict) -> None:
    """假车道目录（非 worktree）必被结构拦下，绝不以主区 dirt 冒充一条车道的 dirt。"""
    main: Path = fleet["main"]
    lanes, rejected = list_worktrees(main)
    paths = {l["path"].replace("\\", "/").lower() for l in lanes}
    reasons = {r["path"].replace("\\", "/").lower(): r["reason"] for r in rejected}
    fake_key = str(fleet["fake"]).replace("\\", "/").lower()
    assert fake_key in reasons, "候选目录未被验证=陷阱防线失效"
    assert reasons[fake_key] == "UPWARD_RESOLUTION"
    assert fake_key not in paths, "非 worktree 目录被算作车道 ⇒ 主区 dirt 重复计数"
    # 主区 dirt 只被计一次（等值几何：真车道集合里不允许出现两份主区清单）
    mains = [l for l in lanes if l["role"] == "main_worktree"]
    assert len(mains) == 1
    assert (main / ".worktrees" / "lane-real").is_dir()


def test_scan_of_naive_candidate_reports_parent_dirt(fleet: dict) -> None:
    """对照组：证明"陷阱确实会出事"——不加 toplevel 自证直接扫假目录，得到的是主区脏清单。"""
    main: Path = fleet["main"]
    (main / "a.txt").write_text("two\n", encoding="utf-8")  # 主区一处未提交改动
    naive = scan_lane(Path(fleet["fake"]), {"path": str(fleet["fake"]), "lane": "fake",
                                            "role": "lane"})
    assert "a.txt" in naive["dirty_paths_sample"], "对照失效：主区改动未出现在假车道视图里"
    verified, _ = list_worktrees(main)
    assert all(l["toplevel_verified"] for l in verified)


def test_self_check_red_flag_on_ancestor_geometry() -> None:
    """父子几何 + 同脏清单 ⇒ 红旗（这就是向上解析发作的确证形态）。"""
    def _lane(path: str, n: int, fps: str) -> dict:
        return {"status": "ok", "path": path, "dirty_total": n, "dirty_fingerprint": fps,
                "lane": Path(path).name, "role": "lane"}

    parent = [_lane("/w/repo", 5, "aaaa")]
    bug = parent + [_lane("/w/repo/.worktrees/scratch", 5, "aaaa")]
    res = _self_check(bug, [])
    assert res["red_flag_upward_resolution"] is True
    assert res["upward_resolution_evidence"][0]["ancestor_geometry"] is True

    sibling = [_lane("/w/repo/.worktrees/lane-a", 5, "aaaa"),
               _lane("/w/repo/.worktrees/lane-b", 5, "aaaa")]
    res2 = _self_check(sibling, [])
    assert res2["red_flag_upward_resolution"] is False, "兄弟副本不该报红（误警即判据失真）"
    assert len(res2["sibling_copy_suspects"]) == 1

    distinct = [_lane("/w/a", 5, "aaaa"), _lane("/w/b", 5, "bbbb")]
    res3 = _self_check(distinct, [])
    assert res3["red_flag_upward_resolution"] is False
    assert res3["identical_dirty_groups"] == []
    assert len(res3["equal_count_different_content"]) == 1, "等数异集应记巧合而非漏报"


# ── 证二：只改不提交必上板 ───────────────────────────────────────────────────


def test_uncommitted_edit_in_lane_appears_on_board(fleet: dict) -> None:
    """B1 的正解：不 claim 不提交，只改盘面文件，也必须出现在公告牌。"""
    lane: Path = fleet["lane"]
    (lane / "a.txt").write_text("edited but never committed\n", encoding="utf-8")
    (lane / "brand_new.py").write_text("x = 1\n", encoding="utf-8")
    board = build_board(fleet["main"], fast=True, skip_schtasks=True, classify_top_n=0)
    lanes = {l["path"].replace("\\", "/").lower(): l
             for l in board["worktrees"]["lanes"]}
    key = str(lane).replace("\\", "/").lower()
    assert key in lanes, "真车道未进入公告牌"
    entry = lanes[key]
    assert entry["dirty_total"] == 2
    assert entry["untracked"] == 1
    assert entry["tracked_modifications_total"] == 1
    assert set(entry["tracked_modifications_sample"]) == {"a.txt"}
    hits = [x for x in board["answers"]["uncommitted_edit_lanes"]
            if x["path"].replace("\\", "/").lower() == key]
    assert hits and hits[0]["dirty_total"] == 2, "answers 面漏报未提交改动"
    assert board["worktrees"]["self_check"]["red_flag_upward_resolution"] is False


def test_classify_reuse_attribution_is_carried_into_board(fleet: dict) -> None:
    """净零证据：判读分类来自既有 classify_workspace_wip.classify()，公告牌不另立分类法。"""
    lane: Path = fleet["lane"]
    (lane / "a.txt").write_text("wip\n", encoding="utf-8")
    board = build_board(fleet["main"], budget_seconds=600, classify_top_n=99,
                        skip_schtasks=True)
    entry = next(l for l in board["worktrees"]["lanes"]
                 if l["path"].replace("\\", "/").lower()
                 == str(lane).replace("\\", "/").lower())
    attr = entry.get("attribution") or {}
    assert attr.get("available") is True, "判读器未复用＝净零声明不成立"
    assert {"active_wip", "fresh_change", "stale_rollback", "untracked_new"} <= set(
        attr["categories"]), "分类词表与既有判读器不同源"
    assert "classify_workspace_wip.classify" in attr["produced_by"]


# ── 证三：新鲜度 ─────────────────────────────────────────────────────────────


def test_stale_generated_at_is_flagged(fleet: dict) -> None:
    """过期读数必判 stale（混合钟/陈旧板是本仓在册事故）。"""
    base = now_utc()
    board = build_board(fleet["main"], fast=True, skip_schtasks=True, classify_top_n=0)
    assert board["clock_consistency"] == "OK"
    assert board["utc_offset_seconds"] == int(
        (base.astimezone().utcoffset() or timedelta(0)).total_seconds())
    fresh = freshness_of(board, now=base)
    assert fresh["stale"] is False and fresh["verdict"] == "FRESH"
    aged = dict(board, epoch_seconds=(base - timedelta(seconds=7200)).timestamp())
    stale = freshness_of(aged, now=base)
    assert stale["stale"] is True and stale["verdict"] == "STALE_RESCAN_REQUIRED"
    broken = freshness_of({"generated_at_utc": "not-a-time", "epoch_seconds": None}, now=base)
    assert broken["stale"] is True and broken["reason"] == "UNPARSEABLE_generated_at"


def test_board_roundtrips_as_valid_yaml_with_commands(fleet: dict) -> None:
    """机读产物必须可被一次调用读回，且每带字段都有 produced_by 溯源。"""
    out = fleet["main"] / "board_out"
    board = build_board(fleet["main"], fast=True, skip_schtasks=True, classify_top_n=0)
    paths = write_board(board, out)
    loaded = load_board(paths["yaml"])
    assert loaded["schema"] == "coordination_state_board/1"
    assert loaded["worktrees"]["self_check"]["rejected_reasons"] == board["worktrees"][
        "self_check"]["rejected_reasons"]
    assert loaded["_freshness"]["stale"] is False
    assert "build_seconds" in loaded["measured"]
    for section in ("worktrees", "sessions", "claims", "queue", "automation", "answers"):
        assert section in loaded
    assert "produced_by" in loaded["queue"] and "produced_by" in loaded["claims"]
    md = render_markdown(board)
    assert md.startswith("---\nttl: task_bound\n")
    assert "施工公告牌" in md and "对话身份桥" in md
    assert time.time() >= board["epoch_seconds"]


# ── 证四：等值性 ─────────────────────────────────────────────────────────────


def test_board_session_set_equals_registry_live_set(fleet: dict) -> None:
    """公告牌不得自造活跃集：与 SessionRegistry.list_active() 严格相等。"""
    main: Path = fleet["main"]
    reg = SessionRegistry(main)
    reg.register("live-a", pid=0)
    reg.register("live-b", pid=0)
    reg.register("gone-c", pid=0)
    data = reg.load()
    # 心跳年龄取"判死阈值与物理修剪宽限之间"：太旧会被 list_active() 物理删册（那是 B3 面的既有语义）
    data["gone-c"]["last_heartbeat"] = time.time() - 300
    reg.save(data)
    live = {s.session_id for s in SessionRegistry(main).list_active()}
    board = build_board(main, fast=True, skip_schtasks=True, classify_top_n=0)
    assert session_ids_of(board) == live == {"live-a", "live-b"}
    ids = {s["session_id"] for s in board["sessions"]["sessions"]}
    assert "gone-c" in ids and board["sessions"]["registry_dead_count"] >= 1
    assert board["sessions"]["live_count"] == len(live)
    assert board["sessions"]["dead_visible_window_seconds"]["judge_dead_after"] == 90
    for s in board["sessions"]["sessions"]:
        assert s["conversation_id"] == "UNKNOWN", "无桥即臆造映射＝B4 反例"
        assert s["identity_bridge_source"] == "NONE_IN_REPOSITORY"


# ── 附证：成本有界性与普查诚实性 ─────────────────────────────────────────────


def test_console_output_decodes_gbk_not_silently_empty() -> None:
    """中文 Windows 控制台码页：UTF-8 直读会把普查面变成"假干净 0 条"。"""
    from zephyr.gov_enforcement.rule_bridge.coordination_state_board import _decode_console

    gbk = "\\ZEPHYR-RESTORE-DRILL,就绪".encode("gbk")
    assert _decode_console(gbk).endswith("就绪")
    assert _decode_console("plain".encode("utf-8")) == "plain"
    assert isinstance(_decode_console(b"\xff\xfe\x81\x81"), str), "全码页失配也必须返回字符串"


def test_budget_bounded_scan_reports_coverage_honestly(fleet: dict) -> None:
    """超预算/超上限必须自报未覆盖——公告牌不许用"干净"掩盖"没看"。"""
    lane: Path = fleet["lane"]
    (lane / "a.txt").write_text("wip\n", encoding="utf-8")
    board = build_board(fleet["main"], fast=True, skip_schtasks=True, classify_top_n=0,
                        max_worktrees=1, budget_seconds=600)
    m = board["measured"]
    assert m["worktrees_scanned"] == 1
    assert m["worktrees_discovered"] >= 2
    assert m["truncated"] is True
    auto = board["automation"]
    assert auto["local_scheduled_tasks"]["query_status"] == "SKIPPED", "跳过查询须留痕非冒充结果"
    assert len(auto["blind_spots"]) >= 3
    assert all(b.get("observable") is False or b.get("observable") == "partial"
               for b in auto["blind_spots"]), "盲区条目必须自标不可观测"
    assert "honest_statement" in auto
