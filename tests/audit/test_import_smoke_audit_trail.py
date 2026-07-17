# [A_test] module_id: SRC-TST-1825 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-455 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.audit_trail.test_import_smoke
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""audit-trail MOD-INF-020 import 冒烟测试 — 验证核心模块可被导入."""

import sys
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT
_PROJECT_ROOT = REPO_ROOT
_SRC_DIR = _PROJECT_ROOT / "src"


def _ensure_path() -> None:
    src_str = str(_SRC_DIR)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


class TestAuditTrailImportSmoke:
    """验证 audit-trail 核心模块可以被成功导入."""

    def test_import_audit_trail_init(self) -> None:
        """测试导入 zephyr.gov_audit 包自身."""
        _ensure_path()
        import zephyr.gov_audit

        assert hasattr(zephyr.gov_audit, "__all__")

    def test_import_models(self) -> None:
        """Can import AuditEntryV1, AuditEventType, LamportClock from audit-trail.models."""
        _ensure_path()
        from zephyr.gov_audit.models import AuditEntryV1, AuditEventType, LamportClock, ProvenanceLevel

        assert AuditEntryV1
        assert AuditEventType
        assert LamportClock
        assert ProvenanceLevel

    def test_import_writer(self) -> None:
        """测试导入 AuditWriter — 不可变审计写入器."""
        _ensure_path()
        from zephyr.gov_audit.writer import AuditWriter

        assert AuditWriter is not None

    def test_import_integrity(self) -> None:
        """测试导入 IntegrityVerifier — 链式完整性验证."""
        _ensure_path()
        from zephyr.gov_audit.integrity import IntegrityVerifier

        assert IntegrityVerifier is not None

    def test_import_agent_signer(self) -> None:
        """测试导入 AgentSigner — Ed25519密码学签名."""
        _ensure_path()
        from zephyr.gov_audit.agent_signer import AgentSigner

        assert AgentSigner is not None

    def test_import_query(self) -> None:
        """测试导入 AuditQuery — 审计查询接口."""
        _ensure_path()
        from zephyr.gov_audit.query import AuditQuery

        assert AuditQuery is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
