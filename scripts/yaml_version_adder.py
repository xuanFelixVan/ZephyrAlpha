#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAML版本号添加脚本
为缺少版本号的文档添加标准版本号
"""

import re
from pathlib import Path
from datetime import datetime
import json

class YAMLVersionAdder:
    def __init__(self, docs_root):
        self.docs_root = Path(docs_root)
        self.stats = {
            'scan_time': datetime.now().isoformat(),
            'total_files': 0,
            'files_with_version': 0,
            'files_without_version': 0,
            'files_updated': 0,
            'files_skipped': 0,
            'error_files': 0,
            'details': []
        }
    
    def _has_yaml_header(self, content):
        """检查是否有YAML头部"""
        return content.strip().startswith('---')
    
    def _has_version_field(self, content):
        """检查是否有version字段"""
        return bool(re.search(r'^version:\s*[^\s]+', content, re.MULTILINE))
    
    def _extract_version_from_filename(self, filename):
        """从文件名提取版本号"""
        # 匹配 _V数字 或 _v数字
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
    
    def _add_version_to_yaml(self, content, version='1.0.0'):
        """在YAML头部添加版本号"""
        # 检查是否有YAML头部
        if not self._has_yaml_header(content):
            # 添加YAML头部
            yaml_header = f"---\nversion: {version}\n---\n\n"
            return yaml_header + content
        
        # 找到YAML头部的结束位置
        yaml_pattern = re.compile(r'^(---\s*\n)(.*?)(\n---)', re.DOTALL)
        match = yaml_pattern.match(content)
        
        if match:
            yaml_header = match.group(2)
            # 在YAML头部添加version字段
            if yaml_header.strip():
                new_yaml_header = f"version: {version}\n{yaml_header}"
            else:
                new_yaml_header = f"version: {version}"
            
            new_content = match.group(1) + new_yaml_header + match.group(3) + content[match.end():]
            return new_content
        
        return content
    
    def process_file(self, file_path):
        """处理单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.stats['error_files'] += 1
            return {'file': str(file_path), 'error': str(e)}
        
        # 检查是否有版本号
        if self._has_version_field(content):
            self.stats['files_with_version'] += 1
            return {'file': str(file_path), 'status': 'already_has_version'}
        
        self.stats['files_without_version'] += 1
        
        # 尝试从文件名提取版本号
        filename = file_path.name
        version = self._extract_version_from_filename(filename)
        
        if not version:
            # 使用默认版本号
            version = '1.0.0'
        
        # 添加版本号
        new_content = self._add_version_to_yaml(content, version)
        
        # 写回文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.stats['files_updated'] += 1
            self.stats['details'].append({
                'file': str(file_path.relative_to(self.docs_root)).replace('\\', '/'),
                'version': version,
                'source': 'filename' if version != '1.0.0' else 'default',
                'status': 'updated'
            })
            
            return {'file': str(file_path), 'status': 'updated', 'version': version}
        except Exception as e:
            self.stats['error_files'] += 1
            return {'file': str(file_path), 'error': str(e)}
    
    def process_all_files(self):
        """处理所有文件"""
        md_files = list(self.docs_root.rglob('*.md'))
        self.stats['total_files'] = len(md_files)
        
        print(f"开始处理 {len(md_files)} 个文件...")
        
        for i, md_file in enumerate(md_files, 1):
            if i % 100 == 0:
                print(f"  进度: {i}/{len(md_files)} ({i/len(md_files)*100:.1f}%)")
            
            result = self.process_file(md_file)
            if result.get('status') == 'updated':
                print(f"  ✓ {result['file']}: 添加版本号 {result['version']}")
        
        return self.stats

def generate_report(stats, output_file):
    """生成报告"""
    report_lines = [
        "# YAML版本号添加报告",
        "",
        f"> **处理时间**: {stats['scan_time']}",
        "",
        "## 📊 处理概要",
        "",
        f"- **扫描文件数**: {stats['total_files']}",
        f"- **已有版本号文件数**: {stats['files_with_version']}",
        f"- **缺少版本号文件数**: {stats['files_without_version']}",
        f"- **已更新文件数**: {stats['files_updated']}",
        f"- **跳过文件数**: {stats['files_skipped']}",
        f"- **错误文件数**: {stats['error_files']}",
        ""
    ]
    
    if stats['files_updated'] > 0:
        report_lines.extend([
            "## ✅ 已更新文件详情（前100个）",
            "",
            "| 文件路径 | 版本号 | 来源 |",
            "|---------|--------|------|"
        ])
        
        for detail in stats['details'][:100]:
            report_lines.append(
                f"| {detail['file']} | {detail['version']} | {detail['source']} |"
            )
        report_lines.append("")
    
    report_lines.extend([
        "## 📝 版本号规则",
        "",
        "### 版本号来源优先级",
        "",
        "1. **文件名提取**: 从文件名中提取版本号（如 _V2, _V3）",
        "2. **默认版本号**: 如果无法提取，使用 1.0.0",
        "",
        "### 版本号格式",
        "",
        "```",
        "version: X.Y.Z",
        "```",
        "",
        "- **X**: 主版本号（重大变更）",
        "- **Y**: 次版本号（功能增加）",
        "- **Z**: 修订号（bug修复）",
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
    output_file = 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/YAML_VERSION_ADDITION_REPORT_20260407.md'
    
    print("=" * 60)
    print("YAML版本号添加工具")
    print("=" * 60)
    
    adder = YAMLVersionAdder(docs_root)
    stats = adder.process_all_files()
    
    print("\n" + "=" * 60)
    print("处理完成!")
    print("=" * 60)
    print(f"扫描文件数: {stats['total_files']}")
    print(f"已有版本号文件数: {stats['files_with_version']}")
    print(f"缺少版本号文件数: {stats['files_without_version']}")
    print(f"已更新文件数: {stats['files_updated']}")
    print(f"错误文件数: {stats['error_files']}")
    
    report_path = generate_report(stats, output_file)
    print(f"\n报告已生成: {report_path}")
    
    # 保存JSON格式结果
    json_file = output_file.replace('.md', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"JSON结果已保存: {json_file}")

if __name__ == '__main__':
    main()
