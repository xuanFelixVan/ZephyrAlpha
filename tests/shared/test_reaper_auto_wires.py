# [MODULE] tests.shared.test_reaper_auto_wires
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.maintenance.reaper_auto_wires (被测), scripts.session_worktree (monkeypatch 判活/注册表), pytest
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] volatile
# [INVARIANTS] 全部在 tmp 仓根（测试禁写生产 .runtime/）；子进程一律 mock runner（零真调 CLI）；
#              判活/mtime 双确认两侧；判型三向分诊；dry-run 零副作用；永不抛
# [STABILITY] volatile
# [SAFETY] L
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_reaper_auto_wires.py — reaper 三条自动维护线单测（st-diskp0 接线队 A，root-cure-plan §7）。

测试组:
- test_read_flag_three_states: enabled 三态（true/false/键缺省=出厂 ON/文件不可读=None）
- test_dead_archive_wire_cmd_face_frozen: 命令面（--days 7 --content-level --json；dry-run 无 --execute）
- test_dead_archive_wire_ok_and_audit: archived/bag 解析+真跑轮审计行+dry-run 零审计
- test_dead_archive_wire_error_fail_visible: rc≠0/不可解析→status=error 且审计行照写
- test_dead_archive_wire_disabled_skips: flag off/不可读→零子进程零审计
- test_git_gc_cmd_frozen_and_guard: 命令面=git gc --auto（--prune=now 守卫拒绝）；dry-run 跳过；超时不抛
- test_dead_lane_zero_loss_auto: 判死候选 dry-run 判型 zero_loss→追加 --execute 自动收+审计行
- test_dead_lane_needs_rescue_alert_only: needs_rescue 只写告警件不自动动
- test_dead_lane_liveness_and_age_filters: 判活同源 + mtime>48h 保守双确认两侧
- test_dead_lane_excluded_and_unregistered: 排除表同源 + 注册表未命中跳过
- test_dead_lane_dry_run_zero_side_effect: 零审计零告警件零 --execute
- test_wires_never_raise: runner 抛任意异常→status=error 不上抛
- test_load_session_worktree_by_path: 计划任务环境（sys.path 无仓根）按路径加载同源真源
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import scripts.session_worktree as sw
from zephyr.shared.maintenance import reaper_auto_wires as raw

_H = 3600.0
_FLAGS_ON = """
flags:
  dead_archive_auto:
    enabled: true
  git_gc_auto:
    enabled: true
  dead_lane_autoreap:
    enabled: true
"""


def _mk_repo(tmp_path: Path, flags_yaml: str = _FLAGS_ON) -> Path:
    (tmp_path / "config").mkdir(parents=True)
    (tmp_path / "config" / "flags.yaml").write_text(flags_yaml, encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "commit_queue.py").write_text("# fake\n", encoding="utf-8")
    (tmp_path / "scripts" / "session_worktree.py").write_text("# fake\n", encoding="utf-8")
    return tmp_path


def _mk_lane(root: Path, lane_root: str, sid: str, *, age_h: float) -> Path:
    lane = root / lane_root / sid
    lane.mkdir(parents=True)
    (lane / "wip.txt").write_text("x", encoding="utf-8")
    old = raw.now_utc().timestamp() - age_h * _H
    os.utime(lane, (old, old))
    return lane


def _runner(responses: list[SimpleNamespace] | None = None, *, fail: Exception | None = None) -> Any:
    """mock runner：按序回放响应并记录 cmd 快照（供命令面断言）。"""
    calls: list[list[str]] = []

    def _run(cmd, **kwargs):
        calls.append(list(cmd))
        if fail is not None:
            raise fail
        return responses[len(calls) - 1] if responses else SimpleNamespace(returncode=0, stdout="", stderr="")

    _run.calls = calls  # type: ignore[attr-defined]
    return _run


def _audit_rows(root: Path, name: str) -> list[dict]:
    p = root / ".runtime" / "audit" / name
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _patch_sw(monkeypatch, *, registry: list[dict], dead_fn=None) -> None:
    """替换 _load_session_worktree 为假模块（判活/注册表可注；normcase/排除表用真源常量）。"""
    fake = SimpleNamespace(
        _list_worktree_registry=lambda: registry,
        _normcase=sw._normcase,
        _ARCHIVE_ALL_EXCLUDED_MARKERS=sw._ARCHIVE_ALL_EXCLUDED_MARKERS,
        _check_archive_target_dead=dead_fn or (lambda sid: (True, "死车道")),
    )
    monkeypatch.setattr(raw, "_load_session_worktree", lambda root_str: fake)


# ============ flag 三态 ============


