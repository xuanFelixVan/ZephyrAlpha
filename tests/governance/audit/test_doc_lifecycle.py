# [BLUEPRINT] MOD-GOV_TEST_DOC_LIFECYCLE | tests/governance/audit/test_doc_lifecycle.py | §
# [MODULE] tests.governance.audit.test_doc_lifecycle
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.doc_lifecycle; scripts/ops_guard.py
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 临时目录隔离；不触碰真实 docs/_working；回收站动作在 tmp repo 内验证
# [MODIFY-GUARD] 状态机转移参数变更需同步 doc_lifecycle.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [A_module] module_id=MOD-GOV_TEST_DOC_LIFECYCLE | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_doc_lifecycle.py — 文档生命周期状态机测试（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）

覆盖：路径分级 / permanent 豁免 / watch 进入 / 复活 / 宽限期归档 /
回收站可恢复 / 零物理删除 / 清单持久化 / 回收站到期清理。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest


@pytest.fixture
def tmp_repo(tmp_path):
    """临时仓库：docs/_working + .runtime 骨架。"""
    repo = tmp_path / "repo"
    (repo / "docs" / "_working").mkdir(parents=True)
    (repo / ".runtime").mkdir()
    return repo


def _write_doc(repo: Path, rel: str, body: str, *, ttl: str | None = "task_bound") -> Path:
    """写测试文档（可选 frontmatter ttl）。"""
    p = repo / "docs" / "_working" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    fm = f"---\nttl: {ttl}\n---\n" if ttl else ""
    p.write_text(fm + body, encoding="utf-8")
    return p


def _evaluate(repo: Path, now: int | None = None):
    from zephyr.governance.audit.doc_lifecycle import evaluate_lifecycle

    return evaluate_lifecycle(repo, now=now)


class TestPathClassification:
    """路径分级：短命路径断裂不算死亡证据。"""

    def test_ephemeral_prefixes(self):
        from zephyr.governance.audit.doc_lifecycle import classify_path

        assert classify_path(".worktrees/AI-X/scripts/foo.py") == "ephemeral"
        assert classify_path(".runtime/tmp/bar.md") == "ephemeral"
        assert classify_path("data/audit_logs/x.jsonl") == "ephemeral"
        assert classify_path(".aidrafts/sess-1/a.py") == "ephemeral"

    def test_ephemeral_regex_swallowed_compat(self):
        """吞噬形态兼容：正则首字符限字母会把 .runtime/ 吞成 runtime/（第三轮统筹实证）。"""
        from zephyr.governance.audit.doc_lifecycle import classify_path

        assert classify_path("runtime/tmp/bar.md") == "ephemeral"
        assert classify_path("worktrees/AI-X/s.py") == "ephemeral"
        assert classify_path("aidrafts/sess-1/a.py") == "ephemeral"
        # 不误伤嵌套合法路径
        assert classify_path("src/zephyr/runtime/x.py") == "durable"

    def test_durable_prefixes(self):
        from zephyr.governance.audit.doc_lifecycle import classify_path

        assert classify_path("src/zephyr/foo.py") == "durable"
        assert classify_path("docs/01_policies/x.md") == "durable"
        assert classify_path("scripts/governance/y.py") == "durable"

    def test_extract_refs_dedup(self):
        from zephyr.governance.audit.doc_lifecycle import extract_refs

        content = "见 [文档](docs/a/b.md) 和 `scripts/x.py`，重复 docs/a/b.md 再 docs/a/b.md"
        refs = extract_refs(content)
        assert refs.count("docs/a/b.md") == 1
        assert "scripts/x.py" in refs


