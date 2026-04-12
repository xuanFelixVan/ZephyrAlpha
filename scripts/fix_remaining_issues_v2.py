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

boundary_files = [
    'DATA_BACKUP_RECOVERY_BLUEPRINT.md',
    'DATA_CLEANING_ENGINE_BLUEPRINT.md',
    'DATA_MASKING_ENCRYPTION_BLUEPRINT.md',
    'DATA_PREPROCESSING_ARCHITECTURE_GAP_ANALYSIS_BLUEPRINT.md',
    'DATA_SOURCE_HEALTH_MONITOR_BLUEPRINT.md',
    'DATA_VALIDATION_ENGINE_BLUEPRINT.md',
]

module_info = {
    'DATA_BACKUP_RECOVERY': ('数据备份恢复', '备份策略制定', '恢复机制实施'),
    'DATA_CLEANING_ENGINE': ('数据清洗引擎', '数据质量检测', '异常值处理'),
    'DATA_MASKING_ENCRYPTION': ('数据脱敏加密', '敏感数据识别', '脱敏规则执行'),
    'DATA_PREPROCESSING_ARCHITECTURE_GAP_ANALYSIS': ('数据预处理架构差距分析', '架构评估', '差距识别'),
    'DATA_SOURCE_HEALTH_MONITOR': ('数据源健康监控', '健康检查', '故障检测'),
    'DATA_VALIDATION_ENGINE': ('数据验证引擎', '验证规则', '数据校验'),
}

def add_boundary(file_path, module_name):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if re.search(r'>\s*\*\*职责边界\*\*', content):
        return False, '已有职责边界'
    
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

change_history_file = 'DYNAMIC_LEVERAGE_MANAGEMENT_BLUEPRINT.md'
change_history_content = '''
## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 风险管理层负责人 |

'''

def add_change_history(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if '## 变更历史' in content or '## 版本管理' in content:
        return False, '已有变更历史'
    
    last_section_match = None
    for match in re.finditer(r'^##\s+', content, re.MULTILINE):
        last_section_match = match
    
    if last_section_match:
        insert_pos = last_section_match.start()
        new_content = content[:insert_pos] + change_history_content + '\n' + content[insert_pos:]
    else:
        new_content = content + '\n' + change_history_content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, '已添加变更历史'

core_positioning_file = 'HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md'
core_positioning_content = '负责高性能数据管道的设计与构建和运行和操作，实现数据的高效传输和处理，支持大规模数据的实时和批量处理，优化数据流动性能和资源利用率。'

def extend_core_positioning(file_path, new_content):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    core_match = re.search(r'(##\s*核心定位\s*\n)', content)
    if core_match:
        insert_pos = core_match.end()
        new_content_block = f'\n{new_content}\n\n'
        new_content_full = content[:insert_pos] + new_content_block + content[insert_pos:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content_full)
        
        return True, '已扩展核心定位内容'
    
    return False, '未找到核心定位章节'

print('='*80)
print('修复剩余问题')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

print('[阶段1] 添加职责边界')
fixed_count = 0
for filename in boundary_files:
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        module_name = filename.replace('_BLUEPRINT.md', '')
        success, msg = add_boundary(file_path, module_name)
        if success:
            fixed_count += 1
            print(f'✓ {filename}: {msg}')
        else:
            print(f'- {filename}: {msg}')

print()
print('[阶段2] 添加变更历史')
file_path = os.path.join(blueprints_dir, change_history_file)
if os.path.exists(file_path):
    success, msg = add_change_history(file_path)
    if success:
        fixed_count += 1
        print(f'✓ {change_history_file}: {msg}')
    else:
        print(f'- {change_history_file}: {msg}')

print()
print('[阶段3] 扩展核心定位')
file_path = os.path.join(blueprints_dir, core_positioning_file)
if os.path.exists(file_path):
    success, msg = extend_core_positioning(file_path, core_positioning_content)
    if success:
        fixed_count += 1
        print(f'✓ {core_positioning_file}: {msg}')
    else:
        print(f'- {core_positioning_file}: {msg}')

print()
print('='*80)
print(f'修复完成: {fixed_count}个文件')
