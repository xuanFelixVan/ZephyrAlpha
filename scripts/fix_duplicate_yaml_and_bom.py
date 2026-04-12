#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复重复YAML头部和BOM字符问题
"""

import re
import os
from pathlib import Path

def fix_duplicate_yaml_and_bom(file_path):
    """修复重复YAML头部和BOM字符问题"""
    try:
        # 尝试多种编码读取
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except:
                continue
        
        if content is None:
            return False, '无法读取文件'
        
        # 删除BOM字符
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # 查找所有YAML头部
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        yaml_matches = list(re.finditer(yaml_pattern, content, re.DOTALL))
        
        if not yaml_matches:
            return False, '未找到YAML头部'
        
        # 如果有多个YAML头部，只保留第二个（通常第二个更完整）
        if len(yaml_matches) > 1:
            second_yaml = yaml_matches[1]
            second_yaml_content = second_yaml.group(1)
            
            # 检查第二个YAML是否有layer字段
            if 'layer:' in second_yaml_content:
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
                        
                        # 替换layer字段
                        second_yaml_content = re.sub(
                            r'^layer:\s*.+$',
                            f'layer: {layer_value}',
                            second_yaml_content,
                            flags=re.MULTILINE
                        )
            
            # 删除第一个YAML头部
            new_content = '---\n' + second_yaml_content + '\n---' + content[second_yaml.end():]
            
            # 写回文件（使用UTF-8无BOM）
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True, '已修复重复YAML头部和BOM字符'
        
        # 如果只有一个YAML头部，检查是否有BOM字符
        if content.startswith('\ufeff'):
            # 写回文件（使用UTF-8无BOM）
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, '已删除BOM字符'
        
        return False, '无需修复'
    
    except Exception as e:
        return False, str(e)

def main():
    """主函数"""
    print('=' * 80)
    print('修复重复YAML头部和BOM字符问题')
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
        success, message = fix_duplicate_yaml_and_bom(blueprint)
        
        if success:
            stats['fixed'] += 1
            print(f'✅ {Path(blueprint).name}: {message}')
        elif message == '无需修复':
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
