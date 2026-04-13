#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
检查缺少layer字段的文档
"""

import re
import os
from pathlib import Path

def check_yaml(file_path):
    """检查YAML头部"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找YAML头部
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        yaml_match = re.search(yaml_pattern, content, re.DOTALL)
        
        if not yaml_match:
            return False, '未找到YAML头部'
        
        yaml_content = yaml_match.group(1)
        
        # 查找layer字段
        layer_match = re.search(r'^layer:\s*.+$', yaml_content, re.MULTILINE)
        
        if not layer_match:
            return False, '缺少layer字段'
        
        return True, '有layer字段'
    
    except Exception as e:
        return False, str(e)

def main():
    """主函数"""
    print('=' * 80)
    print('检查缺少layer字段的文档')
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
        'with_layer': 0,
        'missing_layer': 0,
        'errors': 0
    }
    
    missing_list = []
    
    # 检查每个文档
    for blueprint in blueprints:
        success, message = check_yaml(blueprint)
        
        if success:
            stats['with_layer'] += 1
        elif message == '缺少layer字段':
            stats['missing_layer'] += 1
            missing_list.append(blueprint)
        else:
            stats['errors'] += 1
            print(f'错误 {Path(blueprint).name}: {message}')
    
    print()
    print('=' * 80)
    print('检查统计')
    print('=' * 80)
    print(f'总文档数: {stats["total"]}')
    print(f'有layer字段: {stats["with_layer"]}')
    print(f'缺少layer字段: {stats["missing_layer"]}')
    print(f'错误数: {stats["errors"]}')
    
    if missing_list:
        print()
        print('缺少layer字段的文档:')
        for doc in missing_list[:10]:  # 只显示前10个
            print(f'  - {doc}')
        if len(missing_list) > 10:
            print(f'  ... 还有 {len(missing_list)-10} 个文档')
    
    return stats

if __name__ == '__main__':
    main()
