#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
质量指标监控系统
建立文档质量指标监控机制
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def calculate_quality_metrics():
    """计算质量指标"""
    print("=" * 80)
    print("计算质量指标")
    print("=" * 80)
    
    metrics = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'document_metrics': {},
        'reference_metrics': {},
        'structure_metrics': {},
        'compliance_metrics': {}
    }
    
    # 1. 文档指标
    total_files = 0
    files_with_metadata = 0
    files_with_responsibility = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        total_files += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查YAML元数据
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end > 0:
                    files_with_metadata += 1
                    
                    yaml_content = content[3:yaml_end]
                    
                    # 检查职责描述
                    if 'responsibility:' in yaml_content or '核心职责:' in content:
                        files_with_responsibility += 1
        
        except Exception as e:
            pass
    
    metrics['document_metrics'] = {
        'total_files': total_files,
        'files_with_metadata': files_with_metadata,
        'files_with_responsibility': files_with_responsibility,
        'metadata_compliance_rate': (files_with_metadata / total_files * 100) if total_files > 0 else 0,
        'responsibility_compliance_rate': (files_with_responsibility / total_files * 100) if total_files > 0 else 0
    }
    
    print(f"\n文档指标:")
    print(f"  总文件数: {total_files}")
    print(f"  元数据符合率: {metrics['document_metrics']['metadata_compliance_rate']:.2f}%")
    print(f"  职责符合率: {metrics['document_metrics']['responsibility_compliance_rate']:.2f}%")
    
    # 2. 引用指标
    total_links = 0
    valid_links = 0
    invalid_links = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = re.findall(pattern, content)
            
            for match in matches:
                link_path = match[1]
                
                if link_path.startswith('http') or link_path.startswith('#'):
                    total_links += 1
                    valid_links += 1
                    continue
                
                total_links += 1
                
                if link_path.startswith('../') or link_path.startswith('./'):
                    target_path = (file_path.parent / link_path).resolve()
                    
                    if target_path.exists():
                        valid_links += 1
                    else:
                        invalid_links += 1
                else:
                    valid_links += 1
        
        except Exception as e:
            pass
    
    metrics['reference_metrics'] = {
        'total_links': total_links,
        'valid_links': valid_links,
        'invalid_links': invalid_links,
        'link_validity_rate': (valid_links / total_links * 100) if total_links > 0 else 0
    }
    
    print(f"\n引用指标:")
    print(f"  总链接数: {total_links}")
    print(f"  有效链接: {valid_links}")
    print(f"  无效链接: {invalid_links}")
    print(f"  有效率: {metrics['reference_metrics']['link_validity_rate']:.2f}%")
    
    # 3. 结构指标
    depth_stats = defaultdict(int)
    max_depth = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        rel_path = file_path.relative_to(FACTOR_LIBRARY)
        depth = len(rel_path.parts) - 1
        depth_stats[depth] += 1
        max_depth = max(max_depth, depth)
    
    total_files = sum(depth_stats.values())
    avg_depth = sum(depth * count for depth, count in depth_stats.items()) / total_files if total_files > 0 else 0
    
    metrics['structure_metrics'] = {
        'max_depth': max_depth,
        'avg_depth': avg_depth,
        'depth_distribution': dict(depth_stats),
        'deep_files_count': depth_stats.get(4, 0) + depth_stats.get(5, 0) + depth_stats.get(6, 0)
    }
    
    print(f"\n结构指标:")
    print(f"  最大深度: {max_depth}")
    print(f"  平均深度: {avg_depth:.2f}")
    print(f"  深层文件数: {metrics['structure_metrics']['deep_files_count']}")
    
    # 4. 合规指标
    compliance_score = 0
    max_score = 100
    
    # 元数据符合率 (30分)
    compliance_score += (metrics['document_metrics']['metadata_compliance_rate'] / 100 * 30)
    
    # 职责符合率 (20分)
    compliance_score += (metrics['document_metrics']['responsibility_compliance_rate'] / 100 * 20)
    
    # 链接有效率 (30分)
    compliance_score += (metrics['reference_metrics']['link_validity_rate'] / 100 * 30)
    
    # 结构合理性 (20分)
    if metrics['structure_metrics']['deep_files_count'] < 20:
        compliance_score += 20
    elif metrics['structure_metrics']['deep_files_count'] < 50:
        compliance_score += 15
    elif metrics['structure_metrics']['deep_files_count'] < 100:
        compliance_score += 10
    else:
        compliance_score += 5
    
    metrics['compliance_metrics'] = {
        'compliance_score': compliance_score,
        'compliance_level': get_compliance_level(compliance_score),
        'target_score': 90
    }
    
    print(f"\n合规指标:")
    print(f"  合规分数: {compliance_score:.2f}/100")
    print(f"  合规等级: {metrics['compliance_metrics']['compliance_level']}")
    
    return metrics

def get_compliance_level(score):
    """获取合规等级"""
    if score >= 95:
        return '优秀'
    elif score >= 90:
        return '良好'
    elif score >= 80:
        return '合格'
    elif score >= 70:
        return '待改进'
    else:
        return '不合格'

