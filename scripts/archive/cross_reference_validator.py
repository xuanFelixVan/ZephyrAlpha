#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
跨文档引用验证脚本
检查所有Markdown文档中的引用链接是否有效
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime

def extract_markdown_links(content, file_path):
    """
    提取Markdown文件中的所有链接
    返回: [(link_text, link_url, line_number), ...]
    """
    links = []
    lines = content.split('\n')
    
    # 匹配Markdown链接格式: [text](url)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    
    for line_num, line in enumerate(lines, 1):
        matches = link_pattern.findall(line)
        for text, url in matches:
            # 只处理相对路径链接（排除http/https链接）
            if not url.startswith(('http://', 'https://', '#', 'mailto:')):
                links.append({
                    'text': text,
                    'url': url,
                    'line': line_num,
                    'file': str(file_path)
                })
    
    return links

def check_link_validity(link_url, source_file, docs_root):
    """
    检查链接是否有效
    返回: (is_valid, resolved_path, error_message)
    """
    source_dir = Path(source_file).parent
    
    # 处理相对路径
    if link_url.startswith('./'):
        link_path = source_dir / link_url[2:]
    elif link_url.startswith('../'):
        link_path = source_dir / link_url
    else:
        link_path = source_dir / link_url
    
    try:
        # 解析路径
        resolved_path = link_path.resolve()
        
        # 检查文件是否存在
        if resolved_path.exists():
            if resolved_path.is_file():
                return True, str(resolved_path), None
            else:
                return False, None, "链接指向目录而非文件"
        else:
            return False, None, "目标文件不存在"
    except Exception as e:
        return False, None, f"路径解析错误: {str(e)}"

def scan_all_links(docs_dir):
    """
    扫描docs目录下所有Markdown文件的链接
    """
    results = {
        'scan_time': datetime.now().isoformat(),
        'total_files': 0,
        'total_links': 0,
        'valid_links': 0,
        'invalid_links': 0,
        'files_with_issues': set(),
        'details': []
    }
    
    docs_path = Path(docs_dir)
    
    for md_file in docs_path.rglob('*.md'):
        results['total_files'] += 1
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            links = extract_markdown_links(content, md_file)
            
            for link in links:
                results['total_links'] += 1
                
                is_valid, resolved_path, error = check_link_validity(
                    link['url'], 
                    md_file, 
                    docs_path
                )
                
                if is_valid:
                    results['valid_links'] += 1
                else:
                    results['invalid_links'] += 1
                    results['files_with_issues'].add(str(md_file.relative_to(docs_path)))
                    
                    results['details'].append({
                        'source_file': str(md_file.relative_to(docs_path)),
                        'link_text': link['text'],
                        'link_url': link['url'],
                        'line_number': link['line'],
                        'error': error
                    })
        
        except Exception as e:
            print(f"处理文件 {md_file} 时出错: {str(e)}")
    
    results['files_with_issues'] = len(results['files_with_issues'])
    return results

def generate_report(results, output_file):
    """
    生成引用验证报告
    """
    report_lines = [
        "# 跨文档引用验证报告",
        "",
        f"> **检查时间**: {results['scan_time']}",
        f"> **检查范围**: docs目录下所有Markdown文件的引用链接",
        "",
        "## 📊 检查概要",
        "",
        f"- **扫描文件数**: {results['total_files']}",
        f"- **总链接数**: {results['total_links']}",
        f"- **有效链接数**: {results['valid_links']}",
        f"- **无效链接数**: {results['invalid_links']}",
        f"- **有问题的文件数**: {results['files_with_issues']}",
        f"- **链接有效率**: {results['valid_links'] / results['total_links'] * 100:.2f}%",
        "",
        "## 🔍 无效链接详情",
        ""
    ]
    
    if results['invalid_links'] > 0:
        report_lines.append("### ❌ 无效链接列表（前100条）")
        report_lines.append("")
        report_lines.append("| 源文件 | 链接文本 | 链接URL | 行号 | 错误信息 |")
        report_lines.append("|--------|---------|---------|------|---------|")
        
        for detail in results['details'][:100]:
            report_lines.append(
                f"| {detail['source_file']} | {detail['link_text']} | {detail['link_url']} | {detail['line_number']} | {detail['error']} |"
            )
        report_lines.append("")
        
        # 按文件分组统计
        report_lines.append("### 📁 按文件分组统计（前20个文件）")
        report_lines.append("")
        
        file_issues = defaultdict(list)
        for detail in results['details']:
            file_issues[detail['source_file']].append(detail)
        
        for file, issues in sorted(file_issues.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
            report_lines.append(f"#### {file} ({len(issues)}个问题)")
            report_lines.append("")
            for issue in issues[:5]:
                report_lines.append(f"- 行{issue['line_number']}: [{issue['link_text']}]({issue['link_url']}) - {issue['error']}")
            if len(issues) > 5:
                report_lines.append(f"- ... 还有 {len(issues) - 5} 个问题")
            report_lines.append("")
    else:
        report_lines.append("✅ **所有链接均有效！**")
        report_lines.append("")
    
    report_lines.extend([
        "## ✅ 建议操作",
        "",
        "### 立即修复（P0）",
        "",
        "对于无效链接，建议立即修复：",
        "",
        "1. **检查目标文件是否存在**: 如果文件被移动或删除，更新链接路径",
        "2. **检查路径拼写**: 确保路径大小写和文件名正确",
        "3. **使用相对路径**: 确保相对路径计算正确",
        "",
        "### 预防措施",
        "",
        "1. 使用Markdown lint工具检查链接有效性",
        "2. 在CI/CD流程中加入链接检查",
        "3. 使用pre-commit hook验证链接",
        "",
        "---",
        "",
        f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return output_file

def main():
    """
    主函数
    """
    docs_dir = 'docs'
    output_file = 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/CROSS_REFERENCE_VALIDATION_REPORT_20260407.md'
    
    print(f"开始扫描 {docs_dir} 目录下的所有链接...")
    results = scan_all_links(docs_dir)
    
    print(f"扫描完成，共检查 {results['total_files']} 个文件")
    print(f"总链接数: {results['total_links']}")
    print(f"有效链接: {results['valid_links']}")
    print(f"无效链接: {results['invalid_links']}")
    print(f"有问题的文件: {results['files_with_issues']}")
    
    report_path = generate_report(results, output_file)
    print(f"\n报告已生成: {report_path}")
    
    # 同时保存JSON格式的详细结果
    json_file = output_file.replace('.md', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        # 转换set为list以便JSON序列化
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"JSON结果已保存: {json_file}")

if __name__ == '__main__':
    main()
