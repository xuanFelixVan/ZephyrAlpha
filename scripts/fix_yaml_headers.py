import os
import re
from datetime import datetime

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

def fix_yaml_header(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if content.startswith('---'):
        return False, '已有YAML分隔符'
    
    yaml_fields = ['responsibility:', 'module_id:', 'version:', 'status:', 'created_date:', 'layer:']
    
    first_field_pos = -1
    for field in yaml_fields:
        pos = content.find(field)
        if pos != -1 and (first_field_pos == -1 or pos < first_field_pos):
            first_field_pos = pos
    
    if first_field_pos == -1:
        return False, '未找到YAML字段'
    
    yaml_end_pattern = r'\n\n##|\n\n#|\n\n\*\*|\n\n>'
    yaml_end_match = re.search(yaml_end_pattern, content[first_field_pos:])
    
    if yaml_end_match:
        yaml_content = content[first_field_pos:first_field_pos + yaml_end_match.start()]
        rest_content = content[first_field_pos + yaml_end_match.start():]
    else:
        yaml_content = content[first_field_pos:]
        rest_content = ''
    
    new_content = '---\n' + yaml_content.strip() + '\n---\n' + rest_content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, '已修复YAML头部'

print('='*80)
print('修复YAML头部')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md') and f != 'INDEX.md']

fixed_count = 0
for file in files:
    file_path = os.path.join(blueprints_dir, file)
    success, msg = fix_yaml_header(file_path)
    if success:
        fixed_count += 1
        print(f'✓ {file}: {msg}')

print(f'\n修复完成: {fixed_count}个文件')
