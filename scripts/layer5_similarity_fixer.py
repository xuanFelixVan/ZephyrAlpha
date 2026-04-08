#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5 相似文档职责区分修复工具
优化数据处理模块的职责描述，使其更加区分明显
"""

import os
import re
from pathlib import Path
from datetime import datetime


class Layer5SimilarityFixer:
    """Layer 5相似文档职责区分修复器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.fixes = []
        
        self.responsibility_updates = {
            'CDC_CHANGE_DATA_CAPTURE_BLUEPRINT.md': 
                '负责变更数据捕获模块设计，实时监控数据变更，捕获增量数据，支持数据同步和实时处理。',
            'DATA_ACCESS_AUDIT_BLUEPRINT.md': 
                '负责数据访问审计模块设计，记录数据访问日志，监控访问行为，支持合规审计和安全追溯。',
            'DATA_BACKUP_RECOVERY_BLUEPRINT.md': 
                '负责数据备份恢复模块设计，实现数据备份策略，支持数据恢复和灾难恢复，确保数据安全。',
            'DATA_CLEANING_ENGINE_BLUEPRINT.md': 
                '负责数据清洗引擎设计，实现数据质量检测、异常值处理、缺失值填充，提升数据质量。',
            'DATA_MASKING_ENCRYPTION_BLUEPRINT.md': 
                '负责数据脱敏加密模块设计，实现敏感数据脱敏、数据加密，保护数据隐私和安全。',
            'DATA_OBSERVABILITY_BLUEPRINT.md': 
                '负责数据可观测性模块设计，实现数据质量监控、数据血缘追踪、数据异常检测。',
            'DATA_ORCHESTRATION_SYSTEM_BLUEPRINT.md': 
                '负责数据调度系统设计，实现任务编排、工作流管理、任务依赖调度，自动化数据处理流程。',
            'DATA_QUALITY_MONITORING_BLUEPRINT.md': 
                '负责数据质量监控模块设计，实现数据质量规则定义、质量评分、质量告警功能。',
            'DATA_SECURITY_COMPLIANCE_BLUEPRINT.md': 
                '负责数据安全合规模块设计，实现安全策略管理、合规检查、风险预警功能。',
            'DATA_SOURCE_HEALTH_MONITOR_BLUEPRINT.md': 
                '负责数据源健康监控模块设计，实时监控数据源状态，检测数据源异常，保障数据可用性。',
            'DATA_STANDARDIZATION_ENGINE_BLUEPRINT.md': 
                '负责数据标准化引擎设计，实现数据格式统一、编码转换、数据规范化处理。',
            'DATA_SUBSCRIPTION_SERVICE_BLUEPRINT.md': 
                '负责数据订阅服务设计，实现数据推送、订阅管理、消息分发功能。',
            'DATA_VALIDATION_ENGINE_BLUEPRINT.md': 
                '负责数据验证引擎设计，实现数据校验规则、数据完整性检查、数据一致性验证。',
            'DISTRIBUTED_QUERY_ENGINE_BLUEPRINT.md': 
                '负责分布式查询引擎设计，实现跨数据源查询、查询优化、分布式计算功能。',
            'CLICKHOUSE_INTEGRATION_BLUEPRINT.md': 
                '负责ClickHouse列式存储集成设计，实现高性能OLAP查询、列式数据存储、实时分析功能。',
            'DATA_COST_MANAGEMENT_BLUEPRINT.md': 
                '负责数据成本管理模块设计，实现数据存储成本分析、资源优化、成本预警功能。',
            'DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md': 
                '负责数据生命周期管理模块设计，实现数据归档、数据过期清理、数据保留策略管理。',
            'DATA_SOURCE_MANAGEMENT_BLUEPRINT.md': 
                '负责数据源管理模块设计，实现数据源注册、连接管理、元数据采集功能。',
            'DATA_FABRIC_BLUEPRINT.md': 
                '负责数据编织架构设计，实现跨平台数据集成、数据虚拟化、统一数据访问层。',
            'DATA_MESH_BLUEPRINT.md': 
                '负责数据网格架构设计，实现数据域划分、数据产品化、联邦数据治理。',
            'MONITORING_DASHBOARD_ENHANCEMENT_BLUEPRINT.md': 
                '负责监控仪表盘增强模块设计，实现可视化监控、告警展示、性能分析功能。',
            'RISK_CONTROL_BLUEPRINT.md': 
                '负责风险控制模块设计，实现风险限额管理、风险预警、风险控制策略执行。',
            'MULTI_PERIOD_DYNAMIC_OPTIMIZATION_BLUEPRINT.md': 
                '负责多期动态优化模块设计，实现跨期优化、动态调整、长期投资组合优化。',
            'STRATEGIC_ALLOCATION_ENGINE_BLUEPRINT.md': 
                '负责战略配置引擎设计，实现长期资产配置、战略权重分配、配置再平衡。',
            'STRATEGIC_WEIGHTING_BLUEPRINT.md': 
                '负责战略权重模块设计，实现战略权重计算、权重调整、权重约束管理。',
            'TAIL_RISK_HEDGING_BLUEPRINT.md': 
                '负责尾部风险对冲模块设计，实现尾部风险识别、对冲策略执行、极端风险防护。',
            'TAIL_RISK_METRICS_EXTENSION_BLUEPRINT.md': 
                '负责尾部风险指标扩展模块设计，实现尾部风险度量、极端风险指标计算。',
            'PORTFOLIO_DIVERSIFICATION_METRIC_BLUEPRINT.md': 
                '负责组合分散度指标模块设计，实现分散度计算、集中度分析、组合优化建议。',
            'PORTFOLIO_OPTIMIZATION_DIAGNOSTICS_BLUEPRINT.md': 
                '负责组合优化诊断模块设计，实现优化结果分析、约束冲突检测、优化建议生成。',
        }
        
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
    
    def fix_similar_responsibilities(self):
        """修复相似职责描述"""
        print('\n🔧 修复相似职责描述...')
        
        fixed_count = 0
        
        for doc_name, new_responsibility in self.responsibility_updates.items():
            doc_path = self.blueprints_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = self.read_file(doc_path)
            if not content:
                continue
            
            pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n\n|\n##|\n#|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                old_responsibility = match.group(2).strip()
                
                if len(new_responsibility) < len(old_responsibility) or '设计与构建和运行和操作' in old_responsibility:
                    new_content = content[:match.start(2)] + new_responsibility + content[match.end(2):]
                    
                    if self.write_file(doc_path, new_content):
                        fixed_count += 1
                        self.fixes.append({
                            'file': doc_name,
                            'action': f'优化职责描述: {len(old_responsibility)}字 → {len(new_responsibility)}字'
                        })
                        print(f'  ✅ 已修复: {doc_name}')
        
        print(f'  ✅ 相似职责修复完成: {fixed_count}个文档')
        return fixed_count
    
    def generate_report(self):
        """生成修复报告"""
        print('\n📊 生成修复报告...')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_SIMILARITY_FIX_REPORT_{timestamp}.md'
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 相似文档职责区分修复报告\n\n')
            f.write(f'> **修复时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'> **修复范围**: {self.blueprints_dir}\n\n')
            
            f.write('## 📊 修复统计\n\n')
            f.write(f'- **修复文档**: {len(self.fixes)}个\n\n')
            
            if self.fixes:
                f.write('## 🔧 修复详情\n\n')
                f.write('| 文件 | 操作 |\n')
                f.write('|------|------|\n')
                for fix in self.fixes:
                    f.write(f'| {fix["file"]} | {fix["action"]} |\n')
                f.write('\n')
            
            f.write('---\n\n')
            f.write(f'**修复完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        print(f'  ✅ 修复报告已生成: {report_file}')
        return report_file
    
    def run(self):
        """执行修复"""
        print('=' * 80)
        print('Layer 5 相似文档职责区分修复')
        print('=' * 80)
        
        self.fix_similar_responsibilities()
        
        self.generate_report()
        
        print('\n' + '=' * 80)
        print('修复完成')
        print('=' * 80)
        print(f'\n📊 修复统计:')
        print(f'  - 修复文档: {len(self.fixes)}个')


if __name__ == '__main__':
    fixer = Layer5SimilarityFixer()
    fixer.run()
