#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 11文档职责说明章节添加工具
用途：为所有Layer 11文档自动添加"文档职责说明"章节
版本：v1.0
创建日期：2026-04-06
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

LAYER11_DIR = Path("docs/11_STRATEGIC_DECISION")

RESPONSIBILITY_TEMPLATES = {
    "CAPITAL_ALLOCATION_BLUEPRINT.md": {
        "core_responsibility": "资本配置系统蓝图，负责战略资产配置和资本分配决策",
        "responsible_for": [
            "战略资产配置（季度/年度资产配置）",
            "战术资产配置（月度/周度配置调整）",
            "动态资产配置（市场环境变化调整）",
            "资本分配决策（跨策略资本分配）",
            "配置优化（均值方差、风险平价、Black-Litterman）"
        ],
        "not_responsible_for": [
            "风险预算分配（由风险预算分配模块负责）",
            "策略选择决策（由投资策略选择模块负责）",
            "具体交易执行（由Layer 6组合优化层负责）"
        ],
        "upstream": ["Layer 10 质量保证层", "Layer 7 风险管理层"],
        "downstream": ["Layer 6 组合优化层", "Layer 7 风险管理层"]
    },
    "MARKET_REGIME_BLUEPRINT.md": {
        "core_responsibility": "市场状态识别系统蓝图，负责市场状态判断和预测",
        "responsible_for": [
            "市场状态识别（趋势/震荡/极端）",
            "市场状态预测（状态转换预测）",
            "状态转换预警（范式变化预警）",
            "市场环境报告（状态报告生成）"
        ],
        "not_responsible_for": [
            "资产配置决策（由战略资产配置模块负责）",
            "风险预算分配（由风险预算分配模块负责）",
            "策略选择决策（由投资策略选择模块负责）"
        ],
        "upstream": ["Layer 2 数据层", "Layer 10 质量保证层"],
        "downstream": ["Layer 6 组合优化层", "Layer 7 风险管理层"]
    },
    "MULTI_STRATEGY_COORDINATION_BLUEPRINT.md": {
        "core_responsibility": "多策略协调系统蓝图，负责策略信号冲突解决和资金协调",
        "responsible_for": [
            "策略信号冲突解决（信号优先级判断）",
            "策略资金协调（跨策略资金分配）",
            "策略风险协调（跨策略风险控制）",
            "协调报告生成（协调决策报告）"
        ],
        "not_responsible_for": [
            "资产配置决策（由战略资产配置模块负责）",
            "风险预算分配（由风险预算分配模块负责）",
            "具体交易执行（由Layer 6组合优化层负责）"
        ],
        "upstream": ["Layer 5 策略层", "Layer 10 质量保证层"],
        "downstream": ["Layer 6 组合优化层", "Layer 7 风险管理层"]
    },
    "PERFORMANCE_ATTRIBUTION_BLUEPRINT.md": {
        "core_responsibility": "业绩归因系统蓝图，负责绩效分析和归因报告",
        "responsible_for": [
            "收益归因分析（Brinson归因）",
            "风险归因分析（风险来源分析）",
            "归因报告生成（归因分析报告）",
            "绩效评估（夏普/卡玛/索提诺比率）"
        ],
        "not_responsible_for": [
            "资产配置决策（由战略资产配置模块负责）",
            "风险预算分配（由风险预算分配模块负责）",
            "具体交易执行（由Layer 6组合优化层负责）"
        ],
        "upstream": ["Layer 6 组合优化层", "Layer 7 风险管理层"],
        "downstream": ["Layer 8 报告层", "Layer 10 质量保证层"]
    },
    "TCA_BLUEPRINT.md": {
        "core_responsibility": "交易成本分析系统蓝图，负责交易成本测量和优化",
        "responsible_for": [
            "交易成本测量（显性/隐性成本）",
            "成本归因分析（成本来源分析）",
            "成本优化建议（成本优化方案）",
            "TCA报告生成（成本分析报告）"
        ],
        "not_responsible_for": [
            "资产配置决策（由战略资产配置模块负责）",
            "风险预算分配（由风险预算分配模块负责）",
            "具体交易执行（由Layer 6组合优化层负责）"
        ],
        "upstream": ["Layer 6 组合优化层", "Layer 7 风险管理层"],
        "downstream": ["Layer 8 报告层", "Layer 10 质量保证层"]
    },
    "REBALANCING_BLUEPRINT.md": {
        "core_responsibility": "再平衡决策系统蓝图，负责再平衡策略和执行跟踪",
        "responsible_for": [
            "再平衡触发判断（阈值/时间触发）",
            "再平衡方案生成（优化再平衡方案）",
            "再平衡成本优化（成本最小化）",
            "再平衡执行跟踪（执行监控）"
        ],
        "not_responsible_for": [
            "资产配置决策（由战略资产配置模块负责）",
            "风险预算分配（由风险预算分配模块负责）",
            "具体交易执行（由Layer 6组合优化层负责）"
        ],
        "upstream": ["Layer 6 组合优化层", "Layer 7 风险管理层"],
        "downstream": ["Layer 6 组合优化层", "Layer 8 报告层"]
    },
    "OPEN_SOURCE_INTEGRATION_BLUEPRINT.md": {
        "core_responsibility": "开源项目集成蓝图，负责开源项目的选型和集成方案",
        "responsible_for": [
            "开源项目选型（项目评估和选择）",
            "集成方案设计（技术集成架构）",
            "集成实施指导（集成步骤和最佳实践）",
            "集成效果评估（集成效果分析）"
        ],
        "not_responsible_for": [
            "具体模块实现（由各模块蓝图负责）",
            "技术选型决策（由TECHNOLOGY_SELECTION_DECISION.md负责）",
            "实施路径规划（由BLUEPRINT.md负责）"
        ],
        "upstream": ["技术选型决策", "架构设计文档"],
        "downstream": ["各模块蓝图", "实施团队"]
    },
    "TECHNOLOGY_SELECTION_DECISION.md": {
        "core_responsibility": "技术选型决策文档，负责技术方案的选择和决策记录",
        "responsible_for": [
            "技术方案评估（多方案对比）",
            "技术选型决策（最终方案选择）",
            "决策记录（决策依据和过程）",
            "决策追踪（决策执行跟踪）"
        ],
        "not_responsible_for": [
            "具体技术实现（由各模块蓝图负责）",
            "集成方案设计（由OPEN_SOURCE_INTEGRATION_BLUEPRINT.md负责）",
            "实施路径规划（由BLUEPRINT.md负责）"
        ],
        "upstream": ["需求分析", "技术调研"],
        "downstream": ["开源集成蓝图", "各模块蓝图"]
    }
}

