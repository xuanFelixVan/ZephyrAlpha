# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
文档治理章节定期检查脚本
用途：定期检查文档治理章节覆盖率，确保保持100%
创建时间：2026-04-07
使用方法：
  1. 手动运行：python scripts/governance_check_schedule.py
  2. 定期运行：添加到CI/CD流程或定时任务
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

DOCS_DIR = Path("docs")
REPORT_FILE = Path("docs/09_AUDIT/REPORTS/governance_coverage_history.json")


def check_governance_coverage() -> Dict:
    """检查文档治理章节覆盖率"""
    total_count = 0
    has_governance_count = 0
    missing_files = []
    
    for blueprint_file in DOCS_DIR.rglob("*BLUEPRINT.md"):
        total_count += 1
        try:
            with open(blueprint_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            if '文档治理' in content:
                has_governance_count += 1
            else:
                missing_files.append(str(blueprint_file.relative_to(DOCS_DIR)))
        except Exception as e:
            missing_files.append(f"{blueprint_file.relative_to(DOCS_DIR)} (读取失败: {e})")
    
    coverage_rate = (has_governance_count / total_count * 100) if total_count > 0 else 0
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_count": total_count,
        "has_governance_count": has_governance_count,
        "missing_count": len(missing_files),
        "coverage_rate": round(coverage_rate, 2),
        "missing_files": missing_files,
        "status": "PASS" if coverage_rate >= 100 else "FAIL"
    }


def load_history() -> List[Dict]:
    """加载历史记录"""
    if REPORT_FILE.exists():
        with open(REPORT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_history(history: List[Dict]):
    """保存历史记录"""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def print_report(result: Dict):
    """打印报告"""
    print("=" * 80)
    print("文档治理章节覆盖率检查报告")
    print("=" * 80)
    print(f"检查时间: {result['timestamp']}")
    print(f"总文档数: {result['total_count']}")
    print(f"已有文档治理章节: {result['has_governance_count']}")
    print(f"缺少文档治理章节: {result['missing_count']}")
    print(f"覆盖率: {result['coverage_rate']}%")
    print(f"状态: {'✅ PASS' if result['status'] == 'PASS' else '❌ FAIL'}")
    
    if result['missing_files']:
        print(f"\n❌ 缺少文档治理章节的文档:")
        for filepath in result['missing_files'][:10]:
            print(f"  - {filepath}")
        if len(result['missing_files']) > 10:
            print(f"  ... 还有 {len(result['missing_files']) - 10} 个文档")
    
    print("=" * 80)


def main():
    """主函数"""
    print("🔍 开始检查文档治理章节覆盖率...\n")
    
    # 执行检查
    result = check_governance_coverage()
    
    # 打印报告
    print_report(result)
    
    # 加载并保存历史记录
    history = load_history()
    history.append(result)
    
    # 只保留最近30次记录
    if len(history) > 30:
        history = history[-30:]
    
    save_history(history)
    
    # 分析趋势
    if len(history) >= 2:
        prev_result = history[-2]
        trend = result['coverage_rate'] - prev_result['coverage_rate']
        print(f"\n📈 趋势分析:")
        print(f"  上次覆盖率: {prev_result['coverage_rate']}%")
        print(f"  本次覆盖率: {result['coverage_rate']}%")
        print(f"  变化: {'+' if trend >= 0 else ''}{trend:.2f}%")
    
    # 提供建议
    if result['status'] == 'FAIL':
        print(f"\n💡 建议:")
        print(f"  运行以下命令修复缺少文档治理章节的文档:")
        print(f"  python scripts/add_governance_section_all.py")
    
    return result['status'] == 'PASS'


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
