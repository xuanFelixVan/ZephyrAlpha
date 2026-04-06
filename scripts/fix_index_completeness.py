#!/usr/bin/env python3
"""
修复索引完备性问题

功能:
1. 扫描所有蓝图文件
2. 检查INDEX.md中是否已包含这些文件
3. 将未索引的文件添加到INDEX.md中
"""

import os
import re
from pathlib import Path

class IndexCompletenessFixer:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.index_file = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/INDEX.md'
        self.blueprint_files = []
        self.indexed_files = []
        self.missing_files = []
    
    def run(self):
        """执行修复"""
        print('=' * 80)
        print('修复索引完备性问题')
        print('=' * 80)
        print()
        
        # 1. 扫描所有蓝图文件
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
        print()
        
        # 2. 检查INDEX.md中已索引的文件
        print('2. 检查INDEX.md中已索引的文件...')
        self.check_indexed_files()
        print(f'  ✅ INDEX.md中已索引{len(self.indexed_files)}个文件')
        print()
        
        # 3. 找出未索引的文件
        print('3. 找出未索引的文件...')
        self.find_missing_files()
        print(f'  ⚠️ 发现{len(self.missing_files)}个未索引的文件')
        print()
        
        # 4. 将未索引的文件添加到INDEX.md
        if self.missing_files:
            print('4. 将未索引的文件添加到INDEX.md...')
            self.add_missing_files_to_index()
            print(f'  ✅ 已添加{len(self.missing_files)}个文件到INDEX.md')
            print()
        else:
            print('4. 无需添加文件，索引已完备')
            print()
        
        print('=' * 80)
        print('修复完成')
        print('=' * 80)
    
    def scan_blueprint_files(self):
        """扫描所有蓝图文件"""
        if os.path.exists(self.blueprints_dir):
            for filename in os.listdir(self.blueprints_dir):
                if filename.endswith('.md') and filename != 'INDEX.md':
                    self.blueprint_files.append(filename)
    
    def check_indexed_files(self):
        """检查INDEX.md中已索引的文件"""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取所有链接
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = re.findall(pattern, content)
            
            for text, url in matches:
                # 提取文件名
                if url.startswith('01_BLUEPRINTS/'):
                    filename = url.replace('01_BLUEPRINTS/', '')
                    self.indexed_files.append(filename)
    
    def find_missing_files(self):
        """找出未索引的文件"""
        for filename in self.blueprint_files:
            if filename not in self.indexed_files:
                self.missing_files.append(filename)
        
        # 显示前10个未索引的文件
        if self.missing_files:
            print('  未索引的文件（前10个）:')
            for filename in self.missing_files[:10]:
                print(f'    - {filename}')
            if len(self.missing_files) > 10:
                print(f'    ... 还有{len(self.missing_files) - 10}个文件')
    
    def add_missing_files_to_index(self):
        """将未索引的文件添加到INDEX.md"""
        # 读取INDEX.md内容
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到插入位置（在最后一个表格之后）
        # 查找最后一个 ## 标题
        lines = content.split('\n')
        insert_position = -1
        
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith('## '):
                insert_position = i
                break
        
        if insert_position == -1:
            print('  ❌ 无法找到插入位置')
            return
        
        # 创建新的分类
        new_section = '\n### 其他蓝图\n\n'
        new_section += '| 文件 | 职责 |\n'
        new_section += '|------|------|\n'
        
        for filename in sorted(self.missing_files):
            # 提取文件名作为职责描述
            name = filename.replace('_BLUEPRINT.md', '').replace('_', ' ')
            new_section += f'| [{filename}](01_BLUEPRINTS/{filename}) | {name} |\n'
        
        # 插入新内容
        lines.insert(insert_position, new_section)
        
        # 写回文件
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

if __name__ == '__main__':
    fixer = IndexCompletenessFixer()
    fixer.run()
