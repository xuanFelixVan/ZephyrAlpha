#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 11职责重叠深度分析工具
用途：深度分析文档职责重叠问题
版本：v1.0
创建日期：2026-04-06
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

LAYER11_DIR = Path("docs/11_STRATEGIC_DECISION")


def extract_responsibility(content: str) -> str:
    """提取文档职责描述"""
    patterns = [
        r'##\s*文档职责说明\s*\n(.*?)(?=\n##|\Z)',
        r'\*\*本文档职责\*\*:\s*(.*?)(?=\n\n|\n##|\Z)',
        r'##\s*职责说明\s*\n(.*?)(?=\n##|\Z)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    return ""


def extract_core_content(content: str) -> Set[str]:
    """提取核心内容关键词"""
    keywords = set()
    
    patterns = [
        r'##\s*一、(.*?)(?=\n##|\Z)',
        r'##\s*二、(.*?)(?=\n##|\Z)',
        r'##\s*三、(.*?)(?=\n##|\Z)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section = match.group(1)
            words = re.findall(r'[\u4e00-\u9fa5]{2,8}', section)
            keywords.update(words)
    
    return keywords


def extract_module_id(content: str) -> str:
    """提取module_id"""
    match = re.search(r'module_id:\s*(\S+)', content)
    return match.group(1) if match else ""


def extract_applicable_scope(content: str) -> str:
    """提取适用范围"""
    match = re.search(r'applicable_scope:\s*(.+)', content)
    return match.group(1).strip() if match else ""


def calculate_overlap(set1: Set[str], set2: Set[str]) -> float:
    """计算两个集合的重叠度"""
    if not set1 or not set2:
        return 0.0
    
    intersection = set1 & set2
    union = set1 | set2
    
    return len(intersection) / len(union) if union else 0.0


def analyze_document(file_path: Path) -> Dict:
    """分析单个文档"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'file_name': file_path.name,
            'module_id': extract_module_id(content),
            'applicable_scope': extract_applicable_scope(content),
            'responsibility': extract_responsibility(content),
            'core_keywords': extract_core_content(content),
        }
    except Exception as e:
        print(f"  ✗ 分析失败 {file_path.name}: {e}")
        return None


def check_responsibility_overlap(doc1: Dict, doc2: Dict) -> Dict:
    """检查两个文档的职责重叠"""
    overlap_result = {
        'file1': doc1['file_name'],
        'file2': doc2['file_name'],
        'scope_overlap': False,
        'responsibility_overlap': False,
        'keyword_overlap': 0.0,
        'overlap_score': 0.0,
        'issues': [],
    }
    
    if doc1['applicable_scope'] and doc2['applicable_scope']:
        scope1_words = set(doc1['applicable_scope'].split())
        scope2_words = set(doc2['applicable_scope'].split())
        
        if scope1_words & scope2_words:
            overlap_result['scope_overlap'] = True
            overlap_result['issues'].append(f"适用范围重叠: {doc1['applicable_scope']} vs {doc2['applicable_scope']}")
    
    if doc1['responsibility'] and doc2['responsibility']:
        resp1_words = set(re.findall(r'[\u4e00-\u9fa5]{2,}', doc1['responsibility']))
        resp2_words = set(re.findall(r'[\u4e00-\u9fa5]{2,}', doc2['responsibility']))
        
        resp_overlap = calculate_overlap(resp1_words, resp2_words)
        if resp_overlap > 0.3:
            overlap_result['responsibility_overlap'] = True
            overlap_result['issues'].append(f"职责描述重叠度: {resp_overlap:.2%}")
    
    keyword_overlap = calculate_overlap(doc1['core_keywords'], doc2['core_keywords'])
    overlap_result['keyword_overlap'] = keyword_overlap
    
    overlap_score = 0.0
    if overlap_result['scope_overlap']:
        overlap_score += 0.3
    if overlap_result['responsibility_overlap']:
        overlap_score += 0.4
    overlap_score += keyword_overlap * 0.3
    
    overlap_result['overlap_score'] = overlap_score
    
    return overlap_result


def main():
    """主函数"""
    print("=" * 80)
    print("Layer 11职责重叠深度分析工具")
    print("=" * 80)
    print()
    
    if not LAYER11_DIR.exists():
        print(f"✗ 目录不存在: {LAYER11_DIR}")
        return
    
    md_files = list(LAYER11_DIR.glob("*.md"))
    print(f"发现 {len(md_files)} 个Markdown文件")
    print()
    
    print("=" * 80)
    print("第一阶段：文档分析")
    print("=" * 80)
    print()
    
    documents = []
    for md_file in sorted(md_files):
        print(f"  分析: {md_file.name}")
        doc = analyze_document(md_file)
        if doc:
            documents.append(doc)
    
    print()
    print("=" * 80)
    print("第二阶段：职责重叠检查")
    print("=" * 80)
    print()
    
    overlap_results = []
    
    for i in range(len(documents)):
        for j in range(i + 1, len(documents)):
            overlap = check_responsibility_overlap(documents[i], documents[j])
            if overlap['overlap_score'] > 0.1:
                overlap_results.append(overlap)
    
    overlap_results.sort(key=lambda x: x['overlap_score'], reverse=True)
    
    print(f"发现 {len(overlap_results)} 对文档存在潜在职责重叠")
    print()
    
    print("=" * 80)
    print("高风险职责重叠（重叠度 > 0.3）")
    print("=" * 80)
    print()
    
    high_risk = [r for r in overlap_results if r['overlap_score'] > 0.3]
    for i, result in enumerate(high_risk[:20], 1):
        print(f"{i}. {result['file1']} <-> {result['file2']}")
        print(f"   重叠度: {result['overlap_score']:.2%}")
        for issue in result['issues']:
            print(f"   - {issue}")
        print()
    
    print("=" * 80)
    print("中风险职责重叠（重叠度 0.1-0.3）")
    print("=" * 80)
    print()
    
    medium_risk = [r for r in overlap_results if 0.1 < r['overlap_score'] <= 0.3]
    for i, result in enumerate(medium_risk[:20], 1):
        print(f"{i}. {result['file1']} <-> {result['file2']}")
        print(f"   重叠度: {result['overlap_score']:.2%}")
        print()
    
    print("=" * 80)
    print("职责重叠统计")
    print("=" * 80)
    print()
    print(f"高风险重叠: {len(high_risk)} 对")
    print(f"中风险重叠: {len(medium_risk)} 对")
    print(f"低风险重叠: {len(overlap_results) - len(high_risk) - len(medium_risk)} 对")
    print()
    
    print("=" * 80)
    print("建议整改措施")
    print("=" * 80)
    print()
    
    if high_risk:
        print("🔴 高风险问题需要立即整改:")
        for result in high_risk[:5]:
            print(f"  - {result['file1']} 和 {result['file2']} 存在职责重叠")
        print()
    
    print("✅ 分析完成")


if __name__ == "__main__":
    main()
