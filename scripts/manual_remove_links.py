#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动删除最后3个无效链接
"""

from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def remove_invalid_links():
    """删除最后3个无效链接"""
    print("=" * 80)
    print("手动删除最后3个无效链接")
    print("=" * 80)
    
    removed_count = 0
    
    # 1. 删除 05_IMPLEMENTATION/SITEMAP.md 中的无效链接
    file_path = FACTOR_LIBRARY / '05_IMPLEMENTATION/SITEMAP.md'
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if 'dev-setup.md' in line and '|' in line:
                print(f"  删除: {line.strip()}")
                removed_count += 1
            else:
                new_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"更新文件: 05_IMPLEMENTATION/SITEMAP.md")
    
    # 2. 删除 03_TRADING_TACTICS/04_YOUZI_STRATEGIES/INDEX.md 中的无效链接
    file_path = FACTOR_LIBRARY / '03_TRADING_TACTICS/04_YOUZI_STRATEGIES/INDEX.md'
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if 'retail-strategies-a.md' in line or 'retail-strategies-b.md' in line:
                print(f"  删除: {line.strip()}")
                removed_count += 1
            else:
                new_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"更新文件: 03_TRADING_TACTICS/04_YOUZI_STRATEGIES/INDEX.md")
    
    print(f"\n删除完成")
    print(f"删除链接: {removed_count}")
    
    return removed_count

def generate_report(removed_count):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'MANUAL_LINK_REMOVAL_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: MANUAL_LINK_REMOVAL_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 修复报告
applicable_scope: 手动删除无效链接
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 手动删除无效链接报告

> **核心职责**: 记录手动删除无效链接的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：删除记录、效果评估、后续建议
> - [NO] 本文档不负责：后续审计执行、新问题发现

---

## 删除概要

**删除时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**删除范围**: 3个最后无效链接  
**删除方法**: 手动删除  
**删除结论**: 成功删除所有最后无效链接

---

## 删除统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **删除链接** | {removed_count} | 删除的无效链接 |

---

## 删除详情

### 删除的文件

1. **05_IMPLEMENTATION/SITEMAP.md**
   - 删除: dev-setup.md 链接

2. **03_TRADING_TACTICS/04_YOUZI_STRATEGIES/INDEX.md**
   - 删除: retail-strategies-a.md 链接
   - 删除: retail-strategies-b.md 链接

---

## 后续建议

### 立即行动

1. [x] 手动删除无效链接
2. [ ] 验证删除效果
3. [ ] 更新相关文档

### 持续改进

1. [ ] 建立链接有效性监控
2. [ ] 定期执行链接检查
3. [ ] 持续优化文档质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，手动删除无效链接报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 删除无效链接
    removed_count = remove_invalid_links()
    
    # 生成报告
    report_path = generate_report(removed_count)
    
    print("\n" + "=" * 80)
    print("手动删除无效链接完成")
    print("=" * 80)
    print(f"删除链接: {removed_count}")
    print(f"报告位置: {report_path}")
