#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
文档版本一致性检查脚本
检查文档内版本号与文件名是否匹配
"""

import os
import re
from pathlib import Path
import json
from datetime import datetime

def extract_version_from_yaml(content):
    """
    从YAML头部提取版本号
    """
    yaml_pattern = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL)
    match = yaml_pattern.search(content)
    
    if match:
        yaml_content = match.group(1)
        version_pattern = re.compile(r'^version:\s*([^\s]+)', re.MULTILINE)
        version_match = version_pattern.search(yaml_content)
        if version_match:
            return version_match.group(1).strip()
    
    return None

def extract_version_from_filename(filename):
    """
    从文件名提取版本号
    支持格式: _v1.0.0, _v1.0, _v1
    """
    version_patterns = [
        r'_v(\d+\.\d+\.\d+)',  # _v1.0.0
        r'_v(\d+\.\d+)',        # _v1.0
        r'_v(\d+)',             # _v1
    ]
    
    for pattern in version_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def check_version_consistency(file_path):
    """
    检查单个文件的版本一致性
    返回: (yaml_version, filename_version, is_consistent, note)
    """
    filename = Path(file_path).name
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        yaml_version = extract_version_from_yaml(content)
        filename_version = extract_version_from_filename(filename)
        
        if yaml_version is None and filename_version is None:
            return None, None, True, "文件名和YAML均无版本号"
        elif yaml_version is None:
            return None, filename_version, False, "YAML缺少版本号"
        elif filename_version is None:
            return yaml_version, None, True, "文件名无版本号（允许）"
        else:
            # 比较版本号
            is_consistent = yaml_version == filename_version
            if is_consistent:
                return yaml_version, filename_version, True, "版本号一致"
            else:
                return yaml_version, filename_version, False, "版本号不一致"
    
    except Exception as e:
        return None, None, False, f"检查失败: {str(e)}"

def scan_all_documents(docs_dir):
    """
    扫描docs目录下所有Markdown文件的版本一致性
    """
    results = {
        'scan_time': datetime.now().isoformat(),
        'total_files': 0,
        'consistent_files': 0,
        'inconsistent_files': 0,
        'no_version_files': 0,
        'details': []
    }
    
    docs_path = Path(docs_dir)
    
    for md_file in docs_path.rglob('*.md'):
        results['total_files'] += 1
        
        yaml_version, filename_version, is_consistent, note = check_version_consistency(md_file)
        
        detail = {
            'file': str(md_file.relative_to(docs_path)),
            'yaml_version': yaml_version,
            'filename_version': filename_version,
            'is_consistent': is_consistent,
            'note': note
        }
        
        if yaml_version is None and filename_version is None:
            results['no_version_files'] += 1
        elif is_consistent:
            results['consistent_files'] += 1
        else:
            results['inconsistent_files'] += 1
            results['details'].append(detail)
    
    return results

def generate_report(results, output_file):
    """
    生成版本一致性检查报告
    """
    report_lines = [
        "# 文档版本一致性检查报告",
        "",
        f"> **检查时间**: {results['scan_time']}",
        f"> **检查范围**: docs目录下所有Markdown文件",
        "",
        "## 📊 检查概要",
        "",
        f"- **总文件数**: {results['total_files']}",
        f"- **版本一致文件数**: {results['consistent_files']}",
        f"- **版本不一致文件数**: {results['inconsistent_files']}",
        f"- **无版本号文件数**: {results['no_version_files']}",
        f"- **版本一致率**: {results['consistent_files'] / (results['total_files'] - results['no_version_files']) * 100:.2f}%" if (results['total_files'] - results['no_version_files']) > 0 else "- **版本一致率**: N/A",
        "",
        "## 🔍 版本不一致详情",
        ""
    ]
    
    if results['inconsistent_files'] > 0:
        report_lines.append("### ❌ 版本不一致文件列表")
        report_lines.append("")
        report_lines.append("| 文件路径 | YAML版本 | 文件名版本 | 说明 |")
        report_lines.append("|---------|---------|-----------|------|")
        
        for detail in results['details']:
            report_lines.append(
                f"| {detail['file']} | {detail['yaml_version'] or '无'} | {detail['filename_version'] or '无'} | {detail['note']} |"
            )
        report_lines.append("")
    else:
        report_lines.append("✅ **所有文件的版本号均一致！**")
        report_lines.append("")
    
    report_lines.extend([
        "## ✅ 建议操作",
        "",
        "### 立即修复（P0）",
        "",
        "对于版本不一致的文件，建议立即修复：",
        "",
        "1. **统一版本号**: 将YAML中的版本号与文件名版本号统一",
        "2. **优先使用YAML版本**: YAML中的版本号是权威版本，文件名应跟随YAML版本",
        "3. **更新文件名**: 如果需要修改文件名，使用Git mv命令保留历史",
        "",
        "### 版本号命名规范",
        "",
        "```",
        "文件名格式: MODULE_NAME_v1.0.0.md",
        "YAML格式: version: 1.0.0",
        "```",
        "",
        "### 预防措施",
        "",
        "1. 在文档创建时统一版本号",
        "2. 使用pre-commit hook检查版本一致性",
        "3. 在CI/CD流程中加入版本检查",
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
    output_file = 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/VERSION_CONSISTENCY_REPORT_20260407.md'
    
    print(f"开始扫描 {docs_dir} 目录下的版本一致性...")
    results = scan_all_documents(docs_dir)
    
    print(f"扫描完成，共检查 {results['total_files']} 个文件")
    print(f"版本一致: {results['consistent_files']}")
    print(f"版本不一致: {results['inconsistent_files']}")
    print(f"无版本号: {results['no_version_files']}")
    
    report_path = generate_report(results, output_file)
    print(f"\n报告已生成: {report_path}")
    
    # 同时保存JSON格式的详细结果
    json_file = output_file.replace('.md', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"JSON结果已保存: {json_file}")

if __name__ == '__main__':
    main()
