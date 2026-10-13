# [MODULE] tests.governance.test_session_takeover_ledger
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest；scripts.governance.session_takeover_ledger；zephyr.gov_enforcement.commit_gates.takeover_pending_gate；zephyr.security.access_control.session_concurrency（钩子集成面）
# [CONSUMERS] pytest（tests/governance/）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] tmp_path 假 root 全隔离（零真库/零真 registry/零真 worktree）；worktree dirty 与 PID 存活经 monkeypatch 确定性化；四态覆盖=scan 幂等/条目字段/resolve 迁移/gate 命中与放行；钩子集成用真 SessionRegistry.list_active 判死路径；命中面剔除两支（统筹 2026-10-13 批①）用 tmp_path 内**真 git 仓＋落后 dev 的 worktree**（隔离性不变，只把 status 假阳性这一形复刻进来）——dev-同字节件须移出并记 excluded_dev_identical，参照系不可用须整批保留
# [MODIFY-GUARD] 判据变更与 scripts/governance/session_takeover_ledger.py + takeover_pending_gate.py 同批
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；不写生产路径（宪法 §9.6）
# [TESTS] self
# [A_module] module_id=TEST-MOD-GATE_ENGINE-TEST_SESSION_TAKEOVER_LEDGER | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# -*- coding: utf-8 -*-
"""test_session_takeover_ledger.py — 接管台账四态测试（scan 幂等/条目字段/resolve 迁移/gate 命中与放行）"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.governance import session_takeover_ledger as ledger
from zephyr.gov_enforcement.commit_gates.takeover_pending_gate import make_takeover_pending_gate

NOW = 1_800_000_000.0
DEAD_SID = "st-dead-unit-1"
ALIVE_SID = "st-alive-unit-2"
LOGICAL_SID = "st-logical-chief-3"


def _write_legacy_registry(root: Path, entries: dict) -> None:
    rt = root / ".runtime"
    rt.mkdir(parents=True, exist_ok=True)
    (rt / "session_registry.json").write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")


def _dead_entry(root: Path, *, held: list[str] | None = None) -> dict:
    return {
        "session_id": DEAD_SID,
        "pid": 0,
        "start_time": NOW - 90000,
        "held_files": held if held is not None else [str(root / "src/zephyr/data/foo.py")],
        "last_heartbeat": NOW - 80000,
        "last_activity": NOW - 80000,  # > 7200s 判死线
        "is_breaking_change": False,
        "task_files": [],
        "depends_on_sessions": [],
        "logical": False,
        "last_register_ts": NOW - 90000,
    }


@pytest.fixture()
def fake_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """假 root：死/活/logical 三会话 + staging/袋/心跳残留；git 与 PID 判定确定性化。"""
    root = tmp_path
    _write_legacy_registry(
        root,
        {
            DEAD_SID: _dead_entry(root),
            ALIVE_SID: {
                "session_id": ALIVE_SID,
                "pid": 0,
                "last_heartbeat": NOW - 5,
                "last_activity": NOW - 5,
                "logical": False,
                "held_files": [],
            },
            LOGICAL_SID: {
                "session_id": LOGICAL_SID,
                "pid": 0,
                "last_heartbeat": NOW - 900000,
                "last_activity": NOW - 900000,
                "logical": True,  # 老但 logical——不判死
                "held_files": [],
            },
        },
    )
    # staging 残留 2 件
    staging = root / ".runtime" / "sessions" / DEAD_SID / "staging"
    staging.mkdir(parents=True)
    (staging / "a.yaml").write_text("a: 1", encoding="utf-8")
    (staging / "b.md").write_text("b", encoding="utf-8")
    # 死袋 1 只（session_id 匹配），3 文件三种命运——D-2 裁定 narrow-gate 判据：
    #   residue.py  ——HEAD 有、内容不同 → 活残留，纳入口径
    #   absorbed.py ——HEAD 有、内容仅差 CRLF → 已吸收，不纳（防过咬）
    #   gone_path.py——HEAD 无此路径（已删/已迁移） → 不纳
    dead_dir = root / ".runtime" / "commit_queue" / "dead"
    dead_dir.mkdir(parents=True)
    blobs = root / ".runtime" / "commit_queue" / "blobs"
    blobs.mkdir(parents=True)
    (blobs / "diff.blob").write_bytes(b"alpha = 1\r\n")
    (blobs / "same.blob").write_bytes(b"beta = 1\r\n")
    (dead_dir / f"q-unit-{DEAD_SID}.json").write_text(
        json.dumps(
            {
                "qid": f"q-unit-{DEAD_SID}",
                "session_id": DEAD_SID,
                "files": [
                    {"path": "residue.py", "blob_ref": "blobs/diff.blob"},
                    {"path": "absorbed.py", "blob_ref": "blobs/same.blob"},
                    {"path": "gone_path.py", "blob_ref": "blobs/diff.blob"},
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        ledger,
        "_head_bytes",
        lambda r, rel: {"residue.py": b"alpha = 9\n", "absorbed.py": b"beta = 1\n"}.get(rel),
    )
    # ghost 心跳残留（pid 判死 monkeypatch 后注记为 ghost）
    sess = root / ".runtime" / "sessions" / DEAD_SID
    (sess / "heartbeat.pid").write_text("999999999\n", encoding="utf-8")
    (sess / "heartbeat.jsonl").write_text('{"ts": 1}\n', encoding="utf-8")
    # owned worktree 假目录（git 判定 monkeypatch）
    (root / ".aidrafts" / DEAD_SID).mkdir(parents=True)
    monkeypatch.setattr(
        ledger,
        "_worktree_dirty",
        lambda r, rel: {
            "path": rel,
            "exists": True,
            "dirty_count": 2,
            "dirty_files": ["src/zephyr/data/foo.py", "docs/x.md"],
        },
    )
    monkeypatch.setattr(ledger, "_pid_alive", lambda pid: False)
    monkeypatch.setattr(ledger.time, "time", lambda: NOW)
    return root


# ---------------------------------------------------------------------------
# 态1：scan 判死 + 幂等
# ---------------------------------------------------------------------------


def test_scan_detects_dead_skips_alive_and_logical(fake_root: Path) -> None:
    dead = ledger.scan_dead_sessions(fake_root, now=NOW)
    sids = [d["sid"] for d in dead]
    assert DEAD_SID in sids
    assert ALIVE_SID not in sids
    assert LOGICAL_SID not in sids  # logical 豁免判死
    ev = dead[0]["death_evidence"]
    assert ev["threshold_seconds"] == ledger.DEATH_IDLE_SECONDS == 7200
    assert ev["last_activity_age_seconds"] > 7200
    assert "logical" not in ev["reason"]


def test_orphan_scan_entry_isomorphic_and_cli_end_to_end(fake_root: Path, capsys: pytest.CaptureFixture) -> None:
    """回归（2026-10-02 红蓝审查 F2）：孤儿条目在场时 --scan/--list CLI 端到端不崩且落册。

    原缺陷：_scan_orphan_resources 曾产 session_id 键+扁平资源+字符串证据，
    _cmd_scan 读 d["sid"] 即 KeyError → 整个 scan 崩溃零落册；字符串证据再使
    _cmd_list 的 .get('reason') 崩；孤儿 worktree 缺 dirty_files → 门匹配面恒空。
    本测钉死同构四要件：sid 键 / dict 证据 / resources 包裹 / worktree dirty_files。
    """
    orphan_sid = "st-orphan-hardcrash-9"
    (fake_root / ".aidrafts" / orphan_sid).mkdir(parents=True, exist_ok=True)
    (fake_root / ".aidrafts" / orphan_sid / "wip.py").write_text("x = 1\n", encoding="utf-8")

    dead = ledger.scan_dead_sessions(fake_root, now=NOW)
    orphan = [d for d in dead if d.get("sid") == orphan_sid]
    assert len(orphan) == 1, "孤儿必须被 _scan_orphan_resources 捕获"
    o = orphan[0]
    assert isinstance(o["death_evidence"], dict), "证据必须为 dict（--list 可渲染）"
    assert set(o["resources"]) == {"held_files", "worktrees", "staging", "bags", "heartbeat_files"}
    wt0 = o["resources"]["worktrees"][0]
    assert wt0["dirty_files"], "孤儿必须带 dirty_files（接管人可读面）"
    # F5：普通目录（非 worktree）只盘自身文件，禁吸主仓脏面
    assert wt0.get("non_worktree_dir") is True
    assert all(f.startswith(f".aidrafts/{orphan_sid}/") for f in wt0["dirty_files"])

    assert ledger._cmd_scan(fake_root) == 0, "孤儿在场时 scan CLI 不得崩（原缺陷现场）"
    entries = {e["sid"]: e for e in ledger.load_open_entries(fake_root)}
    e = entries[orphan_sid]
    assert e["status"] == "open"
    assert "orphan_resources" in e["death_evidence"]["reason"]
    rx = "\n".join(e["prescription"])
    assert "worktree remove" in rx and "--resolve" in rx
    assert ledger.entry_match_surface(e) & {f".aidrafts/{orphan_sid}/wip.py"}

    assert ledger._cmd_list(fake_root) == 0, "孤儿条目在场时 list CLI 不得崩"
    assert orphan_sid in capsys.readouterr().out
    assert ledger._cmd_resolve(fake_root, orphan_sid, "taker-x", "review regression") == 0
    assert all(x["sid"] != orphan_sid for x in ledger.load_open_entries(fake_root))


def test_write_entry_idempotent_refresh(fake_root: Path) -> None:
    first = ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW)
    assert first["refresh_count"] == 0
    entry2 = _dead_entry(
        fake_root,
        held=[str(fake_root / "src/zephyr/data/foo.py"), str(fake_root / "src/zephyr/gov_enforcement/bar.py")],
    )
    # 节流窗内（<600s）重复触发（钩子热路径）：原样返回不重收集
    throttled = ledger.write_takeover_entry(fake_root, DEAD_SID, registry_entry=entry2, now=NOW + 30)
    assert throttled["refresh_count"] == 0
    assert len(throttled["resources"]["held_files"]) == 1
    # 超窗后（模拟 --scan 全量刷新）：只 refresh 不新增行，资源数已更新
    second = ledger.write_takeover_entry(fake_root, DEAD_SID, registry_entry=entry2, now=NOW + 700)
    lines = (fake_root / ".runtime" / "takeover_ledger.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1  # 幂等：同 sid 单 open 条目
    assert second["refresh_count"] == 1
    assert len(second["resources"]["held_files"]) == 2  # 资源数已刷新


# ---------------------------------------------------------------------------
# 态2：条目字段完整性与资源收集
# ---------------------------------------------------------------------------


def test_entry_fields_and_resources(fake_root: Path) -> None:
    entry = ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW)
    for key in ("ts", "sid", "death_evidence", "resources", "impacted_modules", "prescription", "status"):
        assert key in entry, f"missing field {key}"
    assert entry["status"] == "open"
    res = entry["resources"]
    assert set(res.keys()) == {"held_files", "worktrees", "staging", "bags", "heartbeat_files"}
    assert res["held_files"] == ["src/zephyr/data/foo.py"]  # 绝对路径已归一为仓根相对
    assert res["worktrees"] == [
        {
            "path": ".aidrafts/" + DEAD_SID,
            "exists": True,
            "dirty_count": 2,
            "dirty_files": ["src/zephyr/data/foo.py", "docs/x.md"],
        }
    ]
    assert res["staging"]["file_count"] == 2
    assert res["bags"] == [
        {
            "qid": f"q-unit-{DEAD_SID}",
            "state": "dead",
            "file_count": 3,
            "residue_files": ["residue.py"],
        }
    ]
    assert any("pid_dead=ghost" in h for h in res["heartbeat_files"])
    # 影响域推断：held+worktree dirty 文件按顶级目录收敛（src/zephyr/<pkg> 与 docs/<seg> 两规则）
    assert entry["impacted_modules"] == ["docs/x.md", "src/zephyr/data"]
    # 处方覆盖五类资源 + resolve 指引
    rx = "\n".join(entry["prescription"])
    assert "release_files" in rx
    assert "worktree" in rx
    assert "staging" in rx
    assert f"requeue q-unit-{DEAD_SID}" in rx
    assert "--resolve" in rx


# ---------------------------------------------------------------------------
# 态3：resolve 迁移
# ---------------------------------------------------------------------------


def test_resolve_migrates_to_resolved_dir(fake_root: Path) -> None:
    ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW)
    done = ledger.resolve_entry(fake_root, DEAD_SID, by="st-taker-unit", note="已按处方接管")
    assert done["status"] == "resolved"
    assert done["resolved_by"] == "st-taker-unit"
    assert done["resolve_note"] == "已按处方接管"
    # open 台账行已移除，resolved/ 出现终态件
    assert ledger.load_open_entries(fake_root) == []
    resolved_dir = fake_root / ".runtime" / "takeover" / "resolved"
    files = list(resolved_dir.glob("*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8"))["sid"] == DEAD_SID
    # 无 open 条目再 resolve = 显式报错
    with pytest.raises(LookupError):
        ledger.resolve_entry(fake_root, DEAD_SID, by="st-taker-unit")


# ---------------------------------------------------------------------------
# 态4：gate 命中与放行
# ---------------------------------------------------------------------------


def _gate(fake_root: Path):
    return make_takeover_pending_gate()


def test_gate_blocks_on_held_file_hit(fake_root: Path) -> None:
    ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW)
    spec = _gate(fake_root)
    gateway = SimpleNamespace(project_root=str(fake_root))
    passed, detail = spec.check(gateway, ["src/zephyr/data/foo.py"])
    assert passed is False
    assert "TAKEOVER-PENDING" in detail
    assert DEAD_SID in detail
    assert "--resolve" in detail  # 处方+解除指引在错误消息里
    assert "release_files" in detail


def test_gate_passes_on_miss_and_empty_and_tests(fake_root: Path) -> None:
    ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW)
    spec = _gate(fake_root)
    gateway = SimpleNamespace(project_root=str(fake_root))
    # 未命中条目面 → 放行
    assert spec.check(gateway, ["src/zephyr/other/needle.py"]) == (True, "")
    # 空 ledger → 放行
    empty_root = fake_root.parent / "empty_root"
    empty_root.mkdir()
    assert spec.check(SimpleNamespace(project_root=str(empty_root)), ["src/zephyr/data/foo.py"]) == (True, "")
    # 台账缺失目录 → fail-open 放行
    # tests/ 豁免：命中文件在 tests/ 下 → 放行
    assert spec.check(gateway, ["tests/governance/test_session_takeover_ledger.py"]) == (True, "")


def test_gate_fail_open_on_broken_ledger(fake_root: Path) -> None:
    lg = fake_root / ".runtime" / "takeover_ledger.jsonl"
    lg.parent.mkdir(parents=True, exist_ok=True)
    lg.write_text("{broken json!!\n", encoding="utf-8")  # 损坏行 → 空表
    spec = _gate(fake_root)
    passed, detail = spec.check(SimpleNamespace(project_root=str(fake_root)), ["src/zephyr/data/foo.py"])
    assert (passed, detail) == (True, "")


def test_gate_blocks_via_main_ledger_from_linked_worktree(tmp_path: Path) -> None:
    """回归（2026-10-02 红蓝审查 F3）：serializer worktree 根网关必须锚主仓台账咬合。

    原缺陷：落地网关 project_root=专用 worktree，台账住主仓 .runtime/（gitignored
    不入 worktree 检出）——门按 worktree 根读恒空，queue landing 全量静默放行
    （T1 落地即失效，咬合实弹 BITE_RC=0 实证）。治本=anchor_main_root 锚主仓根
    （approval_resolver #ARCH-324 同款处方）。
    """
    import subprocess

    main = tmp_path / "main"
    main.mkdir()

    def _g(*args: str) -> None:
        subprocess.run(["git", *args], cwd=str(main), check=True, capture_output=True)

    _g("init", "-q", ".")
    _g("config", "user.email", "t@t.local")
    _g("config", "user.name", "t")
    (main / "seed.txt").write_text("seed\n", encoding="utf-8")
    _g("add", "seed.txt")
    _g("commit", "-m", "seed")
    wt = tmp_path / "landing-wt"
    _g("worktree", "add", str(wt), "-b", "landing-wt")

    (main / ".runtime").mkdir()
    entry = {
        "ts": "unit",
        "ts_epoch": 1.0,
        "sid": "st-dead-lane",
        "status": "open",
        "refresh_count": 0,
        "death_evidence": {"reason": "unit-f3", "threshold_seconds": ledger.DEATH_IDLE_SECONDS},
        "resources": {
            "held_files": [],
            "worktrees": [
                {"path": ".aidrafts/st-dead-lane", "exists": True, "dirty_count": 1, "dirty_files": ["docs/x.md"]}
            ],
            "staging": {"file_count": 0},
            "bags": [],
            "heartbeat_files": [],
        },
        "impacted_modules": [],
        "prescription": ["接管完成后 --resolve st-dead-lane"],
    }
    (main / ".runtime" / "takeover_ledger.jsonl").write_text(
        json.dumps(entry, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    spec = make_takeover_pending_gate()
    gateway = SimpleNamespace(project_root=str(wt))
    passed, detail = spec.check(gateway, ["docs/x.md"])
    assert passed is False, "worktree 根网关必须经主仓台账阻断（F3 原缺陷现场）"
    assert "st-dead-lane" in detail
    assert spec.check(gateway, ["docs/other.md"]) == (True, "")
    # F3 第二层：锁内链 commit() 传**绝对路径**（worktree 内暂存文件）——必须同样咬合
    abs_hit = str(wt / "docs" / "x.md")
    passed2, detail2 = spec.check(gateway, [abs_hit])
    assert passed2 is False, "绝对路径（锁内链实参形态）必须归一后咬合"
    assert "st-dead-lane" in detail2


# ---------------------------------------------------------------------------
# 钩子集成：真 SessionRegistry.list_active 判死路径 → 台账条目生成
# ---------------------------------------------------------------------------


def test_list_active_death_hook_writes_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    root = tmp_path
    reg = SessionRegistry(root)
    shard = root / ".runtime" / "session_registry"
    shard.mkdir(parents=True, exist_ok=True)
    now = time.time()
    old = now - 80000
    (shard / f"{DEAD_SID}.json").write_text(
        json.dumps(
            {
                "session_id": DEAD_SID,
                "pid": 999999999,  # 不存在的 PID（判死证据②）
                "start_time": old,
                "held_files": [str(root / "src/zephyr/data/foo.py")],
                "last_heartbeat": old,
                "last_activity": old,
                "logical": False,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(ledger, "_pid_alive", lambda pid: False)
    active = reg.list_active()
    assert all(i.session_id != DEAD_SID for i in active)  # 判死主流程不受影响
    open_entries = ledger.load_open_entries(root)
    assert [e["sid"] for e in open_entries] == [DEAD_SID]
    ev = open_entries[0]["death_evidence"]
    assert ev["pid_alive"] is False
    assert ev["last_activity_age_seconds"] > 7200


def test_death_hook_skips_soft_expire_pid0_session(tmp_path: Path) -> None:
    """回归（2026-10-02 第四夜红蓝审查 R2-F1）：软判死不得污染接管台账。

    实锤背景：pid=0 逻辑会话仅"心跳 90s 过期"即被 list_active 判死，原钩子无条件
    写台账，导致 idle=4~100s 的活会话挂 open 条目（reason 还谎称 >7200s），
    回头被 TAKEOVER-PENDING 门咬住自己的提交。判死(活性)≠需接管(资源)，此处闸住。
    """

    from zephyr.security.access_control.session_concurrency import SessionRegistry

    root = tmp_path
    SOFT_SID = "st-soft-expire-unit"
    reg = SessionRegistry(root)
    shard = root / ".runtime" / "session_registry"
    shard.mkdir(parents=True, exist_ok=True)
    now = time.time()
    (shard / f"{SOFT_SID}.json").write_text(
        json.dumps(
            {
                "session_id": SOFT_SID,
                "pid": 0,  # 逻辑会话：无硬死亡证据
                "start_time": now - 300,
                "held_files": [str(root / "src/zephyr/data/soft.py")],
                "last_heartbeat": now - 200,  # 心跳 90s 过期 → list_active 判死
                "last_activity": now - 100,  # 但 idle 仅 100s，远未达 7200s
                "logical": False,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    active = reg.list_active()
    assert all(i.session_id != SOFT_SID for i in active)  # 判死主流程不变
    assert ledger.load_open_entries(root) == []  # 台账不得被软判死污染


def test_death_evidence_reason_truthful_when_below_threshold() -> None:
    """回归（R2-F1）：未达阈值时 reason 不得谎称 "> 7200s"（审计可信性）。"""
    now = time.time()
    ev = ledger._death_evidence({"last_activity": now - 100.0, "pid": 0}, now)
    assert "<= 7200s" in ev["reason"]
    assert "> 7200s" not in ev["reason"]
    ev2 = ledger._death_evidence({"last_activity": now - 80000.0, "pid": 0}, now)
    assert "> 7200s" in ev2["reason"]


# ---------------------------------------------------------------------------
# CLI 冒烟：--scan / --list / --resolve
# ---------------------------------------------------------------------------


def test_cli_scan_list_resolve(fake_root: Path, capsys: pytest.CaptureFixture) -> None:
    assert ledger.main(["--scan", "--root", str(fake_root)]) == 0
    out = capsys.readouterr().out
    assert DEAD_SID in out
    assert ledger.main(["--list", "--root", str(fake_root)]) == 0
    assert "release_files" in capsys.readouterr().out
    assert ledger.main(["--resolve", DEAD_SID, "--by", "st-taker-cli", "--root", str(fake_root)]) == 0
    assert ledger.load_open_entries(fake_root) == []
    with pytest.raises(SystemExit):
        ledger.main(["--resolve", DEAD_SID, "--root", str(fake_root)])  # 缺 --by → argparse error


def test_scan_and_write_real_constants_match_contract() -> None:
    """判死阈值契约：任务书定值 7200s，被 gate/文档引用禁漂移。"""
    assert ledger.DEATH_IDLE_SECONDS == 7200


def test_sweep_absorbs_crlf_normalized_and_keeps_real_diff(tmp_path: Path) -> None:
    """回归（2026-10-02 红蓝审查 F4）：行尾规范化吸收 + 真差异不吸收。

    原缺陷：落地管线 git add 对文本 CRLF→LF 规范化，而 absorbed 判据=袋 blob
    原始字节哈希==HEAD 原始字节哈希——CRLF 系死信永久不可吸收（chaos2-st-01-0002
    实测 265 vs 259 字节纯行尾差）。治本=双侧 CRLF 规范化后比对。
    """
    import hashlib
    import subprocess

    main = tmp_path / "main"
    main.mkdir()
    lf_body = "line1" + chr(10) + "line2" + chr(10)

    def _g(*args: str) -> None:
        subprocess.run(["git", *args], cwd=str(main), check=True, capture_output=True)

    _g("init", "-q", ".")
    _g("config", "user.email", "t@t.local")
    _g("config", "user.name", "t")
    (main / "a.txt").write_text(lf_body, encoding="utf-8", newline="")
    _g("add", "a.txt")
    _g("commit", "-m", "seed")

    dead = main / ".runtime" / "commit_queue" / "dead"
    dead.mkdir(parents=True)
    crlf_body = lf_body.replace(chr(10), chr(13) + chr(10))
    crlf_sha = hashlib.sha256(crlf_body.encode("utf-8")).hexdigest()
    blobs = main / ".runtime" / "commit_queue" / "blobs"
    blobs.mkdir(parents=True)
    (blobs / crlf_sha).write_bytes(crlf_body.encode("utf-8"))
    # CRLF 袋：内容语义上已在 HEAD（git add 落地会规范化成 LF）——必须判 absorbed
    (dead / "q-crlf-case.json").write_text(
        json.dumps(
            {
                "qid": "q-crlf-case",
                "session_id": "st-x",
                "files": [
                    {
                        "path": "a.txt",
                        "blob_sha256": crlf_sha,
                        "blob_ref": f"blobs/{crlf_sha}",
                        "action": "modify",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    # 真差异袋：HEAD 无此文件——必须保留（fresh/aged，不吸收）
    (dead / "q-real-diff.json").write_text(
        json.dumps(
            {
                "qid": "q-real-diff",
                "session_id": "st-x",
                "files": [{"path": "missing.txt", "blob_sha256": "0" * 64, "action": "modify"}],
            }
        ),
        encoding="utf-8",
    )

    # 2026-10-03 契约变更：清算默认零写（对齐 blob_gc --archive 的安全哲学），
    # 显式 execute=True 才真正搬迁。先钉"默认不动盘"，再钉"执行后正确分诊"。
    assert ledger._cmd_sweep_absorbed(main) == 0
    assert (dead / "q-crlf-case.json").exists(), "默认 dry-run 不得动盘"

    assert ledger._cmd_sweep_absorbed(main, execute=True) == 0
    assert not (dead / "q-crlf-case.json").exists()
    arch = main / ".runtime" / "commit_queue" / "dead_archive" / "absorbed" / "q-crlf-case.json"
    assert arch.exists(), "CRLF 行尾差死信必须被吸收"
    assert (dead / "q-real-diff.json").exists(), "真差异死信不得吸收"


def test_orphan_plain_dir_never_absorbs_main_repo_dirty(tmp_path: Path) -> None:
    """F5 专项（2026-10-02 红蓝审查）：.aidrafts 普通目录孤儿禁吸主仓 git 脏面。

    原缺陷：普通目录在主仓内跑 git status 报出主仓全量脏文件=错误归因，
    门命中面爆炸误咬无辜 commit（orphansim 实测吸入 400+ 主仓脏文件）。
    """
    import subprocess

    main = tmp_path / "main"
    main.mkdir()

    def _g(*args: str) -> None:
        subprocess.run(["git", *args], cwd=str(main), check=True, capture_output=True)

    _g("init", "-q", ".")
    _g("config", "user.email", "t@t.local")
    _g("config", "user.name", "t")
    (main / "tracked.txt").write_text("v1" + chr(10), encoding="utf-8")
    _g("add", "tracked.txt")
    _g("commit", "-m", "seed")
    (main / "tracked.txt").write_text("v2-dirty" + chr(10), encoding="utf-8")  # 主仓脏面

    orphan = main / ".aidrafts" / "st-plain-orphan"
    orphan.mkdir(parents=True)
    (orphan / "own_wip.py").write_text("x = 1" + chr(10), encoding="utf-8")

    found = ledger._scan_orphan_resources(main, now=1_800_000_000.0)
    hit = [e for e in found if e["sid"] == "st-plain-orphan"]
    assert len(hit) == 1
    wt = hit[0]["resources"]["worktrees"][0]
    assert wt["non_worktree_dir"] is True
    assert wt["dirty_files"] == [".aidrafts/st-plain-orphan/own_wip.py"]
    surface = ledger.entry_match_surface(hit[0])
    assert "tracked.txt" not in surface, "主仓脏文件不得进入孤儿命中面"
    assert surface == {".aidrafts/st-plain-orphan/own_wip.py"}


# ---------------------------------------------------------------------------
# D-2 裁定（2026-10-02 第四夜红蓝审查）：袋内遗留=盘点信息，不上执法命中面
# ---------------------------------------------------------------------------


def test_bag_residue_files_narrow_scope(fake_root: Path) -> None:
    """盘点口径实测：3 件路径里只有 1 件是"路径存活且与 HEAD 仍有差异"。"""
    bag = json.loads(
        (fake_root / ".runtime" / "commit_queue" / "dead" / f"q-unit-{DEAD_SID}.json").read_text(encoding="utf-8")
    )
    assert len(bag["files"]) == 3
    assert ledger.bag_residue_files(fake_root, bag) == ["residue.py"]


def test_residue_is_inventory_only_not_enforced() -> None:
    """裁定钉子：袋内遗留文件进台账盘点，但绝不进 TAKEOVER-PENDING 命中面。

    否决纳面的实测据：真库 1233 死袋抽样 60 只，符合"路径存活且内容有差异"的占
    **57.0%**（264/463），全库外推约 5425 条目 / ~3596 唯一路径（含 AGENTS.md）
    会被永久冻结——老袋目标内容天然不等于今日 HEAD，据此纳面即仓库级事故。
    """
    entry = {
        "sid": DEAD_SID,
        "resources": {
            "held_files": ["scripts/keep.py"],
            "bags": [{"qid": "q-unit", "state": "dead", "residue_files": ["residue.py"]}],
        },
    }
    assert ledger.entry_match_surface(entry) == {"scripts/keep.py"}, "袋残留不得上执法面"
    # 但盘点面必须还查得到：接管人不至于只看到一个哑 file_count
    assert entry["resources"]["bags"][0]["residue_files"] == ["residue.py"]


def test_gate_does_not_bite_bag_residue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """防御后回归：哪怕日后有人把袋残留加回命中面，这条会立刻变红。"""
    entry = {
        "ts": "unit",
        "ts_epoch": 1.0,
        "sid": "st-dead-other",
        "status": "open",
        "refresh_count": 0,
        "death_evidence": {"reason": "unit-d2", "threshold_seconds": ledger.DEATH_IDLE_SECONDS},
        "resources": {
            "held_files": ["scripts/keep.py"],
            "worktrees": [],
            "staging": {"file_count": 0},
            "bags": [{"qid": "q-unit", "state": "dead", "residue_files": ["residue.py"]}],
            "heartbeat_files": [],
        },
        "impacted_modules": [],
        "prescription": ["接管完成后 --resolve st-dead-other"],
    }
    root = tmp_path
    (root / ".runtime").mkdir(parents=True)
    (root / ".runtime" / "takeover_ledger.jsonl").write_text(
        json.dumps(entry, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(ledger, "load_open_entries", lambda r: [entry])

    gw = SimpleNamespace(project_root=str(root))
    spec = make_takeover_pending_gate()
    assert spec.check(gw, ["residue.py"], session_id="st-self") == (True, "")
    passed, detail = spec.check(gw, ["scripts/keep.py"], session_id="st-self")
    assert passed is False and "st-dead-other" in detail, "held_files 面照旧咬合"


# ---------------------------------------------------------------------------
# D-2 裁定（2026-10-02 第四夜红蓝审查）：袋内遗留=盘点信息，不上执法命中面
# ---------------------------------------------------------------------------


def test_bag_residue_files_narrow_scope(fake_root: Path) -> None:
    """盘点口径实测：3 件路径里只有 1 件是"路径存活且与 HEAD 仍有差异"。"""
    bag = json.loads(
        (fake_root / ".runtime" / "commit_queue" / "dead" / f"q-unit-{DEAD_SID}.json").read_text(encoding="utf-8")
    )
    assert len(bag["files"]) == 3
    assert ledger.bag_residue_files(fake_root, bag) == ["residue.py"]


def test_residue_is_inventory_only_not_enforced() -> None:
    """裁定钉子：袋内遗留文件进台账盘点，但绝不进 TAKEOVER-PENDING 命中面。

    否决纳面的实测据：真库 1233 死袋抽样 60 只，符合"路径存活且内容有差异"的占
    **57.0%**（264/463），全库外推约 5425 条目 / ~3596 唯一路径（含 AGENTS.md）
    会被永久冻结——老袋目标内容天然不等于今日 HEAD，据此纳面即仓库级事故。
    """
    entry = {
        "sid": DEAD_SID,
        "resources": {
            "held_files": ["scripts/keep.py"],
            "bags": [{"qid": "q-unit", "state": "dead", "residue_files": ["residue.py"]}],
        },
    }
    assert ledger.entry_match_surface(entry) == {"scripts/keep.py"}, "袋残留不得上执法面"
    # 但盘点面必须还查得到：接管人不至于只看到一个哑 file_count
    assert entry["resources"]["bags"][0]["residue_files"] == ["residue.py"]


def test_gate_does_not_bite_bag_residue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """防御后回归：哪怕日后有人把袋残留加回命中面，这条会立刻变红。"""
    entry = {
        "ts": "unit",
        "ts_epoch": 1.0,
        "sid": "st-dead-other",
        "status": "open",
        "refresh_count": 0,
        "death_evidence": {"reason": "unit-d2", "threshold_seconds": ledger.DEATH_IDLE_SECONDS},
        "resources": {
            "held_files": ["scripts/keep.py"],
            "worktrees": [],
            "staging": {"file_count": 0},
            "bags": [{"qid": "q-unit", "state": "dead", "residue_files": ["residue.py"]}],
            "heartbeat_files": [],
        },
        "impacted_modules": [],
        "prescription": ["接管完成后 --resolve st-dead-other"],
    }
    root = tmp_path
    (root / ".runtime").mkdir(parents=True)
    (root / ".runtime" / "takeover_ledger.jsonl").write_text(
        json.dumps(entry, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(ledger, "load_open_entries", lambda r: [entry])

    gw = SimpleNamespace(project_root=str(root))
    spec = make_takeover_pending_gate()
    assert spec.check(gw, ["residue.py"], session_id="st-self") == (True, "")
    passed, detail = spec.check(gw, ["scripts/keep.py"], session_id="st-self")
    assert passed is False and "st-dead-other" in detail, "held_files 面照旧咬合"


# ---------------------------------------------------------------------------
# C11 活性复核（统筹裁定 2026-10-12）：活班被自身崩溃期 open 条目连坐 → 降 warn＋留痕；
# 死会话/他班条目零放宽；verdict 不可达＝保守照拦（读失败不当活证）。
# ---------------------------------------------------------------------------


def _mk_self_entry(sid: str, path: str) -> dict:
    return {
        "ts": "unit",
        "ts_epoch": 1.0,
        "sid": sid,
        "status": "open",
        "refresh_count": 0,
        "death_evidence": {"reason": "unit-c11", "threshold_seconds": ledger.DEATH_IDLE_SECONDS},
        "resources": {
            "held_files": [path],
            "worktrees": [],
            "staging": {"file_count": 0},
            "bags": [],
            "heartbeat_files": [],
        },
        "impacted_modules": [],
        "prescription": [f"接管完成后 --resolve {sid}"],
    }


def _mk_gate_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, entries: list[dict]):
    root = tmp_path
    (root / ".runtime").mkdir(parents=True, exist_ok=True)
    (root / ".runtime" / "takeover_ledger.jsonl").write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(ledger, "load_open_entries", lambda r: entries)
    return SimpleNamespace(project_root=str(root))


def _patch_verdict(monkeypatch: pytest.MonkeyPatch, state: str | None) -> None:
    import zephyr.security.access_control.session_concurrency as sc

    if state is None:

        def _boom(session_id: str, now=None):  # 单口不可达
            raise RuntimeError("verdict facility down")

        monkeypatch.setattr(sc, "liveness_verdict", _boom)
    else:
        monkeypatch.setattr(
            sc,
            "liveness_verdict",
            lambda session_id, now=None: SimpleNamespace(
                session_id=session_id, state=state, authoritative_signal="UNIT-SIGNAL", reasons=[]
            ),
        )


class TestC11SelfBlockSoften:
    def test_alive_self_block_softened_and_audited(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """提交人＝条目属主且现判活 → 放行但 detail 带降级说明，且逐次落一行留痕。"""
        sid = "st-c11-live"
        gw = _mk_gate_env(tmp_path, monkeypatch, [_mk_self_entry(sid, "docs/a.md")])
        _patch_verdict(monkeypatch, "alive")
        spec = make_takeover_pending_gate()
        passed, detail = spec.check(gw, ["docs/a.md"], session_id=sid)
        assert passed is True, "活班自挡应降级放行（今日 14 枚自挡死袋的解药）"
        assert "降级放行" in detail and sid in detail
        audit = tmp_path / ".runtime" / "session_registry_audit" / "takeover_self_block.jsonl"
        assert audit.exists(), "降级必须留痕，不许静默翻转"
        rec = json.loads(audit.read_text(encoding="utf-8").splitlines()[-1])
        assert rec["event"] == "takeover_self_block_softened" and rec["liveness_state"] == "alive"

    def test_degraded_self_block_also_softened(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        gw = _mk_gate_env(tmp_path, monkeypatch, [_mk_self_entry("st-c11-deg", "docs/b.md")])
        _patch_verdict(monkeypatch, "degraded")
        passed, _ = make_takeover_pending_gate().check(gw, ["docs/b.md"], session_id="st-c11-deg")
        assert passed is True

    def test_dead_self_block_still_blocks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """属主自己判死 → 照拦（跨班保护面一寸不缩，也不能让死会话被静默继承）。"""
        sid = "st-c11-dead"
        gw = _mk_gate_env(tmp_path, monkeypatch, [_mk_self_entry(sid, "docs/c.md")])
        _patch_verdict(monkeypatch, "dead")
        passed, detail = make_takeover_pending_gate().check(gw, ["docs/c.md"], session_id=sid)
        assert passed is False and sid in detail

    def test_other_lane_alive_still_blocks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """活性复核只放开『自挡』一格：他班条目哪怕活着也照拦。"""
        gw = _mk_gate_env(tmp_path, monkeypatch, [_mk_self_entry("st-other", "docs/d.md")])
        _patch_verdict(monkeypatch, "alive")
        passed, detail = make_takeover_pending_gate().check(gw, ["docs/d.md"], session_id="st-me")
        assert passed is False and "st-other" in detail

    def test_verdict_unreadable_fails_closed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """单口读不到＝无正证，保守照拦（在册铁律：读失败不得当活证）。"""
        sid = "st-c11-unread"
        gw = _mk_gate_env(tmp_path, monkeypatch, [_mk_self_entry(sid, "docs/e.md")])
        _patch_verdict(monkeypatch, None)
        passed, detail = make_takeover_pending_gate().check(gw, ["docs/e.md"], session_id=sid)
        assert passed is False and sid in detail

    def test_empty_session_id_never_softens(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """无提交人身份（kwargs 缺＋env 缺）一律照拦——不许把"不知道是谁"当放行理由。"""
        monkeypatch.delenv("ZEPHYR_SESSION_ID", raising=False)
        gw = _mk_gate_env(tmp_path, monkeypatch, [_mk_self_entry("st-x", "docs/f.md")])
        _patch_verdict(monkeypatch, "alive")
        passed, _ = make_takeover_pending_gate().check(gw, ["docs/f.md"])
        assert passed is False


# ---------------------------------------------------------------------------
# 命中面剔除（统筹 2026-10-13 批①）——真 git 面，非 monkeypatch
# 病根实证：.runtime/tmp/mineloop2/evidence/takeover_hit_face_proof_20261013.txt
#   车道 HEAD 落后 dev 时，盘字节已等于落地面的件仍被 status 报 M，被算成"他人未落地成果"，
#   隔空挡死分毫无关的码面袋（解锁班／挖矿二班／维护五班三班同墙）。
# ---------------------------------------------------------------------------


def _mk_lagging_lane(tmp_path: Path) -> tuple[Path, str]:
    """造一个真仓＋一条落后 dev 的车道，含三种件：dev-同字节（假阳性）／真在途／未跟踪。"""
    import subprocess

    root = tmp_path / "repo"
    root.mkdir()

    def g(*args: str, cwd: Path | None = None) -> None:
        subprocess.run(
            ["git", *args],
            cwd=str(cwd or root),
            check=True,
            capture_output=True,
            text=True,
        )

    g("init", "-b", "dev")
    g("config", "user.email", "t@example.invalid")
    g("config", "user.name", "t")
    (root / "a.txt").write_text("v1\n", encoding="utf-8")
    (root / "d.txt").write_text("base\n", encoding="utf-8")
    g("add", "a.txt", "d.txt")
    g("commit", "-m", "c1")
    lane = root / ".worktrees" / "lane"
    g("worktree", "add", str(lane), "-b", "lane")  # 车道 HEAD 停在 c1＝落后 dev
    (root / "a.txt").write_text("v2\n", encoding="utf-8")
    g("add", "a.txt")
    g("commit", "-m", "c2")
    # 假阳性形状复刻：车道里把 a.txt 取成 dev 现值 ⇒ 盘字节==dev，但对自家 HEAD 报 "M  a.txt"
    g("checkout", "dev", "--", "a.txt", cwd=lane)
    (lane / "d.txt").write_text("lane-only-work\n", encoding="utf-8")  # 真在途成果
    (lane / "u.txt").write_text("untracked\n", encoding="utf-8")  # 未跟踪
    return root, ".worktrees/lane"


def test_worktree_dirty_excludes_dev_identical_files(tmp_path: Path) -> None:
    """盘字节==落地面的跟踪件移出命中面并计数留痕；真在途与未跟踪件一律保留。"""
    root, wt_rel = _mk_lagging_lane(tmp_path)
    info = ledger._worktree_dirty(root, wt_rel)
    assert info["dirty_files"] == ["d.txt", "u.txt"], info
    assert info["dirty_count"] == 2, info
    assert info["excluded_dev_identical"] == 1, info
    assert info["excluded_dev_identical_files"] == ["a.txt"], info
    # 剔除不是"文件消失"：被移出者须能被独立复核为等于落地面（防自算口径把真在途件洗掉）
    import subprocess

    same = subprocess.run(
        ["git", "-C", str(root / wt_rel), "diff", "--quiet", ledger._LANDING_REF, "--", "a.txt"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert same.returncode == 0, same.stderr


def test_worktree_dirty_keeps_all_when_ref_unavailable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """参照系不可用＝整批保留＋注记（只缩不扩：宁可多挡一枚袋，绝不静默放行真在途成果）。"""
    root, wt_rel = _mk_lagging_lane(tmp_path)
    monkeypatch.setattr(ledger, "_LANDING_REF", "no-such-landing-ref")
    info = ledger._worktree_dirty(root, wt_rel)
    assert info["dirty_files"] == ["a.txt", "d.txt", "u.txt"], info
    assert info["excluded_dev_identical"] == 0, info
    assert info["dirty_note"] == "dev_identical_check_unavailable", info


# ---------------------------------------------------------------------------
# 态5：存量条目刷新出口（维护七班 P2，2026-10-14）
#   病根＝open 条目一旦"注册表除名＋资源已清完"就再不进 --scan 候选集，带旧证据永久挂 open，
#   L3 门禁按 entry_match_surface 逐件挡无辜袋（维护六班袋 0011 实测死在该形态）。
# ---------------------------------------------------------------------------


def _strip_all_resources(root: Path, *, keep_bag: bool = False) -> None:
    """把 DEAD_SID 的五类资源面清到零（held 走注册表条目改写，其余走删目录）。"""
    reg = root / ".runtime" / "session_registry.json"
    data = json.loads(reg.read_text(encoding="utf-8"))
    if DEAD_SID in data:
        data[DEAD_SID] = {**data[DEAD_SID], "held_files": []}
        reg.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    for rel in (Path(".aidrafts") / DEAD_SID, Path(".runtime") / "sessions" / DEAD_SID):
        target = root / rel
        if target.is_dir():
            shutil.rmtree(target)
    bags_dir = root / ".runtime" / "commit_queue" / "dead"
    if bags_dir.is_dir() and not keep_bag:
        for b in bags_dir.glob(f"*{DEAD_SID}*.json"):
            b.unlink()


def _ledger_bytes(root: Path) -> bytes:
    return (root / ".runtime" / "takeover_ledger.jsonl").read_bytes()


def test_refresh_dry_run_moves_nothing(fake_root: Path) -> None:
    """默认 dry-run：只报数，台账字节零变（与 blob_gc --archive／sweep-absorbed 同哲学）。"""
    ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW)
    before = _ledger_bytes(fake_root)
    rep = ledger.refresh_open_entries(fake_root, execute=False, now=NOW)
    assert _ledger_bytes(fake_root) == before, "dry-run 动了盘"
    rec = next(r for r in rep if r["sid"] == DEAD_SID)
    assert rec["action"] == "dry-run" and rec["all_clear"] is False, rec
    assert rec["after"]["held"] >= 1 and rec["after"]["bags"] >= 1, rec


def test_refresh_all_clear_resolves_only_on_execute(fake_root: Path) -> None:
    """资源面复测归零：dry-run 不收口，--execute 才走 resolve 同一通道搬进 resolved/。"""
    ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW)
    _strip_all_resources(fake_root)
    rep = ledger.refresh_open_entries(fake_root, execute=False, now=NOW + 10)
    rec = next(r for r in rep if r["sid"] == DEAD_SID)
    assert rec["all_clear"] is True and rec["action"] == "dry-run", rec
    assert all(v == 0 for v in rec["after"].values()), rec["after"]
    assert ledger.load_open_entries(fake_root), "dry-run 不该收口"

    rep2 = ledger.refresh_open_entries(fake_root, execute=True, now=NOW + 20)
    rec2 = next(r for r in rep2 if r["sid"] == DEAD_SID)
    assert rec2["action"] == "resolved_all_clear", rec2
    assert all(r["sid"] != DEAD_SID for r in ledger.load_open_entries(fake_root))
    resolved = list((fake_root / ".runtime" / "takeover" / "resolved").glob("*.json"))
    assert any(json.loads(f.read_text(encoding="utf-8"))["sid"] == DEAD_SID for f in resolved)


def test_refresh_keeps_entry_open_when_any_residue_remains(fake_root: Path) -> None:
    """残留即不收口：只剩一只死袋也必须留 open（刷新只缩数不造放行）。"""
    ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW)
    _strip_all_resources(fake_root, keep_bag=True)
    rep = ledger.refresh_open_entries(fake_root, execute=True, now=NOW + 30)
    rec = next(r for r in rep if r["sid"] == DEAD_SID)
    assert rec["all_clear"] is False and rec["action"] == "refreshed", rec
    assert rec["after"]["held"] == 0 and rec["after"]["worktrees"] == 0, rec["after"]
    assert rec["after"]["bags"] >= 1, f"死袋残留被清零＝收口判据被撑大: {rec['after']}"
    assert any(r["sid"] == DEAD_SID for r in ledger.load_open_entries(fake_root))


def test_refresh_bypasses_throttle_window_but_hook_path_still_throttled(fake_root: Path) -> None:
    """节流窗只属判死钩子热路径防 IO 风暴；显式 CLI 刷新必须能**越窗把旧资源数缩到实测面**。

    现场形态＝deadclean：claim 已释放、车道已退、心跳已清，但条目还挂着立案当天的
    held=3/worktrees=1 —— 这些旧数会经 `entry_match_surface` 继续挡别人的袋。
    本测试把这条挡道面直接钉住：窗内（+60s < 600s）刷新后，账面 held/worktrees 必须归零，
    仅死袋残留保留（不收口）。去掉写账的 force 旁路＝这条必红（突变实测）。
    """
    ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW)
    stale = next(r for r in ledger.load_open_entries(fake_root) if r["sid"] == DEAD_SID)
    assert len(stale["resources"]["held_files"]) >= 1, "前置：立案时 held 面非空"

    # 钩子路径在节流窗内仍原样返回（IO 风暴防护不许动）
    same = ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW + 60)
    assert same.get("refresh_count", 0) == 0, "钩子路径不该在节流窗内重刷"

    _strip_all_resources(fake_root, keep_bag=True)  # 只剩一只死袋＝有残留，走刷新支不收口
    rep = ledger.refresh_open_entries(fake_root, execute=True, now=NOW + 60)
    rec = next(r for r in rep if r["sid"] == DEAD_SID)
    assert rec["action"] == "refreshed" and rec["all_clear"] is False, rec
    live = next(r for r in ledger.load_open_entries(fake_root) if r["sid"] == DEAD_SID)
    counts = ledger._resource_counts(live["resources"])
    assert counts["held"] == 0 and counts["worktrees"] == 0, f"旧资源数没被缩掉＝挡道面还在: {counts}"
    assert counts["bags"] >= 1, f"死袋残留被吞＝收口判据被撑大: {counts}"
    assert int(live.get("refresh_count", 0)) >= 1, "窗内刷新未落账（force 旁路失效）"


def test_refresh_single_sid_and_unknown_sid(fake_root: Path) -> None:
    """给 SID 只刷一条；刷不存在的 open 条目＝显式 LookupError（对齐 resolve 语义）。"""
    ledger.write_takeover_entry(fake_root, DEAD_SID, now=NOW)
    rep = ledger.refresh_open_entries(fake_root, sid=DEAD_SID, now=NOW)
    assert [r["sid"] for r in rep] == [DEAD_SID]
    with pytest.raises(LookupError):
        ledger.refresh_open_entries(fake_root, sid="st-never-opened", now=NOW)
