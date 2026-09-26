# [A_test] module_id: MOD-TEST-RB14-S7 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-RB14 | src/zephyr/gov_enforcement/commit_gates/_diff_helpers.py §own-scope + commit_queue_landing §池化两车道
# [MODULE] governance.red_blue_pkg14.test_rb14_s7_cross_lane
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.commit_gates.{_diff_helpers,bare_getenv_gate}; scripts.governance.commit_queue_landing; _common(本包)
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/red_blue_pkg14/test_rb14_s7_cross_lane.py
# [MATURITY] testing
# [INVARIANTS] 全沙盒（tmp 仓+tmp 队列根）；判据（宪法 §3.1 own-diff 作用域）：
#   ①两车道各自文件集：own-scope 拆分=own/foreign 零交叠，外来文件落审计
#   (.runtime/gate_audit/<gate>_foreign_staged.jsonl)；②真实门（NO-BARE-GETENV）
#   在「外来 staged 含违规、本件干净」构造下 passed=True（warn 不阻断无辜提交人）；
#   ③池化两车道并行落地：每工 commit 只触本车道文件（零跨道污染）；④尺能红：
#   把 own-scope 拆分旁路成全量扫描后，同一构造门即红（连坐复现）。
# [MODIFY-GUARD] 包14 场景7（跨道连坐）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_rb14_s7_cross_lane.py — 场景7「跨道连坐」红蓝对抗（own-scope 隔离尺）。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.governance.commit_queue_landing as cql
from governance.red_blue_pkg14._common import enqueue, git_text, make_stub_landing_factory
from zephyr.gov_enforcement.commit_gates import _diff_helpers, bare_getenv_gate
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway


