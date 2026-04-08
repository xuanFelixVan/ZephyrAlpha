#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专业蓝图文件治理 - 待整合目录处理
删除只有占位符README的目录
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def is_placeholder_readme(file_path):
    """判断是否是占位符README"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 移除YAML头部
        content_no_yaml = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        
        # 移除空白行
        content_clean = re.sub(r'\s+', '', content_no_yaml)
        
        # 检查是否包含占位符关键词
        placeholder_keywords = [
            '此目录正在整合中',
            '文档数量较少',
            '建议整合到父目录',
            '此目录包含',
            '请参考目录中的具体文档'
        ]
        
        has_placeholder = any(kw in content for kw in placeholder_keywords)
        
        # 如果内容很短且包含占位符关键词，则认为是占位符
        if len(content_clean) < 200 and has_placeholder:
            return True
        
        return False
    
    except:
        return False

def find_merge_directories():
    """查找待整合目录"""
    print("=" * 80)
    print("查找待整合目录")
    print("=" * 80)
    
    merge_dirs = []
    
    for dir_path in FACTOR_LIBRARY.rglob('*'):
        if not dir_path.is_dir():
            continue
        
        files = list(dir_path.glob('*.md'))
        file_count = len(files)
        
        # 只处理只有README.md的目录
        if file_count == 1:
            readme_path = dir_path / 'README.md'
            if readme_path.exists() and is_placeholder_readme(readme_path):
                rel_path = dir_path.relative_to(FACTOR_LIBRARY)
                merge_dirs.append({
                    'path': dir_path,
                    'rel_path': str(rel_path),
                    'readme_path': readme_path
                })
    
    print(f"\n发现待整合目录: {len(merge_dirs)}个")
    
    return merge_dirs

def delete_merge_directories(merge_dirs):
    """删除待整合目录"""
    print("\n" + "=" * 80)
    print("删除待整合目录")
    print("=" * 80)
    
    deleted_count = 0
    
    for d in merge_dirs:
        try:
            # 删除README.md
            d['readme_path'].unlink()
            print(f"\n删除文件: {d['rel_path']}/README.md")
            
            # 删除目录
            if not list(d['path'].iterdir()):
                d['path'].rmdir()
                print(f"删除目录: {d['rel_path']}")
                deleted_count += 1
            else:
                print(f"跳过（非空）: {d['rel_path']}")
        except Exception as e:
            print(f"\n删除失败: {d['rel_path']}")
            print(f"  错误: {e}")
    
    print(f"\n删除目录: {deleted_count}")
    return deleted_count

def main():
    """主函数"""
    print("=" * 80)
    print("专业蓝图文件治理 - 待整合目录处理")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    merge_dirs = find_merge_directories()
    deleted_count = delete_merge_directories(merge_dirs)
    
    print("\n" + "=" * 80)
    print("治理完成")
    print("=" * 80)
    print(f"待整合目录: {len(merge_dirs)}")
    print(f"删除目录: {deleted_count}")

if __name__ == '__main__':
    main()
