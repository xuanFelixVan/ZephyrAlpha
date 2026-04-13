#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 4机器学习层深度审计脚本
基于专业量化机构五大原则和三层审计标准
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class Layer4DeepAuditor:
    def __init__(self):
        self.project_root = Path(r"D:\ZephyrAlpha")
        self.docs_root = self.project_root / "docs"
        self.audit_time = datetime.now()
        
        self.audit_results = {
            "audit_time": self.audit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "audit_scope": "Layer 4机器学习层",
            "L1_file_system": {
                "directory_structure": [],
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
                "document_classification": [],
                "numbering_system": [],
                "document_quality": []
            },
            "summary": {
                "total_docs": 0,
                "total_issues": 0,
                "L1_issues": 0,
                "L2_issues": 0,
                "L3_issues": 0,
                "compliance_rate": 0.0
            }
        }
        
        self.layer4_keywords = [
            "机器学习", "ML", "MLOps", "模型", "训练", "推理",
            "特征", "Feature", "深度学习", "神经网络", "强化学习",
            "迁移学习", "联邦学习", "AutoML", "模型服务"
        ]
    
    def get_layer4_docs(self) -> List[Path]:
        layer4_docs = []
        
        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name.startswith("."):
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(2000)
                
                yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    if re.search(r'layer:\s*Layer\s*4', yaml_content, re.IGNORECASE):
                        layer4_docs.append(md_file)
                        continue
                
                for keyword in self.layer4_keywords:
                    if keyword.lower() in content.lower():
                        layer4_docs.append(md_file)
                        break
                        
            except Exception as e:
                pass
        
        return layer4_docs
    
    def extract_yaml_header(self, content: str) -> Dict:
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
        
        return {}
    
    def audit_L1_file_system(self, docs: List[Path]):
        print("\n" + "=" * 80)
        print("L1 文件系统层审计")
        print("=" * 80)
        
        for doc_path in docs:
            relative_path = doc_path.relative_to(self.project_root)
            path_str = str(relative_path)
            
            if doc_path.parent != self.docs_root / "01_FRAMEWORK":
                if "01_FRAMEWORK" not in path_str:
                    self.audit_results['L1_file_system']['directory_structure'].append({
                        "doc": path_str,
                        "issue": "目录漂移",
                        "description": "Layer 4文档不在01_FRAMEWORK目录中",
                        "severity": "中"
                    })
            
            if not re.match(r'^[A-Z0-9_]+\.md$', doc_path.name):
                if doc_path.name not in ['INDEX.md', 'README.md']:
                    self.audit_results['L1_file_system']['file_naming'].append({
                        "doc": path_str,
                        "issue": "文件命名不规范",
                        "description": f"文件名不符合专业命名标准: {doc_path.name}",
                        "severity": "低"
                    })
            
            if re.search(r'Layer\s*[0-9]', doc_path.name):
                self.audit_results['L1_file_system']['file_naming'].append({
                    "doc": path_str,
                    "issue": "旧架构命名残留",
                    "description": f"文件名包含旧架构关键词: {doc_path.name}",
                    "severity": "中"
                })
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
                for link_text, link_path in links:
                    if link_path.startswith('http'):
                        continue
                    
                    if link_path.count('../') > 3:
                        self.audit_results['L1_file_system']['path_references'].append({
                            "doc": path_str,
                            "issue": "路径冗余",
                            "description": f"链接路径包含过多../: {link_path}",
                            "severity": "低"
                        })
                    
                    if not link_path.startswith('#'):
                        full_path = (doc_path.parent / link_path).resolve()
                        if not full_path.exists():
                            self.audit_results['L1_file_system']['path_references'].append({
                                "doc": path_str,
                                "issue": "死链接",
                                "description": f"链接指向不存在的文件: {link_path}",
                                "severity": "高"
                            })
                            
            except Exception as e:
                pass
    
    def audit_L2_document_content(self, docs: List[Path]):
        print("\n" + "=" * 80)
        print("L2 文档内容层审计")
        print("=" * 80)
        
        responsibilities = defaultdict(list)
        
        for doc_path in docs:
            relative_path = doc_path.relative_to(self.project_root)
            path_str = str(relative_path)
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                continue
            
            yaml_dict = self.extract_yaml_header(content)
            
            if "responsibility" not in yaml_dict or not yaml_dict["responsibility"]:
                self.audit_results['L2_document_content']['responsibility_driven'].append({
                    "doc": path_str,
                    "issue": "职责缺失",
                    "description": "文档缺少responsibility字段",
                    "severity": "高"
                })
            else:
                responsibility = yaml_dict["responsibility"]
                if len(responsibility) < 20:
                    self.audit_results['L2_document_content']['responsibility_driven'].append({
                        "doc": path_str,
                        "issue": "职责不清",
                        "description": f"职责描述过短: {responsibility}",
                        "severity": "中"
                    })
                
                responsibilities[responsibility].append(path_str)
            
            if "layer" not in yaml_dict:
                self.audit_results['L2_document_content']['responsibility_driven'].append({
                    "doc": path_str,
                    "issue": "Layer归属缺失",
                    "description": "文档缺少layer字段",
                    "severity": "高"
                })
            
            if "module_id" not in yaml_dict:
                self.audit_results['L2_document_content']['version_isolation'].append({
                    "doc": path_str,
                    "issue": "编号缺失",
                    "description": "文档缺少module_id字段",
                    "severity": "高"
                })
            
            if "version" not in yaml_dict:
                self.audit_results['L2_document_content']['version_isolation'].append({
                    "doc": path_str,
                    "issue": "版本号缺失",
                    "description": "文档缺少version字段",
                    "severity": "中"
                })
        
        for responsibility, doc_list in responsibilities.items():
            if len(doc_list) > 1:
                self.audit_results['L2_document_content']['responsibility_driven'].append({
                    "docs": doc_list,
                    "issue": "职责重叠",
                    "description": f"多个文档具有相同职责: {responsibility}",
                    "severity": "高"
                })
    
    def audit_L3_professional_standards(self, docs: List[Path]):
        print("\n" + "=" * 80)
        print("L3 专业标准层审计")
        print("=" * 80)
        
        module_ids = defaultdict(list)
        
        for doc_path in docs:
            relative_path = doc_path.relative_to(self.project_root)
            path_str = str(relative_path)
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                continue
            
            yaml_dict = self.extract_yaml_header(content)
            
            if "module_id" in yaml_dict:
                module_id = yaml_dict["module_id"]
                module_ids[module_id].append(path_str)
                
                if len(module_id) < 10:
                    self.audit_results['L3_professional_standards']['numbering_system'].append({
                        "doc": path_str,
                        "issue": "编号不规范",
                        "description": f"module_id过短: {module_id}",
                        "severity": "中"
                    })
            
            required_fields = [
                "module_id", "version", "status", "created_date",
                "last_updated", "owner", "responsibility", "layer",
                "standard_type", "applicable_scope", "compliance_level",
                "parent_document"
            ]
            
            missing_fields = [field for field in required_fields if field not in yaml_dict]
            if missing_fields:
                self.audit_results['L3_professional_standards']['document_quality'].append({
                    "doc": path_str,
                    "issue": "YAML字段不完整",
                    "description": f"缺少字段: {', '.join(missing_fields)}",
                    "severity": "高"
                })
            
            if "standard_type" not in yaml_dict:
                self.audit_results['L3_professional_standards']['document_classification'].append({
                    "doc": path_str,
                    "issue": "文档类型缺失",
                    "description": "缺少standard_type字段",
                    "severity": "中"
                })
        
        for module_id, doc_list in module_ids.items():
            if len(doc_list) > 1:
                self.audit_results['L3_professional_standards']['numbering_system'].append({
                    "docs": doc_list,
                    "issue": "编号重复",
                    "description": f"多个文档使用相同module_id: {module_id}",
                    "severity": "高"
                })
    
    def run(self):
        print("=" * 80)
        print("Layer 4机器学习层深度审计")
        print("=" * 80)
        print(f"审计时间: {self.audit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计标准: 专业量化机构五大原则 + 三层审计标准")
        print("-" * 80)
        
        layer4_docs = self.get_layer4_docs()
        
        print(f"\n发现 {len(layer4_docs)} 个Layer 4文档")
        print("-" * 80)
        
        self.audit_L1_file_system(layer4_docs)
        self.audit_L2_document_content(layer4_docs)
        self.audit_L3_professional_standards(layer4_docs)
        
        L1_issues = (
            len(self.audit_results['L1_file_system']['directory_structure']) +
            len(self.audit_results['L1_file_system']['file_naming']) +
            len(self.audit_results['L1_file_system']['path_references'])
        )
        
        L2_issues = (
            len(self.audit_results['L2_document_content']['responsibility_driven']) +
            len(self.audit_results['L2_document_content']['index_completeness']) +
            len(self.audit_results['L2_document_content']['version_isolation']) +
            len(self.audit_results['L2_document_content']['doc_code_correspondence'])
        )
        
        L3_issues = (
            len(self.audit_results['L3_professional_standards']['five_principles']) +
            len(self.audit_results['L3_professional_standards']['document_classification']) +
            len(self.audit_results['L3_professional_standards']['numbering_system']) +
            len(self.audit_results['L3_professional_standards']['document_quality'])
        )
        
        total_issues = L1_issues + L2_issues + L3_issues
        
        self.audit_results['summary']['total_docs'] = len(layer4_docs)
        self.audit_results['summary']['total_issues'] = total_issues
        self.audit_results['summary']['L1_issues'] = L1_issues
        self.audit_results['summary']['L2_issues'] = L2_issues
        self.audit_results['summary']['L3_issues'] = L3_issues
        
        if len(layer4_docs) > 0:
            compliance_rate = (len(layer4_docs) - total_issues) / len(layer4_docs) * 100
            self.audit_results['summary']['compliance_rate'] = round(compliance_rate, 2)
        
        print("\n" + "=" * 80)
        print("审计完成统计")
        print("=" * 80)
        print(f"审计文档数: {len(layer4_docs)}")
        print(f"\nL1文件系统层问题: {L1_issues}")
        print(f"  - 目录结构问题: {len(self.audit_results['L1_file_system']['directory_structure'])}")
        print(f"  - 文件命名问题: {len(self.audit_results['L1_file_system']['file_naming'])}")
        print(f"  - 路径引用问题: {len(self.audit_results['L1_file_system']['path_references'])}")
        print(f"\nL2文档内容层问题: {L2_issues}")
        print(f"  - 职责驱动问题: {len(self.audit_results['L2_document_content']['responsibility_driven'])}")
        print(f"  - 索引完备问题: {len(self.audit_results['L2_document_content']['index_completeness'])}")
        print(f"  - 版本隔离问题: {len(self.audit_results['L2_document_content']['version_isolation'])}")
        print(f"  - 文档代码对应问题: {len(self.audit_results['L2_document_content']['doc_code_correspondence'])}")
        print(f"\nL3专业标准层问题: {L3_issues}")
        print(f"  - 五大原则问题: {len(self.audit_results['L3_professional_standards']['five_principles'])}")
        print(f"  - 文档分类问题: {len(self.audit_results['L3_professional_standards']['document_classification'])}")
        print(f"  - 编号体系问题: {len(self.audit_results['L3_professional_standards']['numbering_system'])}")
        print(f"  - 文档质量问题: {len(self.audit_results['L3_professional_standards']['document_quality'])}")
        print(f"\n总问题数: {total_issues}")
        print(f"合规率: {self.audit_results['summary']['compliance_rate']}%")
        
        report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"layer4_deep_audit_{self.audit_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n审计报告已保存至: {report_path}")
        print("=" * 80)

if __name__ == "__main__":
    auditor = Layer4DeepAuditor()
    auditor.run()
