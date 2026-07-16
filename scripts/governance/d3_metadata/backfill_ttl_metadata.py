# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/backfill_ttl_metadata.py | §gate-15
# [MODULE] governance.d3_metadata.backfill_ttl_metadata
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance._shared.frontmatter; _shared.constants
# [CONSUMERS] manual batch backfill; stage-2 of ttl root-cause fix
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 按 ttl_vocabulary.yaml decision_tree 二元判定 ttl 值；6 格式统一回填（.md/.py/.sh/.ps1/.mmd/.yaml/.json）；只回填有头部但无 ttl 的文件；原子写入
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无错误）；EXIT_FINDINGS=1（有文件未能回填）；EXIT_ERROR=2（脚本异常）
# [TESTS] 手动测试：dry-run + 全量回填 + GATE-15 校验归零
# [TTL] permanent
"""批量回填/重判 ttl 字段（6 格式统一入口，GATE-15 存量治理 + GATE-VOCAB-CHANGE 纠偏）

对 docs/ + src/ + scripts/ + tests/ 下所有有头部的文件（6 格式），按
ttl_vocabulary.yaml decision_tree 判定 ttl 值：
  - 默认模式：只回填缺 ttl 字段的文件
  - --rejudge 模式：重判已有 ttl 的文件（词表 decision_tree 变更后纠偏用）

6 格式路由（解析器真源：scripts/governance/_shared/frontmatter.py）：
  .md           → parse_frontmatter    → frontmatter 内 ttl: value
  .py/.sh/.ps1/.mmd → parse_py_header  → # [TTL] value 注释行
  .yaml         → parse_byaml_anchor   → # ttl: value 注释行
  .json         → parse_json_meta      → _meta.ttl 字段

判定口径（与 ttl_vocabulary.yaml decision_tree 完全一致，机器可读 criteria 消费）：
  - Q1: 过程性子目录（_working/changes/delivery/reports/09_audit/decomposition）→ task_bound
    注：_archive 已于 commit 87392b2a60 提升为 permanent zone，不再属于过程性子目录
  - Q2: 过程性 doc_type（log/audit_report）→ task_bound（v3.1.0: operational_rule 已合并入 policy）
  - Q3: 永久区路径 → permanent；否则 → task_bound

Usage::

    # dry-run（只报告，不写入）
    python scripts/governance/d3_metadata/backfill_ttl_metadata.py --dry-run

    # 全量回填（缺 ttl 的文件）
    python scripts/governance/d3_metadata/backfill_ttl_metadata.py

    # 重判模式（已有 ttl 的文件也重判，词表变更后纠偏）
    python scripts/governance/d3_metadata/backfill_ttl_metadata.py --rejudge

    # 限定子目录
    python scripts/governance/d3_metadata/backfill_ttl_metadata.py docs/08_knowledge/01_raw_intake/
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 批量回填/重判 ttl 字段（6 格式统一入口，GATE-15 存量治理 + GATE-VOCAB-CHANGE 纠偏）
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json
import os
import re
import sys
from pathlib import Path

# ── 路径设置 ──
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.frontmatter import (  # noqa: E402
    PY_HEADER_PATTERN,
    _FM_END_PATTERN,
    parse_byaml_anchor,
    parse_frontmatter,
    parse_json_meta,
    parse_py_header,
)
from _shared.yaml_utils import evaluate_ttl, load_decision_tree  # noqa: E402

# ttl 判定树——从 ttl_vocabulary.yaml 动态加载（SSoT 唯一真源，禁止硬编码路径前缀）
# 约束：判定逻辑变更只需改 ttl_vocabulary.yaml decision_tree，本脚本自动同步
_DECISION_TREE = load_decision_tree("ttl_vocabulary.yaml")

# frontmatter 结束符正则——从 _shared.frontmatter import（SSoT，不再本地复制）
# ttl 行正则（匹配 frontmatter 内的 ttl: value 行，用于 rejudge 模式替换）
# 支持 ttl: permanent / ttl: "permanent" / ttl: 'permanent' 格式
_TTL_LINE_PATTERN = re.compile(r'^ttl:\s*["\']?[\w]+["\']?\s*$', re.MULTILINE)


def _infer_ttl(rel_path: str, frontmatter: dict | None = None) -> str:
    """按 ttl_vocabulary.yaml decision_tree 判定 ttl 值（机器可读 criteria 消费）。

    向内收：判定逻辑唯一真源为 ttl_vocabulary.yaml decision_tree，本函数零硬编码。
    替换原 _PERMANENT_ZONE_PREFIXES 硬编码路径前缀（治本：changes/等过程文件不再误判 permanent）。

    Args:
        rel_path: 相对 REPO_ROOT 的路径（正斜杠）。
        frontmatter: 文件 frontmatter dict（可选，用于 Q2 doc_type 判定）。

    Returns:
        "permanent" 或 "task_bound"。
    """
    return evaluate_ttl(rel_path, frontmatter, _DECISION_TREE)


def backfill_file(fpath: Path, dry_run: bool = False, rejudge: bool = False) -> str:
    """回填或重判单个文件的 ttl 字段（6 格式统一入口）。

    Args:
        fpath: 文件绝对路径（.md/.py/.sh/.ps1/.mmd/.yaml/.json）。
        dry_run: True 则只报告不写入。
        rejudge: True 则重判已有 ttl 的文件（词表 decision_tree 变更后纠偏用）。

    Returns:
        "backfilled"（已回填缺 ttl）、"rejudged"（已重判 ttl）、
        "skip_has_ttl"（已有 ttl 且 rejudge=False）、
        "skip_unchanged"（rejudge=True 但 ttl 无变化）、
        "skip_no_fm"（无头部）、"error"（异常）。
    """
    try:
        text = fpath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "error"

    suffix = fpath.suffix.lower()

    # 格式路由（向内收——一个函数，多格式解析；解析器真源：_shared/frontmatter.py）
    if suffix == ".md":
        metadata, _ = parse_frontmatter(text)
    elif suffix in (".py", ".sh", ".ps1", ".mmd"):
        metadata = parse_py_header(text)
    elif suffix == ".yaml":
        metadata = parse_byaml_anchor(text)
    elif suffix == ".json":
        metadata = parse_json_meta(text)
    else:
        return "skip_no_fm"  # 不支持的格式

    if not metadata:
        return "skip_no_fm"

    rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
    # 传 metadata 用于 Q2 doc_type 判定（修复原 bug：未传 frontmatter 导致 Q2 失效）
    new_ttl = _infer_ttl(rel_path, metadata)
    current_ttl = metadata.get("ttl")
    current_ttl_str = str(current_ttl).strip().strip('"\'') if current_ttl else ""

    if current_ttl_str:
        # 已有 ttl
        if not rejudge:
            return "skip_has_ttl"
        if current_ttl_str == new_ttl:
            return "skip_unchanged"
        # rejudge 模式：按格式替换 ttl
        new_text = _replace_ttl(text, suffix, new_ttl)
        action = "rejudged"
    else:
        # 缺 ttl：按格式注入 ttl
        new_text = _inject_ttl(text, suffix, new_ttl)
        action = "backfilled"

    if new_text is None:
        return "error"

    if dry_run:
        return action

    # 原子写入（tmp + os.replace，RULE-ONE 并发安全）
    _atomic_write(fpath, new_text)
    return action


# ── ttl 注入/替换：按格式分发（写入逻辑，非解析逻辑）──

# .yaml 治理锚定结束标记（与 _shared/frontmatter.py _BYAML_ANCHOR_END 一致）
_BYAML_ANCHOR_END = "治理锚定结束"

# .py/.sh/.ps1/.mmd 的 # [TTL] 行正则（rejudge 替换用）
_TTL_PY_LINE_PATTERN = re.compile(r"^#\s*\[TTL\]\s?.*$", re.MULTILINE)
# .yaml 的 # ttl: 行正则（rejudge 替换用）
_TTL_YAML_LINE_PATTERN = re.compile(r"^#\s*ttl:\s*.+$", re.MULTILINE)


def _inject_ttl(text: str, suffix: str, ttl_value: str) -> str | None:
    """按格式注入 ttl 字段（缺 ttl 时用）。返回新文本或 None（失败）。"""
    if suffix == ".md":
        return _inject_md_ttl(text, ttl_value)
    if suffix in (".py", ".sh", ".ps1", ".mmd"):
        return _inject_py_ttl(text, ttl_value)
    if suffix == ".yaml":
        return _inject_yaml_ttl(text, ttl_value)
    if suffix == ".json":
        return _inject_json_ttl(text, ttl_value)
    return None


def _replace_ttl(text: str, suffix: str, ttl_value: str) -> str | None:
    """按格式替换 ttl 字段（rejudge 时用）。返回新文本或 None（失败）。"""
    if suffix == ".md":
        return _replace_md_ttl(text, ttl_value)
    if suffix in (".py", ".sh", ".ps1", ".mmd"):
        return _replace_py_ttl(text, ttl_value)
    if suffix == ".yaml":
        return _replace_yaml_ttl(text, ttl_value)
    if suffix == ".json":
        return _replace_json_ttl(text, ttl_value)
    return None


# ── .md 格式（YAML frontmatter）──

def _inject_md_ttl(text: str, ttl_value: str) -> str | None:
    """在 frontmatter 闭合 --- 前插入 ttl: value 行。"""
    if not text.startswith("---"):
        return None
    fm_end_match = _FM_END_PATTERN.search(text[3:])
    if not fm_end_match:
        return None
    end_pos = 3 + fm_end_match.start()
    return text[: end_pos + 1] + f"ttl: {ttl_value}\n" + text[end_pos + 1 :]


def _replace_md_ttl(text: str, ttl_value: str) -> str | None:
    """替换 frontmatter 内的 ttl: 行（限制在 frontmatter 范围内）。"""
    if not text.startswith("---"):
        return None
    fm_end_match = _FM_END_PATTERN.search(text[3:])
    if not fm_end_match:
        return None
    fm_end = 3 + fm_end_match.start()
    fm_text = text[:fm_end]
    body = text[fm_end:]
    new_fm = _TTL_LINE_PATTERN.sub(f"ttl: {ttl_value}", fm_text, count=1)
    return new_fm + body


# ── .py / .sh / .ps1 / .mmd 格式（# [FIELD] value 注释行）──

def _inject_py_ttl(text: str, ttl_value: str) -> str | None:
    """在最后一个 # [FIELD] 行后插入 # [TTL] value 行。"""
    lines = text.splitlines(keepends=True)
    last_header_idx = -1
    for i, line in enumerate(lines[:30]):
        if PY_HEADER_PATTERN.match(line.rstrip()):
            last_header_idx = i
    if last_header_idx < 0:
        return None  # 无头部（parse_py_header 已返回 None，理论不会到此）
    ttl_line = f"# [TTL] {ttl_value}\n"
    lines.insert(last_header_idx + 1, ttl_line)
    return "".join(lines)


