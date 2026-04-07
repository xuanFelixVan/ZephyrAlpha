#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化职责描述检测工具
用途: 检测文档职责描述问题，生成优化建议
版本: v1.0.0
创建日期: 2026-04-07
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

DOCS_DIR = Path("D:/ZephyrAlpha/docs")

RESPONSIBILITY_KEYWORDS = {
    "管理": ["管理", "维护", "配置", "组织", "协调"],
    "实现": ["实现", "开发", "构建", "创建", "编写"],
    "监控": ["监控", "检测", "跟踪", "追踪", "观察"],
    "优化": ["优化", "改进", "提升", "增强", "完善"],
    "分析": ["分析", "评估", "研究", "调查", "诊断"],
    "设计": ["设计", "规划", "定义", "制定", "架构"]
}

DIRECTORY_RESPONSIBILITY_MAP = {
    "00_OVERVIEW": "系统概览与架构总览，提供全局视角和导航入口",
    "00_RESOURCES": "资源管理与平台文档，管理外部资源和平台集成",
    "01_FRAMEWORK": "系统框架与架构设计，定义系统整体架构和模块边界",
    "02_FACTOR_LIBRARY": "因子库管理与计算，管理因子定义、计算和评估",
    "03_TRADING_TACTICS": "交易策略与战术，定义交易规则和执行策略",
    "04_EXECUTION": "交易执行与风控，执行交易指令和管理风险",
    "05_IMPLEMENTATION": "实施指南与部署文档，指导系统实施和部署",
    "06_ARCHIVE": "归档文档管理，管理历史版本和过时文档",
    "07_RESEARCH": "研究创新与实验，管理研究项目和实验记录",
    "08_KNOWLEDGE": "知识库与案例研究，管理知识资产和案例库",
    "09_AUDIT": "审计与合规检查，执行文档治理审计和合规验证",
    "10_AI_WORKFLOW": "AI工作流与自动化，管理AI辅助流程和自动化任务",
    "11_STRATEGIC_DECISION": "战略决策与市场状态，支持高层决策和市场分析"
}

def scan_all_files():
    """扫描所有文档文件"""
    all_files = []
    for ext in ['*.md']:
        all_files.extend(DOCS_DIR.rglob(ext))
    return [f for f in all_files if not any(part.startswith('.') for part in f.parts)]

