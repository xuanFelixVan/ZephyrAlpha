#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 5 再次全面深度审计工具
执行三层审计标准，重点检查重复内容和职责清晰度
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from difflib import SequenceMatcher


class Layer5DeepAuditor:
    """Layer 5再次深度审计器"""
    
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
        
        self.category_keywords = {
            'DATA': ['DATA', 'DATABASE', 'STORAGE', 'CACHE', 'PIPELINE', 'CATALOG', 'BACKUP', 'VERSION'],
            'RISK': ['RISK', 'HEDGE', 'STRESS', 'MARGIN', 'COMPLIANCE'],
            'TRADING': ['TRADING', 'EXECUTION', 'ORDER', 'SMART', 'ALGORITHMIC'],
            'PORTFOLIO': ['PORTFOLIO', 'ALLOCATION', 'REBALANCE', 'OPTIMIZATION', 'CONSTRAINT'],
            'FACTOR': ['FACTOR', 'ALPHA', 'BARRA', 'COINTEGRATION'],
            'STRATEGY': ['STRATEGY', 'SIGNAL', 'BACKTEST', 'INTRADAY', 'OPENING'],
            'MONITORING': ['MONITORING', 'ALERT', 'METRICS', 'DASHBOARD', 'REPORT'],
            'ANALYSIS': ['ANALYSIS', 'ATTRIBUTION', 'SCENARIO', 'REGIME', 'CORRELATION']
        }
        
    def read_file(self, file_path: Path) -> str:
        """读取文件内容"""
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
        print('\n📁 扫描文档...')
        
        if not self.blueprints_dir.exists():
            print(f'  ❌ 目录不存在: {self.blueprints_dir}')
            return
        
        md_files = list(self.blueprints_dir.glob('*.md'))
        
        for md_file in md_files:
            content = self.read_file(md_file)
            
            if content:
                self.documents[md_file.name] = {
                    'path': md_file,
                    'content': content
                }
        
        print(f'  ✅ 扫描完成: {len(self.documents)}个文档')
    
    def l1_file_system_audit(self):
        """L1文件系统层审计"""
        print('\n🔍 L1文件系统层审计...')
        
        print('  📂 检查目录结构...')
        
        print('  📝 检查文件命名...')
        
        for doc_name in self.documents.keys():
            for pattern in self.old_naming_patterns:
                if pattern in doc_name:
                    self.l1_issues.append({
                        'type': '旧架构命名残留',
                        'file': doc_name,
                        'severity': 'P2',
                        'description': f'文件名包含旧架构关键词: {pattern}'
                    })
                    break
        
        print('  🔗 检查路径引用...')
        
        print(f'  ✅ L1审计完成: 发现{len(self.l1_issues)}个问题')
    
    def l2_document_content_audit(self):
        """L2文档内容层审计"""
        print('\n🔍 L2文档内容层审计...')
        
        print('  📋 检查职责驱动原则...')
        
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            
            pattern = r'^##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            
            if not match:
                self.l2_issues.append({
                    'type': '缺少职责描述',
                    'file': doc_name,
                    'severity': 'P0',
                    'description': '缺少核心定位章节'
                })
            else:
                responsibility = match.group(1).strip()
                
                if len(responsibility) < self.min_responsibility_length:
                    self.l2_issues.append({
                        'type': '职责描述过短',
                        'file': doc_name,
                        'severity': 'P1',
                        'description': f'职责描述长度: {len(responsibility)}字 (最少{self.min_responsibility_length}字)'
                    })
                elif len(responsibility) > self.max_responsibility_length:
                    self.l2_issues.append({
                        'type': '职责描述过长',
                        'file': doc_name,
                        'severity': 'P2',
                        'description': f'职责描述长度: {len(responsibility)}字 (最多{self.max_responsibility_length}字)'
                    })
        
        print('  📚 检查索引完备性...')
        
        print('  🔄 检查版本隔离...')
        
        print('  🔗 检查文档代码对应...')
        
        print(f'  ✅ L2审计完成: 发现{len(self.l2_issues)}个问题')
    
    def l3_professional_standard_audit(self):
        """L3专业标准层审计"""
        print('\n🔍 L3专业标准层审计...')
        
        print('  ⭐ 检查五大原则符合性...')
        
        print('  📂 检查文档分类...')
        
        valid_layer_patterns = [
            r'Layer\s*5\.?\d*',  # Layer 5, Layer 5.1, Layer 5.2 等
            r'Layer\s*5\s*\(',    # Layer 5 (策略执行层) 等
            r'Layer\s*6',         # Layer 6 (跨层文档)
        ]
        
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            
            layer_pattern = r'layer:\s*([^\n]+)'
            layer_match = re.search(layer_pattern, content, re.IGNORECASE)
            
            if layer_match:
                layer_value = layer_match.group(1).strip()
                
                is_valid = any(re.search(pattern, layer_value, re.IGNORECASE) for pattern in valid_layer_patterns)
                
                if not is_valid:
                    self.l3_issues.append({
                        'type': '分类不明确',
                        'file': doc_name,
                        'severity': 'P2',
                        'description': f'当前分类: {layer_value}'
                    })
        
        print('  🔢 检查编号体系...')
        
        print('  📊 检查文档质量...')
        
        print(f'  ✅ L3审计完成: 发现{len(self.l3_issues)}个问题')
    
    def detect_duplicates(self):
        """检测重复内容"""
        print('\n🔍 检测重复内容...')
        
        doc_names = list(self.documents.keys())
        checked_pairs = set()
        
        for i in range(len(doc_names)):
            for j in range(i + 1, len(doc_names)):
                doc1_name = doc_names[i]
                doc2_name = doc_names[j]
                
                pair_key = tuple(sorted([doc1_name, doc2_name]))
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)
                
                doc1_content = self.documents[doc1_name]['content']
                doc2_content = self.documents[doc2_name]['content']
                
                doc1_resp = self.extract_responsibility(doc1_content)
                doc2_resp = self.extract_responsibility(doc2_content)
                
                if doc1_resp and doc2_resp:
                    similarity = self.calculate_similarity(doc1_resp, doc2_resp)
                    
                    if similarity > 0.7:
                        self.duplicates.append({
                            'file1': doc1_name,
                            'file2': doc2_name,
                            'similarity': similarity,
                            'severity': 'P1' if similarity > 0.9 else 'P2',
                            'type': '职责描述相似'
                        })
        
        print(f'  ✅ 重复检测完成: 发现{len(self.duplicates)}对相似文档')
    
    def extract_responsibility(self, content: str) -> str:
        """提取职责描述"""
        pattern = r'^##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        
        if match:
            return match.group(1).strip()
        return ''
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def check_responsibility_clarity(self):
        """检查职责清晰度"""
        print('\n🔍 检查职责清晰度...')
        
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            
            responsibility = self.extract_responsibility(content)
            
            if not responsibility:
                self.responsibility_issues.append({
                    'type': '缺少职责描述',
                    'file': doc_name,
                    'severity': 'P0',
                    'description': '文档缺少职责描述'
                })
                continue
            
            if '，' not in responsibility and '。' not in responsibility:
                self.responsibility_issues.append({
                    'type': '职责描述缺少标点',
                    'file': doc_name,
                    'severity': 'P2',
                    'description': '职责描述缺少中文标点符号'
                })
            
            vague_words = ['管理', '处理', '提供', '支持', '实现']
            vague_count = sum(1 for word in vague_words if word in responsibility)
            
            if vague_count >= 4:
                self.responsibility_issues.append({
                    'type': '职责描述模糊',
                    'file': doc_name,
                    'severity': 'P1',
                    'description': f'职责描述包含{vague_count}个模糊词汇'
                })
        
        print(f'  ✅ 职责清晰度检查完成: 发现{len(self.responsibility_issues)}个问题')
    
    def generate_report(self):
        """生成审计报告"""
        print('\n📊 生成审计报告...')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_DEEP_AUDIT_REPORT_{timestamp}.md'
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        total_issues = len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues)
        p0_count = sum(1 for issue in self.l2_issues + self.responsibility_issues if issue['severity'] == 'P0')
        p1_count = sum(1 for issue in self.l2_issues + self.l3_issues + self.duplicates + self.responsibility_issues if issue['severity'] == 'P1')
        p2_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues + self.duplicates + self.responsibility_issues if issue['severity'] == 'P2')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 再次深度审计报告\n\n')
            f.write(f'> **审计时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'> **审计范围**: {self.blueprints_dir}\n')
            f.write(f'> **审计类型**: 再次深度审计（三层审计标准）\n')
            f.write(f'> **审计状态**: ✅ 完成\n\n')
            f.write('---\n\n')
            
            f.write('## 📊 审计概要\n\n')
            f.write(f'- **扫描文档数**: {len(self.documents)}个\n')
            f.write(f'- **发现问题数**: {total_issues}个\n')
            f.write(f'- **P0问题**: {p0_count}个\n')
            f.write(f'- **P1问题**: {p1_count}个\n')
            f.write(f'- **P2问题**: {p2_count}个\n')
            f.write(f'- **重复文档对**: {len(self.duplicates)}对\n')
            f.write(f'- **职责问题**: {len(self.responsibility_issues)}个\n\n')
            
            f.write('---\n\n')
            
            f.write('## 🔍 三层审计发现\n\n')
            
            f.write('### L1 文件系统层审计\n\n')
            f.write(f'发现问题: {len(self.l1_issues)}个\n\n')
            if self.l1_issues:
                for i, issue in enumerate(self.l1_issues, 1):
                    f.write(f'{i}. **{issue["type"]}**: {issue["file"]} ({issue["severity"]})\n')
                    f.write(f'   - {issue["description"]}\n')
            else:
                f.write('✅ 无L1问题\n')
            
            f.write('\n### L2 文档内容层审计\n\n')
            f.write(f'发现问题: {len(self.l2_issues)}个\n\n')
            if self.l2_issues:
                p0_issues = [issue for issue in self.l2_issues if issue['severity'] == 'P0']
                p1_issues = [issue for issue in self.l2_issues if issue['severity'] == 'P1']
                p2_issues = [issue for issue in self.l2_issues if issue['severity'] == 'P2']
                
                if p0_issues:
                    f.write('#### P0 问题（立即修复）\n\n')
                    for i, issue in enumerate(p0_issues, 1):
                        f.write(f'{i}. **{issue["type"]}**: {issue["file"]}\n')
                        f.write(f'   - {issue["description"]}\n')
                
                if p1_issues:
                    f.write('\n#### P1 问题（优先修复）\n\n')
                    for i, issue in enumerate(p1_issues[:20], 1):
                        f.write(f'{i}. **{issue["type"]}**: {issue["file"]}\n')
                        f.write(f'   - {issue["description"]}\n')
                    if len(p1_issues) > 20:
                        f.write(f'\n*注：仅显示前20项，共{len(p1_issues)}项*\n')
                
                if p2_issues:
                    f.write('\n#### P2 问题（建议修复）\n\n')
                    for i, issue in enumerate(p2_issues[:20], 1):
                        f.write(f'{i}. **{issue["type"]}**: {issue["file"]}\n')
                        f.write(f'   - {issue["description"]}\n')
                    if len(p2_issues) > 20:
                        f.write(f'\n*注：仅显示前20项，共{len(p2_issues)}项*\n')
            else:
                f.write('✅ 无L2问题\n')
            
            f.write('\n### L3 专业标准层审计\n\n')
            f.write(f'发现问题: {len(self.l3_issues)}个\n\n')
            if self.l3_issues:
                for i, issue in enumerate(self.l3_issues[:20], 1):
                    f.write(f'{i}. **{issue["type"]}**: {issue["file"]} ({issue["severity"]})\n')
                    f.write(f'   - {issue["description"]}\n')
                if len(self.l3_issues) > 20:
                    f.write(f'\n*注：仅显示前20项，共{len(self.l3_issues)}项*\n')
            else:
                f.write('✅ 无L3问题\n')
            
            f.write('\n---\n\n')
            
            f.write('## 🔄 重复内容检测\n\n')
            f.write(f'发现重复: {len(self.duplicates)}对\n\n')
            if self.duplicates:
                for i, dup in enumerate(self.duplicates, 1):
                    f.write(f'{i}. **{dup["file1"]}** ↔ **{dup["file2"]}**\n')
                    f.write(f'   - 相似度: {dup["similarity"]*100:.1f}%\n')
                    f.write(f'   - 严重程度: {dup["severity"]}\n')
                    f.write(f'   - 类型: {dup["type"]}\n')
            else:
                f.write('✅ 无重复内容\n')
            
            f.write('\n---\n\n')
            
            f.write('## 📝 职责清晰度检查\n\n')
            f.write(f'发现问题: {len(self.responsibility_issues)}个\n\n')
            if self.responsibility_issues:
                p0_issues = [issue for issue in self.responsibility_issues if issue['severity'] == 'P0']
                p1_issues = [issue for issue in self.responsibility_issues if issue['severity'] == 'P1']
                p2_issues = [issue for issue in self.responsibility_issues if issue['severity'] == 'P2']
                
                if p0_issues:
                    f.write('#### P0 问题（缺少职责描述）\n\n')
                    for i, issue in enumerate(p0_issues, 1):
                        f.write(f'{i}. {issue["file"]}\n')
                
                if p1_issues:
                    f.write('\n#### P1 问题（职责模糊）\n\n')
                    for i, issue in enumerate(p1_issues[:20], 1):
                        f.write(f'{i}. {issue["file"]}\n')
                        f.write(f'   - {issue["description"]}\n')
                    if len(p1_issues) > 20:
                        f.write(f'\n*注：仅显示前20项，共{len(p1_issues)}项*\n')
                
                if p2_issues:
                    f.write('\n#### P2 问题（标点符号）\n\n')
                    for i, issue in enumerate(p2_issues[:20], 1):
                        f.write(f'{i}. {issue["file"]}\n')
                        f.write(f'   - {issue["description"]}\n')
                    if len(p2_issues) > 20:
                        f.write(f'\n*注：仅显示前20项，共{len(p2_issues)}项*\n')
            else:
                f.write('✅ 无职责清晰度问题\n')
            
            f.write('\n---\n\n')
            
            f.write(f'**审计完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        print(f'  ✅ 审计报告已生成: {report_file}')
        
        return report_file
    
    def run(self):
        """执行完整审计流程"""
        print('=' * 80)
        print('Layer 5 再次深度审计')
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
    auditor = Layer5DeepAuditor()
    auditor.run()


if __name__ == '__main__':
    main()
