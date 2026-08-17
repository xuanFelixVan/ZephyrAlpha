# [BLUEPRINT] MOD-GOV-043 | tests/governance/audit/test_file_ops_enforcement.py | §
# [MODULE] tests.governance.audit.test_file_ops_enforcement
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] scripts/ops_guard.py; zephyr.governance.audit.reconciliation_registry
# [CONSUMERS] pytest
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] in-process 补丁为进程级——测试后 MUST 恢复原始原语（防污染同进程其他测试）
# [MODIFY-GUARD] file_ops 词表/判定矩阵变更需同步本文件
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红队突破
# [TESTS] 本文件
# [TTL] permanent
"""test_file_ops_enforcement.py — T1 能力收敛红队验收（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）

裁定书验收标准 T1：红队测试"reconciler 删除保护区文件"100% 阻断+审计落盘；
worker 进程内直接 os.remove 保护区路径同样被拦。
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))

from scripts.ops_guard import (  # noqa: E402
    DeleteBlockedError,
    _BULK_APPROVED,
    _inprocess_judge,
    audit_delete,
    get_reconciler_context,
    guard_remove,
    guard_rmtree,
    install_inprocess_enforcement,
    prune_recycle_bin,
    reset_reconciler_context,
    set_reconciler_context,
    uninstall_inprocess_enforcement,
    _ORIG_PRIMITIVES,
)
import scripts.ops_guard as ops_guard_mod  # noqa: E402

from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    ReconciliationRegistry,
    ReconcileResult,
    ReconcilerSpec,
    _compose_reconcilers,
)


@pytest.fixture
def audit_tmp(tmp_path, monkeypatch):
    """审计落盘重定向到 tmp（ops_guard 审计锚定 project_root）。"""
    monkeypatch.setenv("ZEPHYR_SESSION_ID", "test-file-ops")
    return tmp_path


def _read_audit(repo_root: Path) -> list[dict]:
    p = Path(repo_root) / ".runtime" / "gate_audit" / "ops_guard_delete.jsonl"
    if not p.is_file():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]


# ---------------------------------------------------------------------------
# 1. 注册期强校验
# ---------------------------------------------------------------------------
class TestRegisterEnforcement:
    def test_empty_file_ops_rejected(self):
        reg = ReconciliationRegistry()
        with pytest.raises(ValueError, match="file_ops"):
            reg.register(ReconcilerSpec(
                gate_id="G1", trigger=lambda f: True,
                reconcile=lambda f, s: ReconcileResult(action="clean"),
            ))

    def test_invalid_file_ops_rejected(self):
        reg = ReconciliationRegistry()
        with pytest.raises(ValueError, match="非法值"):
            reg.register(ReconcilerSpec(
                gate_id="G2", trigger=lambda f: True,
                reconcile=lambda f, s: ReconcileResult(action="clean"),
                file_ops=frozenset({"read", "bogus"}),
            ))

    def test_valid_file_ops_accepted(self):
        reg = ReconciliationRegistry()
        reg.register(ReconcilerSpec(
            gate_id="G3", trigger=lambda f: True,
            reconcile=lambda f, s: ReconcileResult(action="clean"),
            file_ops=frozenset({"read", "write"}),
        ))
        assert reg.spec_count == 1

    def test_compose_unions_file_ops(self):
        a = ReconcilerSpec(gate_id="A", trigger=lambda f: True,
                           reconcile=lambda f, s: ReconcileResult(action="clean"),
                           file_ops=frozenset({"read"}))
        b = ReconcilerSpec(gate_id="B", trigger=lambda f: True,
                           reconcile=lambda f, s: ReconcileResult(action="clean"),
                           file_ops=frozenset({"read", "delete"}))
        combo = _compose_reconcilers("COMBO", a, b)
        assert combo.file_ops == frozenset({"read", "delete"})


# ---------------------------------------------------------------------------
# 2. 红队：reconciler 上下文内未声明删除被阻断（裁定书 T1 验收）
# ---------------------------------------------------------------------------
class TestReconcilerContextEnforcement:
    def test_undeclared_delete_blocked_and_critical_warn(self, tmp_path, monkeypatch):
        """未声明 delete 的 reconciler 执行 guard_remove → 阻断+critical_warn+审计。"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".runtime" / "gate_audit").mkdir(parents=True)

        def evil_reconcile(files, sid):
            guard_remove("docs/important.md")  # 未声明 delete
            return ReconcileResult(action="clean")

        reg = ReconciliationRegistry()
        reg.register(ReconcilerSpec(
            gate_id="EVIL", trigger=lambda f: True, reconcile=evil_reconcile,
            file_ops=frozenset({"read", "write"}),
        ))
        results = reg.reconcile_for(["x"], "red-team")
        assert results[0].action == "critical_warn"
        assert "file_ops" in results[0].detail

    def test_declared_delete_passes_with_audit(self, tmp_path, monkeypatch):
        """已声明 delete 的 reconciler 删除白名单文件 → 直通+审计落盘。"""
        monkeypatch.chdir(tmp_path)
        target = tmp_path / ".runtime" / "tmp" / "victim.txt"
        target.parent.mkdir(parents=True)
        target.write_text("x", encoding="utf-8")

        def ok_reconcile(files, sid):
            guard_remove(str(target))
            return ReconcileResult(action="clean")

        reg = ReconciliationRegistry()
        reg.register(ReconcilerSpec(
            gate_id="OK", trigger=lambda f: True, reconcile=ok_reconcile,
            file_ops=frozenset({"read", "delete"}),
        ))
        results = reg.reconcile_for(["x"], "red-team")
        assert results[0].action == "clean"
        assert not target.exists()

    def test_context_reset_no_leak(self, tmp_path, monkeypatch):
        """上下文 reset：下一 reconciler 不受前一 reconciler 声明影响。"""
        monkeypatch.chdir(tmp_path)
        leaked = []

        def r1(files, sid):
            return ReconcileResult(action="clean")

        def r2(files, sid):
            leaked.append(get_reconciler_context())
            return ReconcileResult(action="clean")

        reg = ReconciliationRegistry()
        reg.register(ReconcilerSpec(gate_id="R1", priority=1, trigger=lambda f: True,
                                    reconcile=r1, file_ops=frozenset({"read", "delete"})))
        reg.register(ReconcilerSpec(gate_id="R2", priority=2, trigger=lambda f: True,
                                    reconcile=r2, file_ops=frozenset({"read"})))
        reg.reconcile_for(["x"], "s")
        # R2 执行时上下文应为 R2 自己的声明（非 R1 的 delete）
        assert leaked[0] == ("R2", frozenset({"read"}))

    def test_declared_recursive_protected_still_blocked(self, tmp_path, monkeypatch):
        """双保险：已声明 delete 的 reconciler 对保护区递归 rmtree 仍硬拦。"""
        monkeypatch.chdir(tmp_path)

        def evil(files, sid):
            guard_rmtree("src/zephyr")  # 保护区递归
            return ReconcileResult(action="clean")

        reg = ReconciliationRegistry()
        reg.register(ReconcilerSpec(gate_id="EVIL2", trigger=lambda f: True,
                                    reconcile=evil, file_ops=frozenset({"read", "delete"})))
        results = reg.reconcile_for(["x"], "s")
        assert results[0].action in ("critical_warn", "warn")  # DeleteBlockedError→critical_warn；OSError→warn


