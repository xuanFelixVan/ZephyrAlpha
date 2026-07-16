# PURE-ASSERTION Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 注册 PURE-ASSERTION commit gate (priority=69)，对项目 .md 文档增量阻断纯陈述原则违规（GOV-DOC-016），配套 --full-scan 一次性清理现存违规。

**Architecture:** SSoT checker `check_pure_assertion.py` 持有检测逻辑（6 条 regex + scope 过滤 + frontmatter/code-block 跳过）+ 双模式（`--ci <files>` 供 gate subprocess 调用 / `--full-scan` 供审计）。Gate 薄壳 `pure_assertion_gate.py` subprocess 调 checker，解析 exit code，fail-open/fail-closed（对标 PURE-SHIM 模式）。

**Tech Stack:** Python 3.11+, stdlib only (re, os, subprocess, argparse, pathlib), pytest

**Design doc:** `docs/_working/pure_assertion_gate_design.md` (commit `3eb2b272b7`)

---

## File Structure

| 动作 | 文件 | 责任 |
|------|------|------|
| Create | `scripts/governance/d3_metadata/check_pure_assertion.py` | SSoT checker：6 regex + scope + 结构区跳过 + `--ci`/`--full-scan` 双模式 |
| Create | `src/zephyr/gov_enforcement/commit_gates/pure_assertion_gate.py` | Gate 薄壳：subprocess 调 checker，fail-open/fail-closed |
| Create | `tests/governance/d3_metadata/test_check_pure_assertion.py` | checker 检测逻辑测试（12 用例） |
| Create | `tests/governance/commit_gates/test_pure_assertion_gate.py` | gate 闭包测试（8 用例） |
| Modify | `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py` L88, L308 | 注册 gate（import + register） |

---

## Task 1: SSoT checker 核心——scope 过滤 + 6 条 regex + _check_file

**Files:**
- Create: `scripts/governance/d3_metadata/check_pure_assertion.py`
- Test: `tests/governance/d3_metadata/test_check_pure_assertion.py`

- [ ] **Step 1: 写失败测试（scope + regex + 结构区跳过）**

```python
# tests/governance/d3_metadata/test_check_pure_assertion.py
"""test_check_pure_assertion.py — check_pure_assertion.py 检测逻辑测试。"""
import os
import sys
import importlib.util

# 加载 scripts/ 下的 checker（不可从 src/ import）
_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)
    )))),
    "scripts", "governance", "d3_metadata", "check_pure_assertion.py",
)
_spec = importlib.util.spec_from_file_location("check_pure_assertion", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def test_is_in_scope_include_dirs():
    assert _mod._is_in_scope("docs/03_modules/gov_engine/blueprint.md")
    assert _mod._is_in_scope(".trae/rules/onboarding_detail.md")
    assert _mod._is_in_scope("docs/01_policies_and_standards/standards/naming.md")


def test_is_in_scope_include_files():
    assert _mod._is_in_scope("AGENTS.md")
    assert _mod._is_in_scope("README.md")


def test_is_in_scope_exclude_dirs():
    assert not _mod._is_in_scope("docs/_working/temp.md")
    assert not _mod._is_in_scope("docs/_archive/old.md")
    assert not _mod._is_in_scope("docs/01_policies_and_standards/rules/trae_030.md")


def test_is_in_scope_exclude_files():
    assert not _mod._is_in_scope("docs/02_enterprise_architecture/architecture_debt_registry.md")


def test_is_in_scope_exclude_basenames():
    assert not _mod._is_in_scope("docs/03_modules/CHANGELOG.md")
    assert not _mod._is_in_scope("CHANGELOG.md")


def test_is_in_scope_non_md():
    assert not _mod._is_in_scope("scripts/governance/d3_metadata/check_pure_assertion.py")


def test_check_file_violation_regex1():
    """已废止/已废弃/已弃用"""
    v = _mod._check_file("这是已废止的规则。\n", None)
    assert len(v) == 1 and "已废止" in v[0]


def test_check_file_violation_regex3():
    """之前是X现在改为Y"""
    v = _mod._check_file("之前是手动触发，现在是自动触发。\n", None)
    assert len(v) == 1 and "之前是" in v[0]


def test_check_file_violation_regex6():
    """从X迁移到Y"""
    v = _mod._check_file("从旧路径迁移到新路径。\n", None)
    assert len(v) == 1 and "迁移" in v[0]


def test_check_file_skip_frontmatter():
    content = "---\ntitle: 已废止的旧规则\n---\n正文无违规。\n"
    assert _mod._check_file(content, None) == []


def test_check_file_skip_code_block():
    content = "正文无违规。\n```\n已废止的示例\n```\n正文也无违规。\n"
    assert _mod._check_file(content, None) == []


def test_check_file_incremental_added_lines():
    """只检 added_lines 指定的行"""
    content = "已废止的旧行。\n这行是新增的已废止。\n"
    v = _mod._check_file(content, {2})  # 只检第 2 行
    assert len(v) == 1 and "新增" in v[0]


def test_check_file_no_violation():
    assert _mod._check_file("这是当前有效的规则。\n", None) == []
```

