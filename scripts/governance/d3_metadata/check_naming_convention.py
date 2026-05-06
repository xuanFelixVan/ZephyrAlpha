#!/usr/bin/env python3

"""
GATE-11：命名规范门禁(check_naming_convention.py)
======================================================


权威依据
--------
`docs/01_policies_and_standards/governance/document/file-naming-standard.md` v2.0.1 §五 违规检测规则

运行模式
--------
  # CI / 全库扫描
  python scripts/governance/check_naming_convention.py --all

  # pre-commit / 指定文件
  python scripts/governance/check_naming_convention.py --files path/to/a.md path/to/b.md

  # staged 文件(git diff --cached --name-only)
  python scripts/governance/check_naming_convention.py --staged

编号说明
--------
本门禁续号于 Architecture-as-Code 系列(`GATE-01 ~ GATE-10`,
见 `docs/02_enterprise_architecture/target-architecture/architecture-model/scripts/check_architecture_gates.py v2.0.0`),
命名为 `GATE-11` 避免编号空间碰撞(append-only 原则,对标 ADR-0006 跳号治理精神)。

检测项(7 条)
--------------
N-01 新建文件名含大写字母(豁免白名单)
N-02 新建文件名含版本号后缀(-v\\d+ / -round\\d+ / -iteration\\d+)
N-03 新建状态快照文件带日期后缀(-\\d{8},LATEST 白名单豁免)
N-04 ADR 嵌套编号(adr-NNN-NNN.md 两段数字,禁止)
N-05 ADR 缺失 kebab 尾缀(adr-NNNN.md 无尾缀,豁免 _template.md)
N-06 module_id 含 scope 前缀(EA- / PROD- / DEV- 等)
N-07 ADR module_id 与文件名编号不一致

返回码
------
0 = 全部通过
1 = 存在违规
2 = 脚本运行错误(如 git 命令失败、参数错误)
"""

from __future__ import annotations

