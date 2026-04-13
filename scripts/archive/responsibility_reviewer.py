#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
职责描述审查工具
用于Git pre-commit hook，确保新文档包含合格的职责描述
"""

import re
import sys
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Dict, Tuple


class ResponsibilityReviewer:
    """职责描述审查器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.min_length = 50
        self.max_length = 200
        self.similarity_threshold = 0.80
        
        self.existing_responsibilities = []
        self.issues = []
        
    def extract_responsibility(self, content: str) -> str:
        """提取文档的职责描述"""
        core_match = re.search(r'##\s*核心定位\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        
        if not core_match:
            resp_match = re.search(r'职责[：:]\s*(.+?)(?=\n\n|\n##|\Z)', content, re.DOTALL)
            if resp_match:
                responsibility = resp_match.group(1).strip()
                responsibility = re.sub(r'\*\*(.+?)\*\*', r'\1', responsibility)
                responsibility = re.sub(r'\*(.+?)\*', r'\1', responsibility)
                responsibility = re.sub(r'`(.+?)`', r'\1', responsibility)
                return responsibility
            return ''
        
        responsibility = core_match.group(1).strip()
        responsibility = re.sub(r'\*\*(.+?)\*\*', r'\1', responsibility)
        responsibility = re.sub(r'\*(.+?)\*', r'\1', responsibility)
        responsibility = re.sub(r'`(.+?)`', r'\1', responsibility)
        
        return responsibility
    
    def check_length(self, responsibility: str, filename: str) -> bool:
        """检查职责描述长度"""
        length = len(responsibility)
        
        if length < self.min_length:
            self.issues.append({
                'type': 'length_short',
                'file': filename,
                'message': f'职责描述过短: {length}字（最少{self.min_length}字）',
                'severity': 'warning'
            })
            return False
        
        if length > self.max_length:
            self.issues.append({
                'type': 'length_long',
                'file': filename,
                'message': f'职责描述过长: {length}字（最多{self.max_length}字）',
                'severity': 'warning'
            })
            return False
        
        return True
    
    def check_format(self, responsibility: str, filename: str) -> bool:
        """检查职责描述格式"""
        if not responsibility:
            self.issues.append({
                'type': 'missing',
                'file': filename,
                'message': '缺少职责描述',
                'severity': 'error'
            })
            return False
        
        if '负责' not in responsibility and '实现' not in responsibility and '管理' not in responsibility:
            self.issues.append({
                'type': 'format',
                'file': filename,
                'message': '职责描述格式不规范，应包含"负责"、"实现"或"管理"等关键词',
                'severity': 'warning'
            })
            return False
        
        return True
    
    def check_similarity(self, responsibility: str, filename: str) -> bool:
        """检查职责描述相似度"""
        for existing in self.existing_responsibilities:
            similarity = SequenceMatcher(None, responsibility, existing['responsibility']).ratio()
            
            if similarity >= self.similarity_threshold:
                self.issues.append({
                    'type': 'similarity',
                    'file': filename,
                    'message': f'职责描述与 {existing["file"]} 相似度过高: {similarity:.1%}',
                    'severity': 'warning'
                })
                return False
        
        return True
    
    def load_existing_responsibilities(self):
        """加载现有职责描述"""
        if not self.blueprints_dir.exists():
            return
        
        for file_path in self.blueprints_dir.glob('*.md'):
            if file_path.name == 'INDEX.md':
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            responsibility = self.extract_responsibility(content)
            if responsibility:
                self.existing_responsibilities.append({
                    'file': file_path.name,
                    'responsibility': responsibility
                })
    
    def review_file(self, file_path: Path) -> bool:
        """审查单个文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        responsibility = self.extract_responsibility(content)
        filename = file_path.name
        
        passed = True
        
        if not self.check_format(responsibility, filename):
            passed = False
        
        if responsibility and not self.check_length(responsibility, filename):
            passed = False
        
        if responsibility and not self.check_similarity(responsibility, filename):
            passed = False
        
        return passed
    
    def run(self, files: List[str] = None) -> bool:
        """运行审查"""
        print('=' * 80)
        print('职责描述审查工具')
        print('=' * 80)
        print()
        
        print('阶段1: 加载现有职责描述...')
        self.load_existing_responsibilities()
        print(f'  ✅ 加载了 {len(self.existing_responsibilities)} 个现有职责描述')
        print()
        
        print('阶段2: 审查文件...')
        if files is None:
            files = []
            if self.blueprints_dir.exists():
                for file_path in self.blueprints_dir.glob('*.md'):
                    if file_path.name != 'INDEX.md':
                        files.append(str(file_path))
        
        if not files:
            print('  ⚠️ 未发现需要审查的文件')
            return True
        
        all_passed = True
        for file_str in files:
            file_path = Path(file_str)
            if file_path.exists() and file_path.suffix == '.md':
                print(f'  审查 {file_path.name}...')
                if not self.review_file(file_path):
                    all_passed = False
        
        print()
        
        if self.issues:
            print('阶段3: 发现问题...')
            for issue in self.issues:
                severity_icon = '❌' if issue['severity'] == 'error' else '⚠️'
                print(f'  {severity_icon} {issue["file"]}: {issue["message"]}')
            print()
        
        print('=' * 80)
        print('审查完成')
        print('=' * 80)
        print()
        
        if all_passed:
            print('✅ 所有文件审查通过')
            return True
        else:
            print(f'❌ 发现 {len(self.issues)} 个问题')
            return False


def main():
    """主函数"""
    import subprocess
    
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )
    
    staged_files = result.stdout.strip().split('\n')
    staged_files = [f for f in staged_files if f and f.endswith('.md')]
    
    if not staged_files:
        print('未发现需要审查的Markdown文件')
        return 0
    
    reviewer = ResponsibilityReviewer()
    passed = reviewer.run(staged_files)
    
    if not passed:
        print()
        print('⚠️ 提交被阻止，请修复上述问题后重新提交')
        print()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
