#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
深层目录扁平化脚本。

扫描 docs/ 目录，识别嵌套深度超过阈值的目录，并提出合并/上移建议。
根据文档仓库布局标准 §2～§4 与分类决策矩阵（附录 A）决定目标路径。

用法：
    python scripts/flatten_deep_directories.py --dry-run
    python scripts/flatten_deep_directories.py --execute --threshold 4
    python scripts/flatten_deep_directories.py --report --output deep_directories_report.json

参数：
    --dry-run           只显示分析结果，不执行任何移动（默认）
    --execute           实际执行目录移动（危险！请先 dry-run）
    --threshold N       深度阈值，默认 3（即深度 > 3 的目录视为深层目录）
    --report            生成 JSON 报告文件
    --output FILE       报告文件路径（默认 deep_directories_report.json）
    --docs-root PATH    docs 根目录（默认 'docs'）
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Tuple

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def calculate_depth(path: Path, base: Path) -> int:
    """计算相对于基目录的嵌套深度。"""
    try:
        relative = path.relative_to(base)
        # 将路径拆分为部分，过滤空字符串
        parts = [p for p in relative.parts if p]
        return len(parts)
    except ValueError:
        # 如果路径不在基目录下，返回0（不应该发生）
        return 0


def scan_deep_directories(docs_root: Path, threshold: int) -> List[Dict]:
    """扫描深层目录，返回目录信息列表。"""
    deep_dirs = []
    for dirpath, dirnames, filenames in os.walk(docs_root):
        dirpath = Path(dirpath)
        depth = calculate_depth(dirpath, docs_root)
        if depth > threshold:
            # 统计目录中的文件数量（不包括子目录）
            file_count = len(filenames)
            # 子目录数量
            subdir_count = len(dirnames)
            # 判断是否为稀疏目录（文件数 <= 2）
            sparse = file_count <= 2
            deep_dirs.append({
                'path': str(dirpath),
                'depth': depth,
                'file_count': file_count,
                'subdir_count': subdir_count,
                'sparse': sparse,
                'parent': str(dirpath.parent),
                'name': dirpath.name,
            })
    # 按深度降序排序
    deep_dirs.sort(key=lambda x: x['depth'], reverse=True)
    return deep_dirs


def suggest_flattening(deep_dir: Dict) -> Dict:
    """为深层目录生成扁平化建议。
    
    策略：
    1. 如果目录稀疏（文件数 <= 2）且没有子目录，建议合并到父目录。
    2. 如果目录有子目录但文件少，考虑上移文件，保留子目录。
    3. 否则，建议保留目录但重命名或重构。
    
    返回建议字典。
    """
    path = Path(deep_dir['path'])
    parent = path.parent
    # 简单启发式：如果稀疏且父目录不是深层目录，则合并到父目录
    if deep_dir['sparse'] and deep_dir['subdir_count'] == 0:
        target = str(parent)
        action = 'merge_into_parent'
        reason = f"稀疏目录（{deep_dir['file_count']} 个文件），无子目录，可合并到父目录"
    else:
        # 暂时建议保留，但记录为需要人工评审
        target = None
        action = 'review_manually'
        reason = f"目录有 {deep_dir['file_count']} 个文件和 {deep_dir['subdir_count']} 个子目录，需人工决定是否扁平化"
    
    return {
        'original_path': deep_dir['path'],
        'suggested_action': action,
        'target_path': target,
        'reason': reason,
        'depth': deep_dir['depth'],
        'file_count': deep_dir['file_count'],
        'subdir_count': deep_dir['subdir_count'],
    }


def move_directory(src: Path, dst_parent: Path, dry_run: bool = True) -> bool:
    """将目录内的文件移动到目标父目录，然后删除空目录。
    
    保留 Git 历史（如果文件已被跟踪）。
    """
    if not src.is_dir():
        logger.error(f"源目录不存在：{src}")
        return False
    if dst_parent.is_file():
        logger.error(f"目标父目录是文件：{dst_parent}")
        return False
    # 确保目标父目录存在
    dst_parent.mkdir(parents=True, exist_ok=True)
    
    moved_files = []
    for item in src.iterdir():
        dst = dst_parent / item.name
        if dry_run:
            logger.info(f"[dry-run] 将 {item} 移动到 {dst}")
            moved_files.append(str(item))
        else:
            try:
                # 使用 shutil.move 处理跨设备移动
                shutil.move(str(item), str(dst))
                moved_files.append(str(item))
                logger.info(f"移动 {item} -> {dst}")
            except Exception as e:
                logger.error(f"移动 {item} 失败：{e}")
                return False
    # 如果目录已空，尝试删除
    if not any(src.iterdir()):
        try:
            if not dry_run:
                src.rmdir()
                logger.info(f"删除空目录 {src}")
            else:
                logger.info(f"[dry-run] 删除空目录 {src}")
        except OSError as e:
            logger.warning(f"无法删除目录 {src}：{e}")
    return True


