# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
组合优化层深度审计脚本 V7
用途：执行三层深度审计，检查重复文档和职责不清问题
创建时间：2026-04-07
"""

import re
import hashlib
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
from collections import defaultdict

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")
CONSTRUCTION_DOCS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS")


class Layer6DeepAuditorV7:
    """组合优化层深度审计器 V7"""
    
    def __init__(self):
        self.l1_issues = []  # 文件系统层问题
        self.l2_issues = []  # 文档内容层问题
        self.l3_issues = []  # 专业标准层问题
        self.documents = {}  # 文档信息存储
        self.duplicates = defaultdict(list)  # 重复文档检测
        self.responsibility_map = defaultdict(list)  # 职责映射
        self.module_id_map = defaultdict(list)  # module_id映射
        self.content_hashes = defaultdict(list)  # 内容哈希映射
    
    def read_document(self, filepath: Path) -> str:
        """读取文档内容"""
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        return ""
    
    def extract_yaml_header(self, content: str) -> dict:
        """提取YAML头部"""
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not yaml_match:
            return {}
        
        yaml_content = yaml_match.group(1)
        yaml_dict = {}
        
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                yaml_dict[key.strip()] = value.strip().strip('"\'')
        
        return yaml_dict
    
    def extract_title(self, content: str) -> str:
        """提取文档标题"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else ""
    
    def extract_core_functions(self, content: str) -> List[str]:
        """提取核心功能"""
        functions = []
        
        # 提取职责描述
        patterns = [
            r'核心职责[：:]\s*(.+?)(?:\n\n|\n#)',
            r'单一职责[：:]\s*(.+?)(?:\n\n|\n#)',
            r'功能描述[：:]\s*(.+?)(?:\n\n|\n#)',
            r'核心功能[：:]\s*(.+?)(?:\n\n|\n#)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                functions.append(match.group(1).strip())
        
        return functions
    
    def calculate_content_hash(self, content: str) -> str:
        """计算内容哈希"""
        # 移除YAML头部和空白字符
        content_no_yaml = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        content_normalized = re.sub(r'\s+', '', content_no_yaml)
        return hashlib.md5(content_normalized.encode('utf-8')).hexdigest()
    
    def check_l1_filesystem(self):
        """L1文件系统层审计"""
        print("="*80)
        print("L1 文件系统层审计")
        print("="*80)
        
        # 1.1 目录结构问题
        print("\n1.1 目录结构问题检查...")
        
        # 检查目录漂移
        expected_dirs = {'01_BLUEPRINTS', '02_IMPLEMENTATION_GUIDES', '03_OPERATION_MANUALS', 
                        '05_DESIGN_DOCS', '06_CHECKLISTS'}
        actual_dirs = set()
        
        for item in CONSTRUCTION_DOCS_DIR.iterdir():
            if item.is_dir():
                actual_dirs.add(item.name)
                file_count = len(list(item.glob("**/*.md")))
                
                # 检查稀疏目录
                if file_count < 3 and item.name != '06_CHECKLISTS':
                    self.l1_issues.append({
                        "type": "目录稀疏",
                        "severity": "P2",
                        "description": f"目录 {item.name} 文件数过少({file_count}个)",
                        "path": str(item)
                    })
        
        # 检查漂移目录
        drift_dirs = actual_dirs - expected_dirs
        if drift_dirs:
            for dir_name in drift_dirs:
                self.l1_issues.append({
                    "type": "目录漂移",
                    "severity": "P2",
                    "description": f"目录 {dir_name} 不符合架构设计",
                    "path": str(CONSTRUCTION_DOCS_DIR / dir_name)
                })
        
        # 1.2 文件命名问题
        print("1.2 文件命名问题检查...")
        
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            filename = filepath.name
            
            # 检查命名规范
            if not re.match(r'^[A-Z_]+_BLUEPRINT\.md$', filename) and filename != "INDEX.md":
                self.l1_issues.append({
                    "type": "命名不规范",
                    "severity": "P2",
                    "description": f"文件命名不符合规范: {filename}",
                    "path": str(filepath)
                })
        
        # 1.3 路径引用问题
        print("1.3 路径引用问题检查...")
        
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            content = self.read_document(filepath)
            if not content:
                continue
            
            # 检查死链接
            links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
            for text, link in links:
                if link.startswith('http') or link.startswith('#'):
                    continue
                
                if link.startswith('../'):
                    target_path = filepath.parent.parent / link.replace('../', '')
                else:
                    target_path = filepath.parent / link
                
                if not target_path.exists():
                    self.l1_issues.append({
                        "type": "死链接",
                        "severity": "P1",
                        "description": f"死链接: [{text}]({link})",
                        "path": str(filepath)
                    })
        
        print(f"✅ L1层审计完成，发现 {len(self.l1_issues)} 个问题")
    
    def check_l2_content(self):
        """L2文档内容层审计"""
        print("\n" + "="*80)
        print("L2 文档内容层审计")
        print("="*80)
        
        # 收集所有文档信息
        print("\n收集文档信息...")
        
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            content = self.read_document(filepath)
            if not content:
                continue
            
            yaml_header = self.extract_yaml_header(content)
            title = self.extract_title(content)
            core_functions = self.extract_core_functions(content)
            content_hash = self.calculate_content_hash(content)
            
            doc_info = {
                "filepath": filepath,
                "filename": filepath.name,
                "title": title,
                "module_id": yaml_header.get('module_id', ''),
                "layer": yaml_header.get('layer', ''),
                "core_functions": core_functions,
                "content_hash": content_hash,
                "yaml_header": yaml_header
            }
            
            self.documents[filepath.name] = doc_info
            
            # 构建映射
            if yaml_header.get('module_id'):
                self.module_id_map[yaml_header['module_id']].append(filepath.name)
            
            if core_functions:
                for func in core_functions:
                    self.responsibility_map[func].append(filepath.name)
            
            self.content_hashes[content_hash].append(filepath.name)
        
        # 2.1 职责驱动原则问题
        print("2.1 职责驱动原则检查...")
        
        # 检查职责重叠
        for func, docs in self.responsibility_map.items():
            if len(docs) > 1:
                # 检查是否是真正的重叠
                similar_docs = []
                for doc1 in docs:
                    for doc2 in docs:
                        if doc1 < doc2:
                            doc1_info = self.documents.get(doc1, {})
                            doc2_info = self.documents.get(doc2, {})
                            
                            # 检查标题相似度
                            title1 = doc1_info.get('title', '')
                            title2 = doc2_info.get('title', '')
                            
                            if title1 and title2:
                                # 简单的相似度检查
                                words1 = set(title1.split())
                                words2 = set(title2.split())
                                similarity = len(words1 & words2) / max(len(words1 | words2), 1)
                                
                                if similarity > 0.5:
                                    similar_docs.append((doc1, doc2, similarity))
                
                if similar_docs:
                    for doc1, doc2, sim in similar_docs:
                        self.l2_issues.append({
                            "type": "职责重叠",
                            "severity": "P0",
                            "description": f"文档 {doc1} 和 {doc2} 职责相似度 {sim:.1%}",
                            "path": str(BLUEPRINTS_DIR / doc1)
                        })
        
        # 2.2 索引完备性问题
        print("2.2 索引完备性检查...")
        
        # 检查INDEX.md是否包含所有文档
        index_path = BLUEPRINTS_DIR / "INDEX.md"
        if index_path.exists():
            index_content = self.read_document(index_path)
            
            for doc_name in self.documents.keys():
                if doc_name not in index_content:
                    self.l2_issues.append({
                        "type": "索引不完整",
                        "severity": "P1",
                        "description": f"文档 {doc_name} 未在INDEX.md中索引",
                        "path": str(index_path)
                    })
        
        # 2.3 版本隔离问题
        print("2.3 版本隔离检查...")
        
        # 检查重复文档（基于内容哈希）
        for content_hash, docs in self.content_hashes.items():
            if len(docs) > 1:
                self.l2_issues.append({
                    "type": "重复文档",
                    "severity": "P0",
                    "description": f"文档 {', '.join(docs)} 内容完全相同",
                    "path": str(BLUEPRINTS_DIR / docs[0])
                })
        
        # 检查module_id重复
        for module_id, docs in self.module_id_map.items():
            if len(docs) > 1:
                self.l2_issues.append({
                    "type": "module_id重复",
                    "severity": "P1",
                    "description": f"module_id {module_id} 被多个文档使用: {', '.join(docs)}",
                    "path": str(BLUEPRINTS_DIR / docs[0])
                })
        
        # 2.4 文档代码对应问题
        print("2.4 文档代码对应检查...")
        
        # 检查变更记录
        for doc_name, doc_info in self.documents.items():
            content = self.read_document(doc_info['filepath'])
            
            if '变更历史' not in content and '版本历史' not in content:
                self.l2_issues.append({
                    "type": "变更记录缺失",
                    "severity": "P2",
                    "description": f"文档 {doc_name} 缺少变更历史记录",
                    "path": str(doc_info['filepath'])
                })
        
        print(f"✅ L2层审计完成，发现 {len(self.l2_issues)} 个问题")
    
    def check_l3_standards(self):
        """L3专业标准层审计"""
        print("\n" + "="*80)
        print("L3 专业标准层审计")
        print("="*80)
        
        # 3.1 五大原则符合性问题
        print("\n3.1 五大原则符合性检查...")
        
        for doc_name, doc_info in self.documents.items():
            yaml_header = doc_info['yaml_header']
            
            # 检查YAML头部完整性
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
            missing_fields = [f for f in required_fields if f not in yaml_header]
            
            if missing_fields:
                self.l3_issues.append({
                    "type": "YAML字段缺失",
                    "severity": "P2",
                    "description": f"文档 {doc_name} 缺少字段: {', '.join(missing_fields)}",
                    "path": str(doc_info['filepath'])
                })
            
            # 检查Layer定位
            if not yaml_header.get('layer'):
                self.l3_issues.append({
                    "type": "Layer定位缺失",
                    "severity": "P1",
                    "description": f"文档 {doc_name} 缺少Layer定位",
                    "path": str(doc_info['filepath'])
                })
        
        # 3.2 文档分类问题
        print("3.2 文档分类检查...")
        
        # 检查文档是否在正确的Layer
        for doc_name, doc_info in self.documents.items():
            layer = doc_info.get('layer', '')
            filename = doc_name.upper()
            
            # 基于文件名推断应该的Layer
            expected_layer = None
            if 'DATA' in filename:
                expected_layer = 'Layer 1'
            elif 'ALPHA' in filename or 'FACTOR' in filename:
                expected_layer = 'Layer 2'
            elif 'STRATEGY' in filename:
                expected_layer = 'Layer 3'
            elif 'AI' in filename or 'MACHINE' in filename:
                expected_layer = 'Layer 4'
            elif 'PORTFOLIO' in filename or 'OPTIMIZATION' in filename or 'REBALANCING' in filename:
                expected_layer = 'Layer 6'
            elif 'RISK' in filename:
                expected_layer = 'Layer 7'
            elif 'EXECUTION' in filename or 'TRADING' in filename:
                expected_layer = 'Layer 8'
            elif 'MONITORING' in filename:
                expected_layer = 'Layer 9'
            
            if expected_layer and expected_layer not in layer:
                self.l3_issues.append({
                    "type": "Layer定位不准确",
                    "severity": "P1",
                    "description": f"文档 {doc_name} Layer定位 {layer} 可能不准确，建议 {expected_layer}",
                    "path": str(doc_info['filepath'])
                })
        
        # 3.3 编号体系问题
        print("3.3 编号体系检查...")
        
        for doc_name, doc_info in self.documents.items():
            module_id = doc_info.get('module_id', '')
            
            # 检查module_id格式
            if module_id and not re.match(r'^[A-Z_]+_\d{3}$', module_id):
                self.l3_issues.append({
                    "type": "module_id不规范",
                    "severity": "P2",
                    "description": f"文档 {doc_name} 的module_id {module_id} 不符合规范",
                    "path": str(doc_info['filepath'])
                })
        
        # 3.4 文档质量问题
        print("3.4 文档质量检查...")
        
        for doc_name, doc_info in self.documents.items():
            content = self.read_document(doc_info['filepath'])
            
            # 检查一级标题
            if not re.search(r'^#\s+[^#]', content, re.MULTILINE):
                self.l3_issues.append({
                    "type": "主标题缺失",
                    "severity": "P2",
                    "description": f"文档 {doc_name} 缺少主标题",
                    "path": str(doc_info['filepath'])
                })
            
            # 检查文档治理章节
            if '文档治理' not in content:
                self.l3_issues.append({
                    "type": "文档治理章节缺失",
                    "severity": "P2",
                    "description": f"文档 {doc_name} 缺少文档治理章节",
                    "path": str(doc_info['filepath'])
                })
        
        print(f"✅ L3层审计完成，发现 {len(self.l3_issues)} 个问题")
    
    def generate_report(self) -> str:
        """生成审计报告"""
        report = []
        report.append("# 组合优化层深度审计报告 V7")
        report.append("")
        report.append(f"**审计日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**审计范围**: {BLUEPRINTS_DIR}")
        report.append(f"**审计文档数**: {len(self.documents)}")
        report.append(f"**Git备份分支**: backup/layer6-deep-audit-v7-20260407")
        report.append("")
        report.append("---")
        report.append("")
        
        # 统计
        total_issues = len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)
        p0_issues = len([i for i in self.l1_issues + self.l2_issues + self.l3_issues if i['severity'] == 'P0'])
        p1_issues = len([i for i in self.l1_issues + self.l2_issues + self.l3_issues if i['severity'] == 'P1'])
        p2_issues = len([i for i in self.l1_issues + self.l2_issues + self.l3_issues if i['severity'] == 'P2'])
        
        report.append("## 📊 审计统计")
        report.append("")
        report.append(f"- **总文档数**: {len(self.documents)}")
        report.append(f"- **总问题数**: {total_issues}")
        report.append(f"- **P0级问题**: {p0_issues}个")
        report.append(f"- **P1级问题**: {p1_issues}个")
        report.append(f"- **P2级问题**: {p2_issues}个")
        report.append("")
        report.append("---")
        report.append("")
        
        # L1层问题
        if self.l1_issues:
            report.append("## 🔴 L1 文件系统层问题")
            report.append("")
            
            for issue in self.l1_issues:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report.append(f"### {severity_icon} {issue['type']} ({issue['severity']})")
                report.append("")
                report.append(f"- **描述**: {issue['description']}")
                report.append(f"- **路径**: {issue['path']}")
                report.append("")
        
        # L2层问题
        if self.l2_issues:
            report.append("## 🟡 L2 文档内容层问题")
            report.append("")
            
            for issue in self.l2_issues:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report.append(f"### {severity_icon} {issue['type']} ({issue['severity']})")
                report.append("")
                report.append(f"- **描述**: {issue['description']}")
                report.append(f"- **路径**: {issue['path']}")
                report.append("")
        
        # L3层问题
        if self.l3_issues:
            report.append("## 🟢 L3 专业标准层问题")
            report.append("")
            
            for issue in self.l3_issues:
                severity_icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(issue['severity'], "⚪")
                report.append(f"### {severity_icon} {issue['type']} ({issue['severity']})")
                report.append("")
                report.append(f"- **描述**: {issue['description']}")
                report.append(f"- **路径**: {issue['path']}")
                report.append("")
        
        # 改进建议
        report.append("---")
        report.append("")
        report.append("## 🎯 改进建议")
        report.append("")
        
        if p0_issues > 0:
            report.append("### 立即修复（P0级）")
            report.append("")
            p0_list = [i for i in self.l1_issues + self.l2_issues + self.l3_issues if i['severity'] == 'P0']
            for issue in p0_list:
                report.append(f"- {issue['type']}: {issue['description']}")
            report.append("")
        
        if p1_issues > 0:
            report.append("### 短期修复（P1级）")
            report.append("")
            p1_list = [i for i in self.l1_issues + self.l2_issues + self.l3_issues if i['severity'] == 'P1']
            for issue in p1_list:
                report.append(f"- {issue['type']}: {issue['description']}")
            report.append("")
        
        if p2_issues > 0:
            report.append("### 长期优化（P2级）")
            report.append("")
            p2_list = [i for i in self.l1_issues + self.l2_issues + self.l3_issues if i['severity'] == 'P2']
            for issue in p2_list:
                report.append(f"- {issue['type']}: {issue['description']}")
            report.append("")
        
        return '\n'.join(report)
    
    def run_audit(self):
        """执行审计"""
        print("="*80)
        print("组合优化层深度审计 V7")
        print("="*80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: {BLUEPRINTS_DIR}")
        print("="*80)
        
        # 执行三层审计
        self.check_l1_filesystem()
        self.check_l2_content()
        self.check_l3_standards()
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告
        report_path = Path("docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER6_DEEP_AUDIT_V7_20260407.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8-sig') as f:
            f.write(report)
        
        print("\n" + "="*80)
        print("审计完成")
        print("="*80)
        print(f"总问题数: {len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)}")
        print(f"报告已保存至: {report_path}")
        
        return report


if __name__ == "__main__":
    auditor = Layer6DeepAuditorV7()
    auditor.run_audit()