def test_read_flag_three_states(tmp_path: Path):
    (tmp_path / "config").mkdir()
    f = tmp_path / "config" / "flags.yaml"
    f.write_text("flags:\n  k:\n    enabled: false\n", encoding="utf-8")
    assert raw._read_flag(tmp_path, "k") is False, "显式 false"
    f.write_text("flags:\n  other:\n    enabled: false\n", encoding="utf-8")
    assert raw._read_flag(tmp_path, "k") is True, "键缺省=出厂 ON"
    f.write_text("\t-bad: [broken\n", encoding="utf-8")
    assert raw._read_flag(tmp_path, "k") is None, "不可读=None（跳过不动作）"
    assert raw._read_flag(tmp_path / "nonexistent", "k") is None


# ============ wire④ 死信自动归档（裁定②） ============


def test_dead_archive_wire_cmd_face_frozen(tmp_path: Path):
    """命令面断言：--days 7 --content-level --json 在；dry-run 无 --execute、真跑有。"""
    root = _mk_repo(tmp_path)
    ok = SimpleNamespace(returncode=0, stdout="{}", stderr="")
    runner = _runner([ok, ok])
    raw.run_dead_archive_wire(root, dry_run=True, runner=runner)
    dry_cmd = runner.calls[-1]
    assert dry_cmd[dry_cmd.index("--days") + 1] == "7", "age>7 天=裁定②语义，禁改"
    assert "--content-level" in dry_cmd and dry_cmd[-1] == "--json"
    assert "--execute" not in dry_cmd, "dry-run 轮禁 --execute"
    raw.run_dead_archive_wire(root, dry_run=False, runner=runner)
    exec_cmd = runner.calls[-1]
    assert "--execute" in exec_cmd, "真跑轮必须带 --execute（裁定②自动归档语义）"
    assert runner.calls[-1][1].endswith("commit_queue.py")


def test_dead_archive_wire_ok_and_audit(tmp_path: Path):
    root = _mk_repo(tmp_path)
    payload = {"archived": ["q-1", "q-2"], "kept": {"young": 3}, "bag": "dead_archive_20261016"}
    ok = SimpleNamespace(returncode=0, stdout="DEAD-ARCHIVE: archived=2 kept=3\n" + json.dumps(payload), stderr="")
    r = raw.run_dead_archive_wire(root, dry_run=True, runner=_runner([ok]))
    assert r["status"] == "ok" and r["archived"] == ["q-1", "q-2"] and r["bag"] == "dead_archive_20261016"
    assert r.get("audit_written") is None and _audit_rows(root, "dead_archive_wire.jsonl") == [], "dry-run 零审计"
    r2 = raw.run_dead_archive_wire(root, dry_run=False, runner=_runner([ok]))
    assert r2["status"] == "ok" and r2["audit_written"] is True
    rows = _audit_rows(root, "dead_archive_wire.jsonl")
    assert len(rows) == 1 and rows[0]["archived"] == ["q-1", "q-2"] and rows[0]["days"] == 7.0


def test_dead_archive_wire_error_fail_visible(tmp_path: Path):
    root = _mk_repo(tmp_path)
    bad = SimpleNamespace(returncode=1, stdout="", stderr="ERROR: serializer 租约存活拒绝")
    r = raw.run_dead_archive_wire(root, dry_run=False, runner=_runner([bad]))
    assert r["status"] == "error" and "租约" in r["stderr_tail"]
    r2 = raw.run_dead_archive_wire(
        root, dry_run=False, runner=_runner([SimpleNamespace(returncode=0, stdout="garbage", stderr="")])
    )
    assert r2["status"] == "error" and r2["error"] == "unparsable_output"
    rows = _audit_rows(root, "dead_archive_wire.jsonl")
    assert len(rows) == 2, "失败轮审计行照写（fail-visible）"


def test_dead_archive_wire_disabled_skips(tmp_path: Path):
    root = _mk_repo(tmp_path, flags_yaml="flags:\n  dead_archive_auto:\n    enabled: false\n")
    runner = _runner()
    r = raw.run_dead_archive_wire(root, runner=runner)
    assert r["status"] == "skipped_disabled" and runner.calls == [] and r.get("audit_written") is None
    root2 = _mk_repo(tmp_path / "n2", flags_yaml="\t-bad: [")
    r2 = raw.run_dead_archive_wire(root2, runner=_runner())
    assert r2["status"] == "skipped_flag_unreadable"


# ============ wire⑤ git gc --auto（裁定①例行半） ============


