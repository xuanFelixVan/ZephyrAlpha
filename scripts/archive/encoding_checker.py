#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
文档编码检查脚本
检查所有Markdown文档的编码一致性，确保使用UTF-8编码
"""

import os
import chardet
from pathlib import Path
import json
from datetime import datetime

def check_file_encoding(file_path):
    """
    检查单个文件的编码
    返回: (encoding, confidence, is_utf8)
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']
            is_utf8 = encoding and encoding.lower() in ['utf-8', 'ascii']
            return encoding, confidence, is_utf8
    except Exception as e:
        return None, 0, False

def scan_docs_directory(docs_dir):
    """
    扫描docs目录下的所有Markdown文件
    """
    results = {
        'scan_time': datetime.now().isoformat(),
        'total_files': 0,
        'utf8_files': 0,
        'non_utf8_files': 0,
        'error_files': 0,
        'details': []
    }
    
    docs_path = Path(docs_dir)
    
    for md_file in docs_path.rglob('*.md'):
        results['total_files'] += 1
        
        encoding, confidence, is_utf8 = check_file_encoding(md_file)
        
        detail = {
            'file': str(md_file.relative_to(docs_path)),
            'encoding': encoding,
            'confidence': round(confidence, 2) if confidence else 0,
            'is_utf8': is_utf8
        }
        
        if encoding is None:
            results['error_files'] += 1
            detail['error'] = '无法检测编码'
        elif is_utf8:
            results['utf8_files'] += 1
        else:
            results['non_utf8_files'] += 1
        
        results['details'].append(detail)
    
    return results

def generate_report(results, output_file):
    """
    生成编码检查报告
    """
    report_lines = [
        "# 文档编码检查报告",
        "",
        f"> **检查时间**: {results['scan_time']}",
        f"> **检查范围**: docs目录下所有Markdown文件",
        "",
        "## 📊 检查概要",
        "",
        f"- **总文件数**: {results['total_files']}",
        f"- **UTF-8文件数**: {results['utf8_files']}",
        f"- **非UTF-8文件数**: {results['non_utf8_files']}",
        f"- **错误文件数**: {results['error_files']}",
        f"- **UTF-8合规率**: {results['utf8_files'] / results['total_files'] * 100:.2f}%",
        "",
        "## 🔍 详细检查结果",
        ""
    ]
    
    if results['non_utf8_files'] > 0:
        report_lines.append("### ❌ 非UTF-8编码文件")
        report_lines.append("")
        report_lines.append("| 文件路径 | 检测编码 | 置信度 |")
        report_lines.append("|---------|---------|--------|")
        
        for detail in results['details']:
            if not detail['is_utf8'] and detail['encoding']:
                report_lines.append(
                    f"| {detail['file']} | {detail['encoding']} | {detail['confidence']} |"
                )
        report_lines.append("")
    
    if results['error_files'] > 0:
        report_lines.append("### ⚠️ 检查失败文件")
        report_lines.append("")
        report_lines.append("| 文件路径 | 错误信息 |")
        report_lines.append("|---------|---------|")
        
        for detail in results['details']:
            if 'error' in detail:
                report_lines.append(
                    f"| {detail['file']} | {detail['error']} |"
                )
        report_lines.append("")
    
    report_lines.extend([
        "## ✅ 建议操作",
        "",
        "### 立即修复（P0）",
        "",
        "对于非UTF-8编码的文件，建议立即转换为UTF-8编码：",
        "",
        "```python",
        "import codecs",
        "",
        "# 转换文件编码为UTF-8",
        "def convert_to_utf8(file_path, source_encoding):",
        "    with codecs.open(file_path, 'r', encoding=source_encoding) as f:",
        "        content = f.read()",
        "    with codecs.open(file_path, 'w', encoding='utf-8') as f:",
        "        f.write(content)",
        "```",
        "",
        "### 预防措施",
        "",
        "1. 在Git中设置`.gitattributes`文件，强制Markdown文件使用UTF-8编码",
        "2. 在编辑器中设置默认编码为UTF-8",
        "3. 使用pre-commit hook检查文件编码",
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
    output_file = 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/ENCODING_CHECK_REPORT_20260407.md'
    
    print(f"开始扫描 {docs_dir} 目录...")
    results = scan_docs_directory(docs_dir)
    
    print(f"扫描完成，共检查 {results['total_files']} 个文件")
    print(f"UTF-8文件: {results['utf8_files']}")
    print(f"非UTF-8文件: {results['non_utf8_files']}")
    print(f"错误文件: {results['error_files']}")
    
    report_path = generate_report(results, output_file)
    print(f"\n报告已生成: {report_path}")
    
    # 同时保存JSON格式的详细结果
    json_file = output_file.replace('.md', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"JSON结果已保存: {json_file}")

if __name__ == '__main__':
    main()