def main():
    parser = argparse.ArgumentParser(description='深层目录扁平化工具')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='只显示分析结果，不执行移动（默认）')
    parser.add_argument('--execute', action='store_true',
                        help='实际执行目录移动（危险！请先 dry-run）')
    parser.add_argument('--threshold', type=int, default=3,
                        help='深度阈值，深度 > 阈值的目录视为深层目录（默认 3）')
    parser.add_argument('--report', action='store_true',
                        help='生成 JSON 报告文件')
    parser.add_argument('--output', type=str, default='deep_directories_report.json',
                        help='报告文件路径（默认 deep_directories_report.json）')
    parser.add_argument('--docs-root', type=str, default='docs',
                        help='docs 根目录（默认 docs）')
    args = parser.parse_args()

    if args.execute:
        args.dry_run = False
        logger.warning("执行模式已启用，将实际移动文件和目录！")
        confirm = input("确认执行？(yes/no): ")
        if confirm.lower() != 'yes':
            logger.info("取消执行。")
            sys.exit(0)
    else:
        logger.info("干燥运行模式（不实际移动文件）。")

    docs_root = Path(args.docs_root)
    if not docs_root.is_dir():
        logger.error(f"docs 根目录不存在：{docs_root}")
        sys.exit(1)

    logger.info(f"扫描深层目录（阈值深度 > {args.threshold}）...")
    deep_dirs = scan_deep_directories(docs_root, args.threshold)
    logger.info(f"发现 {len(deep_dirs)} 个深层目录。")

    suggestions = []
    for dd in deep_dirs:
        suggestion = suggest_flattening(dd)
        suggestions.append(suggestion)

    # 打印摘要
    print("\n" + "="*80)
    print("深层目录扁平化分析报告")
    print("="*80)
    for s in suggestions:
        print(f"\n目录：{s['original_path']}")
        print(f"  深度：{s['depth']}，文件数：{s['file_count']}，子目录数：{s['subdir_count']}")
        print(f"  建议操作：{s['suggested_action']}")
        print(f"  目标路径：{s['target_path'] or '无'}")
        print(f"  理由：{s['reason']}")

    # 执行移动（如果启用）
    if not args.dry_run:
        logger.info("开始执行目录扁平化...")
        for s in suggestions:
            if s['suggested_action'] == 'merge_into_parent' and s['target_path']:
                src = Path(s['original_path'])
                dst_parent = Path(s['target_path'])
                success = move_directory(src, dst_parent, dry_run=False)
                if not success:
                    logger.error(f"移动目录失败：{src}")
            else:
                logger.info(f"跳过 {s['original_path']}（建议手动评审）")
        logger.info("执行完成。")

    # 生成报告
    if args.report:
        report_data = {
            'threshold': args.threshold,
            'deep_directories_count': len(deep_dirs),
            'suggestions': suggestions,
            'executed': not args.dry_run,
        }
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        logger.info(f"报告已保存至 {output_path}")

    # 总结
    print("\n" + "="*80)
    print("总结")
    print("="*80)
    print(f"扫描目录总数：{len(deep_dirs)}")
    mergeable = sum(1 for s in suggestions if s['suggested_action'] == 'merge_into_parent')
    print(f"可合并的稀疏目录：{mergeable}")
    print(f"需人工评审的目录：{len(suggestions) - mergeable}")
    if args.dry_run:
        print("\n本次为干燥运行，未实际移动文件。")
        print("若要执行移动，请使用 --execute 参数（务必先备份）。")
    else:
        print("\n已执行目录扁平化操作。")
    print("="*80)


if __name__ == '__main__':
    main()