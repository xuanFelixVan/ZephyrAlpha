#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 5 重复章节和乱码内容清理工具
清理文档中的重复章节和乱码内容
"""

import os
import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class Layer5DuplicateSectionCleaner:
    """Layer 5重复章节和乱码内容清理器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.documents = {}
        self.cleanups = []
        
        self.duplicate_sections = [
            '核心定位',
            '设计目标',
            '核心功能',
            '实现方案'
        ]
        
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
    
    def write_file(self, file_path: Path, content: str):
        """写入文件内容"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f'  ❌ 无法写入文件 {file_path.name}: {e}')
            return False
    
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
    
    def clean_duplicate_sections(self):
        """清理重复章节"""
        print('\n🔧 清理重复章节...')
        
        cleaned_count = 0
        
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            original_content = content
            
            for section_name in self.duplicate_sections:
                pattern = rf'^##\s+{section_name}\s*\n\n.+?(?=\n##|\Z)'
                matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
                
                if len(matches) > 1:
                    first_match = matches[0]
                    
                    for match in matches[1:]:
                        duplicate_content = match.group(0)
                        
                        if self.has_garbled_text(duplicate_content):
                            content = content[:match.start()] + content[match.end():]
                            
                            cleaned_count += 1
                            self.cleanups.append({
                                'type': '删除重复章节（含乱码）',
                                'file': doc_name,
                                'section': section_name,
                                'position': match.start()
                            })
                            print(f'  ✅ 已清理: {doc_name} - 重复{section_name}章节（含乱码）')
                        else:
                            content = content[:match.start()] + content[match.end():]
                            
                            cleaned_count += 1
                            self.cleanups.append({
                                'type': '删除重复章节',
                                'file': doc_name,
                                'section': section_name,
                                'position': match.start()
                            })
                            print(f'  ✅ 已清理: {doc_name} - 重复{section_name}章节')
            
            if content != original_content:
                self.write_file(doc_info['path'], content)
        
        print(f'  ✅ 清理完成: {cleaned_count}个重复章节')
    
    def has_garbled_text(self, text: str) -> bool:
        """检测是否包含乱码"""
        garbled_patterns = [
            r'è[^\x00-\x7F]+',
            r'Ã[^\x00-\x7F]+',
            r'â[^\x00-\x7F]+',
            r'ï[^\x00-\x7F]+',
            r'[\x80-\xFF]{3,}',
        ]
        
        for pattern in garbled_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def clean_garbled_content(self):
        """清理乱码内容"""
        print('\n🔧 清理乱码内容...')
        
        cleaned_count = 0
        
        for doc_name, doc_info in self.documents.items():
            content = doc_info['content']
            original_content = content
            
            if self.has_garbled_text(content):
                lines = content.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    if not self.has_garbled_text(line):
                        cleaned_lines.append(line)
                    else:
                        cleaned_count += 1
                        self.cleanups.append({
                            'type': '删除乱码行',
                            'file': doc_name,
                            'line': line[:50] + '...' if len(line) > 50 else line
                        })
                        print(f'  ✅ 已清理: {doc_name} - 乱码行')
                
                content = '\n'.join(cleaned_lines)
                
                if content != original_content:
                    self.write_file(doc_info['path'], content)
        
        print(f'  ✅ 清理完成: {cleaned_count}行乱码内容')
    
    def generate_report(self):
        """生成清理报告"""
        print('\n📊 生成清理报告...')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_DUPLICATE_SECTION_CLEANUP_REPORT_{timestamp}.md'
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 重复章节和乱码内容清理报告\n\n')
            f.write(f'> **清理时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'> **清理范围**: {self.blueprints_dir}\n')
            f.write(f'> **清理状态**: ✅ 完成\n\n')
            f.write('---\n\n')
            
            f.write('## 📊 清理概要\n\n')
            f.write(f'- **扫描文档数**: {len(self.documents)}个\n')
            f.write(f'- **清理问题数**: {len(self.cleanups)}个\n\n')
            
            f.write('---\n\n')
            
            f.write('## 🔧 清理详情\n\n')
            
            if self.cleanups:
                for i, cleanup in enumerate(self.cleanups, 1):
                    if 'section' in cleanup:
                        f.write(f'{i}. **{cleanup["type"]}**: {cleanup["file"]}\n')
                        f.write(f'   - 章节: {cleanup["section"]}\n')
                    elif 'line' in cleanup:
                        f.write(f'{i}. **{cleanup["type"]}**: {cleanup["file"]}\n')
                        f.write(f'   - 内容: {cleanup["line"]}\n')
                    else:
                        f.write(f'{i}. **{cleanup["type"]}**: {cleanup["file"]}\n')
            else:
                f.write('✅ 无需清理\n')
            
            f.write('\n---\n\n')
            
            f.write(f'**清理完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        print(f'  ✅ 清理报告已生成: {report_file}')
        
        return report_file
    
    def run(self):
        """执行完整清理流程"""
        print('=' * 80)
        print('Layer 5 重复章节和乱码内容清理')
        print('=' * 80)
        
        self.scan_documents()
        
        self.clean_duplicate_sections()
        self.clean_garbled_content()
        
        report_file = self.generate_report()
        
        print('\n' + '=' * 80)
        print('清理完成')
        print('=' * 80)
        print(f'\n📊 清理统计:')
        print(f'  - 扫描文档: {len(self.documents)}个')
        print(f'  - 清理问题: {len(self.cleanups)}个')
        print(f'\n📄 清理报告: {report_file}')
        
        return report_file


def main():
    cleaner = Layer5DuplicateSectionCleaner()
    cleaner.run()


if __name__ == '__main__':
    main()
