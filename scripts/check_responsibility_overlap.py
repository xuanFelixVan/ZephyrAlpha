#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
深度检查职责重叠和重复文档

功能:
1. 扫描所有蓝图文档
2. 提取职责描述
3. 检查职责重叠
4. 检查重复文档
5. 生成详细报告
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import difflib

class ResponsibilityOverlapChecker:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.blueprint_files = []
        self.responsibilities = {}
        self.overlaps = []
        self.duplicates = []
    
    def run(self):
        """执行检查"""
        print('=' * 80)
        print('深度检查职责重叠和重复文档')
        print('=' * 80)
        print()
        
        # 1. 扫描蓝图文件
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
        print()
        
        # 2. 提取职责描述
        print('2. 提取职责描述...')
        self.extract_responsibilities()
        print(f'  ✅ 提取了{len(self.responsibilities)}个职责描述')
        print()
        
        # 3. 检查职责重叠
        print('3. 检查职责重叠...')
        self.check_responsibility_overlap()
        print(f'  ⚠️ 发现{len(self.overlaps)}个职责重叠')
        print()
        
        # 4. 检查重复文档
        print('4. 检查重复文档...')
        self.check_duplicate_documents()
        print(f'  ⚠️ 发现{len(self.duplicates)}个重复文档')
        print()
        
        # 5. 生成报告
        print('5. 生成报告...')
        self.generate_report()
        print(f'  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('检查完成')
        print('=' * 80)
    
    def scan_blueprint_files(self):
        """扫描蓝图文件"""
        if os.path.exists(self.blueprints_dir):
            for root, dirs, files in os.walk(self.blueprints_dir):
                for file in files:
                    if file.endswith('.md') and file != 'INDEX.md':
                        filepath = os.path.join(root, file)
                        self.blueprint_files.append(filepath)
    
    def extract_responsibilities(self):
        """提取职责描述"""
        for filepath in self.blueprint_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 提取标题
                title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else os.path.basename(filepath)
                
                # 提取职责描述
                responsibility = None
                
                # 方法1: 查找"核心定位"或"职责"章节
                resp_match = re.search(r'##\s+(?:核心定位|职责|概述)\s*\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
                if resp_match:
                    responsibility = resp_match.group(1).strip()
                
                # 方法2: 查找第一段描述
                if not responsibility:
                    first_para_match = re.search(r'^#\s+.+?\n\n(.+?)(?=\n\n|\n##|\Z)', content, re.DOTALL)
                    if first_para_match:
                        responsibility = first_para_match.group(1).strip()
                
                # 方法3: 使用文件名
                if not responsibility:
                    responsibility = title
                
                self.responsibilities[filepath] = {
                    'title': title,
                    'responsibility': responsibility,
                    'content': content
                }
            except Exception as e:
                print(f'  ⚠️ 无法读取文件: {filepath} - {e}')
    
    def check_responsibility_overlap(self):
        """检查职责重叠"""
        filepaths = list(self.responsibilities.keys())
        
        for i in range(len(filepaths)):
            for j in range(i + 1, len(filepaths)):
                file1 = filepaths[i]
                file2 = filepaths[j]
                
                resp1 = self.responsibilities[file1]['responsibility']
                resp2 = self.responsibilities[file2]['responsibility']
                
                # 计算相似度
                similarity = difflib.SequenceMatcher(None, resp1, resp2).ratio()
                
                if similarity > 0.7:  # 相似度超过70%
                    self.overlaps.append({
                        'file1': file1,
                        'file2': file2,
                        'similarity': similarity,
                        'resp1': resp1[:100],
                        'resp2': resp2[:100]
                    })
    
    def check_duplicate_documents(self):
        """检查重复文档"""
        filepaths = list(self.responsibilities.keys())
        
        for i in range(len(filepaths)):
            for j in range(i + 1, len(filepaths)):
                file1 = filepaths[i]
                file2 = filepaths[j]
                
                content1 = self.responsibilities[file1]['content']
                content2 = self.responsibilities[file2]['content']
                
                # 计算内容相似度
                similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
                
                if similarity > 0.8:  # 相似度超过80%
                    self.duplicates.append({
                        'file1': file1,
                        'file2': file2,
                        'similarity': similarity
                    })
    
    def generate_report(self):
        """生成报告"""
        report_path = 'docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/RESPONSIBILITY_OVERLAP_CHECK_REPORT_20260407.md'
        
        report_content = f"""---
module_id: RESPONSIBILITY_OVERLAP_CHECK_REPORT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席审计官
layer: Layer 10 (治理与合规层)
standard_type: 专业量化机构级检查报告
applicable_scope: Layer 5策略执行层职责重叠和重复文档检查
compliance_level: 专业标准
check_date: 2026-04-07
---

# 职责重叠和重复文档检查报告

> **检查日期**: 2026-04-07
> **检查范围**: Layer 5策略执行层所有蓝图文档
> **检查标准**: 专业量化机构文档治理五大原则
> **检查类型**: 职责重叠和重复文档深度检查

---

## 📊 一、检查概要

### 1.1 检查结论

本次检查对Layer 5策略执行层的所有蓝图文档进行了深度检查，重点检查职责重叠和重复文档。

**总体评估**: {'✅ 优秀' if len(self.overlaps) == 0 and len(self.duplicates) == 0 else '⚠️ 良好'}

### 1.2 检查范围

- **蓝图文档**: {len(self.blueprint_files)}个
- **职责描述**: {len(self.responsibilities)}个
- **职责重叠**: {len(self.overlaps)}个
- **重复文档**: {len(self.duplicates)}个

---

## 🔍 二、检查结果

### 2.1 职责重叠检查

{self._format_overlap_results()}

### 2.2 重复文档检查

{self._format_duplicate_results()}

---

## 📋 三、改进建议

### 3.1 立即修复（P0级）

{self._format_immediate_fixes()}

### 3.2 近期改进（P1级）

{self._format_short_term_improvements()}

---

## 🎯 四、总结

**检查状态**: ✅ **完成**
**总体评估**: {'✅ 优秀' if len(self.overlaps) == 0 and len(self.duplicates) == 0 else '⚠️ 良好'}

本次检查对Layer 5策略执行层的所有蓝图文档进行了深度检查，{'未发现职责重叠和重复文档问题' if len(self.overlaps) == 0 and len(self.duplicates) == 0 else f'发现{len(self.overlaps)}个职责重叠和{len(self.duplicates)}个重复文档'}。

---

**检查报告版本**: v1.0.0
**检查日期**: 2026-04-07
**检查官**: 首席审计官
**检查状态**: ✅ 完成
"""
        
        # 确保目录存在
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        # 写入报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    def _format_overlap_results(self):
        """格式化职责重叠结果"""
        if not self.overlaps:
            return "✅ 未发现职责重叠问题"
        
        result = []
        for i, overlap in enumerate(self.overlaps[:10], 1):
            result.append(f"#### 重叠 {i}")
            result.append(f"- **文件1**: `{overlap['file1']}`")
            result.append(f"- **文件2**: `{overlap['file2']}`")
            result.append(f"- **相似度**: {overlap['similarity']:.1%}")
            result.append(f"- **职责1**: {overlap['resp1']}...")
            result.append(f"- **职责2**: {overlap['resp2']}...")
            result.append("")
        
        return '\n'.join(result)
    
    def _format_duplicate_results(self):
        """格式化重复文档结果"""
        if not self.duplicates:
            return "✅ 未发现重复文档问题"
        
        result = []
        for i, duplicate in enumerate(self.duplicates[:10], 1):
            result.append(f"#### 重复 {i}")
            result.append(f"- **文件1**: `{duplicate['file1']}`")
            result.append(f"- **文件2**: `{duplicate['file2']}`")
            result.append(f"- **相似度**: {duplicate['similarity']:.1%}")
            result.append("")
        
        return '\n'.join(result)
    
    def _format_immediate_fixes(self):
        """格式化立即修复建议"""
        if not self.overlaps and not self.duplicates:
            return "✅ 无需立即修复"
        
        result = []
        if self.overlaps:
            result.append(f"1. 解决{len(self.overlaps)}个职责重叠问题")
        if self.duplicates:
            result.append(f"2. 处理{len(self.duplicates)}个重复文档")
        
        return '\n'.join(result)
    
    def _format_short_term_improvements(self):
        """格式化近期改进建议"""
        return """1. 建立职责审查机制
2. 定期检查文档重复
3. 完善文档治理流程"""

if __name__ == '__main__':
    checker = ResponsibilityOverlapChecker()
    checker.run()