class TestWatchlistMechanics:
    """状态机转移。"""

    def test_permanent_never_watched(self, tmp_repo):
        """ttl: permanent 文档即使引用全断也不进观察。"""
        _write_doc(
            tmp_repo,
            "policy.md",
            "引用不存在 src/no/such/file.py 和 docs/no/such.md",
            ttl="permanent",
        )
        r = _evaluate(tmp_repo)
        assert r.watched == []
        assert r.skipped_permanent == 1
        from zephyr.governance.audit.doc_lifecycle import load_watchlist

        assert load_watchlist(tmp_repo) == {}

    def test_durable_ghost_enters_watch(self, tmp_repo):
        """task_bound + durable 失效引用 → 进观察，文件原地不动。"""
        doc = _write_doc(tmp_repo, "analysis.md", "分析见 src/gone/module.py 的结论")
        r = _evaluate(tmp_repo)
        assert r.watched == ["docs/_working/analysis.md"]
        assert doc.exists(), "观察期文件必须原地不动"
        assert r.archived == []

    def test_ephemeral_ghost_not_watched(self, tmp_repo):
        """只引用短命路径（.worktrees/.runtime）断裂 → 不进观察（tracker 类文档保护）。"""
        _write_doc(
            tmp_repo,
            "tracker.md",
            "merge 自 .worktrees/AI-GIT-001 完成，快照在 .runtime/quarantine/x.bundle",
        )
        r = _evaluate(tmp_repo)
        assert r.watched == [], "短命路径断裂不得作为死亡证据"

    def test_revival_on_edit(self, tmp_repo):
        """观察期内文档被编辑（mtime 前移）→ 自动复活出清单。"""
        doc = _write_doc(tmp_repo, "doc.md", "引用 src/gone/x.py")
        r1 = _evaluate(tmp_repo)
        assert r1.watched != []
        # 模拟编辑：mtime 前移
        time.sleep(0.02)
        doc.write_text("---\nttl: task_bound\n---\n引用 src/gone/x.py（已更新）", encoding="utf-8")
        os.utime(doc, (time.time() + 5, time.time() + 5))
        r2 = _evaluate(tmp_repo)
        assert r2.revived == ["docs/_working/doc.md"]
        from zephyr.governance.audit.doc_lifecycle import load_watchlist

        assert load_watchlist(tmp_repo) == {}

    def test_revival_on_ghost_cleared(self, tmp_repo):
        """失效引用恢复存在 → 复活。"""
        _write_doc(tmp_repo, "doc.md", "引用 src/exists/x.py")
        _evaluate(tmp_repo)
        # 引用目标出现
        target = tmp_repo / "src" / "exists" / "x.py"
        target.parent.mkdir(parents=True)
        target.write_text("x=1", encoding="utf-8")
        r2 = _evaluate(tmp_repo)
        assert r2.revived == ["docs/_working/doc.md"]

    def test_archive_after_grace(self, tmp_repo):
        """满 7 天宽限 → 归档进回收站，工作区文件消失但可回收。"""
        doc = _write_doc(tmp_repo, "dead.md", "引用 src/gone/x.py")
        t0 = int(time.time())
        _evaluate(tmp_repo, now=t0)
        # 7 天 + 1 秒后仍未复活
        r = _evaluate(tmp_repo, now=t0 + 7 * 24 * 3600 + 1)
        assert r.archived == ["docs/_working/dead.md"]
        assert not doc.exists(), "归档后工作区文件移走"
        # 回收站可恢复实证
        bin_root = tmp_repo / ".runtime" / "recycle_bin"
        assert bin_root.is_dir()
        recycled = list(bin_root.rglob("dead.md"))
        assert len(recycled) == 1, "回收站必须保留原文件（30 天可恢复）"

    def test_no_archive_before_grace(self, tmp_repo):
        """宽限期内不归档。"""
        _write_doc(tmp_repo, "alive.md", "引用 src/gone/x.py")
        t0 = int(time.time())
        _evaluate(tmp_repo, now=t0)
        r = _evaluate(tmp_repo, now=t0 + 6 * 24 * 3600)  # 6 天
        assert r.archived == []
        assert (tmp_repo / "docs" / "_working" / "alive.md").exists()

    def test_healthy_doc_untouched(self, tmp_repo):
        """健康文档（引用都存在）不进任何流程。"""
        real = tmp_repo / "docs" / "real.md"
        real.write_text("x", encoding="utf-8")
        _write_doc(tmp_repo, "ok.md", "引用 docs/real.md")
        r = _evaluate(tmp_repo)
        assert r.watched == [] and r.archived == []


class TestRecycleBin:
    """回收站语义。"""

    def test_prune_after_30_days(self, tmp_repo):
        """回收站 30 天到期物理删除（唯一合法物理删除点）。"""
        from scripts.ops_guard import guard_recycle, prune_recycle_bin

        doc = _write_doc(tmp_repo, "old.md", "内容")
        recycled_rel = guard_recycle(doc, repo_root=tmp_repo, reason="测试")
        assert not doc.exists()
        # 篡改回收站目录时间戳为 31 天前
        ts_dir = next((tmp_repo / ".runtime" / "recycle_bin").iterdir())
        old_name = ts_dir.name
        aged = ts_dir.parent / str(int(old_name) - 31 * 24 * 3600)
        ts_dir.rename(aged)
        n = prune_recycle_bin(repo_root=tmp_repo)
        assert n == 1
        assert not aged.exists(), "到期条目物理清除"

    def test_no_prune_within_30_days(self, tmp_repo):
        from scripts.ops_guard import guard_recycle, prune_recycle_bin

        doc = _write_doc(tmp_repo, "fresh.md", "内容")
        guard_recycle(doc, repo_root=tmp_repo, reason="测试")
        n = prune_recycle_bin(repo_root=tmp_repo)
        assert n == 0


class TestWatchlistPersistence:
    """清单 SSoT 读写。"""

    def test_roundtrip(self, tmp_repo):
        from zephyr.governance.audit.doc_lifecycle import (
            WatchEntry,
            load_watchlist,
            save_watchlist,
        )

        entries = {
            "docs/_working/a.md": WatchEntry(
                state="watch",
                first_seen=1000,
                baseline_mtime=900.0,
                last_checked=1000,
                ghost_refs=["src/x.py"],
                reason="t",
            )
        }
        save_watchlist(tmp_repo, entries)
        loaded = load_watchlist(tmp_repo)
        assert loaded["docs/_working/a.md"].first_seen == 1000
        assert loaded["docs/_working/a.md"].ghost_refs == ["src/x.py"]

    def test_corrupt_watchlist_failopen(self, tmp_repo):
        p = tmp_repo / ".runtime" / "archive_watchlist.json"
        p.write_text("{broken json", encoding="utf-8")
        from zephyr.governance.audit.doc_lifecycle import load_watchlist

        assert load_watchlist(tmp_repo) == {}

    def test_undeclared_ttl_treated_as_watchable(self, tmp_repo):
        """无 frontmatter 文档（undeclared）按 task_bound 语义可进观察。"""
        _write_doc(tmp_repo, "bare.md", "引用 src/gone/x.py", ttl=None)
        r = _evaluate(tmp_repo)
        assert r.watched == ["docs/_working/bare.md"]
