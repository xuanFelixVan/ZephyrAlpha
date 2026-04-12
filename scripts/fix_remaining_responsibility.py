# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
修复剩余职责重叠问题
"""
import os
from pathlib import Path
import yaml
from datetime import datetime

def fix_responsibility_overlap():
    """修复职责重叠"""
    base_path = Path("d:/ZephyrAlpha/docs/02_FACTOR_LIBRARY/04_DATA_SOURCE")
    
    # 需要修复的文件列表及其正确的职责
    fixes = {
        'IFIND/financial_statements/INDEX.md': '财务报表数据模块导航',
        'REALTIME_DATA_STREAMING/BLUEPRINT.md': '实时数据流处理架构与Kafka集成',
        'QUALITY_MANAGEMENT/QUALITY_METRICS.md': '数据质量指标定义与监控',
        'QUALITY_MANAGEMENT/DATA_QUALITY_CONTROL_SYSTEM.md': '数据质量控制体系设计与实施',
        'IFIND/INDEX.md': 'iFind数据源模块导航',
        'DATA_TESTING_FRAMEWORK/BLUEPRINT.md': '数据测试框架设计与测试用例管理',
        'DATA_PROFILING/BLUEPRINT.md': '数据分析与统计特征提取',
        'DATA_SYNC_REPLICATION/BLUEPRINT.md': '数据同步复制策略与一致性保证',
        'DATA_ORCHESTRATION_ENHANCED/BLUEPRINT.md': '数据编排增强功能与工作流管理',
        'DATA_PERMISSION_MANAGEMENT/BLUEPRINT.md': '数据权限管理策略与访问控制',
        'DATA_OBSERVABILITY/BLUEPRINT.md': '数据可观测性架构与监控指标',
        'DATA_MONITORING_ENHANCED/BLUEPRINT.md': '数据监控增强功能与可视化',
        'DATA_LINEAGE_TRACKING/BLUEPRINT.md': '数据血缘追踪与数据流向分析',
        'DATA_LIFECYCLE_MANAGEMENT/BLUEPRINT.md': '数据生命周期管理与归档策略',
        'DATA_COMPRESSION_ARCHIVE/BLUEPRINT.md': '数据压缩归档策略与存储优化',
        'DATA_CONTRACT/BLUEPRINT.md': '数据契约定义与服务级别协议',
        'DATA_CATALOG/BLUEPRINT.md': '数据目录管理与元数据组织',
        'DATA_ANOMALY_DETECTION/BLUEPRINT.md': '数据异常检测算法与告警机制',
        'CONFIG_MANAGEMENT/BLUEPRINT.md': '配置管理系统设计与环境管理',
        '07_DATA_PIPELINE/INDEX.md': '数据管道模块导航',
        '07_DATA_PIPELINE/BLUEPRINT.md': '数据管道架构设计与编排流程',
        '03_CLEANING/INDEX.md': '数据清洗模块导航与文档索引',
        '02_SCHEDULER/BLUEPRINT.md': '任务调度器设计与调度策略',
        '03_CLEANING/BLUEPRINT.md': '数据清洗流程设计与清洗规则制定',
        '03_CLEANING/CLEANING_RULES.md': '数据清洗规则库与异常数据处理',
        'QMT_INTERFACE.md': 'QMT交易接口对接与行情数据获取',
        'NEWS_SENTIMENT_DATA_SOURCE.md': '新闻情感数据源与文本分析',
        'DOCUMENT_NAMING_STANDARD.md': '文档命名规范与标准化指南',
        'DATA_SOURCE_LAYER_GAP_ANALYSIS_V2.md': '数据源层架构差距分析与改进建议',
        'CORRELATION_ANALYSIS.md': '相关性分析方法与因子相关性计算',
        'A_SHARE_HISTORICAL_DATA_PROCESSING_BLUEPRINT.md': 'A股历史数据处理流程设计与实施'
    }
    
    print("="*80)
    print("修复剩余职责重叠问题")
    print("="*80)
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    fixed_count = 0
    
    for file_path, new_responsibility in fixes.items():
        full_path = base_path / file_path
        
        if not full_path.exists():
            print(f"  ⚠️ 文件不存在: {file_path}")
            continue
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 提取YAML
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_data = yaml.safe_load(parts[1])
                    
                    # 更新职责
                    yaml_data['responsibility'] = new_responsibility
                    
                    # 重新生成YAML
                    yaml_str = yaml.dump(yaml_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
                    
                    # 替换内容
                    new_content = f"---\n{yaml_str}---{parts[2]}"
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
                    print(f"  ✓ {file_path}")
                    fixed_count += 1
                    
        except Exception as e:
            print(f"  ⚠️ 修复失败: {file_path} - {str(e)}")
            
    print()
    print(f"修复完成: {fixed_count} 个文件")
    print("="*80)

if __name__ == "__main__":
    fix_responsibility_overlap()