- [ ] **Step 2: 运行测试确认失败**

Run: `$env:PYTHONPATH="src"; python -m pytest tests/governance/d3_metadata/test_check_pure_assertion.py -v`
Expected: FAIL (ModuleNotFoundError / 文件不存在)

- [ ] **Step 3: 实现 checker 核心检测逻辑**

```python
# scripts/governance/d3_metadata/check_pure_assertion.py
# [MODULE] scripts.governance.d3_metadata.check_pure_assertion
# [DOMAIN] D_GOV_DOC_QUALITY
# [DEPENDENCIES] —
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.pure_assertion_gate (subprocess --ci)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] GOV-DOC-016 纯陈述原则检测真源——6 条 regex 检测"过去态"过渡文本；只检 .md 文件（YAML 规则由 rules_integrity_reconciler 负责）；跳过 frontmatter + 代码块避免误报；--ci 模式只检 added 行（增量），--full-scan 模式检全行；exit 0=clean, 1=violations, 2=error
# [TTL] permanent
"""check_pure_assertion.py — GOV-DOC-016 纯陈述原则检测真源（SSoT）。

检测 .md 文档中的"过去态"过渡文本（如"已废止""之前是X现在改为Y"），
正文只应承载当前真实值，历史差异是 git log 的职责。

双模式：
  --ci <files>      供 pure_assertion_gate.py subprocess 调用（增量 added 行）
  --full-scan       供一次性审计（全量扫描所有 in-scope .md）

Exit codes: 0=clean, 1=violations found, 2=script error
"""

from __future__ import annotations

import re

# Exit codes
EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2

# 6 条违规 regex（从 cde1255c^ 恢复，原版词表）
_VIOLATION_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"已[废止弃]\w*"), "已废止/已废弃/已弃用"),
    (re.compile(r"旧[定规]义?[则]?"), "旧定义/旧规则"),
    (re.compile(r"之前是.{1,30}现在"), "之前是X现在改为Y"),
    (re.compile(r"已被取[代替]"), "已被取代/已被替代"),
    (re.compile(r"P[0-9]迁移后"), "P2迁移后"),
    (re.compile(r"从.{1,30}迁移(至|到)"), "从X迁移到Y"),
]

# Scope：INCLUDE 目录前缀
_SCOPE_INCLUDE_DIRS = [
    ".trae/rules/",
    "docs/01_policies_and_standards/",
    "docs/02_enterprise_architecture/",
    "docs/03_modules/",
    "docs/08_knowledge/",
]

# Scope：INCLUDE 精确文件
_SCOPE_INCLUDE_FILES = [
    "AGENTS.md",
    "README.md",
]

# Scope：EXCLUDE 目录前缀（即使命中 INCLUDE 也跳过）
_SCOPE_EXCLUDE_DIRS = [
    "docs/_archive/",
    "docs/_working/",
    "session_logs/",
    "docs/03_governance_reports/",
    "docs/01_policies_and_standards/rules/",
]

# Scope：EXCLUDE 精确文件
_SCOPE_EXCLUDE_FILES = [
    "docs/02_enterprise_architecture/architecture_debt_registry.md",
]

# Scope：EXCLUDE basename（任意层级匹配）
_SCOPE_EXCLUDE_BASENAMES = [
    "CHANGELOG.md",
]


def _is_in_scope(rel_path: str) -> bool:
    """判定 .md 文件是否在 PURE-ASSERTION gate 检测范围内。

    Args:
        rel_path: 相对项目根的路径（正斜杠）。

    Returns:
        True 若 in-scope（INCLUDE 命中且 EXCLUDE 未命中）。
    """
    rel_path = rel_path.replace("\\", "/")
    if not rel_path.endswith(".md"):
        return False
    # EXCLUDE 优先
    for excl_dir in _SCOPE_EXCLUDE_DIRS:
        if rel_path.startswith(excl_dir):
            return False
    for excl_file in _SCOPE_EXCLUDE_FILES:
        if rel_path == excl_file:
            return False
    basename = rel_path.rsplit("/", 1)[-1]
    for excl_bn in _SCOPE_EXCLUDE_BASENAMES:
        if basename == excl_bn:
            return False
    # INCLUDE
    for incl_dir in _SCOPE_INCLUDE_DIRS:
        if rel_path.startswith(incl_dir):
            return True
    for incl_file in _SCOPE_INCLUDE_FILES:
        if rel_path == incl_file:
            return True
    return False


def _check_file(content: str, added_lines: set[int] | None) -> list[str]:
    """检测文件内容中的纯陈述违规。

    Args:
        content: 文件完整内容。
        added_lines: 需检测的 1-based 行号集合（None=检测所有行）。

    Returns:
        违规描述列表，格式 "line {n}: [{pattern_name}] {line_content}"。
    """
    violations: list[str] = []
    in_frontmatter = False
    in_code_block = False

    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()

        # frontmatter 状态机（仅文件首行 --- 触发）
        if i == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter and stripped == "---":
            in_frontmatter = False
            continue

        # 代码块状态机（``` 或 ~~~ toggle）
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        # 跳过 frontmatter 和代码块
        if in_frontmatter or in_code_block:
            continue

        # 增量模式：只检 added 行（状态机仍跟踪所有行）
        if added_lines is not None and i not in added_lines:
            continue

        # 匹配 6 条违规 regex
        for pattern, name in _VIOLATION_PATTERNS:
            if pattern.search(line):
                violations.append(f"line {i}: [{name}] {line.strip()}")
                break  # 一行只报一条

    return violations
