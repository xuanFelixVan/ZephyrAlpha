#!/usr/bin/env python3
"""
Layer 9 研究与创新层深度审计脚本 v1.0

功能:
- L1文件系统层审计：目录结构、文件命名、路径引用
- L2文档内容层审计：职责驱动、索引完备、版本隔离、文档代码对应
- L3专业标准层审计：五大原则、文档分类、编号体系、文档质量
- 重点检查重复内容和职责不清的内容
- 生成详细的审计报告
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import difflib


class AuditLevel(Enum):
    L1_FILE_SYSTEM = "L1文件系统层"
    L2_DOCUMENT_CONTENT = "L2文档内容层"
    L3_PROFESSIONAL_STANDARD = "L3专业标准层"


class IssueSeverity(Enum):
    CRITICAL = "严重"
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


@dataclass
class AuditIssue:
    level: AuditLevel
    category: str
    severity: IssueSeverity
    description: str
    location: str
    suggestion: str
    details: Dict = field(default_factory=dict)


@dataclass
class DocumentInfo:
    filepath: str
    filename: str
    title: str
    module_id: str
    responsibility: str
    layer: str
    version: str
    status: str
    keywords: List[str]
    content_hash: str
    content_preview: str


class Layer9DeepAuditor:
    def __init__(self):
        self.layer9_dir = 'docs/09_RESEARCH_INNOVATION'
        self.audit_issues: List[AuditIssue] = []
        self.documents: List[DocumentInfo] = []
        self.responsibility_map: Dict[str, List[str]] = {}
        self.duplicate_content: List[Tuple[str, str, float]] = []
        self.unclear_responsibility: List[Tuple[str, str]] = []
        
    def run_full_audit(self):
        """执行完整的三层审计"""
        print('=' * 80)
        print('Layer 9 研究与创新层深度审计 v1.0')
        print('=' * 80)
        print(f'审计时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'审计范围: {self.layer9_dir}')
        print()
        
        print('阶段1: 扫描文档文件...')
        self.scan_documents()
        print(f'  ✅ 扫描到 {len(self.documents)} 个文档')
        print()
        
        print('阶段2: L1文件系统层审计...')
        self.audit_l1_file_system()
        print(f'  ✅ 发现 {len([i for i in self.audit_issues if i.level == AuditLevel.L1_FILE_SYSTEM])} 个问题')
        print()
        
        print('阶段3: L2文档内容层审计...')
        self.audit_l2_document_content()
        print(f'  ✅ 发现 {len([i for i in self.audit_issues if i.level == AuditLevel.L2_DOCUMENT_CONTENT])} 个问题')
        print()
        
        print('阶段4: L3专业标准层审计...')
        self.audit_l3_professional_standard()
        print(f'  ✅ 发现 {len([i for i in self.audit_issues if i.level == AuditLevel.L3_PROFESSIONAL_STANDARD])} 个问题')
        print()
        
        print('阶段5: 检测重复内容...')
        self.detect_duplicate_content()
        print(f'  ✅ 发现 {len(self.duplicate_content)} 对重复内容')
        print()
        
        print('阶段6: 检测职责不清问题...')
        self.detect_unclear_responsibility()
        print(f'  ✅ 发现 {len(self.unclear_responsibility)} 个职责不清问题')
        print()
        
        print('阶段7: 生成审计报告...')
        self.generate_report()
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('审计完成')
        print('=' * 80)
        
        self.print_summary()
    
    def scan_documents(self):
        """扫描所有文档"""
        layer9_path = Path(self.layer9_dir)
        if not layer9_path.exists():
            print(f'  ❌ 目录不存在: {self.layer9_dir}')
            return
        
        for md_file in layer9_path.rglob('*.md'):
            if 'maintenance_records' in str(md_file):
                continue
            
            try:
                doc_info = self.extract_document_info(str(md_file))
                if doc_info:
                    self.documents.append(doc_info)
                    
                    if doc_info.responsibility:
                        if doc_info.responsibility not in self.responsibility_map:
                            self.responsibility_map[doc_info.responsibility] = []
                        self.responsibility_map[doc_info.responsibility].append(doc_info.filename)
            except Exception as e:
                print(f'  ⚠️ 无法处理文件: {md_file.name} - {e}')
    
    def extract_document_info(self, filepath: str) -> Optional[DocumentInfo]:
        """提取文档信息"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            filename = os.path.basename(filepath)
            
            title = self._extract_title(content)
            module_id = self._extract_yaml_field(content, 'module_id')
            responsibility = self._extract_responsibility(content)
            layer = self._extract_yaml_field(content, 'layer')
            version = self._extract_yaml_field(content, 'version')
            status = self._extract_yaml_field(content, 'status')
            keywords = self._extract_keywords(content)
            
            content_hash = str(hash(content[:1000]))
            content_preview = content[:500].replace('\n', ' ')
            
            return DocumentInfo(
                filepath=filepath,
                filename=filename,
                title=title,
                module_id=module_id,
                responsibility=responsibility,
                layer=layer,
                version=version,
                status=status,
                keywords=keywords,
                content_hash=content_hash,
                content_preview=content_preview
            )
        except Exception as e:
            return None
    
    def _extract_title(self, content: str) -> str:
        """提取标题"""
        match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        return match.group(1).strip() if match else ""
    
    def _extract_yaml_field(self, content: str, field: str) -> str:
        """提取YAML字段"""
        pattern = rf'{field}:\s*(.+)'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""
    
    def _extract_responsibility(self, content: str) -> str:
        """提取职责描述"""
        patterns = [
            r'##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)',
            r'核心定位[：:]\s*(.+?)(?:\n\n|\n#)',
            r'职责描述[：:]\s*(.+?)(?:\n\n|\n#)',
            r'核心职责[：:]\s*(.+?)(?:\n\n|\n#)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                responsibility = match.group(1).strip()
                responsibility = re.sub(r'\s+', ' ', responsibility)
                return responsibility
        
        return ""
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        keywords = []
        keyword_patterns = [
            r'关键词[：:]\s*(.+?)(?:\n|$)',
            r'关键字[：:]\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in keyword_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                keyword_text = match.group(1).strip()
                keywords.extend([k.strip() for k in keyword_text.split(',')])
                break
        
        return keywords
    
    def audit_l1_file_system(self):
        """L1文件系统层审计"""
        self._check_directory_structure()
        self._check_file_naming()
        self._check_path_references()
    
    def _check_directory_structure(self):
        """检查目录结构"""
        layer9_path = Path(self.layer9_dir)
        
        md_files = list(layer9_path.rglob('*.md'))
        md_files = [f for f in md_files if 'maintenance_records' not in str(f)]
        
        if len(md_files) < 3:
            self.audit_issues.append(AuditIssue(
                level=AuditLevel.L1_FILE_SYSTEM,
                category="目录结构",
                severity=IssueSeverity.LOW,
                description=f"目录文件数量较少: {len(md_files)}个",
                location=self.layer9_dir,
                suggestion="考虑整合相关文档或确认目录定位"
            ))
        
        index_file = layer9_path / 'INDEX.md'
        if not index_file.exists():
            self.audit_issues.append(AuditIssue(
                level=AuditLevel.L1_FILE_SYSTEM,
                category="目录结构",
                severity=IssueSeverity.HIGH,
                description="缺少INDEX.md索引文件",
                location=self.layer9_dir,
                suggestion="创建INDEX.md文件，提供目录导航"
            ))
        
        archive_dir = layer9_path / '_archive'
        if archive_dir.exists():
            archive_files = list(archive_dir.glob('*.md'))
            if archive_files:
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L1_FILE_SYSTEM,
                    category="目录结构",
                    severity=IssueSeverity.LOW,
                    description=f"归档目录包含 {len(archive_files)} 个文档",
                    location=str(archive_dir),
                    suggestion="确认归档文档是否需要清理"
                ))
    
    def _check_file_naming(self):
        """检查文件命名"""
        for doc in self.documents:
            if not re.match(r'^[A-Z_0-9]+\.md$', doc.filename):
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L1_FILE_SYSTEM,
                    category="文件命名",
                    severity=IssueSeverity.MEDIUM,
                    description=f"文件命名不符合规范: {doc.filename}",
                    location=doc.filepath,
                    suggestion="使用大写字母、下划线和数字命名"
                ))
            
            if '_archive' in doc.filepath:
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L1_FILE_SYSTEM,
                    category="文件命名",
                    severity=IssueSeverity.LOW,
                    description=f"归档文件: {doc.filename}",
                    location=doc.filepath,
                    suggestion="确认归档文件是否需要清理"
                ))
    
    def _check_path_references(self):
        """检查路径引用"""
        for doc in self.documents:
            try:
                with open(doc.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                links = re.findall(r'\[.+?\]\((.+?)\)', content)
                
                for link in links:
                    if link.startswith('http'):
                        continue
                    
                    if link.startswith('/'):
                        self.audit_issues.append(AuditIssue(
                            level=AuditLevel.L1_FILE_SYSTEM,
                            category="路径引用",
                            severity=IssueSeverity.MEDIUM,
                            description=f"使用绝对路径: {link}",
                            location=doc.filename,
                            suggestion="使用相对路径代替绝对路径"
                        ))
                    
                    if link.count('../') > 3:
                        self.audit_issues.append(AuditIssue(
                            level=AuditLevel.L1_FILE_SYSTEM,
                            category="路径引用",
                            severity=IssueSeverity.LOW,
                            description=f"路径层级过深: {link}",
                            location=doc.filename,
                            suggestion="简化路径引用"
                        ))
            except Exception as e:
                pass
    
    def audit_l2_document_content(self):
        """L2文档内容层审计"""
        self._check_responsibility_clarity()
        self._check_index_completeness()
        self._check_version_isolation()
    
    def _check_responsibility_clarity(self):
        """检查职责清晰度"""
        for responsibility, files in self.responsibility_map.items():
            if len(files) > 1:
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L2_DOCUMENT_CONTENT,
                    category="职责驱动",
                    severity=IssueSeverity.HIGH,
                    description=f"职责重叠: {len(files)}个文档具有相同职责",
                    location=", ".join(files),
                    suggestion="重新定义职责边界，确保每个文档职责独特",
                    details={"files": files, "responsibility": responsibility[:100]}
                ))
        
        for doc in self.documents:
            if not doc.responsibility:
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L2_DOCUMENT_CONTENT,
                    category="职责驱动",
                    severity=IssueSeverity.HIGH,
                    description="缺少职责描述",
                    location=doc.filename,
                    suggestion="添加'核心定位'章节，明确文档职责"
                ))
            elif len(doc.responsibility) < 50:
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L2_DOCUMENT_CONTENT,
                    category="职责驱动",
                    severity=IssueSeverity.MEDIUM,
                    description=f"职责描述过短: {len(doc.responsibility)}字",
                    location=doc.filename,
                    suggestion="扩展职责描述至50-200字"
                ))
            elif len(doc.responsibility) > 200:
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L2_DOCUMENT_CONTENT,
                    category="职责驱动",
                    severity=IssueSeverity.MEDIUM,
                    description=f"职责描述过长: {len(doc.responsibility)}字",
                    location=doc.filename,
                    suggestion="精简职责描述至50-200字"
                ))
    
    def _check_index_completeness(self):
        """检查索引完备性"""
        index_file = Path(self.layer9_dir) / 'INDEX.md'
        
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8', errors='ignore') as f:
                    index_content = f.read()
                
                for doc in self.documents:
                    if '_archive' in doc.filepath:
                        continue
                    
                    if doc.filename not in index_content and doc.filename != 'INDEX.md':
                        self.audit_issues.append(AuditIssue(
                            level=AuditLevel.L2_DOCUMENT_CONTENT,
                            category="索引完备性",
                            severity=IssueSeverity.MEDIUM,
                            description=f"文档未在INDEX.md中索引: {doc.filename}",
                            location="INDEX.md",
                            suggestion="在INDEX.md中添加文档索引"
                        ))
            except Exception as e:
                pass
    
    def _check_version_isolation(self):
        """检查版本隔离"""
        module_ids = {}
        for doc in self.documents:
            if doc.module_id:
                if doc.module_id in module_ids:
                    self.audit_issues.append(AuditIssue(
                        level=AuditLevel.L2_DOCUMENT_CONTENT,
                        category="版本隔离",
                        severity=IssueSeverity.HIGH,
                        description=f"模块ID重复: {doc.module_id}",
                        location=f"{doc.filename} 和 {module_ids[doc.module_id]}",
                        suggestion="确保每个文档有唯一的module_id"
                    ))
                else:
                    module_ids[doc.module_id] = doc.filename
    
    def audit_l3_professional_standard(self):
        """L3专业标准层审计"""
        self._check_five_principles()
        self._check_document_classification()
        self._check_numbering_system()
        self._check_document_quality()
    
    def _check_five_principles(self):
        """检查五大原则符合性"""
        for doc in self.documents:
            if not doc.responsibility:
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L3_PROFESSIONAL_STANDARD,
                    category="五大原则",
                    severity=IssueSeverity.HIGH,
                    description="违反职责驱动原则：缺少职责描述",
                    location=doc.filename,
                    suggestion="添加明确的职责描述"
                ))
            
            if not doc.module_id:
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L3_PROFESSIONAL_STANDARD,
                    category="五大原则",
                    severity=IssueSeverity.MEDIUM,
                    description="违反命名规范原则：缺少module_id",
                    location=doc.filename,
                    suggestion="添加标准的module_id"
                ))
    
    def _check_document_classification(self):
        """检查文档分类"""
        for doc in self.documents:
            if not doc.layer:
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L3_PROFESSIONAL_STANDARD,
                    category="文档分类",
                    severity=IssueSeverity.MEDIUM,
                    description="缺少层级标识",
                    location=doc.filename,
                    suggestion="在YAML头部添加layer字段"
                ))
            elif 'Layer 9' not in doc.layer and '研究与创新层' not in doc.layer and '创新层' not in doc.layer:
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L3_PROFESSIONAL_STANDARD,
                    category="文档分类",
                    severity=IssueSeverity.LOW,
                    description=f"层级标识可能不正确: {doc.layer}",
                    location=doc.filename,
                    suggestion="确认层级标识是否正确"
                ))
    
    def _check_numbering_system(self):
        """检查编号体系"""
        for doc in self.documents:
            if doc.module_id:
                if not re.match(r'^[A-Z_0-9]+_\d+$', doc.module_id):
                    self.audit_issues.append(AuditIssue(
                        level=AuditLevel.L3_PROFESSIONAL_STANDARD,
                        category="编号体系",
                        severity=IssueSeverity.LOW,
                        description=f"module_id格式不规范: {doc.module_id}",
                        location=doc.filename,
                        suggestion="使用标准格式: [模块名]_[编号]"
                    ))
    
    def _check_document_quality(self):
        """检查文档质量"""
        for doc in self.documents:
            try:
                with open(doc.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if '---' not in content[:100]:
                    self.audit_issues.append(AuditIssue(
                        level=AuditLevel.L3_PROFESSIONAL_STANDARD,
                        category="文档质量",
                        severity=IssueSeverity.HIGH,
                        description="缺少YAML头部",
                        location=doc.filename,
                        suggestion="添加标准YAML头部"
                    ))
                
                if not re.search(r'^#\s+', content, re.MULTILINE):
                    self.audit_issues.append(AuditIssue(
                        level=AuditLevel.L3_PROFESSIONAL_STANDARD,
                        category="文档质量",
                        severity=IssueSeverity.MEDIUM,
                        description="缺少文档标题",
                        location=doc.filename,
                        suggestion="添加一级标题作为文档标题"
                    ))
            except Exception as e:
                pass
    
    def detect_duplicate_content(self):
        """检测重复内容"""
        for i in range(len(self.documents)):
            for j in range(i + 1, len(self.documents)):
                doc1 = self.documents[i]
                doc2 = self.documents[j]
                
                if doc1.responsibility and doc2.responsibility:
                    similarity = difflib.SequenceMatcher(
                        None, 
                        doc1.responsibility, 
                        doc2.responsibility
                    ).ratio()
                    
                    if similarity > 0.8:
                        self.duplicate_content.append((
                            doc1.filename,
                            doc2.filename,
                            similarity
                        ))
                        
                        self.audit_issues.append(AuditIssue(
                            level=AuditLevel.L2_DOCUMENT_CONTENT,
                            category="职责重叠",
                            severity=IssueSeverity.HIGH,
                            description=f"职责描述高度相似: {similarity*100:.1f}%",
                            location=f"{doc1.filename} vs {doc2.filename}",
                            suggestion="重新定义职责边界，确保职责独特",
                            details={
                                "similarity": similarity,
                                "responsibility1": doc1.responsibility[:100],
                                "responsibility2": doc2.responsibility[:100]
                            }
                        ))
                
                if doc1.content_preview and doc2.content_preview:
                    content_similarity = difflib.SequenceMatcher(
                        None,
                        doc1.content_preview,
                        doc2.content_preview
                    ).ratio()
                    
                    if content_similarity > 0.9:
                        self.audit_issues.append(AuditIssue(
                            level=AuditLevel.L2_DOCUMENT_CONTENT,
                            category="内容重复",
                            severity=IssueSeverity.HIGH,
                            description=f"文档内容高度相似: {content_similarity*100:.1f}%",
                            location=f"{doc1.filename} vs {doc2.filename}",
                            suggestion="检查是否为重复文档，考虑合并或删除",
                            details={
                                "similarity": content_similarity
                            }
                        ))
    
    def detect_unclear_responsibility(self):
        """检测职责不清问题"""
        for doc in self.documents:
            if not doc.responsibility:
                self.unclear_responsibility.append((doc.filename, "缺少职责描述"))
                continue
            
            vague_words = ['管理', '处理', '维护', '支持', '提供', '实现', '负责']
            vague_count = sum(1 for word in vague_words if word in doc.responsibility)
            
            if vague_count > 2:
                self.unclear_responsibility.append((doc.filename, f"职责描述过于模糊，包含{vague_count}个模糊词汇"))
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L2_DOCUMENT_CONTENT,
                    category="职责不清",
                    severity=IssueSeverity.MEDIUM,
                    description=f"职责描述过于模糊，包含{vague_count}个模糊词汇",
                    location=doc.filename,
                    suggestion="使用更具体、明确的职责描述",
                    details={"vague_words": vague_words, "responsibility": doc.responsibility[:100]}
                ))
            
            if not re.search(r'(负责|承担|实现|提供|管理|维护|支持|处理)\s+\w+', doc.responsibility):
                self.unclear_responsibility.append((doc.filename, "职责描述缺少明确的动作"))
                self.audit_issues.append(AuditIssue(
                    level=AuditLevel.L2_DOCUMENT_CONTENT,
                    category="职责不清",
                    severity=IssueSeverity.MEDIUM,
                    description="职责描述缺少明确的动作",
                    location=doc.filename,
                    suggestion="添加明确的动作动词，如'负责...''实现...''提供...'",
                    details={"responsibility": doc.responsibility[:100]}
                ))
    
    def generate_report(self):
        """生成审计报告"""
        report_lines = []
        
        report_lines.append('# Layer 9 研究与创新层深度审计报告 v1.0')
        report_lines.append('')
        report_lines.append(f'> **审计时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report_lines.append(f'> **审计范围**: {self.layer9_dir}')
        report_lines.append(f'> **审计标准**: 专业量化机构文档治理五大原则')
        report_lines.append(f'> **审计类型**: 三层深度审计（L1-L3）+ 重复内容检测 + 职责不清检测')
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📊 一、审计概要')
        report_lines.append('')
        report_lines.append(f'**审计文档数**: {len(self.documents)}个')
        report_lines.append(f'**发现问题数**: {len(self.audit_issues)}个')
        report_lines.append(f'**重复内容对**: {len(self.duplicate_content)}对')
        report_lines.append(f'**职责不清问题**: {len(self.unclear_responsibility)}个')
        report_lines.append('')
        
        l1_issues = [i for i in self.audit_issues if i.level == AuditLevel.L1_FILE_SYSTEM]
        l2_issues = [i for i in self.audit_issues if i.level == AuditLevel.L2_DOCUMENT_CONTENT]
        l3_issues = [i for i in self.audit_issues if i.level == AuditLevel.L3_PROFESSIONAL_STANDARD]
        
        report_lines.append('### 1.1 问题分布')
        report_lines.append('')
        report_lines.append('| 审计层级 | 问题数量 | 占比 |')
        report_lines.append('|----------|----------|------|')
        if self.audit_issues:
            report_lines.append(f'| L1文件系统层 | {len(l1_issues)} | {len(l1_issues)/len(self.audit_issues)*100:.1f}% |')
            report_lines.append(f'| L2文档内容层 | {len(l2_issues)} | {len(l2_issues)/len(self.audit_issues)*100:.1f}% |')
            report_lines.append(f'| L3专业标准层 | {len(l3_issues)} | {len(l3_issues)/len(self.audit_issues)*100:.1f}% |')
        report_lines.append('')
        
        report_lines.append('### 1.2 严重程度分布')
        report_lines.append('')
        severity_counts = {}
        for issue in self.audit_issues:
            severity = issue.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        report_lines.append('| 严重程度 | 数量 | 占比 |')
        report_lines.append('|----------|------|------|')
        for severity in ['严重', '高', '中', '低']:
            count = severity_counts.get(severity, 0)
            percentage = (count / len(self.audit_issues) * 100) if self.audit_issues else 0
            report_lines.append(f'| {severity} | {count} | {percentage:.1f}% |')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🔍 二、L1文件系统层审计结果')
        report_lines.append('')
        
        if l1_issues:
            for issue in l1_issues:
                report_lines.append(f'### {issue.category}')
                report_lines.append('')
                report_lines.append(f'**严重程度**: {issue.severity.value}')
                report_lines.append(f'**位置**: {issue.location}')
                report_lines.append(f'**描述**: {issue.description}')
                report_lines.append(f'**建议**: {issue.suggestion}')
                report_lines.append('')
        else:
            report_lines.append('✅ 未发现L1文件系统层问题')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📝 三、L2文档内容层审计结果')
        report_lines.append('')
        
        if l2_issues:
            for issue in l2_issues[:20]:
                report_lines.append(f'### {issue.category}')
                report_lines.append('')
                report_lines.append(f'**严重程度**: {issue.severity.value}')
                report_lines.append(f'**位置**: {issue.location}')
                report_lines.append(f'**描述**: {issue.description}')
                report_lines.append(f'**建议**: {issue.suggestion}')
                report_lines.append('')
        else:
            report_lines.append('✅ 未发现L2文档内容层问题')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🎯 四、L3专业标准层审计结果')
        report_lines.append('')
        
        if l3_issues:
            for issue in l3_issues[:20]:
                report_lines.append(f'### {issue.category}')
                report_lines.append('')
                report_lines.append(f'**严重程度**: {issue.severity.value}')
                report_lines.append(f'**位置**: {issue.location}')
                report_lines.append(f'**描述**: {issue.description}')
                report_lines.append(f'**建议**: {issue.suggestion}')
                report_lines.append('')
        else:
            report_lines.append('✅ 未发现L3专业标准层问题')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🔄 五、重复内容检测结果')
        report_lines.append('')
        
        if self.duplicate_content:
            report_lines.append(f'发现 {len(self.duplicate_content)} 对职责描述高度相似的文档：')
            report_lines.append('')
            
            for file1, file2, similarity in self.duplicate_content[:10]:
                report_lines.append(f'### 相似度: {similarity*100:.1f}%')
                report_lines.append(f'- 文档1: {file1}')
                report_lines.append(f'- 文档2: {file2}')
                report_lines.append('')
        else:
            report_lines.append('✅ 未发现职责描述高度相似的文档')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## ⚠️ 六、职责不清问题检测结果')
        report_lines.append('')
        
        if self.unclear_responsibility:
            report_lines.append(f'发现 {len(self.unclear_responsibility)} 个职责不清问题：')
            report_lines.append('')
            
            for filename, issue in self.unclear_responsibility[:10]:
                report_lines.append(f'- **{filename}**: {issue}')
        else:
            report_lines.append('✅ 未发现职责不清问题')
        
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📈 七、质量评估')
        report_lines.append('')
        
        total_checks = len(self.documents) * 10
        passed_checks = total_checks - len(self.audit_issues)
        compliance_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 100
        
        report_lines.append(f'**总体合规率**: {compliance_rate:.2f}%')
        report_lines.append(f'**通过检查项**: {passed_checks}/{total_checks}')
        report_lines.append('')
        
        critical_issues = [i for i in self.audit_issues if i.severity == IssueSeverity.CRITICAL]
        high_issues = [i for i in self.audit_issues if i.severity == IssueSeverity.HIGH]
        
        if critical_issues:
            report_lines.append(f'⚠️ **发现 {len(critical_issues)} 个严重问题，需要立即处理**')
        if high_issues:
            report_lines.append(f'⚠️ **发现 {len(high_issues)} 个高优先级问题，建议尽快处理**')
        
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🎯 八、改进建议')
        report_lines.append('')
        
        report_lines.append('### 8.1 立即处理')
        report_lines.append('')
        if critical_issues:
            for issue in critical_issues[:5]:
                report_lines.append(f'- {issue.description} ({issue.location})')
        else:
            report_lines.append('- 无严重问题需要立即处理')
        report_lines.append('')
        
        report_lines.append('### 8.2 近期改进')
        report_lines.append('')
        if high_issues:
            for issue in high_issues[:10]:
                report_lines.append(f'- {issue.description} ({issue.location})')
        else:
            report_lines.append('- 无高优先级问题需要近期改进')
        report_lines.append('')
        
        report_lines.append('### 8.3 长期优化')
        report_lines.append('')
        report_lines.append('- 建立文档质量持续监控机制')
        report_lines.append('- 定期运行职责冲突检测工具')
        report_lines.append('- 优化文档创建和审查流程')
        report_lines.append('- 清理归档目录中的历史文档')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        report_lines.append(f'**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report_lines.append(f'**审计工具版本**: v1.0')
        
        report_content = '\n'.join(report_lines)
        
        output_path = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_DEEP_AUDIT_REPORT_20260407.md')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f'  ✅ 报告已保存: {output_path}')
    
    def print_summary(self):
        """打印摘要"""
        print()
        print('审计摘要:')
        print(f'  文档总数: {len(self.documents)}')
        print(f'  问题总数: {len(self.audit_issues)}')
        print(f'  重复内容: {len(self.duplicate_content)}对')
        print(f'  职责不清: {len(self.unclear_responsibility)}个')
        
        if self.audit_issues:
            critical = len([i for i in self.audit_issues if i.severity == IssueSeverity.CRITICAL])
            high = len([i for i in self.audit_issues if i.severity == IssueSeverity.HIGH])
            medium = len([i for i in self.audit_issues if i.severity == IssueSeverity.MEDIUM])
            low = len([i for i in self.audit_issues if i.severity == IssueSeverity.LOW])
            
            print(f'  严重问题: {critical}')
            print(f'  高优先级: {high}')
            print(f'  中优先级: {medium}')
            print(f'  低优先级: {low}')


def main():
    auditor = Layer9DeepAuditor()
    auditor.run_full_audit()


if __name__ == '__main__':
    main()
