#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索引文档优化脚本
优化人机交互层所有INDEX.md文件，减少重复内容
"""

import os
import re
from pathlib import Path
from datetime import datetime

class IndexOptimizer:
    def __init__(self, layer_path):
        self.layer_path = Path(layer_path)
        self.stats = {
            'total_files': 0,
            'optimized_files': 0,
            'skipped_files': 0,
            'errors': []
        }
    
    def optimize_all(self):
        """优化所有INDEX.md文件"""
        print("=" * 80)
        print("索引文档优化")
        print("=" * 80)
        print(f"优化范围: {self.layer_path}")
        print()
        
        # 查找所有INDEX.md文件
        index_files = list(self.layer_path.rglob('INDEX.md'))
        self.stats['total_files'] = len(index_files)
        
        print(f"找到 {len(index_files)} 个INDEX.md文件")
        print()
        
        for index_file in index_files:
            self.optimize_index(index_file)
        
        # 输出统计
        self.print_stats()
    
    def optimize_index(self, index_file):
        """优化单个INDEX.md文件"""
        try:
            # 读取文件
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取关键信息
            info = self.extract_info(content, index_file)
            
            # 生成优化后的内容
            optimized_content = self.generate_optimized_content(info)
            
            # 写回文件
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
            
            self.stats['optimized_files'] += 1
            print(f"✅ 已优化: {index_file.relative_to(self.layer_path)}")
            
        except Exception as e:
            self.stats['errors'].append({
                'file': str(index_file),
                'error': str(e)
            })
            print(f"❌ 错误: {index_file.relative_to(self.layer_path)} - {e}")
    
    def extract_info(self, content, index_file):
        """提取索引文件的关键信息"""
        info = {
            'file_path': index_file,
            'relative_path': str(index_file.relative_to(self.layer_path))
        }
        
        # 提取YAML头部
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            
            # 提取module_id
            module_id_match = re.search(r'module_id:\s*(.+)', yaml_content)
            if module_id_match:
                info['module_id'] = module_id_match.group(1).strip()
            
            # 提取version
            version_match = re.search(r'version:\s*(.+)', yaml_content)
            if version_match:
                info['version'] = version_match.group(1).strip()
            
            # 提取created_date
            created_match = re.search(r'created_date:\s*(.+)', yaml_content)
            if created_match:
                info['created_date'] = created_match.group(1).strip()
            
            # 提取applicable_scope
            scope_match = re.search(r'applicable_scope:\s*(.+)', yaml_content)
            if scope_match:
                info['applicable_scope'] = scope_match.group(1).strip()
        
        # 提取模块编号和名称
        path_parts = index_file.relative_to(self.layer_path).parts
        if len(path_parts) > 1:
            dir_name = path_parts[0]
            # 提取编号和名称（如：01_MONITORING -> 01, MONITORING）
            match = re.match(r'(\d+)_(.+)', dir_name)
            if match:
                info['module_number'] = match.group(1)
                info['module_name'] = match.group(2).replace('_', ' ').title()
        
        # 查找BLUEPRINT文件
        parent_dir = index_file.parent
        blueprint_files = list(parent_dir.glob('*_BLUEPRINT.md'))
        if blueprint_files:
            blueprint_file = blueprint_files[0]
            info['blueprint_file'] = blueprint_file.name
            info['blueprint_name'] = blueprint_file.stem.replace('_', ' ')
        
        return info
    
    def generate_optimized_content(self, info):
        """生成优化后的索引内容"""
        # 使用最小化模板
        template = f"""---
module_id: {info.get('module_id', 'INDEX_UNKNOWN_001')}
version: {info.get('version', '1.0.0')}
status: Active
created_date: {info.get('created_date', datetime.now().strftime('%Y-%m-%d'))}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 文档治理系统
responsibility:
  - 索引文档、导航目录
standard_type: 索引文档
applicable_scope: {info.get('applicable_scope', '文档索引导航')}
compliance_level: 专业标准
---

# {info.get('module_number', '00')} {info.get('module_name', 'Unknown')}索引

> **核心职责**: 目录导航和文档索引
> **版本**: v{info.get('version', '1.0.0')}
> **索引**: `{info.get('module_id', 'INDEX_UNKNOWN_001')}`

## 📄 文档列表

"""
        
        # 添加蓝图文件
        if 'blueprint_file' in info:
            template += f"""| 文档名称 | 类型 | 状态 | 说明 |
|---------|------|------|------|
| [{info['blueprint_name']}]({info['blueprint_file']}) | 蓝图 | 活跃 | 模块功能设计和实现方案 |

"""
        
        template += f"""---

**索引状态**: ✅ 活跃 | **维护**: 按需更新
"""
        
        return template
    
    def print_stats(self):
        """输出统计信息"""
        print()
        print("=" * 80)
        print("优化统计")
        print("=" * 80)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"已优化: {self.stats['optimized_files']}")
        print(f"已跳过: {self.stats['skipped_files']}")
        print(f"错误数: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print()
            print("错误详情:")
            for error in self.stats['errors']:
                print(f"  - {error['file']}: {error['error']}")


def main():
    layer_path = Path(r"D:\ZephyrAlpha\docs\08_HUMAN_AI_INTERFACE")
    
    optimizer = IndexOptimizer(layer_path)
    optimizer.optimize_all()
    
    print()
    print("=" * 80)
    print("优化完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
