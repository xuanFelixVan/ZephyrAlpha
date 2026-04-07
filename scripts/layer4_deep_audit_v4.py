"""
Layer 4机器学习层深度审计脚本 v4
实现四层审计标准，重点检查重复文档和职责不清的内容
"""
import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class Layer4DeepAuditV4:
    def __init__(self):
        self.project_root = Path("D:/ZephyrAlpha")
        self.audit_time = datetime.now()
        self.audit_results = {
            "audit_info": {
                "audit_time": self.audit_time.strftime("%Y-%m-%d %H:%M:%S"),
                "audit_standard": "专业量化机构五大原则 + 四层审计标准v4",
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
        self.doc_hashes = {}
        self.doc_contents = {}
        self.responsibility_map = defaultdict(list)
        
    def get_layer4_docs(self):
        """获取所有Layer 4文档"""
        layer4_docs = []
        
        layer4_dir = self.project_root / "docs" / "01_FRAMEWORK" / "LAYER4_ML"
        if layer4_dir.exists():
            for md_file in layer4_dir.rglob("*.md"):
                layer4_docs.append(str(md_file.relative_to(self.project_root)))
        
        for md_file in self.project_root.glob("docs/01_FRAMEWORK/*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'layer: 4' in content.lower() or 'layer: layer 4' in content.lower():
                        layer4_docs.append(str(md_file.relative_to(self.project_root)))
            except:
                pass
        
        return sorted(list(set(layer4_docs)))
    
    def calculate_content_hash(self, content):
        """计算内容哈希值"""
        normalized = re.sub(r'\s+', ' ', content.lower().strip())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def extract_responsibility(self, content):
        """提取职责描述"""
        responsibility = None
        
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            resp_match = re.search(r'responsibility:\s*\n(\s*-\s*[^\n]+\n?)+', yaml_content)
            if resp_match:
                responsibility = resp_match.group(0).strip()
        
        resp_block = re.search(r'>\s*\*\*核心职责\*\*:\s*([^\n]+)', content)
        if resp_block:
            responsibility = resp_block.group(1).strip()
        
        return responsibility
    
    def audit_L1_file_system(self, docs):
        """L1文件系统层审计"""
        print("\n执行L1文件系统层审计...")
        
        for doc in docs:
            doc_path = self.project_root / doc
            
            if not doc_path.exists():
                continue
            
            if "LAYER4_ML" not in doc and "01_FRAMEWORK" in doc:
                expected_path = doc.replace("docs/01_FRAMEWORK/", "docs/01_FRAMEWORK/LAYER4_ML/")
                self.audit_results["L1_file_system"]["directory_structure"].append({
                    "doc": doc,
                    "issue": "目录漂移",
                    "description": "Layer 4文档不在LAYER4_ML目录中",
                    "current_path": doc,
                    "expected_path": expected_path
                })
            
            filename = doc_path.stem
            if re.search(r'Layer\s*[0-9]', filename, re.IGNORECASE):
                self.audit_results["L1_file_system"]["file_naming"].append({
                    "doc": doc,
                    "issue": "旧架构命名残留",
                    "description": f"文件名包含旧架构关键词: {filename}"
                })
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                for match in re.finditer(link_pattern, content):
                    link_text = match.group(1)
                    link = match.group(2)
                    
                    if link.startswith('http') or link.startswith('#'):
                        continue
                    
                    if link.startswith('./01_FRAMEWORK') or link.startswith('./docs'):
                        self.audit_results["L1_file_system"]["path_references"].append({
                            "doc": doc,
                            "issue": "路径冗余",
                            "description": f"链接路径冗余: {link}",
                            "link": link,
                            "link_text": link_text
                        })
                    
                    if link.startswith('./') or link.startswith('../'):
                        target_path = (doc_path.parent / link).resolve()
                        if not target_path.exists():
                            self.audit_results["L1_file_system"]["path_references"].append({
                                "doc": doc,
                                "issue": "死链接",
                                "description": f"链接指向不存在的文件: {link}",
                                "link": link,
                                "link_text": link_text
                            })
            except Exception as e:
                pass
    
    def audit_L2_document_content(self, docs):
        """L2文档内容层审计"""
        print("执行L2文档内容层审计...")
        
        for doc in docs:
            doc_path = self.project_root / doc
            
            if not doc_path.exists():
                continue
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.doc_contents[doc] = content
                self.doc_hashes[doc] = self.calculate_content_hash(content)
                
                responsibility = self.extract_responsibility(content)
                
                if not responsibility:
                    self.audit_results["L2_document_content"]["responsibility_driven"].append({
                        "doc": doc,
                        "issue": "职责缺失",
                        "description": "文档缺少职责描述"
                    })
                elif len(responsibility) < 20:
                    self.audit_results["L2_document_content"]["responsibility_driven"].append({
                        "doc": doc,
                        "issue": "职责不清",
                        "description": f"职责描述过短: {responsibility}"
                    })
                else:
                    self.responsibility_map[responsibility].append(doc)
                
                yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if not yaml_match:
                    self.audit_results["L2_document_content"]["version_isolation"].append({
                        "doc": doc,
                        "issue": "YAML头部缺失",
                        "description": "文档缺少标准YAML头部"
                    })
                else:
                    yaml_content = yaml_match.group(1)
                    required_fields = ['module_id', 'version', 'status', 'created_date', 'last_updated']
                    for field in required_fields:
                        if field not in yaml_content:
                            self.audit_results["L2_document_content"]["version_isolation"].append({
                                "doc": doc,
                                "issue": "YAML字段缺失",
                                "description": f"YAML头部缺少必要字段: {field}"
                            })
                
            except Exception as e:
                pass
    
    def audit_L3_professional_standards(self, docs):
        """L3专业标准层审计"""
        print("执行L3专业标准层审计...")
        
        module_ids = {}
        
        for doc in docs:
            doc_path = self.project_root / doc
            
            if not doc_path.exists():
                continue
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    
                    module_id_match = re.search(r'module_id:\s*([^\n]+)', yaml_content)
                    if module_id_match:
                        module_id = module_id_match.group(1).strip()
                        
                        if module_id in module_ids:
                            self.audit_results["L3_professional_standards"]["numbering_system"].append({
                                "doc": doc,
                                "issue": "编号重复",
                                "description": f"module_id重复: {module_id} (已在 {module_ids[module_id]} 中使用)"
                            })
                        else:
                            module_ids[module_id] = doc
                    
                    if 'layer:' in yaml_content.lower():
                        layer_match = re.search(r'layer:\s*([^\n]+)', yaml_content, re.IGNORECASE)
                        if layer_match:
                            layer_value = layer_match.group(1).strip()
                            if '4' not in layer_value and '机器学习' not in layer_value:
                                self.audit_results["L3_professional_standards"]["document_classification"].append({
                                    "doc": doc,
                                    "issue": "分类错误",
                                    "description": f"Layer归属错误: {layer_value}"
                                })
                
            except Exception as e:
                pass
    
    def check_duplicate_documents(self, docs):
        """深度检查：重复文档"""
        print("执行深度检查：重复文档...")
        
        hash_groups = defaultdict(list)
        for doc, hash_val in self.doc_hashes.items():
            hash_groups[hash_val].append(doc)
        
        for hash_val, doc_list in hash_groups.items():
            if len(doc_list) > 1:
                self.audit_results["deep_check"]["duplicate_documents"].append({
                    "issue": "内容重复",
                    "description": f"发现{len(doc_list)}个内容相同的文档",
                    "documents": doc_list,
                    "hash": hash_val
                })
        
        content_groups = defaultdict(list)
        for doc, content in self.doc_contents.items():
            title_match = re.search(r'^#\s+([^\n]+)', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip().lower()
                content_groups[title].append(doc)
        
        for title, doc_list in content_groups.items():
            if len(doc_list) > 1:
                self.audit_results["deep_check"]["content_similarity"].append({
                    "issue": "标题重复",
                    "description": f"发现{len(doc_list)}个标题相同的文档: {title}",
                    "documents": doc_list
                })
    
    def check_unclear_responsibility(self, docs):
        """深度检查：职责不清"""
        print("执行深度检查：职责不清...")
        
        for doc in docs:
            doc_path = self.project_root / doc
            
            if not doc_path.exists():
                continue
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                responsibility = self.extract_responsibility(content)
                
                if not responsibility:
                    self.audit_results["deep_check"]["unclear_responsibility"].append({
                        "doc": doc,
                        "issue": "职责缺失",
                        "description": "文档完全没有职责描述"
                    })
                elif '扩展功能、辅助模块' in responsibility:
                    self.audit_results["deep_check"]["unclear_responsibility"].append({
                        "doc": doc,
                        "issue": "职责模糊",
                        "description": f"职责描述过于通用: {responsibility}"
                    })
                elif len(responsibility) < 30:
                    self.audit_results["deep_check"]["unclear_responsibility"].append({
                        "doc": doc,
                        "issue": "职责过短",
                        "description": f"职责描述过短: {responsibility}"
                    })
                
            except Exception as e:
                pass
    
    def check_responsibility_overlap(self):
        """深度检查：职责重叠"""
        print("执行深度检查：职责重叠...")
        
        for responsibility, doc_list in self.responsibility_map.items():
            if len(doc_list) > 1:
                self.audit_results["deep_check"]["responsibility_overlap"].append({
                    "issue": "职责重叠",
                    "description": f"发现{len(doc_list)}个文档具有相同职责",
                    "responsibility": responsibility,
                    "documents": doc_list
                })
    
    def run(self):
        """执行深度审计"""
        print("=" * 80)
        print("Layer 4机器学习层深度审计 v4")
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
            len(self.audit_results['deep_check']['responsibility_overlap']) +
            len(self.audit_results['deep_check']['content_similarity'])
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
        print(f"  - 内容相似: {len(self.audit_results['deep_check']['content_similarity'])}")
        print(f"\n总问题数: {total_issues}")
        print(f"合规率: {self.audit_results['summary']['compliance_rate']}%")
        
        report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"layer4_deep_audit_v4_{self.audit_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n审计报告已保存至: {report_path}")
        print("=" * 80)

if __name__ == "__main__":
    audit = Layer4DeepAuditV4()
    audit.run()
