#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查归档文件是否被引用
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

# 要检查的归档文件列表
ARCHIVE_FILES = [
    '06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/IFIND_CONNECTOR/comprehensive_assessment_report.md',
    '06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/IFIND_CONNECTOR/INDEX.md',
    '06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/QMT_DATA_INTERFACE/comprehensive_assessment_report.md',
    '06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/QMT_DATA_INTERFACE/INDEX.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_1/INDEX.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_1/L1_CLEANER.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_1/L1_NORMALIZER.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_1/L1_VALIDATOR.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_11/INDEX.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_11/L11_QUANT_AGENT.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_11/L11_TEXT_DRIVER.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_11/LAYER_11_ARCHITECTURE.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_11/LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_11/LAYER_11_TOOL_INTERFACE_SPECIFICATION.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_9/INDEX.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_9/L9_ANOMALY_DETECTOR.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_9/L9_FACTOR_MINER.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_9/L9_FEATURE_OPTIMIZER.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_9/L9_HYPERPARAM_OPT.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_9/L9_MARKET_DETECTOR.md',
    '06_ARCHIVE/architecture_v4/module_designs/layer_9/L9_MODEL_ENSEMBLER.md',
]

def check_file_references():
    """检查归档文件是否被引用"""
    print("=" * 80)
    print("检查归档文件是否被引用")
    print("=" * 80)
    
    # 扫描所有文档
    all_files = []
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        # 跳过audit_state目录
        if 'audit_state' in str(file_path):
            continue
        
        all_files.append(file_path)
    
    print(f"\n总文件数: {len(all_files)}")
    
    # 检查每个归档文件的引用情况
    reference_results = {}
    
    for archive_file in ARCHIVE_FILES:
        # 提取文件名（不含路径）
        file_name = Path(archive_file).name
        file_stem = Path(archive_file).stem
        
        # 搜索引用
        references = []
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查是否引用了该文件
                if file_name in content or file_stem in content or archive_file in content:
                    rel_path = file_path.relative_to(FACTOR_LIBRARY)
                    # 排除自身引用
                    if str(rel_path) != archive_file:
                        references.append(str(rel_path))
            
            except Exception as e:
                pass
        
        reference_results[archive_file] = references
        
        if references:
            print(f"\n{archive_file}")
            print(f"  被引用次数: {len(references)}")
            for ref in references[:5]:  # 只显示前5个引用
                print(f"    - {ref}")
            if len(references) > 5:
                print(f"    ... 还有 {len(references) - 5} 个引用")
    
    # 统计
    files_with_references = sum(1 for refs in reference_results.values() if refs)
    files_without_references = sum(1 for refs in reference_results.values() if not refs)
    
    print(f"\n检查完成")
    print(f"有引用的文件: {files_with_references}")
    print(f"无引用的文件: {files_without_references}")
    
    return reference_results, files_with_references, files_without_references

def generate_report(reference_results, files_with_references, files_without_references):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'ARCHIVE_FILES_REFERENCE_CHECK_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: ARCHIVE_FILES_REFERENCE_CHECK_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 检查报告
applicable_scope: 归档文件引用检查
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 归档文件引用检查报告

> **核心职责**: 记录归档文件引用检查的结果
> **职责边界**: 
> - [OK] 本文档负责：检查记录、引用统计、删除建议
> - [NO] 本文档不负责：文件删除执行、后续审计执行

---

## 检查概要

**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**检查范围**: 归档文件  
**检查方法**: 自动化检查  
**检查结论**: 检查归档文件是否被其他文档引用

---

## 检查统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **归档文件总数** | {len(reference_results)} | 待检查的归档文件 |
| **有引用的文件** | {files_with_references} | 被其他文档引用 |
| **无引用的文件** | {files_without_references} | 可安全删除 |

---

## 引用详情

"""
    
    for archive_file, references in reference_results.items():
        if references:
            report_content += f"### {archive_file}\n\n"
            report_content += f"**被引用次数**: {len(references)}\n\n"
            report_content += f"**引用文档**:\n"
            for ref in references:
                report_content += f"- {ref}\n"
            report_content += "\n"
    
    report_content += f"""

---

## 删除建议

### 可安全删除的文件 ({files_without_references}个)

以下文件无任何引用，可安全删除：

"""
    
    for archive_file, references in reference_results.items():
        if not references:
            report_content += f"- {archive_file}\n"
    
    report_content += f"""

### 需谨慎删除的文件 ({files_with_references}个)

以下文件有引用，删除前需确认：

"""
    
    for archive_file, references in reference_results.items():
        if references:
            report_content += f"- {archive_file} (被引用{len(references)}次)\n"
    
    report_content += f"""

---

## 改进建议

### 立即行动

1. [ ] 删除无引用的归档文件
2. [ ] 更新引用链接
3. [ ] 验证删除效果

### 持续改进

1. [ ] 建立归档文件管理机制
2. [ ] 定期执行引用检查
3. [ ] 持续优化文档结构

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，归档文件引用检查报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 检查归档文件引用
    reference_results, files_with_references, files_without_references = check_file_references()
    
    # 生成报告
    report_path = generate_report(reference_results, files_with_references, files_without_references)
    
    print("\n" + "=" * 80)
    print("归档文件引用检查完成")
    print("=" * 80)
    print(f"归档文件总数: {len(reference_results)}")
    print(f"有引用的文件: {files_with_references}")
    print(f"无引用的文件: {files_without_references}")
    print(f"报告位置: {report_path}")
