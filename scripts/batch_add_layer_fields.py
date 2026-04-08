#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量为缺少Layer归属的文档添加layer字段
增强版：使用与weekly_layer_check.py相同的检测逻辑
"""

import re
import os
from pathlib import Path
from collections import defaultdict

# Layer定义和关键词映射
LAYER_KEYWORDS = {
    'Layer 0 (数据源层)': ['数据源', '数据采集', '数据接入', '数据获取', 'DATA_SOURCE', 'DATA_INGESTION', 'DATA_ACQUISITION'],
    'Layer 1 (数据层)': ['数据层', '数据存储', '数据管理', '数据预处理', 'DATA_LAYER', 'DATA_STORAGE', 'DATA_MANAGEMENT', 'DATA_PREPROCESSING'],
    'Layer 2 (Alpha因子层)': ['Alpha', '因子', '因子库', 'FACTOR', 'ALPHA', '因子挖掘', '因子计算'],
    'Layer 3 (策略层)': ['策略', '交易策略', '投资策略', 'STRATEGY', 'TRADING_STRATEGY', '策略组合'],
    'Layer 4 (机器学习层)': ['机器学习', 'ML', '模型', '深度学习', 'MACHINE_LEARNING', 'MODEL', 'DEEP_LEARNING', '神经网络', '训练', '推理'],
    'Layer 5 (执行层)': ['执行', '交易执行', '订单', 'EXECUTION', 'ORDER', '交易执行', '订单管理'],
    'Layer 6 (组合优化层)': ['组合优化', '资产配置', '投资组合', 'PORTFOLIO', 'OPTIMIZATION', '资产配置', '组合管理'],
    'Layer 7 (风控层)': ['风控', '风险管理', '风险控制', 'RISK', 'RISK_MANAGEMENT', '风险监控'],
    'Layer 8 (人机交互层)': ['人机交互', '界面', 'UI', 'HUMAN_AI', 'INTERFACE', '交互', '可视化'],
    'Layer 9 (治理层)': ['治理', '合规', '监管', 'GOVERNANCE', 'COMPLIANCE', '监管合规'],
    'Layer 10 (治理层)': ['治理', '合规', '监管', 'GOVERNANCE', 'COMPLIANCE', '监管合规'],
    'Layer 11 (战略决策层)': ['战略', '决策', '战略决策', 'STRATEGIC', 'DECISION', '投资决策'],
}

def get_yaml_layer(file_path):
    """从YAML头部获取Layer信息 - 增强版"""
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
            
            # 格式2: layer: "Layer 3 (中观策略层) | 业务架构: xxx"
            layer_match = re.search(r'^layer:\s*["\'](.+?)["\']', yaml_content, re.MULTILINE)
            if layer_match:
                layer_value = layer_match.group(1).strip()
                # 提取Layer编号
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
                
                return layer_value.strip()
        
    except Exception as e:
        pass
    
    return None

def infer_layer_from_filename(filename):
    """从文件名推断Layer归属"""
    filename_upper = filename.upper()
    
    # 按优先级匹配关键词
    for layer, keywords in LAYER_KEYWORDS.items():
        for keyword in keywords:
            if keyword.upper() in filename_upper:
                return layer
    
    # 默认返回Layer 4 (机器学习层)，因为大部分蓝图都是ML相关
    return 'Layer 4 (机器学习层)'

def infer_layer_from_content(file_path):
    """从文件内容推断Layer归属"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查内容中的关键词
        content_upper = content.upper()
        
        # 统计每个Layer的关键词出现次数
        layer_scores = defaultdict(int)
        for layer, keywords in LAYER_KEYWORDS.items():
            for keyword in keywords:
                count = content_upper.count(keyword.upper())
                layer_scores[layer] += count
        
        # 返回得分最高的Layer
        if layer_scores:
            return max(layer_scores.items(), key=lambda x: x[1])[0]
    except:
        pass
    
    return None

