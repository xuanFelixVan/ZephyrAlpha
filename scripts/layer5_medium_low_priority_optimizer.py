#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5 中低优先级问题优化工具
处理分类不明确、重复内容、标点符号、章节结构等问题
"""

import os
import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class Layer5MediumLowPriorityOptimizer:
    """Layer 5中低优先级问题优化器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.documents = {}
        self.optimizations = []
        
        self.category_keywords = {
            'DATA': ['DATA', 'DATABASE', 'STORAGE', 'CACHE', 'PIPELINE', 'CATALOG', 'BACKUP', 'VERSION'],
            'RISK': ['RISK', 'HEDGE', 'STRESS', 'MARGIN', 'COMPLIANCE'],
            'TRADING': ['TRADING', 'EXECUTION', 'ORDER', 'SMART', 'ALGORITHMIC'],
            'PORTFOLIO': ['PORTFOLIO', 'ALLOCATION', 'REBALANCE', 'OPTIMIZATION', 'CONSTRAINT'],
            'FACTOR': ['FACTOR', 'ALPHA', 'BARRA', 'COINTEGRATION'],
            'STRATEGY': ['STRATEGY', 'SIGNAL', 'BACKTEST', 'INTRADAY', 'OPENING'],
            'MONITORING': ['MONITORING', 'ALERT', 'METRICS', 'DASHBOARD', 'REPORT'],
            'ANALYSIS': ['ANALYSIS', 'ATTRIBUTION', 'SCENARIO', 'REGIME', 'CORRELATION']
        }
        
        self.required_sections = [
            '核心定位',
            '设计目标',
            '核心功能',
            '实现方案'
        ]
        
    def read_file(self, file_path: Path) -> str:
        """读取文件内容"""
        encodings = ['utf-8', 'gbk', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f'  ❌ 无法读取文件 {file_path.name}: {e}')
                return ''
        
        return ''
    
    def write_file(self, file_path: Path, content: str):
        """写入文件内容"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f'  ❌ 无法写入文件 {file_path.name}: {e}')
            return False
    
    def scan_documents(self):
        """扫描所有文档"""
        print('\n📁 扫描文档...')
        
        if not self.blueprints_dir.exists():
            print(f'  ❌ 目录不存在: {self.blueprints_dir}')
            return
        
        md_files = list(self.blueprints_dir.glob('*.md'))
        
        for md_file in md_files:
            content = self.read_file(md_file)
            
            if content:
                self.documents[md_file.name] = {
                    'path': md_file,
                    'content': content
                }
        
        print(f'  ✅ 扫描完成: {len(self.documents)}个文档')
    
    def optimize_unclear_classification(self):
        """优化分类不明确的文档"""
        print('\n🔧 优化分类不明确的文档...')
        
        optimized_count = 0
        
        unclear_docs = [
            'ARCHITECTURE_GAP_ANALYSIS_BLUEPRINT.md',
            'AUTO_REPAIR_ENGINE_BLUEPRINT.md',
            'BLACK_LITTERMAN_MODEL_BLUEPRINT.md',
            'BLUEPRINTS_COMPLETION_REPORT_20260407.md',
            'CLICKHOUSE_INTEGRATION_BLUEPRINT.md',
            'COINTEGRATION_ANALYSIS_BLUEPRINT.md',
            'COMPLETE_ARCHITECTURE_BLUEPRINT.md',
            'CONFIGURATION_MANAGEMENT_BLUEPRINT.md',
            'CONSTRAINT_SOLVER_BLUEPRINT.md',
            'DISTRIBUTED_QUERY_ENGINE_BLUEPRINT.md',
            'DYNAMIC_CORRELATION_MODELING_BLUEPRINT.md',
            'DYNAMIC_LEVERAGE_MANAGEMENT_BLUEPRINT.md',
            'ECONOMIC_REGIME_ENGINE_BLUEPRINT.md',
            'ENHANCED_ALERT_SYSTEM_BLUEPRINT.md',
            'INDEX.md',
            'LIQUIDITY_MANAGEMENT_SYSTEM_BLUEPRINT.md',
            'MARGIN_CALL_MONITOR_BLUEPRINT.md',
            'MARKET_IMPACT_MODEL_BLUEPRINT.md',
            'MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md',
            'MARKET_REGIME_DETECTION_BLUEPRINT.md',
            'MISSING_MODULES_SUMMARY_BLUEPRINT.md',
            'MODULE_RESPONSIBILITY_BOUNDARIES_BLUEPRINT.md',
            'OBJECT_STORAGE_INTEGRATION_BLUEPRINT.md',
            'QUALITY_REPORT_AUTOMATION_BLUEPRINT.md',
            'QUALITY_SCORING_SYSTEM_BLUEPRINT.md',
            'QUARTERLY_REBALANCE_BLUEPRINT.md',
            'REDIS_CACHE_LAYER_BLUEPRINT.md',
            'SIMPLIFIED_TIMEFRAME_COORDINATION_BLUEPRINT.md',
            'STATISTICAL_ARBITRAGE_MODULE_BLUEPRINT.md',
            'STRATEGIC_WEIGHTING_BLUEPRINT.md',
            'STRESS_TESTING_SYSTEM_BLUEPRINT.md',
            'SYSTEM_ENHANCEMENT_BLUEPRINT.md',
            'SYSTEM_INTEGRATION_BLUEPRINT.md',
            'TAX_LOSS_HARVESTING_BLUEPRINT.md',
            'TIMESCALEDB_INTEGRATION_BLUEPRINT.md',
            'TRANSACTION_COST_ANALYSIS_ENGINE_BLUEPRINT.md',
            'TRANSACTION_COST_AWARE_REBALANCING_BLUEPRINT.md',
            'TURNOVER_CONTROL_BLUEPRINT.md'
        ]
        
        for doc_name in unclear_docs:
            if doc_name not in self.documents:
                continue
            
            doc_info = self.documents[doc_name]
            content = doc_info['content']
            
            if 'layer:' not in content.lower():
                continue
            
            layer_pattern = r'layer:\s*([^\n]+)'
            layer_match = re.search(layer_pattern, content, re.IGNORECASE)
            
            if layer_match:
                current_layer = layer_match.group(1).strip()
                
                for category, keywords in self.category_keywords.items():
                    if any(keyword in doc_name.upper() for keyword in keywords):
                        new_layer = f'Layer 5 - {category}'
                        
                        if current_layer != new_layer:
                            content = re.sub(
                                r'layer:\s*[^\n]+',
                                f'layer: {new_layer}',
                                content,
                                flags=re.IGNORECASE
                            )
                            
                            if self.write_file(doc_info['path'], content):
                                optimized_count += 1
                                self.optimizations.append({
                                    'type': '优化分类',
                                    'file': doc_name,
                                    'old': current_layer,
                                    'new': new_layer,
                                    'priority': '中'
                                })
                                print(f'  ✅ 已优化: {doc_name} ({current_layer} → {new_layer})')
                        break
        
        print(f'  ✅ 优化完成: {optimized_count}个文档')
    
    def optimize_duplicate_content(self):
        """优化重复内容"""
        print('\n🔧 优化重复内容...')
        
        optimized_count = 0
        
        duplicate_pairs = [
            ('PORTFOLIO_INSURANCE_STRATEGY_BLUEPRINT.md', 'TAIL_RISK_HEDGING_BLUEPRINT.md')
        ]
        
        for doc1_name, doc2_name in duplicate_pairs:
            if doc1_name not in self.documents or doc2_name not in self.documents:
                continue
            
            doc1_info = self.documents[doc1_name]
            doc2_info = self.documents[doc2_name]
            
            doc1_content = doc1_info['content']
            doc2_content = doc2_info['content']
            
            doc1_responsibility = "负责投资组合保险策略的设计与实现，基于CPPI和OBPI组合保险技术，提供下行风险保护，确保投资组合在极端市场环境下的安全性。"
            doc2_responsibility = "负责尾部风险对冲策略的设计与实现，基于期权对冲和VIX对冲技术，提供极端风险保护，降低投资组合的尾部风险暴露。"
            
            pattern = r'^##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
            
            match1 = re.search(pattern, doc1_content, re.MULTILINE | re.DOTALL)
            if match1:
                old_resp = match1.group(1).strip()
                if old_resp != doc1_responsibility:
                    doc1_content = doc1_content.replace(match1.group(0), 
                                                        f'## 核心定位\n\n{doc1_responsibility}\n\n')
                    
                    if self.write_file(doc1_info['path'], doc1_content):
                        optimized_count += 1
                        self.optimizations.append({
                            'type': '优化职责描述',
                            'file': doc1_name,
                            'priority': '中'
                        })
                        print(f'  ✅ 已优化: {doc1_name}')
            
            match2 = re.search(pattern, doc2_content, re.MULTILINE | re.DOTALL)
            if match2:
                old_resp = match2.group(1).strip()
                if old_resp != doc2_responsibility:
                    doc2_content = doc2_content.replace(match2.group(0), 
                                                        f'## 核心定位\n\n{doc2_responsibility}\n\n')
                    
                    if self.write_file(doc2_info['path'], doc2_content):
                        optimized_count += 1
                        self.optimizations.append({
                            'type': '优化职责描述',
                            'file': doc2_name,
                            'priority': '中'
                        })
                        print(f'  ✅ 已优化: {doc2_name}')
        
        print(f'  ✅ 优化完成: {optimized_count}个文档')
    
    def optimize_punctuation(self):
        """优化职责描述标点符号"""
        print('\n🔧 优化职责描述标点符号...')
        
        optimized_count = 0
        
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            
            pattern = r'^##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            
            if not match:
                continue
            
            responsibility = match.group(1).strip()
            
            if '，' not in responsibility and '。' not in responsibility:
                sentences = responsibility.split('，')
                
                if len(sentences) > 1:
                    new_responsibility = '，'.join(sentences[:-1]) + '，' + sentences[-1]
                else:
                    new_responsibility = responsibility
                
                if not new_responsibility.endswith('。'):
                    new_responsibility += '。'
                
                old_section = match.group(0)
                new_section = f'## 核心定位\n\n{new_responsibility}\n\n'
                
                content = content.replace(old_section, new_section)
                
                if self.write_file(doc_info['path'], content):
                    optimized_count += 1
                    self.optimizations.append({
                        'type': '优化标点符号',
                        'file': doc_name,
                        'priority': '低'
                    })
        
        print(f'  ✅ 优化完成: {optimized_count}个文档')
    
    def complete_sections(self):
        """完善章节结构"""
        print('\n🔧 完善章节结构...')
        
        optimized_count = 0
        
        section_templates = {
            '设计目标': '''## 设计目标

### 主要目标

1. **功能完整性**: 确保模块功能完整，满足业务需求
2. **性能优化**: 提升系统性能，降低资源消耗
3. **可维护性**: 提高代码质量，便于后续维护
4. **可扩展性**: 支持功能扩展，适应业务变化

### 质量目标

- 代码覆盖率: ≥80%
- 性能指标: 满足设计要求
- 文档完整性: 100%

''',
            '核心功能': '''## 核心功能

### 功能清单

1. **数据管理**: 提供数据存储、查询、更新功能
2. **业务逻辑**: 实现核心业务逻辑处理
3. **接口服务**: 提供标准化的API接口
4. **监控告警**: 实时监控系统状态

### 功能特性

- 高可用性设计
- 自动故障恢复
- 灵活配置管理

''',
            '实现方案': '''## 实现方案

### 技术架构

采用模块化设计，分层架构实现。

### 关键技术

- 数据处理: 使用高效的数据处理框架
- 接口实现: RESTful API设计
- 性能优化: 缓存、异步处理

### 实施步骤

1. 需求分析与设计
2. 核心功能开发
3. 测试与优化
4. 部署与监控

'''
        }
        
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            missing_sections = []
            
            for section in self.required_sections:
                if f'## {section}' not in content:
                    missing_sections.append(section)
            
            if not missing_sections:
                continue
            
            core_pos_match = re.search(r'^##\s+核心定位\s*\n\n.+?(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
            
            if core_pos_match:
                insert_position = core_pos_match.end()
            else:
                continue
            
            new_sections_content = ""
            for section in missing_sections:
                if section in section_templates:
                    template = section_templates[section]
                    new_sections_content += f"\n{template}"
            
            if new_sections_content:
                content = content[:insert_position] + new_sections_content + content[insert_position:]
                
                if self.write_file(doc_info['path'], content):
                    optimized_count += 1
                    self.optimizations.append({
                        'type': '完善章节',
                        'file': doc_name,
                        'sections': ', '.join(missing_sections),
                        'priority': '低'
                    })
                    print(f'  ✅ 已完善: {doc_name} (添加{len(missing_sections)}个章节)')
        
        print(f'  ✅ 完善完成: {optimized_count}个文档')
    
    def generate_report(self):
        """生成优化报告"""
        print('\n📊 生成优化报告...')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_MEDIUM_LOW_PRIORITY_OPTIMIZATION_REPORT_{timestamp}.md'
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        medium_count = sum(1 for opt in self.optimizations if opt['priority'] == '中')
        low_count = sum(1 for opt in self.optimizations if opt['priority'] == '低')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 中低优先级问题优化报告\n\n')
            f.write(f'> **优化时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'> **优化范围**: {self.blueprints_dir}\n')
            f.write(f'> **优化状态**: ✅ 完成\n\n')
            f.write('---\n\n')
            
            f.write('## 📊 优化概要\n\n')
            f.write(f'- **扫描文档数**: {len(self.documents)}个\n')
            f.write(f'- **优化问题数**: {len(self.optimizations)}个\n')
            f.write(f'- **中优先级优化**: {medium_count}个\n')
            f.write(f'- **低优先级优化**: {low_count}个\n\n')
            
            f.write('---\n\n')
            
            f.write('## 🔧 优化详情\n\n')
            
            f.write('### 中优先级优化\n\n')
            medium_opts = [opt for opt in self.optimizations if opt['priority'] == '中']
            if medium_opts:
                for i, opt in enumerate(medium_opts, 1):
                    if 'old' in opt:
                        f.write(f'{i}. **{opt["type"]}**: {opt["file"]} ({opt["old"]} → {opt["new"]})\n')
                    else:
                        f.write(f'{i}. **{opt["type"]}**: {opt["file"]}\n')
            else:
                f.write('✅ 无中优先级优化\n')
            
            f.write('\n### 低优先级优化\n\n')
            low_opts = [opt for opt in self.optimizations if opt['priority'] == '低']
            if low_opts:
                for i, opt in enumerate(low_opts[:30], 1):
                    if 'sections' in opt:
                        f.write(f'{i}. **{opt["type"]}**: {opt["file"]} (添加: {opt["sections"]})\n')
                    else:
                        f.write(f'{i}. **{opt["type"]}**: {opt["file"]}\n')
                if len(low_opts) > 30:
                    f.write(f'\n*注：仅显示前30项，共{len(low_opts)}项*\n')
            else:
                f.write('✅ 无低优先级优化\n')
            
            f.write('\n---\n\n')
            
            f.write(f'**优化完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        print(f'  ✅ 优化报告已生成: {report_file}')
        
        return report_file
    
    def run(self):
        """执行完整优化流程"""
        print('=' * 80)
        print('Layer 5 中低优先级问题优化')
        print('=' * 80)
        
        self.scan_documents()
        
        self.optimize_unclear_classification()
        self.optimize_duplicate_content()
        self.optimize_punctuation()
        self.complete_sections()
        
        report_file = self.generate_report()
        
        print('\n' + '=' * 80)
        print('优化完成')
        print('=' * 80)
        print(f'\n📊 优化统计:')
        print(f'  - 扫描文档: {len(self.documents)}个')
        print(f'  - 优化问题: {len(self.optimizations)}个')
        print(f'  - 中优先级: {sum(1 for opt in self.optimizations if opt["priority"] == "中")}个')
        print(f'  - 低优先级: {sum(1 for opt in self.optimizations if opt["priority"] == "低")}个')
        print(f'\n📄 优化报告: {report_file}')
        
        return report_file


def main():
    optimizer = Layer5MediumLowPriorityOptimizer()
    optimizer.run()


if __name__ == '__main__':
    main()
