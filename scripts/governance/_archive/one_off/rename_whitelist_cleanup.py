# [BLUEPRINT] MOD-INF-005 | scripts/governance/rename_whitelist_cleanup.py | §
# [MODULE] scripts.governance.rename_whitelist_cleanup
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] naming_whitelist_cleanup_plan.md Phase 3
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只替换字符串映射中的旧名为新名，不修改文件其他内容
# [MODIFY-GUARD] REPLACEMENTS 列表变更需 Owner 批准
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=有残留
# [TESTS] 无
# [TTL] task_bound
"""命名规范白名单清理 - 全文替换脚本。

按施工方案 docs/_working/audit/research_notes/naming_whitelist_cleanup_plan.md Phase 3 执行。
将所有引用从旧名（大写/kebab）替换为新名（snake_case）。

用法:
  python rename_whitelist_cleanup.py --dry-run    # 预览替换结果（不修改文件）
  python rename_whitelist_cleanup.py              # 执行替换
  python rename_whitelist_cleanup.py --verify     # 验证残留（检查是否还有旧名）
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


# ── _shared 模块 import bootstrap（P2迁移：复用 get_depgraph_pg_connection）──
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection, REPO_ROOT  # noqa: E402

# 替换映射（按字符串长度降序排列，避免短串先匹配破坏长串）
# 注意: 旧名为原始大写/kebab形式，新名为 snake_case。替换已执行完毕，
# 此列表保留原始旧名供 --verify 验证使用（替换脚本运行时会自修改此列表，
# 需手动恢复旧名）。
REPLACEMENTS: list[tuple[str, str]] = [
    # 1. 完整路径（最长）
    ("src/zephyr/shared/SHARED-QUICKREF.yml", "src/zephyr/shared/api/shared_quickref.yaml"),
    # 2. 文件名+扩展名
    ("ARCHITECTURE_LOCK.yaml", "architecture_lock.yaml"),
    ("ARCHITECTURE_LOCK_yaml", "architecture_lock_yaml"),
    ("SHARED-QUICKREF.yml", "shared_quickref.yaml"),
    ("SHARED-QUICKREF_yml", "shared_quickref_yaml"),
    # 3. 纯名称
    ("SHARED-QUICKREF", "shared_quickref"),
    ("ARCHITECTURE_LOCK", "architecture_lock"),
    # 4. 目录名
    ("session-logs", "session_logs"),
]

# scope.yaml 用正则替换（排除 REGISTRY_SCOPE.yaml）
SCOPE_PATTERN = re.compile(r"(?<!REGISTRY_)SCOPE\.yaml")

# 排除目录
EXCLUDE_DIRS: set[str] = {
    ".git", ".aidrafts", ".ailocks", "__pycache__", ".ruff_cache",
    ".mypy_cache", ".pytest_cache", "node_modules", ".venv", "venv",
    ".tox", ".eggs", ".idea", ".vscode", ".trae",
    "session_logs",  # 历史日志不改
    "_archive",
}

# 排除路径前缀
EXCLUDE_PREFIXES: list[str] = [
    "data/asset_index/",
    "data/scans/",
    "data/classified/",
    "data/security_baselines/",
    "docs/08_knowledge/01_raw_intake/",
    "docs/_working/audit/research_notes/",  # 施工方案文档记录旧名→新名映射，不应替换
    "scripts/_archive/",
]

TEXT_EXTENSIONS: set[str] = {".py", ".yaml", ".yml", ".md", ".json", ".txt", ".cfg", ".ini", ".toml"}


def should_skip(rel_path: str) -> bool:
    """检查路径是否应跳过。Windows 大小写不敏感，统一转小写比较。"""
    normalized = rel_path.replace("\\", "/").lower()
    parts = normalized.split("/")
    for part in parts:
        if part in {d.lower() for d in EXCLUDE_DIRS}:
            return True
    for prefix in EXCLUDE_PREFIXES:
        if normalized.startswith(prefix.lower()):
            return True
    return False


def find_candidate_files(self_rel: str) -> list[Path]:
    """用 git grep 快速定位含旧名的文件，避免遍历整个仓库。"""
    # 所有旧名模式（用于 git grep）
    patterns = [old for old, _ in REPLACEMENTS] + ["SCOPE.yaml"]
    candidate_set: set[str] = set()
    for pattern in patterns:
        try:
            result = subprocess.run(
                ["git", "grep", "-l", "--", pattern],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    line = line.strip()
                    if line:
                        candidate_set.add(line)
        except Exception:
            pass
    # 也搜索未跟踪文件（git grep 只搜已跟踪文件）
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            untracked = set(result.stdout.strip().split("\n"))
            for rel in untracked:
                if not rel:
                    continue
                fp = REPO_ROOT / rel
                if not fp.exists() or fp.suffix.lower() not in TEXT_EXTENSIONS:
                    continue
                try:
                    content = fp.read_text(encoding="utf-8-sig", errors="replace")
                except (OSError, UnicodeDecodeError):
                    continue
                for old, _ in REPLACEMENTS:
                    if old in content:
                        candidate_set.add(rel)
                        break
                else:
                    if SCOPE_PATTERN.search(content):
                        candidate_set.add(rel)
    except Exception:
        pass

    # 过滤排除项
    candidates: list[Path] = []
    for rel in sorted(candidate_set):
        if rel == self_rel:
            continue
        if should_skip(rel):
            continue
        p = REPO_ROOT / rel
        if p.exists() and p.suffix.lower() in TEXT_EXTENSIONS:
            candidates.append(p)
    return candidates


def replace_line(line: str) -> tuple[str, int]:
    """替换一行中的内容，返回 (新行, 替换次数)。"""
    count = 0
    new_line = line
    for old, new in REPLACEMENTS:
        if old in new_line:
            count += new_line.count(old)
            new_line = new_line.replace(old, new)
    # scope.yaml 用正则替换（排除 REGISTRY_SCOPE.yaml）
    new_line, scope_count = SCOPE_PATTERN.subn("scope.yaml", new_line)
    count += scope_count
    return new_line, count


def replace_in_file(file_path: Path, dry_run: bool = False) -> int:
    """替换文件中的内容，返回替换次数。"""
    try:
        raw = file_path.read_bytes()
        content = raw.decode("utf-8-sig")
    except (UnicodeDecodeError, PermissionError):
        return 0

    original = content
    count = 0
    lines = content.split("\n")
    new_lines = []
    for line in lines:
        new_line, line_count = replace_line(line)
        count += line_count
        new_lines.append(new_line)
    content = "\n".join(new_lines)

    if content != original and not dry_run:
        tmp_path = file_path.with_suffix(file_path.suffix + ".tmp")
        tmp_path.write_bytes(content.encode("utf-8"))
        os.replace(str(tmp_path), str(file_path))

    return count


def verify_residual(file_path: Path) -> list[str]:
    """检查文件中是否还有旧名残留。"""
    try:
        content = file_path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, PermissionError):
        return []

    residuals: list[str] = []
    for old, _ in REPLACEMENTS:
        if old in content:
            residuals.append(old)
    matches = SCOPE_PATTERN.findall(content)
    if matches:
        residuals.append("scope.yaml (excluding REGISTRY_SCOPE.yaml)")
    return residuals


def update_depgraph(dry_run: bool = False) -> int:
    """更新 depgraph 中的路径记录（Phase 5）。

    执行 4 条 SQL UPDATE，将 nodes 表中的旧路径替换为新路径。
    依据施工方案 §3.4。

    P2迁移后：depgraph 已迁移到 PostgreSQL，连接由 get_depgraph_pg_connection 统一管理。
    """
    # SQL UPDATE 语句（按施工方案 §3.4）
    # 注意: SCOPE.yaml 排除 REGISTRY_SCOPE.yaml
    updates = [
        (
            "ARCHITECTURE_LOCK.yaml -> architecture_lock.yaml",
            "UPDATE nodes SET path = REPLACE(path, 'ARCHITECTURE_LOCK.yaml', 'architecture_lock.yaml') WHERE path LIKE '%ARCHITECTURE_LOCK.yaml%'",
        ),
        (
            "SHARED-QUICKREF.yml -> shared_quickref.yaml",
            "UPDATE nodes SET path = REPLACE(path, 'SHARED-QUICKREF.yml', 'shared_quickref.yaml') WHERE path LIKE '%SHARED-QUICKREF.yml%'",
        ),
        (
            "session-logs -> session_logs",
            "UPDATE nodes SET path = REPLACE(path, 'session-logs', 'session_logs') WHERE path LIKE '%session-logs%'",
        ),
        (
            "SCOPE.yaml -> scope.yaml (excluding REGISTRY_SCOPE.yaml)",
            "UPDATE nodes SET path = REPLACE(path, 'SCOPE.yaml', 'scope.yaml') WHERE path LIKE '%SCOPE.yaml%' AND path NOT LIKE '%REGISTRY_SCOPE.yaml%'",
        ),
    ]

    mode = "[DRY-RUN] " if dry_run else ""
    total_changes = 0

    if dry_run:
        # dry-run: 只查询受影响的行数，不执行 UPDATE
        conn = get_depgraph_pg_connection(autocommit=True)
        try:
            for desc, sql in updates:
                # 将 UPDATE ... REPLACE ... WHERE ... 转为 SELECT COUNT(*)
                # 提取 WHERE 子句
                where_idx = sql.find("WHERE")
                where_clause = sql[where_idx:] if where_idx >= 0 else ""
                select_sql = f"SELECT COUNT(*) AS cnt FROM nodes {where_clause}"
                cur = conn.execute(select_sql)
                count = cur.fetchone()["cnt"]
                print(f"  {mode}{desc}: {count} rows affected")
                total_changes += count
        finally:
            conn.close()
        print(f"\n{mode}总计: {total_changes} rows would be updated")
        return 0

    conn = get_depgraph_pg_connection(autocommit=False)
    try:
        for desc, sql in updates:
            cur = conn.execute(sql)
            changes = cur.rowcount
            print(f"  {desc}: {changes} rows updated")
            total_changes += changes
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] SQL failed: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    print(f"\n总计: {total_changes} rows updated")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="命名规范白名单清理替换脚本")
    parser.add_argument("--dry-run", action="store_true", help="预览替换结果，不修改文件")
    parser.add_argument("--verify", action="store_true", help="验证残留检查")
    parser.add_argument("--update-depgraph", action="store_true", help="更新 depgraph 路径记录 (Phase 5)")
    args = parser.parse_args()

    if args.update_depgraph:
        return update_depgraph(dry_run=args.dry_run)

    if args.verify:
        # 跳过自身（脚本包含旧名用于验证）
        self_rel = str(Path(__file__).resolve().relative_to(REPO_ROOT)).replace("\\", "/")
        candidates = find_candidate_files(self_rel)
        total_residuals = 0
        for file_path in candidates:
            rel_path = str(file_path.relative_to(REPO_ROOT)).replace("\\", "/")
            residuals = verify_residual(file_path)
            if residuals:
                total_residuals += 1
                print(f"  {rel_path}: {residuals}")
        if total_residuals == 0:
            print("验证通过：无残留旧名")
        else:
            print(f"\n发现 {total_residuals} 个文件有残留旧名")
        return 0 if total_residuals == 0 else 1

    total_replaced = 0
    files_modified = 0
    # 跳过自身（脚本包含旧名用于验证，不能被替换）
    self_rel = str(Path(__file__).resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    candidates = find_candidate_files(self_rel)
    print(f"找到 {len(candidates)} 个候选文件")

    for file_path in candidates:
        rel_path = str(file_path.relative_to(REPO_ROOT)).replace("\\", "/")
        count = replace_in_file(file_path, dry_run=args.dry_run)
        if count > 0:
            files_modified += 1
            total_replaced += count
            mode = "[DRY-RUN] " if args.dry_run else ""
            print(f"  {mode}{rel_path}: {count} replacements")

    mode = "[DRY-RUN] " if args.dry_run else ""
    print(f"\n{mode}总计: {files_modified} 个文件, {total_replaced} 处替换")
    return 0


if __name__ == "__main__":
    sys.exit(main())
