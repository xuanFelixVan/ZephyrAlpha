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

overlap_fixes = {
    'DATA_GOVERNANCE_BLUEPRINT.md': {
        'old': '数据管理架构设计与实施规范与优化维护',
        'new': '数据治理架构与规范制定'
    },
    'DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md': {
        'old': '数据管理架构设计与实施规范与优化维护',
        'new': '数据生命周期管理与优化'
    },
    'DATA_QUALITY_MONITORING_BLUEPRINT.md': {
        'old': '数据管理架构设计与实施规范与优化维护',
        'new': '数据质量监控与改进'
    },
    'DATA_STANDARDIZATION_ENGINE_BLUEPRINT.md': {
        'old': '数据管理架构设计与实施规范与优化维护',
        'new': '数据标准化引擎实施'
    },
    'DATA_VALIDATION_ENGINE_BLUEPRINT.md': {
        'old': '数据管理架构设计与实施规范与优化维护',
        'new': '数据验证引擎实施'
    },
    'DATA_OBSERVABILITY_BLUEPRINT.md': {
        'old': '数据管理架构设计与实施规范与优化维护',
        'new': '数据可观测性实施'
    },
    'COINTEGRATION_ANALYSIS_BLUEPRINT.md': {
        'old': '协整分析',
        'new': '协整关系识别与分析'
    },
    'STATISTICAL_ARBITRAGE_BLUEPRINT.md': {
        'old': '协整分析',
        'new': '统计套利协整分析'
    },
    'PAIRS_TRADING_BLUEPRINT.md': {
        'old': '配对交易',
        'new': '配对交易策略实施'
    },
    'STATISTICAL_ARBITRAGE_BLUEPRINT.md': {
        'old': '配对交易',
        'new': '统计套利配对交易'
    },
    'ALGORITHMIC_TRADING_OPTIMIZER_BLUEPRINT.md': {
        'old': '系统架构蓝图设计与实施指导与实施方案',
        'new': '算法交易系统架构实施'
    },
    'SMART_ORDER_ROUTER_BLUEPRINT.md': {
        'old': '系统架构蓝图设计与实施指导与实施方案',
        'new': '智能订单路由架构实施'
    },
    'TRADING_COST_OPTIMIZATION_BLUEPRINT.md': {
        'old': '系统架构蓝图设计与实施指导与实施方案',
        'new': '交易成本优化架构实施'
    },
    'EXECUTION_ALGORITHM_BLUEPRINT.md': {
        'old': '系统架构蓝图设计与实施指导与实施方案',
        'new': '执行算法架构实施'
    },
    'MARKET_IMPACT_MODEL_BLUEPRINT.md': {
        'old': '系统架构蓝图设计与实施指导与实施方案',
        'new': '市场冲击模型架构实施'
    },
}

def fix_overlap(file_path, old_resp, new_resp):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if f'- {old_resp}' in content:
        content = content.replace(f'- {old_resp}', f'- {new_resp}')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, f'已修复: {old_resp} -> {new_resp}'
    
    return False, '未找到重叠职责'

print('='*80)
print('修复P1问题: 职责重叠')
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
