#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
元数据完整性检查脚本
检查文档元数据是否符合标准
"""

import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

# 必需字段
REQUIRED_FIELDS = ['module_id', 'version', 'status', 'created_date', 'owner']

# 推荐字段
RECOMMENDED_FIELDS = ['responsibility', 'standard_type', 'applicable_scope', 'compliance_level', 'parent_document']

# 有效状态值
VALID_STATUSES = ['Active', 'Draft', 'Deprecated', 'Archived']

# 版本号格式
VERSION_PATTERN = r'^\d+\.\d+\.\d+$'

# 日期格式
DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'

def check_metadata_completeness():
    """检查元数据完整性"""
    print("=" * 80)
    print("检查元数据完整性")
    print("=" * 80)
    
    total_files = 0
    complete_files = 0
    incomplete_files = []
    no_metadata_files = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        # 跳过audit_state目录
        if 'audit_state' in str(file_path):
            continue
        
        total_files += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否有YAML元数据
            if not content.startswith('---'):
                rel_path = file_path.relative_to(FACTOR_LIBRARY)
                no_metadata_files.append({
                    'path': str(rel_path),
                    'file': file_path.name,
                    'parent': str(rel_path.parent)
                })
                continue
            
            yaml_end = content.find('---', 3)
            if yaml_end < 0:
                rel_path = file_path.relative_to(FACTOR_LIBRARY)
                no_metadata_files.append({
                    'path': str(rel_path),
                    'file': file_path.name,
                    'parent': str(rel_path.parent)
                })
                continue
            
            yaml_content = content[3:yaml_end]
            
            # 检查必需字段
            missing_required = []
            for field in REQUIRED_FIELDS:
                if f'{field}:' not in yaml_content:
                    missing_required.append(field)
            
            # 检查推荐字段
            missing_recommended = []
            for field in RECOMMENDED_FIELDS:
                if f'{field}:' not in yaml_content:
                    missing_recommended.append(field)
            
            # 检查字段值格式
            format_issues = []
            
            # 检查version格式
            version_match = re.search(r'version:\s*(.+)', yaml_content)
            if version_match:
                version_value = version_match.group(1).strip()
                if not re.match(VERSION_PATTERN, version_value):
                    format_issues.append(f'version格式错误: {version_value}')
            
            # 检查status值
            status_match = re.search(r'status:\s*(.+)', yaml_content)
            if status_match:
                status_value = status_match.group(1).strip()
                if status_value not in VALID_STATUSES:
                    format_issues.append(f'status值无效: {status_value}')
            
            # 检查日期格式
            for date_field in ['created_date', 'last_updated']:
                date_match = re.search(rf'{date_field}:\s*(.+)', yaml_content)
                if date_match:
                    date_value = date_match.group(1).strip()
                    if not re.match(DATE_PATTERN, date_value):
                        format_issues.append(f'{date_field}格式错误: {date_value}')
            
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            
            if missing_required or format_issues:
                incomplete_files.append({
                    'path': str(rel_path),
                    'file': file_path.name,
                    'parent': str(rel_path.parent),
                    'missing_required': missing_required,
                    'missing_recommended': missing_recommended,
                    'format_issues': format_issues
                })
            else:
                complete_files += 1
        
        except Exception as e:
            print(f"处理文件失败 {file_path}: {e}")
    
    print(f"\n检查完成")
    print(f"总文件数: {total_files}")
    print(f"完整元数据: {complete_files}")
    print(f"不完整元数据: {len(incomplete_files)}")
    print(f"无元数据: {len(no_metadata_files)}")
    print(f"元数据符合率: {complete_files / total_files * 100:.2f}%")
    
    return total_files, complete_files, incomplete_files, no_metadata_files

def generate_report(total_files, complete_files, incomplete_files, no_metadata_files):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'METADATA_COMPLETENESS_CHECK_REPORT_{timestamp}.md'
    
    # 按目录分组
    grouped_incomplete = defaultdict(list)
    for file_info in incomplete_files:
        grouped_incomplete[file_info['parent']].append(file_info)
    
    grouped_no_metadata = defaultdict(list)
    for file_info in no_metadata_files:
        grouped_no_metadata[file_info['parent']].append(file_info)
    
    report_content = f"""---
module_id: METADATA_COMPLETENESS_CHECK_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 检查报告
applicable_scope: 元数据完整性检查
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 元数据完整性检查报告

> **核心职责**: 记录元数据完整性检查的结果
> **职责边界**: 
> - [OK] 本文档负责：检查记录、问题统计、改进建议
> - [NO] 本文档不负责：问题修复、后续审计执行

---

## 检查概要

**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**检查范围**: 全系统文档  
**检查方法**: 自动化检查  
**检查结论**: 发现 {len(incomplete_files) + len(no_metadata_files)} 个文档存在元数据问题

---

## 检查统计

| 统计项 | 数量 | 占比 |
|--------|------|------|
| **总文件数** | {total_files} | 100% |
| **完整元数据** | {complete_files} | {complete_files / total_files * 100:.2f}% |
| **不完整元数据** | {len(incomplete_files)} | {len(incomplete_files) / total_files * 100:.2f}% |
| **无元数据** | {len(no_metadata_files)} | {len(no_metadata_files) / total_files * 100:.2f}% |

---

## 问题详情

### 不完整元数据文档 ({len(incomplete_files)}个)

"""
    
    # 显示前20个不完整元数据文档
    for i, file_info in enumerate(incomplete_files[:20], 1):
        report_content += f"""
**{i}. {file_info['path']}**
"""
        if file_info['missing_required']:
            report_content += f"- 缺少必需字段: {', '.join(file_info['missing_required'])}\n"
        if file_info['missing_recommended']:
            report_content += f"- 缺少推荐字段: {', '.join(file_info['missing_recommended'])}\n"
        if file_info['format_issues']:
            report_content += f"- 格式问题: {', '.join(file_info['format_issues'])}\n"
    
    if len(incomplete_files) > 20:
        report_content += f"\n... 还有 {len(incomplete_files) - 20} 个文档\n"
    
    report_content += f"""
### 无元数据文档 ({len(no_metadata_files)}个)

"""
    
    # 显示前20个无元数据文档
    for i, file_info in enumerate(no_metadata_files[:20], 1):
        report_content += f"{i}. {file_info['path']}\n"
    
    if len(no_metadata_files) > 20:
        report_content += f"\n... 还有 {len(no_metadata_files) - 20} 个文档\n"
    
    report_content += f"""
---

## 改进建议

### 立即行动

1. [ ] 为无元数据文档添加元数据
2. [ ] 补充缺失的必需字段
3. [ ] 修复格式问题

### 持续改进

1. [ ] 建立元数据检查机制
2. [ ] 定期执行元数据检查
3. [ ] 持续优化文档质量

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，元数据完整性检查报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 检查元数据完整性
    total_files, complete_files, incomplete_files, no_metadata_files = check_metadata_completeness()
    
    # 生成报告
    report_path = generate_report(total_files, complete_files, incomplete_files, no_metadata_files)
    
    print("\n" + "=" * 80)
    print("元数据完整性检查完成")
    print("=" * 80)
    print(f"总文件数: {total_files}")
    print(f"完整元数据: {complete_files}")
    print(f"不完整元数据: {len(incomplete_files)}")
    print(f"无元数据: {len(no_metadata_files)}")
    print(f"报告位置: {report_path}")
