#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复YAML头部问题并标准化layer字段
"""

import re
import os
from pathlib import Path

def fix_yaml_and_layer(file_path):
    """修复YAML头部问题并标准化layer字段"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有YAML头部
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        yaml_matches = list(re.finditer(yaml_pattern, content, re.DOTALL))
        
        if not yaml_matches:
            return False, '未找到YAML头部'
        
        # 如果有多个YAML头部，只保留第一个
        if len(yaml_matches) > 1:
            first_yaml = yaml_matches[0]
            second_yaml = yaml_matches[1]
            
            # 提取第一个YAML内容
            first_yaml_content = first_yaml.group(1)
            
            # 检查第一个YAML是否有layer字段
            if 'layer:' not in first_yaml_content:
                # 从第二个YAML中提取layer字段
                second_yaml_content = second_yaml.group(1)
                layer_match = re.search(r'^layer:\s*(.+)$', second_yaml_content, re.MULTILINE)
                
                if layer_match:
                    layer_value = layer_match.group(1).strip()
                    
                    # 去除引号
                    if layer_value.startswith('"') and layer_value.endswith('"'):
                        layer_value = layer_value[1:-1]
                    elif layer_value.startswith("'") and layer_value.endswith("'"):
                        layer_value = layer_value[1:-1]
                    
                    # 提取Layer编号并标准化
                    layer_num_match = re.search(r'Layer (\d+)', layer_value)
                    if layer_num_match:
                        layer_num = layer_num_match.group(1)
                        layer_names = {
                            '0': 'Layer 0 (数据源层)',
                            '1': 'Layer 1 (数据层)',
                            '2': 'Layer 2 (Alpha因子层)',
                            '3': 'Layer 3 (策略层)',
                            '4': 'Layer 4 (机器学习层)',
                            '5': 'Layer 5 (执行层)',
                            '6': 'Layer 6 (组合优化层)',
                            '7': 'Layer 7 (风控层)',
                            '8': 'Layer 8 (人机交互层)',
                            '9': 'Layer 9 (治理层)',
                            '10': 'Layer 10 (治理层)',
                            '11': 'Layer 11 (战略决策层)',
                        }
                        layer_value = layer_names.get(layer_num, f'Layer {layer_num}')
                    
                    # 在第一个YAML中添加layer字段
                    if 'owner:' in first_yaml_content:
                        first_yaml_content = re.sub(
                            r'(owner:.*?\n)',
                            r'\1layer: ' + layer_value + '\n',
                            first_yaml_content
                        )
                    elif 'module_id:' in first_yaml_content:
                        first_yaml_content = re.sub(
                            r'(module_id:.*?\n)',
                            r'\1layer: ' + layer_value + '\n',
                            first_yaml_content
                        )
            
            # 删除第二个YAML头部
            new_content = '---\n' + first_yaml_content + '\n---' + content[second_yaml.end():]
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True, '已修复重复YAML头部'
        
        # 如果只有一个YAML头部，检查layer字段
        yaml_content = yaml_matches[0].group(1)
        
        if 'layer:' in yaml_content:
            # 检查layer字段格式
            layer_match = re.search(r'^layer:\s*(.+)$', yaml_content, re.MULTILINE)
            
            if layer_match:
                layer_value = layer_match.group(1).strip()
                
                # 去除引号
                if layer_value.startswith('"') and layer_value.endswith('"'):
                    layer_value = layer_value[1:-1]
                elif layer_value.startswith("'") and layer_value.endswith("'"):
                    layer_value = layer_value[1:-1]
                
                # 检查是否是标准格式
                if not re.match(r'^Layer \d+ \(.+\)$', layer_value):
                    # 提取Layer编号并标准化
                    layer_num_match = re.search(r'Layer (\d+)', layer_value)
                    if layer_num_match:
                        layer_num = layer_num_match.group(1)
                        layer_names = {
                            '0': 'Layer 0 (数据源层)',
                            '1': 'Layer 1 (数据层)',
                            '2': 'Layer 2 (Alpha因子层)',
                            '3': 'Layer 3 (策略层)',
                            '4': 'Layer 4 (机器学习层)',
                            '5': 'Layer 5 (执行层)',
                            '6': 'Layer 6 (组合优化层)',
                            '7': 'Layer 7 (风控层)',
                            '8': 'Layer 8 (人机交互层)',
                            '9': 'Layer 9 (治理层)',
                            '10': 'Layer 10 (治理层)',
                            '11': 'Layer 11 (战略决策层)',
                        }
                        standard_layer = layer_names.get(layer_num, f'Layer {layer_num}')
                        
                        # 替换layer字段
                        new_yaml_content = re.sub(
                            r'^layer:\s*.+$',
                            f'layer: {standard_layer}',
                            yaml_content,
                            flags=re.MULTILINE
                        )
                        
                        # 重新构建文档
                        new_content = '---\n' + new_yaml_content + '\n---' + content[yaml_matches[0].end():]
                        
                        # 写回文件
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        return True, f'已标准化layer字段: {standard_layer}'
            
            return False, 'layer字段格式正确，无需修复'
        else:
            return False, '缺少layer字段'
    
    except Exception as e:
        return False, str(e)

def main():
    """主函数"""
    print('=' * 80)
    print('修复YAML头部问题并标准化layer字段')
    print('=' * 80)
    print()
    
    # 扫描所有蓝图文件
    blueprints = []
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('_BLUEPRINT.md'):
                file_path = Path(root) / file
                blueprints.append(str(file_path))
    
    print(f'📊 扫描到 {len(blueprints)} 个蓝图文件')
    print()
    
    # 统计
    stats = {
        'total': len(blueprints),
        'fixed': 0,
        'skipped': 0,
        'errors': 0
    }
    
    # 修复每个文档
    for blueprint in blueprints:
        success, message = fix_yaml_and_layer(blueprint)
        
        if success:
            stats['fixed'] += 1
            print(f'✅ {Path(blueprint).name}: {message}')
        elif message in ['layer字段格式正确，无需修复', '缺少layer字段']:
            stats['skipped'] += 1
        else:
            stats['errors'] += 1
    
    print()
    print('=' * 80)
    print('修复统计')
    print('=' * 80)
    print(f'总文档数: {stats["total"]}')
    print(f'已修复: {stats["fixed"]}')
    print(f'已跳过: {stats["skipped"]}')
    print(f'错误数: {stats["errors"]}')
    
    return stats

if __name__ == '__main__':
    main()
