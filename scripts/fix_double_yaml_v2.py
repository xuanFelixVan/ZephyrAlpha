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

def fix_double_yaml(file_path, correct_layer='Layer 6 (组合优化层)'):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    yaml_blocks = re.findall(r'^---\s*[\r\n]+(.*?)^---\s*[\r\n]+', content, re.MULTILINE | re.DOTALL)
    
    if len(yaml_blocks) >= 2:
        first_yaml_end = re.search(r'^---\s*[\r\n]+.*?^---\s*[\r\n]+', content, re.MULTILINE | re.DOTALL)
        if first_yaml_end:
            content = content[first_yaml_end.end():]
            
            yaml_match = re.search(r'^---\s*[\r\n]+(.*?)^---\s*[\r\n]+', content, re.MULTILINE | re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                yaml_content = re.sub(r'layer:\s*.*?[\r\n]+', f'layer: {correct_layer}\n', yaml_content)
                
                if 'standard_type:' not in yaml_content:
                    yaml_content += f'standard_type: 专业量化机构蓝图\n'
                if 'compliance_level:' not in yaml_content:
                    yaml_content += f'compliance_level: 专业标准\n'
                
                content = '---\n' + yaml_content + '---\n\n' + content[yaml_match.end():]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return True, '删除第一个YAML头部，修复layer字段'
    
    return False, '无需修复或修复失败'

files_to_fix = [
    'ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md',
    'STRATEGY_SELECTION_BLUEPRINT.md'
]

print('='*80)
print('修复双YAML头部问题')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

fixed_count = 0
for filename in files_to_fix:
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        success, msg = fix_double_yaml(file_path)
        if success:
            fixed_count += 1
            print(f'✓ {filename}: {msg}')
        else:
            print(f'- {filename}: {msg}')

print()
print('='*80)
print(f'修复完成: {fixed_count}个文件')
