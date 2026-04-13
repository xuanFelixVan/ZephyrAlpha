# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re
from pathlib import Path

def find_all_index_files(root_dir):
    """查找所有INDEX.md文件"""
    index_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == 'INDEX.md':
                index_files.append(os.path.join(root, file))
    return index_files

def extract_links(content, index_file_path):
    """从INDEX.md内容中提取所有链接"""
    # 匹配Markdown链接格式: [text](url)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    links = []
    for text, url in matches:
        # 只处理相对路径链接，不处理http/https链接
        if not url.startswith('http'):
            links.append({
                'text': text,
                'url': url,
                'index_file': index_file_path
            })
    
    return links

def validate_link(link):
    """验证链接是否有效"""
    index_file_dir = os.path.dirname(link['index_file'])
    target_path = os.path.normpath(os.path.join(index_file_dir, link['url']))
    
    return os.path.exists(target_path), target_path

def main():
    root_dir = 'docs'
    
    print('=' * 80)
    print('索引链接有效性验证')
    print('=' * 80)
    print()
    
    # 查找所有INDEX.md文件
    index_files = find_all_index_files(root_dir)
    print(f'找到 {len(index_files)} 个INDEX.md文件')
    print()
    
    # 统计
    total_links = 0
    valid_links = 0
    invalid_links = []
    
    # 检查每个INDEX.md文件
    for index_file in index_files:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        links = extract_links(content, index_file)
        
        for link in links:
            total_links += 1
            is_valid, target_path = validate_link(link)
            
            if is_valid:
                valid_links += 1
            else:
                invalid_links.append({
                    'index_file': index_file,
                    'text': link['text'],
                    'url': link['url'],
                    'target_path': target_path
                })
    
    # 输出结果
    print('=' * 80)
    print('验证结果')
    print('=' * 80)
    print(f'总链接数: {total_links}')
    print(f'有效链接: {valid_links}')
    print(f'无效链接: {len(invalid_links)}')
    print(f'有效率: {valid_links / total_links * 100:.1f}%' if total_links > 0 else '有效率: 0%')
    print()
    
    if invalid_links:
        print('=' * 80)
        print('无效链接列表')
        print('=' * 80)
        for i, link in enumerate(invalid_links, 1):
            print(f'{i}. INDEX文件: {link["index_file"]}')
            print(f'   链接文本: {link["text"]}')
            print(f'   链接URL: {link["url"]}')
            print(f'   目标路径: {link["target_path"]}')
            print()
    else:
        print('✅ 所有链接均有效！')
    
    print('=' * 80)
    print('验证完成')
    print('=' * 80)

if __name__ == '__main__':
    main()
