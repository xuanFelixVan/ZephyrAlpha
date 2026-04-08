"""
修复Layer定位脚本 V3
用途：为缺少Layer的文档添加Layer定位
创建时间：2026-04-07
"""

import re
from pathlib import Path
from datetime import datetime

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")


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


def fix_layer(filepath: Path) -> bool:
    """修复Layer定位"""
    content = read_document(filepath)
    if not content:
        return False
    
    # 从文件名推断Layer
    filename = filepath.stem
    
    layer_mapping = {
        "DATA": "Layer 1 (数据源层)",
        "ALPHA": "Layer 2 (Alpha因子层)",
        "STRATEGY": "Layer 3 (策略层)",
        "AI": "Layer 4 (机器学习层)",
        "PORTFOLIO": "Layer 6 (组合优化层)",
        "REBALANCING": "Layer 6 (组合优化层)",
        "RISK": "Layer 7 (风险管理层)",
        "EXECUTION": "Layer 8 (执行层)",
        "TRADING": "Layer 8 (执行层)",
        "MONITORING": "Layer 9 (监控层)",
        "MEAN_VARIANCE": "Layer 6 (组合优化层)",
        "MARGIN": "Layer 7 (风险管理层)",
    }
    
    layer = "Layer 6 (组合优化层)"  # 默认
    for keyword, layer_name in layer_mapping.items():
        if keyword in filename.upper():
            layer = layer_name
            break
    
    # 检查是否已有layer字段
    if re.search(r'^layer:\s*["\']?', content, re.MULTILINE):
        # 更新layer字段
        content = re.sub(
            r'^layer:\s*["\']?.*?["\']?\s*$',
            f'layer: "{layer}"',
            content,
            flags=re.MULTILINE
        )
    else:
        # 添加layer字段到YAML头部
        content = re.sub(
            r'^(---\s*\n)(.*?)(\n---\s*\n)',
            r'\1\2\nlayer: "' + layer + '"\n\3',
            content,
            flags=re.DOTALL
        )
    
    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    return True


def main():
    """主函数"""
    print("="*80)
    print("修复Layer定位")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    fixed_count = 0
    
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        if fix_layer(filepath):
            fixed_count += 1
            print(f"✅ {filepath.name}")
    
    print("\n" + "="*80)
    print("完成")
    print("="*80)
    print(f"修复Layer定位: {fixed_count}个文档")


if __name__ == "__main__":
    main()
