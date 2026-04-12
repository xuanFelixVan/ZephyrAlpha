#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
问题交接文档生成器
提取所有问题并生成交接文档
"""

import json
from pathlib import Path
from datetime import datetime

def generate_handover_document():
    root_dir = Path("D:/ZephyrAlpha")
    audit_report = root_dir / "docs/09_AUDIT/REPORTS/comprehensive_deep_audit_report.json"
    
    with open(audit_report, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    summary = data.get('summary', {})
    
    doc = f"""# 文档治理问题交接文档

## 📋 审计概要

**审计日期**: {summary.get('audit_date', 'N/A')}
**总文档数**: {summary.get('total_documents', 0)}
**总问题数**: {summary.get('total_issues', 0)}

---

## 📊 问题分布统计

### 按严重程度分布

| 严重程度 | 数量 |
|---------|------|
| **高严重性** | {summary.get('severity_distribution', {}).get('high', 0)} |
| **中严重性** | {summary.get('severity_distribution', {}).get('medium', 0)} |
| **低严重性** | {summary.get('severity_distribution', {}).get('low', 0)} |

---

### 按层级分布

| 层级 | 数量 |
|------|------|
| **L1 文件系统层** | {summary.get('layer_distribution', {}).get('L1', 0)} |
| **L2 文档内容层** | {summary.get('layer_distribution', {}).get('L2', 0)} |
| **L3 专业标准层** | {summary.get('layer_distribution', {}).get('L3', 0)} |

---

### 按类别分布

| 类别 | 数量 |
|------|------|
| **目录结构** | {summary.get('category_distribution', {}).get('目录结构', 0)} |
| **文件命名** | {summary.get('category_distribution', {}).get('文件命名', 0)} |
| **路径引用** | {summary.get('category_distribution', {}).get('路径引用', 0)} |
| **职责驱动** | {summary.get('category_distribution', {}).get('职责驱动', 0)} |
| **版本隔离** | {summary.get('category_distribution', {}).get('版本隔离', 0)} |
| **五大原则** | {summary.get('category_distribution', {}).get('五大原则', 0)} |
| **编号体系** | {summary.get('category_distribution', {}).get('编号体系', 0)} |

---

## 🔍 详细问题清单

"""
    
    layer1_issues = data.get('layer1_issues', [])
    layer2_issues = data.get('layer2_issues', [])
    layer3_issues = data.get('layer3_issues', [])
    
    doc += f"### L1 文件系统层问题 ({len(layer1_issues)}个)\n\n"
    
    for i, issue in enumerate(layer1_issues, 1):
        doc += f"""#### 问题 {i}

**文件位置**: `D:\\ZephyrAlpha\\docs\\{issue.get('file', 'N/A')}`

**问题类别**: {issue.get('category', 'N/A')}

**问题类型**: {issue.get('issue_type', 'N/A')}

**严重程度**: {issue.get('severity', 'N/A')}

**问题描述**: {issue.get('description', 'N/A')}

**建议操作**: {issue.get('suggestion', 'N/A')}

---

"""
    
    doc += f"### L2 文档内容层问题 ({len(layer2_issues)}个)\n\n"
    
    for i, issue in enumerate(layer2_issues, 1):
        doc += f"""#### 问题 {i}

**文件位置**: `D:\\ZephyrAlpha\\docs\\{issue.get('file', 'N/A')}`

**问题类别**: {issue.get('category', 'N/A')}

**问题类型**: {issue.get('issue_type', 'N/A')}

**严重程度**: {issue.get('severity', 'N/A')}

**问题描述**: {issue.get('description', 'N/A')}

**建议操作**: {issue.get('suggestion', 'N/A')}

---

"""
    
    doc += f"### L3 专业标准层问题 ({len(layer3_issues)}个)\n\n"
    
    for i, issue in enumerate(layer3_issues, 1):
        doc += f"""#### 问题 {i}

**文件位置**: `D:\\ZephyrAlpha\\docs\\{issue.get('file', 'N/A')}`

**问题类别**: {issue.get('category', 'N/A')}

**问题类型**: {issue.get('issue_type', 'N/A')}

**严重程度**: {issue.get('severity', 'N/A')}

**问题描述**: {issue.get('description', 'N/A')}

**建议操作**: {issue.get('suggestion', 'N/A')}

---

"""
    
    doc += f"""## 📝 重复文档检测

"""
    
    duplicates = data.get('duplicates', [])
    if duplicates:
        doc += f"发现 {len(duplicates)} 组重复文档\n\n"
        for i, dup in enumerate(duplicates, 1):
            doc += f"### 重复组 {i}\n\n"
            doc += f"**重复类型**: {dup.get('type', 'N/A')}\n\n"
            doc += f"**相似度**: {dup.get('similarity', 0):.2%}\n\n"
            doc += f"**文件列表**:\n"
            for file in dup.get('files', []):
                doc += f"- `D:\\ZephyrAlpha\\docs\\{file}`\n"
            doc += "\n---\n\n"
    else:
        doc += "未发现重复文档\n\n"
    
    doc += f"""## 💡 修复建议

### 优先级排序

**P0 - 立即修复（高严重性）**:
- 路径引用问题（7个死链接）
- 文件命名问题（116个旧架构命名残留）
- 职责驱动问题（257个职责不清）

**P1 - 短期改进（中严重性）**:
- 版本隔离问题（17个）
- 五大原则问题（10个）
- 编号体系问题（7个）

**P2 - 长期优化（低严重性）**:
- 目录结构问题（48个稀疏目录）

---

## 📊 审计质量声明

### 审计局限性

1. **内容语义分析**: 本次审计基于文本模式匹配，未进行深度语义分析
2. **链接可达性**: 仅检查文件存在性，未检查链接内容相关性
3. **职责边界**: 职责分析基于关键词提取，可能存在误判

### 质量保证

1. **三层审计**: 执行了完整的L1-L3三层审计
2. **全面覆盖**: 审计覆盖所有{summary.get('total_documents', 0)}个文档
3. **问题分类**: 所有问题按层级、类别、严重程度分类

---

## 🔗 相关文档

- [最终修复总结报告V8](FINAL_FIX_SUMMARY_V8_20260407.md)
- [最终审计报告](FINAL_AUDIT_REPORT_20260407.md)
- [第一轮深度审计报告](COMPREHENSIVE_DEEP_AUDIT_REPORT_20260407.md)

---

**文档生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**文档生成者**: 问题交接文档生成器
**文档版本**: v1.0.0
"""
    
    output_path = root_dir / "docs/09_AUDIT/REPORTS/ISSUE_HANDOVER_DOCUMENT_20260407.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc)
    
    print(f"✅ 问题交接文档已生成: {output_path}")
    print(f"📊 总问题数: {summary.get('total_issues', 0)}")
    print(f"   - L1层: {len(layer1_issues)}个")
    print(f"   - L2层: {len(layer2_issues)}个")
    print(f"   - L3层: {len(layer3_issues)}个")

if __name__ == "__main__":
    generate_handover_document()
