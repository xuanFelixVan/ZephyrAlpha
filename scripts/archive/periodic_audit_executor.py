#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
定期审计执行脚本
自动化执行快速、标准、深度审计
"""

import os
import re
import json
import yaml
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

DOCS_DIR = Path("D:/ZephyrAlpha/docs")
SCRIPTS_DIR = Path("D:/ZephyrAlpha/scripts")
REPORTS_DIR = DOCS_DIR / "09_AUDIT/REPORTS"
STATE_DIR = DOCS_DIR / "09_AUDIT/STATE"
CONFIG_FILE = DOCS_DIR / "09_AUDIT/CONFIG/PERIODIC_AUDIT_CONFIG.md"

class PeriodicAuditor:
    def __init__(self, audit_type='quick'):
        self.audit_type = audit_type
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.report_file = REPORTS_DIR / f"{audit_type.upper()}_AUDIT_REPORT_{self.timestamp}.md"
        self.state_file = STATE_DIR / f"{audit_type}_audit_state.json"
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'audit_type': audit_type,
            'total_files': 0,
            'total_issues': 0,
            'compliance_rate': 0.0,
            'issues': {
                'P0': [],
                'P1': [],
                'P2': [],
                'P3': []
            }
        }
    
    def run_quick_audit(self):
        """执行快速审计"""
        print("=" * 80)
        print("快速审计 - 每日执行")
        print("=" * 80)
        
        # 1. 检查关键文档
        critical_docs = [
            "System_Manifest.md",
            "INDEX.md",
            "SITEMAP.md"
        ]
        
        print("\n[1/3] 检查关键文档...")
        for doc in critical_docs:
            doc_path = DOCS_DIR / doc
            if not doc_path.exists():
                self.results['issues']['P1'].append({
                    'type': 'missing_critical_doc',
                    'file': doc,
                    'message': f'关键文档缺失: {doc}'
                })
                print(f"  ❌ {doc} - 缺失")
            else:
                print(f"  ✅ {doc} - 存在")
        
        # 2. 验证索引完整性
        print("\n[2/3] 验证索引完整性...")
        index_files = list(DOCS_DIR.rglob("INDEX.md"))
        total_dirs = len([d for d in DOCS_DIR.rglob("*") if d.is_dir() 
                         and 'archive' not in str(d).lower() 
                         and '_archive' not in str(d).lower()])
        
        index_coverage = len(index_files) / total_dirs * 100 if total_dirs > 0 else 0
        print(f"  索引覆盖率: {index_coverage:.2f}%")
        
        if index_coverage < 95:
            self.results['issues']['P2'].append({
                'type': 'low_index_coverage',
                'coverage': index_coverage,
                'message': f'索引覆盖率过低: {index_coverage:.2f}%'
            })
        
        # 3. 检查最新修改的文档
        print("\n[3/3] 检查最新修改的文档...")
        recent_files = []
        cutoff_time = datetime.now() - timedelta(days=1)
        
        for md_file in DOCS_DIR.rglob("*.md"):
            if md_file.stat().st_mtime > cutoff_time.timestamp():
                recent_files.append(md_file)
        
        print(f"  最近24小时修改的文档: {len(recent_files)}个")
        
        # 检查最近修改的文档是否有问题
        for recent_file in recent_files[:10]:  # 只检查前10个
            try:
                with open(recent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否有module_id
                if not re.search(r'module_id:', content):
                    self.results['issues']['P2'].append({
                        'type': 'missing_module_id',
                        'file': str(recent_file.relative_to(DOCS_DIR)),
                        'message': f'缺少module_id: {recent_file.name}'
                    })
            except Exception as e:
                pass
        
        # 计算合规率
        self.results['total_files'] = len(list(DOCS_DIR.rglob("*.md")))
        self.results['total_issues'] = sum(len(v) for v in self.results['issues'].values())
        self.results['compliance_rate'] = (self.results['total_files'] - self.results['total_issues']) / self.results['total_files'] * 100
        
        print(f"\n合规率: {self.results['compliance_rate']:.2f}%")
    
    def run_standard_audit(self):
        """执行标准审计"""
        print("=" * 80)
        print("标准审计 - 每周执行")
        print("=" * 80)
        
        # 调用深度审计脚本
        audit_script = SCRIPTS_DIR / "comprehensive_deep_audit.py"
        if audit_script.exists():
            print("\n执行深度审计脚本...")
            try:
                result = subprocess.run(
                    ['python', str(audit_script)],
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30分钟超时
                )
                print(result.stdout)
                if result.returncode != 0:
                    print(f"审计脚本执行失败: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("审计脚本执行超时")
            except Exception as e:
                print(f"审计脚本执行错误: {e}")
        else:
            print(f"审计脚本不存在: {audit_script}")
        
        # 读取最新的审计结果
        latest_audit = max(STATE_DIR.glob("comprehensive_deep_audit_*.json"), 
                          key=lambda x: x.stat().st_mtime, 
                          default=None)
        
        if latest_audit:
            with open(latest_audit, 'r', encoding='utf-8') as f:
                audit_data = json.load(f)
                self.results['compliance_rate'] = audit_data.get('compliance_rate', 0)
                self.results['total_files'] = audit_data.get('total_files', 0)
                self.results['total_issues'] = audit_data.get('total_issues', 0)
        
        print(f"\n合规率: {self.results['compliance_rate']:.2f}%")
    
    def run_deep_audit(self):
        """执行深度审计"""
        print("=" * 80)
        print("深度审计 - 每月执行")
        print("=" * 80)
        
        # 1. 执行标准审计
        self.run_standard_audit()
        
        # 2. 死链接检查
        print("\n[额外检查] 死链接检查...")
        dead_link_script = SCRIPTS_DIR / "comprehensive_dead_link_fixer.py"
        if dead_link_script.exists():
            try:
                result = subprocess.run(
                    ['python', str(dead_link_script)],
                    capture_output=True,
                    text=True,
                    timeout=3600  # 60分钟超时
                )
                print(result.stdout[:1000])  # 只显示前1000个字符
            except Exception as e:
                print(f"死链接检查失败: {e}")
        
        # 3. 职责重叠检查
        print("\n[额外检查] 职责重叠检查...")
        self.check_responsibility_overlap()
        
        # 4. 版本隔离检查
        print("\n[额外检查] 版本隔离检查...")
        self.check_version_isolation()
    
    def check_responsibility_overlap(self):
        """检查职责重叠"""
        md_files = list(DOCS_DIR.rglob("*.md"))
        responsibilities = defaultdict(list)
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取职责描述
                resp_match = re.search(r'responsibility:\s*\n\s*-\s*(.+)', content)
                if resp_match:
                    responsibility = resp_match.group(1).strip()
                    responsibilities[responsibility].append(str(md_file.relative_to(DOCS_DIR)))
            except Exception as e:
                pass
        
        # 检查重复职责
        for responsibility, files in responsibilities.items():
            if len(files) > 1:
                self.results['issues']['P2'].append({
                    'type': 'responsibility_overlap',
                    'responsibility': responsibility,
                    'files': files,
                    'message': f'职责重叠: {responsibility} 在 {len(files)} 个文件中'
                })
    
    def check_version_isolation(self):
        """检查版本隔离"""
        md_files = list(DOCS_DIR.rglob("*.md"))
        versions = defaultdict(list)
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取版本号
                version_match = re.search(r'version:\s*([\d.]+)', content)
                if version_match:
                    version = version_match.group(1)
                    versions[version].append(str(md_file.relative_to(DOCS_DIR)))
            except Exception as e:
                pass
        
        # 检查版本分布
        print(f"  发现 {len(versions)} 个不同版本")
    
    def generate_report(self):
        """生成审计报告"""
        report = f"""# {self.audit_type.upper()} 审计报告

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**审计类型**: {self.audit_type.upper()}
**审计范围**: 全系统文档

