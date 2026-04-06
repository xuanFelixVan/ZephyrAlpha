#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为缺少交叉引用的Layer 1文档添加交叉引用章节
"""

import re
from pathlib import Path
from typing import Dict, List


# 定义每个文档的交叉引用关系
CROSS_REFERENCES = {
    "ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md": {
        "upstream": [
            ("DATA_SOURCE_MANAGEMENT_BLUEPRINT.md", "DATA_SOURCE_MANAGEMENT_001", "强依赖", "提供数据源连接和配置"),
        ],
        "downstream": [
            ("DATA_QUALITY_MONITORING_BLUEPRINT.md", "DATA_QUALITY_MONITORING_001", "强依赖", "接收另类数据进行质量检查"),
            ("DATA_CATALOG_BLUEPRINT.md", "DATA_CATALOG_001", "中依赖", "注册另类数据资产"),
        ],
        "tech_deps": [
            ("Scrapy", "2.11+", "数据采集", "https://scrapy.org/"),
            ("Selenium", "4.15+", "动态页面抓取", "https://www.selenium.dev/"),
            ("GLM-4-Flash", "latest", "NLP处理", "https://open.bigmodel.cn/"),
            ("Apache Airflow", "2.7+", "任务调度", "https://airflow.apache.org/"),
        ]
    },
    "DATA_CATALOG_METADATA_BLUEPRINT.md": {
        "upstream": [
            ("DATA_SOURCE_MANAGEMENT_BLUEPRINT.md", "DATA_SOURCE_MANAGEMENT_001", "强依赖", "提供数据源元数据"),
            ("DATA_SECURITY_COMPLIANCE_BLUEPRINT.md", "DATA_SECURITY_COMPLIANCE_001", "中依赖", "提供敏感数据分类"),
        ],
        "downstream": [
            ("DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md", "DATA_GOVERNANCE_PLATFORM_001", "强依赖", "提供元数据支持"),
            ("DATA_OBSERVABILITY_BLUEPRINT.md", "DATA_OBSERVABILITY_001", "中依赖", "提供数据资产监控"),
        ],
        "tech_deps": [
            ("OpenMetadata", "1.2+", "元数据管理", "https://docs.open-metadata.org/"),
            ("Apache Atlas", "2.3+", "数据血缘", "https://atlas.apache.org/"),
            ("Elasticsearch", "8.0+", "搜索引擎", "https://www.elastic.co/"),
        ]
    },
    "DATA_COST_MANAGEMENT_BLUEPRINT.md": {
        "upstream": [
            ("DATA_SOURCE_MANAGEMENT_BLUEPRINT.md", "DATA_SOURCE_MANAGEMENT_001", "中依赖", "获取数据源使用情况"),
            ("REALTIME_DATA_LAKE_BLUEPRINT.md", "REALTIME_DATA_LAKE_001", "中依赖", "获取存储成本数据"),
        ],
        "downstream": [
            ("DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md", "DATA_GOVERNANCE_PLATFORM_001", "中依赖", "提供成本治理策略"),
        ],
        "tech_deps": [
            ("Prometheus", "2.40+", "成本监控", "https://prometheus.io/"),
            ("Grafana", "9.0+", "可视化展示", "https://grafana.com/"),
        ]
    },
    "DATA_FABRIC_BLUEPRINT.md": {
        "upstream": [
            ("DATA_SOURCE_MANAGEMENT_BLUEPRINT.md", "DATA_SOURCE_MANAGEMENT_001", "强依赖", "提供数据源连接"),
            ("DATA_CATALOG_BLUEPRINT.md", "DATA_CATALOG_001", "中依赖", "提供数据资产目录"),
        ],
        "downstream": [
            ("HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md", "HIGH_PERFORMANCE_DATA_PIPELINE_001", "强依赖", "提供数据集成服务"),
            ("DATA_OBSERVABILITY_BLUEPRINT.md", "DATA_OBSERVABILITY_001", "中依赖", "提供数据可观测性"),
        ],
        "tech_deps": [
            ("Apache Kafka", "3.5+", "数据流", "https://kafka.apache.org/"),
            ("Apache Flink", "1.19+", "流处理", "https://flink.apache.org/"),
            ("Trino", "430+", "分布式查询", "https://trino.io/"),
        ]
    },
    "DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md": {
        "upstream": [
            ("DATA_CATALOG_BLUEPRINT.md", "DATA_CATALOG_001", "强依赖", "提供数据资产元数据"),
            ("DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md", "DATA_GOVERNANCE_PLATFORM_001", "中依赖", "提供生命周期策略"),
        ],
        "downstream": [
            ("REALTIME_DATA_LAKE_BLUEPRINT.md", "REALTIME_DATA_LAKE_001", "中依赖", "执行数据归档"),
        ],
        "tech_deps": [
            ("Apache Iceberg", "1.4+", "表格式", "https://iceberg.apache.org/"),
            ("Apache Hudi", "0.14+", "数据湖", "https://hudi.apache.org/"),
        ]
    },
    "DATA_SECURITY_COMPLIANCE_BLUEPRINT.md": {
        "upstream": [
            ("DATA_SOURCE_MANAGEMENT_BLUEPRINT.md", "DATA_SOURCE_MANAGEMENT_001", "中依赖", "获取数据源信息"),
        ],
        "downstream": [
            ("DATA_CATALOG_BLUEPRINT.md", "DATA_CATALOG_001", "强依赖", "提供敏感数据标记"),
            ("DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md", "DATA_GOVERNANCE_PLATFORM_001", "强依赖", "执行合规策略"),
            ("DATA_QUALITY_MONITORING_BLUEPRINT.md", "DATA_QUALITY_MONITORING_001", "中依赖", "提供安全检查规则"),
        ],
        "tech_deps": [
            ("Apache Ranger", "2.4+", "权限管理", "https://ranger.apache.org/"),
            ("HashiCorp Vault", "1.15+", "密钥管理", "https://www.vaultproject.io/"),
        ]
    },
    "DATA_SOURCE_MANAGEMENT_BLUEPRINT.md": {
        "upstream": [],
        "downstream": [
            ("DATA_CATALOG_BLUEPRINT.md", "DATA_CATALOG_001", "强依赖", "提供数据源元数据"),
            ("DATA_QUALITY_MONITORING_BLUEPRINT.md", "DATA_QUALITY_MONITORING_001", "强依赖", "提供数据源连接"),
            ("HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md", "HIGH_PERFORMANCE_DATA_PIPELINE_001", "强依赖", "提供数据源连接"),
            ("ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md", "ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT_001", "强依赖", "提供数据源配置"),
        ],
        "tech_deps": [
            ("Apache Airflow", "2.7+", "任务调度", "https://airflow.apache.org/"),
            ("Redis", "7.0+", "连接池管理", "https://redis.io/"),
        ]
    },
    "DATA_VERSION_CONTROL_BLUEPRINT.md": {
        "upstream": [
            ("DATA_CATALOG_BLUEPRINT.md", "DATA_CATALOG_001", "中依赖", "获取数据资产信息"),
        ],
        "downstream": [
            ("DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md", "DATA_GOVERNANCE_PLATFORM_001", "中依赖", "提供版本管理支持"),
        ],
        "tech_deps": [
            ("DVC", "3.0+", "数据版本控制", "https://dvc.org/"),
            ("Git", "2.40+", "版本管理", "https://git-scm.com/"),
            ("LakeFS", "1.0+", "数据湖版本控制", "https://lakefs.io/"),
        ]
    },
    "REALTIME_DATA_LAKE_BLUEPRINT.md": {
        "upstream": [
            ("DATA_SOURCE_MANAGEMENT_BLUEPRINT.md", "DATA_SOURCE_MANAGEMENT_001", "强依赖", "提供数据源连接"),
            ("HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md", "HIGH_PERFORMANCE_DATA_PIPELINE_001", "强依赖", "提供数据处理管道"),
        ],
        "downstream": [
            ("DATA_CATALOG_BLUEPRINT.md", "DATA_CATALOG_001", "中依赖", "注册数据湖资产"),
            ("DATA_QUALITY_MONITORING_BLUEPRINT.md", "DATA_QUALITY_MONITORING_001", "中依赖", "提供数据质量检查点"),
        ],
        "tech_deps": [
            ("Apache Iceberg", "1.4+", "表格式", "https://iceberg.apache.org/"),
            ("Delta Lake", "3.0+", "数据湖", "https://delta.io/"),
            ("MinIO", "latest", "对象存储", "https://min.io/"),
        ]
    },
    "UNIFIED_DATA_INFRASTRUCTURE_BLUEPRINT.md": {
        "upstream": [],
        "downstream": [
            ("DATA_SOURCE_MANAGEMENT_BLUEPRINT.md", "DATA_SOURCE_MANAGEMENT_001", "强依赖", "提供基础设施支持"),
            ("HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md", "HIGH_PERFORMANCE_DATA_PIPELINE_001", "强依赖", "提供数据处理引擎"),
            ("REALTIME_DATA_LAKE_BLUEPRINT.md", "REALTIME_DATA_LAKE_001", "强依赖", "提供存储架构"),
        ],
        "tech_deps": [
            ("Apache Spark", "3.5+", "数据处理", "https://spark.apache.org/"),
            ("Apache Kafka", "3.5+", "消息队列", "https://kafka.apache.org/"),
            ("PostgreSQL", "15+", "关系数据库", "https://www.postgresql.org/"),
            ("Redis", "7.0+", "缓存", "https://redis.io/"),
        ]
    }
}


def add_cross_references(doc_path: Path, refs: Dict) -> bool:
    """为文档添加交叉引用章节"""
    try:
        content = doc_path.read_text(encoding='utf-8')
        
        # 检查是否已有交叉引用
        if '## 📚 相关文档' in content or '## 相关文档' in content:
            print(f"  ⏭️  {doc_path.name}: 已有交叉引用，跳过")
            return False
        
        # 构建交叉引用章节
        cross_ref_section = "\n---\n\n## 📚 相关文档\n\n"
        
        # 添加上游依赖
        if refs.get('upstream'):
            cross_ref_section += "### 上游依赖\n\n"
            cross_ref_section += "| 文档名称 | module_id | 依赖类型 | 说明 |\n"
            cross_ref_section += "|---------|-----------|---------|------|\n"
            for doc_name, module_id, dep_type, desc in refs['upstream']:
                cross_ref_section += f"| [{doc_name.replace('_', ' ').replace('.md', '')}](./{doc_name}) | {module_id} | {dep_type} | {desc} |\n"
            cross_ref_section += "\n"
        
        # 添加下游依赖
        if refs.get('downstream'):
            cross_ref_section += "### 下游依赖\n\n"
            cross_ref_section += "| 文档名称 | module_id | 依赖类型 | 说明 |\n"
            cross_ref_section += "|---------|-----------|---------|------|\n"
            for doc_name, module_id, dep_type, desc in refs['downstream']:
                cross_ref_section += f"| [{doc_name.replace('_', ' ').replace('.md', '')}](./{doc_name}) | {module_id} | {dep_type} | {desc} |\n"
            cross_ref_section += "\n"
        
        # 添加技术依赖
        if refs.get('tech_deps'):
            cross_ref_section += "### 技术依赖\n\n"
            cross_ref_section += "| 技术组件 | 版本 | 用途 | 文档 |\n"
            cross_ref_section += "|---------|------|------|------|\n"
            for tech, version, usage, doc_url in refs['tech_deps']:
                cross_ref_section += f"| **{tech}** | {version} | {usage} | [官方文档]({doc_url}) |\n"
            cross_ref_section += "\n"
        
        # 添加Mermaid图
        cross_ref_section += "### 引用关系图\n\n```mermaid\ngraph LR\n"
        
        # 添加上游节点
        if refs.get('upstream'):
            for i, (doc_name, _, _, _) in enumerate(refs['upstream']):
                node_id = f"U{i}"
                node_label = doc_name.replace('_', ' ').replace('.md', '')[:15]
                cross_ref_section += f"    {node_id}[\"{node_label}\"] --> B\n"
        
        # 添加当前节点
        current_label = doc_path.stem.replace('_', ' ')[:15]
        cross_ref_section += f"    B[\"{current_label}\"]\n"
        
        # 添加下游节点
        if refs.get('downstream'):
            for i, (doc_name, _, _, _) in enumerate(refs['downstream']):
                node_id = f"D{i}"
                node_label = doc_name.replace('_', ' ').replace('.md', '')[:15]
                cross_ref_section += f"    B --> {node_id}[\"{node_label}\"]\n"
        
        # 添加样式
        cross_ref_section += f"    \n    style B fill:#ff6b6b\n"
        if refs.get('upstream'):
            cross_ref_section += "    style U0 fill:#4ecdc4\n"
        if refs.get('downstream'):
            cross_ref_section += "    style D0 fill:#45b7d1\n"
        
        cross_ref_section += "```\n"
        
        # 找到合适的位置插入（在文档末尾或最后一个## 标题之后）
        lines = content.split('\n')
        insert_pos = len(lines)
        
        # 寻找最后一个## 标题
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith('## ') and i > 0:
                insert_pos = i
                break
        
        # 插入交叉引用章节
        lines.insert(insert_pos, cross_ref_section)
        new_content = '\n'.join(lines)
        
        # 写回文件
        doc_path.write_text(new_content, encoding='utf-8')
        print(f"  ✓ {doc_path.name}: 已添加交叉引用")
        return True
    
    except Exception as e:
        print(f"  ✗ {doc_path.name}: 处理失败 - {str(e)}")
        return False


def main():
    """主函数"""
    print("\n" + "="*80)
    print("📝 为缺少交叉引用的Layer 1文档添加交叉引用")
    print("="*80)
    
    blueprints_dir = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for doc_name, refs in CROSS_REFERENCES.items():
        doc_path = blueprints_dir / doc_name
        
        if not doc_path.exists():
            print(f"  ✗ {doc_name}: 文件不存在")
            fail_count += 1
            continue
        
        result = add_cross_references(doc_path, refs)
        
        if result:
            success_count += 1
        else:
            skip_count += 1
    
    print("\n" + "="*80)
    print("📊 处理结果统计")
    print("="*80)
    print(f"✓ 成功添加: {success_count} 个文档")
    print(f"⏭️  跳过: {skip_count} 个文档")
    print(f"✗ 失败: {fail_count} 个文档")
    print("="*80)


if __name__ == '__main__':
    main()
