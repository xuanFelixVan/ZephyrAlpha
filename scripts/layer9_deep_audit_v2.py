#!/usr/bin/env python3
"""
Layer 9 深度审计脚本 v2.0

功能:
- 执行完整的三层审计（L1-L3）
- 重点检查重复内容和职责不清问题
- 检查所有文档的每一个内容
- 生成详细的审计报告
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class AuditIssue:
    level: str
    category: str
    severity: str
    description: str
    filepath: str
    recommendation: str


@dataclass
class DocumentInfo:
    filepath: str
    filename: str
    content: str
    title: str
    responsibility: str
    module_id: str
    version: str
    status: str
    has_yaml: bool
    has_responsibility: bool
    has_core_positioning: bool


class Layer9DeepAuditor:
    def __init__(self):
        self.layer9_dir = 'docs/09_RESEARCH_INNOVATION'
        self.audit_issues: List[AuditIssue] = []
        self.documents: List[DocumentInfo] = []
        self.duplicate_pairs: List[Tuple[str, str, float]] = []
        self.responsibility_issues: List[Tuple[str, str]] = []
        
    def run_full_audit(self):
        """执行完整的三层审计"""
        print('=' * 80)
        print('Layer 9 研究与创新层深度审计 v2.0')
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
        print(f'  ✅ 发现 {len([i for i in self.audit_issues if i.level == "L1"])} 个问题')
        print()
        
        print('阶段3: L2文档内容层审计...')
        self.audit_l2_document_content()
        print(f'  ✅ 发现 {len([i for i in self.audit_issues if i.level == "L2"])} 个问题')
        print()
        
        print('阶段4: L3专业标准层审计...')
        self.audit_l3_professional_standard()
        print(f'  ✅ 发现 {len([i for i in self.audit_issues if i.level == "L3"])} 个问题')
        print()
        
        print('阶段5: 检测重复内容...')
        self.detect_duplicate_content()
        print(f'  ✅ 发现 {len(self.duplicate_pairs)} 对重复内容')
        print()
        
        print('阶段6: 检测职责不清问题...')
        self.detect_unclear_responsibility()
        print(f'  ✅ 发现 {len(self.responsibility_issues)} 个职责不清问题')
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
        """扫描文档"""
        layer9_path = Path(self.layer9_dir)
        if not layer9_path.exists():
            print(f'  ❌ 目录不存在: {self.layer9_dir}')
            return
        
        for md_file in layer9_path.rglob('*.md'):
            if 'maintenance_records' in str(md_file):
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                doc_info = self.extract_document_info(str(md_file), content)
                if doc_info:
                    self.documents.append(doc_info)
            except Exception as e:
                print(f'  ⚠️ 无法读取文件: {md_file.name} - {e}')
    
    def extract_document_info(self, filepath: str, content: str) -> Optional[DocumentInfo]:
        """提取文档信息"""
        filename = os.path.basename(filepath)
        
        title = self._extract_title(content)
        responsibility = self._extract_responsibility(content)
        module_id = self._extract_yaml_field(content, 'module_id')
        version = self._extract_yaml_field(content, 'version')
        status = self._extract_yaml_field(content, 'status')
        
        has_yaml = bool(re.match(r'^---', content))
        has_responsibility = bool(re.search(r'responsibility:', content))
        has_core_positioning = bool(re.search(r'##\s+核心定位', content))
        
        return DocumentInfo(
            filepath=filepath,
            filename=filename,
            content=content,
            title=title,
            responsibility=responsibility,
            module_id=module_id,
            version=version,
            status=status,
            has_yaml=has_yaml,
            has_responsibility=has_responsibility,
            has_core_positioning=has_core_positioning
        )
    
    def _extract_title(self, content: str) -> str:
        """提取标题"""
        match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        return match.group(1).strip() if match else ""
    
    def _extract_responsibility(self, content: str) -> str:
        """提取职责描述"""
        patterns = [
            r'responsibility:\s*\n\s+-\s+(.+?)(?:\n|$)',
            r'##\s+核心定位\s*\n\s*(.+?)(?:\n\n|\n#)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_yaml_field(self, content: str, field: str) -> str:
        """提取YAML字段"""
        pattern = rf'{field}:\s*(.+)'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""
    
    def audit_l1_file_system(self):
        """L1文件系统层审计"""
        self._check_directory_structure()
        self._check_file_naming()
        self._check_path_references()
    
    def _check_directory_structure(self):
        """检查目录结构"""
        layer9_path = Path(self.layer9_dir)
        
        for item in layer9_path.iterdir():
            if item.is_dir():
                if item.name.startswith('_'):
                    continue
                
                files_in_dir = list(item.glob('*.md'))
                if len(files_in_dir) < 3:
                    self.audit_issues.append(AuditIssue(
                        level='L1',
                        category='目录结构',
                        severity='低',
                        description=f'目录稀疏: {item.name} 目录下只有 {len(files_in_dir)} 个文件',
                        filepath=str(item),
                        recommendation='考虑整合到父目录或删除空目录'
                    ))
    
    def _check_file_naming(self):
        """检查文件命名"""
        for doc in self.documents:
            filename = doc.filename
            
            if not re.match(r'^[A-Z][A-Z0-9_]*\.md$', filename):
                if not filename == 'INDEX.md':
                    self.audit_issues.append(AuditIssue(
                        level='L1',
                        category='文件命名',
                        severity='低',
                        description=f'文件命名不规范: {filename}',
                        filepath=doc.filepath,
                        recommendation='使用大写字母、数字和下划线命名'
                    ))
    
    def _check_path_references(self):
        """检查路径引用"""
        for doc in self.documents:
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', doc.content)
            
            for link_text, link_path in links:
                if link_path.startswith('http'):
                    continue
                
                if link_path.count('../') > 3:
                    self.audit_issues.append(AuditIssue(
                        level='L1',
                        category='路径引用',
                        severity='中',
                        description=f'路径冗余: {link_path}',
                        filepath=doc.filepath,
                        recommendation='简化相对路径，减少 ../ 使用'
                    ))
    
    def audit_l2_document_content(self):
        """L2文档内容层审计"""
        self._check_responsibility_principle()
        self._check_index_completeness()
        self._check_version_isolation()
    
    def _check_responsibility_principle(self):
        """检查职责驱动原则"""
        for doc in self.documents:
            if not doc.has_responsibility and not doc.has_core_positioning:
                self.audit_issues.append(AuditIssue(
                    level='L2',
                    category='职责驱动',
                    severity='高',
                    description='缺少职责描述',
                    filepath=doc.filepath,
                    recommendation='添加YAML头部responsibility字段或"核心定位"章节'
                ))
            
            if doc.responsibility:
                if len(doc.responsibility) < 50:
                    self.audit_issues.append(AuditIssue(
                        level='L2',
                        category='职责驱动',
                        severity='中',
                        description=f'职责描述过短: {len(doc.responsibility)}字',
                        filepath=doc.filepath,
                        recommendation='职责描述应在50-200字之间'
                    ))
                elif len(doc.responsibility) > 200:
                    self.audit_issues.append(AuditIssue(
                        level='L2',
                        category='职责驱动',
                        severity='低',
                        description=f'职责描述过长: {len(doc.responsibility)}字',
                        filepath=doc.filepath,
                        recommendation='职责描述应在50-200字之间'
                    ))
    
    def _check_index_completeness(self):
        """检查索引完备性"""
        index_file = Path(self.layer9_dir) / 'INDEX.md'
        
        if not index_file.exists():
            self.audit_issues.append(AuditIssue(
                level='L2',
                category='索引完备',
                severity='高',
                description='缺少INDEX.md索引文件',
                filepath=str(index_file),
                recommendation='创建INDEX.md索引文件'
            ))
            return
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_content = f.read()
            
            for doc in self.documents:
                if doc.filename == 'INDEX.md':
                    continue
                
                if doc.filename not in index_content and os.path.splitext(doc.filename)[0] not in index_content:
                    self.audit_issues.append(AuditIssue(
                        level='L2',
                        category='索引完备',
                        severity='中',
                        description=f'文档未被索引: {doc.filename}',
                        filepath=str(index_file),
                        recommendation='在INDEX.md中添加文档索引'
                    ))
        except Exception as e:
            print(f'  ⚠️ 无法读取INDEX.md: {e}')
    
    def _check_version_isolation(self):
        """检查版本隔离"""
        for doc in self.documents:
            if doc.version and 'v' in doc.version.lower():
                if '_archive' not in doc.filepath:
                    self.audit_issues.append(AuditIssue(
                        level='L2',
                        category='版本隔离',
                        severity='中',
                        description=f'带版本号的文档未归档: {doc.filename}',
                        filepath=doc.filepath,
                        recommendation='将历史版本文档移至_archive目录'
                    ))
    
    def audit_l3_professional_standard(self):
        """L3专业标准层审计"""
        self._check_five_principles()
        self._check_classification_system()
        self._check_numbering_system()
    
    def _check_five_principles(self):
        """检查五大原则符合性"""
        for doc in self.documents:
            if not doc.has_yaml:
                self.audit_issues.append(AuditIssue(
                    level='L3',
                    category='五大原则',
                    severity='高',
                    description='缺少YAML头部',
                    filepath=doc.filepath,
                    recommendation='添加标准YAML头部，包含module_id、version、status等字段'
                ))
            
            if not doc.module_id:
                self.audit_issues.append(AuditIssue(
                    level='L3',
                    category='五大原则',
                    severity='中',
                    description='缺少module_id',
                    filepath=doc.filepath,
                    recommendation='在YAML头部添加module_id字段'
                ))
    
    def _check_classification_system(self):
        """检查分类体系"""
        pass
    
    def _check_numbering_system(self):
        """检查编号体系"""
        module_ids = {}
        
        for doc in self.documents:
            if doc.module_id:
                if doc.module_id in module_ids:
                    self.audit_issues.append(AuditIssue(
                        level='L3',
                        category='编号体系',
                        severity='高',
                        description=f'module_id重复: {doc.module_id}',
                        filepath=doc.filepath,
                        recommendation='确保每个文档有唯一的module_id'
                    ))
                else:
                    module_ids[doc.module_id] = doc.filepath
    
    def detect_duplicate_content(self):
        """检测重复内容"""
        for i, doc1 in enumerate(self.documents):
            for doc2 in self.documents[i+1:]:
                if doc1.filename == doc2.filename:
                    continue
                
                if doc1.responsibility and doc2.responsibility:
                    similarity = self._calculate_similarity(doc1.responsibility, doc2.responsibility)
                    
                    if similarity > 0.8:
                        self.duplicate_pairs.append((doc1.filename, doc2.filename, similarity))
                        
                        self.audit_issues.append(AuditIssue(
                            level='L2',
                            category='职责重叠',
                            severity='中',
                            description=f'职责相似度{similarity:.1%}: {doc1.filename} <-> {doc2.filename}',
                            filepath=f'{doc1.filepath} <-> {doc2.filepath}',
                            recommendation='优化职责描述，确保职责边界清晰'
                        ))
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def detect_unclear_responsibility(self):
        """检测职责不清问题"""
        for doc in self.documents:
            if not doc.responsibility:
                self.responsibility_issues.append((doc.filename, '缺少职责描述'))
                continue
            
            if len(doc.responsibility) < 50:
                self.responsibility_issues.append((doc.filename, '职责描述过短'))
                continue
            
            action_verbs = ['负责', '提供', '实现', '管理', '维护', '记录', '定义', '规划', '设计', '构建']
            has_action = any(verb in doc.responsibility for verb in action_verbs)
            
            if not has_action:
                self.responsibility_issues.append((doc.filename, '职责描述缺少明确的动作'))
    
    def generate_report(self):
        """生成审计报告"""
        report_lines = []
        
        report_lines.append('# Layer 9 研究与创新层深度审计报告 v2.0')
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
        report_lines.append(f'**重复内容对**: {len(self.duplicate_pairs)}对')
        report_lines.append(f'**职责不清问题**: {len(self.responsibility_issues)}个')
        report_lines.append('')
        
        report_lines.append('### 1.1 问题分布')
        report_lines.append('')
        report_lines.append('| 审计层级 | 问题数量 | 占比 |')
        report_lines.append('|----------|----------|------|')
        
        l1_count = len([i for i in self.audit_issues if i.level == 'L1'])
        l2_count = len([i for i in self.audit_issues if i.level == 'L2'])
        l3_count = len([i for i in self.audit_issues if i.level == 'L3'])
        total = len(self.audit_issues)
        
        if total > 0:
            report_lines.append(f'| L1文件系统层 | {l1_count} | {l1_count/total*100:.1f}% |')
            report_lines.append(f'| L2文档内容层 | {l2_count} | {l2_count/total*100:.1f}% |')
            report_lines.append(f'| L3专业标准层 | {l3_count} | {l3_count/total*100:.1f}% |')
        else:
            report_lines.append('| L1文件系统层 | 0 | 0.0% |')
            report_lines.append('| L2文档内容层 | 0 | 0.0% |')
            report_lines.append('| L3专业标准层 | 0 | 0.0% |')
        
        report_lines.append('')
        
        report_lines.append('### 1.2 严重程度分布')
        report_lines.append('')
        report_lines.append('| 严重程度 | 数量 | 占比 |')
        report_lines.append('|----------|------|------|')
        
        severe_count = len([i for i in self.audit_issues if i.severity == '严重'])
        high_count = len([i for i in self.audit_issues if i.severity == '高'])
        medium_count = len([i for i in self.audit_issues if i.severity == '中'])
        low_count = len([i for i in self.audit_issues if i.severity == '低'])
        
        if total > 0:
            report_lines.append(f'| 严重 | {severe_count} | {severe_count/total*100:.1f}% |')
            report_lines.append(f'| 高 | {high_count} | {high_count/total*100:.1f}% |')
            report_lines.append(f'| 中 | {medium_count} | {medium_count/total*100:.1f}% |')
            report_lines.append(f'| 低 | {low_count} | {low_count/total*100:.1f}% |')
        else:
            report_lines.append('| 严重 | 0 | 0.0% |')
            report_lines.append('| 高 | 0 | 0.0% |')
            report_lines.append('| 中 | 0 | 0.0% |')
            report_lines.append('| 低 | 0 | 0.0% |')
        
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📝 二、L1文件系统层审计结果')
        report_lines.append('')
        
        l1_issues = [i for i in self.audit_issues if i.level == 'L1']
        if l1_issues:
            for issue in l1_issues:
                severity_emoji = {'严重': '🔴', '高': '🟠', '中': '🟡', '低': '🟢'}.get(issue.severity, '⚪')
                report_lines.append(f'### {severity_emoji} {issue.category} - {issue.severity}')
                report_lines.append('')
                report_lines.append(f'**问题描述**: {issue.description}')
                report_lines.append(f'**文件位置**: {issue.filepath}')
                report_lines.append(f'**改进建议**: {issue.recommendation}')
                report_lines.append('')
        else:
            report_lines.append('✅ 未发现L1文件系统层问题')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📝 三、L2文档内容层审计结果')
        report_lines.append('')
        
        l2_issues = [i for i in self.audit_issues if i.level == 'L2']
        if l2_issues:
            for issue in l2_issues:
                severity_emoji = {'严重': '🔴', '高': '🟠', '中': '🟡', '低': '🟢'}.get(issue.severity, '⚪')
                report_lines.append(f'### {severity_emoji} {issue.category} - {issue.severity}')
                report_lines.append('')
                report_lines.append(f'**问题描述**: {issue.description}')
                report_lines.append(f'**文件位置**: {issue.filepath}')
                report_lines.append(f'**改进建议**: {issue.recommendation}')
                report_lines.append('')
        else:
            report_lines.append('✅ 未发现L2文档内容层问题')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📝 四、L3专业标准层审计结果')
        report_lines.append('')
        
        l3_issues = [i for i in self.audit_issues if i.level == 'L3']
        if l3_issues:
            for issue in l3_issues:
                severity_emoji = {'严重': '🔴', '高': '🟠', '中': '🟡', '低': '🟢'}.get(issue.severity, '⚪')
                report_lines.append(f'### {severity_emoji} {issue.category} - {issue.severity}')
                report_lines.append('')
                report_lines.append(f'**问题描述**: {issue.description}')
                report_lines.append(f'**文件位置**: {issue.filepath}')
                report_lines.append(f'**改进建议**: {issue.recommendation}')
                report_lines.append('')
        else:
            report_lines.append('✅ 未发现L3专业标准层问题')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🔄 五、重复内容检测结果')
        report_lines.append('')
        
        if self.duplicate_pairs:
            report_lines.append(f'发现 {len(self.duplicate_pairs)} 对职责描述高度相似的文档：')
            report_lines.append('')
            for file1, file2, similarity in self.duplicate_pairs:
                report_lines.append(f'- **{file1}** <-> **{file2}**: 相似度 {similarity:.1%}')
            report_lines.append('')
        else:
            report_lines.append('✅ 未发现职责描述高度相似的文档')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## ⚠️ 六、职责不清问题检测结果')
        report_lines.append('')
        
        if self.responsibility_issues:
            report_lines.append(f'发现 {len(self.responsibility_issues)} 个职责不清问题：')
            report_lines.append('')
            for filename, issue in self.responsibility_issues:
                report_lines.append(f'- **{filename}**: {issue}')
            report_lines.append('')
        else:
            report_lines.append('✅ 所有文档职责描述清晰')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🎯 七、改进建议')
        report_lines.append('')
        
        high_priority = [i for i in self.audit_issues if i.severity in ['严重', '高']]
        medium_priority = [i for i in self.audit_issues if i.severity == '中']
        low_priority = [i for i in self.audit_issues if i.severity == '低']
        
        if high_priority:
            report_lines.append('### 立即处理（高优先级）')
            report_lines.append('')
            for i, issue in enumerate(high_priority, 1):
                report_lines.append(f'{i}. {issue.description} - {issue.recommendation}')
            report_lines.append('')
        
        if medium_priority:
            report_lines.append('### 近期改进（中优先级）')
            report_lines.append('')
            for i, issue in enumerate(medium_priority, 1):
                report_lines.append(f'{i}. {issue.description} - {issue.recommendation}')
            report_lines.append('')
        
        if low_priority:
            report_lines.append('### 持续优化（低优先级）')
            report_lines.append('')
            for i, issue in enumerate(low_priority, 1):
                report_lines.append(f'{i}. {issue.description} - {issue.recommendation}')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        report_lines.append(f'**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        report_content = '\n'.join(report_lines)
        
        output_path = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_DEEP_AUDIT_REPORT_v2_20260407.md')
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
        print(f'  重复内容: {len(self.duplicate_pairs)}对')
        print(f'  职责不清: {len(self.responsibility_issues)}个')
        
        if self.audit_issues:
            print()
            print('问题分布:')
            print(f'  L1文件系统层: {len([i for i in self.audit_issues if i.level == "L1"])}')
            print(f'  L2文档内容层: {len([i for i in self.audit_issues if i.level == "L2"])}')
            print(f'  L3专业标准层: {len([i for i in self.audit_issues if i.level == "L3"])}')


def main():
    auditor = Layer9DeepAuditor()
    auditor.run_full_audit()


if __name__ == '__main__':
    main()
