#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复重复YAML头部和Layer字段格式问题
"""

import re
import os
from pathlib import Path

def fix_duplicate_yaml_and_layer():
    """修复重复YAML头部和Layer字段格式问题"""
    print('=' * 80)
    print('修复重复YAML头部和Layer字段格式问题')
    print('=' * 80)
    print()
    
    # 需要修复的文档列表
    docs_to_fix = [
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/AI_PATTERN_RECOGNITION_ENGINE_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/ALPHA_FACTOR_FACTORY_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/CONSTRAINT_SOLVER_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_QUALITY_MONITORING_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DYNAMIC_CORRELATION_MODELING_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DYNAMIC_LEVERAGE_MANAGEMENT_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/ECONOMIC_REGIME_ENGINE_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/FINANCING_OPTIMIZATION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/INTRADAY_STRATEGY_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/LIQUIDITY_MANAGEMENT_SYSTEM_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MARGIN_CALL_MONITOR_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MARKET_IMPACT_MODEL_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MARKET_REGIME_DETECTION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MEAN_VARIANCE_OPTIMIZATION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MULTI_ASSET_ALLOCATION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/OPENING_STRATEGY_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_INSURANCE_STRATEGY_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_REBALANCING_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/QUARTERLY_REBALANCE_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RISK_CONTROL_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RL_REBALANCING_SYSTEM_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SMART_EXECUTION_ENGINE_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STATISTICAL_ARBITRAGE_MODULE_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STRATEGIC_WEIGHTING_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/TAIL_RISK_HEDGING_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/TRADING_COST_OPTIMIZATION_BLUEPRINT.md',
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/UNIFIED_DATA_INFRASTRUCTURE_BLUEPRINT.md',
    ]
    
    stats = {
        'total': len(docs_to_fix),
        'fixed': 0,
        'skipped': 0,
        'errors': 0
    }
    
    for doc_path in docs_to_fix:
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找所有YAML头部
            yaml_pattern = r'^---\s*\n(.*?)\n---'
            yaml_matches = list(re.finditer(yaml_pattern, content, re.DOTALL))
            
            if len(yaml_matches) > 1:
                # 有多个YAML头部，保留第二个，删除第一个
                first_yaml = yaml_matches[0]
                second_yaml = yaml_matches[1]
                
                # 提取第二个YAML内容
                second_yaml_content = second_yaml.group(1)
                
                # 修正layer字段格式
                # 查找layer字段
                layer_match = re.search(r'^layer:\s*[\'"]?(.+?)[\'"]?\s*$', second_yaml_content, re.MULTILINE)
                
                if layer_match:
                    layer_value = layer_match.group(1)
                    
                    # 提取Layer编号
                    layer_num_match = re.search(r'Layer (\d+)', layer_value)
                    if layer_num_match:
                        layer_num = layer_num_match.group(1)
                        
                        # 根据Layer编号确定正确的Layer名称
                        layer_names = {
                            '0': 'Layer 0 (数据源层)',
                            '1': 'Layer 1 (数据层)',
                            '2': 'Layer 2 (Alpha因子层)',
                            '3': 'Layer 3 (策略层)',
                            '4': 'Layer 4 (机器学习层)',
                            '5': 'Layer 5 (执行层)',
                            '6': 'Layer 6 (组合优化层)',
                            '7': 'Layer 7 (风控层)',
                            '8': 'Layer 8 (人机交互层)',
                            '9': 'Layer 9 (治理层)',
                            '10': 'Layer 10 (治理层)',
                            '11': 'Layer 11 (战略决策层)',
                        }
                        
                        correct_layer = layer_names.get(layer_num, f'Layer {layer_num}')
                        
                        # 替换layer字段
                        second_yaml_content = re.sub(
                            r'^layer:\s*[\'"]?.+?[\'"]?\s*$',
                            f'layer: {correct_layer}',
                            second_yaml_content,
                            flags=re.MULTILINE
                        )
                
                # 删除第一个YAML头部
                new_content = content[first_yaml.end():]
                
                # 替换第二个YAML头部内容
                new_content = '---\n' + second_yaml_content + '\n---' + new_content[second_yaml.end():]
                
                # 写回文件
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                stats['fixed'] += 1
                print(f'✅ {Path(doc_path).name}: 已修复')
            else:
                stats['skipped'] += 1
                print(f'⏭️  {Path(doc_path).name}: 无需修复')
        
        except Exception as e:
            stats['errors'] += 1
            print(f'❌ {Path(doc_path).name}: {str(e)}')
    
    print()
    print('=' * 80)
    print('修复统计')
    print('=' * 80)
    print(f'总文档数: {stats["total"]}')
    print(f'已修复: {stats["fixed"]}')
    print(f'已跳过: {stats["skipped"]}')
    print(f'错误数: {stats["errors"]}')
    
    return stats

if __name__ == '__main__':
    fix_duplicate_yaml_and_layer()
