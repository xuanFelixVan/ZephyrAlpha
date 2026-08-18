# [MODULE] scripts.governance._archive.one_off.oneoff_purge_harvest_candidates
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_ONEOFF_PURGE_HARVEST_CANDIDATES | layer=script | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""一次性 purge 脚本：把 candidate_module_registry.yaml 中 5283 个 CAND-HARVEST-* 条目
归档到独立 archive 文件，主 registry 只保留 ~90 个手工候选，瘦身 6.9MB→~300KB。

病根：harvest_candidates_from_drafts.py 一次性从草稿 CSV 批量收割 5283 条候选，
status=candidate / q1_implemented=pending / 0 promoted，98% 是噪音，撑大主 registry
到 166K 行/6.9MB，拖慢加载与 candidate_module_report 生成。

策略（非硬删，归档保数据）：
  - 文本块切分（按 `  - id:` 边界），保留非 HARVEST 条目原始格式（diff 干净）
  - HARVEST 条目迁到 candidate_module_registry_harvest_archive.yaml（独立文件，带 header）
  - 主 registry 加 purge 备注（日期/数量/归档位置）
  - git history 兜底（文件已 git-tracked，可随时恢复）

Usage::
    python scripts/oneoff_purge_harvest_candidates.py --dry-run   # 只统计不写
    python scripts/oneoff_purge_harvest_candidates.py             # 执行 purge
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "candidate_module_registry.yaml"
)
# 归档文件放 _archive/ 子目录——exempt_parts 已含 _archive，
# 豁免 check_frontmatter ttl 校验 + audit_broken_links 断链扫描（数据归档非文档链接）。
ARCHIVE_PATH = REGISTRY_PATH.parent / "_archive" / "candidate_module_registry_harvest_archive.yaml"
ENTRY_MARKER = "  - id: "
HARVEST_PREFIX = "CAND-HARVEST"


def _split_entries(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    """切分文件为 (header, entry_blocks, trailing)。

    header: 从文件头到 entries: 行（含）+ entries: 后到首个条目前的注释/空行
    entry_blocks: 每个条目的文本块列表（含尾部换行），块以 `  - id:` 开头
    trailing: 最后一个条目后的残余（通常为空或单个换行）
    """
    entries_idx = None
    for i, line in enumerate(lines):
        if line.rstrip() == "entries:":
            entries_idx = i
            break
    if entries_idx is None:
        print("[ERROR] 未找到 entries: 行", file=sys.stderr)
        sys.exit(1)

    # 找首个条目起始
    first_entry_idx = None
    for i in range(entries_idx + 1, len(lines)):
        if lines[i].startswith(ENTRY_MARKER):
            first_entry_idx = i
            break
    if first_entry_idx is None:
        print("[ERROR] entries: 后无条目", file=sys.stderr)
        sys.exit(1)

    header = lines[:first_entry_idx]
    rest = lines[first_entry_idx:]

    # 按 `  - id:` 边界切块
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in rest:
        if line.startswith(ENTRY_MARKER) and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)

    return header, blocks, []  # trailing 通常为空（最后块含 EOF 换行）


def _block_id(block: list[str]) -> str:
    """取条目块的 id（`  - id: CAND-XXX-NNN` → `CAND-XXX-NNN`）。"""
    first = block[0]
    return first[len(ENTRY_MARKER) :].strip() if first.startswith(ENTRY_MARKER) else ""


