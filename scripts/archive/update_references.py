#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
更新引用链接脚本
功能：检查并更新所有引用重命名文件的链接
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state"

# 重命名映射
RENAME_MAPPING = {
    '资产类别定义.md': 'ASSET_CLASS_DEFINITION.md',
    '资产配置模型.md': 'ASSET_ALLOCATION_MODEL.md',
    '配置优化方法.md': 'ALLOCATION_OPTIMIZATION_METHOD.md',
    '风险调整机制.md': 'RISK_ADJUSTMENT_MECHANISM.md',
    '风险预算方法.md': 'RISK_BUDGETING_METHOD.md',
    '策略评估标准.md': 'STRATEGY_EVALUATION_CRITERIA.md',
    '市场环境评估.md': 'MARKET_ENVIRONMENT_ASSESSMENT.md',
    '战略调整机制.md': 'STRATEGIC_ADJUSTMENT_MECHANISM.md',
    '调整触发条件.md': 'ADJUSTMENT_TRIGGER_CONDITIONS.md'
}

def find_references_to_renamed_files():
    """查找引用重命名文件的链接"""
    references = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, DOCS_DIR)
            
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查是否引用了重命名的文件
                for old_name, new_name in RENAME_MAPPING.items():
                    if old_name in content:
                        references.append({
                            'file': rel_path,
                            'old_name': old_name,
                            'new_name': new_name
                        })
            except Exception as e:
                print(f"读取文件失败: {rel_path}, 错误: {str(e)}")
    
    return references

def update_references_in_file(file_path, old_name, new_name):
    """更新文件中的引用"""
    try:
        abs_path = DOCS_DIR / file_path
        
        with open(abs_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 替换引用
        new_content = content.replace(old_name, new_name)
        
        if new_content != content:
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, f"已更新引用: {old_name} -> {new_name}"
        else:
            return False, "未找到引用"
    
    except Exception as e:
        return False, f"错误: {str(e)}"

def main():
    """主函数"""
    print("=" * 80)
    print("更新引用链接")
    print("=" * 80)
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 查找引用
    print("查找引用重命名文件的链接...")
    references = find_references_to_renamed_files()
    print(f"发现 {len(references)} 个引用")
    print()
    
    if not references:
        print("✅ 未发现需要更新的引用")
        print()
        print("=" * 80)
        print("更新完成")
        print("=" * 80)
        return
    
    # 批量更新
    print("批量更新引用...")
    updated_files = []
    failed_files = []
    
    for ref in references:
        success, message = update_references_in_file(ref['file'], ref['old_name'], ref['new_name'])
        
        if success:
            updated_files.append({
                'file': ref['file'],
                'old_name': ref['old_name'],
                'new_name': ref['new_name']
            })
            print(f"✅ {ref['file']}: {message}")
        else:
            failed_files.append({
                'file': ref['file'],
                'old_name': ref['old_name'],
                'new_name': ref['new_name'],
                'reason': message
            })
            print(f"❌ {ref['file']}: {message}")
    
    print()
    print(f"处理完成: 成功 {len(updated_files)} 个, 失败 {len(failed_files)} 个")
    
    # 保存结果
    json_path = OUTPUT_DIR / f'reference_update_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_references': len(references),
            'total_updated': len(updated_files),
            'total_failed': len(failed_files),
            'success_rate': len(updated_files) / len(references) * 100 if references else 0,
            'updated_files': updated_files,
            'failed_files': failed_files
        }, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存至: {json_path}")
    print()
    print("=" * 80)
    print("更新完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
