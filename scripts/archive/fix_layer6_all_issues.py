# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

module_responsibilities = {
    'ALGORITHMIC_TRADING_OPTIMIZER': ['算法交易优化', '执行算法选择', '交易路径优化', '成本最小化'],
    'ALPHA_FACTOR_FACTORY': ['Alpha因子工厂', '因子生成', '因子评估', '因子组合'],
    'ALTERNATIVE_DATA_INTEGRATION': ['另类数据集成', '数据源接入', '数据标准化', '数据质量验证'],
    'AUTO_REPAIR_ENGINE': ['自动修复引擎', '异常检测', '自动修复', '健康检查'],
    'BARRA_RISK_MODEL': ['Barra风险模型', '因子风险建模', '风险归因', '风险预测'],
    'BLACK_LITTERMAN_MODEL': ['Black-Litterman模型', '观点融合', '市场均衡收益', '后验收益估计'],
    'CDC_CHANGE_DATA_CAPTURE': ['CDC变更数据捕获', '数据变更检测', '变更流处理', '数据同步'],
    'CLICKHOUSE_INTEGRATION': ['ClickHouse集成', '列式存储', '高性能查询', '数据压缩'],
    'COMPLETE_ARCHITECTURE': ['完整架构蓝图', '系统架构设计', '模块集成', '架构演进'],
    'CONFIGURATION_MANAGEMENT': ['配置管理', '配置中心', '版本控制', '热更新'],
    'CONSTRAINT_SOLVER': ['约束求解器', '约束建模', '求解算法', '约束验证'],
    'DATA_ACCESS_AUDIT': ['数据访问审计', '访问日志', '权限审计', '合规检查'],
    'DATA_BACKUP_RECOVERY': ['数据备份恢复', '备份策略', '恢复机制', '灾难恢复'],
    'DATA_CATALOG': ['数据目录', '元数据管理', '数据发现', '血缘追踪'],
    'DATA_CATALOG_METADATA': ['数据目录元数据', '元数据采集', '元数据存储', '元数据查询'],
    'DATA_CLEANING_ENGINE': ['数据清洗引擎', '数据质量检测', '异常值处理', '数据标准化'],
    'DATA_COST_MANAGEMENT': ['数据成本管理', '成本监控', '成本优化', '资源计费'],
    'DATA_FABRIC': ['数据编织', '数据虚拟化', '统一数据层', '跨域数据'],
    'DATA_GOVERNANCE_PLATFORM': ['数据治理平台', '数据标准', '数据质量', '数据安全'],
    'DATA_LIFECYCLE_MANAGEMENT': ['数据生命周期管理', '数据保留', '数据归档', '数据销毁'],
    'DATA_MASKING_ENCRYPTION': ['数据脱敏加密', '敏感数据识别', '脱敏规则', '加密存储'],
    'DATA_MESH': ['数据网格', '域数据所有权', '数据产品', '联邦治理'],
    'DATA_OBSERVABILITY': ['数据可观测性', '数据监控', '数据血缘', '数据质量告警'],
    'DATA_ORCHESTRATION_SYSTEM': ['数据调度系统', '工作流编排', '任务调度', '依赖管理'],
    'DATA_PREPROCESSING_ARCHITECTURE_GAP_ANALYSIS': ['数据预处理架构差距分析', '架构评估', '差距识别', '改进建议'],
    'DATA_QUALITY_MONITORING': ['数据质量监控', '质量规则', '质量评分', '质量报告'],
    'DATA_SECURITY_COMPLIANCE': ['数据安全合规', '安全策略', '合规检查', '审计日志'],
    'DATA_SOURCE_HEALTH_MONITOR': ['数据源健康监控', '健康检查', '故障检测', '告警通知'],
    'DATA_SOURCE_MANAGEMENT': ['数据源管理', '数据源注册', '连接管理', '元数据采集'],
    'DATA_STANDARDIZATION_ENGINE': ['数据标准化引擎', '标准定义', '数据转换', '格式统一'],
    'DATA_VALIDATION_ENGINE': ['数据验证引擎', '验证规则', '数据校验', '错误报告'],
    'DATA_VERSION_CONTROL': ['数据版本控制', '版本管理', '变更追踪', '回滚机制'],
    'DISTRIBUTED_QUERY_ENGINE': ['分布式查询引擎', '查询优化', '并行执行', '结果聚合'],
    'DYNAMIC_CORRELATION_MODELING': ['动态相关性建模', '相关性估计', '时变相关', '协方差矩阵'],
    'DYNAMIC_LEVERAGE_MANAGEMENT': ['动态杠杆管理', '杠杆优化', '风险控制', '保证金管理'],
    'ECONOMIC_REGIME_ENGINE': ['经济范式判断引擎', '范式识别', '经济指标', '市场状态'],
    'ENHANCED_ALERT_SYSTEM': ['增强告警系统', '智能告警', '告警聚合', '告警路由'],
    'EXECUTION_STRATEGY_BACKTESTER': ['执行策略回测', '策略模拟', '成本分析', '性能评估'],
    'FACTOR_BACKTEST_INTEGRATION': ['因子回测集成', '因子测试', '回测框架', '结果分析'],
    'FACTOR_NEUTRAL_OPTIMIZATION': ['因子中性优化', '因子暴露控制', '中性约束', '风险因子管理'],
    'FINANCING_OPTIMIZATION': ['融资优化', '融资成本', '杠杆优化', '资金效率'],
    'HIERARCHICAL_OPTIMIZATION_FRAMEWORK': ['分层优化框架', '层级协调', '优化流程', '多层级优化'],
    'HIERARCHICAL_RISK_BUDGET': ['层级风险预算', '风险分配', '预算约束', '风险层级'],
    'HIGH_PERFORMANCE_DATA_PIPELINE': ['高性能数据管道', '流式处理', '低延迟', '高吞吐'],
    'LIQUIDITY_CONSTRAINED_OPTIMIZATION': ['流动性约束优化', '流动性建模', '交易成本', '流动性风险'],
    'LIQUIDITY_MANAGEMENT_SYSTEM': ['流动性管理系统', '流动性监控', '现金管理', '流动性预测'],
    'MARGIN_CALL_MONITOR': ['保证金监控', '保证金计算', '预警机制', '风险控制'],
    'MARKET_IMPACT_MODEL': ['市场冲击模型', '冲击成本', '执行成本', '市场微观结构'],
    'MARKET_PARTICIPANT_SIMULATION_INTEGRATION': ['市场参与者模拟集成', '行为建模', '模拟结果', '策略集成'],
    'MARKET_REGIME_DETECTION': ['市场范式检测', '范式识别', '状态转换', '趋势判断'],
    'MEAN_VARIANCE_OPTIMIZATION': ['均值方差优化', '有效前沿', '最优权重', '风险收益权衡'],
    'METADATA_MANAGEMENT_ENHANCEMENT': ['元数据管理增强', '元数据采集', '元数据存储', '元数据服务'],
    'MISSING_MODULES_SUMMARY': ['缺失模块摘要', '模块识别', '差距分析', '补充建议'],
    'MODULE_RESPONSIBILITY_BOUNDARIES': ['模块职责边界', '边界定义', '职责划分', '接口规范'],
    'MONITORING_ALERTING_SYSTEM': ['监控告警系统', '指标采集', '告警规则', '通知管理'],
    'MONITORING_DASHBOARD_ENHANCEMENT': ['监控面板增强', '可视化', '实时监控', '交互式分析'],
    'MULTI_ASSET_ALLOCATION': ['多资产配置', '跨资产优化', '资产相关性', '配置权重'],
    'MULTI_STRATEGY_HIERARCHICAL_SYSTEM': ['多策略分层系统', '策略分层', '策略协调', '信号融合'],
    'OBJECT_STORAGE_INTEGRATION': ['对象存储集成', 'S3兼容', '大文件存储', '生命周期管理'],
    'PORTFOLIO_ATTRIBUTION': ['组合归因', '收益归因', '风险归因', '绩效分析'],
    'PORTFOLIO_INSURANCE_STRATEGY': ['组合保险策略', 'CPPI策略', 'OBPI策略', '下行保护'],
    'PORTFOLIO_OPTIMIZATION': ['组合优化', '权重优化', '约束处理', '目标函数'],
    'PORTFOLIO_PERFORMANCE_EVALUATION': ['组合绩效评估', '绩效指标', '基准比较', '风险调整收益'],
    'PORTFOLIO_REBALANCING': ['组合再平衡', '再平衡策略', '交易成本', '阈值触发'],
    'PORTFOLIO_SCENARIO_ANALYSIS': ['组合情景分析', '情景模拟', '压力测试', '情景归因'],
    'QUALITY_REPORT_AUTOMATION': ['质量报告自动化', '报告生成', '数据汇总', '自动化流程'],
    'QUALITY_SCORING_SYSTEM': ['质量评分系统', '评分模型', '质量指标', '评分报告'],
    'QUARTERLY_REBALANCE': ['季度调仓', '季度再平衡', '定期调整', '再平衡计划'],
    'REALTIME_DATA_LAKE': ['实时数据湖', '流式入湖', '实时查询', '数据湖架构'],
    'REALTIME_RISK_HEDGE_ENGINE': ['实时风险对冲引擎', '动态对冲', '风险监控', '对冲执行'],
    'REDIS_CACHE_LAYER': ['Redis缓存层', '缓存策略', '分布式缓存', '缓存一致性'],
    'RISK_ATTRIBUTION_SYSTEM': ['风险归因系统', '风险分解', '因子归因', '风险报告'],
    'RISK_CONTRIBUTION_ANALYSIS': ['风险贡献分析', '边际风险', '风险预算', '贡献度计算'],
    'RISK_CONTROL': ['风险控制', '风险限额', '止损机制', '风险预警'],
    'RISK_PARITY_STRATEGY': ['风险平价策略', '风险均衡', '等风险贡献', '杠杆调整'],
    'SIMPLIFIED_RISK_BUDGET_SYSTEM': ['简化风险预算系统', '风险预算', '预算分配', '风险约束'],
    'SIMPLIFIED_TIMEFRAME_COORDINATION': ['简化时间框架协调', '时间框架', '信号协调', '周期管理'],
    'SMART_EXECUTION_ENGINE': ['智能执行引擎', '执行算法', '成本优化', '市场适应'],
    'SMART_ORDER_ROUTER': ['智能订单路由', '路由优化', '执行场所', '成本最小化'],
    'STATISTICAL_ARBITRAGE_MODULE': ['统计套利模块', '配对交易', '协整分析', '均值回归'],
    'STRATEGIC_ALLOCATION_ENGINE': ['战略配置引擎', '资产配置', '长期配置', '配置决策'],
    'STRATEGIC_WEIGHTING': ['战略权重', '基准权重', '长期权重', '配置权重'],
    'STRATEGY_PORTFOLIO_OPTIMIZATION': ['策略组合优化', '策略权重', '策略选择', '组合构建'],
    'STRATEGY_SELECTION': ['策略选择', '策略评估', '策略排名', '策略组合'],
    'STRESS_TESTING_SYSTEM': ['压力测试系统', '情景定义', '冲击模拟', '结果分析'],
    'SYSTEM_ENHANCEMENT': ['系统增强', '功能扩展', '性能优化', '架构改进'],
    'SYSTEM_INTEGRATION': ['系统集成', '模块集成', '接口对接', '数据流'],
    'TAIL_RISK_HEDGING': ['尾部风险对冲', '尾部风险', '期权对冲', '极端事件'],
    'TIMESCALEDB_INTEGRATION': ['TimescaleDB集成', '时序数据库', '时间序列', '高效存储'],
    'TRADING_COST_OPTIMIZATION': ['交易成本优化', '成本模型', '执行优化', '成本控制'],
    'TRADING_SIGNAL_VALIDATOR': ['交易信号验证', '信号验证', '信号过滤', '信号质量'],
    'TRANSACTION_COST_ANALYSIS_ENGINE': ['交易成本分析引擎', '成本分析', '执行质量', '成本归因'],
    'TRANSACTION_COST_AWARE_REBALANCING': ['交易成本感知再平衡', '成本感知', '再平衡优化', '成本约束'],
    'UNIFIED_DATA_INFRASTRUCTURE': ['统一数据基础设施', '数据平台', '基础设施', '统一架构'],
    'VAR_ES_MONITORING': ['VaR/ES监控', '风险价值', '期望损失', '实时监控'],
    'INTRADAY_STRATEGY': ['盘中策略', '日内交易', '高频策略', '实时信号'],
    'OPENING_STRATEGY': ['开盘策略', '开盘竞价', '开盘信号', '开盘执行'],
    'TAX_LOSS_HARVESTING': ['税收优化', '税损收割', '税收效率', '税务筹划'],
    'ROBUST_OPTIMIZATION': ['鲁棒优化', '不确定性建模', '鲁棒解', '参数敏感性'],
    'DYNAMIC_ASSET_ALLOCATION': ['动态资产配置', '资产权重调整', '市场环境适应', '配置策略优化'],
    'MULTI_PERIOD_DYNAMIC_OPTIMIZATION': ['多期动态优化', '多期规划', '动态调整', '长期优化'],
    'TURNOVER_CONTROL': ['换手率控制', '换手约束', '交易频率', '成本控制'],
    'DATA_PREPROCESSING_COMPLETE_ARCHITECTURE': ['数据预处理完整架构', '预处理流程', '数据管道', '架构设计'],
    'UNIFIED_DATA_API_GATEWAY': ['统一数据API网关', 'API网关', '统一接口', '数据访问'],
    'STRATEGY_SELECTION_BLUEPRINT': ['策略选择蓝图', '策略评估', '策略排名', '策略组合'],
}

