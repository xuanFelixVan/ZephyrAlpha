"""
修复module_id重复问题（第十轮）
用途：修复剩余的3组module_id重复问题
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path("D:/ZephyrAlpha")

DUPLICATES_TO_FIX = [
    {
        "module_id": "BLUEPRINT_001",
        "files": [
            "docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/03_CLEANING/BLUEPRINT.md",
            "docs/05_IMPLEMENTATION/BLUEPRINT.md"
        ],
        "new_ids": [
            "DATA_CLEANING_BLUEPRINT_001",
            "IMPLEMENTATION_BLUEPRINT_001"
        ]
    },
    {
        "module_id": "INDEX_DATABASE_001",
        "files": [
            "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/design/database/INDEX.md",
            "docs/06_ARCHIVE/05_IMPLEMENTATION/database/INDEX.md"
        ],
        "new_ids": [
            "INDEX_DATABASE_DESIGN_001",
            "INDEX_DATABASE_ARCHIVE_001"
        ]
    },
    {
        "module_id": "INDEX_CASE_STUDIES_001",
        "files": [
            "docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/case_studies/INDEX.md",
            "docs/09_AUDIT/CASE_STUDIES/INDEX.md"
        ],
        "new_ids": [
            "INDEX_CASE_STUDIES_OPS_001",
            "INDEX_CASE_STUDIES_AUDIT_001"
        ]
    }
]

def read_file_content(file_path: Path) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

def update_module_id(content: str, old_id: str, new_id: str) -> str:
    return re.sub(
        rf'module_id:\s*{re.escape(old_id)}',
        f'module_id: {new_id}',
        content
    )

def write_file_content(file_path: Path, content: str) -> bool:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False

def main():
    print("=" * 80)
    print("修复module_id重复问题（第十轮）")
    print("=" * 80)
    
    fixed_count = 0
    
    for dup in DUPLICATES_TO_FIX:
        print(f"\n处理重复组: {dup['module_id']}")
        print("-" * 80)
        
        for i, file_path in enumerate(dup['files']):
            full_path = PROJECT_ROOT / file_path
            if not full_path.exists():
                print(f"  [跳过] 文件不存在: {file_path}")
                continue
            
            content = read_file_content(full_path)
            if content is None:
                print(f"  [失败] 无法读取: {file_path}")
                continue
            
            new_id = dup['new_ids'][i]
            new_content = update_module_id(content, dup['module_id'], new_id)
            
            if write_file_content(full_path, new_content):
                print(f"  [成功] {file_path}")
                print(f"         {dup['module_id']} -> {new_id}")
                fixed_count += 1
            else:
                print(f"  [失败] 无法写入: {file_path}")
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"修复文件数: {fixed_count}")

if __name__ == "__main__":
    main()
