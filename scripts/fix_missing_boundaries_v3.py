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

files_to_fix = [
    'EXECUTION_STRATEGY_BACKTESTER_BLUEPRINT.md',
    'LIQUIDITY_MANAGEMENT_SYSTEM_BLUEPRINT.md',
    'REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md',
    'SMART_EXECUTION_ENGINE_BLUEPRINT.md',
]

module_info = {
    'EXECUTION_STRATEGY_BACKTESTER': ('执行策略回测', '策略模拟', '成本分析'),
    'LIQUIDITY_MANAGEMENT_SYSTEM': ('流动性管理系统', '流动性监控', '现金管理'),
    'REALTIME_RISK_HEDGE_ENGINE': ('实时风险对冲引擎', '动态对冲', '风险监控'),
    'SMART_EXECUTION_ENGINE': ('智能执行引擎', '执行算法', '成本优化'),
}

def add_boundary(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if re.search(r'>\s*\*\*职责边界\*\*', content):
        return False, '已有职责边界'
    
    filename = os.path.basename(file_path)
    module_name = filename.replace('_BLUEPRINT.md', '')
    
    if module_name in module_info:
        resp1, resp2, resp3 = module_info[module_name]
    else:
        resp1, resp2, resp3 = '本模块核心功能', '模块实现', '质量保证'
    
    boundary_text = f'''
> **职责边界**: 
> - ✅ 本文档负责：{resp1}、{resp2}、{resp3}
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
print('添加缺失职责边界')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

fixed_count = 0
for file in files_to_fix:
    file_path = os.path.join(blueprints_dir, file)
    if os.path.exists(file_path):
        success, msg = add_boundary(file_path)
        if success:
            fixed_count += 1
            print(f'✓ {file}: {msg}')
        else:
            print(f'- {file}: {msg}')
    else:
        print(f'✗ {file}: 文件不存在')

print(f'\n修复完成: {fixed_count}个文件')
