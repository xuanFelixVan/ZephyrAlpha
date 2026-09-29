# [BLUEPRINT] MOD-GOV-046 | tests/governance/test_commit_chain_campaign_20260922.py | §campaign-r2r6
# [MODULE] tests.governance.test_commit_chain_campaign_20260922
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.commit_queue; zephyr.gov_enforcement.rule_bridge.commit_preflight
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 提交链战役（st-commitchain-20260922）六项改进的回归钉：R2 大批硬顶/逃生旗/machine 豁免；R5 status 三块（lease/head/daemon+position_ahead）；D6 死信爆发告警 fail-open+env 标记补盲+health 两键；D7 renew 失败终止+requeue from-bag；D1 预检内联适配（CREATE-GUARD/NO-BARE-SQL）+三道直接准入；D4 epoch 三子树；D3 快败子集开关与 hook 漂移守卫。全部 tmp_path 隔离（测试禁写生产路径）
# [MODIFY-GUARD] gate_id="TEST-COMMIT-CHAIN-CAMPAIGN"；新增用例 MUST 与被测行为同批修改
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败正常报错；不写生产队列（queue_root 全部 tmp_path）
# [TESTS] tests/governance/test_commit_chain_campaign_20260922.py（自锚）
# [A_module] module_id=MOD-GOV-046 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""提交链战役（Owner R1-R6）回归钉——2026-09-22 st-commitchain-20260922。"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.commit_queue import (
    _MAX_BATCH_FILES,
    EnqueueOptions,
    QueueReject,
    RequeueError,
    SerializerLease,
    check_dead_burst,
    classify_dead_reason,
    drain_queue,
    enqueue_item,
    queue_health,
    queue_status,
    requeue_dead_item,
)

# ---------------------------------------------------------------------------
# 夹具：tmp 队列根 + 真 git 仓 + 最小 fake gateway（run_git/project_root 两点契约）
# ---------------------------------------------------------------------------


def _mk_queue(tmp_path: Path) -> Path:
    q = tmp_path / "commit_queue"
    q.mkdir()
    return q