DEFAULT_TEMPLATE = {
    "core_responsibility": "模块蓝图，负责特定功能的实现",
    "responsible_for": [
        "核心功能实现",
        "接口定义",
        "数据模型设计"
    ],
    "not_responsible_for": [
        "其他模块职责",
        "跨模块协调"
    ],
    "upstream": ["上游模块"],
    "downstream": ["下游模块"]
}


def generate_responsibility_section(filename: str) -> str:
    """生成职责说明章节"""
    template = RESPONSIBILITY_TEMPLATES.get(filename, DEFAULT_TEMPLATE)
    
    section = f"""
## 📋 文档职责说明

### 核心职责

本文档是**{template['core_responsibility']}**。

### 职责边界

**负责**：
"""
    
    for item in template['responsible_for']:
        section += f"- ✅ {item}\n"
    
    section += "\n**不负责**：\n"
    for item in template['not_responsible_for']:
        section += f"- ❌ {item}\n"
    
    section += "\n### 对接模块\n\n**上游模块**：\n"
    for item in template['upstream']:
        section += f"- {item}\n"
    
    section += "\n**下游模块**：\n"
    for item in template['downstream']:
        section += f"- {item}\n"
    
    section += "\n---\n"
    
    return section


def add_responsibility_section(file_path: Path) -> bool:
    """为文档添加职责说明章节"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '## 📋 文档职责说明' in content or '## 文档职责说明' in content:
            print(f"✓ {file_path.name} 已包含职责说明章节，跳过")
            return False
        
        title_pattern = r'^(#\s+[^\n]+\n)'
        match = re.search(title_pattern, content, re.MULTILINE)
        
        if not match:
            print(f"✗ {file_path.name} 未找到标题，跳过")
            return False
        
        title_end = match.end()
        
        responsibility_section = generate_responsibility_section(file_path.name)
        
        new_content = content[:title_end] + responsibility_section + content[title_end:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ {file_path.name} 已添加职责说明章节")
        return True
    
    except Exception as e:
        print(f"✗ {file_path.name} 处理失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("Layer 11文档职责说明章节添加工具")
    print("=" * 80)
    print()
    
    if not LAYER11_DIR.exists():
        print(f"✗ 目录不存在: {LAYER11_DIR}")
        return
    
    md_files = list(LAYER11_DIR.glob("*.md"))
    md_files = [f for f in md_files if f.name not in ["INDEX.md", "BLUEPRINT.md", "RESPONSIBILITY_BOUNDARY_MATRIX.md"]]
    
    print(f"发现 {len(md_files)} 个Markdown文件需要处理")
    print()
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for md_file in sorted(md_files):
        result = add_responsibility_section(md_file)
        if result:
            success_count += 1
        else:
            skip_count += 1
    
    print()
    print("=" * 80)
    print(f"处理完成: 成功 {success_count} 个, 跳过 {skip_count} 个, 失败 {fail_count} 个")
    print("=" * 80)


if __name__ == "__main__":
    main()
