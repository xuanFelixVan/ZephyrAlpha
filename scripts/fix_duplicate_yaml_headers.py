#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复人机交互层重复YAML头部问题
删除重复的YAML头部，仅保留第一个完整的YAML元数据块
"""

import re
from pathlib import Path
from datetime import datetime

class DuplicateYAMLFixer:
    def __init__(self):
        self.layer_path = Path('docs/08_HUMAN_AI_INTERFACE')
        self.stats = {
            'scan_time': datetime.now().isoformat(),
            'total_files': 0,
            'files_with_duplicates': 0,
            'files_fixed': 0,
            'files_skipped': 0,
            'errors': [],
            'details': []
        }
    
    def fix_file(self, file_path):
        """修复单个文件的重复YAML头部"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.stats['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
            return False
        
        # 检查是否有重复的YAML头部
        yaml_count = content.count('---')
        if yaml_count <= 2:
            self.stats['files_skipped'] += 1
            return True
        
        # 提取第一个YAML头部
        yaml_pattern = re.compile(r'^(---\s*\n)(.*?)(\n---\s*\n)', re.DOTALL)
        match = yaml_pattern.match(content)
        
        if not match:
            self.stats['files_skipped'] += 1
            return True
        
        # 获取第一个YAML头部
        first_yaml = match.group(0)
        remaining_content = content[match.end():]
        
        # 删除剩余内容中的所有YAML头部
        # 查找所有后续的YAML块并删除
        cleaned_content = remaining_content
        
        # 删除所有后续的YAML块（从---到---之间的内容）
        yaml_block_pattern = re.compile(r'\n---\s*\n.*?\n---\s*\n', re.DOTALL)
        cleaned_content = yaml_block_pattern.sub('\n', cleaned_content)
        
        # 组合最终内容
        final_content = first_yaml + cleaned_content
        
        # 写回文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            self.stats['files_fixed'] += 1
            self.stats['details'].append({
                'file': str(file_path.relative_to(self.layer_path)),
                'original_yaml_count': yaml_count // 2,
                'status': 'fixed'
            })
            
            return True
        except Exception as e:
            self.stats['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
            return False
    
    def fix_all_files(self):
        """修复所有文件"""
        md_files = list(self.layer_path.rglob('*.md'))
        self.stats['total_files'] = len(md_files)
        
        print(f"开始处理 {len(md_files)} 个文件...")
        
        for i, md_file in enumerate(md_files, 1):
            if i % 10 == 0:
                print(f"  进度: {i}/{len(md_files)} ({i/len(md_files)*100:.1f}%)")
            
            # 检查文件是否有重复的YAML头部
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                yaml_count = content.count('---')
                if yaml_count > 2:
                    self.stats['files_with_duplicates'] += 1
                    result = self.fix_file(md_file)
                    if result:
                        print(f"  ✓ {md_file.relative_to(self.layer_path)}: 修复完成")
            except Exception as e:
                self.stats['errors'].append({
                    'file': str(md_file),
                    'error': str(e)
                })
        
        return self.stats
    
    def generate_report(self):
        """生成修复报告"""
        output_dir = Path('docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        report_file = output_dir / f'DUPLICATE_YAML_FIX_REPORT_{timestamp}.md'
        
        report_lines = [
            "# 重复YAML头部修复报告",
            "",
            f"> **修复时间**: {self.stats['scan_time']}",
            "",
            "## 📊 修复统计",
            "",
            f"- **扫描文件数**: {self.stats['total_files']}",
            f"- **发现重复YAML文件数**: {self.stats['files_with_duplicates']}",
            f"- **已修复文件数**: {self.stats['files_fixed']}",
            f"- **跳过文件数**: {self.stats['files_skipped']}",
            f"- **错误文件数**: {len(self.stats['errors'])}",
            ""
        ]
        
        if self.stats['details']:
            report_lines.extend([
                "## ✅ 已修复文件详情",
                "",
                "| 文件路径 | 原YAML数量 | 状态 |",
                "|---------|-----------|------|"
            ])
            
            for detail in self.stats['details']:
                report_lines.append(
                    f"| {detail['file']} | {detail['original_yaml_count']} | {detail['status']} |"
                )
            
            report_lines.append("")
        
        if self.stats['errors']:
            report_lines.extend([
                "## ❌ 错误详情",
                ""
            ])
            
            for error in self.stats['errors']:
                report_lines.append(f"- **{error['file']}**: {error['error']}")
            
            report_lines.append("")
        
        report_lines.extend([
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"\n✅ 修复报告已生成: {report_file}")
        
        return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("重复YAML头部修复工具")
    print("=" * 60)
    
    fixer = DuplicateYAMLFixer()
    stats = fixer.fix_all_files()
    
    print("\n" + "=" * 60)
    print("修复完成!")
    print("=" * 60)
    print(f"扫描文件数: {stats['total_files']}")
    print(f"发现重复YAML文件数: {stats['files_with_duplicates']}")
    print(f"已修复文件数: {stats['files_fixed']}")
    print(f"跳过文件数: {stats['files_skipped']}")
    print(f"错误文件数: {len(stats['errors'])}")
    
    fixer.generate_report()

if __name__ == '__main__':
    main()