def _build_archive_header(harvest_count: int) -> list[str]:
    """归档文件 header（独立 doc_type=register，标明归档性质）。"""
    return [
        "# [A_config] module_id=CFG-candidate-module-registry-harvest-archive | layer=config | stability=stable | safety=M | ai_autonomy=human_gated",
        "module_id: REG-CAND-HARVEST-ARCHIVE-001",
        "ttl: permanent",
        "title: 候选模块登记表 — HARVEST 归档（场外草稿收割 dump）",
        "doc_type: register",
        "registry_id: REG-CAND-HARVEST-ARCHIVE-001",
        "name: 候选模块 HARVEST 归档",
        "description: >-",
        f"  harvest_candidates_from_drafts.py 一次性从场外草稿 CSV 收割的 {harvest_count} 条候选归档。",
        "  status=candidate / q1_implemented=pending / 0 promoted，未经设计准入一问标准评估。",
        "  2026-08-05 从主 candidate_module_registry.yaml purge 迁出，主 registry 仅保留手工候选。",
        "  保留此归档供回溯查证；如需重新评估某条，从本文件取数据过一问标准后晋升到主 registry。",
        "owner: MOD-GOV-029",
        "tier: tier_1_governance",
        "status: active",
        "version: 1.0.0",
        "created: '2026-08-05'",
        "last_updated: '2026-08-05'",
        "unique_key:",
        "- id",
        "entries:",
        "",
    ]


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Purge CAND-HARVEST-* 条目到归档文件")
    parser.add_argument("--dry-run", action="store_true", help="只统计不写文件")
    args = parser.parse_args()

    if not REGISTRY_PATH.exists():
        print(f"[ERROR] 主 registry 不存在: {REGISTRY_PATH}", file=sys.stderr)
        return 1

    lines = REGISTRY_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    header, blocks, _ = _split_entries(lines)

    keep_blocks: list[list[str]] = []
    harvest_blocks: list[list[str]] = []
    for block in blocks:
        bid = _block_id(block)
        if bid.startswith(HARVEST_PREFIX):
            harvest_blocks.append(block)
        else:
            keep_blocks.append(block)

    orig_size = REGISTRY_PATH.stat().st_size
    print(f"[INFO] 原文件: {len(lines)} 行 / {orig_size / 1024:.0f} KB")
    print(f"[INFO] 条目: 保留 {len(keep_blocks)} / 归档 HARVEST {len(harvest_blocks)}")

    if args.dry_run:
        est_keep = sum(len(b) for b in keep_blocks) + len(header)
        print(f"[DRY-RUN] 不写文件。预估主 registry 瘦身后 ~{est_keep} 行")
        return 0

    # 1. 写主 registry（header + 保留块）
    new_header = list(header)
    # 在 header 末尾（entries: 前）插 purge 备注
    purge_note = (
        f"# [PURGE 2026-08-05] 移除 {len(harvest_blocks)} 个 CAND-HARVEST-* 条目到归档文件 "
        f"candidate_module_registry_harvest_archive.yaml（主 registry 瘦身）。"
        f"手工候选 {len(keep_blocks)} 条保留。\n"
    )
    # 插在 entries: 行之前
    for i in range(len(new_header) - 1, -1, -1):
        if new_header[i].rstrip() == "entries:":
            new_header.insert(i, purge_note)
            break

    main_content = "".join(new_header) + "".join("".join(b) for b in keep_blocks)
    REGISTRY_PATH.write_text(main_content, encoding="utf-8", newline="\n")
    new_size = REGISTRY_PATH.stat().st_size
    print(f"[OK] 主 registry 已瘦身: {new_size / 1024:.0f} KB ({len(keep_blocks)} 条，原 {orig_size / 1024:.0f} KB)")

    # 2. 写归档文件
    # 注意：archive_header 元素无 \n（与主 registry header 不同——后者来自
    # splitlines(keepends=True) 自带 \n），必须用 "\n".join + 末尾 \n 补上，
    # 否则 header 全压成一行导致 YAML 解析失败。
    archive_header = _build_archive_header(len(harvest_blocks))
    archive_content = "\n".join(archive_header) + "\n" + "".join("".join(b) for b in harvest_blocks)
    ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE_PATH.write_text(archive_content, encoding="utf-8", newline="\n")
    print(
        f"[OK] 归档文件已写: {ARCHIVE_PATH.name} "
        f"({ARCHIVE_PATH.stat().st_size / 1024:.0f} KB, {len(harvest_blocks)} 条)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
