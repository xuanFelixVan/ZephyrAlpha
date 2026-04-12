#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复剩余问题：职责描述缺失和无效链接
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

# 已删除的文件列表
DELETED_FILES = [
    'factor_neutralization',
    'factor_preprocessing',
    'factor_return_analysis',
    'factor_synthesis',
    'ic_analysis',
    'FACTOR_SCREENING_STRATEGY',
    'FACTOR_VALIDATION_GUIDE',
    'IFIND_CONNECTOR',
    'SUPERCMD_CONNECTOR',
    'OVERFITTING_TEST',
]

def clean_yaml_header(content):
    """清理YAML头部"""
    # 找到所有YAML块
    yaml_blocks = []
    pos = 0
    while True:
        start = content.find('---', pos)
        if start == -1:
            break
        end = content.find('---', start + 3)
        if end == -1:
            break
        yaml_blocks.append((start, end + 3))
        pos = end + 3
    
    if len(yaml_blocks) < 2:
        return content
    
    # 保留最后一个完整的YAML块
    last_start, last_end = yaml_blocks[-1]
    
    # 提取最后一个YAML块的内容
    yaml_content = content[last_start:last_end]
    
    # 移除重复的module_id
    lines = yaml_content.split('\n')
    seen_module_id = False
    cleaned_lines = []
    for line in lines:
        if line.startswith('module_id:'):
            if not seen_module_id:
                cleaned_lines.append(line)
                seen_module_id = True
        else:
            cleaned_lines.append(line)
    
    yaml_content = '\n'.join(cleaned_lines)
    
    # 构建新内容
    new_content = yaml_content + content[last_end:]
    
    return new_content

def fix_yaml_and_responsibility():
    """修复YAML格式和职责描述"""
    print("=" * 80)
    print("修复YAML格式和职责描述")
    print("=" * 80)
    
    fixed_count = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            original_content = content
            
            # 1. 清理YAML头部
            content = clean_yaml_header(content)
            
            # 2. 检查是否有responsibility字段
            if 'responsibility:' not in content:
                # 提取YAML头部
                yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    
                    # 生成职责描述
                    parts = rel_path.parts[:-1]
                    file_name = file_path.stem
                    
                    if file_name.upper() == 'INDEX':
                        responsibility = f"{parts[-1] if parts else '因子库'}目录索引与导航"
                    elif file_name.upper() == 'README':
                        responsibility = f"{parts[-1] if parts else '因子库'}模块说明"
                    else:
                        clean_name = file_name.replace('_', ' ').replace('-', ' ')
                        responsibility = f"{clean_name}相关文档"
                    
                    # 添加responsibility字段
                    new_yaml = yaml_content + f"\nresponsibility:\n  - {responsibility}"
                    content = content.replace(yaml_content, new_yaml)
                    
                    print(f"\n{rel_path}")
                    print(f"  添加职责: {responsibility}")
                    fixed_count += 1
            
            # 3. 检查YAML头部中是否有链接（格式错误）
            yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                # 检查是否有链接在YAML中
                if '[' in yaml_content and '](' in yaml_content:
                    # 移除YAML中的链接
                    lines = yaml_content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        if '[' in line and '](' in line:
                            continue
                        cleaned_lines.append(line)
                    
                    new_yaml = '\n'.join(cleaned_lines)
                    content = content.replace(yaml_content, new_yaml)
                    
                    print(f"\n{rel_path}")
                    print(f"  清理YAML中的链接")
                    fixed_count += 1
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        except Exception as e:
            print(f"  错误: {e}")
    
    print(f"\n修复文件: {fixed_count}")
    return fixed_count

def fix_invalid_links():
    """修复无效链接"""
    print("\n" + "=" * 80)
    print("修复无效链接")
    print("=" * 80)
    
    fixed_count = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            original_content = content
            
            # 检查并移除指向已删除文件的链接
            for deleted_name in DELETED_FILES:
                # 匹配各种链接格式
                patterns = [
                    rf'\[([^\]]*)\]\([^)]*{deleted_name}[^)]*\)',
                    rf'\|\s*\[([^\]]*)\]\([^)]*{deleted_name}[^)]*\)\s*\|',
                    rf'-\s*\[([^\]]*)\]\([^)]*{deleted_name}[^)]*\)',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        # 移除整行（如果是列表项）
                        lines = content.split('\n')
                        new_lines = []
                        for line in lines:
                            if deleted_name in line and '[' in line and '](' in line:
                                # 跳过这一行
                                print(f"\n{rel_path}")
                                print(f"  移除链接行: {line.strip()[:50]}")
                                fixed_count += 1
                                continue
                            new_lines.append(line)
                        content = '\n'.join(new_lines)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        except Exception as e:
            print(f"  错误: {e}")
    
    print(f"\n修复链接: {fixed_count}")
    return fixed_count

def fix_sitemap_index():
    """专门修复SITEMAP.md和INDEX.md"""
    print("\n" + "=" * 80)
    print("修复SITEMAP.md和INDEX.md")
    print("=" * 80)
    
    fixed_count = 0
    
    # 修复INDEX.md
    index_file = FACTOR_LIBRARY / 'INDEX.md'
    if index_file.exists():
        try:
            with open(index_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 清理YAML头部
            content = clean_yaml_header(content)
            
            # 确保有responsibility
            if 'responsibility:' not in content:
                yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    new_yaml = yaml_content + "\nresponsibility:\n  - 因子库目录索引与导航"
                    content = content.replace(yaml_content, new_yaml)
                    print(f"\nINDEX.md")
                    print(f"  添加职责: 因子库目录索引与导航")
                    fixed_count += 1
            
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        except Exception as e:
            print(f"  错误: {e}")
    
    # 修复SITEMAP.md
    sitemap_file = FACTOR_LIBRARY / 'SITEMAP.md'
    if sitemap_file.exists():
        try:
            with open(sitemap_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 清理YAML头部
            content = clean_yaml_header(content)
            
            # 确保有responsibility
            if 'responsibility:' not in content:
                yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    new_yaml = yaml_content + "\nresponsibility:\n  - 因子库文档地图导航"
                    content = content.replace(yaml_content, new_yaml)
                    print(f"\nSITEMAP.md")
                    print(f"  添加职责: 因子库文档地图导航")
                    fixed_count += 1
            
            with open(sitemap_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        except Exception as e:
            print(f"  错误: {e}")
    
    print(f"\n修复文件: {fixed_count}")
    return fixed_count

def main():
    """主函数"""
    print("=" * 80)
    print("修复剩余问题")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_fixed = 0
    
    # 1. 修复YAML格式和职责描述
    total_fixed += fix_yaml_and_responsibility()
    
    # 2. 修复无效链接
    total_fixed += fix_invalid_links()
    
    # 3. 专门修复SITEMAP.md和INDEX.md
    total_fixed += fix_sitemap_index()
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"总修复数: {total_fixed}")

if __name__ == '__main__':
    main()
