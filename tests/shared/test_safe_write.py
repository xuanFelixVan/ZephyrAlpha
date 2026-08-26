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
    UnsafeDeleteRefused,
    assert_safe_rmtree_target,
    content_sha256,
    safe_rmtree,
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


# ── safe_rmtree 删除硬断言（CAND-GOVSEC-001 ① 红队用例）──────────────────────
# 事故型：2026-08-23 src/zephyr 2936 文件被物理删除（走未仪表化通道）。
# 以下用例模拟肇事指令形态，断言硬阻断生效且目标字节级完好。


@pytest.fixture
def drafts(repo: Path) -> Path:
    """伪 .aidrafts/：含一个合法 session worktree 目录。"""
    d = repo / ".aidrafts"
    (d / "sess-001" / "sub").mkdir(parents=True)
    (d / "sess-001" / "sub" / "f.txt").write_text("work\n", encoding="utf-8")
    return d


class TestSafeRmtree:
    """删除硬断言三件套：前缀逃逸阻断 / reparse point 阻断 / 正常删除放行。"""

    def test_dotdot_escape_refused(self, repo: Path, drafts: Path) -> None:
        """红队核心：session_id='../src' 型逃逸——resolve 后越出前缀，硬拒。"""
        src = repo / "src" / "zephyr"
        src.mkdir(parents=True)
        (src / "core.py").write_text("# 2936 files\n", encoding="utf-8")
        with pytest.raises(UnsafeDeleteRefused):
            safe_rmtree(drafts / ".." / "src", allowed_prefix=drafts)
        assert (src / "core.py").read_text(encoding="utf-8") == "# 2936 files\n"

    def test_prefix_itself_refused(self, drafts: Path) -> None:
        """删除允许前缀本身（等于而非严格在内）——硬拒。"""
        with pytest.raises(UnsafeDeleteRefused):
            safe_rmtree(drafts, allowed_prefix=drafts)
        assert (drafts / "sess-001").is_dir()

    def test_absolute_outside_prefix_refused(self, repo: Path, drafts: Path) -> None:
        """绝对路径指向前缀外——硬拒。"""
        outside = repo / "elsewhere"
        outside.mkdir()
        with pytest.raises(UnsafeDeleteRefused):
            safe_rmtree(outside, allowed_prefix=drafts)
        assert outside.is_dir()

    def test_normal_tree_deleted(self, drafts: Path) -> None:
        """合法目标正常删除（白名单路径无误伤）。"""
        assert safe_rmtree(drafts / "sess-001", allowed_prefix=drafts) is True
        assert not (drafts / "sess-001").exists()

    def test_nonexistent_idempotent(self, drafts: Path) -> None:
        """目标不存在 → False 幂等短路，不抛错。"""
        assert safe_rmtree(drafts / "sess-ghost", allowed_prefix=drafts) is False

    def test_single_file_deleted(self, drafts: Path) -> None:
        """单文件目标走 unlink 分支。"""
        f = drafts / "stray.txt"
        f.write_text("x\n", encoding="utf-8")
        assert safe_rmtree(f, allowed_prefix=drafts) is True
        assert not f.exists()

    def test_reparse_point_in_tree_refused(self, repo: Path, drafts: Path) -> None:
        """目标树内含 junction/symlink → 硬拒（Windows rmtree 穿透防目标被删）。"""
        import os
        import subprocess

        victim = repo / "victim"
        victim.mkdir()
        (victim / "important.py").write_text("# do not delete\n", encoding="utf-8")
        link = drafts / "sess-001" / "sub" / "evil_link"
        if os.name == "nt":
            r = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(victim)],
                capture_output=True,
            )
            if r.returncode != 0:
                pytest.skip("无法创建 junction（环境限制）")
        else:
            os.symlink(victim, link, target_is_directory=True)
        try:
            with pytest.raises(UnsafeDeleteRefused):
                safe_rmtree(drafts / "sess-001", allowed_prefix=drafts)
            # 阻断后两边都必须字节级完好
            assert (victim / "important.py").read_text(encoding="utf-8") == "# do not delete\n"
            assert (drafts / "sess-001" / "sub" / "f.txt").read_text(encoding="utf-8") == "work\n"
        finally:
            if os.name == "nt" and link.exists():
                os.rmdir(link)  # rmdir 删 junction 本体不触目标（避免 pytest 清理穿透）

    def test_assert_returns_resolved_path(self, repo: Path, drafts: Path) -> None:
        """assert_safe_rmtree_target 返回 resolve 后路径（调用方删返回值而非入参）。"""
        resolved = assert_safe_rmtree_target(drafts / "." / "sess-001", allowed_prefix=drafts)
        assert resolved == (drafts / "sess-001").resolve()

    def test_inprocess_patch_bypassed_after_assertion(self, repo: Path, drafts: Path, monkeypatch) -> None:
        """批5b 翻硬拦配套：硬断言通过=授权完成——safe_rmtree 直通 in-process 补丁。

        .worktrees 是 ops_guard 保护区：硬拦语义的补丁下裸 rmtree 必拦，而
        safe_rmtree（自带三件套的授权通道）必须直通成功不被自家补丁拦截；
        测试尾恢复 conftest 的 audit-only 观测补丁（观测面不缺口）。
        """
        import scripts.ops_guard as ops_guard_mod
        from scripts.ops_guard import (
            install_inprocess_enforcement,
            install_inprocess_enforcement_audit_only,
            uninstall_inprocess_enforcement,
        )

        wt = repo / ".worktrees" / "sess-x"
        (wt / "sub").mkdir(parents=True)
        (wt / "sub" / "f.txt").write_text("x\n", encoding="utf-8")
        monkeypatch.setattr(ops_guard_mod, "_PROJECT_ROOT_CACHE", repo)
        monkeypatch.delenv(ops_guard_mod.AUDIT_ONLY_ENV, raising=False)  # 硬拦语义
        try:
            install_inprocess_enforcement()
            assert safe_rmtree(wt, allowed_prefix=repo / ".worktrees") is True
            assert not wt.exists(), "授权通道（硬断言通过）必须直通不被补丁拦截"
        finally:
            uninstall_inprocess_enforcement()
            install_inprocess_enforcement_audit_only()  # 恢复 conftest 观测面

    def test_authorized_delete_audited(self, repo: Path, drafts: Path, monkeypatch) -> None:
        """批5c：safe_rmtree 授权通道删除落 safe_rmtree.jsonl——直通期间补丁审计
        短路，本层补痕（删除必有痕原则不缺口）。"""
        import json as _json

        import scripts.ops_guard as ops_guard_mod

        monkeypatch.setattr(ops_guard_mod, "_PROJECT_ROOT_CACHE", repo)
        assert safe_rmtree(drafts / "sess-001", allowed_prefix=drafts) is True
        audit = repo / ".runtime" / "gate_audit" / "safe_rmtree.jsonl"
        assert audit.exists(), "授权通道删除未留痕（删除必有痕原则缺口）"
        rows = [_json.loads(ln) for ln in audit.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert any(r.get("event") == "safe_rmtree" and "sess-001" in r.get("target", "") for r in rows)
