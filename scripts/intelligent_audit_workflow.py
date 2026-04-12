#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
智能审计流程脚本
功能：自动化审计流程，减少人工干预环节
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

# 问题分类规则库
PROBLEM_CLASSIFICATION_RULES = {
    'P0_高风险': {
        'module_id_duplicate': {
            'pattern': r'module_id.*duplicate',
            'description': 'Module ID重复',
            'auto_fix': False,
            'priority': 1
        },
        'yaml_missing': {
            'pattern': r'yaml.*missing',
            'description': 'YAML头部缺失',
            'auto_fix': True,
            'priority': 2
        }
    },
    'P1_中风险': {
        'responsibility_missing': {
            'pattern': r'responsibility.*missing',
            'description': '职责描述缺失',
            'auto_fix': True,
            'priority': 3
        },
        'naming_non_standard': {
            'pattern': r'naming.*non.*standard',
            'description': '命名不规范',
            'auto_fix': True,
            'priority': 4
        }
    },
    'P2_低风险': {
        'sparse_directory': {
            'pattern': r'sparse.*directory',
            'description': '稀疏目录',
            'auto_fix': False,
            'priority': 5
        },
        'format_issue': {
            'pattern': r'format.*issue',
            'description': '格式问题',
            'auto_fix': True,
            'priority': 6
        }
    }
}

