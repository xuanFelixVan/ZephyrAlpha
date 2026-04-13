#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
查找缺少INDEX.md的目录
"""

from pathlib import Path

DOCS_DIR = Path("D:/ZephyrAlpha/docs")

def find_missing_index():
    """查找缺少INDEX.md的目录"""
    
    print("=" * 80)
    print("查找缺少INDEX.md的目录")
    print("=" * 80)
    
    # 扫描所有目录
    dirs = [d for d in DOCS_DIR.rglob("*") if d.is_dir()]
    
    missing_index = []
    
    for dir_path in dirs:
        # 跳过归档目录和特殊目录
        if 'archive' in str(dir_path).lower() or '_archive' in str(dir_path).lower():
            continue
        
        # 跳过.git目录
        if '.git' in str(dir_path):
            continue
        
        # 检查INDEX.md是否存在
        index_file = dir_path / "INDEX.md"
        if not index_file.exists():
            missing_index.append(str(dir_path.relative_to(DOCS_DIR)))
    
    print(f"\n发现 {len(missing_index)} 个目录缺少INDEX.md:")
    for i, dir_path in enumerate(missing_index, 1):
        print(f"{i}. {dir_path}")
    
    return missing_index

if __name__ == "__main__":
    find_missing_index()
