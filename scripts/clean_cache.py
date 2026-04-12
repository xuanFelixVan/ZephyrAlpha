#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
清风量化系统 - 自动化缓存清理脚本

功能: 清理项目中的各种缓存文件、测试文件、临时文件
版本: v1.0
创建日期: 2026-04-01
维护者: Audit Sentinel

使用方法:
    python scripts/clean_cache.py [--dry-run] [--verbose] [--all]

参数:
    --dry-run    : 只显示要清理的文件，不实际删除
    --verbose    : 显示详细输出
    --all        : 清理所有缓存（包括可能需要保留的）
    --help       : 显示帮助信息

清理规则基于 .gitignore 文件配置
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import List, Tuple, Set

class CacheCleaner:
    """缓存清理器"""
    
    def __init__(self, project_root: Path, dry_run: bool = False, verbose: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.cleaned_files = []
        self.cleaned_dirs = []
        self.failed_items = []
        
        # 从 .gitignore 读取忽略模式
        self.ignore_patterns = self._load_gitignore_patterns()
        
    def _load_gitignore_patterns(self) -> List[str]:
        """从 .gitignore 加载忽略模式"""
        gitignore_path = self.project_root / ".gitignore"
        patterns = []
        
        if not gitignore_path.exists():
            print(f"警告: {gitignore_path} 不存在，使用默认模式")
            return self._get_default_patterns()
        
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                patterns.append(line)
        
        print(f"从 .gitignore 加载了 {len(patterns)} 个忽略模式")
        return patterns
    
    def _get_default_patterns(self) -> List[str]:
        """默认的清理模式（当 .gitignore 不存在时使用）"""
        return [
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            "*.so",
            ".Python",
            "build/",
            "develop-eggs/",
            "dist/",
            "downloads/",
            "eggs/",
            ".eggs/",
            "lib/",
            "lib64/",
            "parts/",
            "sdist/",
            "var/",
            "wheels/",
            "*.egg-info/",
            ".installed.cfg",
            "*.egg",
            "venv/",
            "ENV/",
            "env/",
            ".venv/",
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            "*~",
            ".pytest_cache/",
            ".mypy_cache/",
            ".coverage",
            ".coverage.*",
            "htmlcov/",
            ".tox/",
            ".pylint.d/",
            ".flake8",
            ".mccabe",
            "*.cache",
            ".cache/",
            ".ipynb_checkpoints/",
            "*.ipynb_checkpoints/",
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.log.*",
        ]
    
    def _should_clean(self, path: Path, pattern: str) -> bool:
        """检查路径是否匹配清理模式"""
        # 将模式转换为正则表达式（简化版本）
        if pattern.endswith('/'):
            # 目录模式
            dir_pattern = pattern.rstrip('/')
            if dir_pattern in str(path) or dir_pattern in path.name:
                return True
        elif '*' in pattern:
            # 通配符模式
            import fnmatch
            if fnmatch.fnmatch(path.name, pattern):
                return True
        else:
            # 精确匹配
            if path.name == pattern or pattern in str(path):
                return True
        return False
    
    def _safe_remove(self, path: Path) -> Tuple[bool, str]:
        """安全删除文件或目录"""
        try:
            if path.is_file():
                if not self.dry_run:
                    path.unlink()
                self.cleaned_files.append(str(path))
                return True, f"文件: {path}"
            elif path.is_dir():
                if not self.dry_run:
                    shutil.rmtree(path)
                self.cleaned_dirs.append(str(path))
                return True, f"目录: {path}"
            else:
                return False, f"不存在: {path}"
        except Exception as e:
            self.failed_items.append(str(path))
            return False, f"错误: {path} - {e}"
    
    def clean_project(self, clean_all: bool = False):
        """清理整个项目"""
        print(f"{'[干运行] ' if self.dry_run else ''}开始清理项目缓存...")
        print(f"项目根目录: {self.project_root}")
        print(f"使用模式数: {len(self.ignore_patterns)}")
        print("-" * 60)
        
        # 要保留的目录（即使匹配模式也不清理）
        preserve_dirs = [
            ".trae",        # Trae IDE 工作区
            "data",         # 数据目录（部分子目录在.gitignore中指定）
            "docs/00_RESOURCES",  # 外部文档资源
        ]
        
        # 遍历项目目录
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            root_path = Path(root)
            
            # 检查是否在保留目录中
            skip_clean = False
            for preserve in preserve_dirs:
                if preserve in str(root_path):
                    if not clean_all:  # 如果指定了--all，则清理所有
                        skip_clean = True
                        if self.verbose:
                            print(f"跳过保留目录: {root_path}")
                    break
            
            if skip_clean:
                continue
            
            # 处理文件
            for file in files:
                file_path = root_path / file
                for pattern in self.ignore_patterns:
                    if self._should_clean(file_path, pattern):
                        success, msg = self._safe_remove(file_path)
                        if self.verbose or not success:
                            status = "跳过" if self.dry_run else ("成功" if success else "失败")
                            print(f"{status}: {msg}")
                        break
            
            # 处理目录
            for dir_name in dirs:
                dir_path = root_path / dir_name
                for pattern in self.ignore_patterns:
                    if self._should_clean(dir_path, pattern):
                        success, msg = self._safe_remove(dir_path)
                        if self.verbose or not success:
                            status = "跳过" if self.dry_run else ("成功" if success else "失败")
                            print(f"{status}: {msg}")
                        break
        
        # 打印统计信息
        print("-" * 60)
        print("清理完成!")
        
        if self.dry_run:
            print(f"[干运行] 将清理 {len(self.cleaned_files)} 个文件和 {len(self.cleaned_dirs)} 个目录")
            if self.cleaned_files:
                print("文件列表:")
                for f in sorted(self.cleaned_files)[:10]:  # 只显示前10个
                    print(f"  - {f}")
                if len(self.cleaned_files) > 10:
                    print(f"  ... 和其他 {len(self.cleaned_files) - 10} 个文件")
            if self.cleaned_dirs:
                print("目录列表:")
                for d in sorted(self.cleaned_dirs)[:10]:
                    print(f"  - {d}")
                if len(self.cleaned_dirs) > 10:
                    print(f"  ... 和其他 {len(self.cleaned_dirs) - 10} 个目录")
        else:
            print(f"已清理 {len(self.cleaned_files)} 个文件和 {len(self.cleaned_dirs)} 个目录")
            
            # 计算释放的空间（估算）
            total_size = 0
            for f in self.cleaned_files:
                try:
                    total_size += os.path.getsize(f)
                except:
                    pass
            
            for d in self.cleaned_dirs:
                try:
                    for root, dirs, files in os.walk(d):
                        for file in files:
                            try:
                                total_size += os.path.getsize(os.path.join(root, file))
                            except:
                                pass
                except:
                    pass
            
            if total_size > 0:
                size_mb = total_size / (1024 * 1024)
                print(f"释放空间: {size_mb:.2f} MB")
        
        if self.failed_items:
            print(f"失败项目: {len(self.failed_items)} 个")
            if self.verbose:
                for item in self.failed_items:
                    print(f"  - {item}")
        
        # 提示信息
        if not self.dry_run:
            print("\n提示:")
            print("1. 可以使用 'git status' 查看清理后的变化")
            print("2. 可以使用 'git clean -n' 查看git建议清理的文件")
            print("3. 定期运行此脚本可保持项目整洁")
        
        return len(self.cleaned_files) + len(self.cleaned_dirs)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="清风量化系统 - 自动化缓存清理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
    # 干运行（只显示将要清理的文件）
    python scripts/clean_cache.py --dry-run --verbose
    
    # 实际清理
    python scripts/clean_cache.py
    
    # 清理所有缓存（包括通常保留的目录）
    python scripts/clean_cache.py --all
    
    # 详细输出
    python scripts/clean_cache.py --verbose
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示要清理的文件，不实际删除"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="清理所有缓存（包括可能需要保留的目录）"
    )
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 创建清理器并执行清理
    cleaner = CacheCleaner(
        project_root=project_root,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    try:
        cleaned_count = cleaner.clean_project(clean_all=args.all)
        
        if args.dry_run and cleaned_count > 0:
            print(f"\n要执行清理，请移除 --dry-run 参数运行:")
            print(f"  python scripts/clean_cache.py")
        elif cleaned_count == 0 and not args.all:
            print("\n没有找到需要清理的缓存文件。")
            print("要查看更多可能清理的文件，请使用 --all 参数")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n用户中断清理操作")
        return 1
    except Exception as e:
        print(f"清理过程中发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())