class IntelligentAuditor:
    """智能审计器"""
    
    def __init__(self):
        self.issues = []
        self.auto_fixed = []
        self.need_manual = []
        
    def classify_issue(self, issue):
        """智能分类问题"""
        for risk_level, problems in PROBLEM_CLASSIFICATION_RULES.items():
            for problem_type, problem_info in problems.items():
                if re.search(problem_info['pattern'], issue.get('description', ''), re.IGNORECASE):
                    return {
                        'risk_level': risk_level,
                        'problem_type': problem_type,
                        'description': problem_info['description'],
                        'auto_fix': problem_info['auto_fix'],
                        'priority': problem_info['priority']
                    }
        
        # 默认分类
        return {
            'risk_level': 'P2_低风险',
            'problem_type': 'unknown',
            'description': '未知问题',
            'auto_fix': False,
            'priority': 99
        }
    
    def auto_fix_issue(self, issue, classification):
        """自动修复问题"""
        if not classification['auto_fix']:
            return False, "需要人工处理"
        
        problem_type = classification['problem_type']
        
        try:
            if problem_type == 'responsibility_missing':
                # 自动添加职责描述
                return self._fix_responsibility(issue)
            elif problem_type == 'naming_non_standard':
                # 自动修复命名
                return self._fix_naming(issue)
            elif problem_type == 'yaml_missing':
                # 自动添加YAML头部
                return self._fix_yaml(issue)
            elif problem_type == 'format_issue':
                # 自动修复格式
                return self._fix_format(issue)
            else:
                return False, "无法自动修复"
        except Exception as e:
            return False, f"自动修复失败: {str(e)}"
    
    def _fix_responsibility(self, issue):
        """修复职责描述缺失"""
        file_path = DOCS_DIR / issue['path']
        
        if not file_path.exists():
            return False, "文件不存在"
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        if '**核心职责**' in content:
            return False, "已有职责描述"
        
        # 推断职责
        responsibility = self._infer_responsibility(issue['path'])
        
        # 添加职责描述
        responsibility_block = f"""

> **核心职责**: {responsibility}
> **职责边界**: 
> - ✅ 本文档负责：{responsibility}相关内容
> - ❌ 本文档不负责：其他模块内容
"""
        
        # 查找插入位置
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            insert_pos = title_match.end()
            new_content = content[:insert_pos] + responsibility_block + content[insert_pos:]
        else:
            new_content = content + responsibility_block
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"已添加职责: {responsibility}"
    
    def _fix_naming(self, issue):
        """修复命名问题"""
        file_path = DOCS_DIR / issue['path']
        
        if not file_path.exists():
            return False, "文件不存在"
        
        file_name = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path)
        
        # 转换为标准名称
        new_name = file_name.replace(' ', '_').upper()
        
        if new_name == file_name:
            return False, "文件名已符合规范"
        
        new_path = os.path.join(dir_path, new_name)
        
        if os.path.exists(new_path):
            return False, f"目标文件已存在: {new_name}"
        
        os.rename(file_path, new_path)
        return True, f"重命名成功: {file_name} -> {new_name}"
    
    def _fix_yaml(self, issue):
        """修复YAML头部缺失"""
        file_path = DOCS_DIR / issue['path']
        
        if not file_path.exists():
            return False, "文件不存在"
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        if content.startswith('---'):
            return False, "已有YAML头部"
        
        # 添加YAML头部
        yaml_header = f"""---
module_id: {os.path.basename(issue['path']).replace('.md', '').upper()}_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
---

"""
        
        new_content = yaml_header + content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "已添加YAML头部"
    
    def _fix_format(self, issue):
        """修复格式问题"""
        # 简单的格式修复
        file_path = DOCS_DIR / issue['path']
        
        if not file_path.exists():
            return False, "文件不存在"
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 移除BOM
        content = content.replace('\ufeff', '')
        
        # 统一换行符
        content = content.replace('\r\n', '\n')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, "已修复格式问题"
    
    def _infer_responsibility(self, file_path):
        """推断职责"""
        file_name = os.path.basename(file_path)
        
        if 'INDEX' in file_name:
            return '目录导航和文档索引'
        elif 'README' in file_name:
            return '模块说明和快速入门指南'
        elif 'BLUEPRINT' in file_name:
            return '蓝图设计和架构规划'
        elif 'STANDARD' in file_name:
            return '标准规范制定'
        elif 'GUIDE' in file_name:
            return '使用指南和教程'
        elif 'REPORT' in file_name:
            return '分析报告和评估结果'
        else:
            return '文档内容说明'
    
    def run_intelligent_audit(self):
        """执行智能审计"""
        print("=" * 80)
        print("智能审计流程")
        print("=" * 80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 模拟扫描问题（实际应用中应该调用真实的扫描函数）
        print("扫描问题...")
        self.issues = self._scan_issues()
        print(f"发现 {len(self.issues)} 个问题")
        print()
        
        # 智能分类
        print("智能分类问题...")
        classified_issues = []
        for issue in self.issues:
            classification = self.classify_issue(issue)
            classified_issues.append({
                **issue,
                **classification
            })
        
        # 按优先级排序
        classified_issues.sort(key=lambda x: x['priority'])
        
        # 统计分类结果
        risk_stats = {}
        for issue in classified_issues:
            risk_level = issue['risk_level']
            risk_stats[risk_level] = risk_stats.get(risk_level, 0) + 1
        
        print("问题分类统计:")
        for risk_level, count in risk_stats.items():
            print(f"  - {risk_level}: {count}个")
        print()
        
        # 自动修复
        print("自动修复问题...")
        for issue in classified_issues:
            if issue['auto_fix']:
                success, message = self.auto_fix_issue(issue, issue)
                if success:
                    self.auto_fixed.append({
                        'path': issue['path'],
                        'problem_type': issue['problem_type'],
                        'message': message
                    })
                    print(f"✅ {issue['path']}: {message}")
                else:
                    self.need_manual.append({
                        'path': issue['path'],
                        'problem_type': issue['problem_type'],
                        'reason': message
                    })
                    print(f"❌ {issue['path']}: {message}")
            else:
                self.need_manual.append({
                    'path': issue['path'],
                    'problem_type': issue['problem_type'],
                    'reason': '需要人工处理'
                })
        
        print()
        print(f"处理完成: 自动修复 {len(self.auto_fixed)} 个, 需人工处理 {len(self.need_manual)} 个")
        
        # 生成报告
        self._generate_report(classified_issues)
        
        print()
        print("=" * 80)
        print("智能审计完成")
        print("=" * 80)
    
    def _scan_issues(self):
        """扫描问题（简化版）"""
        issues = []
        
        # 扫描职责描述缺失
        for root, dirs, files in os.walk(DOCS_DIR):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, DOCS_DIR)
                
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    
                    if '**核心职责**' not in content:
                        issues.append({
                            'path': rel_path,
                            'description': 'responsibility missing',
                            'type': 'responsibility'
                        })
                except:
                    pass
        
        return issues
    
    def _generate_report(self, classified_issues):
        """生成审计报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = OUTPUT_DIR / f'intelligent_audit_report_{timestamp}.md'
        
        report_content = f"""---
