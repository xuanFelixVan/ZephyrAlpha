#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 5 剩余问题修复工具
修复内容相似文档和编码问题
"""

import os
import re
from pathlib import Path
from datetime import datetime


class Layer5RemainingFixer:
    """Layer 5剩余问题修复器"""
    
    def __init__(self):
        self.base_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        self.fixes = []
        
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
    
    def fix_database_design_docs(self):
        """修复数据库设计文档的编码问题和重复YAML"""
        print('\n🔧 修复数据库设计文档...')
        
        database_dir = self.base_dir / '05_DESIGN_DOCS' / 'database'
        
        docs_to_fix = {
            'P0_06_Account_Management_Detailed_Design.md': {
                'module_id': 'P0_06_ACCOUNT_MANAGEMENT_001',
                'title': '账户管理详细设计',
                'responsibility': ['账户生命周期管理', '资金管理', '账户快照'],
                'description': '负责账户全生命周期管理，包括账户创建、资金划转、账户冻结、账户关闭等功能，支持模拟账户和实盘账户的统一管理。'
            },
            'P0_07_Order_Management_Detailed_Design.md': {
                'module_id': 'P0_07_ORDER_MANAGEMENT_001',
                'title': '订单管理详细设计',
                'responsibility': ['订单生命周期管理', '订单执行', '订单查询'],
                'description': '负责订单全生命周期管理，包括订单创建、订单执行、订单查询、订单撤销等功能，支持多种订单类型和执行策略。'
            }
        }
        
        for doc_name, template in docs_to_fix.items():
            doc_path = database_dir / doc_name
            if not doc_path.exists():
                print(f'  ⚠️ 文件不存在: {doc_name}')
                continue
            
            content = self.read_file(doc_path)
            if not content:
                print(f'  ⚠️ 无法读取: {doc_name}')
                continue
            
            clean_content = re.sub(r'^---\s*\n.*?^---\s*\n', '', content, count=2, flags=re.MULTILINE | re.DOTALL)
            
            clean_content = re.sub(r'^\ufeff', '', clean_content)
            
            yaml_header = f'''---
module_id: {template['module_id']}
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
'''
            for resp in template['responsibility']:
                yaml_header += f'  - {resp}\n'
            yaml_header += f'''layer: Layer 5.2 (组合优化)
---

# {template['title']}

## 核心定位

{template['description']}

'''
            
            new_content = yaml_header + clean_content
            
            if self.write_file(doc_path, new_content):
                self.fixes.append({
                    'file': doc_name,
                    'action': '修复编码问题和重复YAML头部'
                })
                print(f'  ✅ 已修复: {doc_name}')
        
        print(f'  ✅ 数据库设计文档修复完成')
    
    def fix_similar_blueprint_content(self):
        """进一步区分相似蓝图文档的内容"""
        print('\n🔧 区分相似蓝图文档内容...')
        
        blueprints_dir = self.base_dir / '01_BLUEPRINTS'
        
        content_updates = {
            'BLACK_LITTERMAN_MODEL_BLUEPRINT.md': {
                'core_features': '''
## 核心功能

### Black-Litterman模型特有功能

1. **市场均衡收益计算**: 基于市值权重计算市场均衡收益
2. **观点融合引擎**: 将投资者观点与市场均衡收益融合
3. **后验收益估计**: 使用贝叶斯方法估计后验收益分布
4. **协方差调整**: 根据观点不确定性调整协方差矩阵
5. **观点矩阵构建**: 支持相对观点和绝对观点的表达

### 模型参数

- 风险厌恶系数 (δ)
- 观点置信度矩阵 (Ω)
- 观点矩阵 (P, Q)
- 市场均衡权重 (w_mkt)
'''
            },
            'RISK_PARITY_STRATEGY_BLUEPRINT.md': {
                'core_features': '''
## 核心功能

### 风险平价策略特有功能

1. **风险预算分配**: 根据资产风险特性分配风险预算
2. **风险贡献均衡**: 确保各资产风险贡献相等
3. **杠杆调整机制**: 通过杠杆调整实现目标风险水平
4. **风险平价权重优化**: 求解风险平价最优权重
5. **风险贡献监控**: 实时监控各资产风险贡献

### 策略参数

- 目标风险水平 (σ_target)
- 风险预算向量 (b)
- 杠杆上限 (L_max)
- 协方差矩阵 (Σ)
'''
            }
        }
        
        for doc_name, updates in content_updates.items():
            doc_path = blueprints_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = self.read_file(doc_path)
            if not content:
                continue
            
            if 'Black-Litterman模型特有功能' in content or '风险平价策略特有功能' in content:
                print(f'  ⏭️ 已区分: {doc_name}')
                continue
            
            pattern = r'(##\s+核心功能\s*\n)(.*?)(?=\n##|\n#|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                new_content = content[:match.start(2)] + updates['core_features'] + content[match.end(2):]
                
                if self.write_file(doc_path, new_content):
                    self.fixes.append({
                        'file': doc_name,
                        'action': '添加特有功能描述以区分相似文档'
                    })
                    print(f'  ✅ 已修复: {doc_name}')
        
        print(f'  ✅ 蓝图文档区分完成')
    
    def generate_report(self):
        """生成修复报告"""
        print('\n📊 生成修复报告...')
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_REMAINING_FIX_REPORT_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 剩余问题修复报告\n\n')
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
        print('Layer 5 剩余问题修复')
        print('=' * 80)
        
        self.fix_database_design_docs()
        self.fix_similar_blueprint_content()
        
        self.generate_report()
        
        print('\n' + '=' * 80)
        print('修复完成')
        print('=' * 80)
        print(f'\n📊 修复统计:')
        print(f'  - 修复文档: {len(self.fixes)}个')


if __name__ == '__main__':
    fixer = Layer5RemainingFixer()
    fixer.run()
