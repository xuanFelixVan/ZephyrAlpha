# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
完整职责标注更新脚本
用途：扫描所有文档，更新职责标注
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path("D:/ZephyrAlpha")

RESPONSIBILITY_KEYWORDS = {
    "风险预算": [
        "风险预算", "risk budget", "budgeting", "风险分配", "risk allocation",
        "风险限额", "risk limit", "风险权重", "risk weight"
    ],
    "市场状态识别": [
        "市场状态", "market regime", "regime detection", "市场识别",
        "market state", "状态检测", "regime identification"
    ],
    "数据质量": [
        "数据质量", "data quality", "质量监控", "quality monitoring",
        "数据校验", "data validation", "质量检测", "quality check"
    ]
}

RESPONSIBILITY_LAYERS = {
    "风险预算": {
        "primary_layer": "Layer 11",
        "layer_keywords": {
            "Layer 11": ["战略决策", "STRATEGIC_DECISION", "risk_budgeting", "风险预算"],
            "Layer 5": ["策略", "STRATEGY", "hierarchical", "分层"],
            "Layer 3": ["执行", "EXECUTION", "control", "控制", "trading"]
        }
    },
    "市场状态识别": {
        "primary_layer": "Layer 4",
        "layer_keywords": {
            "Layer 4": ["机器学习", "ML", "regime", "状态", "model"],
            "Layer 7": ["监控", "MONITOR", "real_time", "实时"],
            "Layer 9": ["分析", "ANALYTICS", "history", "历史"]
        }
    },
    "数据质量": {
        "primary_layer": "Layer 1",
        "layer_keywords": {
            "Layer 1": ["数据源", "DATA_SOURCE", "source", "采集"],
            "Layer 2": ["处理", "PROCESSING", "clean", "清洗"],
            "Layer 4": ["特征", "FEATURE", "engineer", "工程"],
            "Layer 10": ["治理", "GOVERNANCE", "compliance", "合规"]
        }
    }
}

def scan_all_markdown_files() -> List[Path]:
    docs_dir = PROJECT_ROOT / "docs"
    return list(docs_dir.rglob("*.md"))

def check_file_responsibility(content: str) -> List[str]:
    responsibilities = []
    content_lower = content.lower()
    
    for responsibility, keywords in RESPONSIBILITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                if responsibility not in responsibilities:
                    responsibilities.append(responsibility)
                break
    
    return responsibilities

def infer_responsibility_layer(file_path: str, responsibility: str) -> str:
    layer_config = RESPONSIBILITY_LAYERS.get(responsibility, {})
    primary_layer = layer_config.get("primary_layer", "Layer 1")
    layer_keywords = layer_config.get("layer_keywords", {})
    
    file_path_upper = file_path.upper()
    
    for layer, keywords in layer_keywords.items():
        for keyword in keywords:
            if keyword.upper() in file_path_upper:
                return layer
    
    return primary_layer

def read_file_content(file_path: Path) -> Tuple[str, str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 'utf-8'
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
            return content, 'gbk'
        except:
            return None, None

def has_yaml_header(content: str) -> bool:
    return content.strip().startswith('---')

def extract_yaml_header(content: str) -> Tuple[str, str]:
    if not has_yaml_header(content):
        return "", content
    
    parts = content.split('---', 2)
    if len(parts) >= 3:
        return parts[1].strip(), '---'.join(parts[2:])
    return "", content

def add_responsibility_to_yaml(yaml_header: str, responsibilities: List[Tuple[str, str]]) -> str:
    lines = yaml_header.split('\n')
    new_lines = []
    responsibility_added = False
    
    for line in lines:
        new_lines.append(line)
        if line.startswith('responsibility:') and not responsibility_added:
            for resp, layer in responsibilities:
                new_lines.append(f"  - {resp} ({layer})")
            responsibility_added = True
    
    if not responsibility_added:
        new_lines.append("responsibility:")
        for resp, layer in responsibilities:
            new_lines.append(f"  - {resp} ({layer})")
    
    return '\n'.join(new_lines)

def update_file_responsibility(file_path: Path, responsibilities: List[str]) -> bool:
    content, encoding = read_file_content(file_path)
    if content is None:
        return False
    
    resp_layers = [(resp, infer_responsibility_layer(str(file_path), resp)) for resp in responsibilities]
    
    yaml_header, body = extract_yaml_header(content)
    
    if yaml_header:
        new_yaml = add_responsibility_to_yaml(yaml_header, resp_layers)
        new_content = f"---\n{new_yaml}\n---{body}"
    else:
        resp_yaml = "\n".join([f"  - {resp} ({layer})" for resp, layer in resp_layers])
        new_yaml = f"""module_id: {file_path.stem.upper()}_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
{resp_yaml}
"""
        new_content = f"---\n{new_yaml}\n---\n{content}"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    print("=" * 80)
    print("完整职责标注更新脚本")
    print("=" * 80)
    
    print("\n扫描所有Markdown文件...")
    all_files = scan_all_markdown_files()
    print(f"找到 {len(all_files)} 个Markdown文件")
    
    print("\n分析文件职责...")
    files_with_responsibility = {}
    
    for i, file_path in enumerate(all_files, 1):
        if i % 100 == 0:
            print(f"  已扫描 {i}/{len(all_files)} 个文件...")
        
        content, _ = read_file_content(file_path)
        if content is None:
            continue
        
        responsibilities = check_file_responsibility(content)
        if responsibilities:
            files_with_responsibility[file_path] = responsibilities
    
    print(f"\n发现 {len(files_with_responsibility)} 个文件涉及职责重叠")
    
    print("\n更新文件职责标注...")
    updated_count = 0
    
    for i, (file_path, responsibilities) in enumerate(files_with_responsibility.items(), 1):
        if update_file_responsibility(file_path, responsibilities):
            updated_count += 1
            if updated_count % 50 == 0:
                print(f"  已更新 {updated_count}/{len(files_with_responsibility)} 个文件...")
    
    print("\n" + "=" * 80)
    print("更新完成")
    print("=" * 80)
    print(f"总文件数: {len(files_with_responsibility)}")
    print(f"成功更新: {updated_count}")
    print(f"失败数量: {len(files_with_responsibility) - updated_count}")
    print(f"成功率: {updated_count/len(files_with_responsibility)*100:.1f}%")
    
    print("\n职责分布:")
    resp_count = {}
    for responsibilities in files_with_responsibility.values():
        for resp in responsibilities:
            resp_count[resp] = resp_count.get(resp, 0) + 1
    
    for resp, count in sorted(resp_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {resp}: {count}个文件")

if __name__ == "__main__":
    main()