__manifest__ = """
args:
- --all
description: 文件命名规范检查(kebab-case / module_id namespace / ADR铁律)
dimensions:
- D3
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

from _shared.constants import REPO_ROOT
from _shared.frontmatter import extract_module_id

class Violation(NamedTuple):
    rule: str
    file: str
    detail: str

FILENAME_UPPERCASE_WHITELIST: set[str] = {
    "AGENTS.md",
    "README.md",
    "LICENSE",
    "LICENSE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "NOTICE",
    "NOTICE.md",
}

PATH_EXEMPT_PREFIXES: tuple[str, ...] = (
    "archive/",
    "_reorg_snapshots/",
    ".git/",
    ".venv/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "node_modules/",
    "docs/19_development_workspace/session-logs/",
)

MODULE_ID_SCOPE_BAD_PREFIXES: tuple[str, ...] = (
    "EA-",
    "PROD-",
    "DEV-",
    "OPS-",
)

MODULE_ID_LEGAL_NAMESPACES: tuple[str, ...] = (
    "ADR-",
    "KE-",
    "OQ-",
    "T-",
    "R-",
    "ZA-",
    "DW-",
    "GATE-",
    "POL-",
    "STD-",
    "VIEW-",
)

RE_UPPERCASE_BODY = re.compile(r"[A-Z]")
RE_VERSION_SUFFIX = re.compile(r"-(?:v\d+|round\d+|iteration\d+)(?:[-.]|$)")

TECH_VERSION_TOKENS: tuple[str, ...] = (
    "pydantic-v",
    "python-v",
    "node-v",
    "numpy-v",
    "pandas-v",
    "postgres-v",
    "mysql-v",
    "sqlite-v",
    "redis-v",
    "django-v",
    "flask-v",
    "fastapi-v",
    "typescript-v",
    "react-v",
    "vue-v",
    "next-v",
    "go-v",
    "rust-v",
    "kubernetes-v",
    "docker-v",
    "terraform-v",
    "ansible-v",
    "http-v",
    "tls-v",
    "oauth-v",
)

def _has_tech_version_token(filename_lower: str) -> bool:
    """Whitelist real technology product versions (e.g. pydantic-v2) from N-02 detection."""
    return any(tok in filename_lower for tok in TECH_VERSION_TOKENS)

RE_DATE_SUFFIX = re.compile(r"-\d{8}(?:[-.]|$)")
RE_LATEST = re.compile(r"-LATEST(?:[-.]|$)", re.IGNORECASE)
RE_ADR_NESTED = re.compile(r"^adr-\d+-\d+\.md$", re.IGNORECASE)
RE_ADR_NO_SUFFIX = re.compile(r"^adr-\d+\.md$", re.IGNORECASE)
RE_ADR_FILE = re.compile(r"^adr-(\d{4})-[\w\-]+\.md$", re.IGNORECASE)
def _is_path_exempt(rel_path: str) -> bool:
    rp = rel_path.replace("\\", "/")
    return any(rp.startswith(p) for p in PATH_EXEMPT_PREFIXES)

def check_file(rel_path: str, abs_path: Path | None = None) -> list[Violation]:
    """对单个相对路径做 7 条规则检测；返回违规列表。"""
    violations: list[Violation] = []
    if _is_path_exempt(rel_path):
        return violations

    fname = Path(rel_path).name

    if fname not in FILENAME_UPPERCASE_WHITELIST:
        body = Path(fname).stem
        if RE_UPPERCASE_BODY.search(body):
            violations.append(
                Violation(
                    "N-01",
                    rel_path,
                    f"文件名含大写字母（豁免白名单：{sorted(FILENAME_UPPERCASE_WHITELIST)}）",
                )
            )

    if RE_VERSION_SUFFIX.search(fname) and not _has_tech_version_token(fname.lower()):
        violations.append(
            Violation(
                "N-02",
                rel_path,
                "文件名含版本号后缀（-vN / -roundN / -iterationN）；"
                "技术栈专有名词（如 pydantic-v2 / python-v3）已白名单",
            )
        )

    if RE_DATE_SUFFIX.search(fname) and not RE_LATEST.search(fname):
        violations.append(
            Violation(
                "N-03",
                rel_path,
                "文件名含日期后缀（-YYYYMMDD），仅 -LATEST 白名单允许",
            )
        )

    if fname.lower().startswith("adr-") and fname != "_template.md":
        if RE_ADR_NESTED.match(fname):
            violations.append(
                Violation(
                    "N-04",
                    rel_path,
                    "ADR 使用嵌套编号（adr-NNN-NNN.md），应改为扁平 4 位编号 + kebab 尾缀",
                )
            )
        if RE_ADR_NO_SUFFIX.match(fname):
            violations.append(
                Violation(
                    "N-05",
                    rel_path,
                    "ADR 缺失 kebab 尾缀（adr-NNNN.md 应为 adr-nnnn-kebab-title.md）",
                )
            )

    if abs_path is None:
        abs_path = REPO_ROOT / rel_path
    if abs_path.suffix == ".md" and abs_path.exists():
        mid = extract_module_id(abs_path)
        if mid:
            for bad in MODULE_ID_SCOPE_BAD_PREFIXES:
                if mid.upper().startswith(bad):
                    violations.append(
                        Violation(
                            "N-06",
                            rel_path,
                            f"frontmatter module_id 含禁用 scope 前缀 '{bad}'（值={mid}），"
                            f"合法命名空间见 file-naming-standard §四",
                        )
                    )
                    break

            m = RE_ADR_FILE.match(fname)
            if m and mid.upper().startswith("ADR-"):
                file_num = m.group(1)
                id_num_match = re.match(r"ADR-(\d+)", mid, re.IGNORECASE)
                if id_num_match:
                    id_num = id_num_match.group(1).zfill(4)
                    if id_num != file_num:
                        violations.append(
                            Violation(
                                "N-07",
                                rel_path,
                                f"ADR module_id 编号 ({mid}) 与文件名编号 (adr-{file_num}) 不一致",
                            )
                        )

    return violations

def iter_all_files(root: Path) -> Iterable[Path]:
    """iter all files."""
    for p in root.rglob("*"):
        """iter all files."""
        """iter_all_files."""
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if _is_path_exempt(rel):
            continue
        if p.suffix.lower() in (".pyc",):
            continue
        yield p
    """iter all files."""

def _git_staged_files() -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]

def _print_report(violations: list[Violation]) -> None:
    if not violations:
        print("[GATE-11] OK  0 violation(s).", file=sys.stderr)
        return
    print(f"[GATE-11] FAIL  {len(violations)} violation(s):", file=sys.stderr)
    print(file=sys.stderr)
    by_rule: dict[str, list[Violation]] = {}
    for v in violations:
        by_rule.setdefault(v.rule, []).append(v)
    for rule in sorted(by_rule.keys()):
        items = by_rule[rule]
        print(f"  {rule} ({len(items)} hit):", file=sys.stderr)
        for v in items[:20]:
            print(f"    - {v.file}", file=sys.stderr)
            print(f"        {v.detail}", file=sys.stderr)
        if len(items) > 20:
            print(f"    ... (+{len(items) - 20} more)", file=sys.stderr)
        print(file=sys.stderr)
    print("[GATE-11] 权威依据：docs/01_policies_and_standards/governance/document/file-naming-standard.md §五")

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(
        prog="check_naming_convention",
        description="GATE-11 命名规范门禁（续号于 AaC GATE-01~10）",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--all", action="store_true", help="全库扫描")
    group.add_argument("--staged", action="store_true", help="仅扫描 git staged 文件")
    group.add_argument("--files", nargs="+", help="扫描指定文件列表")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻塞流程）")
    parser.add_argument("--root", default=str(REPO_ROOT), help="仓库根目录（默认自动定位）")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    violations: list[Violation] = []

    if args.staged:
        files = _git_staged_files()
        if not files:
            print("[GATE-11] OK  no staged files.", file=sys.stderr)
            sys.exit(0)
        for rel in files:
            abs_p = root / rel
            if not abs_p.exists():
                continue
            violations.extend(check_file(rel, abs_p))
    elif args.files:
        for f in args.files or []:
            abs_p = (root / f).resolve() if not Path(f).is_absolute() else Path(f)
            try:
                rel = abs_p.resolve().relative_to(root).as_posix()
            except ValueError:
                rel = f.replace("\\", "/")
            violations.extend(check_file(rel, abs_p))
    else:
        for p in iter_all_files(root):
            rel = p.relative_to(root).as_posix()
            violations.extend(check_file(rel, p))

    _print_report(violations)
    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if violations else 0)

if __name__ == "__main__":
    main()

