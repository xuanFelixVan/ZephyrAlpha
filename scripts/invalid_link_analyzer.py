#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
无效链接分析和修复脚本
分析无效链接的类型并提供修复建议
"""

import re
from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict

def analyze_invalid_links(docs_root):
    """分析所有无效链接"""
    docs_path = Path(docs_root)
    
    results = {
        'scan_time': datetime.now().isoformat(),
        'total_files': 0,
        'total_links': 0,
        'valid_links': 0,
        'invalid_links': 0,
        'skipped_links': 0,
        'link_types': defaultdict(int),
        'invalid_patterns': defaultdict(list),
        'files_with_most_issues': defaultdict(int),
        'details': []
    }
    
    # 构建文件索引
    all_files = {}
    for md_file in docs_path.rglob('*.md'):
        rel_path = str(md_file.relative_to(docs_path)).replace('\\', '/')
        all_files[rel_path.lower()] = rel_path
        all_files[md_file.name.lower()] = rel_path
    
    # 扫描所有文件
    for md_file in docs_path.rglob('*.md'):
        results['total_files'] += 1
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            continue
        
        source_file = str(md_file.relative_to(docs_path)).replace('\\', '/')
        source_dir = str(md_file.parent.relative_to(docs_path)).replace('\\', '/')
        
        # 匹配markdown链接
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
        
        for match in link_pattern.finditer(content):
            link_text = match.group(1)
            link_url = match.group(2).strip()
            
            # 跳过非文件链接
            if link_url.startswith(('http://', 'https://', 'mailto:', '#', 'tel:')):
                results['skipped_links'] += 1
                continue
            
            results['total_links'] += 1
            
            # 检查链接类型
            if link_url.startswith('./'):
                link_type = 'relative_current'
            elif link_url.startswith('../'):
                link_type = 'relative_parent'
            elif link_url.startswith('/'):
                link_type = 'absolute'
            else:
                link_type = 'relative'
            
            results['link_types'][link_type] += 1
            
            # 解析链接路径
            if link_url.startswith('./') or link_url.startswith('../'):
                # 相对路径
                target_path = (Path(source_dir) / link_url).resolve()
                try:
                    target_rel = str(target_path.relative_to(docs_path)).replace('\\', '/')
                except ValueError:
                    target_rel = link_url
            else:
                target_rel = link_url
            
            # 检查文件是否存在
            target_file = docs_path / target_rel
            
            # 尝试多种路径
            possible_paths = [
                target_file,
                docs_path / target_rel.lstrip('./'),
                docs_path / (target_rel + '.md'),
                docs_path / (target_rel.rstrip('/') + '.md'),
                docs_path / (target_rel + '/INDEX.md'),
                docs_path / (target_rel + '/index.md'),
            ]
            
            exists = any(p.exists() for p in possible_paths)
            
            if exists:
                results['valid_links'] += 1
            else:
                results['invalid_links'] += 1
                results['files_with_most_issues'][source_file] += 1
                
                # 分析无效链接的模式
                pattern_key = link_url.split('/')[0] if '/' in link_url else link_url
                results['invalid_patterns'][pattern_key].append({
                    'source_file': source_file,
                    'link_text': link_text,
                    'link_url': link_url,
                    'line_number': content[:match.start()].count('\n') + 1
                })
                
                results['details'].append({
                    'source_file': source_file,
                    'link_text': link_text,
                    'link_url': link_url,
                    'line_number': content[:match.start()].count('\n') + 1,
                    'link_type': link_type
                })
    
    return results

def generate_analysis_report(results, output_file):
    """生成分析报告"""
    report_lines = [
        "# 无效链接分析报告",
        "",
        f"> **分析时间**: {results['scan_time']}",
        "",
        "## 📊 总体统计",
        "",
        f"- **扫描文件数**: {results['total_files']}",
        f"- **总链接数**: {results['total_links']}",
        f"- **有效链接数**: {results['valid_links']}",
        f"- **无效链接数**: {results['invalid_links']}",
        f"- **跳过链接数**: {results['skipped_links']}",
        f"- **有效率**: {results['valid_links'] / results['total_links'] * 100:.2f}%",
        "",
        "## 📈 链接类型分布",
        ""
    ]
    
    for link_type, count in sorted(results['link_types'].items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"- **{link_type}**: {count} ({count / results['total_links'] * 100:.2f}%)")
    
    report_lines.extend([
        "",
        "## 🔍 无效链接模式分析",
        ""
    ])
    
    # 按模式分组显示
    for pattern, links in sorted(results['invalid_patterns'].items(), key=lambda x: len(x[1]), reverse=True)[:20]:
        report_lines.append(f"### 模式: `{pattern}` ({len(links)}个无效链接)")
        report_lines.append("")
        
        for link in links[:5]:  # 每个模式只显示前5个示例
            report_lines.append(f"- [{link['link_text']}]({link['link_url']}) - {link['source_file']}:{link['line_number']}")
        
        if len(links) > 5:
            report_lines.append(f"- ... 还有 {len(links) - 5} 个")
        report_lines.append("")
    
    # 问题最多的文件
    report_lines.extend([
        "## 📁 问题最多的文件（Top 20）",
        ""
    ])
    
    for file, count in sorted(results['files_with_most_issues'].items(), key=lambda x: x[1], reverse=True)[:20]:
        report_lines.append(f"- **{file}**: {count}个无效链接")
    
    report_lines.extend([
        "",
        "## 💡 修复建议",
        "",
        "### 1. 路径规范化",
        "- 统一使用相对路径格式（./path/to/file.md）",
        "- 避免使用绝对路径",
        "- 确保文件名大小写一致",
        "",
        "### 2. 文件索引完善",
        "- 为每个目录创建INDEX.md文件",
        "- 确保所有活跃文档都被索引",
        "- 定期检查和更新索引",
        "",
        "### 3. 自动化检查",
        "- 建立CI/CD流程自动检查链接有效性",
        "- 使用脚本定期扫描和修复无效链接",
        "- 在文档创建时自动验证链接",
        "",
        "---",
        f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return output_file

def main():
    """主函数"""
    docs_root = 'docs'
    output_file = 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/INVALID_LINK_ANALYSIS_20260407.md'
    
    print("=" * 60)
    print("开始分析无效链接...")
    print("=" * 60)
    
    results = analyze_invalid_links(docs_root)
    
    print("\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)
    print(f"扫描文件数: {results['total_files']}")
    print(f"总链接数: {results['total_links']}")
    print(f"有效链接数: {results['valid_links']}")
    print(f"无效链接数: {results['invalid_links']}")
    print(f"有效率: {results['valid_links'] / results['total_links'] * 100:.2f}%")
    
    report_path = generate_analysis_report(results, output_file)
    print(f"\n报告已生成: {report_path}")
    
    # 保存JSON格式结果
    json_file = output_file.replace('.md', '.json')
    
    # 转换defaultdict为普通dict以便JSON序列化
    results_for_json = dict(results)
    results_for_json['link_types'] = dict(results_for_json['link_types'])
    results_for_json['invalid_patterns'] = {k: v for k, v in results_for_json['invalid_patterns'].items()}
    results_for_json['files_with_most_issues'] = dict(results_for_json['files_with_most_issues'])
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results_for_json, f, ensure_ascii=False, indent=2)
    print(f"JSON结果已保存: {json_file}")

if __name__ == '__main__':
    main()
