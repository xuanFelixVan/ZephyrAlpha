# [BLUEPRINT] MOD-INF-016 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.shared.test_safe_write
# [DOMAIN] D_SHARED
# [MATURITY] production
# [TTL] permanent
"""safe_write_text CAS 写入工具测试（#ARCH-WORKTREE-WRITE-INTEGRITY-001 P2）。

覆盖：热文件无 base 拒写 / 陈旧 base 拒写 / 正确 base 放行 / 非热文件可选 base /
写后回读校验 / 审计留痕（拒写+成功均落 jsonl）。
真源=file_utils.py（atomic_write_protocol canonical，CREATE-GUARD 裁定扩展而非新建）。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.shared.io.file_utils import (
    StaleWriteRefused,
    content_sha256,
    safe_write_text,
)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """伪仓根：含热文件 AGENTS.md + 普通文件。"""
    (tmp_path / "AGENTS.md").write_text("# rules v1\n", encoding="utf-8")
    (tmp_path / "plain.txt").write_text("p1\n", encoding="utf-8")
    return tmp_path


def _audit_rows(root: Path) -> list[dict]:
    p = root / ".runtime" / "audit" / "safe_write.jsonl"
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def test_hot_file_without_base_refused(repo: Path) -> None:
    with pytest.raises(StaleWriteRefused):
        safe_write_text(repo / "AGENTS.md", "# hijack\n", repo_root=repo)
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == "# rules v1\n"
    rows = _audit_rows(repo)
    assert any(r["event"] == "refused" and r["reason"] == "hot_file_without_base" for r in rows)


def test_hot_file_stale_base_refused(repo: Path) -> None:
    """base 与磁盘不符（他人已推进）→ 拒写不吞改。"""
    stale = content_sha256("# outdated\n")
    with pytest.raises(StaleWriteRefused):
        safe_write_text(repo / "AGENTS.md", "# hijack\n", expected_base_sha256=stale, repo_root=repo)
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == "# rules v1\n"
    rows = _audit_rows(repo)
    assert any(r["event"] == "refused" and r["reason"] == "stale_base" for r in rows)


def test_hot_file_correct_base_written(repo: Path) -> None:
    base = content_sha256("# rules v1\n")
    result = safe_write_text(repo / "AGENTS.md", "# rules v2\n", expected_base_sha256=base, repo_root=repo)
    assert result.written
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == "# rules v2\n"
    assert result.before_sha256 == base
    assert result.after_sha256 == content_sha256("# rules v2\n")
    rows = _audit_rows(repo)
    assert any(r["event"] == "written" for r in rows)


def test_non_hot_file_optional_base(repo: Path) -> None:
    """非热文件：无 base 直接写；带正确 base 也写。"""
    r1 = safe_write_text(repo / "plain.txt", "p2\n", repo_root=repo)
    assert r1.written
    r2 = safe_write_text(repo / "plain.txt", "p3\n", expected_base_sha256=content_sha256("p2\n"), repo_root=repo)
    assert r2.written
    assert (repo / "plain.txt").read_text(encoding="utf-8") == "p3\n"


def test_non_hot_file_stale_base_refused(repo: Path) -> None:
    """非热文件给了 base 就校验——陈旧同样拒写。"""
    with pytest.raises(StaleWriteRefused):
        safe_write_text(repo / "plain.txt", "pX\n", expected_base_sha256=content_sha256("other\n"), repo_root=repo)
    assert (repo / "plain.txt").read_text(encoding="utf-8") == "p1\n"


def test_write_then_reread_consistency(repo: Path) -> None:
    """回读校验：落盘内容与新内容逐字节一致。"""
    content = "# 中文内容混合 ascii 12345\n" * 100
    safe_write_text(repo / "plain.txt", content, repo_root=repo)
    assert (repo / "plain.txt").read_text(encoding="utf-8") == content
