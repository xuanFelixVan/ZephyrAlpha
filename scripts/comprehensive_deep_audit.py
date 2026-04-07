"""
全面深度审计脚本
用途：按照专业量化机构五大原则和三层审计标准，全面审计所有文档
创建时间：2026-04-07
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
from collections import defaultdict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

class ComprehensiveDeepAudit:
    def __init__(self):
        self.all_files = []
        self.all_dirs = []
        self.issues = {
            "L1_目录结构": [],
            "L1_文件命名": [],
            "L1_路径引用": [],
            "L2_职责驱动": [],
            "L2_索引完备性": [],
            "L2_版本隔离": [],
            "L3_五大原则": [],
            "L3_文档分类": [],
            "L3_编号体系": [],
            "L3_文档质量": []
        }
        self.file_hashes = {}
        self.duplicate_files = []
        self.responsibility_map = defaultdict(list)
        self.module_ids = {}
        
    def scan_all_files(self):
        print("扫描所有文件...")
        for root, dirs, files in os.walk(DOCS_DIR):
            root_path = Path(root)
            self.all_dirs.append(root_path)
            
            for file in files:
                if file.endswith('.md'):
                    file_path = root_path / file
                    self.all_files.append(file_path)
        
        print(f"发现 {len(self.all_files)} 个文档文件")
        print(f"发现 {len(self.all_dirs)} 个目录")
    
    def audit_l1_directory_structure(self):
        print("\n" + "=" * 80)
        print("L1 文件系统层审计 - 目录结构")
        print("=" * 80)
        
        sparse_dirs = []
        deep_dirs = []
        empty_dirs = []
        
        for dir_path in self.all_dirs:
            try:
                relative_path = dir_path.relative_to(DOCS_DIR)
                depth = len(relative_path.parts)
                
                md_files = list(dir_path.glob("*.md"))
                all_files = list(dir_path.glob("*"))
                all_subdirs = [f for f in all_files if f.is_dir()]
                
                if depth > 4:
                    deep_dirs.append({
                        "path": str(relative_path),
                        "depth": depth,
                        "file_count": len(md_files)
                    })
                    self.issues["L1_目录结构"].append({
                        "type": "目录层级过深",
                        "path": str(relative_path),
                        "severity": "medium",
                        "detail": f"深度{depth}层，建议不超过4层"
                    })
                
                if len(md_files) < 3 and len(all_subdirs) == 0:
                    sparse_dirs.append({
                        "path": str(relative_path),
                        "file_count": len(md_files)
                    })
                
                if len(all_files) == 0:
                    empty_dirs.append(str(relative_path))
                    self.issues["L1_目录结构"].append({
                        "type": "空目录",
                        "path": str(relative_path),
                        "severity": "low",
                        "detail": "目录为空，建议删除"
                    })
            
            except Exception as e:
                pass
        
        print(f"\n目录层级过深: {len(deep_dirs)}个")
        for d in deep_dirs[:10]:
            print(f"  - {d['path']} (深度{d['depth']})")
        
        print(f"\n稀疏目录: {len(sparse_dirs)}个")
        for d in sparse_dirs[:10]:
            print(f"  - {d['path']} ({d['file_count']}个文件)")
        
        print(f"\n空目录: {len(empty_dirs)}个")
    
    def audit_l1_file_naming(self):
        print("\n" + "=" * 80)
        print("L1 文件系统层审计 - 文件命名")
        print("=" * 80)
        
        old_architecture_files = []
        special_char_files = []
        inconsistent_naming = []
        
        for file_path in self.all_files:
            file_name = file_path.name
            
            if re.search(r'Layer\s*[0-8]', file_name, re.IGNORECASE):
                old_architecture_files.append(str(file_path.relative_to(DOCS_DIR)))
                self.issues["L1_文件命名"].append({
                    "type": "旧架构命名残留",
                    "path": str(file_path.relative_to(DOCS_DIR)),
                    "severity": "high",
                    "detail": f"文件名包含旧架构关键词: {file_name}"
                })
            
            if ' ' in file_name or re.search(r'[\u4e00-\u9fff]', file_name):
                special_char_files.append(str(file_path.relative_to(DOCS_DIR)))
        
        print(f"\n旧架构命名残留: {len(old_architecture_files)}个")
        for f in old_architecture_files[:10]:
            print(f"  - {f}")
        
        print(f"\n特殊字符文件: {len(special_char_files)}个")
    
    def audit_l1_path_references(self):
        print("\n" + "=" * 80)
        print("L1 文件系统层审计 - 路径引用")
        print("=" * 80)
        
        broken_links = []
        redundant_paths = []
        
        for file_path in self.all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                relative_path = file_path.relative_to(DOCS_DIR)
                
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                
                for link_text, link_path in links:
                    if link_path.startswith('http') or link_path.startswith('#'):
                        continue
                    
                    if link_path.count('../') > 3:
                        redundant_paths.append({
                            "file": str(relative_path),
                            "link": link_path
                        })
                    
                    if not link_path.startswith('/'):
                        target_path = (file_path.parent / link_path).resolve()
                        if not target_path.exists():
                            broken_links.append({
                                "file": str(relative_path),
                                "link": link_path,
                                "text": link_text
                            })
            
            except Exception as e:
                pass
        
        print(f"\n死链接: {len(broken_links)}个")
        for link in broken_links[:10]:
            print(f"  - {link['file']} -> {link['link']}")
        
        print(f"\n路径冗余: {len(redundant_paths)}个")
        
        if broken_links:
            self.issues["L1_路径引用"].append({
                "type": "死链接",
                "count": len(broken_links),
                "severity": "medium",
                "detail": f"发现{len(broken_links)}个死链接"
            })
    
    def audit_l2_responsibility(self):
        print("\n" + "=" * 80)
        print("L2 文档内容层审计 - 职责驱动")
        print("=" * 80)
        
        unclear_responsibility = []
        overlapping_responsibility = []
        
        for file_path in self.all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    
                    resp_match = re.search(r'responsibility:\s*\n?\s*-\s*(.+?)(?:\n|$)', yaml_content, re.MULTILINE)
                    if resp_match:
                        responsibility = resp_match.group(1).strip()
                        
                        if len(responsibility) < 10 or responsibility in ['扩展功能、辅助模块', '核心功能、主模块']:
                            unclear_responsibility.append({
                                "path": str(file_path.relative_to(DOCS_DIR)),
                                "responsibility": responsibility
                            })
                        
                        self.responsibility_map[responsibility].append(str(file_path.relative_to(DOCS_DIR)))
            
            except Exception as e:
                pass
        
        for resp, files in self.responsibility_map.items():
            if len(files) > 3 and resp not in ['扩展功能、辅助模块', '核心功能、主模块']:
                overlapping_responsibility.append({
                    "responsibility": resp,
                    "files": files
                })
        
        print(f"\n职责不清: {len(unclear_responsibility)}个")
        for item in unclear_responsibility[:10]:
            print(f"  - {item['path']}: {item['responsibility']}")
        
        print(f"\n职责重叠: {len(overlapping_responsibility)}组")
        for item in overlapping_responsibility[:5]:
            print(f"  - 职责'{item['responsibility']}'出现在{len(item['files'])}个文件")
        
        if unclear_responsibility:
            self.issues["L2_职责驱动"].append({
                "type": "职责不清",
                "count": len(unclear_responsibility),
                "severity": "high",
                "detail": f"发现{len(unclear_responsibility)}个职责描述不清的文档"
            })
        
        if overlapping_responsibility:
            self.issues["L2_职责驱动"].append({
                "type": "职责重叠",
                "count": len(overlapping_responsibility),
                "severity": "high",
                "detail": f"发现{len(overlapping_responsibility)}组职责重叠"
            })
    
    def audit_l2_index_completeness(self):
        print("\n" + "=" * 80)
        print("L2 文档内容层审计 - 索引完备性")
        print("=" * 80)
        
        missing_index = []
        incomplete_index = []
        
        for dir_path in self.all_dirs:
            try:
                relative_path = dir_path.relative_to(DOCS_DIR)
                
                index_file = dir_path / "INDEX.md"
                if not index_file.exists():
                    index_file = dir_path / "index.md"
                
                md_files = [f for f in dir_path.glob("*.md") if f.name.lower() not in ['index.md', 'readme.md']]
                
                if len(md_files) > 0 and not index_file.exists():
                    missing_index.append(str(relative_path))
                    self.issues["L2_索引完备性"].append({
                        "type": "缺少INDEX.md",
                        "path": str(relative_path),
                        "severity": "medium",
                        "detail": f"目录有{len(md_files)}个文档但缺少INDEX.md"
                    })
            
            except Exception as e:
                pass
        
        print(f"\n缺少INDEX.md的目录: {len(missing_index)}个")
        for path in missing_index[:10]:
            print(f"  - {path}")
    
    def audit_l2_version_isolation(self):
        print("\n" + "=" * 80)
        print("L2 文档内容层审计 - 版本隔离")
        print("=" * 80)
        
        print("计算文件哈希值...")
        for file_path in self.all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content_hash = hashlib.md5(content.encode()).hexdigest()
                
                if content_hash in self.file_hashes:
                    self.duplicate_files.append({
                        "file1": self.file_hashes[content_hash],
                        "file2": str(file_path.relative_to(DOCS_DIR)),
                        "hash": content_hash
                    })
                else:
                    self.file_hashes[content_hash] = str(file_path.relative_to(DOCS_DIR))
            
            except Exception as e:
                pass
        
        print(f"\n重复文档: {len(self.duplicate_files)}对")
        for dup in self.duplicate_files[:5]:
            print(f"  - {dup['file1']}")
            print(f"    {dup['file2']}")
        
        if self.duplicate_files:
            self.issues["L2_版本隔离"].append({
                "type": "重复文档",
                "count": len(self.duplicate_files),
                "severity": "high",
                "detail": f"发现{len(self.duplicate_files)}对重复文档"
            })
    
    def audit_l3_module_id(self):
        print("\n" + "=" * 80)
        print("L3 专业标准层审计 - 编号体系")
        print("=" * 80)
        
        missing_module_id = []
        duplicate_module_id = []
        
        for file_path in self.all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    
                    module_match = re.search(r'module_id:\s*(.+?)(?:\n|$)', yaml_content, re.MULTILINE)
                    if module_match:
                        module_id = module_match.group(1).strip()
                        
                        if module_id in self.module_ids:
                            duplicate_module_id.append({
                                "module_id": module_id,
                                "file1": self.module_ids[module_id],
                                "file2": str(file_path.relative_to(DOCS_DIR))
                            })
                        else:
                            self.module_ids[module_id] = str(file_path.relative_to(DOCS_DIR))
                    else:
                        missing_module_id.append(str(file_path.relative_to(DOCS_DIR)))
            
            except Exception as e:
                pass
        
        print(f"\n缺少Module ID: {len(missing_module_id)}个")
        print(f"重复Module ID: {len(duplicate_module_id)}个")
        
        for dup in duplicate_module_id[:5]:
            print(f"  - {dup['module_id']}:")
            print(f"    {dup['file1']}")
            print(f"    {dup['file2']}")
        
        if duplicate_module_id:
            self.issues["L3_编号体系"].append({
                "type": "Module ID重复",
                "count": len(duplicate_module_id),
                "severity": "high",
                "detail": f"发现{len(duplicate_module_id)}个重复的Module ID"
            })
    
    def generate_report(self):
        print("\n" + "=" * 80)
        print("生成审计报告")
        print("=" * 80)
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": len(self.all_files),
                "total_dirs": len(self.all_dirs),
                "total_issues": total_issues,
                "compliance_rate": round((len(self.all_files) - total_issues) / len(self.all_files) * 100, 2) if self.all_files else 0
            },
            "issues": self.issues,
            "duplicate_files": self.duplicate_files[:20],
            "overlapping_responsibility": [
                {
                    "responsibility": resp,
                    "file_count": len(files),
                    "files": files[:5]
                }
                for resp, files in self.responsibility_map.items()
                if len(files) > 3 and resp not in ['扩展功能、辅助模块', '核心功能、主模块']
            ][:10]
        }
        
        report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / f"comprehensive_deep_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n审计报告已保存至: {report_path}")
        
        print("\n" + "=" * 80)
        print("审计摘要")
        print("=" * 80)
        print(f"总文件数: {len(self.all_files)}")
        print(f"总目录数: {len(self.all_dirs)}")
        print(f"总问题数: {total_issues}")
        print(f"合规率: {report['summary']['compliance_rate']}%")
        
        print("\n问题分布:")
        for category, issues in self.issues.items():
            if issues:
                print(f"  {category}: {len(issues)}个问题")
        
        return report
    
    def run(self):
        print("=" * 80)
        print("全面深度审计")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        self.scan_all_files()
        self.audit_l1_directory_structure()
        self.audit_l1_file_naming()
        self.audit_l1_path_references()
        self.audit_l2_responsibility()
        self.audit_l2_index_completeness()
        self.audit_l2_version_isolation()
        self.audit_l3_module_id()
        
        report = self.generate_report()
        
        print("\n" + "=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return report

if __name__ == "__main__":
    auditor = ComprehensiveDeepAudit()
    auditor.run()
