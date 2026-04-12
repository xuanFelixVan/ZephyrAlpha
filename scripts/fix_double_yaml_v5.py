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

def fix_double_yaml_v5(file_path, correct_layer='Layer 6 (组合优化层)'):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    content = content.lstrip('\ufeff')
    
    yaml_delimiters = []
    for match in re.finditer(r'^---', content, re.MULTILINE):
        yaml_delimiters.append(match.start())
    
    print(f'  检测到{len(yaml_delimiters)}个YAML分隔符')
    
    if len(yaml_delimiters) >= 3:
        second_yaml_start = yaml_delimiters[2]
        
        new_content = content[second_yaml_start:]
        
        yaml_match = re.search(r'^---[\r\n]+(.*?)^---[\r\n]+', new_content, re.MULTILINE | re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            
            yaml_content = re.sub(r'layer:\s*.*?[\r\n]+', f'layer: {correct_layer}\n', yaml_content)
            
            if 'standard_type:' not in yaml_content:
                yaml_content += 'standard_type: 专业量化机构蓝图\n'
            if 'compliance_level:' not in yaml_content:
                yaml_content += 'compliance_level: 专业标准\n'
            
            new_content = '---\n' + yaml_content + '---\n\n' + new_content[yaml_match.end():]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True, f'删除前{second_yaml_start}字符，保留第二个YAML头部'
        else:
            return False, '无法匹配第二个YAML块'
    
    return False, f'检测到{len(yaml_delimiters)}个YAML分隔符，无需修复'

files_to_fix = [
    'ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md',
    'STRATEGY_SELECTION_BLUEPRINT.md'
]

print('='*80)
print('修复双YAML头部问题 v5')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

fixed_count = 0
for filename in files_to_fix:
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        print(f'处理: {filename}')
        success, msg = fix_double_yaml_v5(file_path)
        if success:
            fixed_count += 1
            print(f'  ✓ {msg}')
        else:
            print(f'  - {msg}')

print()
print('='*80)
print(f'修复完成: {fixed_count}个文件')
