# [MODULE] tests.scripts.test_nine_face_watch
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] scripts.ops.nine_face_watch (九面测量/预算/告警面), pytest.MonkeyPatch
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] volatile
# [INVARIANTS] 全部落 tmp 目录（basetemp=.runtime/tmp/nfw_bt，48h TTL 清扫面，禁写生产 data/）；
#              假目录树实测九面计数；预算两侧/节流/告警双落点/OFF 降级/dry-run 零副作用
# [STABILITY] volatile
# [SAFETY] L
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_nine_face_watch.py — L5 九面遥测预算单测（st-diskp0-20261015）。

测试组:
- test_nine_face_counts_fake_tree: 假目录树实测九面计数逐面对齐
- test_over_budget_alerts_dual_sink: enabled=true + 收紧预算 → 超限 + 告警双落点
- test_under_budget_no_alert: enabled=true + 放宽预算 → 零告警
- test_disabled_off_degradation: enabled=false → 超限也只记不告警（出厂 OFF 降级）
- test_throttle_then_once: 60min 巡检节流（读基线 ts）+ once 跳过；告警冷却二次超限不刷屏
- test_dry_run_no_side_effect: dry-run 零写（无基线/无告警）
- test_budget_config_fallback_factory: 缺键回出厂预算/缺 flags.yaml 回 (False, 出厂)
- test_git_faces_none_on_error: 非 git 目录 → 车道/staged 面 None+errors，巡检不抛
- test_git_status_real_repo: 真 git 仓 staged+untracked 实测
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ops" / "nine_face_watch.py"