def save_metrics_history(metrics):
    """保存指标历史"""
    history_file = OUTPUT_DIR / 'QUALITY_METRICS_HISTORY.json'
    
    history = []
    if history_file.exists():
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    
    history.append(metrics)
    
    # 只保留最近30天的数据
    if len(history) > 30:
        history = history[-30:]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    print(f"\n指标历史已保存: {history_file}")
    return history_file

def generate_quality_report(metrics):
    """生成质量报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'QUALITY_METRICS_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: QUALITY_METRICS_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 质量报告
applicable_scope: 文档质量指标监控
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 文档质量指标监控报告

> **核心职责**: 记录文档质量指标监控的结果
> **职责边界**: 
> - [OK] 本文档负责：指标记录、趋势分析、改进建议
> - [NO] 本文档不负责：问题修复、后续审计执行

---

## 监控概要

**监控时间**: {metrics['timestamp']}  
**监控范围**: 全系统文档  
**监控方法**: 自动扫描 + 指标计算  
**监控结论**: 文档质量达到{metrics['compliance_metrics']['compliance_level']}水平

---

## 合规指标

### 总体合规分数

| 指标 | 分数 | 等级 | 目标 |
|------|------|------|------|
| **合规分数** | {metrics['compliance_metrics']['compliance_score']:.2f}/100 | {metrics['compliance_metrics']['compliance_level']} | {metrics['compliance_metrics']['target_score']} |

### 合规等级说明

- **优秀** (≥95分): 文档质量卓越，符合专业量化机构最高标准
- **良好** (≥90分): 文档质量良好，符合专业量化机构标准
- **合格** (≥80分): 文档质量合格，基本符合专业量化机构标准
- **待改进** (≥70分): 文档质量待改进，需要优化
- **不合格** (<70分): 文档质量不合格，需要全面整改

---

## 文档指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **总文件数** | {metrics['document_metrics']['total_files']} | 系统中的Markdown文档总数 |
| **元数据符合率** | {metrics['document_metrics']['metadata_compliance_rate']:.2f}% | 包含YAML元数据的文档占比 |
| **职责符合率** | {metrics['document_metrics']['responsibility_compliance_rate']:.2f}% | 包含职责描述的文档占比 |

---

## 引用指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **总链接数** | {metrics['reference_metrics']['total_links']} | 系统中的引用链接总数 |
| **有效链接** | {metrics['reference_metrics']['valid_links']} | 有效的引用链接数 |
| **无效链接** | {metrics['reference_metrics']['invalid_links']} | 无效的引用链接数 |
| **有效率** | {metrics['reference_metrics']['link_validity_rate']:.2f}% | 有效链接占比 |

---

## 结构指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **最大深度** | {metrics['structure_metrics']['max_depth']} | 目录结构的最大嵌套深度 |
| **平均深度** | {metrics['structure_metrics']['avg_depth']:.2f} | 目录结构的平均嵌套深度 |
| **深层文件数** | {metrics['structure_metrics']['deep_files_count']} | 深度>=4的文件数量 |

### 深度分布

| 深度 | 文件数 | 占比 |
|------|--------|------|
"""
    
    total_files = sum(metrics['structure_metrics']['depth_distribution'].values())
    for depth in sorted(metrics['structure_metrics']['depth_distribution'].keys()):
        count = metrics['structure_metrics']['depth_distribution'][depth]
        percentage = (count / total_files * 100) if total_files > 0 else 0
        report_content += f"| {depth} | {count} | {percentage:.1f}% |\n"
    
    report_content += f"""
---

## 质量趋势

### 历史对比

| 指标 | 上次检查 | 本次检查 | 变化 |
|------|---------|---------|------|
| **合规分数** | - | {metrics['compliance_metrics']['compliance_score']:.2f} | - |
| **链接有效率** | - | {metrics['reference_metrics']['link_validity_rate']:.2f}% | - |
| **深层文件数** | - | {metrics['structure_metrics']['deep_files_count']} | - |

---

## 改进建议

### 立即行动

1. [ ] 修复无效链接（{metrics['reference_metrics']['invalid_links']}个）
2. [ ] 补充缺失的元数据
3. [ ] 补充缺失的职责描述

### 持续改进

1. [ ] 执行目录重构计划
2. [ ] 建立质量预警机制
3. [ ] 持续优化文档质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，质量指标监控报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n质量报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 计算质量指标
    metrics = calculate_quality_metrics()
    
    # 保存指标历史
    history_file = save_metrics_history(metrics)
    
    # 生成质量报告
    report_path = generate_quality_report(metrics)
    
    print("\n" + "=" * 80)
    print("质量指标监控完成")
    print("=" * 80)
    print(f"合规分数: {metrics['compliance_metrics']['compliance_score']:.2f}/100")
    print(f"合规等级: {metrics['compliance_metrics']['compliance_level']}")
    print(f"报告位置: {report_path}")
