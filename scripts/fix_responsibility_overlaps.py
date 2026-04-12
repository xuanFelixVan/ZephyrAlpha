# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re
from datetime import datetime

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

overlap_fixes = {
    'ALGORITHMIC_TRADING_OPTIMIZER_BLUEPRINT.md': {
        'old_resp': '成本最小化',
        'new_resp': '算法交易成本最小化',
        'boundary_note': '交易执行层面的成本优化（区别于订单路由的成本优化）'
    },
    'SMART_ORDER_ROUTER_BLUEPRINT.md': {
        'old_resp': '成本最小化',
        'new_resp': '订单路由成本最小化',
        'boundary_note': '订单路由层面的成本优化（区别于算法交易的成本优化）'
    },
    'AUTO_REPAIR_ENGINE_BLUEPRINT.md': {
        'old_resp': '健康检查',
        'new_resp': '系统健康检查与自动修复',
        'boundary_note': '系统级别的健康检查和自动修复（区别于数据源健康监控）'
    },
    'DATA_SOURCE_HEALTH_MONITOR_BLUEPRINT.md': {
        'old_resp': '健康检查',
        'new_resp': '数据源健康监控',
        'boundary_note': '数据源级别的健康监控（区别于系统健康检查）'
    },
    'BARRA_RISK_MODEL_BLUEPRINT.md': {
        'old_resp': '风险归因',
        'new_resp': 'Barra因子风险归因',
        'boundary_note': '基于Barra模型的风险归因（区别于组合绩效归因）'
    },
    'PORTFOLIO_ATTRIBUTION_BLUEPRINT.md': {
        'old_resp': '风险归因',
        'new_resp': '组合绩效风险归因',
        'boundary_note': '组合层面的绩效风险归因（区别于Barra模型风险归因）'
    },
    'COINTEGRATION_ANALYSIS_BLUEPRINT.md': {
        'old_resp': '性能优化',
        'new_resp': '协整分析性能优化',
        'boundary_note': '协整分析算法的性能优化（区别于系统整体性能优化）'
    },
    'SYSTEM_ENHANCEMENT_BLUEPRINT.md': {
        'old_resp': '性能优化',
        'new_resp': '系统整体性能优化',
        'boundary_note': '系统级别的性能优化（区别于具体算法的性能优化）'
    },
    'DATA_ACCESS_AUDIT_BLUEPRINT.md': {
        'old_resp': '合规检查',
        'new_resp': '数据访问合规审计',
        'boundary_note': '数据访问权限的合规审计（区别于数据安全合规）'
    },
    'DATA_SECURITY_COMPLIANCE_BLUEPRINT.md': {
        'old_resp': '合规检查',
        'new_resp': '数据安全合规检查',
        'boundary_note': '数据安全策略的合规检查（区别于数据访问审计）'
    },
    'DATA_COST_MANAGEMENT_BLUEPRINT.md': {
        'old_resp': '成本优化',
        'new_resp': '数据成本管理优化',
        'boundary_note': '数据资源成本的管理优化（区别于交易成本优化）'
    },
    'SMART_EXECUTION_ENGINE_BLUEPRINT.md': {
        'old_resp': '成本优化',
        'new_resp': '智能执行成本优化',
        'boundary_note': '交易执行层面的成本优化（区别于数据成本和交易成本分析）'
    },
    'TRANSACTION_COST_ANALYSIS_ENGINE_BLUEPRINT.md': {
        'old_resp': '成本优化',
        'new_resp': '交易成本分析优化',
        'boundary_note': '交易成本的分析和优化建议（区别于执行成本和数据成本）'
    },
    'DYNAMIC_LEVERAGE_MANAGEMENT_BLUEPRINT.md': {
        'old_resp': ['杠杆优化', '风险控制'],
        'new_resp': ['动态杠杆管理与风险控制', '杠杆风险监控'],
        'boundary_note': '杠杆层面的风险控制（区别于保证金监控和整体风险控制）'
    },
    'FINANCING_OPTIMIZATION_BLUEPRINT.md': {
        'old_resp': '杠杆优化',
        'new_resp': '融资杠杆成本优化',
        'boundary_note': '融资层面的杠杆成本优化（区别于动态杠杆管理）'
    },
    'MARGIN_CALL_MONITOR_BLUEPRINT.md': {
        'old_resp': '风险控制',
        'new_resp': '保证金风险控制',
        'boundary_note': '保证金层面的风险控制（区别于杠杆风险和整体风险）'
    },
    'RISK_CONTROL_BLUEPRINT.md': {
        'old_resp': '风险控制',
        'new_resp': '组合整体风险控制',
        'boundary_note': '组合层面的整体风险控制（区别于保证金和杠杆风险）'
    },
    'ECONOMIC_REGIME_ENGINE_BLUEPRINT.md': {
        'old_resp': '范式识别',
        'new_resp': '经济周期范式识别',
        'boundary_note': '宏观经济层面的范式识别（区别于市场范式检测）'
    },
    'MARKET_REGIME_DETECTION_BLUEPRINT.md': {
        'old_resp': '范式识别',
        'new_resp': '市场状态范式识别',
        'boundary_note': '市场微观结构层面的范式识别（区别于经济周期范式）'
    },
    'FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md': {
        'old_resp': '结果分析',
        'new_resp': '因子回测结果分析',
        'boundary_note': '因子层面的回测结果分析（区别于压力测试结果分析）'
    },
    'STRESS_TESTING_SYSTEM_BLUEPRINT.md': {
        'old_resp': '结果分析',
        'new_resp': '压力测试结果分析',
        'boundary_note': '压力测试层面的结果分析（区别于因子回测结果）'
    },
    'MONITORING_DASHBOARD_ENHANCEMENT_BLUEPRINT.md': {
        'old_resp': '实时监控',
        'new_resp': '监控面板实时展示',
        'boundary_note': '监控面板的实时展示（区别于VaR/ES实时监控）'
    },
    'VAR_ES_MONITORING_BLUEPRINT.md': {
        'old_resp': '实时监控',
        'new_resp': 'VaR/ES风险实时监控',
        'boundary_note': 'VaR/ES指标的实时监控（区别于监控面板展示）'
    },
    'QUARTERLY_REBALANCE_BLUEPRINT.md': {
        'old_resp': '执行优化',
        'new_resp': '季度调仓执行优化',
        'boundary_note': '季度调仓层面的执行优化（区别于交易成本优化）'
    },
    'TRADING_COST_OPTIMIZATION_BLUEPRINT.md': {
        'old_resp': ['执行优化', '成本控制'],
        'new_resp': ['交易执行成本优化', '交易成本控制'],
        'boundary_note': '交易成本层面的优化和控制（区别于季度调仓和换手率控制）'
    },
    'RISK_CONTRIBUTION_ANALYSIS_BLUEPRINT.md': {
        'old_resp': '风险预算',
        'new_resp': '风险贡献度预算分析',
        'boundary_note': '风险贡献度层面的预算分析（区别于风险平价和简化风险预算）'
    },
    'RISK_PARITY_STRATEGY_BLUEPRINT.md': {
        'old_resp': ['风险预算', '权重优化'],
        'new_resp': ['风险平价预算分配', '风险平价权重优化'],
        'boundary_note': '风险平价策略层面的预算和权重（区别于风险贡献度和简化预算）'
    },
    'SIMPLIFIED_RISK_BUDGET_SYSTEM_BLUEPRINT.md': {
        'old_resp': '风险预算',
        'new_resp': '简化风险预算分配',
        'boundary_note': '简化层面的风险预算分配（区别于风险贡献度和风险平价）'
    },
    'TURNOVER_CONTROL_BLUEPRINT.md': {
        'old_resp': '成本控制',
        'new_resp': '换手率成本控制',
        'boundary_note': '换手率层面的成本控制（区别于交易成本控制）'
    },
}

def fix_overlap(file_path, fixes):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    modified = False
    old_resp = fixes['old_resp']
    new_resp = fixes['new_resp']
    
    if isinstance(old_resp, list):
        for i, old in enumerate(old_resp):
            if old in content:
                content = content.replace(f'- {old}', f'- {new_resp[i]}')
                modified = True
    else:
        if f'- {old_resp}' in content:
            content = content.replace(f'- {old_resp}', f'- {new_resp}')
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, f'已修复职责重叠: {old_resp} -> {new_resp}'
    
    return False, '无需修改'

print('='*80)
print('修复职责重叠问题')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

fixed_count = 0
for filename, fixes in overlap_fixes.items():
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        success, msg = fix_overlap(file_path, fixes)
        if success:
            fixed_count += 1
            print(f'✓ {filename}: {msg}')
        else:
            print(f'- {filename}: {msg}')
    else:
        print(f'✗ {filename}: 文件不存在')

print(f'\n修复完成: {fixed_count}个文件')