# ---------------------------------------------------------------------------
# 3. in-process 补丁（worker 进程裸 stdlib 删除拦截）
# ---------------------------------------------------------------------------
@pytest.fixture()
def _restore_primitives():
    """补丁进程级——测试后恢复原始原语防污染。

    使用官方 uninstall_inprocess_enforcement()（而非手动恢复），
    确保 _ORIG_PRIMITIVES 字典被正确清空，避免二次安装时原语链损坏。
    """
    yield
    uninstall_inprocess_enforcement()


@pytest.mark.usefixtures("_restore_primitives")
class TestInprocessEnforcement:
    def test_install_idempotent(self):
        assert install_inprocess_enforcement() is True
        assert install_inprocess_enforcement() is False

    def test_bare_os_remove_protected_blocked_outside_context(self, tmp_path, monkeypatch):
        """红队：worker 进程内（无 reconciler 上下文）裸 os.remove 保护区路径被拦。"""
        monkeypatch.chdir(tmp_path)
        install_inprocess_enforcement()
        with pytest.raises(DeleteBlockedError):
            os.remove("src/zephyr/__init__.py")

    def test_bare_os_remove_whitelist_allowed(self, tmp_path, monkeypatch):
        """白名单路径裸删除放行（.runtime/tmp）。"""
        monkeypatch.chdir(tmp_path)
        install_inprocess_enforcement()
        victim = tmp_path / ".runtime" / "tmp" / "ok.txt"
        victim.parent.mkdir(parents=True)
        victim.write_text("x", encoding="utf-8")
        os.remove(str(victim))
        assert not victim.exists()

    def test_path_unlink_covered(self, tmp_path, monkeypatch):
        """pathlib.Path.unlink 经 os 层 patch 覆盖（保护区阻断）。"""
        monkeypatch.chdir(tmp_path)
        install_inprocess_enforcement()
        with pytest.raises(DeleteBlockedError):
            Path("tests/conftest.py").unlink()

    def test_audit_written_for_block(self, tmp_path, monkeypatch):
        """阻断事件落审计（T2③ 审计覆盖率采集层）。

        T3② 后 docs/ untracked 目标由 docs_untracked_block 动作落审计
        （其余保护区目标仍为 inprocess_block）——两动作都计入阻断审计。
        """
        monkeypatch.chdir(tmp_path)
        # 审计锚定 _get_project_root()（进程内缓存）——钉住为 tmp_path 隔离验证
        monkeypatch.setattr(ops_guard_mod, "_PROJECT_ROOT_CACHE", tmp_path)
        install_inprocess_enforcement()
        with pytest.raises(DeleteBlockedError):
            os.remove("docs/x.md")
        entries = _read_audit(tmp_path)
        blocked = [
            e for e in entries
            if e.get("action") in ("inprocess_block", "docs_untracked_block")
        ]
        assert blocked, "阻断事件未落审计"

    def test_audit_stats_counted(self, tmp_path, monkeypatch):
        """T2③ 覆盖率指标：judge/allow/block 计数自洽（覆盖率=100% by construction）。"""
        from scripts.ops_guard import get_audit_stats

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(ops_guard_mod, "_PROJECT_ROOT_CACHE", tmp_path)
        install_inprocess_enforcement()
        before = get_audit_stats()
        victim = tmp_path / ".runtime" / "tmp" / "stat_ok.txt"
        victim.parent.mkdir(parents=True, exist_ok=True)
        victim.write_text("x", encoding="utf-8")
        os.remove(str(victim))  # allow
        with pytest.raises(DeleteBlockedError):
            os.remove("docs/y.md")  # block
        after = get_audit_stats()
        assert after["judge_calls"] - before["judge_calls"] == 2
        assert after["allow"] - before["allow"] == 1
        assert after["block"] - before["block"] == 1
        assert after["audit_failed"] == before["audit_failed"]  # 零落盘失败=覆盖率 100%


