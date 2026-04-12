#!/usr/bin/env python3

# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
归档区主题归类脚本。

扫描归档目录（06_ARCHIVE, 09_ARCHIVE），根据文件名和内容关键词将文件归类到主题子目录中。

用法：
    python scripts/organize_archive.py --dry-run
    python scripts/organize_archive.py --execute --archive-root docs/06_ARCHIVE

参数：
    --dry-run           只显示分析结果，不执行移动（默认）
    --execute           实际执行文件移动（危险！请先 dry-run）
    --archive-root PATH 归档根目录（默认扫描 docs/06_ARCHIVE 和 docs/09_ARCHIVE）
    --output FILE       输出报告文件（默认 archive_organization_report.json）
    --verbose           输出详细信息
"""

import argparse
import json
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 主题映射：关键词 -> 目标子目录（相对于归档根目录）
THEME_MAPPING = {
    # 审计相关
    r'(?i)audit|审计|合规|检查|报告': 'audit_reports',
    r'(?i)report|报告|总结|汇总': 'reports',
    # 蓝图相关
    r'(?i)blueprint|蓝图|架构|设计': 'blueprints',
    # 技术规格
    r'(?i)spec|规格|技术|设计文档|technical': 'technical_specifications',
    # 因子相关
    r'(?i)factor|因子|alpha|风险|风格': 'factor_library',
    # 策略相关
    r'(?i)strategy|策略|战术|交易': 'strategy_library',
    # 数据相关
    r'(?i)data|数据|数据源|数据处理': 'data_management',
    # 实施相关
    r'(?i)implementation|实施|施工|建设|construction': 'implementation',
    # 运维相关
    r'(?i)operation|运维|监控|部署': 'operations',
    # 研究相关
    r'(?i)research|研究|实验|调研': 'research',
    # 归档重复文件
    r'(?i)duplicate|重复|副本|copy': 'duplicates',
    # 临时文件
    r'(?i)temp|临时|暂存|cache': 'temporary',
}

# 默认归档根目录列表
DEFAULT_ARCHIVE_ROOTS = ['docs/06_ARCHIVE', 'docs/09_ARCHIVE']


def detect_theme(filename: str, content_preview: str = '') -> Optional[str]:
    """根据文件名和内容预览检测主题。"""
    text = filename + ' ' + content_preview
    text_lower = text.lower()
    for pattern, theme in THEME_MAPPING.items():
        if re.search(pattern, text_lower):
            return theme
    return None


def scan_archive_files(archive_roots: List[Path]) -> List[Dict]:
    """扫描归档目录下的所有文件。"""
    all_files = []
    for root in archive_roots:
        if not root.is_dir():
            logger.warning(f"归档目录不存在：{root}")
            continue
        for filepath in root.rglob('*'):
            if filepath.is_file():
                # 跳过某些系统文件
                if filepath.name.startswith('.') or filepath.suffix in ['.tmp', '.bak']:
                    continue
                # 读取文件前几行作为内容预览（最多 200 字符）
                content_preview = ''
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content_preview = f.read(200)
                except Exception:
                    pass
                all_files.append({
                    'path': str(filepath),
                    'name': filepath.name,
                    'size': filepath.stat().st_size,
                    'relative': str(filepath.relative_to(root)),
                    'archive_root': str(root),
                    'content_preview': content_preview,
                })
    return all_files


def suggest_organization(file_info: Dict) -> Dict:
    """为单个文件生成归类建议。"""
    path = Path(file_info['path'])
    theme = detect_theme(file_info['name'], file_info['content_preview'])
    archive_root = Path(file_info['archive_root'])
    if theme:
        target_dir = archive_root / theme
        # 确保目标路径唯一（避免重复文件名）
        target_file = target_dir / path.name
        # 如果目标文件已存在，添加序号
        counter = 1
        while target_file.exists():
            stem = path.stem
            suffix = path.suffix
            new_name = f"{stem}_{counter}{suffix}"
            target_file = target_dir / new_name
            counter += 1
    else:
        target_dir = archive_root / 'unclassified'
        target_file = target_dir / path.name
    
    # 计算相对路径
    relative_target = target_file.relative_to(archive_root.parent) if archive_root.parent != Path('.') else target_file
    
    return {
        'original_path': file_info['path'],
        'original_relative': file_info['relative'],
        'suggested_theme': theme or 'unclassified',
        'target_directory': str(target_dir),
        'target_file': str(target_file),
        'relative_target': str(relative_target),
        'need_move': target_dir != path.parent,
    }


def move_file(src: Path, dst: Path, dry_run: bool = True) -> bool:
    """移动文件到目标位置，创建目录。"""
    if dry_run:
        logger.info(f"[dry-run] 移动 {src} -> {dst}")
        return True
    
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        logger.info(f"移动 {src} -> {dst}")
        return True
    except Exception as e:
        logger.error(f"移动失败：{e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='归档区主题归类')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='只显示分析结果，不执行移动（默认）')
    parser.add_argument('--execute', action='store_true',
                        help='实际执行文件移动（危险！请先 dry-run）')
    parser.add_argument('--force', action='store_true',
                        help='跳过确认，直接执行')
    parser.add_argument('--archive-root', action='append', default=[],
                        help='归档根目录（可多次指定，默认扫描 docs/06_ARCHIVE 和 docs/09_ARCHIVE）')
    parser.add_argument('--output', type=str, default='archive_organization_report.json',
                        help='输出报告文件（默认 archive_organization_report.json）')
    parser.add_argument('--verbose', action='store_true',
                        help='输出详细信息')
    args = parser.parse_args()

    if args.execute:
        args.dry_run = False
        logger.warning("执行模式已启用，将实际移动文件！")
        if not args.force:
            confirm = input("确认执行？(yes/no): ")
            if confirm.lower() != 'yes':
                logger.info("取消执行。")
                sys.exit(0)
    else:
        logger.info("干燥运行模式（不实际移动文件）。")

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 确定归档根目录
    archive_roots = []
    if args.archive_root:
        for root in args.archive_root:
            archive_roots.append(Path(root))
    else:
        for root in DEFAULT_ARCHIVE_ROOTS:
            archive_roots.append(Path(root))
    
    logger.info(f"扫描归档目录：{archive_roots}")
    files = scan_archive_files(archive_roots)
    logger.info(f"找到 {len(files)} 个文件。")

    suggestions = []
    for f in files:
        suggestion = suggest_organization(f)
        suggestions.append(suggestion)

    # 统计主题分布
    theme_counts = {}
    for s in suggestions:
        theme = s['suggested_theme']
        theme_counts[theme] = theme_counts.get(theme, 0) + 1

    # 打印分析结果
    print("\n" + "="*80)
    print("归档区主题归类分析报告")
    print("="*80)
    print(f"文件总数：{len(files)}")
    print("\n主题分布：")
    for theme, count in sorted(theme_counts.items(), key=lambda x: -x[1]):
        print(f"  {theme}: {count} 个文件")
    
    move_candidates = [s for s in suggestions if s['need_move']]
    print(f"\n需要移动的文件数：{len(move_candidates)}")
    if move_candidates and args.verbose:
        print("\n移动计划：")
        for s in move_candidates[:20]:  # 只显示前20个
            print(f"  {s['original_relative']}  ->  {s['relative_target']}")
        if len(move_candidates) > 20:
            print(f"  ... 还有 {len(move_candidates) - 20} 个文件")

    # 执行移动
    if not args.dry_run:
        logger.info("开始执行文件归类...")
        success_count = 0
        for s in move_candidates:
            src = Path(s['original_path'])
            dst = Path(s['target_file'])
            success = move_file(src, dst, dry_run=False)
            if success:
                success_count += 1
        logger.info(f"移动完成，成功 {success_count}/{len(move_candidates)} 个文件。")
    else:
        print("\n本次为干燥运行，未实际移动文件。")
        print("若要执行移动，请使用 --execute 参数（务必先备份）。")

    # 生成报告
    report_data = {
        'archive_roots': [str(r) for r in archive_roots],
        'total_files': len(files),
        'theme_distribution': theme_counts,
        'move_candidates_count': len(move_candidates),
        'suggestions': suggestions,
    }
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    logger.info(f"报告已保存至 {output_path}")

    # 总结
    print("\n" + "="*80)
    print("总结")
    print("="*80)
    print(f"扫描文件总数：{len(files)}")
    print(f"主题分类数：{len(theme_counts)}")
    print(f"需要移动的文件数：{len(move_candidates)}")
    if args.dry_run:
        print("\n干燥运行完成。")
    else:
        print("\n文件归类执行完成。")
    print("="*80)


if __name__ == '__main__':
    main()