import os
import re

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

# 修复职责重叠 - 调整职责描述使其更具体
responsibility_adjustments = {
    'CONSTRAINT_SOLVER_BLUEPRINT.md': {
        'old': '约束验证',
        'new': '约束求解验证'
    },
    'PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md': {
        'old': '约束验证',
        'new': '约束条件验证'
    },
    'MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md': {
        'old': '策略协调',
        'new': '多策略协调'
    },
    'STRATEGY_PORTFOLIO_OPTIMIZATION_BLUEPRINT.md': {
        'old': '策略协调',
        'new': '策略权重协调'
    },
    'PORTFOLIO_REBALANCING_BLUEPRINT.md': {
        'old': '再平衡策略',
        'new': '组合再平衡策略'
    },
    'TRANSACTION_COST_AWARE_REBALANCING_BLUEPRINT.md': {
        'old': '再平衡策略',
        'new': '成本感知再平衡策略'
    },
    'TRANSACTION_COST_ANALYSIS_ENGINE_BLUEPRINT.md': {
        'old': '交易成本优化',
        'new': '交易成本分析优化'
    },
    'TRANSACTION_COST_AWARE_REBALANCING_BLUEPRINT.md': {
        'old': '交易成本优化',
        'new': '交易成本感知优化'
    }
}

# 修复核心定位过短
core_position_extensions = {
    'CONSTRAINT_SOLVER_BLUEPRINT.md': '负责约束求解器的设计与实现，提供约束建模、求解算法和约束验证功能，支持组合优化中的约束处理。本模块是组合优化层的核心组件，确保优化结果满足所有约束条件。',
    'MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md': '负责多策略分层系统的设计与实现，构建策略分层架构，提供策略协调和风险预算分配功能，支持多策略管理。本模块实现策略间的协调与优化，确保各策略协同工作。',
    'PORTFOLIO_OPTIMIZATION_BLUEPRINT.md': '负责投资组合优化框架的设计与实现，协调各类优化器，整合优化结果，提供多目标优化支持。本模块是组合优化层的核心框架，统一管理各类优化任务。',
    'QUARTERLY_REBALANCE_BLUEPRINT.md': '负责季度再平衡模块的设计与实现，制定再平衡计划，优化执行路径，控制交易成本。本模块提供定期再平衡功能，确保投资组合与目标配置保持一致。',
    'ROBUST_OPTIMIZATION_BLUEPRINT.md': '负责鲁棒优化模块的设计与实现，处理参数不确定性，提供鲁棒解求解功能，降低模型风险。本模块确保优化结果在参数不确定性下仍保持良好性能。',
    'STRATEGY_PORTFOLIO_OPTIMIZATION_BLUEPRINT.md': '负责策略组合优化模块的设计与实现，分配策略权重，协调多策略，构建最优组合。本模块实现策略层面的组合优化，提升整体投资效率。',
    'TAX_LOSS_HARVESTING_BLUEPRINT.md': '负责税收损失收割模块的设计与实现，优化税务效率，实现损失收割策略，提升税后收益。本模块通过合理的损失实现策略，降低投资组合的税务负担。',
    'TRANSACTION_COST_AWARE_REBALANCING_BLUEPRINT.md': '负责成本感知再平衡模块的设计与实现，优化交易成本，制定再平衡策略，平衡成本与跟踪误差。本模块在再平衡过程中充分考虑交易成本，实现成本最优的再平衡方案。'
}

fixed_files = []

# 修复职责边界
file_path = os.path.join(blueprints_dir, 'QUARTERLY_REBALANCE_BLUEPRINT.md')
with open(file_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()

if '职责边界' not in content:
    boundary_text = '''> **职责边界**: 
> - ✅ 本文档负责：季度再平衡、定期调整、再平衡计划制定
> - ❌ 本文档不负责：日常再平衡（由PORTFOLIO_REBALANCING负责）
'''
    if '## 核心定位' in content:
        content = content.replace('## 核心定位', boundary_text + '\n## 核心定位', 1)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        fixed_files.append('QUARTERLY_REBALANCE_BLUEPRINT.md')
        print('Added boundary: QUARTERLY_REBALANCE_BLUEPRINT.md')

# 修复职责重叠
for file, adjustment in responsibility_adjustments.items():
    file_path = os.path.join(blueprints_dir, file)
    
    if not os.path.exists(file_path):
        continue
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if adjustment['old'] in content:
        content = content.replace(f'- {adjustment["old"]}', f'- {adjustment["new"]}')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        fixed_files.append(file)
        print(f'Fixed responsibility: {file}')

# 修复核心定位过短
for file, core_text in core_position_extensions.items():
    file_path = os.path.join(blueprints_dir, file)
    
    if not os.path.exists(file_path):
        continue
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 查找核心定位章节
    core_match = re.search(r'## 核心定位\s*[\r\n]+(.+?)(?=\n##|\n>|\Z)', content, re.DOTALL)
    if core_match:
        core_content = core_match.group(1).strip()
        
        if len(core_content) < 50:
            # 替换核心定位内容
            new_content = content[:core_match.start()] + '## 核心定位\n\n' + core_text + '\n' + content[core_match.end():]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            fixed_files.append(file)
            print(f'Extended core position: {file}')

print(f'\nTotal fixed: {len(set(fixed_files))} files')
