#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
Layer 9 职责描述修复脚本

功能:
- 为缺少职责描述的文档添加"核心定位"章节
- 根据文档类型和内容生成合适的职责描述
- 确保职责描述符合50-200字标准
- 更新YAML头部的responsibility字段
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class Layer9ResponsibilityFixer:
    def __init__(self):
        self.layer9_dir = 'docs/09_RESEARCH_INNOVATION'
        self.fixed_count = 0
        self.skipped_count = 0
        self.results = []
        
        self.responsibility_templates = {
            'INDEX.md': '负责提供Layer 9研究与创新层的文档导航和索引服务，整合研究文档、创新提案、实验报告等各类文档的入口，为研究团队和创新团队提供快速文档定位和检索支持，确保研究与创新文档体系的完整性和可访问性。',
            
            'IMPLEMENTATION_GUIDE.md': '负责提供Layer 9研究与创新层的实施指导，详细说明研究项目和创新提案的实施流程、技术要求、质量标准和验收标准，为研究团队和创新团队提供实施参考，确保研究与创新项目的规范实施和高质量交付。',
            
            'BLUEPRINT.md': '负责定义Layer 9研究与创新层的整体架构蓝图，规划研究与创新体系的技术架构、模块划分、接口设计和数据流，为研究团队和创新团队提供架构指导，确保研究与创新体系的可扩展性、可维护性和技术先进性。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_AUDIT_REPORT.md': '负责记录Layer 9研究与创新层的文档治理审计结果，详细记录审计发现的问题、问题严重程度、影响范围和改进建议，为文档治理改进提供依据，确保研究与创新层文档质量持续提升。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_COMPLETE_FIX_REPORT.md': '负责记录Layer 9研究与创新层文档治理的完整修复过程，详细记录修复的问题、修复方法、修复结果和验证情况，为文档治理修复提供完整记录，确保修复工作的可追溯性和有效性。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_CONFIRMATION_AUDIT_REPORT.md': '负责记录Layer 9研究与创新层文档治理的确认审计结果，验证修复措施的有效性，确认问题是否已彻底解决，为文档治理质量提供最终确认，确保研究与创新层文档符合专业标准。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_CRITICAL_ISSUES_REPORT.md': '负责记录Layer 9研究与创新层文档治理的严重问题，详细记录严重问题的类型、影响范围、紧急程度和处理建议，为紧急问题处理提供依据，确保严重问题得到及时有效的处理。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_DEEP_AUDIT_REPORT.md': '负责记录Layer 9研究与创新层文档治理的深度审计结果，详细记录三层审计（L1-L3）的发现、问题分析和改进建议，为文档治理深度改进提供依据，确保研究与创新层文档质量全面达标。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_DEEP_AUDIT_SUMMARY.md': '负责提供Layer 9研究与创新层文档治理深度审计的摘要报告，总结关键发现、主要问题和核心建议，为管理层提供快速了解审计结果的入口，确保审计信息的有效传达。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_FINAL_AUDIT_REPORT.md': '负责记录Layer 9研究与创新层文档治理的最终审计结果，总结审计过程、问题和改进效果，为文档治理质量提供最终评估，确保研究与创新层文档治理达到专业标准。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_FINAL_FIX_REPORT.md': '负责记录Layer 9研究与创新层文档治理的最终修复结果，总结修复过程、修复效果和遗留问题，为文档治理改进提供最终记录，确保修复工作的完整性和有效性。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_FIX_REPORT.md': '负责记录Layer 9研究与创新层文档治理的修复过程，详细记录修复的问题、修复方法和修复结果，为文档治理修复提供记录，确保修复工作的可追溯性。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_MAINTENANCE_PLAN.md': '负责制定Layer 9研究与创新层文档治理的维护计划，规划维护周期、维护内容、维护标准和管理机制，为文档治理维护提供指导，确保研究与创新层文档质量持续保持。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_MAINTENANCE_SUMMARY.md': '负责提供Layer 9研究与创新层文档治理维护的摘要报告，总结维护工作、维护效果和改进建议，为维护工作提供总结，确保维护工作的有效性和持续性。',
            
            'LAYER9_DOCUMENT_GOVERNANCE_RE_AUDIT_REPORT.md': '负责记录Layer 9研究与创新层文档治理的复审结果，验证修复效果和改进措施，为文档治理持续改进提供依据，确保研究与创新层文档质量持续提升。',
            
            'LAYER9_WEEKLY_MAINTENANCE_REPORT_20260407.md': '负责记录Layer 9研究与创新层文档治理的周维护情况，详细记录本周维护工作、发现问题和处理结果，为文档治理维护提供周度记录，确保维护工作的及时性和有效性。',
            
            'COMPLETE_BLUEPRINT_V3.md': '负责记录Layer 9研究与创新层的完整蓝图规划（版本3），详细记录架构设计、模块划分和技术方案，为研究与创新体系提供完整蓝图参考，确保架构设计的完整性和可追溯性。',
            
            'COMPLETE_SUPPLEMENT_v2.md': '负责记录Layer 9研究与创新层的完整补充规划（版本2），详细记录补充需求、补充方案和补充效果，为研究与创新体系提供补充参考，确保补充工作的完整性和有效性。',
            
            'CRITICAL_MISSING_V4.md': '负责记录Layer 9研究与创新层的关键缺失问题（版本4），详细记录关键缺失的模块、功能和技术，为研究与创新体系完善提供依据，确保关键缺失得到及时补充。',
            
            'MISSING_MODULES_SUPPLEMENT.md': '负责记录Layer 9研究与创新层的缺失模块补充情况，详细记录缺失模块的类型、补充方案和补充进度，为研究与创新体系完善提供补充记录，确保缺失模块得到有效补充。',
            
            'SYSTEM_MANIFEST_UPDATE_GUIDE.md': '负责提供Layer 9研究与创新层的系统清单更新指南，详细说明更新流程、更新标准和更新要求，为系统清单维护提供指导，确保系统清单的准确性和时效性。',
        }
    
    def fix_all_documents(self):
        """修复所有文档"""
        print('=' * 80)
        print('Layer 9 职责描述修复工具')
        print('=' * 80)
        print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'修复范围: {self.layer9_dir}')
        print()
        
        print('阶段1: 扫描需要修复的文档...')
        documents_to_fix = self.scan_documents()
        print(f'  ✅ 发现 {len(documents_to_fix)} 个需要修复的文档')
        print()
        
        print('阶段2: 修复文档职责描述...')
        for doc in documents_to_fix:
            self.fix_document(doc)
        print(f'  ✅ 修复完成: {self.fixed_count} 个文档')
        print(f'  ⚠️ 跳过: {self.skipped_count} 个文档')
        print()
        
        print('阶段3: 生成修复报告...')
        self.generate_report()
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('修复完成')
        print('=' * 80)
        
        self.print_summary()
    
    def scan_documents(self) -> List[str]:
        """扫描需要修复的文档"""
        layer9_path = Path(self.layer9_dir)
        if not layer9_path.exists():
            print(f'  ❌ 目录不存在: {self.layer9_dir}')
            return []
        
        documents_to_fix = []
        
        for md_file in layer9_path.rglob('*.md'):
            if 'maintenance_records' in str(md_file):
                continue
            
            filename = md_file.name
            
            if filename in self.responsibility_templates:
                try:
                    with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if not self._has_responsibility(content):
                        documents_to_fix.append(str(md_file))
                except Exception as e:
                    print(f'  ⚠️ 无法读取文件: {filename} - {e}')
        
        return documents_to_fix
    
    def _has_responsibility(self, content: str) -> bool:
        """检查文档是否有职责描述"""
        patterns = [
            r'##\s+核心定位',
            r'核心定位[：:]',
            r'职责描述[：:]',
            r'核心职责[：:]',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def fix_document(self, filepath: str):
        """修复单个文档"""
        filename = os.path.basename(filepath)
        
        if filename not in self.responsibility_templates:
            self.skipped_count += 1
            self.results.append({
                'filename': filename,
                'status': 'skipped',
                'reason': '无对应模板'
            })
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            responsibility = self.responsibility_templates[filename]
            
            new_content = self._add_responsibility(content, responsibility)
            
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                f.write(new_content)
            
            self.fixed_count += 1
            self.results.append({
                'filename': filename,
                'status': 'fixed',
                'responsibility': responsibility[:50] + '...'
            })
            
            print(f'  ✅ 已修复: {filename}')
        except Exception as e:
            self.skipped_count += 1
            self.results.append({
                'filename': filename,
                'status': 'error',
                'reason': str(e)
            })
            print(f'  ❌ 修复失败: {filename} - {e}')
    
    def _add_responsibility(self, content: str, responsibility: str) -> str:
        """添加职责描述"""
        if re.match(r'^---', content):
            yaml_end = content.find('---', 3)
            if yaml_end != -1:
                yaml_content = content[:yaml_end + 3]
                body_content = content[yaml_end + 3:]
                
                if 'responsibility:' in yaml_content:
                    yaml_content = re.sub(
                        r'responsibility:\s*\n(\s+-\s+.+\n)*',
                        f'responsibility:\n  - {responsibility}\n',
                        yaml_content
                    )
                else:
                    yaml_content = yaml_content.rstrip() + f'\nresponsibility:\n  - {responsibility}\n---\n'
                
                if not re.search(r'##\s+核心定位', body_content):
                    responsibility_section = f'\n## 核心定位\n\n{responsibility}\n'
                    body_content = responsibility_section + body_content
                
                return yaml_content + body_content
        else:
            responsibility_section = f'---\nresponsibility:\n  - {responsibility}\n---\n\n## 核心定位\n\n{responsibility}\n\n'
            return responsibility_section + content
        
        return content
    
    def generate_report(self):
        """生成修复报告"""
        report_lines = []
        
        report_lines.append('# Layer 9 职责描述修复报告')
        report_lines.append('')
        report_lines.append(f'> **修复时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report_lines.append(f'> **修复范围**: {self.layer9_dir}')
        report_lines.append(f'> **修复类型**: 添加缺少的职责描述')
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📊 修复概要')
        report_lines.append('')
        report_lines.append(f'**修复文档数**: {self.fixed_count}个')
        report_lines.append(f'**跳过文档数**: {self.skipped_count}个')
        report_lines.append(f'**总处理数**: {len(self.results)}个')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📝 修复详情')
        report_lines.append('')
        
        for result in self.results:
            status_emoji = '✅' if result['status'] == 'fixed' else '⚠️' if result['status'] == 'skipped' else '❌'
            report_lines.append(f'### {status_emoji} {result["filename"]}')
            report_lines.append('')
            report_lines.append(f'**状态**: {result["status"]}')
            if 'responsibility' in result:
                report_lines.append(f'**职责描述**: {result["responsibility"]}')
            if 'reason' in result:
                report_lines.append(f'**原因**: {result["reason"]}')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🎯 后续建议')
        report_lines.append('')
        report_lines.append('### 立即验证')
        report_lines.append('- 运行职责冲突检测工具验证职责描述的唯一性')
        report_lines.append('- 检查职责描述是否符合50-200字标准')
        report_lines.append('- 验证YAML头部的responsibility字段是否正确')
        report_lines.append('')
        
        report_lines.append('### 持续改进')
        report_lines.append('- 定期运行审计工具检查文档质量')
        report_lines.append('- 建立文档质量监控机制')
        report_lines.append('- 优化文档创建和审查流程')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        report_lines.append(f'**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        report_content = '\n'.join(report_lines)
        
        output_path = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_RESPONSIBILITY_FIX_REPORT_20260407.md')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f'  ✅ 报告已保存: {output_path}')
    
    def print_summary(self):
        """打印摘要"""
        print()
        print('修复摘要:')
        print(f'  修复成功: {self.fixed_count}')
        print(f'  跳过文档: {self.skipped_count}')
        print(f'  总处理数: {len(self.results)}')


def main():
    fixer = Layer9ResponsibilityFixer()
    fixer.fix_all_documents()


if __name__ == '__main__':
    main()
