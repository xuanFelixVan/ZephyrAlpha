# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/audit_directory_integrity.py | §
# [MODULE] scripts.governance.d1_structure.audit_directory_integrity
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
# [TTL] task_bound
"""
audit_directory_integrity.py — 01_policies_and_standards/ 目录结构完整性审计

对标：ITIL 4 SACM §4.5（配置审计——CI登记完整性）
     ISO 11179 §5（元数据注册表——标识符唯一性）
     AGENTS.md §5.1（零记忆重启标准——索引↔磁盘一致）
     AGENTS.md §6.2（原子事务模式——重命名=删旧+登记新+索引更新，不可分步）
     PS-STD-012 §7.2（规则体系验证——字段扫描→内容读取→交叉验证→判定修复）

五维检测：
  D1 幽灵文件    —— 磁盘存在但未在任何 index.md 中注册的文件
  D2 ID 冲突     —— 两个以上文件声明相同 module_id
  D3 索引对账    —— index.md 声称文件数 vs 磁盘实际文件数
  D4 命名规范    —— 文件名后缀是否匹配 doc_type（-policy.md / -blueprint.md / -gate.md 等）
  D5 登记缺漏    —— 有 index.md 的目录下，文件是否都在 index.md §2 中有对应条目

Usage:
  python scripts/governance/d1_structure/audit_directory_integrity.py          # 默认扫描
  python scripts/governance/d1_structure/audit_directory_integrity.py --json   # JSON 输出

exit codes: 0=pass, 1=findings, 2=script error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 目录结构完整性审计（D1幽灵文件+D2 ID冲突+D3索引对账+D4命名规范+D5登记缺漏）
dimensions:
- D1
- D2
- D3
- D4
- D5
priority: P0
timeout_seconds: 60
warn_only: false
"""

import json
import re
import sys
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
try:
    import yaml
except ImportError:
    yaml = None
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.frontmatter import extract_module_id

_PS_ROOT = REPO_ROOT / "docs" / "01_policies_and_standards"
_EXCLUDE_NAMES = frozenset({".git", "__pycache__", ".venv", "node_modules", ".mypy_cache"})
_EXCLUDE_SUBDIRS = frozenset({"_reorg_snapshots", "archive"})
_TEMPLATE_DIR = _PS_ROOT / "templates"
# 真源单一化：后缀规则是 doc_type 的属性，由 doc_type_vocabulary.yaml 唯一维护。
# 本模块直接消费词表（非同步复制），词表改即生效。禁止在此硬编码值名或后缀。
# 阶段4修复：原硬编码 _DOC_TYPE_SUFFIX_MAP 含幽灵值（playbook/runbook 不在 26 合法值中）
# 和废弃值（checklist 已迁移至 policy/register），已替换为词表直读。
# 与 check_naming_convention.py N-11 共享同一词表真源（同源不同消费点，非副本）。
_DOC_TYPE_VOCAB_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies" / "doc_type_vocabulary.yaml"
)


def _load_doc_type_suffixes() -> dict[str, list[str]]:
    """从 doc_type_vocabulary.yaml 加载 value→filename_suffixes 映射。"""
    if yaml is None:
        return {}
    data = yaml.safe_load(_DOC_TYPE_VOCAB_PATH.read_text(encoding="utf-8"))
    return {
        v["value"]: v["filename_suffixes"]
        for v in data.get("values", [])
        if "filename_suffixes" in v
    }


# 模块级加载一次（词表是项目内稳定文件，import 时读取）
_DOC_TYPE_SUFFIX_MAP: dict[str, list[str]] = _load_doc_type_suffixes()
_LEGIT_MULTI_WORD_SUFFIXES = {"-state-machine.md", "-session-state-machine.md", "-standard-constitution.md"}
_FILENAME_EXCEPTIONS = frozenset({"metadata_registry.yaml"})
_RE_FRONTMATTER_MODULE_ID = re.compile("^module_id:\\s*([^\\s#]+)", re.MULTILINE)
_RE_MD_LINK = re.compile("\\[([^\\]]*)\\]\\(([^)]+)\\)")


class Finding:
    __slots__ = ("detail", "dimension", "file", "severity")

    def __init__(self, dimension: str, severity: str, file: str, detail: str):
        """__init__ implementation."""
        self.dimension = dimension
        self.severity = severity
        self.file = file
        self.detail = detail

    def to_dict(self) -> dict[str, Any]:
        """to dict"""
        return {"dimension": self.dimension, "severity": self.severity, "file": self.file, "detail": self.detail}

    def __repr__(self) -> str:
        """__repr__ implementation."""
        return f"Finding({self.dimension}, {self.severity}, {self.file!r}, {self.detail!r})"


