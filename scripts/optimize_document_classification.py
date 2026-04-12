#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
优化文档分类体系 - 确保每个文档都有明确的Layer归属
"""

import re
import os
from pathlib import Path
from collections import defaultdict

# Layer定义
LAYERS = {
    'Layer 0': '数据源层',
    'Layer 1': '数据层',
    'Layer 2': 'Alpha因子层',
    'Layer 3': '策略层',
    'Layer 4': '机器学习层',
    'Layer 5': '执行层',
    'Layer 6': '组合优化层',
    'Layer 7': '风控层',
    'Layer 8': '人机交互层',
    'Layer 9': '治理层',
    'Layer 10': '治理层',
    'Layer 11': '战略决策层',
}

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
    """从YAML头部获取Layer信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            layer_match = re.search(r'^layer:\s*(.+)$', yaml_content, re.MULTILINE)
            if layer_match:
                return layer_match.group(1).strip()
    except:
        pass
    
    return None

def optimize_document_classification():
    """优化文档分类体系"""
    print('=' * 80)
    print('优化文档分类体系')
    print('=' * 80)
    print()
    
    # 扫描所有蓝图
    blueprints = scan_all_blueprints()
    print(f'📊 扫描到 {len(blueprints)} 个蓝图文件')
    print()
    
    # 统计Layer归属
    layer_stats = defaultdict(list)
    missing_layer = []
    
    for blueprint in blueprints:
        yaml_layer = get_yaml_layer(blueprint)
        
        if yaml_layer:
            # 提取Layer编号
            layer_num = re.search(r'Layer (\d+)', yaml_layer)
            if layer_num:
                layer_key = f'Layer {layer_num.group(1)}'
                layer_stats[layer_key].append(blueprint)
        else:
            missing_layer.append(blueprint)
    
    # 输出统计结果
    print('📋 Layer归属统计:')
    for layer_num in sorted(layer_stats.keys(), key=lambda x: int(x.split()[1])):
        layer_name = LAYERS.get(layer_num, '未知')
        count = len(layer_stats[layer_num])
        print(f'  {layer_num} ({layer_name}): {count}个文档')
    
    print()
    print(f'⚠️  缺少Layer归属的文档: {len(missing_layer)}个')
    
    if missing_layer:
        print()
        print('缺少Layer归属的文档（前10个）:')
        for doc in missing_layer[:10]:
            print(f'  - {doc}')
    
    # 生成报告
    report_path = Path('docs/09_AUDIT/REPORTS/DOCUMENT_CLASSIFICATION_OPTIMIZATION_REPORT_20260407.md')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('# 文档分类体系优化报告\n\n')
        f.write(f'> **生成日期**: 2026-04-07\n')
        f.write(f'> **扫描范围**: 全系统蓝图文件\n\n')
        
        f.write('## 📊 统计概览\n\n')
        f.write(f'| 指标 | 数值 |\n')
        f.write(f'|------|------|\n')
        f.write(f'| 总蓝图数 | {len(blueprints)} |\n')
        f.write(f'| 有Layer归属 | {len(blueprints) - len(missing_layer)} |\n')
        f.write(f'| 缺少Layer归属 | {len(missing_layer)} |\n')
        f.write(f'| Layer覆盖率 | {(len(blueprints) - len(missing_layer)) / len(blueprints) * 100:.1f}% |\n\n')
        
        f.write('## 📋 Layer归属分布\n\n')
        f.write(f'| Layer | 名称 | 文档数 | 占比 |\n')
        f.write(f'|-------|------|--------|------|\n')
        for layer_num in sorted(layer_stats.keys(), key=lambda x: int(x.split()[1])):
            layer_name = LAYERS.get(layer_num, '未知')
            count = len(layer_stats[layer_num])
            percentage = count / len(blueprints) * 100
            f.write(f'| {layer_num} | {layer_name} | {count} | {percentage:.1f}% |\n')
        f.write('\n')
        
        if missing_layer:
            f.write('## ⚠️ 缺少Layer归属的文档\n\n')
            for doc in missing_layer:
                f.write(f'- {doc}\n')
            f.write('\n')
        
        f.write('## ✅ 改进建议\n\n')
        f.write('1. 为缺少Layer归属的文档添加layer字段\n')
        f.write('2. 确保每个文档都有明确的Layer归属\n')
        f.write('3. 定期运行layer_attribution_check.py检查Layer归属\n')
        f.write('4. 建立文档分类规范，确保新文档都有正确的Layer归属\n')
    
    print()
    print(f'✅ 已生成优化报告: {report_path}')
    
    return {
        'total': len(blueprints),
        'with_layer': len(blueprints) - len(missing_layer),
        'missing_layer': len(missing_layer),
        'layer_stats': dict(layer_stats),
        'missing_list': missing_layer
    }

if __name__ == '__main__':
    optimize_document_classification()
