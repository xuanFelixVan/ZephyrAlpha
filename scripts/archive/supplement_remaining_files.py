#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
补充剩余未索引文件
"""

import json
import re
from pathlib import Path

def get_file_title(file_path: Path) -> str:
    """从文件中提取标题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试从YAML头部提取title
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            title_match = re.search(r'^title:\s*(.+)$', yaml_content, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip()
        
        # 尝试从第一个标题提取
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        
        # 使用文件名作为标题
        return file_path.stem.replace('_', ' ').replace('-', ' ')
        
    except Exception as e:
        return file_path.stem.replace('_', ' ').replace('-', ' ')

def add_to_index(index_file: Path, file_path: Path, docs_root: Path) -> bool:
    """将文件添加到索引中"""
    try:
        # 读取索引文件内容
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查文件是否已经在索引中
        relative_path = file_path.relative_to(index_file.parent)
        if str(relative_path) in content or f"./{relative_path}" in content:
            print(f"  ⚠️ 文件已在索引中: {file_path.name}")
            return False
        
        # 获取文件信息
        title = get_file_title(file_path)
        
        # 生成索引条目
        link_path = f"./{relative_path}"
        index_entry = f"- [{title}]({link_path})\n"
        
        # 找到合适的插入位置
        # 查找"## 📚 文档列表"或类似的章节
        section_match = re.search(r'##\s+📚?\s*文档列表', content)
        if section_match:
            # 在章节后插入
            insert_pos = section_match.end()
            content = content[:insert_pos] + '\n' + index_entry + content[insert_pos:]
        else:
            # 查找"## 📝 变更历史"之前的章节
            history_match = re.search(r'##\s+📝?\s*变更历史', content)
            if history_match:
                # 在变更历史前插入
                insert_pos = history_match.start()
                content = content[:insert_pos] + index_entry + '\n' + content[insert_pos:]
            else:
                # 在文件末尾插入
                content = content.rstrip() + '\n\n' + index_entry
        
        # 写入索引文件
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"  ❌ 添加文件 {file_path} 到索引 {index_file} 时出错: {str(e)}")
        return False

def main():
    docs_root = Path("docs")
    analysis_file = Path("scripts/smart_index_analysis.json")
    
    # 加载分析结果
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    truly_unindexed = analysis.get('truly_unindexed_files', [])
    
    print("=" * 80)
    print("补充剩余未索引文件")
    print("=" * 80)
    print(f"需要补充索引的文件数: {len(truly_unindexed)}")
    print()
    
    success_count = 0
    
    for item in truly_unindexed:
        file_path = Path(item['file'])
        category = item['category']
        
        print(f"处理: {file_path.relative_to(docs_root)} ({category})")
        
        # 找到父索引
        current_dir = file_path.parent
        index_file = None
        
        while current_dir != docs_root:
            potential_index = current_dir / 'INDEX.md'
            if potential_index.exists():
                index_file = potential_index
                break
            current_dir = current_dir.parent
        
        if not index_file:
            index_file = docs_root / 'INDEX.md'
        
        # 添加到索引
        if add_to_index(index_file, file_path, docs_root):
            success_count += 1
            print(f"  ✅ 已添加到索引: {index_file.relative_to(docs_root)}")
        
        print()
    
    print("=" * 80)
    print("补充统计")
    print("=" * 80)
    print(f"总文件数: {len(truly_unindexed)}")
    print(f"成功添加: {success_count}")
    print(f"失败: {len(truly_unindexed) - success_count}")

if __name__ == "__main__":
    main()
