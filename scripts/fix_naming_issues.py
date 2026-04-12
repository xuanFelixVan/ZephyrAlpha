#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
优化命名规范脚本
功能：修复文件命名不规范问题，提升命名规范符合率至95%
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

def check_filename_naming(file_path):
    """检查文件命名规范"""
    file_name = os.path.basename(file_path)
    
    # 检查是否包含中文
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in file_name)
    
    # 检查是否包含空格
    has_space = ' ' in file_name
    
    # 检查是否符合命名规范（大写字母、数字、下划线）
    is_standard = bool(re.match(r'^[A-Z_0-9]+\.md$', file_name))
    
    return {
        'has_chinese': has_chinese,
        'has_space': has_space,
        'is_standard': is_standard,
        'is_valid': not has_chinese and not has_space and is_standard
    }

def fix_filename(file_path):
    """修复文件命名"""
    file_name = os.path.basename(file_path)
    dir_path = os.path.dirname(file_path)
    
    # 移除空格
    new_name = file_name.replace(' ', '_')
    
    # 转换为大写
    name_without_ext = os.path.splitext(new_name)[0]
    ext = os.path.splitext(new_name)[1]
    new_name = name_without_ext.upper() + ext
    
    # 如果文件名没有变化，返回False
    if new_name == file_name:
        return False, "文件名已符合规范"
    
    # 构建新路径
    new_path = os.path.join(dir_path, new_name)
    
    # 检查新文件名是否已存在
    if os.path.exists(new_path):
        return False, f"目标文件已存在: {new_name}"
    
    try:
        # 重命名文件
        os.rename(file_path, new_path)
        return True, f"重命名成功: {file_name} -> {new_name}"
    except Exception as e:
        return False, f"重命名失败: {str(e)}"

def scan_naming_issues():
    """扫描命名不规范的文件"""
    issues = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, DOCS_DIR)
            
            naming_check = check_filename_naming(file_path)
            
            if not naming_check['is_valid']:
                issues.append({
                    'path': rel_path,
                    'abs_path': file_path,
                    'has_chinese': naming_check['has_chinese'],
                    'has_space': naming_check['has_space'],
                    'is_standard': naming_check['is_standard']
                })
    
    return issues

def main():
    """主函数"""
    print("=" * 80)
    print("优化命名规范")
    print("=" * 80)
    print(f"优化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 扫描命名不规范的文件
    print("扫描命名不规范的文件...")
    issues = scan_naming_issues()
    print(f"发现 {len(issues)} 个命名不规范的文件")
    print()
    
    if not issues:
        print("✅ 所有文件命名都符合规范")
        print()
        print("=" * 80)
        print("优化完成")
        print("=" * 80)
        return
    
    # 统计问题类型
    print("问题类型统计:")
    chinese_count = sum(1 for issue in issues if issue['has_chinese'])
    space_count = sum(1 for issue in issues if issue['has_space'])
    non_standard_count = sum(1 for issue in issues if not issue['is_standard'])
    
    print(f"  - 包含中文: {chinese_count}个")
    print(f"  - 包含空格: {space_count}个")
    print(f"  - 不符合标准格式: {non_standard_count}个")
    print()
    
    # 批量修复
    print("批量修复命名问题...")
    fixed_files = []
    failed_files = []
    
    for i, issue in enumerate(issues, 1):
        success, message = fix_filename(issue['abs_path'])
        
        if success:
            fixed_files.append({
                'path': issue['path'],
                'message': message
            })
            print(f"✅ {i}/{len(issues)}: {issue['path']}")
        else:
            failed_files.append({
                'path': issue['path'],
                'reason': message
            })
            print(f"❌ {i}/{len(issues)}: {issue['path']} - {message}")
    
    print()
    print(f"处理完成: 成功 {len(fixed_files)} 个, 失败 {len(failed_files)} 个")
    
    # 计算新的符合率
    total_files = 0
    valid_files = 0
    
    for root, dirs, files in os.walk(DOCS_DIR):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if file.endswith('.md'):
                total_files += 1
                file_path = os.path.join(root, file)
                naming_check = check_filename_naming(file_path)
                if naming_check['is_valid']:
                    valid_files += 1
    
    compliance_rate = valid_files / total_files * 100 if total_files > 0 else 0
    
    print()
    print(f"命名规范符合率: {compliance_rate:.1f}%")
    print(f"目标符合率: 95%")
    
    if compliance_rate >= 95:
        print("✅ 已达到目标符合率")
    else:
        print(f"⚠️ 距离目标还差 {95 - compliance_rate:.1f}%")
    
    # 保存结果
    json_path = OUTPUT_DIR / f'fix_naming_issues_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(issues),
            'total_fixed': len(fixed_files),
            'total_failed': len(failed_files),
            'success_rate': len(fixed_files) / len(issues) * 100 if issues else 0,
            'compliance_rate': compliance_rate,
            'fixed_files': fixed_files,
            'failed_files': failed_files
        }, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存至: {json_path}")
    print()
    print("=" * 80)
    print("优化完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
