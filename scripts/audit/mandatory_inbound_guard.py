#!/usr/bin/env python3
"""
强制入链守卫 (Mandatory Inbound Guard)
Pre-commit钩子 - 检查新文件是否有入链

任何没有入链的新文件将被自动拒绝或自动挂载到索引

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
from typing import List, Set, Dict

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
REPO_ROOT = Path(__file__).resolve().parent.parent


class MandatoryInboundGuard:
    """强制入链守卫 - Pre-commit检查"""
    
    def __init__(self):
        self.orphans = []
        self.auto_mounted = []
        self.failed = []
    
    def extract_yaml_layer(self, content: str) -> str:
        """从文件YAML头部提取layer字段"""
        match = re.search(r'layer:\s*(.+?)(?:\n|$)', content)
        if match:
            return match.group(1).strip()
        return None
    
    def contains_link_to_file(self, source_file: Path, target_file: Path) -> bool:
        """检查source_file是否包含指向target_file的链接"""
        try:
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 获取target相对于source的路径
            try:
                target_rel = target_file.relative_to(source_file.parent)
            except ValueError:
                # 可能需要使用绝对路径
                target_rel = target_file.relative_to(DOCS_DIR)
            
            # 多种可能的链接格式
            patterns = [
                re.escape(f"./{target_file.name}"),
                re.escape(f"../{target_file.name}"),
                re.escape(str(target_rel).replace('\\', '/')),
                re.escape(target_file.stem),
            ]
            
            for pattern in patterns:
                if re.search(rf'\[([^\]]+)\]\({pattern}', content):
                    return True
                if re.search(rf'\[([^\]]+)\]\({pattern}#', content):
                    return True
            
            return False
        except Exception:
            return False
    
    def find_inbound_links(self, target_file: Path) -> List[Dict]:
        """找到所有链接到target_file的文件"""
        inbound = []
        
        for md_file in DOCS_DIR.rglob("*.md"):
            if md_file == target_file:
                continue
            
            if self.contains_link_to_file(md_file, target_file):
                inbound.append({
                    'source': str(md_file.relative_to(DOCS_DIR)).replace('\\', '/'),
                    'file': md_file
                })
        
        return inbound
    
    def auto_mount_to_index(self, md_file: Path) -> bool:
        """自动将文件挂载到相应的INDEX"""
        try:
            # 提取layer
            with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(500)
            
            layer = self.extract_yaml_layer(content)
            if not layer:
                return False
            
            # 寻找对应层的INDEX文件
            possible_indexes = list(DOCS_DIR.rglob(f"{layer}/INDEX.md"))
            
            if not possible_indexes:
                # 尝试其他方式找INDEX
                possible_indexes = list(DOCS_DIR.glob(f"*/INDEX.md"))
                if not possible_indexes:
                    return False
            
            index_file = possible_indexes[0]
            
            # 读取INDEX内容
            with open(index_file, 'r', encoding='utf-8', errors='ignore') as f:
                index_content = f.read()
            
            # 检查是否已经包含该文件
            file_link = f"./{md_file.name}"
            if file_link in index_content or md_file.stem in index_content:
                return True
            
            # 在"文档列表"部分添加该文件
            link_entry = f"- [{md_file.stem}]({file_link})\n"
            
            # 寻找合适的插入位置（在## 文档列表之后）
            if "## 文档列表" in index_content:
                insert_pattern = r"(## 文档列表\n+)"
                index_content = re.sub(
                    insert_pattern,
                    r"\1" + link_entry,
                    index_content,
                    count=1
                )
            else:
                # 如果没有"## 文档列表"，在末尾添加
                index_content += f"\n\n## 新增文件\n\n{link_entry}"
            
            # 写回INDEX文件
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            return True
        
        except Exception as e:
            print(f"⚠️  自动挂载失败 {md_file}: {e}", file=sys.stderr)
            return False
    
    def check_staged_files(self, staged_files: List[str]) -> Tuple[bool, Dict]:
        """
        检查暂存文件是否有入链
        
        Args:
            staged_files: git的暂存文件列表
        
        Returns:
            (是否通过检查, 详细报告dict)
        """
        report = {
            'checked': 0,
            'has_inbound': 0,
            'orphans': [],
            'auto_mounted': [],
            'failed': []
        }
        
        # 转换为Path对象
        md_files = []
        for file_str in staged_files:
            file_path = REPO_ROOT / file_str
            if file_path.suffix.lower() == '.md' and 'docs' in str(file_path):
                md_files.append(file_path)
        
        if not md_files:
            return True, report
        
        print("=" * 70)
        print("强制入链守卫 (Mandatory Inbound Guard)")
        print("=" * 70)
        print(f"检查暂存文件: {len(md_files)} 个Markdown文件")
        print()
        
        for md_file in md_files:
            report['checked'] += 1
            
            # 跳过INDEX文件
            if md_file.name == 'INDEX.md':
                report['has_inbound'] += 1
                print(f"✅ {md_file.relative_to(REPO_ROOT)} (INDEX文件，跳过)")
                continue
            
            # 检查入链
            inbound = self.find_inbound_links(md_file)
            
            if inbound:
                report['has_inbound'] += 1
                sources = ', '.join([ib['source'] for ib in inbound])
                print(f"✅ {md_file.relative_to(REPO_ROOT)}")
                print(f"   链接源: {sources}")
            else:
                print(f"⚠️  {md_file.relative_to(REPO_ROOT)} - 无入链，尝试自动挂载...")
                
                # 尝试自动挂载
                if self.auto_mount_to_index(md_file):
                    self.auto_mounted.append(str(md_file))
                    report['auto_mounted'].append(str(md_file.relative_to(REPO_ROOT)))
                    print(f"   ✅ 自动挂载成功")
                else:
                    self.failed.append(str(md_file))
                    report['failed'].append(str(md_file.relative_to(REPO_ROOT)))
                    print(f"   ❌ 自动挂载失败 - 禁止提交")
        
        print()
        print("=" * 70)
        print("检查结果汇总")
        print("=" * 70)
        print(f"检查数量: {report['checked']}")
        print(f"有入链: {report['has_inbound']}")
        print(f"自动挂载: {len(report['auto_mounted'])}")
        print(f"检查失败: {len(report['failed'])}")
        
        if report['failed']:
            print()
            print("❌ 以下文件无法自动挂载，禁止提交:")
            for f in report['failed']:
                print(f"  - {f}")
        
        if report['auto_mounted']:
            print()
            print("⚠️  以下文件已自动挂载，请review:")
            for f in report['auto_mounted']:
                print(f"  - {f}")
        
        print()
        
        # 返回检查结果 (失败情况下返回False)
        passed = len(report['failed']) == 0
        return passed, report


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='强制入链守卫 (Pre-commit钩子)')
    parser.add_argument('files', nargs='*', default=[],
                        help='要检查的文件列表')
    parser.add_argument('--check-only', action='store_true',
                        help='仅检查，不自动挂载')
    parser.add_argument('--report', type=str,
                        help='输出报告文件')
    
    args = parser.parse_args()
    
    guard = MandatoryInboundGuard()
    passed, report = guard.check_staged_files(args.files)
    
    # 输出报告
    if args.report:
        output_path = Path(args.report)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 报告已保存: {output_path}")
    
    # 返回状态码
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
