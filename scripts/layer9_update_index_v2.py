#!/usr/bin/env python3
"""
Layer 9 INDEX.md更新脚本 v2.0

功能:
- 扫描Layer 9目录下的所有文档
- 更新INDEX.md的文档索引部分
- 分类整理文档（核心文档、审计报告、归档文档等）
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class Layer9IndexUpdaterV2:
    def __init__(self):
        self.layer9_dir = 'docs/09_RESEARCH_INNOVATION'
        self.index_file = f'{self.layer9_dir}/INDEX.md'
        self.documents = {
            '核心文档': [],
            '审计报告': [],
            '实施指南': [],
            '归档文档': []
        }
        
    def update_index(self):
        """更新INDEX.md"""
        print('=' * 80)
        print('Layer 9 INDEX.md更新工具 v2.0')
        print('=' * 80)
        print(f'更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print()
        
        print('阶段1: 扫描文档...')
        self.scan_documents()
        total_docs = sum(len(docs) for docs in self.documents.values())
        print(f'  ✅ 扫描完成: {total_docs}个文档')
        print()
        
        print('阶段2: 分类文档...')
        self.classify_documents()
        print(f'  ✅ 分类完成')
        print(f'    - 核心文档: {len(self.documents["核心文档"])}个')
        print(f'    - 审计报告: {len(self.documents["审计报告"])}个')
        print(f'    - 实施指南: {len(self.documents["实施指南"])}个')
        print(f'    - 归档文档: {len(self.documents["归档文档"])}个')
        print()
        
        print('阶段3: 更新INDEX.md...')
        self.update_index_file()
        print(f'  ✅ 更新完成')
        print()
        
        print('=' * 80)
        print('更新完成')
        print('=' * 80)
        
        self.print_summary()
    
    def scan_documents(self):
        """扫描文档"""
        layer9_path = Path(self.layer9_dir)
        
        for md_file in layer9_path.rglob('*.md'):
            if md_file.name == 'INDEX.md':
                continue
            
            if 'maintenance_records' in str(md_file):
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc_info = self.extract_document_info(str(md_file), content)
                if doc_info:
                    if '_archive' in str(md_file):
                        self.documents['归档文档'].append(doc_info)
                    elif 'AUDIT' in md_file.name or 'REPORT' in md_file.name:
                        self.documents['审计报告'].append(doc_info)
                    elif 'IMPLEMENTATION' in md_file.name or 'GUIDE' in md_file.name:
                        self.documents['实施指南'].append(doc_info)
                    else:
                        self.documents['核心文档'].append(doc_info)
            except Exception as e:
                print(f'  ⚠️ 无法读取文件: {md_file.name} - {e}')
    
    def extract_document_info(self, filepath: str, content: str) -> Dict:
        """提取文档信息"""
        filename = os.path.basename(filepath)
        relative_path = os.path.relpath(filepath, self.layer9_dir)
        
        title = self._extract_title(content)
        responsibility = self._extract_responsibility(content)
        version = self._extract_version(content)
        
        return {
            'filename': filename,
            'relative_path': relative_path,
            'title': title,
            'responsibility': responsibility,
            'version': version
        }
    
    def _extract_title(self, content: str) -> str:
        """提取标题"""
        match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_responsibility(self, content: str) -> str:
        """提取职责描述"""
        patterns = [
            r'responsibility:\s*\n\s+-\s+(.+?)(?:\n|$)',
            r'##\s+核心定位\s*\n\s*(.+?)(?:\n\n|\n#)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                resp = match.group(1).strip()
                if len(resp) > 100:
                    return resp[:100] + '...'
                return resp
        
        return "未定义职责"
    
    def _extract_version(self, content: str) -> str:
        """提取版本"""
        match = re.search(r'version:\s*(.+)', content)
        if match:
            return match.group(1).strip()
        return "v1.0"
    
    def classify_documents(self):
        """分类文档"""
        pass
    
    def update_index_file(self):
        """更新INDEX.md文件"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_index_section = self.generate_index_section()
            
            pattern = r'## 📚 文档索引.*?(?=\n---|\n## |$)'
            new_content = re.sub(pattern, new_index_section, content, flags=re.DOTALL)
            
            new_content = re.sub(
                r'last_updated: \d{4}-\d{2}-\d{2}',
                f'last_updated: {datetime.now().strftime("%Y-%m-%d")}',
                new_content
            )
            
            new_content = re.sub(
                r'\*\*文档总数\*\*: \d+个',
                f'**文档总数**: {sum(len(docs) for docs in self.documents.values())}个',
                new_content
            )
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f'  ✅ INDEX.md已更新')
        except Exception as e:
            print(f'  ❌ 更新失败: {e}')
    
    def generate_index_section(self) -> str:
        """生成索引部分"""
        lines = []
        
        lines.append('## 📚 文档索引')
        lines.append('')
        total_docs = sum(len(docs) for docs in self.documents.values())
        lines.append(f'**文档总数**: {total_docs}个')
        lines.append('')
        
        for category, docs in self.documents.items():
            if not docs:
                continue
            
            lines.append(f'### {category}')
            lines.append('')
            lines.append('| 文档名称 | 核心职责 | 版本 |')
            lines.append('|----------|----------|------|')
            
            for doc in sorted(docs, key=lambda x: x['filename']):
                link = f'[{doc["filename"]}]({doc["relative_path"]})'
                responsibility = doc['responsibility'][:50] + '...' if len(doc['responsibility']) > 50 else doc['responsibility']
                lines.append(f'| {link} | {responsibility} | {doc["version"]} |')
            
            lines.append('')
        
        return '\n'.join(lines)
    
    def print_summary(self):
        """打印摘要"""
        print()
        print('更新摘要:')
        total_docs = sum(len(docs) for docs in self.documents.values())
        print(f'  总文档数: {total_docs}')
        print(f'  核心文档: {len(self.documents["核心文档"])}')
        print(f'  审计报告: {len(self.documents["审计报告"])}')
        print(f'  实施指南: {len(self.documents["实施指南"])}')
        print(f'  归档文档: {len(self.documents["归档文档"])}')


def main():
    updater = Layer9IndexUpdaterV2()
    updater.update_index()


if __name__ == '__main__':
    main()
