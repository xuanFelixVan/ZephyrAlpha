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

remaining_fixes = {
    'DATA_SOURCE_HEALTH_MONITOR_BLUEPRINT.md': {
        'check_duplicate': '数据源健康监控'
    },
    'LIQUIDITY_CONSTRAINED_OPTIMIZATION_BLUEPRINT.md': {
        'old_resp': '交易成本控制',
        'new_resp': '流动性约束成本控制'
    },
    'RISK_PARITY_STRATEGY_BLUEPRINT.md': {
        'check_duplicate': '风险平价权重优化'
    },
}

boundary_files = [
    'CDC_CHANGE_DATA_CAPTURE_BLUEPRINT.md',
    'CLICKHOUSE_INTEGRATION_BLUEPRINT.md',
    'DATA_ACCESS_AUDIT_BLUEPRINT.md',
    'DATA_BACKUP_RECOVERY_BLUEPRINT.md',
    'DATA_CLEANING_ENGINE_BLUEPRINT.md',
    'DATA_MASKING_ENCRYPTION_BLUEPRINT.md',
    'DATA_PREPROCESSING_ARCHITECTURE_GAP_ANALYSIS_BLUEPRINT.md',
    'DATA_SOURCE_HEALTH_MONITOR_BLUEPRINT.md',
    'DATA_VALIDATION_ENGINE_BLUEPRINT.md',
    'DISTRIBUTED_QUERY_ENGINE_BLUEPRINT.md',
    'FACTOR_EXPOSURE_MANAGEMENT_BLUEPRINT.md',
    'ARCHITECTURE_GAP_ANALYSIS_BLUEPRINT.md',
    'COINTEGRATION_ANALYSIS_BLUEPRINT.md',
    'TAIL_RISK_METRICS_EXTENSION_BLUEPRINT.md',
]

module_info = {
    'CDC_CHANGE_DATA_CAPTURE': ('CDC变更数据捕获', '数据变更检测', '变更流处理'),
    'CLICKHOUSE_INTEGRATION': ('ClickHouse集成', '列式存储', '高性能查询'),
    'DATA_ACCESS_AUDIT': ('数据访问审计', '访问日志', '权限审计'),
    'DATA_BACKUP_RECOVERY': ('数据备份恢复', '备份策略', '恢复机制'),
    'DATA_CLEANING_ENGINE': ('数据清洗引擎', '数据质量检测', '异常值处理'),
    'DATA_MASKING_ENCRYPTION': ('数据脱敏加密', '敏感数据识别', '脱敏规则'),
    'DATA_PREPROCESSING_ARCHITECTURE_GAP_ANALYSIS': ('数据预处理架构差距分析', '架构评估', '差距识别'),
    'DATA_SOURCE_HEALTH_MONITOR': ('数据源健康监控', '健康检查', '故障检测'),
    'DATA_VALIDATION_ENGINE': ('数据验证引擎', '验证规则', '数据校验'),
    'DISTRIBUTED_QUERY_ENGINE': ('分布式查询引擎', '查询优化', '并行执行'),
    'FACTOR_EXPOSURE_MANAGEMENT': ('因子暴露管理', '暴露监控', '风险因子'),
    'ARCHITECTURE_GAP_ANALYSIS': ('架构差距分析', '差距识别', '改进建议'),
    'COINTEGRATION_ANALYSIS': ('协整分析', '统计套利', '配对交易'),
    'TAIL_RISK_METRICS_EXTENSION': ('尾部风险指标扩展', '尾部风险', '极端事件'),
}

def fix_duplicate_responsibility(file_path, resp_text):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    pattern = f'- {resp_text}'
    matches = list(re.finditer(pattern, content))
    
    if len(matches) > 1:
        first_match = True
        for match in matches:
            if not first_match:
                content = content[:match.start()] + content[match.end():]
            first_match = False
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, f'已删除重复职责: {resp_text}'
    
    return False, '无重复职责'

def fix_overlap(file_path, old_resp, new_resp):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if f'- {old_resp}' in content:
        content = content.replace(f'- {old_resp}', f'- {new_resp}')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, f'已修复职责: {old_resp} -> {new_resp}'
    
    return False, '无需修改'

def add_boundary(file_path, module_name):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if re.search(r'>\s*\*\*职责边界\*\*', content):
        return False, '已有职责边界'
    
    if module_name in module_info:
        resp1, resp2, resp3 = module_info[module_name]
    else:
        resp1, resp2, resp3 = '本模块核心功能', '模块实现', '质量保证'
    
    boundary_text = f'''
> **职责边界**: 
> - ✅ 本文档负责：{resp1}、{resp2}、{resp3}
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

print('='*80)
print('修复剩余问题')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

print('='*80)
print('修复职责重叠和重复')
print('='*80)

fixed_count = 0
for filename, fixes in remaining_fixes.items():
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        if 'check_duplicate' in fixes:
            success, msg = fix_duplicate_responsibility(file_path, fixes['check_duplicate'])
        else:
            success, msg = fix_overlap(file_path, fixes['old_resp'], fixes['new_resp'])
        
        if success:
            fixed_count += 1
            print(f'✓ {filename}: {msg}')
        else:
            print(f'- {filename}: {msg}')

print(f'\n修复完成: {fixed_count}个文件')

print()
print('='*80)
print('添加缺失职责边界')
print('='*80)

boundary_fixed = 0
for filename in boundary_files:
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        module_name = filename.replace('_BLUEPRINT.md', '')
        success, msg = add_boundary(file_path, module_name)
        if success:
            boundary_fixed += 1
            print(f'✓ {filename}: {msg}')

print(f'\n修复完成: {boundary_fixed}个文件')

print()
print('='*80)
print('修复汇总')
print('='*80)
print(f'职责重叠修复: {fixed_count}个')
print(f'职责边界添加: {boundary_fixed}个')
print()
print('修复完成!')
