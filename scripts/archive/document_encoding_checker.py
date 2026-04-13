# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
文档编码检查和修复工具

功能：
1. 检查所有Markdown文件的编码
2. 验证是否符合UTF-8 without BOM标准
3. 自动修复编码问题
4. 生成检查报告

使用方法：
    python scripts/document_encoding_checker.py --check docs/
    python scripts/document_encoding_checker.py --fix docs/
    python scripts/document_encoding_checker.py --report docs/
"""

import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class DocumentEncodingChecker:
    """文档编码检查器"""
    
    def __init__(self):
        self.results: List[Dict] = []
        self.total_files = 0
        self.passed_files = 0
        self.failed_files = 0
        self.fixed_files = 0
    
    def check_file_encoding(self, file_path: Path) -> Tuple[str, bool]:
        """
        检查文件编码
        
        Returns:
            (encoding, is_valid): 编码类型和是否有效
        """
        with open(file_path, 'rb') as f:
            raw = f.read(3)
        
        if raw.startswith(b'\xef\xbb\xbf'):
            return 'UTF-8 with BOM', False
        elif raw.startswith(b'\xff\xfe'):
            return 'UTF-16 LE', False
        elif raw.startswith(b'\xfe\xff'):
            return 'UTF-16 BE', False
        else:
            return 'UTF-8 without BOM', True
    
    def check_line_endings(self, file_path: Path) -> Tuple[str, bool]:
        """
        检查换行符
        
        Returns:
            (line_ending, is_valid): 换行符类型和是否有效
        """
        with open(file_path, 'rb') as f:
            content = f.read()
        
        if b'\r\n' in content:
            return 'CRLF', False
        elif b'\r' in content:
            return 'CR', False
        else:
            return 'LF', True
    
    def check_file(self, file_path: Path) -> Dict:
        """
        检查单个文件
        
        Returns:
            检查结果字典
        """
        encoding, encoding_valid = self.check_file_encoding(file_path)
        line_ending, line_ending_valid = self.check_line_endings(file_path)
        
        is_valid = encoding_valid and line_ending_valid
        
        result = {
            'file': str(file_path),
            'encoding': encoding,
            'encoding_valid': encoding_valid,
            'line_ending': line_ending,
            'line_ending_valid': line_ending_valid,
            'is_valid': is_valid
        }
        
        return result
    
    def check_directory(self, directory: Path) -> List[Dict]:
        """
        检查目录下所有Markdown文件
        
        Returns:
            检查结果列表
        """
        self.results = []
        self.total_files = 0
        self.passed_files = 0
        self.failed_files = 0
        
        for md_file in directory.rglob('*.md'):
            self.total_files += 1
            result = self.check_file(md_file)
            self.results.append(result)
            
            if result['is_valid']:
                self.passed_files += 1
                print(f"✅ {md_file.relative_to(directory)}")
            else:
                self.failed_files += 1
                issues = []
                if not result['encoding_valid']:
                    issues.append(f"编码: {result['encoding']}")
                if not result['line_ending_valid']:
                    issues.append(f"换行符: {result['line_ending']}")
                print(f"❌ {md_file.relative_to(directory)} - {', '.join(issues)}")
        
        return self.results
    
    def fix_file(self, file_path: Path) -> bool:
        """
        修复文件编码和换行符
        
        Returns:
            是否成功修复
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 统一换行符为LF
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            
            # 写回文件，使用UTF-8 without BOM
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"⚠️ 修复失败: {file_path} - {str(e)}")
            return False
    
    def fix_directory(self, directory: Path) -> int:
        """
        修复目录下所有有问题的Markdown文件
        
        Returns:
            修复的文件数量
        """
        self.fixed_files = 0
        
        for md_file in directory.rglob('*.md'):
            result = self.check_file(md_file)
            
            if not result['is_valid']:
                if self.fix_file(md_file):
                    self.fixed_files += 1
                    print(f"✅ 已修复: {md_file.relative_to(directory)}")
        
        return self.fixed_files
    
    def generate_report(self, directory: Path, output_file: Path = None) -> str:
        """
        生成检查报告
        
        Returns:
            报告内容
        """
        if not self.results:
            self.check_directory(directory)
        
        report_lines = [
            "# 文档编码检查报告",
            "",
            f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**检查目录**: {directory}",
            "",
            "## 📊 检查统计",
            "",
            f"- **总文件数**: {self.total_files}",
            f"- **通过文件数**: {self.passed_files}",
            f"- **失败文件数**: {self.failed_files}",
            f"- **通过率**: {self.passed_files / self.total_files * 100:.2f}%" if self.total_files > 0 else "- **通过率**: 0%",
            "",
            "## ❌ 问题文件列表",
            ""
        ]
        
        failed_results = [r for r in self.results if not r['is_valid']]
        
        if failed_results:
            for result in failed_results:
                issues = []
                if not result['encoding_valid']:
                    issues.append(f"编码: {result['encoding']}")
                if not result['line_ending_valid']:
                    issues.append(f"换行符: {result['line_ending']}")
                
                report_lines.append(f"- `{result['file']}` - {', '.join(issues)}")
        else:
            report_lines.append("✅ 所有文件都符合编码规范！")
        
        report_lines.extend([
            "",
            "---",
            "",
            f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        report = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 报告已保存到: {output_file}")
        
        return report


def main():
    parser = argparse.ArgumentParser(description='文档编码检查和修复工具')
    parser.add_argument('directory', type=str, help='要检查的目录路径')
    parser.add_argument('--check', action='store_true', help='检查文档编码')
    parser.add_argument('--fix', action='store_true', help='修复编码问题')
    parser.add_argument('--report', action='store_true', help='生成检查报告')
    parser.add_argument('--output', type=str, help='报告输出文件路径')
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"❌ 目录不存在: {directory}")
        return
    
    checker = DocumentEncodingChecker()
    
    if args.check:
        print("=== 检查文档编码 ===\n")
        checker.check_directory(directory)
        print(f"\n📊 检查完成: {checker.passed_files}/{checker.total_files} 文件通过")
    
    if args.fix:
        print("\n=== 修复编码问题 ===\n")
        fixed_count = checker.fix_directory(directory)
        print(f"\n✅ 修复完成: 共修复 {fixed_count} 个文件")
    
    if args.report:
        print("\n=== 生成检查报告 ===\n")
        output_file = Path(args.output) if args.output else None
        report = checker.generate_report(directory, output_file)
        if not output_file:
            print(report)


if __name__ == '__main__':
    main()
