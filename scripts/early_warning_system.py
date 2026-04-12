#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
预警机制脚本
功能：建立问题预警机制，在问题发生前预警
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

class EarlyWarningSystem:
    """预警系统"""
    
    def __init__(self):
        self.warnings = []
        self.alerts = []
        
    def check_and_warn(self):
        """检查并预警"""
        print("=" * 80)
        print("预警系统运行")
        print("=" * 80)
        print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 检查各项指标
        self._check_compliance_rate()
        self._check_responsibility_coverage()
        self._check_naming_compliance()
        self._check_yaml_integrity()
        self._check_module_id_uniqueness()
        self._check_document_freshness()
        
        # 生成预警报告
        self._generate_warning_report()
        
        print()
        print("=" * 80)
        print("预警系统运行完成")
        print("=" * 80)
        print(f"发现预警: {len(self.warnings)} 个")
        print(f"发现警报: {len(self.alerts)} 个")
    
    def _check_compliance_rate(self):
        """检查合规率"""
        print("检查合规率...")
        
        # 计算各项合规率
        total_files = 0
        compliant_files = 0
        
        for root, dirs, files in os.walk(DOCS_DIR):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                total_files += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    
                    # 检查基本合规项
                    has_yaml = content.startswith('---')
                    has_responsibility = '**核心职责**' in content
                    
                    if has_yaml and has_responsibility:
                        compliant_files += 1
                except:
                    pass
        
        compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
        
        if compliance_rate < 95:
            self.alerts.append({
                'type': '合规率警报',
                'level': '🔴 高风险',
                'message': f'合规率低于95%: {compliance_rate:.1f}%',
                'action': '立即执行全面审计'
            })
        elif compliance_rate < 99:
            self.warnings.append({
                'type': '合规率预警',
                'level': '🟡 中风险',
                'message': f'合规率接近临界值: {compliance_rate:.1f}%',
                'action': '建议执行优化修复'
            })
        else:
            print(f"  ✅ 合规率正常: {compliance_rate:.1f}%")
    
    def _check_responsibility_coverage(self):
        """检查职责描述覆盖率"""
        print("检查职责描述覆盖率...")
        
        total_files = 0
        files_with_responsibility = 0
        
        for root, dirs, files in os.walk(DOCS_DIR):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                total_files += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    
                    if '**核心职责**' in content:
                        files_with_responsibility += 1
                except:
                    pass
        
        coverage_rate = (files_with_responsibility / total_files * 100) if total_files > 0 else 0
        
        if coverage_rate < 95:
            self.alerts.append({
                'type': '职责描述覆盖率警报',
                'level': '🔴 高风险',
                'message': f'职责描述覆盖率低于95%: {coverage_rate:.1f}%',
                'action': '立即批量添加职责描述'
            })
        elif coverage_rate < 99:
            self.warnings.append({
                'type': '职责描述覆盖率预警',
                'level': '🟡 中风险',
                'message': f'职责描述覆盖率接近临界值: {coverage_rate:.1f}%',
                'action': '建议补充缺失的职责描述'
            })
        else:
            print(f"  ✅ 职责描述覆盖率正常: {coverage_rate:.1f}%")
    
    def _check_naming_compliance(self):
        """检查命名规范符合率"""
        print("检查命名规范符合率...")
        
        total_files = 0
        compliant_files = 0
        
        for root, dirs, files in os.walk(DOCS_DIR):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                total_files += 1
                
                # 检查命名规范
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in file)
                has_space = ' ' in file
                
                if not has_chinese and not has_space:
                    compliant_files += 1
        
        compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
        
        if compliance_rate < 90:
            self.alerts.append({
                'type': '命名规范符合率警报',
                'level': '🔴 高风险',
                'message': f'命名规范符合率低于90%: {compliance_rate:.1f}%',
                'action': '立即批量重命名文件'
            })
        elif compliance_rate < 95:
            self.warnings.append({
                'type': '命名规范符合率预警',
                'level': '🟡 中风险',
                'message': f'命名规范符合率接近临界值: {compliance_rate:.1f}%',
                'action': '建议优化文件命名'
            })
        else:
            print(f"  ✅ 命名规范符合率正常: {compliance_rate:.1f}%")
    
    def _check_yaml_integrity(self):
        """检查YAML完整性"""
        print("检查YAML完整性...")
        
        total_files = 0
        files_with_yaml = 0
        
        for root, dirs, files in os.walk(DOCS_DIR):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                total_files += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    
                    if content.startswith('---'):
                        files_with_yaml += 1
                except:
                    pass
        
        integrity_rate = (files_with_yaml / total_files * 100) if total_files > 0 else 0
        
        if integrity_rate < 95:
            self.alerts.append({
                'type': 'YAML完整性警报',
                'level': '🔴 高风险',
                'message': f'YAML完整性低于95%: {integrity_rate:.1f}%',
                'action': '立即批量添加YAML头部'
            })
        elif integrity_rate < 99:
            self.warnings.append({
                'type': 'YAML完整性预警',
                'level': '🟡 中风险',
                'message': f'YAML完整性接近临界值: {integrity_rate:.1f}%',
                'action': '建议补充缺失的YAML头部'
            })
        else:
            print(f"  ✅ YAML完整性正常: {integrity_rate:.1f}%")
    
    def _check_module_id_uniqueness(self):
        """检查Module ID唯一性"""
        print("检查Module ID唯一性...")
        
        module_ids = {}
        duplicate_count = 0
        
        for root, dirs, files in os.walk(DOCS_DIR):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    
                    match = re.search(r'module_id:\s*(.+)', content)
                    if match:
                        module_id = match.group(1).strip()
                        if module_id in module_ids:
                            duplicate_count += 1
                        else:
                            module_ids[module_id] = file_path
                except:
                    pass
        
        if duplicate_count > 10:
            self.alerts.append({
                'type': 'Module ID唯一性警报',
                'level': '🔴 高风险',
                'message': f'发现 {duplicate_count} 个Module ID重复',
                'action': '立即修复重复的Module ID'
            })
        elif duplicate_count > 0:
            self.warnings.append({
                'type': 'Module ID唯一性预警',
                'level': '🟡 中风险',
                'message': f'发现 {duplicate_count} 个Module ID重复',
                'action': '建议修复重复的Module ID'
            })
        else:
            print(f"  ✅ Module ID唯一性正常: 无重复")
    
    def _check_document_freshness(self):
        """检查文档新鲜度"""
        print("检查文档新鲜度...")
        
        stale_files = 0
        threshold_days = 90  # 90天未更新视为陈旧
        
        for root, dirs, files in os.walk(DOCS_DIR):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                file_path = os.path.join(root, file)
                
                try:
                    # 获取文件修改时间
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    days_since_update = (datetime.now() - mod_time).days
                    
                    if days_since_update > threshold_days:
                        stale_files += 1
                except:
                    pass
        
        if stale_files > 50:
            self.warnings.append({
                'type': '文档新鲜度预警',
                'level': '🟡 中风险',
                'message': f'发现 {stale_files} 个文档超过 {threshold_days} 天未更新',
                'action': '建议审查陈旧文档'
            })
        elif stale_files > 0:
            print(f"  ⚠️ 发现 {stale_files} 个文档超过 {threshold_days} 天未更新")
    
    def _generate_warning_report(self):
        """生成预警报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = OUTPUT_DIR / f'early_warning_report_{timestamp}.md'
        
        report_content = f"""---
