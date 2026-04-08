#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审计报告版本号统一脚本
统一审计报告文件名版本号与YAML版本号
"""

import re
from pathlib import Path
from datetime import datetime
import json

def extract_version_from_filename(filename):
    """
    从文件名提取版本号
    支持格式: _V2, _V3, _v2, _v3
    """
    version_patterns = [
        r'_V(\d+)(?:_|\.|$)',
        r'_v(\d+)(?:_|\.|$)',
    ]
    
    for pattern in version_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            version_num = match.group(1)
            return f"{version_num}.0.0"
    
    return None

def update_yaml_version(content, new_version):
    """
    更新YAML头部的版本号
    """
    yaml_pattern = re.compile(r'^(---\s*\n)(.*?)(\n---)', re.DOTALL)
    match = yaml_pattern.match(content)
    
    if match:
        yaml_header = match.group(2)
        version_pattern = re.compile(r'^version:\s*[^\s]+', re.MULTILINE)
        new_yaml_header = version_pattern.sub(f'version: {new_version}', yaml_header)
        new_content = match.group(1) + new_yaml_header + match.group(3) + content[match.end():]
        return new_content
    
    return None

def process_audit_reports(docs_dir):
    """
    处理所有审计报告文件
    """
    results = {
        'scan_time': datetime.now().isoformat(),
        'total_files': 0,
        'updated_files': 0,
        'skipped_files': 0,
        'error_files': 0,
        'details': []
    }
    
    docs_path = Path(docs_dir)
    
    audit_dirs = [
        '05_IMPLEMENTATION/04_OPERATIONS/audit_state',
        '05_IMPLEMENTATION/07_OPERATIONS/audit_state',
        '09_AUDIT/REPORTS',
        '09_AUDIT/STATE',
        '01_FRAMEWORK/LAYER4_ML'
    ]
    
    for audit_dir in audit_dirs:
        audit_path = docs_path / audit_dir
        if not audit_path.exists():
            continue
        
        for md_file in audit_path.rglob('*.md'):
            results['total_files'] += 1
            
            filename = md_file.name
            file_version = extract_version_from_filename(filename)
            
            if not file_version:
                results['skipped_files'] += 1
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                yaml_version_pattern = re.compile(r'^version:\s*([^\s]+)', re.MULTILINE)
                yaml_match = yaml_version_pattern.search(content)
                
                if yaml_match:
                    current_version = yaml_match.group(1)
                    
                    if current_version != file_version:
                        new_content = update_yaml_version(content, file_version)
                        
                        if new_content:
                            with open(md_file, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            results['updated_files'] += 1
                            results['details'].append({
                                'file': str(md_file.relative_to(docs_path)),
                                'old_version': current_version,
                                'new_version': file_version,
                                'status': 'updated'
                            })
                        else:
                            results['error_files'] += 1
                    else:
                        results['skipped_files'] += 1
                else:
                    new_content = update_yaml_version(content, file_version)
                    if new_content:
                        with open(md_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        results['updated_files'] += 1
                        results['details'].append({
                            'file': str(md_file.relative_to(docs_path)),
                            'old_version': '无',
                            'new_version': file_version,
                            'status': 'added'
                        })
            
            except Exception as e:
                results['error_files'] += 1
                results['details'].append({
                    'file': str(md_file.relative_to(docs_path)),
                    'error': str(e),
                    'status': 'error'
                })
    
    return results

def generate_report(results, output_file):
    """
    生成版本号统一报告
    """
    report_lines = [
        "# 审计报告版本号统一报告",
        "",
        f"> **处理时间**: {results['scan_time']}",
        "",
        "## 📊 处理概要",
        "",
        f"- **扫描文件数**: {results['total_files']}",
        f"- **更新文件数**: {results['updated_files']}",
        f"- **跳过文件数**: {results['skipped_files']}",
        f"- **错误文件数**: {results['error_files']}",
        "",
        "## 🔍 更新详情",
        ""
    ]
    
    if results['updated_files'] > 0:
        report_lines.append("### ✅ 已更新文件（前50个）")
        report_lines.append("")
        report_lines.append("| 文件路径 | 原版本号 | 新版本号 | 状态 |")
        report_lines.append("|---------|---------|---------|------|")
        
        for detail in results['details'][:50]:
            if detail['status'] in ['updated', 'added']:
                status = '✅ 已更新' if detail['status'] == 'updated' else '✅ 已添加'
                report_lines.append(
                    f"| {detail['file']} | {detail['old_version']} | {detail['new_version']} | {status} |"
                )
        report_lines.append("")
    
    if results['error_files'] > 0:
        report_lines.append("### ❌ 错误文件")
        report_lines.append("")
        report_lines.append("| 文件路径 | 错误信息 |")
        report_lines.append("|---------|---------|")
        
        for detail in results['details']:
            if detail['status'] == 'error':
                report_lines.append(
                    f"| {detail['file']} | {detail['error']} |"
                )
        report_lines.append("")
    
    report_lines.extend([
        "## ✅ 版本号命名规范",
        "",
        "### 审计报告版本号格式",
        "",
        "```",
        "文件名格式: REPORT_NAME_V2_20260407.md",
        "YAML格式: version: 2.0.0",
        "```",
        "",
        "### 版本号规则",
        "",
        "1. 文件名中的版本号（V2, V3等）转换为标准版本号格式（2.0.0, 3.0.0）",
        "2. YAML中的版本号必须与文件名版本号一致",
        "3. 版本号格式遵循语义化版本规范（X.Y.Z）",
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
    output_file = 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/AUDIT_REPORT_VERSION_UNIFICATION_20260407.md'
    
    print("开始处理审计报告版本号...")
    results = process_audit_reports(docs_dir)
    
    print(f"扫描文件数: {results['total_files']}")
    print(f"更新文件数: {results['updated_files']}")
    print(f"跳过文件数: {results['skipped_files']}")
    print(f"错误文件数: {results['error_files']}")
    
    report_path = generate_report(results, output_file)
    print(f"\n报告已生成: {report_path}")
    
    json_file = output_file.replace('.md', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"JSON结果已保存: {json_file}")

if __name__ == '__main__':
    main()
