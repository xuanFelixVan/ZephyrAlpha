"""
添加一级标题脚本
用途：为缺少一级标题的文档添加主标题
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


def extract_title_from_content(content: str) -> str:
    """从内容中提取标题"""
    # 尝试从第一个二级标题提取
    match = re.search(r'^##\s+(\d+\.\s+)?(.+)$', content, re.MULTILINE)
    if match:
        return match.group(2).strip()
    
    # 尝试从引用块提取
    match = re.search(r'>\s*\*\*核心定位\*\*:\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    return "蓝图文档"


def add_main_title(filepath: Path) -> bool:
    """添加一级标题"""
    content = read_document(filepath)
    if not content:
        return False
    
    # 检查是否已有一级标题
    if re.search(r'^#\s+[^#]', content, re.MULTILINE):
        return False
    
    # 提取标题
    title = extract_title_from_content(content)
    
    # 从文件名生成更友好的标题
    filename_title = filepath.stem.replace('_BLUEPRINT', '').replace('_', ' ')
    filename_title = ' '.join(word.capitalize() for word in filename_title.split())
    
    # 使用文件名标题
    if not title or title == "蓝图文档":
        title = filename_title
    
    # 找到YAML头部结束位置
    yaml_match = re.match(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
    if yaml_match:
        yaml_end = yaml_match.end()
        rest_content = content[yaml_end:]
        
        # 添加一级标题
        new_content = content[:yaml_end] + f"\n# {title}\n\n" + rest_content
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
        
        return True
    
    return False


def main():
    """主函数"""
    print("="*80)
    print("添加一级标题")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    fixed_count = 0
    
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        if add_main_title(filepath):
            fixed_count += 1
            print(f"✅ {filepath.name}")
    
    print("\n" + "="*80)
    print("完成")
    print("="*80)
    print(f"添加一级标题: {fixed_count}个文档")


if __name__ == "__main__":
    main()
