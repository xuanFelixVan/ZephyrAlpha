# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.test_session_takeover_ledger
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest；scripts.governance.session_takeover_ledger；zephyr.gov_enforcement.commit_gates.takeover_pending_gate；zephyr.security.access_control.session_concurrency（钩子集成面）
# [CONSUMERS] pytest（tests/governance/）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] tmp_path 假 root 全隔离（零真库/零真 registry/零真 worktree）；worktree dirty 与 PID 存活经 monkeypatch 确定性化；四态覆盖=scan 幂等/条目字段/resolve 迁移/gate 命中与放行；钩子集成用真 SessionRegistry.list_active 判死路径
# [MODIFY-GUARD] 判据变更与 scripts/governance/session_takeover_ledger.py + takeover_pending_gate.py 同批
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；不写生产路径（宪法 §9.6）
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# -*- coding: utf-8 -*-
"""test_session_takeover_ledger.py — 接管台账四态测试（scan 幂等/条目字段/resolve 迁移/gate 命中与放行）"""

from __future__ import annotations

import json
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
    # 死袋 1 只（session_id 匹配）
    dead_dir = root / ".runtime" / "commit_queue" / "dead"
    dead_dir.mkdir(parents=True)
    (dead_dir / f"q-unit-{DEAD_SID}.json").write_text(
        json.dumps({"qid": f"q-unit-{DEAD_SID}", "session_id": DEAD_SID, "files": [{"path": "x"}]}),
        encoding="utf-8",
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
    assert o["resources"]["worktrees"][0]["dirty_files"], "worktree 必须带 dirty_files（门咬合面）"

    assert ledger._cmd_scan(fake_root) == 0, "孤儿在场时 scan CLI 不得崩（原缺陷现场）"
    entries = {e["sid"]: e for e in ledger.load_open_entries(fake_root)}
    e = entries[orphan_sid]
    assert e["status"] == "open"
    assert "orphan_resources" in e["death_evidence"]["reason"]
    rx = "\n".join(e["prescription"])
    assert "worktree remove" in rx and "--resolve" in rx
    assert ledger.entry_match_surface(e) & {"src/zephyr/data/foo.py", "docs/x.md"}

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
    assert res["bags"] == [{"qid": f"q-unit-{DEAD_SID}", "state": "dead", "file_count": 1}]
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

    assert ledger._cmd_sweep_absorbed(main) == 0
    assert not (dead / "q-crlf-case.json").exists()
    arch = main / ".runtime" / "commit_queue" / "dead_archive" / "absorbed" / "q-crlf-case.json"
    assert arch.exists(), "CRLF 行尾差死信必须被吸收"
    assert (dead / "q-real-diff.json").exists(), "真差异死信不得吸收"
