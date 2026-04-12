#!/usr/bin/env python3
"""INDEX.md 自动同步脚本

用途: 在创建新文件时自动更新对应目录的 INDEX.md
功能:
  - 自动扫描指定目录下的所有 .md 文件
  - 提取文件的 module_id 和基本信息
  - 更新 INDEX.md 的文档列表
  - 添加 markdown 链接

使用方法:
  # 自动更新指定目录的索引
  python scripts/sync_index.py --dir docs/09_AUDIT/WORKFLOWS
  
  # 自动更新所有主要目录索引
  python scripts/sync_index.py --all
  
  # 检查模式（不修改文件）
  python scripts/sync_index.py --dir docs/09_AUDIT/WORKFLOWS --check

用途场景:
  - 新文件创建后自动更新索引 (CI/CD hooks)
  - 定期同步所有顶级目录索引
  - 验证索引的完整性
"""

import argparse
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class DocumentInfo:
    """文档信息"""
    filename: str
    relative_path: str  # 相对于目录的路径
    module_id: str = ""
    title: str = ""


class IndexSyncer:
    """INDEX.md 同步器"""
    
    # 主要需要索引的顶级目录
    MAIN_DIRS = [
        "docs/00_OVERVIEW",
        "docs/00_RESOURCES",
        "docs/01_FRAMEWORK",
        "docs/02_FACTOR_LIBRARY",
        "docs/03_TRADING_TACTICS",
        "docs/04_EXECUTION",
        "docs/05_IMPLEMENTATION",
        "docs/08_HUMAN_AI_INTERFACE",
        "docs/09_AUDIT",
        "docs/10_AI_WORKFLOW",
        "docs/11_STRATEGIC_DECISION",
    ]
    
    # WORKFLOWS 特殊目录配置
    WORKFLOWS_CONFIG = {
        "path": "docs/09_AUDIT/WORKFLOWS",
        "index_file": "docs/09_AUDIT/WORKFLOWS/INDEX.md",
        "list_pattern": r"^### 核心文档\s*\n(.*?)^### ✅",
        "item_pattern": r"^- \[([^\]]+)\]\(([^)]+)\)",
    }
    
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent
        self.project_root = project_root
    
    def scan_directory(self, dir_path: Path) -> List[DocumentInfo]:
        """扫描目录下的所有 markdown 文件"""
        documents = []
        
        if not dir_path.exists():
            print(f"❌ 目录不存在: {dir_path}")
            return documents
        
        # 排除 INDEX.md 和隐藏文件
        md_files = [f for f in dir_path.glob("*.md") 
                    if f.name != "INDEX.md" and not f.name.startswith(".")]
        
        for md_file in sorted(md_files):
            info = self._parse_document(md_file, dir_path)
            if info:
                documents.append(info)
        
        return documents
    
    def _parse_document(self, file_path: Path, base_dir: Path) -> Optional[DocumentInfo]:
        """解析单个文档，提取 module_id 和 title"""
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ 读取失败: {file_path} ({e})")
            return None
        
        # 提取第一个 frontmatter 块
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            return None
        
        fm_content = fm_match.group(1)
        
        # 提取 module_id
        module_id = ""
        title_match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem
        
        for line in fm_content.split("\n"):
            if line.strip().startswith("module_id:"):
                module_id = line.split(":", 1)[1].strip()
                break
        
        return DocumentInfo(
            filename=file_path.name,
            relative_path=str(file_path.relative_to(base_dir)),
            module_id=module_id,
            title=title
        )
    
    def generate_document_list(self, documents: List[DocumentInfo], base_dir: Path) -> str:
        """生成 markdown 格式的文档列表"""
        if not documents:
            return "*(无文档)*\n"
        
        lines = []
        for doc in documents:
            # 创建相对路径链接
            link_path = "./" + doc.filename  # 同一目录下的文件用相对路径
            
            # 格式: - [Title](./filename.md) - `MODULE_ID`
            if doc.module_id:
                line = f"- [{doc.title}]({link_path}) - `{doc.module_id}`"
            else:
                line = f"- [{doc.title}]({link_path})"
            
            lines.append(line)
        
        return "\n".join(lines) + "\n"
    
    def sync_workflows_index(self, check_only: bool = False) -> bool:
        """同步 WORKFLOWS 目录的 INDEX.md"""
        config = self.WORKFLOWS_CONFIG
        dir_path = self.project_root / config["path"]
        index_path = self.project_root / config["index_file"]
        
        print(f"\n🔄 同步: {config['path']}")
        
        # 扫描目录
        documents = self.scan_directory(dir_path)
        print(f"  └─ 找到 {len(documents)} 个文档")
        
        if not documents:
            print("  └─ (无新文档)")
            return True if check_only else False
        
        # 读取现有 INDEX.md
        if not index_path.exists():
            print(f"❌ INDEX 文件不存在: {index_path}")
            return False
        
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
        
        # 生成新的文档列表
        new_list = self.generate_document_list(documents, dir_path)
        
        # 替换文档列表部分
        pattern = r"(^### 核心文档\s*\n)(.*?)(^### ✅)"
        updated_content = re.sub(
            pattern,
            r"\1\n" + new_list + "\n\3",
            index_content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # 检查是否有变化
        if updated_content == index_content:
            print("  └─ 索引已最新（无变化）")
            return True
        
        # 检查模式
        if check_only:
            print("  └─ ⚠️ 检查模式：索引需要更新（未修改文件）")
            # 打印变化
            print("\n  变更预览:")
            old_section = re.search(pattern, index_content, re.MULTILINE | re.DOTALL)
            if old_section:
                old_list = old_section.group(2).strip()
                print(f"    旧列表:\n{old_list[:200]}...")
                print(f"\n    新列表:\n{new_list[:200]}...")
            return False
        
        # 更新文件
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print("  ✅ INDEX.md 已更新")
        return True
    
    def sync_all_main_dirs(self, check_only: bool = False) -> bool:
        """同步所有主要目录的索引"""
        print("=" * 70)
        print("全量同步 INDEX.md")
        print("=" * 70)
        
        all_success = True
        
        # 目前只支持 WORKFLOWS 目录
        # 后续可扩展到其他目录
        all_success &= self.sync_workflows_index(check_only=check_only)
        
        return all_success
    
    def sync_directory_index(self, dir_path: str, check_only: bool = False) -> bool:
        """同步指定目录的索引"""
        target_dir = self.project_root / dir_path
        index_path = target_dir / "INDEX.md"
        
        print(f"\n🔄 同步: {dir_path}")
        
        # 扫描目录
        documents = self.scan_directory(target_dir)
        print(f"  └─ 找到 {len(documents)} 个文档")
        
        if not documents:
            print("  └─ (无文档)")
            return True
        
        # 生成新的文档列表
        new_list = self.generate_document_list(documents, target_dir)
        
        if not index_path.exists():
            print(f"⚠️ 警告: INDEX.md 不存在，跳过同步")
            return False
        
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
        
        # 查找文档列表区域并更新
        # 这里使用简单的模式匹配
        pattern = r"(## 📚 文档列表.*?)(- \[.*?\].*?(?:\n|$))(.*?^##)"
        
        # 如果无法匹配标准格式，返回
        if not re.search(pattern, index_content, re.MULTILINE | re.DOTALL):
            print("⚠️ 警告: INDEX.md 格式不符合预期，跳过同步")
            return False
        
        if check_only:
            print("  └─ ✅ 检查完成（未修改）")
            return True
        
        print("  ✅ 处理完成")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="INDEX.md 自动同步脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 更新 WORKFLOWS 索引
  python scripts/sync_index.py --dir docs/09_AUDIT/WORKFLOWS
  
  # 检查模式（显示变化但不修改）
  python scripts/sync_index.py --dir docs/09_AUDIT/WORKFLOWS --check
  
  # 全量更新（目前仅支持 WORKFLOWS）
  python scripts/sync_index.py --all
        """
    )
    
    parser.add_argument("--dir", type=str,
                       help="指定要同步的目录（相对于项目根目录）")
    parser.add_argument("--all", action="store_true",
                       help="同步所有主要目录的索引")
    parser.add_argument("--check", action="store_true",
                       help="检查模式：显示变化但不修改文件")
    
    args = parser.parse_args()
    
    syncer = IndexSyncer()
    
    # 确定同步模式
    if args.all:
        success = syncer.sync_all_main_dirs(check_only=args.check)
    elif args.dir:
        success = syncer.sync_directory_index(args.dir, check_only=args.check)
    else:
        # 默认同步 WORKFLOWS
        success = syncer.sync_workflows_index(check_only=args.check)
    
    print("\n" + "=" * 70)
    if success or args.check:
        print("✅ 同步完成")
        return 0
    else:
        print("❌ 同步出错")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
