#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 5 策略执行层深度内容审计工具
检查每个文档的每一个内容，重点检查重复和职责不清的问题
"""

import re
import json
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher


class Layer5DeepContentAuditor:
    """Layer 5深度内容审计器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.documents = {}
        self.issues = []
        self.duplicates = []
        self.responsibility_issues = []
        
        self.similarity_threshold = 0.75
        
    def get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def read_document(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        return f.read()
                except Exception as e:
                    print(f'  ❌ 无法读取文件 {file_path.name}: {e}')
                    return ""
    
    def extract_yaml_header(self, content: str) -> dict:
        yaml_data = {}
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    yaml_data[key.strip()] = value.strip()
        return yaml_data
    
    def extract_core_positioning(self, content: str) -> str:
        pattern = r'##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def extract_sections(self, content: str) -> dict:
        sections = {}
        pattern = r'^##\s+(.+?)\s*\n\n(.+?)(?=\n##|\Z)'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            section_title = match.group(1).strip()
            section_content = match.group(2).strip()
            sections[section_title] = section_content
        return sections
    
    def check_yaml_header(self, filename: str, content: str) -> list:
        issues = []
        yaml_data = self.extract_yaml_header(content)
        
        if not yaml_data:
            issues.append({
                'file': filename,
                'type': 'YAML头部缺失',
                'severity': '高',
                'description': '文档缺少YAML头部元数据',
                'suggestion': '添加标准YAML头部，包含module_id、version、status等字段'
            })
            return issues
        
        required_fields = ['module_id', 'version', 'status', 'layer']
        for field in required_fields:
            if field not in yaml_data:
                issues.append({
                    'file': filename,
                    'type': f'YAML字段缺失',
                    'severity': '中',
                    'description': f'YAML头部缺少{field}字段',
                    'suggestion': f'添加{field}字段到YAML头部'
                })
        
        return issues
    
    def check_responsibility(self, filename: str, content: str) -> list:
        issues = []
        responsibility = self.extract_core_positioning(content)
        
        if not responsibility:
            issues.append({
                'file': filename,
                'type': '职责描述缺失',
                'severity': '高',
                'description': '文档缺少核心定位章节',
                'suggestion': '添加核心定位章节，明确文档职责'
            })
            return issues
        
        if len(responsibility) < 50:
            issues.append({
                'file': filename,
                'type': '职责描述过短',
                'severity': '中',
                'description': f'职责描述仅{len(responsibility)}字，过于简短',
                'suggestion': '扩展职责描述至50-200字'
            })
        elif len(responsibility) > 200:
            issues.append({
                'file': filename,
                'type': '职责描述过长',
                'severity': '中',
                'description': f'职责描述{len(responsibility)}字，过于冗长',
                'suggestion': '精简职责描述至50-200字'
            })
        
        if '负责' not in responsibility and '提供' not in responsibility and '实现' not in responsibility:
            issues.append({
                'file': filename,
                'type': '职责描述不规范',
                'severity': '低',
                'description': '职责描述缺少关键词（负责/提供/实现）',
                'suggestion': '使用标准职责描述格式'
            })
        
        return issues
    
    def check_content_structure(self, filename: str, content: str) -> list:
        issues = []
        sections = self.extract_sections(content)
        
        required_sections = ['核心定位', '设计目标', '核心功能', '实现方案']
        for section in required_sections:
            if section not in sections:
                issues.append({
                    'file': filename,
                    'type': '章节缺失',
                    'severity': '中',
                    'description': f'文档缺少{section}章节',
                    'suggestion': f'添加{section}章节，完善文档结构'
                })
        
        return issues
    
    def check_content_quality(self, filename: str, content: str) -> list:
        issues = []
        
        if len(content) < 500:
            issues.append({
                'file': filename,
                'type': '内容过短',
                'severity': '中',
                'description': f'文档内容仅{len(content)}字，过于简短',
                'suggestion': '扩展文档内容，提供更详细的信息'
            })
        
        if content.count('\n') < 20:
            issues.append({
                'file': filename,
                'type': '结构简单',
                'severity': '低',
                'description': '文档结构过于简单，缺少详细章节',
                'suggestion': '增加章节划分，提高文档可读性'
            })
        
        code_blocks = len(re.findall(r'```', content))
        if code_blocks == 0:
            issues.append({
                'file': filename,
                'type': '缺少代码示例',
                'severity': '低',
                'description': '文档缺少代码示例',
                'suggestion': '添加代码示例，提高文档实用性'
            })
        
        return issues
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        return SequenceMatcher(None, text1, text2).ratio()
    
    def check_duplicates(self):
        print('  检查重复内容...')
        
        files = list(self.blueprints_dir.glob('*_BLUEPRINT.md'))
        
        for i, file1 in enumerate(files):
            for file2 in files[i+1:]:
                content1 = self.documents.get(file1.name, {}).get('content', '')
                content2 = self.documents.get(file2.name, {}).get('content', '')
                
                if not content1 or not content2:
                    continue
                
                resp1 = self.extract_core_positioning(content1)
                resp2 = self.extract_core_positioning(content2)
                
                if resp1 and resp2:
                    similarity = self.calculate_similarity(resp1, resp2)
                    if similarity > self.similarity_threshold:
                        self.duplicates.append({
                            'file1': file1.name,
                            'file2': file2.name,
                            'similarity': f'{similarity:.1%}',
                            'type': '职责描述相似',
                            'severity': '高' if similarity > 0.85 else '中',
                            'description': f'职责描述相似度{similarity:.1%}，存在重复嫌疑',
                            'suggestion': '优化职责描述，突出各自特色'
                        })
                
                sections1 = self.extract_sections(content1)
                sections2 = self.extract_sections(content2)
                
                for section_name in sections1:
                    if section_name in sections2:
                        section_similarity = self.calculate_similarity(
                            sections1[section_name],
                            sections2[section_name]
                        )
                        if section_similarity > 0.85:
                            self.duplicates.append({
                                'file1': file1.name,
                                'file2': file2.name,
                                'similarity': f'{section_similarity:.1%}',
                                'type': f'{section_name}章节相似',
                                'severity': '高',
                                'description': f'{section_name}章节相似度{section_similarity:.1%}，存在重复',
                                'suggestion': f'差异化{section_name}章节内容'
                            })
    
    def audit_document(self, file_path: Path):
        filename = file_path.name
        print(f'  审计 {filename}...')
        
        content = self.read_document(file_path)
        if not content:
            return
        
        self.documents[filename] = {
            'content': content,
            'yaml': self.extract_yaml_header(content),
            'responsibility': self.extract_core_positioning(content),
            'sections': self.extract_sections(content)
        }
        
        issues = []
        issues.extend(self.check_yaml_header(filename, content))
        issues.extend(self.check_responsibility(filename, content))
        issues.extend(self.check_content_structure(filename, content))
        issues.extend(self.check_content_quality(filename, content))
        
        self.issues.extend(issues)
    
    def run(self):
        print('=' * 80)
        print('Layer 5 策略执行层深度内容审计工具')
        print('=' * 80)
        print(f'审计时间: {self._get_timestamp()}')
        print()
        
        print('扫描文档文件...')
        files = list(self.blueprints_dir.glob('*_BLUEPRINT.md'))
        print(f'  找到 {len(files)} 个文档')
        print()
        
        print('审计每个文档...')
        for file_path in files:
            self.audit_document(file_path)
        print()
        
        self.check_duplicates()
        
        print('生成审计报告...')
        self._generate_report()
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('审计完成')
        print('=' * 80)
        print()
        self._print_summary()
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _print_summary(self):
        total_issues = len(self.issues) + len(self.duplicates)
        high_severity = len([i for i in self.issues if i.get('severity') == '高'])
        high_severity += len([d for d in self.duplicates if d.get('severity') == '高'])
        
        print('审计摘要:')
        print(f'  审计文档: {len(self.documents)}个')
        print(f'  发现问题: {total_issues}个')
        print(f'  高严重度: {high_severity}个')
        print(f'  重复内容: {len(self.duplicates)}对')
    
    def _generate_report(self):
        report_path = self.audit_dir / 'LAYER5_DEEP_CONTENT_AUDIT_REPORT_20260407.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 策略执行层深度内容审计报告\n\n')
            f.write(f'> **审计时间**: {self._get_timestamp()}\n')
            f.write(f'> **审计范围**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS\n')
            f.write(f'> **审计标准**: 专业量化机构五大原则 + 三层审计标准\n')
            f.write(f'> **审计类型**: 深度内容审计（逐文档逐内容）\n\n')
            f.write('---\n\n')
            
            f.write('## 📊 一、审计概要\n\n')
            f.write(f'**审计文档数**: {len(self.documents)}个\n')
            f.write(f'**发现问题数**: {len(self.issues) + len(self.duplicates)}个\n')
            f.write(f'**重复内容对**: {len(self.duplicates)}对\n\n')
            
            f.write('### 1.1 问题分布\n\n')
            f.write('| 问题类型 | 数量 | 占比 |\n')
            f.write('|----------|------|------|\n')
            
            issue_types = {}
            for issue in self.issues:
                issue_type = issue['type']
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                percentage = count / len(self.issues) * 100 if self.issues else 0
                f.write(f'| {issue_type} | {count} | {percentage:.1f}% |\n')
            
            f.write('\n### 1.2 严重程度分布\n\n')
            f.write('| 严重程度 | 数量 | 占比 |\n')
            f.write('|----------|------|------|\n')
            
            severity_counts = {'高': 0, '中': 0, '低': 0}
            for issue in self.issues:
                severity = issue.get('severity', '低')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            for duplicate in self.duplicates:
                severity = duplicate.get('severity', '低')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            total = sum(severity_counts.values())
            for severity, count in severity_counts.items():
                percentage = count / total * 100 if total > 0 else 0
                f.write(f'| {severity} | {count} | {percentage:.1f}% |\n')
            
            f.write('\n---\n\n')
            
            f.write('## 🔴 二、高严重度问题\n\n')
            high_issues = [i for i in self.issues if i.get('severity') == '高']
            high_duplicates = [d for d in self.duplicates if d.get('severity') == '高']
            
            if high_issues:
                for i, issue in enumerate(high_issues, 1):
                    f.write(f'### 问题 {i}: {issue["type"]}\n\n')
                    f.write(f'**文件**: {issue["file"]}\n\n')
                    f.write(f'**描述**: {issue["description"]}\n\n')
                    f.write(f'**建议**: {issue["suggestion"]}\n\n')
                    f.write('---\n\n')
            
            if high_duplicates:
                for i, duplicate in enumerate(high_duplicates, 1):
                    f.write(f'### 重复问题 {i}: {duplicate["type"]}\n\n')
                    f.write(f'**文件1**: {duplicate["file1"]}\n\n')
                    f.write(f'**文件2**: {duplicate["file2"]}\n\n')
                    f.write(f'**相似度**: {duplicate["similarity"]}\n\n')
                    f.write(f'**描述**: {duplicate["description"]}\n\n')
                    f.write(f'**建议**: {duplicate["suggestion"]}\n\n')
                    f.write('---\n\n')
            
            f.write('## 🟡 三、中严重度问题\n\n')
            medium_issues = [i for i in self.issues if i.get('severity') == '中']
            
            if medium_issues:
                f.write('| 文件名称 | 问题类型 | 描述 | 建议 |\n')
                f.write('|----------|----------|------|------|\n')
                for issue in medium_issues:
                    f.write(f"| {issue['file']} | {issue['type']} | {issue['description']} | {issue['suggestion']} |\n")
                f.write('\n---\n\n')
            
            f.write('## 🟢 四、低严重度问题\n\n')
            low_issues = [i for i in self.issues if i.get('severity') == '低']
            
            if low_issues:
                f.write('| 文件名称 | 问题类型 | 描述 | 建议 |\n')
                f.write('|----------|----------|------|------|\n')
                for issue in low_issues:
                    f.write(f"| {issue['file']} | {issue['type']} | {issue['description']} | {issue['suggestion']} |\n")
                f.write('\n---\n\n')
            
            f.write('## 📋 五、文档质量统计\n\n')
            f.write('| 文档名称 | YAML完整性 | 职责描述 | 章节数 | 内容长度 | 质量评分 |\n')
            f.write('|----------|-----------|----------|--------|----------|----------|\n')
            
            for filename, doc_data in sorted(self.documents.items()):
                yaml_complete = '✅' if doc_data['yaml'] else '❌'
                responsibility = doc_data['responsibility']
                resp_status = f'{len(responsibility)}字' if responsibility else '❌'
                sections_count = len(doc_data['sections'])
                content_length = len(doc_data['content'])
                
                quality_score = 0
                if doc_data['yaml']:
                    quality_score += 20
                if responsibility and 50 <= len(responsibility) <= 200:
                    quality_score += 30
                if sections_count >= 4:
                    quality_score += 20
                if content_length >= 1000:
                    quality_score += 30
                
                quality_stars = '⭐' * (quality_score // 20)
                
                f.write(f"| {filename} | {yaml_complete} | {resp_status} | {sections_count} | {content_length}字 | {quality_stars} |\n")
            
            f.write('\n---\n\n')
            
            f.write('## 🎯 六、改进建议\n\n')
            f.write('### 6.1 立即处理\n\n')
            
            if high_issues or high_duplicates:
                f.write('**高严重度问题**:\n')
                if high_issues:
                    f.write(f'- 修复{len(high_issues)}个高严重度问题\n')
                if high_duplicates:
                    f.write(f'- 处理{len(high_duplicates)}对高相似度文档\n')
            else:
                f.write('- 无高严重度问题需要立即处理\n')
            
            f.write('\n### 6.2 近期改进\n\n')
            
            if medium_issues:
                f.write(f'- 修复{len(medium_issues)}个中严重度问题\n')
            
            f.write('- 优化职责描述长度\n')
            f.write('- 完善文档结构\n')
            f.write('- 添加代码示例\n')
            
            f.write('\n### 6.3 长期优化\n\n')
            f.write('- 建立文档质量持续监控机制\n')
            f.write('- 定期运行深度审计工具\n')
            f.write('- 优化文档创建流程\n')
            
            f.write('\n---\n\n')
            
            f.write('## 📊 七、审计质量声明\n\n')
            f.write('### 7.1 审计覆盖\n\n')
            f.write(f'- **文档覆盖率**: 100% ({len(self.documents)}/{len(list(self.blueprints_dir.glob("*_BLUEPRINT.md")))}个文档)\n')
            f.write('- **内容检查项**: YAML头部、职责描述、章节结构、内容质量、重复检测\n')
            f.write('- **审计深度**: 逐文档逐内容检查\n\n')
            
            f.write('### 7.2 审计局限性\n\n')
            f.write('- 本审计为自动化审计，可能存在误报\n')
            f.write('- 建议结合人工审查确认问题\n')
            f.write('- 特殊情况需要专业判断\n\n')
            
            f.write(f'**审计完成时间**: {self._get_timestamp()}\n')
            f.write('**审计工具版本**: v1.0\n')
            f.write('**审计状态**: ✅ **完成**\n')


def main():
    auditor = Layer5DeepContentAuditor()
    auditor.run()


if __name__ == '__main__':
    main()
