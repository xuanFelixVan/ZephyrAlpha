# [BLUEPRINT] MOD-INF-005 | scripts/governance/d4_paths/detect_ruins_references.py | §
# [MODULE] scripts.governance.d4_paths.detect_ruins_references
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d4_paths.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""detect_ruins_references.py — 残骸/废弃路径引用检测


对标：PS-STD-003 ABS-44（禁止使用废弃路径作为规则来源）
     GOV-DOC-004 §3（废弃路径清单）

检测内容：
- 任何文件中引用 _DO_NOT_USE_old_tree/ 路径
- 引用已知的废弃路径
- 引用候选池中的文件作为正式规则来源

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 残骸/废弃路径引用检测（ABS-44 — 禁止引用废墟目录）
dimensions:
- D1
- D4
priority: P0
timeout_seconds: 30
warn_only: false
"""


import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
import yaml
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_CODE
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

_SHARED_DIR = REPO_ROOT / "scripts" / "governance" / "_shared"
_DEPRECATED_PATHS_YAML = _SHARED_DIR / "deprecated_paths.yaml"
_WHITELIST_FILES = {
    "AGENTS.md",
    "architecture-rationale-log.md",
    "vibe-coding-script-system-design.md",
    "detect_ruins_references.py",
    "deprecated_paths.yaml",
    "blueprint.md",
}
_RUINS_PATTERNS: list[tuple[str, str]] | None = None
_OBSOLETE_PATH_MARKERS: list[str] | None = None


def _get_ruins_patterns() -> list[tuple[str, str]]:
    """_get_ruins_patterns implementation."""
    global _RUINS_PATTERNS
    if _RUINS_PATTERNS is None:
        with open(_DEPRECATED_PATHS_YAML, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        _RUINS_PATTERNS = [(entry["pattern"], entry["label"]) for entry in data.get("ruins_regex_patterns", [])]
    return _RUINS_PATTERNS


def _get_obsolete_markers() -> list[str]:
    """_get_obsolete_markers implementation."""
    global _OBSOLETE_PATH_MARKERS
    if _OBSOLETE_PATH_MARKERS is None:
        with open(_DEPRECATED_PATHS_YAML, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        _OBSOLETE_PATH_MARKERS = list(data.get("obsolete_markers", []))
    return _OBSOLETE_PATH_MARKERS


def scan_file(filepath: Path) -> list[dict]:
    """扫描单个文件并返回发现列表"""
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings
    is_py = filepath.suffix == ".py"
    for pattern, label in _get_ruins_patterns():
        # .py 文件中的 `\\\\` 是合法字符串转义/正则模式，不是"路径双重嵌套"bug。
        # 该检测针对旧脚本生成的 JSON/YAML 错误路径，跳过 .py 避免假阳性。
        if is_py and "路径双重嵌套" in label:
            continue
        for match in re.finditer(pattern, content, re.IGNORECASE):
            line_num = content[: match.start()].count("\n") + 1
            # 扩展 context 到完整行（capped 250）：让 ZeroResidueScanner 能看到
            # 同行内的审计标记（"废弃"/"迁移"/"v2.0"），避免审计追踪文档被误判为违规。
            line_start = content.rfind("\n", 0, match.start()) + 1
            line_end = content.find("\n", match.end())
            if line_end == -1:
                line_end = len(content)
            context = content[line_start:line_end].replace("\n", " ")
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": line_num,
                    "pattern": label,
                    "context": context[:250],
                }
            )
    for pattern in _get_obsolete_markers():
        if re.search(pattern, content, re.IGNORECASE):
            findings.append(
                {
                    "file": str(filepath.relative_to(REPO_ROOT)),
                    "line": 1,
                    "pattern": f"废弃跳转占位符: {pattern}",
                    "context": "占位跳转文件应删除或走 superseded_by 字段",
                }
            )
    return findings
    "扫描单个文件并返回发现列表."


def scan_repo(scan_dir: Path | None = None) -> tuple[list[dict], int, int]:
    """扫描仓库并返回发现列表."""
    if scan_dir is None:
        "扫描仓库并返回发现列表."
        "扫描并返回发现列表."
        scan_dir = REPO_ROOT
    all_findings = []
    files_scanned = 0
    for filepath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_CODE, exclude_files=frozenset(_WHITELIST_FILES)):
        try:
            rel = filepath.relative_to(REPO_ROOT)
        except ValueError:
            continue
        rel_str = str(rel).replace("\\", "/")
        if rel_str.startswith("_DO_NOT_USE") or rel_str.startswith(".trae"):
            continue
        # 以下目录排除原因：文件内容必然引用废弃路径/废墟目录，属正常语义而非违规
        # - data/backups/: 历史阶段备份文件，引用是当时正常路径
        # - docs/01_policies_and_standards/rules/: 规则文件描述禁止行为时引用禁止内容
        # - docs/01_policies_and_standards/_registry/contracts/: 配置文件声明 forbidden_paths
        # - docs/01_policies_and_standards/_registry/catalogs/: 登记表注册废弃目录为 status:deprecated 条目
        # - docs/08_knowledge/: 知识库条目记录废弃路径作为知识
        # - docs/_working/: 过程性文档（research_notes 等）
        # - scripts/governance/: 治理脚本本身检测废弃路径，必然引用
        # - tests/: 测试用例可能引用废弃路径验证检测逻辑
        _EXCLUDE_PATH_PREFIXES = (
            "data/backups/",
            "docs/01_policies_and_standards/rules/",
            "docs/01_policies_and_standards/_registry/contracts/",
            "docs/01_policies_and_standards/_registry/catalogs/",
            "docs/08_knowledge/",
            "docs/_working/",
            "scripts/governance/",
            "tests/",
        )
        if any(rel_str.startswith(p) for p in _EXCLUDE_PATH_PREFIXES):
            continue
        files_scanned += 1
        findings = scan_file(filepath)
        all_findings.extend(findings)
    return (all_findings, files_scanned, 0)
    "扫描仓库并返回发现列表."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="残骸/废弃路径引用检测")
    parser.add_argument("--scan-dir", default=None, help="扫描目录")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir) if args.scan_dir else None
    findings, files_scanned, errors = scan_repo(scan_dir)
    if findings:
        print(f"\n[RUINS-SCAN] {len(findings)} 残骸路径引用发现（扫描 {files_scanned} 文件）:\n", file=sys.stderr)
        for f in findings:
            print(f"  [{f['pattern']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    {f['context']}", file=sys.stderr)
        print(file=sys.stderr)
    print(f"Scanned {files_scanned} files, {len(findings)} findings, {errors} errors", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
