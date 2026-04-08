#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析P1级问题并生成修复建议
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_p1_issues():
    """分析P1级问题"""
    docs_dir = Path("D:/ZephyrAlpha/docs")
    
    # 统计
    version_naming_files = []
    archived_files = []
    missing_module_id_files = []
    
    # 1. 扫描版本号命名文件
    print("=== 扫描版本号命名文件 ===")
    for md_file in docs_dir.rglob("*.md"):
        if re.search(r'_V\d+', md_file.name):
            # 判断是否应该保留版本号
            # 审计报告、临时报告可以保留版本号
            if any(keyword in str(md_file) for keyword in ['audit_state', 'REPORTS', 'ARCHIVE', 'archive']):
                continue  # 跳过审计报告和归档文件
            version_naming_files.append(md_file)
    
    print(f"发现 {len(version_naming_files)} 个需要清理的版本号命名文件")
    
    # 2. 扫描ARCHIVED文档
    print("\n=== 扫描ARCHIVED文档 ===")
    for md_file in docs_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if 'ARCHIVED' in content or 'archived' in md_file.name.lower():
                    # 检查是否在归档目录
                    if '06_ARCHIVE' not in str(md_file) and 'ARCHIVE' not in str(md_file):
                        archived_files.append(md_file)
        except:
            pass
    
    print(f"发现 {len(archived_files)} 个需要归档的文档")
    
    # 3. 扫描缺少module_id的文件
    print("\n=== 扫描缺少module_id的文件 ===")
    for md_file in docs_dir.rglob("*.md"):
        # 跳过归档目录和特殊目录
        if any(keyword in str(md_file) for keyword in ['06_ARCHIVE', '09_ARCHIVE', '99_ARCHIVE', 'archive']):
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if not re.search(r'^module_id:', content, re.MULTILINE):
                    missing_module_id_files.append(md_file)
        except:
            pass
    
    print(f"发现 {len(missing_module_id_files)} 个缺少module_id的文件")
    
    # 生成报告
    print("\n=== P1级问题分析报告 ===")
    print(f"1. 版本号命名混乱: {len(version_naming_files)} 个文件")
    print(f"2. 归档文档未清理: {len(archived_files)} 个文件")
    print(f"3. module_id覆盖率不足: {len(missing_module_id_files)} 个文件")
    
    # 保存详细列表
    report = {
        'version_naming': [str(f.relative_to(docs_dir)) for f in version_naming_files[:20]],
        'archived_files': [str(f.relative_to(docs_dir)) for f in archived_files[:20]],
        'missing_module_id': [str(f.relative_to(docs_dir)) for f in missing_module_id_files[:20]]
    }
    
    return report

if __name__ == "__main__":
    analyze_p1_issues()
