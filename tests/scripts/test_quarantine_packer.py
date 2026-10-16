# [MODULE] tests.scripts.test_quarantine_packer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] scripts.ops.quarantine_packer (pack/校验/INDEX 面), pytest.MonkeyPatch
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] volatile
# [INVARIANTS] 全部落 tmp_path 假 quarantine 树（basetemp=.runtime/tmp/wireB_bt，48h TTL 清扫面，禁写生产 data/）；
#              pack 搬迁零删除语义实测（解压回读字节全等）；校验失败=自建 pack 清零+原目录不损；
#              指针壳/packs/ 自身永不重打包；INDEX.md 表追加+占位行让位实测
# [STABILITY] volatile
# [SAFETY] L
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_quarantine_packer.py — quarantine 陈旧子目录归仓单测（st-diskp0 裁定③接线）。

测试组:
- test_pack_one_happy_path_revive: pack+指针壳+manifest；解压回读字节全等（复活语义）
- test_verify_fail_rollback: 校验失败 → 自建 pack 删除、原目录零损
- test_scan_candidates_two_sides: 超龄候选/新鲜目录/指针壳/packs 自身/散件四类判定
- test_over_threshold_no_candidates_alerts: 超阈值但零候选 → escalated 告警零动作
- test_dry_run_zero_side_effect: dry-run → would_pack 零写
- test_index_rows_and_placeholder: INDEX.md pack 行+运行台账行追加、占位行让位、二次追加累计
- test_disabled_zero_action: enabled=false → disabled 零动作
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tarfile
import time
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ops" / "quarantine_packer.py"


