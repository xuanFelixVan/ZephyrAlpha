import os
import re
from pathlib import Path
from collections import defaultdict

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
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    links = []
    for text, url in matches:
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

def analyze_invalid_links():
    """分析无效链接的原因"""
    root_dir = 'docs'
    
    # 查找所有INDEX.md文件
    index_files = find_all_index_files(root_dir)
    
    # 统计
    invalid_links = []
    
    # 检查每个INDEX.md文件
    for index_file in index_files:
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(index_file, 'r', encoding='gbk') as f:
                    content = f.read()
            except:
                continue
        
        links = extract_links(content, index_file)
        
        for link in links:
            is_valid, target_path = validate_link(link)
            
            if not is_valid:
                # 分析原因
                reason = analyze_reason(link['url'], target_path)
                invalid_links.append({
                    'index_file': index_file,
                    'text': link['text'],
                    'url': link['url'],
                    'target_path': target_path,
                    'reason': reason
                })
    
    return invalid_links

def analyze_reason(url, target_path):
    """分析无效链接的原因"""
    # 检查是否是文件被删除
    if not os.path.exists(target_path):
        # 检查父目录是否存在
        parent_dir = os.path.dirname(target_path)
        if not os.path.exists(parent_dir):
            return "父目录不存在"
        
        # 检查是否有类似文件
        filename = os.path.basename(target_path)
        parent_files = os.listdir(parent_dir) if os.path.exists(parent_dir) else []
        similar_files = [f for f in parent_files if filename.split('.')[0] in f]
        
        if similar_files:
            return f"文件不存在，但存在类似文件: {', '.join(similar_files)}"
        else:
            return "文件已被删除或移动"
    
    return "未知原因"

def generate_report(invalid_links):
    """生成分析报告"""
    print('=' * 80)
    print('无效链接分析报告')
    print('=' * 80)
    print()
    
    # 按原因分组
    reason_groups = defaultdict(list)
    for link in invalid_links:
        reason_groups[link['reason']].append(link)
    
    # 输出统计
    print(f'总无效链接数: {len(invalid_links)}')
    print()
    
    print('按原因分组统计:')
    print('-' * 80)
    for reason, links in sorted(reason_groups.items(), key=lambda x: len(x[1]), reverse=True):
        print(f'{reason}: {len(links)}个')
    print()
    
    # 输出详细列表
    print('=' * 80)
    print('无效链接详细列表')
    print('=' * 80)
    print()
    
    for i, link in enumerate(invalid_links, 1):
        print(f'{i}. INDEX文件: {link["index_file"]}')
        print(f'   链接文本: {link["text"]}')
        print(f'   链接URL: {link["url"]}')
        print(f'   目标路径: {link["target_path"]}')
        print(f'   原因: {link["reason"]}')
        print()
    
    # 输出修复建议
    print('=' * 80)
    print('修复建议')
    print('=' * 80)
    print()
    
    for reason, links in sorted(reason_groups.items(), key=lambda x: len(x[1]), reverse=True):
        print(f'### {reason} ({len(links)}个)')
        print()
        
        # 按INDEX文件分组
        index_groups = defaultdict(list)
        for link in links:
            index_groups[link['index_file']].append(link)
        
        for index_file, file_links in index_groups.items():
            print(f'在 {index_file} 中:')
            for link in file_links:
                print(f'  - 删除或更新链接: [{link["text"]}]({link["url"]})')
        print()

if __name__ == '__main__':
    invalid_links = analyze_invalid_links()
    generate_report(invalid_links)
