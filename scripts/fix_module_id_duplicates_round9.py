# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
修复module_id重复问题（第九轮）
用途：修复新增的module_id重复问题
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path("D:/ZephyrAlpha")

DUPLICATES_TO_FIX = [
    {
        "module_id": "DATA_QUALITY_MONITORING_BLUEPRINT_001",
        "files": [
            "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_QUALITY_MONITORING_BLUEPRINT.md",
            "docs/01_FRAMEWORK/DATA_QUALITY_MONITORING_BLUEPRINT.md"
        ],
        "new_ids": [
            "DATA_QUALITY_MONITORING_IMPL_001",
            "DATA_QUALITY_MONITORING_FRAMEWORK_001"
        ]
    },
    {
        "module_id": "PORTFOLIO_REBALANCING_BLUEPRINT_001",
        "files": [
            "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_REBALANCING_BLUEPRINT.md",
            "docs/01_FRAMEWORK/PORTFOLIO_REBALANCING_BLUEPRINT.md"
        ],
        "new_ids": [
            "PORTFOLIO_REBALANCING_IMPL_001",
            "PORTFOLIO_REBALANCING_FRAMEWORK_001"
        ]
    },
    {
        "module_id": "BLUEPRINT_001",
        "files": [
            "docs/11_STRATEGIC_DECISION/02_risk_budgeting/风险调整机制.md",
            "docs/11_STRATEGIC_DECISION/04_strategic_adjustment/市场环境评估.md"
        ],
        "new_ids": [
            "RISK_ADJUSTMENT_MECHANISM_001",
            "MARKET_ENVIRONMENT_ASSESSMENT_001"
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
    print("修复module_id重复问题（第九轮）")
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
