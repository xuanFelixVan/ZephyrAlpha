# -*- coding: utf-8 -*-
"""run_archive/巡检/演练 红蓝对抗红队用例——攻击自家图书馆 API 的乱输入面（SOP-D §3/§9）。"""
from __future__ import annotations

import pytest

from zephyr.backtest.run_archive import (
    RunArchiveError,
    create_run,
    load_meta,
    write_step,
)


@pytest.fixture()
def root(tmp_path):
    return tmp_path / "runs"


def _open(root, run_id="VAL-20260912-000000"):
    create_run(run_id, "BT-P0-001", "VAL", artifacts_root=root)
    return run_id


# ── 红队1：文件名路径穿越（ASCII 合法但含分隔符/父引用）──────────────────

@pytest.mark.parametrize("evil", [
    "..%2F..%2Fescape",            # 纯 ASCII 编码探针（应被守门，见独立用例）
    "a..b",                        # 内嵌 ..（无害但歧义，按最严执行）
])
def test_filename_dotdot_segments_rejected(root, evil):
    _open(root)
    with pytest.raises(RunArchiveError):
        write_step(root and "VAL-20260912-000000", "04", b"x", filename=evil, artifacts_root=root)


@pytest.mark.parametrize("evil", [
    "..\\..\\escape.txt",          # Windows 反斜杠穿越
    "../../escape.txt",            # POSIX 穿越（ASCII 内含 /）
])
def test_filename_separator_traversal_rejected(root, evil):
    rid = _open(root)
    with pytest.raises(RunArchiveError):
        write_step(rid, "04", b"x", filename=evil, artifacts_root=root)


@pytest.mark.parametrize("evil", [".", ".."])
def test_filename_windows_reserved_dot_rejected(root, evil):
    rid = _open(root)
    with pytest.raises(RunArchiveError):
        write_step(rid, "04", b"x", filename=evil, artifacts_root=root)


# ── 红队2：run_id 边界 ───────────────────────────────────────────────────

@pytest.mark.parametrize("bad", [
    "VAL-..\\..\\x",               # 分隔符
    "VAL-a/b",                     # 正斜杠（regex 不允许 /，应拒）
    " val-x",                      # 前导空格
    "VAL-",                        # 空主体
])
def test_run_id_hostile_forms_rejected(root, bad):
    with pytest.raises(RunArchiveError):
        create_run(bad, "BT-P0-001", "VAL", artifacts_root=root)


def test_load_meta_never_escapes_root(root):
    _open(root)
    with pytest.raises(RunArchiveError):
        load_meta("../VAL-20260912-000000", artifacts_root=root)   # .. 在 id 中=regex 拒


# ── 红队3：finalize 后追加新文件允许、覆盖仍拒（只增不改语义边界）────────

def test_post_finalized_errata_append_ok_overwrite_still_rejected(root):
    rid = _open(root)
    for step, body in (("01", "s"), ("02", "[]"), ("03", "[]"), ("05", "[]"), ("06", "x")):
        if step == "06":
            write_step(rid, "06", b"x", filename="equity.csv", artifacts_root=root)
        else:
            write_step(rid, step, body, artifacts_root=root)
    write_step(rid, "verdict", "# 判定书", artifacts_root=root)
    from zephyr.backtest.run_archive import finalize_run
    finalize_run(rid, artifacts_root=root)
    write_step(rid, "errata", "# 勘误：xx 修正", artifacts_root=root)   # 追加=合法
    with pytest.raises(RunArchiveError):
        write_step(rid, "verdict", "# 改判定", artifacts_root=root)   # 覆盖=拒绝
