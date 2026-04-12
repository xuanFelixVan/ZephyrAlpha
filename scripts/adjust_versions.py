#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 11版本号调整工具
用途：根据文档成熟度调整版本号
版本：v1.0
创建日期：2026-04-06
"""

import os
import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime

LAYER11_DIR = Path("docs/11_STRATEGIC_DECISION")

VERSION_RULES = {
    "BLUEPRINT.md": "3.0.0",
    "RESPONSIBILITY_BOUNDARY_MATRIX.md": "1.0.0",
    "INDEX.md": "2.0.0",
    "OPEN_SOURCE_INTEGRATION_BLUEPRINT.md": "1.1.0",
    "TECHNOLOGY_SELECTION_DECISION.md": "1.1.0",
    "CAPITAL_ALLOCATION_BLUEPRINT.md": "1.0.0",
    "MARKET_REGIME_BLUEPRINT.md": "1.0.0",
    "MULTI_STRATEGY_COORDINATION_BLUEPRINT.md": "1.0.0",
    "PERFORMANCE_ATTRIBUTION_BLUEPRINT.md": "1.0.0",
    "TCA_BLUEPRINT.md": "1.0.0",
    "REBALANCING_BLUEPRINT.md": "1.0.0",
    "BENCHMARK_MANAGEMENT_BLUEPRINT.md": "1.0.0",
    "DECISION_AUDIT_BLUEPRINT.md": "1.0.0",
    "ESG_INVESTING_BLUEPRINT.md": "1.0.0",
    "INVESTMENT_CONSTRAINT_BLUEPRINT.md": "1.0.0",
    "IPS_MANAGEMENT_BLUEPRINT.md": "1.0.0",
    "LEVERAGE_MANAGEMENT_BLUEPRINT.md": "1.0.0",
    "LIQUIDITY_MANAGEMENT_BLUEPRINT.md": "1.0.0",
    "MACRO_FACTOR_BLUEPRINT.md": "1.0.0",
    "PORTFOLIO_INSURANCE_BLUEPRINT.md": "1.0.0",
    "SCENARIO_ANALYSIS_BLUEPRINT.md": "1.0.0",
    "TAX_MANAGEMENT_BLUEPRINT.md": "1.0.0",
}


def get_current_version(content: str) -> str:
    """获取当前版本号"""
    pattern = r'^version:\s*([\d.]+)'
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return match.group(1)
    return "0.0.0"


def update_version(file_path: Path, new_version: str) -> bool:
    """更新文档版本号"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        current_version = get_current_version(content)
        
        if current_version == new_version:
            print(f"  {file_path.name}: 版本号已是 {new_version}，跳过")
            return False
        
        content = re.sub(
            r'^version:\s*[\d.]+',
            f'version: {new_version}',
            content,
            flags=re.MULTILINE
        )
        
        today = datetime.now().strftime('%Y-%m-%d')
        content = re.sub(
            r'^last_updated:\s*[\d-]+',
            f'last_updated: {today}',
            content,
            flags=re.MULTILINE
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ {file_path.name}: {current_version} -> {new_version}")
        return True
    
    except Exception as e:
        print(f"  ✗ {file_path.name}: 更新失败 - {e}")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("Layer 11版本号调整工具")
    print("=" * 80)
    print()
    
    if not LAYER11_DIR.exists():
        print(f"✗ 目录不存在: {LAYER11_DIR}")
        return
    
    md_files = list(LAYER11_DIR.glob("*.md"))
    
    print(f"发现 {len(md_files)} 个Markdown文件")
    print()
    
    print("=" * 80)
    print("版本号调整规则")
    print("=" * 80)
    print()
    print("版本号分配原则:")
    print("  - v1.0.0: 初始版本，新创建的文档")
    print("  - v1.1.0: 有小幅更新的文档")
    print("  - v2.0.0: 有重大更新的文档（如INDEX.md）")
    print("  - v3.0.0: 总览文档（如BLUEPRINT.md）")
    print()
    
    print("=" * 80)
    print("开始调整版本号")
    print("=" * 80)
    print()
    
    updated_count = 0
    skipped_count = 0
    
    for md_file in sorted(md_files):
        target_version = VERSION_RULES.get(md_file.name)
        if target_version:
            if update_version(md_file, target_version):
                updated_count += 1
            else:
                skipped_count += 1
        else:
            print(f"  ⚠ {md_file.name}: 未定义版本规则，保持原版本")
            skipped_count += 1
    
    print()
    print("=" * 80)
    print("调整总结")
    print("=" * 80)
    print(f"总计更新: {updated_count} 个文档")
    print(f"跳过: {skipped_count} 个文档")
    print()
    
    print("=" * 80)
    print("版本号分布")
    print("=" * 80)
    print()
    
    version_count = {}
    for md_file in sorted(md_files):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            version = get_current_version(content)
            version_count[version] = version_count.get(version, 0) + 1
        except:
            pass
    
    for version, count in sorted(version_count.items()):
        print(f"  v{version}: {count} 个文档")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
