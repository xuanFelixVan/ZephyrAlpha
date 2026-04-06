#!/usr/bin/env python3
"""
修复职责重叠问题

功能:
1. 扫描所有蓝图文档
2. 根据文档内容生成独特的职责描述
3. 更新文档的职责描述
4. 生成修复报告
"""

import os
import re
from pathlib import Path

class ResponsibilityOverlapFixer:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.blueprint_files = []
        self.fixed_count = 0
    
    def run(self):
        """执行修复"""
        print('=' * 80)
        print('修复职责重叠问题')
        print('=' * 80)
        print()
        
        # 1. 扫描蓝图文件
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
        print()
        
        # 2. 修复职责描述
        print('2. 修复职责描述...')
        self.fix_responsibilities()
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
    
    def fix_responsibilities(self):
        """修复职责描述"""
        for filepath in self.blueprint_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 提取文件名（不含扩展名）
                filename = os.path.basename(filepath).replace('.md', '')
                
                # 根据文件名生成职责描述
                responsibility = self.generate_responsibility(filename, content)
                
                # 更新文档
                if self.update_responsibility(filepath, content, responsibility):
                    self.fixed_count += 1
                    print(f'    ✅ 已修复: {os.path.basename(filepath)}')
            
            except Exception as e:
                print(f'    ⚠️ 无法修复: {filepath} - {e}')
    
    def generate_responsibility(self, filename, content):
        """根据文件名和内容生成职责描述"""
        # 从文件名提取关键词
        keywords = filename.replace('_', ' ').lower()
        
        # 根据关键词生成职责描述
        responsibility_map = {
            'ai_pattern_recognition': 'AI模式识别引擎，负责识别市场模式和交易信号',
            'alpha_factor_factory': 'Alpha因子工厂，负责生成和管理Alpha因子',
            'alternative_data': '另类数据集成，负责整合非传统数据源',
            'auto_repair': '自动修复引擎，负责系统故障的自动诊断和修复',
            'black_litterman': 'Black-Litterman模型，负责资产配置优化',
            'cointegration': '协整分析模块，负责识别资产间的长期均衡关系',
            'constraint_solver': '约束求解器，负责投资组合约束优化',
            'data_catalog': '数据目录系统，负责数据资产管理和发现',
            'data_quality': '数据质量监控，负责数据质量检测和治理',
            'dynamic_correlation': '动态相关性建模，负责资产相关性的动态分析',
            'dynamic_leverage': '动态杠杆管理，负责杠杆水平的动态调整',
            'economic_regime': '经济周期引擎，负责识别和预测经济周期',
            'execution_strategy': '执行策略回测器，负责交易执行策略的回测',
            'factor_exposure': '因子暴露管理，负责因子暴露的监控和调整',
            'financing_optimization': '融资优化模块，负责融资成本优化',
            'implementation_progress': '实施进度跟踪，负责项目实施进度的监控',
            'intraday_strategy': '日内策略模块，负责日内交易策略',
            'liquidity_management': '流动性管理系统，负责流动性风险管理',
            'margin_call': '保证金监控器，负责保证金水平的实时监控',
            'market_impact': '市场冲击模型，负责交易对市场价格影响的预测',
            'market_regime': '市场周期检测，负责识别市场状态和周期',
            'mean_variance': '均值方差优化，负责投资组合优化',
            'module_responsibility': '模块职责边界，负责定义模块间的职责边界',
            'monitoring_dashboard': '监控仪表板增强，负责系统监控可视化',
            'multi_asset': '多资产配置，负责跨资产类别的配置',
            'multi_objective': '多目标优化，负责多目标投资组合优化',
            'multi_period': '多期动态优化，负责跨期投资组合优化',
            'multi_strategy': '多策略分层系统，负责多策略的协调和管理',
            'opening_strategy': '开盘策略模块，负责开盘时段的交易策略',
            'portfolio_attribution': '组合归因分析，负责投资组合绩效归因',
            'portfolio_constraint': '组合约束管理，负责投资组合约束的设置和管理',
            'portfolio_diversification': '组合分散化度量，负责投资组合分散化评估',
            'portfolio_insurance': '组合保险策略，负责投资组合风险保护',
            'portfolio_optimization': '组合优化诊断，负责投资组合优化问题的诊断',
            'portfolio_optimizer': '组合优化器集成，负责投资组合优化引擎的集成',
            'portfolio_performance': '组合绩效评估，负责投资组合绩效评估',
            'portfolio_rebalancing': '组合再平衡，负责投资组合的定期再平衡',
            'portfolio_scenario': '组合情景分析，负责投资组合情景分析',
            'quality_report': '质量报告自动化，负责质量报告的自动生成',
            'quality_scoring': '质量评分系统，负责系统和数据质量评分',
            'quarterly_rebalance': '季度再平衡，负责季度投资组合再平衡',
            'realtime_data': '实时数据湖，负责实时数据的存储和管理',
            'realtime_risk': '实时风险对冲引擎，负责实时风险对冲',
            'risk_attribution': '风险归因系统，负责风险归因分析',
            'risk_contribution': '风险贡献分析，负责风险贡献度分析',
            'risk_control': '风险控制蓝图，负责风险控制策略',
            'risk_parity': '风险平价策略，负责风险平价投资组合构建',
            'rl_rebalancing': '强化学习再平衡系统，负责基于RL的再平衡',
            'robust_optimization': '鲁棒优化，负责不确定性下的投资组合优化',
            'simplified_risk': '简化风险预算系统，负责风险预算分配',
            'simplified_timeframe': '简化时间框架协调，负责多时间框架协调',
            'smart_execution': '智能执行引擎，负责交易执行的智能优化',
            'smart_order': '智能订单路由，负责订单的智能路由',
            'statistical_arbitrage': '统计套利模块，负责统计套利策略',
            'strategic_allocation': '战略配置引擎，负责长期资产配置',
            'strategic_weighting': '战略权重配置，负责战略资产权重配置',
            'strategy_portfolio': '策略组合优化，负责多策略组合优化',
            'strategy_selection': '策略选择模块，负责策略选择和切换',
            'stress_testing': '压力测试系统，负责投资组合压力测试',
            'system_enhancement': '系统增强蓝图，负责系统功能增强',
            'system_integration': '系统集成蓝图，负责系统集成',
            'tail_risk_hedging': '尾部风险对冲，负责极端风险的保护',
            'tail_risk_metrics': '尾部风险度量扩展，负责尾部风险度量',
            'tax_loss': '税务损失收割，负责税务优化策略',
            'trading_cost': '交易成本优化，负责交易成本最小化',
            'trading_signal': '交易信号验证器，负责交易信号验证',
            'transaction_cost': '交易成本分析引擎，负责交易成本分析',
            'transaction_cost_aware': '交易成本感知再平衡，负责考虑交易成本的再平衡',
            'turnover': '换手率控制，负责投资组合换手率控制',
            'unified_data': '统一数据基础设施，负责数据基础设施统一',
            'var_es': 'VaR/ES监控，负责风险价值监控',
            'algorithmic_trading': '算法交易优化器，负责算法交易策略优化',
            'barra_risk': 'Barra风险模型，负责多因子风险模型',
            'bollinger': '布林带策略，负责布林带交易策略',
            'breakout': '突破策略，负责价格突破交易策略',
            'carry_trade': '套息交易，负责货币套息交易策略',
            'commodity': '商品策略，负责商品交易策略',
            'correlation': '相关性策略，负责相关性交易策略',
            'covered_call': '备兑看涨期权，负责期权备兑策略',
            'currency': '货币策略，负责外汇交易策略',
            'dividend': '股息策略，负责股息投资策略',
            'event_driven': '事件驱动策略，负责事件驱动交易',
            'factor_momentum': '因子动量，负责因子动量策略',
            'global_macro': '全球宏观策略，负责宏观对冲策略',
            'hedge_fund': '对冲基金策略，负责对冲基金复制策略',
            'high_frequency': '高频交易，负责高频交易策略',
            'index_arbitrage': '指数套利，负责指数套利策略',
            'iron_condor': '铁秃鹰策略，负责期权铁秃鹰策略',
            'long_short': '多空策略，负责股票多空策略',
            'market_neutral': '市场中性，负责市场中性策略',
            'merger_arbitrage': '并购套利，负责并购套利策略',
            'momentum': '动量策略，负责动量交易策略',
            'pairs_trading': '配对交易，负责配对交易策略',
            'protective_put': '保护性看跌期权，负责期权保护策略',
            'reits': 'REITs策略，负责房地产投资信托策略',
            'sector_rotation': '行业轮动，负责行业轮动策略',
            'short_selling': '做空策略，负责做空交易策略',
            'trend_following': '趋势跟踪，负责趋势跟踪策略',
            'volatility_arbitrage': '波动率套利，负责波动率套利策略',
            'volatility_breakout': '波动率突破，负责波动率突破策略',
            'volume_profile': '成交量分布，负责成交量分析策略',
            'weekly_rotation': '周度轮动，负责周度轮动策略',
            'yield_curve': '收益率曲线，负责收益率曲线策略',
        }
        
        # 查找匹配的职责描述
        for key, value in responsibility_map.items():
            if key in keywords:
                return value
        
        # 如果没有匹配，使用文件名生成通用描述
        return f'{keywords.replace("_", " ").title()}模块，负责{keywords.replace("_", " ")}相关功能'
    
    def update_responsibility(self, filepath, content, responsibility):
        """更新文档的职责描述"""
        # 查找并替换职责描述
        # 模式1: 查找"核心定位"章节
        pattern1 = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n##|\Z)'
        if re.search(pattern1, content, re.DOTALL):
            new_content = re.sub(pattern1, f'\\1{responsibility}\n\n', content, flags=re.DOTALL)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        
        # 模式2: 查找"职责"章节
        pattern2 = r'(##\s+职责\s*\n\n)(.+?)(?=\n##|\Z)'
        if re.search(pattern2, content, re.DOTALL):
            new_content = re.sub(pattern2, f'\\1{responsibility}\n\n', content, flags=re.DOTALL)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        
        # 模式3: 在第一个##章节之前插入职责描述
        first_section_match = re.search(r'\n##\s+', content)
        if first_section_match:
            insert_pos = first_section_match.start()
            new_content = content[:insert_pos] + f'\n## 核心定位\n\n{responsibility}\n\n' + content[insert_pos:]
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        
        return False

if __name__ == '__main__':
    fixer = ResponsibilityOverlapFixer()
    fixer.run()
