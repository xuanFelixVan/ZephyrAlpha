#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析和修复缺少Layer归属的文档 - 增强版
"""

import re
import os
from pathlib import Path

def analyze_yaml_issues(file_path):
    """分析YAML头部问题"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 删除BOM字符
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # 查找YAML头部
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        yaml_match = re.search(yaml_pattern, content, re.DOTALL)
        
        if not yaml_match:
            # 尝试查找可能的YAML内容（没有---包围）
            # 查找以module_id开头的内容
            module_id_match = re.search(r'^module_id:', content, re.MULTILINE)
            if module_id_match:
                # 找到module_id，但没有---包围
                return 'missing_delimiters', 'YAML头部缺少---包围'
            else:
                return 'no_yaml', '未找到YAML头部'
        
        yaml_content = yaml_match.group(1)
        
        # 查找layer字段
        layer_match = re.search(r'^layer:\s*.+$', yaml_content, re.MULTILINE)
        
        if not layer_match:
            return 'missing_layer', '缺少layer字段'
        
        return 'ok', 'YAML头部正常'
    
    except Exception as e:
        return 'error', str(e)

def main():
    """主函数"""
    print('=' * 80)
    print('分析缺少Layer归属的文档')
    print('=' * 80)
    print()
    
    # 扫描所有蓝图文件
    blueprints = []
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('_BLUEPRINT.md'):
                file_path = Path(root) / file
                blueprints.append(str(file_path))
    
    print(f'扫描到 {len(blueprints)} 个蓝图文件')
    print()
    
    # 统计
    stats = {
        'total': len(blueprints),
        'ok': 0,
        'missing_layer': 0,
        'missing_delimiters': 0,
        'no_yaml': 0,
        'error': 0
    }
    
    missing_layer_list = []
    missing_delimiters_list = []
    no_yaml_list = []
    error_list = []
    
    # 分析每个文档
    for blueprint in blueprints:
        issue_type, message = analyze_yaml_issues(blueprint)
        
        if issue_type == 'ok':
            stats['ok'] += 1
        elif issue_type == 'missing_layer':
            stats['missing_layer'] += 1
            missing_layer_list.append(blueprint)
        elif issue_type == 'missing_delimiters':
            stats['missing_delimiters'] += 1
            missing_delimiters_list.append(blueprint)
        elif issue_type == 'no_yaml':
            stats['no_yaml'] += 1
            no_yaml_list.append(blueprint)
        else:
            stats['error'] += 1
            error_list.append((blueprint, message))
    
    # 输出结果
    print('分析统计:')
    print(f'  YAML头部正常: {stats["ok"]}个')
    print(f'  缺少layer字段: {stats["missing_layer"]}个')
    print(f'  缺少---包围: {stats["missing_delimiters"]}个')
    print(f'  未找到YAML头部: {stats["no_yaml"]}个')
    print(f'  错误: {stats["error"]}个')
    print()
    
    if missing_layer_list:
        print(f'缺少layer字段的文档 ({len(missing_layer_list)}个):')
        for doc in missing_layer_list[:5]:
            print(f'  - {doc}')
        if len(missing_layer_list) > 5:
            print(f'  ... 还有 {len(missing_layer_list)-5} 个文档')
        print()
    
    if missing_delimiters_list:
        print(f'缺少---包围的文档 ({len(missing_delimiters_list)}个):')
        for doc in missing_delimiters_list[:5]:
            print(f'  - {doc}')
        if len(missing_delimiters_list) > 5:
            print(f'  ... 还有 {len(missing_delimiters_list)-5} 个文档')
        print()
    
    if no_yaml_list:
        print(f'未找到YAML头部的文档 ({len(no_yaml_list)}个):')
        for doc in no_yaml_list[:5]:
            print(f'  - {doc}')
        if len(no_yaml_list) > 5:
            print(f'  ... 还有 {len(no_yaml_list)-5} 个文档')
        print()
    
    if error_list:
        print(f'错误的文档 ({len(error_list)}个):')
        for doc, msg in error_list[:5]:
            print(f'  - {doc}: {msg}')
        if len(error_list) > 5:
            print(f'  ... 还有 {len(error_list)-5} 个文档')
    
    return stats

if __name__ == '__main__':
    main()
