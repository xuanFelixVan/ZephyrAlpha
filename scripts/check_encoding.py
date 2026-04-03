#!/usr/bin/env python3
"""
编码规范检查脚本
定期检查所有文档文件的编码规范，确保符合UTF-8标准

使用方法:
    python scripts/check_encoding.py                    # 检查所有文档
    python scripts/check_encoding.py docs/01_FRAMEWORK/ # 检查特定目录
    python scripts/check_encoding.py --report report.md # 生成报告
    python scripts/check_encoding.py --fix              # 自动修复编码问题
"""

import os
import sys
import argparse
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class EncodingChecker:
    """编码检查器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.allowed_encodings = ['utf-8', 'utf-8-sig', 'ascii', 'us-ascii']
        self.text_extensions = [
            '.md', '.txt', '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h',
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.sh', '.bat', '.ps1', '.html', '.css', '.xml', '.sql',
            '.gitignore', '.editorconfig', '.env', '.rst', '.adoc'
        ]
        
        self.results = {
            'total_files': 0,
            'text_files': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'issues': []
        }
    
    def is_text_file(self, filepath: Path) -> bool:
        """判断是否为文本文件"""
        if not filepath.exists():
            return False
        
        # 检查文件扩展名
        if filepath.suffix.lower() in self.text_extensions:
            return True
        
        # 使用mimetypes判断
        mime_type, _ = mimetypes.guess_type(str(filepath))
        if mime_type and mime_type.startswith('text/'):
            return True
        
        # 尝试读取文件判断
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(8192)
                if b'\x00' in chunk:
                    return False
                try:
                    chunk.decode('utf-8')
                    return True
                except:
                    return False
        except:
            return False
    
    def detect_encoding(self, filepath: Path) -> str:
        """检测文件编码"""
        try:
            with open(filepath, 'rb') as f:
                raw = f.read(4)
            
            # 检查BOM
            if raw.startswith(b'\xff\xfe'):
                return 'utf-16-le'
            elif raw.startswith(b'\xfe\xff'):
                return 'utf-16-be'
            elif raw.startswith(b'\xef\xbb\xbf'):
                return 'utf-8-sig'
            
            # 尝试UTF-8
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    f.read()
                return 'utf-8'
            except:
                pass
            
            # 尝试其他编码
            encodings = ['gbk', 'gb18030', 'latin-1', 'cp1252']
            for enc in encodings:
                try:
                    with open(filepath, 'r', encoding=enc) as f:
                        f.read()
                    return enc
                except:
                    pass
            
            return 'unknown'
        except:
            return 'error'
    
    def check_file(self, filepath: Path) -> Dict:
        """检查单个文件"""
        result = {
            'path': str(filepath.relative_to(self.root_dir)),
            'encoding': None,
            'status': 'skipped',
            'message': ''
        }
        
        if not filepath.exists():
            result['status'] = 'error'
            result['message'] = '文件不存在'
            return result
        
        if not self.is_text_file(filepath):
            result['status'] = 'skipped'
            result['message'] = '非文本文件'
            return result
        
        encoding = self.detect_encoding(filepath)
        result['encoding'] = encoding
        
        # 标准化编码名称
        encoding_lower = encoding.lower()
        if encoding_lower in ['utf-8', 'utf-8-sig', 'ascii', 'us-ascii']:
            result['status'] = 'passed'
            result['message'] = f'编码正确 ({encoding})'
        else:
            result['status'] = 'failed'
            result['message'] = f'编码错误 ({encoding})，应为UTF-8'
        
        return result
    
    def check_directory(self, directory: Path = None) -> List[Dict]:
        """检查目录下所有文件"""
        if directory is None:
            directory = self.root_dir
        
        results = []
        
        # 遍历目录
        for filepath in directory.rglob('*'):
            if filepath.is_file():
                self.results['total_files'] += 1
                
                result = self.check_file(filepath)
                results.append(result)
                
                if result['status'] == 'skipped':
                    self.results['skipped'] += 1
                elif result['status'] == 'passed':
                    self.results['passed'] += 1
                    self.results['text_files'] += 1
                elif result['status'] == 'failed':
                    self.results['failed'] += 1
                    self.results['text_files'] += 1
                    self.results['issues'].append(result)
        
        return results
    
    def fix_encoding(self, filepath: Path) -> bool:
        """修复文件编码"""
        try:
            encoding = self.detect_encoding(filepath)
            
            if encoding.lower() in ['utf-8', 'utf-8-sig', 'ascii', 'us-ascii']:
                return True
            
            # 读取文件内容
            with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()
            
            # 写入UTF-8编码
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"修复失败: {filepath} - {e}")
            return False
    
    def generate_report(self, output_file: str = None) -> str:
        """生成检查报告"""
        report = []
        report.append("# 编码规范检查报告")
        report.append("")
        report.append(f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**检查范围**: {self.root_dir}")
        report.append("")
        
        # 统计信息
        report.append("## 一、统计信息")
        report.append("")
        report.append(f"- **总文件数**: {self.results['total_files']}")
        report.append(f"- **文本文件数**: {self.results['text_files']}")
        report.append(f"- **通过检查**: {self.results['passed']}")
        report.append(f"- **未通过检查**: {self.results['failed']}")
        report.append(f"- **跳过检查**: {self.results['skipped']}")
        report.append("")
        
        # 合规率
        if self.results['text_files'] > 0:
            compliance_rate = (self.results['passed'] / self.results['text_files']) * 100
            report.append(f"**编码合规率**: {compliance_rate:.2f}%")
        else:
            report.append("**编码合规率**: N/A")
        report.append("")
        
        # 问题列表
        if self.results['issues']:
            report.append("## 二、问题文件列表")
            report.append("")
            report.append("| 文件路径 | 当前编码 | 状态 |")
            report.append("|---------|---------|------|")
            for issue in self.results['issues']:
                report.append(f"| {issue['path']} | {issue['encoding']} | ❌ {issue['message']} |")
            report.append("")
            
            # 修复建议
            report.append("## 三、修复建议")
            report.append("")
            report.append("### 3.1 手动修复")
            report.append("")
            report.append("1. 在编辑器中打开文件")
            report.append("2. 选择 'Save with Encoding' 或 '另存为编码'")
            report.append("3. 选择 'UTF-8' 编码")
            report.append("4. 保存文件")
            report.append("")
            report.append("### 3.2 自动修复")
            report.append("")
            report.append("运行以下命令自动修复编码问题：")
            report.append("")
            report.append("```bash")
            report.append("python scripts/check_encoding.py --fix")
            report.append("```")
            report.append("")
        else:
            report.append("## 二、检查结果")
            report.append("")
            report.append("✅ 所有文本文件编码符合规范")
            report.append("")
        
        report_content = '\n'.join(report)
        
        # 写入文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return report_content

def main():
    parser = argparse.ArgumentParser(description='编码规范检查脚本')
    parser.add_argument('path', nargs='?', default='.', help='要检查的路径')
    parser.add_argument('--report', '-r', help='生成报告文件')
    parser.add_argument('--fix', '-f', action='store_true', help='自动修复编码问题')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    # 创建检查器
    checker = EncodingChecker(args.path)
    
    print("🔍 开始编码规范检查...")
    print(f"检查路径: {checker.root_dir}")
    print()
    
    # 执行检查
    results = checker.check_directory()
    
    # 显示结果
    if args.verbose:
        print("\n详细检查结果:")
        print("-" * 80)
        for result in results:
            status_icon = {
                'passed': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'error': '⚠️'
            }.get(result['status'], '❓')
            print(f"{status_icon} {result['path']:60s} {result['encoding'] or 'N/A':15s} {result['message']}")
    
    # 自动修复
    if args.fix and checker.results['issues']:
        print("\n🔧 开始自动修复编码问题...")
        fixed_count = 0
        for issue in checker.results['issues']:
            filepath = checker.root_dir / issue['path']
            if checker.fix_encoding(filepath):
                print(f"✅ 已修复: {issue['path']}")
                fixed_count += 1
            else:
                print(f"❌ 修复失败: {issue['path']}")
        print(f"\n修复完成: {fixed_count}/{len(checker.results['issues'])} 个文件")
    
    # 生成报告
    if args.report:
        report = checker.generate_report(args.report)
        print(f"\n📄 报告已生成: {args.report}")
    else:
        report = checker.generate_report()
        print("\n" + report)
    
    # 返回退出码
    if checker.results['failed'] > 0:
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