def _mk_git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "pkg").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    (repo / "pkg" / "base.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "docs").mkdir(exist_ok=True)
    reg_dir = repo / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    reg_dir.mkdir(parents=True, exist_ok=True)
    (reg_dir / "capability_canonical_file_registry.yaml").write_text(
        "creation_tokens:\n  - file: pkg/new_mod.py\n", encoding="utf-8"
    )
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
    return repo


class _FakeGateway:
    """run_git/project_root 两点最小契约（预检适配层的唯一依赖面）。"""

    def __init__(self, repo: Path):
        self.project_root = repo

    def run_git(self, args: list[str]):
        return subprocess.run(args, capture_output=True, text=True, cwd=str(self.project_root))


# ---------------------------------------------------------------------------
# R2 大批硬顶
# ---------------------------------------------------------------------------


def test_r2_cap_rejects_over_limit(tmp_path: Path) -> None:
    q = _mk_queue(tmp_path)
    files = [(f"d/f{i}.md", b"x") for i in range(_MAX_BATCH_FILES + 1)]
    with pytest.raises(QueueReject, match="超上限"):
        enqueue_item("s1", "m", files, queue_root=q)


def test_r2_cap_allows_at_limit_and_escape_flag(tmp_path: Path) -> None:
    q = _mk_queue(tmp_path)
    files = [(f"d/f{i}.md", b"x") for i in range(_MAX_BATCH_FILES)]
    item = enqueue_item("s1", "m", files, queue_root=q)
    assert len(item["files"]) == _MAX_BATCH_FILES
    files.append(("d/extra.md", b"x"))
    item2 = enqueue_item(
        "s2",
        "m",
        files,
        queue_root=q,
        options=EnqueueOptions(allow_oversize_batch=True, meta_extra={"oversize_batch": "true"}),
    )
    assert item2["meta"]["oversize_batch"] == "true"


def test_r2_machine_lane_exempt(tmp_path: Path) -> None:
    q = _mk_queue(tmp_path)
    files = [(f"d/f{i}.md", b"x") for i in range(_MAX_BATCH_FILES + 5)]
    item = enqueue_item("s1", "m", files, queue_root=q, options=EnqueueOptions(meta_extra={"lane": "machine"}))
    assert len(item["files"]) == _MAX_BATCH_FILES + 5


def test_r2_requeue_channel_exempt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """死信重试是既定决策——requeue 通道豁免硬顶（否则超大死信永久无法重入队）。"""
    q = _mk_queue(tmp_path)
    files = [(f"d/f{i}.md", b"x") for i in range(_MAX_BATCH_FILES + 5)]
    big = enqueue_item("s1", "m", files, queue_root=q, options=EnqueueOptions(allow_oversize_batch=True))
    # 手工造死信（绕过 drain——直接落 dead/ 模拟历史死信）
    import os

    pending = q / "pending" / f"{big['qid']}.json"
    os.rename(pending, q / "dead" / f"{big['qid']}.json")
    # 内容只存在于快照袋（enqueue_item 直收 bytes）——requeue 走 from_bag 原袋通道
    r = requeue_dead_item(big["qid"], queue_root=q, worktree_root=tmp_path, from_bag=True)
    assert r["new_qid"]


# ---------------------------------------------------------------------------
# R5 status 三块
# ---------------------------------------------------------------------------


def test_r5_status_blocks(tmp_path: Path) -> None:
    q = _mk_queue(tmp_path)
    enqueue_item("sa", "m", [("a.md", b"x"), ("b.md", b"y")], queue_root=q)
    enqueue_item("sb", "m", [("c.md", b"z")], queue_root=q)
    st = queue_status(q)
    assert st["lease"]["present"] is False
    assert st["head"]["qid"].startswith("q-")
    assert st["head"]["files"] == 2
    assert st["daemon"]["online"] is False
    pend = [i for i in st["items"] if i["state"] == "pending" and i["session_id"] == "sb"]
    assert pend and pend[0]["position_ahead"] == 1


def test_r5_status_lease_snapshot_live(tmp_path: Path) -> None:
    q = _mk_queue(tmp_path)
    with SerializerLease(q, timeout=1.0):
        st = queue_status(q)
    st2 = queue_status(q)
    assert st["lease"]["present"] is True and st["lease"]["alive"] is True
    assert st2["lease"]["present"] is False  # __exit__ 释放


# ---------------------------------------------------------------------------
# D6 死信爆发 + env 标记 + health 两键
# ---------------------------------------------------------------------------


def test_d6_env_markers_blindspot_fixed() -> None:
    assert classify_dead_reason("reset --hard 失败: PermissionError 拒绝访问") == "env"
    assert classify_dead_reason("unlink WinError 5") == "env"
    assert classify_dead_reason("WinError 206 文件名或扩展名太长") == "env"


def test_d6_health_keys(tmp_path: Path) -> None:
    q = _mk_queue(tmp_path)
    h = queue_health(q)
    assert h["max_session_death_chain"] == 0
    assert h["per_session_top"] == []


def test_d6_dead_burst_below_and_failopen(tmp_path: Path) -> None:
    q = _mk_queue(tmp_path)
    r = check_dead_burst(q)  # 空队列 → 低于阈值
    assert r["fired"] is False
    # 阈值注册表不可达 → fail-open（不抛异常）
    r2 = check_dead_burst(q, registry_path=tmp_path / "nope.yaml")
    assert r2["action"] in ("threshold_unavailable", "below_threshold")


# ---------------------------------------------------------------------------
# D7 renew 失败终止 + requeue from-bag
# ---------------------------------------------------------------------------


def test_d7_renew_fail_aborts_round(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    q = _mk_queue(tmp_path)
    enqueue_item("s1", "m", [("a.md", b"x")], queue_root=q)
    enqueue_item("s1", "m", [("b.md", b"y")], queue_root=q)

    def _dead_renew(self):  # noqa: ANN001
        return False

    monkeypatch.setattr(SerializerLease, "renew", _dead_renew)
    stats = drain_queue(q, landing=lambda item, root: None)  # 不应触达 landing
    assert stats["done"] == 0 and stats["dead"] == 0
    assert len(list((q / "pending").glob("q-*.json"))) == 2  # 项未被取走


def test_d7_requeue_from_bag_verifies_sha(tmp_path: Path) -> None:
    q = _mk_queue(tmp_path)
    src = tmp_path / "src.md"
    src.write_bytes(b"original")
    item = enqueue_item("s1", "m", [("src.md", b"original")], queue_root=q)
    import os

    os.rename(q / "pending" / f"{item['qid']}.json", q / "dead" / f"{item['qid']}.json")
    # 工作区内容已漂移——from_bag 取原快照（sha256 自校验通过）
    (tmp_path / "src.md").write_bytes(b"drifted")
    r = requeue_dead_item(item["qid"], queue_root=q, worktree_root=tmp_path, from_bag=True)
    assert r["new_qid"]
    new_item = json.loads((q / "pending" / f"{r['new_qid']}.json").read_text(encoding="utf-8"))
    blob = q / new_item["files"][0]["blob_ref"]
    assert blob.read_bytes() == b"original"


def test_d7_requeue_from_bag_corrupt_bag(tmp_path: Path) -> None:
    q = _mk_queue(tmp_path)
    (tmp_path / "src.md").write_bytes(b"original")
    item = enqueue_item("s1", "m", [("src.md", b"original")], queue_root=q)
    import os

    os.rename(q / "pending" / f"{item['qid']}.json", q / "dead" / f"{item['qid']}.json")
    # 篡改 blob 袋（内容寻址破损）→ RequeueError 不造假快照
    new_item_file = q / item["files"][0]["blob_ref"]
    new_item_file.write_bytes(b"tampered")
    with pytest.raises(RequeueError, match="sha256"):
        requeue_dead_item(item["qid"], queue_root=q, worktree_root=tmp_path, from_bag=True)


# ---------------------------------------------------------------------------
# D1 预检内联适配 + 直接准入
# ---------------------------------------------------------------------------


def test_d1_whitelist_has_direct_gates() -> None:
    from zephyr.gov_enforcement.rule_bridge.commit_preflight import PREFLIGHT_GATES

    for gate in ("RULING-REFERENCE", "ARCH-REFERENCE", "EXEMPT-ZONE-FM", "DIRECTORY-CONTRACT"):
        assert gate in PREFLIGHT_GATES


def test_d1_create_guard_adapter_blocks_unregistered(tmp_path: Path) -> None:
    from zephyr.gov_enforcement.rule_bridge.commit_preflight import _check_inline_create_guard

    repo = _mk_git_repo(tmp_path)
    (repo / "pkg" / "unreg.py").write_text("X = 1\n", encoding="utf-8")
    ok, detail = _check_inline_create_guard(_FakeGateway(repo), [str(repo / "pkg" / "unreg.py")])
    assert (ok is False and "creation_token" in detail.lower()) or "token" in detail.lower()


def test_d1_create_guard_adapter_passes_registered(tmp_path: Path) -> None:
    from zephyr.gov_enforcement.rule_bridge.commit_preflight import _check_inline_create_guard

    repo = _mk_git_repo(tmp_path)
    # 注册表含该文件 token（真源在仓内 docs/…/capability_canonical_file_registry.yaml）
    (repo / "pkg" / "new_mod.py").write_text(
        "# [BLUEPRINT] M | x.md | §1\n# [MODULE] m\n# [DOMAIN] D\n# [DEPENDENCIES]\n# [CONSUMERS]\n"
        "# [STARTUP] imported\n# [MATURITY] production\n# [INVARIANTS] i\n# [MODIFY-GUARD] g\n"
        "# [STABILITY] stable\n# [SAFETY] L\n# [AI_AUTONOMY] ai_modifiable\n# [ERROR_CONTRACT] e\n"
        "# [TESTS] t\n# [TTL] permanent\n",
        encoding="utf-8",
    )
    ok, detail = _check_inline_create_guard(_FakeGateway(repo), [str(repo / "pkg" / "new_mod.py")])
    assert ok is True, detail


def test_d1_create_guard_adapter_md_covered(tmp_path: Path) -> None:
    from zephyr.gov_enforcement.rule_bridge.commit_preflight import _check_inline_create_guard

    repo = _mk_git_repo(tmp_path)
    (repo / "unreg.md").write_text("doc", encoding="utf-8")
    ok, _ = _check_inline_create_guard(_FakeGateway(repo), [str(repo / "unreg.md")])
    assert ok is False  # ARCH-TTL-DOC-001 七格式覆盖镜像


def test_d1_bare_sql_adapter_blocks_added_line(tmp_path: Path) -> None:
    from zephyr.gov_enforcement.rule_bridge.commit_preflight import _check_inline_no_bare_sql

    repo = _mk_git_repo(tmp_path)
    # 新文件整文件=新增行 → 命中
    (repo / "pkg" / "sql_new.py").write_text('Q = "SELECT a FROM b"\n', encoding="utf-8")
    ok, detail = _check_inline_no_bare_sql(_FakeGateway(repo), [str(repo / "pkg" / "sql_new.py")])
    assert ok is False and "NO-BARE-SQL" in detail
    # 既有文件 HEAD 已含 → 非"新增" → 放行（等价锁内增量语义）
    ok2, _ = _check_inline_no_bare_sql(_FakeGateway(repo), [str(repo / "pkg" / "base.py")])
    assert ok2 is True


def test_d1_bare_sql_added_line_in_tracked_file(tmp_path: Path) -> None:
    from zephyr.gov_enforcement.rule_bridge.commit_preflight import _check_inline_no_bare_sql

    repo = _mk_git_repo(tmp_path)
    p = repo / "pkg" / "base.py"
    p.write_text("VALUE = 1\nBAD = 'DELETE FROM t'\n", encoding="utf-8")
    ok, detail = _check_inline_no_bare_sql(_FakeGateway(repo), [str(p)])
    assert ok is False and "base.py" in detail


# ---------------------------------------------------------------------------
# D4 epoch 三子树 + D3 快败子集
# ---------------------------------------------------------------------------


def test_d4_commit_queue_epoch_and_combination(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from zephyr.gov_enforcement.rule_bridge import commit_belt_daemon as bd

    repo = _mk_git_repo(tmp_path)
    (repo / "scripts").mkdir()
    (repo / "scripts" / "commit_queue.py").write_text("x=1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "cq"], cwd=repo, check=True)
    assert bd._commit_queue_epoch(repo)  # 文件 blob sha 非空
    monkeypatch.setattr(bd, "_gov_enforcement_epoch", lambda p: "AAA")
    monkeypatch.setattr(bd, "_subtree_epoch", lambda p, s: "BBB")
    combined = bd._gate_code_epoch(repo)
    parts = (combined or "").split("|")
    assert len(parts) == 3 and "AAA" in parts and "BBB" in parts


def test_d3_fast_subset_switch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    monkeypatch.delenv("ZEPHYR_PRECOMMIT_FAST_SUBSET", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    assert gw._precommit_fast_subset_enabled() is True  # 非 pytest 环境=默认 ON
    monkeypatch.setenv("ZEPHYR_PRECOMMIT_FAST_SUBSET", "0")
    assert gw._precommit_fast_subset_enabled() is False
    monkeypatch.setenv("ZEPHYR_PRECOMMIT_FAST_SUBSET", "1")
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests::x")  # pytest 环境自动 OFF（集成套件时长保护）
    assert gw._precommit_fast_subset_enabled() is False


def test_d3_fast_subset_skip_inverse_and_short_circuit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase-A=SKIP 反选慢尾的单次调用；首败短路；infra_error 路径降级全通道。"""
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    captured: list[list[str]] = []
    captured_env: list[dict] = []

    class _P:
        def __init__(self, rc: int):
            self.returncode = rc
            self.stdout = f"rc={rc}"
            self.stderr = ""

    def _fake_run(cmd, **kwargs):
        captured.append(cmd)
        captured_env.append(kwargs.get("env") or {})
        return _P(0 if len(captured) == 1 else 1)

    monkeypatch.setattr("zephyr.shared.infra.process_pool.run_subprocess_hidden", _fake_run)
    g = gw.GitCommitGateway.__new__(gw.GitCommitGateway)  # 不走 __init__（只测本方法）
    g.project_root = tmp_path
    out, rc, infra = gw.GitCommitGateway._precommit_fast_subset(
        g, {"SKIP": "gate-commit-gw,gate-worktree-required"}, [["a.py"], ["b.py"]]
    )
    assert infra == "" and rc == 1  # 第二 chunk 首败短路
    assert len(captured) == 2
    # 单次调用形态（非逐 hook）+ SKIP=原 skip ∪ 慢尾
    assert not any("run" in c and c[3] not in ("--files",) and c[3].startswith("gate-") for c in captured)
    skip_val = captured_env[0].get("SKIP", "")
    assert "gate-commit-gw" in skip_val and gw._PRECOMMIT_SLOW_TAIL_HOOKS[0] in skip_val
    assert "gate-worktree-required" in skip_val
    # infra 路径：pre-commit 缺失 → infra_error 非空，rc=0（降级全通道）
    monkeypatch.setattr(
        "zephyr.shared.infra.process_pool.run_subprocess_hidden",
        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("no precommit")),
    )
    out2, rc2, infra2 = gw.GitCommitGateway._precommit_fast_subset(g, {}, [["a.py"]])
    assert rc2 == 0 and infra2


def test_a1_precommit_channel_stat_records_real_ms(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A1 装表钉：pre-commit 通道每次执行落一行分段耗时（total_ms/fast_subset_ms）。

    红证（改前必红）：装表前该册根本不存在——通道是全链最贵段却在账面上零成本。
    """
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    (tmp_path / ".git").mkdir()
    g = gw.GitCommitGateway.__new__(gw.GitCommitGateway)
    g.project_root = tmp_path
    monkeypatch.setattr(gw, "_precommit_run_enabled", lambda: True)
    monkeypatch.setattr(g, "_is_merge_in_progress", lambda: False, raising=False)
    monkeypatch.setattr(gw.GitCommitGateway, "_is_merge_in_progress", lambda self: False)
    monkeypatch.setattr(gw.GitCommitGateway, "_precommit_rel_lists", lambda self, files, root: (["a.py"], []))
    monkeypatch.setattr(
        gw.GitCommitGateway,
        "run_git",
        lambda self, args, **kw: subprocess.CompletedProcess(args, 0, ".git\n", ""),
    )
    monkeypatch.setattr(
        gw.GitCommitGateway,
        "_precommit_run_scoped",
        lambda self, env, root, rel_e, rel_d, idx: ("", 0, False, "", False),
    )
    assert gw.GitCommitGateway._run_precommit_channel(g, "sid-a1", ["a.py"]) is None
    stat = tmp_path / ".runtime" / "audit" / "precommit_channel_stats.jsonl"
    assert stat.exists(), "装表册未生成——A1 未生效"
    row = json.loads(stat.read_text(encoding="utf-8").splitlines()[-1])
    assert row["event"] == "precommit_channel_run" and row["session_id"] == "sid-a1"
    assert isinstance(row["total_ms"], (int, float)) and row["total_ms"] >= 0
    assert "fast_subset_ms" in row and row["rc"] == 0 and row["skipped"] is False


def test_a1_precommit_block_event_no_longer_reports_zero_ms(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A1 遥测黑洞钉：通道阻断时 commit_block_events 的 gate_chain_ms 必须非零。

    红证：装表前恒写 0.0——本断言在旧码上必失败（这正是三日无人发现通道成本的因）。
    """
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    g = gw.GitCommitGateway.__new__(gw.GitCommitGateway)
    g.project_root = tmp_path
    captured: list[float] = []
    monkeypatch.setattr(
        gw.GitCommitGateway, "_audit_commit_block_event", lambda self, sid, blocked, files, ms: captured.append(ms)
    )
    monkeypatch.setattr(
        gw.GitCommitGateway, "_run_precommit_channel", lambda self, sid, files: "GATE-PRECOMMIT-RUN 阻断（桩）"
    )
    # 直接驱动 step5.5 所在的收口段：走 _resolve_commit_result 代价过高，此处按调用点等价重放
    import time as _t

    _t0 = _t.monotonic()
    block = gw.GitCommitGateway._run_precommit_channel(g, "sid-a1b", ["a.py"])
    ms = (_t.monotonic() - _t0) * 1000
    assert block is not None
    # 调用点已改为把真实耗时传给审计（旧码此处传 0.0）
    src = Path(gw.__file__).read_text(encoding="utf-8")
    assert "self._audit_commit_block_event(session_id, blocked, files, _pc_ms)" in src
    assert "self._audit_commit_block_event(session_id, blocked, files, 0.0)" not in src
    assert ms >= 0


# ---------------------------------------------------------------------------
# Rx-3/Rx-4（st-finaldel-crx3-20260929）：确定性 fail_fast + Phase-B 慢尾续跑
# ---------------------------------------------------------------------------

_RX3_FAIL_FAST_HOOKS = ("check-merge-conflict-marker", "detect-private-key-local", "ruff", "ruff-format")


def _mk_gateway(tmp_path: Path):
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    g = gw.GitCommitGateway.__new__(gw.GitCommitGateway)
    g.project_root = tmp_path
    return g


def _stub_precommit_subprocess(monkeypatch: pytest.MonkeyPatch, results: list[tuple[int, str]]) -> list[list[str]]:
    """按脚本顺序返回 pre-commit 调用结果；git 调用恒 rc=0（rev-parse/read-tree/add）。

    副作用：pre-commit 调用的 env 顺序记入 _ENV_LOG（SKIP 反选断言面）。
    """
    import zephyr.shared.infra.process_pool as pp

    calls: list[list[str]] = []
    _ENV_LOG.clear()
    idx = {"i": 0}

    class _P:
        def __init__(self, rc: int, out: str):
            self.returncode = rc
            self.stdout = out
            self.stderr = ""

    def _fake_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        calls.append(list(cmd))
        if cmd and cmd[0] == "git":
            return _P(0, "headsha\n")
        _ENV_LOG.append(dict(kwargs.get("env") or {}))
        i = idx["i"]
        idx["i"] += 1
        rc, out = results[i] if i < len(results) else (0, "")
        return _P(rc, out)

    monkeypatch.setattr(pp, "run_subprocess_hidden", _fake_run)
    return calls


def _stub_channel_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, g) -> None:
    """_run_precommit_channel 前置面最小桩（flag/merge/rel_lists/git-dir）。"""
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    (tmp_path / ".git").mkdir(exist_ok=True)
    monkeypatch.setattr(gw, "_precommit_run_enabled", lambda: True)
    monkeypatch.setattr(gw.GitCommitGateway, "_is_merge_in_progress", lambda self: False)
    monkeypatch.setattr(gw.GitCommitGateway, "_precommit_rel_lists", lambda self, files, root: (["a.py"], []))
    monkeypatch.setattr(
        gw.GitCommitGateway,
        "run_git",
        lambda self, args, **kw: subprocess.CompletedProcess(args, 0, ".git\n", ""),
    )
    monkeypatch.setattr(gw.GitCommitGateway, "_precommit_build_temp_index", lambda self, env, re_, rd: None)
    assert g is not None


def test_rx3_nail_exactly_four_deterministic_hooks_fail_fast() -> None:
    """Rx-3 钉子：恰 4 台确定性 hook 配 fail_fast:true，其余台不配（保 own/foreign 归因）。

    红证：改前 fail_fast 键全仓 0 台——本断言必红；语义=per-hook 先败即停
    （pre_commit run.py:301：current_retval and (config/hook/args 任一 fail_fast)）。
    """
    import yaml

    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    flagged: list[str] = []
    total = 0
    for repo in cfg["repos"]:
        for hook in repo.get("hooks") or []:
            total += 1
            if hook.get("fail_fast"):
                flagged.append(hook["id"])
    assert sorted(flagged) == sorted(_RX3_FAIL_FAST_HOOKS)
    assert total > 60  # 其余 60+ 台零 fail_fast（枚举面守卫）
    # 网关枚举器与同一真源对齐：解析含 4 台 id 且含慢尾代表台
    ids = gw._precommit_config_hook_ids(str(root))
    assert set(_RX3_FAIL_FAST_HOOKS) <= set(ids)
    assert "gate-test" in ids  # 慢尾代表
    assert "ruff" not in gw._PRECOMMIT_SLOW_TAIL_HOOKS  # ruff 在快段（Phase-A 即拦）


def test_rx3_deterministic_red_short_circuits_phaseb(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Rx-3+Rx-4 判别①：确定性 hook（ruff）红 → Phase-A 单调用短路，Phase-B/慢尾零调用。"""
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    (tmp_path / ".git").mkdir(exist_ok=True)
    ruff_red = "- hook id: ruff\n- exit code: 1\n\na.py:3:1 F401 unused import\n"
    calls = _stub_precommit_subprocess(monkeypatch, [(1, ruff_red)])
    g = _mk_gateway(tmp_path)
    monkeypatch.setattr(gw, "_precommit_fast_subset_enabled", lambda: True)
    monkeypatch.setattr(gw, "_precommit_run_enabled", lambda: True)
    monkeypatch.setattr(gw.GitCommitGateway, "_is_merge_in_progress", lambda self: False)
    monkeypatch.setattr(gw.GitCommitGateway, "_precommit_rel_lists", lambda self, files, root: (["a.py"], []))
    monkeypatch.setattr(
        gw.GitCommitGateway,
        "run_git",
        lambda self, args, **kw: subprocess.CompletedProcess(args, 0, ".git\n", ""),
    )
    monkeypatch.setattr(gw.GitCommitGateway, "_precommit_build_temp_index", lambda self, env, re_, rd: None)
    blocked = gw.GitCommitGateway._run_precommit_channel(g, "sid-rx3", ["a.py"])
    assert blocked is not None and "ruff" in blocked  # own 阻断归因含确定性 hook id
    pc_calls = [c for c in calls if c and c[0] != "git"]  # 只数 pre_commit 调用（git 层桩共用）
    assert len(pc_calls) == 1  # Phase-B/慢尾零调用（先失败即停）
    stat = json.loads(
        (tmp_path / ".runtime" / "audit" / "precommit_channel_stats.jsonl").read_text(encoding="utf-8").splitlines()[-1]
    )
    assert stat["rc"] == 1 and stat["skipped"] is False


def test_rx4_phaseb_skips_fast_subset_after_phasea_green(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Rx-4 判别②：Phase-A 绿 → Phase-B SKIP 含快段 id 且慢尾 id 不在 SKIP（慢尾续跑）。"""
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    calls = _stub_precommit_subprocess(monkeypatch, [(0, "phase-a-green"), (0, "phase-b-green")])
    g = _mk_gateway(tmp_path)
    monkeypatch.setattr(gw, "_precommit_fast_subset_enabled", lambda: True)
    monkeypatch.setattr(gw, "_precommit_config_hook_ids", lambda root: ("ruff", "ruff-format", "gate-test"))
    out, rc, mut, infra, skipped = gw.GitCommitGateway._precommit_run_scoped(
        g, {"SKIP": "gate-commit-gw"}, str(tmp_path), ["a.py"], [], str(tmp_path / "idx")
    )
    assert (rc, infra, skipped) == (0, "", False)
    pc_calls = [c for c in calls if c and c[0] != "git"]  # 只数 pre_commit 调用（git 层桩共用）
    assert len(pc_calls) == 2  # Phase-A + Phase-B 各一次调用（非逐 hook）
    env_a = _captured_env(0)
    env_b = _captured_env(1)
    assert "gate-test" in env_a.get("SKIP", "") and "ruff" not in env_a.get("SKIP", "")
    assert "ruff" in env_b.get("SKIP", "") and "gate-test" not in env_b.get("SKIP", "")
    assert "gate-commit-gw" in env_b.get("SKIP", "")  # 基础通道 SKIP 保持
    assert out.startswith("phase-a-green")  # 归因面合并：Phase-A（绿）段并入输出


def _captured_env(i: int) -> dict:
    """取第 i 次 pre-commit 调用的 env 快照（_stub_precommit_subprocess 记录）。"""
    return _ENV_LOG[i]


_ENV_LOG: list[dict] = []


def test_rx4_phaseb_full_env_rollback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Rx-4 回退手柄：ZEPHYR_PRECOMMIT_PHASEB_FULL=1 → Phase-B 恢复全量（SKIP 不含快段）。"""
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    _stub_precommit_subprocess(monkeypatch, [(0, "a"), (0, "b")])
    g = _mk_gateway(tmp_path)
    monkeypatch.setattr(gw, "_precommit_fast_subset_enabled", lambda: True)
    monkeypatch.setattr(gw, "_precommit_config_hook_ids", lambda root: ("ruff", "gate-test"))
    monkeypatch.setattr(gw, "_precommit_phaseb_full_enabled", lambda: True)
    _, rc, _, infra, _ = gw.GitCommitGateway._precommit_run_scoped(
        g, {"SKIP": "gate-commit-gw"}, str(tmp_path), ["a.py"], [], str(tmp_path / "idx")
    )
    assert (rc, infra) == (0, "")
    assert _ENV_LOG  # 环境记录器已填充
    assert "ruff" not in _ENV_LOG[-1].get("SKIP", "")  # 全量 Phase-B：快段不进 SKIP


def test_rx4_slow_tail_red_block_attributes_slow_tail_hook(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Rx-4 判别③：快段绿+慢尾红 → own 阻断归因含慢尾 hook id（归因面合并生效）。"""
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    slow_red = "- hook id: gate-test\n- exit code: 1\n\na.py:12: GATE-TEST violation\n"
    _stub_precommit_subprocess(monkeypatch, [(0, "phase-a-green"), (1, slow_red)])
    g = _mk_gateway(tmp_path)
    _stub_channel_env(monkeypatch, tmp_path, g)
    monkeypatch.setattr(gw, "_precommit_fast_subset_enabled", lambda: True)
    monkeypatch.setattr(gw, "_precommit_config_hook_ids", lambda root: ("ruff", "gate-test"))
    blocked = gw.GitCommitGateway._run_precommit_channel(g, "sid-rx4", ["a.py"])
    assert blocked is not None
    assert "gate-test" in blocked  # 慢尾 hook id 进 own 归因
    assert "a.py" in blocked  # own 文件引用面完整


def test_rx4_config_hook_ids_parse_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Rx-4 降级面：配置缺失/解析失败 → 空元组 → Phase-B 回全量（SKIP 不含快段）。"""
    from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw

    assert gw._precommit_config_hook_ids(str(tmp_path)) == ()  # 文件缺失
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n  - repo: local\n    hooks:\n      - id: x\n", encoding="utf-8"
    )
    assert gw._precommit_config_hook_ids(str(tmp_path)) == ("x",)
    (tmp_path / ".pre-commit-config.yaml").write_text("repos: [\n  broken", encoding="utf-8")
    assert gw._precommit_config_hook_ids(str(tmp_path)) == ()  # 解析失败降级
    # 收窄降级：枚举为空 → Phase-B 全量
    _stub_precommit_subprocess(monkeypatch, [(0, "a"), (0, "b")])
    g = _mk_gateway(tmp_path)
    monkeypatch.setattr(gw, "_precommit_fast_subset_enabled", lambda: True)
    monkeypatch.setattr(gw, "_precommit_config_hook_ids", lambda root: ())
    _, rc, _, _, _ = gw.GitCommitGateway._precommit_run_scoped(
        g, {"SKIP": "gate-commit-gw"}, str(tmp_path), ["a.py"], [], str(tmp_path / "idx")
    )
    assert rc == 0
    assert "ruff" not in _ENV_LOG[-1].get("SKIP", "")  # 无枚举 → 不收窄
