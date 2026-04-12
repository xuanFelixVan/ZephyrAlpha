#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""修复蓝图INDEX.md的分类问题"""
import re

file_path = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS\INDEX.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_pattern = r'## 4\. 风险控制层蓝图（Layer 7）\s*### 4\.1 风险模型与归因.*?### 4\.2 风险对冲与压力测试'
new_text = '''### 3.5 风险模型与归因

| 文档名称 | module_id | 版本 | 状态 | 最后更新 | 文档路径 |
|----------|-----------|------|------|----------|----------|
| Barra风险模型蓝图 | BARRA_RISK_MODEL_001 | v1.0.0 | Active | 2026-04-03 | [链接](./BARRA_RISK_MODEL_BLUEPRINT.md) |
| 风险归因系统蓝图 | RISK_ATTRIBUTION_SYSTEM_001 | v1.0.0 | Active | 2026-04-03 | [链接](./RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md) |

---

## 4. 风险控制层蓝图（Layer 7）
### 4.1 风险对冲与压力测试'''

content_new = re.sub(old_pattern, new_text, content, flags=re.DOTALL)

if content_new != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content_new)
    print('File modified successfully')
else:
    print('No changes made - pattern not found')
