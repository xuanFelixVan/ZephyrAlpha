#!/usr/bin/env python3
"""批量修复双YAML frontmatter问题（v2 - 处理BOM字符）

问题场景：
- 文件包含BOM字符(\ufeff)导致第二个YAML块被误判
- 第一个frontmatter后跟着BOM+换行+第二个frontmatter

修复策略：
1. 检测真正的双YAML（BOM导致的）
2. 合并两个frontmatter块
3. 保留第一个为主，第二个的额外字段合并进来
4. 移除BOM字符

使用：
    python scripts/batch_fix_double_yaml_v2.py --dry-run  # 预览
    python scripts/batch_fix_double_yaml_v2.py --apply   # 执行修复
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"

# 匹配YAML frontmatter的正则（处理BOM字符）
FM_PATTERN = re.compile(r"^\ufeff?---\s*\n(.*?)\n---\s*\n", re.DOTALL)
YAML_KV_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*\s*:", re.MULTILINE)


def parse_frontmatter(text: str) -> Tuple[Optional[str], str]:
    """解析frontmatter，返回(frontmatter内容, 剩余内容)"""
    match = FM_PATTERN.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end():]


def has_yaml_content(text: str) -> bool:
    """检查文本是否包含YAML键值对"""
    return bool(YAML_KV_PATTERN.search(text))


def is_double_yaml(content: str) -> bool:
    """检测是否真正的双YAML问题"""
    # 解析第一个frontmatter
    first_fm, after_first = parse_frontmatter(content)
    if first_fm is None:
        return False
    
    # 跳过空白字符（包括BOM）
    after_first_stripped = after_first.lstrip('\n\r\ufeff ')
    
    # 检查第二个frontmatter
    second_match = FM_PATTERN.match(after_first_stripped)
    if not second_match:
        return False
    
    # 验证第二个块包含YAML内容
    second_fm = second_match.group(1)
    return has_yaml_content(second_fm)


def merge_frontmatters(first: str, second: str) -> str:
    """合并两个frontmatter，第一个为主，补充第二个的额外字段"""
    # 解析为字典
    first_dict = parse_yaml_simple(first)
    second_dict = parse_yaml_simple(second)
    
    # 合并：second中的额外字段补充到first
    merged = dict(first_dict)
    for key, value in second_dict.items():
        if key not in merged:
            merged[key] = value
    
    # 格式化为YAML
    return format_frontmatter(merged)


def parse_yaml_simple(text: str) -> Dict[str, str]:
    """简易YAML解析（单层键值对）"""
    result = {}
    current_key = None
    current_list = []
    
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        
        # 列表项
        if stripped.startswith('- ') and current_key:
            current_list.append(stripped[2:].strip())
            continue
        
        # 保存上一个列表
        if current_key and current_list:
            result[current_key] = current_list
            current_list = []
            current_key = None
        
        # 键值对
        if ':' in stripped and not stripped.startswith('#'):
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            if value:
                # 去掉引号
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                result[key] = value
            else:
                current_key = key
                current_list = []
    
    # 保存最后一个列表
    if current_key and current_list:
        result[current_key] = current_list
    
    return result


def format_frontmatter(fm: Dict) -> str:
    """格式化为YAML frontmatter"""
    lines = ['---']
    for key, value in fm.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            # 转义特殊字符
            if value and (':' in str(value) or '#' in str(value) or '\n' in str(value)):
                value = f'"{value}"'
            lines.append(f"{key}: {value}")
    lines.append('---')
    return '\n'.join(lines)


def fix_file(file_path: Path, dry_run: bool = True) -> Tuple[bool, str]:
    """修复单个文件，返回(是否修复, 消息)"""
    try:
        # 读取原始内容
        raw = file_path.read_bytes()
        has_bom = raw[:3] == b'\xef\xbb\xbf'
        content = raw.decode('utf-8-sig')
        
        # 检查是否双YAML
        if not is_double_yaml(content):
            return False, "非双YAML问题"
        
        # 解析两个frontmatter
        first_fm, after_first = parse_frontmatter(content)
        after_first_stripped = after_first.lstrip('\n\r\ufeff ')
        second_match = FM_PATTERN.match(after_first_stripped)
        second_fm = second_match.group(1) if second_match else ""
        body = after_first_stripped[second_match.end():] if second_match else after_first_stripped
        
        # 合并
        merged_fm = merge_frontmatters(first_fm, second_fm)
        
        # 组装新内容
        new_content = merged_fm + '\n' + body
        
        if dry_run:
            return True, "可修复（预览模式）"
        
        # 写入（不添加BOM）
        file_path.write_text(new_content, encoding='utf-8')
        return True, "已修复"
        
    except Exception as e:
        return False, f"错误: {e}"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='批量修复双YAML frontmatter')
    parser.add_argument('--dry-run', action='store_true', help='预览模式（不实际修改）')
    parser.add_argument('--apply', action='store_true', help='执行修复')
    parser.add_argument('--path', type=str, default=str(DOCS_ROOT), help='docs目录路径')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.apply:
        print("请指定 --dry-run 或 --apply")
        sys.exit(1)
    
    docs_root = Path(args.path)
    md_files = list(docs_root.rglob('*.md'))
    
    print(f"扫描 {len(md_files)} 个 .md 文件...")
    print("-" * 70)
    
    fixable = []
    errors = []
    
    for f in md_files:
        fixed, msg = fix_file(f, dry_run=not args.apply)
        if fixed:
            fixable.append((f, msg))
            rel = f.relative_to(docs_root.parent)
            print(f"{'[预览]' if args.dry_run else '[修复]'} {rel}: {msg}")
        elif "错误" in msg:
            errors.append((f, msg))
    
    print("-" * 70)
    print(f"总计: {len(fixable)} 个文件可修复")
    
    if errors:
        print(f"错误: {len(errors)} 个文件")
    
    if args.dry_run and fixable:
        print(f"\n运行以下命令执行修复:")
        print(f"  python {__file__} --apply")


if __name__ == '__main__':
    main()
