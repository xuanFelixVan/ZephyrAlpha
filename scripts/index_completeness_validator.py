#!/usr/bin/env python3
"""
索引完整性验证脚本
检查所有活跃文档是否被索引，所有归档文档是否不在活跃索引中
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set

class IndexCompletenessValidator:
    def __init__(self, docs_root: str):
        self.docs_root = Path(docs_root)
        self.results = {
            'total_files': 0,
            'indexed_files': 0,
            'unindexed_files': 0,
            'archive_files_in_active_index': 0,
            'unindexed_details': [],
            'archive_in_active_details': []
        }
    
    def find_all_md_files(self) -> Dict[str, List[Path]]:
        """查找所有Markdown文件，分为活跃和归档两类"""
        active_files = []
        archive_files = []
        
        for root, dirs, files in os.walk(self.docs_root):
            # 跳过.git目录
            if '.git' in root:
                continue
            
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    
                    # 判断是否为归档文件
                    if '06_ARCHIVE' in str(file_path) or '99_ARCHIVE' in str(file_path):
                        archive_files.append(file_path)
                    else:
                        active_files.append(file_path)
        
        return {
            'active': active_files,
            'archive': archive_files
        }
    
    def find_all_index_files(self) -> List[Path]:
        """查找所有INDEX.md文件"""
        index_files = []
        for root, dirs, files in os.walk(self.docs_root):
            if '.git' in root:
                continue
            for file in files:
                if file == 'INDEX.md':
                    index_files.append(Path(root) / file)
        return index_files
    
    def extract_indexed_files(self, index_files: List[Path]) -> Set[str]:
        """从所有INDEX.md文件中提取被索引的文件"""
        indexed_files = set()
        
        for index_file in index_files:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取所有Markdown链接
            matches = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            for match in matches:
                text, url = match.groups()
                
                # 跳过外部链接和锚点链接
                if url.startswith('http://') or url.startswith('https://') or url.startswith('#'):
                    continue
                
                # 处理相对路径
                if url.startswith('./'):
                    target_path = index_file.parent / url[2:]
                elif url.startswith('../'):
                    target_path = index_file.parent / url
                else:
                    target_path = index_file.parent / url
                
                # 规范化路径
                try:
                    target_path = target_path.resolve()
                    # 只添加.md文件
                    if target_path.suffix == '.md':
                        indexed_files.add(str(target_path))
                except:
                    pass
        
        return indexed_files
    
    def run_validation(self) -> Dict:
        """运行完整验证"""
        print("=" * 80)
        print("索引完整性验证")
        print("=" * 80)
        print(f"文档根目录: {self.docs_root}")
        print()
        
        # 查找所有文件
        all_files = self.find_all_md_files()
        active_files = all_files['active']
        archive_files = all_files['archive']
        
        print(f"活跃文件数: {len(active_files)}")
        print(f"归档文件数: {len(archive_files)}")
        print()
        
        # 查找所有索引文件
        index_files = self.find_all_index_files()
        print(f"索引文件数: {len(index_files)}")
        print()
        
        # 提取被索引的文件
        indexed_files = self.extract_indexed_files(index_files)
        print(f"被索引的文件数: {len(indexed_files)}")
        print()
        
        # 检查活跃文件是否被索引
        print("=" * 80)
        print("检查活跃文件索引完整性")
        print("=" * 80)
        
        unindexed_active = []
        
        for active_file in active_files:
            # 跳过INDEX.md文件本身
            if active_file.name == 'INDEX.md':
                continue
            
            # 跳过README.md文件
            if active_file.name == 'README.md':
                continue
            
            # 跳过SITEMAP.md文件
            if active_file.name == 'SITEMAP.md':
                continue
            
            # 跳过FAQ.md文件
            if active_file.name == 'FAQ.md':
                continue
            
            # 跳过HANDOVER.md文件
            if active_file.name == 'HANDOVER.md':
                continue
            
            # 跳过审计状态文件
            if 'audit_state' in str(active_file):
                continue
            
            # 跳过维护记录文件
            if 'maintenance_records' in str(active_file):
                continue
            
            # 检查是否被索引
            if str(active_file.resolve()) not in indexed_files:
                unindexed_active.append(active_file)
        
        self.results['total_files'] = len(active_files)
        self.results['indexed_files'] = len(active_files) - len(unindexed_active)
        self.results['unindexed_files'] = len(unindexed_active)
        
        print(f"总活跃文件数: {self.results['total_files']}")
        print(f"已索引文件数: {self.results['indexed_files']}")
        print(f"未索引文件数: {self.results['unindexed_files']}")
        
        if self.results['total_files'] > 0:
            completeness_rate = (self.results['indexed_files'] / self.results['total_files']) * 100
            print(f"索引完整率: {completeness_rate:.1f}%")
        
        print()
        
        # 打印未索引文件详情
        if unindexed_active:
            print("=" * 80)
            print("未索引文件详情（前20个）")
            print("=" * 80)
            
            for i, file in enumerate(unindexed_active[:20], 1):
                relative_path = file.relative_to(self.docs_root)
                print(f"{i}. {relative_path}")
            
            if len(unindexed_active) > 20:
                print(f"... 还有 {len(unindexed_active) - 20} 个未索引文件")
        
        print()
        
        # 检查归档文件是否在活跃索引中
        print("=" * 80)
        print("检查归档文件是否在活跃索引中")
        print("=" * 80)
        
        archive_in_active = []
        
        for archive_file in archive_files:
            if str(archive_file.resolve()) in indexed_files:
                # 检查引用它的索引文件是否为活跃索引
                for index_file in index_files:
                    if '06_ARCHIVE' not in str(index_file) and '99_ARCHIVE' not in str(index_file):
                        with open(index_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 检查是否引用了归档文件
                        try:
                            relative_link = archive_file.relative_to(index_file.parent)
                            if str(relative_link) in content or f"./{relative_link}" in content:
                                archive_in_active.append({
                                    'archive_file': archive_file,
                                    'index_file': index_file
                                })
                        except ValueError:
                            # 归档文件不在索引文件的子路径中，跳过
                            pass
        
        self.results['archive_files_in_active_index'] = len(archive_in_active)
        
        print(f"在活跃索引中的归档文件数: {self.results['archive_files_in_active_index']}")
        
        print()
        print("=" * 80)
        
        if self.results['unindexed_files'] == 0 and self.results['archive_files_in_active_index'] == 0:
            print("✅ 索引完整性验证通过！")
        else:
            issues = []
            if self.results['unindexed_files'] > 0:
                issues.append(f"{self.results['unindexed_files']} 个未索引文件")
            if self.results['archive_files_in_active_index'] > 0:
                issues.append(f"{self.results['archive_files_in_active_index']} 个归档文件在活跃索引中")
            
            print(f"⚠️ 发现问题: {', '.join(issues)}")
        
        return self.results

def main():
    docs_root = r"D:\ZephyrAlpha\docs"
    validator = IndexCompletenessValidator(docs_root)
    results = validator.run_validation()
    
    # 返回退出码
    exit(0 if results['unindexed_files'] == 0 and results['archive_files_in_active_index'] == 0 else 1)

if __name__ == "__main__":
    main()
