"""
大写文件全量重命名脚本（Wave 1 + Wave 2）
- 使用 git mv 保留历史
- 自动替换全库交叉引用
- 支持 --dry-run 预览

用法：
  python scripts/tools/rename_uppercase_wave.py --dry-run    # 预览
  python scripts/tools/rename_uppercase_wave.py --execute    # 执行
"""
import argparse
import io
import os
import re
import subprocess
import sys
from pathlib import Path

# Windows PowerShell UTF-8 fix
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT = Path('D:/ZephyrAlpha')

FIXED_NAMES = {
    'README.md', 'INDEX.md', 'AGENTS.md', 'CHANGELOG.md',
    'LICENSE', 'SITEMAP.md', 'CONTRIBUTING.md', 'SECURITY.md',
}
EXCLUDE_DIRS = {'.git', '.venv', '.venv-1', '.trae', 'review_materials_package'}
KE_PAT = re.compile(r'^KE-\d{3}-[a-z0-9-]+\.md$')
DR_PAT = re.compile(r'^DR-[A-Z]+-\d{8}-\d{3}\.md$')
SESS_PAT = re.compile(r'^session-\d{8}.*\.md$')

TEXT_EXTS = {'.md', '.yaml', '.yml', '.mdc', '.py', '.json', '.toml'}


def to_lowercase_kebab(name: str) -> str:
    """TECH_DECISION_RECORDS.md → tech-decision-records.md"""
    stem, ext = os.path.splitext(name)
    new_stem = stem.lower().replace('_', '-')
    # collapse multiple hyphens
    new_stem = re.sub(r'-{2,}', '-', new_stem)
    return new_stem + ext.lower()


def collect_files_to_rename() -> list[tuple[Path, Path]]:
    """返回 [(old_path, new_path), ...] 列表"""
    pairs = []
    for fp in ROOT.rglob('*.md'):
        parts_set = set(fp.parts)
        if any(e in parts_set for e in EXCLUDE_DIRS):
            continue
        fname = fp.name
        if fname in FIXED_NAMES:
            continue
        if not re.search(r'[A-Z]', fname):
            continue  # already compliant
        if KE_PAT.match(fname) or DR_PAT.match(fname) or SESS_PAT.match(fname):
            continue  # already compliant special pattern
        new_name = to_lowercase_kebab(fname)
        if new_name == fname:
            continue
        new_path = fp.parent / new_name
        pairs.append((fp, new_path))
    return sorted(pairs, key=lambda p: str(p[0]))


def check_conflicts(pairs: list[tuple[Path, Path]]) -> list[str]:
    """检查目标文件名是否与已存在文件冲突（排除被重命名的文件本身）。
    Windows 文件系统大小写不敏感，需用 os.path.samefile 判断是否同一文件。
    """
    conflicts = []
    for old, new in pairs:
        if new.exists():
            try:
                if os.path.samefile(old, new):
                    continue  # 同一文件在大小写不敏感系统上的正常表现
            except Exception:
                pass
            conflicts.append(f'  [CONFLICT] {old.name} -> {new.name} (target exists: {new})')
    return conflicts


def git_mv(old: Path, new: Path, dry_run: bool) -> bool:
    if dry_run:
        print(f'  [dry] git mv "{old.relative_to(ROOT)}" "{new.relative_to(ROOT)}"')
        return True
    # Try git mv first (tracked files)
    result = subprocess.run(
        ['git', 'mv', str(old), str(new)],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    if result.returncode == 0:
        return True
    # Fallback: os.rename for untracked files
    if 'not under version control' in result.stderr:
        try:
            import shutil
            shutil.move(str(old), str(new))
            print(f'  [os.rename] {old.name} → {new.name} (untracked file)')
            return True
        except Exception as e:
            print(f'  [FAIL] os.rename failed: {e}')
            return False
    print(f'  [FAIL] git mv: {result.stderr.strip()}')
    return False


def update_references(rename_map: dict[str, str], dry_run: bool) -> int:
    """在全库文本文件中替换旧文件名引用，返回修改文件数"""
    modified_count = 0
    for fp in ROOT.rglob('*'):
        if fp.is_dir():
            continue
        if fp.suffix.lower() not in TEXT_EXTS:
            continue
        parts_set = set(fp.parts)
        if any(e in parts_set for e in EXCLUDE_DIRS):
            continue
        try:
            content = fp.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue

        new_content = content
        for old_name, new_name in rename_map.items():
            # replace exact basename occurrences (in links, frontmatter, comments)
            new_content = new_content.replace(old_name, new_name)

        if new_content != content:
            modified_count += 1
            if dry_run:
                # show which replacements happened
                changed = [o for o, n in rename_map.items() if o in content]
                print(f'  [dry] 引用替换: {fp.relative_to(ROOT)} ({", ".join(changed)})')
            else:
                fp.write_text(new_content, encoding='utf-8')

    return modified_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='预览，不实际执行')
    parser.add_argument('--execute', action='store_true', help='实际执行重命名')
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        parser.print_help()
        sys.exit(1)

    dry_run = args.dry_run

    pairs = collect_files_to_rename()
    print(f'\n发现 {len(pairs)} 个需要重命名的大写文件：\n')
    for old, new in pairs:
        print(f'  {old.relative_to(ROOT)}')
        print(f'    → {new.relative_to(ROOT)}')

    if not pairs:
        print('✅ 没有需要重命名的文件')
        sys.exit(0)

    conflicts = check_conflicts(pairs)
    if conflicts:
        print('\n[WARNING] 发现命名冲突，这些文件将被跳过（需人工处理）:')
        for c in conflicts:
            print(c)
        # Remove conflicting pairs from the list, continue with the rest
        conflict_old_names = {c.split(' -> ')[0].split('] ')[1] for c in conflicts}
        pairs = [(old, new) for old, new in pairs if old.name not in conflict_old_names]
        print(f'\n继续执行其余 {len(pairs)} 个非冲突文件...\n')

    # build rename map: {old_basename: new_basename}
    rename_map = {old.name: new.name for old, new in pairs}

    print(f'\n{"[DRY RUN] " if dry_run else ""}开始执行...\n')

    # Step 1: git mv all files
    print('── Step 1: git mv 重命名 ──')
    failed = []
    for old, new in pairs:
        ok = git_mv(old, new, dry_run)
        if not ok:
            failed.append(old)

    if failed:
        print(f'\n[WARNING] {len(failed)} 个文件重命名失败（已跳过）:')
        for f in failed:
            print(f'  {f}')
        print()

    # Step 2: update cross-references
    print(f'\n── Step 2: 交叉引用替换 ──')
    count = update_references(rename_map, dry_run)
    print(f'\n  {"将" if dry_run else "已"}修改 {count} 个文件的引用')

    print(f'\n✅ {"Dry run 完成（未实际修改）" if dry_run else "完成！请执行 git commit"}')
    if not dry_run:
        print('\n建议提交命令：')
        print('  git add -A')
        print('  git commit -m "refactor: rename all legacy uppercase .md files to lowercase kebab-case"')


if __name__ == '__main__':
    main()
