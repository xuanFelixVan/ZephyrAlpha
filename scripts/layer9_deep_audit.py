#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 9研究与创新层深度审计脚本
按照专业量化机构五大原则和三层审计标准进行全面审计
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class Layer9DeepAuditor:
    """Layer 9深度审计器"""
    
    def __init__(self):
        self.layer9_path = Path("docs/09_RESEARCH_INNOVATION")
        self.audit_results = {
            "L1_文件系统层": {
                "目录结构问题": [],
                "文件命名问题": [],
                "路径引用问题": []
            },
            "L2_文档内容层": {
                "职责驱动问题": [],
                "索引完备性问题": [],
                "版本隔离问题": [],
                "文档代码对应问题": []
            },
            "L3_专业标准层": {
                "五大原则问题": [],
                "文档分类问题": [],
                "编号体系问题": [],
                "文档质量问题": []
            }
        }
        self.documents = []
        self.module_ids = defaultdict(list)
        self.responsibilities = defaultdict(list)
        
    def run_audit(self):
        """执行完整审计"""
        print("=" * 80)
        print("Layer 9研究与创新层深度审计")
        print("=" * 80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计路径: {self.layer9_path}")
        print()
        
        # L1文件系统层审计
        self.audit_L1_filesystem()
        
        # L2文档内容层审计
        self.audit_L2_content()
        
        # L3专业标准层审计
        self.audit_L3_standards()
        
        # 生成报告
        self.generate_report()
        
    def audit_L1_filesystem(self):
        """L1文件系统层审计"""
        print("🔍 执行L1文件系统层审计...")
        print()
        
        # 1.1 目录结构问题
        self.check_directory_structure()
        
        # 1.2 文件命名问题
        self.check_file_naming()
        
        # 1.3 路径引用问题
        self.check_path_references()
        
    def check_directory_structure(self):
        """检查目录结构"""
        print("  📁 检查目录结构...")
        
        # 检查目录层级深度
        for root, dirs, files in os.walk(self.layer9_path):
            rel_path = os.path.relpath(root, self.layer9_path)
            depth = rel_path.count(os.sep) if rel_path != "." else 0
            
            # 检查目录层级过深
            if depth > 4:
                self.audit_results["L1_文件系统层"]["目录结构问题"].append({
                    "问题类型": "目录层级过深",
                    "路径": root,
                    "层级深度": depth,
                    "严重程度": "中"
                })
            
            # 检查稀疏目录
            if len(files) < 3 and depth > 0 and not root.endswith("_archive") and not root.endswith("maintenance_records"):
                self.audit_results["L1_文件系统层"]["目录结构问题"].append({
                    "问题类型": "稀疏目录",
                    "路径": root,
                    "文件数": len(files),
                    "严重程度": "低"
                })
        
        print("    ✅ 目录结构检查完成")
        
    def check_file_naming(self):
        """检查文件命名"""
        print("  📝 检查文件命名...")
        
        md_files = list(self.layer9_path.rglob("*.md"))
        
        for md_file in md_files:
            filename = md_file.name
            
            # 检查命名不规范
            if not re.match(r'^[A-Z0-9_]+\.md$', filename) and filename != "INDEX.md":
                # 检查是否包含中文
                if re.search(r'[\u4e00-\u9fff]', filename):
                    self.audit_results["L1_文件系统层"]["文件命名问题"].append({
                        "问题类型": "文件名包含中文",
                        "文件": str(md_file.relative_to(self.layer9_path)),
                        "严重程度": "低"
                    })
            
            # 检查版本号缺失（对于蓝图文件）
            if "BLUEPRINT" in filename and "V" not in filename and filename != "BLUEPRINT.md":
                self.audit_results["L1_文件系统层"]["文件命名问题"].append({
                    "问题类型": "蓝图文件缺少版本号",
                    "文件": str(md_file.relative_to(self.layer9_path)),
                    "严重程度": "低"
                })
        
        print("    ✅ 文件命名检查完成")
        
    def check_path_references(self):
        """检查路径引用"""
        print("  🔗 检查路径引用...")
        
        md_files = list(self.layer9_path.rglob("*.md"))
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查过多的../引用
                if content.count("../") > 10:
                    self.audit_results["L1_文件系统层"]["路径引用问题"].append({
                        "问题类型": "路径引用冗余",
                        "文件": str(md_file.relative_to(self.layer9_path)),
                        "引用次数": content.count("../"),
                        "严重程度": "低"
                    })
                
                # 检查绝对路径硬编码
                if re.search(r'\[.*?\]\([A-Z]:\\', content):
                    self.audit_results["L1_文件系统层"]["路径引用问题"].append({
                        "问题类型": "绝对路径硬编码",
                        "文件": str(md_file.relative_to(self.layer9_path)),
                        "严重程度": "中"
                    })
                    
            except Exception as e:
                pass
        
        print("    ✅ 路径引用检查完成")
        
    def audit_L2_content(self):
        """L2文档内容层审计"""
        print()
        print("🔍 执行L2文档内容层审计...")
        print()
        
        # 加载所有文档
        self.load_all_documents()
        
        # 2.1 职责驱动问题
        self.check_responsibility()
        
        # 2.2 索引完备性问题
        self.check_index_completeness()
        
        # 2.3 版本隔离问题
        self.check_version_isolation()
        
        # 2.4 文档代码对应问题
        self.check_document_code_correspondence()
        
    def load_all_documents(self):
        """加载所有文档"""
        print("  📄 加载所有文档...")
        
        md_files = list(self.layer9_path.rglob("*.md"))
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 提取YAML头部
                yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                yaml_header = yaml_match.group(1) if yaml_match else ""
                
                # 提取module_id
                module_id_match = re.search(r'module_id:\s*(.+)', yaml_header)
                module_id = module_id_match.group(1).strip() if module_id_match else None
                
                # 提取responsibility
                responsibility_match = re.search(r'responsibility:\s*\n(\s+-\s+.+\n)+', yaml_header)
                responsibility = responsibility_match.group(0) if responsibility_match else ""
                
                doc_info = {
                    "path": str(md_file.relative_to(self.layer9_path)),
                    "filename": md_file.name,
                    "content": content,
                    "yaml_header": yaml_header,
                    "module_id": module_id,
                    "responsibility": responsibility,
                    "size": len(content)
                }
                
                self.documents.append(doc_info)
                
                # 记录module_id
                if module_id:
                    self.module_ids[module_id].append(md_file.name)
                
                # 记录responsibility
                if responsibility:
                    self.responsibilities[responsibility].append(md_file.name)
                    
            except Exception as e:
                print(f"    ⚠️  加载文档失败: {md_file.name} - {e}")
        
        print(f"    ✅ 已加载 {len(self.documents)} 个文档")
        
    def check_responsibility(self):
        """检查职责驱动原则"""
        print("  🎯 检查职责驱动原则...")
        
        # 检查职责不清
        for doc in self.documents:
            if not doc["responsibility"] or doc["responsibility"].strip() == "":
                self.audit_results["L2_文档内容层"]["职责驱动问题"].append({
                    "问题类型": "职责不清",
                    "文件": doc["path"],
                    "严重程度": "高"
                })
        
        # 检查职责重叠
        responsibility_docs = defaultdict(list)
        for doc in self.documents:
            if doc["responsibility"]:
                # 提取职责关键词
                resp_lines = doc["responsibility"].split('\n')
                for line in resp_lines:
                    if line.strip().startswith('-'):
                        key = line.strip()
                        responsibility_docs[key].append(doc["filename"])
        
        for resp, docs in responsibility_docs.items():
            if len(docs) > 1:
                self.audit_results["L2_文档内容层"]["职责驱动问题"].append({
                    "问题类型": "职责重叠",
                    "职责": resp,
                    "文件列表": docs,
                    "严重程度": "高"
                })
        
        print("    ✅ 职责驱动检查完成")
        
    def check_index_completeness(self):
        """检查索引完备性"""
        print("  📇 检查索引完备性...")
        
        # 检查根目录INDEX.md
        root_index = self.layer9_path / "INDEX.md"
        if not root_index.exists():
            self.audit_results["L2_文档内容层"]["索引完备性问题"].append({
                "问题类型": "缺少根索引",
                "路径": str(self.layer9_path),
                "严重程度": "高"
            })
        else:
            # 检查索引是否包含所有活跃文档
            with open(root_index, 'r', encoding='utf-8-sig') as f:
                index_content = f.read()
            
            for doc in self.documents:
                if doc["filename"] != "INDEX.md" and "_archive" not in doc["path"]:
                    if doc["filename"] not in index_content:
                        self.audit_results["L2_文档内容层"]["索引完备性问题"].append({
                            "问题类型": "索引不完整",
                            "缺失文件": doc["filename"],
                            "严重程度": "中"
                        })
        
        print("    ✅ 索引完备性检查完成")
        
    def check_version_isolation(self):
        """检查版本隔离"""
        print("  📦 检查版本隔离...")
        
        # 检查重复文档
        content_hashes = defaultdict(list)
        for doc in self.documents:
            # 使用前500字符作为内容指纹
            content_hash = hash(doc["content"][:500])
            content_hashes[content_hash].append(doc["filename"])
        
        for content_hash, docs in content_hashes.items():
            if len(docs) > 1:
                self.audit_results["L2_文档内容层"]["版本隔离问题"].append({
                    "问题类型": "重复文档",
                    "文件列表": docs,
                    "严重程度": "高"
                })
        
        # 检查历史版本是否归档
        for doc in self.documents:
            if "_archive" not in doc["path"]:
                # 检查文件名中是否包含版本号
                if re.search(r'_v\d+|_V\d+', doc["filename"]):
                    self.audit_results["L2_文档内容层"]["版本隔离问题"].append({
                        "问题类型": "历史版本未归档",
                        "文件": doc["path"],
                        "严重程度": "中"
                    })
        
        print("    ✅ 版本隔离检查完成")
        
    def check_document_code_correspondence(self):
        """检查文档代码对应"""
        print("  💻 检查文档代码对应...")
        
        # 检查蓝图文档是否包含代码示例
        for doc in self.documents:
            if "BLUEPRINT" in doc["filename"]:
                # 检查是否包含代码块
                if "```" not in doc["content"]:
                    self.audit_results["L2_文档内容层"]["文档代码对应问题"].append({
                        "问题类型": "蓝图缺少代码示例",
                        "文件": doc["path"],
                        "严重程度": "中"
                    })
        
        print("    ✅ 文档代码对应检查完成")
        
    def audit_L3_standards(self):
        """L3专业标准层审计"""
        print()
        print("🔍 执行L3专业标准层审计...")
        print()
        
        # 3.1 五大原则问题
        self.check_five_principles()
        
        # 3.2 文档分类问题
        self.check_document_classification()
        
        # 3.3 编号体系问题
        self.check_numbering_system()
        
        # 3.4 文档质量问题
        self.check_document_quality()
        
    def check_five_principles(self):
        """检查五大原则符合性"""
        print("  ⭐ 检查五大原则符合性...")
        
        # 职责驱动原则
        for doc in self.documents:
            if not doc["responsibility"]:
                self.audit_results["L3_专业标准层"]["五大原则问题"].append({
                    "原则": "职责驱动",
                    "问题": "缺少职责定义",
                    "文件": doc["path"],
                    "严重程度": "高"
                })
        
        # 索引完备性原则
        root_index = self.layer9_path / "INDEX.md"
        if not root_index.exists():
            self.audit_results["L3_专业标准层"]["五大原则问题"].append({
                "原则": "索引完备",
                "问题": "缺少根索引文件",
                "严重程度": "高"
            })
        
        # 版本隔离原则
        for doc in self.documents:
            if "_archive" not in doc["path"]:
                if re.search(r'_v\d+|_V\d+', doc["filename"]):
                    self.audit_results["L3_专业标准层"]["五大原则问题"].append({
                        "原则": "版本隔离",
                        "问题": "历史版本未归档",
                        "文件": doc["path"],
                        "严重程度": "中"
                    })
        
        print("    ✅ 五大原则检查完成")
        
    def check_document_classification(self):
        """检查文档分类"""
        print("  📂 检查文档分类...")
        
        # 检查文档是否在正确的分类目录
        for doc in self.documents:
            if "BLUEPRINT" in doc["filename"]:
                # 蓝图文件应该在根目录或专门的蓝图目录
                if "_archive" in doc["path"]:
                    self.audit_results["L3_专业标准层"]["文档分类问题"].append({
                        "问题类型": "蓝图文件在归档目录",
                        "文件": doc["path"],
                        "严重程度": "低"
                    })
            
            if "AUDIT" in doc["filename"] or "GOVERNANCE" in doc["filename"]:
                # 审计文档应该在专门的审计目录或根目录
                pass  # 目前在根目录，符合规范
        
        print("    ✅ 文档分类检查完成")
        
    def check_numbering_system(self):
        """检查编号体系"""
        print("  🔢 检查编号体系...")
        
        # 检查module_id重复
        for module_id, docs in self.module_ids.items():
            if len(docs) > 1:
                self.audit_results["L3_专业标准层"]["编号体系问题"].append({
                    "问题类型": "module_id重复",
                    "module_id": module_id,
                    "文件列表": docs,
                    "严重程度": "高"
                })
        
        # 检查module_id缺失
        for doc in self.documents:
            if not doc["module_id"] and "_archive" not in doc["path"]:
                self.audit_results["L3_专业标准层"]["编号体系问题"].append({
                    "问题类型": "module_id缺失",
                    "文件": doc["path"],
                    "严重程度": "中"
                })
        
        print("    ✅ 编号体系检查完成")
        
    def check_document_quality(self):
        """检查文档质量"""
        print("  ✨ 检查文档质量...")
        
        for doc in self.documents:
            # 检查YAML头部缺失
            if not doc["yaml_header"]:
                self.audit_results["L3_专业标准层"]["文档质量问题"].append({
                    "问题类型": "YAML头部缺失",
                    "文件": doc["path"],
                    "严重程度": "高"
                })
            
            # 检查文档大小（过小可能内容不完整）
            if doc["size"] < 500 and "_archive" not in doc["path"]:
                self.audit_results["L3_专业标准层"]["文档质量问题"].append({
                    "问题类型": "文档内容过少",
                    "文件": doc["path"],
                    "文档大小": doc["size"],
                    "严重程度": "中"
                })
        
        print("    ✅ 文档质量检查完成")
        
    def generate_report(self):
        """生成审计报告"""
        print()
        print("=" * 80)
        print("审计报告生成")
        print("=" * 80)
        print()
        
        # 统计问题数量
        total_issues = 0
        high_issues = 0
        medium_issues = 0
        low_issues = 0
        
        for layer, categories in self.audit_results.items():
            for category, issues in categories.items():
                total_issues += len(issues)
                for issue in issues:
                    severity = issue.get("严重程度", "低")
                    if severity == "高":
                        high_issues += 1
                    elif severity == "中":
                        medium_issues += 1
                    else:
                        low_issues += 1
        
        print(f"📊 审计统计:")
        print(f"  - 审计文档数: {len(self.documents)}")
        print(f"  - 发现问题总数: {total_issues}")
        print(f"  - 高严重度问题: {high_issues}")
        print(f"  - 中严重度问题: {medium_issues}")
        print(f"  - 低严重度问题: {low_issues}")
        print()
        
        # 输出详细问题
        for layer, categories in self.audit_results.items():
            layer_issues = sum(len(issues) for issues in categories.values())
            if layer_issues > 0:
                print(f"\n{layer}:")
                for category, issues in categories.items():
                    if issues:
                        print(f"\n  {category}:")
                        for i, issue in enumerate(issues, 1):
                            severity = issue.get("严重程度", "低")
                            severity_icon = "🔴" if severity == "高" else "🟡" if severity == "中" else "🟢"
                            print(f"    {i}. {severity_icon} {issue.get('问题类型', '未知问题')}")
                            if "文件" in issue:
                                print(f"       文件: {issue['文件']}")
                            if "文件列表" in issue:
                                print(f"       文件列表: {', '.join(issue['文件列表'])}")
        
        # 保存报告
        report_path = self.layer9_path / f"LAYER9_DEEP_AUDIT_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                "audit_time": datetime.now().isoformat(),
                "audit_path": str(self.layer9_path),
                "documents_count": len(self.documents),
                "total_issues": total_issues,
                "high_issues": high_issues,
                "medium_issues": medium_issues,
                "low_issues": low_issues,
                "audit_results": self.audit_results
            }, f, indent=2, ensure_ascii=False)
        
        print()
        print(f"✅ 审计报告已保存: {report_path}")
        print()

if __name__ == "__main__":
    auditor = Layer9DeepAuditor()
    auditor.run_audit()
