import os
import re
from datetime import datetime

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

def fix_double_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    content = content.replace('\ufeff', '')
    
    yaml_pattern = r'---\s*[\r\n]+(.*?)[\r\n]+---'
    yaml_matches = list(re.finditer(yaml_pattern, content, re.DOTALL))
    
    if len(yaml_matches) < 2:
        return False, '无双YAML头部'
    
    second_yaml = yaml_matches[1]
    second_yaml_content = second_yaml.group(1)
    
    new_content = '---\n' + second_yaml_content.strip() + '\n---\n' + content[second_yaml.end():]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, '已修复双YAML头部'

print('='*80)
print('修复双YAML头部')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md') and f != 'INDEX.md']

fixed_count = 0
for file in files:
    file_path = os.path.join(blueprints_dir, file)
    success, msg = fix_double_yaml(file_path)
    if success:
        fixed_count += 1
        print(f'✓ {file}: {msg}')

print(f'\n修复完成: {fixed_count}个文件')
