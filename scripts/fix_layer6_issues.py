import os
import re
from datetime import datetime

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

responsibility_templates = {
    'BLACK_LITTERMAN_MODEL_BLUEPRINT.md': ['Black-Litterman模型', '观点融合', '市场均衡收益计算', '后验收益估计'],
    'CONSTRAINT_SOLVER_BLUEPRINT.md': ['约束建模', '求解算法', '优化引擎', '约束验证'],
    'DYNAMIC_ASSET_ALLOCATION_BLUEPRINT.md': ['动态资产配置', '资产权重调整', '市场环境适应', '配置策略优化'],
    'FACTOR_NEUTRAL_OPTIMIZATION_BLUEPRINT.md': ['因子中性优化', '因子暴露控制', '中性约束求解', '风险因子管理'],
    'HIERARCHICAL_OPTIMIZATION_FRAMEWORK_BLUEPRINT.md': ['分层优化框架', '层级协调', '优化流程管理', '多层级优化'],
    'LIQUIDITY_CONSTRAINED_OPTIMIZATION_BLUEPRINT.md': ['流动性约束优化', '流动性建模', '交易成本控制', '流动性风险'],
    'MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md': ['市场参与者模拟', '模拟结果应用', '模拟集成', '行为建模'],
    'MEAN_VARIANCE_OPTIMIZATION_BLUEPRINT.md': ['均值方差优化', '有效前沿计算', '最优权重求解', '风险收益权衡'],
    'MULTI_ASSET_ALLOCATION_BLUEPRINT.md': ['多资产配置', '跨资产优化', '资产相关性建模', '配置权重分配'],
    'MULTI_OBJECTIVE_OPTIMIZATION_BLUEPRINT.md': ['多目标优化', '目标权衡', 'Pareto前沿', '优化目标管理'],
    'MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md': ['多策略分层', '策略协调', '层级优化', '信号融合'],
    'PORTFOLIO_ATTRIBUTION_BLUEPRINT.md': ['组合归因', '收益分解', '风险归因', '归因报告'],
    'PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md': ['组合约束管理', '约束条件设置', '约束验证', '约束优化'],
    'PORTFOLIO_DIVERSIFICATION_METRIC_BLUEPRINT.md': ['分散度度量', '风险分散评估', '集中度分析', '分散化优化'],
    'PORTFOLIO_INSURANCE_STRATEGY_BLUEPRINT.md': ['组合保险策略', '保本策略', 'CPPI策略', 'OBPI策略'],
    'PORTFOLIO_OPTIMIZATION_BLUEPRINT.md': ['投资组合优化框架', '优化流程协调', '优化结果整合', '多目标优化支持'],
    'PORTFOLIO_OPTIMIZATION_DIAGNOSTICS_BLUEPRINT.md': ['优化诊断', '结果验证', '性能分析', '问题排查'],
    'PORTFOLIO_OPTIMIZER_INTEGRATION_BLUEPRINT.md': ['优化器集成', '接口封装', '优化器协调', '结果整合'],
    'PORTFOLIO_PERFORMANCE_EVALUATION_BLUEPRINT.md': ['组合绩效评估', '绩效指标计算', '基准比较', '绩效报告'],
    'PORTFOLIO_REBALANCING_BLUEPRINT.md': ['组合再平衡', '再平衡策略', '交易成本优化', '再平衡触发'],
    'PORTFOLIO_SCENARIO_ANALYSIS_BLUEPRINT.md': ['情景分析', '压力测试', '情景归因', '情景报告生成'],
    'QUARTERLY_REBALANCE_BLUEPRINT.md': ['季度再平衡', '定期调整', '再平衡计划', '执行优化'],
    'RISK_PARITY_STRATEGY_BLUEPRINT.md': ['风险平价策略', '风险贡献均衡', '权重优化', '风险预算'],
    'ROBUST_OPTIMIZATION_BLUEPRINT.md': ['鲁棒优化', '不确定性建模', '鲁棒解求解', '参数敏感性'],
    'STRATEGY_PORTFOLIO_OPTIMIZATION_BLUEPRINT.md': ['策略组合优化', '策略权重分配', '策略协调', '组合构建'],
    'TAX_LOSS_HARVESTING_BLUEPRINT.md': ['税收损失收割', '税务优化', '损失实现', '税务效率'],
    'TRANSACTION_COST_ANALYSIS_ENGINE_BLUEPRINT.md': ['交易成本分析', '成本建模', '成本预测', '成本优化'],
    'TRANSACTION_COST_AWARE_REBALANCING_BLUEPRINT.md': ['成本感知再平衡', '交易成本优化', '再平衡策略', '成本控制']
}

