"""
修复双重YAML头部脚本
用途：删除重复的YAML头部，保留完整的那个
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


def fix_double_yaml(filepath: Path) -> bool:
    """修复双重YAML头部"""
    content = read_document(filepath)
    if not content:
        return False
    
    # 检查是否有双重YAML头部
    # 模式：第一个YAML头部 + --- + 第二个YAML头部
    pattern = r'^---\s*\n.*?\n---\s*\n\s*---\s*\n(.*?)\n---\s*\n'
    
    match = re.match(pattern, content, re.DOTALL)
    if match:
        # 保留第二个YAML头部
        second_yaml = match.group(1)
        
        # 找到第二个YAML头部结束后的内容
        rest_start = match.end()
        rest_content = content[rest_start:]
        
        # 构建新文档
        new_content = f"---\n{second_yaml}\n---\n" + rest_content
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
        
        return True
    
    return False


def main():
    """主函数"""
    print("="*80)
    print("修复双重YAML头部")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    fixed_count = 0
    
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        if fix_double_yaml(filepath):
            fixed_count += 1
            print(f"✅ {filepath.name}")
    
    print("\n" + "="*80)
    print("完成")
    print("="*80)
    print(f"修复双重YAML头部: {fixed_count}个文档")


if __name__ == "__main__":
    main()
