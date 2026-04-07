#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 4机器学习层深度审计 v3
重点检查：重复文档、职责不清、三层审计标准
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
import hashlib

class Layer4DeepAuditV3:
    def __init__(self):
        self.project_root = Path("D:/ZephyrAlpha")
        self.audit_time = datetime.now()
        self.audit_results = {
            "audit_info": {
                "audit_time": self.audit_time.strftime('%Y-%m-%d %H:%M:%S'),
                "audit_standard": "专业量化机构五大原则 + 三层审计标准 + 深度检查v3",
                "audit_scope": "Layer 4机器学习层所有文档"
            },
            "L1_file_system": {
                "directory_structure": [],
                "file_naming": [],
                "path_references": []
            },
            "L2_document_content": {
                "responsibility_driven": [],
                "index_completeness": [],
                "version_isolation": []
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
                "responsibility_overlap": [],
                "content_similarity": []
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
        
        self.layer4_docs = []
        self.responsibility_map = defaultdict(list)
        self.content_hash_map = defaultdict(list)
    
    def get_layer4_docs(self) -> List[Path]:
        """获取所有Layer 4文档"""
        docs_dir = self.project_root / "docs"
        md_files = list(docs_dir.rglob("*.md"))
        
        layer4_docs = []
        for md_file in md_files:
            if '06_ARCHIVE' in str(md_file):
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                layer_match = re.search(r'layer:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
                if layer_match:
                    layer_value = layer_match.group(1).strip()
                    if 'layer 4' in layer_value.lower() or 'layer4' in layer_value.lower() or '机器学习' in layer_value:
                        layer4_docs.append(md_file)
                        continue
                
                if any(keyword in str(md_file).lower() for keyword in ['ml', 'machine_learning', 'machine-learning', '机器学习', 'layer4', 'layer_4', 'layer 4']):
                    layer4_docs.append(md_file)
                    
            except:
                pass
        
        return layer4_docs
    
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
    
    def extract_yaml_header(self, content: str) -> Tuple[Optional[str], str]:
        """提取YAML头部"""
        if not content.startswith('---'):
            return None, content
        
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), '---' + '---'.join(parts[2:])
        return None, content
    
    def calculate_content_hash(self, content: str) -> str:
        """计算内容哈希"""
        yaml_header, body = self.extract_yaml_header(content)
        clean_content = re.sub(r'\s+', ' ', body.lower())
        return hashlib.md5(clean_content.encode()).hexdigest()
    
    def audit_L1_file_system(self, docs: List[Path]):
        """L1文件系统层审计"""
        print("\n" + "=" * 80)
        print("L1 文件系统层审计")
        print("=" * 80)
        
        for doc in docs:
            doc_str = str(doc.relative_to(self.project_root))
            
            if '01_FRAMEWORK' not in str(doc):
                self.audit_results['L1_file_system']['directory_structure'].append({
                    "doc": doc_str,
                    "issue": "目录漂移",
                    "description": f"Layer 4文档不在01_FRAMEWORK目录中",
                    "current_path": doc_str,
                    "expected_path": f"docs/01_FRAMEWORK/LAYER4_ML/{doc.name}"
                })
            
            file_name = doc.name
            
            if re.search(r'layer[_\s]*\d+', file_name, re.IGNORECASE):
                if not re.match(r'^layer\d+_', file_name, re.IGNORECASE):
                    self.audit_results['L1_file_system']['file_naming'].append({
                        "doc": doc_str,
                        "issue": "文件命名不规范",
                        "description": f"文件名包含Layer关键词但格式不规范: {file_name}",
                        "current_name": file_name,
                        "suggested_name": re.sub(r'layer[_\s]*(\d+)', r'layer\1_', file_name, flags=re.IGNORECASE)
                    })
            
            if ' ' in file_name:
                self.audit_results['L1_file_system']['file_naming'].append({
                    "doc": doc_str,
                    "issue": "文件名包含空格",
                    "description": f"文件名包含空格: {file_name}",
                    "current_name": file_name,
                    "suggested_name": file_name.replace(' ', '_')
                })
            
            content = self.read_file_content(doc)
            if content:
                link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
                matches = re.finditer(link_pattern, content)
                
                for match in matches:
                    link = match.group(2)
                    
                    if link.startswith('http') or link.startswith('#'):
                        continue
                    
                    if link.startswith('/'):
                        link_path = self.project_root / link.lstrip('/')
                    else:
                        link_path = doc.parent / link
                    
                    if not link_path.exists():
                        self.audit_results['L1_file_system']['path_references'].append({
                            "doc": doc_str,
                            "issue": "死链接",
                            "description": f"链接指向不存在的文件: {link}",
                            "link": link,
                            "link_text": match.group(1)
                        })
        
        L1_issues = (
            len(self.audit_results['L1_file_system']['directory_structure']) +
            len(self.audit_results['L1_file_system']['file_naming']) +
            len(self.audit_results['L1_file_system']['path_references'])
        )
        
        print(f"目录结构问题: {len(self.audit_results['L1_file_system']['directory_structure'])}")
        print(f"文件命名问题: {len(self.audit_results['L1_file_system']['file_naming'])}")
        print(f"路径引用问题: {len(self.audit_results['L1_file_system']['path_references'])}")
        print(f"L1总问题数: {L1_issues}")
    
    def audit_L2_document_content(self, docs: List[Path]):
        """L2文档内容层审计"""
        print("\n" + "=" * 80)
        print("L2 文档内容层审计")
        print("=" * 80)
        
        for doc in docs:
            doc_str = str(doc.relative_to(self.project_root))
            content = self.read_file_content(doc)
            
            if not content:
                continue
            
            yaml_header, body = self.extract_yaml_header(content)
            
            if not yaml_header:
                self.audit_results['L2_document_content']['responsibility_driven'].append({
                    "doc": doc_str,
                    "issue": "缺少YAML头部",
                    "description": "文档缺少标准YAML元数据"
                })
                continue
            
            if 'responsibility:' not in yaml_header:
                self.audit_results['L2_document_content']['responsibility_driven'].append({
                    "doc": doc_str,
                    "issue": "缺少responsibility字段",
                    "description": "YAML头部缺少职责描述字段"
                })
            else:
                resp_match = re.search(r'responsibility:\s*\n((?:\s+-\s+.+\n?)+)', yaml_header)
                if resp_match:
                    resp_text = resp_match.group(1).strip()
                    
                    if len(resp_text) < 20:
                        self.audit_results['L2_document_content']['responsibility_driven'].append({
                            "doc": doc_str,
                            "issue": "职责描述过短",
                            "description": f"职责描述过短: {resp_text}",
                            "current_responsibility": resp_text
                        })
                    else:
                        self.responsibility_map[resp_text].append(doc_str)
            
            if 'layer:' not in yaml_header:
                self.audit_results['L2_document_content']['responsibility_driven'].append({
                    "doc": doc_str,
                    "issue": "缺少layer字段",
                    "description": "YAML头部缺少Layer归属字段"
                })
            
            if 'module_id:' not in yaml_header:
                self.audit_results['L2_document_content']['responsibility_driven'].append({
                    "doc": doc_str,
                    "issue": "缺少module_id字段",
                    "description": "YAML头部缺少模块编号字段"
                })
        
        L2_issues = (
            len(self.audit_results['L2_document_content']['responsibility_driven']) +
            len(self.audit_results['L2_document_content']['index_completeness']) +
            len(self.audit_results['L2_document_content']['version_isolation'])
        )
        
        print(f"职责驱动问题: {len(self.audit_results['L2_document_content']['responsibility_driven'])}")
        print(f"索引完备问题: {len(self.audit_results['L2_document_content']['index_completeness'])}")
        print(f"版本隔离问题: {len(self.audit_results['L2_document_content']['version_isolation'])}")
        print(f"L2总问题数: {L2_issues}")
    
    def audit_L3_professional_standards(self, docs: List[Path]):
        """L3专业标准层审计"""
        print("\n" + "=" * 80)
        print("L3 专业标准层审计")
        print("=" * 80)
        
        module_ids = defaultdict(list)
        
        for doc in docs:
            doc_str = str(doc.relative_to(self.project_root))
            content = self.read_file_content(doc)
            
            if not content:
                continue
            
            yaml_header, body = self.extract_yaml_header(content)
            
            if not yaml_header:
                self.audit_results['L3_professional_standards']['document_quality'].append({
                    "doc": doc_str,
                    "issue": "YAML头部缺失",
                    "description": "文档缺少标准YAML元数据"
                })
                continue
            
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner', 'responsibility']
            missing_fields = []
            
            for field in required_fields:
                if f'{field}:' not in yaml_header:
                    missing_fields.append(field)
            
            if missing_fields:
                self.audit_results['L3_professional_standards']['document_quality'].append({
                    "doc": doc_str,
                    "issue": "YAML字段不完整",
                    "description": f"缺少必填字段: {', '.join(missing_fields)}",
                    "missing_fields": missing_fields
                })
            
            module_id_match = re.search(r'module_id:\s*(.+?)(?:\n|$)', yaml_header)
            if module_id_match:
                module_id = module_id_match.group(1).strip()
                module_ids[module_id].append(doc_str)
                
                if len(module_id) < 5:
                    self.audit_results['L3_professional_standards']['numbering_system'].append({
                        "doc": doc_str,
                        "issue": "编号不规范",
                        "description": f"module_id过短: {module_id}",
                        "current_module_id": module_id
                    })
        
        for module_id, doc_list in module_ids.items():
            if len(doc_list) > 1:
                self.audit_results['L3_professional_standards']['numbering_system'].append({
                    "issue": "编号重复",
                    "description": f"多个文档使用相同的module_id: {module_id}",
                    "docs": doc_list,
                    "module_id": module_id
                })
        
        L3_issues = (
            len(self.audit_results['L3_professional_standards']['five_principles']) +
            len(self.audit_results['L3_professional_standards']['document_classification']) +
            len(self.audit_results['L3_professional_standards']['numbering_system']) +
            len(self.audit_results['L3_professional_standards']['document_quality'])
        )
        
        print(f"五大原则问题: {len(self.audit_results['L3_professional_standards']['five_principles'])}")
        print(f"文档分类问题: {len(self.audit_results['L3_professional_standards']['document_classification'])}")
        print(f"编号体系问题: {len(self.audit_results['L3_professional_standards']['numbering_system'])}")
        print(f"文档质量问题: {len(self.audit_results['L3_professional_standards']['document_quality'])}")
        print(f"L3总问题数: {L3_issues}")
    
    def check_duplicate_documents(self, docs: List[Path]):
        """检查重复文档"""
        print("\n" + "=" * 80)
        print("深度检查：重复文档")
        print("=" * 80)
        
        for doc in docs:
            content = self.read_file_content(doc)
            if not content:
                continue
            
            content_hash = self.calculate_content_hash(content)
            self.content_hash_map[content_hash].append(str(doc.relative_to(self.project_root)))
        
        for content_hash, doc_list in self.content_hash_map.items():
            if len(doc_list) > 1:
                self.audit_results['deep_check']['duplicate_documents'].append({
                    "issue": "重复文档",
                    "description": f"发现{len(doc_list)}个内容相似的文档",
                    "docs": doc_list,
                    "content_hash": content_hash
                })
        
        print(f"发现重复文档组: {len(self.audit_results['deep_check']['duplicate_documents'])}")
    
    def check_unclear_responsibility(self, docs: List[Path]):
        """检查职责不清"""
        print("\n" + "=" * 80)
        print("深度检查：职责不清")
        print("=" * 80)
        
        vague_keywords = ['管理', '处理', '操作', '相关', '其他', '等', '等等', '功能', '模块']
        
        for doc in docs:
            doc_str = str(doc.relative_to(self.project_root))
            content = self.read_file_content(doc)
            
            if not content:
                continue
            
            yaml_header, body = self.extract_yaml_header(content)
            
            issues = []
            
            if not yaml_header:
                issues.append("缺少YAML头部")
            
            if yaml_header and 'responsibility:' not in yaml_header:
                issues.append("缺少responsibility字段")
            
            if yaml_header:
                resp_match = re.search(r'responsibility:\s*\n((?:\s+-\s+.+\n?)+)', yaml_header)
                if resp_match:
                    resp_text = resp_match.group(1).strip()
                    
                    if len(resp_text) < 20:
                        issues.append(f"职责描述过短: {resp_text}")
                    
                    vague_count = sum(1 for keyword in vague_keywords if keyword in resp_text)
                    if vague_count > 2:
                        issues.append(f"职责描述包含过多模糊关键词: {resp_text}")
            
            if issues:
                self.audit_results['deep_check']['unclear_responsibility'].append({
                    "doc": doc_str,
                    "issues": issues,
                    "description": "; ".join(issues)
                })
        
        print(f"发现职责不清文档: {len(self.audit_results['deep_check']['unclear_responsibility'])}")
    
    def check_responsibility_overlap(self):
        """检查职责重叠"""
        print("\n" + "=" * 80)
        print("深度检查：职责重叠")
        print("=" * 80)
        
        for resp_text, doc_list in self.responsibility_map.items():
            if len(doc_list) > 1:
                self.audit_results['deep_check']['responsibility_overlap'].append({
                    "issue": "职责重叠",
                    "description": f"发现{len(doc_list)}个文档具有相同的职责描述",
                    "responsibility": resp_text,
                    "docs": doc_list
                })
        
        print(f"发现职责重叠组: {len(self.audit_results['deep_check']['responsibility_overlap'])}")
    
    def run(self):
        """执行深度审计"""
        print("=" * 80)
        print("Layer 4机器学习层深度审计 v3")
        print("=" * 80)
        print(f"审计时间: {self.audit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计标准: {self.audit_results['audit_info']['audit_standard']}")
        print("-" * 80)
        
        layer4_docs = self.get_layer4_docs()
        
        print(f"\n发现 {len(layer4_docs)} 个Layer 4文档")
        print("-" * 80)
        
        self.audit_L1_file_system(layer4_docs)
        self.audit_L2_document_content(layer4_docs)
        self.audit_L3_professional_standards(layer4_docs)
        
        self.check_duplicate_documents(layer4_docs)
        self.check_unclear_responsibility(layer4_docs)
        self.check_responsibility_overlap()
        
        L1_issues = (
            len(self.audit_results['L1_file_system']['directory_structure']) +
            len(self.audit_results['L1_file_system']['file_naming']) +
            len(self.audit_results['L1_file_system']['path_references'])
        )
        
        L2_issues = (
            len(self.audit_results['L2_document_content']['responsibility_driven']) +
            len(self.audit_results['L2_document_content']['index_completeness']) +
            len(self.audit_results['L2_document_content']['version_isolation'])
        )
        
        L3_issues = (
            len(self.audit_results['L3_professional_standards']['five_principles']) +
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
        print(f"  - 索引完备问题: {len(self.audit_results['L2_document_content']['index_completeness'])}")
        print(f"  - 版本隔离问题: {len(self.audit_results['L2_document_content']['version_isolation'])}")
        print(f"\nL3专业标准层问题: {L3_issues}")
        print(f"  - 五大原则问题: {len(self.audit_results['L3_professional_standards']['five_principles'])}")
        print(f"  - 文档分类问题: {len(self.audit_results['L3_professional_standards']['document_classification'])}")
        print(f"  - 编号体系问题: {len(self.audit_results['L3_professional_standards']['numbering_system'])}")
        print(f"  - 文档质量问题: {len(self.audit_results['L3_professional_standards']['document_quality'])}")
        print(f"\n深度检查问题: {deep_issues}")
        print(f"  - 重复文档: {len(self.audit_results['deep_check']['duplicate_documents'])}")
        print(f"  - 职责不清: {len(self.audit_results['deep_check']['unclear_responsibility'])}")
        print(f"  - 职责重叠: {len(self.audit_results['deep_check']['responsibility_overlap'])}")
        print(f"\n总问题数: {total_issues}")
        print(f"合规率: {self.audit_results['summary']['compliance_rate']}%")
        
        report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"layer4_deep_audit_v3_{self.audit_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n审计报告已保存至: {report_path}")
        print("=" * 80)

if __name__ == "__main__":
    audit = Layer4DeepAuditV3()
    audit.run()