```

- [ ] **Step 4: 运行测试确认通过**

Run: `$env:PYTHONPATH="src"; python -m pytest tests/governance/d3_metadata/test_check_pure_assertion.py -v`
Expected: PASS (12 用例全过)

- [ ] **Step 5: Commit**

```bash
$env:PYTHONPATH="src"; python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_commit; r=session_worktree_commit('<SESSION_ID>', ['scripts/governance/d3_metadata/check_pure_assertion.py', 'tests/governance/d3_metadata/test_check_pure_assertion.py'], 'feat(check_pure_assertion): SSoT checker 核心检测逻辑——6 regex + scope 过滤 + frontmatter/code-block 跳过\n\nGOV-DOC-016 纯陈述原则检测真源，支持 --ci 增量 / --full-scan 全量双模式（后续 Task 实现）。12 测试用例覆盖 scope 边界 + 6 regex + 结构区跳过 + 增量检测。')"
```

---

## Task 2: SSoT checker——--ci + --full-scan 模式 + main()

**Files:**
- Modify: `scripts/governance/d3_metadata/check_pure_assertion.py` (追加 `_get_added_lines_ci` / `_read_staged_content` / `_walk_scope_files` / `main`)
- Modify: `tests/governance/d3_metadata/test_check_pure_assertion.py` (追加模式测试)

- [ ] **Step 1: 追加模式测试**

```python
# 追加到 tests/governance/d3_metadata/test_check_pure_assertion.py

def test_get_added_lines_ci_parses_diff(tmp_path, monkeypatch):
    """--ci 模式解析 git diff 输出提取 added 行号。"""
    fake_diff = """@@ -1,2 +1,3 @@
 unchanged
+新增违规行
 unchanged
@@ -5,1 +6,2 @@
 unchanged
+另一新增行
"""
    def fake_run(*args, **kwargs):
        class R:
            returncode = 0
            stdout = fake_diff
            stderr = ""
        return R()
    monkeypatch.setattr(_mod.subprocess, "run", fake_run)
    added = _mod._get_added_lines_ci("fake.md")
    assert added == {2, 7}


def test_walk_scope_files_finds_md(tmp_path):
    """--full-scan 模式遍历项目根，返回 in-scope .md 文件。"""
    (tmp_path / "AGENTS.md").write_text("ok")
    (tmp_path / "docs" / "_working").mkdir(parents=True)
    (tmp_path / "docs" / "_working" / "temp.md").write_text("skip")
    (tmp_path / "docs" / "03_modules").mkdir(parents=True)
    (tmp_path / "docs" / "03_modules" / "blueprint.md").write_text("ok")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "foo.py").write_text("skip")
    files = _mod._walk_scope_files(str(tmp_path))
    basenames = sorted(os.path.basename(f) for f in files)
    assert basenames == ["AGENTS.md", "blueprint.md"]
```

- [ ] **Step 2: 运行测试确认失败**

Run: `$env:PYTHONPATH="src"; python -m pytest tests/governance/d3_metadata/test_check_pure_assertion.py::test_get_added_lines_ci_parses_diff -v`
Expected: FAIL (AttributeError: module has no attribute `_get_added_lines_ci`)

- [ ] **Step 3: 实现 --ci + --full-scan 模式**

追加到 `scripts/governance/d3_metadata/check_pure_assertion.py`：

```python
import argparse
import os
import subprocess
import sys

_HUNK_HEADER_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def _get_project_root() -> str:
    """获取 git 项目根目录。"""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return os.getcwd()


def _to_rel_path(abs_or_rel: str, project_root: str) -> str:
    """将路径转为相对项目根的正斜杠路径。"""
    p = os.path.abspath(abs_or_rel)
    root = os.path.abspath(project_root)
    if p.startswith(root):
        rel = p[len(root):].lstrip(os.sep)
        return rel.replace("\\", "/")
    return abs_or_rel.replace("\\", "/")


