"""
完善索引脚本
用途：自动生成完整的INDEX.md
创建时间：2026-04-07
"""

import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime

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
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1) if match else ""


def get_layer_number(layer_str: str) -> int:
    """获取Layer编号"""
    if not layer_str:
        return 99
    
    match = re.search(r'Layer\s*(\d+)', layer_str, re.IGNORECASE)
    return int(match.group(1)) if match else 99


def generate_index():
    """生成完整的INDEX.md"""
    print("="*80)
    print("生成完整索引")
    print("="*80)
    
    # 收集所有文档信息
    documents = []
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        content = read_document(filepath)
        if not content:
            continue
        
        yaml_header = extract_yaml_header(content)
        title = extract_title(content)
        
        doc_info = {
            "filename": filepath.name,
            "title": title or filepath.stem,
            "module_id": yaml_header.get('module_id', 'UNKNOWN_001'),
            "version": yaml_header.get('version', 'v1.0.0'),
            "status": yaml_header.get('status', 'Active'),
            "layer": yaml_header.get('layer', 'Unknown'),
            "layer_num": get_layer_number(yaml_header.get('layer', '')),
            "created_date": yaml_header.get('created_date', '2026-04-07'),
        }
        
        documents.append(doc_info)
    
    # 按Layer分组
    layer_groups = {}
    for doc in documents:
        layer_num = doc['layer_num']
        if layer_num not in layer_groups:
            layer_groups[layer_num] = []
        layer_groups[layer_num].append(doc)
    
    # 生成索引内容
    index_content = []
    index_content.append("---")
    index_content.append("module_id: IMPL_蓝图文档总索引_001")
    index_content.append("version: 1.0.0")
    index_content.append("status: Active")
    index_content.append("created_date: 2026-04-07")
    index_content.append("last_updated: 2026-04-07")
    index_content.append("owner: 实施团队")
    index_content.append("standard_type: 专业量化机构蓝图")
    index_content.append("applicable_scope: 全系统")
    index_content.append("compliance_level: 专业标准")
    index_content.append("---")
    index_content.append("")
    index_content.append("# 蓝图文档总索引")
    index_content.append("")
    index_content.append("**版本**: v1.0.0 | **更新日期**: 2026-04-07 | **状态**: Active")
    index_content.append("")
    index_content.append("---")
    index_content.append("")
    index_content.append("## 📋 概述")
    index_content.append("")
    index_content.append("本文档是组合优化层蓝图文档的总索引，提供所有蓝图文档的快速导航。")
    index_content.append("")
    index_content.append("---")
    index_content.append("")
    index_content.append("## 📊 文档统计")
    index_content.append("")
    index_content.append(f"- **总文档数**: {len(documents)}")
    index_content.append(f"- **Active文档**: {len([d for d in documents if d['status'] == 'Active'])}")
    index_content.append(f"- **更新日期**: 2026-04-07")
    index_content.append("")
    index_content.append("---")
    index_content.append("")
    
    # 按Layer生成索引
    for layer_num in sorted(layer_groups.keys()):
        layer_docs = layer_groups[layer_num]
        
        if layer_num == 99:
            layer_name = "未分类文档"
        else:
            layer_names = {
                1: "数据源层",
                2: "Alpha因子层",
                3: "策略层",
                4: "机器学习层",
                5: "回测层",
                6: "组合优化层",
                7: "风险管理层",
                8: "执行层",
                9: "监控层",
            }
            layer_name = layer_names.get(layer_num, f"Layer {layer_num}")
        
        index_content.append(f"## {layer_num}. Layer {layer_num} ({layer_name})")
        index_content.append("")
        index_content.append(f"**文档数**: {len(layer_docs)}")
        index_content.append("")
        index_content.append("| 文档名称 | module_id | 版本 | 状态 | 最后更新 | 文档路径 |")
        index_content.append("|----------|-----------|------|------|----------|----------|")
        
        for doc in sorted(layer_docs, key=lambda x: x['filename']):
            index_content.append(
                f"| {doc['title']} | {doc['module_id']} | {doc['version']} | {doc['status']} | {doc['created_date']} | [链接](./{doc['filename']}) |"
            )
        
        index_content.append("")
    
    # 添加文档治理章节
    index_content.append("---")
    index_content.append("")
    index_content.append("## 文档治理")
    index_content.append("")
    index_content.append("### 文档索引")
    index_content.append("")
    index_content.append("**本文档在系统中的位置**:")
    index_content.append("- **所属层级**: 系统索引")
    index_content.append("- **模块索引**: IMPL_蓝图文档总索引_001")
    index_content.append("- **文档路径**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/INDEX.md")
    index_content.append("")
    index_content.append("### 版本管理")
    index_content.append("")
    index_content.append("**版本历史**:")
    index_content.append("- v1.0.0 (2026-04-07): 初始版本，自动生成完整索引")
    index_content.append("")
    index_content.append("### 维护责任")
    index_content.append("")
    index_content.append("**文档维护**:")
    index_content.append("- **责任模块**: 实施团队")
    index_content.append("- **维护周期**: 每周审查")
    index_content.append("- **变更流程**: 提交变更申请 → 技术评审 → 更新文档")
    index_content.append("")
    index_content.append("---")
    index_content.append("")
    index_content.append("**版本**: v1.0.0 | **创建日期**: 2026-04-07 | **状态**: Active")
    
    # 保存索引文件
    index_path = BLUEPRINTS_DIR / "INDEX.md"
    with open(index_path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(index_content))
    
    print(f"\n✅ 索引生成完成")
    print(f"  总文档数: {len(documents)}")
    print(f"  Layer分组: {len(layer_groups)}")
    print(f"  索引路径: {index_path}")
    
    return len(documents)


if __name__ == "__main__":
    generate_index()
