#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理归档文档
将ARCHIVED文档移动到正确的归档目录
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

def clean_archived_documents():
    """清理归档文档"""
    docs_dir = Path("D:/ZephyrAlpha/docs")
    archive_dir = docs_dir / "06_ARCHIVE" / "20260407_p1_cleanup_archive"
    
    # 创建归档目录
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # 统计
    total_files = 0
    archived_files = 0
    
    print("=== 开始清理归档文档 ===\n")
    
    # 遍历所有Markdown文件
    for md_file in docs_dir.rglob("*.md"):
        # 跳过已经在归档目录的文件
        if '06_ARCHIVE' in str(md_file) or '09_ARCHIVE' in str(md_file) or '99_ARCHIVE' in str(md_file):
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                
                # 检查是否包含ARCHIVED标记
                if 'ARCHIVED' in content or 'Archived' in content or 'archived' in md_file.name.lower():
                    total_files += 1
                    
                    # 移动到归档目录
                    dest_path = archive_dir / md_file.name
                    
                    # 如果目标文件已存在，添加时间戳
                    if dest_path.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dest_path = archive_dir / f"{md_file.stem}_{timestamp}{md_file.suffix}"
                    
                    # 移动文件
                    shutil.move(str(md_file), str(dest_path))
                    print(f"  ✅ 归档: {md_file.relative_to(docs_dir)}")
                    archived_files += 1
                    
        except Exception as e:
            print(f"  ❌ 错误: {md_file.name} - {e}")
    
    print(f"\n=== 清理完成 ===")
    print(f"总文件数: {total_files}")
    print(f"归档文件数: {archived_files}")
    print(f"归档目录: {archive_dir}")
    print(f"归档率: {archived_files/total_files*100:.2f}%" if total_files > 0 else "归档率: 0%")

if __name__ == "__main__":
    clean_archived_documents()
