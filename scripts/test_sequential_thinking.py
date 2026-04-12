#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
测试 SequentialThinking MCP 工具
分析如何优化项目文档结构
"""

import json
import sys

# 构建请求
request = {
    "jsonrpc": "2.0",
    "method": "sequential_thinking",
    "params": {
        "question": "如何优化 ZephyrAlpha 项目的文档结构？",
        "context": "项目是一个量化交易系统，包含以下文档目录结构：\n- docs/01_FRAMEWORK - 架构文档\n- docs/02_FACTOR_LIBRARY - 因子库\n- docs/03_TRADING_TACTICS - 策略与执行\n- docs/04_EXECUTION - 执行文档\n- docs/05_IMPLEMENTATION - 实施文档\n- docs/09_AUDIT - 审计与治理\n\n项目有 3000+ 文件，包含多个模块：AI 因子挖掘、风险管理、合规检查等。\n\n请分析当前文档结构的问题，并提出优化方案。",
        "steps": 5
    },
    "id": 1
}

# 发送请求
sys.stdout.write(json.dumps(request) + '\n')
sys.stdout.flush()

# 读取响应
for line in sys.stdin:
    try:
        response = json.loads(line)
        if 'result' in response:
            print("=" * 80)
            print("SequentialThinking 分析结果")
            print("=" * 80)
            print(response['result'])
            print("=" * 80)
            break
        elif 'error' in response:
            print("Error:", response['error'])
            break
    except json.JSONDecodeError:
        continue
