#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
第25轮审计P1问题修复脚本
功能：修复所有P1级别问题
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def fix_index_responsibility():
    """修复INDEX.md职责描述"""
    print("=" * 80)
    print("修复INDEX.md职责描述")
    print("=" * 80)
    
    # 找到所有INDEX.md文件
    index_files = []
    for root, dirs, files in os.walk(DOCS_DIR / "02_FACTOR_LIBRARY"):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        if 'INDEX.md' in files:
            index_files.append(os.path.join(root, 'INDEX.md'))
    
    print(f"找到 {len(index_files)} 个INDEX.md文件")
    
    fixed_count = 0
    for index_file in index_files:
        try:
            with open(index_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否有标准职责描述格式
            if '**核心职责**:' not in content:
                # 提取目录名
                dir_name = os.path.basename(os.path.dirname(index_file))
                
                # 添加标准职责描述
                responsibility_block = f"""

> **核心职责**: {dir_name}模块目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：{dir_name}模块目录导航、文档索引、阅读路径推荐
> - ❌ 本文档不负责：具体模块内容、实施细节、技术规范
"""
                
                # 在第一个标题后插入
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    insert_pos = title_match.end()
                    new_content = content[:insert_pos] + responsibility_block + content[insert_pos:]
                    
                    with open(index_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    fixed_count += 1
                    print(f"✅ 修复: {os.path.relpath(index_file, DOCS_DIR)}")
        except Exception as e:
            print(f"❌ 错误: {os.path.relpath(index_file, DOCS_DIR)} - {str(e)}")
    
    print(f"\n修复完成: {fixed_count} 个文件")
    return fixed_count

def fix_blueprint_responsibility():
    """修复BLUEPRINT.md职责描述"""
    print("\n" + "=" * 80)
    print("修复BLUEPRINT.md职责描述")
    print("=" * 80)
    
    # 找到所有BLUEPRINT.md文件
    blueprint_files = []
    for root, dirs, files in os.walk(DOCS_DIR / "02_FACTOR_LIBRARY"):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        if 'BLUEPRINT.md' in files:
            blueprint_files.append(os.path.join(root, 'BLUEPRINT.md'))
    
    print(f"找到 {len(blueprint_files)} 个BLUEPRINT.md文件")
    
    fixed_count = 0
    for blueprint_file in blueprint_files:
        try:
            with open(blueprint_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否有标准职责描述格式
            if '**核心职责**:' not in content:
                # 提取目录名
                dir_name = os.path.basename(os.path.dirname(blueprint_file))
                
                # 添加标准职责描述
                responsibility_block = f"""

> **核心职责**: {dir_name}模块蓝图设计和架构规划
> **职责边界**: 
> - ✅ 本文档负责：{dir_name}模块架构设计、技术选型、接口定义、实施路径
> - ❌ 本文档不负责：具体代码实现、测试用例、部署流程
"""
                
                # 在第一个标题后插入
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    insert_pos = title_match.end()
                    new_content = content[:insert_pos] + responsibility_block + content[insert_pos:]
                    
                    with open(blueprint_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    fixed_count += 1
                    print(f"✅ 修复: {os.path.relpath(blueprint_file, DOCS_DIR)}")
        except Exception as e:
            print(f"❌ 错误: {os.path.relpath(blueprint_file, DOCS_DIR)} - {str(e)}")
    
    print(f"\n修复完成: {fixed_count} 个文件")
    return fixed_count

def check_duplicate_content():
    """检查重复内容"""
    print("\n" + "=" * 80)
    print("检查重复内容")
    print("=" * 80)
    
    duplicates = [
        {
            'path1': '02_FACTOR_LIBRARY/04_DATA_SOURCE/07_DATA_PIPELINE/BLUEPRINT.md',
            'path2': '02_FACTOR_LIBRARY/04_DATA_SOURCE/07_DATA_PIPELINE/README.md',
            'title': '数据流水线蓝图'
        },
        {
            'path1': '02_FACTOR_LIBRARY/04_DATA_SOURCE/IFIND/INDEX.md',
            'path2': '02_FACTOR_LIBRARY/04_DATA_SOURCE/IFIND/README.md',
            'title': 'iFind数据源'
        }
    ]
    
    for dup in duplicates:
        file1 = DOCS_DIR / dup['path1']
        file2 = DOCS_DIR / dup['path2']
        
        print(f"\n检查: {dup['title']}")
        print(f"  文件1: {dup['path1']}")
        print(f"  文件2: {dup['path2']}")
        
        if file1.exists() and file2.exists():
            with open(file1, 'r', encoding='utf-8-sig') as f:
                content1 = f.read()
            with open(file2, 'r', encoding='utf-8-sig') as f:
                content2 = f.read()
            
            # 比较内容
            if content1 == content2:
                print("  ⚠️ 内容完全相同，建议删除其中一个")
            else:
                print("  ✅ 内容不同，职责可能有差异")
                
                # 检查职责描述
                resp1 = re.search(r'\*\*核心职责\*\*:\s*(.+)', content1)
                resp2 = re.search(r'\*\*核心职责\*\*:\s*(.+)', content2)
                
                if resp1 and resp2:
                    print(f"  文件1职责: {resp1.group(1)}")
                    print(f"  文件2职责: {resp2.group(1)}")
                else:
                    print("  ⚠️ 缺少职责描述")
        else:
            print("  ⚠️ 文件不存在")
    
    return len(duplicates)

def main():
    """主函数"""
    print("第25轮审计P1问题修复")
    print("=" * 80)
    
    # 修复INDEX.md职责描述
    index_fixed = fix_index_responsibility()
    
    # 修复BLUEPRINT.md职责描述
    blueprint_fixed = fix_blueprint_responsibility()
    
    # 检查重复内容
    duplicate_count = check_duplicate_content()
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"INDEX.md修复: {index_fixed} 个")
    print(f"BLUEPRINT.md修复: {blueprint_fixed} 个")
    print(f"重复内容检查: {duplicate_count} 对")

if __name__ == '__main__':
    main()
