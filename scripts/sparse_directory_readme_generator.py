"""
Layer 1 稀疏目录README生成器
为稀疏目录添加补充文档
"""
import os
from pathlib import Path
from typing import Dict, List
import yaml
from datetime import datetime

class SparseDirectoryReadmeGenerator:
    """稀疏目录README生成器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "docs" / "02_FACTOR_LIBRARY" / "04_DATA_SOURCE"
        
        # 稀疏目录定义（文件数<3）
        self.sparse_directories = [
            'CONFIG_MANAGEMENT',
            'DATA_ANOMALY_DETECTION',
            'DATA_API_GATEWAY',
            'DATA_BACKUP_RECOVERY',
            'DATA_CATALOG',
            'DATA_COMPRESSION_ARCHIVE',
            'DATA_CONTRACT',
            'DATA_FEDERATION',
            'DATA_LIFECYCLE_MANAGEMENT',
            'DATA_LINEAGE_TRACKING',
            'DATA_MONITORING_ENHANCED',
            'DATA_OBSERVABILITY',
            'DATA_ORCHESTRATION_ENHANCED',
            'DATA_PERMISSION_MANAGEMENT',
            'DATA_PROFILING',
            'DATA_SECURITY_PRIVACY',
            'DATA_STANDARDIZATION',
            'DATA_SYNC_REPLICATION',
            'DATA_TESTING_FRAMEWORK',
            'DATA_VERSION_CONTROL',
            'REALTIME_DATA_STREAMING',
            'TIME_SERIES_STORAGE',
            'IFIND'
        ]
        
        # 模块描述映射
        self.module_descriptions = {
            'CONFIG_MANAGEMENT': {
                'name': '配置管理',
                'description': '系统配置管理与环境变量管理',
                'features': [
                    '环境变量管理',
                    '配置文件解析',
                    '配置热更新',
                    '配置版本控制'
                ]
            },
            'DATA_ANOMALY_DETECTION': {
                'name': '数据异常检测',
                'description': '数据异常检测算法与告警机制',
                'features': [
                    '异常值检测',
                    '数据漂移检测',
                    '实时告警',
                    '异常报告生成'
                ]
            },
            'DATA_API_GATEWAY': {
                'name': '数据API网关',
                'description': '统一数据访问接口与API管理',
                'features': [
                    '统一API接口',
                    '请求路由',
                    '访问控制',
                    'API文档管理'
                ]
            },
            'DATA_BACKUP_RECOVERY': {
                'name': '数据备份恢复',
                'description': '数据备份策略与灾难恢复机制',
                'features': [
                    '自动备份',
                    '增量备份',
                    '灾难恢复',
                    '备份验证'
                ]
            },
            'DATA_CATALOG': {
                'name': '数据目录',
                'description': '数据资产管理与元数据组织',
                'features': [
                    '数据资产注册',
                    '元数据管理',
                    '数据搜索',
                    '数据血缘追踪'
                ]
            },
            'DATA_COMPRESSION_ARCHIVE': {
                'name': '数据压缩归档',
                'description': '数据压缩策略与长期存储优化',
                'features': [
                    '数据压缩',
                    '归档策略',
                    '存储优化',
                    '数据解压'
                ]
            },
            'DATA_CONTRACT': {
                'name': '数据契约',
                'description': '数据契约定义与服务级别协议',
                'features': [
                    '契约定义',
                    'SLA管理',
                    '契约验证',
                    '变更通知'
                ]
            },
            'DATA_FEDERATION': {
                'name': '数据联邦',
                'description': '跨源数据访问与联邦查询',
                'features': [
                    '跨源查询',
                    '数据虚拟化',
                    '联邦优化',
                    '统一视图'
                ]
            },
            'DATA_LIFECYCLE_MANAGEMENT': {
                'name': '数据生命周期管理',
                'description': '数据生命周期管理与归档策略',
                'features': [
                    '生命周期定义',
                    '自动归档',
                    '数据清理',
                    '合规管理'
                ]
            },
            'DATA_LINEAGE_TRACKING': {
                'name': '数据血缘追踪',
                'description': '数据血缘追踪与流向分析',
                'features': [
                    '血缘追踪',
                    '影响分析',
                    '流向可视化',
                    '血缘报告'
                ]
            },
            'DATA_MONITORING_ENHANCED': {
                'name': '数据监控增强',
                'description': '增强的数据监控与可视化功能',
                'features': [
                    '实时监控',
                    '可视化仪表板',
                    '性能分析',
                    '告警管理'
                ]
            },
            'DATA_OBSERVABILITY': {
                'name': '数据可观测性',
                'description': '数据可观测性架构与监控指标',
                'features': [
                    '可观测性指标',
                    '分布式追踪',
                    '日志聚合',
                    '健康检查'
                ]
            },
            'DATA_ORCHESTRATION_ENHANCED': {
                'name': '数据编排增强',
                'description': '增强的数据编排与工作流管理',
                'features': [
                    '工作流编排',
                    '任务调度',
                    '依赖管理',
                    '执行监控'
                ]
            },
            'DATA_PERMISSION_MANAGEMENT': {
                'name': '数据权限管理',
                'description': '数据权限策略与访问控制',
                'features': [
                    '权限定义',
                    '角色管理',
                    '访问控制',
                    '审计日志'
                ]
            },
            'DATA_PROFILING': {
                'name': '数据分析',
                'description': '数据统计分析与特征提取',
                'features': [
                    '统计分析',
                    '特征提取',
                    '数据质量评估',
                    '分析报告'
                ]
            },
            'DATA_SECURITY_PRIVACY': {
                'name': '数据安全隐私',
                'description': '数据安全策略与隐私保护机制',
                'features': [
                    '数据加密',
                    '脱敏处理',
                    '访问审计',
                    '合规检查'
                ]
            },
            'DATA_STANDARDIZATION': {
                'name': '数据标准化',
                'description': '数据标准化规则与格式统一',
                'features': [
                    '格式标准化',
                    '数据映射',
                    '质量规则',
                    '标准化报告'
                ]
            },
            'DATA_SYNC_REPLICATION': {
                'name': '数据同步复制',
                'description': '数据同步策略与一致性保证',
                'features': [
                    '实时同步',
                    '增量复制',
                    '冲突解决',
                    '一致性检查'
                ]
            },
            'DATA_TESTING_FRAMEWORK': {
                'name': '数据测试框架',
                'description': '数据测试框架与测试用例管理',
                'features': [
                    '测试用例管理',
                    '数据验证',
                    '测试报告',
                    '持续集成'
                ]
            },
            'DATA_VERSION_CONTROL': {
                'name': '数据版本控制',
                'description': '数据版本控制策略与变更追踪',
                'features': [
                    '版本管理',
                    '变更追踪',
                    '版本回滚',
                    '差异对比'
                ]
            },
            'REALTIME_DATA_STREAMING': {
                'name': '实时数据流',
                'description': '实时数据流处理架构与Kafka集成',
                'features': [
                    '流式处理',
                    'Kafka集成',
                    '实时计算',
                    '流式监控'
                ]
            },
            'TIME_SERIES_STORAGE': {
                'name': '时序存储',
                'description': '时序数据存储架构与TimescaleDB集成',
                'features': [
                    '时序存储',
                    'TimescaleDB集成',
                    '时间窗口查询',
                    '数据压缩'
                ]
            },
            'IFIND': {
                'name': 'iFind数据源',
                'description': 'iFind数据源接入与金融数据获取',
                'features': [
                    'iFind API接入',
                    '财务数据获取',
                    '因子数据管理',
                    '数据缓存'
                ]
            }
        }
        
        self.generation_log = {
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'generated_files': [],
            'statistics': {
                'total_directories': 0,
                'generated_readmes': 0,
                'skipped_directories': 0
            }
        }
        
    def run_generation(self):
        """运行README生成"""
        print("="*80)
        print("Layer 1 稀疏目录README生成")
        print("="*80)
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.generation_log['statistics']['total_directories'] = len(self.sparse_directories)
        
        for dir_name in self.sparse_directories:
            dir_path = self.docs_path / dir_name
            
            if not dir_path.exists():
                print(f"  ⚠️ 目录不存在: {dir_name}")
                continue
                
            # 检查是否已有README
            readme_path = dir_path / "README.md"
            if readme_path.exists():
                print(f"  - 跳过 {dir_name} (README已存在)")
                self.generation_log['statistics']['skipped_directories'] += 1
                continue
                
            # 生成README
            self._generate_readme(dir_name, dir_path)
            self.generation_log['statistics']['generated_readmes'] += 1
            
        print()
        print("-"*80)
        print(f"生成完成: {self.generation_log['statistics']['generated_readmes']} 个README")
        print(f"跳过: {self.generation_log['statistics']['skipped_directories']} 个目录")
        print()
        
        # 保存生成日志
        self._save_generation_log()
        
        print("="*80)
        print("README生成完成")
        print("="*80)
        
    def _generate_readme(self, dir_name: str, dir_path: Path):
        """生成README文件"""
        module_info = self.module_descriptions.get(dir_name, {
            'name': dir_name.replace('_', ' '),
            'description': f'{dir_name}模块',
            'features': ['功能待定义']
        })
        
        # 获取目录下的文件列表
        files = list(dir_path.glob("*.md"))
        file_list = "\n".join([f"- [{f.stem}]({f.name})" for f in files])
        
        # 生成README内容
        content = f"""---
