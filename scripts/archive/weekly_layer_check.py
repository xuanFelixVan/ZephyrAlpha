#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
定期Layer归属检查脚本
每周运行一次，确保新文档都有正确的Layer归属
增强版V2：支持多种layer字段格式，包括带引号的格式
"""

import re
import os
from pathlib import Path
from datetime import datetime
import json

def scan_all_blueprints():
    """扫描所有蓝图文件"""
    blueprints = []
    
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('_BLUEPRINT.md'):
                file_path = Path(root) / file
                blueprints.append(str(file_path))
    
    return blueprints

def get_yaml_layer(file_path):
    """从YAML头部获取Layer信息 - 增强版V2"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有YAML头部
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        yaml_matches = list(re.finditer(yaml_pattern, content, re.DOTALL))
        
        # 从所有YAML头部中查找layer字段
        for match in yaml_matches:
            yaml_content = match.group(1)
            
            # 尝试多种layer字段格式
            # 格式1: layer: Layer 4 (机器学习层)
            layer_match = re.search(r'^layer:\s*(.+)$', yaml_content, re.MULTILINE)
            if layer_match:
                layer_value = layer_match.group(1).strip()
                
                # 去除引号
                if layer_value.startswith('"') and layer_value.endswith('"'):
                    layer_value = layer_value[1:-1]
                elif layer_value.startswith("'") and layer_value.endswith("'"):
                    layer_value = layer_value[1:-1]
                
                # 检查是否是标准格式
                if re.match(r'^Layer \d+ \(.+\)$', layer_value):
                    return layer_value
                
                # 如果不是标准格式，提取Layer编号并返回标准格式
                layer_num_match = re.search(r'Layer (\d+)', layer_value)
                if layer_num_match:
                    layer_num = layer_num_match.group(1)
                    layer_names = {
                        '0': 'Layer 0 (数据源层)',
                        '1': 'Layer 1 (数据层)',
                        '2': 'Layer 2 (Alpha因子层)',
                        '3': 'Layer 3 (策略层)',
                        '4': 'Layer 4 (机器学习层)',
                        '5': 'Layer 5 (执行层)',
                        '6': 'Layer 6 (组合优化层)',
                        '7': 'Layer 7 (风控层)',
                        '8': 'Layer 8 (人机交互层)',
                        '9': 'Layer 9 (治理层)',
                        '10': 'Layer 10 (治理层)',
                        '11': 'Layer 11 (战略决策层)',
                    }
                    return layer_names.get(layer_num, f'Layer {layer_num}')
                
                return layer_value
        
    except Exception as e:
        pass
    
    return None

def weekly_layer_check():
    """每周Layer归属检查"""
    print('=' * 80)
    print('定期Layer归属检查')
    print('=' * 80)
    print()
    print(f'检查时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # 扫描所有蓝图
    blueprints = scan_all_blueprints()
    print(f'扫描到 {len(blueprints)} 个蓝图文件')
    print()
    
    # 检查每个蓝图的Layer归属
    missing_layer = []
    layer_stats = {}
    
    for blueprint in blueprints:
        yaml_layer = get_yaml_layer(blueprint)
        
        if not yaml_layer:
            missing_layer.append(blueprint)
        else:
            # 统计Layer分布
            layer_num = re.search(r'Layer (\d+)', yaml_layer)
            if layer_num:
                layer_key = f'Layer {layer_num.group(1)}'
                layer_stats[layer_key] = layer_stats.get(layer_key, 0) + 1
    
    # 输出结果
    print('Layer归属统计:')
    for layer_num in sorted(layer_stats.keys(), key=lambda x: int(x.split()[1])):
        count = layer_stats[layer_num]
        print(f'  {layer_num}: {count}个文档')
    
    print()
    print(f'缺少Layer归属的文档: {len(missing_layer)}个')
    
    if missing_layer:
        print()
        print('缺少Layer归属的文档:')
        for doc in missing_layer:
            print(f'  - {doc}')
    
    # 计算覆盖率
    coverage_rate = (len(blueprints) - len(missing_layer)) / len(blueprints) * 100
    
    print()
    print(f'Layer覆盖率: {coverage_rate:.1f}%')
    
    # 保存检查结果
    result = {
        'check_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_blueprints': len(blueprints),
        'with_layer': len(blueprints) - len(missing_layer),
        'missing_layer': len(missing_layer),
        'coverage_rate': coverage_rate,
        'layer_stats': layer_stats,
        'missing_list': missing_layer
    }
    
    # 保存到JSON文件
    result_path = Path('docs/09_AUDIT/STATE/weekly_layer_check_result.json')
    result_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print()
    print(f'检查结果已保存: {result_path}')
    
    # 生成报告
    report_path = Path('docs/09_AUDIT/REPORTS/WEEKLY_LAYER_CHECK_REPORT.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('# 定期Layer归属检查报告\n\n')
        f.write(f'> **检查时间**: {result["check_time"]}\n')
        f.write(f'> **检查范围**: 全系统蓝图文件\n\n')
        
        f.write('## 检查统计\n\n')
        f.write(f'| 指标 | 数值 |\n')
        f.write(f'|------|------|\n')
        f.write(f'| 总蓝图数 | {result["total_blueprints"]} |\n')
        f.write(f'| 有Layer归属 | {result["with_layer"]} |\n')
        f.write(f'| 缺少Layer归属 | {result["missing_layer"]} |\n')
        f.write(f'| Layer覆盖率 | {result["coverage_rate"]:.1f}% |\n\n')
        
        f.write('## Layer归属分布\n\n')
        f.write(f'| Layer | 文档数 |\n')
        f.write(f'|-------|--------|\n')
        for layer_num in sorted(layer_stats.keys(), key=lambda x: int(x.split()[1])):
            count = layer_stats[layer_num]
            f.write(f'| {layer_num} | {count} |\n')
        f.write('\n')
        
        if missing_layer:
            f.write('## 缺少Layer归属的文档\n\n')
            for doc in missing_layer:
                f.write(f'- {doc}\n')
            f.write('\n')
        
        f.write('## 改进建议\n\n')
        if missing_layer:
            f.write('1. 运行 `scripts/batch_add_layer_fields.py` 为缺少Layer归属的文档添加layer字段\n')
            f.write('2. 重新运行本脚本验证修复效果\n')
        else:
            f.write('所有文档都有正确的Layer归属，无需改进。\n')
    
    print(f'检查报告已保存: {report_path}')
    
    return result

if __name__ == '__main__':
    weekly_layer_check()