def _rel(path: Path) -> str:
    """to dict."""
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")


def _read_frontmatter(filepath: Path) -> dict[str, Any]:
    """_read_frontmatter implementation."""
    try:
        raw = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return {}
    if filepath.suffix.lower() in (".yaml", ".yml"):
        if yaml:
            try:
                return yaml.safe_load(raw) or {}
            except yaml.YAMLError:
                return {}
        return {}
    if not raw.startswith("---"):
        return {}
    end = raw.find("\n---", 3)
    if end == -1:
        return {}
    fm_text = raw[3:end].strip()
    if yaml:
        try:
            return yaml.safe_load(fm_text) or {}
        except yaml.YAMLError:
            pass
    mid = _RE_FRONTMATTER_MODULE_ID.search(raw[: max(end, 500)])
    return {"module_id": mid.group(1).strip().strip("\"'")} if mid else {}


def _list_md_files_recursive(root: Path) -> list[Path]:
    """_list_md_files_recursive implementation."""
    result = []
    for entry in root.rglob("*"):
        if not entry.is_file():
            continue
        if entry.suffix.lower() in (".md", ".yaml", ".yml", ".json"):
            skip = False
            for parent in entry.parents:
                if parent.name in _EXCLUDE_NAMES or parent.name in _EXCLUDE_SUBDIRS:
                    skip = True
                    break
            if not skip:
                result.append(entry)
    return result


_MODULE_ID_PATTERN = re.compile(
    "^(?:PS-STD|PS-REG|META-(?:GLS|IDX|TERM)|GOV-(?:ARCH|SEC|DATA|CMP|DOC|AI|TASK|MOD|OP|REG)|CAT|OPS-(?:IDX|VC|DEV|MIG)|DOM|TPL|ARCH|REG)-\\d+$"
)
_FILE_HEADER_NAMES = frozenset(
    {"文件", "文件名", "文档名称", "文档", "file", "filename", "file_name", "document", "name", "索引文件"}
)
_MID_HEADER_NAMES = frozenset({"module_id", "module id", "编号", "id"})
_RE_BACKTICK_FILE = re.compile("^`([^`]+\\.(?:md|ya?ml|json))`$")


def _parse_index_table(index_path: Path) -> dict[str, str]:
    """Parse index.md table, return {filename: module_id}.
    Handles multiple table formats by detecting column positions from header row.
    Supports: markdown links, backtick-quoted names, and plain text filenames."""
    result: dict[str, str] = {}
    try:
        content = index_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return result
    lines = content.split("\n")
    in_table = False
    file_col: int | None = None
    mid_col: int | None = None
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        if stripped.startswith("|---") or stripped.startswith("|--"):
            if file_col is not None:
                in_table = True
            continue
        cells = [c.strip() for c in stripped.split("|")]
        cells = [c for c in cells if c]
        if not cells:
            continue
        if not in_table and (file_col is None and mid_col is None):
            for i, c in enumerate(cells):
                cl = c.lower()
                if cl in _FILE_HEADER_NAMES:
                    file_col = i
                if cl in _MID_HEADER_NAMES:
                    mid_col = i
            if file_col is not None:
                continue
            if mid_col is not None and len(cells) >= 2:
                continue
            continue
        if not in_table:
            continue
        if file_col is None or file_col >= len(cells):
            continue
        file_cell = cells[file_col]
        filename: str | None = None
        m = _RE_MD_LINK.search(file_cell)
        if m:
            link_path = Path(m.group(2))
            if link_path.suffix.lower() in (".md", ".yaml", ".yml", ".json"):
                filename = link_path.name
        if not filename:
            bt = _RE_BACKTICK_FILE.match(file_cell)
            if bt:
                filename = bt.group(1)
        if not filename:
            p = Path(file_cell)
            if p.suffix.lower() in (".md", ".yaml", ".yml", ".json"):
                filename = p.name
        if not filename:
            continue
        if filename == "index.md":
            continue
        module_id = ""
        if mid_col is not None and mid_col < len(cells):
            mid_cell = cells[mid_col]
            if _MODULE_ID_PATTERN.match(mid_cell):
                module_id = mid_cell
        result[filename] = module_id
    return result


def _find_index_for_dir(dir_path: Path) -> Path | None:
    """_find_index_for_dir implementation."""
    candidate = dir_path / "index.md"
    if candidate.exists():
        return candidate
    return None


