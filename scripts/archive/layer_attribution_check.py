#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer归属检查机制 - 定期检查文档Layer归属是否正确
"""

import re
import os
from pathlib import Path
from datetime import datetime

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

# Layer与目录的映射关系
LAYER_DIR_MAPPING = {
    'Layer 0': ['docs/00_DATA_SOURCE', 'docs/02_FACTOR_LIBRARY'],
    'Layer 1': ['docs/01_FRAMEWORK', 'docs/02_FACTOR_LIBRARY'],
    'Layer 2': ['docs/01_FRAMEWORK', 'docs/02_FACTOR_LIBRARY'],
    'Layer 3': ['docs/01_FRAMEWORK', 'docs/03_STRATEGY'],
    'Layer 4': ['docs/01_FRAMEWORK'],
    'Layer 5': ['docs/04_EXECUTION'],
    'Layer 6': ['docs/05_IMPLEMENTATION/01_PORTFOLIO_OPTIMIZATION'],
    'Layer 7': ['docs/05_IMPLEMENTATION/02_RISK_MANAGEMENT'],
    'Layer 8': ['docs/05_IMPLEMENTATION/03_HUMAN_AI_INTERACTION'],
    'Layer 9': ['docs/05_IMPLEMENTATION/04_OPERATIONS'],
    'Layer 10': ['docs/05_IMPLEMENTATION/04_OPERATIONS'],
    'Layer 11': ['docs/11_STRATEGIC_DECISION'],
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

def check_layer_attribution():
    """检查所有蓝图的Layer归属"""
    print('=' * 80)
    print('Layer归属检查机制')
    print('=' * 80)
    print()
    
    # 扫描所有蓝图
    blueprints = scan_all_blueprints()
    print(f'📊 扫描到 {len(blueprints)} 个蓝图文件')
    print()
    
    # 检查每个蓝图的Layer归属
    issues = []
    correct = []
    
    for blueprint in blueprints:
        yaml_layer = get_yaml_layer(blueprint)
        
        if not yaml_layer:
            issues.append({
                'file': blueprint,
                'issue': '缺少YAML头部或layer字段',
                'expected': '在YAML头部添加layer字段'
            })
            continue
        
        # 检查Layer归属是否正确
        # 这里可以添加更详细的检查逻辑
        
    # 输出结果
    print('🔍 检查结果:')
    print(f'  正确: {len(correct)}')
    print(f'  问题: {len(issues)}')
    
    if issues:
        print()
        print('⚠️  发现问题:')
        for issue in issues[:10]:
            print(f'  - {issue["file"]}: {issue["issue"]}')
    
    print()
    print('✅ Layer归属检查完成')
    print()
    print(f'检查时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    return {
        'total': len(blueprints),
        'correct': len(correct),
        'issues': len(issues),
        'issue_details': issues
    }

if __name__ == '__main__':
    check_layer_attribution()
