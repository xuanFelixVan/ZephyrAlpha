#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合深度审计工具
功能：
1. L1文件系统层审计
2. L2文档内容层审计
3. L3专业标准层审计
4. 重复文档检测
5. 职责分析
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

@dataclass
class AuditIssue:
    layer: str
    category: str
    severity: str
    file: str
    issue_type: str
    description: str
    suggestion: str

@dataclass
class DocumentInfo:
    file_path: str
    title: str
    content_hash: str
    module_id: str
    responsibility: str
    word_count: int
    has_frontmatter: bool
    has_index: bool
    issues: List[AuditIssue] = field(default_factory=list)

class ComprehensiveDeepAuditor:
    def __init__(self, docs_dir: Path):
        self.docs_dir = Path(docs_dir)
        self.documents: List[DocumentInfo] = []
        self.issues: List[AuditIssue] = []
        self.content_hashes: Dict[str, List[str]] = defaultdict(list)
        self.module_ids: Dict[str, List[str]] = defaultdict(list)
        self.responsibilities: Dict[str, List[str]] = defaultdict(list)
        
    def execute_full_audit(self) -> Dict:
        print("\n" + "="*80)
        print("综合深度审计开始")
        print("="*80)
        
        print(f"\n[步骤1/6] 扫描所有文档文件...")
        self._scan_all_documents()
        print(f"  扫描完成: {len(self.documents)}个文档")
        
        print(f"\n[步骤2/6] L1文件系统层审计...")
        l1_issues = self._audit_layer1()
        print(f"  发现问题: {len(l1_issues)}个")
        
        print(f"\n[步骤3/6] L2文档内容层审计...")
        l2_issues = self._audit_layer2()
        print(f"  发现问题: {len(l2_issues)}个")
        
        print(f"\n[步骤4/6] L3专业标准层审计...")
        l3_issues = self._audit_layer3()
        print(f"  发现问题: {len(l3_issues)}个")
        
        print(f"\n[步骤5/6] 重复文档检测...")
        duplicates = self._detect_duplicates()
        print(f"  发现重复: {len(duplicates)}组")
        
        print(f"\n[步骤6/6] 职责分析...")
        responsibility_issues = self._analyze_responsibilities()
        print(f"  发现问题: {len(responsibility_issues)}个")
        
        return self._generate_comprehensive_report()
    
    def _scan_all_documents(self):
        md_files = list(self.docs_dir.rglob("*.md"))
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                content_hash = hashlib.md5(content.encode()).hexdigest()
                
                title = self._extract_title(content)
                module_id = self._extract_module_id(content)
                responsibility = self._extract_responsibility(content)
                word_count = len(content.split())
                has_frontmatter = bool(re.search(r'^---\s*\n.*?\n---', content, re.DOTALL))
                has_index = md_file.name == 'INDEX.md'
                
                doc_info = DocumentInfo(
                    file_path=str(md_file.relative_to(self.docs_dir)),
                    title=title,
                    content_hash=content_hash,
                    module_id=module_id,
                    responsibility=responsibility,
                    word_count=word_count,
                    has_frontmatter=has_frontmatter,
                    has_index=has_index
                )
                
                self.documents.append(doc_info)
                
                if content_hash:
                    self.content_hashes[content_hash].append(doc_info.file_path)
                if module_id:
                    self.module_ids[module_id].append(doc_info.file_path)
                if responsibility:
                    self.responsibilities[responsibility].append(doc_info.file_path)
                    
            except Exception as e:
                print(f"  警告: 无法读取文件 {md_file}: {e}")
    
    def _extract_title(self, content: str) -> str:
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else "未命名"
    
    def _extract_module_id(self, content: str) -> str:
        match = re.search(r'module_id:\s*(.+)', content)
        return match.group(1).strip() if match else ""
    
    def _extract_responsibility(self, content: str) -> str:
        match = re.search(r'responsibility:\s*\n\s+-\s*(.+)', content)
        if match:
            return match.group(1).strip()
        
        match = re.search(r'职责[：:]\s*(.+)', content)
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _audit_layer1(self) -> List[AuditIssue]:
        issues = []
        
        print("  [1.1] 检查目录结构...")
        issues.extend(self._check_directory_structure())
        
        print("  [1.2] 检查文件命名...")
        issues.extend(self._check_file_naming())
        
        print("  [1.3] 检查路径引用...")
        issues.extend(self._check_path_references())
        
        self.issues.extend(issues)
        return issues
    
    def _check_directory_structure(self) -> List[AuditIssue]:
        issues = []
        
        for directory in self.docs_dir.rglob("*"):
            if not directory.is_dir():
                continue
            
            rel_path = str(directory.relative_to(self.docs_dir))
            
            if rel_path.startswith('06_ARCHIVE'):
                continue
            
            files_in_dir = list(directory.glob("*.md"))
            if len(files_in_dir) == 0:
                issues.append(AuditIssue(
                    layer="L1",
                    category="目录结构",
                    severity="medium",
                    file=rel_path,
                    issue_type="空目录",
                    description=f"目录为空，建议删除或填充内容",
                    suggestion="删除空目录或添加必要文档"
                ))
            elif len(files_in_dir) < 3 and directory != self.docs_dir:
                issues.append(AuditIssue(
                    layer="L1",
                    category="目录结构",
                    severity="low",
                    file=rel_path,
                    issue_type="稀疏目录",
                    description=f"目录文件过少({len(files_in_dir)}个)，建议整合",
                    suggestion="考虑整合到父目录或补充文档"
                ))
            
            path_depth = len(Path(rel_path).parts)
            if path_depth > 4:
                issues.append(AuditIssue(
                    layer="L1",
                    category="目录结构",
                    severity="medium",
                    file=rel_path,
                    issue_type="层级过深",
                    description=f"目录层级过深({path_depth}层)，难以导航",
                    suggestion="考虑扁平化目录结构"
                ))
        
        return issues
    
    def _check_file_naming(self) -> List[AuditIssue]:
        issues = []
        
        for doc in self.documents:
            if doc.file_path.startswith('06_ARCHIVE'):
                continue
            
            file_name = Path(doc.file_path).stem
            
            if re.search(r'Layer\s*\d+', file_name, re.IGNORECASE):
                issues.append(AuditIssue(
                    layer="L1",
                    category="文件命名",
                    severity="high",
                    file=doc.file_path,
                    issue_type="旧架构命名残留",
                    description=f"文件名包含旧架构关键词: {file_name}",
                    suggestion="重命名文件，移除旧架构关键词"
                ))
            
            if ' ' in file_name:
                issues.append(AuditIssue(
                    layer="L1",
                    category="文件命名",
                    severity="low",
                    file=doc.file_path,
                    issue_type="文件名包含空格",
                    description=f"文件名包含空格: {file_name}",
                    suggestion="使用下划线替代空格"
                ))
            
            if re.search(r'[\u4e00-\u9fff]', file_name):
                issues.append(AuditIssue(
                    layer="L1",
                    category="文件命名",
                    severity="low",
                    file=doc.file_path,
                    issue_type="文件名包含中文",
                    description=f"文件名包含中文字符: {file_name}",
                    suggestion="使用英文命名"
                ))
        
        return issues
    
    def _check_path_references(self) -> List[AuditIssue]:
        issues = []
        
        for doc in self.documents:
            if doc.file_path.startswith('06_ARCHIVE'):
                continue
            
            try:
                file_path = self.docs_dir / doc.file_path
                content = file_path.read_text(encoding='utf-8')
                
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                
                for link_text, link_path in links:
                    if link_path.startswith(('http://', 'https://', '#', 'mailto:')):
                        continue
                    
                    if link_path.count('../') > 3:
                        issues.append(AuditIssue(
                            layer="L1",
                            category="路径引用",
                            severity="medium",
                            file=doc.file_path,
                            issue_type="路径冗余",
                            description=f"链接使用过多相对路径: {link_path}",
                            suggestion="简化路径引用"
                        ))
                    
                    if not link_path.startswith(('#', 'http', 'mailto')):
                        target_path = (file_path.parent / link_path).resolve()
                        if not target_path.exists():
                            issues.append(AuditIssue(
                                layer="L1",
                                category="路径引用",
                                severity="high",
                                file=doc.file_path,
                                issue_type="死链接",
                                description=f"链接指向不存在的文件: {link_path}",
                                suggestion="修复或删除无效链接"
                            ))
                            
            except Exception as e:
                pass
        
        return issues
    
    def _audit_layer2(self) -> List[AuditIssue]:
        issues = []
        
        print("  [2.1] 检查职责驱动原则...")
        issues.extend(self._check_responsibility_principle())
        
        print("  [2.2] 检查索引完备性...")
        issues.extend(self._check_index_completeness())
        
        print("  [2.3] 检查版本隔离...")
        issues.extend(self._check_version_isolation())
        
        self.issues.extend(issues)
        return issues
    
    def _check_responsibility_principle(self) -> List[AuditIssue]:
        issues = []
        
        for doc in self.documents:
            if doc.file_path.startswith('06_ARCHIVE'):
                continue
            
            if not doc.responsibility and not doc.has_index:
                issues.append(AuditIssue(
                    layer="L2",
                    category="职责驱动",
                    severity="high",
                    file=doc.file_path,
                    issue_type="职责不清",
                    description="文档缺少明确的职责描述",
                    suggestion="在文档头部添加职责说明"
                ))
            
            if doc.word_count < 100 and not doc.has_index:
                issues.append(AuditIssue(
                    layer="L2",
                    category="职责驱动",
                    severity="medium",
                    file=doc.file_path,
                    issue_type="内容过短",
                    description=f"文档内容过短({doc.word_count}字)，职责可能不完整",
                    suggestion="扩充文档内容或合并到相关文档"
                ))
        
        return issues
    
    def _check_index_completeness(self) -> List[AuditIssue]:
        issues = []
        
        directories = set()
        for doc in self.documents:
            if not doc.file_path.startswith('06_ARCHIVE'):
                dir_path = str(Path(doc.file_path).parent)
                if dir_path != '.':
                    directories.add(dir_path)
        
        for directory in directories:
            index_file = self.docs_dir / directory / "INDEX.md"
            if not index_file.exists():
                issues.append(AuditIssue(
                    layer="L2",
                    category="索引完备性",
                    severity="high",
                    file=directory,
                    issue_type="缺少索引",
                    description="目录缺少INDEX.md导航文件",
                    suggestion="创建INDEX.md索引文件"
                ))
        
        return issues
    
    def _check_version_isolation(self) -> List[AuditIssue]:
        issues = []
        
        for module_id, files in self.module_ids.items():
            if len(files) > 1:
                issues.append(AuditIssue(
                    layer="L2",
                    category="版本隔离",
                    severity="high",
                    file=", ".join(files),
                    issue_type="编号重复",
                    description=f"多个文档使用相同module_id: {module_id}",
                    suggestion="为每个文档分配唯一的module_id"
                ))
        
        return issues
    
    def _audit_layer3(self) -> List[AuditIssue]:
        issues = []
        
        print("  [3.1] 检查五大原则符合性...")
        issues.extend(self._check_five_principles())
        
        print("  [3.2] 检查文档分类...")
        issues.extend(self._check_document_classification())
        
        print("  [3.3] 检查编号体系...")
        issues.extend(self._check_numbering_system())
        
        self.issues.extend(issues)
        return issues
    
    def _check_five_principles(self) -> List[AuditIssue]:
        issues = []
        
        for doc in self.documents:
            if doc.file_path.startswith('06_ARCHIVE'):
                continue
            
            if not doc.has_frontmatter:
                issues.append(AuditIssue(
                    layer="L3",
                    category="五大原则",
                    severity="high",
                    file=doc.file_path,
                    issue_type="缺少元数据",
                    description="文档缺少标准YAML前置信息",
                    suggestion="添加完整的YAML前置信息"
                ))
        
        return issues
    
    def _check_document_classification(self) -> List[AuditIssue]:
        issues = []
        
        valid_categories = [
            '01_FRAMEWORK', '02_REQUIREMENTS', '03_ARCHITECTURE',
            '04_DESIGN', '05_IMPLEMENTATION', '06_ARCHIVE',
            '07_TESTING', '08_KNOWLEDGE_BASE', '09_AUDIT',
            '09_RESEARCH_INNOVATION'
        ]
        
        for doc in self.documents:
            if doc.file_path.startswith('06_ARCHIVE'):
                continue
            
            first_dir = doc.file_path.split('/')[0] if '/' in doc.file_path else ''
            if first_dir and first_dir not in valid_categories:
                issues.append(AuditIssue(
                    layer="L3",
                    category="文档分类",
                    severity="medium",
                    file=doc.file_path,
                    issue_type="分类错误",
                    description=f"文档可能放置在错误的分类目录: {first_dir}",
                    suggestion="检查文档分类是否正确"
                ))
        
        return issues
    
    def _check_numbering_system(self) -> List[AuditIssue]:
        issues = []
        
        for doc in self.documents:
            if doc.file_path.startswith('06_ARCHIVE'):
                continue
            
            if not doc.module_id:
                issues.append(AuditIssue(
                    layer="L3",
                    category="编号体系",
                    severity="medium",
                    file=doc.file_path,
                    issue_type="编号缺失",
                    description="文档缺少module_id编号",
                    suggestion="添加标准化的module_id"
                ))
        
        return issues
    
    def _detect_duplicates(self) -> List[Dict]:
        duplicates = []
        
        for content_hash, files in self.content_hashes.items():
            if len(files) > 1:
                duplicates.append({
                    'type': '内容重复',
                    'files': files,
                    'severity': 'high',
                    'description': f'{len(files)}个文档内容完全相同'
                })
        
        for module_id, files in self.module_ids.items():
            if len(files) > 1 and module_id:
                duplicates.append({
                    'type': '编号重复',
                    'files': files,
                    'severity': 'high',
                    'description': f'{len(files)}个文档使用相同module_id: {module_id}'
                })
        
        return duplicates
    
    def _analyze_responsibilities(self) -> List[AuditIssue]:
        issues = []
        
        for responsibility, files in self.responsibilities.items():
            if len(files) > 1 and responsibility:
                issues.append(AuditIssue(
                    layer="L2",
                    category="职责分析",
                    severity="medium",
                    file=", ".join(files),
                    issue_type="职责重叠",
                    description=f"多个文档承担相同职责: {responsibility}",
                    suggestion="合并职责相同的文档或明确职责边界"
                ))
        
        return issues
    
    def _generate_comprehensive_report(self) -> Dict:
        total_issues = len(self.issues)
        
        severity_counts = defaultdict(int)
        layer_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for issue in self.issues:
            severity_counts[issue.severity] += 1
            layer_counts[issue.layer] += 1
            category_counts[issue.category] += 1
        
        return {
            'summary': {
                'audit_date': datetime.now().isoformat(),
                'total_documents': len(self.documents),
                'total_issues': total_issues,
                'severity_distribution': dict(severity_counts),
                'layer_distribution': dict(layer_counts),
                'category_distribution': dict(category_counts)
            },
            'layer1_issues': [
                {
                    'category': issue.category,
                    'severity': issue.severity,
                    'file': issue.file,
                    'issue_type': issue.issue_type,
                    'description': issue.description,
                    'suggestion': issue.suggestion
                }
                for issue in self.issues if issue.layer == "L1"
            ],
            'layer2_issues': [
                {
                    'category': issue.category,
                    'severity': issue.severity,
                    'file': issue.file,
                    'issue_type': issue.issue_type,
                    'description': issue.description,
                    'suggestion': issue.suggestion
                }
                for issue in self.issues if issue.layer == "L2"
            ],
            'layer3_issues': [
                {
                    'category': issue.category,
                    'severity': issue.severity,
                    'file': issue.file,
                    'issue_type': issue.issue_type,
                    'description': issue.description,
                    'suggestion': issue.suggestion
                }
                for issue in self.issues if issue.layer == "L3"
            ],
            'duplicates': self._detect_duplicates(),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[Dict]:
        recommendations = []
        
        high_severity_issues = [i for i in self.issues if i.severity == 'high']
        if high_severity_issues:
            recommendations.append({
                'priority': 'P0',
                'action': f'立即修复{len(high_severity_issues)}个高严重性问题',
                'impact': '影响文档质量和系统稳定性',
                'timeline': '24小时内'
            })
        
        duplicate_issues = [i for i in self.issues if i.issue_type in ['编号重复', '职责重叠']]
        if duplicate_issues:
            recommendations.append({
                'priority': 'P1',
                'action': f'处理{len(duplicate_issues)}个重复问题',
                'impact': '影响文档职责清晰度',
                'timeline': '1周内'
            })
        
        return recommendations
    
    def save_report(self, report: Dict, output_file: Path):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存: {output_file}")

def main():
    docs_dir = Path("D:/ZephyrAlpha/docs")
    auditor = ComprehensiveDeepAuditor(docs_dir)
    
    report = auditor.execute_full_audit()
    
    print("\n" + "="*80)
    print("审计结果汇总")
    print("="*80)
    print(f"\n总文档数: {report['summary']['total_documents']}")
    print(f"总问题数: {report['summary']['total_issues']}")
    
    print(f"\n按严重程度分布:")
    for severity, count in report['summary']['severity_distribution'].items():
        print(f"  {severity}: {count}个")
    
    print(f"\n按层级分布:")
    for layer, count in report['summary']['layer_distribution'].items():
        print(f"  {layer}: {count}个")
    
    print(f"\n按类别分布:")
    for category, count in report['summary']['category_distribution'].items():
        print(f"  {category}: {count}个")
    
    print(f"\n重复文档数: {len(report['duplicates'])}组")
    
    output_file = docs_dir.parent / "docs/09_AUDIT/REPORTS/comprehensive_deep_audit_report.json"
    auditor.save_report(report, output_file)

if __name__ == "__main__":
    main()