def _replace_py_ttl(text: str, ttl_value: str) -> str | None:
    """替换 # [TTL] 行。"""
    new_line = f"# [TTL] {ttl_value}"
    new_text, count = _TTL_PY_LINE_PATTERN.subn(new_line, text, count=1)
    if count == 0:
        return None
    return new_text


# ── .yaml 格式（治理锚定块）──

def _inject_yaml_ttl(text: str, ttl_value: str) -> str | None:
    """在 # --- 治理锚定结束 --- 前插入 # ttl: value 行。"""
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines[:30]):
        if _BYAML_ANCHOR_END in line:
            ttl_line = f"# ttl: {ttl_value}\n"
            lines.insert(i, ttl_line)
            return "".join(lines)
    return None


def _replace_yaml_ttl(text: str, ttl_value: str) -> str | None:
    """替换 # ttl: 行。"""
    new_line = f"# ttl: {ttl_value}"
    new_text, count = _TTL_YAML_LINE_PATTERN.subn(new_line, text, count=1)
    if count == 0:
        return None
    return new_text


# ── .json 格式（_meta 字段）──

def _inject_json_ttl(text: str, ttl_value: str) -> str | None:
    """在 _meta dict 中注入 ttl 字段，重新 dump JSON。"""
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    meta = data.get("_meta")
    if not isinstance(meta, dict):
        return None
    meta["ttl"] = ttl_value
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _replace_json_ttl(text: str, ttl_value: str) -> str | None:
    """替换 _meta 中的 ttl 字段，重新 dump JSON（与 inject 逻辑一致）。"""
    return _inject_json_ttl(text, ttl_value)


