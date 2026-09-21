# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/syncers/normalize_blueprint_autogen_anchors.py | §
# [MODULE] scripts.governance.d5_architecture.syncers.normalize_blueprint_autogen_anchors
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants, scripts.governance._shared.file_utils (atomic_write_safe), scripts.governance._shared.file_lock (blueprint_write_lock)
# [CONSUMERS] CI/pre-write gate (--check), AI 施工者按需 CLI, blueprint AUTOGEN 模板治本批（st-laneJ）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] AUTOGEN 标记区内的失效 AGENTS.md §编号引用必须归一为稳定规则名锚点；重跑幂等（第二遍零改动）；--check 模式零写入仅报告
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# noqa: m11-perm-manual-legitimate  M11豁免: 本工具为一次性/按需 CLI + CI --check 双入口，非常驻服务非 cron
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/blueprint/test_normalize_blueprint_autogen_anchors.py -q
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""蓝图 AUTOGEN 区失效 AGENTS.md §编号引用归一器（#移交① 治本，2026-09-16，lane J）。

病根：L0 宪法 2026-09-12 替换 v1 后 AGENTS.md 的 §编号全部失效（§7 由「代码规范」
变为「核心系统速查」），但 40 份既有蓝图 §0.1「代码文件清单」AUTOGEN 标记区内残留
一行同款手写模板：
    > **架构归属SSoT**：见 AGENTS.md RULE-DEPGRAPH（depgraph SSoT 真源唯一指针）
该行被错误标注为 AUTOGEN（generator=extract_depgraph.py），但 extract_depgraph.py 实为
depgraph 只读查询工具（仅产 JSON，永不写蓝图正文）——故此行为纯手写复制病毒感染体，
"人工修复即被下次重建回填"的表象其实是"根本没有生成器会重建它"。§2 路径索引的同款
AGENTS §编号病已由 sync_blueprint_code_index.py 模板治本（GW-C st-bptmpl-20260916）。

治本（生成为唯一 / 手工不可写模式 + 存量归一）：
  1. 将 §0.1 手写残留的失效 §编号行归一为稳定规则名锚点（RULE-DEPGRAPH / RULE-SSOT），
     与 sync_blueprint_code_index 模板的稳定锚口径一致（L0 §6：稳定锚=规则名 RULE-XXX）。
  2. 只替换 §0.1 SSoT 模板行（严格锚定），绝不触碰 AUTOGEN 区外的散文式 §N 历史引用
     （如 model_downloader「§6.1 data/models/ 目录生命周期」= 决策记录留痕，属合法历史）。
  3. --check 模式扫描全部蓝图 AUTOGEN 标记区，报告任何残留失效 AGENTS.md §编号引用，
     作为防回潮自检门禁（CI 调用，exit 1=有回潮）。

用法：
  python scripts/governance/d5_architecture/syncers/normalize_blueprint_autogen_anchors.py --check   # 仅检测（CI）
  python scripts/governance/d5_architecture/syncers/normalize_blueprint_autogen_anchors.py --dry-run   # 预演将改哪些
  python scripts/governance/d5_architecture/syncers/normalize_blueprint_autogen_anchors.py --apply     # 归一落盘（幂等）
