#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补充module_id覆盖率
为缺少module_id的文档自动生成module_id
"""

import os
import re
from pathlib import Path
from datetime import datetime

def generate_module_id(file_path, docs_dir):
    """生成module_id"""
    # 获取相对路径
    rel_path = file_path.relative_to(docs_dir)
    
    # 提取关键信息
    parts = list(rel_path.parts)
    
    # 移除docs前缀
    if parts[0] == 'docs':
        parts = parts[1:]
    
    # 构建module_id
    # 格式: 目录层级_文件名_时间戳
    if len(parts) > 1:
        # 提取目录层级
        dir_level = '_'.join(parts[:-1]).upper()
        # 清理特殊字符
        dir_level = re.sub(r'[^A-Z0-9_]', '_', dir_level)
        dir_level = re.sub(r'_+', '_', dir_level).strip('_')
    else:
        dir_level = 'ROOT'
    
    # 提取文件名
    file_name = file_path.stem.upper()
    file_name = re.sub(r'[^A-Z0-9_]', '_', file_name)
    file_name = re.sub(r'_+', '_', file_name).strip('_')
    
    # 添加时间戳
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 组合成module_id
    module_id = f"{dir_level}_{file_name}_{timestamp}"
    
    # 限制长度
    if len(module_id) > 100:
        module_id = module_id[:100]
    
    return module_id

def add_module_id(file_path, docs_dir):
    """为单个文件添加module_id"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否已有module_id
        if re.search(r'^module_id:', content, re.MULTILINE):
            return False
        
        # 生成module_id
        module_id = generate_module_id(file_path, docs_dir)
        
        # 检查是否有YAML头部
        if content.startswith('---'):
            # 在YAML头部添加module_id
            lines = content.split('\n')
            # 在第一个---后添加module_id
            insert_pos = 1
            if lines[0].strip() == '---':
                lines.insert(insert_pos, f'module_id: {module_id}')
            else:
                lines.insert(0, f'---\nmodule_id: {module_id}')
            
            new_content = '\n'.join(lines)
        else:
            # 添加YAML头部
            yaml_header = f"""---
module_id: {module_id}
---

"""
            new_content = yaml_header + content
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
        
        print(f"  ✅ 添加: {file_path.relative_to(docs_dir)}")
        return True
        
    except Exception as e:
        print(f"  ❌ 错误: {file_path.name} - {e}")
        return False

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs")
    
    # 统计
    total_files = 0
    added_files = 0
    
    print("=== 开始补充module_id ===\n")
    
    # 遍历所有Markdown文件
    for md_file in docs_dir.rglob("*.md"):
        # 跳过归档目录
        if any(keyword in str(md_file) for keyword in ['06_ARCHIVE', '09_ARCHIVE', '99_ARCHIVE', 'archive']):
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                
                # 检查是否缺少module_id
                if not re.search(r'^module_id:', content, re.MULTILINE):
                    total_files += 1
                    if add_module_id(md_file, docs_dir):
                        added_files += 1
        except:
            pass
    
    print(f"\n=== 补充完成 ===")
    print(f"总文件数: {total_files}")
    print(f"添加文件数: {added_files}")
    print(f"添加率: {added_files/total_files*100:.2f}%" if total_files > 0 else "添加率: 0%")

if __name__ == "__main__":
    main()