def _load_module(monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("nine_face_watch_under_test", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _write_flags(root: Path, enabled: bool, **budget) -> None:
    lines = ["flags:", "  nine_face_budget:", f"    enabled: {str(enabled).lower()}"]
    for k, v in budget.items():
        lines.append(f"    {k}: {v}")
    flags = root / "config" / "flags.yaml"
    flags.parent.mkdir(parents=True, exist_ok=True)
    flags.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _wt_porcelain(root: Path) -> str:
    """以给定根生成的 worktree porcelain 文本：主区+2 车道+1 pool+1 serializer。"""
    r = str(root).replace("\\", "/").rstrip("/")
    return (
        f"worktree {r}\n"
        f"worktree {r}/.aidrafts/st-a\n"
        f"worktree {r}/.worktrees/st-b\n"
        f"worktree {r}/.aidrafts_pool/pool-20260919-c433\n"
        f"worktree {r}/.runtime/commit_queue/worktrees/w0\n"
    )


#: staged(M )+untracked(??)+双脏(MM)=3；仅工作树改动(空格 X 位)不计 → staged=3
_ST_PORCELAIN = "M  a.py\n?? b.py\nMM d.py\n M c.py\n"


@pytest.fixture()
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """tmp 全套环境：假 .runtime 九面目录树 + flags（enabled/预算可按用例覆写）。"""
    mod = _load_module(monkeypatch)
    root = tmp_path / "repo"
    rt = root / ".runtime"
    # ① dead 袋：3 袋 q-*.json + 状态文件/杂件（不计数）
    dead = rt / "commit_queue" / "dead"
    dead.mkdir(parents=True)
    for i in range(3):
        (dead / f"q-20261016-test-{i:04d}.json").write_text("{}", encoding="utf-8")
    (dead / "_recurrence_state.json").write_text("{}", encoding="utf-8")
    # ⑨ pending 袋：2 袋
    pend = rt / "commit_queue" / "pending"
    pend.mkdir(parents=True)
    for i in range(2):
        (pend / f"q-20261016-test-{i:04d}.json").write_text("{}", encoding="utf-8")
    # ② tmp：4KiB
    tmpd = rt / "tmp" / "sub"
    tmpd.mkdir(parents=True)
    (tmpd / "blob.bin").write_bytes(b"x" * 4096)
    # ⑤ quarantine：2KiB 嵌套
    qd = rt / "quarantine" / "pack"
    qd.mkdir(parents=True)
    (qd / "evidence.bin").write_bytes(b"y" * 2048)
    # ⑥ sessions：2 目录 + 1 散件（散件不计数）
    sd = rt / "sessions"
    sd.mkdir(parents=True)
    (sd / "st-a").mkdir()
    (sd / "st-b").mkdir()
    (sd / "stray.txt").write_text("x", encoding="utf-8")
    # ⑦ audit：gate_audit 1KiB + audit 2KiB = 3KiB（探针填料名避开 nine_face_alerts.jsonl 真名）
    ga = rt / "gate_audit"
    ga.mkdir(parents=True)
    (ga / "ops_guard.jsonl").write_text("z" * 1024, encoding="utf-8")
    ad = rt / "audit"
    ad.mkdir(parents=True)
    (ad / "sample_probe.jsonl").write_text("w" * 2048, encoding="utf-8")
    # ⑧ .runtime 根散件：2 个
    (rt / "backup.lock").write_text("x", encoding="utf-8")
    (rt / "board_idx_offset.txt").write_text("x", encoding="utf-8")
    _write_flags(root, enabled=False)  # 出厂 OFF
    return {"mod": mod, "root": root, "rt": rt, "set_flags": _write_flags}


def test_nine_face_counts_fake_tree(env):
    """假目录树实测：九面计数逐面对齐（件数面整数/GiB 面三位小数）。"""
    e = env
    mod = e["mod"]
    faces, errors = mod.measure_faces(
        e["root"],
        worktree_porcelain=_wt_porcelain(e["root"]),
        status_porcelain=_ST_PORCELAIN,
    )
    assert errors == [], errors
    assert faces["dead_bags"] == 3
    assert faces["tmp_gib"] == round(4096 / mod.GIB, 3)
    assert faces["lanes"] == 2, faces
    assert faces["staged"] == 3, faces
    assert faces["quarantine_gib"] == round(2048 / mod.GIB, 3)
    assert faces["sessions"] == 2
    assert faces["audit_gib"] == round((1024 + 2048) / mod.GIB, 3)
    assert faces["root_files"] == 2
    assert faces["queue_backlog"] == 3 + 2


def test_parse_worktree_lanes_exclusions(env):
    """车道面去主区/pool/serializer 判据逐类实测（含反斜杠路径归一）。"""
    e = env
    # 主区/pool/serializer 全排除，仅余 2 条会话车道
    lanes = e["mod"]._parse_worktree_lanes(_wt_porcelain(Path("D:/fakerepo")), Path("D:/fakerepo"))
    assert lanes == ["D:/fakerepo/.aidrafts/st-a", "D:/fakerepo/.worktrees/st-b"], lanes
    # 仅主区+pool+serializer 三类 → 零车道
    only_excluded = (
        "worktree D:/fakerepo\n"
        "worktree D:/fakerepo/.aidrafts_pool/pool-20260919-c433\n"
        "worktree D:/fakerepo/.runtime/commit_queue/worktree\n"
    )
    assert e["mod"]._parse_worktree_lanes(only_excluded, Path("D:/fakerepo")) == []
    # 反斜杠/大小写路径归一后仍正确去主区
    bs = "worktree D:\\fakerepo\nworktree D:\\fakerepo\\.aidrafts\\st-c\n"
    assert e["mod"]._parse_worktree_lanes(bs, Path("D:/fakerepo")) == ["D:\\fakerepo\\.aidrafts\\st-c"]


def test_over_budget_alerts_dual_sink(env):
    """enabled=true + 收紧预算：超限 → workspace_alerts 件 + nine_face_alerts.jsonl 审计行双落点。"""
    e = env
    e["set_flags"](e["root"], enabled=True, dead_bags=1, queue_backlog=1)
    alert_dir = e["rt"] / "workspace_alerts"
    audit_dir = e["rt"] / "audit"
    r = e["mod"].patrol_once(
        repo_root=e["root"],
        alert_dir=alert_dir,
        audit_dir=audit_dir,
        once=True,
    )
    assert r["action"] == "patrolled" and r["budget_state"] == "breach", r
    breach_faces = {b["face"] for b in r["breaches"]}
    assert breach_faces == {"dead_bags", "queue_backlog"}, r["breaches"]
    assert r["alert"] and r["alert"]["alert_file"], "告警件未落"
    body = json.loads(Path(r["alert"]["alert_file"]).read_text(encoding="utf-8"))
    assert body["event"] == "nine_face_budget_breach" and body["severity"] == "escalated"
    assert "零自动处置" in body["note"], "告警必须声明零处置"
    assert {b["face"] for b in body["breaches"]} == breach_faces
    lines = (audit_dir / e["mod"].ALERT_AUDIT_FILENAME).read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["event"] == "nine_face_budget_breach"
    # 基线同步刷新
    baseline = json.loads((audit_dir / e["mod"].BASELINE_FILENAME).read_text(encoding="utf-8"))
    assert baseline["budget_state"] == "breach" and baseline["faces"]["dead_bags"] == 3


def test_under_budget_no_alert(env):
    """enabled=true + 放宽预算：零超限零告警。"""
    e = env
    e["set_flags"](e["root"], enabled=True, dead_bags=10**9, queue_backlog=10**9)
    alert_dir = e["rt"] / "workspace_alerts"
    r = e["mod"].patrol_once(
        repo_root=e["root"],
        alert_dir=alert_dir,
        audit_dir=e["rt"] / "audit",
        once=True,
    )
    assert r["budget_state"] == "ok" and r["breaches"] == [] and r["alert"] is None
    assert not (alert_dir / "nine_face_alerts.jsonl").exists() if alert_dir.exists() else True


def test_disabled_off_degradation(env):
    """enabled=false（出厂 OFF）：超限也只记基线不告警（budget_state=disabled）。"""
    e = env
    e["set_flags"](e["root"], enabled=False, dead_bags=1)  # 必超限但 OFF
    alert_dir = e["rt"] / "workspace_alerts"
    r = e["mod"].patrol_once(
        repo_root=e["root"],
        alert_dir=alert_dir,
        audit_dir=e["rt"] / "audit",
        once=True,
    )
    assert r["budget_state"] == "disabled" and r["breaches"] == [] and r["alert"] is None
    assert not r["enabled"]
    # 基线仍写（采样与告警两段解耦）
    baseline = json.loads((e["rt"] / "audit" / e["mod"].BASELINE_FILENAME).read_text(encoding="utf-8"))
    assert baseline["budget_enabled"] is False and baseline["faces"]["dead_bags"] == 3


def test_throttle_then_once(env):
    """60min 巡检节流（读基线 ts 判距）+ once 跳过；告警冷却：二次超限不刷屏。"""
    e = env
    e["set_flags"](e["root"], enabled=True, dead_bags=1)
    kw = dict(repo_root=e["root"], alert_dir=e["rt"] / "workspace_alerts", audit_dir=e["rt"] / "audit")
    r1 = e["mod"].patrol_once(**kw, once=True)
    assert r1["action"] == "patrolled" and r1["alert"], r1
    r2 = e["mod"].patrol_once(**kw, min_interval_min=60)
    assert r2["action"] == "throttled", "fresh 基线应被节流"
    r3 = e["mod"].patrol_once(**kw, min_interval_min=60, once=True)
    assert r3["action"] == "patrolled"
    # 告警冷却（默认 60min）：巡检放行但告警不重发
    assert r3["budget_state"] == "breach" and r3["alert"] is None, r3


def test_dry_run_no_side_effect(env):
    """dry-run：返回九面读数但零写盘（无基线/无告警件）。"""
    e = env
    e["set_flags"](e["root"], enabled=True, dead_bags=1)
    r = e["mod"].patrol_once(
        repo_root=e["root"],
        alert_dir=e["rt"] / "workspace_alerts",
        audit_dir=e["rt"] / "audit",
        once=True,
        dry_run=True,
    )
    assert r.get("dry_run") is True and r["row"] is not None
    assert r["budget_state"] == "breach", "dry-run 仍判读超限（只算不写）"
    assert not (e["rt"] / "audit" / e["mod"].BASELINE_FILENAME).exists(), "dry-run 不得写基线"
    alerts = e["rt"] / "workspace_alerts"
    assert not alerts.exists() or not any(alerts.iterdir()), "dry-run 不得写告警"


def test_budget_config_fallback_factory(env, tmp_path):
    """缺键回出厂预算；缺 flags.yaml 回 (False, 出厂预算)。"""
    e = env
    e["set_flags"](e["root"], enabled=True, dead_bags=5)  # 只覆写一键
    enabled, budgets = e["mod"].read_nine_face_budget_config(e["root"])
    assert enabled is True
    assert budgets["dead_bags"] == 5.0, "覆写键生效"
    assert budgets["tmp_gib"] == 5.0 and budgets["queue_backlog"] == 150, "缺席键回出厂"
    enabled2, budgets2 = e["mod"].read_nine_face_budget_config(tmp_path / "no-flags")
    assert enabled2 is False and budgets2["lanes"] == 60, "缺配置回出厂 OFF"


def test_git_faces_none_on_error(env, tmp_path, monkeypatch):
    """非 git 目录：车道/staged 面=None+errors 行内记录，巡检不抛不误超限。"""
    e = env
    bare = tmp_path / "not_a_repo"
    bare.mkdir()
    # tmp 目录物理位于仓内——GIT_DIR 指向不存在路径强制 git 失能（否则向上发现主仓误读真车道）
    monkeypatch.setenv("GIT_DIR", str(bare / ".git"))
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(bare))
    e["set_flags"](bare, enabled=True, lanes=0, staged=0)
    faces, errors = e["mod"].measure_faces(bare, worktree_porcelain="", status_porcelain="")
    assert faces["lanes"] == 0 and faces["staged"] == 0  # 注入口路径（纯文本解析）
    faces2, errors2 = e["mod"].measure_faces(bare)  # 真跑 git（非仓目录）
    assert faces2["lanes"] is None and faces2["staged"] is None
    assert any("git_worktree_list_failed" in x for x in errors2)
    assert any("git_status_failed" in x for x in errors2)
    r = e["mod"].patrol_once(
        repo_root=bare,
        alert_dir=bare / ".runtime" / "workspace_alerts",
        audit_dir=bare / ".runtime" / "audit",
        once=True,
    )
    assert r["action"] == "patrolled", "git 失能不反噬整轮巡检"
    baseline = json.loads((bare / ".runtime" / "audit" / e["mod"].BASELINE_FILENAME).read_text(encoding="utf-8"))
    assert baseline["faces"]["lanes"] is None and baseline["errors"], baseline


def test_git_status_real_repo(env, tmp_path):
    """真 git 仓 staged+untracked 实测（add 1 件+untracked 1 件=2）。"""
    e = env
    repo = tmp_path / "realrepo"
    repo.mkdir()

    def _git(*args: str) -> None:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

        run_subprocess_hidden(["git", *args], cwd=repo, check=True, capture_output=True)

    _git("init", "-q")
    (repo / "a.txt").write_text("a", encoding="utf-8")
    _git("add", "a.txt")
    (repo / "b.txt").write_text("b", encoding="utf-8")
    faces, errors = e["mod"].measure_faces(repo)
    assert errors == [], errors
    assert faces["staged"] == 2, faces
    assert faces["lanes"] == 0, faces  # 仅主区，零车道
