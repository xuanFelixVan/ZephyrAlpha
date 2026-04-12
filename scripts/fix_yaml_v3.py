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

files_to_fix = [
    'DATA_CATALOG_BLUEPRINT.md',
    'DATA_COST_MANAGEMENT_BLUEPRINT.md',
    'DATA_FABRIC_BLUEPRINT.md',
    'DATA_MESH_BLUEPRINT.md',
    'ECONOMIC_REGIME_ENGINE_BLUEPRINT.md',
    'ENHANCED_ALERT_SYSTEM_BLUEPRINT.md',
    'MARGIN_CALL_MONITOR_BLUEPRINT.md',
    'MARKET_REGIME_DETECTION_BLUEPRINT.md',
]

responsibility_updates = {
    'DATA_CATALOG_BLUEPRINT.md': ['数据目录管理', '元数据索引', '数据资产发现', '数据血缘追踪'],
    'DATA_COST_MANAGEMENT_BLUEPRINT.md': ['数据成本管理', '存储成本优化', '计算成本控制', '成本监控告警'],
    'DATA_FABRIC_BLUEPRINT.md': ['数据编织架构', '数据虚拟化', '统一数据访问', '跨域数据集成'],
    'DATA_MESH_BLUEPRINT.md': ['数据网格架构', '数据产品化', '领域数据自治', '联邦数据治理'],
    'ECONOMIC_REGIME_ENGINE_BLUEPRINT.md': ['经济周期识别', '宏观环境分析', '经济指标监控', '周期转换预测'],
    'ENHANCED_ALERT_SYSTEM_BLUEPRINT.md': ['增强告警系统', '智能告警聚合', '告警降噪', '告警优先级排序'],
    'MARGIN_CALL_MONITOR_BLUEPRINT.md': ['保证金监控', '追加保证金预警', '保证金充足率计算', '强平风险提示'],
    'MARKET_REGIME_DETECTION_BLUEPRINT.md': ['市场状态识别', '市场环境分类', '状态转换检测', '市场特征分析'],
}

def fix_yaml_direct(file_path, new_responsibilities):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    content = content.replace('\ufeff', '')
    
    module_id_matches = list(re.finditer(r'module_id:', content))
    
    if len(module_id_matches) < 2:
        return False, f'只找到{len(module_id_matches)}个module_id'
    
    second_module_id_start = module_id_matches[1].start()
    
    second_yaml_end = content.find('---', second_module_id_start)
    if second_yaml_end == -1:
        return False, '未找到第二个YAML结束标记'
    
    second_yaml_content = content[second_module_id_start:second_yaml_end]
    
    resp_pattern = r'responsibility:\s*\n((?:  - .+\n?)+)'
    resp_match = re.search(resp_pattern, second_yaml_content)
    
    if resp_match:
        old_resp_block = resp_match.group(0)
        new_resp_block = 'responsibility:\n'
        for resp in new_responsibilities:
            new_resp_block += f'  - {resp}\n'
        
        new_yaml_content = second_yaml_content.replace(old_resp_block, new_resp_block)
    else:
        layer_match = re.search(r'layer:.*\n', second_yaml_content)
        if layer_match:
            insert_pos = layer_match.end()
            new_resp_block = 'responsibility:\n'
            for resp in new_responsibilities:
                new_resp_block += f'  - {resp}\n'
            new_yaml_content = second_yaml_content[:insert_pos] + new_resp_block + second_yaml_content[insert_pos:]
        else:
            new_resp_block = '\nresponsibility:\n'
            for resp in new_responsibilities:
                new_resp_block += f'  - {resp}\n'
            new_yaml_content = second_yaml_content.rstrip() + new_resp_block
    
    new_content = '---\n' + new_yaml_content + '---\n' + content[second_yaml_end + 3:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f'已修复YAML结构并更新responsibility: {len(new_responsibilities)}项'

print('='*80)
print('修复YAML结构问题')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

fixed_count = 0
for filename in files_to_fix:
    file_path = os.path.join(blueprints_dir, filename)
    if os.path.exists(file_path):
        new_responsibilities = responsibility_updates.get(filename, [])
        success, msg = fix_yaml_direct(file_path, new_responsibilities)
        if success:
            fixed_count += 1
            print(f'✓ {filename}: {msg}')
        else:
            print(f'- {filename}: {msg}')
    else:
        print(f'- {filename}: 文件不存在')

print(f'\n修复完成: {fixed_count}个文件')
