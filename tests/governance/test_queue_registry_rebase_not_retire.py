# [A_test] module_id: MOD-GOV_queue_registry_rebase_not_retire | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_queue_registry_rebase_not_retire
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; subprocess; scripts.commit_queue; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_queue_registry_rebase_not_retire.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根，绝不碰主仓 .runtime/commit_queue 与真实 dev）；
#              每条尺须既能红又能绿（阳性=漂移必被合并仲裁/必死信，阴性=对齐必静默放行），
#              恒绿尺不得进本文件
# [MODIFY-GUARD] 卷宗 §10 Tier-2 条目 6 回归闸：注册表族漂移被重新判死（re-based 失效）或
#                mergeable 放行吞掉真冲突（逃逸口）即红；非 mergeable 严格性松动亦红
# [STABILITY] volatile
# [SAFETY] L
# [TTL] permanent
"""注册表族 stale 基底＝re-base 交三向合并仲裁，不死袋（2026-09-26 四袋事故治本）。

病灶：`_revalidate_stale_base` 对 mergeable 注册表族（is_registry_mergeable）也把
base_blob≠HEAD 计入 mismatched → cascade_stale 死信；而该族自 2026-09-22（W2）起
落地侧本就做条目级三向合并——合并才是仲裁者（同键异容仍死信带双方全文，绝不静默）。
实证死袋：q-20260926-st-zmaster2-20260926-0004（族文件基底漂移）与 -0009
（head_reader 缺失变体）。

治本口径（docs/_working/three_piece_infra/rebase_fix/CASE.md）：
  队列层注入 mergeable_pred（缺省 None=旧严格行为逐字节不变），落地侧
  `_stale_revalidate_counted` 传 is_registry_mergeable；放行路径记
  item.meta.rebased_registry。本文件四条红证 A/B/C/D 各钉一面。
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REG_REL = "docs/01_policies_and_standards/_registry/catalogs/probe_registry.yaml"
PY_REL = "scripts/demo_tool.py"
HEAD_MISSING = "(head_reader 缺失无法重校验)"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cq():
    return _load("_cq_rebase", "scripts/commit_queue.py")


@pytest.fixture(scope="module")
def cql():
    return _load("_cql_rebase", "scripts/governance/commit_queue_landing.py")


def _git(cwd: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120
    )
    assert r.returncode == 0, f"git {' '.join(args)} -> {r.stderr[:300]}"
    return r.stdout.strip()


def _book(pairs: list[tuple[str, str]]) -> str:
    """注册表文本：pairs=[(gate_id, note)]，gate_id=身份键（同 entry_identity_key 口径）。"""
    body = "".join(f"  - gate_id: {g}\n    note: {n}\n" for g, n in pairs)
    return f"total_gates: {len(pairs)}\ngates:\n{body}"


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """tmp 真 git 仓（dev 分支）——零生产写入，口径同 test_commit_queue_base_head.repo。"""
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "dev")
    _git(r, "config", "user.email", "probe@local")
    _git(r, "config", "user.name", "probe")
    _git(r, "config", "core.autocrlf", "false")
    return r


def _commit(repo: Path, path: str, text: str, msg: str) -> str:
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    _git(repo, "add", "--", path)
    _git(repo, "commit", "-qm", msg)
    return _git(repo, "rev-parse", "HEAD")


def _reader(repo: Path):
    """_pool_head_reader 同款：dev 树 blob id；路径不在 HEAD → None。"""

    def read(rel: str) -> str | None:
        r = subprocess.run(
            ["git", "rev-parse", "--verify", "-q", f"refs/heads/dev:{rel}"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return r.stdout.strip() if r.returncode == 0 else None

    return read


def _stale_item(path: str, base_blob: str, base_head: str, qid: str = "q-probe-rebase") -> dict:
    return {
        "qid": qid,
        "session_id": "probe-rebase",
        "base_head": base_head,
        "meta": {"stale": True, "stale_by": "q-other-bag"},
        "files": [{"path": path, "base_blob": base_blob}],
    }


# ---------------------------------------------------------------------------
# 红证 A（本改动要点）：mergeable 族基底漂移 → 重校验放行，条目级合并让 X/Y 双活；
# 同一项在旧严格口径（mergeable_pred=None）下必死——先能红。
# ---------------------------------------------------------------------------


def test_red_a_registry_drift_rebased_and_both_entries_land(cq, cql, repo: Path, tmp_path: Path) -> None:
    base_sha = _commit(repo, REG_REL, _book([("A", "seed")]), "C0 袋的基底")
    base_blob = _git(repo, "rev-parse", f"{base_sha}:{REG_REL}")
    # 袋内容＝在 C0 上纯新增 X
    theirs = _book([("A", "seed"), ("X", "bag-new-entry")]).encode("utf-8")
    # HEAD 期间被他人推进：纯新增 Y（与 X 不同键，合法共存面）
    old_dev = _commit(repo, REG_REL, _book([("A", "seed"), ("Y", "other-session-entry")]), "C1 他人加 Y")

    reader = _reader(repo)
    assert reader(REG_REL) != base_blob  # 前提：基底确已漂移（尺的判别力来源）

    # 先能红：旧严格口径（缺省 mergeable_pred=None，= 今晚 0004 的死因）必须判 mismatched
    item_strict = json.loads(json.dumps(_stale_item(REG_REL, base_blob, base_sha)))
    ok_strict, mism_strict = cq._revalidate_stale_base(item_strict, reader)
    assert not ok_strict and mism_strict == [REG_REL], "改动前口径失效——旧行为被顺手改动？"
    assert "rebased_registry" not in (item_strict.get("meta") or {}), "严格口径不得留 re-base 痕"

    # 改动后：生产 pool 走的注入口放行，且 meta 留痕（合并仲裁，不是重校验放行）
    item = _stale_item(REG_REL, base_blob, base_sha)
    ok, mism = cql._stale_revalidate_counted(item, reader)
    assert ok and mism == [], f"mergeable 族漂移应交合并仲裁，实得 {mism!r}"
    assert item["meta"]["rebased_registry"] == [REG_REL], "放行路径必须留审计痕，不静默"

    # 合并是仲裁者：X（袋侧新增）与 Y（HEAD 侧新增）双双落地
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue-a", worktree_path=tmp_path / "wt-a")
    merged = landing._merge_registry_file(item, REG_REL, theirs, old_dev).decode("utf-8")
    assert "gate_id: X" in merged and "gate_id: Y" in merged and "gate_id: A" in merged, merged

    # 阴性控制（尺非恒放行）：基底对齐（未漂移）的同类项 ⇒ ok 且**不**记 rebased_registry
    aligned = _stale_item(REG_REL, _git(repo, "rev-parse", f"{old_dev}:{REG_REL}"), base_sha, qid="q-aligned")
    ok2, mism2 = cql._stale_revalidate_counted(aligned, reader)
    assert ok2 and mism2 == [] and "rebased_registry" not in (aligned.get("meta") or {})


# ---------------------------------------------------------------------------
# 红证 B（fail-closed 逐字节保留）：非 mergeable 文件（.py）基底漂移 → 仍 mismatched。
# ---------------------------------------------------------------------------


def test_red_b_nonmergeable_stale_base_still_fatal(cq, cql, repo: Path) -> None:
    base_sha = _commit(repo, PY_REL, "VALUE = 1\n", "C0 py 基底")
    base_blob = _git(repo, "rev-parse", f"{base_sha}:{PY_REL}")
    _commit(repo, PY_REL, "VALUE = 2\n", "C1 他人改 py（HEAD 漂移）")
    reader = _reader(repo)

    item = _stale_item(PY_REL, base_blob, base_sha)
    ok, mism = cql._stale_revalidate_counted(item, reader)  # 已注入谓词的最宽口径
    assert not ok and mism == [PY_REL], f"非 mergeable 漂移必须仍死，实得 ok={ok} mism={mism!r}"
    assert "rebased_registry" not in (item.get("meta") or {}), "非 mergeable 不得混入 re-base 痕"

    # 阴性控制：同一路径基底对齐 ⇒ 放行（证明上一条红来自漂移判定，非恒红）
    aligned = _stale_item(PY_REL, _git(repo, "rev-parse", f"refs/heads/dev:{PY_REL}"), base_sha)
    ok2, mism2 = cql._stale_revalidate_counted(aligned, reader)
    assert ok2 and mism2 == []


# ---------------------------------------------------------------------------
# 红证 C（无新逃逸口）：mergeable 族同身份键双方各改 → 放行进合并后，合并仍死信，
# 且死信文本携带双方条目全文——本改动绝不吞掉真冲突。
# ---------------------------------------------------------------------------


def test_red_c_same_key_conflict_still_deadletters_with_both_texts(cql, repo: Path, tmp_path: Path) -> None:
    base_sha = _commit(repo, REG_REL, _book([("A", "base-note")]), "C0 基底：A=base")
    base_blob = _git(repo, "rev-parse", f"{base_sha}:{REG_REL}")
    old_dev = _commit(repo, REG_REL, _book([("A", "OURS-side-edit")]), "C1 dev 侧改 A")
    theirs = _book([("A", "THEIRS-side-edit")]).encode("utf-8")

    item = _stale_item(REG_REL, base_blob, base_sha)
    ok, mism = cql._stale_revalidate_counted(item, _reader(repo))
    assert ok and mism == [] and item["meta"]["rebased_registry"] == [REG_REL], "真冲突项先交合并（仲裁权在合并）"

    landing = cql.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue-c", worktree_path=tmp_path / "wt-c")
    with pytest.raises(RuntimeError, match="三向合并失败") as ei:
        landing._merge_registry_file(item, REG_REL, theirs, old_dev)
    text = str(ei.value)
    assert "OURS-side-edit" in text and "THEIRS-side-edit" in text, f"死信须带双方条目全文，实得 {text[:300]!r}"


# ---------------------------------------------------------------------------
# 红证 D（head_reader 缺失面）：非 mergeable → 仍带 loud marker 致命（-0009 变体中
# 属非 mergeable 的那半必须保持响亮）；mergeable → re-base 留痕放行（-0009 全族袋
# 由合并接管）；同两项在缺省严格口径下都得死（先能红）。
# ---------------------------------------------------------------------------


def test_red_d_head_reader_missing_marker_preserved_for_nonmergeable(cq, cql, repo: Path) -> None:
    base_sha = _commit(repo, PY_REL, "VALUE = 1\n", "C0 基底")
    py_blob = _git(repo, "rev-parse", f"{base_sha}:{PY_REL}")
    _commit(repo, REG_REL, _book([("A", "seed")]), "C1 无关推进")
    reg_blob = _git(repo, "rev-parse", f"refs/heads/dev:{REG_REL}")

    # 先能红：head_reader=None 旧口径对族文件也判死（-0009 的真死因）
    item_reg_strict = _stale_item(REG_REL, reg_blob, base_sha)
    ok_s, mism_s = cq._revalidate_stale_base(item_reg_strict, None)
    assert not ok_s and mism_s == [f"{REG_REL}{HEAD_MISSING}"], "head_reader 缺失旧口径必须判死（红基线）"

    # 改动后·非 mergeable：注入谓词也照死，marker 逐字保留
    item_py = _stale_item(PY_REL, py_blob, base_sha)
    ok, mism = cql._stale_revalidate_counted(item_py, None)
    assert not ok and mism == [f"{PY_REL}{HEAD_MISSING}"], f"非 mergeable 缺 head_reader 必须仍响亮：{mism!r}"

    # 改动后·mergeable：交合并仲裁 + 留痕（合并器对 base 不可知自会 fail-closed，见卷宗）
    item_reg = _stale_item(REG_REL, reg_blob, base_sha)
    ok2, mism2 = cql._stale_revalidate_counted(item_reg, None)
    assert ok2 and mism2 == [] and item_reg["meta"]["rebased_registry"] == [REG_REL]

    # 混合袋（族+非族）：非族 marker 拖袋殉葬语义不变（mismatched 只含非族项）
    mixed = {
        "qid": "q-mixed",
        "base_head": base_sha,
        "meta": {"stale": True},
        "files": [{"path": PY_REL, "base_blob": py_blob}, {"path": REG_REL, "base_blob": reg_blob}],
    }
    ok3, mism3 = cql._stale_revalidate_counted(mixed, None)
    assert not ok3 and mism3 == [f"{PY_REL}{HEAD_MISSING}"], f"混合袋非族项必须仍死：{mism3!r}"
    assert mixed["meta"]["rebased_registry"] == [REG_REL], "混合袋中族项仍须留 re-base 痕"
