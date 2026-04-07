import os
import re

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

responsibility_boundaries = {
    'BLACK_LITTERMAN_MODEL': {
        '负责': 'Black-Litterman模型、观点融合、市场均衡收益计算',
        '不负责': '风险预算分配（由风险预算模块负责）'
    },
    'CONSTRAINT_SOLVER': {
        '负责': '约束数学建模、求解算法实现、约束冲突检测',
        '不负责': '约束规则制定（由约束管理模块负责）'
    },
    'DYNAMIC_ASSET_ALLOCATION': {
        '负责': '动态资产配置、资产权重调整、市场环境适应',
        '不负责': '单资产优化（由均值方差优化模块负责）'
    },
    'FACTOR_NEUTRAL_OPTIMIZATION': {
        '负责': '因子中性约束、因子暴露控制、中性优化求解',
        '不负责': '因子计算（由因子模块负责）'
    },
    'HIERARCHICAL_OPTIMIZATION_FRAMEWORK': {
        '负责': '分层优化框架、优化层级协调、层级间约束传递',
        '不负责': '具体优化算法（由各优化模块负责）'
    },
    'LIQUIDITY_CONSTRAINED_OPTIMIZATION': {
        '负责': '流动性约束建模、流动性成本估算、流动性优化',
        '不负责': '流动性预测（由流动性管理模块负责）'
    },
    'MEAN_VARIANCE_OPTIMIZATION': {
        '负责': '均值方差优化、有效前沿计算、最优权重求解',
        '不负责': '风险模型构建（由风险模型模块负责）'
    },
    'MULTI_ASSET_ALLOCATION': {
        '负责': '多资产配置、跨资产优化、资产相关性建模',
        '不负责': '单资产优化（由均值方差优化模块负责）'
    },
    'MULTI_OBJECTIVE_OPTIMIZATION': {
        '负责': '多目标优化、帕累托最优解生成、目标权衡分析',
        '不负责': '单目标优化（由均值方差优化模块负责）'
    },
    'MULTI_STRATEGY_HIERARCHICAL_SYSTEM': {
        '负责': '多策略分层、策略协调、层级优化',
        '不负责': '策略信号生成（由策略模块负责）'
    },
    'PORTFOLIO_ATTRIBUTION': {
        '负责': '组合归因分析、收益分解、风险归因',
        '不负责': '组合优化（由优化模块负责）'
    },
    'PORTFOLIO_CONSTRAINT_MANAGEMENT': {
        '负责': '约束规则管理、约束配置、约束验证',
        '不负责': '约束求解（由约束求解模块负责）'
    },
    'PORTFOLIO_DIVERSIFICATION_METRIC': {
        '负责': '分散度度量、风险分散评估、集中度分析',
        '不负责': '组合优化（由优化模块负责）'
    },
    'PORTFOLIO_INSURANCE_STRATEGY': {
        '负责': '组合保险策略、CPPI/OBPI实现、保本线管理',
        '不负责': '组合优化（由优化模块负责）'
    },
    'PORTFOLIO_OPTIMIZATION': {
        '负责': '投资组合优化框架、优化流程协调、优化结果整合',
        '不负责': '具体优化算法（由各优化模块负责）'
    },
    'PORTFOLIO_OPTIMIZATION_DIAGNOSTICS': {
        '负责': '优化诊断、优化结果验证、优化问题检测',
        '不负责': '优化求解（由优化模块负责）'
    },
    'PORTFOLIO_OPTIMIZER_INTEGRATION': {
        '负责': '优化器集成、优化接口统一、优化器调度',
        '不负责': '优化算法实现（由各优化模块负责）'
    },
    'PORTFOLIO_PERFORMANCE_EVALUATION': {
        '负责': '组合绩效评估、绩效指标计算、绩效归因',
        '不负责': '组合优化（由优化模块负责）'
    },
    'PORTFOLIO_REBALANCING': {
        '负责': '组合再平衡、信号驱动再平衡、再平衡执行',
        '不负责': '再平衡信号生成（由信号模块负责）'
    },
    'PORTFOLIO_SCENARIO_ANALYSIS': {
        '负责': '情景分析、压力测试、情景归因',
        '不负责': '情景生成（由情景模块负责）'
    },
    'QUARTERLY_REBALANCE': {
        '负责': '季度再平衡、定期再平衡、再平衡计划',
        '不负责': '再平衡信号生成（由信号模块负责）'
    },
    'RISK_PARITY_STRATEGY': {
        '负责': '风险平价策略、风险贡献均衡、风险预算分配',
        '不负责': '风险模型构建（由风险模型模块负责）'
    },
    'ROBUST_OPTIMIZATION': {
        '负责': '鲁棒优化、不确定性建模、鲁棒解求解',
        '不负责': '不确定性预测（由预测模块负责）'
    },
    'STRATEGY_PORTFOLIO_OPTIMIZATION': {
        '负责': '策略组合优化、策略权重分配、策略风险控制',
        '不负责': '策略信号生成（由策略模块负责）'
    },
    'TAX_LOSS_HARVESTING': {
        '负责': '税收损失收割、税务优化、税后收益最大化',
        '不负责': '交易执行（由交易模块负责）'
    },
    'TRANSACTION_COST_ANALYSIS_ENGINE': {
        '负责': '交易成本分析、成本预测、成本优化',
        '不负责': '交易执行（由交易模块负责）'
    },
    'TRANSACTION_COST_AWARE_REBALANCING': {
        '负责': '成本感知再平衡、交易成本优化、再平衡成本控制',
        '不负责': '再平衡信号生成（由信号模块负责）'
    }
}

fixed_files = []
skipped_files = []

for file in os.listdir(blueprints_dir):
    if file.endswith('.md') and 'BLUEPRINT' in file:
        file_path = os.path.join(blueprints_dir, file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查文件是否有足够内容
        if len(content) < 200:
            skipped_files.append((file, '文件内容过短'))
            continue
        
        # 检查是否缺少职责边界（使用多种模式）
        has_boundary = False
        patterns = [
            r'>\s*\*\*职责边界\*\*:',
            r'>\s*\*\*职责边界\*\*：',
            r'职责边界.*负责',
        ]
        for pattern in patterns:
            if re.search(pattern, content):
                has_boundary = True
                break
        
        if has_boundary:
            skipped_files.append((file, '已有职责边界'))
            continue
        
        # 提取模块名称
        module_name = file.replace('_BLUEPRINT.md', '')
        
        if module_name not in responsibility_boundaries:
            skipped_files.append((file, '未找到职责边界模板'))
            continue
        
        boundary = responsibility_boundaries[module_name]
        boundary_text = f'''> **职责边界**: 
> - ✅ 本文档负责：{boundary['负责']}
> - ❌ 本文档不负责：{boundary['不负责']}
'''
        
        # 在核心定位之前插入职责边界
        if '## 核心定位' in content:
            new_content = content.replace('## 核心定位', boundary_text + '\n## 核心定位', 1)
            
            # 验证修改后的内容长度
            if len(new_content) > len(content):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                fixed_files.append(file)
                print(f'Added boundary: {file}')
            else:
                skipped_files.append((file, '修改后内容未增长'))
        else:
            skipped_files.append((file, '未找到核心定位章节'))

print(f'\n修复完成: {len(fixed_files)} 个文件')
print(f'跳过: {len(skipped_files)} 个文件')

if skipped_files:
    print('\n跳过详情:')
    for f, reason in skipped_files[:10]:
        print(f'  - {f}: {reason}')
