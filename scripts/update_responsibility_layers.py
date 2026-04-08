"""
职责标注更新脚本
用途：批量更新文档职责标注，解决职责重叠问题
创建时间：2026-04-07
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path("D:/ZephyrAlpha")

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

def load_governance_report() -> Dict:
    report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE/governance_check_report_final_round7_v2.json"
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

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

def add_responsibility_layer_to_yaml(yaml_header: str, responsibility: str, layer: str) -> str:
    lines = yaml_header.split('\n')
    new_lines = []
    responsibility_added = False
    
    for line in lines:
        new_lines.append(line)
        if line.startswith('responsibility:') and not responsibility_added:
            new_lines.append(f"  responsibility_layer: {layer}")
            responsibility_added = True
    
    if not responsibility_added:
        new_lines.append(f"responsibility: {responsibility}")
        new_lines.append(f"  responsibility_layer: {layer}")
    
    return '\n'.join(new_lines)

def update_file_responsibility(file_path: str, responsibility: str) -> bool:
    full_path = PROJECT_ROOT / file_path
    if not full_path.exists():
        return False
    
    content, encoding = read_file_content(full_path)
    if content is None:
        return False
    
    layer = infer_responsibility_layer(file_path, responsibility)
    
    yaml_header, body = extract_yaml_header(content)
    
    if yaml_header:
        new_yaml = add_responsibility_layer_to_yaml(yaml_header, responsibility, layer)
        new_content = f"---\n{new_yaml}\n---{body}"
    else:
        new_yaml = f"""module_id: {full_path.stem.upper()}_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility: {responsibility}
responsibility_layer: {layer}
"""
        new_content = f"---\n{new_yaml}\n---\n{content}"
    
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    print("=" * 80)
    print("职责标注更新脚本")
    print("=" * 80)
    
    print("\n加载治理报告...")
    report = load_governance_report()
    
    overlap_issues = report.get('issues', {}).get('responsibility_overlap', [])
    
    print(f"\n发现 {len(overlap_issues)} 个职责重叠问题")
    
    total_files = 0
    updated_files = 0
    
    for issue in overlap_issues:
        responsibility = issue['responsibility']
        files = issue['files']
        count = issue['count']
        
        print(f"\n处理职责: {responsibility} ({count}个文件)")
        print("-" * 80)
        
        for file_path in files:
            total_files += 1
            if update_file_responsibility(file_path, responsibility):
                updated_files += 1
                if updated_files % 50 == 0:
                    print(f"  已更新 {updated_files}/{total_files} 个文件...")
    
    print("\n" + "=" * 80)
    print("更新完成")
    print("=" * 80)
    print(f"总文件数: {total_files}")
    print(f"成功更新: {updated_files}")
    print(f"失败数量: {total_files - updated_files}")
    print(f"成功率: {updated_files/total_files*100:.1f}%")

if __name__ == "__main__":
    main()
