#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件编码修复工具 (无外部依赖版本)

功能：
1. 检测文件编码问题
2. 修复文件编码为UTF-8 without BOM
3. 生成修复报告

使用方法：
    python fix_file_encoding.py [目录路径] [--dry-run]

示例：
    python fix_file_encoding.py docs/01_FRAMEWORK --dry-run
    python fix_file_encoding.py docs/01_FRAMEWORK
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class FileEncodingFixer:
    """文件编码修复器"""
    
    def __init__(self, root_dir: str, dry_run: bool = False):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.results = {
            'total_files': 0,
            'fixed_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'details': []
        }
    
    def detect_and_read_file(self, file_path: Path) -> Tuple[str, str, str]:
        """
        检测文件编码并读取内容
        
        Returns:
            (encoding, content, error_message)
        """
        encodings_to_try = [
            'utf-8',
            'utf-8-sig',
            'gbk',
            'gb2312',
            'gb18030',
            'big5',
            'latin-1',
            'cp1252',
            'iso-8859-1'
        ]
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                    content = f.read()
                return encoding, content, None
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                return None, None, f"读取失败: {str(e)}"
        
        return None, None, "无法识别文件编码"
    
    def has_bom(self, file_path: Path) -> bool:
        """检查文件是否有BOM"""
        try:
            with open(file_path, 'rb') as f:
                first_bytes = f.read(3)
                return first_bytes == b'\xef\xbb\xbf'
        except:
            return False
    
    def fix_file_encoding(self, file_path: Path) -> Dict:
        """修复单个文件的编码"""
        result = {
            'file': str(file_path.relative_to(self.root_dir)),
            'original_encoding': None,
            'has_bom': False,
            'status': 'unknown',
            'message': ''
        }
        
        try:
            result['has_bom'] = self.has_bom(file_path)
            encoding, content, error = self.detect_and_read_file(file_path)
            
            if error:
                result['status'] = 'failed'
                result['message'] = error
                return result
            
            result['original_encoding'] = encoding
            
            if encoding == 'utf-8' and not result['has_bom']:
                result['status'] = 'skipped'
                result['message'] = f'已经是UTF-8编码 (无BOM)'
                return result
            
            if encoding == 'utf-8-sig' or (encoding == 'utf-8' and result['has_bom']):
                if self.dry_run:
                    result['status'] = 'dry_run'
                    result['message'] = f'将移除BOM: {encoding} -> UTF-8 (无BOM)'
                else:
                    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                        f.write(content)
                    result['status'] = 'fixed'
                    result['message'] = f'已移除BOM: {encoding} -> UTF-8 (无BOM)'
                return result
            
            if encoding in ['gbk', 'gb2312', 'gb18030', 'big5', 'latin-1', 'cp1252', 'iso-8859-1']:
                if self.dry_run:
                    result['status'] = 'dry_run'
                    result['message'] = f'将修复: {encoding} -> UTF-8'
                else:
                    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                        f.write(content)
                    result['status'] = 'fixed'
                    result['message'] = f'已修复: {encoding} -> UTF-8'
                return result
            
            result['status'] = 'skipped'
            result['message'] = f'编码 {encoding} 无需修复'
            return result
            
        except Exception as e:
            result['status'] = 'failed'
            result['message'] = f'修复失败: {str(e)}'
            return result
    
    def scan_and_fix(self) -> Dict:
        """扫描并修复所有Markdown文件"""
        print(f"开始扫描目录: {self.root_dir}")
        print(f"模式: {'干运行 (不实际修改文件)' if self.dry_run else '实际修复'}")
        print("-" * 80)
        
        md_files = list(self.root_dir.rglob('*.md'))
        self.results['total_files'] = len(md_files)
        
        print(f"找到 {len(md_files)} 个Markdown文件")
        print("-" * 80)
        
        for file_path in md_files:
            result = self.fix_file_encoding(file_path)
            self.results['details'].append(result)
            
            if result['status'] == 'fixed':
                self.results['fixed_files'] += 1
                print(f"[OK] {result['file']}: {result['message']}")
            elif result['status'] == 'dry_run':
                self.results['fixed_files'] += 1
                print(f"[DRY] {result['file']}: {result['message']}")
            elif result['status'] == 'failed':
                self.results['failed_files'] += 1
                print(f"[FAIL] {result['file']}: {result['message']}")
            else:
                self.results['skipped_files'] += 1
        
        return self.results
    
    def generate_report(self) -> str:
        """生成修复报告"""
        report = []
        report.append("=" * 80)
        report.append("文件编码修复报告")
        report.append("=" * 80)
        report.append(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"扫描目录: {self.root_dir}")
        report.append(f"模式: {'干运行' if self.dry_run else '实际修复'}")
        report.append("")
        
        report.append("## 统计信息")
        report.append("-" * 80)
        report.append(f"总文件数: {self.results['total_files']}")
        report.append(f"修复文件数: {self.results['fixed_files']}")
        report.append(f"失败文件数: {self.results['failed_files']}")
        report.append(f"跳过文件数: {self.results['skipped_files']}")
        report.append("")
        
        if self.results['fixed_files'] > 0:
            report.append("## 修复详情")
            report.append("-" * 80)
            for detail in self.results['details']:
                if detail['status'] in ['fixed', 'dry_run']:
                    report.append(f"- {detail['file']}: {detail['message']}")
            report.append("")
        
        if self.results['failed_files'] > 0:
            report.append("## 失败详情")
            report.append("-" * 80)
            for detail in self.results['details']:
                if detail['status'] == 'failed':
                    report.append(f"- {detail['file']}: {detail['message']}")
            report.append("")
        
        report.append("**修复工具**: fix_file_encoding.py v2.0.0 (无外部依赖版)")
        report.append(f"**修复日期**: {datetime.now().strftime('%Y-%m-%d')}")
        
        return "\n".join(report)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='文件编码修复工具')
    parser.add_argument('directory', help='要扫描的目录路径')
    parser.add_argument('--dry-run', action='store_true', help='干运行模式，不实际修改文件')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"错误: 目录不存在 - {args.directory}")
        sys.exit(1)
    
    fixer = FileEncodingFixer(args.directory, args.dry_run)
    fixer.scan_and_fix()
    
    print("\n" + fixer.generate_report())


if __name__ == '__main__':
    main()
