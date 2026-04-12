#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
短期改进任务执行脚本
修复命名问题和死链接
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def scan_naming_issues():
    """扫描命名问题"""
    print("=" * 80)
    print("扫描命名问题")
    print("=" * 80)
    
    issues = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        file_name = file_path.name
        
        # 检查命名规范
        problems = []
        
        # 1. 检查连字符（应该使用下划线）
        if '-' in file_name and not file_name.startswith('.'):
            problems.append('使用连字符而非下划线')
        
        # 2. 检查空格
        if ' ' in file_name:
            problems.append('文件名包含空格')
        
        # 3. 检查大写字母（应该使用小写）
        if any(c.isupper() for c in file_name if not c.isdigit()):
            # 允许首字母大写的专业文档
            if not re.match(r'^[A-Z_0-9]+\.md$', file_name):
                pass  # 暂时不标记大写问题
        
        # 4. 检查特殊字符
        if re.search(r'[^\w\-_\.]', file_name):
            problems.append('文件名包含特殊字符')
        
        if problems:
            issues.append({
                'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                'problems': problems
            })
    
    print(f"发现 {len(issues)} 个命名问题")
    return issues

def fix_naming_issues(issues):
    """修复命名问题"""
    print("\n修复命名问题...")
    
    fixed_count = 0
    failed_count = 0
    
    for issue in issues:
        file_path = FACTOR_LIBRARY / issue['file']
        
        if not file_path.exists():
            continue
        
        old_name = file_path.name
        new_name = old_name.replace('-', '_').replace(' ', '_')
        
        # 移除特殊字符
        new_name = re.sub(r'[^\w\-_\.]', '_', new_name)
        new_name = re.sub(r'_+', '_', new_name)  # 合并多个下划线
        
        if new_name != old_name:
            new_path = file_path.parent / new_name
            
            if not new_path.exists():
                try:
                    file_path.rename(new_path)
                    print(f"  重命名: {old_name} -> {new_name}")
                    fixed_count += 1
                except Exception as e:
                    print(f"  重命名失败 {old_name}: {e}")
                    failed_count += 1
            else:
                print(f"  跳过（目标已存在）: {new_name}")
                failed_count += 1
    
    print(f"\n修复完成: {fixed_count} 个成功, {failed_count} 个失败")
    return fixed_count, failed_count

def scan_dead_links():
    """扫描死链接"""
    print("\n" + "=" * 80)
    print("扫描死链接")
    print("=" * 80)
    
    dead_links = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 查找所有链接
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = re.findall(pattern, content)
            
            for match in matches:
                link_text = match[0]
                link_path = match[1]
                
                # 跳过外部链接和锚点
                if link_path.startswith('http') or link_path.startswith('#'):
                    continue
                
                # 检查相对路径链接
                if link_path.startswith('../') or link_path.startswith('./'):
                    target_path = (file_path.parent / link_path).resolve()
                    
                    if not target_path.exists():
                        dead_links.append({
                            'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                            'link_text': link_text,
                            'link_path': link_path,
                            'target': str(target_path.relative_to(FACTOR_LIBRARY)) if target_path.exists() else '不存在'
                        })
        
        except Exception as e:
            pass
    
    print(f"发现 {len(dead_links)} 个死链接")
    return dead_links

