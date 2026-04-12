#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
删除无内容的模板文件并更新索引
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

# 需要删除的文件列表（内容完全相同的模板文件）
FILES_TO_DELETE = [
    # 第1组：6个文件内容相同
    '01_STANDARDS/factor_neutralization.md',
    '01_STANDARDS/factor_preprocessing.md',
    '01_STANDARDS/factor_return_analysis.md',
    '01_STANDARDS/factor_synthesis.md',
    '01_STANDARDS/ic_analysis.md',
    # 第2组：2个文件内容相同
    '01_STANDARDS/FACTOR_SCREENING_STRATEGY.md',
    # 第3组：2个文件内容相同
    '01_STANDARDS/FACTOR_VALIDATION_GUIDE.md',
    # 第4组：3个文件内容相同
    '04_DATA_SOURCE/IFIND_CONNECTOR.md',
    '04_DATA_SOURCE/SUPERCMD_CONNECTOR.md',
    # 第5组：2个文件内容相同
    '05_BACKTEST/OVERFITTING_TEST.md',
]

def check_file_content(file_path):
    """检查文件是否有实际内容"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否有实际内容（除了YAML头部和变更记录）
        # 移除YAML头部
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        
        # 移除变更记录
        content = re.sub(r'## 变更记录.*$', '', content, flags=re.DOTALL)
        content = re.sub(r'## 更新记录.*$', '', content, flags=re.DOTALL)
        
        # 移除表格
        content = re.sub(r'\|.*\|', '', content)
        
        # 移除空白行和特殊字符
        content = re.sub(r'[\s\-\|]+', '', content)
        
        # 如果剩余内容少于50个字符，认为是模板文件
        return len(content) < 50
    
    except Exception as e:
        print(f"  检查错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("删除无内容的模板文件")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    deleted_count = 0
    skipped_count = 0
    
    for file_rel_path in FILES_TO_DELETE:
        file_path = FACTOR_LIBRARY / file_rel_path
        
        print(f"\n检查: {file_rel_path}")
        
        if not file_path.exists():
            print(f"  文件不存在，跳过")
            skipped_count += 1
            continue
        
        # 检查文件内容
        if check_file_content(file_path):
            print(f"  确认为模板文件，准备删除")
            
            # 删除文件
            try:
                file_path.unlink()
                print(f"  ✓ 已删除")
                deleted_count += 1
            except Exception as e:
                print(f"  ✗ 删除失败: {e}")
        else:
            print(f"  文件有实际内容，保留")
            skipped_count += 1
    
    print("\n" + "=" * 80)
    print("删除完成")
    print("=" * 80)
    print(f"删除文件: {deleted_count}")
    print(f"跳过文件: {skipped_count}")

if __name__ == '__main__':
    main()
