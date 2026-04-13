#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 5 YAML头部和职责描述修复工具
修复发现的问题：
1. 缺少YAML头部标记
2. 职责描述过长
3. 职责描述格式混乱
"""

import os
import re
from pathlib import Path
from datetime import datetime


class Layer5YAMLResponsibilityFixer:
    """Layer 5 YAML头部和职责描述修复器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.fixes = []
        self.max_responsibility_length = 200
        
        self.responsibility_fixes = {
            'DATA_PREPROCESSING_COMPLETE_ARCHITECTURE_BLUEPRINT.md': 
                '负责数据预处理完整架构设计，梳理数据预处理整体架构，确保架构完整性和一致性，提供模块集成和实施路径规划。',
            'FACTOR_EXPOSURE_MANAGEMENT_BLUEPRINT.md': 
                '负责因子暴露管理模块设计，监控组合因子暴露，实现因子中性化和风险控制功能，支持组合风险管理。',
            'FACTOR_NEUTRAL_OPTIMIZATION_BLUEPRINT.md': 
                '负责因子中性优化模块设计，实现因子暴露中性化处理，优化投资组合的因子风险暴露，确保组合符合因子中性约束。'
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
    
    def write_file(self, file_path: Path, content: str):
        """写入文件内容"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f'  ❌ 无法写入文件 {file_path.name}: {e}')
            return False
    
    def fix_missing_yaml_header(self):
        """修复缺少YAML头部标记的文档"""
        print('\n🔧 修复缺少YAML头部标记的文档...')
        
        fixed_count = 0
        
        for md_file in self.blueprints_dir.glob('*.md'):
            if md_file.name == 'INDEX.md':
                continue
                
            content = self.read_file(md_file)
            if not content:
                continue
            
            if content.strip().startswith('module_id:'):
                yaml_end_match = re.search(r'^layer:\s*[^\n]+\n', content, re.MULTILINE)
                
                if yaml_end_match:
                    yaml_content = content[:yaml_end_match.end()]
                    remaining_content = content[yaml_end_match.end():]
                    
                    remaining_content = remaining_content.lstrip('\n')
                    
                    new_content = '---\n' + yaml_content + '---\n\n' + remaining_content
                    
                    if self.write_file(md_file, new_content):
                        fixed_count += 1
                        self.fixes.append({
                            'type': '缺少YAML头部',
                            'file': md_file.name,
                            'action': '添加YAML头部标记'
                        })
                        print(f'  ✅ 已修复: {md_file.name}')
        
        print(f'  ✅ YAML头部修复完成: {fixed_count}个文档')
        return fixed_count
    
    def fix_long_responsibility(self):
        """修复职责描述过长"""
        print('\n🔧 修复职责描述过长...')
        
        fixed_count = 0
        
        for doc_name, new_responsibility in self.responsibility_fixes.items():
            doc_path = self.blueprints_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = self.read_file(doc_path)
            if not content:
                continue
            
            pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n\n|\n##|\n#|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                old_responsibility = match.group(2).strip()
                
                if len(old_responsibility) > self.max_responsibility_length:
                    new_content = content[:match.start(2)] + new_responsibility + content[match.end(2):]
                    
                    if self.write_file(doc_path, new_content):
                        fixed_count += 1
                        self.fixes.append({
                            'type': '职责描述过长',
                            'file': doc_name,
                            'action': f'缩短职责描述: {len(old_responsibility)}字 → {len(new_responsibility)}字'
                        })
                        print(f'  ✅ 已修复: {doc_name} ({len(old_responsibility)}字 → {len(new_responsibility)}字)')
        
        print(f'  ✅ 职责描述修复完成: {fixed_count}个文档')
        return fixed_count
    
    def fix_malformed_responsibility(self):
        """修复格式混乱的职责描述"""
        print('\n🔧 修复格式混乱的职责描述...')
        
        fixed_count = 0
        
        for md_file in self.blueprints_dir.glob('*.md'):
            if md_file.name == 'INDEX.md':
                continue
                
            content = self.read_file(md_file)
            if not content:
                continue
            
            pattern = r'##\s+核心定位\s*\n\n\s*\n> \*\*职责边界\*\*:'
            
            if re.search(pattern, content):
                new_content = re.sub(
                    r'(##\s+核心定位\s*\n\n)\s*\n(> \*\*职责边界\*\*:)',
                    r'\1\2',
                    content
                )
                
                if new_content != content:
                    if self.write_file(md_file, new_content):
                        fixed_count += 1
                        self.fixes.append({
                            'type': '职责描述格式',
                            'file': md_file.name,
                            'action': '修复核心定位格式'
                        })
                        print(f'  ✅ 已修复: {md_file.name}')
        
        print(f'  ✅ 格式修复完成: {fixed_count}个文档')
        return fixed_count
    
    def generate_report(self):
        """生成修复报告"""
        print('\n📊 生成修复报告...')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_YAML_RESPONSIBILITY_FIX_REPORT_{timestamp}.md'
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 YAML头部和职责描述修复报告\n\n')
            f.write(f'> **修复时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'> **修复范围**: {self.blueprints_dir}\n\n')
            
            f.write('## 📊 修复统计\n\n')
            f.write(f'- **修复文档**: {len(self.fixes)}个\n\n')
            
            if self.fixes:
                f.write('## 🔧 修复详情\n\n')
                f.write('| 类型 | 文件 | 操作 |\n')
                f.write('|------|------|------|\n')
                for fix in self.fixes:
                    f.write(f'| {fix["type"]} | {fix["file"]} | {fix["action"]} |\n')
                f.write('\n')
            
            f.write('---\n\n')
            f.write(f'**修复完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        print(f'  ✅ 修复报告已生成: {report_file}')
        return report_file
    
    def run(self):
        """执行修复"""
        print('=' * 80)
        print('Layer 5 YAML头部和职责描述修复')
        print('=' * 80)
        
        self.fix_missing_yaml_header()
        self.fix_long_responsibility()
        self.fix_malformed_responsibility()
        
        self.generate_report()
        
        print('\n' + '=' * 80)
        print('修复完成')
        print('=' * 80)
        print(f'\n📊 修复统计:')
        print(f'  - 修复文档: {len(self.fixes)}个')


if __name__ == '__main__':
    fixer = Layer5YAMLResponsibilityFixer()
    fixer.run()
