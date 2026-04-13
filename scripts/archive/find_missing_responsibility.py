# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
查找缺少职责描述的文件
用途：找出所有缺少responsibility字段的文档
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def has_responsibility(content: str) -> bool:
    return bool(re.search(r'^responsibility:', content, re.MULTILINE))

def main():
    print("=" * 80)
    print("查找缺少职责描述的文件")
    print("=" * 80)
    print(f"扫描目录: {DOCS_DIR}")
    print("=" * 80)
    
    missing_files = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = Path(root) / file
            rel_path = file_path.relative_to(DOCS_DIR)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not has_responsibility(content):
                    missing_files.append(str(rel_path))
                    print(f"✗ {rel_path}")
            except Exception as e:
                print(f"? {rel_path}: {str(e)}")
    
    print("\n" + "=" * 80)
    print(f"缺少职责描述的文件数: {len(missing_files)}")
    print("=" * 80)
    
    if missing_files:
        print("\n文件列表:")
        for file_path in missing_files:
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()
