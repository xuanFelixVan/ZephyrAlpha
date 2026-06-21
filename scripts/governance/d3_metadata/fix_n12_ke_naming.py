# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/fix_n12_ke_naming.py | §
# [MODULE] scripts.governance.d3_metadata.fix_n12_ke_naming
# [INVARIANTS] N-12 target pattern: ^ke-\d{3}-[a-z][a-z0-9-]+\.md$; sequence numbers are 3-digit zero-padded starting from 001; content never modified
# [MODIFY-GUARD] _CATEGORY_PREFIXES, _CATEGORY_AND_SECTION_RE changes require Owner approval
# [CONSUMERS] check_naming_convention.py N-12; pre_commit GATE-11
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=clean/no violations; exit 1=violations found (dry-run); exit 2=usage error; exit 3=apply errors
# [TESTS] tests/unit/test_gate11_naming_convention.py
"""修复 N-12 KE 条目命名违规 — 将旧格式重命名为 ke-NNN-kebab-title.md。

旧格式示例:
  ke-agent-inst-6-15-002.md          → ke-002-drift-immune-arc.md
  ke-documentat-1-2-iso-42010-004.md → ke-004-iso-42010-four-elements.md
  ke-governance-5-008-2.md           → ke-008-revision_history.md
  ke-module-blu-3-1-001.md           → ke-001-audit-dimension-classification.md

目标格式: ke-NNN-kebab-title.md
  NNN = 三位零填充序号（001-999）
  kebab-title = 从文件名提取的语义标题（kebab-case，不含类别前缀和章节号）
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

KE_TARGET_PATTERN = re.compile(r"^ke-\d{3}-[a-z][a-z0-9-]+\.md$")

_CATEGORY_PREFIXES: list[str] = [
    "agent-inst-",
    "documentat-",
    "governance-",
    "module-blu-",
    "session-lo-",
    "knowledge--",
    "test-cover-",
]

# 匹配 "类别前缀+章节号-" 整体前缀，一步剥离
# 章节号格式: N / N-N / N-N-N 等（纯数字段，用 - 连接）
# 关键: 章节号段是纯数字（如 6-15），语义标题段含字母（如 audit-gate-ent）
# 正则策略: 匹配 "类别前缀-" 后跟可选字母段+数字段链 的模式
_CATEGORY_AND_SECTION_RE: list[re.Pattern[str]] = [
    # agent-inst-N-N-...-N- (纯数字章节号链)
    re.compile(r"^agent-inst-(?:\d+-)+"),
    # documentat-N-N-...-N- 或 documentat-ter-N-...-N- (bis/ter等后缀)
    re.compile(r"^documentat-(?:[a-z]+-)?(?:\d+-)+"),
    # governance-N-N-...-N- 或 governance-a-N-...-N-
    re.compile(r"^governance-(?:[a-z]+-)?(?:\d+-)+"),
    # module-blu-N-N-...-N- 或 module-blu-p0-N-...-N-
    re.compile(r"^module-blu-(?:[a-z]+-)?(?:\d+-)+"),
    # session-lo-N-N-...-N- 或 session-lo-bug-N-
    re.compile(r"^session-lo-(?:[a-z]+-)?(?:\d+-)+"),
    # knowledge--N-N-...-N-
    re.compile(r"^knowledge--(?:\d+-)+"),
    # test-cover-unknown-N-...-N-
    re.compile(r"^test-cover-[a-z]+-(?:\d+-)+"),
]

_MULTI_HYPHEN_RE = re.compile(r"-{2,}")


@dataclass
class RenamePlan:
    old_path: Path
    new_path: Path
    old_name: str
    new_name: str
    seq_num: int
    extracted_title: str
    reason: str


@dataclass
class RefUpdate:
    file_path: Path
    line_num: int
    old_ref: str
    new_ref: str


@dataclass
class FixSummary:
    total_scanned: int = 0
    already_compliant: int = 0
    violations_found: int = 0
    renames_planned: int = 0
    renames_applied: int = 0
    renames_failed: int = 0
    ref_updates_planned: int = 0
    ref_updates_applied: int = 0
    ref_updates_failed: int = 0
    rename_plans: list[RenamePlan] = field(default_factory=list)
    ref_updates: list[RefUpdate] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 序号提取
# ---------------------------------------------------------------------------

def _extract_sequence(stem: str) -> int | None:
    """从 KE 文件名 stem 中提取序号。

    策略:
    1. 匹配末尾 -NNN 模式（三位数字，如 -002, -008, -000）
    2. 如果末尾是 -NNN-N（三位数字+1位后缀），取三位数字部分
    3. 如果末尾是 -N 或 -NN（1-2位数字），可能是章节号而非序号，
       继续向前查找三位数字序号
    4. 如果找不到三位数字序号，使用末尾数字作为序号
    """
    # 优先匹配 -NNN-N 模式（三位序号+后缀版本号，如 -008-2）
    m = re.search(r"-(\d{3})-\d+$", stem)
    if m:
        return int(m.group(1))
    # 其次匹配 -NNN 尾部模式（三位序号，如 -002）
    m = re.search(r"-(\d{3})$", stem)
    if m:
        return int(m.group(1))
    # 回退: 匹配末尾 -N 或 -NN（可能是序号，如 -5, -15）
    m = re.search(r"-(\d{1,2})$", stem)
    if m:
        return int(m.group(1))
    return None


# ---------------------------------------------------------------------------
# 标题提取
# ---------------------------------------------------------------------------

def _extract_title(stem: str) -> str:
    """从 KE 文件名 stem 中提取语义标题。

    策略:
    1. 去掉 "ke-" 前缀
    2. 用 _CATEGORY_AND_SECTION_RE 一步剥离 "类别+章节号-" 前缀
    3. 如果上一步没匹配，尝试单独剥离类别前缀
    4. 去掉尾部序号（-NNN 或 -NNN-N）
    5. 清理连续连字符、首尾连字符
    6. 如果结果为空或仅数字，使用类别名作为标题
    """
    body = stem

    # Step 0: 去掉 "ke-" 前缀
    if body.startswith("ke-"):
        body = body[3:]

    # Step 1: 一步剥离 "类别+章节号-" 前缀
    stripped = False
    for pat in _CATEGORY_AND_SECTION_RE:
        m = pat.match(body)
        if m:
            body = body[m.end():]
            stripped = True
            break

    # Step 2: 如果没匹配到章节号模式，尝试单独剥离类别前缀
    if not stripped:
        for prefix in _CATEGORY_PREFIXES:
            if body.startswith(prefix):
                body = body[len(prefix):]
                break

    # Step 3: 去掉尾部序号
    body = re.sub(r"-\d{1,3}(?:-\d+)?$", "", body)

    # Step 4: 清理
    body = _MULTI_HYPHEN_RE.sub("-", body)
    body = body.strip("-")

    # Step 5: 空标题回退
    if not body or re.match(r"^\d+$", body):
        for prefix in _CATEGORY_PREFIXES:
            if stem.startswith("ke-" + prefix):
                body = prefix.rstrip("-")
                break
        else:
            body = "untitled"

    if len(body) > 60:
        body = body[:60].rstrip("-")

    return body


# ---------------------------------------------------------------------------
# 新文件名生成
# ---------------------------------------------------------------------------

def _generate_new_name(stem: str, assigned_seq: int) -> tuple[str, int, str]:
    """生成合规的新文件名。

    Args:
        stem: 原文件名 stem（小写，无扩展名）
        assigned_seq: 分配的序号（已确保唯一）

    Returns:
        (new_filename, sequence_number, extracted_title)
    """
    title = _extract_title(stem)
    new_name = f"ke-{assigned_seq:03d}-{title}.md"
    return new_name, assigned_seq, title


# ---------------------------------------------------------------------------
# 扫描与规划
# ---------------------------------------------------------------------------

def _scan_ke_files(docs_dir: Path) -> list[Path]:
    """扫描 docs/ 下所有 ke-*.md 文件（路径含 knowledge 或 08_knowledge）。"""
    ke_files: list[Path] = []
    for root, _dirs, files in os.walk(docs_dir):
        root_path = Path(root)
        rel = str(root_path).replace("\\", "/").lower()
        if "knowledge" not in rel and "08_knowledge" not in rel:
            continue
        for f in sorted(files):
            if f.lower().startswith("ke-") and f.lower().endswith(".md"):
                ke_files.append(root_path / f)
    return ke_files


def _find_next_available_seq(used_seqs: set[int]) -> int:
    """找到下一个可用的序号（从 1 开始）。"""
    seq = 1
    while seq in used_seqs:
        seq += 1
    return seq


def plan_renames(docs_dir: Path) -> FixSummary:
    """扫描所有 KE 文件，生成重命名计划。

    序号分配策略:
    1. 已合规文件: 保留原序号，标记为已占用
    2. 违规文件: 优先使用从文件名提取的序号（若未被占用且在1-999范围内）
    3. 提取的序号已被占用或无效: 分配下一个可用序号
    """
    summary = FixSummary()
    ke_files = _scan_ke_files(docs_dir)
    summary.total_scanned = len(ke_files)

    used_seqs: set[int] = set()
    all_plans: list[RenamePlan] = []

    for fpath in ke_files:
        name = fpath.name
        stem = fpath.stem.lower()

        if KE_TARGET_PATTERN.match(name.lower()):
            summary.already_compliant += 1
            m = re.match(r"^ke-(\d{3})-", name.lower())
            if m:
                used_seqs.add(int(m.group(1)))
            continue

        summary.violations_found += 1

        extracted_seq = _extract_sequence(stem)
        if extracted_seq is not None and extracted_seq not in used_seqs and 1 <= extracted_seq <= 999:
            assigned_seq = extracted_seq
        else:
            assigned_seq = _find_next_available_seq(used_seqs)

        new_name, seq, title = _generate_new_name(stem, assigned_seq)

        new_path = fpath.parent / new_name

        collision_suffix = 0
        while new_path.exists() and new_path != fpath:
            collision_suffix += 1
            alt_title = f"{title}-{collision_suffix}"
            alt_name = f"ke-{seq:03d}-{alt_title}.md"
            new_path = fpath.parent / alt_name
            new_name = alt_name

        used_seqs.add(seq)

        plan = RenamePlan(
            old_path=fpath,
            new_path=new_path,
            old_name=name,
            new_name=new_name,
            seq_num=seq,
            extracted_title=title,
            reason=f"N-12 violation: {name} → {new_name}",
        )
        all_plans.append(plan)

    summary.renames_planned = len(all_plans)
    summary.rename_plans = all_plans
    return summary


# ---------------------------------------------------------------------------
# 引用更新
# ---------------------------------------------------------------------------

def _find_references(project_root: Path, old_name: str) -> list[RefUpdate]:
    """在项目中搜索对旧文件名的引用。"""
    refs: list[RefUpdate] = []
    old_stem = Path(old_name).stem

    try:
        result = subprocess.run(
            ["rg", "--line-number", "--no-heading",
             "-e", re.escape(old_name), "-e", re.escape(old_stem),
             "--glob", "!{.git,__pycache__,.ruff_cache,.mypy_cache}/**",
             str(project_root)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0 and result.stdout:
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split(":", 2)
                if len(parts) < 3:
                    continue
                file_path_str, line_num_str, _content = parts[0], parts[1], parts[2]
                file_path = Path(file_path_str)
                try:
                    line_num = int(line_num_str)
                except ValueError:
                    continue
                if file_path.name == old_name and file_path.parent.name in ("01_raw_intake", "04_archived", "02_triaged"):
                    continue
                if ".git" in str(file_path) or "__pycache__" in str(file_path):
                    continue
                refs.append(RefUpdate(
                    file_path=file_path,
                    line_num=line_num,
                    old_ref=old_name,
                    new_ref="",
                ))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return refs


def _update_references_in_file(file_path: Path, old_name: str, new_name: str, old_stem: str, new_stem: str) -> bool:
    """在单个文件中替换旧文件名引用为新文件名。"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False

    new_content = content.replace(old_name, new_name)
    new_content = new_content.replace(old_stem, new_stem)

    if new_content == content:
        return True

    try:
        tmp_path = f"{file_path}.{os.getpid()}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_path, file_path)
        return True
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return False


