#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
P2级改进：更新架构引用
替换旧架构引用为新架构术语
"""

import re
from pathlib import Path
from datetime import datetime

class ArchitectureReferenceUpdater:
    def __init__(self, layer_path):
        self.layer_path = Path(layer_path)
        self.stats = {
            'total_files': 0,
            'updated_files': 0,
            'total_replacements': 0,
            'errors': []
        }
        
        # 架构术语映射
        self.architecture_mapping = {
            'Layer 0': '数据层',
            'Layer 1': '数据层',
            'Layer 2': '因子层',
            'Layer 3': '信号层',
            'Layer 4': '策略层',
            'Layer 5': '组合层',
            'Layer 6': '执行层',
            'Layer 7': '风险层',
            'Layer 8': '人机交互层',
            'Layer 9': '基础设施层',
            'Layer0': '数据层',
            'Layer1': '数据层',
            'Layer2': '因子层',
            'Layer3': '信号层',
            'Layer4': '策略层',
            'Layer5': '组合层',
            'Layer6': '执行层',
            'Layer7': '风险层',
            'Layer8': '人机交互层',
            'Layer9': '基础设施层'
        }
    
    def update_all(self):
        """更新所有文件中的架构引用"""
        print("=" * 80)
        print("P2级改进：更新架构引用")
        print("=" * 80)
        print(f"处理范围: {self.layer_path}")
        print()
        
        # 查找所有markdown文件
        md_files = list(self.layer_path.rglob('*.md'))
        self.stats['total_files'] = len(md_files)
        
        print(f"找到 {len(md_files)} 个markdown文件")
        print()
        
        for md_file in md_files:
            self.update_file(md_file)
        
        self.print_stats()
    
    def update_file(self, md_file):
        """更新单个文件中的架构引用"""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            replacements = 0
            
            # 替换架构术语
            for old_term, new_term in self.architecture_mapping.items():
                # 统计替换次数
                count = content.count(old_term)
                if count > 0:
                    replacements += count
                    content = content.replace(old_term, new_term)
            
            if content != original_content:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.stats['updated_files'] += 1
                self.stats['total_replacements'] += replacements
                print(f"✅ 已更新: {md_file.relative_to(self.layer_path)} ({replacements}处替换)")
            else:
                print(f"⏭️  跳过: {md_file.relative_to(self.layer_path)} (无需更新)")
            
        except Exception as e:
            self.stats['errors'].append({
                'file': str(md_file),
                'error': str(e)
            })
            print(f"❌ 错误: {md_file.relative_to(self.layer_path)} - {e}")
    
    def print_stats(self):
        """输出统计信息"""
        print()
        print("=" * 80)
        print("更新统计")
        print("=" * 80)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"更新文件数: {self.stats['updated_files']}")
        print(f"总替换次数: {self.stats['total_replacements']}")
        print(f"错误数: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print()
            print("错误详情:")
            for error in self.stats['errors']:
                print(f"  - {error['file']}: {error['error']}")


def main():
    layer_path = Path(r"D:\ZephyrAlpha\docs\08_HUMAN_AI_INTERFACE")
    
    updater = ArchitectureReferenceUpdater(layer_path)
    updater.update_all()
    
    print()
    print("=" * 80)
    print("更新完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
