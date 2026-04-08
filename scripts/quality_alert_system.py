#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
质量预警机制
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')
HISTORY_FILE = OUTPUT_DIR / 'QUALITY_METRICS_HISTORY.json'

# 质量阈值定义
QUALITY_THRESHOLDS = {
    'compliance_score': {
        'excellent': 90,
        'good': 80,
        'acceptable': 70,
        'warning': 60,
        'critical': 50
    },
    'metadata_compliance_rate': {
        'excellent': 99,
        'good': 95,
        'acceptable': 90,
        'warning': 80,
        'critical': 70
    },
    'responsibility_compliance_rate': {
        'excellent': 95,
        'good': 85,
        'acceptable': 75,
        'warning': 60,
        'critical': 50
    },
    'link_validity_rate': {
        'excellent': 99,
        'good': 95,
        'acceptable': 90,
        'warning': 85,
        'critical': 80
    },
    'deep_file_count': {
        'excellent': 20,
        'good': 50,
        'acceptable': 100,
        'warning': 150,
        'critical': 200
    }
}

def get_quality_level(value, threshold_name):
    """获取质量等级"""
    thresholds = QUALITY_THRESHOLDS.get(threshold_name, {})
    
    # 对于deep_file_count，值越小越好
    if threshold_name == 'deep_file_count':
        if value <= thresholds.get('excellent', 20):
            return 'excellent', '优秀'
        elif value <= thresholds.get('good', 50):
            return 'good', '良好'
        elif value <= thresholds.get('acceptable', 100):
            return 'acceptable', '可接受'
        elif value <= thresholds.get('warning', 150):
            return 'warning', '警告'
        else:
            return 'critical', '严重'
    else:
        # 对于其他指标，值越大越好
        if value >= thresholds.get('excellent', 90):
            return 'excellent', '优秀'
        elif value >= thresholds.get('good', 80):
            return 'good', '良好'
        elif value >= thresholds.get('acceptable', 70):
            return 'acceptable', '可接受'
        elif value >= thresholds.get('warning', 60):
            return 'warning', '警告'
        else:
            return 'critical', '严重'

