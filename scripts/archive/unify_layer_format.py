#!/usr/bin/env python3
"""统一 Layer 字段格式为 layer_XX 标准格式。

将所有非标准 layer 值（如 "Layer 5 (策略执行层)"、"Layer 5.1"、"全系统" 等）
统一为 "layer_XX" 格式，与 ARCHITECTURE.md 对齐。

用法:
  python scripts/unify_layer_format.py          # dry-run
  python scripts/unify_layer_format.py --apply   # 实际执行
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

# Layer 路径到标准 layer_XX 的映射
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

# 中文 Layer 名称到标准格式的映射
# 注意：必须按长度降序排列，避免 "Layer 1" 先于 "Layer 10"/"Layer 11" 匹配
LAYER_NAME_MAP = [
    ("Layer 7.5-7.9", "layer_07"),
    ("Layer 0-11", "layer_00"),
    ("Layer 0-9", "layer_00"),
    ("Layer 1-7", "layer_01"),
    ("Layer 5.1", "layer_05"),
    ("Layer 5.2", "layer_05"),
    ("Layer 5.3", "layer_05"),
    ("Layer 5.4", "layer_05"),
    ("Layer 7.5", "layer_07"),
    ("Layer 7.6", "layer_07"),
    ("Layer 7.7", "layer_07"),
    ("Layer 10", "layer_10"),
    ("Layer 11", "layer_11"),
    ("Layer 0", "layer_00"),
    ("Layer 1", "layer_01"),
    ("Layer 2", "layer_02"),
    ("Layer 3", "layer_03"),
    ("Layer 4", "layer_04"),
    ("Layer 5", "layer_05"),
    ("Layer 6", "layer_06"),
    ("Layer 7", "layer_07"),
    ("Layer 8", "layer_08"),
    ("Layer 9", "layer_09"),
    ("全系统", "layer_00"),
    ("跨系统", "layer_00"),
    ("跨层系统", "layer_00"),
]


def infer_layer_from_path(file_path: Path) -> str:
    """从文件路径推断标准 layer 值"""
    parts = file_path.relative_to(DOCS).parts
    for part in parts:
        if part in LAYER_MAP:
            return LAYER_MAP[part]
    return "layer_00"


def normalize_layer(value: str, file_path: Path) -> str:
    """将非标准 layer 值标准化"""
    # 已经是标准格式
    if re.match(r'^layer_\d{2}$', str(value)):
        return str(value)

    # 从中文/英文 Layer 名称映射（按长度降序匹配，避免 Layer 1 先于 Layer 10 匹配）
    val_str = str(value).strip()
    for name, standard in LAYER_NAME_MAP:
        if val_str.startswith(name):
            return standard

    # 从路径推断
    return infer_layer_from_path(file_path)


def process_file(file_path: Path, apply: bool = False) -> dict:
    """处理单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except (UnicodeDecodeError, OSError):
        return {'path': file_path, 'status': 'error', 'reason': 'read_error'}

    # 解析首道 frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {'path': file_path, 'status': 'skip', 'reason': 'no_frontmatter'}

    fm_str = match.group(1)
    import yaml
    try:
        metadata = yaml.safe_load(fm_str) or {}
    except yaml.YAMLError:
        return {'path': file_path, 'status': 'skip', 'reason': 'yaml_error'}

    if 'layer' not in metadata:
        return {'path': file_path, 'status': 'skip', 'reason': 'no_layer_field'}

    old_layer = metadata['layer']
    new_layer = normalize_layer(old_layer, file_path)

    if old_layer == new_layer:
        return {'path': file_path, 'status': 'skip', 'reason': 'already_standard'}

    if apply:
        # 替换 frontmatter 中的 layer 行
        # 使用正则精确替换，避免影响其他内容
        old_fm = match.group(0)
        new_fm = re.sub(
            r'^layer:\s*.*$',
            f'layer: {new_layer}',
            old_fm,
            flags=re.MULTILINE
        )
        new_content = new_fm + content[match.end():]

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except OSError as e:
            return {'path': file_path, 'status': 'error', 'reason': str(e)}

    return {
        'path': file_path,
        'status': 'modified' if apply else 'would_modify',
        'old_layer': old_layer,
        'new_layer': new_layer
    }


def main():
    parser = argparse.ArgumentParser(description='统一 Layer 字段格式')
    parser.add_argument('--apply', action='store_true', help='实际执行修改')
    args = parser.parse_args()

    all_md = list(DOCS.rglob('*.md'))
    print(f"{'[APPLY]' if args.apply else '[DRY-RUN]'} 扫描 {len(all_md)} 个 .md 文件...")

    stats = {'modified': 0, 'skip': 0, 'error': 0}
    layer_changes = {}

    for i, fp in enumerate(all_md):
        if (i + 1) % 500 == 0:
            print(f"  进度: {i+1}/{len(all_md)}")

        result = process_file(fp, apply=args.apply)
        status = result['status']

        if status in ('modified', 'would_modify'):
            stats['modified'] += 1
            rel = fp.relative_to(DOCS.parent)
            old_l = result['old_layer']
            new_l = result['new_layer']
            key = f"{old_l} → {new_l}"
            layer_changes[key] = layer_changes.get(key, 0) + 1
            if stats['modified'] <= 50:  # 只打印前50个
                print(f"  {rel}: {old_l} → {new_l}")
        elif status == 'error':
            stats['error'] += 1
        else:
            stats['skip'] += 1

    action = '已修改' if args.apply else '将修改'
    print(f"\n结果: {action} {stats['modified']} 个文件, 跳过 {stats['skip']} 个, 错误 {stats['error']} 个")

    if layer_changes:
        print(f"\nLayer 变更分布:")
        for key, count in sorted(layer_changes.items(), key=lambda x: -x[1]):
            print(f"  {key}: {count} 个文件")


if __name__ == '__main__':
    main()
