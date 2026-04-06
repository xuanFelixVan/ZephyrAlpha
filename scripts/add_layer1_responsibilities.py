#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为Layer 1文档添加职责描述
基于文档内容分析，为每个文档添加清晰的职责描述
"""

import re
from pathlib import Path
from typing import Dict, List


# 定义每个文档的职责描述
RESPONSIBILITY_DEFINITIONS = {
    "ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md": {
        "responsibility": "另类数据源集成与因子构建，包括新闻数据、社交媒体数据、分析师预期数据的采集、处理和因子生成",
        "core_duties": [
            "另类数据源接入（新闻、社交媒体、分析师预期）",
            "数据采集与清洗（API接口、爬虫、实时流）",
            "NLP处理与因子构建（情感分析、事件提取、实体识别）",
            "因子管理与验证（存储、IC验证、监控）"
        ],
        "excluded_duties": [
            "传统市场数据采集",
            "数据质量监控",
            "数据存储基础设施"
        ]
    },
    "DATA_CATALOG_BLUEPRINT.md": {
        "responsibility": "数据资产目录与元数据管理，提供数据资产的注册、发现、血缘追踪和元数据管理服务",
        "core_duties": [
            "数据资产注册与编目",
            "元数据管理（表描述、字段说明、所有者信息）",
            "数据血缘追踪与可视化",
            "数据资产搜索与发现"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量监控"
        ]
    },
    "DATA_CATALOG_METADATA_BLUEPRINT.md": {
        "responsibility": "数据目录与元数据管理系统，负责数据资产的注册、发现和元数据管理",
        "core_duties": [
            "数据资产注册",
            "元数据管理",
            "数据资产发现",
            "血缘追踪"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量监控"
        ]
    },
    "DATA_COST_MANAGEMENT_BLUEPRINT.md": {
        "responsibility": "数据成本管理与优化，监控和优化数据存储、计算和传输成本",
        "core_duties": [
            "数据成本监控与分析",
            "存储成本优化",
            "计算成本优化",
            "成本报告与预算管理"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量监控"
        ]
    },
    "DATA_FABRIC_BLUEPRINT.md": {
        "responsibility": "数据编织与集成，构建统一的数据访问层，实现跨平台数据集成",
        "core_duties": [
            "数据源连接与集成",
            "数据虚拟化",
            "统一数据访问层",
            "跨平台数据编排"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量监控"
        ]
    },
    "DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md": {
        "responsibility": "数据治理平台，制定和执行数据治理策略，确保数据合规和质量",
        "core_duties": [
            "数据治理策略制定",
            "数据合规管理",
            "数据质量标准执行",
            "数据资产管理"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量监控"
        ]
    },
    "DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md": {
        "responsibility": "数据生命周期管理，管理数据从创建到归档的完整生命周期",
        "core_duties": [
            "数据生命周期策略制定",
            "数据归档管理",
            "数据保留策略执行",
            "数据销毁管理"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量监控"
        ]
    },
    "DATA_MESH_BLUEPRINT.md": {
        "responsibility": "数据网格架构，实现分布式数据管理和数据产品化",
        "core_duties": [
            "数据域划分与管理",
            "数据产品定义",
            "数据所有权管理",
            "分布式数据治理"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量监控"
        ]
    },
    "DATA_OBSERVABILITY_BLUEPRINT.md": {
        "responsibility": "数据可观测性，监控数据管道健康状况，及时发现和诊断数据问题",
        "core_duties": [
            "数据管道监控",
            "数据质量指标采集",
            "异常检测与告警",
            "数据血缘追踪"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量修复"
        ]
    },
    "DATA_QUALITY_MONITORING_BLUEPRINT.md": {
        "responsibility": "数据质量监控与异常检测，保障全系统数据质量",
        "core_duties": [
            "质量规则管理",
            "质量检测执行",
            "异常检测与识别",
            "质量报告生成"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据清洗",
            "数据修复"
        ]
    },
    "DATA_SECURITY_COMPLIANCE_BLUEPRINT.md": {
        "responsibility": "数据安全与合规管理，确保数据安全性和合规性",
        "core_duties": [
            "数据安全策略制定",
            "敏感数据识别与保护",
            "访问控制管理",
            "合规审计"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量监控"
        ]
    },
    "DATA_SOURCE_MANAGEMENT_BLUEPRINT.md": {
        "responsibility": "数据源管理，统一管理各类数据源的连接、配置和监控",
        "core_duties": [
            "数据源注册与配置",
            "连接管理与监控",
            "数据源元数据管理",
            "数据源健康检查"
        ],
        "excluded_duties": [
            "数据采集执行",
            "数据存储",
            "数据质量监控"
        ]
    },
    "DATA_VERSION_CONTROL_BLUEPRINT.md": {
        "responsibility": "数据版本控制，管理数据集的版本历史和变更追踪",
        "core_duties": [
            "数据版本管理",
            "变更追踪",
            "版本回滚",
            "版本比较"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量监控"
        ]
    },
    "HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md": {
        "responsibility": "高性能数据管道，构建低延迟、高吞吐的数据处理流水线",
        "core_duties": [
            "高性能数据处理",
            "流批一体处理",
            "资源优化与调度",
            "水平扩展支持"
        ],
        "excluded_duties": [
            "数据采集",
            "数据存储",
            "数据质量监控"
        ]
    },
    "REALTIME_DATA_LAKE_BLUEPRINT.md": {
        "responsibility": "实时数据湖，构建支持实时数据摄入和查询的数据湖架构",
        "core_duties": [
            "实时数据摄入",
            "数据湖存储管理",
            "实时查询支持",
            "数据分层管理"
        ],
        "excluded_duties": [
            "数据采集",
            "数据处理",
            "数据质量监控"
        ]
    },
    "UNIFIED_DATA_INFRASTRUCTURE_BLUEPRINT.md": {
        "responsibility": "统一数据基础设施，构建统一的数据采集、存储和处理基础设施",
        "core_duties": [
            "数据采集框架",
            "数据存储架构",
            "数据处理引擎",
            "基础设施管理"
        ],
        "excluded_duties": [
            "业务数据处理",
            "数据质量监控",
            "数据治理"
        ]
    }
}


def add_responsibility_section(doc_path: Path, resp_def: Dict) -> bool:
    """为文档添加职责描述章节"""
    try:
        content = doc_path.read_text(encoding='utf-8')
        
        # 检查是否已有职责描述
        if '## 核心定位' in content or '## 职责说明' in content or '## 职责定义' in content:
            print(f"  ⏭️  {doc_path.name}: 已有职责描述，跳过")
            return False
        
        # 构建职责描述章节
        responsibility_section = f"""
