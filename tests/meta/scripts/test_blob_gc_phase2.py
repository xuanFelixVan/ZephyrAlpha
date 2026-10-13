# [MODULE] tests.meta.scripts.test_blob_gc_phase2
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] pytest；scripts.governance.blob_gc（importlib 文件加载，禁吃主区旧码）
# [CONSUMERS] pytest（st-deadclean-20261013 段三立法：blob_gc phase2 落码配对测试）
# [STARTUP] manual
# [INVARIANTS] 全部 tmp_path 隔离，禁触生产 .runtime/commit_queue；mtime 用 os.utime 显式造，
#              禁依赖真实时钟；每条判据都要"能红"（phase1 与 phase2 候选集差一枚即红）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_blob_gc_phase2.py — blobs 归档式 GC 的 phase2（D 类随清袋走）配对测试。

在册背景：blob_gc.py 头册 [TESTS] 声明 tests/governance/test_blob_gc.py，实测全仓零命中
＝该在册工具长期**无配对测试**（本班补，非新建第二真源）。Owner 2026-10-13 派工令 v2 面 7
裁 phase2"随清袋走、当日不隔夜"；统筹记账的承重墙＝竞态复扫的"仍引用"只数活引用面，
否则 D 类候选会被自己的归档 JSON 判成仍被引用而全数跳空，旗变空转。
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "governance" / "blob_gc.py"


def _load():
    spec = importlib.util.spec_from_file_location("blob_gc_under_test", str(_SCRIPT))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


bg = _load()
SHA = {
    "z": hashlib.sha256(b"orphan content\n").hexdigest(),
    "d": hashlib.sha256(b"archive-only content\n").hexdigest(),
    "live": hashlib.sha256(b"live content\n").hexdigest(),
    "dead": hashlib.sha256(b"dead-only content\n").hexdigest(),
    "done": hashlib.sha256(b"done content\n").hexdigest(),
}
OLD = datetime(2020, 1, 1)


def _mk_blob(root: Path, key: str, *, age_days: float = 30.0) -> Path:
    p = root / bg.BLOBS_DIR / SHA[key]
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(f"{key} content\n".encode())
    ts = (datetime.now().astimezone() - timedelta(days=age_days)).timestamp()
    os.utime(p, (ts, ts))
    return p


def _mk_bag(root: Path, subdir: str, qid: str, keys: list[str]) -> Path:
    d = root / subdir
    d.mkdir(parents=True, exist_ok=True)
    bag = {"qid": qid, "files": [{"path": f"x{i}.py", "blob_sha256": SHA[k]} for i, k in enumerate(keys)]}
    p = d / f"{qid}.json"
    p.write_text(json.dumps(bag, ensure_ascii=False), encoding="utf-8")
    return p


@pytest.fixture()
def qroot(tmp_path: Path) -> Path:
    """五类各一枚：A 活引／B 仅 dead／C2 仅 done／D 仅归档史（须独占，混引会判 mixed 禁碰）／Z 零引用。"""
    root = tmp_path / "commit_queue"
    for key in SHA:
        _mk_blob(root, key)
    _mk_bag(root, "pending", "q-live-0001", ["live"])
    _mk_bag(root, "dead", "q-dead-0001", ["dead"])
    _mk_bag(root, "done", "q-done-0001", ["done"])
    _mk_bag(root, "dead_archive_20260901", "q-old-0001", ["d"])
    # Z 类：SHA["z"] 不落任何 JSON/JSONL 引用
    return root


def test_phase1_candidates_exclude_archive_only(qroot: Path) -> None:
    """phase1 缺省行为逐字不变：D 类不入候选（旧不变量的回归锚）。"""
    plan = bg.build_report(qroot, now=datetime.now().astimezone(), grace_days=7.0, phase=1)
    assert plan["orphan_candidates"]["shas"] == [SHA["z"]]
    assert plan["buckets"]["archive_only"]["count"] == 1, "夹具须真造出 D 类一枚"
    assert plan["buckets"]["mixed"]["count"] == 0, "混引夹具会让 D 消失，此处须为 0"


def test_phase2_adds_archive_only_and_labels_class(qroot: Path) -> None:
    plan = bg.build_report(qroot, now=datetime.now().astimezone(), grace_days=7.0, phase=2)
    assert sorted(plan["orphan_candidates"]["shas"]) == sorted([SHA["z"], SHA["d"]])
    assert plan["candidate_class"][SHA["d"]] == "archive_only"
    assert plan["candidate_class"][SHA["z"]] == "orphan"


def test_phase2_archive_moves_d_class_and_skips_live_and_dead(qroot: Path) -> None:
    """承重墙：归档 JSON 仍在场也不拦 D 类搬迁；A/B/C 引用面一律不动。"""
    plan = bg.run_archive(qroot, now=datetime.now().astimezone(), grace_days=7.0, phase=2)
    moved = set(plan["run"]["moved"])
    assert moved == {SHA["z"], SHA["d"]}, f"实搬 {moved}——D 被自己的归档史判成仍引用＝phase2 空转"
    assert (qroot / bg.ARCHIVE_DIR / SHA["d"]).is_file()
    for keep in ("live", "dead", "done"):
        assert (qroot / bg.BLOBS_DIR / SHA[keep]).is_file(), f"{keep} 类被误搬＝违反不变量"
    assert plan["run"]["skipped_race_refs"] == [], "race 集须为空（活引用面根本没进候选）"
    rows = [
        json.loads(l)
        for l in (qroot / bg.ARCHIVE_DIR / bg.MANIFEST_NAME).read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    assert {r["class"] for r in rows} == {"orphan", "archive_only"}
    assert all(r["phase"] == 2 for r in rows)


def test_phase1_archive_unchanged_after_flag_added(qroot: Path) -> None:
    """加旗后 phase1 必须与历史行为全等：只搬 Z，D 类原地不动。"""
    plan = bg.run_archive(qroot, now=datetime.now().astimezone(), grace_days=7.0)
    assert set(plan["run"]["moved"]) == {SHA["z"]}
    assert (qroot / bg.BLOBS_DIR / SHA["d"]).is_file()


def test_grace_window_holds_fresh_d_class(qroot: Path) -> None:
    """宽限期内（刚归档的 D 类）不搬——竞态第 1 层对 phase2 同样生效。"""
    fresh = qroot / bg.BLOBS_DIR / SHA["d"]
    now = datetime.now().astimezone().timestamp()
    os.utime(fresh, (now, now))
    plan = bg.build_report(qroot, now=datetime.now().astimezone(), grace_days=7.0, phase=2)
    assert plan["orphan_candidates"]["shas"] == [SHA["z"]]


def test_cli_phase_flag_wires_through(qroot: Path, capsys) -> None:
    rc = bg.main(["--json", "--phase", "2"], queue_root=str(qroot))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["phase"] == 2
    assert sorted(out["orphan_candidates"]["shas"]) == sorted([SHA["z"], SHA["d"]])
    with pytest.raises(SystemExit):
        bg.main(["--phase", "3"], queue_root=str(qroot))
