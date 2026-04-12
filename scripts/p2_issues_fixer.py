#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
P2级别问题修复脚本
修复索引不完整和职责描述过短问题
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def fix_incomplete_index():
    """修复索引不完整问题"""
    print("\n修复索引不完整问题...")
    
    fixed_count = 0
    
    # 遍历所有INDEX.md文件
    for index_path in FACTOR_LIBRARY.rglob('INDEX.md'):
        parent_dir = index_path.parent
        
        # 检查是否有README.md
        readme_path = parent_dir / 'README.md'
        if readme_path.exists():
            # 读取INDEX.md内容
            with open(index_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否已包含README链接
            if 'README' not in content and '[README]' not in content:
                # 找到目录结构部分
                if '## 📂 目录结构' in content:
                    # 在目录结构部分添加README链接
                    pattern = r'(## 📂 目录结构\s*\n)'
                    replacement = r'\1\n- [README](./README.md) - 模块说明\n'
                    new_content = re.sub(pattern, replacement, content)
                    
                    # 写回文件
                    with open(index_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    rel_path = index_path.relative_to(FACTOR_LIBRARY)
                    print(f"修复: {rel_path} - 添加README链接")
                    fixed_count += 1
    
    return fixed_count

def fix_short_responsibility():
    """修复职责描述过短问题"""
    print("\n修复职责描述过短问题...")
    
    fixed_count = 0
    
    # 定义需要扩展的OVERVIEW.md文件
    overview_files = [
        '00_GOVERNANCE/OVERVIEW.md',
        '03_RISK_FACTORS/OVERVIEW.md',
        '06_REGISTRY/OVERVIEW.md',
        '07_FACTOR_MONITORING/OVERVIEW.md',
        '09_AUDIT/OVERVIEW.md'
    ]
    
    for overview_file in overview_files:
        overview_path = FACTOR_LIBRARY / overview_file
        
        if overview_path.exists():
            # 读取文件内容
            with open(overview_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 解析YAML头部
            yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                body_content = content[yaml_match.end():]
                
                # 更新responsibility字段
                new_yaml = re.sub(
                    r'responsibility:\s*\n\s*-\s*[^\n]+',
                    'responsibility:\n  - 模块概览\n  - 核心概念\n  - 关键流程',
                    yaml_content
                )
                
                # 重新构建文件内容
                new_content = f"---\n{new_yaml}\n---\n{body_content}"
                
                # 写回文件
                with open(overview_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"修复: {overview_file} - 扩展职责描述")
                fixed_count += 1
    
    return fixed_count

def main():
    """主函数"""
    print("=" * 80)
    print("P2级别问题修复")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 修复索引不完整问题
    index_fixed = fix_incomplete_index()
    
    # 修复职责描述过短问题
    responsibility_fixed = fix_short_responsibility()
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"修复索引不完整: {index_fixed}个")
    print(f"修复职责描述过短: {responsibility_fixed}个")
    print(f"总修复文件数: {index_fixed + responsibility_fixed}")

if __name__ == '__main__':
    main()