module_id: INTELLIGENT_AUDIT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 智能审计报告
applicable_scope: 全系统文档治理
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 智能审计报告

## 📊 审计概要

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: 全系统文档  
**审计方法**: 智能分类+自动修复  
**审计结论**: 自动修复 {len(self.auto_fixed)} 个问题，需人工处理 {len(self.need_manual)} 个问题

---

## 📈 问题分类统计

| 风险级别 | 问题数量 | 自动修复 | 需人工处理 |
|---------|---------|---------|-----------|
"""
        
        # 统计各风险级别
        risk_stats = {}
        for issue in classified_issues:
            risk_level = issue['risk_level']
            if risk_level not in risk_stats:
                risk_stats[risk_level] = {'total': 0, 'auto': 0, 'manual': 0}
            risk_stats[risk_level]['total'] += 1
        
        for issue in self.auto_fixed:
            for classified_issue in classified_issues:
                if classified_issue['path'] == issue['path']:
                    risk_level = classified_issue['risk_level']
                    risk_stats[risk_level]['auto'] += 1
                    break
        
        for issue in self.need_manual:
            for classified_issue in classified_issues:
                if classified_issue['path'] == issue['path']:
                    risk_level = classified_issue['risk_level']
                    risk_stats[risk_level]['manual'] += 1
                    break
        
        for risk_level, stats in sorted(risk_stats.items()):
            report_content += f"| **{risk_level}** | {stats['total']} | {stats['auto']} | {stats['manual']} |\n"
        
        report_content += f"""
---

## 🔍 自动修复结果

**自动修复数量**: {len(self.auto_fixed)} 个

"""
        
        if self.auto_fixed:
            for i, issue in enumerate(self.auto_fixed[:20], 1):
                report_content += f"{i}. {issue['path']}\n   - 问题: {issue['problem_type']}\n   - 结果: {issue['message']}\n"
            
            if len(self.auto_fixed) > 20:
                report_content += f"... 还有 {len(self.auto_fixed) - 20} 个问题\n"
        else:
            report_content += "✅ 无自动修复问题\n"
        
        report_content += f"""
---

## ⚠️ 需人工处理问题

**需人工处理数量**: {len(self.need_manual)} 个

"""
        
        if self.need_manual:
            for i, issue in enumerate(self.need_manual[:20], 1):
                report_content += f"{i}. {issue['path']}\n   - 问题: {issue['problem_type']}\n   - 原因: {issue['reason']}\n"
            
            if len(self.need_manual) > 20:
                report_content += f"... 还有 {len(self.need_manual) - 20} 个问题\n"
        else:
            report_content += "✅ 无需人工处理问题\n"
        
        report_content += f"""
---

## 💡 改进建议

"""
        
        if len(self.auto_fixed) > 0:
            report_content += "✅ 自动修复效果良好，建议继续优化自动修复规则\n"
        
        if len(self.need_manual) > 10:
            report_content += "⚠️ 需人工处理问题较多，建议优化自动修复规则\n"
        elif len(self.need_manual) > 0:
            report_content += "✅ 需人工处理问题较少，建议及时处理\n"
        else:
            report_content += "✅ 所有问题已自动修复，审计流程优化效果显著\n"
        
        report_content += f"""
---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，智能审计报告 | 首席文档架构师 |
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"报告已保存至: {report_path}")
        
        # 保存JSON结果
        json_path = OUTPUT_DIR / f'intelligent_audit_result_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_issues': len(classified_issues),
                'auto_fixed': len(self.auto_fixed),
                'need_manual': len(self.need_manual),
                'risk_stats': risk_stats,
                'auto_fixed_details': self.auto_fixed,
                'need_manual_details': self.need_manual
            }, f, ensure_ascii=False, indent=2)
        
        print(f"JSON结果已保存至: {json_path}")

def main():
    """主函数"""
    auditor = IntelligentAuditor()
    auditor.run_intelligent_audit()

if __name__ == '__main__':
    main()
