#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
自动补充索引脚本
根据未索引文件分析结果，自动补充索引
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

class IndexSupplementer:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.analysis_file = self.docs_root.parent / 'scripts' / 'unindexed_files_analysis.json'
        self.results = {
            'total_files': 0,
            'indexed_files': 0,
            'updated_indexes': 0,
            'errors': []
        }
    
    def load_analysis(self) -> Dict:
        """加载未索引文件分析结果"""
        with open(self.analysis_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_file_title(self, file_path: Path) -> str:
        """从文件中提取标题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试从YAML头部提取title
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                title_match = re.search(r'^title:\s*(.+)$', yaml_content, re.MULTILINE)
                if title_match:
                    return title_match.group(1).strip()
            
            # 尝试从第一个标题提取
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip()
            
            # 使用文件名作为标题
            return file_path.stem.replace('_', ' ').replace('-', ' ')
            
        except Exception as e:
            return file_path.stem.replace('_', ' ').replace('-', ' ')
    
    def get_file_description(self, file_path: Path, category: str) -> str:
        """生成文件描述"""
        # 根据文件类型生成描述
        descriptions = {
            '其他文档': '系统文档',
            '技术规格': '技术规格说明',
            '实施指南': '实施指南文档',
            '设计文档': '设计文档',
            '案例研究': '案例研究',
            '培训材料': '培训材料'
        }
        return descriptions.get(category, '系统文档')
    
    def find_parent_index(self, file_path: Path) -> Path:
        """找到文件所属的索引文件"""
        current_dir = file_path.parent
        
        # 查找最近的INDEX.md
        while current_dir != self.docs_root:
            index_file = current_dir / 'INDEX.md'
            if index_file.exists():
                return index_file
            current_dir = current_dir.parent
        
        # 如果没有找到，返回根目录的INDEX.md
        return self.docs_root / 'INDEX.md'
    
    def add_to_index(self, index_file: Path, file_path: Path, category: str) -> bool:
        """将文件添加到索引中"""
        try:
            # 读取索引文件内容
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查文件是否已经在索引中
            relative_path = file_path.relative_to(index_file.parent)
            if str(relative_path) in content or f"./{relative_path}" in content:
                return False
            
            # 获取文件信息
            title = self.get_file_title(file_path)
            description = self.get_file_description(file_path, category)
            
            # 生成索引条目
            if index_file == self.docs_root / 'INDEX.md':
                # 根索引使用绝对路径
                link_path = f"./{relative_path}"
            else:
                # 其他索引使用相对路径
                link_path = f"./{relative_path}"
            
            index_entry = f"- [{title}]({link_path}) - {description}\n"
            
            # 找到合适的插入位置
            # 查找"## 📚 文档列表"或类似的章节
            section_match = re.search(r'##\s+📚?\s*文档列表', content)
            if section_match:
                # 在章节后插入
                insert_pos = section_match.end()
                content = content[:insert_pos] + '\n' + index_entry + content[insert_pos:]
            else:
                # 查找"## 📝 变更历史"之前的章节
                history_match = re.search(r'##\s+📝?\s*变更历史', content)
                if history_match:
                    # 在变更历史前插入
                    insert_pos = history_match.start()
                    content = content[:insert_pos] + index_entry + '\n' + content[insert_pos:]
                else:
                    # 在文件末尾插入
                    content = content.rstrip() + '\n\n' + index_entry
            
            # 写入索引文件
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            self.results['errors'].append(f"添加文件 {file_path} 到索引 {index_file} 时出错: {str(e)}")
            return False
    
    def supplement_indexes(self):
        """补充索引"""
        print("=" * 80)
        print("自动补充索引")
        print("=" * 80)
        print(f"文档根目录: {self.docs_root}")
        print(f"分析文件: {self.analysis_file}")
        print()
        
        # 加载分析结果
        analysis = self.load_analysis()
        
        print(f"总未索引文件数: {analysis['unindexed_files']}")
        print()
        
        # 按优先级处理
        for recommendation in analysis['recommendations']:
            category = recommendation['category']
            priority = recommendation['priority']
            should_index = recommendation['should_index']
            
            print("=" * 80)
            print(f"处理类别: {category} (优先级: {priority})")
            print("=" * 80)
            print(f"需要索引的文件数: {should_index}")
            print()
            
            # 获取该类别的文件列表
            files = analysis['file_categories'].get(category, [])
            
            indexed_count = 0
            for file_str in files:
                file_path = Path(file_str)
                
                # 找到父索引
                parent_index = self.find_parent_index(file_path)
                
                # 添加到索引
                if self.add_to_index(parent_index, file_path, category):
                    indexed_count += 1
                    self.results['indexed_files'] += 1
                    print(f"  ✅ 添加: {file_path.relative_to(self.docs_root)}")
                
                # 限制处理的文件数量
                if indexed_count >= should_index:
                    break
            
            print(f"\n已索引文件数: {indexed_count}/{should_index}")
            print()
        
        print("=" * 80)
        print("补充统计")
        print("=" * 80)
        print(f"总处理文件数: {self.results['total_files']}")
        print(f"已索引文件数: {self.results['indexed_files']}")
        
        if self.results['errors']:
            print(f"\n错误数: {len(self.results['errors'])}")
            for error in self.results['errors']:
                print(f"  ❌ {error}")

if __name__ == "__main__":
    supplementer = IndexSupplementer()
    supplementer.supplement_indexes()
