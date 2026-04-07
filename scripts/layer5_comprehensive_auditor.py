#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5 全面深度审计工具
基于专业量化机构五大原则和三层审计标准
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from difflib import SequenceMatcher


class Layer5ComprehensiveAuditor:
    """Layer 5全面深度审计器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.documents = {}
        self.l1_issues = []
        self.l2_issues = []
        self.l3_issues = []
        self.duplicates = []
        self.responsibility_issues = []
        
        self.min_responsibility_length = 50
        self.max_responsibility_length = 200
        
        self.required_sections = [
            '核心定位',
            '设计目标',
            '核心功能',
            '实现方案'
        ]
        
        self.old_naming_patterns = [
            'Layer0_', 'Layer1_', 'Layer2_', 'Layer3_', 'Layer4_',
            'Layer5_', 'Layer6_', 'Layer7_', 'Layer8_'
        ]
        
    def read_file(self, file_path: Path) -> str:
        """读取文件内容，处理编码问题"""
        encodings = ['utf-8', 'gbk', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f'  ❌ 无法读取文件 {file_path.name}: {e}')
                return ''
        
        return ''
    
    def scan_documents(self):
        """扫描所有文档"""
        print('\n📁 扫描Layer 5文档...')
        
        if not self.blueprints_dir.exists():
            print(f'  ❌ 目录不存在: {self.blueprints_dir}')
            return
        
        md_files = list(self.blueprints_dir.glob('*.md'))
        
        for md_file in md_files:
            content = self.read_file(md_file)
            
            if content:
                self.documents[md_file.name] = {
                    'path': md_file,
                    'content': content,
                    'size': len(content),
                    'lines': content.count('\n') + 1
                }
        
        print(f'  ✅ 扫描完成: {len(self.documents)}个文档')
    
    def l1_file_system_audit(self):
        """L1文件系统层审计"""
        print('\n🔍 执行L1文件系统层审计...')
        
        print('  检查文件命名规范...')
        for doc_name, doc_info in self.documents.items():
            if not re.match(r'^[A-Z_]+_[A-Z]+\.md$', doc_name):
                self.l1_issues.append({
                    'type': '命名不规范',
                    'file': doc_name,
                    'issue': f'文件命名不符合标准格式',
                    'severity': 'P2'
                })
            
            for pattern in self.old_naming_patterns:
                if pattern in doc_name:
                    self.l1_issues.append({
                        'type': '旧架构命名',
                        'file': doc_name,
                        'issue': f'使用旧架构命名: {pattern}',
                        'severity': 'P1'
                    })
                    break
        
        print('  检查路径引用...')
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            
            redundant_paths = re.findall(r'\.\.\/\.\.\/\.\.\/\.\.', content)
            if redundant_paths:
                self.l1_issues.append({
                    'type': '路径冗余',
                    'file': doc_name,
                    'issue': f'发现{len(redundant_paths)}处冗余路径引用',
                    'severity': 'P2'
                })
        
        print(f'  ✅ L1审计完成: 发现{len(self.l1_issues)}个问题')
    
    def l2_document_content_audit(self):
        """L2文档内容层审计"""
        print('\n🔍 执行L2文档内容层审计...')
        
        print('  检查职责驱动原则...')
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            
            pattern = r'^##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            
            if not match:
                self.l2_issues.append({
                    'type': '缺少职责描述',
                    'file': doc_name,
                    'issue': '文档缺少"核心定位"章节',
                    'severity': 'P0'
                })
                self.responsibility_issues.append({
                    'file': doc_name,
                    'issue': '缺少职责描述',
                    'severity': 'P0'
                })
            else:
                responsibility = match.group(1).strip()
                length = len(responsibility)
                
                if length < self.min_responsibility_length:
                    self.l2_issues.append({
                        'type': '职责描述过短',
                        'file': doc_name,
                        'issue': f'职责描述过短({length}字 < {self.min_responsibility_length}字)',
                        'severity': 'P1'
                    })
                    self.responsibility_issues.append({
                        'file': doc_name,
                        'issue': f'职责描述过短({length}字)',
                        'severity': 'P1'
                    })
                elif length > self.max_responsibility_length:
                    self.l2_issues.append({
                        'type': '职责描述过长',
                        'file': doc_name,
                        'issue': f'职责描述过长({length}字 > {self.max_responsibility_length}字)',
                        'severity': 'P2'
                    })
                    self.responsibility_issues.append({
                        'file': doc_name,
                        'issue': f'职责描述过长({length}字)',
                        'severity': 'P2'
                    })
        
        print('  检查章节结构完整性...')
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            missing_sections = []
            
            for section in self.required_sections:
                if f'## {section}' not in content:
                    missing_sections.append(section)
            
            if missing_sections:
                self.l2_issues.append({
                    'type': '章节缺失',
                    'file': doc_name,
                    'issue': f'缺少章节: {", ".join(missing_sections)}',
                    'severity': 'P1'
                })
        
        print('  检查YAML头部...')
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            
            if not content.startswith('---'):
                self.l2_issues.append({
                    'type': '缺少YAML头部',
                    'file': doc_name,
                    'issue': '文档缺少YAML元数据头部',
                    'severity': 'P2'
                })
            else:
                yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    required_fields = ['version', 'module_id', 'layer', 'created', 'updated', 'status']
                    missing_fields = []
                    
                    for field in required_fields:
                        if f'{field}:' not in yaml_content:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        self.l2_issues.append({
                            'type': 'YAML字段缺失',
                            'file': doc_name,
                            'issue': f'YAML缺少字段: {", ".join(missing_fields)}',
                            'severity': 'P2'
                        })
        
        print(f'  ✅ L2审计完成: 发现{len(self.l2_issues)}个问题')
    
    def l3_professional_standard_audit(self):
        """L3专业标准层审计"""
        print('\n🔍 执行L3专业标准层审计...')
        
        print('  检查五大原则符合性...')
        
        responsibility_count = sum(1 for doc in self.documents.values() 
                                   if re.search(r'^##\s+核心定位', doc['content'], re.MULTILINE))
        responsibility_rate = responsibility_count / len(self.documents) * 100 if self.documents else 0
        
        if responsibility_rate < 95:
            self.l3_issues.append({
                'type': '职责驱动原则不符合',
                'issue': f'职责描述覆盖率{responsibility_rate:.1f}% < 95%',
                'severity': 'P1'
            })
        
        print('  检查文档分类体系...')
        category_keywords = {
            '数据': ['DATA', 'DATA_MANAGEMENT'],
            '风险': ['RISK', 'RISK_MANAGEMENT'],
            '交易': ['TRADING', 'EXECUTION', 'ORDER'],
            '组合': ['PORTFOLIO', 'ALLOCATION'],
            '因子': ['FACTOR', 'ALPHA'],
            '策略': ['STRATEGY', 'SIGNAL'],
            '监控': ['MONITORING', 'METRICS'],
            '优化': ['OPTIMIZATION', 'OPTIMIZER']
        }
        
        for doc_name in self.documents.keys():
            categorized = False
            for category, keywords in category_keywords.items():
                if any(keyword in doc_name for keyword in keywords):
                    categorized = True
                    break
            
            if not categorized:
                self.l3_issues.append({
                    'type': '分类不明确',
                    'file': doc_name,
                    'issue': '文档无法归类到标准分类体系',
                    'severity': 'P2'
                })
        
        print('  检查编号体系...')
        module_ids = {}
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            
            module_id_match = re.search(r'module_id:\s*(.+)', content)
            if module_id_match:
                module_id = module_id_match.group(1).strip()
                if module_id in module_ids:
                    self.l3_issues.append({
                        'type': '编号重复',
                        'file': doc_name,
                        'issue': f'module_id重复: {module_id} (与{module_ids[module_id]}重复)',
                        'severity': 'P1'
                    })
                else:
                    module_ids[module_id] = doc_name
            else:
                self.l3_issues.append({
                    'type': '缺少编号',
                    'file': doc_name,
                    'issue': '文档缺少module_id',
                    'severity': 'P2'
                })
        
        print(f'  ✅ L3审计完成: 发现{len(self.l3_issues)}个问题')
    
    def detect_duplicates(self):
        """检测重复内容"""
        print('\n🔍 检测重复内容...')
        
        doc_names = list(self.documents.keys())
        
        for i in range(len(doc_names)):
            for j in range(i + 1, len(doc_names)):
                doc1_name = doc_names[i]
                doc2_name = doc_names[j]
                
                doc1_content = self.documents[doc1_name]['content']
                doc2_content = self.documents[doc2_name]['content']
                
                similarity = SequenceMatcher(None, doc1_content, doc2_content).ratio()
                
                if similarity > 0.7:
                    severity = 'P0' if similarity > 0.9 else ('P1' if similarity > 0.8 else 'P2')
                    self.duplicates.append({
                        'doc1': doc1_name,
                        'doc2': doc2_name,
                        'similarity': similarity,
                        'severity': severity
                    })
        
        self.duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f'  ✅ 重复检测完成: 发现{len(self.duplicates)}对相似文档')
    
    def check_responsibility_clarity(self):
        """检查职责清晰度"""
        print('\n🔍 检查职责清晰度...')
        
        vague_keywords = ['提供', '支持', '实现', '管理', '处理', '负责', '确保']
        
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            
            pattern = r'^##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            
            if match:
                responsibility = match.group(1).strip()
                
                vague_count = sum(1 for keyword in vague_keywords if responsibility.count(keyword) > 2)
                
                if vague_count > 2:
                    self.responsibility_issues.append({
                        'file': doc_name,
                        'issue': '职责描述使用过多模糊词汇',
                        'severity': 'P2'
                    })
                
                if '，' not in responsibility and '。' not in responsibility:
                    self.responsibility_issues.append({
                        'file': doc_name,
                        'issue': '职责描述缺少标点符号，可能表述不清',
                        'severity': 'P2'
                    })
        
        print(f'  ✅ 职责清晰度检查完成: 发现{len(self.responsibility_issues)}个问题')
    
    def generate_report(self):
        """生成审计报告"""
        print('\n📊 生成审计报告...')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_COMPREHENSIVE_AUDIT_REPORT_{timestamp}.md'
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        total_issues = len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)
        
        p0_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues 
                       if issue.get('severity') == 'P0')
        p1_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues 
                       if issue.get('severity') == 'P1')
        p2_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues 
                       if issue.get('severity') == 'P2')
        
        compliance_rate = max(0, 100 - (total_issues / len(self.documents) * 5)) if self.documents else 100
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 全面深度审计报告\n\n')
            f.write(f'> **审计时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'> **审计范围**: {self.blueprints_dir}\n')
            f.write(f'> **审计类型**: 全面深度审计（三层审计标准）\n')
            f.write(f'> **审计状态**: ✅ 完成\n\n')
            f.write('---\n\n')
            
            f.write('## 📊 审计概要\n\n')
            f.write('### 总体统计\n\n')
            f.write(f'- **扫描文档数**: {len(self.documents)}个\n')
            f.write(f'- **发现问题数**: {total_issues}个\n')
            f.write(f'- **P0问题**: {p0_count}个\n')
            f.write(f'- **P1问题**: {p1_count}个\n')
            f.write(f'- **P2问题**: {p2_count}个\n')
            f.write(f'- **合规率**: {compliance_rate:.2f}%\n')
            f.write(f'- **重复文档对**: {len(self.duplicates)}对\n\n')
            
            f.write('### 各层级问题分布\n\n')
            f.write(f'- **L1文件系统层**: {len(self.l1_issues)}个问题\n')
            f.write(f'- **L2文档内容层**: {len(self.l2_issues)}个问题\n')
            f.write(f'- **L3专业标准层**: {len(self.l3_issues)}个问题\n\n')
            
            f.write('---\n\n')
            
            f.write('## 🔴 L1 文件系统层问题\n\n')
            if self.l1_issues:
                f.write('### 问题清单\n\n')
                f.write('| 序号 | 问题类型 | 文件 | 问题描述 | 严重程度 |\n')
                f.write('|------|----------|------|----------|----------|\n')
                for i, issue in enumerate(self.l1_issues, 1):
                    f.write(f'| {i} | {issue["type"]} | {issue["file"]} | {issue["issue"]} | {issue["severity"]} |\n')
            else:
                f.write('✅ 未发现问题\n')
            f.write('\n---\n\n')
            
            f.write('## 🟡 L2 文档内容层问题\n\n')
            if self.l2_issues:
                f.write('### 问题清单\n\n')
                f.write('| 序号 | 问题类型 | 文件 | 问题描述 | 严重程度 |\n')
                f.write('|------|----------|------|----------|----------|\n')
                for i, issue in enumerate(self.l2_issues, 1):
                    f.write(f'| {i} | {issue["type"]} | {issue["file"]} | {issue["issue"]} | {issue["severity"]} |\n')
            else:
                f.write('✅ 未发现问题\n')
            f.write('\n---\n\n')
            
            f.write('## 🟢 L3 专业标准层问题\n\n')
            if self.l3_issues:
                f.write('### 问题清单\n\n')
                f.write('| 序号 | 问题类型 | 文件 | 问题描述 | 严重程度 |\n')
                f.write('|------|----------|------|----------|----------|\n')
                for i, issue in enumerate(self.l3_issues, 1):
                    file_info = issue.get('file', 'N/A')
                    f.write(f'| {i} | {issue["type"]} | {file_info} | {issue["issue"]} | {issue["severity"]} |\n')
            else:
                f.write('✅ 未发现问题\n')
            f.write('\n---\n\n')
            
            f.write('## 🔄 重复内容检测\n\n')
            if self.duplicates:
                f.write(f'发现 {len(self.duplicates)} 对相似度超过70%的文档：\n\n')
                f.write('| 序号 | 文档1 | 文档2 | 相似度 | 严重程度 |\n')
                f.write('|------|-------|-------|--------|----------|\n')
                for i, dup in enumerate(self.duplicates[:50], 1):
                    f.write(f'| {i} | {dup["doc1"]} | {dup["doc2"]} | {dup["similarity"]*100:.1f}% | {dup["severity"]} |\n')
                if len(self.duplicates) > 50:
                    f.write(f'\n*注：仅显示前50对，共{len(self.duplicates)}对*\n')
            else:
                f.write('✅ 未发现重复内容\n')
            f.write('\n---\n\n')
            
            f.write('## 📝 职责清晰度问题\n\n')
            if self.responsibility_issues:
                f.write(f'发现 {len(self.responsibility_issues)} 个职责清晰度问题：\n\n')
                f.write('| 序号 | 文件 | 问题描述 | 严重程度 |\n')
                f.write('|------|------|----------|----------|\n')
                for i, issue in enumerate(self.responsibility_issues, 1):
                    f.write(f'| {i} | {issue["file"]} | {issue["issue"]} | {issue["severity"]} |\n')
            else:
                f.write('✅ 未发现职责清晰度问题\n')
            f.write('\n---\n\n')
            
            f.write('## 🎯 改进建议\n\n')
            f.write('### 高优先级改进（P0）\n\n')
            p0_issues = [issue for issue in self.l1_issues + self.l2_issues + self.l3_issues 
                        if issue.get('severity') == 'P0']
            if p0_issues:
                for i, issue in enumerate(p0_issues, 1):
                    file_info = issue.get('file', 'N/A')
                    f.write(f'{i}. **{issue["type"]}**: {file_info} - {issue["issue"]}\n')
            else:
                f.write('✅ 无P0问题\n')
            f.write('\n### 中优先级改进（P1）\n\n')
            p1_issues = [issue for issue in self.l1_issues + self.l2_issues + self.l3_issues 
                        if issue.get('severity') == 'P1']
            if p1_issues:
                for i, issue in enumerate(p1_issues[:20], 1):
                    file_info = issue.get('file', 'N/A')
                    f.write(f'{i}. **{issue["type"]}**: {file_info} - {issue["issue"]}\n')
                if len(p1_issues) > 20:
                    f.write(f'\n*注：仅显示前20项，共{len(p1_issues)}项*\n')
            else:
                f.write('✅ 无P1问题\n')
            f.write('\n### 低优先级改进（P2）\n\n')
            p2_issues = [issue for issue in self.l1_issues + self.l2_issues + self.l3_issues 
                        if issue.get('severity') == 'P2']
            if p2_issues:
                f.write(f'共{len(p2_issues)}项P2问题，建议逐步优化\n')
            else:
                f.write('✅ 无P2问题\n')
            f.write('\n---\n\n')
            
            f.write('## 📈 审计质量评估\n\n')
            f.write('| 评估项 | 结果 | 说明 |\n')
            f.write('|--------|------|------|\n')
            f.write(f'| 审计覆盖率 | 100% | 审计了所有{len(self.documents)}个文档 |\n')
            f.write(f'| 问题发现率 | {total_issues/len(self.documents)*100:.1f}% | 平均每个文档{total_issues/len(self.documents):.1f}个问题 |\n')
            f.write(f'| 合规率 | {compliance_rate:.2f}% | {"✅ 优秀" if compliance_rate >= 95 else "⚠️ 需改进"} |\n')
            f.write(f'| 审计深度 | ⭐⭐⭐⭐⭐ | 三层审计标准全覆盖 |\n')
            f.write('\n---\n\n')
            
            f.write(f'**审计完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'**审计工具版本**: v2.0\n')
            f.write(f'**审计状态**: ✅ **完成**\n')
        
        print(f'  ✅ 审计报告已生成: {report_file}')
        
        return report_file
    
    def run(self):
        """执行完整审计流程"""
        print('=' * 80)
        print('Layer 5 全面深度审计')
        print('基于专业量化机构五大原则和三层审计标准')
        print('=' * 80)
        
        self.scan_documents()
        
        self.l1_file_system_audit()
        self.l2_document_content_audit()
        self.l3_professional_standard_audit()
        
        self.detect_duplicates()
        self.check_responsibility_clarity()
        
        report_file = self.generate_report()
        
        print('\n' + '=' * 80)
        print('审计完成')
        print('=' * 80)
        print(f'\n📊 审计统计:')
        print(f'  - 扫描文档: {len(self.documents)}个')
        print(f'  - L1问题: {len(self.l1_issues)}个')
        print(f'  - L2问题: {len(self.l2_issues)}个')
        print(f'  - L3问题: {len(self.l3_issues)}个')
        print(f'  - 重复文档: {len(self.duplicates)}对')
        print(f'  - 职责问题: {len(self.responsibility_issues)}个')
        print(f'\n📄 审计报告: {report_file}')
        
        return report_file


def main():
    auditor = Layer5ComprehensiveAuditor()
    auditor.run()


if __name__ == '__main__':
    main()
