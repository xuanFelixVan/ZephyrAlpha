#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
补充缺失的职责描述
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def generate_responsibility(file_path, title):
    """根据文件路径和标题生成职责描述"""
    rel_path = file_path.relative_to(FACTOR_LIBRARY)
    parts = rel_path.parts[:-1]
    file_name = file_path.stem
    
    # 根据文件类型生成职责
    if file_name.upper() == 'INDEX':
        if parts:
            return f"{parts[-1]}目录索引与导航"
        else:
            return "因子库目录索引与导航"
    
    if file_name.upper() == 'README':
        if parts:
            return f"{parts[-1]}模块说明文档"
        else:
            return "因子库说明文档"
    
    if file_name.upper() == 'BLUEPRINT':
        if parts:
            return f"{parts[-1]}蓝图设计文档"
        else:
            return "蓝图设计文档"
    
    # 根据标题生成
    if title:
        # 移除常见后缀
        title = re.sub(r'\s*(文档|指南|标准|规范|系统|框架|模块|组件|工具|接口|连接器|蓝图)$', '', title)
        return f"{title}相关文档"
    
    # 根据文件名生成
    clean_name = re.sub(r'[_-]', ' ', file_name)
    return f"{clean_name}相关文档"

def fix_responsibility():
    """补充缺失的职责描述"""
    print("=" * 80)
    print("补充缺失的职责描述")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 扫描所有文件
    all_files = list(FACTOR_LIBRARY.rglob('*.md'))
    print(f"\n扫描文件: {len(all_files)}个")
    
    fixed_count = 0
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否有responsibility字段
            if 'responsibility:' not in content:
                continue
            
            # 提取responsibility值
            match = re.search(r'responsibility:\s*\n?\s*-\s*(.+?)(?:\n|$)', content)
            
            if match:
                resp_value = match.group(1).strip()
                
                # 检查职责描述是否过短或无意义
                if len(resp_value) < 5 or resp_value in ['管理因子库', '提供使用指南', '文档', '系统']:
                    # 提取标题
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else None
                    
                    # 生成新的职责描述
                    new_responsibility = generate_responsibility(file_path, title)
                    
                    # 替换职责描述
                    new_content = re.sub(
                        r'responsibility:\s*\n?\s*-\s*.+?(?:\n|$)',
                        f'responsibility:\n  - {new_responsibility}\n',
                        content
                    )
                    
                    # 写入文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"\n{file_path.relative_to(FACTOR_LIBRARY)}")
                    print(f"  {resp_value} -> {new_responsibility}")
                    fixed_count += 1
        
        except Exception as e:
            print(f"  错误: {e}")
    
    print("\n" + "=" * 80)
    print("补充完成")
    print("=" * 80)
    print(f"修复文件: {fixed_count}")

if __name__ == '__main__':
    fix_responsibility()