def load_history():
    """加载历史数据"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def calculate_current_metrics():
    """计算当前质量指标"""
    print("=" * 80)
    print("计算当前质量指标")
    print("=" * 80)
    
    # 扫描所有文档
    total_files = 0
    files_with_metadata = 0
    files_with_responsibility = 0
    total_links = 0
    valid_links = 0
    deep_files = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        # 跳过audit_state目录
        if 'audit_state' in str(file_path):
            continue
        
        total_files += 1
        
        # 计算深度
        rel_path = file_path.relative_to(FACTOR_LIBRARY)
        depth = len(rel_path.parts) - 1
        if depth >= 4:
            deep_files += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查元数据
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end > 0:
                    yaml_content = content[3:yaml_end]
                    if 'module_id:' in yaml_content and 'version:' in yaml_content:
                        files_with_metadata += 1
                    if 'responsibility:' in yaml_content:
                        files_with_responsibility += 1
            
            # 检查链接
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, content):
                link_path = match.group(2)
                # 跳过外部链接和锚点链接
                if link_path.startswith('http') or link_path.startswith('#') or link_path.startswith('file:'):
                    continue
                
                total_links += 1
                
                # 检查链接是否有效
                if link_path.startswith('/'):
                    target_path = FACTOR_LIBRARY / link_path[1:]
                else:
                    target_path = file_path.parent / link_path
                
                try:
                    target_path = target_path.resolve()
                    if target_path.exists():
                        valid_links += 1
                except:
                    pass
        
        except Exception as e:
            pass
    
    # 计算比率
    metadata_compliance_rate = (files_with_metadata / total_files * 100) if total_files > 0 else 0
    responsibility_compliance_rate = (files_with_responsibility / total_files * 100) if total_files > 0 else 0
    link_validity_rate = (valid_links / total_links * 100) if total_links > 0 else 0
    
    # 计算合规分数
    compliance_score = (
        metadata_compliance_rate * 0.3 +
        responsibility_compliance_rate * 0.3 +
        link_validity_rate * 0.2 +
        (100 - min(deep_files, 100)) * 0.2
    )
    
    metrics = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_files': total_files,
        'compliance_score': round(compliance_score, 2),
        'metadata_compliance_rate': round(metadata_compliance_rate, 2),
        'responsibility_compliance_rate': round(responsibility_compliance_rate, 2),
        'link_validity_rate': round(link_validity_rate, 2),
        'deep_file_count': deep_files,
        'total_links': total_links,
        'valid_links': valid_links
    }
    
    print(f"\n当前质量指标:")
    print(f"  总文件数: {total_files}")
    print(f"  合规分数: {compliance_score:.2f}")
    print(f"  元数据符合率: {metadata_compliance_rate:.2f}%")
    print(f"  职责符合率: {responsibility_compliance_rate:.2f}%")
    print(f"  链接有效率: {link_validity_rate:.2f}%")
    print(f"  深层文件数: {deep_files}")
    
    return metrics

def generate_alerts(metrics):
    """生成预警"""
    print("\n" + "=" * 80)
    print("生成质量预警")
    print("=" * 80)
    
    alerts = []
    
    # 检查合规分数
    level, level_name = get_quality_level(metrics['compliance_score'], 'compliance_score')
    if level in ['warning', 'critical']:
        alerts.append({
            'type': 'compliance_score',
            'level': level,
            'level_name': level_name,
            'value': metrics['compliance_score'],
            'threshold': QUALITY_THRESHOLDS['compliance_score'][level],
            'message': f"合规分数 {metrics['compliance_score']:.2f} 处于{level_name}水平"
        })
    
    # 检查元数据符合率
    level, level_name = get_quality_level(metrics['metadata_compliance_rate'], 'metadata_compliance_rate')
    if level in ['warning', 'critical']:
        alerts.append({
            'type': 'metadata_compliance_rate',
            'level': level,
            'level_name': level_name,
            'value': metrics['metadata_compliance_rate'],
            'threshold': QUALITY_THRESHOLDS['metadata_compliance_rate'][level],
            'message': f"元数据符合率 {metrics['metadata_compliance_rate']:.2f}% 处于{level_name}水平"
        })
    
    # 检查职责符合率
    level, level_name = get_quality_level(metrics['responsibility_compliance_rate'], 'responsibility_compliance_rate')
    if level in ['warning', 'critical']:
        alerts.append({
            'type': 'responsibility_compliance_rate',
            'level': level,
            'level_name': level_name,
            'value': metrics['responsibility_compliance_rate'],
            'threshold': QUALITY_THRESHOLDS['responsibility_compliance_rate'][level],
            'message': f"职责符合率 {metrics['responsibility_compliance_rate']:.2f}% 处于{level_name}水平"
        })
    
    # 检查链接有效率
    level, level_name = get_quality_level(metrics['link_validity_rate'], 'link_validity_rate')
    if level in ['warning', 'critical']:
        alerts.append({
            'type': 'link_validity_rate',
            'level': level,
            'level_name': level_name,
            'value': metrics['link_validity_rate'],
            'threshold': QUALITY_THRESHOLDS['link_validity_rate'][level],
            'message': f"链接有效率 {metrics['link_validity_rate']:.2f}% 处于{level_name}水平"
        })
    
    # 检查深层文件数
    level, level_name = get_quality_level(metrics['deep_file_count'], 'deep_file_count')
    if level in ['warning', 'critical']:
        alerts.append({
            'type': 'deep_file_count',
            'level': level,
            'level_name': level_name,
            'value': metrics['deep_file_count'],
            'threshold': QUALITY_THRESHOLDS['deep_file_count'][level],
            'message': f"深层文件数 {metrics['deep_file_count']} 处于{level_name}水平"
        })
    
    # 打印预警
    if alerts:
        print(f"\n发现 {len(alerts)} 个预警:")
        for i, alert in enumerate(alerts, 1):
            print(f"\n{i}. [{alert['level_name']}] {alert['message']}")
            print(f"   当前值: {alert['value']}")
            print(f"   阈值: {alert['threshold']}")
    else:
        print("\n无预警，所有指标均处于良好水平")
    
    return alerts

def generate_report(metrics, alerts):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'QUALITY_ALERT_REPORT_{timestamp}.md'
    
    # 获取质量等级
    compliance_level, compliance_name = get_quality_level(metrics['compliance_score'], 'compliance_score')
    metadata_level, metadata_name = get_quality_level(metrics['metadata_compliance_rate'], 'metadata_compliance_rate')
    responsibility_level, responsibility_name = get_quality_level(metrics['responsibility_compliance_rate'], 'responsibility_compliance_rate')
    link_level, link_name = get_quality_level(metrics['link_validity_rate'], 'link_validity_rate')
    deep_level, deep_name = get_quality_level(metrics['deep_file_count'], 'deep_file_count')
    
    report_content = f"""---
