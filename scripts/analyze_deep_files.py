#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析深层文件 - 识别可删除/重构文件
"""

import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

def get_file_depth(file_path):
    """获取文件深度"""
    rel_path = file_path.relative_to(FACTOR_LIBRARY)
    return len(rel_path.parts) - 1

def analyze_file_content(file_path):
    """分析文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否是归档文件
        is_archive = 'archive' in str(file_path).lower() or '_archive' in str(file_path).lower()
        
        # 检查是否是备份文件
        is_backup = 'backup' in str(file_path).lower() or '_backup' in str(file_path).lower()
        
        # 检查是否是临时文件
        is_temp = 'temp' in str(file_path).lower() or 'tmp' in str(file_path).lower()
        
        # 检查是否是重复文件（文件名包含日期）
        has_date = bool(re.search(r'\d{8}', file_path.stem))
        
        # 检查是否是版本文件
        is_version = bool(re.search(r'_v\d+|_v\d+\.\d+|_v\d+\.\d+\.\d+', file_path.stem, re.IGNORECASE))
        
        # 检查文件大小
        file_size = len(content)
        
        # 检查是否有实质内容（超过500字符）
        has_content = file_size > 500
        
        # 检查是否是INDEX文件
        is_index = file_path.stem.upper() == 'INDEX'
        
        # 检查是否是README文件
        is_readme = file_path.stem.upper() == 'README'
        
        # 检查是否是蓝图文件
        is_blueprint = 'BLUEPRINT' in file_path.stem.upper()
        
        # 检查是否是报告文件
        is_report = 'REPORT' in file_path.stem.upper()
        
        # 检查是否是审计文件
        is_audit = 'AUDIT' in str(file_path).upper()
        
        # 检查是否是状态文件
        is_state = 'STATE' in str(file_path).upper()
        
        # 检查是否有元数据
        has_metadata = content.startswith('---')
        
        # 检查是否有职责描述
        has_responsibility = 'responsibility:' in content
        
        # 检查创建日期
        created_date_match = re.search(r'created_date:\s*(\d{4}-\d{2}-\d{2})', content)
        created_date = created_date_match.group(1) if created_date_match else None
        
        # 检查最后更新日期
        last_updated_match = re.search(r'last_updated:\s*(\d{4}-\d{2}-\d{2})', content)
        last_updated = last_updated_match.group(1) if last_updated_match else None
        
        # 判断是否可以删除
        can_delete = False
        delete_reason = []
        
        if is_archive:
            can_delete = True
            delete_reason.append('归档文件')
        
        if is_backup:
            can_delete = True
            delete_reason.append('备份文件')
        
        if is_temp:
            can_delete = True
            delete_reason.append('临时文件')
        
        if has_date and is_report:
            can_delete = True
            delete_reason.append('带日期的报告文件（可能是重复的）')
        
        if is_version and not has_content:
            can_delete = True
            delete_reason.append('版本文件且无实质内容')
        
        # 判断是否需要重构
        need_refactor = False
        refactor_reason = []
        
        if file_path.parent.name == 'archive':
            need_refactor = True
            refactor_reason.append('在archive目录中')
        
        if file_path.parent.name == '_archive':
            need_refactor = True
            refactor_reason.append('在_archive目录中')
        
        if file_path.parent.name == 'backup':
            need_refactor = True
            refactor_reason.append('在backup目录中')
        
        return {
            'is_archive': is_archive,
            'is_backup': is_backup,
            'is_temp': is_temp,
            'has_date': has_date,
            'is_version': is_version,
            'file_size': file_size,
            'has_content': has_content,
            'is_index': is_index,
            'is_readme': is_readme,
            'is_blueprint': is_blueprint,
            'is_report': is_report,
            'is_audit': is_audit,
            'is_state': is_state,
            'has_metadata': has_metadata,
            'has_responsibility': has_responsibility,
            'created_date': created_date,
            'last_updated': last_updated,
            'can_delete': can_delete,
            'delete_reason': delete_reason,
            'need_refactor': need_refactor,
            'refactor_reason': refactor_reason
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'can_delete': False,
            'delete_reason': [],
            'need_refactor': False,
            'refactor_reason': []
        }

