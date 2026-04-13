#!/usr/bin/env python3
"""
自动索引编译器 (Auto-Index Compiler)
从文件系统自动生成索引，不依赖人工维护
防止AI幻觉导致的索引不一致

版本: 1.0.0
日期: 2026-04-13
"""

import io
import os
import sys
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Set, Tuple

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

# 排除的文件/目录名称
EXCLUDE_PATTERNS = {
    'INDEX.md',  # 不扫描已有的索引文件
    '.git',
    '.github',
    '__pycache__',
    '.DS_Store',
    'node_modules'
}

# 特定层级的INDEX路径
LAYER_INDEXES = {
    'layer_00': 'docs/00_OVERVIEW/INDEX.md',
    'layer_01': 'docs/01_FRAMEWORK/INDEX.md',
    'layer_02': 'docs/02_FACTOR_LIBRARY/INDEX.md',
    'layer_03': 'docs/03_TRADING_TACTICS/INDEX.md',
    'layer_04': 'docs/04_EXECUTION/INDEX.md',
    'layer_05': 'docs/05_IMPLEMENTATION/INDEX.md',
    'layer_06': 'docs/06_ARCHIVE/INDEX.md',
    'layer_07': 'docs/07_AI_REPORTING/INDEX.md',
    'layer_08': 'docs/08_HUMAN_AI_INTERFACE/INDEX.md',
    'layer_09': 'docs/09_AUDIT/INDEX.md',
    'layer_10': 'docs/10_GOVERNANCE_COMPLIANCE/INDEX.md',
    'layer_11': 'docs/11_STRATEGIC_DECISION/INDEX.md',
}


class IndexCompiler:
    """自动索引编译器 - 从文件系统生成索引"""
    
    def __init__(self):
        self.compiled_count = 0
        self.total_files = 0
        self.layer_structure = defaultdict(list)
        
    def extract_yaml_layer(self, content: str) -> str:
        """从文件的YAML头部提取layer字段"""
        match = re.search(r'layer:\s*(.+?)(?:\n|$)', content)
        if match:
            return match.group(1).strip()
        return None
    
    def scan_files_by_layer(self) -> Dict[str, List[Path]]:
        """按层级扫描所有文件"""
        files_by_layer = defaultdict(list)
        
        for md_file in DOCS_DIR.rglob("*.md"):
            # 排除检查
            if any(pattern in str(md_file) for pattern in EXCLUDE_PATTERNS):
                continue
            
            # 读取文件提取layer
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(500)  # 只读前500字符来提取YAML
                
                layer = self.extract_yaml_layer(content)
                if layer:
                    files_by_layer[layer].append(md_file)
                    self.total_files += 1
            except Exception as e:
                print(f"⚠️  无法读取 {md_file}: {e}")
        
        return files_by_layer
    
    def generate_index_content(self, layer: str, files: List[Path]) -> str:
        """生成标准格式的INDEX内容"""
        
        files = sorted([f for f in files if f.name != 'INDEX.md'])
        
        # 提取文件信息
        file_entries = []
        for f in files:
            rel_path = f.relative_to(DOCS_DIR)
            display_name = f.stem
            file_entries.append({
                'name': display_name,
                'path': f'./{f.name}',
                'file': f
            })
        
        # 生成markdown内容
        content = f"""---
module_id: {layer.upper()}_INDEX_AUTO
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Auto-Index Compiler
standard_type: 自动索引
applicable_scope: {layer}
compliance_level: 强制标准
priority: P0-CRITICAL
layer: {layer}
responsibility:
  - 自动生成层级索引，保证文件可索引
  - 防止AI幻觉导致的索引不一致
  - 实时维护文件目录完整性
---

# {layer.upper()} 自动索引

> ⚠️  本文件由自动索引编译器自动生成，请勿手动修改  
> 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> 文件总数: {len(file_entries)}

## 文档列表

"""
        
        # 按文件名排序添加链接
        for entry in sorted(file_entries, key=lambda x: x['name']):
            content += f"- [{entry['name']}]({entry['path']})\n"
        
        content += f"""

---

**生成信息**
- 生成时间: {datetime.now().isoformat()}
- 扫描范围: {DOCS_DIR}
- 自动化工具: Auto-Index Compiler v1.0.0
"""
        
        return content
    
    def compile_all_indexes(self, recompile: bool = True) -> Dict[str, bool]:
        """编译所有层级的索引"""
        
        print("=" * 70)
        print("自动索引编译器 (Auto-Index Compiler)")
        print("=" * 70)
        print(f"工作目录: {DOCS_DIR}")
        print(f"编译时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"重编译模式: {'开启' if recompile else '禁用'}")
        print()
        
        # Phase 1: 按层级扫描所有文件
        print("[1/3] 按层级扫描文件系统...")
        files_by_layer = self.scan_files_by_layer()
        print(f"      发现 {self.total_files} 个文件，跨越 {len(files_by_layer)} 个层级")
        print()
        
        # Phase 2: 编译每个层级的索引
        print("[2/3] 编译层级索引...")
        results = {}
        
        for layer in sorted(files_by_layer.keys()):
            files = files_by_layer[layer]
            
            # 确定索引文件路径
            if layer in LAYER_INDEXES:
                index_path = DOCS_DIR / LAYER_INDEXES[layer].replace('docs/', '')
            else:
                # 尝试在该层目录下创建INDEX.md
                layer_dir = DOCS_DIR / layer
                index_path = layer_dir / 'INDEX.md'
            
            # 确保目录存在
            index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 生成索引内容
            new_content = self.generate_index_content(layer, files)
            
            # 写入文件
            try:
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.compiled_count += 1
                results[layer] = True
                status = "✅ 编译成功"
            except Exception as e:
                results[layer] = False
                status = f"❌ 编译失败: {e}"
            
            print(f"  {status} | {layer} ({len(files)} 个文件)")
        
        print()
        
        # Phase 3: 汇总报告
        print("[3/3] 编译完成汇总")
        print(f"      成功编译: {sum(1 for v in results.values() if v)} / {len(results)} 个层级")
        print()
        
        return results
    
    def report_compilation_status(self):
        """生成编译状态报告"""
        return {
            'timestamp': datetime.now().isoformat(),
            'compiled_count': self.compiled_count,
            'total_files': self.total_files,
            'status': 'SUCCESS' if self.compiled_count > 0 else 'FAILED'
        }


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自动索引编译器')
    parser.add_argument('--recompile-all', action='store_true', 
                        help='重新编译所有索引')
    parser.add_argument('--layer', type=str,
                        help='只编译指定层级')
    parser.add_argument('--output', type=str,
                        help='输出报告文件')
    
    args = parser.parse_args()
    
    compiler = IndexCompiler()
    results = compiler.compile_all_indexes(recompile=args.recompile_all or True)
    
    # 输出报告
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = compiler.report_compilation_status()
        report['results'] = {k: ('SUCCESS' if v else 'FAILED') for k, v in results.items()}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 报告已保存: {output_path}")
    
    print("\n" + "=" * 70)
    print("自动索引编译完成")
    print("=" * 70)
    
    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