## 核心定位

**单一职责**: {resp_def['responsibility']}

### 职责边界

**✅ 核心职责**:
"""
        for duty in resp_def['core_duties']:
            responsibility_section += f"\n- {duty}"
        
        responsibility_section += "\n\n**❌ 非职责范围**:"
        for duty in resp_def['excluded_duties']:
            responsibility_section += f"\n- {duty}"
        
        responsibility_section += "\n"
        
        # 找到合适的位置插入（在第一个## 标题之后）
        lines = content.split('\n')
        insert_pos = -1
        
        for i, line in enumerate(lines):
            if line.startswith('## ') and i > 0:
                insert_pos = i
                break
        
        if insert_pos > 0:
            # 在第一个## 标题之前插入
            lines.insert(insert_pos, responsibility_section)
            new_content = '\n'.join(lines)
            
            # 写回文件
            doc_path.write_text(new_content, encoding='utf-8')
            print(f"  ✓ {doc_path.name}: 已添加职责描述")
            return True
        else:
            print(f"  ✗ {doc_path.name}: 未找到合适的插入位置")
            return False
    
    except Exception as e:
        print(f"  ✗ {doc_path.name}: 处理失败 - {str(e)}")
        return False


def main():
    """主函数"""
    print("\n" + "="*80)
    print("📝 为Layer 1文档添加职责描述")
    print("="*80)
    
    blueprints_dir = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for doc_name, resp_def in RESPONSIBILITY_DEFINITIONS.items():
        doc_path = blueprints_dir / doc_name
        
        if not doc_path.exists():
            print(f"  ✗ {doc_name}: 文件不存在")
            fail_count += 1
            continue
        
        result = add_responsibility_section(doc_path, resp_def)
        
        if result:
            success_count += 1
        elif '已有职责描述' in str(result):
            skip_count += 1
        else:
            fail_count += 1
    
    print("\n" + "="*80)
    print("📊 处理结果统计")
    print("="*80)
    print(f"✓ 成功添加: {success_count} 个文档")
    print(f"⏭️  跳过: {skip_count} 个文档")
    print(f"✗ 失败: {fail_count} 个文档")
    print("="*80)


if __name__ == '__main__':
    main()
