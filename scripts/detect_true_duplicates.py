# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
真正的职责重叠检测脚本
用途：基于module_id、标题和核心功能检测真正的重复文档
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import difflib

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")


def read_document(filepath: Path) -> str:
    """读取文档内容"""
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""


def extract_yaml_header(content: str) -> dict:
    """提取YAML头部"""
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not yaml_match:
        return {}
    
    yaml_content = yaml_match.group(1)
    yaml_dict = {}
    
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            yaml_dict[key.strip()] = value.strip().strip('"\'')
    
    return yaml_dict


def extract_title(content: str) -> str:
    """提取文档标题"""
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_core_functions(content: str) -> List[str]:
    """提取核心功能列表"""
    functions = []
    
    # 查找核心功能章节
    patterns = [
        r'##\s*核心功能\s*\n(.*?)(?=\n##|\Z)',
        r'##\s*核心职责\s*\n(.*?)(?=\n##|\Z)',
        r'##\s*主要功能\s*\n(.*?)(?=\n##|\Z)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section = match.group(1)
            # 提取列表项
            items = re.findall(r'^\s*[-*]\s*(.+?)$', section, re.MULTILINE)
            functions.extend(items)
            break
    
    return functions


def extract_keywords_from_title(title: str) -> Set[str]:
    """从标题提取关键词"""
    # 移除常见词
    stop_words = {'BLUEPRINT', '蓝图', '系统', '模块', '框架', '架构', '集成', '优化', '管理'}
    
    # 分割标题
    words = re.split(r'[\s_\-]+', title.upper())
    
    # 过滤关键词
    keywords = set()
    for word in words:
        if word and word not in stop_words and len(word) > 2:
            keywords.add(word)
    
    return keywords


def calculate_similarity(title1: str, title2: str) -> float:
    """计算标题相似度"""
    return difflib.SequenceMatcher(None, title1.upper(), title2.upper()).ratio()


def detect_true_duplicates():
    """检测真正的重复文档"""
    print("="*80)
    print("真正的职责重叠检测")
    print("="*80)
    print("\n检测方法:")
    print("  1. 标题相似度分析")
    print("  2. 核心功能重叠分析")
    print("  3. module_id冲突检测")
    print()
    
    documents = []
    
    # 收集所有文档信息
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        content = read_document(filepath)
        yaml_header = extract_yaml_header(content)
        title = extract_title(content)
        core_functions = extract_core_functions(content)
        
        documents.append({
            "filename": filepath.name,
            "title": title,
            "module_id": yaml_header.get('module_id', ''),
            "layer": yaml_header.get('layer', 'Unknown'),
            "core_functions": core_functions,
            "keywords": extract_keywords_from_title(title)
        })
    
    # 检测方法1: 标题相似度
    print("="*80)
    print("检测方法1: 标题相似度分析")
    print("="*80)
    
    title_duplicates = []
    for i, doc1 in enumerate(documents):
        for doc2 in documents[i+1:]:
            similarity = calculate_similarity(doc1['title'], doc2['title'])
            if similarity > 0.8:  # 80%相似度阈值
                title_duplicates.append({
                    "doc1": doc1['filename'],
                    "doc2": doc2['filename'],
                    "title1": doc1['title'],
                    "title2": doc2['title'],
                    "similarity": similarity
                })
    
    if title_duplicates:
        print(f"\n🔴 发现 {len(title_duplicates)} 组标题高度相似的文档:\n")
        for dup in title_duplicates:
            print(f"  相似度: {dup['similarity']:.1%}")
            print(f"    文档1: {dup['doc1']}")
            print(f"      标题: {dup['title1']}")
            print(f"    文档2: {dup['doc2']}")
            print(f"      标题: {dup['title2']}")
            print()
    else:
        print("\n✅ 未发现标题高度相似的文档")
    
    # 检测方法2: 核心功能重叠
    print("\n" + "="*80)
    print("检测方法2: 核心功能重叠分析")
    print("="*80)
    
    function_duplicates = []
    for i, doc1 in enumerate(documents):
        if not doc1['core_functions']:
            continue
        for doc2 in documents[i+1:]:
            if not doc2['core_functions']:
                continue
            
            # 计算核心功能重叠度
            funcs1 = set(doc1['core_functions'])
            funcs2 = set(doc2['core_functions'])
            
            if funcs1 and funcs2:
                overlap = funcs1 & funcs2
                if len(overlap) >= 3:  # 至少3个核心功能相同
                    function_duplicates.append({
                        "doc1": doc1['filename'],
                        "doc2": doc2['filename'],
                        "overlap_count": len(overlap),
                        "overlap_functions": list(overlap)[:5]
                    })
    
    if function_duplicates:
        print(f"\n🔴 发现 {len(function_duplicates)} 组核心功能重叠的文档:\n")
        for dup in function_duplicates:
            print(f"  重叠功能数: {dup['overlap_count']}")
            print(f"    文档1: {dup['doc1']}")
            print(f"    文档2: {dup['doc2']}")
            print(f"    重叠功能:")
            for func in dup['overlap_functions']:
                print(f"      - {func}")
            print()
    else:
        print("\n✅ 未发现核心功能重叠的文档")
    
    # 检测方法3: module_id冲突
    print("\n" + "="*80)
    print("检测方法3: module_id冲突检测")
    print("="*80)
    
    module_id_map = defaultdict(list)
    for doc in documents:
        if doc['module_id']:
            module_id_map[doc['module_id']].append(doc['filename'])
    
    module_id_conflicts = {k: v for k, v in module_id_map.items() if len(v) > 1}
    
    if module_id_conflicts:
        print(f"\n🔴 发现 {len(module_id_conflicts)} 个重复的module_id:\n")
        for module_id, files in module_id_conflicts.items():
            print(f"  module_id: {module_id}")
            for f in files:
                print(f"    - {f}")
            print()
    else:
        print("\n✅ 未发现module_id冲突")
    
    # 检测方法4: 关键词重叠（同一Layer内）
    print("\n" + "="*80)
    print("检测方法4: 同Layer内关键词重叠分析")
    print("="*80)
    
    layer_docs = defaultdict(list)
    for doc in documents:
        layer = doc['layer']
        if layer != 'Unknown':
            layer_docs[layer].append(doc)
    
    keyword_duplicates = []
    for layer, docs in layer_docs.items():
        if len(docs) < 2:
            continue
        
        for i, doc1 in enumerate(docs):
            for doc2 in docs[i+1:]:
                # 计算关键词重叠度
                keywords1 = doc1['keywords']
                keywords2 = doc2['keywords']
                
                if keywords1 and keywords2:
                    overlap = keywords1 & keywords2
                    if len(overlap) >= 2:  # 至少2个关键词相同
                        keyword_duplicates.append({
                            "layer": layer,
                            "doc1": doc1['filename'],
                            "doc2": doc2['filename'],
                            "overlap_keywords": list(overlap)
                        })
    
    if keyword_duplicates:
        print(f"\n⚠️ 发现 {len(keyword_duplicates)} 组同Layer内关键词重叠的文档:\n")
        for dup in keyword_duplicates[:10]:  # 只显示前10组
            print(f"  Layer: {dup['layer']}")
            print(f"    文档1: {dup['doc1']}")
            print(f"    文档2: {dup['doc2']}")
            print(f"    重叠关键词: {', '.join(dup['overlap_keywords'])}")
            print()
        if len(keyword_duplicates) > 10:
            print(f"  ... 还有 {len(keyword_duplicates) - 10} 组")
    else:
        print("\n✅ 未发现同Layer内关键词重叠")
    
    # 总结
    print("\n" + "="*80)
    print("总结")
    print("="*80)
    
    total_issues = len(title_duplicates) + len(function_duplicates) + len(module_id_conflicts)
    
    print(f"\n检测结果:")
    print(f"  标题相似重复: {len(title_duplicates)} 组")
    print(f"  核心功能重叠: {len(function_duplicates)} 组")
    print(f"  module_id冲突: {len(module_id_conflicts)} 个")
    print(f"  关键词重叠: {len(keyword_duplicates)} 组")
    
    if total_issues > 0:
        print(f"\n🔴 总计发现 {total_issues} 个真正的职责重叠问题")
        print("\n建议:")
        if title_duplicates:
            print("  1. 合并标题高度相似的文档")
        if function_duplicates:
            print("  2. 合并核心功能重叠的文档")
        if module_id_conflicts:
            print("  3. 修复重复的module_id")
    else:
        print("\n✅ 未发现真正的职责重叠问题")
        print("\n说明:")
        print("  之前的'职责重叠'检测基于applicable_scope字段，")
        print("  该字段描述的是适用范围而非具体职责。")
        print("  实际上这些文档职责不同，只是适用范围相同。")
    
    return {
        "title_duplicates": title_duplicates,
        "function_duplicates": function_duplicates,
        "module_id_conflicts": module_id_conflicts,
        "keyword_duplicates": keyword_duplicates
    }


if __name__ == "__main__":
    results = detect_true_duplicates()
