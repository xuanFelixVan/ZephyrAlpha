#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复无效链接脚本
自动修复文档索引中的无效链接
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
import sys

class InvalidLinkFixer:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.results = {
            'total_files': 0,
            'fixed_files': 0,
            'removed_links': 0,
            'errors': []
        }
    
    def find_all_index_files(self) -> List[Path]:
        """查找所有INDEX.md文件"""
        index_files = []
        for index_file in self.docs_root.rglob("INDEX.md"):
            index_files.append(index_file)
        return index_files
    
    def is_archive_index(self, file_path: Path) -> bool:
        """判断是否为归档目录的索引文件"""
        archive_indicators = ['06_ARCHIVE', '99_ARCHIVE', 'archive', 'archived']
        return any(indicator in str(file_path) for indicator in archive_indicators)
    
    def fix_archive_index_links(self, index_file: Path) -> Tuple[bool, int]:
        """修复归档目录索引中的无效链接"""
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            removed_count = 0
            
            # 查找所有相对路径链接
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = list(re.finditer(link_pattern, content))
            
            # 从后往前删除，避免位置偏移
            for match in reversed(matches):
                link_text = match.group(1)
                link_url = match.group(2)
                
                # 跳过外部链接和锚点链接
                if link_url.startswith('http://') or link_url.startswith('https://') or link_url.startswith('#'):
                    continue
                
                # 检查是否为审计相关的链接
                if '09_AUDIT' in link_url or 'MODULE_ID_REGISTRY' in link_url or 'RESPONSIBILITY_BOUNDARY' in link_url or 'PROFESSIONAL_DOCUMENT_GOVERNANCE' in link_url:
                    # 移除这行
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    
                    line = content[line_start:line_end]
                    
                    # 检查是否为表格行或列表项
                    if line.strip().startswith('|') or line.strip().startswith('-') or line.strip().startswith('*'):
                        content = content[:line_start] + content[line_end:]
                        removed_count += 1
            
            if content != original_content:
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, removed_count
            
            return False, 0
            
        except Exception as e:
            self.results['errors'].append(f"修复文件 {index_file} 时出错: {str(e)}")
            return False, 0
    
    def fix_regular_index_links(self, index_file: Path) -> Tuple[bool, int]:
        """修复常规索引中的无效链接"""
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            removed_count = 0
            
            # 查找所有相对路径链接
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = list(re.finditer(link_pattern, content))
            
            # 从后往前删除，避免位置偏移
            for match in reversed(matches):
                link_text = match.group(1)
                link_url = match.group(2)
                
                # 跳过外部链接和锚点链接
                if link_url.startswith('http://') or link_url.startswith('https://') or link_url.startswith('#'):
                    continue
                
                # 处理相对路径
                if link_url.startswith('./'):
                    target_path = index_file.parent / link_url[2:]
                elif link_url.startswith('../'):
                    target_path = index_file.parent / link_url
                else:
                    target_path = index_file.parent / link_url
                
                # 规范化路径
                try:
                    target_path = target_path.resolve()
                except:
                    continue
                
                # 检查文件是否存在
                if not target_path.exists():
                    # 移除这行
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    
                    line = content[line_start:line_end]
                    
                    # 检查是否为表格行或列表项
                    if line.strip().startswith('|') or line.strip().startswith('-') or line.strip().startswith('*'):
                        content = content[:line_start] + content[line_end:]
                        removed_count += 1
            
            if content != original_content:
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, removed_count
            
            return False, 0
            
        except Exception as e:
            self.results['errors'].append(f"修复文件 {index_file} 时出错: {str(e)}")
            return False, 0
    
    def run_fix(self):
        """运行修复"""
        print("=" * 80)
        print("无效链接修复")
        print("=" * 80)
        print(f"文档根目录: {self.docs_root}")
        print()
        
        # 查找所有索引文件
        index_files = self.find_all_index_files()
        print(f"找到索引文件数: {len(index_files)}")
        print()
        
        # 分类处理
        archive_indexes = [f for f in index_files if self.is_archive_index(f)]
        regular_indexes = [f for f in index_files if not self.is_archive_index(f)]
        
        print(f"归档目录索引文件数: {len(archive_indexes)}")
        print(f"常规索引文件数: {len(regular_indexes)}")
        print()
        
        # 修复归档目录索引
        print("=" * 80)
        print("修复归档目录索引")
        print("=" * 80)
        
        for index_file in archive_indexes:
            fixed, removed = self.fix_archive_index_links(index_file)
            if fixed:
                self.results['fixed_files'] += 1
                self.results['removed_links'] += removed
                print(f"✅ 修复: {index_file.relative_to(self.docs_root)} (移除 {removed} 个链接)")
        
        print()
        
        # 修复常规索引
        print("=" * 80)
        print("修复常规索引")
        print("=" * 80)
        
        for index_file in regular_indexes:
            fixed, removed = self.fix_regular_index_links(index_file)
            if fixed:
                self.results['fixed_files'] += 1
                self.results['removed_links'] += removed
                print(f"✅ 修复: {index_file.relative_to(self.docs_root)} (移除 {removed} 个链接)")
        
        print()
        print("=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总文件数: {len(index_files)}")
        print(f"修复文件数: {self.results['fixed_files']}")
        print(f"移除链接数: {self.results['removed_links']}")
        
        if self.results['errors']:
            print(f"\n错误数: {len(self.results['errors'])}")
            for error in self.results['errors']:
                print(f"  ❌ {error}")

if __name__ == "__main__":
    fixer = InvalidLinkFixer()
    fixer.run_fix()
