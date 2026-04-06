"""
组合优化层深度审计脚本 V6
基于专业量化机构五大原则和三层审计标准
创建时间：2026-04-07
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import hashlib

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")


def read_document(filepath: Path) -> Tuple[str, str]:
    """读取文档内容"""
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read(), encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    return "", 'utf-8'


def extract_yaml_header(content: str) -> dict:
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


def extract_title(content: str) -> str:
    """提取文档标题"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1) if match else ""


def extract_sections(content: str) -> List[str]:
    """提取文档章节"""
    sections = re.findall(r'^##\s+(\d+\.?\s*.+)$', content, re.MULTILINE)
    return sections


def get_content_hash(content: str) -> str:
    """获取内容哈希值"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


class Layer6DeepAuditorV6:
    """组合优化层深度审计器 V6"""
    
    def __init__(self):
        self.l1_issues = []  # 文件系统层问题
        self.l2_issues = []  # 文档内容层问题
        self.l3_issues = []  # 专业标准层问题
        self.documents = {}  # 文档信息存储
        self.duplicates = defaultdict(list)  # 重复文档检测
        self.responsibility_map = defaultdict(list)  # 职责映射
        self.module_id_map = defaultdict(list)  # module_id映射
        self.content_hashes = defaultdict(list)  # 内容哈希映射
    
    def check_l1_filesystem(self):
        """L1文件系统层审计"""
        print("\n" + "="*80)
        print("L1 文件系统层审计")
        print("="*80)
        
        # 1.1 目录结构检查
        print("\n1.1 目录结构检查")
        
        # 检查目录漂移
        expected_dirs = {'01_FRAMEWORK', '01_BLUEPRINTS'}
        actual_dirs = set()
        for item in BLUEPRINTS_DIR.parent.iterdir():
            if item.is_dir():
                actual_dirs.add(item.name)
        
        drift_dirs = actual_dirs - expected_dirs
        if drift_dirs:
            for dir_name in drift_dirs:
                self.l1_issues.append({
                    "type": "目录漂移",
                    "severity": "P1",
                    "description": f"目录 {dir_name} 可能存在漂移",
                    "location": str(BLUEPRINTS_DIR.parent / dir_name)
                })
        
        # 检查稀疏目录
        for item in BLUEPRINTS_DIR.parent.iterdir():
            if item.is_dir():
                file_count = len(list(item.glob("*.md")))
                if file_count < 3 and file_count > 0:
                    self.l1_issues.append({
                        "type": "稀疏目录",
                        "severity": "P2",
                        "description": f"目录 {item.name} 文件数过少 ({file_count}个)",
                        "location": str(item)
                    })
        
        # 1.2 文件命名检查
        print("\n1.2 文件命名检查")
        
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            filename = filepath.name
            
            # 检查旧架构命名残留
            if re.search(r'Layer\s*\d', filename, re.IGNORECASE):
                self.l1_issues.append({
                    "type": "旧架构命名残留",
                    "severity": "P2",
                    "description": f"文件名包含旧架构关键词: {filename}",
                    "location": str(filepath)
                })
            
            # 检查特殊字符
            if re.search(r'[\s\u4e00-\u9fff]', filename):
                self.l1_issues.append({
                    "type": "特殊字符问题",
                    "severity": "P2",
                    "description": f"文件名包含空格或中文: {filename}",
                    "location": str(filepath)
                })
        
        # 1.3 路径引用检查
        print("\n1.3 路径引用检查")
        
        for filepath in BLUEPRINTS_DIR.glob("*.md"):
            if filepath.name == "INDEX.md":
                continue
            
            content, _ = read_document(filepath)
            
            # 检查链接
            links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
            for text, link in links:
                if link.startswith('http'):
                    continue
                
                # 检查死链接
                if link.startswith('../'):
                    target_path = filepath.parent.parent / link.replace('../', '')
                else:
                    target_path = filepath.parent / link
                
                if not target_path.exists():
                    self.l1_issues.append({
                        "type": "死链接",
                        "severity": "P1",
                        "description": f"链接 [{text}]({link}) 指向不存在的文件",
                        "location": str(filepath)
                    })
        
        print(f"\nL1层问题统计: {len(self.l1_issues)}个")
    
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
            
            content, encoding = read_document(filepath)
            if not content:
                continue
            
            yaml_header = extract_yaml_header(content)
            title = extract_title(content)
            sections = extract_sections(content)
            content_hash = get_content_hash(content)
            
            doc_info = {
                "filepath": filepath,
                "filename": filepath.name,
                "yaml": yaml_header,
                "title": title,
                "sections": sections,
                "content": content,
                "content_hash": content_hash,
                "encoding": encoding
            }
            
            self.documents[filepath.name] = doc_info
            
            # 构建职责映射
            responsibility = yaml_header.get('applicable_scope', '') or self.extract_responsibility(content)
            if responsibility:
                self.responsibility_map[responsibility].append(filepath.name)
            
            # 构建module_id映射
            module_id = yaml_header.get('module_id', '')
            if module_id:
                self.module_id_map[module_id].append(filepath.name)
            
            # 构建内容哈希映射
            self.content_hashes[content_hash].append(filepath.name)
        
        # 2.1 职责驱动原则检查
        print("\n2.1 职责驱动原则检查")
        
        # 检查职责重叠
        for responsibility, files in self.responsibility_map.items():
            if len(files) > 1:
                # 进一步分析是否真正重叠
                titles = [self.documents[f]['title'] for f in files]
                if len(set(titles)) > 1:
                    # 标题不同，可能是职责不同
                    continue
                
                self.l2_issues.append({
                    "type": "职责重叠",
                    "severity": "P1",
                    "description": f"职责 '{responsibility}' 被 {len(files)} 个文档承担",
                    "files": files,
                    "location": str(BLUEPRINTS_DIR)
                })
        
        # 检查职责不清
        for filename, doc_info in self.documents.items():
            if not doc_info['yaml'].get('applicable_scope') and not self.extract_responsibility(doc_info['content']):
                self.l2_issues.append({
                    "type": "职责不清",
                    "severity": "P2",
                    "description": f"文档缺少明确的职责描述",
                    "location": str(doc_info['filepath'])
                })
        
        # 2.2 索引完备性检查
        print("\n2.2 索引完备性检查")
        
        # 检查INDEX.md
        index_path = BLUEPRINTS_DIR / "INDEX.md"
        if not index_path.exists():
            self.l2_issues.append({
                "type": "索引缺失",
                "severity": "P0",
                "description": "缺少INDEX.md索引文件",
                "location": str(BLUEPRINTS_DIR)
            })
        else:
            # 检查索引完整性
            index_content, _ = read_document(index_path)
            indexed_files = set(re.findall(r'\[([^\]]+)\]\([^)]*([^/)]+\.md)\)', index_content))
            indexed_files = {f[1] for f in indexed_files}
            
            all_files = set(self.documents.keys())
            missing_files = all_files - indexed_files
            
            if missing_files:
                self.l2_issues.append({
                    "type": "索引不完整",
                    "severity": "P1",
                    "description": f"索引缺少 {len(missing_files)} 个文档",
                    "files": list(missing_files),
                    "location": str(index_path)
                })
        
        # 2.3 版本隔离检查
        print("\n2.3 版本隔离检查")
        
        # 检查内容重复
        for content_hash, files in self.content_hashes.items():
            if len(files) > 1:
                self.l2_issues.append({
                    "type": "内容重复",
                    "severity": "P0",
                    "description": f"发现 {len(files)} 个内容完全相同的文档",
                    "files": files,
                    "location": str(BLUEPRINTS_DIR)
                })
        
        # 检查module_id重复
        for module_id, files in self.module_id_map.items():
            if len(files) > 1:
                self.l2_issues.append({
                    "type": "module_id重复",
                    "severity": "P0",
                    "description": f"module_id '{module_id}' 被 {len(files)} 个文档使用",
                    "files": files,
                    "location": str(BLUEPRINTS_DIR)
                })
        
        # 检查变更记录
        for filename, doc_info in self.documents.items():
            if '变更历史' not in doc_info['content'] and '版本历史' not in doc_info['content']:
                self.l2_issues.append({
                    "type": "变更记录缺失",
                    "severity": "P2",
                    "description": f"文档缺少变更历史记录",
                    "location": str(doc_info['filepath'])
                })
        
        print(f"\nL2层问题统计: {len(self.l2_issues)}个")
    
    def check_l3_standards(self):
        """L3专业标准层审计"""
        print("\n" + "="*80)
        print("L3 专业标准层审计")
        print("="*80)
        
        # 3.1 五大原则符合性检查
        print("\n3.1 五大原则符合性检查")
        
        # 职责驱动原则
        multi_responsibility_docs = []
        for filename, doc_info in self.documents.items():
            sections = doc_info['sections']
            # 检查是否有多个核心章节（可能多职责）
            core_sections = [s for s in sections if any(kw in s for kw in ['核心', '主要', '关键'])]
            if len(core_sections) > 3:
                multi_responsibility_docs.append(filename)
        
        if multi_responsibility_docs:
            self.l3_issues.append({
                "type": "职责驱动原则违反",
                "severity": "P2",
                "description": f"{len(multi_responsibility_docs)} 个文档可能存在多职责",
                "files": multi_responsibility_docs,
                "location": str(BLUEPRINTS_DIR)
            })
        
        # 3.2 文档分类检查
        print("\n3.2 文档分类检查")
        
        for filename, doc_info in self.documents.items():
            layer = doc_info['yaml'].get('layer', '')
            if not layer or layer == 'Unknown':
                self.l3_issues.append({
                    "type": "Layer定位缺失",
                    "severity": "P1",
                    "description": f"文档缺少Layer定位",
                    "location": str(doc_info['filepath'])
                })
        
        # 3.3 编号体系检查
        print("\n3.3 编号体系检查")
        
        for filename, doc_info in self.documents.items():
            module_id = doc_info['yaml'].get('module_id', '')
            
            # 检查编号缺失
            if not module_id:
                self.l3_issues.append({
                    "type": "module_id缺失",
                    "severity": "P1",
                    "description": f"文档缺少module_id",
                    "location": str(doc_info['filepath'])
                })
            
            # 检查编号规范
            if module_id and not re.match(r'^[A-Z_]+_\d{3}$', module_id):
                self.l3_issues.append({
                    "type": "module_id不规范",
                    "severity": "P2",
                    "description": f"module_id '{module_id}' 不符合规范",
                    "location": str(doc_info['filepath'])
                })
        
        # 3.4 文档质量检查
        print("\n3.4 文档质量检查")
        
        for filename, doc_info in self.documents.items():
            # 检查YAML头部
            if not doc_info['content'].startswith('---'):
                self.l3_issues.append({
                    "type": "YAML头部缺失",
                    "severity": "P1",
                    "description": f"文档缺少YAML头部",
                    "location": str(doc_info['filepath'])
                })
            
            # 检查YAML字段完整性
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
            missing_fields = [f for f in required_fields if f not in doc_info['yaml']]
            if missing_fields:
                self.l3_issues.append({
                    "type": "YAML字段不完整",
                    "severity": "P2",
                    "description": f"缺少字段: {', '.join(missing_fields)}",
                    "location": str(doc_info['filepath'])
                })
            
            # 检查文档治理章节
            if '文档治理' not in doc_info['content']:
                self.l3_issues.append({
                    "type": "文档治理章节缺失",
                    "severity": "P2",
                    "description": f"文档缺少文档治理章节",
                    "location": str(doc_info['filepath'])
                })
        
        print(f"\nL3层问题统计: {len(self.l3_issues)}个")
    
    def extract_responsibility(self, content: str) -> str:
        """从文档内容提取职责"""
        # 尝试从摘要或概述中提取
        patterns = [
            r'##\s*\d+\.?\s*概述\s*\n+(.+?)(?=\n##|\Z)',
            r'##\s*\d+\.?\s*摘要\s*\n+(.+?)(?=\n##|\Z)',
            r'##\s*\d+\.?\s*简介\s*\n+(.+?)(?=\n##|\Z)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()[:200]
        
        return ""
    
    def generate_report(self) -> str:
        """生成审计报告"""
        report = []
        report.append("# 组合优化层深度审计报告 V6")
        report.append("")
        report.append(f"**审计日期**: 2026-04-07")
        report.append(f"**审计范围**: {BLUEPRINTS_DIR}")
        report.append(f"**审计文档数**: {len(self.documents)}")
        report.append(f"**Git备份分支**: backup/layer6-deep-audit-v6-20260407")
        report.append("")
        report.append("---")
        report.append("")
        
        # 问题统计
        report.append("## 📊 问题统计")
        report.append("")
        
        p0_issues = [i for i in self.l1_issues + self.l2_issues + self.l3_issues if i.get('severity') == 'P0']
        p1_issues = [i for i in self.l1_issues + self.l2_issues + self.l3_issues if i.get('severity') == 'P1']
        p2_issues = [i for i in self.l1_issues + self.l2_issues + self.l3_issues if i.get('severity') == 'P2']
        
        report.append(f"| 问题级别 | L1层 | L2层 | L3层 | 总计 |")
        report.append(f"|---------|------|------|------|------|")
        report.append(f"| **P0级** | {len([i for i in self.l1_issues if i.get('severity') == 'P0'])} | {len([i for i in self.l2_issues if i.get('severity') == 'P0'])} | {len([i for i in self.l3_issues if i.get('severity') == 'P0'])} | {len(p0_issues)} |")
        report.append(f"| **P1级** | {len([i for i in self.l1_issues if i.get('severity') == 'P1'])} | {len([i for i in self.l2_issues if i.get('severity') == 'P1'])} | {len([i for i in self.l3_issues if i.get('severity') == 'P1'])} | {len(p1_issues)} |")
        report.append(f"| **P2级** | {len([i for i in self.l1_issues if i.get('severity') == 'P2'])} | {len([i for i in self.l2_issues if i.get('severity') == 'P2'])} | {len([i for i in self.l3_issues if i.get('severity') == 'P2'])} | {len(p2_issues)} |")
        report.append(f"| **总计** | {len(self.l1_issues)} | {len(self.l2_issues)} | {len(self.l3_issues)} | {len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)} |")
        report.append("")
        
        # L1层问题详情
        if self.l1_issues:
            report.append("## 🔴 L1 文件系统层问题")
            report.append("")
            for issue in self.l1_issues:
                report.append(f"### {issue['type']} [{issue['severity']}]")
                report.append(f"- **描述**: {issue['description']}")
                report.append(f"- **位置**: {issue['location']}")
                if 'files' in issue:
                    report.append(f"- **相关文件**: {', '.join(issue['files'])}")
                report.append("")
        
        # L2层问题详情
        if self.l2_issues:
            report.append("## 🟡 L2 文档内容层问题")
            report.append("")
            for issue in self.l2_issues:
                report.append(f"### {issue['type']} [{issue['severity']}]")
                report.append(f"- **描述**: {issue['description']}")
                report.append(f"- **位置**: {issue['location']}")
                if 'files' in issue:
                    report.append(f"- **相关文件**: {', '.join(issue['files'])}")
                report.append("")
        
        # L3层问题详情
        if self.l3_issues:
            report.append("## 🟢 L3 专业标准层问题")
            report.append("")
            for issue in self.l3_issues:
                report.append(f"### {issue['type']} [{issue['severity']}]")
                report.append(f"- **描述**: {issue['description']}")
                report.append(f"- **位置**: {issue['location']}")
                if 'files' in issue:
                    report.append(f"- **相关文件**: {', '.join(issue['files'])}")
                report.append("")
        
        # 改进建议
        report.append("## 📋 改进建议")
        report.append("")
        
        if p0_issues:
            report.append("### 立即修复（P0级）")
            for issue in p0_issues:
                report.append(f"- {issue['type']}: {issue['description']}")
            report.append("")
        
        if p1_issues:
            report.append("### 短期修复（P1级）")
            for issue in p1_issues:
                report.append(f"- {issue['type']}: {issue['description']}")
            report.append("")
        
        if p2_issues:
            report.append("### 长期优化（P2级）")
            for issue in p2_issues:
                report.append(f"- {issue['type']}: {issue['description']}")
            report.append("")
        
        return "\n".join(report)
    
    def run_audit(self):
        """执行完整审计"""
        print("="*80)
        print("组合优化层深度审计 V6")
        print("="*80)
        print(f"审计目录: {BLUEPRINTS_DIR}")
        print(f"审计时间: 2026-04-07")
        print("="*80)
        
        self.check_l1_filesystem()
        self.check_l2_content()
        self.check_l3_standards()
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告
        report_path = Path("docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER6_DEEP_AUDIT_V6_20260407.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8-sig') as f:
            f.write(report)
        
        print("\n" + "="*80)
        print("审计完成")
        print("="*80)
        print(f"报告已保存至: {report_path}")
        print(f"L1层问题: {len(self.l1_issues)}个")
        print(f"L2层问题: {len(self.l2_issues)}个")
        print(f"L3层问题: {len(self.l3_issues)}个")
        print(f"总问题数: {len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)}个")


if __name__ == "__main__":
    auditor = Layer6DeepAuditorV6()
    auditor.run_audit()
