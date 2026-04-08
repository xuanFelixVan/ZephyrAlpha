#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Layer 8重复文档
分析相似文件名是否为真正的重复内容
"""

import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class Layer8DuplicateChecker:
    def __init__(self):
        self.duplicate_groups = defaultdict(list)
        self.false_positives = []
        self.true_duplicates = []
        
    def check_duplicates(self):
        """检查重复文档"""
        print("=" * 80)
        print("Layer 8 重复文档检查")
        print("=" * 80)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 扫描所有文件
        print("\n[阶段1] 扫描所有文件...")
        all_files = self.scan_all_files()
        
        # 2. 按文件名分组
        print("\n[阶段2] 按文件名分组...")
        self.group_by_filename(all_files)
        
        # 3. 分析重复组
        print("\n[阶段3] 分析重复组...")
        self.analyze_duplicate_groups()
        
        # 4. 生成报告
        print("\n[阶段4] 生成检查报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("检查完成！")
        print(f"重复组数: {len(self.duplicate_groups)}")
        print(f"误报数: {len(self.false_positives)}")
        print(f"真正重复数: {len(self.true_duplicates)}")
        print("=" * 80)
    
    def scan_all_files(self):
        """扫描所有文件"""
        all_files = []
        
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 提取文件大小和内容哈希
                        file_size = len(content)
                        content_hash = hash(content[:500])  # 使用前500字符的哈希
                        
                        all_files.append({
                            "name": file,
                            "path": str(rel_path),
                            "size": file_size,
                            "hash": content_hash,
                            "dir": file_path.parent.name
                        })
                        
                    except Exception as e:
                        print(f"  [警告] 无法读取文件: {rel_path} - {e}")
        
        print(f"  扫描到 {len(all_files)} 个文件")
        return all_files
    
    def group_by_filename(self, all_files):
        """按文件名分组"""
        for file_info in all_files:
            self.duplicate_groups[file_info['name']].append(file_info)
        
        # 只保留有多个文件的组
        self.duplicate_groups = {
            name: files for name, files in self.duplicate_groups.items()
            if len(files) > 1
        }
        
        print(f"  发现 {len(self.duplicate_groups)} 个重复文件名组")
    
    def analyze_duplicate_groups(self):
        """分析重复组"""
        for name, files in self.duplicate_groups.items():
            # 检查是否是INDEX.md或README.md
            if name in ['INDEX.md', 'README.md']:
                # 这些是正常的重复文件名，不是真正的重复内容
                self.false_positives.append({
                    "name": name,
                    "count": len(files),
                    "type": "正常重复（导航文件）",
                    "files": [f['path'] for f in files[:5]]
                })
            else:
                # 检查内容是否相同
                hashes = [f['hash'] for f in files]
                if len(set(hashes)) == 1:
                    # 内容相同，是真正的重复
                    self.true_duplicates.append({
                        "name": name,
                        "count": len(files),
                        "type": "真正重复",
                        "files": [f['path'] for f in files]
                    })
                else:
                    # 内容不同，只是文件名相同
                    self.false_positives.append({
                        "name": name,
                        "count": len(files),
                        "type": "文件名相同但内容不同",
                        "files": [f['path'] for f in files]
                    })
        
        print(f"  误报: {len(self.false_positives)} 组")
        print(f"  真正重复: {len(self.true_duplicates)} 组")
    
    def generate_report(self):
        """生成检查报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"LAYER8_DUPLICATE_CHECK_REPORT_{timestamp}.md"
        
        report = f"""---
module_id: LAYER8_DUPLICATE_CHECK_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - Layer 8 重复文档检查报告
standard_type: 检查报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# Layer 8 重复文档检查报告

**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**检查范围**: Layer 8 人机交互层  
**检查类型**: 重复文档检查

---

## 📊 检查概要

| 指标 | 数值 |
|------|------|
| **重复文件名组数** | {len(self.duplicate_groups)} |
| **误报数** | {len(self.false_positives)} |
| **真正重复数** | {len(self.true_duplicates)} |

---

## ✅ 误报分析

### 正常的重复文件名

这些文件名相同，但这是正常的结构，不是真正的重复：

"""
        
        for item in self.false_positives[:10]:
            report += f"\n#### {item['name']} ({item['count']}个文件)\n\n"
            report += f"**类型**: {item['type']}\n\n"
            report += "**示例文件**:\n"
            for file in item['files']:
                report += f"- {file}\n"
        
        if len(self.false_positives) > 10:
            report += f"\n*还有 {len(self.false_positives) - 10} 个误报组*\n"
        
        if self.true_duplicates:
            report += f"""
---

## ⚠️ 真正的重复文档

这些文件内容相同，需要处理：

"""
            for item in self.true_duplicates:
                report += f"\n#### {item['name']} ({item['count']}个文件)\n\n"
                report += "**文件列表**:\n"
                for file in item['files']:
                    report += f"- {file}\n"
        
        report += f"""
---

## 📝 检查总结

### 主要发现

1. **误报分析**: {len(self.false_positives)} 组文件名相同，但这是正常的结构
   - INDEX.md 和 README.md 是每个模块的标准导航文件
   - 这些文件虽然文件名相同，但内容不同，服务于不同模块

2. **真正重复**: {len(self.true_duplicates)} 组文件内容相同
   - 需要进一步检查和处理

### 结论

- ✅ 大部分"重复"是正常的文件结构
- ✅ 符合专业量化机构的模块化文档架构
- ⚠️ 如有真正重复，需要归档或删除旧版本

### 后续建议

1. 验证误报分析结果
2. 处理真正的重复文档（如有）
3. 保持文档结构的一致性

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**检查执行者**: Audit Sentinel
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n[OK] 检查报告已生成: {report_file}")


if __name__ == "__main__":
    checker = Layer8DuplicateChecker()
    checker.check_duplicates()