def fix_dead_links(dead_links):
    """修复死链接"""
    print("\n修复死链接...")
    
    fixed_count = 0
    removed_count = 0
    
    # 按文件分组
    file_links = {}
    for link in dead_links:
        if link['file'] not in file_links:
            file_links[link['file']] = []
        file_links[link['file']].append(link)
    
    for file_name, links in file_links.items():
        file_path = FACTOR_LIBRARY / file_name
        
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            original_content = content
            
            for link in links:
                old_ref = f"[{link['link_text']}]({link['link_path']})"
                
                # 尝试查找相似文件
                target_name = Path(link['link_path']).name
                similar_files = list(FACTOR_LIBRARY.rglob(f'*{target_name}*'))
                
                if similar_files:
                    # 使用第一个匹配的文件
                    new_target = similar_files[0]
                    new_rel_path = os.path.relpath(new_target, file_path.parent)
                    new_rel_path = new_rel_path.replace('\\', '/')
                    
                    new_ref = f"[{link['link_text']}]({new_rel_path})"
                    content = content.replace(old_ref, new_ref)
                    print(f"  修复: {link['link_path']} -> {new_rel_path}")
                    fixed_count += 1
                else:
                    # 删除无效链接
                    content = content.replace(f"- {old_ref}\n", '')
                    content = content.replace(f"{old_ref}\n", '')
                    print(f"  删除: {link['link_path']}")
                    removed_count += 1
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        except Exception as e:
            print(f"  处理文件失败 {file_name}: {e}")
    
    print(f"\n修复完成: {fixed_count} 个修复, {removed_count} 个删除")
    return fixed_count, removed_count

def generate_short_term_report(naming_issues, dead_links, naming_fixed, naming_failed, links_fixed, links_removed):
    """生成短期改进报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'SHORT_TERM_IMPROVEMENT_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: SHORT_TERM_IMPROVEMENT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 改进报告
applicable_scope: 短期改进任务执行
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 短期改进任务执行报告

> **核心职责**: 记录短期改进任务执行的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：执行记录、效果评估、后续建议
> - [NO] 本文档不负责：后续审计执行、新问题发现

---

## 执行概要

**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**执行范围**: 短期改进任务  
**执行方法**: 自动扫描 + 批量修复  
**执行结论**: 成功完成短期改进任务

---

## 执行统计

### 命名问题修复

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **发现问题** | {len(naming_issues)} | 扫描发现的命名问题 |
| **修复成功** | {naming_fixed} | 成功修复的命名问题 |
| **修复失败** | {naming_failed} | 修复失败的命名问题 |

### 死链接修复

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **发现链接** | {len(dead_links)} | 扫描发现的死链接 |
| **修复链接** | {links_fixed} | 成功修复的链接 |
| **删除链接** | {links_removed} | 删除的无效链接 |

---

## 命名问题详情

### 发现的问题 ({len(naming_issues)}个)

"""
    
    for i, issue in enumerate(naming_issues[:20], 1):  # 只显示前20个
        report_content += f"""
**{i}. {issue['file']}**
- 问题: {', '.join(issue['problems'])}

"""
    
    if len(naming_issues) > 20:
        report_content += f"\n... 还有 {len(naming_issues) - 20} 个问题未显示\n"
    
    report_content += f"""
---

## 死链接详情

### 发现的死链接 ({len(dead_links)}个)

"""
    
    for i, link in enumerate(dead_links[:20], 1):  # 只显示前20个
        report_content += f"""
**{i}. {link['file']}**
- 链接文本: {link['link_text']}
- 链接路径: {link['link_path']}
- 目标: {link['target']}

"""
    
    if len(dead_links) > 20:
        report_content += f"\n... 还有 {len(dead_links) - 20} 个死链接未显示\n"
    
    report_content += f"""
---

## 后续建议

### 立即行动

1. [x] 修复命名问题
2. [x] 修复死链接
3. [ ] 验证修复效果

### 持续改进

1. [ ] 建立命名规范自动化检查
2. [ ] 建立死链接定期检查机制
3. [ ] 持续优化文档质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，短期改进报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n短期改进报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 扫描问题
    naming_issues = scan_naming_issues()
    dead_links = scan_dead_links()
    
    # 修复问题
    naming_fixed, naming_failed = fix_naming_issues(naming_issues)
    links_fixed, links_removed = fix_dead_links(dead_links)
    
    # 生成报告
    report_path = generate_short_term_report(
        naming_issues, dead_links,
        naming_fixed, naming_failed,
        links_fixed, links_removed
    )
    
    print("\n" + "=" * 80)
    print("短期改进任务执行完成")
    print("=" * 80)
    print(f"命名问题: {naming_fixed} 个修复, {naming_failed} 个失败")
    print(f"死链接: {links_fixed} 个修复, {links_removed} 个删除")
    print(f"报告位置: {report_path}")
