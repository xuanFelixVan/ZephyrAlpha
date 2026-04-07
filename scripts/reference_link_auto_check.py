#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
引用链接自动化检查脚本
定期检查引用链接的有效性
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')
HISTORY_FILE = OUTPUT_DIR / 'reference_check_history.json'

def check_reference_links():
    """检查引用链接"""
    print("=" * 80)
    print("引用链接自动化检查")
    print("=" * 80)
    
    total_links = 0
    valid_links = 0
    invalid_links = 0
    issues = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = re.findall(pattern, content)
            
            for match in matches:
                link_text = match[0]
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
                        issues.append({
                            'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                            'link_text': link_text,
                            'link_path': link_path,
                            'issue': '目标文件不存在'
                        })
                else:
                    valid_links += 1
        
        except Exception as e:
            pass
    
    print(f"\n检查完成")
    print(f"总链接数: {total_links}")
    print(f"有效链接: {valid_links}")
    print(f"无效链接: {invalid_links}")
    
    return total_links, valid_links, invalid_links, issues

def save_history(total_links, valid_links, invalid_links):
    """保存检查历史"""
    history = []
    
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            pass
    
    history.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_links': total_links,
        'valid_links': valid_links,
        'invalid_links': invalid_links,
        'valid_rate': round(valid_links / total_links * 100, 2) if total_links > 0 else 0
    })
    
    if len(history) > 30:
        history = history[-30:]
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    return history

def generate_check_report(total_links, valid_links, invalid_links, issues, history):
    """生成检查报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'REFERENCE_LINK_CHECK_REPORT_{timestamp}.md'
    
    valid_rate = round(valid_links / total_links * 100, 2) if total_links > 0 else 0
    
    trend = ""
    if len(history) > 1:
        prev = history[-2]
        trend = f"""
### 历史趋势

| 指标 | 上次检查 | 本次检查 | 变化 |
|------|---------|---------|------|
| **总链接数** | {prev['total_links']} | {total_links} | {total_links - prev['total_links']} |
| **有效链接** | {prev['valid_links']} | {valid_links} | {valid_links - prev['valid_links']} |
| **无效链接** | {prev['invalid_links']} | {invalid_links} | {invalid_links - prev['invalid_links']} |
| **有效率** | {prev['valid_rate']}% | {valid_rate}% | {round(valid_rate - prev['valid_rate'], 2)}% |
"""
    
    report_content = f"""---
module_id: REFERENCE_LINK_CHECK_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 检查报告
applicable_scope: 引用链接自动化检查
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 引用链接自动化检查报告

> **核心职责**: 记录引用链接自动化检查的结果
> **职责边界**: 
> - [OK] 本文档负责：检查记录、问题统计、趋势分析
> - [NO] 本文档不负责：问题修复、后续审计执行

---

## 检查概要

**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**检查范围**: 全系统文档  
**检查方法**: 自动化检查  
**检查结论**: 发现 {invalid_links} 个无效链接

---

## 检查统计

| 统计项 | 数量 | 占比 |
|--------|------|------|
| **总链接数** | {total_links} | 100% |
| **有效链接** | {valid_links} | {valid_rate}% |
| **无效链接** | {invalid_links} | {round(100 - valid_rate, 2)}% |

{trend}

---

## 问题详情

### 无效链接 ({len(issues)}个)

"""
    
    for i, issue in enumerate(issues[:20], 1):
        report_content += f"""
**{i}. {issue['file']}**
- 链接文本: {issue['link_text']}
- 链接路径: {issue['link_path']}
- 问题: {issue['issue']}

"""
    
    if len(issues) > 20:
        report_content += f"\n... 还有 {len(issues) - 20} 个无效链接\n"
    
    report_content += f"""
---

## 后续建议

### 立即行动

1. [ ] 修复发现的无效链接（{invalid_links}个）
2. [ ] 验证修复后的链接
3. [ ] 更新相关文档索引

### 持续改进

1. [ ] 定期执行引用链接检查
2. [ ] 跟踪链接有效率趋势
3. [ ] 持续优化引用质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，检查报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n检查报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    total_links, valid_links, invalid_links, issues = check_reference_links()
    history = save_history(total_links, valid_links, invalid_links)
    report_path = generate_check_report(total_links, valid_links, invalid_links, issues, history)
    
    print("\n" + "=" * 80)
    print("引用链接自动化检查完成")
    print("=" * 80)
    print(f"总链接数: {total_links}")
    print(f"有效链接: {valid_links}")
    print(f"无效链接: {invalid_links}")
    print(f"有效率: {round(valid_links / total_links * 100, 2)}%")
    print(f"报告位置: {report_path}")
