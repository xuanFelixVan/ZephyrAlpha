#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 5 全面深度审计问题修复工具
修复审计报告中发现的所有问题
"""

import os
import re
from pathlib import Path
from datetime import datetime


class Layer5ComprehensiveFixer:
    """Layer 5全面深度审计问题修复器"""
    
    def __init__(self):
        self.base_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.fixes = []
        
        self.module_id_fixes = {
            'ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md': 'ALTERNATIVE_DATA_INTEGRATION_001',
            'STRATEGY_SELECTION_BLUEPRINT.md': 'STRATEGY_SELECTION_001',
        }
        
        self.layer_fixes = {
            'QUARTERLY_REBALANCE_BLUEPRINT.md': 'Layer 5.2 (组合优化)',
            'TRANSACTION_COST_AWARE_REBALANCING_BLUEPRINT.md': 'Layer 5.2 (组合优化)',
        }
        
        self.yaml_missing_docs = [
            'RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md',
            'SMART_EXECUTION_ENGINE_BLUEPRINT.md',
            'SYSTEM_ENHANCEMENT_BLUEPRINT.md',
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
    
    def fix_module_id_duplicates(self):
        """修复module_id重复问题"""
        print('\n🔧 修复module_id重复问题...')
        
        blueprints_dir = self.base_dir / '01_BLUEPRINTS'
        
        for doc_name, new_id in self.module_id_fixes.items():
            doc_path = blueprints_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = self.read_file(doc_path)
            if not content:
                continue
            
            old_id_pattern = r'module_id:\s*05_IMPLEMENTATION_06_CONSTRUCTION_DOCS_01_BLUEPRINTS_001'
            new_content = re.sub(old_id_pattern, f'module_id: {new_id}', content)
            
            if new_content != content:
                if self.write_file(doc_path, new_content):
                    self.fixes.append({
                        'file': doc_name,
                        'action': f'修复module_id: {new_id}'
                    })
                    print(f'  ✅ 已修复: {doc_name} -> {new_id}')
        
        print(f'  ✅ module_id修复完成')
    
    def fix_layer_classification(self):
        """修复分类层级错误"""
        print('\n🔧 修复分类层级错误...')
        
        blueprints_dir = self.base_dir / '01_BLUEPRINTS'
        
        for doc_name, new_layer in self.layer_fixes.items():
            doc_path = blueprints_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = self.read_file(doc_path)
            if not content:
                continue
            
            old_layer_pattern = r'layer:\s*Layer 6 \(组合优化层\)'
            new_content = re.sub(old_layer_pattern, f'layer: {new_layer}', content)
            
            if new_content != content:
                if self.write_file(doc_path, new_content):
                    self.fixes.append({
                        'file': doc_name,
                        'action': f'修复层级分类: {new_layer}'
                    })
                    print(f'  ✅ 已修复: {doc_name} -> {new_layer}')
        
        print(f'  ✅ 层级分类修复完成')
    
    def fix_missing_yaml_headers(self):
        """修复缺失的YAML头部"""
        print('\n🔧 修复缺失的YAML头部...')
        
        blueprints_dir = self.base_dir / '01_BLUEPRINTS'
        
        yaml_templates = {
            'RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md': {
                'module_id': 'RISK_ATTRIBUTION_SYSTEM_001',
                'responsibility': ['风险归因分析', '风险分解', '风险贡献计算']
            },
            'SMART_EXECUTION_ENGINE_BLUEPRINT.md': {
                'module_id': 'SMART_EXECUTION_ENGINE_001',
                'responsibility': ['智能执行引擎', '订单执行优化', '执行策略选择']
            },
            'SYSTEM_ENHANCEMENT_BLUEPRINT.md': {
                'module_id': 'SYSTEM_ENHANCEMENT_001',
                'responsibility': ['系统增强', '功能扩展', '性能优化']
            },
        }
        
        for doc_name, template in yaml_templates.items():
            doc_path = blueprints_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = self.read_file(doc_path)
            if not content:
                continue
            
            if content.startswith('---'):
                continue
            
            yaml_header = f'''---
module_id: {template['module_id']}
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
responsibility:
'''
            for resp in template['responsibility']:
                yaml_header += f'  - {resp}\n'
            yaml_header += 'layer: Layer 5.2 (组合优化)\n---\n\n'
            
            new_content = yaml_header + content
            
            if self.write_file(doc_path, new_content):
                self.fixes.append({
                    'file': doc_name,
                    'action': '添加YAML头部'
                })
                print(f'  ✅ 已修复: {doc_name}')
        
        print(f'  ✅ YAML头部修复完成')
    
    def fix_similar_index_files(self):
        """修复相似的INDEX.md文件"""
        print('\n🔧 修复相似的INDEX.md文件...')
        
        index_files = [
            ('02_IMPLEMENTATION_GUIDES/INDEX.md', '实施指南索引', '提供实施指南文档的导航和概览'),
            ('03_OPERATION_MANUALS/INDEX.md', '操作手册索引', '提供操作手册文档的导航和概览'),
            ('04_CONFIG_TEMPLATES/INDEX.md', '配置模板索引', '提供配置模板文档的导航和概览'),
            ('05_DESIGN_DOCS/INDEX.md', '设计文档索引', '提供设计文档的导航和概览'),
            ('06_CHECKLISTS/INDEX.md', '检查清单索引', '提供检查清单文档的导航和概览'),
            ('05_DESIGN_DOCS/a_stock_rules/INDEX.md', 'A股规则索引', '提供A股规则文档的导航和概览'),
            ('05_DESIGN_DOCS/data_consistency/INDEX.md', '数据一致性索引', '提供数据一致性文档的导航和概览'),
            ('05_DESIGN_DOCS/trading_costs/INDEX.md', '交易成本索引', '提供交易成本文档的导航和概览'),
            ('05_DESIGN_DOCS/ui_design/INDEX.md', 'UI设计索引', '提供UI设计文档的导航和概览'),
            ('05_DESIGN_DOCS/web_interface/INDEX.md', 'Web接口索引', '提供Web接口文档的导航和概览'),
            ('05_DESIGN_DOCS/database/INDEX.md', '数据库设计索引', '提供数据库设计文档的导航和概览'),
        ]
        
        for index_path, title, description in index_files:
            full_path = self.base_dir / index_path
            if not full_path.exists():
                continue
            
            content = self.read_file(full_path)
            if not content:
                continue
            
            new_content = f'''# {title}

> **核心定位**: {description}，支持快速定位和访问相关文档。

## 📋 文档列表

'''
            
            dir_path = full_path.parent
            md_files = [f for f in dir_path.glob('*.md') if f.name != 'INDEX.md']
            
            for md_file in sorted(md_files):
                new_content += f'- [{md_file.stem}]({md_file.name})\n'
            
            new_content += '''
---

**最后更新**: ''' + datetime.now().strftime('%Y-%m-%d') + '''
'''
            
            if self.write_file(full_path, new_content):
                self.fixes.append({
                    'file': index_path,
                    'action': '重写INDEX.md内容'
                })
                print(f'  ✅ 已修复: {index_path}')
        
        print(f'  ✅ INDEX.md修复完成')
    
    def fix_similar_blueprint_files(self):
        """修复相似的蓝图文件"""
        print('\n🔧 修复相似的蓝图文件...')
        
        blueprints_dir = self.base_dir / '01_BLUEPRINTS'
        
        similar_pairs = [
            ('BLACK_LITTERMAN_MODEL_BLUEPRINT.md', 'RISK_PARITY_STRATEGY_BLUEPRINT.md'),
        ]
        
        responsibility_updates = {
            'BLACK_LITTERMAN_MODEL_BLUEPRINT.md': '负责Black-Litterman模型设计，实现市场观点融合、后验收益估计、协方差调整，支持投资组合优化决策。',
            'RISK_PARITY_STRATEGY_BLUEPRINT.md': '负责风险平价策略设计，实现风险预算分配、风险贡献均衡、杠杆调整，支持风险均衡投资组合构建。',
        }
        
        for doc_name, new_resp in responsibility_updates.items():
            doc_path = blueprints_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = self.read_file(doc_path)
            if not content:
                continue
            
            pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n\n|\n##|\n#|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                new_content = content[:match.start(2)] + new_resp + content[match.end(2):]
                
                if self.write_file(doc_path, new_content):
                    self.fixes.append({
                        'file': doc_name,
                        'action': '更新职责描述以区分相似文档'
                    })
                    print(f'  ✅ 已修复: {doc_name}')
        
        print(f'  ✅ 蓝图文件修复完成')
    
    def generate_report(self):
        """生成修复报告"""
        print('\n📊 生成修复报告...')
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_COMPREHENSIVE_FIX_REPORT_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 全面深度审计问题修复报告\n\n')
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
        print('Layer 5 全面深度审计问题修复')
        print('=' * 80)
        
        self.fix_module_id_duplicates()
        self.fix_layer_classification()
        self.fix_missing_yaml_headers()
        self.fix_similar_index_files()
        self.fix_similar_blueprint_files()
        
        self.generate_report()
        
        print('\n' + '=' * 80)
        print('修复完成')
        print('=' * 80)
        print(f'\n📊 修复统计:')
        print(f'  - 修复文档: {len(self.fixes)}个')


if __name__ == '__main__':
    fixer = Layer5ComprehensiveFixer()
    fixer.run()
