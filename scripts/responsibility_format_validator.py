#!/usr/bin/env python3
"""
职责格式验证器

功能:
1. 验证职责描述格式
2. 检查长度、结构、关键词
3. 生成格式验证报告
4. 提供优化建议
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

class ResponsibilityFormatValidator:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.blueprint_files = []
        self.validation_results = []
        
        # 格式标准
        self.min_length = 50
        self.max_length = 200
        self.required_keywords = ['负责', '包括', '功能']
        self.forbidden_patterns = [
            r'XX模块',
            r'相关功能$',
            r'Blueprint模块',
            r'模块，负责.*相关功能'
        ]
    
    def run(self):
        """执行验证"""
        print('=' * 80)
        print('职责格式验证器')
        print('=' * 80)
        print()
        
        # 1. 扫描蓝图文件
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
        print()
        
        # 2. 验证职责格式
        print('2. 验证职责格式...')
        self.validate_format()
        print(f'  ✅ 已验证{len(self.validation_results)}个文档')
        print()
        
        # 3. 生成报告
        print('3. 生成报告...')
        self.generate_report()
        print(f'  ✅ 报告已生成')
        print()
        
        # 4. 输出统计
        self.print_statistics()
        
        print('=' * 80)
        print('验证完成')
        print('=' * 80)
    
    def scan_blueprint_files(self):
        """扫描蓝图文件"""
        if os.path.exists(self.blueprints_dir):
            for root, dirs, files in os.walk(self.blueprints_dir):
                for file in files:
                    if file.endswith('.md') and file != 'INDEX.md':
                        filepath = os.path.join(root, file)
                        self.blueprint_files.append(filepath)
    
    def validate_format(self):
        """验证格式"""
        for filepath in self.blueprint_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 提取职责描述
                pattern = r'##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
                match = re.search(pattern, content, re.DOTALL)
                
                result = {
                    'filepath': filepath,
                    'filename': os.path.basename(filepath),
                    'has_responsibility': False,
                    'responsibility': '',
                    'length': 0,
                    'length_valid': False,
                    'has_keywords': False,
                    'missing_keywords': [],
                    'has_forbidden_patterns': False,
                    'forbidden_matches': [],
                    'is_specific': False,
                    'issues': [],
                    'score': 0
                }
                
                if match:
                    responsibility = match.group(1).strip()
                    result['has_responsibility'] = True
                    result['responsibility'] = responsibility
                    result['length'] = len(responsibility)
                    
                    # 检查长度
                    if self.min_length <= len(responsibility) <= self.max_length:
                        result['length_valid'] = True
                    else:
                        result['issues'].append(f'长度不符合标准（{len(responsibility)}字，应在{self.min_length}-{self.max_length}字之间）')
                    
                    # 检查关键词
                    missing_keywords = []
                    for keyword in self.required_keywords:
                        if keyword not in responsibility:
                            missing_keywords.append(keyword)
                    
                    if not missing_keywords:
                        result['has_keywords'] = True
                    else:
                        result['missing_keywords'] = missing_keywords
                        result['issues'].append(f'缺少关键词: {", ".join(missing_keywords)}')
                    
                    # 检查禁止模式
                    forbidden_matches = []
                    for pattern in self.forbidden_patterns:
                        if re.search(pattern, responsibility):
                            forbidden_matches.append(pattern)
                    
                    if not forbidden_matches:
                        result['is_specific'] = True
                    else:
                        result['has_forbidden_patterns'] = True
                        result['forbidden_matches'] = forbidden_matches
                        result['issues'].append('使用了通用模板或禁止模式')
                    
                    # 计算得分
                    score = 0
                    if result['has_responsibility']:
                        score += 25
                    if result['length_valid']:
                        score += 25
                    if result['has_keywords']:
                        score += 25
                    if result['is_specific']:
                        score += 25
                    
                    result['score'] = score
                else:
                    result['issues'].append('未找到职责描述')
                
                self.validation_results.append(result)
            
            except Exception as e:
                print(f'  ⚠️ 无法验证文件: {filepath} - {e}')
    
    def generate_report(self):
        """生成报告"""
        report_dir = 'docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state'
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        report_path = os.path.join(report_dir, f'RESPONSIBILITY_FORMAT_VALIDATION_REPORT_{timestamp}.md')
        
        # 统计数据
        total = len(self.validation_results)
        has_resp = sum(1 for r in self.validation_results if r['has_responsibility'])
        length_valid = sum(1 for r in self.validation_results if r['length_valid'])
        has_keywords = sum(1 for r in self.validation_results if r['has_keywords'])
        is_specific = sum(1 for r in self.validation_results if r['is_specific'])
        avg_score = sum(r['score'] for r in self.validation_results) / total if total > 0 else 0
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f'''---
module_id: RESPONSIBILITY_FORMAT_VALIDATION_REPORT_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席审计官
layer: Layer 10 (治理与合规层)
standard_type: 专业量化机构级验证报告
applicable_scope: Layer 5策略执行层职责格式验证
compliance_level: 专业标准
validation_date: {datetime.now().strftime('%Y-%m-%d')}
---

# 职责格式验证报告

> **验证日期**: {datetime.now().strftime('%Y-%m-%d')}
> **验证范围**: Layer 5策略执行层所有蓝图文档
> **验证标准**: 专业量化机构文档治理五大原则
> **验证类型**: 职责描述格式验证

---

## 📊 一、验证概要

### 1.1 验证结论

本次验证对Layer 5策略执行层的所有蓝图文档进行了职责格式验证。

**总体评估**: {'✅ 优秀' if avg_score >= 90 else '⚠️ 良好' if avg_score >= 70 else '❌ 需改进'}

### 1.2 验证范围

- **蓝图文档**: {total}个
- **平均得分**: {avg_score:.1f}分
- **职责描述存在率**: {has_resp / total * 100:.1f}%
- **长度符合率**: {length_valid / total * 100:.1f}%
- **关键词符合率**: {has_keywords / total * 100:.1f}%
- **具体性符合率**: {is_specific / total * 100:.1f}%

---

## 🔍 二、验证标准

### 2.1 格式标准

| 标准 | 要求 | 说明 |
|------|------|------|
| **存在性** | 必须存在 | 每个文档必须有职责描述 |
| **长度** | {self.min_length}-{self.max_length}字 | 职责描述长度应在合理范围 |
| **关键词** | 必须包含 | 必须包含"负责"、"包括"、"功能"等关键词 |
| **具体性** | 禁止通用模板 | 不能使用"XX模块，负责XX相关功能"等通用模板 |

---

## 📋 三、验证结果

### 3.1 得分分布

''')
            
            # 按得分分组
            excellent = [r for r in self.validation_results if r['score'] >= 90]
            good = [r for r in self.validation_results if 70 <= r['score'] < 90]
            needs_improvement = [r for r in self.validation_results if r['score'] < 70]
            
            f.write(f'- **优秀（≥90分）**: {len(excellent)}个\n')
            f.write(f'- **良好（70-89分）**: {len(good)}个\n')
            f.write(f'- **需改进（<70分）**: {len(needs_improvement)}个\n\n')
            
            if needs_improvement:
                f.write('### 3.2 需改进文档\n\n')
                f.write('| 文件名 | 得分 | 问题 |\n')
                f.write('|--------|------|------|\n')
                
                for result in needs_improvement:
                    issues_str = '; '.join(result['issues'][:2])  # 只显示前2个问题
                    f.write(f'| {result["filename"]} | {result["score"]}分 | {issues_str} |\n')
                
                f.write('\n### 3.3 详细问题分析\n\n')
                
                for result in needs_improvement[:10]:  # 只显示前10个
                    f.write(f'''#### {result["filename"]}

- **得分**: {result["score"]}分
- **职责描述**: {result["responsibility"][:100] if result["responsibility"] else "无"}...
- **问题列表**:
''')
                    for issue in result['issues']:
                        f.write(f'  - {issue}\n')
                    f.write('\n')
            
            f.write(f'''---

## 📈 四、改进建议

### 4.1 立即修复（P0级）

''')
            
            if needs_improvement:
                f.write(f'1. 修复{len(needs_improvement)}个格式问题文档\n')
            else:
                f.write('✅ 无需立即修复\n')
            
            f.write('''
### 4.2 近期改进（P1级）

1. 建立职责格式标准
2. 开发自动修复工具
3. 完善审查机制

---

## 🎯 五、总结

**验证状态**: ✅ **完成**
**总体评估**: ''' + ('✅ 优秀' if avg_score >= 90 else '⚠️ 良好' if avg_score >= 70 else '❌ 需改进') + f'''

本次验证对Layer 5策略执行层的所有蓝图文档进行了职责格式验证，平均得分{avg_score:.1f}分。

---

**验证报告版本**: v1.0.0
**验证日期**: {datetime.now().strftime('%Y-%m-%d')}
**验证官**: 首席审计官
**验证状态**: ✅ 完成
''')
        
        # 同时生成JSON报告
        json_report_path = os.path.join(report_dir, f'responsibility_format_validation_report_{timestamp}.json')
        
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_files': total,
                'statistics': {
                    'has_responsibility': has_resp,
                    'length_valid': length_valid,
                    'has_keywords': has_keywords,
                    'is_specific': is_specific,
                    'average_score': avg_score
                },
                'validation_results': self.validation_results
            }, f, ensure_ascii=False, indent=2)
    
    def print_statistics(self):
        """输出统计"""
        total = len(self.validation_results)
        has_resp = sum(1 for r in self.validation_results if r['has_responsibility'])
        length_valid = sum(1 for r in self.validation_results if r['length_valid'])
        has_keywords = sum(1 for r in self.validation_results if r['has_keywords'])
        is_specific = sum(1 for r in self.validation_results if r['is_specific'])
        avg_score = sum(r['score'] for r in self.validation_results) / total if total > 0 else 0
        
        print()
        print('统计信息:')
        print(f'  - 总文档数: {total}')
        print(f'  - 职责描述存在率: {has_resp / total * 100:.1f}%')
        print(f'  - 长度符合率: {length_valid / total * 100:.1f}%')
        print(f'  - 关键词符合率: {has_keywords / total * 100:.1f}%')
        print(f'  - 具体性符合率: {is_specific / total * 100:.1f}%')
        print(f'  - 平均得分: {avg_score:.1f}分')

if __name__ == '__main__':
    validator = ResponsibilityFormatValidator()
    validator.run()
