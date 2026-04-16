#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
每月文档治理审计脚本
执行时间: 每月1日 10:00
审计范围: 全系统所有文档
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class MonthlyAuditor:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.docs_root = self.project_root / "docs"
        self.audit_time = datetime.now()
        self.audit_results = {
            "audit_time": self.audit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "audit_type": "monthly",
            "total_docs": 0,
            "yaml_completeness": {
                "total": 0,
                "complete": 0,
                "incomplete": 0,
                "issues": []
            },
            "responsibility_clarity": {
                "total": 0,
                "clear": 0,
                "unclear": 0,
                "issues": []
            },
            "layer_attribution": {
                "total": 0,
                "correct": 0,
                "incorrect": 0,
                "issues": []
            },
            "index_coverage": {
                "system_manifest": 0,
                "layer_index": 0,
                "issues": []
            },
            "link_validity": {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "issues": []
            },
            "summary": {
                "total_checked": 0,
                "total_issues": 0,
                "compliance_rate": 0.0
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
    
    def check_yaml_completeness(self, yaml_dict: Dict, doc_path: Path) -> List[Dict]:
        issues = []
        required_fields = [
            "module_id", "version", "status", "created_date",
            "last_updated", "owner", "responsibility", "layer",
            "standard_type", "applicable_scope", "compliance_level",
            "parent_document"
        ]
        
        for field in required_fields:
            if field not in yaml_dict or not yaml_dict[field]:
                issues.append({
                    "doc": str(doc_path.relative_to(self.project_root)),
                    "field": field,
                    "issue": "缺失或为空"
                })
        
        return issues
    
    def check_responsibility_clarity(self, yaml_dict: Dict, doc_path: Path) -> List[Dict]:
        issues = []
        
        if "responsibility" not in yaml_dict:
            issues.append({
                "doc": str(doc_path.relative_to(self.project_root)),
                "issue": "缺少responsibility字段"
            })
        else:
            responsibility = yaml_dict["responsibility"]
            if len(responsibility) < 20:
                issues.append({
                    "doc": str(doc_path.relative_to(self.project_root)),
                    "issue": "职责描述过短",
                    "responsibility": responsibility
                })
        
        return issues
    
    def check_layer_attribution(self, yaml_dict: Dict, doc_path: Path) -> List[Dict]:
        issues = []
        
        if "layer" not in yaml_dict:
            issues.append({
                "doc": str(doc_path.relative_to(self.project_root)),
                "issue": "缺少layer字段"
            })
        else:
            layer = yaml_dict["layer"]
            if not re.search(r'Layer \d+', layer):
                issues.append({
                    "doc": str(doc_path.relative_to(self.project_root)),
                    "issue": "layer字段格式不正确",
                    "layer": layer
                })
        
        return issues
    
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
        
        yaml_dict = self.extract_yaml_header(content)
        
        if not yaml_dict:
            return {
                "doc": str(doc_path.relative_to(self.project_root)),
                "status": "error",
                "message": "未找到YAML头部"
            }
        
        yaml_issues = self.check_yaml_completeness(yaml_dict, doc_path)
        responsibility_issues = self.check_responsibility_clarity(yaml_dict, doc_path)
        layer_issues = self.check_layer_attribution(yaml_dict, doc_path)
        
        return {
            "doc": str(doc_path.relative_to(self.project_root)),
            "status": "success",
            "yaml_issues": yaml_issues,
            "responsibility_issues": responsibility_issues,
            "layer_issues": layer_issues
        }
    
    def run(self):
        print("=" * 80)
        print("每月文档治理审计")
        print("=" * 80)
        print(f"审计时间: {self.audit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: 全系统所有文档")
        print("-" * 80)
        
        all_docs = self.get_all_docs()
        
        print(f"\n发现 {len(all_docs)} 个文档")
        print("-" * 80)
        
        for i, doc_path in enumerate(all_docs, 1):
            if i % 50 == 0:
                print(f"\n进度: [{i}/{len(all_docs)}]")
            
            result = self.audit_document(doc_path)
            
            if result['status'] == 'success':
                self.audit_results['yaml_completeness']['total'] += 1
                self.audit_results['responsibility_clarity']['total'] += 1
                self.audit_results['layer_attribution']['total'] += 1
                
                if not result['yaml_issues']:
                    self.audit_results['yaml_completeness']['complete'] += 1
                else:
                    self.audit_results['yaml_completeness']['incomplete'] += 1
                    self.audit_results['yaml_completeness']['issues'].extend(result['yaml_issues'])
                
                if not result['responsibility_issues']:
                    self.audit_results['responsibility_clarity']['clear'] += 1
                else:
                    self.audit_results['responsibility_clarity']['unclear'] += 1
                    self.audit_results['responsibility_clarity']['issues'].extend(result['responsibility_issues'])
                
                if not result['layer_issues']:
                    self.audit_results['layer_attribution']['correct'] += 1
                else:
                    self.audit_results['layer_attribution']['incorrect'] += 1
                    self.audit_results['layer_attribution']['issues'].extend(result['layer_issues'])
        
        total_issues = (
            len(self.audit_results['yaml_completeness']['issues']) +
            len(self.audit_results['responsibility_clarity']['issues']) +
            len(self.audit_results['layer_attribution']['issues'])
        )
        
        self.audit_results['total_docs'] = len(all_docs)
        self.audit_results['summary']['total_checked'] = len(all_docs)
        self.audit_results['summary']['total_issues'] = total_issues
        
        if len(all_docs) > 0:
            compliance_rate = (len(all_docs) - total_issues) / len(all_docs) * 100
            self.audit_results['summary']['compliance_rate'] = round(compliance_rate, 2)
        
        print("\n" + "=" * 80)
        print("审计完成统计")
        print("=" * 80)
        print(f"审计文档数: {len(all_docs)}")
        print(f"YAML完整性: {self.audit_results['yaml_completeness']['complete']}/{self.audit_results['yaml_completeness']['total']}")
        print(f"职责清晰度: {self.audit_results['responsibility_clarity']['clear']}/{self.audit_results['responsibility_clarity']['total']}")
        print(f"Layer归属正确: {self.audit_results['layer_attribution']['correct']}/{self.audit_results['layer_attribution']['total']}")
        print(f"发现问题数: {total_issues}")
        print(f"合规率: {self.audit_results['summary']['compliance_rate']}%")
        
        report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"monthly_audit_{self.audit_time.strftime('%Y%m')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n审计报告已保存至: {report_path}")
        print("=" * 80)

if __name__ == "__main__":
    auditor = MonthlyAuditor()
    auditor.run()
