#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 9 INDEX.md清理工具
清理已删除文档的索引项，确保INDEX.md与实际文档一致
"""

import os
import re
from pathlib import Path
from datetime import datetime

class Layer9IndexCleaner:
    def __init__(self):
        self.layer9_dir = 'docs/09_RESEARCH_INNOVATION'
        self.index_file = f'{self.layer9_dir}/INDEX.md'
        self.existing_docs = set()
        self.indexed_docs = set()
        
    def scan_existing_documents(self):
        """扫描实际存在的文档"""
        print('阶段1: 扫描实际存在的文档...')
        
        for root, dirs, files in os.walk(self.layer9_dir):
            for file in files:
                if file.endswith('.md') and file != 'INDEX.md':
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.layer9_dir)
                    relative_path = relative_path.replace('\\', '/')
                    self.existing_docs.add(file)
        
        print(f'  ✅ 扫描到 {len(self.existing_docs)} 个实际存在的文档')
        return self.existing_docs
    
    def extract_indexed_documents(self):
        """从INDEX.md中提取已索引的文档"""
        print('阶段2: 提取已索引的文档...')
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取表格中的文档链接
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        
        for match in matches:
            doc_name = match[1]
            # 处理相对路径
            if doc_name.startswith('_archive/'):
                doc_name = doc_name.replace('_archive/', '')
            self.indexed_docs.add(doc_name)
        
        print(f'  ✅ 提取到 {len(self.indexed_docs)} 个已索引的文档')
        return self.indexed_docs
    
    def identify_missing_docs(self):
        """识别已删除但仍在索引中的文档"""
        print('阶段3: 识别已删除的文档...')
        
        missing_docs = self.indexed_docs - self.existing_docs
        print(f'  ✅ 发现 {len(missing_docs)} 个已删除但仍在索引中的文档')
        
        if missing_docs:
            print('  已删除的文档:')
            for doc in sorted(missing_docs):
                print(f'    - {doc}')
        
        return missing_docs
    
    def identify_unindexed_docs(self):
        """识别未索引的文档"""
        print('阶段4: 识别未索引的文档...')
        
        unindexed_docs = self.existing_docs - self.indexed_docs
        print(f'  ✅ 发现 {len(unindexed_docs)} 个未索引的文档')
        
        if unindexed_docs:
            print('  未索引的文档:')
            for doc in sorted(unindexed_docs):
                print(f'    - {doc}')
        
        return unindexed_docs
    
    def generate_clean_index(self):
        """生成清理后的INDEX.md"""
        print('阶段5: 生成清理后的INDEX.md...')
        
        # 读取现有INDEX.md
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分类文档
        core_docs = []
        audit_docs = []
        implementation_docs = []
        archive_docs = []
        
        for doc in sorted(self.existing_docs):
            doc_path = doc
            if doc in ['BLUEPRINT.md', 'DOCUMENT_QUALITY_MONITORING_MECHANISM.md',
                      'DOCUMENT_GOVERNANCE_MAINTENANCE_PLAN.md',
                      'DOCUMENT_GOVERNANCE_MAINTENANCE_SUMMARY.md',
                      'MISSING_MODULES_ANALYSIS.md']:
                core_docs.append(doc)
            elif doc.startswith('DOCUMENT_GOVERNANCE_') or doc in ['FINAL_COMPLETENESS_ANALYSIS.md',
                                                                    'WEEKLY_MAINTENANCE_REPORT_20260407.md']:
                audit_docs.append(doc)
            elif doc in ['IMPLEMENTATION_GUIDE.md', 'IMPLEMENTATION_PRIORITY.md',
                        'OPENSOURCE_INTEGRATION_GUIDE.md']:
                implementation_docs.append(doc)
            else:
                # 检查是否在归档目录
                if os.path.exists(os.path.join(self.layer9_dir, '_archive', doc)):
                    archive_docs.append(doc)
        
        # 生成新的索引内容
        new_content = f"""---
module_id: INDEX_RESEARCH_INNOVATION_001
version: 2.1.0
status: Active
created_date: 2026-04-04
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 系统架构师
responsibility:
  - 负责提供Layer 9研究与创新层的文档导航和索引服务，整合研究文档、创新提案、实验报告等各类文档的入口，为研究团队和创新团队提供快速文档定位和检索支持，确保研究与创新文档体系的完整性和可访问性。
