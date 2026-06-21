"""
DM-315: 拆分security/目录到多设计域路径
执行八步工作流的第三步-施工

迁移映射:
  security/llm-security/      → security/llm_defense/llm-security/
  security/llm_security_01/   → security/llm_defense/llm_security_01/
  security/audit-trail/       → observability/audit-trail/
  security/semantic-auditor/  → governance/semantic_audit/
  security/red-blue-validator/→ security/adversarial_validation/
  security/mcp/               → infrastructure/mcp_servers/
"""

import os
import re
import shutil
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(r"D:\ZephyrAlpha")
SRC = ROOT / "src" / "zephyr"

# 迁移映射: (old_subdir, new_base_path_relative_to_src/zephyr/)
MIGRATIONS = [
    ("llm-security", "security/llm_defense/llm-security"),
    ("llm_security_01", "security/llm_defense/llm_security_01"),
    ("audit-trail", "observability/audit-trail"),
    ("semantic-auditor", "governance/semantic_audit"),
    ("red-blue-validator", "security/adversarial_validation"),
    ("mcp", "infrastructure/mcp_servers"),
]

# import路径替换映射: old_prefix → new_prefix
IMPORT_REPLACEMENTS = {
    "zephyr.security.llm_defense.llm_security.": "zephyr.security.llm_defense.llm_security.",
    "zephyr.security.llm_defense.llm_security_01.": "zephyr.security.llm_defense.llm_security_01.",
    "zephyr.observability.audit_trail.": "zephyr.observability.audit_trail.",
    "zephyr.governance.semantic_audit.": "zephyr.governance.semantic_audit.",
    "zephyr.security.adversarial_validation": "zephyr.security.adversarial_validation",
    "zephyr.infrastructure.mcp_servers.": "zephyr.infrastructure.mcp_servers.",
}

# [MODULE]头部替换映射
MODULE_REPLACEMENTS = {
    "zephyr.security.llm_defense.llm_security.": "zephyr.security.llm_defense.llm_security.",
    "zephyr.security.llm_defense.llm_security_01.": "zephyr.security.llm_defense.llm_security_01.",
    "zephyr.observability.audit_trail.": "zephyr.observability.audit_trail.",
    "zephyr.governance.semantic_audit.": "zephyr.governance.semantic_audit.",
    "zephyr.security.adversarial_validation": "zephyr.security.adversarial_validation",
    "zephyr.infrastructure.mcp_servers.": "zephyr.infrastructure.mcp_servers.",
}


def create_target_dirs():
    """创建所有目标目录结构"""
    created = []
    for old_sub, new_rel in MIGRATIONS:
        target = SRC / new_rel
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created.append(str(target))
            print(f"  CREATED: {target}")
        # 确保所有子目录的父目录有__init__.py
        _ensure_init_files(target)
    return created


def _ensure_init_files(directory: Path):
    """确保目录及其所有父目录（在src/zephyr/下）都有__init__.py"""
    rel = directory.relative_to(SRC)
    parts = rel.parts
    current = SRC
    for part in parts:
        current = current / part
        init_file = current / "__init__.py"
        if not init_file.exists() and current.is_dir():
            tmp = init_file.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write("")
            os.replace(str(tmp), str(init_file))
            print(f"  INIT: {init_file}")


def move_files():
    """移动所有文件到目标目录"""
    moved = []
    for old_sub, new_rel in MIGRATIONS:
        old_dir = SRC / "security" / old_sub
        target_dir = SRC / new_rel
        if not old_dir.exists():
            print(f"  SKIP (not found): {old_dir}")
            continue
        for root, dirs, files in os.walk(old_dir):
            rel_from_old = Path(root).relative_to(old_dir)
            dest_dir = target_dir / rel_from_old
            if not dest_dir.exists():
                dest_dir.mkdir(parents=True, exist_ok=True)
            for fname in files:
                src_file = Path(root) / fname
                dst_file = dest_dir / fname
                if dst_file.exists():
                    print(f"  SKIP (exists): {dst_file}")
                    continue
                # 原子写入：先复制再删除原文件
                shutil.copy2(str(src_file), str(dst_file))
                moved.append((str(src_file), str(dst_file)))
                print(f"  MOVED: {src_file} → {dst_file}")
    return moved


def update_imports_in_file(file_path: str) -> list:
    """更新单个文件中的import路径和MODULE头部"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return []

    original = content
    changes = []

    # 替换import语句
    for old_prefix, new_prefix in IMPORT_REPLACEMENTS.items():
        if old_prefix in content:
            content = content.replace(old_prefix, new_prefix)
            changes.append(f"import: {old_prefix} → {new_prefix}")

    # 替换[MODULE]头部
    for old_prefix, new_prefix in MODULE_REPLACEMENTS.items():
        old_module_tag = f"[MODULE] {old_prefix}"
        new_module_tag = f"[MODULE] {new_prefix}"
        if old_module_tag in content:
            content = content.replace(old_module_tag, new_module_tag)
            changes.append(f"MODULE: {old_prefix} → {new_prefix}")

    if content != original:
        tmp_path = file_path + f".{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, file_path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return []

    return changes


def update_all_imports():
    """更新所有.py文件中的import路径"""
    py_files = []
    for root, dirs, files in os.walk(SRC):
        for fname in files:
            if fname.endswith(".py"):
                py_files.append(os.path.join(root, fname))
    # 也扫描scripts和tests
    for scan_dir in [ROOT / "scripts", ROOT / "tests"]:
        if scan_dir.exists():
            for root, dirs, files in os.walk(scan_dir):
                for fname in files:
                    if fname.endswith(".py"):
                        py_files.append(os.path.join(root, fname))

    total_changes = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(update_imports_in_file, f): f for f in py_files}
        for future in as_completed(futures):
            result = future.result()
            if result:
                total_changes.extend(result)

    print(f"  Updated {len(total_changes)} import references in {len(py_files)} files")
    return total_changes


def delete_old_files():
    """删除security/下已迁移的子目录（保留security/本身和access_control/等未迁移目录）"""
    deleted = []
    for old_sub, new_rel in MIGRATIONS:
        old_dir = SRC / "security" / old_sub
        if old_dir.exists():
            # 验证目标目录存在且非空
            target_dir = SRC / new_rel
            if target_dir.exists() and any(target_dir.iterdir()):
                shutil.rmtree(str(old_dir))
                deleted.append(str(old_dir))
                print(f"  DELETED: {old_dir}")
            else:
                print(f"  SKIP DELETE (target empty/missing): {target_dir}")
    return deleted


def main():
    print("=" * 60)
    print("DM-315: 拆分security/目录到多设计域路径")
    print("=" * 60)

    print("\n[1/5] 创建目标目录结构...")
    created = create_target_dirs()

    print("\n[2/5] 移动文件...")
    moved = move_files()
    print(f"  共移动 {len(moved)} 个文件")

    print("\n[3/5] 更新import路径和MODULE头部...")
    changes = update_all_imports()

    print("\n[4/5] 验证目标目录完整性...")
    for old_sub, new_rel in MIGRATIONS:
        target = SRC / new_rel
        py_count = sum(1 for _ in target.rglob("*.py"))
        print(f"  {new_rel}: {py_count} .py files")

    print("\n[5/5] 删除旧目录...")
    deleted = delete_old_files()

    print("\n" + "=" * 60)
    print(f"完成: 创建 {len(created)} 目录, 移动 {len(moved)} 文件, "
          f"更新 {len(changes)} import, 删除 {len(deleted)} 旧目录")
    print("=" * 60)


if __name__ == "__main__":
    main()
