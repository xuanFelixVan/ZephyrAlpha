# [A_test] module_id: MOD-QCURE-BLOBS-test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_blob_gc
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest；scripts.governance.blob_gc（importlib 文件加载，不 import 生产 .runtime）
# [CONSUMERS] pytest 自动发现；QMine M4 验收回归尺
# [STARTUP] python -m pytest tests/governance/test_blob_gc.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（假 blobs 库+假四态袋全落 tmp_path，绝不读写生产 .runtime/commit_queue）；
#              时间锚固定（2026-09-25 12:00 +08:00 注入 now），宽限期判定与真实时钟解耦（os.utime 造假 mtime）
# [MODIFY-GUARD] MOD-QCURE-BLOBS 验收回归尺：分桶口径/候选=孤儿∧mtime>宽限/二次重扫竞态防护/manifest 留痕字段任一漂移即红
# [STABILITY] volatile
# [SAFETY] L
# [TTL] task_bound
"""blob_gc 回归尺：四态引用扫描、分桶、dry-run 零写、归档+manifest、宽限期、二次重扫竞态、restore 逆向。

全量 tmp_path 造假队列（blobs 库+pending/processing/done/dead/hold/dead_archive_*/dead_triage*.jsonl），
时间锚固定注入，绝不触生产队列（P0-C 同款纪律）。
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 25, 12, 0, 0, tzinfo=timezone(timedelta(hours=8)))
OLD_MTIME = (NOW - timedelta(days=30)).timestamp()  # 超宽限（默认 7d）
FRESH_MTIME = (NOW - timedelta(days=1)).timestamp()  # 宽限期内，禁搬
PHANTOM_SHA = "e" * 64  # JSON 引用但 blob 缺盘


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gc():
    return _load("_blob_gc_mod", "scripts/governance/blob_gc.py")


@pytest.fixture()
def qroot(tmp_path: Path) -> Path:
    """假队列根：四态目录就位；blobs_archive 由 archive 运行自建（断言 dry-run 不创建）。"""
    for d in ("pending", "processing", "done", "dead", "blobs"):
        (tmp_path / d).mkdir()
    return tmp_path


def _content(tag: str) -> bytes:
    return f"blob-content-{tag}".encode()


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _write_blob(root: Path, tag: str, *, mtime: float | None = None) -> str:
    content = _content(tag)
    sha = _sha(content)
    path = root / "blobs" / sha
    path.write_bytes(content)
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return sha


def _write_bag(directory: Path, name: str, shas: list[str]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    bag = {"qid": name, "files": [{"path": f"f{i}.txt", "blob_sha256": s} for i, s in enumerate(shas)]}
    (directory / name).write_text(json.dumps(bag, ensure_ascii=False), encoding="utf-8")


def _populate(root: Path) -> dict[str, str]:
    """矿簿 §1⑥ 台账缩样：A 活(2)/B 仅dead(1)/C2 仅done(1)/C1 混引(1)/D 仅归档(1)/Z 孤儿(2)/幻影(1)/坏袋(1)。"""
    shas = {
        "live": _write_blob(root, "live"),
        "hold": _write_blob(root, "hold"),
        "dead_only": _write_blob(root, "dead_only"),
        "done_only": _write_blob(root, "done_only"),
        "arch_only": _write_blob(root, "arch_only"),
        "mix": _write_blob(root, "mix"),
        "orphan_old": _write_blob(root, "orphan_old", mtime=OLD_MTIME),
        "orphan_fresh": _write_blob(root, "orphan_fresh", mtime=FRESH_MTIME),
    }
    _write_bag(root / "pending", "q-live.json", [shas["live"]])
    _write_bag(root / "hold_st_x", "hold1.json", [shas["hold"]])
    _write_bag(root / "dead", "q-dead.json", [shas["dead_only"], PHANTOM_SHA])
    (root / "dead" / "q-broken.json").write_text("{not-json", encoding="utf-8")  # 坏袋
    _write_bag(root / "done", "q-done.json", [shas["done_only"]])
    _write_bag(root / "done", "q-mix.json", [shas["mix"]])
    _write_bag(root / "dead_archive_20260801", "q-arch.json", [shas["arch_only"]])
    triage = root / "dead_triage_x.jsonl"  # 根级归档史 jsonl：袋逐行 + 坏行
    line = json.dumps({"qid": "t1", "files": [{"path": "a", "blob_sha256": shas["mix"]}]}, ensure_ascii=False)
    triage.write_text(line + "\n{bad-line\n", encoding="utf-8")
    (root / "blobs" / "not-a-blob.txt").write_text("foreign", encoding="utf-8")  # 非 64-hex，不入盘账
    return shas


def _snapshot(root: Path) -> set[tuple[str, int, int]]:
    return sorted(
        (str(p.relative_to(root)), p.stat().st_size, p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()
    )


# ── 1. 分桶正确 ───────────────────────────────────────────────────────────────


def test_buckets_counts_and_bytes(gc, qroot):
    shas = _populate(qroot)
    report = gc.build_report(qroot, now=NOW)
    got = {key: item["count"] for key, item in report["buckets"].items()}
    assert got == {
        "live": 2,
        "dead_only": 1,
        "done_only": 1,
        "done_archive_mix": 1,
        "archive_only": 1,
        "orphan": 2,
        "mixed": 0,
    }
    buckets = report["buckets"]
    assert buckets["live"]["bytes"] == len(_content("live")) + len(_content("hold"))
    assert buckets["dead_only"]["bytes"] == len(_content("dead_only"))
    assert buckets["archive_only"]["bytes"] == len(_content("arch_only"))
    assert report["orphan_candidates"] == {
        "count": 1,
        "bytes": len(_content("orphan_old")),
        "shas": [shas["orphan_old"]],
    }
    assert report["phantom_refs"] == [PHANTOM_SHA]
    assert report["skipped"] == {"bags": 1, "jsonl_lines": 1}  # 坏袋 + triage 坏行，不中断
    assert report["scanned"] == {"blobs_on_disk": 8, "referenced_shas": 7}  # 6 真实被引 + 1 幻影


# ── 2. dry-run 零写 ──────────────────────────────────────────────────────────


def test_dry_run_writes_nothing(gc, qroot, capsys):
    _populate(qroot)
    before = _snapshot(qroot)
    assert gc.main(["--json"], queue_root=qroot) == 0
    assert gc.main([], queue_root=qroot) == 0  # 人读输出同样零写
    assert _snapshot(qroot) == before
    assert not (qroot / "blobs_archive").exists()  # 归档目录都不许被创建
    assert '"mode": "dry-run"' in capsys.readouterr().out


def test_missing_blobs_dir_refused(gc, tmp_path, capsys):
    assert gc.main([], queue_root=tmp_path) == 2  # 队列根缺 blobs/ = exit 2 拒绝
    assert "blobs 目录缺失" in capsys.readouterr().err


# ── 3+4. archive 迁移+manifest / 宽限期拦截 ──────────────────────────────────


def test_archive_moves_candidates_and_leaves_manifest(gc, qroot):
    shas = _populate(qroot)
    old_sha, fresh_sha = shas["orphan_old"], shas["orphan_fresh"]
    report = gc.run_archive(qroot, now=NOW)
    assert report["run"]["moved"] == [old_sha]
    assert report["run"]["skipped_race_refs"] == []
    assert not (qroot / "blobs" / old_sha).exists()  # 源已挪走
    moved = qroot / "blobs_archive" / old_sha
    assert moved.read_bytes() == _content("orphan_old")  # 内容寻址原样
    assert (qroot / "blobs" / fresh_sha).exists()  # 宽限期拦截：新鲜孤儿禁搬
    # 被引用 blob 一个不动（A/B/C/D 全保护）
    for tag in ("live", "hold", "dead_only", "done_only", "arch_only", "mix"):
        assert (qroot / "blobs" / shas[tag]).exists()
    # manifest 留痕：单行、字段齐全、可逆锚定
    lines = (qroot / "blobs_archive" / "manifest.jsonl").read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[0])
    assert record["action"] == "archive"
    assert record["sha"] == old_sha
    assert record["src_path"] == f"blobs/{old_sha}"
    assert record["dst_path"] == f"blobs_archive/{old_sha}"
    assert record["size_bytes"] == len(_content("orphan_old"))
    assert record["run_id"] and record["archived_at"] and record["mtime"]


def test_archive_idempotent_on_second_run(gc, qroot):
    shas = _populate(qroot)
    first = gc.run_archive(qroot, now=NOW)
    assert first["run"]["moved"] == [shas["orphan_old"]]
    second = gc.run_archive(qroot, now=NOW)
    assert second["run"]["moved"] == []
    assert second["orphan_candidates"]["count"] == 0  # 孤儿已被消化


# ── 5. 二次重扫竞态（扫描后新增引用 → 跳过） ─────────────────────────────────


def test_race_rescan_skips_newly_referenced(gc, qroot, monkeypatch):
    shas = _populate(qroot)
    target = shas["orphan_old"]
    original = gc._scan_refs
    calls = {"n": 0}

    def wrapper(root):
        result = original(root)
        calls["n"] += 1
        if calls["n"] == 1:  # 第一次扫描（出候选）之后、二次重扫之前，袋刚入队引用同一 blob
            _write_bag(root / "pending", "q-late.json", [target])
        return result

    monkeypatch.setattr(gc, "_scan_refs", wrapper)
    report = gc.run_archive(qroot, now=NOW)
    assert calls["n"] == 2  # 确证动前二次重扫发生了
    assert report["run"]["moved"] == []
    assert report["run"]["skipped_race_refs"] == [target]
    assert (qroot / "blobs" / target).exists()  # 零丢失：候选被交集排除
    assert not (qroot / "blobs_archive").exists()  # 无搬迁=零落盘


# ── 6. restore 逆向 ──────────────────────────────────────────────────────────


def test_restore_roundtrip_and_skips(gc, qroot):
    shas = _populate(qroot)
    old_sha = shas["orphan_old"]
    gc.run_archive(qroot, now=NOW)
    manifest = qroot / "blobs_archive" / "manifest.jsonl"
    first = gc.run_restore(manifest, now=NOW)
    assert first["restored"] == [old_sha]
    assert (qroot / "blobs" / old_sha).read_bytes() == _content("orphan_old")
    assert not (qroot / "blobs_archive" / old_sha).exists()
    second = gc.run_restore(manifest, now=NOW)
    assert second["restored"] == []
    assert second["already_at_source"] == [old_sha]  # 已在源位（含自愈重落同 sha 场景）不覆盖
    assert (qroot / "blobs_archive" / "manifest.jsonl.restore.jsonl").exists()  # 还原留痕旁挂审计


def test_restore_missing_and_bad_lines(gc, tmp_path):
    manifest = tmp_path / "manifest.jsonl"
    lines = [
        json.dumps({"action": "archive", "sha": "f" * 64, "src_path": "blobs/x", "dst_path": "blobs_archive/x"}),
        "not-json",  # 坏行跳过计数
    ]
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report = gc.run_restore(manifest, now=NOW)
    assert report["missing"] == ["f" * 64]  # 两侧皆缺=幻影，不中断
    assert report["bad_lines"] == 1


def test_restore_missing_manifest_exit2(gc, tmp_path, capsys):
    assert gc.main(["--restore", str(tmp_path / "nope.jsonl")], queue_root=tmp_path) == 2
    assert "manifest 不存在" in capsys.readouterr().err
