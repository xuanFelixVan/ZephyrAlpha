#!/usr/bin/env python3
"""
P0级蓝图整合脚本
将分散的P0级蓝图整合到 docs/11_STRATEGIC_DECISION/
"""

import shutil
from pathlib import Path
from datetime import datetime

DOCS_ROOT = Path("d:/ZephyrAlpha/docs")
TARGET_DIR = DOCS_ROOT / "11_STRATEGIC_DECISION"
ARCHIVE_DIR = DOCS_ROOT / "99_ARCHIVE" / f"P0_BLUEPRINT_INTEGRATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# P0蓝图整合映射
BLUEPRINT_INTEGRATION = {
    # 风险预算相关蓝图
    "risk-budgeting-framework-blueprint.md": {
        "source": DOCS_ROOT / "01_FRAMEWORK" / "dynamic-risk-budgeting-blueprint.md",
        "target_name": "risk-budgeting-framework-blueprint.md",
        "exists_check": DOCS_ROOT / "10_AI_WORKFLOW" / "risk-budget-management-blueprint.md",
    },
    # 可以添加更多需要整合的蓝图
}

def integrate_blueprint(name, config, dry_run=True):
    """整合单个蓝图"""
    source = config["source"]
    target = TARGET_DIR / config["target_name"]
    exists_check = config.get("exists_check")

    print(f"\n[INFO] 处理: {name}")

    # 检查源文件是否存在
    if not source.exists():
        print(f"  [SKIP] 源文件不存在: {source}")
        return False

    # 检查目标是否已存在
    if target.exists():
        print(f"  [SKIP] 目标已存在: {target}")
        return False

    # 检查是否有重复内容
    if exists_check and exists_check.exists():
        print(f"  [WARN] 发现重复内容文件: {exists_check}")
        print(f"         需要人工决定保留哪个版本")
        return False

    if dry_run:
        print(f"  [DRY-RUN] 将移动: {source.name} -> 11_STRATEGIC_DECISION/{config['target_name']}")
        return True

    try:
        # 移动文件
        shutil.move(str(source), str(target))
        print(f"  [OK] 已整合: {source.name} -> {target.name}")
        return True
    except Exception as e:
        print(f"  [ERROR] 移动失败: {e}")
        return False

def update_complete_blueprint_overview():
    """更新 complete-blueprint-overview.md 的统计"""
    overview_file = TARGET_DIR / "complete-blueprint-overview.md"

    if not overview_file.exists():
        print("[ERROR] 找不到 complete-blueprint-overview.md")
        return False

    print("\n[INFO] 更新 complete-blueprint-overview.md 统计...")

    # 读取文件
    content = overview_file.read_text(encoding='utf-8')

    # 更新统计数字
    # 从 21/32 更新为 23/32（如果成功整合2个）
    if "existing_count: 21" in content:
        content = content.replace("existing_count: 21", "existing_count: 23")
        content = content.replace("missing_count: 11", "missing_count: 9")
        print("  [OK] 已更新统计: 21 -> 23 个已有, 11 -> 9 个缺失")

    # 写回文件
    overview_file.write_text(content, encoding='utf-8')
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="P0级蓝图整合工具")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行")
    parser.add_argument("--execute", action="store_true", help="实际执行")

    args = parser.parse_args()

    dry_run = not args.execute
    mode = "[DRY-RUN]" if dry_run else "[EXECUTE]"

    print("="*70)
    print(f"P0级蓝图整合 {mode}")
    print("="*70)

    success_count = 0
    for name, config in BLUEPRINT_INTEGRATION.items():
        if integrate_blueprint(name, config, dry_run):
            success_count += 1

    # 更新统计
    if not dry_run and success_count > 0:
        update_complete_blueprint_overview()

    print("\n" + "="*70)
    print(f"完成: {success_count}/{len(BLUEPRINT_INTEGRATION)} 个蓝图已整合")
    if dry_run:
        print("确认无误后，运行: python scripts/integrate_p0_blueprints.py --execute")
    print("="*70)

if __name__ == "__main__":
    main()
