#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BLUEPRINT文档最终优化脚本
彻底删除重复的YAML头部
"""

import os
import re
from pathlib import Path
from datetime import datetime

class BlueprintFinalOptimizer:
    def __init__(self, layer_path):
        self.layer_path = Path(layer_path)
        self.stats = {
            'total_files': 0,
            'yaml_fixed': 0,
            'errors': []
        }
    
    def optimize_all(self):
        """优化所有BLUEPRINT文件"""
        print("=" * 80)
        print("BLUEPRINT文档最终优化")
        print("=" * 80)
        print(f"优化范围: {self.layer_path}")
        print()
        
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        self.stats['total_files'] = len(blueprint_files)
        
        print(f"找到 {len(blueprint_files)} 个BLUEPRINT文件")
        print()
        
        for blueprint_file in blueprint_files:
            self.optimize_blueprint(blueprint_file)
        
        self.print_stats()
    
    def optimize_blueprint(self, blueprint_file):
        """优化单个BLUEPRINT文件"""
        try:
            with open(blueprint_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 删除重复的YAML头部
            content = self.fix_duplicate_yaml_v2(content)
            
            if content != original_content:
                with open(blueprint_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已优化: {blueprint_file.relative_to(self.layer_path)}")
            else:
                print(f"⏭️  跳过: {blueprint_file.relative_to(self.layer_path)} (无需修改)")
            
        except Exception as e:
            self.stats['errors'].append({
                'file': str(blueprint_file),
                'error': str(e)
            })
            print(f"❌ 错误: {blueprint_file.relative_to(self.layer_path)} - {e}")
    
    def fix_duplicate_yaml_v2(self, content):
        """删除重复的YAML头部（增强版）"""
        # 查找所有以---开头的行
        lines = content.split('\n')
        
        # 查找所有YAML块的起始和结束位置
        yaml_blocks = []
        in_yaml = False
        yaml_start = -1
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_yaml:
                    # 开始一个新的YAML块
                    in_yaml = True
                    yaml_start = i
                else:
                    # 结束当前YAML块
                    in_yaml = False
                    yaml_blocks.append((yaml_start, i))
        
        # 如果有多个YAML块，只保留第一个
        if len(yaml_blocks) > 1:
            # 保留第一个YAML块
            first_yaml_start, first_yaml_end = yaml_blocks[0]
            
            # 构建新内容
            new_lines = []
            
            # 添加第一个YAML块
            new_lines.extend(lines[first_yaml_start:first_yaml_end + 1])
            
            # 添加第一个YAML块之后的内容，跳过其他YAML块
            skip_ranges = []
            for start, end in yaml_blocks[1:]:
                skip_ranges.extend(range(start, end + 1))
            
            for i, line in enumerate(lines):
                if i > first_yaml_end and i not in skip_ranges:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
            self.stats['yaml_fixed'] += 1
        
        return content
    
    def print_stats(self):
        """输出统计信息"""
        print()
        print("=" * 80)
        print("优化统计")
        print("=" * 80)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"修复YAML头部: {self.stats['yaml_fixed']}")
        print(f"错误数: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print()
            print("错误详情:")
            for error in self.stats['errors']:
                print(f"  - {error['file']}: {error['error']}")


def main():
    layer_path = Path(r"D:\ZephyrAlpha\docs\08_HUMAN_AI_INTERFACE")
    
    optimizer = BlueprintFinalOptimizer(layer_path)
    optimizer.optimize_all()
    
    print()
    print("=" * 80)
    print("优化完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
