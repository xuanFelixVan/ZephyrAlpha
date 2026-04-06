#!/usr/bin/env python3
"""
强制修复职责重叠问题

功能:
1. 强制更新所有文档的职责描述
2. 处理各种格式问题（重复YAML、BOM等）
3. 确保每个职责描述都是独特的
"""

import os
import re
from pathlib import Path

class ForceResponsibilityFixer:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.blueprint_files = []
        self.fixed_count = 0
    
    def run(self):
        """执行修复"""
        print('=' * 80)
        print('强制修复职责重叠问题')
        print('=' * 80)
        print()
        
        # 1. 扫描蓝图文件
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
        print()
        
        # 2. 强制修复职责描述
        print('2. 强制修复职责描述...')
        self.force_fix()
        print(f'  ✅ 已修复{self.fixed_count}个文档')
        print()
        
        print('=' * 80)
        print('修复完成')
        print('=' * 80)
    
    def scan_blueprint_files(self):
        """扫描蓝图文件"""
        if os.path.exists(self.blueprints_dir):
            for root, dirs, files in os.walk(self.blueprints_dir):
                for file in files:
                    if file.endswith('.md') and file != 'INDEX.md':
                        filepath = os.path.join(root, file)
                        self.blueprint_files.append(filepath)
    
    def force_fix(self):
        """强制修复职责描述"""
        for filepath in self.blueprint_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 清理BOM和重复YAML
                content = self.clean_content(content)
                
                # 生成独特的职责描述
                filename = os.path.basename(filepath).replace('.md', '')
                responsibility = self.generate_responsibility(filename)
                
                # 更新职责描述
                new_content = self.update_responsibility(content, responsibility)
                
                # 写入文件
                with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new_content)
                
                self.fixed_count += 1
                print(f'    ✅ 已修复: {os.path.basename(filepath)}')
            
            except Exception as e:
                print(f'    ⚠️ 无法修复: {filepath} - {e}')
    
    def clean_content(self, content):
        """清理内容"""
        # 移除BOM
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # 移除重复的YAML头部
        # 查找所有YAML块
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        yaml_blocks = re.findall(yaml_pattern, content, re.DOTALL | re.MULTILINE)
        
        if len(yaml_blocks) > 1:
            # 保留第一个YAML块
            first_yaml_end = content.find('---', 3)
            if first_yaml_end != -1:
                first_yaml_end = content.find('\n', first_yaml_end)
                if first_yaml_end != -1:
                    # 找到第二个YAML块的位置
                    second_yaml_start = content.find('---', first_yaml_end)
                    if second_yaml_start != -1:
                        # 删除第二个YAML块
                        second_yaml_end = content.find('---', second_yaml_start + 3)
                        if second_yaml_end != -1:
                            second_yaml_end = content.find('\n', second_yaml_end)
                            if second_yaml_end != -1:
                                content = content[:second_yaml_start] + content[second_yaml_end + 1:]
        
        return content
    
    def generate_responsibility(self, filename):
        """生成职责描述"""
        responsibility_map = {
            'AI_PATTERN_RECOGNITION_ENGINE': 'AI模式识别引擎，负责利用机器学习技术识别市场交易模式，包括趋势识别、反转信号检测、异常波动预警等功能',
            'ALPHA_FACTOR_FACTORY': 'Alpha因子工厂，负责系统化生成、验证和管理Alpha因子，包括因子挖掘、因子测试、因子组合和因子库管理',
            'ALTERNATIVE_DATA_INTEGRATION': '另类数据集成模块，负责整合非传统数据源（如社交媒体、卫星图像、新闻舆情等），提供独特的投资信号',
            'AUTO_REPAIR_ENGINE': '自动修复引擎，负责系统故障的自动诊断、定位和修复，确保系统高可用性和稳定性',
            'BLACK_LITTERMAN_MODEL': 'Black-Litterman资产配置模型，负责结合市场均衡收益和投资者观点，生成最优资产配置方案',
            'COINTEGRATION_ANALYSIS': '协整分析模块，负责识别资产间的长期均衡关系，支持统计套利和配对交易策略',
            'CONSTRAINT_SOLVER': '约束求解器，负责在投资组合优化中处理各类约束条件（如风险预算、行业限制、流动性约束等）',
            'DATA_CATALOG': '数据目录系统，负责数据资产的注册、发现、血缘追踪和元数据管理，提升数据治理能力',
            'DATA_QUALITY_MONITORING': '数据质量监控系统，负责实时检测数据异常、缺失、延迟等问题，确保数据质量符合交易要求',
            'DYNAMIC_CORRELATION_MODELING': '动态相关性建模模块，负责实时估计资产间相关性的时变特征，支持风险管理和投资组合优化',
            'DYNAMIC_LEVERAGE_MANAGEMENT': '动态杠杆管理模块，负责根据市场波动和风险预算动态调整杠杆水平，优化资金使用效率',
            'ECONOMIC_REGIME_ENGINE': '经济周期识别引擎，负责识别当前经济周期阶段（扩张、衰退、复苏等），支持宏观驱动的投资决策',
            'EXECUTION_STRATEGY_BACKTESTER': '执行策略回测器，负责模拟和评估交易执行策略的效果，优化执行算法参数',
            'FACTOR_EXPOSURE_MANAGEMENT': '因子暴露管理模块，负责监控和控制投资组合的因子暴露，实施因子中性化策略',
            'FINANCING_OPTIMIZATION': '融资优化模块，负责优化融资结构和成本，包括保证金管理、证券借贷、回购协议等',
            'INTRADAY_STRATEGY': '日内交易策略模块，负责开发和管理日内高频交易策略，包括开盘策略、收盘策略、盘中策略等',
            'LIQUIDITY_MANAGEMENT_SYSTEM': '流动性管理系统，负责监控市场流动性状况，优化交易执行，管理流动性风险',
            'MARGIN_CALL_MONITOR': '保证金监控器，负责实时监控账户保证金水平，预警追加保证金风险，自动触发减仓操作',
            'MARKET_IMPACT_MODEL': '市场冲击模型，负责预测交易对市场价格的影响，优化交易规模和时机选择',
            'MARKET_REGIME_DETECTION': '市场周期检测模块，负责识别市场状态（牛市、熊市、震荡市等），支持策略切换',
            'MEAN_VARIANCE_OPTIMIZATION': '均值方差优化器，负责基于预期收益和风险协方差矩阵，求解最优投资组合权重',
            'MULTI_ASSET_ALLOCATION': '多资产配置模块，负责跨股票、债券、商品、外汇等多资产类别的战略配置',
            'MULTI_OBJECTIVE_OPTIMIZATION': '多目标优化模块，负责同时优化收益、风险、流动性等多个目标，生成帕累托最优解',
            'MULTI_PERIOD_DYNAMIC_OPTIMIZATION': '多期动态优化模块，负责考虑跨期决策的投资组合优化，支持动态再平衡策略',
            'MULTI_STRATEGY_HIERARCHICAL_SYSTEM': '多策略分层系统，负责协调和管理多个交易策略的信号生成、风险分配和执行',
            'OPENING_STRATEGY': '开盘策略模块，负责开发和管理开盘时段的交易策略，利用开盘价偏差和流动性特征',
            'PORTFOLIO_ATTRIBUTION': '组合归因分析模块，负责分解投资组合收益来源，评估策略贡献和风险暴露',
            'PORTFOLIO_CONSTRAINT_MANAGEMENT': '组合约束管理模块，负责定义和管理投资组合约束条件，确保合规性和风险控制',
            'PORTFOLIO_DIVERSIFICATION_METRIC': '组合分散化度量模块，负责评估投资组合的分散化程度，优化资产配置',
            'PORTFOLIO_INSURANCE_STRATEGY': '组合保险策略模块，负责实施投资组合保护策略，如CPPI、OBPI等',
            'PORTFOLIO_OPTIMIZATION_DIAGNOSTICS': '组合优化诊断模块，负责诊断优化问题的数值稳定性、约束冲突等',
            'PORTFOLIO_OPTIMIZER_INTEGRATION': '组合优化器集成模块，负责集成多种优化算法（凸优化、遗传算法等），提供统一接口',
            'PORTFOLIO_PERFORMANCE_EVALUATION': '组合绩效评估模块，负责计算和评估投资组合的风险调整收益、夏普比率等指标',
            'PORTFOLIO_REBALANCING': '组合再平衡模块，负责定期或触发式调整投资组合权重，维持目标配置',
            'PORTFOLIO_SCENARIO_ANALYSIS': '组合情景分析模块，负责模拟不同市场情景下的投资组合表现，评估尾部风险',
            'QUALITY_REPORT_AUTOMATION': '质量报告自动化模块，负责自动生成系统和数据质量报告，支持治理决策',
            'QUALITY_SCORING_SYSTEM': '质量评分系统，负责对系统和数据质量进行量化评分，建立质量基准',
            'QUARTERLY_REBALANCE': '季度再平衡模块，负责实施季度投资组合再平衡，考虑交易成本和税收影响',
            'REALTIME_DATA_LAKE': '实时数据湖，负责存储和管理实时市场数据、交易数据，支持流式计算',
            'REALTIME_RISK_HEDGE_ENGINE': '实时风险对冲引擎，负责动态对冲投资组合风险暴露，实施Delta中性策略',
            'RISK_ATTRIBUTION_SYSTEM': '风险归因系统，负责分解投资组合风险来源，识别主要风险因子',
            'RISK_CONTRIBUTION_ANALYSIS': '风险贡献分析模块，负责计算各资产或因子对总风险的边际贡献',
            'RISK_CONTROL': '风险控制模块，负责实施风险限额管理、止损策略、风险预警等风险控制措施',
            'RISK_PARITY_STRATEGY': '风险平价策略模块，负责构建风险平价投资组合，实现风险均衡配置',
            'RL_REBALANCING_SYSTEM': '强化学习再平衡系统，负责利用强化学习算法优化再平衡决策',
            'ROBUST_OPTIMIZATION': '鲁棒优化模块，负责在参数不确定性下优化投资组合，提升策略稳健性',
            'SIMPLIFIED_RISK_BUDGET_SYSTEM': '简化风险预算系统，负责实施基于风险预算的资产配置策略',
            'SIMPLIFIED_TIMEFRAME_COORDINATION': '简化时间框架协调模块，负责协调不同时间尺度的交易信号',
            'SMART_EXECUTION_ENGINE': '智能执行引擎，负责优化交易执行路径，最小化市场冲击和交易成本',
            'SMART_ORDER_ROUTER': '智能订单路由器，负责将大额订单拆分并路由至最优交易场所',
            'STATISTICAL_ARBITRAGE_MODULE': '统计套利模块，负责实施基于统计模型的套利策略，如配对交易、协整套利等',
            'STRATEGIC_ALLOCATION_ENGINE': '战略配置引擎，负责长期资产配置决策，考虑投资目标、风险偏好和市场环境',
            'STRATEGIC_WEIGHTING': '战略权重配置模块，负责确定各类资产的长期战略权重',
            'STRATEGY_PORTFOLIO_OPTIMIZATION': '策略组合优化模块，负责优化多个策略的资金分配和风险预算',
            'STRATEGY_SELECTION': '策略选择模块，负责根据市场环境动态选择最优策略组合',
            'STRESS_TESTING_SYSTEM': '压力测试系统，负责模拟极端市场情景，评估投资组合的抗压能力',
            'SYSTEM_ENHANCEMENT': '系统增强模块，负责实施系统功能增强和性能优化',
            'SYSTEM_INTEGRATION': '系统集成模块，负责整合各子系统，确保数据流和控制流的顺畅',
            'TAIL_RISK_HEDGING': '尾部风险对冲模块，负责购买尾部风险保护，如期权、VIX期货等',
            'TAIL_RISK_METRICS_EXTENSION': '尾部风险度量扩展模块，负责计算VaR、CVaR等尾部风险指标',
            'TAX_LOSS_HARVESTING': '税务损失收割模块，负责识别和实施税务优化策略，降低税负',
            'TRADING_COST_OPTIMIZATION': '交易成本优化模块，负责最小化交易成本，包括佣金、价差、市场冲击等',
            'TRADING_SIGNAL_VALIDATOR': '交易信号验证器，负责验证交易信号的有效性，过滤虚假信号',
            'TRANSACTION_COST_ANALYSIS_ENGINE': '交易成本分析引擎，负责分析交易成本的构成，优化执行策略',
            'TRANSACTION_COST_AWARE_REBALANCING': '交易成本感知再平衡模块，负责在再平衡决策中考虑交易成本',
            'TURNOVER_CONTROL': '换手率控制模块，负责控制投资组合换手率，平衡交易成本和策略收益',
            'UNIFIED_DATA_INFRASTRUCTURE': '统一数据基础设施，负责建立统一的数据平台，支持数据共享和治理',
            'VAR_ES_MONITORING': 'VaR/ES监控系统，负责实时监控投资组合的风险价值和预期损失',
            'ALGORITHMIC_TRADING_OPTIMIZER': '算法交易优化器，负责优化算法交易策略参数，提升执行效率',
            'BARRA_RISK_MODEL': 'Barra风险模型，负责实施多因子风险模型，支持风险分解和对冲',
            'MODULE_RESPONSIBILITY_BOUNDARIES': '模块职责边界定义，负责明确各模块的职责范围和接口规范',
            'MONITORING_DASHBOARD_ENHANCEMENT': '监控仪表板增强模块，负责提升系统监控的可视化和交互能力',
            'IMPLEMENTATION_PROGRESS_TRACKING': '实施进度跟踪模块，负责跟踪项目实施进度，管理里程碑',
            'MARKET_PARTICIPANT_SIMULATION_INTEGRATION': '市场参与者模拟集成模块，负责模拟不同市场参与者的行为',
            'DATA_CATALOG_METADATA': '数据目录元数据管理模块，负责管理数据资产的元数据信息',
            'DATA_COST_MANAGEMENT': '数据成本管理模块，负责优化数据采购和使用成本',
            'DATA_FABRIC': '数据编织架构，负责建立统一的数据访问层，支持跨平台数据整合',
            'DATA_GOVERNANCE_PLATFORM': '数据治理平台，负责实施数据治理策略，确保数据质量和合规性',
            'DATA_LIFECYCLE_MANAGEMENT': '数据生命周期管理模块，负责管理数据从创建到归档的全生命周期',
            'DATA_MESH': '数据网格架构，负责实施数据网格模式，支持分布式数据管理',
            'DATA_OBSERVABILITY': '数据可观测性模块，负责监控数据流和数据质量，提供数据血缘追踪',
            'DATA_SECURITY_COMPLIANCE': '数据安全合规模块，负责确保数据处理符合安全规范和法规要求',
            'DATA_SOURCE_MANAGEMENT': '数据源管理模块，负责管理外部数据源的接入、配置和监控',
            'DATA_VERSION_CONTROL': '数据版本控制模块，负责管理数据集的版本，支持数据回溯',
            'DYNAMIC_ASSET_ALLOCATION': '动态资产配置模块，负责根据市场条件动态调整资产配置',
            'ENHANCED_ALERT_SYSTEM': '增强告警系统，负责实施多渠道、多级别的告警机制',
            'FACTOR_BACKTEST_INTEGRATION': '因子回测集成模块，负责集成因子回测框架，支持因子验证',
            'FACTOR_NEUTRAL_OPTIMIZATION': '因子中性优化模块，负责构建因子中性投资组合',
            'HIERARCHICAL_OPTIMIZATION_FRAMEWORK': '分层优化框架，负责实施多层级投资组合优化',
            'HIERARCHICAL_RISK_BUDGET': '分层风险预算模块，负责在多个层级分配风险预算',
            'HIGH_PERFORMANCE_DATA_PIPELINE': '高性能数据管道，负责构建低延迟、高吞吐的数据处理流水线',
            'LIQUIDITY_CONSTRAINED_OPTIMIZATION': '流动性约束优化模块，负责在流动性约束下优化投资组合',
            'AI_ENHANCEMENT_INTEGRATION': 'AI增强集成模块，负责将AI技术集成到交易系统中，提升策略智能化水平',
        }
        
        # 查找匹配的职责描述
        for key, value in responsibility_map.items():
            if key in filename:
                return value
        
        # 如果没有匹配，使用文件名生成通用描述
        return f'{filename.replace("_", " ").title()}模块，负责{filename.replace("_", " ").lower()}相关功能'
    
    def update_responsibility(self, content, responsibility):
        """更新职责描述"""
        # 查找并替换"核心定位"章节
        pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n##|\Z)'
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, f'\\1{responsibility}\n\n', content, flags=re.DOTALL)
            return new_content
        
        # 如果没有找到"核心定位"章节，在第一个##章节之前插入
        first_section_match = re.search(r'\n##\s+', content)
        if first_section_match:
            insert_pos = first_section_match.start()
            new_content = content[:insert_pos] + f'\n## 核心定位\n\n{responsibility}\n\n' + content[insert_pos:]
            return new_content
        
        return content

if __name__ == '__main__':
    fixer = ForceResponsibilityFixer()
    fixer.run()