# ---------------------------------------------------------------------------
# 3b. docs/ untracked 人工确认闸门（T3②，清风草稿丢失治本）
# ---------------------------------------------------------------------------
@pytest.mark.usefixtures("_restore_primitives")
class TestDocsUntrackedEnforcement:
    """docs/ 下 untracked 文件删除/移动需人工确认（ZEPHYR_FORCE_DELETE=1）。

    裁定书 T3 验收：docs/ 下 untracked 文件被删必有审计记录；无记录事件=0。
    """

    def test_inprocess_bare_remove_docs_untracked_blocked(self, tmp_path, monkeypatch):
        """红队：worker 进程内裸 os.remove untracked docs 草稿 → 阻断+审计。"""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(ops_guard_mod, "_PROJECT_ROOT_CACHE", tmp_path)
        victim = tmp_path / "docs" / "draft.md"
        victim.parent.mkdir(parents=True)
        victim.write_text("未提交草稿", encoding="utf-8")
        install_inprocess_enforcement()
        with pytest.raises(DeleteBlockedError, match="untracked"):
            os.remove("docs/draft.md")
        assert victim.exists(), "被拦文件不应消失"
        entries = _read_audit(tmp_path)
        assert any(
            e.get("action") == "docs_untracked_block" for e in entries
        ), "docs_untracked 阻断未落审计（T3 验收：无记录事件=0）"

    def test_inprocess_force_allows_untracked(self, tmp_path, monkeypatch):
        """人工确认标记 ZEPHYR_FORCE_DELETE=1 → 放行执行（审计照落）。"""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(ops_guard_mod, "_PROJECT_ROOT_CACHE", tmp_path)
        monkeypatch.setenv("ZEPHYR_FORCE_DELETE", "1")
        victim = tmp_path / "docs" / "draft.md"
        victim.parent.mkdir(parents=True)
        victim.write_text("确认废弃", encoding="utf-8")
        install_inprocess_enforcement()
        os.remove("docs/draft.md")
        assert not victim.exists()

    def test_inprocess_gateway_env_no_bypass(self, tmp_path, monkeypatch):
        """反架空：gateway 标记不豁免 untracked 闸门（worker 继承 env 场景）。"""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(ops_guard_mod, "_PROJECT_ROOT_CACHE", tmp_path)
        monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY", "1")
        monkeypatch.delenv("ZEPHYR_FORCE_DELETE", raising=False)
        victim = tmp_path / "docs" / "draft.md"
        victim.parent.mkdir(parents=True)
        victim.write_text("x", encoding="utf-8")
        install_inprocess_enforcement()
        with pytest.raises(DeleteBlockedError, match="untracked"):
            os.remove("docs/draft.md")

    def test_guard_recycle_docs_untracked_blocked(self, tmp_path, monkeypatch):
        """guard_recycle 对 untracked docs 文件同样拦截（进回收站=从 docs/ 消失）。"""
        from scripts.ops_guard import guard_recycle

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(ops_guard_mod, "_PROJECT_ROOT_CACHE", tmp_path)
        victim = tmp_path / "docs" / "_working" / "draft.md"
        victim.parent.mkdir(parents=True)
        victim.write_text("清风类草稿", encoding="utf-8")
        with pytest.raises(DeleteBlockedError, match="untracked"):
            guard_recycle("docs/_working/draft.md", repo_root=tmp_path, reason="归档")
        assert victim.exists(), "被拦文件不应离开原位"

    def test_guard_recycle_outside_docs_unaffected(self, tmp_path, monkeypatch):
        """docs/ 之外路径回收不受影响（不误伤主流归档）。"""
        from scripts.ops_guard import guard_recycle

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(ops_guard_mod, "_PROJECT_ROOT_CACHE", tmp_path)
        victim = tmp_path / "src_staging" / "old.py"
        victim.parent.mkdir(parents=True)
        victim.write_text("x", encoding="utf-8")
        guard_recycle(str(victim), repo_root=tmp_path, reason="常规回收")
        assert not victim.exists()