"""

from __future__ import annotations

import re
import sys
from argparse import ArgumentParser
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_lock import blueprint_write_lock
from _shared.file_utils import atomic_write_safe

ensure_utf8_stdout()

BLUEPRINT_GLOBS = [
    "docs/03_modules/**/*.md",
]

# AUTOGEN 标记（HTML 注释）
AUTOGEN_MARKER_PREFIX = "<!-- AUTOGEN"

# 标题行（用于界定 AUTOGEN 区起点：区内=最近一个标题之后出现过 AUTOGEN 标记）
HEADING_RE = re.compile(r"^#{1,6}\s")

# 被本工具治理的病灶签名：架构归属 SSoT 归属行内仍写死 AGENTS.md §编号
# （锚定到"SSoT 归属"语义，避免误伤历史决策记录里合法的散文式 §N 引用）
SSOT_STALE_REF = re.compile(r"架构归属 ?SSoT.*AGENTS\.md\s*§\s*\d")

# 唯一被授权归一的 §0.1 SSoT 模板行（严格锚定，含带/不带空格两变体）
SSOT_STALE_LINE = re.compile(
    r"^(\s*>\s*\*\*架构归属 ?SSoT\*\*：见 )AGENTS\.md\s*§\s*7「代码规范」"
    r"(（depgraph SSoT 真源唯一指针）\s*)$"
)

# 归一后的稳定锚文案（与 sync_blueprint_code_index 模板同口径：规则名，非 §编号）
SSOT_CANONICAL = "> **架构归属 SSoT**：见 AGENTS.md RULE-DEPGRAPH / RULE-SSOT（depgraph SSoT 真源唯一指针）"


def _iter_blueprints(root: Path) -> list[Path]:
    """列出全部待检蓝图（去重、稳定排序）。"""
    found: set[Path] = set()
    for pattern in BLUEPRINT_GLOBS:
        found.update(root.glob(pattern))
    return sorted(found)


def _in_autogen_region(lines: list[str], idx: int) -> bool:
    """判定 lines[idx] 是否位于 AUTOGEN 标记区内。

    规则：从 idx 向前回退到最近一个标题行；若该标题行与 idx 之间出现过
    ``<!-- AUTOGEN`` 标记，则视为落在自动区块内（应受门禁保护、禁手写漂移）。
    """
    for j in range(idx - 1, -1, -1):
        stripped = lines[j].lstrip()
        if stripped.startswith(AUTOGEN_MARKER_PREFIX):
            return True
        if HEADING_RE.match(lines[j]):
            return False
    return False


def find_stale_autogen_refs(content: str) -> list[tuple[int, str]]:
    """返回 AUTOGEN 区内残留的 SSoT 归属失效 AGENTS.md §编号引用（行号 1-based + 行文本）。

    零误伤设计：只判定被本工具治理的病灶签名（架构归属 SSoT 归属行写死 §编号），
    历史决策记录里的散文式 §N 引用（如 model_downloader「§6.1 data/models/ 生命周期」）
    与不属 SSoT 归属语义的行不在门禁范围。
    """
    lines = content.splitlines()
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if SSOT_STALE_REF.search(line) and _in_autogen_region(lines, i):
            hits.append((i + 1, line))
    return hits


def normalize_content(content: str) -> tuple[str, bool]:
    """把 §0.1 SSoT 失效行归一为稳定锚；返回 (新内容, 是否有改动)。

    仅替换严格锚定的 SSoT 模板行，其余内容逐字保留（幂等：已归一后再次调用零改动）。
    """
    out_lines: list[str] = []
    changed = False
    for line in content.split("\n"):
        m = SSOT_STALE_LINE.match(line)
        if m:
            if line != SSOT_CANONICAL:
                out_lines.append(SSOT_CANONICAL)
                changed = True
            else:
                out_lines.append(line)
        else:
            out_lines.append(line)
    return "\n".join(out_lines), changed


def _process_blueprint(bp_path: Path, *, apply: bool) -> tuple[bool, list[tuple[int, str]]]:
    """处理单个蓝图；返回 (是否落盘改动, 该文件 AUTOGEN 区残留失效引用)。"""
    with blueprint_write_lock(bp_path):
        content = bp_path.read_text(encoding="utf-8")
        new_content, changed = normalize_content(content)
        if apply and changed:
            if not atomic_write_safe(bp_path, new_content):
                raise OSError(f"原子写入失败: {bp_path}")
        residual = find_stale_autogen_refs(new_content)
    return changed, residual


def run(root: Path, mode: str) -> int:
    """执行归一/检查。mode ∈ {check, dry-run, apply}。"""
    blueprints = _iter_blueprints(root)
    stale_files: list[tuple[Path, list[tuple[int, str]]]] = []
    dirty: list[Path] = []

    for bp in blueprints:
        try:
            content = bp.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:  # pragma: no cover - 磁盘异常兜底
            print(f"⚠️ 读取失败 {bp.relative_to(root)}: {exc}", file=sys.stderr)
            continue
        new_content, changed = normalize_content(content)
        if changed:
            dirty.append(bp)
        residual = find_stale_autogen_refs(new_content)
        if residual:
            stale_files.append((bp, residual))

    rel = [str(p.relative_to(root)).replace("\\", "/") for p in dirty]

    if mode == "apply":
        for bp in dirty:
            _process_blueprint(bp, apply=True)
        print(f"[BP-AUTOGEN-ANCHOR] ✅ 归一落盘 {len(dirty)} 份蓝图")
    elif mode == "dry-run":
        print(f"[BP-AUTOGEN-ANCHOR] 预演：将归一 {len(dirty)} 份蓝图")
        for r in rel:
            print(f"  - {r}")
    # check 与其余模式都要报告残留（防回潮）
    if stale_files:
        total_hits = sum(len(h) for _, h in stale_files)
        print(
            f"[BP-AUTOGEN-ANCHOR] 🔴 AUTOGEN 区仍存失效 AGENTS.md §编号引用 {total_hits} 处 / {len(stale_files)} 文件"
        )
        for bp, hits in stale_files:
            for lineno, text in hits:
                print(f"  {bp.relative_to(REPO_ROOT)}:{lineno}: {text.strip()[:80]}")
        return EXIT_FINDINGS

    print("[BP-AUTOGEN-ANCHOR] ✅ AUTOGEN 区无失效 AGENTS.md §编号引用（稳定锚合规）")
    return EXIT_PASS


def main() -> int:
    """入口函数."""
    parser = ArgumentParser(description="蓝图 AUTOGEN 区失效 AGENTS §编号引用归一/自检")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="仅检测 AUTOGEN 区残留失效引用（CI 模式，零写入）")
    group.add_argument("--dry-run", action="store_true", help="预演将归一的蓝图清单，零写入")
    group.add_argument("--apply", action="store_true", help="归一落盘（幂等）")
    args = parser.parse_args()

    mode = "apply" if args.apply else ("dry-run" if args.dry_run else "check")
    try:
        return run(REPO_ROOT, mode)
    except Exception as exc:  # noqa: BLE001 - CLI 顶层兜底 fail-loud
        print(f"[BP-AUTOGEN-ANCHOR] ❌ 异常: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
