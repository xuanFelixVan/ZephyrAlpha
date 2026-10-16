# [MODULE] tests.scripts.test_archive_sanitize
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] scripts.ops.archive_sanitize (被测), scripts.git_commit (写面接线), pytest.MonkeyPatch
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] volatile
# [INVARIANTS] 全部在 tmp 目录/仓；三类变换实测（doc_type 改名/ttl 置 permanent/键名→Marker）；
#              frontmatter 域界（正文 doc_type/ttl 不动）；键名常量真源命中（DENY_ENV_PATTERNS）；
#              remaining_markers 如实上报；写面自动档 env 回滚通道实测
# [STABILITY] volatile
# [SAFETY] L
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_archive_sanitize.py — D4 归档写面前置脱敏单测（st-diskp0-20261015）。

测试组:
- test_three_transforms: ①doc_type→archived_doc_type ②ttl 非 permanent→permanent ③键名→Marker
- test_frontmatter_scope_only: 正文 doc_type/ttl 行不触碰（域界）
- test_body_key_names_redacted: 正文键名（22 件实锤位）同样归一
- test_remaining_markers_reported: 已含裸 Marker 如实上报（不伪造已脱敏）
- test_ttl_comment_preserved_and_permanent_untouched: 值 token 替换保留行尾注释；permanent 原样
- test_sanitize_paths_execute_on_dir: 目录批量 + --execute 落盘
- test_git_commit_writeface_autosanitize: git_commit 写面自动档（变换+git add 重暂存）与 env 回滚
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _load(name: str, rel: str, monkeypatch: pytest.MonkeyPatch | None = None):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def san(monkeypatch: pytest.MonkeyPatch):
    return _load("archive_sanitize_under_test", "ops/archive_sanitize.py", monkeypatch)


_DOC = """---
doc_type: report
ttl: task_bound
owner: someone
---

# Body: 入口只读 [REDACTED:REAL_KEY_NAME]_ACCOUNT(8887871)
row: ZEPHYR_AUDIT_HMAC_SECRET 与 FOO_LIVE_BAR 两个字样
doc_type: keep_me
ttl: keep_me
"""


def test_three_transforms(san):
    """①doc_type 改名 ②ttl→permanent ③键名→Marker（含 marker+后缀 归一）。"""
    new, st = san.sanitize_archive_text(_DOC, is_markdown=True)
    assert "archived_doc_type: report" in new and "\ndoc_type: report" not in new
    assert "ttl: permanent" in new
    assert "ZEPHYR_AUDIT_HMAC_SECRET" not in new, "HMAC 键名应被脱敏"
    assert "FOO_LIVE_BAR" not in new, "*_LIVE_* 族应被脱敏"
    assert "[REDACTED:REAL_KEY_NAME]_ACCOUNT" not in new, "Marker+后缀应归一为裸 Marker"
    assert st["doc_type_renamed"] == 1 and st["ttl_permanent"] == 1 and st["keys_redacted"] == 3


def test_frontmatter_scope_only(san):
    """①②只动 frontmatter：正文里的 doc_type:/ttl: 行保持原样。"""
    new, _st = san.sanitize_archive_text(_DOC, is_markdown=True)
    body = new.split("---", 2)[2]
    assert "doc_type: keep_me" in body and "ttl: keep_me" in body


def test_body_key_names_redacted(san):
    """正文键名归一（REAL-KEY-REFERENCE-SCAN 扫全文，body 是实锤病灶位）。"""
    doc = "no frontmatter, body-only note about FOO_LIVE_BAR\n"
    new, st = san.sanitize_archive_text(doc, is_markdown=True)
    assert "FOO_LIVE_BAR" not in new and st["keys_redacted"] == 1


def test_remaining_markers_reported(san):
    """变换后仍含裸 Marker → remaining_markers 如实计数（Owner 准入面）。"""
    new, st = san.sanitize_archive_text(_DOC, is_markdown=True)
    assert st["remaining_markers"] == 3, st


def test_ttl_comment_preserved_and_permanent_untouched(san):
    """ttl 值替换保留行尾注释；permanent 原样不重写。"""
    doc = "---\nttl: task_bound  # 2026-09-01 起\nttl2: permanent\n---\nbody\n"
    new, st = san.sanitize_archive_text(doc, is_markdown=True)
    assert "ttl: permanent  # 2026-09-01 起" in new, "行尾注释必须保留"
    assert st["ttl_permanent"] == 1
    doc2 = "---\nttl: permanent\n---\nbody\n"
    new2, st2 = san.sanitize_archive_text(doc2, is_markdown=True)
    assert st2["ttl_permanent"] == 0 and new2 is doc2, "permanent 不动且零变化恒等返回"


def test_sanitize_paths_execute_on_dir(san, tmp_path: Path):
    """目录批量：dry-run 零写盘；--execute 落盘且 yaml 后缀也进扫。"""
    d = tmp_path / "docs" / "_archive" / "batch"
    d.mkdir(parents=True)
    (d / "a.md").write_text(_DOC, encoding="utf-8")
    (d / "b.yaml").write_text("---\ndoc_type: x\nttl: task_bound\n---\n", encoding="utf-8")
    reports, rc = san.sanitize_paths([d], execute=False)
    assert rc == 0 and len(reports) == 2
    assert all(not r["changed"] or not r.get("write_failed") for r in reports)
    assert "doc_type: report" in (d / "a.md").read_text(encoding="utf-8"), "dry-run 不写盘"
    reports2, rc2 = san.sanitize_paths([d], execute=True)
    assert rc2 == 0
    assert "archived_doc_type: report" in (d / "a.md").read_text(encoding="utf-8")
    assert "ttl: permanent" in (d / "b.yaml").read_text(encoding="utf-8")


def test_git_commit_writeface_autosanitize(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """写面自动档：docs/_archive 件提交前被变换并重暂存；env=0 回滚通道放行原文。"""
    gc = _load("git_commit_under_test", "git_commit.py")
    repo = tmp_path / "repo"
    repo.mkdir()

    def _git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)

    assert _git("init").returncode == 0
    _git("config", "user.email", "t@l")
    _git("config", "user.name", "t")
    zone = repo / "docs" / "_archive"
    zone.mkdir(parents=True)
    f = zone / "a.md"
    f.write_text("---\ndoc_type: report\nttl: task_bound\n---\nbody\n", encoding="utf-8")
    _git("add", "-A")
    _git("commit", "-m", "init")
    # 自动档：变换 + git add 重暂存
    gc._sanitize_archive_zone_files(["docs/_archive/a.md"], str(repo))
    text = f.read_text(encoding="utf-8")
    assert "archived_doc_type: report" in text and "ttl: permanent" in text
    staged = _git("diff", "--cached", "--unified=0")
    assert "archived_doc_type" in staged.stdout, "变换后必须重暂存（门禁看 staged 面）"
    # 回滚通道：env=0 → 原文不动
    f.write_text("---\ndoc_type: report\nttl: task_bound\n---\nbody\n", encoding="utf-8")
    monkeypatch.setenv("ZEPHYR_ARCHIVE_SANITIZE", "0")
    gc._sanitize_archive_zone_files(["docs/_archive/a.md"], str(repo))
    assert "archived_doc_type" not in f.read_text(encoding="utf-8"), "env=0 必须停用自动档"
