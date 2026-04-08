#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量重命名文件脚本
功能：将不符合命名规范的文件重命名为标准格式
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
    
    # 检查是否为日期格式文件名
    is_date_format = bool(re.match(r'^[a-z_0-9]+_\d{8}_\d{6}\.md$', file_name))
    
    # 检查是否为版本格式文件名
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

def convert_to_standard_name(file_name):
    """将文件名转换为标准格式"""
    # 如果是标准文件名，直接返回
    if file_name in STANDARD_FILENAMES:
        return file_name
    
    # 移除空格
    new_name = file_name.replace(' ', '_')
    
    # 转换为大写
    name_without_ext = os.path.splitext(new_name)[0]
    ext = os.path.splitext(new_name)[1]
    new_name = name_without_ext.upper() + ext
    
    return new_name

def rename_file(file_path):
    """重命名文件"""
    file_name = os.path.basename(file_path)
    dir_path = os.path.dirname(file_path)
    
    # 转换为标准名称
    new_name = convert_to_standard_name(file_name)
    
    # 如果文件名没有变化，返回False
    if new_name == file_name:
        return False, "文件名已符合规范", file_name
    
    # 构建新路径
    new_path = os.path.join(dir_path, new_name)
    
    # 检查新文件名是否已存在
    if os.path.exists(new_path):
        return False, f"目标文件已存在: {new_name}", new_name
    
    try:
        # 重命名文件
        os.rename(file_path, new_path)
        return True, f"重命名成功: {file_name} -> {new_name}", new_name
    except Exception as e:
        return False, f"重命名失败: {str(e)}", new_name

def scan_and_rename():
    """扫描并重命名不符合规范的文件"""
    renamed_files = []
    failed_files = []
    total_files = 0
    valid_files = 0
    
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
                # 重命名文件
                success, message, new_name = rename_file(file_path)
                
                if success:
                    renamed_files.append({
                        'old_path': rel_path,
                        'new_name': new_name,
                        'message': message
                    })
                    valid_files += 1
                else:
                    failed_files.append({
                        'path': rel_path,
                        'reason': message
                    })
    
    compliance_rate = valid_files / total_files * 100 if total_files > 0 else 0
    
    return {
        'total_files': total_files,
        'valid_files': valid_files,
        'compliance_rate': compliance_rate,
        'renamed_files': renamed_files,
        'failed_files': failed_files
    }

def main():
    """主函数"""
    print("=" * 80)
    print("批量重命名文件")
    print("=" * 80)
    print(f"重命名时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 扫描并重命名
    print("扫描并重命名不符合规范的文件...")
    result = scan_and_rename()
    
    print()
    print(f"总文件数: {result['total_files']}")
    print(f"符合规范文件数: {result['valid_files']}")
    print(f"命名规范符合率: {result['compliance_rate']:.1f}%")
    print()
    
    # 显示重命名结果
    if result['renamed_files']:
        print(f"成功重命名 {len(result['renamed_files'])} 个文件:")
        for i, file_info in enumerate(result['renamed_files'][:20], 1):
            print(f"  {i}. {file_info['old_path']}")
            print(f"     -> {file_info['new_name']}")
        
        if len(result['renamed_files']) > 20:
            print(f"... 还有 {len(result['renamed_files']) - 20} 个文件")
        print()
    
    if result['failed_files']:
        print(f"重命名失败 {len(result['failed_files'])} 个文件:")
        for i, file_info in enumerate(result['failed_files'][:10], 1):
            print(f"  {i}. {file_info['path']}")
            print(f"     原因: {file_info['reason']}")
        
        if len(result['failed_files']) > 10:
            print(f"... 还有 {len(result['failed_files']) - 10} 个文件")
        print()
    
    # 判断是否达到目标
    if result['compliance_rate'] >= 95:
        print("✅ 已达到目标符合率（95%）")
    else:
        print(f"⚠️ 距离目标还差 {95 - result['compliance_rate']:.1f}%")
    
    # 保存结果
    json_path = OUTPUT_DIR / f'batch_rename_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_files': result['total_files'],
            'valid_files': result['valid_files'],
            'compliance_rate': result['compliance_rate'],
            'renamed_count': len(result['renamed_files']),
            'failed_count': len(result['failed_files']),
            'renamed_files': result['renamed_files'],
            'failed_files': result['failed_files']
        }, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存至: {json_path}")
    print()
    print("=" * 80)
    print("重命名完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
