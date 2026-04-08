#!/usr/bin/env python3
"""
Layer 9 INDEX.md更新脚本

功能:
- 扫描Layer 9目录下的所有文档
- 按类型分类组织文档
- 更新INDEX.md，添加完整的文档索引
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class Layer9IndexUpdater:
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
        print('Layer 9 INDEX.md更新工具')
        print('=' * 80)
        print(f'更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print()
        
        print('阶段1: 扫描文档...')
        self.scan_documents()
        print(f'  ✅ 扫描完成')
        print()
        
        print('阶段2: 分类文档...')
        self.classify_documents()
        print(f'  ✅ 分类完成')
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
        if not layer9_path.exists():
            print(f'  ❌ 目录不存在: {self.layer9_dir}')
            return
        
        for md_file in layer9_path.glob('*.md'):
            if md_file.name == 'INDEX.md':
                continue
            
            doc_info = self.extract_document_info(str(md_file))
            if doc_info:
                self.documents['核心文档'].append(doc_info)
        
        archive_path = layer9_path / '_archive'
        if archive_path.exists():
            for md_file in archive_path.glob('*.md'):
                doc_info = self.extract_document_info(str(md_file))
                if doc_info:
                    self.documents['归档文档'].append(doc_info)
    
    def extract_document_info(self, filepath: str) -> Optional[Dict]:
        """提取文档信息"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            filename = os.path.basename(filepath)
            relative_path = filepath.replace('\\', '/')
            
            title = self._extract_title(content)
            responsibility = self._extract_responsibility(content)
            version = self._extract_yaml_field(content, 'version')
            
            return {
                'filename': filename,
                'path': relative_path,
                'title': title,
                'responsibility': responsibility,
                'version': version
            }
        except Exception as e:
            return None
    
    def _extract_title(self, content: str) -> str:
        """提取标题"""
        match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        match = re.search(r'^##\s+(.+?)$', content, re.MULTILINE)
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
        
        return ""
    
    def _extract_yaml_field(self, content: str, field: str) -> str:
        """提取YAML字段"""
        pattern = rf'{field}:\s*(.+)'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""
    
    def classify_documents(self):
        """分类文档"""
        all_docs = self.documents['核心文档'].copy()
        self.documents['核心文档'] = []
        
        for doc in all_docs:
            filename = doc['filename']
            
            if 'AUDIT_REPORT' in filename or 'AUDIT' in filename:
                self.documents['审计报告'].append(doc)
            elif 'GUIDE' in filename or 'IMPLEMENTATION' in filename:
                self.documents['实施指南'].append(doc)
            else:
                self.documents['核心文档'].append(doc)
    
    def update_index_file(self):
        """更新INDEX.md文件"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            index_section = self.generate_index_section()
            
            if '## 📚 文档索引' in content:
                content = re.sub(
                    r'## 📚 文档索引.*?(?=\n---|\n##|\Z)',
                    index_section,
                    content,
                    flags=re.DOTALL
                )
            else:
                insert_pos = content.find('## 📝 维护说明')
                if insert_pos != -1:
                    content = content[:insert_pos] + index_section + '\n\n' + content[insert_pos:]
                else:
                    content += '\n\n' + index_section
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'  ✅ INDEX.md已更新')
        except Exception as e:
            print(f'  ❌ 更新失败: {e}')
    
    def generate_index_section(self) -> str:
        """生成索引章节"""
        lines = []
        
        lines.append('## 📚 文档索引')
        lines.append('')
        lines.append(f'**文档总数**: {sum(len(docs) for docs in self.documents.values())}个')
        lines.append('')
        
        for category, docs in self.documents.items():
            if not docs:
                continue
            
            lines.append(f'### {category}')
            lines.append('')
            lines.append('| 文档名称 | 核心职责 | 版本 |')
            lines.append('|----------|----------|------|')
            
            for doc in sorted(docs, key=lambda x: x['filename']):
                filename = doc['filename']
                path = doc['path']
                responsibility = doc['responsibility'] if doc['responsibility'] else '待补充'
                version = doc['version'] if doc['version'] else '-'
                
                lines.append(f'| [{filename}]({path}) | {responsibility} | {version} |')
            
            lines.append('')
        
        lines.append('---')
        lines.append('')
        
        return '\n'.join(lines)
    
    def print_summary(self):
        """打印摘要"""
        print()
        print('更新摘要:')
        for category, docs in self.documents.items():
            print(f'  {category}: {len(docs)}个文档')
        print(f'  总计: {sum(len(docs) for docs in self.documents.values())}个文档')


def main():
    updater = Layer9IndexUpdater()
    updater.update_index()


if __name__ == '__main__':
    main()
