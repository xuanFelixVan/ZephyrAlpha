#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关键文档引用修复脚本
修复System_Manifest.md和INDEX.md中的无效链接
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def load_invalid_links(json_file):
    """
    加载无效链接数据
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['details']

def analyze_links_by_file(details, target_files):
    """
    按文件分组分析无效链接
    """
    file_links = defaultdict(list)
    for detail in details:
        if detail['source_file'] in target_files:
            file_links[detail['source_file']].append(detail)
    return file_links

def find_correct_path(link_url, docs_root):
    """
    尝试找到正确的文件路径
    """
    docs_path = Path(docs_root)
    
    # 提取文件名
    filename = Path(link_url).name
    
    # 在docs目录下搜索该文件
    for md_file in docs_path.rglob(filename):
        return str(md_file.relative_to(docs_path))
    
    return None

def fix_links_in_file(file_path, invalid_links, docs_root):
    """
    修复文件中的无效链接
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes = []
    
    for link in invalid_links:
        link_url = link['link_url']
        line_number = link['line_number']
        
        # 尝试找到正确的路径
        correct_path = find_correct_path(link_url, docs_root)
        
        if correct_path:
            # 替换链接 - 使用字符串替换而不是正则表达式替换
            old_link = f'[{link["link_text"]}]({link_url})'
            new_link = f'[{link["link_text"]}]({correct_path})'
            
            if old_link in content:
                content = content.replace(old_link, new_link)
                fixes.append({
                    'line': line_number,
                    'old_url': link_url,
                    'new_url': correct_path,
                    'status': 'fixed'
                })
        else:
            fixes.append({
                'line': line_number,
                'old_url': link_url,
                'new_url': None,
                'status': 'file_not_found'
            })
    
    # 如果有修复，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return fixes

def generate_fix_report(fixes_by_file, output_file):
    """
    生成修复报告
    """
    report_lines = [
        "# 关键文档引用修复报告",
        "",
        "## 修复概要",
        ""
    ]
    
    total_fixed = 0
    total_not_found = 0
    
    for file, fixes in fixes_by_file.items():
        fixed = sum(1 for f in fixes if f['status'] == 'fixed')
        not_found = sum(1 for f in fixes if f['status'] == 'file_not_found')
        total_fixed += fixed
        total_not_found += not_found
        
        report_lines.append(f"### {file}")
        report_lines.append(f"- 修复成功: {fixed}")
        report_lines.append(f"- 文件未找到: {not_found}")
        report_lines.append("")
        
        if fixes:
            report_lines.append("| 行号 | 原链接 | 新链接 | 状态 |")
            report_lines.append("|------|--------|--------|------|")
            for fix in fixes:
                new_url = fix['new_url'] or '未找到'
                status = '✅ 已修复' if fix['status'] == 'fixed' else '❌ 文件不存在'
                report_lines.append(f"| {fix['line']} | {fix['old_url']} | {new_url} | {status} |")
            report_lines.append("")
    
    report_lines.insert(3, f"- 总修复数: {total_fixed}")
    report_lines.insert(4, f"- 未找到文件数: {total_not_found}")
    report_lines.insert(5, "")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return output_file

def main():
    """
    主函数
    """
    docs_root = 'docs'
    json_file = 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/CROSS_REFERENCE_VALIDATION_REPORT_20260407.json'
    output_file = 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/KEY_DOCS_LINK_FIX_REPORT_20260407.md'
    
    # 目标文件
    target_files = [
        'System_Manifest.md',
        'INDEX.md',
        'SITEMAP.md'
    ]
    
    print("加载无效链接数据...")
    details = load_invalid_links(json_file)
    
    print("分析关键文档的无效链接...")
    file_links = analyze_links_by_file(details, target_files)
    
    print(f"发现 {len(file_links)} 个关键文档需要修复")
    
    fixes_by_file = {}
    
    for file, links in file_links.items():
        print(f"\n处理文件: {file}")
        print(f"无效链接数: {len(links)}")
        
        file_path = Path(docs_root) / file
        if file_path.exists():
            fixes = fix_links_in_file(file_path, links, docs_root)
            fixes_by_file[file] = fixes
            
            fixed_count = sum(1 for f in fixes if f['status'] == 'fixed')
            print(f"修复成功: {fixed_count}")
        else:
            print(f"文件不存在: {file_path}")
    
    print("\n生成修复报告...")
    report_path = generate_fix_report(fixes_by_file, output_file)
    print(f"报告已生成: {report_path}")

if __name__ == '__main__':
    main()
