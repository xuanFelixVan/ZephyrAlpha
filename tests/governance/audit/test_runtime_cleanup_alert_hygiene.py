# [BLUEPRINT] MOD-GOV_AUDIT | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] tests.governance.audit.test_runtime_cleanup_alert_hygiene
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_AUDIT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_runtime_cleanup_alert_hygiene.py — TTL cleanup 告警卫生单测（T5，2026-08-14）

权威依据：reconciliation_registry.py make_runtime_cleanup_reconciler /
make_tmp_cleanup_reconciler（#ARCH-RECONCILER-AUTO-DELETE-GOV-001 裁定5）

裁定语义：锁定跳过=clean——PermissionError（WinError 32/5 文件被占用）
不计入 errors、不触发 warn；仅真异常（其他 OSError）计入 errors。
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    make_runtime_cleanup_reconciler,
)


def _make_gateway(project_root: Path) -> MagicMock:
    gw = MagicMock()
    gw.project_root = project_root
    return gw


def _make_stale_file(d: Path, name: str) -> Path:
    """造 mtime 超 7 天 TTL 的文件。"""
    d.mkdir(parents=True, exist_ok=True)
    f = d / name
    f.write_text("stale", encoding="utf-8")
    old = time.time() - 8 * 86400
    os.utime(f, (old, old))
    return f


class TestLockedSkipCleanSemantics:
    def test_locked_file_does_not_warn(self, tmp_path: Path, monkeypatch):
        """锁定文件（PermissionError）→ clean，locked_skipped 计数。"""
        _make_stale_file(tmp_path / ".runtime" / "handoffs", "old.md")
        monkeypatch.setattr(os, "remove", MagicMock(side_effect=PermissionError("file in use")))
        spec = make_runtime_cleanup_reconciler(_make_gateway(tmp_path))
        result = spec.reconcile([], "sess-t5")
        assert result.action == "clean"
        assert "errors=0" in result.detail
        assert "locked_skipped=1" in result.detail

    def test_genuine_error_still_warns(self, tmp_path: Path, monkeypatch):
        """真异常（非 PermissionError 的 OSError）→ warn 照常报（T5 不吞真告警）。"""
        _make_stale_file(tmp_path / ".runtime" / "handoffs", "old.md")
        monkeypatch.setattr(os, "remove", MagicMock(side_effect=OSError("disk io error")))
        spec = make_runtime_cleanup_reconciler(_make_gateway(tmp_path))
        result = spec.reconcile([], "sess-t5")
        assert result.action == "warn"
        assert "errors=1" in result.detail

    def test_normal_delete_clean(self, tmp_path: Path):
        """正常删除过期文件 → clean + deleted 计数。"""
        _make_stale_file(tmp_path / ".runtime" / "handoffs", "old.md")
        spec = make_runtime_cleanup_reconciler(_make_gateway(tmp_path))
        result = spec.reconcile([], "sess-t5")
        assert result.action == "clean"
        assert "deleted=1" in result.detail
        assert "errors=0" in result.detail


class TestPruneAndCap:
    """2026-09-02 挂死治本回归（pid 45476 实证）。"""

    def test_worktree_dirs_pruned(self, tmp_path: Path):
        """commit_queue/ 与 tmp/_wt_*/ 目录被剪枝——内部过期文件不被 TTL 删除（防腐蚀队列/隔离 worktree）。"""
        protected1 = _make_stale_file(tmp_path / ".runtime" / "commit_queue" / "worktree", "stale_in_queue.py")
        protected2 = _make_stale_file(tmp_path / ".runtime" / "tmp" / "_wt_demo", "stale_in_wt.py")
        _make_stale_file(tmp_path / ".runtime" / "handoffs", "old.md")
        spec = make_runtime_cleanup_reconciler(_make_gateway(tmp_path))
        result = spec.reconcile([], "sess-prune")
        assert "deleted=1" in result.detail
        assert protected1.exists(), "commit_queue/ 内文件不应被 TTL 清理"
        assert protected2.exists(), "tmp/_wt_*/ 内文件不应被 TTL 清理"

    def test_delete_cap_converges(self, tmp_path: Path):
        """单批删除上限 2000——大批量积压分批收敛，单次 reconcile 有界（防数小时阻塞）。"""
        d = tmp_path / ".runtime" / "handoffs"
        for i in range(2005):
            _make_stale_file(d, f"stale_{i}.md")
        spec = make_runtime_cleanup_reconciler(_make_gateway(tmp_path))
        result = spec.reconcile([], "sess-cap")
        assert "deleted=2000" in result.detail
        assert "capped_at=2000" in result.detail
        remaining = len(list(d.glob("stale_*.md")))
        assert remaining == 5
