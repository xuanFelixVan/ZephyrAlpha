#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 4机器学习层深度审计脚本 v2
重点检查:
1. 重复文档检测
2. 职责不清检测
3. 职责重叠检测
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import hashlib

class Layer4DeepAuditorV2:
    def __init__(self):
        self.project_root = Path("D:/ZephyrAlpha")
        self.audit_time = datetime.now()
        self.audit_results = {
            "audit_time": self.audit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "audit_scope": "Layer 4机器学习层",
            "audit_type": "深度审计v2 - 重复与职责检查",
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
            "deep_check": {
                "duplicate_documents": [],
                "unclear_responsibility": [],
                "responsibility_overlap": []
            },
            "summary": {
                "total_docs": 0,
                "total_issues": 0,
                "L1_issues": 0,
                "L2_issues": 0,
                "L3_issues": 0,
                "deep_issues": 0,
                "compliance_rate": 0.0
            }
        }
        
        self.all_docs = []
        self.doc_contents = {}
        self.doc_hashes = {}
        self.responsibility_map = defaultdict(list)
        
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """读取文件内容"""
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except:
                continue
        return None
    
    def extract_yaml_header(self, content: str) -> Tuple[Optional[Dict], str]:
        """提取YAML头部"""
        if not content.startswith('---'):
            return None, content
        
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_text = parts[1].strip()
            body = '---' + '---'.join(parts[2:])
            
            yaml_dict = {}
            for line in yaml_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    yaml_dict[key.strip()] = value.strip()
            
            return yaml_dict, body
        return None, content
    
    def calculate_content_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_layer4_docs(self) -> List[Path]:
        """获取Layer 4文档列表"""
        layer4_keywords = [
            'layer4', 'layer_4', 'ml', 'machine_learning', 
            'model', 'feature', 'train', 'predict', 'experiment',
            '机器学习', '特征工程', '模型训练'
        ]
        
        all_md_files = list(self.project_root.rglob("*.md"))
        layer4_docs = []
        
        for md_file in all_md_files:
            if 'node_modules' in str(md_file) or '.git' in str(md_file):
                continue
            
            content = self.read_file_content(md_file)
            if not content:
                continue
            
            yaml_header, body = self.extract_yaml_header(content)
            
            is_layer4 = False
            
            if yaml_header and 'layer' in yaml_header:
                layer_value = yaml_header['layer'].lower()
                if 'layer 4' in layer_value or 'layer4' in layer_value:
                    is_layer4 = True
            
            if not is_layer4:
                path_str = str(md_file).lower()
                for keyword in layer4_keywords:
                    if keyword in path_str:
                        is_layer4 = True
                        break
            
            if not is_layer4:
                body_lower = body.lower()
                for keyword in layer4_keywords:
                    if keyword in body_lower:
                        is_layer4 = True
                        break
            
            if is_layer4:
                layer4_docs.append(md_file)
                self.all_docs.append(md_file)
                self.doc_contents[md_file] = content
                self.doc_hashes[md_file] = self.calculate_content_hash(body)
        
        return layer4_docs
    
    def check_duplicate_documents(self):
        """检查重复文档"""
        print("\n" + "=" * 80)
        print("深度检查: 重复文档检测")
        print("=" * 80)
        
        hash_groups = defaultdict(list)
        for doc_path, doc_hash in self.doc_hashes.items():
            hash_groups[doc_hash].append(doc_path)
        
        duplicates = []
        for doc_hash, docs in hash_groups.items():
            if len(docs) > 1:
                duplicates.append({
                    "hash": doc_hash,
                    "docs": [str(d.relative_to(self.project_root)) for d in docs],
                    "count": len(docs),
                    "severity": "高"
                })
        
        self.audit_results['deep_check']['duplicate_documents'] = duplicates
        print(f"发现 {len(duplicates)} 组重复文档")
        
        if duplicates:
            print("\n重复文档详情:")
            for i, dup in enumerate(duplicates[:10], 1):
                print(f"\n{i}. 重复组 (共{dup['count']}个文档):")
                for doc in dup['docs']:
                    print(f"   - {doc}")
    
    def check_unclear_responsibility(self):
        """检查职责不清的文档"""
        print("\n" + "=" * 80)
        print("深度检查: 职责不清检测")
        print("=" * 80)
        
        unclear_docs = []
        
        for doc_path in self.all_docs:
            content = self.doc_contents[doc_path]
            yaml_header, body = self.extract_yaml_header(content)
            
            issues = []
            
            if not yaml_header:
                issues.append("缺少YAML头部")
            elif 'responsibility' not in yaml_header:
                issues.append("缺少responsibility字段")
            else:
                resp = yaml_header['responsibility']
                if len(resp) < 20:
                    issues.append(f"职责描述过短: {resp}")
                elif '系统功能模块' in resp or '待定义' in resp or 'TODO' in resp:
                    issues.append(f"职责描述不明确: {resp}")
            
            body_lower = body.lower()
            vague_keywords = ['待定', 'todo', '待补充', '待完善', '待定义', 'tbd']
            for keyword in vague_keywords:
                if keyword in body_lower:
                    issues.append(f"包含模糊关键词: {keyword}")
            
            if issues:
                unclear_docs.append({
                    "doc": str(doc_path.relative_to(self.project_root)),
                    "issues": issues,
                    "severity": "高" if "缺少YAML头部" in issues or "缺少responsibility字段" in issues else "中"
                })
        
        self.audit_results['deep_check']['unclear_responsibility'] = unclear_docs
        print(f"发现 {len(unclear_docs)} 个职责不清的文档")
        
        if unclear_docs:
            print("\n职责不清文档详情 (前10个):")
            for i, doc in enumerate(unclear_docs[:10], 1):
                print(f"\n{i}. {doc['doc']}")
                for issue in doc['issues']:
                    print(f"   - {issue}")
    
    def check_responsibility_overlap(self):
        """检查职责重叠"""
        print("\n" + "=" * 80)
        print("深度检查: 职责重叠检测")
        print("=" * 80)
        
        overlap_docs = []
        
        for doc_path in self.all_docs:
            content = self.doc_contents[doc_path]
            yaml_header, body = self.extract_yaml_header(content)
            
            if not yaml_header or 'responsibility' not in yaml_header:
                continue
            
            resp = yaml_header['responsibility'].lower()
            
            self.responsibility_map[resp].append(doc_path)
        
        for resp, docs in self.responsibility_map.items():
            if len(docs) > 1:
                overlap_docs.append({
                    "responsibility": resp,
                    "docs": [str(d.relative_to(self.project_root)) for d in docs],
                    "count": len(docs),
                    "severity": "中"
                })
        
        self.audit_results['deep_check']['responsibility_overlap'] = overlap_docs
        print(f"发现 {len(overlap_docs)} 组职责重叠的文档")
        
        if overlap_docs:
            print("\n职责重叠文档详情 (前10组):")
            for i, overlap in enumerate(overlap_docs[:10], 1):
                print(f"\n{i}. 职责: {overlap['responsibility']}")
                print(f"   文档数: {overlap['count']}")
                for doc in overlap['docs']:
                    print(f"   - {doc}")
    
    def audit_L1_file_system(self, layer4_docs: List[Path]):
        """L1文件系统层审计"""
        print("\n" + "=" * 80)
        print("L1文件系统层审计")
        print("=" * 80)
        
        for doc_path in layer4_docs:
            doc_str = str(doc_path.relative_to(self.project_root))
            
            if '01_FRAMEWORK' not in doc_str:
                self.audit_results['L1_file_system']['directory_structure'].append({
                    "doc": doc_str,
                    "issue": "目录漂移",
                    "description": "Layer 4文档不在01_FRAMEWORK目录中",
                    "severity": "中"
                })
            
            file_name = doc_path.stem
            if re.search(r'layer[_\s]*[0-9]', file_name, re.IGNORECASE):
                self.audit_results['L1_file_system']['file_naming'].append({
                    "doc": doc_str,
                    "issue": "旧架构命名残留",
                    "description": f"文件名包含旧架构关键词: {file_name}",
                    "severity": "低"
                })
            
            content = self.doc_contents[doc_path]
            link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
            matches = re.findall(link_pattern, content)
            
            for text, link in matches:
                if link.startswith('http'):
                    continue
                
                if link.startswith('/'):
                    self.audit_results['L1_file_system']['path_references'].append({
                        "doc": doc_str,
                        "issue": "绝对路径硬编码",
                        "description": f"使用绝对路径: {link}",
                        "severity": "低"
                    })
                
                link_path = doc_path.parent / link
                if not link_path.exists():
                    self.audit_results['L1_file_system']['path_references'].append({
                        "doc": doc_str,
                        "issue": "死链接",
                        "description": f"链接指向不存在的文件: {link}",
                        "severity": "高"
                    })
    
    def audit_L2_document_content(self, layer4_docs: List[Path]):
        """L2文档内容层审计"""
        print("\n" + "=" * 80)
        print("L2文档内容层审计")
        print("=" * 80)
        
        for doc_path in layer4_docs:
            doc_str = str(doc_path.relative_to(self.project_root))
            content = self.doc_contents[doc_path]
            yaml_header, body = self.extract_yaml_header(content)
            
            if not yaml_header:
                self.audit_results['L2_document_content']['responsibility_driven'].append({
                    "doc": doc_str,
                    "issue": "职责缺失",
                    "description": "文档缺少YAML头部，无法确定职责",
                    "severity": "高"
                })
            else:
                if 'responsibility' not in yaml_header:
                    self.audit_results['L2_document_content']['responsibility_driven'].append({
                        "doc": doc_str,
                        "issue": "职责缺失",
                        "description": "文档缺少responsibility字段",
                        "severity": "高"
                    })
                elif len(yaml_header.get('responsibility', '')) < 20:
                    self.audit_results['L2_document_content']['responsibility_driven'].append({
                        "doc": doc_str,
                        "issue": "职责不清",
                        "description": f"职责描述过短: {yaml_header.get('responsibility', '')}",
                        "severity": "中"
                    })
                
                if 'layer' not in yaml_header:
                    self.audit_results['L2_document_content']['responsibility_driven'].append({
                        "doc": doc_str,
                        "issue": "Layer归属缺失",
                        "description": "文档缺少layer字段",
                        "severity": "中"
                    })
            
            if 'module_id' not in (yaml_header or {}):
                self.audit_results['L2_document_content']['version_isolation'].append({
                    "doc": doc_str,
                    "issue": "编号缺失",
                    "description": "文档缺少module_id字段",
                    "severity": "中"
                })
    
    def audit_L3_professional_standards(self, layer4_docs: List[Path]):
        """L3专业标准层审计"""
        print("\n" + "=" * 80)
        print("L3专业标准层审计")
        print("=" * 80)
        
        required_fields = [
            'module_id', 'version', 'status', 'created_date', 
            'last_updated', 'owner', 'responsibility', 'layer', 'standard_type'
        ]
        
        for doc_path in layer4_docs:
            doc_str = str(doc_path.relative_to(self.project_root))
            content = self.doc_contents[doc_path]
            yaml_header, body = self.extract_yaml_header(content)
            
            if not yaml_header:
                self.audit_results['L3_professional_standards']['document_quality'].append({
                    "doc": doc_str,
                    "issue": "YAML头部缺失",
                    "description": "文档缺少标准YAML元数据",
                    "severity": "高"
                })
                continue
            
            missing_fields = []
            for field in required_fields:
                if field not in yaml_header:
                    missing_fields.append(field)
            
            if missing_fields:
                self.audit_results['L3_professional_standards']['document_quality'].append({
                    "doc": doc_str,
                    "issue": "YAML字段不完整",
                    "description": f"缺少字段: {', '.join(missing_fields)}",
                    "severity": "中"
                })
            
            if 'standard_type' not in yaml_header:
                self.audit_results['L3_professional_standards']['document_classification'].append({
                    "doc": doc_str,
                    "issue": "文档类型缺失",
                    "description": "缺少standard_type字段",
                    "severity": "中"
                })
            
            if 'module_id' in yaml_header:
                module_id = yaml_header['module_id']
                if len(module_id) < 10:
                    self.audit_results['L3_professional_standards']['numbering_system'].append({
                        "doc": doc_str,
                        "issue": "编号不规范",
                        "description": f"module_id过短: {module_id}",
                        "severity": "低"
                    })
    
    def run(self):
        """执行深度审计"""
        print("=" * 80)
        print("Layer 4机器学习层深度审计 v2")
        print("=" * 80)
        print(f"审计时间: {self.audit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计标准: 专业量化机构五大原则 + 三层审计标准 + 深度检查")
        print("-" * 80)
        
        layer4_docs = self.get_layer4_docs()
        
        print(f"\n发现 {len(layer4_docs)} 个Layer 4文档")
        print("-" * 80)
        
        self.audit_L1_file_system(layer4_docs)
        self.audit_L2_document_content(layer4_docs)
        self.audit_L3_professional_standards(layer4_docs)
        
        self.check_duplicate_documents()
        self.check_unclear_responsibility()
        self.check_responsibility_overlap()
        
        L1_issues = (
            len(self.audit_results['L1_file_system']['directory_structure']) +
            len(self.audit_results['L1_file_system']['file_naming']) +
            len(self.audit_results['L1_file_system']['path_references'])
        )
        
        L2_issues = (
            len(self.audit_results['L2_document_content']['responsibility_driven']) +
            len(self.audit_results['L2_document_content']['version_isolation'])
        )
        
        L3_issues = (
            len(self.audit_results['L3_professional_standards']['document_classification']) +
            len(self.audit_results['L3_professional_standards']['numbering_system']) +
            len(self.audit_results['L3_professional_standards']['document_quality'])
        )
        
        deep_issues = (
            len(self.audit_results['deep_check']['duplicate_documents']) +
            len(self.audit_results['deep_check']['unclear_responsibility']) +
            len(self.audit_results['deep_check']['responsibility_overlap'])
        )
        
        total_issues = L1_issues + L2_issues + L3_issues + deep_issues
        
        self.audit_results['summary']['total_docs'] = len(layer4_docs)
        self.audit_results['summary']['total_issues'] = total_issues
        self.audit_results['summary']['L1_issues'] = L1_issues
        self.audit_results['summary']['L2_issues'] = L2_issues
        self.audit_results['summary']['L3_issues'] = L3_issues
        self.audit_results['summary']['deep_issues'] = deep_issues
        
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
        print(f"  - 版本隔离问题: {len(self.audit_results['L2_document_content']['version_isolation'])}")
        print(f"\nL3专业标准层问题: {L3_issues}")
        print(f"  - 文档分类问题: {len(self.audit_results['L3_professional_standards']['document_classification'])}")
        print(f"  - 编号体系问题: {len(self.audit_results['L3_professional_standards']['numbering_system'])}")
        print(f"  - 文档质量问题: {len(self.audit_results['L3_professional_standards']['document_quality'])}")
        print(f"\n深度检查问题: {deep_issues}")
        print(f"  - 重复文档: {len(self.audit_results['deep_check']['duplicate_documents'])}")
        print(f"  - 职责不清: {len(self.audit_results['deep_check']['unclear_responsibility'])}")
        print(f"  - 职责重叠: {len(self.audit_results['deep_check']['responsibility_overlap'])}")
        print(f"\n总问题数: {total_issues}")
        print(f"合规率: {self.audit_results['summary']['compliance_rate']}%")
        
        report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"layer4_deep_audit_v2_{self.audit_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n审计报告已保存至: {report_path}")
        print("=" * 80)

if __name__ == "__main__":
    auditor = Layer4DeepAuditorV2()
    auditor.run()
