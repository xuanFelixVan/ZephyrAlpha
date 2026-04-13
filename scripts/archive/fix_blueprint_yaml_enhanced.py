#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
BLUEPRINT文档YAML修复脚本（增强版）
处理复杂的YAML头部重复问题
"""

import re
from pathlib import Path

class BlueprintYAMLFixerEnhanced:
    def __init__(self, layer_path):
        self.layer_path = Path(layer_path)
        self.stats = {
            'total_files': 0,
            'yaml_fixed': 0,
            'errors': []
        }
    
    def fix_all(self):
        """修复所有BLUEPRINT文件"""
        print("=" * 80)
        print("BLUEPRINT文档YAML修复（增强版）")
        print("=" * 80)
        print(f"修复范围: {self.layer_path}")
        print()
        
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        self.stats['total_files'] = len(blueprint_files)
        
        print(f"找到 {len(blueprint_files)} 个BLUEPRINT文件")
        print()
        
        for blueprint_file in blueprint_files:
            self.fix_blueprint(blueprint_file)
        
        self.print_stats()
    
    def fix_blueprint(self, blueprint_file):
        """修复单个BLUEPRINT文件"""
        try:
            with open(blueprint_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 查找所有---行的位置
            lines = content.split('\n')
            dash_lines = []
            for i, line in enumerate(lines):
                if line.strip() == '---':
                    dash_lines.append(i)
            
            # 如果有3个或更多---行，说明有重复的YAML块
            if len(dash_lines) >= 3:
                # 第一个YAML块：从第0个---到第1个---
                # 第二个YAML块：从第2个---开始，需要找到它的结束标记
                
                # 构建新内容：只保留第一个YAML块
                first_yaml_end = dash_lines[1]
                
                # 查找第二个YAML块的结束位置
                # 如果有第4个---，那么第二个YAML块在第2个---和第3个---之间
                # 如果没有第4个---，那么第二个YAML块从第2个---开始，直到遇到非YAML内容
                
                if len(dash_lines) >= 4:
                    # 有第4个---，第二个YAML块在第2个---和第3个---之间
                    second_yaml_end = dash_lines[3]
                    # 删除第2个---到第3个---之间的内容
                    new_lines = lines[:first_yaml_end + 1] + lines[second_yaml_end + 1:]
                else:
                    # 没有第4个---，需要找到第二个YAML块的结束位置
                    # 从第2个---开始，查找第一个非YAML内容
                    
                    # 简单处理：删除第2个---之后的所有内容，直到遇到##标题
                    second_yaml_start = dash_lines[2]
                    
                    # 查找第一个##标题的位置
                    first_chapter = -1
                    for i in range(second_yaml_start + 1, len(lines)):
                        if lines[i].startswith('##'):
                            first_chapter = i
                            break
                    
                    if first_chapter > 0:
                        # 删除第2个---到第一个##标题之间的内容
                        new_lines = lines[:first_yaml_end + 1] + lines[first_chapter:]
                    else:
                        # 没有找到##标题，保留原样
                        new_lines = lines
                
                content = '\n'.join(new_lines)
                
                if content != original_content:
                    with open(blueprint_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.stats['yaml_fixed'] += 1
                    print(f"✅ 已修复: {blueprint_file.relative_to(self.layer_path)}")
                else:
                    print(f"⏭️  跳过: {blueprint_file.relative_to(self.layer_path)} (无需修改)")
            else:
                print(f"⏭️  跳过: {blueprint_file.relative_to(self.layer_path)} (无需修改)")
            
        except Exception as e:
            self.stats['errors'].append({
                'file': str(blueprint_file),
                'error': str(e)
            })
            print(f"❌ 错误: {blueprint_file.relative_to(self.layer_path)} - {e}")
    
    def print_stats(self):
        """输出统计信息"""
        print()
        print("=" * 80)
        print("修复统计")
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
    
    fixer = BlueprintYAMLFixerEnhanced(layer_path)
    fixer.fix_all()
    
    print()
    print("=" * 80)
    print("修复完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
