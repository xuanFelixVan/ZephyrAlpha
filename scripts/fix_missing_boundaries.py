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
    'ALGORITHMIC_TRADING_OPTIMIZER_BLUEPRINT.md',
    'AUTO_REPAIR_ENGINE_BLUEPRINT.md',
    'CLICKHOUSE_INTEGRATION_BLUEPRINT.md',
    'COINTEGRATION_ANALYSIS_BLUEPRINT.md',
    'DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md',
    'DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md',
    'DATA_MESH_BLUEPRINT.md',
    'DATA_OBSERVABILITY_BLUEPRINT.md',
    'DATA_FABRIC_BLUEPRINT.md',
    'DATA_COST_MANAGEMENT_BLUEPRINT.md',
    'DATA_CATALOG_BLUEPRINT.md',
    'DATA_CATALOG_METADATA_BLUEPRINT.md',
    'BARRA_RISK_MODEL_BLUEPRINT.md',
    'BLACK_LITTERMAN_MODEL_BLUEPRINT.md',
    'CONSTRAINT_SOLVER_BLUEPRINT.md',
]

module_info = {
    'ALGORITHMIC_TRADING_OPTIMIZER': ('算法交易优化', '执行算法选择', '交易路径优化'),
    'AUTO_REPAIR_ENGINE': ('自动修复引擎', '异常检测', '自动修复'),
    'CLICKHOUSE_INTEGRATION': ('ClickHouse集成', '列式存储', '高性能查询'),
    'COINTEGRATION_ANALYSIS': ('协整分析', '统计套利', '配对交易'),
    'DATA_GOVERNANCE_PLATFORM': ('数据治理平台', '数据标准', '数据质量'),
    'DATA_LIFECYCLE_MANAGEMENT': ('数据生命周期管理', '数据保留', '数据归档'),
    'DATA_MESH': ('数据网格', '域数据所有权', '数据产品'),
    'DATA_OBSERVABILITY': ('数据可观测性', '数据监控', '数据血缘'),
    'DATA_FABRIC': ('数据编织', '数据虚拟化', '统一数据层'),
    'DATA_COST_MANAGEMENT': ('数据成本管理', '成本监控', '成本优化'),
    'DATA_CATALOG': ('数据目录', '元数据管理', '数据发现'),
    'DATA_CATALOG_METADATA': ('数据目录元数据', '元数据采集', '元数据存储'),
    'BARRA_RISK_MODEL': ('Barra风险模型', '因子风险建模', '风险归因'),
    'BLACK_LITTERMAN_MODEL': ('Black-Litterman模型', '观点融合', '市场均衡收益'),
    'CONSTRAINT_SOLVER': ('约束求解器', '约束建模', '求解算法'),
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
