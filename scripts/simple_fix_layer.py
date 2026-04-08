"""
简单修复Layer定位脚本
用途：为所有缺少Layer定位的文档添加Layer字段
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


def infer_layer_from_filename(filename: str) -> str:
    """从文件名推断Layer"""
    filename_upper = filename.upper()
    
    layer_mapping = {
        "DATA": "Layer 1 (数据源层)",
        "ALPHA": "Layer 2 (Alpha因子层)",
        "FACTOR": "Layer 2 (Alpha因子层)",
        "STRATEGY": "Layer 3 (策略层)",
        "AI": "Layer 4 (机器学习层)",
        "MACHINE": "Layer 4 (机器学习层)",
        "PORTFOLIO": "Layer 6 (组合优化层)",
        "OPTIMIZATION": "Layer 6 (组合优化层)",
        "REBALANCING": "Layer 6 (组合优化层)",
        "RISK": "Layer 7 (风险管理层)",
        "EXECUTION": "Layer 8 (执行层)",
        "TRADING": "Layer 8 (执行层)",
        "MONITORING": "Layer 9 (监控层)",
        "IMPLEMENTATION": "Layer 6 (组合优化层)",
    }
    
    for keyword, layer_name in layer_mapping.items():
        if keyword in filename_upper:
            return layer_name
    
    return "Layer 6 (组合优化层)"  # 默认


def main():
    """主函数"""
    print("="*80)
    print("修复Layer定位")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    stats = {
        "total": 0,
        "success": 0,
        "no_change": 0,
        "failed": 0
    }
    
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        stats["total"] += 1
        content = read_document(filepath)
        
        if not content:
            stats["failed"] += 1
            print(f"❌ {filepath.name}: 无法读取")
            continue
        
        # 检查是否已有layer字段
        if re.search(r'^layer:\s*["\']?.*?["\']?\s*$', content, re.MULTILINE):
            stats["no_change"] += 1
            continue
        
        # 从文件名推断Layer
        layer = infer_layer_from_filename(filepath.name)
        
        # 添加layer字段到YAML头部
        yaml_match = re.match(r'^(---\s*\n)(.*?)(\n---\s*\n)', content, re.DOTALL)
        
        if yaml_match:
            yaml_content = yaml_match.group(2)
            rest_content = content[yaml_match.end():]
            
            # 添加layer字段
            yaml_content += f'\nlayer: "{layer}"'
            
            # 重新构建文档
            new_content = f"---\n{yaml_content}\n---\n" + rest_content
            
            # 保存文件
            try:
                with open(filepath, 'w', encoding='utf-8-sig') as f:
                    f.write(new_content)
                stats["success"] += 1
                print(f"✅ {filepath.name}: 添加Layer定位 -> {layer}")
            except Exception as e:
                stats["failed"] += 1
                print(f"❌ {filepath.name}: 保存失败 - {e}")
        else:
            stats["failed"] += 1
            print(f"❌ {filepath.name}: 无YAML头部")
    
    print("\n" + "="*80)
    print("修复完成")
    print("="*80)
    print(f"总文档数: {stats['total']}")
    print(f"修复成功: {stats['success']}")
    print(f"无需修复: {stats['no_change']}")
    print(f"修复失败: {stats['failed']}")


if __name__ == "__main__":
    main()
