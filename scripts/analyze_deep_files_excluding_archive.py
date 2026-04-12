#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
重新分析深层文件 - 排除归档文件
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
        
        # 判断文件类型
        file_type = 'unknown'
        if is_archive:
            file_type = 'archive'
        elif is_backup:
            file_type = 'backup'
        elif is_temp:
            file_type = 'temp'
        elif is_index:
            file_type = 'index'
        elif is_readme:
            file_type = 'readme'
        elif is_blueprint:
            file_type = 'blueprint'
        elif is_report:
            file_type = 'report'
        elif is_state:
            file_type = 'state'
        elif has_content:
            file_type = 'content'
        
        return {
            'is_archive': is_archive,
            'is_backup': is_backup,
            'is_temp': is_temp,
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
            'file_type': file_type
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'file_type': 'error'
        }

def analyze_deep_files_excluding_archive():
    """分析深层文件 - 排除归档文件"""
    print("=" * 80)
    print("分析深层文件 - 排除归档文件")
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
        
        # 排除归档文件
        if not analysis.get('is_archive', False):
            deep_files_analysis.append({
                'path': str(rel_path),
                'depth': depth,
                'analysis': analysis
            })
    
    # 统计
    total_count = len(deep_files_analysis)
    files_by_type = defaultdict(int)
    for file_info in deep_files_analysis:
        file_type = file_info['analysis'].get('file_type', 'unknown')
        files_by_type[file_type] += 1
    
    print(f"\n分析完成")
    print(f"非归档深层文件: {total_count}")
    print(f"\n文件类型分布:")
    for file_type, count in sorted(files_by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"  {file_type}: {count}")
    
    return deep_files_analysis, total_count, files_by_type

def generate_report(deep_files_analysis, total_count, files_by_type):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'DEEP_FILES_ANALYSIS_EXCLUDING_ARCHIVE_REPORT_{timestamp}.md'
    
    # 按深度分组
    files_by_depth = defaultdict(list)
    for file_info in deep_files_analysis:
        files_by_depth[file_info['depth']].append(file_info)
    
    report_content = f"""---
module_id: DEEP_FILES_ANALYSIS_EXCLUDING_ARCHIVE_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 分析报告
applicable_scope: 深层文件分析（排除归档）
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 深层文件分析报告（排除归档）

> **核心职责**: 记录深层文件分析的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：分析记录、问题统计、改进建议
> - [NO] 本文档不负责：文件删除执行、后续审计执行

---

## 分析概要

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**分析范围**: 全系统文档（排除归档文件）  
**分析方法**: 自动化分析  
**分析结论**: 识别非归档深层文件

---

## 分析统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **非归档深层文件** | {total_count} | 深度≥4的非归档文件 |

---

## 文件类型分布

"""
    
    for file_type, count in sorted(files_by_type.items(), key=lambda x: x[1], reverse=True):
        report_content += f"- **{file_type}**: {count}个文件\n"
    
    report_content += f"""

---

## 深度分布

"""
    
    for depth in sorted(files_by_depth.keys(), reverse=True):
        count = len(files_by_depth[depth])
        report_content += f"- **深度{depth}**: {count}个文件\n"
    
    report_content += f"""

---

## 文件列表（按类型分组）

"""
    
    # 按类型分组
    files_by_type_grouped = defaultdict(list)
    for file_info in deep_files_analysis:
        file_type = file_info['analysis'].get('file_type', 'unknown')
        files_by_type_grouped[file_type].append(file_info)
    
    for file_type in sorted(files_by_type_grouped.keys()):
        files = files_by_type_grouped[file_type]
        report_content += f"### {file_type} ({len(files)}个)\n\n"
        
        for i, file_info in enumerate(files[:20], 1):  # 只显示前20个
            path = file_info['path']
            depth = file_info['depth']
            report_content += f"{i}. {path} (深度{depth})\n"
        
        if len(files) > 20:
            report_content += f"... 还有 {len(files) - 20} 个文件\n"
        
        report_content += "\n"
    
    report_content += f"""

---

## 改进建议

### 立即行动

1. [ ] 分析非归档深层文件
2. [ ] 优化目录结构
3. [ ] 验证优化效果

### 持续改进

1. [ ] 建立深层文件监控机制
2. [ ] 定期执行深度检查
3. [ ] 持续优化目录结构

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，深层文件分析报告（排除归档） | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 分析深层文件
    deep_files_analysis, total_count, files_by_type = analyze_deep_files_excluding_archive()
    
    # 生成报告
    report_path = generate_report(deep_files_analysis, total_count, files_by_type)
    
    print("\n" + "=" * 80)
    print("深层文件分析完成（排除归档）")
    print("=" * 80)
    print(f"非归档深层文件: {total_count}")
    print(f"报告位置: {report_path}")
