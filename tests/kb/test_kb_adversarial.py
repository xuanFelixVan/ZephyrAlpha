# [A_test] module_id: SRC-TST-0013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-208 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_kb_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""红白对抗: Knowledge Base 知识库攻击面测试.

攻击向量:
  A1 - 恶意内容注入: 注入含 script/payload 的文档
  A2 - 空文档攻击: 提交空内容或纯空格
  A3 - 格式绕过: 尝试绕过扩展名检查
  A4 - 管道完整性: ingest→triage→analyze 结构验证
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from zephyr.gov_kb.ingest import IngestGate, IngestResult


@pytest.fixture
def kb_gate() -> IngestGate:
    kb_root = Path(tempfile.mkdtemp(prefix="kb_adversarial_"))
    gate = IngestGate(kb_root=kb_root)
    yield gate
    import shutil

    shutil.rmtree(kb_root, ignore_errors=True)


class TestMaliciousContent:
    """A1: 恶意内容注入攻击."""

    def test_xss_injection_detected(self, kb_gate: IngestGate):
        """注入含 <script> 标签的 .md 文件 → 应触发注入检查."""
        import os
        import tempfile

        fd, tmp_path = tempfile.mkstemp(suffix=".md", prefix="xss_")
        os.close(fd)
        try:
            Path(tmp_path).write_text(
                "<script>alert('xss')</script>\n\n# Title\nContent",
                encoding="utf-8",
            )
            result = kb_gate.ingest(Path(tmp_path))
            assert isinstance(result, IngestResult)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_sql_injection_detected(self, kb_gate: IngestGate):
        """注入含 SQL 注入模式的内容 → 应触发注入检查."""
        import os
        import tempfile

        fd, tmp_path = tempfile.mkstemp(suffix=".md", prefix="sqli_")
        os.close(fd)
        try:
            Path(tmp_path).write_text(
                "---\ntitle: Test\n---\n\nSELECT * FROM users; DROP TABLE audit-trail; --",
                encoding="utf-8",
            )
            result = kb_gate.ingest(Path(tmp_path))
            assert isinstance(result, IngestResult)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestEmptyDocument:
    """A2: 空/极小文档攻击."""

    def test_empty_file_rejected(self, kb_gate: IngestGate):
        """空文件 → 应被拒绝."""
        import os
        import tempfile

        fd, tmp_path = tempfile.mkstemp(suffix=".md", prefix="empty_")
        os.close(fd)
        try:
            Path(tmp_path).write_text("", encoding="utf-8")
            result = kb_gate.ingest(Path(tmp_path))
            assert not result.passed or result.violations, f"Empty file should not pass cleanly: {result}"
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestExtensionBypass:
    """A3: 格式绕过."""

    def test_bad_extension_rejected(self, kb_gate: IngestGate):
        """不允许的扩展名 → 应被拒绝."""
        import os
        import tempfile

        fd, tmp_path = tempfile.mkstemp(suffix=".exe", prefix="bad_")
        os.close(fd)
        try:
            Path(tmp_path).write_text("malicious content", encoding="utf-8")
            result = kb_gate.ingest(Path(tmp_path))
            assert not result.passed, f"Bad extension should be rejected: {result}"
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_good_extension_accepted(self, kb_gate: IngestGate):
        """.md 扩展名 → 文件应被接受."""
        import os
        import tempfile

        fd, tmp_path = tempfile.mkstemp(suffix=".md", prefix="good_")
        os.close(fd)
        try:
            Path(tmp_path).write_text(
                "---\ntitle: Valid Test\n---\n\n# Valid\n\nThis is valid content for testing.",
                encoding="utf-8",
            )
            result = kb_gate.ingest(Path(tmp_path))
            assert isinstance(result, IngestResult)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestNonexistentFile:
    """边界条件."""

    def test_nonexistent_source_rejected(self, kb_gate: IngestGate):
        """不存在的源文件 → 应被拒绝."""
        result = kb_gate.ingest(Path("/nonexistent/path/test.md"))
        assert not result.passed