def _get_added_lines_ci(rel_path: str) -> set[int]:
    """--ci 模式：从 git diff --cached 提取 added 行号集合。"""
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--unified=0", "--", rel_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode != 0:
            return set()
    except Exception:
        return set()
    added: set[int] = set()
    current = 0
    for line in r.stdout.splitlines():
        m = _HUNK_HEADER_RE.match(line)
        if m:
            current = int(m.group(1))
            continue
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            added.add(current)
            current += 1
        elif line.startswith("-"):
            pass
        else:
            current += 1
    return added


def _read_staged_content(rel_path: str) -> str:
    """读取 staged 版本文件内容（git show :path）。"""
    try:
        r = subprocess.run(
            ["git", "show", ":" + rel_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode == 0:
            return r.stdout
    except Exception:
        pass
    return ""


def _walk_scope_files(project_root: str) -> list[str]:
    """--full-scan 模式：遍历项目根，返回所有 in-scope .md 文件绝对路径。"""
    result: list[str] = []
    for dirpath, _dirs, filenames in os.walk(project_root):
        # 跳过 .git
        if ".git" in dirpath:
            continue
        for fname in filenames:
            if not fname.endswith(".md"):
                continue
            abs_path = os.path.join(dirpath, fname)
            rel = _to_rel_path(abs_path, project_root)
            if _is_in_scope(rel):
                result.append(abs_path)
    return result


def _run_ci_mode(files: list[str], project_root: str) -> int:
    """--ci 模式：检查指定文件的 added 行。"""
    all_violations: list[str] = []
    for abs_file in files:
        rel = _to_rel_path(abs_file, project_root)
        if not _is_in_scope(rel):
            continue
        added = _get_added_lines_ci(rel)
        if not added:
            continue
        content = _read_staged_content(rel)
        if not content:
            continue
        violations = _check_file(content, added)
        for v in violations:
            all_violations.append(f"{rel}: {v}")
    if all_violations:
        print("PURE_ASSERTION_VIOLATION——检出纯陈述原则违规（GOV-DOC-016）：", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        print("\n正文只应承载当前真实值，历史差异是 git log 的职责。", file=sys.stderr)
        print("修复：删除过渡文本（'已废止''之前是X现在改为Y'等），直接写当前值。", file=sys.stderr)
        return EXIT_FINDINGS
    return EXIT_CLEAN


def _run_full_scan(project_root: str) -> int:
    """--full-scan 模式：全量扫描所有 in-scope .md 文件。"""
    files = _walk_scope_files(project_root)
    all_violations: list[str] = []
    for abs_file in files:
        rel = _to_rel_path(abs_file, project_root)
        try:
            with open(abs_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue
        violations = _check_file(content, None)
        for v in violations:
            all_violations.append(f"{rel}: {v}")
    if all_violations:
        print(f"PURE-ASSERTION full-scan: 检出 {len(all_violations)} 条违规：", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        return EXIT_FINDINGS
    print(f"PURE-ASSERTION full-scan: 扫描 {len(files)} 个 in-scope .md 文件，0 违规。")
    return EXIT_CLEAN


def main() -> int:
    """入口：argparse 解析 --ci / --full-scan。"""
    parser = argparse.ArgumentParser(
        description="GOV-DOC-016 纯陈述原则检测（SSoT）"
    )
    parser.add_argument(
        "--ci", nargs="*", default=None, metavar="FILE",
        help="增量模式：检查指定文件的 staged added 行",
    )
    parser.add_argument(
        "--full-scan", action="store_true",
        help="全量模式：扫描所有 in-scope .md 文件",
    )
    args = parser.parse_args()

    project_root = _get_project_root()

    if args.full_scan:
        return _run_full_scan(project_root)
    if args.ci is not None:
        return _run_ci_mode(args.ci, project_root)
    # 无参数：报错
    print("错误：必须指定 --ci <files> 或 --full-scan", file=sys.stderr)
    return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 运行测试确认通过**

Run: `$env:PYTHONPATH="src"; python -m pytest tests/governance/d3_metadata/test_check_pure_assertion.py -v`
Expected: PASS (14 用例全过)

- [ ] **Step 5: Commit**

```bash
$env:PYTHONPATH="src"; python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_commit; r=session_worktree_commit('<SESSION_ID>', ['scripts/governance/d3_metadata/check_pure_assertion.py', 'tests/governance/d3_metadata/test_check_pure_assertion.py'], 'feat(check_pure_assertion): --ci 增量 / --full-scan 全量双模式 + main() 入口\n\n--ci 模式供 pure_assertion_gate subprocess 调用（git diff added 行）；--full-scan 模式供一次性审计（walk 全部 in-scope .md）。exit 0=clean, 1=violations, 2=error。')"
```

---

## Task 3: Gate——pure_assertion_gate.py + 测试

**Files:**
- Create: `src/zephyr/gov_enforcement/commit_gates/pure_assertion_gate.py`
- Test: `tests/governance/commit_gates/test_pure_assertion_gate.py`

- [ ] **Step 1: 写失败测试（8 用例）**

```python
# tests/governance/commit_gates/test_pure_assertion_gate.py
"""test_pure_assertion_gate.py — pure_assertion_gate.py 闭包测试。"""
from unittest.mock import MagicMock, patch
from zephyr.gov_enforcement.commit_gates.pure_assertion_gate import make_pure_assertion_gate


def _make_gateway(staged_md=None, wt_root="/fake"):
    gw = MagicMock()
    # _run_git 模拟
    calls = {"diff": staged_md or []}

    def _run_git(cmd):
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        r = R()
        if cmd[0:4] == ["git", "diff", "--cached", "--name-only"]:
            r.stdout = "\n".join(calls["diff"])
        elif cmd[0:2] == ["git", "rev-parse"] and "--show-toplevel" in cmd:
            r.stdout = wt_root
        return r
    gw._run_git = _run_git
    gw.project_root = wt_root
    return gw


def test_pass_no_staged_md():
    gw = _make_gateway(staged_md=[])
    gate = make_pure_assertion_gate()
    passed, detail = gate.check(gw, [])
    assert passed is True


def test_pass_all_excluded():
    gw = _make_gateway(staged_md=["docs/_working/temp.md"])
    gate = make_pure_assertion_gate()
    passed, _ = gate.check(gw, ["docs/_working/temp.md"])
    assert passed is True


@patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.subprocess.run")
def test_block_added_violation(mock_run):
    """staged .md added 行含违规 → block。"""
    mock_run.return_value = MagicMock(returncode=1, stderr="AGENTS.md: line 5: [已废止/已废弃/已弃用] 已废止的规则", stdout="")
    gw = _make_gateway(staged_md=["AGENTS.md"], wt_root="/fake")
    # 模拟文件存在
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.isfile", return_value=True):
        with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.exists", return_value=True):
            gate = make_pure_assertion_gate()
            passed, detail = gate.check(gw, ["AGENTS.md"])
    assert passed is False
    assert "PURE_ASSERTION" in detail


@patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.subprocess.run")
def test_pass_clean_exit0(mock_run):
    """checker exit 0 → pass。"""
    mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")
    gw = _make_gateway(staged_md=["AGENTS.md"], wt_root="/fake")
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.isfile", return_value=True):
        gate = make_pure_assertion_gate()
        passed, _ = gate.check(gw, ["AGENTS.md"])
    assert passed is True


@patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.subprocess.run")
def test_failopen_exit2(mock_run):
    """checker exit 2 → fail-open。"""
    mock_run.return_value = MagicMock(returncode=2, stderr="script error", stdout="")
    gw = _make_gateway(staged_md=["AGENTS.md"], wt_root="/fake")
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.isfile", return_value=True):
        gate = make_pure_assertion_gate()
        passed, _ = gate.check(gw, ["AGENTS.md"])
    assert passed is True


@patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.subprocess.run")
def test_failopen_timeout(mock_run):
    """checker 超时 → fail-open。"""
    import subprocess as sp
    mock_run.side_effect = sp.TimeoutExpired(cmd="check", timeout=60)
    gw = _make_gateway(staged_md=["AGENTS.md"], wt_root="/fake")
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.isfile", return_value=True):
        gate = make_pure_assertion_gate()
        passed, _ = gate.check(gw, ["AGENTS.md"])
    assert passed is True


def test_failopen_script_missing():
    """checker 脚本缺失 → fail-open。"""
    gw = _make_gateway(staged_md=["AGENTS.md"], wt_root="/fake")
    with patch("zephyr.gov_enforcement.commit_gates.pure_assertion_gate.os.path.isfile", return_value=False):
        gate = make_pure_assertion_gate()
        passed, _ = gate.check(gw, ["AGENTS.md"])
    assert passed is True


def test_gate_priority_and_id():
    gate = make_pure_assertion_gate()
    assert gate.gate_id == "PURE-ASSERTION"
    assert gate.priority == 69
```

- [ ] **Step 2: 运行测试确认失败**

Run: `$env:PYTHONPATH="src"; python -m pytest tests/governance/commit_gates/test_pure_assertion_gate.py -v`
Expected: FAIL (ImportError: module not found)

- [ ] **Step 3: 实现 gate 薄壳**

```python
# src/zephyr/gov_enforcement/commit_gates/pure_assertion_gate.py
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.pure_assertion_gate
# [DOMAIN] D_GOV_DOC_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d3_metadata.check_pure_assertion (subprocess --ci，检测真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .md 文件 added 行含纯陈述违规（GOV-DOC-016）时阻断 commit；只检 staged .md added 行（增量检测，现存违规 grandfather）；checker 缺失/超时/exit 2 时 fail-open（不阻断）；exit 1 时硬阻断；scope 过滤在 checker 内（SSoT）
# [MODIFY-GUARD] gate_id="PURE-ASSERTION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——subprocess 异常降级为 fail-open；检出违规则 fail-closed
# [TESTS] tests/governance/commit_gates/test_pure_assertion_gate.py
# [A_module] module_id=MOD-GOV-pure_assertion_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pure_assertion_gate.py — 纯陈述原则阻断门禁（PURE-ASSERTION，GOV-DOC-016 治本）

治本 AD-001 阶段3 删除 _check_pure_assertion 后纯陈述检测无 commit-time 强制：
本 gate 在 GitCommitGateway pre-commit 阶段（in-process）注册，--no-verify 绕不过。
检测真源=check_pure_assertion.py（subprocess 调用 --ci），本 gate 是 thin wrapper。

Usage::

    from zephyr.gov_enforcement.commit_gates.pure_assertion_gate import make_pure_assertion_gate
    registry.register(make_pure_assertion_gate())
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_pure_assertion_gate"]

_PROJECT_ROOT = (
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))))
)
_CHECKER_SCRIPT = os.path.join(
    _PROJECT_ROOT, "scripts", "governance", "d3_metadata", "check_pure_assertion.py"
)


def _get_staged_md_files(gateway) -> list[str]:
    """获取所有 staged .md 文件（新增+修改）。git 异常时返回空列表（fail-open）。"""
    try:
        r = gateway._run_git(["git", "diff", "--cached", "--name-only"])
        if r.returncode != 0:
            logger.warning("PURE-ASSERTION fail-open: git diff 失败(rc=%d)。", r.returncode)
            return []
        return [
            f.replace("\\", "/") for f in r.stdout.strip().splitlines()
            if f.endswith(".md")
        ]
    except Exception as e:
        logger.warning("PURE-ASSERTION fail-open: git diff 异常(%s: %s)。", type(e).__name__, e)
        return []


def _resolve_worktree_root(gateway) -> str:
    """获取 worktree root 绝对路径，失败回退 gateway.project_root。"""
    try:
        r = gateway._run_git(["git", "rev-parse", "--show-toplevel"])
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return str(gateway.project_root)


def _resolve_abs_paths(rel_files: list[str], wt_root: str) -> list[str]:
    """将相对路径解析为绝对路径，过滤不存在的文件。"""
    abs_files = []
    for rel in rel_files:
        if os.path.isabs(rel):
            abs_files.append(rel)
        else:
            abs_files.append(os.path.join(wt_root, rel.replace("/", os.sep)))
    return [f for f in abs_files if os.path.isfile(f)]


def _run_assertion_checker(abs_files: list[str], wt_root: str) -> subprocess.CompletedProcess | None:
    """subprocess 调用 check_pure_assertion.py --ci <files>。"""
    if not os.path.isfile(_CHECKER_SCRIPT):
        logger.warning("PURE-ASSERTION fail-open: check_pure_assertion.py 不存在(%s)。", _CHECKER_SCRIPT)
        return None
    try:
        return subprocess.run(
            [sys.executable, _CHECKER_SCRIPT, "--ci"] + abs_files,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=wt_root, timeout=60,
        )
    except subprocess.TimeoutExpired:
        logger.warning("PURE-ASSERTION fail-open: checker 超时(60s)。")
        return None
    except Exception as e:
        logger.warning("PURE-ASSERTION fail-open: subprocess 异常(%s: %s)。", type(e).__name__, e)
        return None


def _parse_assertion_result(result: subprocess.CompletedProcess) -> tuple[bool, str]:
    """解析 checker exit code：0=pass, 2=fail-open, 1=block。"""
    if result.returncode == 0:
        return True, ""
    if result.returncode == 2:
        logger.warning("PURE-ASSERTION fail-open: checker 异常(exit 2): %s", result.stderr[:200])
        return True, ""
    # exit 1 = 违规
    detail = result.stderr.strip() if result.stderr else "纯陈述违规检出"
    return False, (
        "PURE_ASSERTION_VIOLATION——检出纯陈述原则违规（GOV-DOC-016）。\n"
        "正文只应承载当前真实值，历史差异是 git log 的职责。\n"
        "修复：删除过渡文本（'已废止''之前是X现在改为Y'等），直接写当前值。\n"
        + detail
    )


def make_pure_assertion_gate() -> GateSpec:
    """构造纯陈述原则阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="PURE-ASSERTION", priority=69)。
        priority=69——紧邻 PURE-SHIM(68) 之后、DANGLING-REFERENCE(70) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        staged_md = _get_staged_md_files(gateway)
        if not staged_md:
            return True, ""
        wt_root = _resolve_worktree_root(gateway)
        abs_files = _resolve_abs_paths(staged_md, wt_root)
        if not abs_files:
            return True, ""
        result = _run_assertion_checker(abs_files, wt_root)
        if result is None:
            return True, ""
        return _parse_assertion_result(result)

    return GateSpec(gate_id="PURE-ASSERTION", check=_check, priority=69)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `$env:PYTHONPATH="src"; python -m pytest tests/governance/commit_gates/test_pure_assertion_gate.py -v`
Expected: PASS (8 用例全过)

- [ ] **Step 5: Commit**

```bash
$env:PYTHONPATH="src"; python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_commit; r=session_worktree_commit('<SESSION_ID>', ['src/zephyr/gov_enforcement/commit_gates/pure_assertion_gate.py', 'tests/governance/commit_gates/test_pure_assertion_gate.py'], 'feat(pure_assertion_gate): GOV-DOC-016 纯陈述原则 commit gate（priority=69）\n\n对标 PURE-SHIM 模式：thin wrapper subprocess 调 check_pure_assertion.py --ci。fail-open on checker 缺失/超时/exit 2；fail-closed on exit 1（检出违规）。8 测试用例覆盖 pass/block/fail-open 场景。')"
```

---

## Task 4: Gate 注册——git_commit_gateway.py

**Files:**
- Modify: `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py` L88, L308

- [ ] **Step 1: 添加 import（L88 后）**

在 `from zephyr.gov_enforcement.commit_gates.pure_shim_gate import make_pure_shim_gate` 之后添加：

```python
from zephyr.gov_enforcement.commit_gates.pure_assertion_gate import make_pure_assertion_gate
```

- [ ] **Step 2: 添加 register 调用（L308 后）**

在 `self._gate_registry.register(make_pure_shim_gate())` 之后添加：

```python
        self._gate_registry.register(make_pure_assertion_gate())  # priority=69 治本纯陈述原则（GOV-DOC-016，subprocess 调 check_pure_assertion.py --ci）
```

- [ ] **Step 3: 验证 gate 已注册**

Run: `$env:PYTHONPATH="src"; python -c "from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway; gw = GitCommitGateway.__new__(GitCommitGateway); from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry; gw._gate_registry = CommitGateRegistry(); gw._gate_registry.register(make_pure_assertion_gate()); specs = gw._gate_registry._specs; assert 'PURE-ASSERTION' in specs; assert specs['PURE-ASSERTION'].priority == 69; print('OK: PURE-ASSERTION registered at priority=69')"`

Expected: `OK: PURE-ASSERTION registered at priority=69`

- [ ] **Step 4: Commit**

```bash
$env:PYTHONPATH="src"; python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_commit; r=session_worktree_commit('<SESSION_ID>', ['src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py'], 'feat(git_commit_gateway): 注册 PURE-ASSERTION gate (priority=69)\n\nimport make_pure_assertion_gate + registry.register。紧邻 PURE-SHIM(68) 之后。')"
```

---

## Task 5: 全量扫描 + 清理现存违规

**Files:**
- Modify: 多个 .md 文件（扫描结果决定）

- [ ] **Step 1: 运行全量扫描**

Run: `$env:PYTHONPATH="src"; python scripts/governance/d3_metadata/check_pure_assertion.py --full-scan 2>&1`
Expected: 输出现存违规清单（file:line:pattern:content）

- [ ] **Step 2: 按文件逐个清理违规**

对扫描输出的每个 file:line，读取上下文，删除过渡文本，直接写当前值。

清理规则（每种 pattern 的修复策略）：
- `已废止/已废弃/已弃用` → 删除整句或删除"已废止"前缀，只保留当前描述
- `旧定义/旧规则` → 删除整句
- `之前是X现在改为Y` → 删除整句，只写"现在"后面的部分
- `已被取代/已被替代` → 删除整句
- `P2迁移后` → 删除整句或删除"P2迁移后"前缀
- `从X迁移到Y` → 删除整句

- [ ] **Step 3: 验证清理后 0 违规**

Run: `$env:PYTHONPATH="src"; python scripts/governance/d3_metadata/check_pure_assertion.py --full-scan 2>&1`
Expected: `PURE-ASSERTION full-scan: 扫描 N 个 in-scope .md 文件，0 违规。`

- [ ] **Step 4: Commit**

```bash
$env:PYTHONPATH="src"; python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_commit; r=session_worktree_commit('<SESSION_ID>', [<清理的文件列表>], 'fix(docs): 清理现存纯陈述违规——GOV-DOC-016 全量达标\n\ncheck_pure_assertion.py --full-scan 验证 0 违规。删除过渡文本（已废止/之前是X现在改为Y等），直接写当前值。')"
```

---

## Task 6: 文档同步（5 处）

**Files:**
- Modify: `AGENTS.md` L381
- Modify: `docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml` §gov_doc_016 + change_history
- Modify: `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`
- Modify: `docs/03_modules/_cross_layer/gate_engine/blueprint.md` §0.1
- Modify: `.trae/rules/onboarding_detail.md` L416

- [ ] **Step 1: 更新 AGENTS.md L381**

将"已废弃，未迁移"段落改为：

```markdown
**GATE-PURE-ASSERTION 纯陈述原则门禁（GOV-DOC-016）** — 注册制 gate `PURE-ASSERTION`（priority=69，in-process，`--no-verify` 绕不过）。检测范围：所有 .md 项目文档（`.trae/rules/`、`AGENTS.md`、`README.md`、`docs/01_policies_and_standards/` 除 `rules/`、`docs/02_enterprise_architecture/` 除 `architecture_debt_registry.md`、`docs/03_modules/`、`docs/08_knowledge/`）。豁免：`docs/_archive/`、`docs/_working/`、`session_logs/`、`CHANGELOG.md`、`docs/03_governance_reports/`、YAML 规则文件（由 `rules_integrity_reconciler` 独立负责）。增量检测：只检 staged added 行，现存违规 grandfather。检测真源=`check_pure_assertion.py`（subprocess `--ci` 调用）。
```

- [ ] **Step 2: 更新 trae_030 §gov_doc_016**

scope 字段从 `doc_numbering_metadata` 扩展描述为：

```yaml
  scope: |
    所有 .md 项目文档（.trae/rules/、AGENTS.md、README.md、
    docs/01_policies_and_standards/ 除 rules/ 子目录、
    docs/02_enterprise_architecture/ 除 architecture_debt_registry.md、
    docs/03_modules/、docs/08_knowledge/）。
    豁免：docs/_archive/、docs/_working/、session_logs/、CHANGELOG.md、
    docs/03_governance_reports/、YAML 规则文件。
    YAML 规则文件的纯陈述治理由 rules_integrity_reconciler 独立负责。
```

change_history 追加版本条目：

```yaml
  - version: "1.1.4"
    date: "2026-07-17"
    change: |
      scope 从"规则文档"扩到"所有 .md 项目文档"；强制力从 post-commit reconciler
      升级为 commit gate PURE-ASSERTION (priority=69)，in-process 阻断。
```

- [ ] **Step 3: 更新 capability_canonical_file_registry.yaml**

追加 2 个新能力条目：

```yaml
  - capability_id: check_pure_assertion
    canonical_file: scripts/governance/d3_metadata/check_pure_assertion.py
    description: "GOV-DOC-016 纯陈述原则检测真源（SSoT）——6 regex + scope 过滤 + frontmatter/code-block 跳过"
    creation_tokens:
      - commit: "<COMMIT_HASH>"
        date: "2026-07-17"
    consumers:
      - zephyr.gov_enforcement.commit_gates.pure_assertion_gate (subprocess --ci)

  - capability_id: PURE-ASSERTION
    canonical_file: src/zephyr/gov_enforcement/commit_gates/pure_assertion_gate.py
    description: "纯陈述原则 commit gate（priority=69），in-process 阻断 GOV-DOC-016 违规"
    creation_tokens:
      - commit: "<COMMIT_HASH>"
        date: "2026-07-17"
    consumers:
      - zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
```

- [ ] **Step 4: 更新 blueprint.md §0.1 gate inventory**

在 PURE-SHIM 条目后追加：

```markdown
| PURE-ASSERTION | 69 | `pure_assertion_gate.py` | 纯陈述原则（GOV-DOC-016）——.md 文档 added 行含"已废止/之前是X现在改为Y"等过渡文本时阻断 | `check_pure_assertion.py --ci` |
```

- [ ] **Step 5: 更新 onboarding_detail.md L416 触发表**

在"修改任何 trae_XXX 规则文件 → Read trae_030 全文"之后追加一行：

```markdown
| 修改任何 .md 项目文档 | Read trae_030 §gov_doc_016（纯陈述原则——正文只写现在，历史归 git log） |
```

- [ ] **Step 6: Commit**

```bash
$env:PYTHONPATH="src"; python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_commit; r=session_worktree_commit('<SESSION_ID>', ['AGENTS.md', 'docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml', 'docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml', 'docs/03_modules/_cross_layer/gate_engine/blueprint.md', '.trae/rules/onboarding_detail.md'], 'docs: 同步 PURE-ASSERTION gate 到 5 处文档\n\nAGENTS.md L381 从'已废弃'改为'已迁移到注册制 gate'；trae_030 scope 扩到所有 .md 文档 (v1.1.4)；capability_registry 登记 2 新能力；blueprint §0.1 补 gate 条目；onboarding 触发表加 .md 文档行。')"
```

- [ ] **Step 7: 最终验证**

Run: `$env:PYTHONPATH="src"; python scripts/governance/d3_metadata/check_pure_assertion.py --full-scan`
Expected: `PURE-ASSERTION full-scan: 扫描 N 个 in-scope .md 文件，0 违规。`

Run: `$env:PYTHONPATH="src"; python -m pytest tests/governance/commit_gates/test_pure_assertion_gate.py tests/governance/d3_metadata/test_check_pure_assertion.py -v`
Expected: PASS (22 用例全过)

Run: `$env:PYTHONPATH="src"; python -c "from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway; gw = GitCommitGateway.__new__(GitCommitGateway); print('import OK')"`
Expected: `import OK`（注册无语法错误）
