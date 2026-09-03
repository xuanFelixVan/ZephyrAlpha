# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | docs/01_policies_and_standards/sop/industry_chain_data_audit_sop.md | §#ARCH-308 B1
# [A_module] module_id=MOD-GOV_DRIFT_WATCHDOG | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [MODULE] tests.scripts.test_classify_workspace_wip
# [DOMAIN] D_GOV_AUDIT
# [MATURITY] production
"""classify_workspace_wip 单元测试（#ARCH-308 B1 工作区脏文件判读器）。

覆盖：四分类核心判定（active_wip/runtime_telemetry/derived_sync/stale_rollback/
fresh_change/untracked）+ 自定义白名单 + auto-sync 降级。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "governance"))

import classify_workspace_wip as cw  # noqa: E402


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "dev")
    _git(
        repo,
        "-c",
        "user.email=t@t",
        "-c",
        "user.name=t",
        "-c",
        "core.autocrlf=false",
        "commit",
        "--allow-empty",
        "-q",
        "-m",
        "init",
    )
    for name in ("derived.yaml", "telemetry.jsonl", "plain.txt", "claimed.txt"):
        (repo / name).write_text(f"{name}-v1\n", encoding="utf-8")
        _git(repo, "add", name)
    _git(
        repo,
        "-c",
        "user.email=t@t",
        "-c",
        "user.name=t",
        "-c",
        "core.autocrlf=false",
        "commit",
        "-q",
        "-m",
        "add files",
    )
    return repo


@pytest.fixture
def allowlist(tmp_path: Path) -> Path:
    """自定义白名单：B 类精确路径 + C 类精确路径。"""
    p = tmp_path / "allowlist.yaml"
    p.write_text(
        "entries:\n"
        "  - path: derived.yaml\n"
        "    class: B\n"
        "  - path: telemetry.jsonl\n"
        "    class: C\n",
        encoding="utf-8",
    )
    return p


def _cat(result: dict, cat: str) -> list[str]:
    return [e["path"] for e in result["categories"][cat]]


def test_derived_sync_and_telemetry_classification(git_repo: Path, allowlist: Path) -> None:
    """B 类→derived_sync（非孤儿 WIP）；C 类→runtime_telemetry（存量债）。"""
    (git_repo / "derived.yaml").write_text("regen-v2\n", encoding="utf-8")
    (git_repo / "telemetry.jsonl").write_text("append\n", encoding="utf-8")
    result = cw.classify(git_repo, allowlist)
    assert _cat(result, cw.CAT_DERIVED_SYNC) == ["derived.yaml"]
    assert _cat(result, cw.CAT_RUNTIME_TELEMETRY) == ["telemetry.jsonl"]
    assert result["needs_attention"] == 0
    assert "孤儿WIP=0" in result["conclusion"]


def test_active_wip_priority(git_repo: Path, allowlist: Path, monkeypatch) -> None:
    """活跃会话 claim 优先于白名单分类。"""
    monkeypatch.setattr(
        cw, "_active_sessions_and_claims", lambda root: (["sess-x"], {"derived.yaml": "sess-x"})
    )
    (git_repo / "derived.yaml").write_text("wip\n", encoding="utf-8")
    result = cw.classify(git_repo, allowlist)
    assert _cat(result, cw.CAT_ACTIVE_WIP) == ["derived.yaml"]
    assert _cat(result, cw.CAT_DERIVED_SYNC) == []


def test_stale_vs_fresh_by_mtime(git_repo: Path, allowlist: Path) -> None:
    """非白名单 tracked 修改按 mtime vs HEAD 时间二分：陈旧回退 / 新鲜写入。"""
    (git_repo / "plain.txt").write_text("stale-content\n", encoding="utf-8")
    # mtime 拨回 HEAD 提交前 1 小时 → 陈旧回退
    old = os.path.getmtime(git_repo / "plain.txt") - 3600
    os.utime(git_repo / "plain.txt", (old, old))
    (git_repo / "claimed.txt").write_text("fresh-content\n", encoding="utf-8")
    result = cw.classify(git_repo, allowlist)
    assert _cat(result, cw.CAT_STALE_ROLLBACK) == ["plain.txt"]
    assert _cat(result, cw.CAT_FRESH_CHANGE) == ["claimed.txt"]
    assert result["needs_attention"] == 2


def test_untracked_classification(git_repo: Path, allowlist: Path) -> None:
    """untracked 新文件归 untracked_new 并计入需人工关注。"""
    (git_repo / "newfile.py").write_text("print('new')\n", encoding="utf-8")
    result = cw.classify(git_repo, allowlist)
    assert _cat(result, cw.CAT_UNTRACKED) == ["newfile.py"]
    assert result["needs_attention"] == 1


def test_auto_sync_category(git_repo: Path, allowlist: Path, monkeypatch) -> None:
    """auto-sync 产物清单命中 → auto_sync（非 WIP 噪音）。"""
    monkeypatch.setattr(cw, "_auto_sync_matcher", lambda: lambda p: p.startswith("derived.yaml"))
    (git_repo / "derived.yaml").write_text("x\n", encoding="utf-8")
    result = cw.classify(git_repo, allowlist)
    # B 类白名单优先于 auto-sync（derived.yaml 同时命中两者时归 B 类）
    assert _cat(result, cw.CAT_DERIVED_SYNC) == ["derived.yaml"]


def test_staged_flag(git_repo: Path, allowlist: Path) -> None:
    """staged 标记：index 有暂存内容的条目带 staged=True（A1 unstage 对象提示）。"""
    (git_repo / "plain.txt").write_text("staged-content\n", encoding="utf-8")
    _git(git_repo, "add", "plain.txt")
    result = cw.classify(git_repo, allowlist)
    entries = result["categories"][cw.CAT_FRESH_CHANGE]
    assert entries and entries[0]["staged"] is True


def test_json_output_smoke(git_repo: Path, allowlist: Path, capsys) -> None:
    """--json 机读输出冒烟（结构完整可序列化）。"""
    (git_repo / "plain.txt").write_text("v2\n", encoding="utf-8")
    rc = cw.main(["--root", str(git_repo), "--allowlist", str(allowlist), "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert "categories" in out and "conclusion" in out
