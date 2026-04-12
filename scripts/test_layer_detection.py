#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
测试layer字段检测
"""

import re

# 测试数据
test_cases = [
    ('Layer 4 (机器学习层)', '标准格式'),
    ('"Layer 4 (机器学习层)"', '带双引号'),
    ("'Layer 4 (机器学习层)'", '带单引号'),
    ('Layer 4 (机器学习层) | 业务架构: xxx', '带额外信息'),
    ('"Layer 4 (机器学习层) | 业务架构: xxx"', '带双引号和额外信息'),
]

print('=' * 80)
print('测试layer字段检测')
print('=' * 80)
print()

for layer_value, desc in test_cases:
    print(f'测试: {desc}')
    print(f'原始值: {layer_value}')
    
    # 去除引号
    if layer_value.startswith('"') and layer_value.endswith('"'):
        layer_value = layer_value[1:-1]
    elif layer_value.startswith("'") and layer_value.endswith("'"):
        layer_value = layer_value[1:-1]
    
    print(f'去除引号后: {layer_value}')
    
    # 检查是否是标准格式
    if re.match(r'^Layer \d+ \(.+\)$', layer_value):
        print('✅ 是标准格式')
    else:
        print('❌ 不是标准格式')
        
        # 提取Layer编号
        layer_num_match = re.search(r'Layer (\d+)', layer_value)
        if layer_num_match:
            layer_num = layer_num_match.group(1)
            print(f'   Layer编号: {layer_num}')
    
    print()

# 测试实际的YAML内容
yaml_content = '''
module_id: CONSTRAINT_SOLVER_001
version: 1.0.0
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: '2026-04-06'
created_date: 2026-04-03
layer: "Layer 4 (机器学习层)"
index: CONSTRAINT_SOLVER_001
'''

print('=' * 80)
print('测试实际的YAML内容')
print('=' * 80)
print()

layer_match = re.search(r'^layer:\s*(.+)$', yaml_content, re.MULTILINE)
if layer_match:
    layer_value = layer_match.group(1).strip()
    print(f'找到layer字段: {layer_value}')
    
    # 去除引号
    if layer_value.startswith('"') and layer_value.endswith('"'):
        layer_value = layer_value[1:-1]
    elif layer_value.startswith("'") and layer_value.endswith("'"):
        layer_value = layer_value[1:-1]
    
    print(f'去除引号后: {layer_value}')
    
    # 检查是否是标准格式
    if re.match(r'^Layer \d+ \(.+\)$', layer_value):
        print('✅ 是标准格式')
    else:
        print('❌ 不是标准格式')
else:
    print('❌ 未找到layer字段')
