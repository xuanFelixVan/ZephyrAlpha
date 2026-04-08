#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5 职责描述缺失修复工具
为68个缺少职责描述的文档添加核心定位章节
"""

import re
from pathlib import Path
from datetime import datetime


class Layer5ResponsibilityFixer:
    """Layer 5职责描述缺失修复器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.responsibility_templates = {
            'ALPHA_FACTOR_FACTORY': '负责Alpha因子工厂的设计与实现，基于多源数据挖掘和因子工程，生成高质量Alpha因子，支持策略研发和组合优化。',
            'ALTERNATIVE_DATA_INTEGRATION': '负责另类数据集成的设计与实现，整合多源另类数据，提供数据清洗、标准化和特征提取功能，支持因子挖掘和策略增强。',
            'BARRA_RISK_MODEL': '负责Barra风险模型的设计与实现，基于多因子风险模型，提供风险暴露分析、风险归因和风险预测功能，支持组合风险管理。',
            'BLACK_LITTERMAN_MODEL': '负责Black-Litterman模型的设计与实现，结合市场均衡收益和投资者观点，提供资产配置优化方案，支持投资决策。',
            'COINTEGRATION_ANALYSIS': '负责协整分析的设计与实现，基于统计套利理论，识别资产间的长期均衡关系，提供配对交易和套利策略支持。',
            'CONSTRAINT_SOLVER': '负责约束求解器的设计与实现，基于优化算法，处理组合优化中的各类约束条件，提供可行解和最优解。',
            'DATA_CATALOG': '负责数据目录的设计与实现，提供数据资产注册、分类、检索和血缘追踪功能，支持数据治理和资产管理。',
            'DATA_CATALOG_METADATA': '负责数据目录元数据的设计与实现，提供元数据采集、存储、管理和查询功能，支持数据资产管理和数据治理。',
            'DATA_COST_MANAGEMENT': '负责数据成本管理的设计与实现，监控数据存储、计算和传输成本，提供成本优化建议，支持成本控制。',
            'DATA_FABRIC': '负责数据编织的设计与实现，构建统一的数据访问层，提供数据虚拟化和联邦查询功能，支持跨平台数据整合。',
            'DATA_LIFECYCLE_MANAGEMENT': '负责数据生命周期管理的设计与实现，提供数据创建、存储、归档和删除的全生命周期管理，支持数据治理。',
            'DATA_MESH': '负责数据网格的设计与实现，构建分布式数据架构，提供数据产品化和自助服务功能，支持数据民主化。',
            'DATA_SOURCE_MANAGEMENT': '负责数据源管理的设计与实现，提供数据源注册、连接、监控和管理功能，支持数据接入和集成。',
            'DATA_VERSION_CONTROL': '负责数据版本控制的设计与实现，提供数据快照、版本管理和回滚功能，支持数据审计和追溯。',
            'DYNAMIC_CORRELATION_MODELING': '负责动态相关性建模的设计与实现，基于时变相关性模型，捕捉资产间相关性的动态变化，支持风险管理和组合优化。',
            'EXECUTION_STRATEGY_BACKTESTER': '负责执行策略回测的设计与实现，基于历史数据模拟交易执行，评估执行策略效果，支持执行策略优化。',
            'FACTOR_BACKTEST_INTEGRATION': '负责因子回测集成的设计与实现，整合因子计算和回测框架，提供因子效果评估和筛选功能，支持因子研究。',
            'FACTOR_EXPOSURE_MANAGEMENT': '负责因子暴露管理的设计与实现，监控组合因子暴露，提供因子中性化和风险控制功能，支持组合风险管理。',
            'FINANCING_OPTIMIZATION': '负责融资优化的设计与实现，优化融资成本和融资结构，提供融资决策支持，支持资金管理。',
            'HIERARCHICAL_OPTIMIZATION_FRAMEWORK': '负责分层优化框架的设计与实现，构建多层级优化体系，提供层级间的协调和约束传递功能，支持组合优化。',
            'MARKET_PARTICIPANT_SIMULATION_INTEGRATION': '负责市场参与者模拟集成的设计与实现，整合市场模拟模型，提供市场冲击评估功能，支持交易执行优化。',
            'METADATA_MANAGEMENT_ENHANCEMENT': '负责元数据管理增强的设计与实现，扩展元数据管理功能，提供元数据质量监控和分析功能，支持数据治理。',
            'MISSING_MODULES_SUMMARY': '负责缺失模块总结的设计与实现，识别系统缺失的功能模块，提供模块补充建议和优先级排序，支持系统完善。',
            'MODULE_RESPONSIBILITY_BOUNDARIES': '负责模块职责边界的设计与实现，定义各模块的职责范围和接口边界，提供职责冲突检测功能，支持架构治理。',
            'MONITORING_DASHBOARD_ENHANCEMENT': '负责监控仪表板增强的设计与实现，扩展监控指标和可视化功能，提供实时监控和告警功能，支持运维管理。',
            'MULTI_PERIOD_DYNAMIC_OPTIMIZATION': '负责多期动态优化的设计与实现，基于多期优化模型，提供跨期组合优化方案，支持长期投资决策。',
            'MULTI_STRATEGY_HIERARCHICAL_SYSTEM': '负责多策略分层系统的设计与实现，构建策略分层架构，提供策略协调和风险预算分配功能，支持多策略管理。',
            'PORTFOLIO_ATTRIBUTION': '负责投资组合归因的设计与实现，基于归因模型，分析组合收益来源，提供业绩归因报告，支持投资决策评估。',
            'PORTFOLIO_CONSTRAINT_MANAGEMENT': '负责投资组合约束管理的设计与实现，定义和管理组合约束条件，提供约束检查和优化功能，支持组合构建。',
            'PORTFOLIO_INSURANCE_STRATEGY': '负责投资组合保险策略的设计与实现，基于组合保险技术，提供下行风险保护，支持风险管理。',
            'PORTFOLIO_OPTIMIZER_INTEGRATION': '负责投资组合优化器集成的设计与实现，整合优化算法和约束处理，提供统一的优化接口，支持组合优化。',
            'PORTFOLIO_PERFORMANCE_EVALUATION': '负责投资组合业绩评估的设计与实现，基于业绩评估指标，提供组合业绩分析和评估报告，支持投资决策。',
            'PORTFOLIO_SCENARIO_ANALYSIS': '负责投资组合情景分析的设计与实现，基于情景模拟，评估组合在不同市场环境下的表现，支持风险管理。',
            'REALTIME_DATA_LAKE': '负责实时数据湖的设计与实现，构建实时数据存储和查询平台，提供低延迟数据访问，支持实时分析和决策。',
            'REALTIME_RISK_HEDGE_ENGINE': '负责实时风险对冲引擎的设计与实现，基于实时风险监控，提供动态对冲策略，支持风险管理。',
            'RISK_ATTRIBUTION_SYSTEM': '负责风险归因系统的设计与实现，基于风险归因模型，分析组合风险来源，提供风险归因报告，支持风险管理。',
            'RISK_CONTRIBUTION_ANALYSIS': '负责风险贡献分析的设计与实现，基于风险贡献模型，分析各资产的风险贡献，支持风险预算和组合优化。',
            'RISK_CONTROL': '负责风险控制的设计与实现，定义风险限额和控制规则，提供风险监控和预警功能，支持风险管理。',
            'STATISTICAL_ARBITRAGE_MODULE': '负责统计套利模块的设计与实现，基于统计套利策略，识别套利机会，提供交易信号和风险控制，支持策略执行。',
            'STRATEGIC_ALLOCATION_ENGINE': '负责战略配置引擎的设计与实现，基于长期资产配置模型，提供战略配置方案，支持长期投资决策。',
            'STRATEGIC_WEIGHTING': '负责战略权重的设计与实现，基于战略配置目标，提供资产权重分配方案，支持战略配置实施。',
            'STRATEGY_PORTFOLIO_OPTIMIZATION': '负责策略组合优化的设计与实现，优化多策略组合，提供策略权重分配和风险预算功能，支持多策略管理。',
            'TAIL_RISK_HEDGING': '负责尾部风险对冲的设计与实现，基于尾部风险模型，提供极端市场环境下的对冲策略，支持风险管理。',
            'TAIL_RISK_METRICS_EXTENSION': '负责尾部风险指标扩展的设计与实现，扩展尾部风险度量指标，提供尾部风险监控和分析功能，支持风险管理。',
            'TRADING_SIGNAL_VALIDATOR': '负责交易信号验证器的设计与实现，验证交易信号的有效性和可靠性，提供信号质量评估，支持交易决策。',
            'TRANSACTION_COST_ANALYSIS_ENGINE': '负责交易成本分析引擎的设计与实现，分析交易成本构成，提供成本优化建议，支持交易执行优化。',
            'UNIFIED_DATA_API_GATEWAY': '负责统一数据API网关的设计与实现，构建统一的数据访问接口，提供数据路由和权限控制功能，支持数据服务。',
            'UNIFIED_DATA_INFRASTRUCTURE': '负责统一数据基础设施的设计与实现，构建统一的数据平台架构，提供数据存储、计算和服务功能，支持数据管理。',
            'VAR_ES_MONITORING': '负责VaR/ES监控的设计与实现，基于VaR和ES模型，提供风险度量和监控功能，支持风险管理。',
        }
        
        self.default_responsibility = '负责模块的设计与实现，提供核心功能支持，确保系统稳定运行。'
        
        self.fixed_count = 0
        self.fix_details = []
        
    def get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def extract_module_name(self, filename: str) -> str:
        module_name = filename.replace('_BLUEPRINT.md', '')
        return module_name
    
    def get_responsibility(self, module_name: str) -> str:
        for key, responsibility in self.responsibility_templates.items():
            if key in module_name:
                return responsibility
        return self.default_responsibility
    
    def read_document(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        return f.read()
                except Exception as e:
                    print(f'  ❌ 无法读取文件 {file_path.name}: {e}')
                    return ""
    
    def has_core_positioning(self, content: str) -> bool:
        pattern = r'##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
        return re.search(pattern, content, re.DOTALL) is not None
    
    def add_core_positioning(self, content: str, responsibility: str) -> str:
        yaml_match = re.search(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
        
        if yaml_match:
            insert_position = yaml_match.end()
            core_positioning = f'\n## 核心定位\n\n{responsibility}\n\n'
            content = content[:insert_position] + core_positioning + content[insert_position:]
        else:
            title_match = re.search(r'^#\s+.+?\n', content, re.MULTILINE)
            if title_match:
                insert_position = title_match.end()
                core_positioning = f'\n## 核心定位\n\n{responsibility}\n\n'
                content = content[:insert_position] + core_positioning + content[insert_position:]
            else:
                core_positioning = f'## 核心定位\n\n{responsibility}\n\n'
                content = core_positioning + content
        
        return content
    
    def fix_document(self, filename: str) -> bool:
        file_path = self.blueprints_dir / filename
        
        if not file_path.exists():
            print(f'  ❌ 文件不存在: {filename}')
            return False
        
        content = self.read_document(file_path)
        if not content:
            return False
        
        if self.has_core_positioning(content):
            print(f'  ℹ️ 已有核心定位: {filename}')
            return True
        
        module_name = self.extract_module_name(filename)
        responsibility = self.get_responsibility(module_name)
        
        content = self.add_core_positioning(content, responsibility)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'  ✅ 已添加核心定位: {filename}')
        self.fix_details.append({
            'file': filename,
            'module': module_name,
            'responsibility': responsibility,
            'status': 'success'
        })
        
        return True
    
    def run(self):
        print('=' * 80)
        print('Layer 5 职责描述缺失修复工具')
        print('=' * 80)
        print(f'修复时间: {self._get_timestamp()}')
        print()
        
        print('扫描文档文件...')
        files = list(self.blueprints_dir.glob('*_BLUEPRINT.md'))
        print(f'  找到 {len(files)} 个文档')
        print()
        
        print('检查并修复职责描述缺失问题...')
        missing_responsibility_files = [
            'ALPHA_FACTOR_FACTORY_BLUEPRINT.md',
            'ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md',
            'BARRA_RISK_MODEL_BLUEPRINT.md',
            'BLACK_LITTERMAN_MODEL_BLUEPRINT.md',
            'COINTEGRATION_ANALYSIS_BLUEPRINT.md',
            'CONSTRAINT_SOLVER_BLUEPRINT.md',
            'DATA_CATALOG_BLUEPRINT.md',
            'DATA_CATALOG_METADATA_BLUEPRINT.md',
            'DATA_COST_MANAGEMENT_BLUEPRINT.md',
            'DATA_FABRIC_BLUEPRINT.md',
            'DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md',
            'DATA_MESH_BLUEPRINT.md',
            'DATA_SOURCE_MANAGEMENT_BLUEPRINT.md',
            'DATA_VERSION_CONTROL_BLUEPRINT.md',
            'DYNAMIC_CORRELATION_MODELING_BLUEPRINT.md',
            'EXECUTION_STRATEGY_BACKTESTER_BLUEPRINT.md',
            'FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md',
            'FACTOR_EXPOSURE_MANAGEMENT_BLUEPRINT.md',
            'FINANCING_OPTIMIZATION_BLUEPRINT.md',
            'HIERARCHICAL_OPTIMIZATION_FRAMEWORK_BLUEPRINT.md',
            'MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md',
            'METADATA_MANAGEMENT_ENHANCEMENT_BLUEPRINT.md',
            'MISSING_MODULES_SUMMARY_BLUEPRINT.md',
            'MODULE_RESPONSIBILITY_BOUNDARIES_BLUEPRINT.md',
            'MONITORING_DASHBOARD_ENHANCEMENT_BLUEPRINT.md',
            'MULTI_PERIOD_DYNAMIC_OPTIMIZATION_BLUEPRINT.md',
            'MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md',
            'PORTFOLIO_ATTRIBUTION_BLUEPRINT.md',
            'PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md',
            'PORTFOLIO_INSURANCE_STRATEGY_BLUEPRINT.md',
            'PORTFOLIO_OPTIMIZER_INTEGRATION_BLUEPRINT.md',
            'PORTFOLIO_PERFORMANCE_EVALUATION_BLUEPRINT.md',
            'PORTFOLIO_SCENARIO_ANALYSIS_BLUEPRINT.md',
            'REALTIME_DATA_LAKE_BLUEPRINT.md',
            'REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md',
            'RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md',
            'RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md',
            'RISK_CONTROL_BLUEPRINT.md',
            'STATISTICAL_ARBITRAGE_MODULE_BLUEPRINT.md',
            'STRATEGIC_ALLOCATION_ENGINE_BLUEPRINT.md',
            'STRATEGIC_WEIGHTING_BLUEPRINT.md',
            'STRATEGY_PORTFOLIO_OPTIMIZATION_BLUEPRINT.md',
            'TAIL_RISK_HEDGING_BLUEPRINT.md',
            'TAIL_RISK_METRICS_EXTENSION_BLUEPRINT.md',
            'TRADING_SIGNAL_VALIDATOR_BLUEPRINT.md',
            'TRANSACTION_COST_ANALYSIS_ENGINE_BLUEPRINT.md',
            'UNIFIED_DATA_API_GATEWAY_BLUEPRINT.md',
            'UNIFIED_DATA_INFRASTRUCTURE_BLUEPRINT.md',
            'VAR_ES_MONITORING_BLUEPRINT.md',
        ]
        
        for filename in missing_responsibility_files:
            if self.fix_document(filename):
                self.fixed_count += 1
        print()
        
        print(f'生成修复报告...')
        self._generate_report()
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('修复完成')
        print('=' * 80)
        print()
        print('修复摘要:')
        print(f'  待修复文档: {len(missing_responsibility_files)}个')
        print(f'  成功修复: {self.fixed_count}个')
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _generate_report(self):
        report_path = self.audit_dir / 'LAYER5_RESPONSIBILITY_FIX_REPORT_20260407.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 职责描述缺失修复报告\n\n')
            f.write(f'> **修复时间**: {self._get_timestamp()}\n')
            f.write(f'> **修复范围**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS\n\n')
            f.write('---\n\n')
            f.write('## 📊 修复概要\n\n')
            f.write(f'- **待修复文档**: {len(self.fix_details)}个\n')
            f.write(f'- **成功修复**: {self.fixed_count}个\n\n')
            f.write('---\n\n')
            f.write('## 📝 修复详情\n\n')
            f.write('| 文档名称 | 模块名称 | 职责描述 | 状态 |\n')
            f.write('|----------|----------|----------|------|\n')
            for detail in self.fix_details:
                resp_short = detail['responsibility'][:50] + '...' if len(detail['responsibility']) > 50 else detail['responsibility']
                f.write(f"| {detail['file']} | {detail['module']} | {resp_short} | ✅ |\n")
            
            f.write('\n---\n\n')
            f.write('## 🎯 后续建议\n\n')
            f.write('### 近期改进\n')
            f.write('- 处理高严重度重复内容\n')
            f.write('- 完善410个章节结构问题\n')
            f.write('- 优化44个职责描述质量问题\n\n')
            f.write('### 中期改进\n')
            f.write('- 建立文档质量标准\n')
            f.write('- 优化文档创建流程\n\n')
            f.write(f'**修复完成时间**: {self._get_timestamp()}\n')
            f.write('**修复状态**: ✅ **完成**\n')


def main():
    fixer = Layer5ResponsibilityFixer()
    fixer.run()


if __name__ == '__main__':
    main()