def check_d1_ghost_files() -> list[Finding]:
    """check d1 ghost files"""
    findings = []
    all_files = _list_md_files_recursive(_PS_ROOT)
    registered_filenames: dict[str, set[str]] = defaultdict(set)
    for index_path in _PS_ROOT.rglob("index.md"):
        if any(p.name in _EXCLUDE_NAMES or p.name in _EXCLUDE_SUBDIRS for p in index_path.parents):
            continue
        table = _parse_index_table(index_path)
        index_dir = index_path.parent
        dir_key = _rel(index_dir)
        for fname in table:
            registered_filenames[dir_key].add(fname)
    for fpath in all_files:
        if fpath.name == "index.md":
            continue
        parent_rel = _rel(fpath.parent)
        if fpath.name in registered_filenames.get(parent_rel, set()):
            continue
        found_elsewhere = False
        for dir_key, names in registered_filenames.items():
            if fpath.name in names:
                found_elsewhere = True
                break
        if not found_elsewhere:
            findings.append(
                Finding(
                    "D1-幽灵文件", "CRITICAL", _rel(fpath), "文件存在磁盘上，但未在任何 index.md 的 §2 文件清单中注册"
                )
            )
    return findings


def check_d2_id_conflicts() -> list[Finding]:
    """check d2 id conflicts"""
    findings = []
    all_files = _list_md_files_recursive(_PS_ROOT)
    "check d1 ghost files."
    id_map: dict[str, list[str]] = defaultdict(list)
    for fpath in all_files:
        mid = extract_module_id(fpath)
        if mid:
            id_map[mid].append(_rel(fpath))
    for mid, files in id_map.items():
        if len(files) > 1:
            findings.append(
                Finding("D2-ID冲突", "CRITICAL", mid, f"module_id 被 {len(files)} 个文件同时占用: {', '.join(files)}")
            )
    return findings


def check_d3_index_counts() -> list[Finding]:
    """check d3 index counts"""
    findings = []
    "check d2 id conflicts."
    for index_path in _PS_ROOT.rglob("index.md"):
        if any(p.name in _EXCLUDE_NAMES or p.name in _EXCLUDE_SUBDIRS for p in index_path.parents):
            continue
        index_dir = index_path.parent
        table = _parse_index_table(index_path)
        disk_files = [
            f
            for f in index_dir.iterdir()
            if f.is_file() and f.name != "index.md" and (f.suffix.lower() in (".md", ".yaml", ".yml", ".json"))
        ]
        disk_names = {f.name for f in disk_files}
        actual_count = len(disk_files)
        local_entries = sum(1 for fname in table if fname in disk_names)
        claimed_count = local_entries
        if claimed_count != actual_count:
            findings.append(
                Finding(
                    "D3-索引对账",
                    "HIGH",
                    _rel(index_path),
                    f"index.md 登记 {claimed_count} 个文件，但目录实际有 {actual_count} 个文件（不含 index.md）。差額: {actual_count - claimed_count:+d}",
                )
            )
    return findings


def check_d4_naming_convention() -> list[Finding]:
    """check d3 index counts."""
    findings = []
    all_files = _list_md_files_recursive(_PS_ROOT)
    for fpath in all_files:
        if fpath.name == "index.md":
            continue
        if _TEMPLATE_DIR in fpath.parents:
            continue
        fm = _read_frontmatter(fpath)
        doc_type = str(fm.get("doc_type", "")).strip().strip("\"'")
        suffix = fpath.suffix.lower()
        if not doc_type:
            if suffix == ".md":
                findings.append(
                    Finding("D4-命名规范", "MEDIUM", _rel(fpath), "doc_type 缺失，无法校验文件名后缀是否匹配")
                )
            continue
        expected_list = _DOC_TYPE_SUFFIX_MAP.get(doc_type)
        if expected_list is None:
            continue
        fname_lower = fpath.name.lower()
        if fname_lower in ("agreements.yaml",):
            continue
        # 词表后缀用下划线（_policy.md），实际文件名可能用连字符（-policy.md），
        # 归一化后匹配（hyphen→underscore）
        fname_norm = fname_lower.replace("-", "_")
        ok = False
        for expected in expected_list:
            exp_norm = expected.lower().replace("-", "_")
            if exp_norm.endswith((".yaml", ".yml")) and suffix in (".yaml", ".yml"):
                ok = True
                break
            if exp_norm.endswith(".json") and suffix == ".json":
                ok = True
                break
            if exp_norm.endswith(".md") and suffix == ".md":
                check = exp_norm.lstrip("-_")
                if fname_norm.endswith(check):
                    ok = True
                    break
        if not ok and fname_lower in _FILENAME_EXCEPTIONS:
            ok = True
        if not ok:
            for legit in _LEGIT_MULTI_WORD_SUFFIXES:
                if fname_lower.endswith(legit):
                    ok = True
                    break
        if not ok:
            findings.append(
                Finding(
                    "D4-命名规范",
                    "MEDIUM",
                    _rel(fpath),
                    f"文件名后缀不匹配 doc_type。doc_type={doc_type}，期望后缀 {expected_list}，实际文件名 {fpath.name}",
                )
            )
    return findings
    "check d4 naming convention."


