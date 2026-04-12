#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
职责重叠问题详细分析
"""

import re
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def parse_yaml_safe(content):
    """安全解析YAML头部"""
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        body_content = content[yaml_match.end():]
        
        try:
            yaml_dict = yaml.safe_load(yaml_content)
            return yaml_dict if yaml_dict else {}, body_content
        except:
            return {}, body_content
    
    return {}, content

def analyze_responsibility_overlap():
    """分析职责重叠问题"""
    
    responsibilities = defaultdict(list)
    
    # 收集所有职责信息
    for md_file in FACTOR_LIBRARY.rglob('*.md'):
        rel_path = md_file.relative_to(FACTOR_LIBRARY)
        
        with open(md_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        yaml_dict, _ = parse_yaml_safe(content)
        
        if 'responsibility' in yaml_dict:
            resp = yaml_dict['responsibility']
            if isinstance(resp, list):
                for r in resp:
                    responsibilities[r].append(str(rel_path))
            else:
                responsibilities[str(resp)].append(str(rel_path))
    
    # 生成报告
    report = f"""# 职责重叠问题详细分析报告

## 分析概要

- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析范围**: D:\\ZephyrAlpha\\docs\\02_FACTOR_LIBRARY
- **分析重点**: 职责重叠问题

---

## 职责重叠统计

| 统计项 | 数量 |
|--------|------|
| 总职责数 | {len(responsibilities)} |
| 重叠职责数 | {sum(1 for paths in responsibilities.values() if len(paths) > 1)} |
| 单一职责数 | {sum(1 for paths in responsibilities.values() if len(paths) == 1)} |

---

## 职责重叠详情

"""
    
    overlap_count = 0
    for resp, paths in sorted(responsibilities.items()):
        if len(paths) > 1:
            overlap_count += 1
            report += f"### {overlap_count}. 职责: \"{resp}\"\n\n"
            report += f"**出现次数**: {len(paths)}次\n\n"
            report += "**出现文档**:\n"
            for path in paths:
                report += f"- {path}\n"
            report += "\n**建议**: 区分文档职责，避免职责重叠\n\n"
            report += "---\n\n"
    
    if overlap_count == 0:
        report += "✅ 无职责重叠问题\n"
    
    report += f"""
---

## 职责重叠原因分析

### 1. INDEX.md与OVERVIEW.md职责相似

很多子目录的INDEX.md和OVERVIEW.md文档使用了相似的职责描述，导致职责重叠。

**示例**:
- `02_ALPHA_FACTORS_INDEX/INDEX.md` 和 `02_ALPHA_FACTORS_INDEX/OVERVIEW.md` 都使用了"Alpha因子索引维护"职责

**解决方案**:
- INDEX.md: 负责目录导航、模块索引
- OVERVIEW.md: 负责模块概览、核心概念介绍

### 2. 不同层级的文档职责重叠

同一职责在不同层级的文档中重复出现。

**示例**:
- `01_STANDARDS/FACTOR_REGISTRY.md` 和 `06_REGISTRY/INDEX.md` 都使用了"因子注册管理"职责

**解决方案**:
- 明确各层级文档的职责边界
- 使用更具体的职责描述

---

## 修复建议

### 立即修复（P1）

1. **区分INDEX.md和OVERVIEW.md职责**
   - INDEX.md: 目录导航、模块索引
   - OVERVIEW.md: 模块概览、核心概念

2. **细化职责描述**
   - 使用更具体的职责描述
   - 避免使用过于宽泛的职责

### 长期优化（P2）

1. **建立职责词典**
   - 标准化职责描述
   - 避免同义词导致的重叠

2. **定期职责审计**
   - 定期检查职责重叠
   - 及时调整职责描述

---

**分析完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # 保存报告
    report_path = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE\RESPONSIBILITY_OVERLAP_ANALYSIS.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n职责重叠分析报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    analyze_responsibility_overlap()