def analyze_deep_files():
    """分析深层文件"""
    print("=" * 80)
    print("分析深层文件")
    print("=" * 80)
    
    # 扫描所有文档
    all_files = []
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        # 跳过audit_state目录
        if 'audit_state' in str(file_path):
            continue
        
        depth = get_file_depth(file_path)
        if depth >= 4:
            all_files.append({
                'path': file_path,
                'depth': depth
            })
    
    print(f"\n深层文件总数（深度≥4）: {len(all_files)}")
    
    # 分析每个文件
    deep_files_analysis = []
    for file_info in all_files:
        file_path = file_info['path']
        depth = file_info['depth']
        
        rel_path = file_path.relative_to(FACTOR_LIBRARY)
        analysis = analyze_file_content(file_path)
        
        deep_files_analysis.append({
            'path': str(rel_path),
            'depth': depth,
            'analysis': analysis
        })
    
    # 统计
    can_delete_count = sum(1 for f in deep_files_analysis if f['analysis'].get('can_delete', False))
    need_refactor_count = sum(1 for f in deep_files_analysis if f['analysis'].get('need_refactor', False))
    
    print(f"\n分析完成")
    print(f"可删除文件: {can_delete_count}")
    print(f"需重构文件: {need_refactor_count}")
    
    return deep_files_analysis, can_delete_count, need_refactor_count

def generate_report(deep_files_analysis, can_delete_count, need_refactor_count):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'DEEP_FILES_ANALYSIS_REPORT_{timestamp}.md'
    
    # 按深度分组
    files_by_depth = defaultdict(list)
    for file_info in deep_files_analysis:
        files_by_depth[file_info['depth']].append(file_info)
    
    # 可删除文件列表
    can_delete_files = [f for f in deep_files_analysis if f['analysis'].get('can_delete', False)]
    
    # 需重构文件列表
    need_refactor_files = [f for f in deep_files_analysis if f['analysis'].get('need_refactor', False)]
    
    report_content = f"""---
module_id: DEEP_FILES_ANALYSIS_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 分析报告
applicable_scope: 深层文件分析
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 深层文件分析报告

> **核心职责**: 记录深层文件分析的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：分析记录、问题统计、改进建议
> - [NO] 本文档不负责：文件删除执行、后续审计执行

---

## 分析概要

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**分析范围**: 全系统文档  
**分析方法**: 自动化分析  
**分析结论**: 识别出可删除和需重构的深层文件

---

## 分析统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **深层文件总数** | {len(deep_files_analysis)} | 深度≥4的文件 |
| **可删除文件** | {can_delete_count} | 归档、备份、临时文件 |
| **需重构文件** | {need_refactor_count} | 需要移动或重构的文件 |

---

## 深度分布

"""
    
    for depth in sorted(files_by_depth.keys(), reverse=True):
        count = len(files_by_depth[depth])
        report_content += f"- **深度{depth}**: {count}个文件\n"
    
    report_content += f"""

---

## 可删除文件列表 ({can_delete_count}个)

"""
    
    for i, file_info in enumerate(can_delete_files, 1):
        path = file_info['path']
        depth = file_info['depth']
        reasons = file_info['analysis'].get('delete_reason', [])
        reasons_str = '、'.join(reasons)
        
        report_content += f"**{i}. {path}**\n"
        report_content += f"- 深度: {depth}\n"
        report_content += f"- 删除理由: {reasons_str}\n\n"
    
    report_content += f"""

---

## 需重构文件列表 ({need_refactor_count}个)

"""
    
    for i, file_info in enumerate(need_refactor_files, 1):
        path = file_info['path']
        depth = file_info['depth']
        reasons = file_info['analysis'].get('refactor_reason', [])
        reasons_str = '、'.join(reasons)
        
        report_content += f"**{i}. {path}**\n"
        report_content += f"- 深度: {depth}\n"
        report_content += f"- 重构理由: {reasons_str}\n\n"
    
    report_content += f"""

---

## 改进建议

### 立即行动

1. [ ] 删除归档、备份、临时文件
2. [ ] 重构深层目录结构
3. [ ] 验证删除效果

### 持续改进

1. [ ] 建立深层文件监控机制
2. [ ] 定期执行深度检查
3. [ ] 持续优化目录结构

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，深层文件分析报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path, can_delete_files

if __name__ == '__main__':
    # 分析深层文件
    deep_files_analysis, can_delete_count, need_refactor_count = analyze_deep_files()
    
    # 生成报告
    report_path, can_delete_files = generate_report(deep_files_analysis, can_delete_count, need_refactor_count)
    
    print("\n" + "=" * 80)
    print("深层文件分析完成")
    print("=" * 80)
    print(f"深层文件总数: {len(deep_files_analysis)}")
    print(f"可删除文件: {can_delete_count}")
    print(f"需重构文件: {need_refactor_count}")
    print(f"报告位置: {report_path}")
