# [MODULE] scripts.governance._archive.one_off.oneoff_fix_generator_nonidempotent
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
# [A_module] module_id=MOD-GOV_ONEOFF_FIX_GENERATOR_NONIDEMPOTENT | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""一次性脚本：批量修复 6 个生成器的 datetime.now() 和 write_text newline（#ARCH-REGEN-NONIDEMPOTENT-001）。

治本：#ARCH-REGEN-NONIDEMPOTENT-001
原因：Edit 工具报告成功但未持久化，改用 Python pathlib.Path.write_text 可靠写入。

使用：python scripts/oneoff_fix_generator_nonidempotent.py
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GEN_DIR = REPO / "scripts" / "governance" / "d5_architecture" / "generators"


def fix_file(path: Path, replacements: list[tuple[str, str]]) -> int:
    """对 path 做 replacements 列表中的所有替换，返回替换次数。"""
    content = path.read_text(encoding="utf-8")
    n = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new, 1)
            n += 1
    if n > 0:
        path.write_text(content, encoding="utf-8", newline="\n")
    return n


# ── generate_path_tree.py ──
n1 = fix_file(
    GEN_DIR / "generate_path_tree.py",
    [
        (
            '    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")',
            '    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：幂等时间源\n'
            '    now = idempotent_timestamp(Path(__file__))',
        ),
        (
            '            out_path.write_text(content, encoding="utf-8")\n            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")\n\n        if args.lang in ("en", "both"):\n            content = _FRONTMATTER + generate_path_tree("en", conn, "full")\n            out_path = output_dir / en_name\n            out_path.write_text(content, encoding="utf-8")',
            '            out_path.write_text(content, encoding="utf-8", newline="\\n")\n            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")\n\n        if args.lang in ("en", "both"):\n            content = _FRONTMATTER + generate_path_tree("en", conn, "full")\n            out_path = output_dir / en_name\n            out_path.write_text(content, encoding="utf-8", newline="\\n")',
        ),
    ],
)
print(f"generate_path_tree.py: {n1} replacements")

# ── generate_domain_doc.py ──
n2 = fix_file(
    GEN_DIR / "generate_domain_doc.py",
    [
        (
            '    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")\n\n    # 统计',
            '    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：\n'
            '    # 时间真源改为脚本最近 git commit 时间（idempotent_date / idempotent_timestamp），\n'
            '    # 相同 commit → 相同输出，消除 datetime.now() 导致的 per-second diff 非收敛循环。\n'
            '    # 下方 frontmatter date 字段直接调 idempotent_date()，不再需要 now 局部变量。\n\n    # 统计',
        ),
        (
            '    lines.append(f"date: {now.split()[0]}")',
            '    lines.append(f"date: {idempotent_date(Path(__file__))}")',
        ),
    ],
)
print(f"generate_domain_doc.py: {n2} replacements")

# ── generate_integration_topology.py ──
n3 = fix_file(
    GEN_DIR / "generate_integration_topology.py",
    [
        (
            '    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")',
            '    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：幂等时间源\n'
            '    now = idempotent_timestamp(Path(__file__))',
        ),
        (
            '        out_path.write_text(content, encoding="utf-8")',
            '        out_path.write_text(content, encoding="utf-8", newline="\\n")',
        ),
    ],
)
print(f"generate_integration_topology.py: {n3} replacements")

# ── generate_navigation_index.py ──
n4 = fix_file(
    GEN_DIR / "generate_navigation_index.py",
    [
        (
            '    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")',
            '    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：幂等时间源\n'
            '    now = idempotent_timestamp(Path(__file__))',
        ),
        (
            '    out_path.write_text(content, encoding="utf-8")',
            '    out_path.write_text(content, encoding="utf-8", newline="\\n")',
        ),
    ],
)
print(f"generate_navigation_index.py: {n4} replacements")

# ── generate_dataflow_diagram.py（3 处 datetime.now().isoformat）──
n5 = fix_file(
    GEN_DIR / "generate_dataflow_diagram.py",
    [
        (
            '    now = datetime.now().isoformat(timespec="seconds")',
            '    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：幂等时间源（脚本最近 git commit 时间）\n'
            '    now = idempotent_timestamp(Path(__file__))',
        ),
        (
            '        md_path.write_text(md_text, encoding="utf-8")',
            '        md_path.write_text(md_text, encoding="utf-8", newline="\\n")',
        ),
        (
            '    (out_dir / "dataflow_index.md").write_text(index_md, encoding="utf-8")',
            '    (out_dir / "dataflow_index.md").write_text(index_md, encoding="utf-8", newline="\\n")',
        ),
    ],
)
# 第二、三处 datetime.now().isoformat 用 replace_all 模式
content5 = (GEN_DIR / "generate_dataflow_diagram.py").read_text(encoding="utf-8")
remaining = content5.count('    now = datetime.now().isoformat(timespec="seconds")')
if remaining > 0:
    content5 = content5.replace(
        '    now = datetime.now().isoformat(timespec="seconds")',
        '    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：幂等时间源（脚本最近 git commit 时间）\n'
        '    now = idempotent_timestamp(Path(__file__))',
    )
    (GEN_DIR / "generate_dataflow_diagram.py").write_text(content5, encoding="utf-8", newline="\n")
    print(f"generate_dataflow_diagram.py: replaced {remaining} remaining datetime.now()")
print(f"generate_dataflow_diagram.py: {n5} initial replacements")

# ── zoomable_html.py ──
n6 = fix_file(
    GEN_DIR / "zoomable_html.py",
    [
        (
            '    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")',
            '    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：幂等时间源\n'
            '    gen_time = idempotent_timestamp(Path(__file__))',
        ),
        (
            '    out_path.write_text(html, encoding="utf-8")',
            '    out_path.write_text(html, encoding="utf-8", newline="\\n")',
        ),
    ],
)
print(f"zoomable_html.py: {n6} replacements")

print("\n=== 完成。请用 rg 验证：rg -n 'datetime\\.now\\(\\)' scripts/governance/d5_architecture/generators/*.py ===")