module_id: {dir_name}_README_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility: {module_info['name']}模块说明与使用指南
layer: "Layer 1 (数据预处理层)"
---

# {module_info['name']}

> **核心职责**: {module_info['description']}
> **职责边界**: 
> - ✅ 本模块负责：{module_info['description']}相关功能
> - ❌ 本模块不负责：其他数据处理功能

## 📋 模块概述

{module_info['description']}

### 核心功能

{self._format_features(module_info['features'])}

## 📁 文档索引

{file_list}

## 🚀 快速开始

### 1. 模块定位

本模块位于 **Layer 1 (数据预处理层)**，负责{module_info['description']}。

### 2. 主要用途

{self._format_usage(module_info['features'])}

### 3. 相关模块

- 数据采集模块
- 数据清洗模块
- 数据存储模块

## 📊 技术架构

### 架构位置

```
Layer 0: 基础设施层
Layer 1: 数据预处理层 ← 当前模块
  ├── 数据采集
  ├── 数据清洗
  ├── 数据存储
  └── {module_info['name']}
Layer 2: 因子计算层
Layer 3: 策略引擎层
```

### 关键接口

- 数据输入接口
- 数据输出接口
- 配置接口

## 🔧 使用指南

### 配置说明

```yaml
{dir_name.lower()}:
  enabled: true
  config_path: config/{dir_name.lower()}.yaml
```

