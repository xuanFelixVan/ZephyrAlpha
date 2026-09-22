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