standard_type: 专业量化机构目录索引
applicable_scope: Layer 9 - 研究与创新层
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
---
## 核心定位

负责提供Layer 9研究与创新层的文档导航和索引服务，整合研究文档、创新提案、实验报告等各类文档的入口，为研究团队和创新团队提供快速文档定位和检索支持，确保研究与创新文档体系的完整性和可访问性。

---

# Layer 9: 研究与创新层目录索引

> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容

> **版本**: v2.1
> **架构**: Layer 9 - 研究与创新层
> **最后更新**: {datetime.now().strftime('%Y-%m-%d')}
> **维护者**: 系统架构师

---

## 🎯 目录职责

本目录存放Layer 9研究与创新层的所有文档，包括：
- AI虚拟研究实验室
- 创新孵化器
- 学术前沿追踪
- 研究知识管理
- 因子挖掘研究

---

## 📚 文档索引

**文档总数**: {len(self.existing_docs)}个

### 核心文档

| 文档名称 | 核心职责 | 版本 |
|----------|----------|------|
"""
        
        # 添加核心文档
        for doc in core_docs:
            doc_path = doc
            new_content += f"| [{doc}]({doc_path}) | 负责Layer 9研究与创新层相关功能 | 1.0.0 |\n"
        
        new_content += "\n### 审计报告\n\n| 文档名称 | 核心职责 | 版本 |\n|----------|----------|------|\n"
        
        # 添加审计报告
        for doc in audit_docs:
            new_content += f"| [{doc}]({doc}) | 负责记录Layer 9研究与创新层文档治理审计结果 | 1.0.0 |\n"
        
        new_content += "\n### 实施指南\n\n| 文档名称 | 核心职责 | 版本 |\n|----------|----------|------|\n"
        
        # 添加实施指南
        for doc in implementation_docs:
            new_content += f"| [{doc}]({doc}) | 负责提供Layer 9研究与创新层实施指导 | 1.0.0 |\n"
        
        new_content += "\n### 归档文档\n\n| 文档名称 | 核心职责 | 版本 |\n|----------|----------|------|\n"
        
        # 添加归档文档
        archive_files = []
        archive_dir = os.path.join(self.layer9_dir, '_archive')
        if os.path.exists(archive_dir):
            for file in os.listdir(archive_dir):
                if file.endswith('.md') and file != 'INDEX.md':
                    archive_files.append(file)
        
        for doc in sorted(archive_files):
            new_content += f"| [{doc}](_archive/{doc}) | 负责记录Layer 9研究与创新层历史规划 | 1.0.0 |\n"
        
        new_content += f"""
---

## 📝 维护说明

- **创建日期**: 2026-04-04
- **最后更新**: {datetime.now().strftime('%Y-%m-%d')}
- **维护者**: 系统架构师
- **更新频率**: 按需更新
"""
        
        # 写入新的INDEX.md
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f'  ✅ INDEX.md已更新')
        print(f'  ✅ 文档总数: {len(self.existing_docs)}个')
    
    def run(self):
        """运行清理流程"""
        print('=' * 80)
        print('Layer 9 INDEX.md清理工具')
        print('=' * 80)
        print(f'清理时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print()
        
        self.scan_existing_documents()
        self.extract_indexed_documents()
        missing_docs = self.identify_missing_docs()
        unindexed_docs = self.identify_unindexed_docs()
        
        print()
        print('阶段5: 生成清理后的INDEX.md...')
        self.generate_clean_index()
        
        print()
        print('=' * 80)
        print('清理完成')
        print('=' * 80)
        
        print()
        print('清理摘要:')
        print(f'  实际文档数: {len(self.existing_docs)}')
        print(f'  已索引文档数: {len(self.indexed_docs)}')
        print(f'  已删除文档数: {len(missing_docs)}')
        print(f'  未索引文档数: {len(unindexed_docs)}')

if __name__ == "__main__":
    cleaner = Layer9IndexCleaner()
    cleaner.run()