# ---------------------------------------------------------------------------
# 执行重命名
# ---------------------------------------------------------------------------

def _atomic_rename(old_path: Path, new_path: Path) -> bool:
    """原子重命名文件。"""
    try:
        os.rename(old_path, new_path)
        return True
    except OSError:
        return False


def apply_renames(summary: FixSummary, project_root: Path) -> FixSummary:
    """执行重命名和引用更新。"""
    for plan in summary.rename_plans:
        success = _atomic_rename(plan.old_path, plan.new_path)
        if success:
            summary.renames_applied += 1
        else:
            summary.renames_failed += 1
            summary.errors.append(f"RENAME FAILED: {plan.old_path} → {plan.new_path}")
            continue

        old_stem = plan.old_name.rsplit(".", 1)[0]
        new_stem = plan.new_name.rsplit(".", 1)[0]

        refs = _find_references(project_root, plan.old_name)
        for ref in refs:
            ref.new_ref = plan.new_name
            ok = _update_references_in_file(ref.file_path, plan.old_name, plan.new_name, old_stem, new_stem)
            if ok:
                summary.ref_updates_applied += 1
            else:
                summary.ref_updates_failed += 1
                summary.errors.append(f"REF UPDATE FAILED: {ref.file_path}:{ref.line_num}")

        summary.ref_updates_planned += len(refs)
        summary.ref_updates.extend(refs)

    return summary


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------

