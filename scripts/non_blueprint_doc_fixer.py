#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5 非蓝图文档修复工具
修复缺少职责描述和标准章节的非蓝图文档
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class NonBlueprintDocFixer:
    """非蓝图文档修复器"""
    
    def __init__(self):
        self.base_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        self.fixes = []
        
        self.doc_responsibilities = {
            'AI_CONSTRUCTION_QUICK_REFERENCE.md': {
                'title': 'AI建设快速参考',
                'responsibility': '提供AI辅助建设的快速参考指南，包含常用命令、模板、最佳实践等，支持快速上手和日常查阅。'
            },
            'BLUEPRINT_TEMPLATE.md': {
                'title': '蓝图模板',
                'responsibility': '提供蓝图文档的标准模板，包含YAML头部、核心定位、设计目标、核心功能等章节结构，确保蓝图文档格式统一。'
            },
            'CONSTRUCTION_SPECIFICATION.md': {
                'title': '建设规范',
                'responsibility': '定义系统建设的整体规范，包括文档规范、代码规范、流程规范等，确保建设过程标准化。'
            },
            'IMPLEMENTATION_PROGRESS.md': {
                'title': '实施进度',
                'responsibility': '跟踪记录系统实施进度，包含各模块完成情况、里程碑达成状态、待办事项等，支持项目管理和进度可视化。'
            },
            'INDEX.md': {
                'title': '建设文档索引',
                'responsibility': '提供建设文档的总入口导航，包含各子目录链接、快速开始指南、文档阅读路径等，支持快速定位所需文档。'
            },
            'NEW_EMPLOYEE_ONBOARDING_GUIDE.md': {
                'title': '新员工入职指南',
                'responsibility': '提供新员工入职引导，包含环境配置、权限申请、文档阅读顺序、常用工具介绍等，支持快速融入团队。'
            },
            'README.md': {
                'title': '建设文档说明',
                'responsibility': '提供建设文档的整体说明，包含目录结构、文档分类、使用方法等，帮助读者快速了解文档体系。'
            },
            'VERSION_MANAGEMENT_GUIDE.md': {
                'title': '版本管理指南',
                'responsibility': '定义文档和代码的版本管理规范，包含版本号规则、分支策略、发布流程等，确保版本管理规范化。'
            },
        }
        
        self.subdir_docs = {
            '02_IMPLEMENTATION_GUIDES': {
                'BACKTEST_ENGINE_GUIDE.md': {
                    'title': '回测引擎指南',
                    'responsibility': '提供回测引擎的使用指南，包含配置方法、运行流程、结果分析等，支持策略回测验证。'
                },
                'EVENT_BUS_GUIDE.md': {
                    'title': '事件总线指南',
                    'responsibility': '提供事件总线的使用指南，包含事件发布订阅、消息格式、错误处理等，支持模块间通信。'
                },
                'INDEX.md': {
                    'title': '实施指南索引',
                    'responsibility': '提供实施指南文档的导航和概览，支持快速定位和访问相关指南文档。'
                },
                'STRATEGY_FACTORY_GUIDE.md': {
                    'title': '策略工厂指南',
                    'responsibility': '提供策略工厂的使用指南，包含策略创建、参数配置、策略组合等，支持策略管理和部署。'
                },
            },
            '03_OPERATION_MANUALS': {
                'DEPLOYMENT_MANUAL.md': {
                    'title': '部署手册',
                    'responsibility': '提供系统部署的详细手册，包含环境准备、部署步骤、配置说明、验证方法等，支持系统上线部署。'
                },
                'INDEX.md': {
                    'title': '操作手册索引',
                    'responsibility': '提供操作手册文档的导航和概览，支持快速定位和访问相关操作文档。'
                },
                'MAINTENANCE_MANUAL.md': {
                    'title': '维护手册',
                    'responsibility': '提供系统维护的详细手册，包含日常维护、故障排查、性能优化等，支持系统稳定运行。'
                },
                'MONITORING_MANUAL.md': {
                    'title': '监控手册',
                    'responsibility': '提供系统监控的详细手册，包含监控指标、告警配置、日志分析等，支持系统状态监控。'
                },
                'RISK_MONITORING_MANUAL.md': {
                    'title': '风险监控手册',
                    'responsibility': '提供风险监控的详细手册，包含风险指标、预警规则、应急处理等，支持风险实时监控。'
                },
            },
            '04_CONFIG_TEMPLATES': {
                'API_DOCUMENTATION_TEMPLATE.md': {
                    'title': 'API文档模板',
                    'responsibility': '提供API文档的标准模板，包含接口定义、参数说明、返回格式、示例代码等，确保API文档格式统一。'
                },
                'CHANGE_REQUEST_TEMPLATE.md': {
                    'title': '变更请求模板',
                    'responsibility': '提供变更请求的标准模板，包含变更内容、影响分析、风险评估、审批流程等，确保变更管理规范化。'
                },
                'DEPLOYMENT_CHECKLIST_TEMPLATE.md': {
                    'title': '部署检查清单模板',
                    'responsibility': '提供部署检查清单的标准模板，包含部署前检查、部署步骤、部署后验证等，确保部署过程完整。'
                },
                'INCIDENT_REPORT_TEMPLATE.md': {
                    'title': '事故报告模板',
                    'responsibility': '提供事故报告的标准模板，包含事故描述、影响范围、根因分析、解决方案等，确保事故处理规范化。'
                },
                'INDEX.md': {
                    'title': '配置模板索引',
                    'responsibility': '提供配置模板文档的导航和概览，支持快速定位和访问相关模板文档。'
                },
                'MODULE_DEVELOPMENT_TEMPLATE.md': {
                    'title': '模块开发模板',
                    'responsibility': '提供模块开发的标准模板，包含模块设计、接口定义、测试用例等，确保模块开发规范化。'
                },
                'PERFORMANCE_REPORT_TEMPLATE.md': {
                    'title': '性能报告模板',
                    'responsibility': '提供性能报告的标准模板，包含性能指标、测试结果、优化建议等，确保性能报告格式统一。'
                },
                'TECHNICAL_REVIEW_TEMPLATE.md': {
                    'title': '技术评审模板',
                    'responsibility': '提供技术评审的标准模板，包含评审内容、评审标准、评审记录等，确保技术评审规范化。'
                },
                'TEST_PLAN_TEMPLATE.md': {
                    'title': '测试计划模板',
                    'responsibility': '提供测试计划的标准模板，包含测试范围、测试用例、测试环境等，确保测试计划完整。'
                },
            },
            '05_DESIGN_DOCS': {
                'INDEX.md': {
                    'title': '设计文档索引',
                    'responsibility': '提供设计文档的导航和概览，支持快速定位和访问相关设计文档。'
                },
                'PERSONAL_TECH_DECISION_CHECKLIST.md': {
                    'title': '个人技术决策检查清单',
                    'responsibility': '提供个人技术决策的检查清单，包含技术选型、方案对比、风险评估等，支持技术决策规范化。'
                },
                'PROFESSIONAL_QUANT_DEVELOPMENT_PROCESS.md': {
                    'title': '专业量化开发流程',
                    'responsibility': '定义专业量化系统的开发流程，包含需求分析、设计开发、测试部署等阶段，确保开发过程规范化。'
                },
                'README.md': {
                    'title': '设计文档说明',
                    'responsibility': '提供设计文档的整体说明，包含设计原则、文档分类、阅读路径等，帮助读者快速了解设计文档体系。'
                },
                'REVIEW_MATERIAL_DISTRIBUTION_CHECKLIST.md': {
                    'title': '评审材料分发检查清单',
                    'responsibility': '提供评审材料分发的检查清单，包含材料准备、分发流程、反馈收集等，确保评审材料分发规范化。'
                },
                'T.08.AR001.a_stock_rule_engine_design.md': {
                    'title': 'A股规则引擎设计',
                    'responsibility': '提供A股规则引擎的详细设计，包含规则定义、规则执行、规则管理等，支持A股交易规则实现。'
                },
                'TECHNICAL_REVIEW_MEETING_AGENDA.md': {
                    'title': '技术评审会议议程',
                    'responsibility': '提供技术评审会议的标准议程，包含评审内容、时间安排、参与人员等，确保技术评审会议高效。'
                },
                'TECHNICAL_SOLUTION_SUMMARY_REPORT.md': {
                    'title': '技术方案总结报告',
                    'responsibility': '提供技术方案总结报告的模板，包含方案概述、技术选型、实施计划等，确保技术方案总结完整。'
                },
            },
            '06_CHECKLISTS': {
                'CODE_REVIEW_CHECKLIST.md': {
                    'title': '代码评审检查清单',
                    'responsibility': '提供代码评审的检查清单，包含代码规范、性能优化、安全检查等，确保代码质量。'
                },
                'DOCUMENT_QUALITY_GATE.md': {
                    'title': '文档质量门禁',
                    'responsibility': '定义文档质量门禁标准，包含格式规范、内容完整性、索引一致性等，确保文档质量达标。'
                },
                'INDEX.md': {
                    'title': '检查清单索引',
                    'responsibility': '提供检查清单文档的导航和概览，支持快速定位和访问相关检查清单。'
                },
                'POST_DEPLOYMENT_CHECKLIST.md': {
                    'title': '部署后检查清单',
                    'responsibility': '提供部署后的检查清单，包含功能验证、性能检查、日志检查等，确保部署成功。'
                },
                'PRE_DEPLOYMENT_CHECKLIST.md': {
                    'title': '部署前检查清单',
                    'responsibility': '提供部署前的检查清单，包含环境准备、配置检查、依赖验证等，确保部署准备就绪。'
                },
            },
        }
        
        self.deep_subdir_docs = {
            '05_DESIGN_DOCS/a_stock_rules': {
                'INDEX.md': {
                    'title': 'A股规则索引',
                    'responsibility': '提供A股规则文档的导航和概览，支持快速定位和访问相关规则文档。'
                },
                'README.md': {
                    'title': 'A股规则说明',
                    'responsibility': '提供A股规则的整体说明，包含规则分类、规则优先级、规则冲突处理等，帮助理解A股规则体系。'
                },
            },
            '05_DESIGN_DOCS/database': {
                'INDEX.md': {
                    'title': '数据库设计索引',
                    'responsibility': '提供数据库设计文档的导航和概览，支持快速定位和访问相关数据库设计文档。'
                },
                'P0_01_Database_Design_Document.md': {
                    'title': '数据库设计文档',
                    'responsibility': '提供数据库的整体设计文档，包含数据库架构、表结构设计、索引设计等，支持数据库开发。'
                },
                'P0_01_Database_Design_Review_Report.md': {
                    'title': '数据库设计评审报告',
                    'responsibility': '提供数据库设计的评审报告，包含评审内容、评审意见、改进建议等，确保数据库设计质量。'
                },
                'P0_02_Data_Dictionary.md': {
                    'title': '数据字典',
                    'responsibility': '提供数据字典文档，包含数据元素定义、数据类型、数据约束等，确保数据定义规范化。'
                },
                'P0_03_Internal_Service_Interface_Design.md': {
                    'title': '内部服务接口设计',
                    'responsibility': '提供内部服务接口的详细设计，包含接口定义、参数说明、返回格式等，支持服务间通信。'
                },
                'P0_04_Third_Party_Interface_Integration_Design.md': {
                    'title': '第三方接口集成设计',
                    'responsibility': '提供第三方接口集成的详细设计，包含接口对接、数据转换、异常处理等，支持外部系统集成。'
                },
                'P0_05_Multi_Engine_Coordinator_Design.md': {
                    'title': '多引擎协调器设计',
                    'responsibility': '提供多引擎协调器的详细设计，包含引擎调度、负载均衡、故障转移等，支持多引擎协同工作。'
                },
            },
            '05_DESIGN_DOCS/data_consistency': {
                'INDEX.md': {
                    'title': '数据一致性索引',
                    'responsibility': '提供数据一致性文档的导航和概览，支持快速定位和访问相关数据一致性文档。'
                },
                'COMPENSATING_TRANSACTION_DESIGN.md': {
                    'title': '补偿事务设计',
                    'responsibility': '提供补偿事务的详细设计，包含事务补偿机制、补偿流程、异常处理等，支持分布式事务一致性。'
                },
                'MULTI_ENGINE_DATA_CONSISTENCY_DESIGN.md': {
                    'title': '多引擎数据一致性设计',
                    'responsibility': '提供多引擎数据一致性的详细设计，包含数据同步、冲突解决、一致性保证等，支持多引擎数据一致性。'
                },
                'SAGA_IMPLEMENTATION_FLOWCHART.md': {
                    'title': 'SAGA实现流程图',
                    'responsibility': '提供SAGA模式的实现流程图，包含事务流程、补偿流程、状态转换等，支持SAGA事务实现。'
                },
            },
            '05_DESIGN_DOCS/trading_costs': {
                'INDEX.md': {
                    'title': '交易成本索引',
                    'responsibility': '提供交易成本文档的导航和概览，支持快速定位和访问相关交易成本文档。'
                },
                'T.05.TE001.trading_cost_model_algorithm_document.md': {
                    'title': '交易成本模型算法文档',
                    'responsibility': '提供交易成本模型的算法文档，包含成本模型、参数估计、模型验证等，支持交易成本分析。'
                },
                'TRADING_COST_TEST_CASE_DESIGN.md': {
                    'title': '交易成本测试用例设计',
                    'responsibility': '提供交易成本的测试用例设计，包含测试场景、测试数据、预期结果等，支持交易成本模型测试。'
                },
            },
            '05_DESIGN_DOCS/ui_design': {
                'INDEX.md': {
                    'title': 'UI设计索引',
                    'responsibility': '提供UI设计文档的导航和概览，支持快速定位和访问相关UI设计文档。'
                },
                'README.md': {
                    'title': 'UI设计说明',
                    'responsibility': '提供UI设计的整体说明，包含设计原则、组件库、样式规范等，帮助理解UI设计体系。'
                },
                'ui_layout_standard.md': {
                    'title': 'UI布局标准',
                    'responsibility': '定义UI布局的标准规范，包含布局规则、间距规范、响应式设计等，确保UI布局一致性。'
                },
            },
            '05_DESIGN_DOCS/web_interface': {
                'INDEX.md': {
                    'title': 'Web接口索引',
                    'responsibility': '提供Web接口文档的导航和概览，支持快速定位和访问相关Web接口文档。'
                },
                'API_INTERFACE_SPECIFICATION.md': {
                    'title': 'API接口规范',
                    'responsibility': '定义API接口的规范，包含接口格式、认证方式、错误码等，确保API接口标准化。'
                },
                'FRONTEND_COMPONENT_STRUCTURE.md': {
                    'title': '前端组件结构',
                    'responsibility': '定义前端组件的结构规范，包含组件分类、组件接口、组件通信等，确保前端组件规范化。'
                },
                'T.06.UI001.web_management_interface_architecture_design.md': {
                    'title': 'Web管理界面架构设计',
                    'responsibility': '提供Web管理界面的架构设计，包含界面架构、模块划分、技术选型等，支持Web管理界面开发。'
                },
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
    
    def add_core_positioning(self, content: str, title: str, responsibility: str) -> str:
        """添加核心定位章节"""
        core_positioning = f'''
## 核心定位

{responsibility}

'''
        
        if '## 核心定位' in content:
            return content
        
        lines = content.split('\n')
        insert_pos = 0
        
        for i, line in enumerate(lines):
            if line.startswith('# '):
                insert_pos = i + 1
                break
        
        lines.insert(insert_pos, core_positioning)
        return '\n'.join(lines)
    
    def add_design_goals(self, content: str) -> str:
        """添加设计目标章节"""
        design_goals = '''
## 设计目标

### 主要目标

1. **功能完整性**: 确保文档内容完整，满足使用需求
2. **易用性**: 提高文档可读性，便于快速理解
3. **可维护性**: 文档结构清晰，便于后续维护
4. **一致性**: 确保文档格式和风格统一

### 质量目标

- 文档完整性: 100%
- 格式规范性: 100%
- 内容准确性: 100%

'''
        
        if '## 设计目标' in content:
            return content
        
        lines = content.split('\n')
        insert_pos = len(lines)
        
        for i, line in enumerate(lines):
            if line.startswith('## ') and '核心定位' not in line:
                insert_pos = i
                break
        
        lines.insert(insert_pos, design_goals)
        return '\n'.join(lines)
    
    def fix_root_docs(self):
        """修复根目录文档"""
        print('\n🔧 修复根目录文档...')
        
        for doc_name, info in self.doc_responsibilities.items():
            doc_path = self.base_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = self.read_file(doc_path)
            if not content:
                continue
            
            if '## 核心定位' in content:
                print(f'  ⏭️ 已有核心定位: {doc_name}')
                continue
            
            new_content = self.add_core_positioning(content, info['title'], info['responsibility'])
            new_content = self.add_design_goals(new_content)
            
            if self.write_file(doc_path, new_content):
                self.fixes.append({
                    'file': doc_name,
                    'action': '添加核心定位和设计目标章节'
                })
                print(f'  ✅ 已修复: {doc_name}')
    
    def fix_subdir_docs(self):
        """修复子目录文档"""
        print('\n🔧 修复子目录文档...')
        
        for subdir, docs in self.subdir_docs.items():
            subdir_path = self.base_dir / subdir
            
            for doc_name, info in docs.items():
                doc_path = subdir_path / doc_name
                if not doc_path.exists():
                    continue
                
                content = self.read_file(doc_path)
                if not content:
                    continue
                
                if '## 核心定位' in content:
                    print(f'  ⏭️ 已有核心定位: {subdir}/{doc_name}')
                    continue
                
                new_content = self.add_core_positioning(content, info['title'], info['responsibility'])
                new_content = self.add_design_goals(new_content)
                
                if self.write_file(doc_path, new_content):
                    self.fixes.append({
                        'file': f'{subdir}/{doc_name}',
                        'action': '添加核心定位和设计目标章节'
                    })
                    print(f'  ✅ 已修复: {subdir}/{doc_name}')
    
    def fix_deep_subdir_docs(self):
        """修复深层子目录文档"""
        print('\n🔧 修复深层子目录文档...')
        
        for subdir, docs in self.deep_subdir_docs.items():
            subdir_path = self.base_dir / subdir
            
            for doc_name, info in docs.items():
                doc_path = subdir_path / doc_name
                if not doc_path.exists():
                    continue
                
                content = self.read_file(doc_path)
                if not content:
                    continue
                
                if '## 核心定位' in content:
                    print(f'  ⏭️ 已有核心定位: {subdir}/{doc_name}')
                    continue
                
                new_content = self.add_core_positioning(content, info['title'], info['responsibility'])
                new_content = self.add_design_goals(new_content)
                
                if self.write_file(doc_path, new_content):
                    self.fixes.append({
                        'file': f'{subdir}/{doc_name}',
                        'action': '添加核心定位和设计目标章节'
                    })
                    print(f'  ✅ 已修复: {subdir}/{doc_name}')
    
    def fix_main_index(self):
        """修复主INDEX.md，添加所有文档链接"""
        print('\n🔧 修复主INDEX.md索引完整性...')
        
        index_path = self.base_dir / 'INDEX.md'
        if not index_path.exists():
            print(f'  ⚠️ INDEX.md不存在')
            return
        
        content = self.read_file(index_path)
        if not content:
            return
        
        all_docs = []
        
        for md_file in self.base_dir.glob('*.md'):
            if md_file.name != 'INDEX.md':
                all_docs.append(md_file.name)
        
        for subdir in self.base_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                for md_file in subdir.glob('**/*.md'):
                    rel_path = md_file.relative_to(self.base_dir)
                    all_docs.append(str(rel_path))
        
        missing_docs = []
        for doc in all_docs:
            if doc not in content:
                missing_docs.append(doc)
        
        if not missing_docs:
            print(f'  ✅ INDEX.md已包含所有文档')
            return
        
        print(f'  📝 发现{len(missing_docs)}个缺失文档链接')
        
        additional_links = '\n### 其他文档\n\n'
        for doc in sorted(missing_docs):
            doc_name = Path(doc).stem
            additional_links += f'- [{doc_name}]({doc})\n'
        
        if '---' in content:
            parts = content.rsplit('---', 1)
            new_content = parts[0] + additional_links + '\n---' + parts[1]
        else:
            new_content = content + '\n' + additional_links
        
        if self.write_file(index_path, new_content):
            self.fixes.append({
                'file': 'INDEX.md',
                'action': f'添加{len(missing_docs)}个缺失文档链接'
            })
            print(f'  ✅ 已添加{len(missing_docs)}个缺失文档链接')
    
    def generate_report(self):
        """生成修复报告"""
        print('\n📊 生成修复报告...')
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'NON_BLUEPRINT_DOC_FIX_REPORT_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# 非蓝图文档修复报告\n\n')
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
        print('非蓝图文档修复')
        print('=' * 80)
        
        self.fix_root_docs()
        self.fix_subdir_docs()
        self.fix_deep_subdir_docs()
        self.fix_main_index()
        
        self.generate_report()
        
        print('\n' + '=' * 80)
        print('修复完成')
        print('=' * 80)
        print(f'\n📊 修复统计:')
        print(f'  - 修复文档: {len(self.fixes)}个')


if __name__ == '__main__':
    fixer = NonBlueprintDocFixer()
    fixer.run()
