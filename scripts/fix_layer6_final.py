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
    'DATA_SOURCE_HEALTH_MONITOR_BLUEPRINT.md',
    'DATA_VALIDATION_ENGINE_BLUEPRINT.md',
]

module_info = {
    'DATA_BACKUP_RECOVERY': ('数据备份恢复', '备份策略制定', '恢复机制实施'),
    'DATA_CLEANING_ENGINE': ('数据清洗引擎', '数据质量检测', '异常值处理'),
    'DATA_MASKING_ENCRYPTION': ('数据脱敏加密', '敏感数据识别', '脱敏规则执行'),
    'DATA_SOURCE_HEALTH_MONITOR': ('数据源健康监控', '健康检查', '故障检测'),
    'DATA_VALIDATION_ENGINE': ('数据验证引擎', '验证规则', '数据校验'),
}

core_positioning_extensions = {
    'DATA_CLEANING_ENGINE_BLUEPRINT.md': '负责数据清洗引擎的设计与构建和运行和操作，实现数据质量检测、异常值识别与处理、数据标准化转换，确保数据质量符合业务要求。',
    'DATA_MASKING_ENCRYPTION_BLUEPRINT.md': '负责数据脱敏加密系统的设计与构建和运行和操作，实现敏感数据识别、脱敏规则执行、加密存储，确保数据安全合规。',
    'DATA_SOURCE_HEALTH_MONITOR_BLUEPRINT.md': '负责数据源健康监控系统的设计与构建和运行和操作，实现数据源健康检查、故障检测与告警、自动切换机制，确保数据源稳定可靠。',
    'DATA_SUBSCRIPTION_SERVICE_BLUEPRINT.md': '负责数据订阅服务的设计与构建和运行和操作，实现数据推送、订阅管理、消息队列集成，支持实时和批量数据订阅。',
    'DATA_VALIDATION_ENGINE_BLUEPRINT.md': '负责数据验证引擎的设计与构建和运行和操作，实现数据校验规则配置、验证执行、异常报告生成，确保数据准确性和完整性。',
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

def extend_core_positioning(file_path, new_content_text):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    core_match = re.search(r'(##\s*核心定位\s*\n)(.+?)(?=\n##|\n#|$)', content, re.DOTALL)
    if core_match:
        existing_text = core_match.group(2).strip()
        if len(existing_text) < 100:
            new_content_block = f'\n{new_content_text}\n\n'
            new_content_full = content[:core_match.end(1)] + new_content_block + content[core_match.end():]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content_full)
            
            return True, '已扩展核心定位内容'
    
    return False, '核心定位已足够长或未找到'

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
print('[阶段2] 扩展核心定位')
for filename, new_content in core_positioning_extensions.items():
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        success, msg = extend_core_positioning(file_path, new_content)
        if success:
            fixed_count += 1
            print(f'✓ {filename}: {msg}')
        else:
            print(f'- {filename}: {msg}')

print()
print('='*80)
print(f'修复完成: {fixed_count}个文件')
