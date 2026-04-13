#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
Layer 9 归档文档清理脚本

功能:
- 分析归档目录中的历史文档
- 评估文档的保留价值
- 提供清理建议
- 执行清理操作（可选）
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ArchiveDocumentInfo:
    filepath: str
    filename: str
    version: str
    status: str
    created_date: str
    last_updated: str
    title: str
    has_references: bool
    content_preview: str
    recommendation: str
    reason: str


class Layer9ArchiveCleaner:
    def __init__(self):
        self.layer9_dir = 'docs/09_RESEARCH_INNOVATION'
        self.archive_dir = f'{self.layer9_dir}/_archive'
        self.documents: List[ArchiveDocumentInfo] = []
        self.keep_count = 0
        self.delete_count = 0
        
    def analyze_archive(self):
        """分析归档文档"""
        print('=' * 80)
        print('Layer 9 归档文档清理分析')
        print('=' * 80)
        print(f'分析时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'分析范围: {self.archive_dir}')
        print()
        
        print('阶段1: 扫描归档文档...')
        self.scan_archive_documents()
        print(f'  ✅ 发现 {len(self.documents)} 个归档文档')
        print()
        
        print('阶段2: 分析文档价值...')
        print(f'  ✅ 已完成文档价值分析')
        print()
        
        print('阶段3: 生成清理报告...')
        self.generate_report()
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('分析完成')
        print('=' * 80)
        
        self.print_summary()
    
    def scan_archive_documents(self):
        """扫描归档文档"""
        archive_path = Path(self.archive_dir)
        if not archive_path.exists():
            print(f'  ❌ 归档目录不存在: {self.archive_dir}')
            return
        
        for md_file in archive_path.glob('*.md'):
            try:
                doc_info = self.extract_document_info(str(md_file))
                if doc_info:
                    self.documents.append(doc_info)
            except Exception as e:
                print(f'  ⚠️ 无法处理文件: {md_file.name} - {e}')
    
    def extract_document_info(self, filepath: str) -> Optional[ArchiveDocumentInfo]:
        """提取文档信息"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            filename = os.path.basename(filepath)
            
            version = self._extract_yaml_field(content, 'version')
            status = self._extract_yaml_field(content, 'status')
            created_date = self._extract_yaml_field(content, 'created_date')
            last_updated = self._extract_yaml_field(content, 'last_updated')
            title = self._extract_title(content)
            
            has_references = self._check_references(filepath, filename)
            
            content_preview = content[:300].replace('\n', ' ')
            
            recommendation, reason = self._evaluate_document(
                filename, version, status, created_date, has_references
            )
            
            if recommendation == 'keep':
                self.keep_count += 1
            else:
                self.delete_count += 1
            
            return ArchiveDocumentInfo(
                filepath=filepath,
                filename=filename,
                version=version,
                status=status,
                created_date=created_date,
                last_updated=last_updated,
                title=title,
                has_references=has_references,
                content_preview=content_preview,
                recommendation=recommendation,
                reason=reason
            )
        except Exception as e:
            return None
    
    def _extract_yaml_field(self, content: str, field: str) -> str:
        """提取YAML字段"""
        pattern = rf'{field}:\s*(.+)'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""
    
    def _extract_title(self, content: str) -> str:
        """提取标题"""
        match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        return match.group(1).strip() if match else ""
    
    def _check_references(self, filepath: str, filename: str) -> bool:
        """检查文档是否有引用"""
        layer9_path = Path(self.layer9_dir)
        
        for md_file in layer9_path.glob('*.md'):
            if md_file.name == filename:
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if filename in content or os.path.splitext(filename)[0] in content:
                    return True
            except Exception:
                pass
        
        return False
    
    def _evaluate_document(self, filename: str, version: str, status: str, 
                          created_date: str, has_references: bool) -> tuple:
        """评估文档价值"""
        if has_references:
            return ('keep', '文档有活跃引用，建议保留')
        
        if 'v3' in version.lower() or 'v4' in version.lower():
            return ('keep', '文档版本较新，可能仍有参考价值')
        
        if 'CRITICAL' in filename or 'COMPLETE' in filename:
            return ('keep', '文档包含关键或完整信息，建议保留')
        
        if 'SUPPLEMENT' in filename or 'GUIDE' in filename:
            return ('delete', '补充文档或指南，可考虑删除或整合')
        
        if 'MISSING' in filename:
            return ('delete', '缺失模块补充文档，问题已解决可删除')
        
        return ('keep', '默认保留，需人工确认')
    
    def generate_report(self):
        """生成清理报告"""
        report_lines = []
        
        report_lines.append('# Layer 9 归档文档清理分析报告')
        report_lines.append('')
        report_lines.append(f'> **分析时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report_lines.append(f'> **分析范围**: {self.archive_dir}')
        report_lines.append(f'> **分析标准**: 文档引用、版本状态、内容价值')
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📊 分析概要')
        report_lines.append('')
        report_lines.append(f'**归档文档数**: {len(self.documents)}个')
        report_lines.append(f'**建议保留**: {self.keep_count}个')
        report_lines.append(f'**建议删除**: {self.delete_count}个')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📝 文档详情')
        report_lines.append('')
        
        for doc in self.documents:
            status_emoji = '✅' if doc.recommendation == 'keep' else '⚠️'
            report_lines.append(f'### {status_emoji} {doc.filename}')
            report_lines.append('')
            report_lines.append(f'**版本**: {doc.version}')
            report_lines.append(f'**状态**: {doc.status}')
            report_lines.append(f'**创建日期**: {doc.created_date}')
            report_lines.append(f'**最后更新**: {doc.last_updated}')
            report_lines.append(f'**有引用**: {"是" if doc.has_references else "否"}')
            report_lines.append(f'**建议**: {doc.recommendation}')
            report_lines.append(f'**原因**: {doc.reason}')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🎯 清理建议')
        report_lines.append('')
        
        report_lines.append('### 建议保留的文档')
        report_lines.append('')
        keep_docs = [d for d in self.documents if d.recommendation == 'keep']
        if keep_docs:
            for doc in keep_docs:
                report_lines.append(f'- **{doc.filename}**: {doc.reason}')
        else:
            report_lines.append('- 无')
        report_lines.append('')
        
        report_lines.append('### 建议删除的文档')
        report_lines.append('')
        delete_docs = [d for d in self.documents if d.recommendation == 'delete']
        if delete_docs:
            for doc in delete_docs:
                report_lines.append(f'- **{doc.filename}**: {doc.reason}')
        else:
            report_lines.append('- 无')
        report_lines.append('')
        
        report_lines.append('### 清理操作建议')
        report_lines.append('')
        report_lines.append('1. **保留文档**: 将建议保留的文档移至主目录或保留在归档目录')
        report_lines.append('2. **删除文档**: 将建议删除的文档移至更深层归档或删除')
        report_lines.append('3. **整合文档**: 考虑将相关文档整合为一个完整文档')
        report_lines.append('4. **更新引用**: 删除文档前，更新所有引用该文档的内容')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## ⚠️ 注意事项')
        report_lines.append('')
        report_lines.append('1. **备份重要**: 执行删除操作前，请确保已备份重要文档')
        report_lines.append('2. **检查引用**: 删除文档前，请确认没有其他文档引用')
        report_lines.append('3. **人工确认**: 建议人工确认后再执行删除操作')
        report_lines.append('4. **渐进清理**: 建议分批次清理，避免一次性删除过多文档')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        report_lines.append(f'**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        report_content = '\n'.join(report_lines)
        
        output_path = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_ARCHIVE_CLEANUP_REPORT_20260407.md')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f'  ✅ 报告已保存: {output_path}')
    
    def print_summary(self):
        """打印摘要"""
        print()
        print('分析摘要:')
        print(f'  归档文档: {len(self.documents)}')
        print(f'  建议保留: {self.keep_count}')
        print(f'  建议删除: {self.delete_count}')


def main():
    cleaner = Layer9ArchiveCleaner()
    cleaner.analyze_archive()


if __name__ == '__main__':
    main()
