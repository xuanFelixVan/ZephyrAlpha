# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re
from datetime import datetime

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

fixes = {
    'ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md': {
        'remove_first_yaml': True,
        'fix_layer': 'Layer 6 (组合优化层)',
        'ensure_fields': {
            'standard_type': '专业量化机构蓝图',
            'compliance_level': '专业标准',
        }
    },
    'STRATEGY_SELECTION_BLUEPRINT.md': {
        'remove_first_yaml': True,
        'fix_layer': 'Layer 6 (组合优化层)',
        'ensure_fields': {
            'standard_type': '专业量化机构蓝图',
            'compliance_level': '专业标准',
        }
    }
}

def fix_double_yaml_and_fields(file_path, config):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    original_content = content
    
    if config.get('remove_first_yaml'):
        yaml_pattern = r'^---\s*\n.*?^---\s*\n'
        matches = list(re.finditer(yaml_pattern, content, re.MULTILINE | re.DOTALL))
        
        if len(matches) >= 2:
            first_yaml = matches[0]
            content = content[first_yaml.end():]
            print(f'  - 删除第一个YAML头部')
    
    yaml_match = re.search(r'^---\s*\n(.*?)^---\s*\n', content, re.MULTILINE | re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        
        if config.get('fix_layer'):
            yaml_content = re.sub(
                r'layer:\s*.*?\n',
                f'layer: {config["fix_layer"]}\n',
                yaml_content
            )
            print(f'  - 修复layer: {config["fix_layer"]}')
        
        if config.get('ensure_fields'):
            for field, value in config['ensure_fields'].items():
                if field not in yaml_content:
                    yaml_content += f'{field}: {value}\n'
                    print(f'  - 添加字段: {field}: {value}')
        
        content = '---\n' + yaml_content + '---\n\n' + content[yaml_match.end():]
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

print('='*80)
print('修复Layer 6文档问题')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

fixed_count = 0
for filename, config in fixes.items():
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        print(f'修复: {filename}')
        if fix_double_yaml_and_fields(file_path, config):
            fixed_count += 1
            print(f'  ✓ 修复成功')
        else:
            print(f'  - 无需修复')
    print()

print('='*80)
print(f'修复完成: {fixed_count}个文件')