boundary_templates = {
    'QUARTERLY_REBALANCE_BLUEPRINT.md': {
        '负责': '季度再平衡、定期调整、再平衡计划制定',
        '不负责': '日常再平衡（由PORTFOLIO_REBALANCING负责）'
    }
}

core_position_templates = {
    'CONSTRAINT_SOLVER_BLUEPRINT.md': '负责约束求解器的设计与实现，提供约束建模、求解算法和约束验证功能，支持组合优化中的约束处理。',
    'MULTI_ASSET_ALLOCATION_BLUEPRINT.md': '负责多资产配置模块的设计与实现，提供跨资产优化、资产相关性建模和配置权重分配功能，支持多资产组合构建。',
    'MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md': '负责多策略分层系统的设计与实现，构建策略分层架构，提供策略协调和风险预算分配功能，支持多策略管理。',
    'PORTFOLIO_OPTIMIZATION_BLUEPRINT.md': '负责投资组合优化框架的设计与实现，协调各类优化器，整合优化结果，提供多目标优化支持。',
    'QUARTERLY_REBALANCE_BLUEPRINT.md': '负责季度再平衡模块的设计与实现，制定再平衡计划，优化执行路径，控制交易成本。',
    'ROBUST_OPTIMIZATION_BLUEPRINT.md': '负责鲁棒优化模块的设计与实现，处理参数不确定性，提供鲁棒解求解功能，降低模型风险。',
    'STRATEGY_PORTFOLIO_OPTIMIZATION_BLUEPRINT.md': '负责策略组合优化模块的设计与实现，分配策略权重，协调多策略，构建最优组合。',
    'TAX_LOSS_HARVESTING_BLUEPRINT.md': '负责税收损失收割模块的设计与实现，优化税务效率，实现损失收割策略，提升税后收益。',
    'TRANSACTION_COST_AWARE_REBALANCING_BLUEPRINT.md': '负责成本感知再平衡模块的设计与实现，优化交易成本，制定再平衡策略，平衡成本与跟踪误差。'
}

fixed_files = []

for file, responsibilities in responsibility_templates.items():
    file_path = os.path.join(blueprints_dir, file)
    
    if not os.path.exists(file_path):
        print(f'File not found: {file}')
        continue
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    original_content = content
    
    # 修复responsibility项
    resp_match = re.search(r'responsibility:\s*[\r\n]+((?:\s+-\s+.+[\r\n]?)+)', content)
    if resp_match:
        resp_text = resp_match.group(1)
        existing_items = re.findall(r'-\s+(.+)', resp_text)
        existing_items = [item.strip() for item in existing_items if item.strip()]
        
        # 检查是否只有1项或包含乱码
        if len(existing_items) <= 1 or any('æ' in item or '' in item for item in existing_items):
            new_resp = 'responsibility:\n' + '\n'.join([f'  - {r}' for r in responsibilities]) + '\n'
            content = content[:resp_match.start()] + new_resp + content[resp_match.end():]
            print(f'Fixed responsibility: {file}')
    
    # 添加职责边界
    if file in boundary_templates:
        if '职责边界' not in content:
            boundary = boundary_templates[file]
            boundary_text = f'''> **职责边界**: 
> - ✅ 本文档负责：{boundary['负责']}
> - ❌ 本文档不负责：{boundary['不负责']}
'''
            if '## 核心定位' in content:
                content = content.replace('## 核心定位', boundary_text + '\n## 核心定位', 1)
                print(f'Added boundary: {file}')
    
    # 修复核心定位
    if file in core_position_templates:
        core_match = re.search(r'## 核心定位\s*[\r\n]+(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if core_match:
            core_content = core_match.group(1).strip()
            if len(core_content) < 50 or '负责' not in core_content:
                new_core = f'\n{core_position_templates[file]}\n'
                content = content[:core_match.start()] + '## 核心定位' + new_core + content[core_match.end():]
                print(f'Fixed core position: {file}')
    
    # 添加变更历史
    if '## 变更历史' not in content and '## 11. 变更历史' not in content:
        change_history = f'''
## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime("%Y-%m-%d")} | 初始版本创建 | 组合优化层负责人 |

'''
        # 在文档末尾添加
        if content.rstrip().endswith('---'):
            content = content.rstrip()[:-3] + change_history + '---\n'
        else:
            content = content.rstrip() + change_history
        print(f'Added change history: {file}')
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        fixed_files.append(file)

print(f'\nTotal fixed: {len(fixed_files)} files')