def _load_module(monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("quarantine_packer_under_test", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _age_dir(path: Path, days: float) -> None:
    old = time.time() - days * 86400
    os.utime(path, (old, old))


@pytest.fixture()
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """假 quarantine 树：olds/（120 天，两文件）+ fresh/（当天）+ packs/。"""
    mod = _load_module(monkeypatch)
    root = tmp_path / "repo"
    qdir = root / ".runtime" / "quarantine"
    olds = qdir / "olds"
    olds.mkdir(parents=True)
    sub = olds / "sub"
    sub.mkdir()
    (sub / "b.bin").write_bytes(b"\x00\x01\x02beta")
    (olds / "a.txt").write_bytes(b"alpha\n")
    fresh = qdir / "fresh"
    fresh.mkdir()
    (fresh / "new.txt").write_bytes(b"new\n")
    (qdir / "packs").mkdir()
    _age_dir(olds, 120)
    return {
        "mod": mod,
        "root": root,
        "qdir": qdir,
        "audit": root / ".runtime" / "audit",
        "alerts": root / ".runtime" / "workspace_alerts",
        "olds": olds,
    }


def test_pack_one_happy_path_revive(env):
    """pack 搬迁：pack 落盘+原位指针壳+manifest；解压回读与原字节全等（零删除复活语义）。"""
    e = env
    mod, qdir, olds = e["mod"], e["qdir"], e["olds"]
    orig = {"a.txt": olds.joinpath("a.txt").read_bytes(), "sub/b.bin": olds.joinpath("sub", "b.bin").read_bytes()}
    r = mod.pack_one(qdir, "olds")
    assert (
        r["action"] == "packed"
        and r["file_count"] == 2
        and r["orig_bytes"] == len(orig["a.txt"]) + len(orig["sub/b.bin"])
    )
    pack = qdir / "packs" / "olds.tar.gz"
    assert pack.exists() and r["pack_sha256"] == mod._sha256_file(pack)
    assert Path(r["manifest"]).exists(), "manifest 留证"
    # 原位指针壳：仅 README.md 且含指针标记
    entries = sorted(p.name for p in olds.iterdir())
    assert entries == ["README.md"]
    readme = (olds / "README.md").read_text(encoding="utf-8")
    assert mod.README_MARKER in readme and "olds.tar.gz" in readme and r["pack_sha256"] in readme
    # 复活语义：解压回读字节全等
    revive = qdir / "_revive_check"
    with tarfile.open(pack, "r:gz") as tf:
        tf.extractall(revive)  # noqa: S202 — 测试面自产 pack
    assert (revive / "olds" / "a.txt").read_bytes() == orig["a.txt"]
    assert (revive / "olds" / "sub" / "b.bin").read_bytes() == orig["sub/b.bin"]
    # 再跑不重打包（指针壳跳过）
    r2 = mod.scan_candidates(qdir, threshold_gib=1.5, mtime_days=90)
    assert r2["candidates"] == [], "指针壳不得再成候选"


def test_verify_fail_rollback(env, monkeypatch):
    """校验失败（sha 伪造失配）：自建 pack 清零、原目录零损、动作=failed_verify。"""
    e = env
    mod, qdir, olds = e["mod"], e["qdir"], e["olds"]
    monkeypatch.setattr(mod, "_sha256_file", lambda p: "0" * 64)  # 压前侧恒伪 → 与压内必失配
    r = mod.pack_one(qdir, "olds")
    assert r["action"] == "failed_verify" and r.get("error")
    assert not (qdir / "packs" / "olds.tar.gz").exists(), "坏 pack 清场"
    assert (olds / "a.txt").read_bytes() == b"alpha\n" and (olds / "sub" / "b.bin").exists(), "原目录零损"
    assert not (qdir / "packs" / "olds.tar.gz.tmp").exists(), "tmp 残件清场"


def test_scan_candidates_two_sides(env):
    """候选判定两侧：超龄入选（mtime_over）；新鲜/指针壳/packs 自身/散件不入。"""
    e = env
    mod, qdir = e["mod"], e["qdir"]
    scan = mod.scan_candidates(qdir, threshold_gib=1.5, mtime_days=90)
    assert [c["name"] for c in scan["candidates"]] == ["olds"]
    assert scan["candidates"][0]["reason"] == "mtime_over" and scan["candidates"][0]["age_days"] > 90
    assert scan["over_threshold"] is False and scan["total_bytes"] > 0
    # 指针壳：fresh 改造为壳 → 不入候选（olds 未打包仍入选）
    fresh = qdir / "fresh"
    (fresh / "new.txt").unlink()
    (fresh / "README.md").write_text(f"<!-- {mod.README_MARKER}: packed=x -->\n", encoding="utf-8")
    _age_dir(fresh, 200)
    scan2 = mod.scan_candidates(qdir, threshold_gib=1.5, mtime_days=90)
    assert [c["name"] for c in scan2["candidates"]] == ["olds"], "指针壳不入候选"
    # 散件不入候选（只有目录入）；未打包的 olds 仍在候选
    (qdir / "loose.txt").write_text("x", encoding="utf-8")
    scan3 = mod.scan_candidates(qdir, threshold_gib=1.5, mtime_days=90)
    assert [c["name"] for c in scan3["candidates"]] == ["olds"], "散件不入候选"


def test_over_threshold_no_candidates_alerts(env):
    """超阈值零候选（把 mtime_days 调到巨大）：escalated 告警件+台账，零打包零删除。"""
    e = env
    mod, qdir = e["mod"], e["qdir"]
    summary, errors = mod.run_once(
        repo_root=e["root"],
        quarantine_dir=qdir,
        audit_dir=e["audit"],
        alert_dir=e["alerts"],
        mtime_days=10**9,  # 无候选
        threshold_gib=0.000000001,  # 必超阈（任意正体积）
    )
    assert errors == [], errors
    assert summary["over_threshold"] is True and summary["candidates"] == 0 and summary["alerted"] == 1
    assert summary["packed"] == 0
    body = json.loads(Path(summary["alert_file"]).read_text(encoding="utf-8"))
    assert body["event"] == "quarantine_over_threshold_no_candidate" and body["severity"] == "escalated"
    assert "零动作" in body["note"]
    assert (e["qdir"] / "fresh" / "new.txt").exists() and (e["qdir"] / "olds" / "a.txt").exists(), "零删除"
    lines = (e["audit"] / mod.LEDGER_FILENAME).read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(lines[-1])["event"] == "quarantine_over_threshold_no_candidate"


def test_dry_run_zero_side_effect(env):
    """dry-run：would_pack 判定出全，零 pack/零删除/零台账/零 INDEX。"""
    e = env
    mod, qdir = e["mod"], e["qdir"]
    summary, errors = mod.run_once(
        repo_root=e["root"], quarantine_dir=qdir, audit_dir=e["audit"], alert_dir=e["alerts"], dry_run=True
    )
    assert errors == [] and summary["dry_run"] is True and summary["candidates"] == 1 and summary["packed"] == 0
    assert (qdir / "olds" / "a.txt").exists(), "原目录零损"
    assert sorted(p.name for p in (qdir / "packs").iterdir()) == [], "零 pack 落盘"
    assert not (e["audit"] / mod.LEDGER_FILENAME).exists(), "零台账"


def test_index_rows_and_placeholder(env, tmp_path):
    """INDEX.md：pack 行/运行台账行追加、占位行让位、二次追加累计、CAS 复用 safe_write_text。"""
    e = env
    mod, qdir = e["mod"], e["qdir"]
    summary, _ = mod.run_once(repo_root=e["root"], quarantine_dir=qdir, audit_dir=e["audit"], alert_dir=e["alerts"])
    assert summary["packed"] == 1
    index = qdir / "packs" / "INDEX.md"
    text = index.read_text(encoding="utf-8")
    assert "| olds.tar.gz | .runtime/quarantine/olds |" in text
    assert "_（空——尚无" not in text, "占位行让位"
    assert text.count("| pack+migrate |") == 1
    sha_line = [ln for ln in text.splitlines() if "olds.tar.gz" in ln and ln.startswith("|")][0]
    assert e["mod"]._sha256_file(qdir / "packs" / "olds.tar.gz") in sha_line, "INDEX 记 pack sha256"
    # 二次追加：第二目录打包后两行并存
    second = qdir / "second"
    second.mkdir()
    (second / "c.txt").write_bytes(b"c\n")
    _age_dir(second, 100)
    r2, _ = mod.run_once(repo_root=e["root"], quarantine_dir=qdir, audit_dir=e["audit"], alert_dir=e["alerts"])
    assert r2["packed"] == 1
    text2 = index.read_text(encoding="utf-8")
    assert "olds.tar.gz" in text2 and "second.tar.gz" in text2
    assert text2.count("| pack+migrate |") == 2


def test_disabled_zero_action(env, tmp_path):
    """enabled=false（flags 覆写）：disabled 零动作零读判副作用。"""
    e = env
    mod, qdir, root = e["mod"], e["qdir"], e["root"]
    flags = root / "config" / "flags.yaml"
    flags.parent.mkdir(parents=True, exist_ok=True)
    flags.write_text("flags:\n  quarantine_pack:\n    enabled: false\n", encoding="utf-8")
    summary, errors = mod.run_once(repo_root=root, quarantine_dir=qdir, audit_dir=e["audit"], alert_dir=e["alerts"])
    assert errors == [] and summary["action"] == "disabled" and summary["packed"] == 0
    assert (qdir / "olds" / "a.txt").exists() and sorted(p.name for p in (qdir / "packs").iterdir()) == []
    assert not (e["audit"] / mod.LEDGER_FILENAME).exists()
