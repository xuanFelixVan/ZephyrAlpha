#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5 重复内容处理工具
智能分析和处理文档重复内容
"""

import re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict


class Layer5DuplicateHandler:
    """Layer 5重复内容处理器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.documents = {}
        self.duplicates = []
        self.duplicate_stats = defaultdict(int)
        
        self.similarity_threshold = 0.85
        self.template_sections = [
            '文档治理',
            '变更历史',
            '版本记录',
            '相关文档',
            '参考资料',
            '附录',
            '1. 文档治理',
            '2. 变更历史',
        ]
        
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
                except Exception:
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
    
    def is_template_section(self, section_name: str) -> bool:
        for template in self.template_sections:
            if template in section_name:
                return True
        return False
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1, text2).ratio()
    
    def analyze_duplicates(self):
        print('  分析重复内容...')
        
        files = list(self.blueprints_dir.glob('*_BLUEPRINT.md'))
        
        for file_path in files:
            content = self.read_document(file_path)
            if content:
                self.documents[file_path.name] = {
                    'content': content,
                    'sections': self.extract_sections(content)
                }
        
        doc_names = list(self.documents.keys())
        
        for i, doc1_name in enumerate(doc_names):
            for doc2_name in doc_names[i+1:]:
                doc1 = self.documents[doc1_name]
                doc2 = self.documents[doc2_name]
                
                for section_name in doc1['sections']:
                    if section_name in doc2['sections']:
                        if self.is_template_section(section_name):
                            continue
                        
                        section1 = doc1['sections'][section_name]
                        section2 = doc2['sections'][section_name]
                        
                        similarity = self.calculate_similarity(section1, section2)
                        
                        if similarity > self.similarity_threshold:
                            self.duplicates.append({
                                'file1': doc1_name,
                                'file2': doc2_name,
                                'section': section_name,
                                'similarity': f'{similarity:.1%}',
                                'similarity_value': similarity,
                                'severity': '高' if similarity > 0.95 else '中',
                                'type': '章节重复',
                                'description': f'{section_name}章节相似度{similarity:.1%}',
                                'suggestion': '差异化章节内容或合并文档'
                            })
                            
                            self.duplicate_stats[section_name] += 1
    
    def categorize_duplicates(self) -> dict:
        categorized = {
            '高优先级': [],
            '中优先级': [],
            '低优先级': []
        }
        
        for duplicate in self.duplicates:
            if duplicate['similarity_value'] > 0.95:
                categorized['高优先级'].append(duplicate)
            elif duplicate['similarity_value'] > 0.90:
                categorized['中优先级'].append(duplicate)
            else:
                categorized['低优先级'].append(duplicate)
        
        return categorized
    
    def run(self):
        print('=' * 80)
        print('Layer 5 重复内容处理工具')
        print('=' * 80)
        print(f'处理时间: {self._get_timestamp()}')
        print()
        
        print('扫描文档文件...')
        files = list(self.blueprints_dir.glob('*_BLUEPRINT.md'))
        print(f'  找到 {len(files)} 个文档')
        print()
        
        self.analyze_duplicates()
        
        categorized = self.categorize_duplicates()
        
        print(f'生成处理报告...')
        self._generate_report(categorized)
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('处理完成')
        print('=' * 80)
        print()
        self._print_summary(categorized)
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _print_summary(self, categorized):
        print('处理摘要:')
        print(f'  扫描文档: {len(self.documents)}个')
        print(f'  发现重复: {len(self.duplicates)}对')
        print(f'  高优先级: {len(categorized["高优先级"])}对')
        print(f'  中优先级: {len(categorized["中优先级"])}对')
        print(f'  低优先级: {len(categorized["低优先级"])}对')
        print()
        print('重复最多的章节:')
        for section, count in sorted(self.duplicate_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f'  - {section}: {count}对')
    
    def _generate_report(self, categorized):
        report_path = self.audit_dir / 'LAYER5_DUPLICATE_HANDLING_REPORT_20260407.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 重复内容处理报告\n\n')
            f.write(f'> **处理时间**: {self._get_timestamp()}\n')
            f.write(f'> **处理范围**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS\n\n')
            f.write('---\n\n')
            
            f.write('## 📊 处理概要\n\n')
            f.write(f'- **扫描文档**: {len(self.documents)}个\n')
            f.write(f'- **发现重复**: {len(self.duplicates)}对\n')
            f.write(f'- **高优先级**: {len(categorized["高优先级"])}对\n')
            f.write(f'- **中优先级**: {len(categorized["中优先级"])}对\n')
            f.write(f'- **低优先级**: {len(categorized["低优先级"])}对\n\n')
            
            f.write('---\n\n')
            
            f.write('## 📊 重复章节统计\n\n')
            f.write('| 章节名称 | 重复次数 | 占比 |\n')
            f.write('|----------|----------|------|\n')
            
            total = sum(self.duplicate_stats.values())
            for section, count in sorted(self.duplicate_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                percentage = count / total * 100 if total > 0 else 0
                f.write(f"| {section} | {count} | {percentage:.1f}% |\n")
            
            f.write('\n---\n\n')
            
            f.write('## 🔴 高优先级重复（相似度>95%）\n\n')
            if categorized['高优先级']:
                f.write('| 文件1 | 文件2 | 章节 | 相似度 | 建议 |\n')
                f.write('|-------|-------|------|--------|------|\n')
                for dup in categorized['高优先级'][:20]:
                    f.write(f"| {dup['file1']} | {dup['file2']} | {dup['section']} | {dup['similarity']} | {dup['suggestion']} |\n")
            else:
                f.write('无高优先级重复内容\n')
            
            f.write('\n---\n\n')
            
            f.write('## 🟡 中优先级重复（相似度90%-95%）\n\n')
            if categorized['中优先级']:
                f.write('| 文件1 | 文件2 | 章节 | 相似度 | 建议 |\n')
                f.write('|-------|-------|------|--------|------|\n')
                for dup in categorized['中优先级'][:20]:
                    f.write(f"| {dup['file1']} | {dup['file2']} | {dup['section']} | {dup['similarity']} | {dup['suggestion']} |\n")
            else:
                f.write('无中优先级重复内容\n')
            
            f.write('\n---\n\n')
            
            f.write('## 🎯 处理建议\n\n')
            f.write('### 立即处理\n\n')
            if categorized['高优先级']:
                f.write(f'1. **处理{len(categorized["高优先级"])}对高优先级重复内容**\n')
                f.write('   - 识别真正需要合并的文档\n')
                f.write('   - 差异化章节内容\n')
                f.write('   - 删除冗余内容\n\n')
            
            f.write('### 近期处理\n\n')
            if categorized['中优先级']:
                f.write(f'1. **处理{len(categorized["中优先级"])}对中优先级重复内容**\n')
                f.write('   - 优化章节内容\n')
                f.write('   - 提高内容差异化\n\n')
            
            f.write('### 长期优化\n\n')
            f.write(f'1. **监控{len(categorized["低优先级"])}对低优先级重复内容**\n')
            f.write('   - 定期检查重复情况\n')
            f.write('   - 建立内容规范\n\n')
            
            f.write('---\n\n')
            
            f.write('## 📈 处理效果预期\n\n')
            f.write('| 处理阶段 | 处理数量 | 预计效果 |\n')
            f.write('|----------|----------|----------|\n')
            f.write(f'| 立即处理 | {len(categorized["高优先级"])}对 | 减少{len(categorized["高优先级"])}对高相似度重复 |\n')
            f.write(f'| 近期处理 | {len(categorized["中优先级"])}对 | 减少{len(categorized["中优先级"])}对中等相似度重复 |\n')
            f.write(f'| 长期监控 | {len(categorized["低优先级"])}对 | 持续监控低相似度重复 |\n\n')
            
            f.write(f'**处理完成时间**: {self._get_timestamp()}\n')
            f.write('**处理状态**: ✅ **完成**\n')


def main():
    handler = Layer5DuplicateHandler()
    handler.run()


if __name__ == '__main__':
    main()
