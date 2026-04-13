# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
INDEX.md索引完整性检查与修复脚本
用途：检查并补充INDEX.md中缺失的文档索引
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")
INDEX_FILE = BLUEPRINTS_DIR / "INDEX.md"


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


def get_all_blueprint_files() -> Set[str]:
    """获取所有蓝图文件"""
    files = set()
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name != "INDEX.md":
            files.add(filepath.name)
    return files


def get_indexed_files() -> Set[str]:
    """获取INDEX.md中已索引的文件"""
    content = read_document(INDEX_FILE)
    
    # 提取所有链接中的文件名
    pattern = r'\[链接\]\(\./([^\)]+\.md)\)'
    matches = re.findall(pattern, content)
    
    return set(matches)


def get_layer_from_yaml(layer_str: str) -> Tuple[int, str]:
    """从layer字段提取层级编号和名称"""
    if not layer_str:
        return (0, "Unknown")
    
    # 提取Layer编号
    match = re.search(r'Layer\s*(\d+)', layer_str, re.IGNORECASE)
    if match:
        layer_num = int(match.group(1))
        
        # 提取中文名称
        cn_match = re.search(r'Layer\s*\d+\s*\(([^)]+)\)', layer_str)
        layer_name = cn_match.group(1) if cn_match else layer_str
        
        return (layer_num, layer_name)
    
    return (0, layer_str)


def categorize_by_layer(documents: Dict) -> Dict[int, List[Dict]]:
    """按Layer分类文档"""
    layer_docs = defaultdict(list)
    
    for filename, info in documents.items():
        layer_num, layer_name = get_layer_from_yaml(info.get('layer', ''))
        layer_docs[layer_num].append({
            "filename": filename,
            "title": info.get('title', ''),
            "module_id": info.get('module_id', ''),
            "version": info.get('version', 'v1.0.0'),
            "layer_name": layer_name,
            "created_date": info.get('created_date', '2026-04-07')
        })
    
    return layer_docs


def generate_index_entry(doc: Dict) -> str:
    """生成索引条目"""
    return f"| {doc['title'].replace('蓝图', '')}蓝图 | {doc['module_id']} | {doc['version']} | Active | {doc['created_date']} | [链接](./{doc['filename']}) 🆕 |"


def check_and_fix_index():
    """检查并修复索引"""
    print("="*80)
    print("INDEX.md索引完整性检查")
    print("="*80)
    
    # 获取所有文件
    all_files = get_all_blueprint_files()
    indexed_files = get_indexed_files()
    
    # 找出缺失的文件
    missing_files = all_files - indexed_files
    
    print(f"\n总文件数: {len(all_files)}")
    print(f"已索引数: {len(indexed_files)}")
    print(f"缺失文件数: {len(missing_files)}")
    
    if not missing_files:
        print("\n✅ 索引完整，无缺失文件")
        return
    
    print(f"\n🔴 发现 {len(missing_files)} 个缺失文件:\n")
    
    # 收集缺失文件的信息
    missing_docs = {}
    for filename in sorted(missing_files):
        filepath = BLUEPRINTS_DIR / filename
        content = read_document(filepath)
        yaml_header = extract_yaml_header(content)
        title = extract_title(content)
        
        missing_docs[filename] = {
            "title": title.replace('蓝图', '').replace('v1.0', '').strip(),
            "module_id": yaml_header.get('module_id', 'UNKNOWN_001'),
            "version": yaml_header.get('version', 'v1.0.0'),
            "layer": yaml_header.get('layer', 'Unknown'),
            "created_date": yaml_header.get('created_date', '2026-04-07')
        }
        
        print(f"  - {filename}")
        print(f"    标题: {missing_docs[filename]['title']}")
        print(f"    Layer: {missing_docs[filename]['layer']}")
        print()
    
    # 按Layer分类
    layer_docs = categorize_by_layer(missing_docs)
    
    print("\n" + "="*80)
    print("按Layer分类的缺失文档")
    print("="*80)
    
    for layer_num in sorted(layer_docs.keys()):
        docs = layer_docs[layer_num]
        print(f"\n### Layer {layer_num} ({len(docs)}个文档)")
        print("\n| 文档名称 | module_id | 版本 | 状态 | 最后更新 | 文档路径 |")
        print("|----------|-----------|------|------|----------|----------|")
        for doc in docs:
            print(generate_index_entry(doc))
    
    # 生成修复建议
    print("\n" + "="*80)
    print("修复建议")
    print("="*80)
    print("\n将以上表格内容添加到INDEX.md的相应章节中。")
    
    return missing_docs, layer_docs


if __name__ == "__main__":
    results = check_and_fix_index()
