"""
修复剩余问题脚本
用途：修复死链接和Layer定位缺失
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


def fix_dead_links(filepath: Path) -> int:
    """修复死链接"""
    content = read_document(filepath)
    if not content:
        return 0
    
    original_content = content
    fixed_count = 0
    
    # 查找所有链接
    links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
    
    for text, link in links:
        if link.startswith('http') or link.startswith('#'):
            continue
        
        # 检查链接是否存在
        if link.startswith('../'):
            target_path = filepath.parent.parent / link.replace('../', '')
        else:
            target_path = filepath.parent / link
        
        if not target_path.exists():
            # 删除死链接，保留文本
            content = content.replace(f'[{text}]({link})', text)
            fixed_count += 1
    
    # 保存修改
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(content)
    
    return fixed_count


def fix_layer_positioning(filepath: Path) -> bool:
    """修复Layer定位"""
    content = read_document(filepath)
    if not content:
        return False
    
    # 检查是否已有Layer定位
    if re.search(r'layer:\s*["\']?Layer\s+\d+', content):
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
        "IMPLEMENTATION": "Layer 6 (组合优化层)",
    }
    
    layer = None
    for keyword, layer_name in layer_mapping.items():
        if keyword in filename.upper():
            layer = layer_name
            break
    
    if not layer:
        layer = "Layer 6 (组合优化层)"  # 默认
    
    # 添加Layer定位到YAML头部
    yaml_match = re.match(r'^(---\s*\n.*?)(\n---\s*\n)', content, re.DOTALL)
    if yaml_match:
        yaml_header = yaml_match.group(1)
        yaml_end = yaml_match.group(2)
        rest_content = content[yaml_match.end():]
        
        # 添加layer字段
        if 'layer:' not in yaml_header:
            yaml_header += f"\nlayer: {layer}"
        
        content = yaml_header + yaml_end + rest_content
        
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        
        return True
    
    return False


def fix_change_history(filepath: Path) -> bool:
    """补充变更历史"""
    content = read_document(filepath)
    if not content:
        return False
    
    if '变更历史' in content or '版本历史' in content:
        return False
    
    # 添加变更历史
    change_history = """

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 实施团队 |
"""
    
    # 在文档末尾添加
    content = content.rstrip()
    if content.endswith('---'):
        content = content[:-3].rstrip()
    
    content = content + change_history + "\n\n---\n"
    
    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    return True


def main():
    """主函数"""
    print("="*80)
    print("修复剩余问题")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 需要修复的文档
    docs_to_fix = [
        "DYNAMIC_CORRELATION_MODELING_BLUEPRINT.md",
        "FACTOR_EXPOSURE_MANAGEMENT_BLUEPRINT.md",
        "IMPLEMENTATION_PROGRESS_TRACKING.md",
        "MULTI_PERIOD_DYNAMIC_OPTIMIZATION_BLUEPRINT.md",
        "PORTFOLIO_OPTIMIZATION_DIAGNOSTICS_BLUEPRINT.md",
    ]
    
    total_fixed = {
        "dead_links": 0,
        "layer_positioning": 0,
        "change_history": 0
    }
    
    for filename in docs_to_fix:
        filepath = BLUEPRINTS_DIR / filename
        if not filepath.exists():
            continue
        
        print(f"\n处理: {filename}")
        
        # 修复死链接
        dead_links_fixed = fix_dead_links(filepath)
        if dead_links_fixed > 0:
            total_fixed["dead_links"] += dead_links_fixed
            print(f"  ✅ 修复死链接: {dead_links_fixed}个")
        
        # 修复Layer定位
        if filename == "IMPLEMENTATION_PROGRESS_TRACKING.md":
            layer_fixed = fix_layer_positioning(filepath)
            if layer_fixed:
                total_fixed["layer_positioning"] += 1
                print(f"  ✅ 添加Layer定位")
        
        # 补充变更历史
        if filename == "IMPLEMENTATION_PROGRESS_TRACKING.md":
            history_fixed = fix_change_history(filepath)
            if history_fixed:
                total_fixed["change_history"] += 1
                print(f"  ✅ 补充变更历史")
    
    print("\n" + "="*80)
    print("修复完成")
    print("="*80)
    print(f"修复死链接: {total_fixed['dead_links']}个")
    print(f"添加Layer定位: {total_fixed['layer_positioning']}个")
    print(f"补充变更历史: {total_fixed['change_history']}个")


if __name__ == "__main__":
    main()
