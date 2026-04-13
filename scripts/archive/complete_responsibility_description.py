#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
完善职责描述

功能:
1. 扫描所有蓝图文件
2. 检查缺少职责描述的文档
3. 为缺少职责描述的文档添加核心定位
"""

import os
import re
from pathlib import Path

class ResponsibilityDescriptionCompleter:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.blueprint_files = []
        self.files_without_responsibility = []
    
    def run(self):
        """执行完善"""
        print('=' * 80)
        print('完善职责描述')
        print('=' * 80)
        print()
        
        # 1. 扫描所有蓝图文件
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
        print()
        
        # 2. 检查缺少职责描述的文件
        print('2. 检查缺少职责描述的文件...')
        self.check_responsibility_description()
        print(f'  ⚠️ 发现{len(self.files_without_responsibility)}个文件缺少职责描述')
        print()
        
        # 3. 为缺少职责描述的文件添加核心定位
        if self.files_without_responsibility:
            print('3. 为缺少职责描述的文件添加核心定位...')
            self.add_responsibility_description()
            print(f'  ✅ 已为{len(self.files_without_responsibility)}个文件添加职责描述')
            print()
        else:
            print('3. 所有文件都有职责描述，无需完善')
            print()
        
        print('=' * 80)
        print('完善完成')
        print('=' * 80)
    
    def scan_blueprint_files(self):
        """扫描所有蓝图文件"""
        if os.path.exists(self.blueprints_dir):
            for filename in os.listdir(self.blueprints_dir):
                if filename.endswith('.md') and filename != 'INDEX.md':
                    self.blueprint_files.append(filename)
    
    def check_responsibility_description(self):
        """检查缺少职责描述的文件"""
        for filename in self.blueprint_files:
            filepath = os.path.join(self.blueprints_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有核心定位或核心职责
            if not re.search(r'核心定位[：:]', content) and not re.search(r'核心职责[：:]', content):
                self.files_without_responsibility.append(filename)
        
        # 显示前10个缺少职责描述的文件
        if self.files_without_responsibility:
            print('  缺少职责描述的文件（前10个）:')
            for filename in self.files_without_responsibility[:10]:
                print(f'    - {filename}')
            if len(self.files_without_responsibility) > 10:
                print(f'    ... 还有{len(self.files_without_responsibility) - 10}个文件')
    
    def add_responsibility_description(self):
        """为缺少职责描述的文件添加核心定位"""
        for filename in self.files_without_responsibility:
            filepath = os.path.join(self.blueprints_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 从文件名生成职责描述
            name = filename.replace('_BLUEPRINT.md', '').replace('_', ' ')
            
            # 查找标题
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else name
            
            # 在标题后添加核心定位
            lines = content.split('\n')
            new_lines = []
            title_found = False
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # 在标题后添加核心定位
                if line.startswith('# ') and not title_found:
                    title_found = True
                    # 添加空行和核心定位
                    new_lines.append('')
                    new_lines.append(f'> **核心定位**: {title}的核心功能实现')
                    new_lines.append('')
            
            # 写回文件
            new_content = '\n'.join(new_lines)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f'    ✅ 已为 {filename} 添加职责描述')

if __name__ == '__main__':
    completer = ResponsibilityDescriptionCompleter()
    completer.run()
