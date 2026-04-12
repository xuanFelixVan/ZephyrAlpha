# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
Layer 1 职责精确化方案实施脚本
基于职责分类体系为每个文档分配唯一职责
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
from datetime import datetime
from collections import defaultdict

class ResponsibilityRefiner:
    """职责精确化处理器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "docs" / "02_FACTOR_LIBRARY" / "04_DATA_SOURCE"
        
        # 职责分类体系
        self.responsibility_categories = {
            'core': {
                'prefix': '核心职责',
                'keywords': ['数据采集', '数据清洗', '数据存储', '数据质量', '数据管道']
            },
            'support': {
                'prefix': '支撑职责',
                'keywords': ['配置管理', '监控告警', '安全隐私', '备份恢复', '性能优化']
            },
            'documentation': {
                'prefix': '文档职责',
                'keywords': ['蓝图设计', 'API文档', '实施指南', '模块导航']
            }
        }
        
        # 模块职责映射
        self.module_responsibility_map = {
            # 数据源连接器
            'BAOSTOCK_CONNECTOR': 'Baostock数据源接入与数据获取',
            'IFIND_CONNECTOR': 'iFind数据源接入与金融数据获取',
            'QMT_INTERFACE': 'QMT交易接口对接与行情数据获取',
            'SUPERCMD_CONNECTOR': 'SuperCMD命令行接口对接',
            
            # 数据采集与处理
            'DATA_ACQUISITION': '数据采集策略制定与数据源管理',
            'DATA_REQUIREMENTS': '数据需求分析与数据规格定义',
            'DATA_SOURCE_ADAPTERS': '数据源适配器设计与统一接口实现',
            'A_SHARE_HISTORICAL_DATA_PROCESSING_BLUEPRINT': 'A股历史数据处理流程设计与实施',
            
            # 数据清洗
            '03_CLEANING': {
                'BLUEPRINT': '数据清洗流程设计与清洗规则制定',
                'CLEANING_RULES': '数据清洗规则库与异常数据处理',
                'INDEX': '数据清洗模块导航与文档索引'
            },
            
            # 数据质量
            'QUALITY_MANAGEMENT': {
                'DATA_QUALITY_CONTROL_SYSTEM': '数据质量控制体系设计与实施',
                'QUALITY_METRICS': '数据质量指标定义与监控',
                'INDEX': '数据质量管理模块导航'
            },
            
            # 数据管道
            '07_DATA_PIPELINE': {
                'BLUEPRINT': '数据管道架构设计与编排流程',
                'README': '数据管道模块说明与使用指南',
                'INDEX': '数据管道模块导航'
            },
            
            # 调度器
            '02_SCHEDULER': {
                'BLUEPRINT': '任务调度器设计与调度策略',
                'SCHEDULER_API': '调度器API接口定义与使用说明',
                'INDEX': '调度器模块导航'
            },
            
            # 时序存储
            'TIME_SERIES_STORAGE': {
                'BLUEPRINT': '时序数据存储架构设计与TimescaleDB集成',
                'INDEX': '时序存储模块导航'
            },
            
            # 实时数据流
            'REALTIME_DATA_STREAMING': {
                'BLUEPRINT': '实时数据流处理架构与Kafka集成',
                'INDEX': '实时数据流模块导航'
            },
            
            # 数据目录
            'DATA_CATALOG': {
                'BLUEPRINT': '数据目录管理与元数据组织',
                'INDEX': '数据目录模块导航'
            },
            
            # 数据血缘
            'DATA_LINEAGE_TRACKING': {
                'BLUEPRINT': '数据血缘追踪与数据流向分析',
                'INDEX': '数据血缘追踪模块导航'
            },
            
            # 数据联邦
            'DATA_FEDERATION': {
                'BLUEPRINT': '数据联邦架构与跨源数据访问',
                'INDEX': '数据联邦模块导航'
            },
            
            # 数据契约
            'DATA_CONTRACT': {
                'BLUEPRINT': '数据契约定义与服务级别协议',
                'INDEX': '数据契约模块导航'
            },
            
            # 数据版本控制
            'DATA_VERSION_CONTROL': {
                'BLUEPRINT': '数据版本控制策略与变更追踪',
                'INDEX': '数据版本控制模块导航'
            },
            
            # 数据同步复制
            'DATA_SYNC_REPLICATION': {
                'BLUEPRINT': '数据同步复制策略与一致性保证',
                'INDEX': '数据同步复制模块导航'
            },
            
            # 数据标准化
            'DATA_STANDARDIZATION': {
                'BLUEPRINT': '数据标准化规则与格式统一',
                'INDEX': '数据标准化模块导航'
            },
            
            # 数据安全隐私
            'DATA_SECURITY_PRIVACY': {
                'BLUEPRINT': '数据安全策略与隐私保护机制',
                'INDEX': '数据安全隐私模块导航'
            },
            
            # 数据生命周期管理
            'DATA_LIFECYCLE_MANAGEMENT': {
                'BLUEPRINT': '数据生命周期管理与归档策略',
                'INDEX': '数据生命周期管理模块导航'
            },
            
            # 数据压缩归档
            'DATA_COMPRESSION_ARCHIVE': {
                'BLUEPRINT': '数据压缩归档策略与存储优化',
                'INDEX': '数据压缩归档模块导航'
            },
            
            # 数据备份恢复
            'DATA_BACKUP_RECOVERY': {
                'BLUEPRINT': '数据备份恢复策略与灾难恢复',
                'INDEX': '数据备份恢复模块导航'
            },
            
            # 数据API网关
            'DATA_API_GATEWAY': {
                'BLUEPRINT': '统一数据API网关设计与接口管理',
                'INDEX': '数据API网关模块导航'
            },
            
            # 数据异常检测
            'DATA_ANOMALY_DETECTION': {
                'BLUEPRINT': '数据异常检测算法与告警机制',
                'INDEX': '数据异常检测模块导航'
            },
            
            # 配置管理
            'CONFIG_MANAGEMENT': {
                'BLUEPRINT': '配置管理系统设计与环境管理',
                'INDEX': '配置管理模块导航'
            },
            
            # 数据监控增强
            'DATA_MONITORING_ENHANCED': {
                'BLUEPRINT': '数据监控增强功能与可视化',
                'INDEX': '数据监控增强模块导航'
            },
            
            # 数据可观测性
            'DATA_OBSERVABILITY': {
                'BLUEPRINT': '数据可观测性架构与监控指标',
                'INDEX': '数据可观测性模块导航'
            },
            
            # 数据编排增强
            'DATA_ORCHESTRATION_ENHANCED': {
                'BLUEPRINT': '数据编排增强功能与工作流管理',
                'INDEX': '数据编排增强模块导航'
            },
            
            # 数据权限管理
            'DATA_PERMISSION_MANAGEMENT': {
                'BLUEPRINT': '数据权限管理策略与访问控制',
                'INDEX': '数据权限管理模块导航'
            },
            
            # 数据分析
            'DATA_PROFILING': {
                'BLUEPRINT': '数据分析与统计特征提取',
                'INDEX': '数据分析模块导航'
            },
            
            # 数据测试框架
            'DATA_TESTING_FRAMEWORK': {
                'BLUEPRINT': '数据测试框架设计与测试用例管理',
                'INDEX': '数据测试框架模块导航'
            },
            
            # iFind相关
            'IFIND': {
                'INDEX': 'iFind数据源模块导航',
                'factor_master_index': 'iFind因子主索引与因子列表',
                'financial_statements': {
                    'INDEX': '财务报表数据模块导航',
                    'FINANCIAL_STATEMENTS_API': '财务报表API接口与数据获取',
                    'THS_BD_COMPLETE_INDICATOR_LIST': '同花顺完整指标列表与数据字典'
                }
            },
            
            # 其他文档
            'STATISTICAL_TOOLS': '统计分析工具与数据计算方法',
            'MACRO_DATA': '宏观经济数据获取与处理',
            'FREE_DATA_SOURCES': '免费数据源汇总与使用指南',
            'DOCUMENT_NAMING_STANDARD': '文档命名规范与标准化指南',
            'CORRELATION_ANALYSIS': '相关性分析方法与因子相关性计算',
            'NEWS_SENTIMENT_DATA_SOURCE': '新闻情感数据源与文本分析',
            'DATA_SOURCE_LAYER_GAP_ANALYSIS_V2': '数据源层架构差距分析与改进建议',
            'INDEX': 'Layer 1数据预处理层总索引与模块导航'
        }
        
        self.fix_log = {
            'fix_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'fixes': [],
            'statistics': {
                'total_docs': 0,
                'fixed_docs': 0,
                'skipped_docs': 0,
                'errors': 0
            }
        }
        
    def run_refinement(self):
        """运行职责精确化"""
        print("="*80)
        print("Layer 1 职责精确化方案实施")
        print("="*80)
        print(f"实施时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 收集所有文档
        all_docs = self._collect_all_documents()
        self.fix_log['statistics']['total_docs'] = len(all_docs)
        print(f"收集到 {len(all_docs)} 个文档")
        print()
        
        # 为每个文档分配唯一职责
        print("开始职责精确化处理...")
        print("-"*80)
        
        for doc_path, doc_data in all_docs.items():
            unique_responsibility = self._assign_unique_responsibility(doc_path, doc_data)
            
            if unique_responsibility:
                self._update_document_responsibility(doc_data['path'], doc_data, unique_responsibility)
                self.fix_log['statistics']['fixed_docs'] += 1
            else:
                self.fix_log['statistics']['skipped_docs'] += 1
                
        print()
        print("-"*80)
        print(f"处理完成: 修复 {self.fix_log['statistics']['fixed_docs']} 个文档")
        print(f"跳过: {self.fix_log['statistics']['skipped_docs']} 个文档")
        print()
        
        # 验证职责唯一性
        print("验证职责唯一性...")
        print("-"*80)
        duplicates = self._verify_unique_responsibilities(all_docs)
        
        if duplicates:
            print(f"⚠️ 发现 {len(duplicates)} 个职责重复")
            for resp, docs in duplicates.items():
                print(f"  - {resp}: {len(docs)}个文档")
        else:
            print("✅ 所有职责唯一，无重复")
            
        print()
        
        # 保存修复日志
        self._save_fix_log()
        
        print("="*80)
        print("职责精确化完成")
        print("="*80)
        
    def _collect_all_documents(self) -> Dict:
        """收集所有文档"""
        all_docs = {}
        
        for md_file in self.docs_path.rglob("*.md"):
            rel_path = md_file.relative_to(self.docs_path)
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                yaml_data = self._extract_yaml(content)
                
                all_docs[str(rel_path)] = {
                    'path': md_file,
                    'content': content,
                    'yaml': yaml_data,
                    'filename': md_file.stem,
                    'parent': md_file.parent.name if md_file.parent.name != '04_DATA_SOURCE' else 'root'
                }
            except Exception as e:
                print(f"  ⚠️ 读取失败: {rel_path} - {str(e)}")
                self.fix_log['statistics']['errors'] += 1
                
        return all_docs
        
    def _assign_unique_responsibility(self, doc_path: str, doc_data: Dict) -> str:
        """为文档分配唯一职责"""
        parts = Path(doc_path).parts
        filename = doc_data['filename']
        parent = doc_data['parent']
        
        # 根据路径查找职责映射
        if len(parts) == 1:
            # 根目录文档
            key = filename
            if key in self.module_responsibility_map:
                return self.module_responsibility_map[key]
        elif len(parts) == 2:
            # 一级子目录文档
            parent_key = parts[0]
            file_key = filename
            
            if parent_key in self.module_responsibility_map:
                parent_map = self.module_responsibility_map[parent_key]
                if isinstance(parent_map, dict):
                    if file_key in parent_map:
                        return parent_map[file_key]
                    elif 'INDEX' in parent_map and file_key == 'INDEX':
                        return parent_map['INDEX']
                    elif 'BLUEPRINT' in parent_map and file_key == 'BLUEPRINT':
                        return parent_map['BLUEPRINT']
                        
        elif len(parts) >= 3:
            # 多级子目录文档
            parent_key = parts[0]
            sub_key = parts[1]
            file_key = filename
            
            if parent_key in self.module_responsibility_map:
                parent_map = self.module_responsibility_map[parent_key]
                if isinstance(parent_map, dict) and sub_key in parent_map:
                    sub_map = parent_map[sub_key]
                    if isinstance(sub_map, dict) and file_key in sub_map:
                        return sub_map[file_key]
                        
        # 如果没有找到映射，生成默认职责
        return self._generate_default_responsibility(doc_path, doc_data)
        
    def _generate_default_responsibility(self, doc_path: str, doc_data: Dict) -> str:
        """生成默认职责"""
        filename = doc_data['filename']
        parent = doc_data['parent']
        
        # 根据文件名模式生成职责
        if 'BLUEPRINT' in filename:
            return f"{parent.replace('_', ' ')} - 蓝图设计"
        elif 'INDEX' in filename:
            return f"{parent.replace('_', ' ')} - 模块导航"
        elif 'API' in filename:
            return f"{parent.replace('_', ' ')} - API接口"
        elif 'README' in filename:
            return f"{parent.replace('_', ' ')} - 模块说明"
        else:
            return f"{parent.replace('_', ' ')} - {filename.replace('_', ' ')}"
            
    def _update_document_responsibility(self, doc_path: Path, doc_data: Dict, new_responsibility: str):
        """更新文档职责"""
        try:
            yaml_data = doc_data['yaml'].copy() if doc_data['yaml'] else {}
            
            # 更新职责
            yaml_data['responsibility'] = new_responsibility
            
            # 重新生成YAML
            yaml_str = yaml.dump(yaml_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            # 替换内容
            content = doc_data['content']
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    new_content = f"---\n{yaml_str}---{parts[2]}"
                    
                    with open(doc_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
                    print(f"  ✓ {doc_path.name}: {new_responsibility}")
                    
                    self.fix_log['fixes'].append({
                        'file': str(doc_path.relative_to(self.docs_path)),
                        'responsibility': new_responsibility
                    })
                    return
                    
            # 如果没有YAML头部，添加
            new_content = f"---\n{yaml_str}---\n\n{content}"
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print(f"  ✓ {doc_path.name}: {new_responsibility}")
            
            self.fix_log['fixes'].append({
                'file': str(doc_path.relative_to(self.docs_path)),
                'responsibility': new_responsibility
            })
            
        except Exception as e:
            print(f"  ⚠️ 更新失败: {doc_path.name} - {str(e)}")
            self.fix_log['statistics']['errors'] += 1
            
    def _verify_unique_responsibilities(self, all_docs: Dict) -> Dict:
        """验证职责唯一性"""
        responsibility_count = defaultdict(list)
        
        for doc_path, doc_data in all_docs.items():
            yaml_data = self._extract_yaml(doc_data['content'])
            if yaml_data and 'responsibility' in yaml_data:
                resp = yaml_data['responsibility']
                # 处理list类型的responsibility
                if isinstance(resp, list):
                    resp_key = '|'.join(sorted(resp))
                else:
                    resp_key = str(resp)
                responsibility_count[resp_key].append(doc_path)
                
        # 找出重复的职责
        duplicates = {k: v for k, v in responsibility_count.items() if len(v) > 1}
        return duplicates
        
    def _extract_yaml(self, content: str) -> dict:
        """提取YAML头部"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    return yaml.safe_load(parts[1]) or {}
                except:
                    pass
        return {}
        
    def _save_fix_log(self):
        """保存修复日志"""
        log_path = self.base_path / "docs" / "09_AUDIT" / "STATE" / \
                  f"responsibility_refinement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.fix_log, f, ensure_ascii=False, indent=2)
            
        print(f"✓ 修复日志已保存: {log_path}")

if __name__ == "__main__":
    refiner = ResponsibilityRefiner("d:/ZephyrAlpha")
    refiner.run_refinement()