module_id: QUALITY_ALERT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 预警报告
applicable_scope: 质量预警机制
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 质量预警报告

> **核心职责**: 记录质量预警的结果
> **职责边界**: 
> - [OK] 本文档负责：预警记录、问题统计、改进建议
> - [NO] 本文档不负责：问题修复、后续审计执行

---

## 预警概要

**预警时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**预警范围**: 全系统文档  
**预警方法**: 自动化检测  
**预警结论**: 发现 {len(alerts)} 个预警

---

## 质量指标

| 指标 | 当前值 | 等级 | 状态 |
|------|--------|------|------|
| **合规分数** | {metrics['compliance_score']:.2f} | {compliance_name} | {'✅' if compliance_level in ['excellent', 'good'] else '⚠️' if compliance_level == 'acceptable' else '❌'} |
| **元数据符合率** | {metrics['metadata_compliance_rate']:.2f}% | {metadata_name} | {'✅' if metadata_level in ['excellent', 'good'] else '⚠️' if metadata_level == 'acceptable' else '❌'} |
| **职责符合率** | {metrics['responsibility_compliance_rate']:.2f}% | {responsibility_name} | {'✅' if responsibility_level in ['excellent', 'good'] else '⚠️' if responsibility_level == 'acceptable' else '❌'} |
| **链接有效率** | {metrics['link_validity_rate']:.2f}% | {link_name} | {'✅' if link_level in ['excellent', 'good'] else '⚠️' if link_level == 'acceptable' else '❌'} |
| **深层文件数** | {metrics['deep_file_count']} | {deep_name} | {'✅' if deep_level in ['excellent', 'good'] else '⚠️' if deep_level == 'acceptable' else '❌'} |

---

## 预警详情

"""
    
    if alerts:
        for i, alert in enumerate(alerts, 1):
            report_content += f"### {i}. {alert['message']}\n\n"
            report_content += f"- **预警等级**: {alert['level_name']}\n"
            report_content += f"- **当前值**: {alert['value']}\n"
            report_content += f"- **阈值**: {alert['threshold']}\n\n"
    else:
        report_content += "无预警，所有指标均处于良好水平。\n"
    
    report_content += f"""

---

## 改进建议

### 立即行动

"""
    
    if alerts:
        for i, alert in enumerate(alerts, 1):
            if alert['type'] == 'compliance_score':
                report_content += f"{i}. [ ] 提升合规分数至 {QUALITY_THRESHOLDS['compliance_score']['good']} 分以上\n"
            elif alert['type'] == 'metadata_compliance_rate':
                report_content += f"{i}. [ ] 提升元数据符合率至 {QUALITY_THRESHOLDS['metadata_compliance_rate']['good']}% 以上\n"
            elif alert['type'] == 'responsibility_compliance_rate':
                report_content += f"{i}. [ ] 提升职责符合率至 {QUALITY_THRESHOLDS['responsibility_compliance_rate']['good']}% 以上\n"
            elif alert['type'] == 'link_validity_rate':
                report_content += f"{i}. [ ] 提升链接有效率至 {QUALITY_THRESHOLDS['link_validity_rate']['good']}% 以上\n"
            elif alert['type'] == 'deep_file_count':
                report_content += f"{i}. [ ] 减少深层文件数至 {QUALITY_THRESHOLDS['deep_file_count']['good']} 个以下\n"
    else:
        report_content += "1. [ ] 保持当前质量水平\n"
        report_content += "2. [ ] 持续优化文档质量\n"
    
    report_content += f"""

### 持续改进

1. [ ] 定期执行质量检查
2. [ ] 跟踪质量指标趋势
3. [ ] 持续优化文档质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，质量预警报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 计算当前质量指标
    metrics = calculate_current_metrics()
    
    # 生成预警
    alerts = generate_alerts(metrics)
    
    # 生成报告
    report_path = generate_report(metrics, alerts)
    
    print("\n" + "=" * 80)
    print("质量预警完成")
    print("=" * 80)
    print(f"预警数量: {len(alerts)}")
    print(f"报告位置: {report_path}")
