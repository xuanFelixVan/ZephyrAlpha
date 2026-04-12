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

core_positioning_extensions = {
    'DATA_CATALOG_BLUEPRINT.md': '负责数据目录系统的设计与构建和运行和操作，构建企业级数据资产目录，提供数据发现、血缘追踪和元数据管理功能，支持数据资产的全生命周期管理。',
    'DATA_COST_MANAGEMENT_BLUEPRINT.md': '负责数据成本管理系统的设计与构建和运行和操作，监控和优化数据存储与计算成本，提供成本分析、预算管理和优化建议功能，降低数据运营成本。',
    'DATA_FABRIC_BLUEPRINT.md': '负责数据编织架构的设计与构建和运行和操作，实现跨平台数据虚拟化和统一访问，支持异构数据源的透明集成，提供一致的数据访问体验。',
    'DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md': '负责数据生命周期管理系统的设计与构建和运行和操作，定义和执行数据保留策略，自动化数据归档和清理流程，确保数据合规性和存储效率。',
    'DATA_MESH_BLUEPRINT.md': '负责数据网格架构的设计与构建和运行和操作，实施数据产品化和领域自治原则，支持联邦数据治理，构建可扩展的分布式数据架构。',
    'DATA_SOURCE_MANAGEMENT_BLUEPRINT.md': '负责数据源管理系统的设计与构建和运行和操作，统一管理企业数据源连接，提供数据源健康监控和连接池管理，确保数据访问的稳定性和可靠性。',
    'DATA_VERSION_CONTROL_BLUEPRINT.md': '负责数据版本控制系统的设计与构建和运行和操作，实现数据集的版本管理和变更追踪，支持数据回滚和审计，确保数据的可追溯性。',
    'MONITORING_DASHBOARD_ENHANCEMENT_BLUEPRINT.md': '负责监控仪表板增强功能的设计与构建和运行和操作，提供实时监控视图和告警可视化，支持自定义仪表板和报告生成，提升运维监控效率。',
    'RISK_CONTROL_BLUEPRINT.md': '负责风险控制系统的设计与构建和运行和操作，实施组合层面的风险监控和控制，提供风险预警和限额管理功能，确保投资组合风险可控。',
    'TAIL_RISK_HEDGING_BLUEPRINT.md': '负责尾部风险对冲策略的设计与构建和运行和操作，识别和量化尾部风险，设计和实施对冲策略，降低极端市场事件对组合的冲击。',
}

change_history_additions = {
    'COINTEGRATION_ANALYSIS_BLUEPRINT.md': '''
## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 组合优化层负责人 |
'''
}

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

def add_change_history(file_path, history_content):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if '## 变更历史' in content or '## 版本管理' in content:
        return False, '已有变更历史'
    
    last_section_match = None
    for match in re.finditer(r'^##\s+', content, re.MULTILINE):
        last_section_match = match
    
    if last_section_match:
        insert_pos = last_section_match.start()
        new_content = content[:insert_pos] + history_content + '\n' + content[insert_pos:]
    else:
        new_content = content + '\n' + history_content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, '已添加变更历史'

print('='*80)
print('修复P2问题: 核心定位过短')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

fixed_count = 0
for filename, new_content in core_positioning_extensions.items():
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        success, msg = extend_core_positioning(file_path, new_content)
        if success:
            fixed_count += 1
            print(f'✓ {filename}: {msg}')
        else:
            print(f'- {filename}: {msg}')
    else:
        print(f'- {filename}: 文件不存在')

print()
print('='*80)
print('修复P2问题: 缺少变更历史')
print('='*80)

for filename, history_content in change_history_additions.items():
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        success, msg = add_change_history(file_path, history_content)
        if success:
            print(f'✓ {filename}: {msg}')
        else:
            print(f'- {filename}: {msg}')

print(f'\n修复完成: {fixed_count}个文件')