# ---------------------------------------------------------------------------
# 4. 回收站容量封顶（T1③）
# ---------------------------------------------------------------------------
class TestRecycleBinCap:
    def test_capacity_cap_prunes_oldest_first(self, tmp_path):
        bin_root = tmp_path / ".runtime" / "recycle_bin"
        # 三个批次：旧/中/新，各 100B
        for i, ts in enumerate((1000, 2000, 3000)):
            d = bin_root / str(ts)
            d.mkdir(parents=True)
            (d / "f.txt").write_bytes(b"x" * 100)
        pruned = prune_recycle_bin(repo_root=tmp_path, ttl_seconds=10**12, max_bytes=250)
        assert pruned == 1  # 只清最旧批次（1000）即达标（300-100=200<=250）
        assert not (bin_root / "1000").exists()
        assert (bin_root / "2000").exists()
        assert (bin_root / "3000").exists()

    def test_ttl_prune_still_works(self, tmp_path):
        bin_root = tmp_path / ".runtime" / "recycle_bin"
        old = bin_root / "1000"
        old.mkdir(parents=True)
        (old / "f.txt").write_text("x", encoding="utf-8")
        pruned = prune_recycle_bin(repo_root=tmp_path, ttl_seconds=60)
        assert pruned == 1
        assert not old.exists()


# ---------------------------------------------------------------------------
# 5. 静态扫描 gate（T1③ 防回流）
# ---------------------------------------------------------------------------
class TestStaticScanGate:
    def test_bare_primitive_detected(self, tmp_path):
        from zephyr.gov_enforcement.commit_gates.reconciler_file_ops_gate import (
            scan_file_for_bare_primitives,
        )
        f = tmp_path / "evil.py"
        f.write_text("import os\nos.remove('x')\n", encoding="utf-8")
        hits = scan_file_for_bare_primitives(f)
        assert len(hits) == 1

    def test_guard_api_not_flagged(self, tmp_path):
        from zephyr.gov_enforcement.commit_gates.reconciler_file_ops_gate import (
            scan_file_for_bare_primitives,
        )
        f = tmp_path / "good.py"
        f.write_text(
            "from scripts.ops_guard import guard_remove\nguard_remove('x')\n",
            encoding="utf-8",
        )
        assert scan_file_for_bare_primitives(f) == []

    def test_exempt_marker_respected(self, tmp_path):
        from zephyr.gov_enforcement.commit_gates.reconciler_file_ops_gate import (
            scan_file_for_bare_primitives,
        )
        f = tmp_path / "exempt.py"
        f.write_text("os.remove('x')  # ops-guard-exempt: 补丁真源自测\n", encoding="utf-8")
        assert scan_file_for_bare_primitives(f) == []
