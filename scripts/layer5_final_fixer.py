#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5 剩余问题最终修复工具
修复职责描述长度问题和module_id重复
"""

import os
import re
from pathlib import Path
from datetime import datetime


class Layer5FinalFixer:
    """Layer 5剩余问题最终修复器"""
    
    def __init__(self):
        self.base_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        self.fixes = []
        
        self.short_responsibility_fixes = {
            'INDEX.md': '提供建设文档的总入口导航，包含各子目录链接、快速开始指南、文档阅读路径等，支持快速定位所需文档，帮助读者快速了解文档体系结构。',
            '04_CONFIG_TEMPLATES/API_DOCUMENTATION_TEMPLATE.md': '提供API文档的标准模板，包含接口定义、参数说明、返回格式、示例代码等，确保API文档格式统一，支持前后端协作开发。',
            '04_CONFIG_TEMPLATES/CHANGE_REQUEST_TEMPLATE.md': '提供变更请求的标准模板，包含变更内容、影响分析、风险评估、审批流程等，确保变更管理规范化，支持变更追踪和审计。',
            '04_CONFIG_TEMPLATES/DEPLOYMENT_CHECKLIST_TEMPLATE.md': '提供部署检查清单的标准模板，包含部署前检查、部署步骤、部署后验证等，确保部署过程完整，降低部署风险。',
            '04_CONFIG_TEMPLATES/INCIDENT_REPORT_TEMPLATE.md': '提供事故报告的标准模板，包含事故描述、影响范围、根因分析、解决方案等，确保事故处理规范化，支持事故复盘和预防。',
            '04_CONFIG_TEMPLATES/MODULE_DEVELOPMENT_TEMPLATE.md': '提供模块开发的标准模板，包含模块设计、接口定义、测试用例等，确保模块开发规范化，支持模块化开发和复用。',
            '04_CONFIG_TEMPLATES/PERFORMANCE_REPORT_TEMPLATE.md': '提供性能报告的标准模板，包含性能指标、测试结果、优化建议等，确保性能报告格式统一，支持性能分析和优化。',
            '04_CONFIG_TEMPLATES/TECHNICAL_REVIEW_TEMPLATE.md': '提供技术评审的标准模板，包含评审内容、评审标准、评审记录等，确保技术评审规范化，支持技术决策质量保证。',
            '04_CONFIG_TEMPLATES/TEST_PLAN_TEMPLATE.md': '提供测试计划的标准模板，包含测试范围、测试用例、测试环境等，确保测试计划完整，支持测试过程管理和质量保证。',
        }
        
        self.long_responsibility_fixes = {
            'AI_CONSTRUCTION_QUICK_REFERENCE.md': '提供AI辅助建设的快速参考指南，包含常用命令、模板、最佳实践，支持快速上手。',
            'BLUEPRINT_TEMPLATE.md': '提供蓝图文档的标准模板，包含YAML头部、核心定位、设计目标等章节，确保蓝图格式统一。',
            'CONSTRUCTION_SPECIFICATION.md': '定义系统建设的整体规范，包括文档规范、代码规范、流程规范，确保建设标准化。',
            'IMPLEMENTATION_PROGRESS.md': '跟踪记录系统实施进度，包含各模块完成情况、里程碑状态，支持项目管理。',
            'NEW_EMPLOYEE_ONBOARDING_GUIDE.md': '提供新员工入职引导，包含环境配置、权限申请、文档阅读顺序，支持快速融入。',
            'README.md': '提供建设文档的整体说明，包含目录结构、文档分类、使用方法，帮助了解文档体系。',
            'VERSION_MANAGEMENT_GUIDE.md': '定义文档和代码的版本管理规范，包含版本号规则、分支策略，确保版本规范化。',
            '02_IMPLEMENTATION_GUIDES/BACKTEST_ENGINE_GUIDE.md': '提供回测引擎的使用指南，包含配置方法、运行流程、结果分析，支持策略回测。',
            '02_IMPLEMENTATION_GUIDES/EVENT_BUS_GUIDE.md': '提供事件总线的使用指南，包含事件发布订阅、消息格式，支持模块间通信。',
            '02_IMPLEMENTATION_GUIDES/STRATEGY_FACTORY_GUIDE.md': '提供策略工厂的使用指南，包含策略创建、参数配置，支持策略管理和部署。',
            '03_OPERATION_MANUALS/RISK_MONITORING_MANUAL.md': '提供风险监控的详细手册，包含风险指标、预警规则，支持风险实时监控。',
        }
        
        self.module_id_fixes = {
            '05_DESIGN_DOCS/a_stock_rules/README.md': 'A_STOCK_RULES_README_001',
        }
        
        self.index_differentiation = {
            '02_IMPLEMENTATION_GUIDES/INDEX.md': {
                'title': '实施指南索引',
                'responsibility': '提供实施指南文档的导航，包含回测引擎、事件总线、策略工厂等指南链接，支持开发人员快速定位实施相关文档。'
            },
            '05_DESIGN_DOCS/a_stock_rules/INDEX.md': {
                'title': 'A股规则索引',
                'responsibility': '提供A股规则文档的导航，包含规则定义、规则执行、规则管理等文档链接，支持A股交易规则相关文档快速定位。'
            },
            '05_DESIGN_DOCS/trading_costs/INDEX.md': {
                'title': '交易成本索引',
                'responsibility': '提供交易成本文档的导航，包含成本模型、测试用例等文档链接，支持交易成本分析相关文档快速定位。'
            },
            '05_DESIGN_DOCS/ui_design/INDEX.md': {
                'title': 'UI设计索引',
                'responsibility': '提供UI设计文档的导航，包含设计说明、布局标准等文档链接，支持前端UI开发相关文档快速定位。'
            },
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
            except Exception:
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
    
    def fix_short_responsibility(self):
        """修复过短的职责描述"""
        print('\n🔧 修复过短的职责描述...')
        
        for doc_path, new_resp in self.short_responsibility_fixes.items():
            full_path = self.base_dir / doc_path
            if not full_path.exists():
                continue
            
            content = self.read_file(full_path)
            if not content:
                continue
            
            pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n\n|\n##|\n#|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                new_content = content[:match.start(2)] + new_resp + content[match.end(2):]
                
                if self.write_file(full_path, new_content):
                    self.fixes.append({
                        'file': doc_path,
                        'action': f'扩展职责描述到{len(new_resp)}字'
                    })
                    print(f'  ✅ 已修复: {doc_path}')
    
    def fix_long_responsibility(self):
        """修复过长的职责描述"""
        print('\n🔧 修复过长的职责描述...')
        
        for doc_path, new_resp in self.long_responsibility_fixes.items():
            full_path = self.base_dir / doc_path
            if not full_path.exists():
                continue
            
            content = self.read_file(full_path)
            if not content:
                continue
            
            pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n\n|\n##|\n#|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                new_content = content[:match.start(2)] + new_resp + content[match.end(2):]
                
                if self.write_file(full_path, new_content):
                    self.fixes.append({
                        'file': doc_path,
                        'action': f'缩短职责描述到{len(new_resp)}字'
                    })
                    print(f'  ✅ 已修复: {doc_path}')
    
    def fix_module_id_duplicates(self):
        """修复module_id重复"""
        print('\n🔧 修复module_id重复...')
        
        for doc_path, new_id in self.module_id_fixes.items():
            full_path = self.base_dir / doc_path
            if not full_path.exists():
                continue
            
            content = self.read_file(full_path)
            if not content:
                continue
            
            old_id_pattern = r'module_id:\s*05_IMPLEMENTATION_06_CONSTRUCTION_DOCS_05_DESIGN_DOCS_A_STOCK_RULES_001'
            new_content = re.sub(old_id_pattern, f'module_id: {new_id}', content)
            
            if new_content != content:
                if self.write_file(full_path, new_content):
                    self.fixes.append({
                        'file': doc_path,
                        'action': f'修复module_id: {new_id}'
                    })
                    print(f'  ✅ 已修复: {doc_path}')
    
    def fix_similar_index_files(self):
        """修复相似的INDEX.md文件"""
        print('\n🔧 修复相似的INDEX.md文件...')
        
        for doc_path, info in self.index_differentiation.items():
            full_path = self.base_dir / doc_path
            if not full_path.exists():
                continue
            
            content = self.read_file(full_path)
            if not content:
                continue
            
            pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n\n|\n##|\n#|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                new_content = content[:match.start(2)] + info['responsibility'] + content[match.end(2):]
                
                if self.write_file(full_path, new_content):
                    self.fixes.append({
                        'file': doc_path,
                        'action': '更新职责描述以区分相似INDEX'
                    })
                    print(f'  ✅ 已修复: {doc_path}')
    
    def generate_report(self):
        """生成修复报告"""
        print('\n📊 生成修复报告...')
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_FINAL_FIX_REPORT_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 剩余问题最终修复报告\n\n')
            f.write(f'> **修复时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'> **修复范围**: {self.base_dir}\n\n')
            
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
        print('Layer 5 剩余问题最终修复')
        print('=' * 80)
        
        self.fix_short_responsibility()
        self.fix_long_responsibility()
        self.fix_module_id_duplicates()
        self.fix_similar_index_files()
        
        self.generate_report()
        
        print('\n' + '=' * 80)
        print('修复完成')
        print('=' * 80)
        print(f'\n📊 修复统计:')
        print(f'  - 修复文档: {len(self.fixes)}个')


if __name__ == '__main__':
    fixer = Layer5FinalFixer()
    fixer.run()