---

## 📊 审计结果

| 指标 | 数值 |
|------|------|
| **总文件数** | {self.results['total_files']} |
| **总问题数** | {self.results['total_issues']} |
| **合规率** | {self.results['compliance_rate']:.2f}% |

---

## 🔍 问题分布

| 优先级 | 数量 |
|--------|------|
| **P0（严重）** | {len(self.results['issues']['P0'])} |
| **P1（重要）** | {len(self.results['issues']['P1'])} |
| **P2（次要）** | {len(self.results['issues']['P2'])} |
| **P3（建议）** | {len(self.results['issues']['P3'])} |

---

## 📝 问题详情

"""
        
        for priority in ['P0', 'P1', 'P2', 'P3']:
            if self.results['issues'][priority]:
                report += f"\n### {priority} 问题\n\n"
                for issue in self.results['issues'][priority]:
                    report += f"- **{issue['type']}**: {issue['message']}\n"
        
        report += f"""
---

## ✅ 审计结论

- **合规率**: {self.results['compliance_rate']:.2f}%
- **审计状态**: {'✅ 通过' if self.results['compliance_rate'] >= 99.5 else '⚠️ 需要改进'}
- **下次审计**: {(datetime.now() + timedelta(days=1 if self.audit_type == 'quick' else 7)).strftime('%Y-%m-%d')}

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 保存报告
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n审计报告已保存至: {self.report_file}")
    
    def save_state(self):
        """保存审计状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"审计状态已保存至: {self.state_file}")
    
    def run(self):
        """执行审计"""
        print(f"\n开始执行 {self.audit_type} 审计...")
        
        if self.audit_type == 'quick':
            self.run_quick_audit()
        elif self.audit_type == 'standard':
            self.run_standard_audit()
        elif self.audit_type == 'deep':
            self.run_deep_audit()
        else:
            print(f"未知的审计类型: {self.audit_type}")
            return
        
        self.generate_report()
        self.save_state()
        
        print(f"\n{self.audit_type.upper()} 审计完成！")

if __name__ == "__main__":
    import sys
    
    audit_type = sys.argv[1] if len(sys.argv) > 1 else 'quick'
    
    auditor = PeriodicAuditor(audit_type)
    auditor.run()
