#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
为缺少YAML头部的文档添加标准YAML头部
"""

import re
import os
from pathlib import Path
from datetime import datetime

def infer_layer_from_path(file_path):
    """根据文件路径推断Layer归属"""
    file_name = os.path.basename(file_path).upper()
    
    # Layer 0: 数据源层
    if any(keyword in file_name for keyword in ['DATA_SOURCE', 'MARKET_DATA', 'ALTERNATIVE_DATA', 'REALTIME_DATA']):
        return 'Layer 0 (数据源层)'
    
    # Layer 1: 数据层
    if any(keyword in file_name for keyword in ['DATA_CATALOG', 'DATA_QUALITY', 'DATA_VERSION', 'DATA_GOVERNANCE', 
                                                  'DATA_LIFECYCLE', 'DATA_SECURITY', 'DATA_COST', 'DATA_OBSERVABILITY',
                                                  'DATA_FABRIC', 'DATA_MESH', 'HIGH_PERFORMANCE_DATA']):
        return 'Layer 1 (数据层)'
    
    # Layer 2: Alpha因子层
    if any(keyword in file_name for keyword in ['ALPHA_FACTOR', 'FACTOR_', 'COINTEGRATION', 'FACTOR_BACKTEST',
                                                  'FACTOR_EXPOSURE', 'FACTOR_NEUTRAL']):
        return 'Layer 2 (Alpha因子层)'
    
    # Layer 3: 策略层
    if any(keyword in file_name for keyword in ['STRATEGY_', 'INTRADAY_STRATEGY', 'OPENING_STRATEGY',
                                                  'STATISTICAL_ARBITRAGE', 'MULTI_STRATEGY']):
        return 'Layer 3 (策略层)'
    
    # Layer 4: 机器学习层
    if any(keyword in file_name for keyword in ['AI_', 'ML_', 'MACHINE_LEARNING', 'AUTO_REPAIR', 'AI_ENHANCEMENT',
                                                  'MARKET_REGIME', 'ECONOMIC_REGIME']):
        return 'Layer 4 (机器学习层)'
    
    # Layer 5: 执行层
    if any(keyword in file_name for keyword in ['EXECUTION_', 'SMART_EXECUTION', 'SMART_ORDER', 'TRADING_SIGNAL',
                                                  'MARKET_IMPACT', 'TRADING_COST']):
        return 'Layer 5 (执行层)'
    
    # Layer 6: 组合优化层
    if any(keyword in file_name for keyword in ['PORTFOLIO_', 'MULTI_ASSET', 'MULTI_OBJECTIVE', 'DYNAMIC_ASSET',
                                                  'BLACK_LITTERMAN', 'RISK_PARITY', 'HIERARCHICAL_RISK',
                                                  'PORTFOLIO_ATTRIBUTION', 'PORTFOLIO_CONSTRAINT', 'PORTFOLIO_DIVERSIFICATION',
                                                  'PORTFOLIO_INSURANCE', 'PORTFOLIO_OPTIMIZATION', 'PORTFOLIO_PERFORMANCE',
                                                  'PORTFOLIO_REBALANCING', 'PORTFOLIO_SCENARIO', 'STRATEGY_PORTFOLIO',
                                                  'STRATEGIC_ALLOCATION', 'STRATEGIC_WEIGHTING', 'RL_REBALANCING',
                                                  'SIMPLIFIED_RISK_BUDGET', 'TRANSACTION_COST_AWARE', 'TURNOVER_CONTROL',
                                                  'QUARTERLY_REBALANCE', 'MEAN_VARIANCE', 'ROBUST_OPTIMIZATION',
                                                  'LIQUIDITY_CONSTRAINED', 'HIERARCHICAL_OPTIMIZATION', 'FINANCING_OPTIMIZATION',
                                                  'TAX_LOSS_HARVESTING']):
        return 'Layer 6 (组合优化层)'
    
    # Layer 7: 风控层
    if any(keyword in file_name for keyword in ['RISK_', 'VAR_ES', 'STRESS_TEST', 'TAIL_RISK', 'MARGIN_CALL',
                                                  'LIQUIDITY_MANAGEMENT', 'DYNAMIC_LEVERAGE', 'REALTIME_RISK',
                                                  'RISK_ATTRIBUTION', 'RISK_CONTRIBUTION', 'RISK_CONTROL',
                                                  'BARRA_RISK']):
        return 'Layer 7 (风控层)'
    
    # Layer 8: 人机交互层
    if any(keyword in file_name for keyword in ['MONITORING_DASHBOARD', 'ENHANCED_ALERT', 'QUALITY_REPORT',
                                                  'QUALITY_SCORING', 'SYSTEM_ENHANCEMENT', 'SYSTEM_INTEGRATION']):
        return 'Layer 8 (人机交互层)'
    
    # Layer 9: 治理层
    if any(keyword in file_name for keyword in ['GOVERNANCE', 'COMPLIANCE', 'AUDIT']):
        return 'Layer 9 (治理层)'
    
    # 默认返回Layer 4
    return 'Layer 4 (机器学习层)'

def add_yaml_header(file_path):
    """为文档添加YAML头部"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经有YAML头部
        if content.startswith('---'):
            return False, '已有YAML头部'
        
        # 推断Layer归属
        layer = infer_layer_from_path(file_path)
        
        # 提取module_id
        module_id_match = re.search(r'module_id:\s*`?([A-Z_0-9]+)`?', content, re.IGNORECASE)
        if module_id_match:
            module_id = module_id_match.group(1)
        else:
            # 从文件名生成module_id
            file_name = os.path.basename(file_path).replace('_BLUEPRINT.md', '').upper()
            module_id = f'{file_name}_001'
        
        # 创建YAML头部
        yaml_header = f'''---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 个人开发者
standard_type: 专业量化机构文档
layer: "{layer}"
---
'''
        
        # 添加YAML头部
        new_content = yaml_header + content
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f'已添加YAML头部 (Layer: {layer})'
    
    except Exception as e:
        return False, str(e)

