import os
import re

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

fixes = {
    'PORTFOLIO_OPTIMIZATION_BLUEPRINT.md': {
        'add_fields': {
            'owner': '实施团队',
            'responsibility': ['投资组合优化框架', '优化流程协调', '优化结果整合']
        },
        'add_boundary': {
            '负责': '投资组合优化框架、优化流程协调、优化结果整合',
            '不负责': '具体优化算法（由各优化模块负责）'
        }
    },
    'TRANSACTION_COST_ANALYSIS_ENGINE_BLUEPRINT.md': {
        'add_fields': {
            'owner': '实施团队',
            'compliance_level': '专业标准'
        }
    },
    'MULTI_ASSET_ALLOCATION_BLUEPRINT.md': {
        'add_responsibility': ['多资产配置', '跨资产优化', '资产相关性建模'],
        'add_boundary': {
            '负责': '多资产配置、跨资产优化、资产相关性建模',
            '不负责': '单资产优化（由均值方差优化模块负责）'
        }
    },
    'MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md': {
        'add_responsibility': ['多策略分层', '策略协调', '层级优化']
    },
    'PORTFOLIO_SCENARIO_ANALYSIS_BLUEPRINT.md': {
        'add_responsibility': ['情景分析', '压力测试', '情景归因'],
        'add_boundary': {
            '负责': '情景分析、压力测试、情景归因',
            '不负责': '情景生成（由情景模块负责）'
        }
    },
    'MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md': {
        'fix_responsibility': ['市场参与者模拟', '模拟结果应用', '模拟集成']
    },
    'PORTFOLIO_DIVERSIFICATION_METRIC_BLUEPRINT.md': {
        'fix_responsibility': ['分散度度量', '风险分散评估', '集中度分析']
    },
    'ROBUST_OPTIMIZATION_BLUEPRINT.md': {
        'fix_responsibility': ['鲁棒优化', '不确定性建模', '鲁棒解求解']
    },
    'DYNAMIC_ASSET_ALLOCATION_BLUEPRINT.md': {
        'add_boundary': {
            '负责': '动态资产配置、资产权重调整、市场环境适应',
            '不负责': '单资产优化（由均值方差优化模块负责）'
        }
    },
    'MEAN_VARIANCE_OPTIMIZATION_BLUEPRINT.md': {
        'add_boundary': {
            '负责': '均值方差优化、有效前沿计算、最优权重求解',
            '不负责': '风险模型构建（由风险模型模块负责）'
        }
    }
}

fixed_files = []

for file, actions in fixes.items():
    file_path = os.path.join(blueprints_dir, file)
    
    if not os.path.exists(file_path):
        print(f'File not found: {file}')
        continue
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    original_content = content
    
    # 添加字段
    if 'add_fields' in actions:
        for field, value in actions['add_fields'].items():
            if field not in content:
                # 在layer字段之前添加
                layer_match = re.search(r'layer:', content)
                if layer_match:
                    if isinstance(value, list):
                        field_content = f'{field}:\n' + '\n'.join([f'  - {v}' for v in value]) + '\n'
                    else:
                        field_content = f'{field}: {value}\n'
                    content = content[:layer_match.start()] + field_content + content[layer_match.start():]
    
    # 添加responsibility
    if 'add_responsibility' in actions:
        if 'responsibility:' not in content:
            layer_match = re.search(r'layer:', content)
            if layer_match:
                resp_content = 'responsibility:\n' + '\n'.join([f'  - {v}' for v in actions['add_responsibility']]) + '\n'
                content = content[:layer_match.start()] + resp_content + content[layer_match.start():]
    
    # 修复responsibility项不足
    if 'fix_responsibility' in actions:
        resp_match = re.search(r'responsibility:\s*[\r\n]+((?:\s+-\s+.+[\r\n]?)+)', content)
        if resp_match:
            new_resp = 'responsibility:\n' + '\n'.join([f'  - {v}' for v in actions['fix_responsibility']]) + '\n'
            content = content[:resp_match.start()] + new_resp + content[resp_match.end():]
    
    # 添加职责边界
    if 'add_boundary' in actions:
        if '职责边界' not in content:
            boundary_text = f'''> **职责边界**: 
> - ✅ 本文档负责：{actions['add_boundary']['负责']}
> - ❌ 本文档不负责：{actions['add_boundary']['不负责']}
'''
            if '## 核心定位' in content:
                content = content.replace('## 核心定位', boundary_text + '\n## 核心定位', 1)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        fixed_files.append(file)
        print(f'Fixed: {file}')

print(f'\nTotal fixed: {len(fixed_files)} files')