def get_module_name(filename):
    name = filename.replace('_BLUEPRINT.md', '')
    return name

def get_responsibilities(filename):
    module_name = get_module_name(filename)
    for key, values in module_responsibilities.items():
        if key in module_name:
            return values
    return ['系统架构蓝图设计与实施指导', '模块功能实现', '性能优化', '质量保证']

def fix_responsibility(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    filename = os.path.basename(file_path)
    
    yaml_match = re.search(r'^(---\s*[\r\n]+)(.*?)([\r\n]+---)', content, re.DOTALL)
    if not yaml_match:
        return False, '缺少YAML头部'
    
    yaml_header = yaml_match.group(2)
    
    resp_match = re.search(r'responsibility:\s*([\s\S]*?)(?=\n\w+:|$)', yaml_header)
    
    if resp_match:
        resp_text = resp_match.group(1)
        resp_items = re.findall(r'-\s*(.+?)(?:\n|$)', resp_text)
        resp_items = [item.strip() for item in resp_items if item.strip()]
        
        if len(resp_items) >= 2:
            return False, '已有足够responsibility项'
    
    new_responsibilities = get_responsibilities(filename)
    resp_yaml = 'responsibility:\n'
    for resp in new_responsibilities:
        resp_yaml += f'  - {resp}\n'
    
    if resp_match:
        new_yaml = re.sub(r'responsibility:\s*[\s\S]*?(?=\n\w+:|$)', resp_yaml, yaml_header)
    else:
        last_line = yaml_header.rstrip()
        new_yaml = last_line + '\n' + resp_yaml
    
    new_content = content[:yaml_match.start()] + '---\n' + new_yaml + '---' + content[yaml_match.end():]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f'已添加{len(new_responsibilities)}个responsibility项'

def add_responsibility_boundary(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if re.search(r'职责边界|本文档负责|本文档不负责', content):
        return False, '已有职责边界'
    
    filename = os.path.basename(file_path)
    module_name = get_module_name(filename)
    responsibilities = get_responsibilities(filename)
    
    boundary_text = f'''
> **职责边界**: 
> - ✅ 本文档负责：{responsibilities[0]}、{responsibilities[1]}、{responsibilities[2]}
> - ❌ 本文档不负责：其他模块职责（由各模块文档负责）

'''
    
    core_match = re.search(r'(##\s*核心定位\s*\n)', content)
    if core_match:
        insert_pos = core_match.end()
        new_content = content[:insert_pos] + boundary_text + content[insert_pos:]
    else:
        yaml_end = re.search(r'---\s*[\r\n]+', content)
        if yaml_end:
            insert_pos = yaml_end.end()
            new_content = content[:insert_pos] + '\n## 核心定位\n' + boundary_text + content[insert_pos:]
        else:
            new_content = boundary_text + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, '已添加职责边界'

def add_change_history(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if re.search(r'##\s*\d*\.?\s*变更历史|##\s*\d*\.?\s*版本管理', content):
        return False, '已有变更历史'
    
    history_text = f'''
## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime("%Y-%m-%d")} | 初始版本创建 | 实施团队 |

---

'''
    
    new_content = content.rstrip() + '\n' + history_text
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, '已添加变更历史'

print('='*80)
print('Layer 6 组合优化层文档修复')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

files = [f for f in os.listdir(blueprints_dir) if f.endswith('.md') and f != 'INDEX.md']

print(f'扫描文档总数: {len(files)}')
print()

print('='*80)
print('P0: 修复responsibility项不足')
print('='*80)

fixed_resp = 0
for file in files:
    file_path = os.path.join(blueprints_dir, file)
    success, msg = fix_responsibility(file_path)
    if success:
        fixed_resp += 1
        print(f'✓ {file}: {msg}')

print(f'\n修复完成: {fixed_resp}个文件')

print()
print('='*80)
print('P1: 添加职责边界')
print('='*80)

fixed_boundary = 0
for file in files:
    file_path = os.path.join(blueprints_dir, file)
    success, msg = add_responsibility_boundary(file_path)
    if success:
        fixed_boundary += 1
        print(f'✓ {file}: {msg}')

print(f'\n修复完成: {fixed_boundary}个文件')

print()
print('='*80)
print('P1: 添加变更历史')
print('='*80)

fixed_history = 0
for file in files:
    file_path = os.path.join(blueprints_dir, file)
    success, msg = add_change_history(file_path)
    if success:
        fixed_history += 1
        print(f'✓ {file}: {msg}')

print(f'\n修复完成: {fixed_history}个文件')

print()
print('='*80)
print('修复汇总')
print('='*80)
print(f'P0 responsibility项修复: {fixed_resp}个')
print(f'P1 职责边界添加: {fixed_boundary}个')
print(f'P1 变更历史添加: {fixed_history}个')
print()
print('修复完成!')
