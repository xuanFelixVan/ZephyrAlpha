#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 5 第十三轮审计问题修复工具
修复职责清晰度问题和重复文档职责区分
"""

import os
import re
from pathlib import Path
from datetime import datetime


class Layer5ThirteenthRoundFixer:
    """Layer 5第十三轮审计问题修复器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.fixes = []
        
        self.responsibility_fixes = {
            'CDC_CHANGE_DATA_CAPTURE_BLUEPRINT.md': 
                '负责变更数据捕获模块设计，实时监控数据库变更，捕获增量数据，支持数据同步和实时处理。',
            'DATA_ACCESS_AUDIT_BLUEPRINT.md': 
                '负责数据访问审计模块设计，记录数据访问日志，监控访问行为，支持合规审计和安全追溯。',
            'DATA_CATALOG_BLUEPRINT.md': 
                '负责数据目录模块设计，实现数据资产注册、元数据管理、数据血缘追踪，提供统一数据资产视图。',
            'DATA_COST_MANAGEMENT_BLUEPRINT.md': 
                '负责数据成本管理模块设计，实现数据存储成本分析、资源优化、成本预警功能。',
            'DATA_FABRIC_BLUEPRINT.md': 
                '负责数据编织架构设计，实现跨平台数据集成、数据虚拟化、统一数据访问层。',
            'DATA_ORCHESTRATION_SYSTEM_BLUEPRINT.md': 
                '负责数据调度系统设计，实现任务编排、工作流管理、任务依赖调度，自动化数据处理流程。',
            'DATA_PREPROCESSING_ARCHITECTURE_GAP_ANALYSIS_BLUEPRINT.md': 
                '负责数据预处理架构差距分析，识别架构缺陷，制定改进计划，确保架构完整性。',
            'DATA_PREPROCESSING_COMPLETE_ARCHITECTURE_BLUEPRINT.md': 
                '负责数据预处理完整架构设计，梳理数据预处理整体架构，确保架构完整性和一致性。',
            'DATA_SOURCE_MANAGEMENT_BLUEPRINT.md': 
                '负责数据源管理模块设计，实现数据源注册、连接管理、元数据采集功能。',
            'DATA_SUBSCRIPTION_SERVICE_BLUEPRINT.md': 
                '负责数据订阅服务设计，实现数据推送、订阅管理、消息分发功能，支持实时数据分发。',
            'DATA_VERSION_CONTROL_BLUEPRINT.md': 
                '负责数据版本控制模块设计，实现数据版本管理、变更追踪、历史回溯功能。',
            'INDEX.md': 
                '负责Layer 5策略执行层蓝图文档索引，提供所有蓝图文档的导航和概览，支持快速定位和访问模块文档。',
            'MONITORING_DASHBOARD_ENHANCEMENT_BLUEPRINT.md': 
                '负责监控仪表盘增强模块设计，实现实时监控、可视化展示、告警通知功能。',
            'RISK_CONTROL_BLUEPRINT.md': 
                '负责风险控制模块设计，实现风险评估、风险预警、风险应对策略功能。',
            'STRATEGIC_WEIGHTING_BLUEPRINT.md': 
                '负责战略权重模块设计，实现战略权重计算、权重调整、权重约束管理，支持长期资产配置。',
            'HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md': 
                '负责高性能数据管道设计，实现数据高速传输、并行处理、流式计算功能。',
            'LIQUIDITY_CONSTRAINED_OPTIMIZATION_BLUEPRINT.md': 
                '负责流动性约束优化模块设计，实现流动性风险评估、约束优化、交易成本控制功能。',
            'DATA_BACKUP_RECOVERY_BLUEPRINT.md': 
                '负责数据备份恢复模块设计，实现数据备份策略制定、备份执行、数据恢复功能。',
            'DATA_MASKING_ENCRYPTION_BLUEPRINT.md': 
                '负责数据脱敏加密模块设计，实现敏感数据脱敏、数据加密、密钥管理功能。',
            'DATA_OBSERVABILITY_BLUEPRINT.md': 
                '负责数据可观测性模块设计，实现数据质量监控、数据血缘追踪、数据异常检测功能。',
            'DATA_SECURITY_COMPLIANCE_BLUEPRINT.md': 
                '负责数据安全合规模块设计，实现安全策略管理、合规检查、风险预警功能。',
            'DATA_SOURCE_HEALTH_MONITOR_BLUEPRINT.md': 
                '负责数据源健康监控模块设计，实时监控数据源状态，检测数据源异常，保障数据可用性。',
            'DATA_VALIDATION_ENGINE_BLUEPRINT.md': 
                '负责数据验证引擎设计，实现数据校验规则、数据完整性检查、数据一致性验证功能。',
            'DATA_CLEANING_ENGINE_BLUEPRINT.md': 
                '负责数据清洗引擎设计，实现数据质量检测、异常值处理、数据标准化功能。',
            'DATA_QUALITY_MONITORING_BLUEPRINT.md': 
                '负责数据质量监控模块设计，实现数据质量规则定义、质量评分、质量告警功能。',
            'DATA_STANDARDIZATION_ENGINE_BLUEPRINT.md': 
                '负责数据标准化引擎设计，实现数据格式统一、编码转换、数据规范化处理功能。',
            'DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md': 
                '负责数据生命周期管理模块设计，实现数据归档、数据过期清理、数据保留策略管理功能。',
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
    
    def fix_responsibility_clarity(self):
        """修复职责清晰度问题"""
        print('\n🔧 修复职责清晰度问题...')
        
        fixed_count = 0
        
        for doc_name, new_responsibility in self.responsibility_fixes.items():
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
                
                vague_words = ['负责', '管理', '处理', '提供', '支持']
                vague_count = sum(1 for word in vague_words if word in old_responsibility)
                
                has_chinese_punct = '。' in old_responsibility or '，' in old_responsibility
                
                need_fix = False
                reason = ''
                
                if vague_count >= 3:
                    need_fix = True
                    reason = f'模糊词汇过多({vague_count}个)'
                elif not has_chinese_punct:
                    need_fix = True
                    reason = '缺少中文标点'
                
                if need_fix:
                    new_content = content[:match.start(2)] + new_responsibility + content[match.end(2):]
                    
                    if self.write_file(doc_path, new_content):
                        fixed_count += 1
                        self.fixes.append({
                            'file': doc_name,
                            'action': f'修复职责清晰度: {reason}'
                        })
                        print(f'  ✅ 已修复: {doc_name} ({reason})')
        
        print(f'  ✅ 职责清晰度修复完成: {fixed_count}个文档')
        return fixed_count
    
    def generate_report(self):
        """生成修复报告"""
        print('\n📊 生成修复报告...')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_THIRTEENTH_ROUND_FIX_REPORT_{timestamp}.md'
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 第十三轮审计问题修复报告\n\n')
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
        print('Layer 5 第十三轮审计问题修复')
        print('=' * 80)
        
        self.fix_responsibility_clarity()
        
        self.generate_report()
        
        print('\n' + '=' * 80)
        print('修复完成')
        print('=' * 80)
        print(f'\n📊 修复统计:')
        print(f'  - 修复文档: {len(self.fixes)}个')


if __name__ == '__main__':
    fixer = Layer5ThirteenthRoundFixer()
    fixer.run()
