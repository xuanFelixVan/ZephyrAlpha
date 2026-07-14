# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/migrate_illegal_doctype.py | §gate-15
# [MODULE] governance.d3_metadata.migrate_illegal_doctype
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance._shared.frontmatter; _shared.constants; _shared.encoding; _shared.yaml_utils
# [CONSUMERS] manual batch migration; stage-2 of doc_type root-cause fix
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 只迁移 frontmatter 内的非法 doc_type 值；不改正文；PENDING_REVIEW 跳过不写入；原子写入
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无错误）；EXIT_FINDINGS=1（有 PENDING_REVIEW 或异常）；EXIT_ERROR=2（脚本异常）
# [TESTS] 手动测试：dry-run + 全量迁移 + 抽样验证
# [TTL] task_bound
"""批量迁移非法 doc_type 值（doc_type 存量治理 Stage 2.2）

扫描全项目（docs/ + src/ + scripts/ + config/ + architecture_model/），
找到 frontmatter 中 doc_type 值为非法的文件，机械替换为合法值。

非法值分两类：
  1. 幽灵值——不在词表 26 合法值中，也不在 7 废弃值中（如 domain_architecture_doc）
     → 用 ILLEGAL_MAP 硬编码映射（源自实测枚举 2026-06-26）
  2. 废弃值——在词表 deprecated_values 中，带 migrated_to 字段
     → 从词表动态加载：单值迁移，多值标 PENDING_REVIEW

无法机械映射的值（如 architecture_discussion、archive）标 PENDING_REVIEW 跳过。

Usage::

    # dry-run（只报告，不写入）
    python scripts/governance/d3_metadata/migrate_illegal_doctype.py --dry-run

    # 全量迁移
    python scripts/governance/d3_metadata/migrate_illegal_doctype.py

    # 限定子目录
    python scripts/governance/d3_metadata/migrate_illegal_doctype.py docs/02_enterprise_architecture/
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 批量迁移非法 doc_type 值（doc_type 存量治理 Stage 2.2）
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


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
from _shared.encoding import ensure_utf8_stdout  # noqa: E402
from _shared.frontmatter import _FM_END_PATTERN, parse_frontmatter  # noqa: E402  # SSoT 治本 2026-07-02 (ARCH-033 Phase 7)
from _shared.yaml_utils import load_vocabulary_deprecated_map, load_vocabulary_values, load_yaml  # noqa: E402  # D-D-05：词表加载收敛到 SSoT

ensure_utf8_stdout()

# _FM_END_PATTERN 已改为从 _shared.frontmatter import（SSoT 治本 2026-07-02, ARCH-033 Phase 7）

# ── 词表路径 ──
_DOC_TYPE_VOCAB_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies" / "doc_type_vocabulary.yaml"
)

# ── 非法值→合法值映射（幽灵值，实测枚举 2026-06-26）──
# 这些值不在词表 26 合法值中，也不在 7 废弃值中
ILLEGAL_MAP: dict[str, str] = {
    # 批量产物（106 个，生成器已在 Stage 1 修复）
    "domain_architecture_doc": "architecture_view",
    "domain_architecture_diagram": "architecture_view",
    # config/ 目录（8+1+1=10 个）
    "rule": "register",
    "capacity_slo": "register",
    "manifest": "register",
    # 拼写规范化（6 个）
    "service_interface_spec": "architecture_view",
    # 报告类（4+2+1+1+1=9 个）
    "governance_report": "audit_report",
    "report": "audit_report",
    "capacity_report": "audit_report",
    "constraint_violations_report": "audit_report",
    "design_vs_production_report": "audit_report",
    # 登记表类（2+1+1=4 个）
    "catalog": "register",
    "registry_of_registries": "register",
    # 去前缀（1 个）
    "architecture_construction_plan": "blueprint",
    # 设计类（1 个）——v2.0.0: design 已废弃，合并到 blueprint
    "architecture_design": "blueprint",
    # 参考数据（3+1=4 个）——v2.0.0: reference 已废弃，按文件实际内容拆分
    "runtime_plane_mapping": "register",
    "cross_domain_matrix": "architecture_view",
    "capability_heatmap": "register",
    "architecture_tree_scope": "register",
    # 记录类（1 个）
    "delivery_record": "audit_report",
    # 索引类（1+1+2=4 个）
    "directory_index": "index",
    "domain_index": "index",
    "task_card_index": "index",
    # 其他单例
    "governance_readme": "index",
    "red_team_corpus": "register",  # v2.0.0: reference 已废弃，red_team_corpus 是配置文件
    "handoff_instruction": "policy",  # v3.1.0: operational_rule 合并入 policy
}

# 无法机械映射的值——需人工裁定
PENDING_REVIEW_VALUES: set[str] = {
    "architecture_discussion",  # 无法确定：design? discussion?
    "archive",  # log/audit_report 二选一，需看内容
}

# 排除目录
_EXCLUDE_DIRS = frozenset({".git", "__pycache__", ".venv", "node_modules", ".mypy_cache", ".trae"})


def _load_legal_values() -> set[str]:
    """从 doc_type_vocabulary.yaml 加载合法值集合（活跃值）。

    D-D-05 治本（2026-06-30）：收敛到 SSoT ``load_vocabulary_values``，
    禁止各脚本复制 _load_xxx() 函数。
    """
    return load_vocabulary_values("doc_type_vocabulary.yaml")


def _load_deprecated_map() -> dict[str, str]:
    """从词表加载废弃值→合法值映射（仅单值 migrated_to）。

    D-D-05 治本（2026-06-30）：收敛到 SSoT ``load_vocabulary_deprecated_map``。
    多值 migrated_to（如 governance_standard→[policy, standard]）映射为 None，
    调用方需过滤 None 值（这些值会被自动归入 PENDING_REVIEW）。
    """
    full_map = load_vocabulary_deprecated_map("doc_type_vocabulary.yaml")
    # 过滤 None（多值/N/A）——保留单值映射，与原逻辑等价
    return {k: v for k, v in full_map.items() if v is not None}


def _get_doc_type(fpath: Path) -> str | None:
    """提取文件的 doc_type 值。

    对 .md 文件解析 frontmatter，对 .yaml/.yml 文件解析顶层 YAML。
    """
    try:
        text = fpath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    if fpath.suffix.lower() == ".md":
        if not text.startswith("---"):
            return None
        metadata, _ = parse_frontmatter(text)
        if not metadata:
            return None
        dt = metadata.get("doc_type")
        return str(dt).strip().strip("\"'") if dt else None

    if fpath.suffix.lower() in (".yaml", ".yml"):
        try:
            data = load_yaml(fpath)
        except Exception:
            return None
        if isinstance(data, dict):
            dt = data.get("doc_type")
            return str(dt).strip().strip("\"'") if dt else None

    return None


def _replace_doctype_in_text(text: str, old_value: str, new_value: str, is_md: bool) -> str | None:
    """在 frontmatter 内替换 doc_type 值。

    Args:
        text: 文件全文。
        old_value: 旧值（非法值）。
        new_value: 新值（合法值）。
        is_md: True=.md 文件（只替换 frontmatter 内），False=.yaml 文件。

    Returns:
        替换后的全文，或 None（未找到匹配）。
    """
    # 构建匹配 doc_type: <old_value> 的正则（支持引号和空格变体）
    pattern = re.compile(
        r'^(doc_type:\s*)["\']?' + re.escape(old_value) + r'["\']?\s*$',
        re.MULTILINE,
    )

    if is_md:
        # .md: 只在 frontmatter 内替换
        if not text.startswith("---"):
            return None
        fm_end_match = _FM_END_PATTERN.search(text[3:])
        if not fm_end_match:
            return None
        end_pos = 3 + fm_end_match.start()
        frontmatter = text[: end_pos + 1]
        new_frontmatter, count = pattern.subn(r"\g<1>" + new_value, frontmatter)
        if count == 0:
            return None
        return new_frontmatter + text[end_pos + 1 :]
    else:
        # .yaml: 全文替换第一个匹配
        new_text, count = pattern.subn(r"\g<1>" + new_value, text)
        if count == 0:
            return None
        return new_text


def _atomic_write(fpath: Path, content: str) -> None:
    """原子写入文件（tmp + os.replace）。"""
    tmp_path = fpath.with_suffix(fpath.suffix + ".tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8", newline="\n")
        os.replace(tmp_path, fpath)
    except Exception:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise


def _is_excluded(fpath: Path) -> bool:
    """检查文件是否在排除目录中。"""
    for parent in fpath.parents:
        if parent.name in _EXCLUDE_DIRS:
            return True
    return False


def main() -> int:
    # 解析参数
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    path_args = [a for a in args if not a.startswith("-")]

    # 加载合法值集合和废弃值映射
    legal_values = _load_legal_values()
    deprecated_map = _load_deprecated_map()

    # 合并映射：ILLEGAL_MAP + deprecated_map（deprecated 单值）
    full_map: dict[str, str] = {**ILLEGAL_MAP, **deprecated_map}

    # PENDING_REVIEW 值集合：硬编码 + 废弃值中多值/N/A 的
    pending_values = set(PENDING_REVIEW_VALUES)
    # 检查 deprecated_values 中哪些没被 full_map 收录（多值/N/A）
    data = load_yaml(_DOC_TYPE_VOCAB_PATH)
    for v in data.get("deprecated_values", []):
        val = v.get("value", "")
        if val not in full_map:
            pending_values.add(val)

    # 确定扫描范围
    scan_roots: list[Path] = []
    if path_args:
        scan_roots = [(REPO_ROOT / p).resolve() for p in path_args]
    else:
        # 全量扫描：docs/ + src/ + scripts/ + config/ + architecture_model/
        for d in ("docs", "src", "scripts", "config", "architecture_model"):
            p = REPO_ROOT / d
            if p.is_dir():
                scan_roots.append(p)

    # 收集文件
    files: list[Path] = []
    for root in scan_roots:
        if root.is_file():
            if root.suffix.lower() in (".md", ".yaml", ".yml") and not _is_excluded(root):
                files.append(root)
        elif root.is_dir():
            for f in root.rglob("*"):
                if f.is_file() and f.suffix.lower() in (".md", ".yaml", ".yml"):
                    if not _is_excluded(f):
                        files.append(f)

    if not files:
        print("OK: no files to scan")
        return EXIT_PASS

    # 统计
    stats = {
        "migrated": 0,
        "pending_review": 0,
        "skip_legal": 0,
        "skip_no_doctype": 0,
        "error": 0,
    }
    migration_detail: dict[str, dict[str, int]] = {}  # old_value → {new_value: count}
    pending_files: list[str] = []

    for fpath in files:
        try:
            dt = _get_doc_type(fpath)
            if dt is None:
                stats["skip_no_doctype"] += 1
                continue

            if dt in legal_values:
                stats["skip_legal"] += 1
                continue

            rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")

            if dt in pending_values:
                stats["pending_review"] += 1
                pending_files.append(f"  {rel_path}  (doc_type={dt})")
                continue

            if dt in full_map:
                new_value = full_map[dt]
                text = fpath.read_text(encoding="utf-8")
                is_md = fpath.suffix.lower() == ".md"
                new_text = _replace_doctype_in_text(text, dt, new_value, is_md)
                if new_text is None:
                    # 理论上不该发生——doc_type 存在但正则没匹配
                    stats["error"] += 1
                    print(f"  ERROR: regex mismatch for {rel_path} (doc_type={dt})")
                    continue

                if not dry_run:
                    _atomic_write(fpath, new_text)

                stats["migrated"] += 1
                detail = migration_detail.setdefault(dt, {})
                detail[new_value] = detail.get(new_value, 0) + 1
            else:
                # 未知非法值——不在 ILLEGAL_MAP 也不在 deprecated
                stats["pending_review"] += 1
                pending_files.append(f"  {rel_path}  (doc_type={dt} [UNKNOWN])")

        except Exception as e:
            stats["error"] += 1
            rel_path = str(fpath.relative_to(REPO_ROOT)).replace("\\", "/")
            print(f"  ERROR: {rel_path}: {e}")

    # 输出统计报告
    mode_label = "DRY-RUN" if dry_run else "APPLIED"
    print(f"\n{'=' * 60}")
    print(f"doc_type Migration Report ({mode_label})")
    print(f"{'=' * 60}")
    print(f"  Total files scanned        : {len(files)}")
    print(f"  Migrated                   : {stats['migrated']}")
    if migration_detail:
        for old_val, new_map in sorted(migration_detail.items()):
            for new_val, count in new_map.items():
                print(f"    {old_val:<35} → {new_val:<20} : {count}")
    print(f"  Pending review             : {stats['pending_review']}")
    print(f"  Skipped (legal doc_type)   : {stats['skip_legal']}")
    print(f"  Skipped (no doc_type)      : {stats['skip_no_doctype']}")
    print(f"  Errors                     : {stats['error']}")
    print(f"{'=' * 60}")

    if pending_files:
        print(f"\nPENDING_REVIEW files ({len(pending_files)}):")
        for line in pending_files:
            print(line)

    if dry_run:
        print("\nDry-run complete. Run without --dry-run to apply changes.")
    else:
        print("\nMigration complete.")

    if stats["error"] > 0 or stats["pending_review"] > 0:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
