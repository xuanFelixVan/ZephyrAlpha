# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
检查所有蓝图文档的文档治理章节覆盖率
用途：扫描所有蓝图文档，识别缺少文档治理章节的文档
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict

DOCS_DIR = Path("docs")


def has_governance_section(content: str) -> bool:
    """检查是否已有文档治理章节"""
    return '文档治理' in content


def extract_yaml_header(content: str) -> dict:
    """提取YAML头部信息"""
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not yaml_match:
        return {}
    
    yaml_content = yaml_match.group(1)
    yaml_dict = {}
    
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            yaml_dict[key.strip()] = value.strip().strip('"\'')
    
    return yaml_dict


def scan_all_blueprints() -> Dict[str, List[Path]]:
    """扫描所有蓝图文档并分类"""
    categories = defaultdict(list)
    
    for blueprint_file in DOCS_DIR.rglob("*BLUEPRINT.md"):
        relative_path = blueprint_file.relative_to(DOCS_DIR)
        category = str(relative_path.parts[0]) if len(relative_path.parts) > 1 else "root"
        categories[category].append(blueprint_file)
    
    return categories


def check_governance_coverage() -> Tuple[int, int, List[Path], List[Path]]:
    """检查文档治理章节覆盖率"""
    categories = scan_all_blueprints()
    
    total_count = 0
    has_governance_count = 0
    missing_governance = []
    has_governance = []
    
    for category, files in sorted(categories.items()):
        for filepath in files:
            total_count += 1
            try:
                with open(filepath, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                if has_governance_section(content):
                    has_governance_count += 1
                    has_governance.append(filepath)
                else:
                    missing_governance.append(filepath)
            except Exception as e:
                print(f"  ❌ 读取失败 {filepath.name}: {e}")
                missing_governance.append(filepath)
    
    return total_count, has_governance_count, missing_governance, has_governance


def main():
    """主函数"""
    print("=" * 80)
    print("文档治理章节覆盖率检查")
    print("=" * 80)
    
    total, has_gov, missing, has = check_governance_coverage()
    
    coverage_rate = (has_gov / total * 100) if total > 0 else 0
    
    print(f"\n📊 总体统计:")
    print(f"  总文档数: {total}")
    print(f"  已有文档治理章节: {has_gov}")
    print(f"  缺少文档治理章节: {len(missing)}")
    print(f"  覆盖率: {coverage_rate:.1f}%")
    
    if missing:
        print(f"\n❌ 缺少文档治理章节的文档 ({len(missing)}个):")
        
        # 按目录分组显示
        from collections import defaultdict
        by_category = defaultdict(list)
        for filepath in missing:
            relative_path = filepath.relative_to(DOCS_DIR)
            category = str(relative_path.parts[0]) if len(relative_path.parts) > 1 else "root"
            by_category[category].append(filepath)
        
        for category in sorted(by_category.keys()):
            files = by_category[category]
            print(f"\n  📁 {category} ({len(files)}个):")
            for filepath in files[:5]:  # 只显示前5个
                print(f"    - {filepath.name}")
            if len(files) > 5:
                print(f"    ... 还有 {len(files) - 5} 个文档")
    
    print("\n" + "=" * 80)
    
    if coverage_rate >= 100:
        print("✅ 文档治理章节覆盖率已达100%！")
    else:
        print(f"⚠️  需要为 {len(missing)} 个文档添加文档治理章节")
    
    print("=" * 80)
    
    return missing


if __name__ == "__main__":
    missing_files = main()
    
    # 返回缺少文档治理章节的文件列表，供其他脚本使用
    if missing_files:
        print(f"\n💡 提示: 可以运行 scripts/add_governance_section_all.py 来批量添加文档治理章节")