class _FakeGateway:
    """own-scope 拆分最小依赖面：project_root（审计/relpath 用）。"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = str(project_root)


# ── 蓝方 ①：own/foreign 拆分+外来审计 ───────────────────────────────────────


def test_s7_blue_split_own_foreign_with_audit(sb_repo, tmp_path):
    gw = _FakeGateway(sb_repo)
    staged = ["lane_a/clean.py", "lane_b/foreign.py", "lane_a/own2.py"]
    own, foreign = _diff_helpers._split_own_foreign(
        gw, staged, ["lane_a/clean.py", "lane_a/own2.py"], None, gate_name="RB14-S7-PROBE"
    )
    assert own == ["lane_a/clean.py", "lane_a/own2.py"], f"own 车道文件集: {own}"
    assert foreign == ["lane_b/foreign.py"], f"外来文件隔离: {foreign}"
    audit = sb_repo / ".runtime" / "gate_audit" / "rb14_s7_probe_foreign_staged.jsonl"
    assert audit.exists(), "外来 staged 必须落审计（可疑不静默）"
    rec = json.loads(audit.read_text(encoding="utf-8").splitlines()[0])
    assert rec["gate"] == "RB14-S7-PROBE" and rec["foreign_files"] == ["lane_b/foreign.py"]
    assert rec["foreign_count"] == 1


def test_s7_blue_empty_scope_falls_back_full_scan(sb_repo):
    """历史直调形态（files 与 session 归属皆空）→ 退化全量扫描，保守面不改宽。"""
    gw = _FakeGateway(sb_repo)
    own, foreign = _diff_helpers._split_own_foreign(gw, ["x.py", "y.py"], None, None, gate_name="RB14-S7-PROBE2")
    assert own == ["x.py", "y.py"] and foreign == []


# ── 蓝方 ②+红证：真实门在「外来违规、本件干净」下的隔离与连坐复现 ────────────


@pytest.fixture()
def two_lane_repo(tmp_path: Path):
    """沙盒仓：车道 A 暂存干净件；车道 B 暂存裸 os.environ.get 违规件。"""
    repo = tmp_path / "s7_repo"
    repo.mkdir()
    repo.joinpath("lane_a").mkdir()
    repo.joinpath("lane_b").mkdir()
    git = _git_factory(repo)
    git("init", "-q", "--initial-branch=dev")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    git("add", "--", "base.txt")
    git("commit", "-qm", "init")
    (repo / "lane_a" / "clean.py").write_text("VALUE = 42\n", encoding="utf-8")
    (repo / "lane_b" / "evil.py").write_text("TOKEN = os.environ.get('ZEPHYR_SECRET_KEY')\n", encoding="utf-8")
    git("add", "--", "lane_a/clean.py", "lane_b/evil.py")
    return repo


def _git_factory(repo: Path):
    import os
    import subprocess

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=str(repo), check=True, capture_output=True)

    return git


def test_s7_blue_real_gate_no_guilt_by_association(two_lane_repo):
    """车道 A 提交（files=clean.py）：外来车道 B 的违规件不得阻断 A（warn+审计）。"""
    repo = two_lane_repo
    gw = GitCommitGateway(project_root=repo)
    spec = bare_getenv_gate.make_bare_getenv_gate()
    own_abs = str(repo / "lane_a" / "clean.py")
    passed, detail = spec.check(gw, [own_abs], session_id="rb14-s7-lane-a")
    assert passed, f"own-scope 隔离：外来违规不得连坐无辜提交人: {detail}"
    audit = repo / ".runtime" / "gate_audit" / "no_bare_getenv_foreign_staged.jsonl"
    assert audit.exists(), "外来违规件必须 warn+审计（不静默放过）"
    rec = json.loads(audit.read_text(encoding="utf-8").splitlines()[-1])
    assert "lane_b/evil.py" in rec["foreign_files"], f"审计须点名外来件: {rec}"


def test_s7_red_full_scan_bypass_reproduces_guilt_by_association(two_lane_repo, monkeypatch):
    """红证：旁路 own-scope 拆分（全量扫描=own 化前旧形态）→ 同一构造门必红。"""
    monkeypatch.setattr(
        bare_getenv_gate,
        "_split_own_foreign",
        lambda gateway, staged, files, session_id, *, gate_name: (list(staged), []),
    )
    repo = two_lane_repo
    gw = GitCommitGateway(project_root=repo)
    spec = bare_getenv_gate.make_bare_getenv_gate()
    own_abs = str(repo / "lane_a" / "clean.py")
    passed, detail = spec.check(gw, [own_abs], session_id="rb14-s7-lane-a")
    assert not passed, "红证失真：全量扫描形态下外来违规竟未触发连坐"
    assert "os.environ" in detail or "os.getenv" in detail, f"死因须指向外来违规: {detail}"


# ── 蓝方 ③：池化两车道并行落地 → 零跨道污染 ─────────────────────────────────


def test_s7_blue_pool_two_lanes_disjoint_files(sb_repo, sb_queue, monkeypatch):
    enqueue(sb_repo, sb_queue, "rb14-s7-pool-a", "s7/lane_a/own_a.txt", "A 车道\n", "A 车道件")
    enqueue(sb_repo, sb_queue, "rb14-s7-pool-b", "s7/lane_b/own_b.txt", "B 车道\n", "B 车道件")

    monkeypatch.setattr(cql, "make_worker_landing", make_stub_landing_factory([]))
    stats = cql.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=2)

    assert stats["done"] == 2, f"两车道各落一件: {stats}"
    # dev 上每个 commit 只触本车道文件（零跨道污染）
    for lane, rel in (("a", "s7/lane_a/own_a.txt"), ("b", "s7/lane_b/own_b.txt")):
        names = git_text(sb_repo, "log", "dev", "--name-only", "--format=", "--", rel)
        assert names.strip() == rel, f"{rel} 的提交只许触自身: {names!r}"
    tip_files = git_text(sb_repo, "show", "dev", "--name-only", "--format=").split()
    assert set(tip_files) <= {"s7/lane_a/own_a.txt", "s7/lane_b/own_b.txt"}, f"dev 树无外来物: {tip_files}"
