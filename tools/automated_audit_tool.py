"""
自动化审计工具（简化版）

适用于个人开发、AI维护、个人使用场景
提供基础的自动化合规检查功能

使用方法:
    python automated_audit_tool.py --type daily
    python automated_audit_tool.py --type weekly
    python automated_audit_tool.py --type monthly
"""

import os
import json
import argparse
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd


class SimpleAuditTool:
    """简化版自动化审计工具"""
    
    def __init__(self, project_root: str = "d:\\ZephyrAlpha"):
        self.project_root = Path(project_root)
        self.audit_results = []
        self.report_dir = self.project_root / "docs" / "09_AUDIT" / "REPORTS" / "automated"
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def run_daily_audit(self) -> Dict[str, Any]:
        """执行每日审计"""
        print("🔍 开始执行每日审计...")
        
        results = {
            'audit_type': 'daily',
            'audit_date': date.today().isoformat(),
            'audit_time': datetime.now().isoformat(),
            'checks': []
        }
        
        results['checks'].append(self._check_document_completeness())
        results['checks'].append(self._check_file_naming())
        results['checks'].append(self._check_index_consistency())
        
        results['overall_status'] = self._calculate_overall_status(results['checks'])
        results['summary'] = self._generate_summary(results['checks'])
        
        self._save_report(results, 'daily')
        return results
    
    def run_weekly_audit(self) -> Dict[str, Any]:
        """执行每周审计"""
        print("🔍 开始执行每周审计...")
        
        results = {
            'audit_type': 'weekly',
            'audit_date': date.today().isoformat(),
            'audit_time': datetime.now().isoformat(),
            'checks': []
        }
        
        results['checks'].append(self._check_document_updates())
        results['checks'].append(self._check_knowledge_base())
        results['checks'].append(self._check_compliance_standards())
        
        results['overall_status'] = self._calculate_overall_status(results['checks'])
        results['summary'] = self._generate_summary(results['checks'])
        
        self._save_report(results, 'weekly')
        return results
    
    def run_monthly_audit(self) -> Dict[str, Any]:
        """执行每月审计"""
        print("🔍 开始执行每月审计...")
        
        results = {
            'audit_type': 'monthly',
            'audit_date': date.today().isoformat(),
            'audit_time': datetime.now().isoformat(),
            'checks': []
        }
        
        results['checks'].append(self._check_document_completeness())
        results['checks'].append(self._check_file_naming())
        results['checks'].append(self._check_index_consistency())
        results['checks'].append(self._check_document_updates())
        results['checks'].append(self._check_knowledge_base())
        results['checks'].append(self._check_compliance_standards())
        
        results['overall_status'] = self._calculate_overall_status(results['checks'])
        results['summary'] = self._generate_summary(results['checks'])
        
        self._save_report(results, 'monthly')
        return results
    
    def _check_document_completeness(self) -> Dict[str, Any]:
        """检查文档完整性"""
        print("  📄 检查文档完整性...")
        
        required_docs = [
            "docs/01_FRAMEWORK/INDEX.md",
            "docs/01_FRAMEWORK/SYSTEM_MANIFEST.md",
            "docs/01_FRAMEWORK/INVESTMENT_PHILOSOPHY.md",
            "docs/01_FRAMEWORK/RESEARCH_METHODOLOGY.md",
            "docs/08_KNOWLEDGE/KNOWLEDGE_TRANSFER_SYSTEM.md",
            "docs/09_AUDIT/STANDARDS/COMPLIANCE_AUDIT_SYSTEM.md"
        ]
        
        missing_docs = []
        for doc in required_docs:
            doc_path = self.project_root / doc
            if not doc_path.exists():
                missing_docs.append(doc)
        
        return {
            'check_name': 'document_completeness',
            'status': 'PASS' if not missing_docs else 'FAIL',
            'total_required': len(required_docs),
            'missing_count': len(missing_docs),
            'missing_docs': missing_docs,
            'details': f"必需文档: {len(required_docs)}, 缺失: {len(missing_docs)}"
        }
    
    def _check_file_naming(self) -> Dict[str, Any]:
        """检查文件命名规范"""
        print("  📝 检查文件命名规范...")
        
        docs_dir = self.project_root / "docs"
        non_compliant_files = []
        
        for md_file in docs_dir.rglob("*.md"):
            if md_file.name != md_file.name.upper():
                if not md_file.name.startswith("."):
                    non_compliant_files.append(str(md_file.relative_to(self.project_root)))
        
        return {
            'check_name': 'file_naming',
            'status': 'PASS' if not non_compliant_files else 'FAIL',
            'total_files': len(list(docs_dir.rglob("*.md"))),
            'non_compliant_count': len(non_compliant_files),
            'non_compliant_files': non_compliant_files[:10],
            'details': f"总文件数: {len(list(docs_dir.rglob('*.md')))}, 不合规: {len(non_compliant_files)}"
        }
    
    def _check_index_consistency(self) -> Dict[str, Any]:
        """检查索引一致性"""
        print("  🗂️ 检查索引一致性...")
        
        index_file = self.project_root / "docs" / "01_FRAMEWORK" / "INDEX.md"
        
        if not index_file.exists():
            return {
                'check_name': 'index_consistency',
                'status': 'FAIL',
                'details': '索引文件不存在'
            }
        
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        referenced_files = []
        for line in content.split('\n'):
            if '.md' in line and '[' in line:
                start = line.find('(') + 1
                end = line.find(')', start)
                if start > 0 and end > start:
                    ref = line[start:end]
                    if ref.endswith('.md'):
                        referenced_files.append(ref)
        
        missing_references = []
        for ref in referenced_files[:20]:
            ref_path = self.project_root / "docs" / ref.lstrip('./')
            if not ref_path.exists():
                missing_references.append(ref)
        
        return {
            'check_name': 'index_consistency',
            'status': 'PASS' if not missing_references else 'FAIL',
            'total_references': len(referenced_files),
            'missing_count': len(missing_references),
            'missing_references': missing_references,
            'details': f"引用文件: {len(referenced_files)}, 缺失: {len(missing_references)}"
        }
    
    def _check_document_updates(self) -> Dict[str, Any]:
        """检查文档更新及时性"""
        print("  🕒 检查文档更新及时性...")
        
        docs_dir = self.project_root / "docs"
        outdated_docs = []
        threshold_days = 90
        
        for md_file in docs_dir.rglob("*.md"):
            stat = md_file.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            days_since_update = (datetime.now() - last_modified).days
            
            if days_since_update > threshold_days:
                outdated_docs.append({
                    'file': str(md_file.relative_to(self.project_root)),
                    'days_outdated': days_since_update
                })
        
        return {
            'check_name': 'document_updates',
            'status': 'PASS' if not outdated_docs else 'FAIL',
            'threshold_days': threshold_days,
            'outdated_count': len(outdated_docs),
            'outdated_docs': outdated_docs[:10],
            'details': f"过期文档（>{threshold_days}天）: {len(outdated_docs)}"
        }
    
    def _check_knowledge_base(self) -> Dict[str, Any]:
        """检查知识库维护情况"""
        print("  📚 检查知识库维护情况...")
        
        knowledge_dir = self.project_root / "docs" / "08_KNOWLEDGE"
        
        if not knowledge_dir.exists():
            return {
                'check_name': 'knowledge_base',
                'status': 'FAIL',
                'details': '知识库目录不存在'
            }
        
        knowledge_files = list(knowledge_dir.rglob("*.md"))
        
        return {
            'check_name': 'knowledge_base',
            'status': 'PASS',
            'total_files': len(knowledge_files),
            'details': f"知识库文件数: {len(knowledge_files)}"
        }
    
    def _check_compliance_standards(self) -> Dict[str, Any]:
        """检查合规标准文档"""
        print("  ✅ 检查合规标准文档...")
        
        required_standards = [
            "docs/09_AUDIT/STANDARDS/AUDIT_STANDARDS_v5.1.md",
            "docs/09_AUDIT/STANDARDS/COMPLIANCE_AUDIT_SYSTEM.md",
            "docs/09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md"
        ]
        
        missing_standards = []
        for standard in required_standards:
            standard_path = self.project_root / standard
            if not standard_path.exists():
                missing_standards.append(standard)
        
        return {
            'check_name': 'compliance_standards',
            'status': 'PASS' if not missing_standards else 'FAIL',
            'total_required': len(required_standards),
            'missing_count': len(missing_standards),
            'missing_standards': missing_standards,
            'details': f"必需标准: {len(required_standards)}, 缺失: {len(missing_standards)}"
        }
    
    def _calculate_overall_status(self, checks: List[Dict[str, Any]]) -> str:
        """计算总体状态"""
        failed_checks = [c for c in checks if c['status'] == 'FAIL']
        
        if not failed_checks:
            return 'PASS'
        elif len(failed_checks) <= len(checks) * 0.3:
            return 'WARNING'
        else:
            return 'FAIL'
    
    def _generate_summary(self, checks: List[Dict[str, Any]]) -> str:
        """生成摘要"""
        total = len(checks)
        passed = sum(1 for c in checks if c['status'] == 'PASS')
        failed = sum(1 for c in checks if c['status'] == 'FAIL')
        
        return f"总检查项: {total}, 通过: {passed}, 失败: {failed}"
    
    def _save_report(self, results: Dict[str, Any], audit_type: str):
        """保存审计报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"{audit_type}_audit_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 审计报告已保存: {report_file}")
        
        self._print_summary(results)
    
    def _print_summary(self, results: Dict[str, Any]):
        """打印摘要"""
        print("\n" + "="*60)
        print(f"审计类型: {results['audit_type']}")
        print(f"审计日期: {results['audit_date']}")
        print(f"总体状态: {results['overall_status']}")
        print(f"摘要: {results['summary']}")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='自动化审计工具（简化版）')
    parser.add_argument('--type', choices=['daily', 'weekly', 'monthly'], 
                       required=True, help='审计类型')
    parser.add_argument('--project-root', default='d:\\ZephyrAlpha',
                       help='项目根目录')
    
    args = parser.parse_args()
    
    audit_tool = SimpleAuditTool(args.project_root)
    
    if args.type == 'daily':
        results = audit_tool.run_daily_audit()
    elif args.type == 'weekly':
        results = audit_tool.run_weekly_audit()
    elif args.type == 'monthly':
        results = audit_tool.run_monthly_audit()
    
    print("\n✅ 审计完成！")


if __name__ == '__main__':
    main()
