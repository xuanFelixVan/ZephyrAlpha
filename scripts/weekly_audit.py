#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
每周文档治理审计脚本
执行时间: 每周一 09:00
审计范围: 新增文档和最近修改的文档
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class WeeklyAuditor:
    def __init__(self):
        self.project_root = Path(r"D:\ZephyrAlpha")
        self.docs_root = self.project_root / "docs"
        self.audit_time = datetime.now()
        self.audit_results = {
            "audit_time": self.audit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "audit_type": "weekly",
            "new_docs": [],
            "modified_docs": [],
            "yaml_issues": [],
            "responsibility_issues": [],
            "layer_issues": [],
            "summary": {
                "total_checked": 0,
                "total_issues": 0,
                "compliance_rate": 0.0
            }
        }
    
    def get_recently_modified_docs(self, days: int = 7) -> List[Path]:
        recently_modified = []
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name.startswith("."):
                continue
            
            try:
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                if mtime > cutoff_time:
                    recently_modified.append(md_file)
            except Exception as e:
                print(f"Error checking {md_file}: {e}")
        
        return recently_modified
    
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
        print("每周文档治理审计")
        print("=" * 80)
        print(f"审计时间: {self.audit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: 最近7天修改的文档")
        print("-" * 80)
        
        recently_modified = self.get_recently_modified_docs(days=7)
        
        print(f"\n发现 {len(recently_modified)} 个最近修改的文档")
        print("-" * 80)
        
        for i, doc_path in enumerate(recently_modified, 1):
            print(f"\n[{i}/{len(recently_modified)}] 审计: {doc_path.relative_to(self.project_root)}")
            
            result = self.audit_document(doc_path)
            
            if result['status'] == 'success':
                self.audit_results['modified_docs'].append(result)
                
                if result['yaml_issues']:
                    self.audit_results['yaml_issues'].extend(result['yaml_issues'])
                    print(f"  ✓ YAML问题: {len(result['yaml_issues'])} 个")
                
                if result['responsibility_issues']:
                    self.audit_results['responsibility_issues'].extend(result['responsibility_issues'])
                    print(f"  ✓ 职责问题: {len(result['responsibility_issues'])} 个")
                
                if result['layer_issues']:
                    self.audit_results['layer_issues'].extend(result['layer_issues'])
                    print(f"  ✓ Layer问题: {len(result['layer_issues'])} 个")
                
                if not (result['yaml_issues'] or result['responsibility_issues'] or result['layer_issues']):
                    print(f"  ✓ 无问题")
            else:
                print(f"  ✗ 错误: {result.get('message', '未知错误')}")
        
        total_issues = (
            len(self.audit_results['yaml_issues']) +
            len(self.audit_results['responsibility_issues']) +
            len(self.audit_results['layer_issues'])
        )
        
        self.audit_results['summary']['total_checked'] = len(recently_modified)
        self.audit_results['summary']['total_issues'] = total_issues
        
        if len(recently_modified) > 0:
            compliance_rate = (len(recently_modified) - total_issues) / len(recently_modified) * 100
            self.audit_results['summary']['compliance_rate'] = round(compliance_rate, 2)
        
        print("\n" + "=" * 80)
        print("审计完成统计")
        print("=" * 80)
        print(f"审计文档数: {len(recently_modified)}")
        print(f"发现问题数: {total_issues}")
        print(f"合规率: {self.audit_results['summary']['compliance_rate']}%")
        
        report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"weekly_audit_{self.audit_time.strftime('%Y%m%d')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n审计报告已保存至: {report_path}")
        print("=" * 80)

if __name__ == "__main__":
    auditor = WeeklyAuditor()
    auditor.run()