def test_git_gc_cmd_frozen_and_guard(tmp_path: Path, monkeypatch):
    assert raw.GIT_GC_CMD == ("git", "gc", "--auto"), "命令面冻结；--prune=now 深清=Owner 永不入 cmd"
    root = _mk_repo(tmp_path)
    runner = _runner()
    r = raw.run_git_gc_auto_wire(root, dry_run=True, runner=runner)
    assert r["status"] == "skipped_dry_run" and runner.calls == [], "dry-run 轮直接跳过（gc 无只读形态）"
    ok = SimpleNamespace(returncode=0, stdout="", stderr="")
    runner2 = _runner([ok])
    r2 = raw.run_git_gc_auto_wire(root, dry_run=False, runner=runner2)
    assert r2["status"] == "ok" and r2["rc"] == 0 and r2["audit_written"] is True
    assert runner2.calls[-1][:3] == ["git", "gc", "--auto"]
    assert _audit_rows(root, "git_gc_wire.jsonl"), "真跑轮审计行"
    # 命令面双保险：有人改常量塞 --prune=now → 拒绝执行（深清=Owner 门位）
    monkeypatch.setattr(raw, "GIT_GC_CMD", ("git", "gc", "--auto", "--prune=now"))
    r3 = raw.run_git_gc_auto_wire(root, dry_run=False, runner=_runner([ok]))
    assert r3["status"] == "error" and r3["error"] == "cmd_guard_prune_forbidden"
    assert len(_audit_rows(root, "git_gc_wire.jsonl")) == 1, "prune 守卫拒绝轮未执行不追加审计"


def test_git_gc_wire_timeout_never_raises(tmp_path: Path):
    root = _mk_repo(tmp_path)
    runner = _runner(fail=subprocess.TimeoutExpired(cmd="git", timeout=600))
    r = raw.run_git_gc_auto_wire(root, dry_run=False, runner=runner)
    assert r["status"] == "error" and "timeout" in r["error"]
    assert _audit_rows(root, "git_gc_wire.jsonl"), "超时轮审计行照写"


# ============ wire⑥ 死车道自动收（L3 补件） ============


def test_dead_lane_zero_loss_auto(tmp_path: Path, monkeypatch):
    root = _mk_repo(tmp_path)
    lane = _mk_lane(root, ".aidrafts", "st-dead-1016", age_h=72.0)
    _patch_sw(
        monkeypatch,
        registry=[{"path": str(lane), "bare": False}],
        dead_fn=lambda sid: (True, "死车道（registry 无活跃记录 + 无新鲜锁/免疫标记）"),
    )
    plan = SimpleNamespace(returncode=0, stdout="[ARCHIVE] DRY-RUN 计划\n  判型: zero_loss\n", stderr="")
    done = SimpleNamespace(returncode=0, stdout="[ARCHIVE] 已归档: st-dead-1016\n", stderr="")
    runner = _runner([plan, done])
    r = raw.run_dead_lane_wire(root, dry_run=False, runner=runner, now_ts=raw.now_utc().timestamp())
    assert r["dead_candidates"] == 1 and r["auto_archived"] == ["st-dead-1016"], r
    assert len(runner.calls) == 2 and "--execute" in runner.calls[1], "zero_loss 判型才追加 --execute"
    rows = _audit_rows(root, "dead_lane_wire.jsonl")
    assert rows and rows[0]["auto_archived"] == ["st-dead-1016"]


def test_dead_lane_needs_rescue_alert_only(tmp_path: Path, monkeypatch):
    root = _mk_repo(tmp_path)
    lane = _mk_lane(root, ".worktrees", "st-dirty-1016", age_h=72.0)
    _patch_sw(
        monkeypatch,
        registry=[{"path": str(lane), "bare": False}],
        dead_fn=lambda sid: (True, "死车道（registry 无活跃记录 + 无新鲜锁/免疫标记）"),
    )
    plan = SimpleNamespace(returncode=0, stdout="  判型: needs_rescue\n", stderr="")
    runner = _runner([plan])
    r = raw.run_dead_lane_wire(root, dry_run=False, runner=runner, now_ts=raw.now_utc().timestamp())
    assert r["needs_rescue"] == [{"sid": "st-dirty-1016", "verdict": "needs_rescue"}]
    assert len(runner.calls) == 1, "needs_rescue 只 dry-run 判型，绝不自动 --execute"
    alert = root / ".runtime" / "workspace_alerts" / "dead_lane_needs_rescue_st-dirty-1016.json"
    assert alert.exists(), "执行轮写告警件留夜巡/人工"
    assert json.loads(alert.read_text(encoding="utf-8"))["verdict"] == "needs_rescue"


