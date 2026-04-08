#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Pre-commit Hook - 文档质量检查
在提交代码前自动检查文档质量
"""

import os
import sys
import re
import subprocess
from pathlib import Path
from typing import List, Dict


class DocumentQualityHook:
    """文档质量检查Hook"""
    
    def __init__(self):
        self.min_responsibility_length = 50
        self.max_responsibility_length = 200
        self.min_document_length = 1000
        
        self.required_sections = [
            '核心定位',
            '设计目标',
            '核心功能',
            '实现方案'
        ]
        
        self.errors = []
        self.warnings = []
        
    def get_staged_files(self) -> List[str]:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True
        )
        
        files = result.stdout.strip().split('\n')
        return [f for f in files if f.endswith('.md') and not f.startswith('.git')]
    
    def check_file_naming(self, file_path: str) -> bool:
        filename = Path(file_path).name
        
        if not re.match(r'^[A-Z_]+_[A-Z]+\.md$', filename):
            self.warnings.append(f"⚠️  {filename}: 文件命名不规范，建议使用大写字母和下划线")
            return False
        
        old_patterns = ['Layer0_', 'Layer1_', 'Layer2_', 'Layer3_', 'Layer4_',
                       'Layer5_', 'Layer6_', 'Layer7_', 'Layer8_']
        for pattern in old_patterns:
            if pattern in filename:
                self.errors.append(f"❌ {filename}: 使用旧架构命名 '{pattern}'")
                return False
        
        return True
    
    def check_yaml_header(self, file_path: str, content: str) -> bool:
        if not content.startswith('---'):
            self.warnings.append(f"⚠️  {file_path}: 缺少YAML头部")
            return False
        
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not yaml_match:
            self.errors.append(f"❌ {file_path}: YAML头部格式错误")
            return False
        
        yaml_content = yaml_match.group(1)
        
        required_fields = ['version', 'module_id', 'layer', 'created', 'updated', 'status']
        missing_fields = []
        
        for field in required_fields:
            if f'{field}:' not in yaml_content:
                missing_fields.append(field)
        
        if missing_fields:
            self.errors.append(f"❌ {file_path}: YAML头部缺少字段: {', '.join(missing_fields)}")
            return False
        
        return True
    
    def check_responsibility(self, file_path: str, content: str) -> bool:
        pattern = r'^##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        
        if not match:
            self.errors.append(f"❌ {file_path}: 缺少'核心定位'章节")
            return False
        
        responsibility = match.group(1).strip()
        length = len(responsibility)
        
        if length < self.min_responsibility_length:
            self.errors.append(
                f"❌ {file_path}: 职责描述过短 ({length}字 < {self.min_responsibility_length}字)"
            )
            return False
        
        if length > self.max_responsibility_length:
            self.warnings.append(
                f"⚠️  {file_path}: 职责描述过长 ({length}字 > {self.max_responsibility_length}字)"
            )
            return False
        
        return True
    
    def check_sections(self, file_path: str, content: str) -> bool:
        missing_sections = []
        
        for section in self.required_sections:
            if f'## {section}' not in content:
                missing_sections.append(section)
        
        if missing_sections:
            self.errors.append(
                f"❌ {file_path}: 缺少章节: {', '.join(missing_sections)}"
            )
            return False
        
        return True
    
    def check_document_length(self, file_path: str, content: str) -> bool:
        word_count = len(content)
        
        if word_count < self.min_document_length:
            self.warnings.append(
                f"⚠️  {file_path}: 文档长度不足 ({word_count}字 < {self.min_document_length}字)"
            )
            return False
        
        return True
    
    def check_file(self, file_path: str) -> Dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except Exception as e:
                self.errors.append(f"❌ {file_path}: 无法读取文件 - {e}")
                return {'valid': False}
        
        results = {
            'naming': self.check_file_naming(file_path),
            'yaml': self.check_yaml_header(file_path, content),
            'responsibility': self.check_responsibility(file_path, content),
            'sections': self.check_sections(file_path, content),
            'length': self.check_document_length(file_path, content)
        }
        
        return results
    
    def run(self):
        print('=' * 80)
        print('Git Pre-commit Hook - 文档质量检查')
        print('=' * 80)
        print()
        
        staged_files = self.get_staged_files()
        
        if not staged_files:
            print('✅ 没有暂存的Markdown文件需要检查')
            return 0
        
        print(f'检查 {len(staged_files)} 个暂存的Markdown文件...')
        print()
        
        for file_path in staged_files:
            if os.path.exists(file_path):
                print(f'检查: {file_path}')
                self.check_file(file_path)
        
        print()
        print('=' * 80)
        print('检查结果')
        print('=' * 80)
        print()
        
        if self.errors:
            print('❌ 发现错误:')
            for error in self.errors:
                print(f'  {error}')
            print()
        
        if self.warnings:
            print('⚠️  发现警告:')
            for warning in self.warnings:
                print(f'  {warning}')
            print()
        
        if not self.errors and not self.warnings:
            print('✅ 所有文档质量检查通过')
            print()
            return 0
        
        if self.errors:
            print('❌ 提交被拒绝，请修复错误后重新提交')
            print()
            print('💡 提示:')
            print('  - 使用 --no-verify 跳过此检查（不推荐）')
            print('  - 修复错误后重新提交')
            print()
            return 1
        
        if self.warnings:
            print('⚠️  发现警告，建议修复后提交')
            print()
            print('💡 提示:')
            print('  - 可以继续提交，但建议修复警告')
            print('  - 使用 git commit --no-verify 跳过此检查')
            print()
            return 0
        
        return 0


def main():
    hook = DocumentQualityHook()
    exit_code = hook.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
