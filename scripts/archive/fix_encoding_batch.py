# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
修复编码问题文件脚本
用途：将编码问题的文件转换为UTF-8编码
创建时间：2026-04-07
"""

import os
import chardet
from pathlib import Path
from typing import Tuple
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def detect_encoding(file_path: Path) -> str:
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        result = chardet.detect(raw_data)
        return result['encoding']
    except Exception:
        return 'utf-8'

def fix_encoding(file_path: Path) -> Tuple[bool, str]:
    try:
        encoding = detect_encoding(file_path)
        
        if encoding.lower() == 'utf-8':
            return True, "已是UTF-8编码"
        
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"已从{encoding}转换为UTF-8"
        
    except Exception as e:
        return False, f"处理失败: {str(e)}"

def main():
    print("=" * 80)
    print("修复编码问题文件")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"扫描目录: {DOCS_DIR}")
    print("=" * 80)
    
    stats = {
        "total_files": 0,
        "already_utf8": 0,
        "fixed": 0,
        "failed": 0
    }
    
    failed_files = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = Path(root) / file
            rel_path = file_path.relative_to(DOCS_DIR)
            
            stats["total_files"] += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read()
                stats["already_utf8"] += 1
            except UnicodeDecodeError:
                success, message = fix_encoding(file_path)
                
                if success:
                    stats["fixed"] += 1
                    print(f"✓ {rel_path}: {message}")
                else:
                    stats["failed"] += 1
                    failed_files.append((str(rel_path), message))
                    print(f"✗ {rel_path}: {message}")
    
    print("\n" + "=" * 80)
    print("处理完成")
    print("=" * 80)
    print(f"总文件数: {stats['total_files']}")
    print(f"已是UTF-8: {stats['already_utf8']}")
    print(f"已修复: {stats['fixed']}")
    print(f"失败: {stats['failed']}")
    
    if failed_files:
        print("\n失败文件列表:")
        for file_path, message in failed_files:
            print(f"  - {file_path}: {message}")
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
