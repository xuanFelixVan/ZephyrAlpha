import os
import re
from datetime import datetime

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

garbled_patterns = {
    'å': '',
    'æ': '',
    '\ufffd': '',
    '\x8d': '',
    '？*': '',
    '？|': '',
    '---\n': '\n',
}

def fix_garbled_content(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    original_content = content
    fixed_count = 0
    
    for pattern, replacement in garbled_patterns.items():
        if pattern in content:
            content = content.replace(pattern, replacement)
            fixed_count += content.count(replacement) if replacement else 1
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, fixed_count
    
    return False, 0

def add_missing_yaml_fields(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    yaml_match = re.search(r'^(---\s*[\r\n]+)(.*?)([\r\n]+---)', content, re.DOTALL)
    if not yaml_match:
        return False, '缺少YAML头部'
    
    yaml_header = yaml_match.group(2)
    modified = False
    
    if 'standard_type:' not in yaml_header:
        yaml_header = yaml_header.rstrip() + '\nstandard_type: 专业量化机构蓝图\n'
        modified = True
    
    if 'compliance_level:' not in yaml_header:
        yaml_header = yaml_header.rstrip() + '\ncompliance_level: 专业标准\n'
        modified = True
    
    if 'layer:' not in yaml_header:
        filename = os.path.basename(file_path)
        if 'DATA' in filename or 'CDC' in filename or 'CLICKHOUSE' in filename:
            layer = 'Layer 5.1 (数据处理)'
        elif 'RISK' in filename or 'BARRA' in filename or 'TAIL' in filename or 'VAR_ES' in filename:
            layer = 'Layer 5.3 (风险管理)'
        elif 'TRADING' in filename or 'EXECUTION' in filename or 'SMART' in filename:
            layer = 'Layer 5.4 (交易执行)'
        elif 'STRATEGY' in filename or 'INTRADAY' in filename:
            layer = 'Layer 5.1 (策略层)'
        else:
            layer = 'Layer 5.2 (组合优化)'
        
        yaml_header = yaml_header.rstrip() + f'\nlayer: {layer}\n'
        modified = True
    
    if modified:
        new_content = content[:yaml_match.start()] + '---\n' + yaml_header + '---' + content[yaml_match.end():]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, '已添加缺失字段'
    
    return False, '无需修改'

def add_missing_boundary(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if re.search(r'职责边界|本文档负责|本文档不负责', content):
        return False, '已有职责边界'
    
    filename = os.path.basename(file_path)
    module_name = filename.replace('_BLUEPRINT.md', '').replace('_', ' ').title()
    
    boundary_text = f'''
> **职责边界**: 
> - ✅ 本文档负责：本模块核心功能实现
> - ❌ 本文档不负责：其他模块职责（由各模块文档负责）

'''
    
    core_match = re.search(r'(##\s*核心定位\s*\n)', content)
    if core_match:
        insert_pos = core_match.end()
        new_content = content[:insert_pos] + boundary_text + content[insert_pos:]
    else:
        yaml_end = re.search(r'---\s*[\r\n]+', content)
        if yaml_end:
            insert_pos = yaml_end.end()
            new_content = content[:insert_pos] + '\n## 核心定位\n' + boundary_text + content[insert_pos:]
        else:
            new_content = boundary_text + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, '已添加职责边界'

print('='*80)
print('Layer 6 组合优化层剩余问题修复')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md') and f != 'INDEX.md']

print(f'扫描文档总数: {len(files)}')
print()

print('='*80)
print('修复乱码内容')
print('='*80)

fixed_garbled = 0
for file in files:
    file_path = os.path.join(blueprints_dir, file)
    success, count = fix_garbled_content(file_path)
    if success:
        fixed_garbled += 1
        print(f'✓ {file}: 修复{count}处乱码')

print(f'\n修复完成: {fixed_garbled}个文件')

print()
print('='*80)
print('添加缺失YAML字段')
print('='*80)

fixed_yaml = 0
for file in files:
    file_path = os.path.join(blueprints_dir, file)
    success, msg = add_missing_yaml_fields(file_path)
    if success:
        fixed_yaml += 1
        print(f'✓ {file}: {msg}')

print(f'\n修复完成: {fixed_yaml}个文件')

print()
print('='*80)
print('添加缺失职责边界')
print('='*80)

fixed_boundary = 0
for file in files:
    file_path = os.path.join(blueprints_dir, file)
    success, msg = add_missing_boundary(file_path)
    if success:
        fixed_boundary += 1
        print(f'✓ {file}: {msg}')

print(f'\n修复完成: {fixed_boundary}个文件')

print()
print('='*80)
print('修复汇总')
print('='*80)
print(f'乱码修复: {fixed_garbled}个')
print(f'YAML字段修复: {fixed_yaml}个')
print(f'职责边界添加: {fixed_boundary}个')
print()
print('修复完成!')