def add_layer_to_yaml(file_path, layer):
    """在YAML头部添加layer字段"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有YAML头部
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        
        if yaml_match:
            yaml_content = yaml_match.group(1)
            
            # 检查是否已有layer字段
            if 'layer:' in yaml_content:
                return False, '已有layer字段'
            
            # 在YAML头部添加layer字段
            # 找到合适的位置插入（在owner字段之后，或者在module_id字段之后）
            if 'owner:' in yaml_content:
                new_yaml = re.sub(
                    r'(owner:.*?\n)',
                    r'\1layer: ' + layer + '\n',
                    yaml_content
                )
            elif 'module_id:' in yaml_content:
                new_yaml = re.sub(
                    r'(module_id:.*?\n)',
                    r'\1layer: ' + layer + '\n',
                    yaml_content
                )
            else:
                # 在YAML头部开头添加
                new_yaml = 'layer: ' + layer + '\n' + yaml_content
            
            # 重新构建文档
            new_content = '---\n' + new_yaml + '\n---' + content[yaml_match.end():]
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True, '成功'
        else:
            return False, '未找到YAML头部'
    
    except Exception as e:
        return False, str(e)

def batch_add_layer_fields():
    """批量为缺少Layer归属的文档添加layer字段"""
    print('=' * 80)
    print('批量为缺少Layer归属的文档添加layer字段')
    print('=' * 80)
    print()
    
    # 扫描所有蓝图文件
    blueprints = []
    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('_BLUEPRINT.md'):
                file_path = Path(root) / file
                blueprints.append(str(file_path))
    
    print(f'📊 扫描到 {len(blueprints)} 个蓝图文件')
    print()
    
    # 找出缺少Layer归属的文档
    missing_layer = []
    for blueprint in blueprints:
        yaml_layer = get_yaml_layer(blueprint)
        if not yaml_layer:
            missing_layer.append(blueprint)
    
    print(f'⚠️  发现 {len(missing_layer)} 个缺少Layer归属的文档')
    print()
    
    # 为每个文档添加layer字段
    stats = {
        'total': len(missing_layer),
        'success': 0,
        'failed': 0,
        'skipped': 0,
    }
    
    results = []
    
    for blueprint in missing_layer:
        # 从文件名推断Layer
        filename = Path(blueprint).stem
        layer_from_name = infer_layer_from_filename(filename)
        
        # 从内容推断Layer
        layer_from_content = infer_layer_from_content(blueprint)
        
        # 优先使用内容推断的结果
        final_layer = layer_from_content if layer_from_content else layer_from_name
        
        # 添加layer字段
        success, message = add_layer_to_yaml(blueprint, final_layer)
        
        if success:
            stats['success'] += 1
            results.append({
                'file': blueprint,
                'layer': final_layer,
                'method': 'content' if layer_from_content else 'filename',
                'status': 'success'
            })
            print(f'✅ {Path(blueprint).name}: {final_layer}')
        else:
            stats['failed'] += 1
            results.append({
                'file': blueprint,
                'layer': final_layer,
                'method': 'content' if layer_from_content else 'filename',
                'status': 'failed',
                'message': message
            })
            print(f'❌ {Path(blueprint).name}: {message}')
    
    print()
    print('=' * 80)
    print('处理统计')
    print('=' * 80)
    print(f'总文档数: {stats["total"]}')
    print(f'成功处理: {stats["success"]}')
    print(f'失败数: {stats["failed"]}')
    print(f'跳过数: {stats["skipped"]}')
    
    # 保存处理结果
    report_path = Path('docs/09_AUDIT/REPORTS/BATCH_ADD_LAYER_FIELDS_REPORT_20260407.md')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('# 批量添加Layer字段报告\n\n')
        f.write(f'> **处理日期**: 2026-04-07\n')
        f.write(f'> **处理范围**: 缺少Layer归属的蓝图文件\n\n')
        
        f.write('## 📊 处理统计\n\n')
        f.write(f'| 指标 | 数值 |\n')
        f.write(f'|------|------|\n')
        f.write(f'| 总文档数 | {stats["total"]} |\n')
        f.write(f'| 成功处理 | {stats["success"]} |\n')
        f.write(f'| 失败数 | {stats["failed"]} |\n')
        f.write(f'| 成功率 | {stats["success"] / max(1, stats["total"]) * 100:.1f}% |\n\n')
        
        f.write('## ✅ 成功处理的文档\n\n')
        for result in results:
            if result['status'] == 'success':
                f.write(f'- **{Path(result["file"]).name}**: {result["layer"]} (推断方法: {result["method"]})\n')
        f.write('\n')
        
        if stats['failed'] > 0:
            f.write('## ❌ 处理失败的文档\n\n')
            for result in results:
                if result['status'] == 'failed':
                    f.write(f'- **{Path(result["file"]).name}**: {result["message"]}\n')
            f.write('\n')
    
    print()
    print(f'✅ 已保存处理报告: {report_path}')
    
    return stats

if __name__ == '__main__':
    batch_add_layer_fields()
