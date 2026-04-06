#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除重复的layer字段
"""

import re
import os
from pathlib import Path

def remove_duplicate_layer(file_path):
    """删除重复的layer字段"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找YAML头部
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        yaml_match = re.search(yaml_pattern, content, re.DOTALL)
        
        if not yaml_match:
            return False, '未找到YAML头部'
        
        yaml_content = yaml_match.group(1)
        
        # 查找所有layer字段
        layer_matches = list(re.finditer(r'^layer:\s*.+$', yaml_content, re.MULTILINE))
        
        if len(layer_matches) <= 1:
            return False, '无需修复'
        
        # 删除第二个及以后的layer字段
        for i in range(1, len(layer_matches)):
            yaml_content = yaml_content.replace(layer_matches[i].group(0) + '\n', '')
        
        # 重新构建文档
        new_content = '---\n' + yaml_content + '\n---' + content[yaml_match.end():]
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f'已删除{len(layer_matches)-1}个重复layer字段'
    
    except Exception as e:
        return False, str(e)

def main():
    """主函数"""
    print('=' * 80)
    print('删除重复的layer字段')
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
        success, message = remove_duplicate_layer(blueprint)
        
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
