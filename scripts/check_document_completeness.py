#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
文档内容完整性检查工具
用途：检查Layer 11文档内容的完整性
版本：v1.0
创建日期：2026-04-07
"""

import re
from pathlib import Path
from typing import Dict, List

LAYER11_DIR = Path("docs/11_STRATEGIC_DECISION")


REQUIRED_YAML_FIELDS = [
    "module_id",
    "version",
    "status",
    "created_date",
    "last_updated",
    "owner",
    "standard_type",
    "applicable_scope",
    "compliance_level",
    "parent_document",
]


REQUIRED_SECTIONS = [
    {
        "name": "文档职责说明",
        "patterns": [
            r'##\s*📋\s*文档职责说明',
            r'##\s*文档职责说明',
        ],
        "required": True,
        "weight": 10,
    },
    {
        "name": "执行摘要",
        "patterns": [
            r'##\s*📋\s*执行摘要',
            r'##\s*执行摘要',
        ],
        "required": True,
        "weight": 8,
    },
    {
        "name": "架构设计",
        "patterns": [
            r'##\s*一、架构设计',
            r'##\s*一、.*架构',
        ],
        "required": True,
        "weight": 9,
    },
    {
        "name": "功能设计",
        "patterns": [
            r'##\s*二、功能设计',
            r'##\s*二、.*功能',
            r'##\s*二、核心功能',
        ],
        "required": True,
        "weight": 9,
    },
    {
        "name": "数据模型",
        "patterns": [
            r'##\s*三、数据模型',
            r'##\s*三、.*数据',
            r'##\s*四、数据模型',
        ],
        "required": False,
        "weight": 7,
    },
    {
        "name": "实施路径",
        "patterns": [
            r'##\s*.*实施路径',
            r'##\s*.*实施计划',
            r'##\s*.*实施步骤',
        ],
        "required": True,
        "weight": 8,
    },
    {
        "name": "成功指标",
        "patterns": [
            r'##\s*.*成功指标',
            r'##\s*.*性能指标',
            r'##\s*.*质量指标',
        ],
        "required": False,
        "weight": 6,
    },
    {
        "name": "相关文档",
        "patterns": [
            r'##\s*.*相关文档',
            r'##\s*.*参考文档',
        ],
        "required": False,
        "weight": 5,
    },
    {
        "name": "版本历史",
        "patterns": [
            r'##\s*.*版本历史',
            r'##\s*.*变更历史',
        ],
        "required": False,
        "weight": 4,
    },
]


def check_yaml_fields(content: str) -> Dict:
    """检查YAML头部字段"""
    results = {
        "found": [],
        "missing": [],
    }
    
    yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not yaml_match:
        results["missing"] = REQUIRED_YAML_FIELDS.copy()
        return results
    
    yaml_content = yaml_match.group(1)
    
    for field in REQUIRED_YAML_FIELDS:
        if re.search(rf'^{field}:', yaml_content, re.MULTILINE):
            results["found"].append(field)
        else:
            results["missing"].append(field)
    
    return results


def check_sections(content: str) -> Dict:
    """检查文档章节"""
    results = {}
    
    for section in REQUIRED_SECTIONS:
        found = False
        for pattern in section["patterns"]:
            if re.search(pattern, content):
                found = True
                break
        
        results[section["name"]] = {
            "found": found,
            "required": section["required"],
            "weight": section["weight"],
        }
    
    return results


def calculate_completeness_score(yaml_results: Dict, section_results: Dict) -> float:
    """计算完整性得分"""
    total_weight = 0
    achieved_weight = 0
    
    yaml_weight = 10
    total_weight += yaml_weight
    if len(yaml_results["missing"]) == 0:
        achieved_weight += yaml_weight
    else:
        achieved_weight += yaml_weight * (len(yaml_results["found"]) / len(REQUIRED_YAML_FIELDS))
    
    for section_name, result in section_results.items():
        total_weight += result["weight"]
        if result["found"]:
            achieved_weight += result["weight"]
    
    return (achieved_weight / total_weight) * 100 if total_weight > 0 else 0


def analyze_document(file_path: Path) -> Dict:
    """分析单个文档"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        yaml_results = check_yaml_fields(content)
        section_results = check_sections(content)
        completeness_score = calculate_completeness_score(yaml_results, section_results)
        
        return {
            "file_name": file_path.name,
            "yaml_fields": yaml_results,
            "sections": section_results,
            "completeness_score": completeness_score,
        }
    except Exception as e:
        print(f"  ✗ 分析失败 {file_path.name}: {e}")
        return None


def main():
    """主函数"""
    print("=" * 80)
    print("文档内容完整性检查工具")
    print("=" * 80)
    print()
    
    if not LAYER11_DIR.exists():
        print(f"✗ 目录不存在: {LAYER11_DIR}")
        return
    
    md_files = list(LAYER11_DIR.glob("*.md"))
    print(f"发现 {len(md_files)} 个Markdown文件")
    print()
    
    print("=" * 80)
    print("第一阶段：检查文档完整性")
    print("=" * 80)
    print()
    
    results = []
    
    for md_file in sorted(md_files):
        if md_file.name == "INDEX.md":
            continue
        
        print(f"检查: {md_file.name}")
        result = analyze_document(md_file)
        if result:
            results.append(result)
            
            print(f"  完整性得分: {result['completeness_score']:.1f}%")
            
            if result['yaml_fields']['missing']:
                print(f"  缺失YAML字段: {', '.join(result['yaml_fields']['missing'])}")
            
            missing_required_sections = [
                name for name, res in result['sections'].items()
                if res['required'] and not res['found']
            ]
            if missing_required_sections:
                print(f"  缺失必要章节: {', '.join(missing_required_sections)}")
            
            print()
    
    print("=" * 80)
    print("第二阶段：统计分析")
    print("=" * 80)
    print()
    
    if results:
        avg_score = sum(r['completeness_score'] for r in results) / len(results)
        print(f"平均完整性得分: {avg_score:.1f}%")
        
        high_quality = [r for r in results if r['completeness_score'] >= 90]
        medium_quality = [r for r in results if 70 <= r['completeness_score'] < 90]
        low_quality = [r for r in results if r['completeness_score'] < 70]
        
        print(f"高质量文档 (≥90%): {len(high_quality)} 个")
        print(f"中等质量文档 (70-90%): {len(medium_quality)} 个")
        print(f"低质量文档 (<70%): {len(low_quality)} 个")
        print()
        
        print("=" * 80)
        print("第三阶段：改进建议")
        print("=" * 80)
        print()
        
        if low_quality:
            print("需要改进的文档:")
            for result in sorted(results, key=lambda x: x['completeness_score']):
                if result['completeness_score'] < 90:
                    print(f"  - {result['file_name']}: {result['completeness_score']:.1f}%")
        
        print()
        
        print("=" * 80)
        print("常见缺失章节统计")
        print("=" * 80)
        print()
        
        section_missing_count = {}
        for result in results:
            for section_name, section_result in result['sections'].items():
                if not section_result['found']:
                    section_missing_count[section_name] = section_missing_count.get(section_name, 0) + 1
        
        for section_name, count in sorted(section_missing_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {section_name}: {count} 个文档缺失")
        
        print()
    
    print("=" * 80)
    print("检查完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
