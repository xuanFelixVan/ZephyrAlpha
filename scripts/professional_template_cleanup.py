#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专业蓝图文件治理 - 空模板文件清理
"""

import re
import hashlib
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def get_file_hash(file_path):
    """计算文件内容哈希"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        return hashlib.md5(content.encode()).hexdigest()
    except:
        return None

def analyze_file_content(file_path):
    """分析文件内容，判断是否为空模板"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 移除YAML头部
        content_no_yaml = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        
        # 移除变更记录表格
        content_no_yaml = re.sub(r'## 变更记录.*$', '', content_no_yaml, flags=re.DOTALL)
        content_no_yaml = re.sub(r'## 更新记录.*$', '', content_no_yaml, flags=re.DOTALL)
        
        # 移除表格
        content_no_yaml = re.sub(r'\|.*\|', '', content_no_yaml)
        
        # 移除空白行和特殊字符
        content_clean = re.sub(r'[\s\-\|]+', '', content_no_yaml)
        
        # 计算实际内容长度
        content_length = len(content_clean)
        
        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else None
        
        # 判断是否有实际内容
        has_real_content = content_length > 50
        
        return {
            'content_length': content_length,
            'title': title,
            'has_real_content': has_real_content,
            'full_content': content
        }
    
    except Exception as e:
        return {
            'content_length': 0,
            'title': None,
            'has_real_content': False,
            'error': str(e)
        }

def find_duplicate_content():
    """查找内容完全相同的文件"""
    print("=" * 80)
    print("查找内容完全相同的文件")
    print("=" * 80)
    
    hash_map = {}
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        file_hash = get_file_hash(file_path)
        if file_hash:
            if file_hash not in hash_map:
                hash_map[file_hash] = []
            hash_map[file_hash].append(file_path)
    
    # 找出重复的
    duplicates = {k: v for k, v in hash_map.items() if len(v) > 1}
    
    print(f"\n发现重复文件组: {len(duplicates)}组")
    
    for hash_val, files in duplicates.items():
        print(f"\n哈希: {hash_val}")
        for f in files:
            print(f"  - {f.relative_to(FACTOR_LIBRARY)}")
    
    return duplicates

def analyze_empty_templates():
    """分析空模板文件"""
    print("\n" + "=" * 80)
    print("分析空模板文件")
    print("=" * 80)
    
    empty_templates = []
    has_content_files = []
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        analysis = analyze_file_content(file_path)
        
        rel_path = file_path.relative_to(FACTOR_LIBRARY)
        
        if analysis.get('error'):
            print(f"\n错误: {rel_path}")
            print(f"  {analysis['error']}")
            continue
        
        if not analysis['has_real_content']:
            empty_templates.append({
                'path': file_path,
                'rel_path': str(rel_path),
                'content_length': analysis['content_length'],
                'title': analysis['title']
            })
        else:
            has_content_files.append({
                'path': file_path,
                'rel_path': str(rel_path),
                'content_length': analysis['content_length'],
                'title': analysis['title']
            })
    
    print(f"\n空模板文件: {len(empty_templates)}个")
    print(f"有内容文件: {len(has_content_files)}个")
    
    return empty_templates, has_content_files

def check_valuable_content(empty_templates):
    """检查空模板中是否有有价值的内容"""
    print("\n" + "=" * 80)
    print("检查空模板中是否有有价值的内容")
    print("=" * 80)
    
    valuable_files = []
    safe_to_delete = []
    
    for template in empty_templates:
        try:
            with open(template['path'], 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否有有价值的关键词
            valuable_keywords = [
                'API', '接口', '配置', '参数', '示例', '代码',
                '实现', '设计', '架构', '流程', '步骤', '方法',
                '公式', '算法', '模型', '策略', '因子', '数据'
            ]
            
            has_valuable = False
            for keyword in valuable_keywords:
                if keyword in content and len(content) > 200:
                    has_valuable = True
                    break
            
            if has_valuable:
                valuable_files.append(template)
            else:
                safe_to_delete.append(template)
        
        except:
            safe_to_delete.append(template)
    
    print(f"\n有价值的文件: {len(valuable_files)}个")
    print(f"可安全删除: {len(safe_to_delete)}个")
    
    if valuable_files:
        print("\n有价值的文件列表:")
        for f in valuable_files[:10]:  # 只显示前10个
            print(f"  - {f['rel_path']}")
    
    return valuable_files, safe_to_delete

def delete_empty_templates(safe_to_delete):
    """删除空模板文件"""
    print("\n" + "=" * 80)
    print("删除空模板文件")
    print("=" * 80)
    
    deleted_count = 0
    
    for template in safe_to_delete:
        try:
            template['path'].unlink()
            print(f"\n删除: {template['rel_path']}")
            deleted_count += 1
        except Exception as e:
            print(f"\n删除失败: {template['rel_path']}")
            print(f"  错误: {e}")
    
    print(f"\n删除文件: {deleted_count}")
    return deleted_count

def main():
    """主函数"""
    print("=" * 80)
    print("专业蓝图文件治理 - 空模板文件清理")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 查找重复内容
    duplicates = find_duplicate_content()
    
    # 2. 分析空模板文件
    empty_templates, has_content_files = analyze_empty_templates()
    
    # 3. 检查有价值内容
    valuable_files, safe_to_delete = check_valuable_content(empty_templates)
    
    # 4. 删除空模板
    deleted_count = delete_empty_templates(safe_to_delete)
    
    print("\n" + "=" * 80)
    print("清理完成")
    print("=" * 80)
    print(f"重复文件组: {len(duplicates)}")
    print(f"空模板文件: {len(empty_templates)}")
    print(f"有内容文件: {len(has_content_files)}")
    print(f"有价值文件: {len(valuable_files)}")
    print(f"删除文件: {deleted_count}")

if __name__ == '__main__':
    main()
