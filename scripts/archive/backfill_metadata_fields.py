#!/usr/bin/env python3
"""为首道 YAML frontmatter 补全缺失的 module_id、layer、version、status、responsibility 字段。

用法:
  python scripts/backfill_metadata_fields.py --dry-run
  python scripts/backfill_metadata_fields.py --apply
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"

# Layer 路径映射：从文件路径推断 layer 值
LAYER_MAP = {
    "00_OVERVIEW": "layer_00",
    "01_FRAMEWORK": "layer_01",
    "02_FACTOR_LIBRARY": "layer_02",
    "03_TRADING_TACTICS": "layer_03",
    "04_EXECUTION": "layer_04",
    "05_IMPLEMENTATION": "layer_05",
    "06_ARCHIVE": "layer_06",
    "06_CONSTRUCTION_DOCS": "layer_05",
    "07_AI_REPORTING": "layer_07",
    "08_KNOWLEDGE": "layer_08",
    "09_AUDIT": "layer_09",
    "09_ARCHIVE": "layer_09",
    "09_RESEARCH_INNOVATION": "layer_09",
    "10_GOVERNANCE_COMPLIANCE": "layer_10",
    "11_STRATEGIC_DECISION": "layer_11",
    "module_designs": "layer_00",
}


def infer_layer(file_path: Path) -> str:
    """从文件路径推断 layer 值"""
    parts = file_path.relative_to(DOCS).parts
    for part in parts:
        if part in LAYER_MAP:
            return LAYER_MAP[part]
    return "layer_00"


def generate_module_id(file_path: Path) -> str:
    """基于文件路径生成唯一 module_id"""
    rel = file_path.relative_to(DOCS)
    # 将路径转为大写下划线格式
    parts = list(rel.parts)
    # 移除 .md 扩展名
    parts[-1] = parts[-1].replace('.md', '')
    # 转为大写，替换特殊字符
    module_id = '_'.join(parts).upper()
    module_id = re.sub(r'[^A-Z0-9_]', '_', module_id)
    module_id = re.sub(r'_+', '_', module_id)
    module_id = module_id.strip('_')
    # 限制长度
    if len(module_id) > 120:
        module_id = module_id[:120]
    return module_id


def parse_frontmatter(content: str) -> tuple[dict, str, int]:
    """解析首道 frontmatter，返回 (metadata, body, fm_end_pos)
    fm_end_pos 是 frontmatter 结束后的位置（包含闭合 --- 后的换行）
    """
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}, content, 0

    import yaml
    try:
        metadata = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}, content, 0

    return metadata, content[match.end():], match.end()


def build_frontmatter(metadata: dict) -> str:
    """从 metadata dict 构建 YAML frontmatter 字符串"""
    lines = ['---']
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f'{key}:')
            for item in value:
                lines.append(f'  - {item}')
        elif isinstance(value, str) and ('\n' in value or ':' in value):
            lines.append(f'{key}: "{value}"')
        else:
            lines.append(f'{key}: {value}')
    lines.append('---')
    return '\n'.join(lines) + '\n'


def process_file(file_path: Path, apply: bool = False) -> dict:
    """处理单个文件，返回变更信息"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except (UnicodeDecodeError, OSError):
        return {'path': file_path, 'status': 'error', 'reason': 'read_error'}

    metadata, body, fm_end = parse_frontmatter(content)

    if not metadata and not content.startswith('---'):
        # 无 frontmatter，需要创建
        metadata = {}

    changes = []

    # 补全 module_id
    if 'module_id' not in metadata:
        new_id = generate_module_id(file_path)
        metadata['module_id'] = new_id
        changes.append(f'+module_id: {new_id}')

    # 补全 layer
    if 'layer' not in metadata:
        new_layer = infer_layer(file_path)
        metadata['layer'] = new_layer
        changes.append(f'+layer: {new_layer}')

    # 补全 version
    if 'version' not in metadata:
        metadata['version'] = '1.0.0'
        changes.append('+version: 1.0.0')

    # 补全 status
    if 'status' not in metadata:
        metadata['status'] = 'Active'
        changes.append('+status: Active')

    # 补全 responsibility
    if 'responsibility' not in metadata:
        # 从文件名推断
        stem = file_path.stem
        if stem == 'INDEX':
            resp = f'处理INDEX相关业务'
        elif stem == 'README':
            resp = f'模块说明与导航'
        elif stem == 'SITEMAP':
            resp = f'目录结构映射'
        else:
            # 从文件名生成
            name = stem.replace('-', ' ').replace('_', ' ').title()
            resp = f'{name}相关业务'
        metadata['responsibility'] = [resp]
        changes.append(f'+responsibility: {resp}')

    if not changes:
        return {'path': file_path, 'status': 'skip', 'reason': 'no_missing_fields'}

    if apply:
        # 确保 module_id 字段在最前面
        ordered = {}
        if 'module_id' in metadata:
            ordered['module_id'] = metadata.pop('module_id')
        ordered.update(metadata)

        new_fm = build_frontmatter(ordered)
        new_content = new_fm + body

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except OSError as e:
            return {'path': file_path, 'status': 'error', 'reason': str(e)}

    return {'path': file_path, 'status': 'modified' if apply else 'would_modify', 'changes': changes}


def main():
    parser = argparse.ArgumentParser(description='补全缺失的 frontmatter 字段')
    parser.add_argument('--apply', action='store_true', help='实际执行修改（默认 dry-run）')
    parser.add_argument('--docs-root', type=str, default=str(DOCS), help='docs 根目录')
    args = parser.parse_args()

    docs_root = Path(args.docs_root)
    all_md = list(docs_root.rglob('*.md'))

    print(f"{'[APPLY]' if args.apply else '[DRY-RUN]'} 扫描 {len(all_md)} 个 .md 文件...")

    stats = {'modified': 0, 'skip': 0, 'error': 0}
    for i, fp in enumerate(all_md):
        if (i + 1) % 500 == 0:
            print(f"  进度: {i+1}/{len(all_md)}")

        result = process_file(fp, apply=args.apply)
        status = result['status']
        if status in ('modified', 'would_modify'):
            stats['modified'] += 1
            rel = fp.relative_to(docs_root.parent)
            changes = result.get('changes', [])
            print(f"  {rel}: {', '.join(changes)}")
        elif status == 'error':
            stats['error'] += 1
            print(f"  ERROR: {fp}: {result.get('reason')}")
        else:
            stats['skip'] += 1

    action = '已修改' if args.apply else '将修改'
    print(f"\n结果: {action} {stats['modified']} 个文件, 跳过 {stats['skip']} 个, 错误 {stats['error']} 个")


if __name__ == '__main__':
    main()
