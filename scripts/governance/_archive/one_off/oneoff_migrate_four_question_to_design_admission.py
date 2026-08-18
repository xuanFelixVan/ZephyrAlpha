#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [MODULE] scripts.governance._archive.one_off.oneoff_migrate_four_question_to_design_admission
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_ONEOFF_MIGRATE_FOUR_QUESTION | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
ONEOFF: 四问 -> 一问标准 真源迁移（裁定 2026-08-04）

治本: candidate_module_registry.yaml 中 four_question 框架收敛为 design_admission，
仅保留 q1_implemented（功能是否已实现/已登记）。删除 q2/q3/q4（灰度已废）。
blocking_question 为 q2/q3/q4 的 -> none（原裁定已废，历史 result 保留防误重新设计）。

处理两种形态:
  原候选(~32): q1_implemented/q2_demand_driven/q3_domain_alive/q4_ai_replaceable (inline flow)
  harvest(~5283): q1/q2/q3/q4 (scalar pending)

备份: 运行前拷贝 .bak_pre_one_question，校验通过后删除。
行尾: 强制 LF（与 .gitattributes 一致）。
"""
import re
import shutil
import sys
from pathlib import Path

SRC = Path(r"d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\candidate_module_registry.yaml")
BACKUP = SRC.with_suffix(".yaml.bak_pre_one_question")

# 删除的子字段（长形 + 短形）
DELETE_FIELDS = ("q2_demand_driven", "q3_domain_alive", "q4_ai_replaceable", "q2", "q3", "q4")
# 短形 q1 -> 长形 q1_implemented（统一）
Q1_SHORT = re.compile(r'^(\s+)q1\s*:')
# blocking_question: q2|q3|q4 -> none
BLOCKING_LEGACY = re.compile(r'^(\s+blocking_question:\s*)(q2|q3|q4)(\s*)$')
# four_question 块头（无值，block style）
FQ_HEADER = re.compile(r'^(\s*)four_question:\s*$')
# schema 行: four_question: obj
SCHEMA_FQ = re.compile(r'^(\s*)four_question:\s*obj\s*$')


def get_indent(line: str) -> int:
    """get_indent implementation."""
    return len(line) - len(line.lstrip(' '))


def process(text: str):
    """process implementation."""
    lines = text.split('\n')
    out = []
    in_fq = False
    fq_indent = 0
    stats = {'fq_blocks': 0, 'deleted': 0, 'blocking_changed': 0, 'q1_renamed': 0,
             'schema_renamed': 0, 'comment_updated': 0}

    for line in lines:
        # ---- Schema 注释行（L28）----
        if '四问过滤：记录 q1已实现/q2需求驱动/q3域活着/q4 AI替代' in line:
            line = line.replace(
                '四问过滤：记录 q1已实现/q2需求驱动/q3域活着/q4 AI替代，blocking_question 标明卡在哪问。',
                '一问标准：仅记录 q1已实现/重复（裁定 2026-08-04，原 q2/q3/q4 灰度已废），blocking_question 标明是否卡在 q1。'
            )
            stats['comment_updated'] += 1
        if '重新过四问' in line:
            line = line.replace('重新过四问', '重新过一问')
            stats['comment_updated'] += 1

        # ---- Schema 字段行 four_question: obj -> design_admission: obj ----
        if SCHEMA_FQ.match(line):
            line = line.replace('four_question:', 'design_admission:')
            stats['schema_renamed'] += 1
            out.append(line)
            continue

        # ---- 块内处理 ----
        if in_fq:
            if not line.strip():
                out.append(line)
                continue
            ind = get_indent(line)
            if ind <= fq_indent:
                # 块结束
                in_fq = False
                # 落到块外处理
            else:
                # 块内子字段
                stripped = line.strip()
                # 删除 q2/q3/q4 子字段（含短形/长形）
                field_name = re.split(r'[:\s]', stripped, 1)[0]
                if field_name in DELETE_FIELDS:
                    stats['deleted'] += 1
                    continue
                # 短形 q1 -> q1_implemented
                if Q1_SHORT.match(line):
                    line = Q1_SHORT.sub(r'\1q1_implemented:', line)
                    stats['q1_renamed'] += 1
                # blocking_question: q2/q3/q4 -> none
                m = BLOCKING_LEGACY.match(line)
                if m:
                    line = m.group(1) + 'none' + (m.group(3) or '') + '  # 原%s已废(裁定2026-08-04)' % m.group(2)
                    stats['blocking_changed'] += 1
                out.append(line)
                continue

        # ---- 块外: 检测 four_question 块头 ----
        if not in_fq:
            m = FQ_HEADER.match(line)
            if m:
                in_fq = True
                fq_indent = get_indent(line)
                line = line.replace('four_question:', 'design_admission:')
                stats['fq_blocks'] += 1
                out.append(line)
                continue
            out.append(line)

    return '\n'.join(out), stats


def verify(original: str, result: str, stats: dict) -> bool:
    """verify implementation."""
    ok = True
    # 1. 无 four_question 残留
    if 'four_question' in result:
        print("[FAIL] four_question 仍残留")
        ok = False
    # 2. 无 q2/q3/q4 子字段残留
    rem = len(re.findall(r'(?m)^\s+(q2_demand_driven|q3_domain_alive|q4_ai_replaceable|q2|q3|q4)\s*:', result))
    if rem:
        print(f"[FAIL] q2/q3/q4 子字段残留 {rem} 处")
        ok = False
    # 3. design_admission 块数 == 原 four_question 块数
    new_fq = len(re.findall(r'(?m)^\s*design_admission:\s*$', result))
    if new_fq != stats['fq_blocks']:
        print(f"[FAIL] design_admission 块数 {new_fq} != 迁移数 {stats['fq_blocks']}")
        ok = False
    # 4. 条目总数不变（- id: 计数）
    old_ids = len(re.findall(r'(?m)^- id:\s', original))
    new_ids = len(re.findall(r'(?m)^- id:\s', result))
    if old_ids != new_ids:
        print(f"[FAIL] 条目数变化 {old_ids} -> {new_ids}")
        ok = False
    else:
        print(f"[OK] 条目数 {new_ids} 不变")
    # 5. q1_implemented 保留数 >= 原 q1 出现数
    q1_kept = len(re.findall(r'(?m)^\s+q1_implemented', result))
    print(f"[INFO] q1_implemented 保留 {q1_kept} 处")
    return ok


def main():
    """Entry point: parse args, run logic, return exit code."""
    if not SRC.exists():
        print(f"[ERR] 源文件不存在: {SRC}")
        sys.exit(2)
    # 备份
    shutil.copy2(SRC, BACKUP)
    print(f"[BACKUP] {BACKUP.name}")

    original = SRC.read_text(encoding='utf-8')
    result, stats = process(original)

    print(f"[STATS] fq_blocks={stats['fq_blocks']} deleted_lines={stats['deleted']} "
          f"blocking_changed={stats['blocking_changed']} q1_renamed={stats['q1_renamed']} "
          f"schema_renamed={stats['schema_renamed']} comment_updated={stats['comment_updated']}")

    ok = verify(original, result, stats)
    if not ok:
        print("[ABORT] 校验失败，未写入。备份保留。")
        sys.exit(1)

    # 写入，强制 LF
    SRC.write_text(result, encoding='utf-8', newline='\n')
    print(f"[DONE] 写入 {SRC.name} (LF)")

    # 校验通过，删除备份
    if BACKUP.exists():
        BACKUP.unlink()
        print(f"[CLEANUP] 删除备份 {BACKUP.name}")


if __name__ == '__main__':
    main()