def test_dead_lane_liveness_and_age_filters(tmp_path: Path, monkeypatch):
    root = _mk_repo(tmp_path)
    alive = _mk_lane(root, ".aidrafts", "st-alive", age_h=72.0)
    young = _mk_lane(root, ".aidrafts", "st-young", age_h=1.0)
    old = _mk_lane(root, ".aidrafts", "st-old", age_h=72.0)
    reg = [
        {"path": str(alive), "bare": False},
        {"path": str(young), "bare": False},
        {"path": str(old), "bare": False},
    ]
    _patch_sw(monkeypatch, registry=reg, dead_fn=lambda sid: (sid != "st-alive", "仍活跃"))
    plan = SimpleNamespace(returncode=0, stdout="  判型: zero_loss\n", stderr="")
    runner = _runner([plan])
    r = raw.run_dead_lane_wire(root, dry_run=True, runner=runner, now_ts=raw.now_utc().timestamp())
    assert r["skipped_alive"] == 1, "判活同源：活跃注册表命中→活"
    assert r["skipped_young"] == 1, "mtime>48h 保守双确认：新鲜车道留"
    assert r["dead_candidates"] == 1
    assert r.get("planned") == [{"sid": "st-old", "verdict": "zero_loss"}]


def test_dead_lane_excluded_and_unregistered(tmp_path: Path, monkeypatch):
    root = _mk_repo(tmp_path)
    _mk_lane(root, ".aidrafts", ".aidrafts_pool", age_h=72.0)
    _mk_lane(root, ".aidrafts", "st-ghost-shell", age_h=72.0)
    _patch_sw(monkeypatch, registry=[{"path": str(root / ".worktrees" / "other"), "bare": False}])
    runner = _runner()
    r = raw.run_dead_lane_wire(root, dry_run=True, runner=runner, now_ts=raw.now_utc().timestamp())
    assert r["skipped_excluded"] == 1, "排除表同源（.aidrafts_pool 不进收割面）"
    assert r["skipped_not_registered"] == 1, "git worktree 注册表未命中=壳目录，不进本线"
    assert runner.calls == []


def test_dead_lane_dry_run_zero_side_effect(tmp_path: Path, monkeypatch):
    root = _mk_repo(tmp_path)
    lane1 = _mk_lane(root, ".aidrafts", "st-dry", age_h=72.0)
    lane2 = _mk_lane(root, ".aidrafts", "st-dry2", age_h=72.0)
    _patch_sw(
        monkeypatch,
        registry=[{"path": str(lane1), "bare": False}, {"path": str(lane2), "bare": False}],
        dead_fn=lambda sid: (True, "死车道"),
    )
    plan = SimpleNamespace(returncode=0, stdout="  判型: zero_loss\n", stderr="")
    rescue = SimpleNamespace(returncode=0, stdout="  判型: needs_rescue\n", stderr="")
    runner = _runner([plan, rescue])
    r = raw.run_dead_lane_wire(root, dry_run=True, runner=runner, now_ts=raw.now_utc().timestamp())
    assert all("--execute" not in c for c in runner.calls), "dry-run 轮零 --execute"
    assert "audit_written" not in r and _audit_rows(root, "dead_lane_wire.jsonl") == []
    assert not (root / ".runtime" / "workspace_alerts").exists() or not list(
        (root / ".runtime" / "workspace_alerts").iterdir()
    ), "dry-run 轮零告警件"


def test_wires_never_raise(tmp_path: Path, monkeypatch):
    root = _mk_repo(tmp_path)
    boom = _runner(fail=RuntimeError("boom"))
    assert raw.run_dead_archive_wire(root, dry_run=False, runner=boom)["status"] == "error"
    assert raw.run_git_gc_auto_wire(root, dry_run=False, runner=boom)["status"] == "error"
    lane = _mk_lane(root, ".aidrafts", "st-x", age_h=72.0)
    _patch_sw(monkeypatch, registry=[{"path": str(lane), "bare": False}], dead_fn=lambda sid: (True, "死"))
    r = raw.run_dead_lane_wire(root, dry_run=False, runner=boom, now_ts=raw.now_utc().timestamp())
    assert r["status"] == "completed_with_errors" and r["errors"]


def test_load_session_worktree_by_path():
    """按路径加载（计划任务环境 sys.path 无仓根也能拿同源真源）+缓存命中同对象。"""
    m1 = raw._load_session_worktree("D:/ZephyrAlpha")
    m2 = raw._load_session_worktree("D:/ZephyrAlpha")
    assert m1 is m2, "lru_cache 同 root 命中"
    assert hasattr(m1, "_check_archive_target_dead") and hasattr(m1, "_ARCHIVE_ALL_EXCLUDED_MARKERS")
    assert m1._ARCHIVE_ACTIVE_LOCK_TTL == 3600 and m1._ARCHIVE_COMMIT_PERSISTED_TTL == 86400
