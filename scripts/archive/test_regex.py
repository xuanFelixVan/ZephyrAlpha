#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复Layer 8审计脚本的responsibility检测逻辑
"""

import re

yaml_content = """module_id: 08_HUMAN_AI_INTERFACE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
  - 蓝图章节命名标准文档"""

print("原始正则表达式测试:")
resp_match_old = re.search(r'responsibility:\s*\n((?:\s+-.*\n)+)', yaml_content)
if resp_match_old:
    print("✅ 找到responsibility字段:")
    print(resp_match_old.group(0))
else:
    print("❌ 未找到responsibility字段")

print("\n改进的正则表达式测试:")
# 改进的正则表达式：允许最后一项后面没有换行符
resp_match_new = re.search(r'responsibility:\s*\n((?:\s+-[^\n]+\n?)+)', yaml_content)
if resp_match_new:
    print("✅ 找到responsibility字段:")
    print(resp_match_new.group(0))
    
    # 提取职责列表
    responsibilities = []
    for line in resp_match_new.group(1).strip().split('\n'):
        if line.strip().startswith('-'):
            resp = line.strip()[1:].strip()
            responsibilities.append(resp)
    
    print("\n职责列表:")
    for resp in responsibilities:
        print(f"  - {resp}")
else:
    print("❌ 未找到responsibility字段")
