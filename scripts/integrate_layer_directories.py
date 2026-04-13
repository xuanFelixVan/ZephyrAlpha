#!/usr/bin/env python3
"""
Layer目录整合脚本
分析并整合命名不规范的Layer目录到标准目录结构中
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DOCS_ROOT = Path("d:/ZephyrAlpha/docs")
ARCHIVE_DIR = DOCS_ROOT / "99_ARCHIVE"

# 标准目录映射关系
LAYER_MAPPINGS = {
    # Layer重复目录 -> 标准目录
    "01_Layer_Definition": "01_FRAMEWORK",
    "02_Layer_Hierarchy": "01_FRAMEWORK",
    "03_Layer_Identifier": "02_FACTOR_LIBRARY",
    "05_Layer_3_Strategy": "03_TRADING_TACTICS",
    "06_Layer_3_Sentiment": "03_TRADING_TACTICS",
    "06__Layer_": "03_TRADING_TACTICS",  # 可能也是策略相关
    "07_Layer_6_Portfolio": "04_EXECUTION",  # 执行/组合优化
    "08_Layer_7_AI_Report": "07_AI_REPORTING",
    "09_Layer_8_HCI": "08_HUMAN_AI_INTERFACE",
    "10_Layer_X_Template": "11_STRATEGIC_DECISION",  # 模板归入战略层
    "14_Layer": "01_FRAMEWORK",  # 通用Layer定义
    "19_Layer 7 (AI)": "07_AI_REPORTING",
    "21_Layer X (Layer)": "11_STRATEGIC_DECISION",
    "24_Layer_3": "03_TRADING_TACTICS",
    "30_Layer_7_AI": "07_AI_REPORTING",
    "32_Layer_8": "08_HUMAN_AI_INTERFACE",
    "35_Layer_X_Layer": "11_STRATEGIC_DECISION",
    
    # 小写Layer目录
    "layer_1": "01_FRAMEWORK",
    "layer_4": "04_EXECUTION",
    "layer_6": "07_AI_REPORTING",  # Layer 6是组合优化，可归入AI报告或执行
    "layer_9": "09_AUDIT",  # Layer 9是研究与创新
    
    # 带括号的Layer目录
    "Layer 1 ()": "01_FRAMEWORK",
    "Layer 1 (数据源层)": "01_FRAMEWORK",
    "Layer 3 ()": "03_TRADING_TACTICS",
    "Layer 3 (策略层)": "03_TRADING_TACTICS",
    "Layer 3 (舆情分析层)": "03_TRADING_TACTICS",
    "Layer 6 ()": "04_EXECUTION",
    "Layer 6 (组合优化层)": "04_EXECUTION",
    "Layer 7 (AI)": "07_AI_REPORTING",
    "Layer 7 (AI报告层)": "07_AI_REPORTING",
    "Layer 8 ()": "08_HUMAN_AI_INTERFACE",
    "Layer 8 (人机交互层)": "08_HUMAN_AI_INTERFACE",
    "Layer X ([Layer])": "11_STRATEGIC_DECISION",
    "Layer X ([Layer名称])": "11_STRATEGIC_DECISION",
    
    # 特殊字符目录（文件少，可直接归档）
    "'[Layer]'": None,  # 归档
    "'[Layer定位]'": None,
    "- 层级": None,
    "- 层级标识": None,
    "01_'[Layer]'": None,
    "02_-": None,
    "03_-": None,
    "04_-": None,
    "layer_": None,
    "l": None,
    "37": None,
    "舆情分析": None,
    "12_lay": None,
    "13_laye": None,
    "15_Layer 1 ()": "01_FRAMEWORK",
    "16_Layer 3 ()": "03_TRADING_TACTICS",
    "17_Layer 3 ()": "03_TRADING_TACTICS",
    "18_Layer 6 ()": "04_EXECUTION",
    "20_Layer 8 ()": "08_HUMAN_AI_INTERFACE",
}

# 高风险目录（需要手动评估）
HIGH_RISK_DIRS = [
    "06_CONSTRUCTION_DOCS",  # 有4个文件，可能是重要文档
    "07_AI_REPORTING",  # 有2个文件，与标准目录同名
    "07_RESEARCH",  # 有18个文件，可能是重要内容
    "08_HUMAN_AI_INTERFACE",  # 有151个文件！非常重要
    "08_KNOWLEDGE",  # 13个文件
    "08_KNOWLEDGE_BASE",  # 6个文件
    "09_RESEARCH_INNOVATION",  # 30个文件
    "10_GOVERNANCE_COMPLIANCE",  # 21个文件，可能是新标准目录
    "11_Sentiment_Analysis",  # 1个文件
    "12_MODULE_DESIGNS",  # 3个文件
]


def analyze_directory(dir_name: str) -> dict:
    """分析目录内容"""
    dir_path = DOCS_ROOT / dir_name
    if not dir_path.exists():
        return None
    
    files = list(dir_path.rglob("*.md"))
    total_size = sum(f.stat().st_size for f in files if f.exists())
    
    return {
        "name": dir_name,
        "path": dir_path,
        "file_count": len(files),
        "total_size_kb": total_size / 1024,
        "mapping": LAYER_MAPPINGS.get(dir_name),
        "is_high_risk": dir_name in HIGH_RISK_DIRS,
    }


def print_analysis():
    """打印目录分析结果"""
    print("="*70)
    print("Layer目录整合分析")
    print("="*70)
    
    # 分析所有映射的目录
    mappings_found = []
    orphaned_dirs = []
    high_risk_dirs = []
    
    for dir_name in LAYER_MAPPINGS:
        info = analyze_directory(dir_name)
        if info:
            mappings_found.append(info)
    
    # 检查高风险的非映射目录
    for dir_name in HIGH_RISK_DIRS:
        if dir_name not in LAYER_MAPPINGS:
            info = analyze_directory(dir_name)
            if info:
                high_risk_dirs.append(info)
    
    print("\n[1] 可自动整合的目录 (有明确映射):")
    print("-" * 70)
    for info in sorted(mappings_found, key=lambda x: x["file_count"], reverse=True):
        if info["mapping"]:
            print(f"  {info['name']:<35} -> {info['mapping']:<25} ({info['file_count']} files)")
        else:
            print(f"  {info['name']:<35} -> [ARCHIVE]                ({info['file_count']} files)")
    
    print("\n[2] 高价值目录 (需要手动评估):")
    print("-" * 70)
    for info in sorted(high_risk_dirs, key=lambda x: x["file_count"], reverse=True):
        print(f"  {info['name']:<35} ({info['file_count']:>3} files, {info['total_size_kb']:.1f} KB)")
    
    print("\n[3] 建议操作:")
    print("-" * 70)
    auto_count = sum(1 for i in mappings_found if i["mapping"])
    archive_count = sum(1 for i in mappings_found if not i["mapping"])
    print(f"  - 自动整合: {auto_count} 个目录 (合并到标准目录)")
    print(f"  - 归档清理: {archive_count} 个目录 (移动到99_ARCHIVE)")
    print(f"  - 手动评估: {len(high_risk_dirs)} 个目录 (需人工决策)")
    
    print("\n" + "="*70)


def execute_integration(dry_run: bool = True):
    """执行目录整合"""
    print("="*70)
    print(f"执行目录整合 {'[DRY-RUN]' if dry_run else '[EXECUTE]'}")
    print("="*70)
    
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    stats = {"integrated": 0, "archived": 0, "skipped": 0, "errors": 0}
    
    for dir_name, target in LAYER_MAPPINGS.items():
        dir_path = DOCS_ROOT / dir_name
        if not dir_path.exists():
            continue
        
        files = list(dir_path.rglob("*.md"))
        
        if target is None:
            # 归档
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            target_path = ARCHIVE_DIR / f"{dir_name}_ARCHIVED_{timestamp}"
            
            if dry_run:
                print(f"[DRY-RUN] Archive: {dir_name} ({len(files)} files)")
            else:
                try:
                    shutil.move(str(dir_path), str(target_path))
                    print(f"[OK] Archived: {dir_name}")
                    stats["archived"] += 1
                except Exception as e:
                    print(f"[ERROR] Failed to archive {dir_name}: {e}")
                    stats["errors"] += 1
        else:
            # 整合到目标目录
            target_path = DOCS_ROOT / target
            
            if not target_path.exists():
                print(f"[SKIP] Target not found: {target}")
                stats["skipped"] += 1
                continue
            
            if dry_run:
                print(f"[DRY-RUN] Integrate: {dir_name} -> {target} ({len(files)} files)")
            else:
                # 移动文件到目标目录的子目录
                subdir_name = f"integrated_from_{dir_name.replace(' ', '_').replace('(', '').replace(')', '')}"
                target_subdir = target_path / subdir_name
                
                try:
                    target_subdir.mkdir(exist_ok=True)
                    
                    # 复制文件
                    for file in files:
                        dest = target_subdir / file.name
                        shutil.copy2(str(file), str(dest))
                    
                    # 移动原目录到归档
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    archive_path = ARCHIVE_DIR / f"{dir_name}_INTEGRATED_{timestamp}"
                    shutil.move(str(dir_path), str(archive_path))
                    
                    print(f"[OK] Integrated: {dir_name} -> {target}/{subdir_name}")
                    stats["integrated"] += 1
                except Exception as e:
                    print(f"[ERROR] Failed to integrate {dir_name}: {e}")
                    stats["errors"] += 1
    
    print("\n" + "="*70)
    print("统计:")
    print(f"  整合: {stats['integrated']}")
    print(f"  归档: {stats['archived']}")
    print(f"  跳过: {stats['skipped']}")
    print(f"  错误: {stats['errors']}")
    print("="*70)


def main():
    parser = argparse.ArgumentParser(description="Layer目录整合工具")
    parser.add_argument("--analyze", action="store_true", help="仅分析")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行")
    parser.add_argument("--execute", action="store_true", help="实际执行")
    
    args = parser.parse_args()
    
    if args.analyze or (not args.dry_run and not args.execute):
        print_analysis()
    elif args.dry_run:
        execute_integration(dry_run=True)
    elif args.execute:
        execute_integration(dry_run=False)


if __name__ == "__main__":
    main()
