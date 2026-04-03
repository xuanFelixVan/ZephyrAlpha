#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
架构更新脚本 - 将Layer 0-8架构更新为Layer 0-11架构
用途：系统性地更新所有文档中的架构引用
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
import json
from datetime import datetime

class ArchitectureUpdater:
    """架构更新器"""
    
    def __init__(self, docs_path: str):
        self.docs_path = Path(docs_path)
        self.updates_log = []
        self.stats = {
            'total_files': 0,
            'updated_files': 0,
            'skipped_files': 0,
            'error_files': 0
        }
        
        # 定义需要替换的模式
        self.replacement_patterns = [
            # Layer 0-8 -> Layer 0-11
            (r'Layer 0-8', 'Layer 0-11'),
            (r'Layer0-8', 'Layer0-11'),
            (r'layer 0-8', 'layer 0-11'),
            
            # Layer 0-7 -> Layer 0-11
            (r'Layer 0-7', 'Layer 0-11'),
            (r'Layer0-7', 'Layer0-11'),
            (r'layer 0-7', 'layer 0-11'),
            
            # 架构描述更新
            (r'八层架构', '十二层架构'),
            (r'8层架构', '12层架构'),
            (r'七层架构', '十二层架构'),
            (r'7层架构', '12层架构'),
            
            # 版本号更新
            (r'version: 5\.1\.0', 'version: 5.3.0'),
            (r'version: 5\.2\.0', 'version: 5.3.0'),
            (r'v5\.1', 'v5.3'),
            (r'v5\.2', 'v5.3'),
        ]
        
        # 排除的目录和文件
        self.exclude_dirs = {
            '06_ARCHIVE',  # 归档目录不更新
            '.git',
            '__pycache__',
            'node_modules'
        }
        
        self.exclude_files = {
            '.json',
            '.pyc',
            '.pyo',
            '.png',
            '.jpg',
            '.jpeg',
            '.gif',
            '.pdf'
        }
    
    def should_process_file(self, file_path: Path) -> bool:
        """判断是否应该处理该文件"""
        # 检查目录
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return False
        
        # 检查文件扩展名
        if file_path.suffix.lower() in self.exclude_files:
            return False
        
        # 只处理Markdown和文本文件
        return file_path.suffix.lower() in {'.md', '.txt', '.yaml', '.yml'}
    
    def update_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """更新单个文件"""
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            changes = []
            
            # 应用所有替换模式
            for pattern, replacement in self.replacement_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    changes.append(f"替换 '{pattern}' -> '{replacement}' ({len(matches)}次)")
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    f.write(content)
                
                return True, changes
            
            return False, []
            
        except Exception as e:
            return None, [f"错误: {str(e)}"]
    
    def scan_and_update(self) -> Dict:
        """扫描并更新所有文档"""
        print("=" * 80)
        print("架构更新脚本 - Layer 0-8 → Layer 0-11")
        print("=" * 80)
        print()
        
        # 遍历所有文件
        for file_path in self.docs_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            if not self.should_process_file(file_path):
                continue
            
            self.stats['total_files'] += 1
            
            # 更新文件
            updated, changes = self.update_file(file_path)
            
            if updated is True:
                self.stats['updated_files'] += 1
                rel_path = file_path.relative_to(self.docs_path)
                print(f"✅ 已更新: {rel_path}")
                for change in changes:
                    print(f"   - {change}")
                self.updates_log.append({
                    'file': str(rel_path),
                    'status': 'updated',
                    'changes': changes
                })
            elif updated is False:
                self.stats['skipped_files'] += 1
            else:
                self.stats['error_files'] += 1
                rel_path = file_path.relative_to(self.docs_path)
                print(f"❌ 错误: {rel_path}")
                for change in changes:
                    print(f"   - {change}")
                self.updates_log.append({
                    'file': str(rel_path),
                    'status': 'error',
                    'changes': changes
                })
        
        # 打印统计信息
        print()
        print("=" * 80)
        print("更新统计")
        print("=" * 80)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"已更新: {self.stats['updated_files']}")
        print(f"未变化: {self.stats['skipped_files']}")
        print(f"错误: {self.stats['error_files']}")
        print()
        
        return {
            'stats': self.stats,
            'updates_log': self.updates_log
        }
    
    def save_report(self, output_path: str):
        """保存更新报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'updates_log': self.updates_log
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 更新报告已保存: {output_path}")


def main():
    """主函数"""
    docs_path = r"D:\ZephyrAlpha\docs"
    output_path = r"D:\ZephyrAlpha\docs\architecture_update_report.json"
    
    updater = ArchitectureUpdater(docs_path)
    updater.scan_and_update()
    updater.save_report(output_path)
    
    print()
    print("✅ 架构更新完成！")


if __name__ == '__main__':
    main()
