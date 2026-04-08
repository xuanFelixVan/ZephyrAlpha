#!/usr/bin/env python3
"""
职责完整性检查器

功能:
1. 检查职责描述是否存在
2. 检查职责描述是否为空
3. 检查职责描述是否为通用模板
4. 生成完整性检查报告
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

class ResponsibilityCompletenessChecker:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.blueprint_files = []
        self.check_results = []
        
        # 通用模板模式
        self.generic_patterns = [
            r'^[A-Z_]+模块，负责[a-z_]+相关功能$',
            r'^.*Blueprint模块，负责.*相关功能$',
            r'^.*模块，负责.*相关功能$'
        ]
    
    def run(self):
        """执行检查"""
        print('=' * 80)
        print('职责完整性检查器')
        print('=' * 80)
        print()
        
        # 1. 扫描蓝图文件
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
        print()
        
        # 2. 检查完整性
        print('2. 检查职责完整性...')
        self.check_completeness()
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
    
    def check_completeness(self):
        """检查完整性"""
        for filepath in self.blueprint_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                result = {
                    'filepath': filepath,
                    'filename': os.path.basename(filepath),
                    'has_responsibility_section': False,
                    'responsibility': '',
                    'is_empty': False,
                    'is_generic': False,
                    'issues': [],
                    'status': '✅ 完整'
                }
                
                # 检查是否有"核心定位"章节
                pattern = r'##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    result['has_responsibility_section'] = True
                    responsibility = match.group(1).strip()
                    result['responsibility'] = responsibility
                    
                    # 检查是否为空
                    if not responsibility or responsibility.isspace():
                        result['is_empty'] = True
                        result['issues'].append('职责描述为空')
                        result['status'] = '❌ 空描述'
                    
                    # 检查是否为通用模板
                    for pattern in self.generic_patterns:
                        if re.match(pattern, responsibility):
                            result['is_generic'] = True
                            result['issues'].append('使用了通用模板')
                            result['status'] = '⚠️ 通用模板'
                            break
                    
                    # 检查长度
                    if len(responsibility) < 20:
                        result['issues'].append('职责描述过短')
                        if result['status'] == '✅ 完整':
                            result['status'] = '⚠️ 过短'
                else:
                    result['issues'].append('缺少"核心定位"章节')
                    result['status'] = '❌ 缺失章节'
                
                self.check_results.append(result)
            
            except Exception as e:
                print(f'  ⚠️ 无法检查文件: {filepath} - {e}')
    
    def generate_report(self):
        """生成报告"""
        report_dir = 'docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state'
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        report_path = os.path.join(report_dir, f'RESPONSIBILITY_COMPLETENESS_REPORT_{timestamp}.md')
        
        # 统计数据
        total = len(self.check_results)
        complete = sum(1 for r in self.check_results if r['status'] == '✅ 完整')
        missing = sum(1 for r in self.check_results if '❌ 缺失章节' in r['status'])
        empty = sum(1 for r in self.check_results if r['is_empty'])
        generic = sum(1 for r in self.check_results if r['is_generic'])
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f'''---
module_id: RESPONSIBILITY_COMPLETENESS_REPORT_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席审计官
layer: Layer 10 (治理与合规层)
standard_type: 专业量化机构级检查报告
applicable_scope: Layer 5策略执行层职责完整性检查
compliance_level: 专业标准
check_date: {datetime.now().strftime('%Y-%m-%d')}
---

# 职责完整性检查报告

> **检查日期**: {datetime.now().strftime('%Y-%m-%d')}
> **检查范围**: Layer 5策略执行层所有蓝图文档
> **检查标准**: 专业量化机构文档治理五大原则
> **检查类型**: 职责描述完整性检查

---

## 📊 一、检查概要

### 1.1 检查结论

本次检查对Layer 5策略执行层的所有蓝图文档进行了职责完整性检查。

**总体评估**: {'✅ 优秀' if complete / total >= 0.95 else '⚠️ 良好' if complete / total >= 0.80 else '❌ 需改进'}

### 1.2 检查范围

- **蓝图文档**: {total}个
- **完整文档**: {complete}个（{complete / total * 100:.1f}%）
- **缺失章节**: {missing}个
- **空描述**: {empty}个
- **通用模板**: {generic}个

---

## 🔍 二、检查结果

### 2.1 状态分布

| 状态 | 数量 | 百分比 |
|------|------|--------|
| ✅ 完整 | {complete} | {complete / total * 100:.1f}% |
| ⚠️ 通用模板 | {generic} | {generic / total * 100:.1f}% |
| ⚠️ 过短 | {sum(1 for r in self.check_results if '⚠️ 过短' in r['status'])} | {sum(1 for r in self.check_results if '⚠️ 过短' in r['status']) / total * 100:.1f}% |
| ❌ 空描述 | {empty} | {empty / total * 100:.1f}% |
| ❌ 缺失章节 | {missing} | {missing / total * 100:.1f}% |

''')
            
            # 列出问题文档
            problem_docs = [r for r in self.check_results if r['status'] != '✅ 完整']
            
            if problem_docs:
                f.write('### 2.2 问题文档列表\n\n')
                f.write('| 文件名 | 状态 | 问题 |\n')
                f.write('|--------|------|------|\n')
                
                for result in problem_docs:
                    issues_str = '; '.join(result['issues'])
                    f.write(f'| {result["filename"]} | {result["status"]} | {issues_str} |\n')
                
                f.write('\n### 2.3 详细问题分析\n\n')
                
                for result in problem_docs[:10]:  # 只显示前10个
                    f.write(f'''#### {result["filename"]}

- **状态**: {result["status"]}
- **职责描述**: {result["responsibility"][:100] if result["responsibility"] else "无"}...
- **问题列表**:
''')
                    for issue in result['issues']:
                        f.write(f'  - {issue}\n')
                    f.write('\n')
            else:
                f.write('✅ 所有文档职责描述完整\n\n')
            
            f.write(f'''---

## 📋 三、改进建议

### 3.1 立即修复（P0级）

''')
            
            if missing > 0:
                f.write(f'1. 为{missing}个缺失章节的文档添加职责描述\n')
            if empty > 0:
                f.write(f'2. 为{empty}个空描述的文档补充内容\n')
            if missing == 0 and empty == 0:
                f.write('✅ 无需立即修复\n')
            
            f.write('''
### 3.2 近期改进（P1级）

''')
            
            if generic > 0:
                f.write(f'1. 优化{generic}个使用通用模板的文档\n')
            else:
                f.write('1. 建立职责审查机制\n')
            
            f.write('''2. 完善文档结构
3. 建立知识库

---

## 🎯 四、总结

**检查状态**: ✅ **完成**
**总体评估**: ''' + ('✅ 优秀' if complete / total >= 0.95 else '⚠️ 良好' if complete / total >= 0.80 else '❌ 需改进') + f'''

本次检查对Layer 5策略执行层的所有蓝图文档进行了职责完整性检查，{complete}个文档职责描述完整。

---

**检查报告版本**: v1.0.0
**检查日期**: {datetime.now().strftime('%Y-%m-%d')}
**检查官**: 首席审计官
**检查状态**: ✅ 完成
''')
        
        # 同时生成JSON报告
        json_report_path = os.path.join(report_dir, f'responsibility_completeness_report_{timestamp}.json')
        
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_files': total,
                'statistics': {
                    'complete': complete,
                    'missing': missing,
                    'empty': empty,
                    'generic': generic
                },
                'check_results': self.check_results
            }, f, ensure_ascii=False, indent=2)
    
    def print_statistics(self):
        """输出统计"""
        total = len(self.check_results)
        complete = sum(1 for r in self.check_results if r['status'] == '✅ 完整')
        missing = sum(1 for r in self.check_results if '❌ 缺失章节' in r['status'])
        empty = sum(1 for r in self.check_results if r['is_empty'])
        generic = sum(1 for r in self.check_results if r['is_generic'])
        
        print()
        print('统计信息:')
        print(f'  - 总文档数: {total}')
        print(f'  - 完整文档: {complete}个（{complete / total * 100:.1f}%）')
        print(f'  - 缺失章节: {missing}个')
        print(f'  - 空描述: {empty}个')
        print(f'  - 通用模板: {generic}个')

if __name__ == '__main__':
    checker = ResponsibilityCompletenessChecker()
    checker.run()
