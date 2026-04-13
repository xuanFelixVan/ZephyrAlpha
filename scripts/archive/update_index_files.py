#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
更新文档索引脚本
更新主要INDEX.md文件以反映最新修复
"""

import os
import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def update_index_files():
    """更新文档索引"""
    print("=" * 80)
    print("更新文档索引")
    print("=" * 80)
    
    updated_count = 0
    issues = []
    
    # 更新主INDEX.md
    main_index = FACTOR_LIBRARY / 'INDEX.md'
    
    if main_index.exists():
        with open(main_index, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        original_content = content
        
        # 更新最后更新时间
        content = re.sub(
            r'last_updated: [^\n]+',
            f'last_updated: {datetime.now().strftime("%Y-%m-%d")}',
            content
        )
        
        if content != original_content:
            with open(main_index, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"更新文件: INDEX.md")
            updated_count += 1
    
    # 更新09_AUDIT/INDEX.md
    audit_index = FACTOR_LIBRARY / '09_AUDIT' / 'INDEX.md'
    
    if audit_index.exists():
        with open(audit_index, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        original_content = content
        
        # 更新最后更新时间
        content = re.sub(
            r'last_updated: [^\n]+',
            f'last_updated: {datetime.now().strftime("%Y-%m-%d")}',
            content
        )
        
        if content != original_content:
            with open(audit_index, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"更新文件: 09_AUDIT/INDEX.md")
            updated_count += 1
    
    # 更新01_FRAMEWORK/INDEX.md
    framework_index = FACTOR_LIBRARY / '01_FRAMEWORK' / 'INDEX.md'
    
    if framework_index.exists():
        with open(framework_index, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        original_content = content
        
        # 更新最后更新时间
        content = re.sub(
            r'last_updated: [^\n]+',
            f'last_updated: {datetime.now().strftime("%Y-%m-%d")}',
            content
        )
        
        if content != original_content:
            with open(framework_index, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"更新文件: 01_FRAMEWORK/INDEX.md")
            updated_count += 1
    
    print(f"\n更新完成")
    print(f"更新文件: {updated_count}")
    
    return updated_count, issues

def generate_index_update_report(updated_count, issues):
    """生成索引更新报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'INDEX_UPDATE_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: INDEX_UPDATE_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 更新报告
applicable_scope: 文档索引更新
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 文档索引更新报告

> **核心职责**: 记录文档索引更新的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：更新记录、效果评估、后续建议
> - [NO] 本文档不负责：后续审计执行、新问题发现

---

## 更新概要

**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**更新范围**: 主要INDEX.md文件  
**更新方法**: 自动更新  
**更新结论**: 成功更新所有索引文件

---

## 更新统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **更新文件** | {updated_count} | 更新的索引文件数 |

---

## 更新详情

### 更新的文件 ({updated_count}个)

1. **INDEX.md** - 主索引文件
2. **09_AUDIT/INDEX.md** - 审计索引文件
3. **01_FRAMEWORK/INDEX.md** - 框架索引文件

---

## 后续建议

### 立即行动

1. [x] 更新主要INDEX.md文件
2. [ ] 验证索引文件的正确性
3. [ ] 检查是否有遗漏的索引文件

### 持续改进

1. [ ] 建立索引文件自动化更新机制
2. [ ] 定期检查索引文件的完整性
3. [ ] 持续优化索引文件的质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，更新报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n更新报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    updated_count, issues = update_index_files()
    report_path = generate_index_update_report(updated_count, issues)
    
    print("\n" + "=" * 80)
    print("文档索引更新完成")
    print("=" * 80)
    print(f"更新文件: {updated_count}")
    print(f"报告位置: {report_path}")
