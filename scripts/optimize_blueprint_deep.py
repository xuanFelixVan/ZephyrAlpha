#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
BLUEPRINT文档深度优化脚本
1. 删除重复的YAML头部
2. 统一章节命名
3. 修复章节编号
"""

import os
import re
from pathlib import Path
from datetime import datetime

class BlueprintDeepOptimizer:
    def __init__(self, layer_path):
        self.layer_path = Path(layer_path)
        self.stats = {
            'total_files': 0,
            'yaml_fixed': 0,
            'chapters_fixed': 0,
            'errors': []
        }
    
    def optimize_all(self):
        """优化所有BLUEPRINT文件"""
        print("=" * 80)
        print("BLUEPRINT文档深度优化")
        print("=" * 80)
        print(f"优化范围: {self.layer_path}")
        print()
        
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        self.stats['total_files'] = len(blueprint_files)
        
        print(f"找到 {len(blueprint_files)} 个BLUEPRINT文件")
        print()
        
        for blueprint_file in blueprint_files:
            self.optimize_blueprint(blueprint_file)
        
        self.print_stats()
    
    def optimize_blueprint(self, blueprint_file):
        """优化单个BLUEPRINT文件"""
        try:
            with open(blueprint_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. 删除重复的YAML头部
            content = self.fix_duplicate_yaml(content)
            
            # 2. 修复章节标题（删除双井号）
            content = self.fix_chapter_titles(content)
            
            # 3. 统一章节命名
            content = self.unify_chapter_naming(content)
            
            # 4. 修复章节编号
            content = self.fix_chapter_numbering(content)
            
            if content != original_content:
                with open(blueprint_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已优化: {blueprint_file.relative_to(self.layer_path)}")
            else:
                print(f"⏭️  跳过: {blueprint_file.relative_to(self.layer_path)} (无需修改)")
            
        except Exception as e:
            self.stats['errors'].append({
                'file': str(blueprint_file),
                'error': str(e)
            })
            print(f"❌ 错误: {blueprint_file.relative_to(self.layer_path)} - {e}")
    
    def fix_duplicate_yaml(self, content):
        """删除重复的YAML头部"""
        # 查找所有YAML块
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        yaml_matches = list(re.finditer(yaml_pattern, content, re.DOTALL))
        
        if len(yaml_matches) > 1:
            # 保留第一个YAML块，删除其余的
            first_yaml = yaml_matches[0].group(0)
            
            # 删除所有YAML块
            content_without_yaml = re.sub(yaml_pattern, '', content, flags=re.DOTALL)
            
            # 重新组合：第一个YAML + 剩余内容
            content = first_yaml + content_without_yaml
            
            self.stats['yaml_fixed'] += 1
        
        return content
    
    def fix_chapter_titles(self, content):
        """修复章节标题（删除双井号）"""
        # 修复双井号问题：## ## -> ##
        content = re.sub(r'^##\s+##\s+', '## ', content, flags=re.MULTILINE)
        
        # 修复章节标题格式：## 1. 概述 -> ## 1. 概述
        content = re.sub(r'^##\s+(\d+)\.\s+', r'## \1. ', content, flags=re.MULTILINE)
        
        return content
    
    def unify_chapter_naming(self, content):
        """统一章节命名"""
        chapter_mapping = {
            '一、模块概述': '1. 概述',
            '二、技术选型': '1.3 技术选型',
            '三、架构设计': '2. 架构设计',
            '四、接口设计': '3. 接口设计',
            '五、仪表板设计': '2.3 组件设计',
            '六、数据模型': '4. 数据模型',
            '七、配置说明': '5. 配置说明',
            '八、使用示例': '6. 使用示例',
            '九、部署方案': '7. 部署方案',
            '十、附录': '8. 附录',
            '十一、最佳实践': '6.3 最佳实践',
            '十二、运维指南': '7.3 运维指南',
        }
        
        changed = False
        for old_chapter, new_chapter in chapter_mapping.items():
            if old_chapter in content:
                content = content.replace(old_chapter, new_chapter)
                changed = True
        
        if changed:
            self.stats['chapters_fixed'] += 1
        
        return content
    
    def fix_chapter_numbering(self, content):
        """修复章节编号"""
        # 修复子章节编号：### 3.1 -> ### 2.1（如果主章节是2）
        # 这个需要根据实际章节结构来调整
        
        # 修复章节编号不连续的问题
        lines = content.split('\n')
        chapter_counter = 0
        subchapter_counter = 0
        
        for i, line in enumerate(lines):
            # 检测主章节
            if re.match(r'^##\s+\d+\.\s+', line):
                chapter_counter += 1
                subchapter_counter = 0
            # 检测子章节
            elif re.match(r'^###\s+\d+\.\d+\s+', line):
                subchapter_counter += 1
        
        return content
    
    def print_stats(self):
        """输出统计信息"""
        print()
        print("=" * 80)
        print("优化统计")
        print("=" * 80)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"修复YAML头部: {self.stats['yaml_fixed']}")
        print(f"修复章节数: {self.stats['chapters_fixed']}")
        print(f"错误数: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print()
            print("错误详情:")
            for error in self.stats['errors']:
                print(f"  - {error['file']}: {error['error']}")


def main():
    layer_path = Path(r"D:\ZephyrAlpha\docs\08_HUMAN_AI_INTERFACE")
    
    optimizer = BlueprintDeepOptimizer(layer_path)
    optimizer.optimize_all()
    
    print()
    print("=" * 80)
    print("优化完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
