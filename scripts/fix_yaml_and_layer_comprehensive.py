"""
全面修复双重YAML头部和Layer定位脚本
用途：修复所有文档的双重YAML头部和Layer定位问题
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


def fix_document(filepath: Path) -> dict:
    """修复文档"""
    content = read_document(filepath)
    if not content:
        return {"status": "failed", "reason": "无法读取"}
    
    changes = []
    
    # 1. 检查并修复双重YAML头部
    # 模式：第一个YAML头部 + 空行 + 第二个YAML头部（可能有BOM）
    double_yaml_pattern = r'^---\s*\n.*?\n---\s*\n\s*\ufeff?---\s*\n(.*?)\n---\s*\n'
    
    match = re.match(double_yaml_pattern, content, re.DOTALL)
    if match:
        # 保留第二个YAML头部
        second_yaml = match.group(1)
        rest_start = match.end()
        rest_content = content[rest_start:]
        
        # 构建新文档
        content = f"---\n{second_yaml}\n---\n" + rest_content
        changes.append("修复双重YAML头部")
    
    # 2. 检查并添加Layer定位
    # 提取YAML头部
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        
        # 检查是否已有layer字段
        if not re.search(r'^layer:\s*', yaml_content, re.MULTILINE):
            # 从文件名推断Layer
            filename = filepath.stem.upper()
            
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
            
            layer = "Layer 6 (组合优化层)"  # 默认
            for keyword, layer_name in layer_mapping.items():
                if keyword in filename:
                    layer = layer_name
                    break
            
            # 添加layer字段
            yaml_content += f"\nlayer: \"{layer}\""
            
            # 重新构建文档
            rest_content = content[yaml_match.end():]
            content = f"---\n{yaml_content}\n---\n" + rest_content
            changes.append(f"添加Layer定位: {layer}")
    
    # 3. 保存文件
    if changes:
        try:
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            return {"status": "success", "changes": changes}
        except Exception as e:
            return {"status": "failed", "reason": str(e)}
    
    return {"status": "no_change", "reason": "无需修复"}


def main():
    """主函数"""
    print("="*80)
    print("全面修复双重YAML头部和Layer定位")
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
        result = fix_document(filepath)
        
        if result["status"] == "success":
            stats["success"] += 1
            print(f"✅ {filepath.name}: {', '.join(result['changes'])}")
        elif result["status"] == "no_change":
            stats["no_change"] += 1
        else:
            stats["failed"] += 1
            print(f"❌ {filepath.name}: {result['reason']}")
    
    print("\n" + "="*80)
    print("修复完成")
    print("="*80)
    print(f"总文档数: {stats['total']}")
    print(f"修复成功: {stats['success']}")
    print(f"无需修复: {stats['no_change']}")
    print(f"修复失败: {stats['failed']}")


if __name__ == "__main__":
    main()
