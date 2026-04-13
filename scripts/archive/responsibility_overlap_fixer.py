#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
职责重叠问题修复脚本
区分INDEX.md、OVERVIEW.md和README.md的职责
"""

import re
import yaml
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

# 定义不同文档类型的标准职责
DOCUMENT_RESPONSIBILITIES = {
    'INDEX.md': {
        'template': [
            '目录导航',
            '模块索引',
            '职责协调'
        ],
        'description': '目录导航、模块索引、职责协调'
    },
    'OVERVIEW.md': {
        'template': [
            '模块概览',
            '核心概念',
            '关键流程'
        ],
        'description': '模块概览、核心概念、关键流程'
    },
    'README.md': {
        'template': [
            '模块说明',
            '使用指南',
            '快速开始'
        ],
        'description': '模块说明、使用指南、快速开始'
    }
}

def parse_yaml_safe(content):
    """安全解析YAML头部"""
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        body_content = content[yaml_match.end():]
        
        try:
            yaml_dict = yaml.safe_load(yaml_content)
            return yaml_dict if yaml_dict else {}, body_content
        except:
            return {}, body_content
    
    return {}, content

def update_yaml_responsibility(content, doc_type):
    """更新YAML头部的responsibility字段"""
    yaml_dict, body = parse_yaml_safe(content)
    
    if not yaml_dict:
        return content
    
    # 更新responsibility字段
    yaml_dict['responsibility'] = DOCUMENT_RESPONSIBILITIES[doc_type]['template']
    
    # 重新构建YAML头部
    yaml_header = '---\n'
    for key, value in yaml_dict.items():
        if isinstance(value, list):
            yaml_header += f'{key}:\n'
            for item in value:
                yaml_header += f'  - {item}\n'
        elif isinstance(value, str):
            yaml_header += f'{key}: {value}\n'
        else:
            yaml_header += f'{key}: {value}\n'
    yaml_header += '---\n'
    
    return yaml_header + body

def fix_responsibility_overlap():
    """修复职责重叠问题"""
    print("\n修复职责重叠问题...")
    
    fixed_count = 0
    
    # 遍历所有.md文件
    for md_file in FACTOR_LIBRARY.rglob('*.md'):
        file_name = md_file.name
        
        # 只处理INDEX.md、OVERVIEW.md和README.md
        if file_name in ['INDEX.md', 'OVERVIEW.md', 'README.md']:
            rel_path = md_file.relative_to(FACTOR_LIBRARY)
            
            # 读取文件内容
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 更新职责
            new_content = update_yaml_responsibility(content, file_name)
            
            # 如果内容有变化，写回文件
            if new_content != content:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"修复: {rel_path} - 更新职责为{DOCUMENT_RESPONSIBILITIES[file_name]['description']}")
                fixed_count += 1
    
    return fixed_count

def main():
    """主函数"""
    print("=" * 80)
    print("职责重叠问题修复")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    fixed_count = fix_responsibility_overlap()
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"修复文件数: {fixed_count}")
    print("\n说明:")
    print("- INDEX.md: 负责目录导航、模块索引、职责协调")
    print("- OVERVIEW.md: 负责模块概览、核心概念、关键流程")
    print("- README.md: 负责模块说明、使用指南、快速开始")

if __name__ == '__main__':
    main()
