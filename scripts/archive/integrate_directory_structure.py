# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
整合目录结构脚本
用途：重命名design为05_DESIGN_DOCS，整合ui_design到design目录
创建时间：2026-04-07
"""

import shutil
from pathlib import Path
from datetime import datetime

CONSTRUCTION_DOCS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS")


def main():
    """主函数"""
    print("="*80)
    print("整合目录结构")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    operations = []
    
    # 1. 整合ui_design到design目录
    print("\n1. 整合ui_design到design目录")
    
    ui_design_dir = CONSTRUCTION_DOCS_DIR / "ui_design"
    design_dir = CONSTRUCTION_DOCS_DIR / "design"
    
    if ui_design_dir.exists():
        print("✅ ui_design 目录存在")
        
        if design_dir.exists():
            # 创建 ui_design 子目录
            target_ui_dir = design_dir / "ui_design"
            
            try:
                if not target_ui_dir.exists():
                    target_ui_dir.mkdir(parents=True)
                    print("✅ 创建目标目录: design/ui_design")
                
                # 移动所有文件
                for item in ui_design_dir.iterdir():
                    if item.is_file():
                        target_file = target_ui_dir / item.name
                        shutil.copy2(item, target_file)
                        print(f"✅ 复制文件: {item.name}")
                    elif item.is_dir():
                        target_subdir = target_ui_dir / item.name
                        if target_subdir.exists():
                            shutil.rmtree(target_subdir)
                        shutil.copytree(item, target_subdir)
                        print(f"✅ 复制目录: {item.name}")
                
                # 删除原目录
                shutil.rmtree(ui_design_dir)
                operations.append(("整合", "ui_design", "design/ui_design"))
                print("✅ 删除原目录: ui_design")
            except Exception as e:
                print(f"❌ 整合失败: {e}")
        else:
            print("⚠️ design 目录不存在")
    else:
        print("⚠️ ui_design 目录不存在")
    
    # 2. 重命名design为05_DESIGN_DOCS
    print("\n2. 重命名design为05_DESIGN_DOCS")
    
    if design_dir.exists():
        print("✅ design 目录存在")
        
        new_design_dir = CONSTRUCTION_DOCS_DIR / "05_DESIGN_DOCS"
        
        if not new_design_dir.exists():
            try:
                design_dir.rename(new_design_dir)
                operations.append(("重命名", "design", "05_DESIGN_DOCS"))
                print("✅ 重命名: design -> 05_DESIGN_DOCS")
            except Exception as e:
                print(f"❌ 重命名失败: {e}")
        else:
            print("⚠️ 05_DESIGN_DOCS 目录已存在")
    else:
        print("⚠️ design 目录不存在")
    
    # 3. 检查目录结构
    print("\n3. 检查目录结构")
    
    expected_dirs = [
        "01_BLUEPRINTS",
        "02_IMPLEMENTATION_GUIDES",
        "03_OPERATION_MANUALS",
        "04_CONFIG_TEMPLATES",
        "05_DESIGN_DOCS",
        "06_CHECKLISTS"
    ]
    
    print("\n预期目录结构:")
    for dir_name in expected_dirs:
        dir_path = CONSTRUCTION_DOCS_DIR / dir_name
        if dir_path.exists():
            file_count = len(list(dir_path.glob("**/*.*")))
            print(f"  ✅ {dir_name}: {file_count}个文件")
        else:
            print(f"  ❌ {dir_name}: 不存在")
    
    print("\n" + "="*80)
    print("整合完成")
    print("="*80)
    print(f"总操作数: {len(operations)}")
    
    for op_type, source, target in operations:
        print(f"  - {op_type}: {source} -> {target}")
    
    return operations


if __name__ == "__main__":
    main()
