#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
修复文档分类问题

功能:
1. 扫描所有蓝图文件
2. 检查是否缺少layer标识
3. 为缺少layer标识的文档添加正确的layer标识
"""

import os
import re
from pathlib import Path

class DocumentClassificationFixer:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.blueprint_files = []
        self.files_without_layer = []
        self.default_layer = "Layer 5 (策略执行层)"
    
    def run(self):
        """执行修复"""
        print('=' * 80)
        print('修复文档分类问题')
        print('=' * 80)
        print()
        
        # 1. 扫描所有蓝图文件
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
        print()
        
        # 2. 检查缺少layer标识的文件
        print('2. 检查缺少layer标识的文件...')
        self.check_layer_identification()
        print(f'  ⚠️ 发现{len(self.files_without_layer)}个文件缺少layer标识')
        print()
        
        # 3. 为缺少layer标识的文件添加layer标识
        if self.files_without_layer:
            print('3. 为缺少layer标识的文件添加layer标识...')
            self.add_layer_identification()
            print(f'  ✅ 已为{len(self.files_without_layer)}个文件添加layer标识')
            print()
        else:
            print('3. 所有文件都有layer标识，无需修复')
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
    
    def check_layer_identification(self):
        """检查缺少layer标识的文件"""
        for filename in self.blueprint_files:
            filepath = os.path.join(self.blueprints_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有layer标识
            if not re.search(r'layer:\s*[\'"]Layer', content):
                self.files_without_layer.append(filename)
        
        # 显示前10个缺少layer标识的文件
        if self.files_without_layer:
            print('  缺少layer标识的文件（前10个）:')
            for filename in self.files_without_layer[:10]:
                print(f'    - {filename}')
            if len(self.files_without_layer) > 10:
                print(f'    ... 还有{len(self.files_without_layer) - 10}个文件')
    
    def add_layer_identification(self):
        """为缺少layer标识的文件添加layer标识"""
        for filename in self.files_without_layer:
            filepath = os.path.join(self.blueprints_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找YAML头部
            yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                # 在YAML头部添加layer标识
                # 查找最后一个字段
                lines = yaml_content.split('\n')
                
                # 添加layer字段
                lines.append(f"layer: '{self.default_layer}'")
                
                # 重新构建YAML头部
                new_yaml = '\n'.join(lines)
                new_content = content.replace(yaml_content, new_yaml)
                
                # 写回文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f'    ✅ 已为 {filename} 添加layer标识')
            else:
                print(f'    ⚠️ {filename} 没有YAML头部，跳过')

if __name__ == '__main__':
    fixer = DocumentClassificationFixer()
    fixer.run()
