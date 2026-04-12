#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Alpha因子层P1级别问题修复
明确职责描述，为每个README.md补充具体职责内容
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

# 定义每个README的具体职责
README_RESPONSIBILITIES = {
    'README.md': {
        'title': '因子库概述',
        'responsibilities': ['因子库整体架构设计', '因子计算流程管理', '因子质量监控'],
        'description': '清风量化系统因子库，提供因子定义、计算、回测和监控的完整框架。'
    },
    '00_GOVERNANCE/README.md': {
        'title': '治理框架',
        'responsibilities': ['治理框架制定', '文档管理规范', '质量监控流程'],
        'description': '因子库治理框架，包括文档管理规范、质量监控流程和持续改进机制。'
    },
    '02_ALPHA_FACTORS_INDEX/README.md': {
        'title': 'Alpha因子索引',
        'responsibilities': ['Alpha因子索引维护', 'Alpha因子分类管理', 'Alpha因子性能跟踪'],
        'description': 'Alpha因子索引和分类文档，跟踪Alpha因子的性能表现。'
    },
    '03_RISK_FACTORS/README.md': {
        'title': '风险因子',
        'responsibilities': ['风险因子定义', '风险因子计算', '风险因子监控'],
        'description': '风险因子定义、计算和监控文档，管理风险暴露因子。'
    },
    '05_BACKTEST/README.md': {
        'title': '回测系统',
        'responsibilities': ['回测框架设计', '回测流程管理', '回测结果分析'],
        'description': '因子回测框架，提供回测流程管理和结果分析功能。'
    },
    '06_REGISTRY/README.md': {
        'title': '因子注册表',
        'responsibilities': ['因子注册管理', '因子版本控制', '因子生命周期管理'],
        'description': '因子注册表，管理因子的注册、版本和生命周期。'
    },
    '07_FACTOR_MONITORING/README.md': {
        'title': '因子监控',
        'responsibilities': ['因子性能监控', '因子预警管理', '因子报告生成'],
        'description': '因子性能监控系统，提供预警管理和报告生成功能。'
    },
    '09_AUDIT/README.md': {
        'title': '审计系统',
        'responsibilities': ['审计报告生成', '质量评估分析', '改进建议制定'],
        'description': '因子库审计系统，生成审计报告和质量评估分析。'
    },
    '10_MANUAL/README.md': {
        'title': '使用手册',
        'responsibilities': ['使用指南编写', 'FAQ维护', '最佳实践总结'],
        'description': '因子库使用手册，包括使用指南、FAQ和最佳实践。'
    }
}

# 定义04_DATA_SOURCE子目录的职责
DATA_SOURCE_RESPONSIBILITIES = {
    '02_SCHEDULER': {
        'title': '数据调度器',
        'responsibilities': ['数据任务调度', '数据获取编排', '数据流程管理'],
        'description': '数据调度器，负责数据任务的调度和编排。'
    },
    '03_CLEANING': {
        'title': '数据清洗',
        'responsibilities': ['数据清洗规则', '数据质量检查', '异常数据处理'],
        'description': '数据清洗模块，提供数据清洗规则和质量检查功能。'
    },
    '07_DATA_PIPELINE': {
        'title': '数据流水线',
        'responsibilities': ['数据流水线设计', '数据流程编排', '数据依赖管理'],
        'description': '数据流水线，管理数据处理的完整流程。'
    },
    'CONFIG_MANAGEMENT': {
        'title': '配置管理',
        'responsibilities': ['配置文件管理', '配置版本控制', '配置变更追踪'],
        'description': '配置管理模块，管理数据源的配置文件和版本。'
    },
    'DATA_ANOMALY_DETECTION': {
        'title': '数据异常检测',
        'responsibilities': ['异常检测算法', '异常告警机制', '异常处理流程'],
        'description': '数据异常检测模块，检测和处理数据异常。'
    },
    'DATA_API_GATEWAY': {
        'title': '数据API网关',
        'responsibilities': ['API接口管理', 'API访问控制', 'API性能监控'],
        'description': '数据API网关，提供统一的API接口管理。'
    },
    'DATA_BACKUP_RECOVERY': {
        'title': '数据备份恢复',
        'responsibilities': ['数据备份策略', '数据恢复流程', '备份验证机制'],
        'description': '数据备份恢复模块，管理数据的备份和恢复。'
    },
    'DATA_CATALOG': {
        'title': '数据目录',
        'responsibilities': ['数据目录维护', '数据元数据管理', '数据血缘追踪'],
        'description': '数据目录模块，管理数据的目录和元数据。'
    },
    'DATA_COMPRESSION_ARCHIVE': {
        'title': '数据压缩归档',
        'responsibilities': ['数据压缩策略', '数据归档流程', '存储优化管理'],
        'description': '数据压缩归档模块，管理数据的压缩和归档。'
    },
    'DATA_CONTRACT': {
        'title': '数据契约',
        'responsibilities': ['数据契约定义', '数据接口规范', '契约验证机制'],
        'description': '数据契约模块，定义和管理数据接口规范。'
    },
    'DATA_FEDERATION': {
        'title': '数据联邦',
        'responsibilities': ['联邦查询引擎', '多源数据整合', '查询优化策略'],
        'description': '数据联邦模块，提供多源数据整合和查询功能。'
    },
    'DATA_LIFECYCLE_MANAGEMENT': {
        'title': '数据生命周期管理',
        'responsibilities': ['生命周期策略', '数据过期处理', '存储成本优化'],
        'description': '数据生命周期管理模块，管理数据的完整生命周期。'
    },
    'DATA_LINEAGE_TRACKING': {
        'title': '数据血缘追踪',
        'responsibilities': ['血缘关系追踪', '数据来源追溯', '影响分析'],
        'description': '数据血缘追踪模块，追踪数据的血缘关系。'
    },
    'DATA_MONITORING_ENHANCED': {
        'title': '增强数据监控',
        'responsibilities': ['实时监控仪表板', '性能指标收集', '告警规则配置'],
        'description': '增强数据监控模块，提供实时监控和告警功能。'
    },
    'DATA_OBSERVABILITY': {
        'title': '数据可观测性',
        'responsibilities': ['可观测性框架', '指标收集分析', '问题诊断工具'],
        'description': '数据可观测性模块，提供数据可观测性框架。'
    },
    'DATA_ORCHESTRATION_ENHANCED': {
        'title': '增强数据编排',
        'responsibilities': ['编排引擎', '工作流管理', '依赖调度'],
        'description': '增强数据编排模块，提供工作流管理和依赖调度。'
    },
    'DATA_PERMISSION_MANAGEMENT': {
        'title': '数据权限管理',
        'responsibilities': ['权限策略管理', '访问控制列表', '权限审计'],
        'description': '数据权限管理模块，管理数据的访问权限。'
    },
    'DATA_PROFILING': {
        'title': '数据画像',
        'responsibilities': ['数据质量画像', '数据特征分析', '数据统计报告'],
        'description': '数据画像模块，分析数据的特征和质量。'
    },
    'DATA_SECURITY_PRIVACY': {
        'title': '数据安全隐私',
        'responsibilities': ['数据加密', '隐私保护', '安全审计'],
        'description': '数据安全隐私模块，保护数据的安全和隐私。'
    },
    'DATA_STANDARDIZATION': {
        'title': '数据标准化',
        'responsibilities': ['数据标准定义', '数据格式规范', '标准合规检查'],
        'description': '数据标准化模块，定义和管理数据标准。'
    },
    'DATA_SYNC_REPLICATION': {
        'title': '数据同步复制',
        'responsibilities': ['同步策略管理', '复制机制', '一致性保证'],
        'description': '数据同步复制模块，管理数据的同步和复制。'
    },
    'DATA_TESTING_FRAMEWORK': {
        'title': '数据测试框架',
        'responsibilities': ['测试用例管理', '自动化测试', '测试报告生成'],
        'description': '数据测试框架，提供数据测试的完整框架。'
    },
    'DATA_VERSION_CONTROL': {
        'title': '数据版本控制',
        'responsibilities': ['版本管理', '变更追踪', '版本回滚'],
        'description': '数据版本控制模块，管理数据的版本和变更。'
    },
    'IFIND': {
        'title': 'iFind数据源',
        'responsibilities': ['iFind接口集成', '因子数据获取', '数据质量验证'],
        'description': 'iFind数据源集成，获取因子数据和财务数据。'
    },
    'REALTIME_DATA_STREAMING': {
        'title': '实时数据流',
        'responsibilities': ['流数据处理', '实时数据分发', '流式计算'],
        'description': '实时数据流模块，处理实时数据流。'
    },
    'TIME_SERIES_STORAGE': {
        'title': '时序存储',
        'responsibilities': ['时序数据存储', '查询优化', '存储压缩'],
        'description': '时序存储模块，管理时序数据的存储和查询。'
    }
}

