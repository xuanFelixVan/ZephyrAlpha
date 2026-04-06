#!/usr/bin/env python3
"""
文档结构检查器

功能:
1. 检查文档结构是否符合标准
2. 检查YAML头部完整性
3. 检查核心定位章节
4. 生成结构检查报告
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

class DocumentStructureChecker:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.blueprint_files = []
        self.check_results = []
        
        # 必需的YAML字段
        self.required_yaml_fields = [
            'module_id', 'version', 'status', 'created_date', 
            'last_updated', 'owner', 'layer', 'standard_type',
            'applicable_scope', 'compliance_level'
        ]
    
    def run(self):
        """执行检查"""
        print('=' * 80)
        print('文档结构检查器')
        print('=' * 80)
        print()
        
        # 1. 扫描蓝图文件
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
        print()
        
        # 2. 检查文档结构
        print('2. 检查文档结构...')
        self.check_structure()
        print(f'  ✅ 已检查{len(self.check_results)}个文档')
        print()
        
        # 3. 生成报告
        print('3. 生成报告...')
        self.generate_report()
        print(f'  ✅ 报告已生成')
        print()
        
        # 4. 输出统计
        self.print_statistics()
        
        print('=' * 80)
        print('检查完成')
        print('=' * 80)
    
    def scan_blueprint_files(self):
        """扫描蓝图文件"""
        if os.path.exists(self.blueprints_dir):
            for root, dirs, files in os.walk(self.blueprints_dir):
                for file in files:
                    if file.endswith('.md') and file != 'INDEX.md':
                        filepath = os.path.join(root, file)
                        self.blueprint_files.append(filepath)
    
    def check_structure(self):
        """检查结构"""
        for filepath in self.blueprint_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                result = {
                    'filepath': filepath,
                    'filename': os.path.basename(filepath),
                    'has_yaml': False,
                    'yaml_complete': False,
                    'missing_yaml_fields': [],
                    'has_core_positioning': False,
                    'core_positioning_quality': '',
                    'has_title': False,
                    'structure_score': 0,
                    'issues': [],
                    'status': '✅ 完整'
                }
                
                # 检查YAML头部
                yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
                yaml_match = re.search(yaml_pattern, content, re.DOTALL)
                
                if yaml_match:
                    result['has_yaml'] = True
                    yaml_content = yaml_match.group(1)
                    
                    # 检查必需字段
                    missing_fields = []
                    for field in self.required_yaml_fields:
                        if f'{field}:' not in yaml_content:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        result['yaml_complete'] = True
                    else:
                        result['missing_yaml_fields'] = missing_fields
                        result['issues'].append(f'YAML缺少字段: {", ".join(missing_fields)}')
                        result['status'] = '⚠️ YAML不完整'
                else:
                    result['issues'].append('缺少YAML头部')
                    result['status'] = '❌ 缺少YAML'
                
                # 检查核心定位章节
                core_pattern = r'##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
                core_match = re.search(core_pattern, content, re.DOTALL)
                
                if core_match:
                    result['has_core_positioning'] = True
                    core_content = core_match.group(1).strip()
                    
                    # 评估核心定位质量
                    if len(core_content) < 50:
                        result['core_positioning_quality'] = '⚠️ 过短'
                        result['issues'].append('核心定位描述过短')
                    elif len(core_content) > 200:
                        result['core_positioning_quality'] = '⚠️ 过长'
                        result['issues'].append('核心定位描述过长')
                    else:
                        result['core_positioning_quality'] = '✅ 合适'
                else:
                    result['issues'].append('缺少核心定位章节')
                    result['status'] = '❌ 缺少核心定位'
                
                # 检查文档标题
                title_pattern = r'^#\s+(.+?)$'
                title_match = re.search(title_pattern, content, re.MULTILINE)
                
                if title_match:
                    result['has_title'] = True
                else:
                    result['issues'].append('缺少文档标题')
                    if result['status'] == '✅ 完整':
                        result['status'] = '⚠️ 缺少标题'
                
                # 计算结构得分
                score = 0
                if result['has_yaml']:
                    score += 25
                if result['yaml_complete']:
                    score += 25
                if result['has_core_positioning']:
                    score += 25
                if result['has_title']:
                    score += 25
                
                result['structure_score'] = score
                
                self.check_results.append(result)
            
            except Exception as e:
                print(f'  ⚠️ 无法检查文件: {filepath} - {e}')
    
    def generate_report(self):
        """生成报告"""
        report_dir = 'docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state'
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        report_path = os.path.join(report_dir, f'DOCUMENT_STRUCTURE_CHECK_REPORT_{timestamp}.md')
        
        # 统计数据
        total = len(self.check_results)
        complete = sum(1 for r in self.check_results if r['status'] == '✅ 完整')
        has_yaml = sum(1 for r in self.check_results if r['has_yaml'])
        yaml_complete = sum(1 for r in self.check_results if r['yaml_complete'])
        has_core = sum(1 for r in self.check_results if r['has_core_positioning'])
        has_title = sum(1 for r in self.check_results if r['has_title'])
        avg_score = sum(r['structure_score'] for r in self.check_results) / total if total > 0 else 0
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f'''---
module_id: DOCUMENT_STRUCTURE_CHECK_REPORT_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席审计官
layer: Layer 10 (治理与合规层)
standard_type: 专业量化机构级检查报告
applicable_scope: Layer 5策略执行层文档结构检查
compliance_level: 专业标准
check_date: {datetime.now().strftime('%Y-%m-%d')}
---

# 文档结构检查报告

> **检查日期**: {datetime.now().strftime('%Y-%m-%d')}
> **检查范围**: Layer 5策略执行层所有蓝图文档
> **检查标准**: 专业量化机构文档治理五大原则
> **检查类型**: 文档结构完整性检查

---

## 📊 一、检查概要

### 1.1 检查结论

本次检查对Layer 5策略执行层的所有蓝图文档进行了结构完整性检查。

**总体评估**: {'✅ 优秀' if avg_score >= 90 else '⚠️ 良好' if avg_score >= 70 else '❌ 需改进'}

### 1.2 检查范围

- **蓝图文档**: {total}个
- **平均得分**: {avg_score:.1f}分
- **YAML头部存在率**: {has_yaml / total * 100:.1f}%
- **YAML完整率**: {yaml_complete / total * 100:.1f}%
- **核心定位存在率**: {has_core / total * 100:.1f}%
- **文档标题存在率**: {has_title / total * 100:.1f}%

---

## 🔍 二、检查结果

### 2.1 得分分布

''')
            
            # 按得分分组
            excellent = [r for r in self.check_results if r['structure_score'] >= 90]
            good = [r for r in self.check_results if 70 <= r['structure_score'] < 90]
            needs_improvement = [r for r in self.check_results if r['structure_score'] < 70]
            
            f.write(f'- **优秀（≥90分）**: {len(excellent)}个\n')
            f.write(f'- **良好（70-89分）**: {len(good)}个\n')
            f.write(f'- **需改进（<70分）**: {len(needs_improvement)}个\n\n')
            
            if needs_improvement:
                f.write('### 2.2 需改进文档\n\n')
                f.write('| 文件名 | 得分 | 问题 |\n')
                f.write('|--------|------|------|\n')
                
                for result in needs_improvement:
                    issues_str = '; '.join(result['issues'][:2])  # 只显示前2个问题
                    f.write(f'| {result["filename"]} | {result["structure_score"]}分 | {issues_str} |\n')
                
                f.write('\n### 2.3 详细问题分析\n\n')
                
                for result in needs_improvement[:10]:  # 只显示前10个
                    f.write(f'''#### {result["filename"]}

- **得分**: {result["structure_score"]}分
- **YAML头部**: {'✅ 存在' if result['has_yaml'] else '❌ 缺失'}
- **YAML完整性**: {'✅ 完整' if result['yaml_complete'] else '⚠️ 不完整'}
- **核心定位**: {'✅ 存在' if result['has_core_positioning'] else '❌ 缺失'}
- **文档标题**: {'✅ 存在' if result['has_title'] else '❌ 缺失'}
- **问题列表**:
''')
                    for issue in result['issues']:
                        f.write(f'  - {issue}\n')
                    f.write('\n')
            
            f.write(f'''---

## 📋 三、改进建议

### 3.1 立即修复（P0级）

''')
            
            if needs_improvement:
                f.write(f'1. 修复{len(needs_improvement)}个结构问题文档\n')
            else:
                f.write('✅ 无需立即修复\n')
            
            f.write('''
### 3.2 近期改进（P1级）

1. 建立文档结构标准
2. 开发自动修复工具
3. 完善审查机制

---

## 🎯 四、总结

**检查状态**: ✅ **完成**
**总体评估**: ''' + ('✅ 优秀' if avg_score >= 90 else '⚠️ 良好' if avg_score >= 70 else '❌ 需改进') + f'''

本次检查对Layer 5策略执行层的所有蓝图文档进行了结构完整性检查，平均得分{avg_score:.1f}分。

---

**检查报告版本**: v1.0.0
**检查日期**: {datetime.now().strftime('%Y-%m-%d')}
**检查官**: 首席审计官
**检查状态**: ✅ 完成
''')
        
        # 同时生成JSON报告
        json_report_path = os.path.join(report_dir, f'document_structure_check_report_{timestamp}.json')
        
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_files': total,
                'statistics': {
                    'has_yaml': has_yaml,
                    'yaml_complete': yaml_complete,
                    'has_core_positioning': has_core,
                    'has_title': has_title,
                    'average_score': avg_score
                },
                'check_results': self.check_results
            }, f, ensure_ascii=False, indent=2)
    
    def print_statistics(self):
        """输出统计"""
        total = len(self.check_results)
        complete = sum(1 for r in self.check_results if r['status'] == '✅ 完整')
        has_yaml = sum(1 for r in self.check_results if r['has_yaml'])
        yaml_complete = sum(1 for r in self.check_results if r['yaml_complete'])
        has_core = sum(1 for r in self.check_results if r['has_core_positioning'])
        has_title = sum(1 for r in self.check_results if r['has_title'])
        avg_score = sum(r['structure_score'] for r in self.check_results) / total if total > 0 else 0
        
        print()
        print('统计信息:')
        print(f'  - 总文档数: {total}')
        print(f'  - 完整文档: {complete}个（{complete / total * 100:.1f}%）')
        print(f'  - YAML头部存在率: {has_yaml / total * 100:.1f}%')
        print(f'  - YAML完整率: {yaml_complete / total * 100:.1f}%')
        print(f'  - 核心定位存在率: {has_core / total * 100:.1f}%')
        print(f'  - 文档标题存在率: {has_title / total * 100:.1f}%')
        print(f'  - 平均得分: {avg_score:.1f}分')

if __name__ == '__main__':
    checker = DocumentStructureChecker()
    checker.run()
