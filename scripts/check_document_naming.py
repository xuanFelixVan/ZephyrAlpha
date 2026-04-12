#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
文档命名规范检查脚本

功能：
1. 检查文件名是否包含中文字符
2. 检查文件名是否符合专业量化机构命名规范
3. 检查文件名是否使用正确的扩展名
4. 生成命名规范检查报告

使用方法：
    python check_document_naming.py [目录路径]

示例：
    python check_document_naming.py docs/
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class DocumentNamingChecker:
    """文档命名规范检查器"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.issues = []
        self.stats = {
            'total_files': 0,
            'chinese_files': 0,
            'non_standard_files': 0,
            'wrong_extension_files': 0
        }
        
    def has_chinese(self, text: str) -> bool:
        """检查字符串是否包含中文字符"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def is_standard_naming(self, filename: str) -> bool:
        """
        检查文件名是否符合专业量化机构命名规范
        
        规范：
        1. 使用大写字母、数字、下划线
        2. 不包含空格、中文、特殊字符
        3. 格式：MODULE_NAME_TYPE.md 或 P0-01_MODULE_NAME.md
        """
        # 移除扩展名
        name = Path(filename).stem
        
        # 检查是否符合标准格式
        patterns = [
            r'^[A-Z][A-Z0-9_]*$',  # 全大写下划线格式
            r'^P\d-\d+_[A-Z][A-Z0-9_]*$',  # P0-01格式
            r'^T\.\d+\.[A-Z]+\d+\.[a-z_]+$',  # T.08.AR001.a_stock_rule_engine_design格式
            r'^INDEX$',  # INDEX.md
            r'^README$',  # README.md
        ]
        
        for pattern in patterns:
            if re.match(pattern, name):
                return True
        
        return False
    
    def check_file(self, file_path: Path) -> Dict:
        """检查单个文件的命名规范"""
        filename = file_path.name
        
        issue = {
            'path': str(file_path.relative_to(self.root_dir)),
            'filename': filename,
            'issues': []
        }
        
        # 检查中文字符
        if self.has_chinese(filename):
            issue['issues'].append('包含中文字符')
            self.stats['chinese_files'] += 1
        
        # 检查命名规范
        if not self.is_standard_naming(filename):
            issue['issues'].append('不符合专业命名规范')
            self.stats['non_standard_files'] += 1
        
        # 检查扩展名
        if file_path.suffix.lower() not in ['.md', '.yaml', '.yml', '.json', '.csv']:
            if file_path.suffix.lower() in ['.txt', '.doc', '.docx']:
                issue['issues'].append(f'不推荐的扩展名: {file_path.suffix}')
                self.stats['wrong_extension_files'] += 1
        
        if issue['issues']:
            self.issues.append(issue)
        
        return issue
    
    def scan_directory(self):
        """扫描目录中的所有文件"""
        print(f"正在扫描目录: {self.root_dir}")
        
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file():
                # 跳过隐藏文件和特定目录
                if file_path.name.startswith('.') or \
                   any(part.startswith('.') for part in file_path.parts):
                    continue
                
                # 跳过非文档文件
                if file_path.suffix.lower() not in ['.md', '.yaml', '.yml', '.json', '.csv', '.txt']:
                    continue
                
                self.stats['total_files'] += 1
                self.check_file(file_path)
        
        print(f"扫描完成: 共检查 {self.stats['total_files']} 个文件")
    
    def generate_report(self) -> str:
        """生成命名规范检查报告"""
        report = []
        report.append("=" * 80)
        report.append("文档命名规范检查报告")
        report.append("=" * 80)
        report.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"检查目录: {self.root_dir}")
        report.append("")
        
        # 统计信息
        report.append("## 统计信息")
        report.append("-" * 80)
        report.append(f"总文件数: {self.stats['total_files']}")
        report.append(f"包含中文的文件: {self.stats['chinese_files']}")
        report.append(f"不符合命名规范的文件: {self.stats['non_standard_files']}")
        report.append(f"扩展名不推荐的文件: {self.stats['wrong_extension_files']}")
        report.append(f"问题文件总数: {len(self.issues)}")
        report.append("")
        
        # 问题详情
        if self.issues:
            report.append("## 问题详情")
            report.append("-" * 80)
            
            for i, issue in enumerate(self.issues, 1):
                report.append(f"\n{i}. {issue['path']}")
                report.append(f"   文件名: {issue['filename']}")
                report.append(f"   问题: {', '.join(issue['issues'])}")
        
        # 建议修复
        report.append("\n## 修复建议")
        report.append("-" * 80)
        
        if self.stats['chinese_files'] > 0:
            report.append(f"1. 重命名 {self.stats['chinese_files']} 个包含中文的文件")
        
        if self.stats['non_standard_files'] > 0:
            report.append(f"2. 重命名 {self.stats['non_standard_files']} 个不符合命名规范的文件")
        
        if self.stats['wrong_extension_files'] > 0:
            report.append(f"3. 修改 {self.stats['wrong_extension_files']} 个扩展名不推荐的文件")
        
        report.append("\n" + "=" * 80)
        report.append("检查完成")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, output_file: str):
        """保存报告到文件"""
        report = self.generate_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"报告已保存到: {output_file}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python check_document_naming.py [目录路径]")
        print("示例: python check_document_naming.py docs/")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    
    if not os.path.exists(root_dir):
        print(f"错误: 目录不存在: {root_dir}")
        sys.exit(1)
    
    # 创建检查器
    checker = DocumentNamingChecker(root_dir)
    
    # 扫描目录
    checker.scan_directory()
    
    # 生成报告
    report = checker.generate_report()
    print(report)
    
    # 保存报告
    output_file = f"naming_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    checker.save_report(output_file)
    
    # 返回退出码
    if checker.issues:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
