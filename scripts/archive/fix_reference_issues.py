#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
引用问题智能修复脚本
自动修复31个引用问题
"""

import os
import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def find_similar_file(target_name, search_dir):
    """查找相似文件"""
    target_name_lower = target_name.lower()
    
    for file_path in search_dir.rglob('*.md'):
        if file_path.name.lower() == target_name_lower:
            return file_path
    
    for file_path in search_dir.rglob('*.md'):
        if target_name_lower.replace('_', '') in file_path.name.lower().replace('_', ''):
            return file_path
    
    return None

def fix_reference_issues():
    """修复引用问题"""
    print("=" * 80)
    print("修复引用问题")
    print("=" * 80)
    
    fixed_count = 0
    removed_count = 0
    issues = []
    
    problem_files = [
        '01_FRAMEWORK/PERFORMANCE_BENCHMARK_FRAMEWORK.md',
        '06_ARCHIVE/ARCHIVE_README.md',
        '08_KNOWLEDGE/KNOWLEDGE_BASE_CASE_STUDIES.md',
        '08_KNOWLEDGE/KNOWLEDGE_TRANSFER_SYSTEM.md',
        '09_AUDIT/INDEX_AUDIT.md',
        '09_AUDIT/RISK_MANAGEMENT_DOCUMENT_INDEX.md'
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
            
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = list(re.finditer(pattern, content))
            
            for match in reversed(matches):
                link_text = match.group(1)
                link_path = match.group(2)
                
                if link_path.startswith('http') or link_path.startswith('#'):
                    continue
                
                if link_path.startswith('../') or link_path.startswith('./'):
                    target_path = (file_path.parent / link_path).resolve()
                    
                    if not target_path.exists():
                        target_name = Path(link_path).name
                        
                        similar_file = find_similar_file(target_name, FACTOR_LIBRARY)
                        
                        if similar_file:
                            new_rel_path = os.path.relpath(similar_file, file_path.parent)
                            new_rel_path = new_rel_path.replace('\\', '/')
                            
                            old_ref = match.group(0)
                            new_ref = f'[{link_text}]({new_rel_path})'
                            content = content[:match.start()] + new_ref + content[match.end():]
                            
                            issues.append({
                                'file': rel_path,
                                'link_text': link_text,
                                'old_path': link_path,
                                'new_path': new_rel_path,
                                'action': 'fixed'
                            })
                            fixed_count += 1
                            print(f"  修复: {link_path} -> {new_rel_path}")
                        else:
                            issues.append({
                                'file': rel_path,
                                'link_text': link_text,
                                'old_path': link_path,
                                'new_path': None,
                                'action': 'removed'
                            })
                            removed_count += 1
                            print(f"  无法找到: {link_path}")
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"更新文件: {rel_path}")
                
        except Exception as e:
            print(f"处理文件失败 {rel_path}: {e}")
    
    print(f"\n修复完成")
    print(f"修复引用: {fixed_count}")
    print(f"无法修复: {removed_count}")
    
    return fixed_count, removed_count, issues

def generate_fix_report(fixed_count, removed_count, issues):
    """生成修复报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'REFERENCE_FIX_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: REFERENCE_FIX_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 修复报告
applicable_scope: 引用问题修复
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 引用问题修复报告

> **核心职责**: 记录引用问题修复的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：修复记录、效果评估、后续建议
> - [NO] 本文档不负责：后续审计执行、新问题发现

---

## 修复概要

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复范围**: 31个引用问题  
**修复方法**: 自动查找 + 智能修复  
**修复结论**: 成功修复部分引用问题

---

## 修复统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **修复引用** | {fixed_count} | 成功修复的引用 |
| **无法修复** | {removed_count} | 无法找到目标文件的引用 |
| **总处理数** | {fixed_count + removed_count} | 处理的引用总数 |

---

## 修复详情

### 成功修复的引用 ({fixed_count}个)

"""
    
    fixed_issues = [i for i in issues if i['action'] == 'fixed']
    for i, issue in enumerate(fixed_issues[:20], 1):
        report_content += f"""
**{i}. {issue['file']}**
- 链接文本: {issue['link_text']}
- 原路径: {issue['old_path']}
- 新路径: {issue['new_path']}
- 操作: 修复

"""
    
    if len(fixed_issues) > 20:
        report_content += f"\n... 还有 {len(fixed_issues) - 20} 个修复\n"
    
    report_content += f"""
### 无法修复的引用 ({removed_count}个)

"""
    
    removed_issues = [i for i in issues if i['action'] == 'removed']
    for i, issue in enumerate(removed_issues[:20], 1):
        report_content += f"""
**{i}. {issue['file']}**
- 链接文本: {issue['link_text']}
- 原路径: {issue['old_path']}
- 操作: 需要人工处理

"""
    
    if len(removed_issues) > 20:
        report_content += f"\n... 还有 {len(removed_issues) - 20} 个需要人工处理\n"
    
    report_content += f"""
---

## 后续建议

### 立即行动

1. [ ] 人工处理无法修复的引用（{removed_count}个）
2. [ ] 验证修复后的引用链接
3. [ ] 更新相关文档索引

### 持续改进

1. [ ] 建立引用链接自动化检查
2. [ ] 定期执行引用链接审查
3. [ ] 持续优化引用质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，修复报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n修复报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    fixed_count, removed_count, issues = fix_reference_issues()
    report_path = generate_fix_report(fixed_count, removed_count, issues)
    
    print("\n" + "=" * 80)
    print("引用问题修复完成")
    print("=" * 80)
    print(f"修复引用: {fixed_count}")
    print(f"无法修复: {removed_count}")
    print(f"报告位置: {report_path}")
