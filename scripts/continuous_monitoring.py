"""
持续监控机制脚本
用途：定期运行深度审计并生成报告
创建时间：2026-04-07
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

def run_quick_audit() -> Dict:
    stats = {
        "total_files": 0,
        "total_dirs": 0,
        "files_with_yaml": 0,
        "files_with_responsibility": 0,
        "files_with_module_id": 0,
        "encoding_issues": 0,
        "sparse_dirs": 0
    }
    
    for root, dirs, files in os.walk(DOCS_DIR):
        stats["total_dirs"] += 1
        
        md_files = [f for f in files if f.endswith('.md')]
        
        if len(md_files) < 3 and len(md_files) > 0:
            stats["sparse_dirs"] += 1
        
        for file in md_files:
            stats["total_files"] += 1
            file_path = Path(root) / file
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.startswith('---'):
                    stats["files_with_yaml"] += 1
                    
                    if 'responsibility:' in content:
                        stats["files_with_responsibility"] += 1
                    
                    if 'module_id:' in content:
                        stats["files_with_module_id"] += 1
            except UnicodeDecodeError:
                stats["encoding_issues"] += 1
    
    return stats

def calculate_compliance_rate(stats: Dict) -> float:
    if stats["total_files"] == 0:
        return 0.0
    
    yaml_rate = stats["files_with_yaml"] / stats["total_files"]
    responsibility_rate = stats["files_with_responsibility"] / stats["total_files"]
    module_id_rate = stats["files_with_module_id"] / stats["total_files"]
    encoding_rate = 1 - (stats["encoding_issues"] / stats["total_files"])
    
    compliance_rate = (yaml_rate + responsibility_rate + module_id_rate + encoding_rate) / 4
    
    return round(compliance_rate * 100, 2)

def generate_monitoring_report(stats: Dict, compliance_rate: float):
    report_path = OUTPUT_DIR / f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 文档治理监控报告\n\n")
        f.write(f"> **监控时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> **监控范围**: {DOCS_DIR}\n")
        f.write(f"> **合规率**: {compliance_rate}%\n\n")
        
        f.write("## 📊 监控统计\n\n")
        f.write(f"- **总文件数**: {stats['total_files']}\n")
        f.write(f"- **总目录数**: {stats['total_dirs']}\n")
        f.write(f"- **稀疏目录数**: {stats['sparse_dirs']}\n\n")
        
        f.write("## ✅ 合规性指标\n\n")
        f.write("| 指标 | 数量 | 比例 |\n")
        f.write("|------|------|------|\n")
        
        yaml_rate = round(stats['files_with_yaml'] / stats['total_files'] * 100, 2) if stats['total_files'] > 0 else 0
        f.write(f"| YAML头部 | {stats['files_with_yaml']} | {yaml_rate}% |\n")
        
        resp_rate = round(stats['files_with_responsibility'] / stats['total_files'] * 100, 2) if stats['total_files'] > 0 else 0
        f.write(f"| 职责描述 | {stats['files_with_responsibility']} | {resp_rate}% |\n")
        
        module_rate = round(stats['files_with_module_id'] / stats['total_files'] * 100, 2) if stats['total_files'] > 0 else 0
        f.write(f"| Module ID | {stats['files_with_module_id']} | {module_rate}% |\n")
        
        encoding_rate = round((1 - stats['encoding_issues'] / stats['total_files']) * 100, 2) if stats['total_files'] > 0 else 0
        f.write(f"| UTF-8编码 | {stats['total_files'] - stats['encoding_issues']} | {encoding_rate}% |\n\n")
        
        f.write("## 🎯 合规率趋势\n\n")
        f.write(f"- **当前合规率**: {compliance_rate}%\n")
        f.write(f"- **目标合规率**: 99.9%+\n")
        
        if compliance_rate >= 99.9:
            f.write(f"- **状态**: ✅ 达标\n")
        elif compliance_rate >= 95:
            f.write(f"- **状态**: ⚠️ 接近达标\n")
        else:
            f.write(f"- **状态**: ❌ 需要改进\n")
        
        f.write("\n")
        
        f.write("## 📝 改进建议\n\n")
        
        if stats['encoding_issues'] > 0:
            f.write(f"1. **修复编码问题**: 还有{stats['encoding_issues']}个文件存在编码问题\n")
        
        if stats['files_with_yaml'] < stats['total_files']:
            missing_yaml = stats['total_files'] - stats['files_with_yaml']
            f.write(f"2. **添加YAML头部**: 还有{missing_yaml}个文件缺少YAML头部\n")
        
        if stats['files_with_responsibility'] < stats['total_files']:
            missing_resp = stats['total_files'] - stats['files_with_responsibility']
            f.write(f"3. **添加职责描述**: 还有{missing_resp}个文件缺少职责描述\n")
        
        if stats['sparse_dirs'] > 0:
            f.write(f"4. **整合稀疏目录**: 还有{stats['sparse_dirs']}个稀疏目录需要整合\n")
        
        f.write("\n")
        f.write("## 🔄 下次监控\n\n")
        f.write("- **建议频率**: 每日运行一次\n")
        f.write("- **运行命令**: `python scripts/continuous_monitoring.py`\n")
    
    return report_path

def save_stats_history(stats: Dict, compliance_rate: float):
    history_path = OUTPUT_DIR / "monitoring_history.json"
    
    history = []
    if history_path.exists():
        with open(history_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
    
    history.append({
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "compliance_rate": compliance_rate
    })
    
    if len(history) > 30:
        history = history[-30:]
    
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def main():
    print("=" * 80)
    print("文档治理持续监控")
    print("=" * 80)
    print(f"监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"监控范围: {DOCS_DIR}")
    print("=" * 80)
    
    print("\n运行快速审计...")
    stats = run_quick_audit()
    
    print(f"总文件数: {stats['total_files']}")
    print(f"总目录数: {stats['total_dirs']}")
    print(f"稀疏目录数: {stats['sparse_dirs']}")
    
    print("\n计算合规率...")
    compliance_rate = calculate_compliance_rate(stats)
    print(f"合规率: {compliance_rate}%")
    
    print("\n生成监控报告...")
    report_path = generate_monitoring_report(stats, compliance_rate)
    print(f"报告已保存至: {report_path}")
    
    print("\n保存历史记录...")
    save_stats_history(stats, compliance_rate)
    
    print("\n" + "=" * 80)
    print("监控完成")
    print("=" * 80)
    print(f"合规率: {compliance_rate}%")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
