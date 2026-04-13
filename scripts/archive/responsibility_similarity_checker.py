#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
职责相似度检查器

功能:
1. 检查所有文档的职责描述相似度
2. 支持自定义相似度阈值
3. 生成详细的相似度报告
4. 提供优化建议
"""

import os
import re
import difflib
import json
from datetime import datetime
from pathlib import Path

class ResponsibilitySimilarityChecker:
    def __init__(self, threshold=0.7):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.threshold = threshold
        self.blueprint_files = []
        self.responsibilities = {}
        self.similarities = []
    
    def run(self):
        """执行检查"""
        print('=' * 80)
        print('职责相似度检查器')
        print('=' * 80)
        print(f'相似度阈值: {self.threshold * 100}%')
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
        
        # 3. 检查相似度
        print('3. 检查职责相似度...')
        self.check_similarity()
        print(f'  ⚠️ 发现{len(self.similarities)}个相似度超过阈值的文档对')
        print()
        
        # 4. 生成报告
        print('4. 生成报告...')
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
                
                # 提取"核心定位"章节的内容
                pattern = r'##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    responsibility = match.group(1).strip()
                    self.responsibilities[filepath] = {
                        'responsibility': responsibility,
                        'filename': os.path.basename(filepath)
                    }
            except Exception as e:
                print(f'  ⚠️ 无法读取文件: {filepath} - {e}')
    
    def check_similarity(self):
        """检查相似度"""
        filepaths = list(self.responsibilities.keys())
        
        for i in range(len(filepaths)):
            for j in range(i + 1, len(filepaths)):
                file1 = filepaths[i]
                file2 = filepaths[j]
                
                resp1 = self.responsibilities[file1]['responsibility']
                resp2 = self.responsibilities[file2]['responsibility']
                
                # 计算相似度
                similarity = difflib.SequenceMatcher(None, resp1, resp2).ratio()
                
                if similarity > self.threshold:
                    self.similarities.append({
                        'file1': file1,
                        'file2': file2,
                        'filename1': self.responsibilities[file1]['filename'],
                        'filename2': self.responsibilities[file2]['filename'],
                        'similarity': similarity,
                        'resp1': resp1[:100],
                        'resp2': resp2[:100]
                    })
    
    def generate_report(self):
        """生成报告"""
        report_dir = 'docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state'
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        report_path = os.path.join(report_dir, f'RESPONSIBILITY_SIMILARITY_REPORT_{timestamp}.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f'''---
module_id: RESPONSIBILITY_SIMILARITY_REPORT_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席审计官
layer: Layer 10 (治理与合规层)
standard_type: 专业量化机构级检查报告
applicable_scope: Layer 5策略执行层职责相似度检查
compliance_level: 专业标准
check_date: {datetime.now().strftime('%Y-%m-%d')}
threshold: {self.threshold * 100}%
---

# 职责相似度检查报告

> **检查日期**: {datetime.now().strftime('%Y-%m-%d')}
> **检查范围**: Layer 5策略执行层所有蓝图文档
> **相似度阈值**: {self.threshold * 100}%
> **检查标准**: 专业量化机构文档治理五大原则

---

## 📊 一、检查概要

### 1.1 检查结论

本次检查对Layer 5策略执行层的所有蓝图文档进行了职责相似度检查。

**总体评估**: {'✅ 优秀' if len(self.similarities) == 0 else '⚠️ 需改进' if len(self.similarities) < 10 else '❌ 不合格'}

### 1.2 检查范围

- **蓝图文档**: {len(self.blueprint_files)}个
- **职责描述**: {len(self.responsibilities)}个
- **相似文档对**: {len(self.similarities)}个
- **相似度阈值**: {self.threshold * 100}%

---

## 🔍 二、检查结果

### 2.1 相似度分布

''')
            
            if self.similarities:
                f.write('| 序号 | 文件1 | 文件2 | 相似度 |\n')
                f.write('|------|-------|-------|--------|\n')
                
                for idx, sim in enumerate(self.similarities, 1):
                    f.write(f'| {idx} | {sim["filename1"]} | {sim["filename2"]} | {sim["similarity"] * 100:.1f}% |\n')
                
                f.write('\n### 2.2 详细分析\n\n')
                
                for idx, sim in enumerate(self.similarities, 1):
                    f.write(f'''#### 相似文档对 {idx}

- **文件1**: `{sim["filename1"]}`
- **文件2**: `{sim["filename2"]}`
- **相似度**: {sim["similarity"] * 100:.1f}%
- **职责1**: {sim["resp1"]}...
- **职责2**: {sim["resp2"]}...

''')
            else:
                f.write('✅ 未发现相似度超过阈值的文档对\n\n')
            
            f.write(f'''---

## 📋 三、改进建议

### 3.1 立即修复（P0级）

''')
            
            if self.similarities:
                f.write(f'1. 解决{len(self.similarities)}个相似度问题\n')
            else:
                f.write('✅ 无需立即修复\n')
            
            f.write('''
### 3.2 近期改进（P1级）

1. 优化相似度阈值
2. 建立职责审查机制
3. 完善文档结构

---

## 🎯 四、总结

**检查状态**: ✅ **完成**
**总体评估**: ''' + ('✅ 优秀' if len(self.similarities) == 0 else '⚠️ 需改进' if len(self.similarities) < 10 else '❌ 不合格') + f'''

本次检查对Layer 5策略执行层的所有蓝图文档进行了职责相似度检查，发现{len(self.similarities)}个相似度超过{self.threshold * 100}%的文档对。

---

**检查报告版本**: v1.0.0
**检查日期**: {datetime.now().strftime('%Y-%m-%d')}
**检查官**: 首席审计官
**检查状态**: ✅ 完成
''')
        
        # 同时生成JSON报告
        json_report_path = os.path.join(report_dir, f'responsibility_similarity_report_{timestamp}.json')
        
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'threshold': self.threshold,
                'total_files': len(self.blueprint_files),
                'total_responsibilities': len(self.responsibilities),
                'similar_pairs': len(self.similarities),
                'similarities': self.similarities
            }, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='职责相似度检查器')
    parser.add_argument('--threshold', type=float, default=0.7, help='相似度阈值（0-1之间，默认0.7）')
    
    args = parser.parse_args()
    
    checker = ResponsibilitySimilarityChecker(threshold=args.threshold)
    checker.run()
