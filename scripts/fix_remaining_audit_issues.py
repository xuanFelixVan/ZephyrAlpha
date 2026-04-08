"""
修复剩余11个审计问题脚本
用途：修复L1和L3层剩余问题
创建时间：2026-04-07
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

CONSTRUCTION_DOCS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS")
BLUEPRINTS_DIR = CONSTRUCTION_DOCS_DIR / "01_BLUEPRINTS"


def read_document(filepath: Path) -> str:
    """读取文档内容"""
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""


def fix_layer_position(filepath: Path, correct_layer: str) -> bool:
    """修复Layer定位"""
    content = read_document(filepath)
    if not content:
        return False
    
    # 更新layer字段
    if re.search(r'^layer:\s*["\']?.*?["\']?\s*$', content, re.MULTILINE):
        content = re.sub(
            r'^layer:\s*["\']?.*?["\']?\s*$',
            f'layer: "{correct_layer}"',
            content,
            flags=re.MULTILINE
        )
    else:
        # 添加layer字段
        content = re.sub(
            r'(---\s*\n.*?)(\n---\s*\n)',
            r'\1\nlayer: "' + correct_layer + '"\n\2',
            content,
            flags=re.DOTALL
        )
    
    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    return True


def rename_file(filepath: Path, new_name: str) -> bool:
    """重命名文件"""
    try:
        new_path = filepath.parent / new_name
        shutil.move(str(filepath), str(new_path))
        return True
    except Exception as e:
        print(f"❌ 重命名失败: {e}")
        return False


def main():
    """主函数"""
    print("="*80)
    print("修复剩余11个审计问题")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    fixes = []
    
    # 修复P1级问题：Layer定位不准确
    print("\n修复P1级问题：Layer定位不准确")
    
    layer_fixes = [
        ("FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md", "Layer 2 (Alpha因子层)"),
        ("FACTOR_EXPOSURE_MANAGEMENT_BLUEPRINT.md", "Layer 2 (Alpha因子层)"),
        ("FACTOR_NEUTRAL_OPTIMIZATION_BLUEPRINT.md", "Layer 2 (Alpha因子层)"),
        ("TRADING_COST_OPTIMIZATION_BLUEPRINT.md", "Layer 6 (组合优化层)"),
    ]
    
    for filename, correct_layer in layer_fixes:
        filepath = BLUEPRINTS_DIR / filename
        if filepath.exists():
            if fix_layer_position(filepath, correct_layer):
                fixes.append(f"✅ 修复Layer定位: {filename} -> {correct_layer}")
                print(f"✅ {filename}: Layer定位已修复为 {correct_layer}")
        else:
            fixes.append(f"❌ 文件不存在: {filename}")
            print(f"❌ 文件不存在: {filename}")
    
    # 修复P2级问题：文件命名不规范
    print("\n修复P2级问题：文件命名不规范")
    
    old_name = "MARKET_PARTICIPANT_SIMULATION_INTEGRATION_ARCHITECTURE.md"
    new_name = "MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md"
    
    old_path = BLUEPRINTS_DIR / old_name
    if old_path.exists():
        if rename_file(old_path, new_name):
            fixes.append(f"✅ 重命名文件: {old_name} -> {new_name}")
            print(f"✅ 文件已重命名: {old_name} -> {new_name}")
    else:
        fixes.append(f"❌ 文件不存在: {old_name}")
        print(f"❌ 文件不存在: {old_name}")
    
    # P2级问题：目录漂移和稀疏目录（需要手动决策）
    print("\n⚠️ P2级问题：目录漂移和稀疏目录")
    print("以下目录需要手动处理：")
    print("1. 04_CONFIG_TEMPLATES - 建议保留（现有4个配置模板文件）")
    print("2. 05_PROGRESS_TRACKING - 建议整合到01_BLUEPRINTS")
    print("3. design - 建议重命名为05_DESIGN_DOCS")
    print("4. ui_design - 建议整合到design/ui_design")
    
    fixes.append("⚠️ 目录漂移问题需要手动决策")
    
    print("\n" + "="*80)
    print("修复完成")
    print("="*80)
    print(f"总修复数: {len([f for f in fixes if f.startswith('✅')])}")
    print(f"失败数: {len([f for f in fixes if f.startswith('❌')])}")
    
    return fixes


if __name__ == "__main__":
    main()
