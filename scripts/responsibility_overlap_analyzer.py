#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
战略决策层职责重叠精确分析脚本
分析目标：识别真正的职责重叠，而非概念重叠
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json

class ResponsibilityOverlapAnalyzer:
    def __init__(self, docs_root):
        self.docs_root = Path(docs_root)
        self.strategic_dir = self.docs_root / "11_STRATEGIC_DECISION"
        self.documents = []
        self.responsibilities = defaultdict(list)
        self.true_overlaps = []
        
    def run_analysis(self):
        """执行精确分析"""
        print("=" * 80)
        print("战略决策层职责重叠精确分析")
        print("=" * 80)
        print(f"分析目录: {self.strategic_dir}")
        print()
        
        # 1. 扫描所有文档
        print("1. 扫描所有文档...")
        self.scan_documents()
        
        # 2. 提取职责信息
        print("\n2. 提取职责信息...")
        self.extract_responsibilities()
        
        # 3. 分析真正的职责重叠
        print("\n3. 分析真正的职责重叠...")
        self.analyze_true_overlaps()
        
        # 4. 生成分析报告
        print("\n4. 生成分析报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("分析完成")
        print("=" * 80)
        
    def scan_documents(self):
        """扫描所有文档"""
        md_files = list(self.strategic_dir.rglob("*.md"))
        
        for md_file in md_files:
            if 'archive' in str(md_file).lower():
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取YAML头部
                yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                yaml_header = yaml_match.group(1) if yaml_match else ""
                
                # 提取标题
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else md_file.stem
                
                # 提取核心职责（支持中英文冒号）
                responsibility_match = re.search(r'核心职责[：:]\s*(.+?)(?:\n|$)', content)
                responsibility = responsibility_match.group(1).strip() if responsibility_match else ""
                
                # 提取职责边界
                boundary_match = re.search(r'本文档负责[：:]\s*(.+?)(?:\n|$)', content)
                boundary = boundary_match.group(1).strip() if boundary_match else ""
                
                # 提取module_id
                module_id_match = re.search(r'module_id:\s*(.+?)(?:\n|$)', yaml_header)
                module_id = module_id_match.group(1).strip() if module_id_match else ""
                
                doc_info = {
                    'path': str(md_file.relative_to(self.docs_root)),
                    'filename': md_file.name,
                    'title': title,
                    'responsibility': responsibility,
                    'boundary': boundary,
                    'module_id': module_id,
                    'yaml_header': yaml_header,
                    'content': content,
                    'is_index': md_file.name == 'INDEX.md'
                }
                
                self.documents.append(doc_info)
                
            except Exception as e:
                print(f"  ⚠️ 读取文件失败: {md_file.name} - {str(e)}")
        
        print(f"  ✅ 扫描完成: {len(self.documents)} 个文档")
        
    def extract_responsibilities(self):
        """提取职责信息"""
        for doc in self.documents:
            if doc['is_index']:
                continue
            
            # 提取核心职责
            if doc['responsibility']:
                self.responsibilities[doc['responsibility']].append({
                    'filename': doc['filename'],
                    'title': doc['title'],
                    'module_id': doc['module_id'],
                    'boundary': doc['boundary']
                })
        
        print(f"  ✅ 提取完成: {len(self.responsibilities)} 个不同职责")
        
    def analyze_true_overlaps(self):
        """分析真正的职责重叠"""
        overlap_count = 0
        
        # 检查相同职责的文档
        for responsibility, docs in self.responsibilities.items():
            if len(docs) > 1:
                # 检查是否是真正的职责重叠
                # 如果职责描述完全相同，且文档不是索引文档，则认为是真正的重叠
                overlap_count += 1
                self.true_overlaps.append({
                    'responsibility': responsibility,
                    'documents': docs,
                    'count': len(docs)
                })
        
        print(f"  ✅ 分析完成: 发现 {overlap_count} 个真正的职责重叠")
        
    def generate_report(self):
        """生成分析报告"""
        report_path = self.docs_root / "05_IMPLEMENTATION" / "07_OPERATIONS" / "audit_state" / "STRATEGIC_DECISION_RESPONSIBILITY_OVERLAP_ANALYSIS_20260407.md"
        
        # 统计文档
        total_docs = len(self.documents)
        docs_with_responsibility = len([d for d in self.documents if d['responsibility']])
        docs_without_responsibility = total_docs - docs_with_responsibility
        
        report = f"""# 战略决策层职责重叠精确分析报告

> **分析时间**: {self.get_current_time()}
> **分析范围**: 11_STRATEGIC_DECISION（战略决策层）
> **分析方法**: 职责描述精确匹配 + 职责边界分析

---

## 📊 一、分析概览

### 1.1 文档统计

| 统计项 | 数量 |
|--------|------|
| **文档总数** | {total_docs} |
| **有职责描述** | {docs_with_responsibility} |
| **无职责描述** | {docs_without_responsibility} |
| **职责清晰度** | {docs_with_responsibility / total_docs * 100:.1f}% |

### 1.2 职责重叠统计

| 统计项 | 数量 |
|--------|------|
| **不同职责数** | {len(self.responsibilities)} |
| **职责重叠数** | {len(self.true_overlaps)} |

---

## 🔍 二、职责重叠详情

"""
        
        if self.true_overlaps:
            for idx, overlap in enumerate(self.true_overlaps, 1):
                report += f"""
### 重叠 {idx}: {overlap['responsibility']}

**重叠文档数**: {overlap['count']}个

| 文档名称 | 标题 | module_id | 职责边界 |
|----------|------|-----------|----------|
"""
                for doc in overlap['documents']:
                    report += f"| {doc['filename']} | {doc['title'][:30]} | {doc['module_id']} | {doc['boundary'][:30] if doc['boundary'] else '未定义'} |\n"
                
                report += "\n**分析结论**: 这些文档的职责描述完全相同，需要明确职责边界或合并文档。\n\n"
        else:
            report += "✅ 未发现真正的职责重叠问题\n\n"
        
        report += f"""
---

## 📋 三、文档职责清单

### 3.1 根目录文档

| 文档名称 | 标题 | 核心职责 | module_id | 状态 |
|----------|------|----------|-----------|------|
"""
        
        root_docs = [d for d in self.documents if d['path'].count('\\') == 1 and not d['is_index']]
        for doc in root_docs:
            status = "✅" if doc['responsibility'] else "⚠️"
            report += f"| {doc['filename']} | {doc['title'][:30]} | {doc['responsibility'][:30] if doc['responsibility'] else '未定义'} | {doc['module_id']} | {status} |\n"
        
        report += f"""
### 3.2 子目录文档

"""
        
        subdirs = ['01_asset_allocation', '02_risk_budgeting', '03_strategy_selection', '04_strategic_adjustment']
        for subdir in subdirs:
            subdir_docs = [d for d in self.documents if subdir in d['path'] and not d['is_index']]
            if subdir_docs:
                report += f"""
#### {subdir}

| 文档名称 | 标题 | 核心职责 | module_id | 状态 |
|----------|------|----------|-----------|------|
"""
                for doc in subdir_docs:
                    status = "✅" if doc['responsibility'] else "⚠️"
                    report += f"| {doc['filename']} | {doc['title'][:30]} | {doc['responsibility'][:30] if doc['responsibility'] else '未定义'} | {doc['module_id']} | {status} |\n"
        
        report += f"""
---

## 🎯 四、修复建议

### 4.1 立即修复项 (P0)

"""
        
        if self.true_overlaps:
            for idx, overlap in enumerate(self.true_overlaps, 1):
                report += f"{idx}. **职责重叠**: {overlap['responsibility']} - 建议明确职责边界或合并文档\n"
        else:
            report += "✅ 无需立即修复\n"
        
        report += f"""
### 4.2 短期改进项 (P1)

"""
        
        if docs_without_responsibility > 0:
            report += f"1. **补充职责描述**: {docs_without_responsibility}个文档缺少职责描述\n"
        else:
            report += "✅ 无需短期改进\n"
        
        report += f"""
---

## 📊 五、质量指标

| 指标 | 当前值 | 目标值 | 状态 |
|------|--------|--------|------|
| **职责清晰度** | {docs_with_responsibility / total_docs * 100:.1f}% | ≥95% | {'✅' if docs_with_responsibility / total_docs >= 0.95 else '⚠️'} |
| **职责重叠数** | {len(self.true_overlaps)} | 0 | {'✅' if len(self.true_overlaps) == 0 else '⚠️'} |

---

## 📝 六、分析声明

**分析方法**: 职责描述精确匹配 + 职责边界分析

**分析范围**: 
- ✅ 职责描述提取
- ✅ 职责重叠识别
- ✅ 职责边界分析

**分析局限性**:
- 本分析基于文档职责描述，未深入分析文档内容
- 职责重叠判断基于描述文本相同，可能存在误判
- 需要人工复核确认问题

**后续建议**:
1. 对职责重叠问题立即修复
2. 对缺少职责描述的文档补充内容
3. 建立职责描述标准模板

---

**分析完成时间**: {self.get_current_time()}
**分析报告路径**: {report_path.relative_to(self.docs_root)}
"""
        
        # 保存报告
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"  ✅ 报告已生成: {report_path.relative_to(self.docs_root)}")
        
        # 保存JSON数据
        json_path = report_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_time': self.get_current_time(),
                'documents': self.documents,
                'true_overlaps': self.true_overlaps,
                'statistics': {
                    'total_documents': total_docs,
                    'docs_with_responsibility': docs_with_responsibility,
                    'docs_without_responsibility': docs_without_responsibility,
                    'responsibility_clarity': docs_with_responsibility / total_docs * 100,
                    'overlap_count': len(self.true_overlaps)
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 数据已保存: {json_path.relative_to(self.docs_root)}")
        
    def get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    analyzer = ResponsibilityOverlapAnalyzer("docs")
    analyzer.run_analysis()
