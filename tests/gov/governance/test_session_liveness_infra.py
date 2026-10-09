# [MODULE] tests.gov.governance.test_session_liveness_infra
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.rule_bridge.git_commit_gateway; heartbeat_daemon; session_concurrency
# [CONSUMERS] 2026-10-10 总统筹增补令质量守卫：①A13 破断器（根锚统一+hot_files 填充+他伤豁免窗）
#             ③ghost_session 治本（exited 残留无条件重 spawn+缺根响亮失败+开班单一 API）
# [INVARIANTS] 全部用例 tmp 根/桩注入（零主区零真进程）；红证判据=增补令原文逐条
# [MODIFY-GUARD] 新建 2026-10-10 st-regsolo-20261010（增补令随批测试，tests/ 豁免 token）
# [TTL] permanent
"""会话活性基础设施守卫（总统筹 2026-10-10 增补令①③）。

①A13 破断器：allow_overlap 台账读写统一锚主仓根（池工 worktree 调用不再写/读影子
台账）；hot_files 按主仓根判定填充（此前恒 []→TRAE-079 他伤豁免永不命中）；
_ judge_eviction_excuse 事件窗命中判据红蓝双向。
③ghost_session：心跳审计末条 status=exited=死亡证明 → spawn 无条件重拉（pid 文件
再活也不算"已在运行"）；缺仓库根启动响亮失败（返回 1 零心跳记录，禁影子路径假
成功）；开班单一 API（register(pid=0, logical=True) 一口，禁裸两步）。
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from zephyr.gov_enforcement.rule_bridge import session_worktree as sw  # noqa: E402
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: E402
    _check_hot_overlap_escalation,
    _judge_eviction_excuse,
    _log_allow_overlap_usage,
)
from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import heartbeat_last_status, run_daemon  # noqa: E402
from zephyr.security.access_control.session_concurrency import SessionRegistry  # noqa: E402

_CAP = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"


# ── 增补令①：A13 破断器 ────────────────────────────────────────────────


def _patch_anchor(monkeypatch, main_root: Path) -> None:
    import zephyr.shared.io.paths as paths_mod

    monkeypatch.setattr(paths_mod, "anchor_main_root", lambda p: main_root)


def test_usage_ledger_anchors_main_root_and_fills_hot_files(tmp_path, monkeypatch):
    """红证①两连：池工 worktree 调用 → 台账落主区（非影子）；hot_files 实判填充（非恒 []）。"""
    main_root = tmp_path / "main"
    main_root.mkdir()
    wt = tmp_path / "wt"
    wt.mkdir()
    _patch_anchor(monkeypatch, main_root)
    import zephyr.shared.io.file_utils as fu

    monkeypatch.setattr(fu, "is_hot_file", lambda p, r: "catalogs" in str(p))

    _log_allow_overlap_usage(wt, "st-victim", [_CAP, "docs/plain.md"])

    main_ledger = main_root / ".runtime" / "gate_audit" / "allow_overlap_usage.jsonl"
    shadow = wt / ".runtime" / "gate_audit" / "allow_overlap_usage.jsonl"
    assert main_ledger.is_file() and not shadow.exists(), "台账必须落主区（影子路径=根错位病根）"
    rec = json.loads(main_ledger.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert rec["hot_files"] == [_CAP], "hot_files 必须按主仓根实判填充（恒 [] =豁免腿失效根因）"
    assert rec["files"] == 2


def test_escalation_reads_main_root_ledger(tmp_path, monkeypatch):
    """红证①三连：worktree 根调用升级判定 → 读的是主区台账（清主区有效、影子无效）。"""
    main_root = tmp_path / "main"
    wt = tmp_path / "wt"
    wt.mkdir(parents=True)
    main_root.mkdir()
    _patch_anchor(monkeypatch, main_root)
    ledger = main_root / ".runtime" / "gate_audit" / "allow_overlap_usage.jsonl"
    ledger.parent.mkdir(parents=True)
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        json.dumps({"ts": now, "session": "st-s1", "hot_files": [_CAP], "eviction_excused": False}) for _ in range(5)
    ]
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

    blocked, reason = _check_hot_overlap_escalation(wt, "st-s1")
    assert blocked is True, "主区台账 5 次热册 overlap 必须经 worktree 根调用也被看到（根锚统一）"
    assert "st-s1" in reason


def test_eviction_excuse_window_hit_and_miss():
    """他伤豁免判据红蓝：窗内+命中热册=豁免；窗外/未命中=照常计数。"""
    ts_in = datetime.fromisoformat("2026-10-09T06:00:00+08:00")
    ts_out = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)
    assert _judge_eviction_excuse(ts_in, [_CAP]) is True, "带外来吸收上下文的记录豁免必命中（增补令红证）"
    assert _judge_eviction_excuse(ts_in, ["docs/other.md"]) is False
    assert _judge_eviction_excuse(ts_out, [_CAP]) is False
    assert _judge_eviction_excuse("not-a-datetime", [_CAP]) is False


# ── 增补令③：ghost_session 治本 ───────────────────────────────────────


def _write_heartbeat(tmp_path: Path, sid: str, records: list[dict]) -> Path:
    hb_dir = tmp_path / ".runtime" / "sessions" / sid
    hb_dir.mkdir(parents=True, exist_ok=True)
    hb = hb_dir / "heartbeat.jsonl"
    hb.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return hb


def test_spawn_respawns_on_exited_residue(tmp_path, monkeypatch):
    """红证③①：exited 残留 + pid 文件指向活进程 → 必须 respawn（新鲜判据不得把它当活证）。"""
    sid = "st-ghost-exited"
    _write_heartbeat(
        tmp_path,
        sid,
        [
            {"ts": "2026-10-10T00:00:00+00:00", "pid": 1, "status": "alive"},
            {"ts": "2026-10-10T00:01:00+00:00", "pid": 1, "status": "exited"},
        ],
    )
    pid_file = tmp_path / ".runtime" / "locks" / f"heartbeat_{sid}.pid"
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()), encoding="utf-8")  # 活 pid——无守卫时幂等判据会跳过重拉

    spawned: list[list] = []

    class _Proc:
        pid = 99999

    def fake_spawn(cmd, cwd=None, env=None):
        spawned.append(cmd)
        return _Proc()

    monkeypatch.setattr(sw, "spawn_python_hidden", fake_spawn)
    rc = sw._spawn_heartbeat_daemon(sid, tmp_path, worktree_path=tmp_path)
    assert rc == 99999 and spawned, "exited 残留必须无条件重 spawn（keeper 处方①）"
    assert pid_file.read_text(encoding="utf-8").strip() == "99999"


def test_spawn_idempotent_when_last_status_alive(tmp_path, monkeypatch):
    """蓝证：末条 alive + pid 文件活进程 → 幂等不重拉（守卫不得误杀既有守护）。"""
    sid = "st-ghost-alive"
    _write_heartbeat(tmp_path, sid, [{"ts": "2026-10-10T00:00:00+00:00", "pid": 1, "status": "alive"}])
    pid_file = tmp_path / ".runtime" / "locks" / f"heartbeat_{sid}.pid"
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()), encoding="utf-8")

    def fail_spawn(cmd, cwd=None, env=None):
        raise AssertionError("alive 幂等态不得重 spawn")

    monkeypatch.setattr(sw, "spawn_python_hidden", fail_spawn)
    rc = sw._spawn_heartbeat_daemon(sid, tmp_path, worktree_path=tmp_path)
    assert rc == os.getpid()


def test_run_daemon_missing_root_fails_loudly(tmp_path):
    """红证③②：缺仓库根启动=响亮失败（返回 1 且零心跳记录），禁影子路径假成功。"""
    ghost_root = tmp_path / "no_such_root"
    rc = run_daemon("st-ghost-missing", ghost_root, max_iterations=1)
    assert rc == 1, "缺根启动必须失败（shadow-path 假成功=deadcure2 守护 bug 活案例）"
    assert not (tmp_path / ".runtime").exists(), "失败路径上一条心跳都不许落"


def test_open_session_single_api(tmp_path):
    """红证③②：开班单一 API=pid0+logical 一口完成（禁裸两步）。"""
    reg = SessionRegistry(tmp_path)
    reg.open_session("st-chief-test")
    info = reg.get_session("st-chief-test")
    assert info is not None
    entry = info.to_dict() if hasattr(info, "to_dict") else vars(info)
    assert int(entry.get("pid") or 0) == 0
    assert entry.get("logical") is True, "开班必须自带 logical=True（裸两步窗口=判死竞态根因）"


def test_heartbeat_last_status_reader(tmp_path):
    sid = "st-reader"
    _write_heartbeat(tmp_path, sid, [{"ts": "t", "pid": 1, "status": "alive"}])
    assert heartbeat_last_status(tmp_path, sid) == "alive"
    _write_heartbeat(tmp_path, sid, [{"ts": "t", "pid": 1, "status": "exited"}])
    assert heartbeat_last_status(tmp_path, sid) == "exited"
    assert heartbeat_last_status(tmp_path, "st-never-existed") is None
