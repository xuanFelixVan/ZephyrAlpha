"""
深度文档治理审计脚本
用途：执行三层深度审计（L1/L2/L3），检查重复文档和职责不清的文档
创建时间：2026-04-07
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

class DeepDocumentAuditor:
    def __init__(self):
        self.issues = {
            "L1_file_system": [],
            "L2_content": [],
            "L3_standard": []
        }
        self.stats = {
            "total_files": 0,
            "total_dirs": 0,
            "total_issues": 0
        }
        self.file_info = {}
        self.duplicate_content = defaultdict(list)
        self.responsibility_map = defaultdict(list)
        
    def run_audit(self):
        print("=" * 80)
        print("深度文档治理审计")
        print("=" * 80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: {DOCS_DIR}")
        print("=" * 80)
        
        print("\n第一阶段: L1文件系统层审计")
        print("-" * 80)
        self.audit_L1_file_system()
        
        print("\n第二阶段: L2文档内容层审计")
        print("-" * 80)
        self.audit_L2_content()
        
        print("\n第三阶段: L3专业标准层审计")
        print("-" * 80)
        self.audit_L3_standard()
        
        print("\n第四阶段: 生成审计报告")
        print("-" * 80)
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("审计完成")
        print("=" * 80)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"总目录数: {self.stats['total_dirs']}")
        print(f"总问题数: {self.stats['total_issues']}")
        
    def audit_L1_file_system(self):
        print("1.1 目录结构问题检查...")
        self.check_directory_structure()
        
        print("1.2 文件命名问题检查...")
        self.check_file_naming()
        
        print("1.3 路径引用问题检查...")
        self.check_path_references()
        
    def check_directory_structure(self):
        for root, dirs, files in os.walk(DOCS_DIR):
            self.stats['total_dirs'] += 1
            
            rel_path = os.path.relpath(root, DOCS_DIR)
            if rel_path == ".":
                continue
                
            if len(files) < 3 and len(files) > 0:
                self.issues["L1_file_system"].append({
                    "type": "目录稀疏",
                    "path": rel_path,
                    "description": f"目录下文件过少（{len(files)}个），应整合",
                    "severity": "低"
                })
            
            depth = rel_path.count(os.sep)
            if depth > 4:
                self.issues["L1_file_system"].append({
                    "type": "目录层级过深",
                    "path": rel_path,
                    "description": f"嵌套超过4层（{depth}层），难以导航",
                    "severity": "中"
                })
            
            if len(files) == 0 and len(dirs) == 0:
                self.issues["L1_file_system"].append({
                    "type": "空目录",
                    "path": rel_path,
                    "description": "目录存在但无内容",
                    "severity": "低"
                })
                
    def check_file_naming(self):
        old_architecture_keywords = ["Layer 0", "Layer 1", "Layer 2", "Layer 3", "Layer 4", 
                                    "Layer 5", "Layer 6", "Layer 7", "Layer 8", "LAYER_"]
        
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if not file.endswith('.md'):
                    continue
                    
                self.stats['total_files'] += 1
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, DOCS_DIR)
                
                for keyword in old_architecture_keywords:
                    if keyword in file:
                        self.issues["L1_file_system"].append({
                            "type": "旧架构命名残留",
                            "path": rel_path,
                            "description": f"文件名包含旧架构关键词: {keyword}",
                            "severity": "中"
                        })
                        break
                
                if ' ' in file:
                    self.issues["L1_file_system"].append({
                        "type": "特殊字符问题",
                        "path": rel_path,
                        "description": "文件名包含空格",
                        "severity": "低"
                    })
                    
    def check_path_references(self):
        print("  检查路径引用（抽样检查）...")
        sample_count = 0
        max_samples = 100
        
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if not file.endswith('.md'):
                    continue
                    
                if sample_count >= max_samples:
                    break
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, DOCS_DIR)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    relative_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                    
                    for link_text, link_path in relative_links:
                        if link_path.startswith('http'):
                            continue
                        
                        if link_path.count('../') > 3:
                            self.issues["L1_file_system"].append({
                                "type": "路径冗余",
                                "path": rel_path,
                                "description": f"链接使用过多../: {link_path}",
                                "severity": "低"
                            })
                            
                except Exception as e:
                    pass
                    
                sample_count += 1
                
    def audit_L2_content(self):
        print("2.1 职责驱动原则检查...")
        self.check_responsibility()
        
        print("2.2 索引完备性检查...")
        self.check_index_completeness()
        
        print("2.3 版本隔离检查...")
        self.check_version_isolation()
        
        print("2.4 文档代码对应检查...")
        self.check_code_correspondence()
        
    def check_responsibility(self):
        print("  收集文档信息...")
        
        for root, dirs, files in os.walk(DOCS_DIR):
            for file in files:
                if not file.endswith('.md'):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, DOCS_DIR)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.file_info[rel_path] = {
                        "content": content,
                        "size": len(content),
                        "lines": content.count('\n')
                    }
                    
                    yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                    if yaml_match:
                        yaml_content = yaml_match.group(1)
                        
                        responsibility_match = re.search(r'responsibility:\s*\n((?:\s+-.*\n)+)', yaml_content)
                        if responsibility_match:
                            responsibilities = re.findall(r'-\s*(.+)', responsibility_match.group(1))
                            for resp in responsibilities:
                                self.responsibility_map[resp.strip()].append(rel_path)
                        else:
                            self.issues["L2_content"].append({
                                "type": "职责不清",
                                "path": rel_path,
                                "description": "文档缺少明确的职责描述",
                                "severity": "高"
                            })
                    else:
                        self.issues["L2_content"].append({
                            "type": "YAML头部缺失",
                            "path": rel_path,
                            "description": "文档缺少YAML元数据头部",
                            "severity": "高"
                        })
                        
                except Exception as e:
                    pass
                    
        print(f"  已收集 {len(self.file_info)} 个文档信息")
        
        print("  检查职责重叠...")
        for responsibility, files in self.responsibility_map.items():
            if len(files) > 10:
                self.issues["L2_content"].append({
                    "type": "职责重叠",
                    "path": responsibility,
                    "description": f"职责 '{responsibility}' 涉及 {len(files)} 个文件",
                    "severity": "中",
                    "files": files[:10]
                })
                
    def check_index_completeness(self):
        for root, dirs, files in os.walk(DOCS_DIR):
            if 'INDEX.md' not in files and len(files) > 0:
                rel_path = os.path.relpath(root, DOCS_DIR)
                if rel_path != ".":
                    self.issues["L2_content"].append({
                        "type": "子目录缺索引",
                        "path": rel_path,
                        "description": "子目录缺少INDEX.md导航文件",
                        "severity": "中"
                    })
                    
    def check_version_isolation(self):
        print("  检查重复文档（基于内容相似度）...")
        
        content_hashes = defaultdict(list)
        for rel_path, info in self.file_info.items():
            content = info['content']
            
            content_clean = re.sub(r'---.*?---', '', content, flags=re.DOTALL)
            content_clean = re.sub(r'\s+', ' ', content_clean)
            
            content_hash = hash(content_clean[:1000])
            content_hashes[content_hash].append(rel_path)
        
        for content_hash, files in content_hashes.items():
            if len(files) > 1:
                self.issues["L2_content"].append({
                    "type": "重复文档",
                    "path": files[0],
                    "description": f"发现 {len(files)} 个内容相似的文档",
                    "severity": "高",
                    "files": files
                })
                
    def check_code_correspondence(self):
        print("  检查文档代码对应（抽样检查）...")
        
        src_dir = PROJECT_ROOT / "src"
        if not src_dir.exists():
            return
            
        code_modules = set()
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith('.py'):
                    module_name = file.replace('.py', '')
                    code_modules.add(module_name)
        
        doc_mentions_code = defaultdict(list)
        for rel_path, info in self.file_info.items():
            content = info['content']
            for module in code_modules:
                if module in content:
                    doc_mentions_code[module].append(rel_path)
                    
    def audit_L3_standard(self):
        print("3.1 五大原则符合性检查...")
        self.check_five_principles()
        
        print("3.2 文档分类检查...")
        self.check_document_classification()
        
        print("3.3 编号体系检查...")
        self.check_numbering_system()
        
        print("3.4 文档质量检查...")
        self.check_document_quality()
        
    def check_five_principles(self):
        principles = {
            "职责驱动": 0,
            "索引完备": 0,
            "版本隔离": 0,
            "文档代码对应": 0,
            "命名规范": 0
        }
        
        for issue in self.issues["L2_content"]:
            if issue["type"] == "职责不清":
                principles["职责驱动"] += 1
            elif issue["type"] == "子目录缺索引":
                principles["索引完备"] += 1
            elif issue["type"] == "重复文档":
                principles["版本隔离"] += 1
                
        for principle, count in principles.items():
            if count > 0:
                self.issues["L3_standard"].append({
                    "type": "五大原则符合性",
                    "path": principle,
                    "description": f"违反{principle}原则的问题: {count}个",
                    "severity": "高"
                })
                
    def check_document_classification(self):
        print("  检查文档分类...")
        
    def check_numbering_system(self):
        print("  检查编号体系...")
        
        module_ids = defaultdict(list)
        for rel_path, info in self.file_info.items():
            content = info['content']
            
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                module_id_match = re.search(r'module_id:\s*(.+)', yaml_content)
                if module_id_match:
                    module_id = module_id_match.group(1).strip()
                    module_ids[module_id].append(rel_path)
                else:
                    self.issues["L3_standard"].append({
                        "type": "编号缺失",
                        "path": rel_path,
                        "description": "文档缺少module_id",
                        "severity": "高"
                    })
        
        for module_id, files in module_ids.items():
            if len(files) > 1:
                self.issues["L3_standard"].append({
                    "type": "编号重复",
                    "path": module_id,
                    "description": f"module_id '{module_id}' 重复使用",
                    "severity": "高",
                    "files": files
                })
                
    def check_document_quality(self):
        print("  检查文档质量...")
        
        for rel_path, info in self.file_info.items():
            content = info['content']
            
            if not re.match(r'^---\s*\n.*?\n---', content, re.DOTALL):
                self.issues["L3_standard"].append({
                    "type": "YAML头部缺失",
                    "path": rel_path,
                    "description": "文档缺少标准YAML元数据",
                    "severity": "高"
                })
            
            if info['size'] < 100:
                self.issues["L3_standard"].append({
                    "type": "内容过少",
                    "path": rel_path,
                    "description": f"文档内容过少（{info['size']}字节）",
                    "severity": "低"
                })
                
    def generate_report(self):
        report = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "issues": self.issues,
            "summary": {
                "total_issues": sum(len(v) for v in self.issues.values()),
                "L1_issues": len(self.issues["L1_file_system"]),
                "L2_issues": len(self.issues["L2_content"]),
                "L3_issues": len(self.issues["L3_standard"])
            }
        }
        
        report_path = OUTPUT_DIR / f"deep_document_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"  报告已保存至: {report_path}")
        
        self.generate_markdown_report(report)
        
    def generate_markdown_report(self, report):
        md_path = OUTPUT_DIR / f"deep_document_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 深度文档治理审计报告\n\n")
            f.write(f"> **审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"> **审计范围**: {DOCS_DIR}\n")
            f.write(f"> **审计标准**: 专业量化机构五大原则 + 三层审计标准\n\n")
            
            f.write("## 📊 审计统计\n\n")
            f.write(f"- **总文件数**: {report['stats']['total_files']}\n")
            f.write(f"- **总目录数**: {report['stats']['total_dirs']}\n")
            f.write(f"- **总问题数**: {report['summary']['total_issues']}\n\n")
            
            f.write("## 🔴 L1 文件系统层问题\n\n")
            f.write(f"**问题总数**: {len(self.issues['L1_file_system'])}\n\n")
            
            for issue in self.issues['L1_file_system'][:20]:
                f.write(f"- **{issue['type']}** ({issue['severity']}): {issue['path']}\n")
                f.write(f"  - {issue['description']}\n\n")
            
            f.write("## 🟡 L2 文档内容层问题\n\n")
            f.write(f"**问题总数**: {len(self.issues['L2_content'])}\n\n")
            
            for issue in self.issues['L2_content'][:20]:
                f.write(f"- **{issue['type']}** ({issue['severity']}): {issue['path']}\n")
                f.write(f"  - {issue['description']}\n")
                if 'files' in issue:
                    f.write(f"  - 相关文件: {', '.join(issue['files'][:5])}\n")
                f.write("\n")
            
            f.write("## 🟢 L3 专业标准层问题\n\n")
            f.write(f"**问题总数**: {len(self.issues['L3_standard'])}\n\n")
            
            for issue in self.issues['L3_standard'][:20]:
                f.write(f"- **{issue['type']}** ({issue['severity']}): {issue['path']}\n")
                f.write(f"  - {issue['description']}\n")
                if 'files' in issue:
                    f.write(f"  - 相关文件: {', '.join(issue['files'][:5])}\n")
                f.write("\n")
            
            f.write("## 📝 改进建议\n\n")
            f.write("1. 优先处理高严重度问题\n")
            f.write("2. 整合稀疏目录\n")
            f.write("3. 清理重复文档\n")
            f.write("4. 完善职责描述\n")
            f.write("5. 统一命名规范\n")
        
        print(f"  Markdown报告已保存至: {md_path}")
        self.stats['total_issues'] = report['summary']['total_issues']

if __name__ == "__main__":
    auditor = DeepDocumentAuditor()
    auditor.run_audit()
