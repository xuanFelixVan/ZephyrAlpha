"""
职责重叠详细分析脚本
用途：详细分析职责重叠的文档组合
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

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


def extract_responsibility(content: str) -> str:
    """提取职责描述"""
    patterns = [
        r'职责[：:]\s*(.+?)(?:\n|$)',
        r'responsibility[：:]\s*(.+?)(?:\n|$)',
        r'本文档职责[：:]\s*(.+?)(?:\n|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return ""


def extract_module_summary(content: str) -> str:
    """提取模块摘要"""
    # 提取第一个标题后的第一段
    lines = content.split('\n')
    summary_lines = []
    in_summary = False
    
    for i, line in enumerate(lines):
        if line.startswith('# ') and i > 0:
            in_summary = True
            continue
        if in_summary:
            if line.startswith('##'):
                break
            if line.strip() and not line.startswith('>'):
                summary_lines.append(line.strip())
    
    return ' '.join(summary_lines[:3])  # 只取前3行


def analyze_responsibility_overlap():
    """分析职责重叠"""
    print("="*80)
    print("职责重叠详细分析")
    print("="*80)
    
    # 构建职责映射
    responsibility_map = defaultdict(list)
    documents_info = {}
    
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        content = read_document(filepath)
        yaml_header = extract_yaml_header(content)
        responsibility = yaml_header.get('applicable_scope', '') or extract_responsibility(content)
        summary = extract_module_summary(content)
        
        if responsibility:
            responsibility_map[responsibility].append(filepath.name)
        
        documents_info[filepath.name] = {
            "yaml": yaml_header,
            "responsibility": responsibility,
            "summary": summary[:200],  # 限制长度
            "layer": yaml_header.get('layer', 'Unknown')
        }
    
    # 找出重叠组
    overlap_groups = {k: v for k, v in responsibility_map.items() if len(v) > 1}
    
    print(f"\n发现 {len(overlap_groups)} 组职责重叠\n")
    
    for i, (responsibility, files) in enumerate(overlap_groups.items(), 1):
        print("="*80)
        print(f"重叠组 #{i}")
        print("="*80)
        print(f"\n职责描述: {responsibility}")
        print(f"涉及文档数: {len(files)}")
        print("\n涉及文档:")
        
        for j, filename in enumerate(files, 1):
            info = documents_info.get(filename, {})
            print(f"\n  {j}. {filename}")
            print(f"     Layer: {info.get('layer', 'Unknown')}")
            print(f"     摘要: {info.get('summary', 'N/A')[:100]}...")
            
            # 读取更多细节
            filepath = BLUEPRINTS_DIR / filename
            content = read_document(filepath)
            
            # 提取核心功能
            core_functions = []
            if '核心功能' in content or '核心职责' in content:
                lines = content.split('\n')
                for k, line in enumerate(lines):
                    if '核心功能' in line or '核心职责' in line:
                        # 提取接下来的几行
                        for m in range(k+1, min(k+6, len(lines))):
                            if lines[m].strip().startswith('-'):
                                core_functions.append(lines[m].strip())
            
            if core_functions:
                print(f"     核心功能:")
                for func in core_functions[:5]:
                    print(f"       {func}")
        
        print("\n" + "-"*80)
        print("分析建议:")
        
        # 分析是否真正重复
        layers = [documents_info[f].get('layer', '') for f in files]
        unique_layers = set(layers)
        
        if len(unique_layers) == 1:
            print("  🔴 高风险: 所有文档属于同一Layer，可能存在真正重复")
            print("  建议: 合并文档或明确划分职责边界")
        else:
            print("  ⚠️ 中风险: 文档属于不同Layer，可能是跨层协作")
            print("  建议: 明确各文档在不同Layer中的职责定位")
        
        print("="*80 + "\n")
    
    return overlap_groups


if __name__ == "__main__":
    overlap_groups = analyze_responsibility_overlap()
    
    print("\n" + "="*80)
    print("总结")
    print("="*80)
    print(f"\n总重叠组数: {len(overlap_groups)}")
    print(f"总涉及文档数: {sum(len(v) for v in overlap_groups.values())}")
    print("\n建议优先处理:")
    for responsibility, files in list(overlap_groups.items())[:3]:
        print(f"  - {responsibility}: {len(files)}个文档")
