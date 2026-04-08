#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5 高优先级问题修复工具
处理剩余的4个高优先级问题
"""

import re
from pathlib import Path
from datetime import datetime


class Layer5HighPriorityFixer:
    """Layer 5高优先级问题修复器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.yaml_template = '''---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 系统架构师
responsibility:
  - {responsibility}
standard_type: 专业量化机构蓝图文档
applicable_scope: Layer 5 - 策略执行层
parent_document: ../INDEX.md
implementation_status: 设计阶段
---

'''
        
        self.documents_to_fix = {
            'ARCHITECTURE_GAP_ANALYSIS_BLUEPRINT.md': {
                'module_id': 'ARCHITECTURE_GAP_ANALYSIS_001',
                'responsibility': '负责架构差距分析，识别当前架构与目标架构之间的差距，提供架构改进建议和实施路径规划。'
            },
            'HIERARCHICAL_RISK_BUDGET_BLUEPRINT.md': {
                'module_id': 'HIERARCHICAL_RISK_BUDGET_001',
                'responsibility': '负责分层风险预算的设计与实现，基于风险预算技术，实现多层级风险分配，优化风险分散效果。'
            },
            'SIMPLIFIED_RISK_BUDGET_SYSTEM_BLUEPRINT.md': {
                'module_id': 'SIMPLIFIED_RISK_BUDGET_SYSTEM_001',
                'responsibility': '负责简化风险预算系统的设计与实现，基于简化风险预算模型，实现快速风险分配，提升决策效率。'
            },
            'PORTFOLIO_DIVERSIFICATION_METRIC_BLUEPRINT.md': {
                'module_id': 'PORTFOLIO_DIVERSIFICATION_METRIC_001',
                'responsibility': '负责投资组合分散化指标的设计与实现，基于分散化度量技术，量化投资组合分散程度，优化风险分散效果。'
            },
            'PORTFOLIO_OPTIMIZATION_DIAGNOSTICS_BLUEPRINT.md': {
                'module_id': 'PORTFOLIO_OPTIMIZATION_DIAGNOSTICS_001',
                'responsibility': '负责投资组合优化诊断的设计与实现，基于诊断技术，分析优化结果，识别优化问题，提供改进建议。'
            },
            'QUALITY_REPORT_AUTOMATION_BLUEPRINT.md': {
                'module_id': 'QUALITY_REPORT_AUTOMATION_001',
                'responsibility': '负责质量报告自动化的设计与实现，基于自动化技术，生成质量报告，提升报告生成效率。'
            },
            'QUALITY_SCORING_SYSTEM_BLUEPRINT.md': {
                'module_id': 'QUALITY_SCORING_SYSTEM_001',
                'responsibility': '负责质量评分系统的设计与实现，基于评分模型，量化质量指标，支持质量评估决策。'
            }
        }
        
        self.fixed_count = 0
        self.fix_details = []
        
    def get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def has_yaml_header(self, content: str) -> bool:
        return content.strip().startswith('---')
    
    def add_yaml_header(self, content: str, module_id: str, responsibility: str) -> str:
        yaml_header = self.yaml_template.format(
            module_id=module_id,
            responsibility=responsibility
        )
        return yaml_header + content
    
    def update_core_positioning(self, content: str, new_responsibility: str) -> str:
        pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n##|\Z)'
        replacement = r'\1' + new_responsibility + r'\n\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        return content
    
    def fix_document(self, filename: str, config: dict) -> bool:
        file_path = self.blueprints_dir / filename
        
        if not file_path.exists():
            print(f'  ❌ 文件不存在: {filename}')
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    print(f'  ❌ 无法读取文件 {filename}: {e}')
                    return False
        
        if not self.has_yaml_header(content):
            content = self.add_yaml_header(content, config['module_id'], config['responsibility'])
            print(f'  ✅ 已添加YAML头部: {filename}')
        else:
            print(f'  ℹ️ 已有YAML头部: {filename}')
        
        content = self.update_core_positioning(content, config['responsibility'])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'  ✅ 已修复: {filename}')
        self.fix_details.append({
            'file': filename,
            'module_id': config['module_id'],
            'responsibility': config['responsibility'],
            'status': 'success'
        })
        
        return True
    
    def run(self):
        print('=' * 80)
        print('Layer 5 高优先级问题修复工具')
        print('=' * 80)
        print(f'修复时间: {self._get_timestamp()}')
        print()
        
        print('修复高优先级问题...')
        for filename, config in self.documents_to_fix.items():
            print(f'  处理 {filename}...')
            if self.fix_document(filename, config):
                self.fixed_count += 1
        print()
        
        print(f'生成修复报告...')
        self._generate_report()
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('修复完成')
        print('=' * 80)
        print()
        print('修复摘要:')
        print(f'  待修复文档: {len(self.documents_to_fix)}个')
        print(f'  成功修复: {self.fixed_count}个')
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _generate_report(self):
        report_path = self.audit_dir / 'LAYER5_HIGH_PRIORITY_FIX_REPORT_20260407.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 高优先级问题修复报告\n\n')
            f.write(f'> **修复时间**: {self._get_timestamp()}\n')
            f.write(f'> **修复范围**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS\n\n')
            f.write('---\n\n')
            f.write('## 📊 修复概要\n\n')
            f.write(f'- **待修复文档**: {len(self.documents_to_fix)}个\n')
            f.write(f'- **成功修复**: {self.fixed_count}个\n\n')
            f.write('---\n\n')
            f.write('## 📝 修复详情\n\n')
            f.write('| 文档名称 | 模块ID | 职责描述 | 状态 |\n')
            f.write('|----------|--------|----------|------|\n')
            for detail in self.fix_details:
                f.write(f"| {detail['file']} | {detail['module_id']} | {detail['responsibility']} | ✅ |\n")
            
            f.write('\n---\n\n')
            f.write('## 🎯 后续建议\n\n')
            f.write('### 近期改进\n')
            f.write('- 处理108个层级标识问题\n')
            f.write('- 验证修复效果\n\n')
            f.write('### 中期改进\n')
            f.write('- 建立文档质量持续监控机制\n')
            f.write('- 优化文档创建流程\n\n')
            f.write(f'**修复完成时间**: {self._get_timestamp()}\n')
            f.write('**修复状态**: ✅ **完成**\n')


def main():
    fixer = Layer5HighPriorityFixer()
    fixer.run()


if __name__ == '__main__':
    main()