def main():
    """主函数"""
    print('=' * 80)
    print('为缺少YAML头部的文档添加标准YAML头部')
    print('=' * 80)
    print()
    
    # 读取缺少Layer归属的文档列表
    missing_layer_docs = [
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/AI_ENHANCEMENT_INTEGRATION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/AUTO_REPAIR_ENGINE_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/BARRA_RISK_MODEL_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/BLACK_LITTERMAN_MODEL_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/COINTEGRATION_ANALYSIS_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_CATALOG_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_MESH_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_OBSERVABILITY_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/HIERARCHICAL_RISK_BUDGET_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MARKET_IMPACT_MODEL_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MULTI_OBJECTIVE_OPTIMIZATION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_ATTRIBUTION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_OPTIMIZER_INTEGRATION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_PERFORMANCE_EVALUATION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_REBALANCING_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RISK_PARITY_STRATEGY_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RL_REBALANCING_SYSTEM_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SIMPLIFIED_RISK_BUDGET_SYSTEM_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STRATEGY_PORTFOLIO_OPTIMIZATION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STRESS_TESTING_SYSTEM_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SYSTEM_ENHANCEMENT_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/TAX_LOSS_HARVESTING_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/VAR_ES_MONITORING_BLUEPRINT.md',
    ]
    
    # 添加YAML头部
    added_count = 0
    failed_count = 0
    
    for doc in missing_layer_docs:
        if os.path.exists(doc):
            success, message = add_yaml_header(doc)
            if success:
                print(f'✓ {doc}: {message}')
                added_count += 1
            else:
                print(f'✗ {doc}: {message}')
                failed_count += 1
        else:
            print(f'✗ {doc}: 文件不存在')
            failed_count += 1
    
    print()
    print(f'添加完成: {added_count}个成功, {failed_count}个失败')

if __name__ == '__main__':
    main()
