"""
修复YAML头部脚本
用途：修复格式混乱的YAML头部
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


def fix_yaml_header(filepath: Path) -> bool:
    """修复YAML头部"""
    content = read_document(filepath)
    if not content:
        return False
    
    # 提取文件名信息
    filename = filepath.stem
    
    # 从文件名生成module_id
    module_id = filename.upper()[:30] + "_001"
    
    # 推断Layer
    layer_mapping = {
        "MARGIN": "Layer 7 (风险管理层)",
        "MEAN_VARIANCE": "Layer 6 (组合优化层)",
        "OPTIMIZATION": "Layer 6 (组合优化层)",
    }
    
    layer = "Layer 6 (组合优化层)"  # 默认
    for keyword, layer_name in layer_mapping.items():
        if keyword in filename.upper():
            layer = layer_name
            break
    
    # 创建标准的YAML头部
    yaml_header = f"""---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
layer: '{layer}'
standard_type: 专业量化机构蓝图
applicable_scope: Layer 6 组合优化层
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
---
"""
    
    # 移除旧的YAML头部和混乱的内容
    # 查找第一个真正的标题（## 或 #）
    content_match = re.search(r'\n##\s+', content)
    if content_match:
        # 保留标题之后的内容
        rest_content = content[content_match.start():]
    else:
        # 如果没有找到标题，保留全部内容（移除开头的---）
        rest_content = re.sub(r'^---\s*\n', '', content)
        # 移除中间的layer行
        rest_content = re.sub(r"\nlayer:\s*['\"].*?['\"]\s*\n", '\n', rest_content)
        # 移除多余的---
        rest_content = re.sub(r'\n---\s*\n', '\n', rest_content)
    
    # 添加一级标题
    title = filename.replace('_BLUEPRINT', '').replace('_', ' ')
    title = ' '.join(word.capitalize() for word in title.split())
    
    # 构建新文档
    new_content = yaml_header + f"\n# {title}\n" + rest_content
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.write(new_content)
    
    return True


def main():
    """主函数"""
    print("="*80)
    print("修复YAML头部")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 需要修复的文档
    docs_to_fix = [
        "MARGIN_CALL_MONITOR_BLUEPRINT.md",
        "MEAN_VARIANCE_OPTIMIZATION_BLUEPRINT.md",
    ]
    
    fixed_count = 0
    
    for filename in docs_to_fix:
        filepath = BLUEPRINTS_DIR / filename
        if not filepath.exists():
            continue
        
        if fix_yaml_header(filepath):
            fixed_count += 1
            print(f"✅ {filename}")
    
    print("\n" + "="*80)
    print("完成")
    print("="*80)
    print(f"修复YAML头部: {fixed_count}个文档")


if __name__ == "__main__":
    main()
