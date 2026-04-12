#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
每季度文档治理审计脚本
执行时间: 每季度首月1日 14:00
审计范围: 全系统深度审计（三层审计）
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class QuarterlyAuditor:
    def __init__(self):
        self.project_root = Path(r"D:\ZephyrAlpha")
        self.docs_root = self.project_root / "docs"
        self.audit_time = datetime.now()
        self.audit_results = {
            "audit_time": self.audit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "audit_type": "quarterly",
            "L1_file_system": {
                "directory_separation": [],
                "file_naming": [],
                "path_references": []
            },
            "L2_document_content": {
                "responsibility_driven": [],
                "index_completeness": [],
                "version_isolation": [],
                "doc_code_correspondence": []
            },
            "L3_professional_standards": {
                "five_principles": [],
                "classification_system": [],
                "numbering_system": [],
                "content_quality": []
            },
            "total_docs": 0,
            "summary": {
                "total_checked": 0,
                "total_issues": 0,
                "compliance_rate": 0.0,
                "L1_compliance": 0.0,
                "L2_compliance": 0.0,
                "L3_compliance": 0.0
            }
        }
    
    def get_all_docs(self) -> List[Path]:
        all_docs = []
        
        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name.startswith("."):
                continue
            all_docs.append(md_file)
        
        return all_docs
    
    def extract_yaml_header(self, content: str) -> Optional[Dict]:
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            yaml_content = match.group(1)
            yaml_dict = {}
            
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    yaml_dict[key.strip()] = value.strip()
            
            return yaml_dict
        
        return None
    
    def audit_L1_file_system(self, doc_path: Path) -> Dict:
        issues = []
        
        relative_path = doc_path.relative_to(self.project_root)
        path_str = str(relative_path)
        
        if "src/" in path_str and path_str.endswith(".md"):
            issues.append({
                "doc": path_str,
                "issue": "文档文件不应在src/目录中"
            })
        
        if "tests/" in path_str and path_str.endswith(".md"):
            issues.append({
                "doc": path_str,
                "issue": "文档文件不应在tests/目录中"
            })
        
        if not re.match(r'^[A-Z0-9_]+\.md$', doc_path.name):
            if doc_path.name not in ['INDEX.md', 'README.md', 'SITEMAP.md']:
                issues.append({
                    "doc": path_str,
                    "issue": "文件命名不符合规范（应使用大写字母、数字和下划线）"
                })
        
        return {
            "doc": path_str,
            "issues": issues
        }
    
    def audit_L2_document_content(self, doc_path: Path, content: str) -> Dict:
        issues = []
        
        yaml_dict = self.extract_yaml_header(content)
        
        if not yaml_dict:
            issues.append({
                "doc": str(doc_path.relative_to(self.project_root)),
                "issue": "缺少YAML头部"
            })
            return {
                "doc": str(doc_path.relative_to(self.project_root)),
                "issues": issues
            }
        
        if "responsibility" not in yaml_dict or len(yaml_dict.get("responsibility", "")) < 20:
            issues.append({
                "doc": str(doc_path.relative_to(self.project_root)),
                "issue": "职责描述不清晰或缺失"
            })
        
        if "layer" not in yaml_dict:
            issues.append({
                "doc": str(doc_path.relative_to(self.project_root)),
                "issue": "缺少Layer归属"
            })
        
        return {
            "doc": str(doc_path.relative_to(self.project_root)),
            "issues": issues
        }
    
    def audit_L3_professional_standards(self, doc_path: Path, content: str) -> Dict:
        issues = []
        
        yaml_dict = self.extract_yaml_header(content)
        
        if not yaml_dict:
            return {
                "doc": str(doc_path.relative_to(self.project_root)),
                "issues": issues
            }
        
        if "module_id" not in yaml_dict:
            issues.append({
                "doc": str(doc_path.relative_to(self.project_root)),
                "issue": "缺少module_id"
            })
        
        if "standard_type" not in yaml_dict:
            issues.append({
                "doc": str(doc_path.relative_to(self.project_root)),
                "issue": "缺少standard_type"
            })
        
        if "compliance_level" not in yaml_dict:
            issues.append({
                "doc": str(doc_path.relative_to(self.project_root)),
                "issue": "缺少compliance_level"
            })
        
        return {
            "doc": str(doc_path.relative_to(self.project_root)),
            "issues": issues
        }
    
    def audit_document(self, doc_path: Path) -> Dict:
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(doc_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except Exception as e:
                return {
                    "doc": str(doc_path.relative_to(self.project_root)),
                    "status": "error",
                    "message": f"编码错误: {str(e)}"
                }
        
        L1_result = self.audit_L1_file_system(doc_path)
        L2_result = self.audit_L2_document_content(doc_path, content)
        L3_result = self.audit_L3_professional_standards(doc_path, content)
        
        return {
            "doc": str(doc_path.relative_to(self.project_root)),
            "status": "success",
            "L1_issues": L1_result['issues'],
            "L2_issues": L2_result['issues'],
            "L3_issues": L3_result['issues']
        }
    
    def run(self):
        print("=" * 80)
        print("每季度文档治理审计（三层审计）")
        print("=" * 80)
        print(f"审计时间: {self.audit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: 全系统深度审计")
        print("-" * 80)
        
        all_docs = self.get_all_docs()
        
        print(f"\n发现 {len(all_docs)} 个文档")
        print("-" * 80)
        
        L1_total_issues = 0
        L2_total_issues = 0
        L3_total_issues = 0
        
        for i, doc_path in enumerate(all_docs, 1):
            if i % 50 == 0:
                print(f"\n进度: [{i}/{len(all_docs)}]")
            
            result = self.audit_document(doc_path)
            
            if result['status'] == 'success':
                if result['L1_issues']:
                    self.audit_results['L1_file_system']['directory_separation'].extend(result['L1_issues'])
                    L1_total_issues += len(result['L1_issues'])
                
                if result['L2_issues']:
                    self.audit_results['L2_document_content']['responsibility_driven'].extend(result['L2_issues'])
                    L2_total_issues += len(result['L2_issues'])
                
                if result['L3_issues']:
                    self.audit_results['L3_professional_standards']['five_principles'].extend(result['L3_issues'])
                    L3_total_issues += len(result['L3_issues'])
        
        total_issues = L1_total_issues + L2_total_issues + L3_total_issues
        
        self.audit_results['total_docs'] = len(all_docs)
        self.audit_results['summary']['total_checked'] = len(all_docs)
        self.audit_results['summary']['total_issues'] = total_issues
        
        if len(all_docs) > 0:
            compliance_rate = (len(all_docs) - total_issues) / len(all_docs) * 100
            self.audit_results['summary']['compliance_rate'] = round(compliance_rate, 2)
            
            L1_compliance = (len(all_docs) - L1_total_issues) / len(all_docs) * 100
            L2_compliance = (len(all_docs) - L2_total_issues) / len(all_docs) * 100
            L3_compliance = (len(all_docs) - L3_total_issues) / len(all_docs) * 100
            
            self.audit_results['summary']['L1_compliance'] = round(L1_compliance, 2)
            self.audit_results['summary']['L2_compliance'] = round(L2_compliance, 2)
            self.audit_results['summary']['L3_compliance'] = round(L3_compliance, 2)
        
        print("\n" + "=" * 80)
        print("审计完成统计")
        print("=" * 80)
        print(f"审计文档数: {len(all_docs)}")
        print(f"\nL1文件系统层:")
        print(f"  问题数: {L1_total_issues}")
        print(f"  合规率: {self.audit_results['summary']['L1_compliance']}%")
        print(f"\nL2文档内容层:")
        print(f"  问题数: {L2_total_issues}")
        print(f"  合规率: {self.audit_results['summary']['L2_compliance']}%")
        print(f"\nL3专业标准层:")
        print(f"  问题数: {L3_total_issues}")
        print(f"  合规率: {self.audit_results['summary']['L3_compliance']}%")
        print(f"\n总体:")
        print(f"  总问题数: {total_issues}")
        print(f"  总合规率: {self.audit_results['summary']['compliance_rate']}%")
        
        quarter = (self.audit_time.month - 1) // 3 + 1
        report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"quarterly_audit_{self.audit_time.year}Q{quarter}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n审计报告已保存至: {report_path}")
        print("=" * 80)

if __name__ == "__main__":
    auditor = QuarterlyAuditor()
    auditor.run()