def _atomic_write(fpath: Path, content: str) -> None:
    """原子写入文件（tmp + os.replace）。

    确保并发安全：写入过程中崩溃不会留下半截文件。
    """
    tmp_path = fpath.with_suffix(fpath.suffix + ".tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8", newline="\n")
        os.replace(tmp_path, fpath)
    except Exception:
        # 清理 tmp 文件
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise


def _parse_metadata(fpath: Path) -> dict | None:
    """按扩展名路由到 SSoT 解析器，返回 metadata dict（统计用）。"""
    suffix = fpath.suffix.lower()
    try:
        text = fpath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if suffix == ".md":
        metadata, _ = parse_frontmatter(text)
        return metadata
    if suffix in (".py", ".sh", ".ps1", ".mmd"):
        return parse_py_header(text)
    if suffix == ".yaml":
        return parse_byaml_anchor(text)
    if suffix == ".json":
        return parse_json_meta(text)
    return None


def main() -> int:
    # 解析参数
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    rejudge = "--rejudge" in args
    path_args = [a for a in args if not a.startswith("-")]

    # 支持的格式
    valid_suffixes = {".md", ".py", ".sh", ".ps1", ".mmd", ".yaml", ".json"}
    exempt_parts = {"__pycache__", ".git", ".ailocks", "_backups", "_archive",
                    ".aidrafts", ".runtime", "data", "models", ".mypy_cache",
                    ".pytest_cache", ".ruff_cache"}

    # 确定扫描范围
    if path_args:
        # 限定子目录/文件
        scan_dirs = [(REPO_ROOT / p).resolve() for p in path_args]
    else:
        # 全量扫描 docs/ + src/ + scripts/ + tests/
        scan_dirs = [REPO_ROOT / d for d in ("docs", "src", "scripts", "tests")]

    # 收集所有支持格式的文件
    all_files: list[Path] = []
    for scan_dir in scan_dirs:
        if scan_dir.is_file() and scan_dir.suffix.lower() in valid_suffixes:
            all_files.append(scan_dir)
        elif scan_dir.is_dir():
            for fp in scan_dir.rglob("*"):
                if (fp.is_file() and fp.suffix.lower() in valid_suffixes
                        and not any(p in exempt_parts
                                    for p in fp.relative_to(REPO_ROOT).parts)):
                    all_files.append(fp)

    if not all_files:
        print("OK: no files to backfill")
        return EXIT_PASS

    # 统计
    stats = {
        "backfilled": 0,
        "rejudged": 0,
        "skip_has_ttl": 0,
        "skip_unchanged": 0,
        "skip_no_fm": 0,
        "error": 0,
    }
    ttl_changes = {"permanent": 0, "task_bound": 0}

    changed_files: list[str] = []
    for fpath in all_files:
        result = backfill_file(fpath, dry_run=dry_run, rejudge=rejudge)
        stats[result] = stats.get(result, 0) + 1
        if result in ("backfilled", "rejudged"):
            rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
            changed_files.append(rel_path)
            metadata = _parse_metadata(fpath)
            ttl_value = _infer_ttl(rel_path, metadata or {})
            ttl_changes[ttl_value] += 1

    # 输出统计报告
    mode_parts = []
    if dry_run:
        mode_parts.append("DRY-RUN")
    if rejudge:
        mode_parts.append("REJUDGE")
    mode_label = " + ".join(mode_parts) if mode_parts else "APPLIED"
    print(f"\n{'=' * 60}")
    print(f"ttl Backfill/Rejudge Report ({mode_label})")
    print(f"{'=' * 60}")
    print(f"  Total files scanned          : {len(all_files)}")
    print(f"  Backfilled (was missing)     : {stats['backfilled']}")
    print(f"  Rejudged (ttl changed)       : {stats['rejudged']}")
    print(f"    → permanent                : {ttl_changes['permanent']}")
    print(f"    → task_bound               : {ttl_changes['task_bound']}")
    print(f"  Skipped (has ttl, no rejudge) : {stats['skip_has_ttl']}")
    print(f"  Skipped (unchanged)           : {stats['skip_unchanged']}")
    print(f"  Skipped (no header)           : {stats['skip_no_fm']}")
    print(f"  Errors                        : {stats['error']}")
    print(f"{'=' * 60}")

    if dry_run:
        print("\nDry-run complete. Run without --dry-run to apply changes.")
    else:
        print("\nBackfill/Rejudge complete. Run check_frontmatter_metadata.py to verify.")

    # 输出修改的文件列表（供 reconciler/手动纠偏提交用，每行一个相对路径）
    if changed_files:
        print(f"\n=== CHANGED FILES ({len(changed_files)}) ===")
        for f in changed_files:
            print(f)

    if stats["error"] > 0:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
