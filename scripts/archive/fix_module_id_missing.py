# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
修复Module ID缺失脚本
用途：为缺少Module ID的文档添加唯一标识
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import Tuple, List
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def has_module_id(content: str) -> bool:
    return bool(re.search(r'^module_id:', content, re.MULTILINE))

def generate_module_id(file_path: Path, existing_ids: set) -> str:
    file_name = file_path.stem
    file_name = re.sub(r'[^a-zA-Z0-9_]', '_', file_name)
    file_name = re.sub(r'_+', '_', file_name)
    file_name = file_name.strip('_').upper()
    
    if not file_name:
        file_name = "MODULE"
    
    base_id = f"{file_name}_001"
    
    if base_id not in existing_ids:
        return base_id
    
    counter = 2
    while f"{file_name}_{counter:03d}" in existing_ids:
        counter += 1
    
    return f"{file_name}_{counter:03d}"

def add_module_id_to_yaml(content: str, module_id: str) -> str:
    yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    
    if not yaml_match:
        yaml_header = f"""---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 个人开发者
standard_type: 专业量化机构文档
---
"""
        return yaml_header + content
    
    yaml_content = yaml_match.group(1)
    
    if re.search(r'^module_id:', yaml_content, re.MULTILINE):
        return content
    
    if re.search(r'^---\s*$', yaml_content, re.MULTILINE):
        yaml_content = f"module_id: {module_id}\n" + yaml_content
    else:
        yaml_content = f"module_id: {module_id}\n\n" + yaml_content
    
    return f"---\n{yaml_content}\n---" + content[yaml_match.end():]

def collect_existing_module_ids() -> set:
    existing_ids = set()
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = Path(root) / file
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                module_id_match = re.search(r'^module_id:\s*(.+)$', content, re.MULTILINE)
                if module_id_match:
                    existing_ids.add(module_id_match.group(1).strip())
            except Exception:
                pass
    
    return existing_ids

def process_file(file_path: Path, existing_ids: set) -> Tuple[bool, str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_module_id(content):
            return True, "已有Module ID"
        
        module_id = generate_module_id(file_path, existing_ids)
        existing_ids.add(module_id)
        
        new_content = add_module_id_to_yaml(content, module_id)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"已添加Module ID: {module_id}"
        
    except Exception as e:
        return False, f"处理失败: {str(e)}"

def main():
    print("=" * 80)
    print("修复Module ID缺失")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"扫描目录: {DOCS_DIR}")
    print("=" * 80)
    
    print("\n收集现有Module ID...")
    existing_ids = collect_existing_module_ids()
    print(f"已收集 {len(existing_ids)} 个现有Module ID")
    
    stats = {
        "total_files": 0,
        "already_has": 0,
        "fixed": 0,
        "failed": 0
    }
    
    failed_files = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = Path(root) / file
            rel_path = file_path.relative_to(DOCS_DIR)
            
            stats["total_files"] += 1
            
            success, message = process_file(file_path, existing_ids)
            
            if success:
                if "已有" in message:
                    stats["already_has"] += 1
                else:
                    stats["fixed"] += 1
                    print(f"✓ {rel_path}: {message}")
            else:
                stats["failed"] += 1
                failed_files.append((str(rel_path), message))
                print(f"✗ {rel_path}: {message}")
    
    print("\n" + "=" * 80)
    print("处理完成")
    print("=" * 80)
    print(f"总文件数: {stats['total_files']}")
    print(f"已有Module ID: {stats['already_has']}")
    print(f"已修复: {stats['fixed']}")
    print(f"失败: {stats['failed']}")
    
    if failed_files:
        print("\n失败文件列表:")
        for file_path, message in failed_files[:10]:
            print(f"  - {file_path}: {message}")
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
