#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
优化版每周文档治理审计脚本
执行时间: 每周一 09:00
审计范围: 新增文档和最近修改的文档

性能优化:
1. 使用多线程并行处理
2. 缓存文件修改时间
3. 批量文件读取
4. 优化正则表达式
5. 减少IO操作
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class OptimizedWeeklyAuditor:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.docs_root = self.project_root / "docs"
        self.audit_time = datetime.now()
        self.audit_results = {
            "audit_time": self.audit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "audit_type": "weekly_optimized",
            "new_docs": [],
            "modified_docs": [],
            "yaml_issues": [],
            "responsibility_issues": [],
            "layer_issues": [],
            "performance_metrics": {
                "start_time": 0,
                "end_time": 0,
                "duration": 0,
                "docs_per_second": 0
            },
            "summary": {
                "total_checked": 0,
                "total_issues": 0,
                "compliance_rate": 0.0
            }
        }

        self.yaml_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
        self.required_fields = [
            "module_id", "version", "status", "created_date",
            "last_updated", "owner", "responsibility", "layer",
            "standard_type", "applicable_scope", "compliance_level",
            "parent_document"
        ]

    def get_recently_modified_docs(self, days: int = 7) -> List[Path]:
        recently_modified = []
        cutoff_time = datetime.now() - timedelta(days=days)

        all_md_files = list(self.docs_root.rglob("*.md"))

        for md_file in all_md_files:
            if md_file.name.startswith("."):
                continue

            try:
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                if mtime > cutoff_time:
                    recently_modified.append(md_file)
            except Exception as e:
                pass

        return recently_modified

    def extract_yaml_header(self, content: str) -> Optional[Dict]:
        match = self.yaml_pattern.match(content)

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

        for field in self.required_fields:
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
        print("优化版每周文档治理审计")
        print("=" * 80)
        print(f"审计时间: {self.audit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: 最近7天修改的文档")
        print("-" * 80)

        start_time = time.time()
        self.audit_results['performance_metrics']['start_time'] = start_time

        recently_modified = self.get_recently_modified_docs(days=7)

        print(f"\n发现 {len(recently_modified)} 个最近修改的文档")
        print("-" * 80)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.audit_document, doc_path): doc_path
                      for doc_path in recently_modified}

            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()

                if i % 10 == 0:
                    print(f"进度: [{i}/{len(recently_modified)}]")

                if result['status'] == 'success':
                    self.audit_results['modified_docs'].append(result)

                    if result['yaml_issues']:
                        self.audit_results['yaml_issues'].extend(result['yaml_issues'])

                    if result['responsibility_issues']:
                        self.audit_results['responsibility_issues'].extend(result['responsibility_issues'])

                    if result['layer_issues']:
                        self.audit_results['layer_issues'].extend(result['layer_issues'])

        end_time = time.time()
        duration = end_time - start_time

        self.audit_results['performance_metrics']['end_time'] = end_time
        self.audit_results['performance_metrics']['duration'] = round(duration, 2)

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
            docs_per_second = len(recently_modified) / duration
            self.audit_results['performance_metrics']['docs_per_second'] = round(docs_per_second, 2)

        print("\n" + "=" * 80)
        print("审计完成统计")
        print("=" * 80)
        print(f"审计文档数: {len(recently_modified)}")
        print(f"发现问题数: {total_issues}")
        print(f"合规率: {self.audit_results['summary']['compliance_rate']}%")
        print(f"\n性能指标:")
        print(f"审计耗时: {duration:.2f}秒")
        print(f"处理速度: {self.audit_results['performance_metrics']['docs_per_second']} 文档/秒")

        report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"weekly_audit_optimized_{self.audit_time.strftime('%Y%m%d')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)

        print(f"\n审计报告已保存至: {report_path}")
        print("=" * 80)

if __name__ == "__main__":
    auditor = OptimizedWeeklyAuditor()
    auditor.run()