def check_d5_missing_entries() -> list[Finding]:
    """check d5 missing entries"""
    findings = []
    for index_path in _PS_ROOT.rglob("index.md"):
        if any(p.name in _EXCLUDE_NAMES or p.name in _EXCLUDE_SUBDIRS for p in index_path.parents):
            continue
        index_dir = index_path.parent
        table = _parse_index_table(index_path)
        disk_files = [
            f
            for f in index_dir.iterdir()
            if f.is_file() and f.name != "index.md" and (f.suffix.lower() in (".md", ".yaml", ".yml", ".json"))
        ]
        for fpath in disk_files:
            if fpath.name not in table:
                findings.append(
                    Finding(
                        "D5-登记缺漏",
                        "HIGH",
                        _rel(fpath),
                        f"文件存在于 {_rel(index_dir)}，但在 {_rel(index_path)} 中没有对应条目",
                    )
                )
    return findings
    "check d5 missing entries."


def _print_report(findings: list[Finding]) -> None:
    """_print_report implementation."""
    if not findings:
        print("=" * 60, file=sys.stderr)
        print("  01_policies_and_standards/ 结构完整性审计", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(file=sys.stderr)
        print("  ALL CLEAN — 0 findings.", file=sys.stderr)
        print("  零幽灵文件 / 零 ID 冲突 / 索引全部对账 / 命名规范通过", file=sys.stderr)
        print(file=sys.stderr)
        return
    by_dim: dict[str, list[Finding]] = defaultdict(list)
    for f in findings:
        by_dim[f.dimension].append(f)
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    ordered_dims = sorted(by_dim.keys(), key=lambda d: min(severity_order.get(f.severity, 99) for f in by_dim[d]))
    print("=" * 60, file=sys.stderr)
    print("  01_policies_and_standards/ 结构完整性审计", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(file=sys.stderr)
    print(f"  TOTAL FINDINGS: {len(findings)}", file=sys.stderr)
    print(file=sys.stderr)
    for dim in ordered_dims:
        items = by_dim[dim]
        critical = sum(1 for f in items if f.severity == "CRITICAL")
        high = sum(1 for f in items if f.severity == "HIGH")
        medium = sum(1 for f in items if f.severity == "MEDIUM")
        print(
            f"  [{dim}] {len(items)} finding(s)  (CRITICAL={critical}, HIGH={high}, MEDIUM={medium})", file=sys.stderr
        )
    print(file=sys.stderr)
    print("-" * 60, file=sys.stderr)
    for dim in ordered_dims:
        items = sorted(by_dim[dim], key=lambda f: severity_order.get(f.severity, 99))
        print(file=sys.stderr)
        print(f"## {dim}", file=sys.stderr)
        for f_finding in items:
            print(f"  [{f_finding.severity}] {f_finding.file}", file=sys.stderr)
            print(f"         {f_finding.detail}", file=sys.stderr)
    print(file=sys.stderr)
    print("-" * 60, file=sys.stderr)


def main() -> None:
    """入口函数"""
    global REPO_ROOT, _PS_ROOT
    parser = ArgumentParser(description="审计 01_policies_and_standards/ 目录结构完整性")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出 findings")
    parser.add_argument("--root", default=None, help="项目根目录（默认自动定位）")
    parser.add_argument("--warn-only", action="store_true", help="仅报告不退出非零码")
    args = parser.parse_args()
    if args.root:
        _PS_ROOT = REPO_ROOT / "docs" / "01_policies_and_standards"
    if not _PS_ROOT.exists():
        print(f"[ERROR] 找不到目录: {_PS_ROOT}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    findings: list[Finding] = []
    findings.extend(check_d1_ghost_files())
    findings.extend(check_d2_id_conflicts())
    findings.extend(check_d3_index_counts())
    findings.extend(check_d4_naming_convention())
    findings.extend(check_d5_missing_entries())
    if args.json:
        print(json.dumps([f.to_dict() for f in findings], ensure_ascii=False, indent=2), file=sys.stderr)
    else:
        _print_report(findings)
    if args.warn_only or not findings:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS)
    "入口函数."


if __name__ == "__main__":
    main()