def update_readme_responsibility(readme_path, info):
    """更新README的职责描述"""
    try:
        with open(readme_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 提取YAML头部
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            body_content = content[yaml_match.end():]
            
            # 解析YAML
            yaml_dict = {}
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    yaml_dict[key.strip()] = value.strip()
            
            # 更新responsibility
            yaml_dict['responsibility'] = info['responsibilities']
            
            # 重建YAML
            yaml_lines = ['---']
            for key, value in yaml_dict.items():
                if key == 'responsibility':
                    yaml_lines.append(f'{key}:')
                    for resp in value:
                        yaml_lines.append(f'  - {resp}')
                else:
                    yaml_lines.append(f'{key}: {value}')
            yaml_lines.append('---')
            
            # 更新body内容
            if not body_content.strip() or '提供' in body_content and '文档支持' in body_content:
                body_content = f"""
# {info['title']}

> **核心职责**: {info['description']}
> **职责边界**: 
> - ✅ 本文档负责：{', '.join(info['responsibilities'][:2])}
> - ❌ 本文档不负责：具体实现细节、其他模块内容

---

## 📋 概述

{info['description']}

## 🎯 核心职责

"""
                for i, resp in enumerate(info['responsibilities'], 1):
                    body_content += f"{i}. **{resp}**\n"
                
                body_content += f"""
---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 补充具体职责描述 | 文档管理团队 |
"""
            
            # 组合新内容
            new_content = '\n'.join(yaml_lines) + '\n' + body_content
            
            # 写入文件
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"错误: {readme_path} - {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("Alpha因子层P1级别问题修复 - 明确职责描述")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    updated_count = 0
    
    # 更新根目录和一级目录的README
    for readme_rel, info in README_RESPONSIBILITIES.items():
        readme_path = FACTOR_LIBRARY / readme_rel
        if readme_path.exists():
            if update_readme_responsibility(readme_path, info):
                print(f"\n更新: {readme_rel}")
                updated_count += 1
    
    # 更新04_DATA_SOURCE子目录的README
    data_source_dir = FACTOR_LIBRARY / '04_DATA_SOURCE'
    if data_source_dir.exists():
        for subdir, info in DATA_SOURCE_RESPONSIBILITIES.items():
            readme_path = data_source_dir / subdir / 'README.md'
            if readme_path.exists():
                if update_readme_responsibility(readme_path, info):
                    print(f"\n更新: 04_DATA_SOURCE/{subdir}/README.md")
                    updated_count += 1
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"更新README文件: {updated_count}")

if __name__ == '__main__':
    main()