module_id: EARLY_WARNING_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 预警报告
applicable_scope: 全系统文档治理预警
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 预警系统报告

## 📊 预警概要

**运行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**预警范围**: 全系统文档治理  
**预警结论**: 发现 {len(self.warnings)} 个预警，{len(self.alerts)} 个警报

---

## 🔴 警报列表（高风险）

"""
        
        if self.alerts:
            for i, alert in enumerate(self.alerts, 1):
                report_content += f"### {i}. {alert['type']}\n\n"
                report_content += f"**级别**: {alert['level']}\n\n"
                report_content += f"**消息**: {alert['message']}\n\n"
                report_content += f"**行动**: {alert['action']}\n\n"
                report_content += "---\n\n"
        else:
            report_content += "✅ 无高风险警报\n\n"
        
        report_content += f"""
---

## 🟡 预警列表（中风险）

"""
        
        if self.warnings:
            for i, warning in enumerate(self.warnings, 1):
                report_content += f"### {i}. {warning['type']}\n\n"
                report_content += f"**级别**: {warning['level']}\n\n"
                report_content += f"**消息**: {warning['message']}\n\n"
                report_content += f"**行动**: {warning['action']}\n\n"
                report_content += "---\n\n"
        else:
            report_content += "✅ 无中风险预警\n\n"
        
        report_content += f"""
---

## 💡 改进建议

"""
        
        if self.alerts:
            report_content += "### 立即行动\n\n"
            for alert in self.alerts:
                report_content += f"- **{alert['type']}**: {alert['action']}\n"
            report_content += "\n"
        
        if self.warnings:
            report_content += "### 短期改进\n\n"
            for warning in self.warnings:
                report_content += f"- **{warning['type']}**: {warning['action']}\n"
            report_content += "\n"
        
        if not self.alerts and not self.warnings:
            report_content += "✅ 文档治理状态良好，建议继续保持。\n\n"
        
        report_content += f"""
---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，预警系统报告 | 首席文档架构师 |
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"报告已保存至: {report_path}")
        
        # 保存JSON结果
        json_path = OUTPUT_DIR / f'early_warning_result_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'warnings_count': len(self.warnings),
                'alerts_count': len(self.alerts),
                'warnings': self.warnings,
                'alerts': self.alerts
            }, f, ensure_ascii=False, indent=2)
        
        print(f"JSON结果已保存至: {json_path}")

def main():
    """主函数"""
    warning_system = EarlyWarningSystem()
    warning_system.check_and_warn()

if __name__ == '__main__':
    main()
