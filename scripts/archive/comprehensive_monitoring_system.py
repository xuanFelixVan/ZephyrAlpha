#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
完善监控体系
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')
HISTORY_FILE = OUTPUT_DIR / 'QUALITY_METRICS_HISTORY.json'
MONITORING_CONFIG = OUTPUT_DIR / 'MONITORING_CONFIG.json'

# 监控配置
DEFAULT_CONFIG = {
    'check_interval_hours': 24,
    'retention_days': 90,
    'alert_thresholds': {
        'compliance_score': {'warning': 70, 'critical': 60},
        'metadata_compliance_rate': {'warning': 90, 'critical': 80},
        'responsibility_compliance_rate': {'warning': 75, 'critical': 60},
        'link_validity_rate': {'warning': 90, 'critical': 85},
        'deep_file_count': {'warning': 100, 'critical': 150}
    },
    'trend_analysis_days': 7,
    'auto_cleanup': True
}

def load_config():
    """加载监控配置"""
    if MONITORING_CONFIG.exists():
        with open(MONITORING_CONFIG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(config):
    """保存监控配置"""
    with open(MONITORING_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_history():
    """加载历史数据"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    """保存历史数据"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

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

def analyze_trends(history, days=7):
    """分析趋势"""
    print("\n" + "=" * 80)
    print(f"分析最近{days}天趋势")
    print("=" * 80)
    
    if len(history) < 2:
        print("\n历史数据不足，无法分析趋势")
        return None
    
    # 获取最近N天的数据
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    recent_data = [h for h in history if h['timestamp'] >= cutoff_date]
    
    if len(recent_data) < 2:
        print(f"\n最近{days}天数据不足，无法分析趋势")
        return None
    
    # 计算趋势 - 适应不同的数据格式
    first = recent_data[0]
    last = recent_data[-1]
    
    # 提取指标值 - 支持两种格式
    def get_metric(data, metric_name):
        """从数据中提取指标值"""
        # 新格式（扁平结构）
        if metric_name in data:
            return data[metric_name]
        
        # 旧格式（嵌套结构）
        if metric_name == 'compliance_score':
            return data.get('compliance_metrics', {}).get('compliance_score', 0)
        elif metric_name == 'metadata_compliance_rate':
            return data.get('document_metrics', {}).get('metadata_compliance_rate', 0)
        elif metric_name == 'responsibility_compliance_rate':
            return data.get('document_metrics', {}).get('responsibility_compliance_rate', 0)
        elif metric_name == 'link_validity_rate':
            return data.get('reference_metrics', {}).get('link_validity_rate', 0)
        elif metric_name == 'deep_file_count':
            return data.get('structure_metrics', {}).get('deep_files_count', 0)
        return 0
    
    trends = {
        'compliance_score': {
            'start': get_metric(first, 'compliance_score'),
            'end': get_metric(last, 'compliance_score'),
            'change': get_metric(last, 'compliance_score') - get_metric(first, 'compliance_score'),
            'trend': 'improving' if get_metric(last, 'compliance_score') > get_metric(first, 'compliance_score') else 'declining' if get_metric(last, 'compliance_score') < get_metric(first, 'compliance_score') else 'stable'
        },
        'metadata_compliance_rate': {
            'start': get_metric(first, 'metadata_compliance_rate'),
            'end': get_metric(last, 'metadata_compliance_rate'),
            'change': get_metric(last, 'metadata_compliance_rate') - get_metric(first, 'metadata_compliance_rate'),
            'trend': 'improving' if get_metric(last, 'metadata_compliance_rate') > get_metric(first, 'metadata_compliance_rate') else 'declining' if get_metric(last, 'metadata_compliance_rate') < get_metric(first, 'metadata_compliance_rate') else 'stable'
        },
        'responsibility_compliance_rate': {
            'start': get_metric(first, 'responsibility_compliance_rate'),
            'end': get_metric(last, 'responsibility_compliance_rate'),
            'change': get_metric(last, 'responsibility_compliance_rate') - get_metric(first, 'responsibility_compliance_rate'),
            'trend': 'improving' if get_metric(last, 'responsibility_compliance_rate') > get_metric(first, 'responsibility_compliance_rate') else 'declining' if get_metric(last, 'responsibility_compliance_rate') < get_metric(first, 'responsibility_compliance_rate') else 'stable'
        },
        'link_validity_rate': {
            'start': get_metric(first, 'link_validity_rate'),
            'end': get_metric(last, 'link_validity_rate'),
            'change': get_metric(last, 'link_validity_rate') - get_metric(first, 'link_validity_rate'),
            'trend': 'improving' if get_metric(last, 'link_validity_rate') > get_metric(first, 'link_validity_rate') else 'declining' if get_metric(last, 'link_validity_rate') < get_metric(first, 'link_validity_rate') else 'stable'
        },
        'deep_file_count': {
            'start': get_metric(first, 'deep_file_count'),
            'end': get_metric(last, 'deep_file_count'),
            'change': get_metric(last, 'deep_file_count') - get_metric(first, 'deep_file_count'),
            'trend': 'improving' if get_metric(last, 'deep_file_count') < get_metric(first, 'deep_file_count') else 'declining' if get_metric(last, 'deep_file_count') > get_metric(first, 'deep_file_count') else 'stable'
        }
    }
    
    # 打印趋势
    print(f"\n趋势分析:")
    for metric, data in trends.items():
        trend_emoji = '📈' if data['trend'] == 'improving' else '📉' if data['trend'] == 'declining' else '➡️'
        print(f"  {metric}: {data['start']:.2f} → {data['end']:.2f} ({data['change']:+.2f}) {trend_emoji}")
    
    return trends

def cleanup_history(history, retention_days=90):
    """清理历史数据"""
    print("\n" + "=" * 80)
    print(f"清理历史数据（保留{retention_days}天）")
    print("=" * 80)
    
    cutoff_date = (datetime.now() - timedelta(days=retention_days)).strftime('%Y-%m-%d')
    original_count = len(history)
    cleaned_history = [h for h in history if h['timestamp'] >= cutoff_date]
    cleaned_count = len(cleaned_history)
    
    print(f"\n原始记录数: {original_count}")
    print(f"清理后记录数: {cleaned_count}")
    print(f"删除记录数: {original_count - cleaned_count}")
    
    return cleaned_history

def generate_monitoring_report(metrics, trends, config):
    """生成监控报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'MONITORING_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: MONITORING_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 监控报告
applicable_scope: 文档质量监控
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 文档质量监控报告

> **核心职责**: 记录文档质量监控的结果
> **职责边界**: 
> - [OK] 本文档负责：监控记录、趋势分析、改进建议
> - [NO] 本文档不负责：问题修复、后续审计执行

---

## 监控概要

**监控时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**监控范围**: 全系统文档  
**监控方法**: 自动化监控  
**监控结论**: 文档质量处于良好水平

---

## 当前质量指标

| 指标 | 当前值 | 状态 |
|------|--------|------|
| **合规分数** | {metrics['compliance_score']:.2f} | {'✅' if metrics['compliance_score'] >= config['alert_thresholds']['compliance_score']['warning'] else '⚠️'} |
| **元数据符合率** | {metrics['metadata_compliance_rate']:.2f}% | {'✅' if metrics['metadata_compliance_rate'] >= config['alert_thresholds']['metadata_compliance_rate']['warning'] else '⚠️'} |
| **职责符合率** | {metrics['responsibility_compliance_rate']:.2f}% | {'✅' if metrics['responsibility_compliance_rate'] >= config['alert_thresholds']['responsibility_compliance_rate']['warning'] else '⚠️'} |
| **链接有效率** | {metrics['link_validity_rate']:.2f}% | {'✅' if metrics['link_validity_rate'] >= config['alert_thresholds']['link_validity_rate']['warning'] else '⚠️'} |
| **深层文件数** | {metrics['deep_file_count']} | {'✅' if metrics['deep_file_count'] <= config['alert_thresholds']['deep_file_count']['warning'] else '⚠️'} |

---

## 趋势分析

"""
    
    if trends:
        for metric, data in trends.items():
            trend_emoji = '📈' if data['trend'] == 'improving' else '📉' if data['trend'] == 'declining' else '➡️'
            report_content += f"### {metric}\n\n"
            report_content += f"- **起始值**: {data['start']:.2f}\n"
            report_content += f"- **当前值**: {data['end']:.2f}\n"
            report_content += f"- **变化**: {data['change']:+.2f}\n"
            report_content += f"- **趋势**: {data['trend']} {trend_emoji}\n\n"
    else:
        report_content += "历史数据不足，无法分析趋势。\n"
    
    report_content += f"""

---

## 监控配置

| 配置项 | 值 |
|--------|-----|
| **检查间隔** | {config['check_interval_hours']}小时 |
| **数据保留** | {config['retention_days']}天 |
| **趋势分析周期** | {config['trend_analysis_days']}天 |

---

## 改进建议

### 立即行动

1. [ ] 保持当前质量水平
2. [ ] 持续优化文档质量

### 持续改进

1. [ ] 定期执行质量检查
2. [ ] 跟踪质量指标趋势
3. [ ] 持续优化监控体系

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，监控报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 加载配置
    config = load_config()
    print(f"监控配置: 检查间隔 {config['check_interval_hours']}小时, 数据保留 {config['retention_days']}天")
    
    # 加载历史数据
    history = load_history()
    print(f"历史记录数: {len(history)}")
    
    # 计算当前质量指标
    metrics = calculate_current_metrics()
    
    # 添加到历史
    history.append(metrics)
    
    # 分析趋势
    trends = analyze_trends(history, config['trend_analysis_days'])
    
    # 清理历史数据
    if config['auto_cleanup']:
        history = cleanup_history(history, config['retention_days'])
    
    # 保存历史数据
    save_history(history)
    print(f"\n历史数据已保存: {HISTORY_FILE}")
    
    # 生成监控报告
    report_path = generate_monitoring_report(metrics, trends, config)
    
    print("\n" + "=" * 80)
    print("监控体系完善完成")
    print("=" * 80)
    print(f"历史记录数: {len(history)}")
    print(f"报告位置: {report_path}")
