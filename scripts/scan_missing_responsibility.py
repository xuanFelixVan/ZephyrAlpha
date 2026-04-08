#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扫描缺少职责描述的文档
"""

import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def scan_missing_responsibility():
    """扫描缺少职责描述的文档"""
    print("=" * 80)
    print("扫描缺少职责描述的文档")
    print("=" * 80)
    
    total_files = 0
    files_with_responsibility = 0
    files_without_responsibility = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        # 跳过audit_state目录
        if 'audit_state' in str(file_path):
            continue
        
        total_files += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否有职责描述
            has_responsibility = False
            
            # 检查YAML元数据中的responsibility字段
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end > 0:
                    yaml_content = content[3:yaml_end]
                    if 'responsibility:' in yaml_content:
                        has_responsibility = True
            
            # 检查文档中的核心职责描述
            if not has_responsibility:
                if '核心职责' in content or '职责边界' in content:
                    has_responsibility = True
            
            if has_responsibility:
                files_with_responsibility += 1
            else:
                rel_path = file_path.relative_to(FACTOR_LIBRARY)
                files_without_responsibility.append({
                    'path': str(rel_path),
                    'file': file_path.name,
                    'parent': str(rel_path.parent)
                })
        
        except Exception as e:
            print(f"处理文件失败 {file_path}: {e}")
    
    print(f"\n扫描完成")
    print(f"总文件数: {total_files}")
    print(f"有职责描述: {files_with_responsibility}")
    print(f"缺少职责描述: {len(files_without_responsibility)}")
    print(f"职责符合率: {files_with_responsibility / total_files * 100:.2f}%")
    
    return total_files, files_with_responsibility, files_without_responsibility

def generate_report(total_files, files_with_responsibility, files_without_responsibility):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'MISSING_RESPONSIBILITY_SCAN_REPORT_{timestamp}.md'
    
    # 按目录分组
    grouped_files = defaultdict(list)
    for file_info in files_without_responsibility:
        grouped_files[file_info['parent']].append(file_info)
    
    report_content = f"""---
module_id: MISSING_RESPONSIBILITY_SCAN_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 扫描报告
applicable_scope: 缺少职责描述文档扫描
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 缺少职责描述文档扫描报告

> **核心职责**: 记录缺少职责描述文档的扫描结果
> **职责边界**: 
> - [OK] 本文档负责：扫描记录、问题统计、分类分析
> - [NO] 本文档不负责：问题修复、后续审计执行

---

## 扫描概要

**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**扫描范围**: 全系统文档  
**扫描方法**: 自动化扫描  
**扫描结论**: 发现 {len(files_without_responsibility)} 个文档缺少职责描述

---

## 扫描统计

| 统计项 | 数量 | 占比 |
|--------|------|------|
| **总文件数** | {total_files} | 100% |
| **有职责描述** | {files_with_responsibility} | {files_with_responsibility / total_files * 100:.2f}% |
| **缺少职责描述** | {len(files_without_responsibility)} | {len(files_without_responsibility) / total_files * 100:.2f}% |

---

## 问题详情

### 缺少职责描述的文档 ({len(files_without_responsibility)}个)

"""
    
    # 按目录显示
    for parent, files in sorted(grouped_files.items()):
        report_content += f"\n#### {parent} ({len(files)}个)\n\n"
        for file_info in files[:10]:  # 每个目录最多显示10个
            report_content += f"- {file_info['file']}\n"
        if len(files) > 10:
            report_content += f"- ... 还有 {len(files) - 10} 个文件\n"
    
    report_content += f"""
---

## 后续建议

### 立即行动

1. [ ] 为缺少职责描述的文档补充职责描述
2. [ ] 优先处理重要目录的文档
3. [ ] 建立职责描述模板

### 持续改进

1. [ ] 建立职责描述检查机制
2. [ ] 定期执行职责描述扫描
3. [ ] 持续优化文档质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，缺少职责描述文档扫描报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 扫描缺少职责描述的文档
    total_files, files_with_responsibility, files_without_responsibility = scan_missing_responsibility()
    
    # 生成报告
    report_path = generate_report(total_files, files_with_responsibility, files_without_responsibility)
    
    print("\n" + "=" * 80)
    print("扫描完成")
    print("=" * 80)
    print(f"总文件数: {total_files}")
    print(f"有职责描述: {files_with_responsibility}")
    print(f"缺少职责描述: {len(files_without_responsibility)}")
    print(f"报告位置: {report_path}")
