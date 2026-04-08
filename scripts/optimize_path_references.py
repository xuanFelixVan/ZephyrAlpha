#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路径引用优化脚本
优化10个需要优化的文档的路径引用
"""

import os
import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def optimize_path_references():
    """优化路径引用"""
    print("=" * 80)
    print("优化路径引用")
    print("=" * 80)
    
    optimized_count = 0
    issues = []
    
    problem_files = [
        '09_AUDIT/REPORTS/PHASE3_CORE_DOCS_COMPLETION_20260407.md',
        '00_OVERVIEW/INDEX.md',
        '05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/NEW_EMPLOYEE_ONBOARDING_GUIDE.md',
        '09_AUDIT/REPORTS/EXCELLENCE_STANDARD_ACHIEVEMENT_REPORT_20260402.md',
        '11_STRATEGIC_DECISION/INDEX.md',
        '05_IMPLEMENTATION/04_OPERATIONS/DOCUMENT_GOVERNANCE_CONTINUOUS_IMPROVEMENT.md',
        '01_FRAMEWORK/INDEX.md',
        '05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/MARKET_PARTICIPANT_SIMULATION_SPEC.md',
        '09_AUDIT/STATE/FOLLOW_UP_ACTION_REPORT_20260407_151323.md',
        '09_AUDIT/STATE/LAYER26_DEEP_AUDIT_REPORT_20260407_145027.md'
    ]
    
    for rel_path in problem_files:
        file_path = FACTOR_LIBRARY / rel_path
        
        if not file_path.exists():
            print(f"文件不存在: {rel_path}")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            original_content = content
            original_count = content.count('../')
            
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = list(re.finditer(pattern, content))
            
            for match in reversed(matches):
                link_text = match.group(1)
                link_path = match.group(2)
                
                if link_path.startswith('http') or link_path.startswith('#'):
                    continue
                
                if link_path.startswith('../'):
                    parts = link_path.split('/')
                    new_parts = []
                    skip_next = False
                    
                    for i, part in enumerate(parts):
                        if skip_next:
                            skip_next = False
                            continue
                        
                        if part == '..' and i + 1 < len(parts) and parts[i + 1] == '..':
                            new_parts.append('..')
                            skip_next = True
                        else:
                            new_parts.append(part)
                    
                    if len(new_parts) < len(parts):
                        new_path = '/'.join(new_parts)
                        old_ref = match.group(0)
                        new_ref = f'[{link_text}]({new_path})'
                        content = content[:match.start()] + new_ref + content[match.end():]
                        
                        issues.append({
                            'file': rel_path,
                            'link_text': link_text,
                            'old_path': link_path,
                            'new_path': new_path,
                            'action': 'optimized'
                        })
                        optimized_count += 1
            
            new_count = content.count('../')
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"优化文件: {rel_path}")
                print(f"  ../引用: {original_count} -> {new_count}")
                
        except Exception as e:
            print(f"处理文件失败 {rel_path}: {e}")
    
    print(f"\n优化完成")
    print(f"优化引用: {optimized_count}")
    
    return optimized_count, issues

def generate_optimization_report(optimized_count, issues):
    """生成优化报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'PATH_OPTIMIZATION_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: PATH_OPTIMIZATION_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 优化报告
applicable_scope: 路径引用优化
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 路径引用优化报告

> **核心职责**: 记录路径引用优化的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：优化记录、效果评估、后续建议
> - [NO] 本文档不负责：后续审计执行、新问题发现

---

## 优化概要

**优化时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**优化范围**: 10个需要优化的文档  
**优化方法**: 自动简化 + 智能优化  
**优化结论**: 成功优化部分路径引用

---

## 优化统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **优化引用** | {optimized_count} | 成功优化的引用 |
| **处理文件** | 10 | 处理的文件数 |

---

## 优化详情

### 成功优化的引用 ({optimized_count}个)

"""
    
    for i, issue in enumerate(issues[:20], 1):
        report_content += f"""
**{i}. {issue['file']}**
- 链接文本: {issue['link_text']}
- 原路径: {issue['old_path']}
- 新路径: {issue['new_path']}
- 操作: 优化

"""
    
    if len(issues) > 20:
        report_content += f"\n... 还有 {len(issues) - 20} 个优化\n"
    
    report_content += f"""
---

## 后续建议

### 立即行动

1. [ ] 验证优化后的引用链接
2. [ ] 更新相关文档索引
3. [ ] 检查是否有新的路径引用问题

### 持续改进

1. [ ] 建立路径引用自动化检查
2. [ ] 定期执行路径引用审查
3. [ ] 持续优化路径引用质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，优化报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n优化报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    optimized_count, issues = optimize_path_references()
    report_path = generate_optimization_report(optimized_count, issues)
    
    print("\n" + "=" * 80)
    print("路径引用优化完成")
    print("=" * 80)
    print(f"优化引用: {optimized_count}")
    print(f"报告位置: {report_path}")
