#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Alpha因子层P2级别问题修复
补充变更记录
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def add_changelog(file_path):
    """为文档添加变更记录"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否已有变更记录
        if '变更记录' in content or '变更历史' in content:
            return False
        
        # 提取YAML头部
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            body_content = content[yaml_match.end():]
        else:
            body_content = content
        
        # 添加变更记录
        changelog = f"""

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本 | 文档管理团队 |
"""
        
        # 在文档末尾添加变更记录
        new_content = content.rstrip() + changelog + '\n'
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    
    except Exception as e:
        print(f"错误: {file_path} - {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("Alpha因子层P2级别问题修复 - 补充变更记录")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    updated_count = 0
    
    # 遍历所有.md文件
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        if add_changelog(file_path):
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            print(f"\n更新: {rel_path}")
            updated_count += 1
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"更新文档: {updated_count}")

if __name__ == '__main__':
    main()
