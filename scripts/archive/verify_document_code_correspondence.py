#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
文档代码对应原则验证工具
用途：验证Layer 11文档与代码的对应关系
版本：v1.0
创建日期：2026-04-07
"""

import re
from pathlib import Path
from typing import Dict, List

LAYER11_DIR = Path("docs/11_STRATEGIC_DECISION")
SRC_DIR = Path("src")


DOCUMENT_CODE_MAPPING = {
    "MARKET_REGIME_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/economic_regime_engine/",
            "src/modules/economic_regime_engine/economic_regime_engine.py",
        ],
        "keywords": ["regime", "market_state", "economic_cycle"],
        "status": "已实现",
    },
    "SCENARIO_ANALYSIS_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/scenario_analyzer.py",
        ],
        "keywords": ["scenario", "stress_test", "pressure"],
        "status": "已实现",
    },
    "INVESTMENT_CONSTRAINT_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/compliance_checker.py",
        ],
        "keywords": ["constraint", "compliance", "limit"],
        "status": "已实现",
    },
    "CAPITAL_ALLOCATION_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/capital_allocation/",
        ],
        "keywords": ["capital", "allocation", "asset_allocation"],
        "status": "待实现",
    },
    "MACRO_FACTOR_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/macro_factor/",
        ],
        "keywords": ["macro", "factor", "exposure"],
        "status": "待实现",
    },
    "REBALANCING_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/rebalancing/",
        ],
        "keywords": ["rebalance", "rebalancing"],
        "status": "待实现",
    },
    "IPS_MANAGEMENT_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/ips_management/",
        ],
        "keywords": ["ips", "investment_policy"],
        "status": "待实现",
    },
    "MULTI_STRATEGY_COORDINATION_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/multi_strategy/",
        ],
        "keywords": ["multi_strategy", "coordination"],
        "status": "待实现",
    },
    "PERFORMANCE_ATTRIBUTION_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/performance_attribution/",
        ],
        "keywords": ["attribution", "performance", "brinson"],
        "status": "待实现",
    },
    "TCA_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/execution_cost_reporter.py",
            "src/modules/tca/",
        ],
        "keywords": ["tca", "transaction_cost", "execution_cost"],
        "status": "部分实现",
    },
    "BENCHMARK_MANAGEMENT_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/benchmark_management/",
        ],
        "keywords": ["benchmark", "tracking_error"],
        "status": "待实现",
    },
    "PORTFOLIO_INSURANCE_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/portfolio_insurance/",
        ],
        "keywords": ["cppi", "tipp", "portfolio_insurance"],
        "status": "待实现",
    },
    "LEVERAGE_MANAGEMENT_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/leverage_management/",
        ],
        "keywords": ["leverage", "margin", "financing"],
        "status": "待实现",
    },
    "LIQUIDITY_MANAGEMENT_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/liquidity_management/",
        ],
        "keywords": ["liquidity", "liquid"],
        "status": "待实现",
    },
    "ESG_INVESTING_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/esg/",
        ],
        "keywords": ["esg", "sustainable"],
        "status": "待实现",
    },
    "TAX_MANAGEMENT_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/tax_management/",
        ],
        "keywords": ["tax", "taxation"],
        "status": "待实现",
    },
    "DECISION_AUDIT_BLUEPRINT.md": {
        "expected_paths": [
            "src/modules/decision_audit/",
        ],
        "keywords": ["audit", "decision_trace"],
        "status": "待实现",
    },
    "OPEN_SOURCE_INTEGRATION_BLUEPRINT.md": {
        "expected_paths": [
            "src/integration/",
        ],
        "keywords": ["open_source", "integration"],
        "status": "待实现",
    },
}


def check_code_exists(expected_paths: List[str]) -> Dict:
    """检查代码是否存在"""
    results = {
        "found": [],
        "not_found": [],
    }
    
    for path in expected_paths:
        full_path = Path(path)
        if full_path.exists():
            results["found"].append(path)
        else:
            results["not_found"].append(path)
    
    return results


def search_keywords_in_code(keywords: List[str], src_dir: Path) -> Dict:
    """在代码中搜索关键词"""
    results = {}
    
    for keyword in keywords:
        results[keyword] = []
        
        for py_file in src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if keyword.lower() in content.lower():
                        results[keyword].append(str(py_file.relative_to(src_dir)))
            except:
                pass
    
    return results


def analyze_document(doc_name: str, mapping: Dict) -> Dict:
    """分析单个文档"""
    result = {
        "document": doc_name,
        "expected_status": mapping["status"],
        "code_check": check_code_exists(mapping["expected_paths"]),
        "keyword_search": search_keywords_in_code(mapping["keywords"], SRC_DIR),
    }
    
    found_count = len(result["code_check"]["found"])
    total_count = len(mapping["expected_paths"])
    result["coverage"] = f"{found_count}/{total_count}"
    
    if found_count > 0:
        result["actual_status"] = "已实现" if found_count == total_count else "部分实现"
    else:
        keyword_matches = sum(1 for k, files in result["keyword_search"].items() if files)
        if keyword_matches > 0:
            result["actual_status"] = "部分实现"
        else:
            result["actual_status"] = "待实现"
    
    return result


def main():
    """主函数"""
    print("=" * 80)
    print("文档代码对应原则验证工具")
    print("=" * 80)
    print()
    
    if not LAYER11_DIR.exists():
        print(f"✗ 目录不存在: {LAYER11_DIR}")
        return
    
    if not SRC_DIR.exists():
        print(f"✗ 目录不存在: {SRC_DIR}")
        return
    
    print("=" * 80)
    print("第一阶段：验证文档与代码对应关系")
    print("=" * 80)
    print()
    
    results = []
    
    for doc_name, mapping in DOCUMENT_CODE_MAPPING.items():
        print(f"检查: {doc_name}")
        result = analyze_document(doc_name, mapping)
        results.append(result)
        
        print(f"  预期状态: {result['expected_status']}")
        print(f"  实际状态: {result['actual_status']}")
        print(f"  代码覆盖率: {result['coverage']}")
        
        if result['code_check']['found']:
            print(f"  已找到代码:")
            for path in result['code_check']['found']:
                print(f"    ✓ {path}")
        
        if result['code_check']['not_found']:
            print(f"  未找到代码:")
            for path in result['code_check']['not_found']:
                print(f"    ✗ {path}")
        
        print()
    
    print("=" * 80)
    print("第二阶段：统计分析")
    print("=" * 80)
    print()
    
    status_count = {}
    for result in results:
        status = result['actual_status']
        status_count[status] = status_count.get(status, 0) + 1
    
    print("实现状态统计:")
    for status, count in sorted(status_count.items()):
        print(f"  {status}: {count} 个文档")
    
    print()
    
    print("=" * 80)
    print("第三阶段：生成实施建议")
    print("=" * 80)
    print()
    
    print("已实现模块:")
    for result in results:
        if result['actual_status'] == "已实现":
            print(f"  ✓ {result['document']}")
    
    print()
    
    print("部分实现模块:")
    for result in results:
        if result['actual_status'] == "部分实现":
            print(f"  ⚠ {result['document']}")
    
    print()
    
    print("待实现模块:")
    for result in results:
        if result['actual_status'] == "待实现":
            print(f"  ✗ {result['document']}")
    
    print()
    
    print("=" * 80)
    print("验证总结")
    print("=" * 80)
    print()
    
    total = len(results)
    implemented = status_count.get("已实现", 0)
    partial = status_count.get("部分实现", 0)
    pending = status_count.get("待实现", 0)
    
    print(f"总文档数: {total}")
    print(f"已实现: {implemented} ({implemented/total*100:.1f}%)")
    print(f"部分实现: {partial} ({partial/total*100:.1f}%)")
    print(f"待实现: {pending} ({pending/total*100:.1f}%)")
    print()
    
    print("=" * 80)
    print("建议优先实施的模块")
    print("=" * 80)
    print()
    
    priority_modules = [
        "CAPITAL_ALLOCATION_BLUEPRINT.md",
        "REBALANCING_BLUEPRINT.md",
        "MULTI_STRATEGY_COORDINATION_BLUEPRINT.md",
        "PERFORMANCE_ATTRIBUTION_BLUEPRINT.md",
    ]
    
    for i, module in enumerate(priority_modules, 1):
        print(f"{i}. {module}")
    
    print()


if __name__ == "__main__":
    main()