### API调用示例

```python
from zephyr.layer1.{dir_name.lower()} import {dir_name.title().replace('_', '')}Manager

# 初始化
manager = {dir_name.title().replace('_', '')}Manager()

# 使用示例
result = manager.process()
```

## 📈 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 处理延迟 | < 100ms | 单次处理延迟 |
| 吞吐量 | > 1000/s | 每秒处理量 |
| 可用性 | > 99.9% | 服务可用性 |

## 🔍 监控与告警

### 监控指标

- 处理成功率
- 处理延迟
- 错误率

### 告警规则

- 错误率 > 1% 触发告警
- 延迟 > 500ms 触发告警

## 📝 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本创建 | 首席架构师 |

---

**文档结束**
"""
        
        # 写入文件
        readme_path = dir_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"  ✓ 生成 {dir_name}/README.md")
        
        self.generation_log['generated_files'].append(str(readme_path.relative_to(self.docs_path)))
        
    def _format_features(self, features: List[str]) -> str:
        """格式化功能列表"""
        return "\n".join([f"- {feature}" for feature in features])
        
    def _format_usage(self, features: List[str]) -> str:
        """格式化用途说明"""
        return "\n".join([f"- 用于{feature}" for feature in features])
        
    def _save_generation_log(self):
        """保存生成日志"""
        log_path = self.base_path / "docs" / "09_AUDIT" / "STATE" / \
                  f"readme_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.generation_log, f, ensure_ascii=False, indent=2)
            
        print(f"✓ 生成日志已保存: {log_path}")

if __name__ == "__main__":
    generator = SparseDirectoryReadmeGenerator("d:/ZephyrAlpha")
    generator.run_generation()
