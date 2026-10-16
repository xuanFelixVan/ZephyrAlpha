# [MODULE] tests.shared.test_runtime_hygiene
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.io.runtime_hygiene (被测), pytest
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] volatile
# [INVARIANTS] 全部在 tmp 仓根（测试禁写生产 .runtime/）；轮转用小 max_bytes 实测；
#              TTL 按 mtime 两侧；rescue/.gitkeep 豁免；dry-run 零副作用
# [STABILITY] volatile
# [SAFETY] L
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_runtime_hygiene.py — D3 .runtime 卫生面单测（st-diskp0-20261015）。

测试组:
- test_rotate_sequence_with_gzip_oldest: 连续轮转→.1/.2 位移，第 N 轮最老段压成 .N.gz（不再 unlink）
- test_sweep_audit_rotation_walks_dirs: 两审计目录都进扫，动作计数正确
- test_tmp_ttl_sides_and_exemptions: >48h 清/新鲜留/rescue 豁免/.gitkeep 豁免/顶层散文件也清
- test_dry_run_zero_side_effect: dry-run 只报计数零删除
- test_run_runtime_hygiene_combined: 单入口双腿返回+永不抛（坏输入也不炸）
"""

from __future__ import annotations

import gzip
import os
import time
from pathlib import Path

import pytest

from zephyr.shared.io.runtime_hygiene import (
    DEFAULT_MAX_BYTES,
    rotate_audit_segment,
    run_runtime_hygiene,
    sweep_audit_rotation,
    sweep_runtime_tmp,
)

_H = 3600.0


def _mk(path: Path, size: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"-" * size)
    return path


def test_rotate_sequence_with_gzip_oldest(tmp_path: Path):
    """连续三轮：.1 位移；第三次最老段 .2 被 gzip 成 .2.gz（有界保留，不物理丢弃）。"""
    big = tmp_path / "ga" / "ops_guard_delete.jsonl"
    _mk(big, 2048)
    kw = dict(max_bytes=1024, backup_count=2)
    assert rotate_audit_segment(big, **kw) == "rotated"
    assert big.with_name(big.name + ".1").exists() and not big.exists()
    _mk(big, 2048)
    assert rotate_audit_segment(big, **kw) == "rotated"
    assert big.with_name(big.name + ".2").exists()
    _mk(big, 2048)
    action = rotate_audit_segment(big, **kw)
    assert action == "rotated_gz", f"第三轮最老段应 gzip: {action}"
    gz = big.with_name(big.name + ".2.gz")
    assert gz.exists(), "最老段应被压缩保留"
    assert gzip.decompress(gz.read_bytes()) == b"-" * 2048, "gz 内容应与原段逐字节一致"
    assert big.with_name(big.name + ".1").exists(), "当前段应变 .1"


def test_sweep_audit_rotation_walks_dirs(tmp_path: Path):
    """两审计目录都进扫：超阈当前段被轮转，历史段与普通文件不动。"""
    _mk(tmp_path / ".runtime" / "gate_audit" / "a.jsonl", 3000)
    _mk(tmp_path / ".runtime" / "audit" / "b.jsonl", 3000)
    _mk(tmp_path / ".runtime" / "gate_audit" / "small.jsonl", 10)
    stats = sweep_audit_rotation(tmp_path, max_bytes=1024, backup_count=3)
    assert stats["scanned"] == 3 and stats["rotated"] == 2 and not stats["errors"], stats
    assert (tmp_path / ".runtime" / "gate_audit" / "a.jsonl.1").exists()
    assert (tmp_path / ".runtime" / "audit" / "b.jsonl.1").exists()
    assert (tmp_path / ".runtime" / "gate_audit" / "small.jsonl").exists(), "未超阈不动"


def test_tmp_ttl_sides_and_exemptions(tmp_path: Path):
    """TTL 两侧 + 豁免：>48h 目录/散文件清；新鲜留；rescue/ 与 .gitkeep 永久豁免。"""
    tmp = tmp_path / ".runtime" / "tmp"
    old_dir = tmp / "pytest_999"
    (old_dir / "deep").mkdir(parents=True)
    (old_dir / "deep" / "f.txt").write_text("old", encoding="utf-8")
    old_file = tmp / "commit_msg.txt"
    old_file.write_text("stale", encoding="utf-8")
    fresh_dir = tmp / "st-active-20261015"
    fresh_dir.mkdir(parents=True)
    (fresh_dir / "wip.txt").write_text("busy", encoding="utf-8")
    rescue = tmp / "rescue"
    (rescue / "st-old").mkdir(parents=True)
    (rescue / "st-old" / "casefile.jsonl").write_text("evidence", encoding="utf-8")
    keep = tmp / ".gitkeep"
    keep.write_text("", encoding="utf-8")
    old_ts = time.time() - 49 * _H
    for p in (old_dir, old_file, rescue, keep):
        os.utime(p, (old_ts, old_ts))
    stats = sweep_runtime_tmp(tmp_path, ttl_hours=48)
    assert not old_dir.exists(), "超 TTL 目录应被清"
    assert not old_file.exists(), "超 TTL 顶层散文件应被清"
    assert fresh_dir.exists() and (fresh_dir / "wip.txt").exists(), "新鲜条目必须保留（今日在班车）"
    assert (rescue / "st-old" / "casefile.jsonl").exists(), "rescue/ 豁免——存证面禁清"
    assert keep.exists(), ".gitkeep 豁免"
    assert stats["removed_dirs"] == 1 and stats["removed_files"] == 1
    assert stats["skipped_protected"] == 2 and not stats["errors"], stats


def test_dry_run_zero_side_effect(tmp_path: Path):
    """dry-run：计数照报、盘面零变化。"""
    _mk(tmp_path / ".runtime" / "gate_audit" / "big.jsonl", 3000)
    tmp = tmp_path / ".runtime" / "tmp"
    old = tmp / "old_dir"
    old.mkdir(parents=True)
    os.utime(old, (time.time() - 100 * _H,) * 2)
    rot = sweep_audit_rotation(tmp_path, max_bytes=1024, dry_run=True)
    ttls = sweep_runtime_tmp(tmp_path, ttl_hours=48, dry_run=True)
    assert rot["rotated"] == 1 and (tmp_path / ".runtime" / "gate_audit" / "big.jsonl").exists()
    assert not (tmp_path / ".runtime" / "gate_audit" / "big.jsonl.1").exists(), "dry-run 不得真轮转"
    assert ttls["removed_dirs"] == 1 and old.exists(), "dry-run 不得真删"


def test_run_runtime_hygiene_combined(tmp_path: Path):
    """单入口双腿：两键齐返；坏输入（目录缺/只读盘面）也永不抛。"""
    _mk(tmp_path / ".runtime" / "audit" / "x.jsonl", 3000)
    out = run_runtime_hygiene(tmp_path, dry_run=True, max_bytes=1024)
    assert set(out) >= {"audit_rotation", "tmp_ttl", "dry_run"}
    assert out["audit_rotation"]["rotated"] == 1
    empty = run_runtime_hygiene(tmp_path / "not_a_repo", dry_run=False)
    assert "audit_rotation" in empty and "tmp_ttl" in empty
    assert DEFAULT_MAX_BYTES > 0  # 判据常量同源引用（audit_jsonl_writer）可导入