def extract_responsibility(file_path):
    """提取文档职责描述"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            
            resp_match = re.search(r'responsibility:\s*\n?\s*-\s*(.+?)(?:\n|$)', yaml_content, re.MULTILINE)
            if resp_match:
                return resp_match.group(1).strip()
        
        return None
    except Exception as e:
        return None

def check_responsibility_length(responsibility):
    """检查职责描述长度"""
    if not responsibility:
        return {"status": "missing", "message": "缺少职责描述"}
    
    length = len(responsibility)
    if length < 50:
        return {"status": "too_short", "message": f"职责描述过短({length}字符)，建议扩展至50-200字符"}
    elif length > 200:
        return {"status": "too_long", "message": f"职责描述过长({length}字符)，建议精简至50-200字符"}
    else:
        return {"status": "ok", "message": f"职责描述长度符合标准({length}字符)"}

def check_responsibility_keywords(responsibility):
    """检查职责描述关键词"""
    if not responsibility:
        return {"status": "missing", "message": "缺少职责描述"}
    
    found_categories = []
    for category, keywords in RESPONSIBILITY_KEYWORDS.items():
        if any(kw in responsibility for kw in keywords):
            found_categories.append(category)
    
    if found_categories:
        return {"status": "ok", "message": f"包含行为动词: {', '.join(found_categories)}"}
    else:
        return {"status": "missing_keywords", "message": "职责描述缺少明确的行为动词"}

def suggest_responsibility(file_path, current_responsibility):
    """生成职责描述优化建议"""
    relative_path = file_path.relative_to(DOCS_DIR)
    path_parts = str(relative_path).split(os.sep)
    
    if path_parts and path_parts[0] in DIRECTORY_RESPONSIBILITY_MAP:
        base_dir = path_parts[0]
        standard_resp = DIRECTORY_RESPONSIBILITY_MAP[base_dir]
        
        file_name = file_path.stem
        file_keywords = file_name.replace('_', ' ').lower()
        
        if 'blueprint' in file_keywords:
            suggestion = f"{standard_resp}，定义{file_name.replace('_', ' ')}的详细设计和实施方案"
        elif 'report' in file_keywords:
            suggestion = f"{standard_resp}，记录{file_name.replace('_', ' ')}的分析结果和改进建议"
        elif 'index' in file_keywords.lower():
            suggestion = f"目录导航与文档索引，提供{base_dir}目录的文档清单和导航"
        else:
            suggestion = standard_resp
        
        return suggestion
    
    return current_responsibility

def detect_responsibility_issues(all_files):
    """检测职责描述问题"""
    issues = {
        "missing_responsibility": [],
        "too_short": [],
        "too_long": [],
        "missing_keywords": [],
        "overlapping": defaultdict(list)
    }
    
    responsibility_map = defaultdict(list)
    
    for file_path in all_files:
        relative_path = str(file_path.relative_to(DOCS_DIR))
        responsibility = extract_responsibility(file_path)
        
        if not responsibility:
            issues["missing_responsibility"].append({
                "path": relative_path,
                "suggestion": suggest_responsibility(file_path, None)
            })
            continue
        
        responsibility_map[responsibility].append(relative_path)
        
        length_check = check_responsibility_length(responsibility)
        if length_check["status"] == "too_short":
            issues["too_short"].append({
                "path": relative_path,
                "responsibility": responsibility,
                "length": len(responsibility),
                "suggestion": suggest_responsibility(file_path, responsibility)
            })
        elif length_check["status"] == "too_long":
            issues["too_long"].append({
                "path": relative_path,
                "responsibility": responsibility,
                "length": len(responsibility)
            })
        
        keyword_check = check_responsibility_keywords(responsibility)
        if keyword_check["status"] == "missing_keywords":
            issues["missing_keywords"].append({
                "path": relative_path,
                "responsibility": responsibility,
                "suggestion": suggest_responsibility(file_path, responsibility)
            })
    
    for resp, files in responsibility_map.items():
        if len(files) > 3:
            issues["overlapping"][resp] = files
    
    return issues

def generate_report(issues, output_path):
    """生成检测报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_issues": sum(len(v) if isinstance(v, list) else len(v) for v in issues.values()),
            "missing_responsibility": len(issues["missing_responsibility"]),
            "too_short": len(issues["too_short"]),
            "too_long": len(issues["too_long"]),
            "missing_keywords": len(issues["missing_keywords"]),
            "overlapping_groups": len(issues["overlapping"])
        },
        "issues": {
            "missing_responsibility": issues["missing_responsibility"][:10],
            "too_short": issues["too_short"][:10],
            "too_long": issues["too_long"][:10],
            "missing_keywords": issues["missing_keywords"][:10],
            "overlapping": {k: v[:5] for k, v in list(issues["overlapping"].items())[:5]}
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report

def print_summary(issues):
    """打印检测摘要"""
    print("\n" + "=" * 80)
    print("职责描述检测摘要")
    print("=" * 80)
    
    print(f"\n缺少职责描述: {len(issues['missing_responsibility'])}个")
    for item in issues['missing_responsibility'][:5]:
        print(f"  - {item['path']}")
    
    print(f"\n职责描述过短: {len(issues['too_short'])}个")
    for item in issues['too_short'][:5]:
        print(f"  - {item['path']}: {item['responsibility']} ({item['length']}字符)")
    
    print(f"\n职责描述过长: {len(issues['too_long'])}个")
    for item in issues['too_long'][:5]:
        print(f"  - {item['path']}: {item['responsibility'][:50]}... ({item['length']}字符)")
    
    print(f"\n缺少行为动词: {len(issues['missing_keywords'])}个")
    for item in issues['missing_keywords'][:5]:
        print(f"  - {item['path']}: {item['responsibility']}")
    
    print(f"\n职责重叠: {len(issues['overlapping'])}组")
    for resp, files in list(issues['overlapping'].items())[:5]:
        print(f"  - '{resp}'出现在{len(files)}个文件")

def main():
    print("=" * 80)
    print("自动化职责描述检测工具")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    print("\n扫描所有文档...")
    all_files = scan_all_files()
    print(f"发现 {len(all_files)} 个文档文件")
    
    print("\n检测职责描述问题...")
    issues = detect_responsibility_issues(all_files)
    
    print_summary(issues)
    
    output_path = DOCS_DIR / "09_AUDIT" / "STATE" / f"responsibility_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = generate_report(issues, output_path)
    
    print(f"\n检测报告已保存至: {output_path}")
    
    print("\n" + "=" * 80)
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()
