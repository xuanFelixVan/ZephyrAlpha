#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 5 第八轮深度修复工具
修复发现的问题：
1. 删除备份文件
2. 修复重复YAML头部
3. 修复重复核心定位章节
4. 修复职责描述过长
"""

import os
import re
from pathlib import Path
from datetime import datetime


class Layer5EighthRoundFixer:
    """Layer 5第八轮修复器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.fixes = []
        self.deletions = []
        
        self.max_responsibility_length = 200
        
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
    
    def delete_backup_files(self):
        """删除备份文件"""
        print('\n🗑️ 删除备份文件...')
        
        backup_patterns = ['*.bak', '*.bak2', '*.bak3', '*.backup', '*.old']
        deleted_count = 0
        
        for pattern in backup_patterns:
            for backup_file in self.blueprints_dir.glob(pattern):
                try:
                    backup_file.unlink()
                    self.deletions.append({
                        'file': backup_file.name,
                        'reason': '备份文件'
                    })
                    deleted_count += 1
                    print(f'  ✅ 已删除: {backup_file.name}')
                except Exception as e:
                    print(f'  ❌ 删除失败: {backup_file.name} - {e}')
        
        print(f'  ✅ 删除完成: {deleted_count}个备份文件')
        return deleted_count
    
    def fix_duplicate_yaml_headers(self):
        """修复重复YAML头部"""
        print('\n🔧 修复重复YAML头部...')
        
        fixed_count = 0
        files_to_fix = [
            'DATA_CATALOG_BLUEPRINT.md',
            'DATA_CATALOG_METADATA_BLUEPRINT.md'
        ]
        
        for doc_name in files_to_fix:
            doc_path = self.blueprints_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = self.read_file(doc_path)
            if not content:
                continue
            
            pattern = r'^---\s*\n.*?\n---\s*\n\s*---\s*\n.*?\n---\s*\n'
            
            if re.search(pattern, content, re.DOTALL):
                first_yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                
                if first_yaml_match:
                    first_yaml = first_yaml_match.group(0)
                    remaining_content = content[first_yaml_match.end():]
                    
                    remaining_content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', remaining_content, count=1, flags=re.DOTALL)
                    
                    new_content = first_yaml + remaining_content
                    
                    if self.write_file(doc_path, new_content):
                        fixed_count += 1
                        self.fixes.append({
                            'type': '重复YAML头部',
                            'file': doc_name,
                            'action': '删除重复YAML头部'
                        })
                        print(f'  ✅ 已修复: {doc_name}')
        
        print(f'  ✅ YAML修复完成: {fixed_count}个文档')
        return fixed_count
    
    def fix_duplicate_core_positioning(self):
        """修复重复核心定位章节"""
        print('\n🔧 修复重复核心定位章节...')
        
        fixed_count = 0
        
        for md_file in self.blueprints_dir.glob('*.md'):
            content = self.read_file(md_file)
            if not content:
                continue
            
            pattern = r'##\s+核心定位'
            matches = list(re.finditer(pattern, content))
            
            if len(matches) > 1:
                first_match = matches[0]
                
                next_section_pattern = r'\n##\s+'
                next_match = re.search(next_section_pattern, content[first_match.end():])
                
                if next_match:
                    first_section_end = first_match.end() + next_match.start()
                else:
                    first_section_end = len(content)
                
                first_section = content[first_match.start():first_section_end]
                
                remaining_content = content[first_section_end:]
                
                remaining_content = re.sub(pattern, '', remaining_content, count=len(matches)-1)
                
                remaining_content = re.sub(
                    r'\n\n负责[^#]*?(?=\n##|\n#|\Z)',
                    '',
                    remaining_content,
                    flags=re.DOTALL
                )
                
                new_content = content[:first_match.start()] + first_section + remaining_content
                
                if self.write_file(md_file, new_content):
                    fixed_count += 1
                    self.fixes.append({
                        'type': '重复核心定位',
                        'file': md_file.name,
                        'action': f'删除{len(matches)-1}个重复章节'
                    })
                    print(f'  ✅ 已修复: {md_file.name} ({len(matches)}个核心定位 → 1个)')
        
        print(f'  ✅ 核心定位修复完成: {fixed_count}个文档')
        return fixed_count
    
    def fix_long_responsibility(self):
        """修复职责描述过长"""
        print('\n🔧 修复职责描述过长...')
        
        fixed_count = 0
        files_to_fix = {
            'DATA_PREPROCESSING_COMPLETE_ARCHITECTURE_BLUEPRINT.md': '负责数据预处理完整架构设计，梳理数据预处理整体架构，确保架构完整性和一致性，提供模块集成和实施路径规划。',
            'FACTOR_NEUTRAL_OPTIMIZATION_BLUEPRINT.md': '负责因子中性优化模块设计，实现因子暴露中性化处理，优化投资组合的因子风险暴露，确保组合符合因子中性约束。'
        }
        
        for doc_name, new_responsibility in files_to_fix.items():
            doc_path = self.blueprints_dir / doc_name
            if not doc_path.exists():
                continue
            
            content = self.read_file(doc_path)
            if not content:
                continue
            
            pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n\n|\n##|\Z)'
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
    
    def fix_data_catalog_similarity(self):
        """修复DATA_CATALOG和DATA_CATALOG_METADATA的职责相似问题"""
        print('\n🔧 修复DATA_CATALOG职责相似问题...')
        
        fixed_count = 0
        
        data_catalog_path = self.blueprints_dir / 'DATA_CATALOG_BLUEPRINT.md'
        data_catalog_meta_path = self.blueprints_dir / 'DATA_CATALOG_METADATA_BLUEPRINT.md'
        
        new_data_catalog_resp = '负责数据目录的设计与构建，提供数据资产注册、分类、检索和血缘追踪功能，支持数据治理和资产管理。'
        
        new_data_catalog_meta_resp = '负责数据目录元数据管理的设计与实现，提供元数据采集、存储、查询和版本控制功能，支持数据血缘追踪和影响分析。'
        
        if data_catalog_path.exists():
            content = self.read_file(data_catalog_path)
            if content:
                pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n\n|\n##|\Z)'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    new_content = content[:match.start(2)] + new_data_catalog_resp + content[match.end(2):]
                    
                    if self.write_file(data_catalog_path, new_content):
                        fixed_count += 1
                        self.fixes.append({
                            'type': '职责相似',
                            'file': 'DATA_CATALOG_BLUEPRINT.md',
                            'action': '更新职责描述以区分'
                        })
                        print(f'  ✅ 已修复: DATA_CATALOG_BLUEPRINT.md')
        
        if data_catalog_meta_path.exists():
            content = self.read_file(data_catalog_meta_path)
            if content:
                pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n\n|\n##|\Z)'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    new_content = content[:match.start(2)] + new_data_catalog_meta_resp + content[match.end(2):]
                    
                    if self.write_file(data_catalog_meta_path, new_content):
                        fixed_count += 1
                        self.fixes.append({
                            'type': '职责相似',
                            'file': 'DATA_CATALOG_METADATA_BLUEPRINT.md',
                            'action': '更新职责描述以区分'
                        })
                        print(f'  ✅ 已修复: DATA_CATALOG_METADATA_BLUEPRINT.md')
        
        print(f'  ✅ 职责区分修复完成: {fixed_count}个文档')
        return fixed_count
    
    def generate_report(self):
        """生成修复报告"""
        print('\n📊 生成修复报告...')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_EIGHTH_ROUND_FIX_REPORT_{timestamp}.md'
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 第八轮深度修复报告\n\n')
            f.write(f'> **修复时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'> **修复范围**: {self.blueprints_dir}\n\n')
            
            f.write('## 📊 修复统计\n\n')
            f.write(f'- **删除文件**: {len(self.deletions)}个\n')
            f.write(f'- **修复文档**: {len(self.fixes)}个\n\n')
            
            if self.deletions:
                f.write('## 🗑️ 删除文件列表\n\n')
                for deletion in self.deletions:
                    f.write(f'- **{deletion["file"]}**: {deletion["reason"]}\n')
                f.write('\n')
            
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
        print('Layer 5 第八轮深度修复')
        print('=' * 80)
        
        self.delete_backup_files()
        self.fix_duplicate_yaml_headers()
        self.fix_duplicate_core_positioning()
        self.fix_long_responsibility()
        self.fix_data_catalog_similarity()
        
        self.generate_report()
        
        print('\n' + '=' * 80)
        print('修复完成')
        print('=' * 80)
        print(f'\n📊 修复统计:')
        print(f'  - 删除文件: {len(self.deletions)}个')
        print(f'  - 修复文档: {len(self.fixes)}个')


if __name__ == '__main__':
    fixer = Layer5EighthRoundFixer()
    fixer.run()
