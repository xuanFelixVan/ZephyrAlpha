#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复命名不规范的文件
功能：将不符合规范的文件名改为标准格式
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

# 定义文件重命名映射
RENAME_MAP = {
    'factor_catalog.md': 'FACTOR_CATALOG.md',
    'factor_library_manual.md': 'FACTOR_LIBRARY_MANUAL.md',
    'backtest_standards.md': 'BACKTEST_STANDARDS.md',
    'factor_neutralization.md': 'FACTOR_NEUTRALIZATION.md',
    'factor_preprocessing.md': 'FACTOR_PREPROCESSING.md',
    'factor_return_analysis.md': 'FACTOR_RETURN_ANALYSIS.md',
    'factor_synthesis.md': 'FACTOR_SYNTHESIS.md',
    'ic_analysis.md': 'IC_ANALYSIS.md',
    'research_management.md': 'RESEARCH_MANAGEMENT.md',
    'T.02.FE001.factor_definition.md': 'FACTOR_DEFINITION.md',
    'T.03.RF001.barra_style_factors.md': 'BARRA_STYLE_FACTORS.md',
    'T.03.RF002.industry_factors.md': 'INDUSTRY_FACTORS.md',
    'T.03.RF003.tail_risk_factors.md': 'TAIL_RISK_FACTORS.md',
    'T.03.RM003.barra_optimizer.md': 'BARRA_OPTIMIZER.md',
    'T.03.RM004.factor_transparency_report.md': 'FACTOR_TRANSPARENCY_REPORT.md',
    'factor_master_index.md': 'FACTOR_MASTER_INDEX.md',
    'correlation_matrix.md': 'CORRELATION_MATRIX.md',
    'factor_monitoring.md': 'FACTOR_MONITORING.md'
}

def fix_naming():
    """修复文件命名"""
    print("=" * 80)
    print("修复命名不规范的文件")
    print("=" * 80)
    
    renamed_count = 0
    failed_count = 0
    
    for old_name, new_name in RENAME_MAP.items():
        # 查找文件
        file_path = None
        for root, dirs, files in os.walk(DOCS_DIR / "02_FACTOR_LIBRARY"):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            if old_name in files:
                file_path = os.path.join(root, old_name)
                break
        
        if not file_path:
            print(f"⚠️ 文件不存在: {old_name}")
            failed_count += 1
            continue
        
        try:
            # 重命名文件
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            
            # 检查新文件名是否已存在
            if os.path.exists(new_path):
                print(f"⚠️ 目标文件已存在: {new_name}")
                failed_count += 1
                continue
            
            # 重命名
            os.rename(file_path, new_path)
            
            renamed_count += 1
            print(f"✅ 重命名: {old_name} → {new_name}")
            print(f"   路径: {os.path.relpath(new_path, DOCS_DIR)}")
        
        except Exception as e:
            print(f"❌ 错误: {old_name} - {str(e)}")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"成功重命名: {renamed_count} 个")
    print(f"重命名失败: {failed_count} 个")
    
    return renamed_count, failed_count

def main():
    """主函数"""
    renamed, failed = fix_naming()
    
    print("\n" + "=" * 80)
    print("总结")
    print("=" * 80)
    print(f"总处理文件: {len(RENAME_MAP)} 个")
    print(f"成功重命名: {renamed} 个")
    print(f"重命名失败: {failed} 个")

if __name__ == '__main__':
    main()
