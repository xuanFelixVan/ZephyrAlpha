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
