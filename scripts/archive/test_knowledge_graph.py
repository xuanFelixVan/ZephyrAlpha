#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
测试 Knowledge Graph Memory 工具
创建项目架构的知识图谱
"""

import json
import sys

# 构建请求
request = {
    "jsonrpc": "2.0",
    "method": "create_knowledge_graph",
    "params": {
        "graph_name": "ZephyrAlpha Architecture",
        "entities": [
            {
                "id": "data_layer",
                "label": "数据层",
                "properties": {
                    "description": "Layer 0: 数据层，负责数据源接入、数据清洗和存储",
                    "modules": ["数据源接入", "数据清洗", "数据存储 (SQLite/DuckDB)"]
                }
            },
            {
                "id": "preprocessing_layer",
                "label": "前置层",
                "properties": {
                    "description": "Layer 1: 前置层，负责数据预处理、特征工程和数据验证",
                    "modules": ["数据预处理", "特征工程", "数据验证"]
                }
            },
            {
                "id": "alpha_layer",
                "label": "Alpha层",
                "properties": {
                    "description": "Layer 2: Alpha层，负责Alpha因子挖掘、因子库管理和因子评估",
                    "modules": ["Alpha因子挖掘", "因子库管理", "因子评估"]
                }
            },
            {
                "id": "risk_layer",
                "label": "风险层",
                "properties": {
                    "description": "Layer 3: 风险层，负责风险管理、合规检查和风险控制",
                    "modules": ["风险管理", "合规检查", "风险控制"]
                }
            },
            {
                "id": "portfolio_layer",
                "label": "组合层",
                "properties": {
                    "description": "Layer 4: 组合层，负责组合优化和资产配置",
                    "modules": ["组合优化", "资产配置"]
                }
            },
            {
                "id": "execution_layer",
                "label": "执行层",
                "properties": {
                    "description": "Layer 5: 执行层，负责订单执行和交易管理",
                    "modules": ["订单执行", "交易管理"]
                }
            },
            {
                "id": "monitoring_layer",
                "label": "监控层",
                "properties": {
                    "description": "Layer 6: 监控层，负责系统监控和性能分析",
                    "modules": ["系统监控", "性能分析"]
                }
            },
            {
                "id": "attribution_layer",
                "label": "归因层",
                "properties": {
                    "description": "Layer 7: 归因层，负责绩效归因和策略评估",
                    "modules": ["绩效归因", "策略评估"]
                }
            }
        ],
        "relations": [
            {
                "source": "data_layer",
                "target": "preprocessing_layer",
                "type": "FEEDS_INTO",
                "properties": {
                    "description": "数据层向前置层提供原始数据"
                }
            },
            {
                "source": "preprocessing_layer",
                "target": "alpha_layer",
                "type": "PROVIDES_FEATURES",
                "properties": {
                    "description": "前置层为Alpha层提供特征数据"
                }
            },
            {
                "source": "alpha_layer",
                "target": "risk_layer",
                "type": "GENERATES_SIGNALS",
                "properties": {
                    "description": "Alpha层生成交易信号供风险层评估"
                }
            },
            {
                "source": "risk_layer",
                "target": "portfolio_layer",
                "type": "RISK_ADJUSTS",
                "properties": {
                    "description": "风险层对交易信号进行风险调整"
                }
            },
            {
                "source": "portfolio_layer",
                "target": "execution_layer",
                "type": "GENERATES_ORDERS",
                "properties": {
                    "description": "组合层生成订单供执行层执行"
                }
            },
            {
                "source": "execution_layer",
                "target": "monitoring_layer",
                "type": "REPORTS_EXECUTION",
                "properties": {
                    "description": "执行层向监控层报告执行情况"
                }
            },
            {
                "source": "monitoring_layer",
                "target": "attribution_layer",
                "type": "PROVIDES_DATA",
                "properties": {
                    "description": "监控层为归因层提供监控数据"
                }
            },
            {
                "source": "attribution_layer",
                "target": "alpha_layer",
                "type": "FEEDBACK",
                "properties": {
                    "description": "归因层向Alpha层提供反馈，优化因子"
                }
            }
        ]
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
            print("Knowledge Graph Memory 测试结果")
            print("=" * 80)
            print(response['result'])
            print("=" * 80)
            break
        elif 'error' in response:
            print("Error:", response['error'])
            break
    except json.JSONDecodeError:
        continue
