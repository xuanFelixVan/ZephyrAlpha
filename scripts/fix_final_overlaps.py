import os
import re
from datetime import datetime

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

overlap_fixes = {
    'STATISTICAL_ARBITRAGE_MODULE_BLUEPRINT.md': {
        'old': '- 配对交易',
        'new': '- 统计套利配对交易'
    },
    'COINTEGRATION_ANALYSIS_BLUEPRINT.md': {
        'old': '- 配对交易',
        'new': '- 协整分析配对交易'
    },
}

def fix_overlap(file_path, old_resp, new_resp):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if old_resp in content:
        content = content.replace(old_resp, new_resp)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, f'已修复: {old_resp} -> {new_resp}'
    
    return False, '未找到重叠职责'

print('='*80)
print('修复职责重叠问题')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

fixed_count = 0
for filename, fixes in overlap_fixes.items():
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        success, msg = fix_overlap(file_path, fixes['old'], fixes['new'])
        if success:
            fixed_count += 1
            print(f'✓ {filename}: {msg}')
        else:
            print(f'- {filename}: {msg}')
    else:
        print(f'- {filename}: 文件不存在')

print(f'\n修复完成: {fixed_count}个文件')
