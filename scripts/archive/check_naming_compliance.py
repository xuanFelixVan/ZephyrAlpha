#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
智能命名规范检查脚本
功能：智能检查文件命名规范，区分标准命名和非标准命名
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

# 标准文件名列表（允许小写）
STANDARD_FILENAMES = {
    'INDEX.md', 'README.md', 'ARCHITECTURE.md', 'CHANGELOG.md',
    'CONTRIBUTING.md', 'LICENSE.md', 'TODO.md', 'NOTES.md'
}

def check_filename_naming(file_path):
    """检查文件命名规范"""
    file_name = os.path.basename(file_path)
    
    # 检查是否包含中文
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in file_name)
    
    # 检查是否包含空格
    has_space = ' ' in file_name
    
    # 检查是否为标准文件名
    if file_name in STANDARD_FILENAMES:
        return {
            'has_chinese': has_chinese,
            'has_space': has_space,
            'is_standard': True,
            'is_valid': not has_chinese and not has_space
        }
    
    # 检查是否符合命名规范（大写字母、数字、下划线）
    is_standard = bool(re.match(r'^[A-Z_0-9]+\.md$', file_name))
    
    # 检查是否为日期格式文件名（如automated_check_report_20260407_031229.md）
    is_date_format = bool(re.match(r'^[a-z_0-9]+_\d{8}_\d{6}\.md$', file_name))
    
    # 检查是否为版本格式文件名（如BLUEPRINT_v2.0.1_backup.md）
    is_version_format = bool(re.match(r'^[A-Z_0-9]+_v[\d.]+.*\.md$', file_name, re.IGNORECASE))
    
    # 判断是否有效
    is_valid = (not has_chinese and not has_space and 
                (is_standard or is_date_format or is_version_format))
    
    return {
        'has_chinese': has_chinese,
        'has_space': has_space,
        'is_standard': is_standard or is_date_format or is_version_format,
        'is_valid': is_valid
    }

def scan_naming_compliance():
    """扫描命名规范符合情况"""
    total_files = 0
    valid_files = 0
    issues = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            total_files += 1
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, DOCS_DIR)
            
            naming_check = check_filename_naming(file_path)
            
            if naming_check['is_valid']:
                valid_files += 1
            else:
                issues.append({
                    'path': rel_path,
                    'has_chinese': naming_check['has_chinese'],
                    'has_space': naming_check['has_space'],
                    'is_standard': naming_check['is_standard']
                })
    
    compliance_rate = valid_files / total_files * 100 if total_files > 0 else 0
    
    return {
        'total_files': total_files,
        'valid_files': valid_files,
        'compliance_rate': compliance_rate,
        'issues': issues
    }

def main():
    """主函数"""
    print("=" * 80)
    print("智能命名规范检查")
    print("=" * 80)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 扫描命名规范符合情况
    print("扫描命名规范符合情况...")
    result = scan_naming_compliance()
    
    print(f"总文件数: {result['total_files']}")
    print(f"符合规范文件数: {result['valid_files']}")
    print(f"命名规范符合率: {result['compliance_rate']:.1f}%")
    print()
    
    # 统计问题类型
    if result['issues']:
        print("问题类型统计:")
        chinese_count = sum(1 for issue in result['issues'] if issue['has_chinese'])
        space_count = sum(1 for issue in result['issues'] if issue['has_space'])
        non_standard_count = sum(1 for issue in result['issues'] if not issue['is_standard'])
        
        print(f"  - 包含中文: {chinese_count}个")
        print(f"  - 包含空格: {space_count}个")
        print(f"  - 不符合标准格式: {non_standard_count}个")
        print()
        
        # 显示前20个问题文件
        print("问题文件列表（前20个）:")
        for i, issue in enumerate(result['issues'][:20], 1):
            problems = []
            if issue['has_chinese']:
                problems.append('包含中文')
            if issue['has_space']:
                problems.append('包含空格')
            if not issue['is_standard']:
                problems.append('不符合标准格式')
            print(f"{i}. {issue['path']}")
            print(f"   问题: {', '.join(problems)}")
        
        if len(result['issues']) > 20:
            print(f"... 还有 {len(result['issues']) - 20} 个问题文件")
    else:
        print("✅ 所有文件命名都符合规范")
    
    print()
    
    # 判断是否达到目标
    if result['compliance_rate'] >= 95:
        print("✅ 已达到目标符合率（95%）")
    else:
        print(f"⚠️ 距离目标还差 {95 - result['compliance_rate']:.1f}%")
    
    # 保存结果
    json_path = OUTPUT_DIR / f'naming_compliance_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_files': result['total_files'],
            'valid_files': result['valid_files'],
            'compliance_rate': result['compliance_rate'],
            'issues_count': len(result['issues']),
            'issues': result['issues']
        }, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存至: {json_path}")
    print()
    print("=" * 80)
    print("检查完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