def _print_summary(summary: FixSummary, dry_run: bool) -> None:
    """打印摘要。"""
    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"\n{'='*70}")
    print(f"N-12 KE Naming Fix - {mode} Mode Summary")
    print(f"{'='*70}")
    print(f"  Total KE files scanned:    {summary.total_scanned}")
    print(f"  Already compliant:         {summary.already_compliant}")
    print(f"  Violations found:          {summary.violations_found}")
    print(f"  Renames planned:           {summary.renames_planned}")

    if not dry_run:
        print(f"  Renames applied:           {summary.renames_applied}")
        print(f"  Renames failed:            {summary.renames_failed}")
        print(f"  Ref updates planned:       {summary.ref_updates_planned}")
        print(f"  Ref updates applied:       {summary.ref_updates_applied}")
        print(f"  Ref updates failed:        {summary.ref_updates_failed}")

    if summary.rename_plans:
        print(f"\n{'-'*70}")
        print("Rename Plans:")
        print(f"{'-'*70}")
        for i, plan in enumerate(summary.rename_plans, 1):
            print(f"  {i:4d}. {plan.old_name}")
            print(f"        -> {plan.new_name}")
            print(f"        (seq={plan.seq_num:03d}, title=\"{plan.extracted_title}\")")

    if summary.errors:
        print(f"\n{'-'*70}")
        print("Errors:")
        print(f"{'-'*70}")
        for err in summary.errors:
            print(f"  ERR: {err}")

    print(f"{'='*70}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fix N-12 KE entry naming violations (ke-NNN-kebab-title.md)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=True,
        help="Show what would change without modifying (default)",
    )
    parser.add_argument(
        "--apply", action="store_true", default=False,
        help="Actually make changes",
    )
    parser.add_argument(
        "--docs-dir", type=str, default=None,
        help="docs/ directory path (auto-detected by default)",
    )
    parser.add_argument(
        "--project-root", type=str, default=None,
        help="Project root path (auto-detected by default)",
    )
    args = parser.parse_args()

    apply_mode = args.apply
    if apply_mode:
        args.dry_run = False

    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = Path(__file__).resolve().parents[3]

    if args.docs_dir:
        docs_dir = Path(args.docs_dir).resolve()
    else:
        docs_dir = project_root / "docs"

    if not docs_dir.exists():
        print(f"ERROR: docs directory not found: {docs_dir}", file=sys.stderr)
        return 2

    print(f"Scanning KE files in: {docs_dir}")
    print(f"Project root: {project_root}")
    print(f"Mode: {'APPLY' if apply_mode else 'DRY-RUN'}")

    summary = plan_renames(docs_dir)

    if apply_mode and summary.rename_plans:
        summary = apply_renames(summary, project_root)

    _print_summary(summary, dry_run=not apply_mode)

    if summary.violations_found > 0 and not apply_mode:
        return EXIT_FINDINGS

    if summary.errors:
        return 3

    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
