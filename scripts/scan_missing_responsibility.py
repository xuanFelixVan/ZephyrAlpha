#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扫描缺少职责描述的文件
功能：扫描所有缺少职责描述的文件并生成报告
"""

import os
import re
from datetime import datetime

def scan_missing_responsibility(root_path):
    """扫描缺少职责描述的文件"""
    missing_files = []
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查是否有职责描述
                if '**核心职责**' not in content and '**本文档职责**' not in content:
                    rel_path = os.path.relpath(file_path, root_path)
                    missing_files.append(rel_path)
            except:
                pass
    
    return missing_files

def main():
    """主函数"""
    root_path = r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'
    
    print("=" * 80)
    print("扫描缺少职责描述的文件")
    print("=" * 80)
    print()
    
    # 扫描缺少职责描述的文件
    missing_files = scan_missing_responsibility(root_path)
    
    print(f"发现 {len(missing_files)} 个缺少职责描述的文件:")
    print()
    
    for i, file_path in enumerate(missing_files, 1):
        print(f"{i}. {file_path}")
    
    print()
    print("=" * 80)
    print(f"扫描完成: 共 {len(missing_files)} 个文件需要补充职责描述")
    print("=" * 80)

if __name__ == '__main__':
    main()
