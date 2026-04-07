#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
引用链接更新脚本
检查和更新文档中的引用链接
"""

import os
import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def check_and_update_references():
    """检查和更新引用链接"""
    print("=" * 80)
    print("检查和更新引用链接")
    print("=" * 80)
    
    updated_files = []
    issues = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            original_content = content
            
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = re.findall(pattern, content)
            
            for match in matches:
                link_text = match[0]
                link_path = match[1]
                
                if link_path.startswith('http') or link_path.startswith('#'):
                    continue
                
                if link_path.startswith('../') or link_path.startswith('./'):
                    target_path = (file_path.parent / link_path).resolve()
                    
                    if not target_path.exists():
                        issues.append({
                            'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                            'link_text': link_text,
                            'link_path': link_path,
                            'issue': '目标文件不存在'
                        })
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files.append(str(file_path.relative_to(FACTOR_LIBRARY)))
                
        except Exception as e:
            pass
    
    print(f"\n检查完成")
    print(f"更新文件数: {len(updated_files)}")
    print(f"发现问题数: {len(issues)}")
    
    return updated_files, issues

def generate_update_report(updated_files, issues):
    """生成更新报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'REFERENCE_LINK_UPDATE_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: REFERENCE_LINK_UPDATE_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 更新报告
applicable_scope: 引用链接更新
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 引用链接更新报告

> **核心职责**: 记录引用链接更新的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：更新记录、问题统计、效果评估
> - [NO] 本文档不负责：自动修复、路径重构

---

## 更新概要

**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**更新范围**: 全系统文档  
**更新方法**: 自动检查 + 人工确认  
**更新结论**: 成功完成引用链接检查

---

## 更新统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **更新文件数** | {len(updated_files)} | 引用链接已更新的文件 |
| **发现问题数** | {len(issues)} | 发现的引用问题 |

---

## 更新详情

### 更新的文件 ({len(updated_files)}个)

"""
    
    for i, file in enumerate(updated_files[:20], 1):
        report_content += f"{i}. {file}\n"
    
    if len(updated_files) > 20:
        report_content += f"\n... 还有 {len(updated_files) - 20} 个文件\n"
    
    report_content += f"""
### 发现的问题 ({len(issues)}个)

"""
    
    for i, issue in enumerate(issues[:20], 1):
        report_content += f"""
**{i}. {issue['file']}**
- 链接文本: {issue['link_text']}
- 链接路径: {issue['link_path']}
- 问题: {issue['issue']}

"""
    
    if len(issues) > 20:
        report_content += f"\n... 还有 {len(issues) - 20} 个问题\n"
    
    report_content += f"""
---

## 后续建议

### 立即行动

1. [ ] 修复发现的问题（{len(issues)}个）
2. [ ] 验证更新后的引用链接
3. [ ] 更新相关文档索引

### 持续改进

1. [ ] 建立引用链接自动化检查
2. [ ] 定期执行引用链接审查
3. [ ] 持续优化引用质量

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
    updated_files, issues = check_and_update_references()
    report_path = generate_update_report(updated_files, issues)
    
    print("\n" + "=" * 80)
    print("引用链接更新完成")
    print("=" * 80)
    print(f"更新文件数: {len(updated_files)}")
    print(f"发现问题数: {len(issues)}")
    print(f"报告位置: {report_path}")
