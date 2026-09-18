# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] scripts.governance.registry_batch_edit
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.io.file_utils (safe_write_text, content_sha256)
# [CONSUMERS] AI sessions（登记表批量编辑统一入口）；registry_mass_deletion_gate（语义对齐）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 登记表 YAML 批量编辑通用工具——只提供纯插入式编辑（插入行删除后必须与原文逐字节一致才许落盘，2026-09-09 险些蒸发 4703 行治本）；YAML 条目数只增不减断言；CAS 语义落盘（safe_write_text expected_base_sha256=读入原文 hash，陈旧基线拒写）；拒绝时输出 unified diff 前 40 行供 AI 定位正则失配点；fail-closed（任何校验不过=不落盘）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验失败/写失败→返回 ok=False（不落盘，reason+diff_head 携带现场）；插入内容与声称 blocks 不一致→拒绝；YAML 解析失败→拒绝；CAS 拒写（StaleWriteRefused/WriteVerificationError）→ok=False 不重试不绕过；verify-only 模式只读零写入
# [TESTS] tests/governance/commit_gates/test_registry_batch_edit.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | anchor:scripts/governance/registry_batch_edit.py
# [TTL] permanent
"""
registry_batch_edit.py — 登记表 YAML 批量编辑通用工具（防蒸发，纯插入式）

病根（第一性原理，2026-09-09 夜 4703 行蒸发事故，nodebt 晨报裁定 7）：
    首版批量补登 param_origin 的脚本正则未匹配缩进条目，纯删除逻辑一次性清空
    alert_threshold_registry + risk_limit_registry 两登记表 4703 行。
    批量编辑的破坏力与"正则是否匹配"强耦合——没匹配上就从"插入"变成"删除"。

治本：把"纯插入"从纪律升级为工具强制——
    1. verify_pure_insertion(): difflib 只允许 equal/insert opcode，出现任何
       delete/replace 即拒绝（拦截正则失配整块误删/缩进漏配重排/行尾翻转）；
    2. 字节级复核：keepends 行集拼接 == 原文（读入无损自检）；
    3. 插入段拼接 == 调用方声称的 blocks（防工具自身 bug 静默插错）；
    4. YAML 双断言：两侧可解析 + 条目数只增不减；
    5. CAS 落盘：safe_write_text(expected_base_sha256=原文 hash)，磁盘已被他人
       推进时 StaleWriteRefused 拒写；写后回读校验防"修改已生效"假象。

背景事故细节：见 docs/_working/2026-09-10-nodebt-night-report.md 裁定 7。

Usage::

    # scripts 端导入（_shared/registry_batch_edit.py 为本文件 re-export 壳）
    from _shared.registry_batch_edit import insert_blocks, RegistryEditResult

    # 直摆插入（锚点行后追加 block；锚点命中 0 次或多次=拒绝）
    result = insert_blocks(
        "docs/01_policies_and_standards/_registry/catalogs/foo_registry.yaml",
        blocks=[block_text],
        after_lines=["  - issue_id: '<上一个条目的 issue_id 原文>'"],
    )
    if not result.ok:
        print(result.reason)
        print(result.diff_head)

    CLI:
        python scripts/governance/registry_batch_edit.py --file <登记表路径> \
            --blocks-file <UTF-8 块文件> [--after-line "锚点行原文"]... [--verify-only]
        # --blocks-file: 块以 "===== BLOCK N =====" 行分隔，块内为待插入原文
"""

from __future__ import annotations

import argparse
import difflib
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO_CANDIDATES = (Path(__file__).resolve().parent.parent.parent,)
for _c in _REPO_CANDIDATES:
    if (_c / "src").exists():
        sys.path.insert(0, str(_c / "src"))
        break

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402

__all__ = [
    "RegistryEditResult",
    "verify_pure_insertion",
    "insert_blocks",
]

_DIFF_HEAD_LINES = 40

_BLOCK_SEP = "===== BLOCK "


@dataclass(frozen=True)
class RegistryEditResult:
    """编辑结果（ok=False 时 reason/diff_head 携带现场供 AI 直接定位）。"""

    ok: bool
    path: str
    original_lines: int
    final_lines: int
    inserted_blocks: int
    reason: str
    diff_head: str


def _diff_head(orig_lines: list[str], new_lines: list[str]) -> str:
    """unified diff 前 40 行（拒绝现场定位正则失配点）。"""
    diff = difflib.unified_diff(orig_lines, new_lines, fromfile="original", tofile="proposed", n=2)
    return "".join(list(diff)[:_DIFF_HEAD_LINES])


def _yaml_entry_count(text: str) -> int | None:
    """YAML 顶层条目数（list=元素数 / dict=键数）；解析失败返回 None。"""
    try:
        import yaml

        data = yaml.safe_load(text)
    except Exception:  # noqa: BLE001 — 解析失败由调用方拒绝
        return None
    if data is None:
        return 0
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        return len(data)
    return None


def verify_pure_insertion(
    original: str,
    new_text: str,
    blocks: list[str] | None = None,
) -> tuple[bool, str, str]:
    """校验 new_text 是否可由 original 经"纯插入"得到。

    "纯插入"的可执行化 = original 是 new_text 的行级保序子序列：
    difflib.SequenceMatcher opcodes 只允许 equal/insert，出现任何
    delete/replace 即拒绝（换行符差异按字节计，keepends 保真）。

    Args:
        original: 原文。
        new_text: 拟落盘新文本。
        blocks: 调用方声称插入的块列表；给定时校验所有 insert 段拼接与之一致
            （防工具自身 bug 静默插错位置/内容）。

    Returns:
        (ok, reason, diff_head)。ok=False 时 reason 说明首个违规，
        diff_head 为 unified diff 前 40 行（ok=True 时为空串）。
    """
    orig_lines = original.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    # 读入无损自检：keepends 拼接 == 原文（防上游读入环节吞字节）
    if "".join(orig_lines) != original or "".join(new_lines) != new_text:
        return False, "readback mismatch: splitlines(keepends) join != 原文（行尾/编码异常）", ""

    sm = difflib.SequenceMatcher(a=orig_lines, b=new_lines, autojunk=False)
    inserted_parts: list[str] = []
    for tag, _i1, _i2, j1, j2 in sm.get_opcodes():
        if tag in ("delete", "replace"):
            near = orig_lines[_i1][_i2] if False else (orig_lines[_i1].rstrip() if _i1 < len(orig_lines) else "")
            return (
                False,
                f"non-insert opcode: {tag} near L{_i1 + 1} ({near[:40]!r})——"
                "纯插入校验失败：新文本删除/改动了原文行（正则失配？缩进漏配？行尾翻转？）",
                _diff_head(orig_lines, new_lines),
            )
        if tag == "insert":
            inserted_parts.extend(new_lines[j1:j2])

    # 插入段拼接 == 调用方声称的 blocks（blocks 未给定时跳过该自检）
    if blocks is not None:
        claimed = "".join(
            b if b.endswith("\n") else b + "\n" for b in blocks
        )
        actual = "".join(inserted_parts)
        if actual != claimed:
            return (
                False,
                "inserted-content mismatch: 实际插入段与声称的 blocks 不一致"
                "（锚点位置漂移？块内换行差异？）",
                _diff_head(orig_lines, new_lines),
            )

    return True, "", ""


def insert_blocks(
    path: str | Path,
    blocks: list[str],
    *,
    after_lines: list[str] | None = None,
    repo_root: str | Path | None = None,
    yaml_assert: bool = True,
    newline: str = "\n",
) -> RegistryEditResult:
    """登记表纯插入式批量编辑唯一写入口。

    流程：读原文 → 构造新文本（每块插到 after_lines 末个锚点行之后；after_lines
    为空 = 追加到文件尾）→ verify_pure_insertion → YAML 双断言 → CAS 落盘。
    任一环节失败：不落盘，返回 ok=False（diff_head 给现场）。

    Args:
        path: 登记表路径（相对 repo_root 或绝对）。
        blocks: 待插入文本块（每个块 = 一段完整原文，通常为 YAML 条目）。
        after_lines: 锚点行原文列表（整行语义匹配，忽略首尾空白/行尾符差异；
            插入位置 = 列表中最后一个命中的锚点行之后；空/None = 追加文件尾）。
            锚点命中 0 次 = 拒绝。注意：锚点行必须是 YAML 条目边界行（如
            "- gate_id: XXX" 条目首行）——在条目中间插入会把该条目拦腰截断。
        repo_root: 仓根（CAS 审计锚定）；None 自动推导。
        yaml_assert: YAML 双断言开关（两侧可解析 + 条目数只增不减）。
        newline: 行尾策略（默认 "\\n"——登记表 .gitattributes 钉 LF 约定）。

    Returns:
        RegistryEditResult（ok=False 时 reason/diff_head 携带现场）。
    """
    target = Path(path)
    try:
        original = target.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001 — 读失败不落盘
        return RegistryEditResult(False, str(target), 0, 0, len(blocks), f"read failed: {e}", "")

    # 行尾域语义（2026-09-09 clearance-night T5 二次裁定）：
    # 仓库 .gitattributes 全局 `* text=auto eol=lf`——git 侧规范形态恒为 LF，
    # 工作区磁盘上的 CRLF 字节是历史噪声（commit 时被 git 归一化，+N 行零删除
    # 实证）。因此本工具内存域统一 LF（universal-newlines 读入即 LF + blocks
    # 用 \n），落盘 newline="\n"，回读校验同域——hash 必然一致。
    # （曾试过"探测 CRLF→写回 CRLF"：read_text 读入吞 \r\n 致回读 hash 恒不等，
    # WriteVerificationError 误拒——该路径已删除，勿回退。）

    # 定位插入点：最后一个命中的锚点行之后；无锚点 = 文件尾
    orig_lines = original.splitlines(keepends=True)
    insert_at = len(orig_lines)
    if after_lines:
        anchor_idx: int | None = None
        for anchor in after_lines:
            norm_anchor = anchor.rstrip("\r\n").lstrip()
            for i, line in enumerate(orig_lines):
                # 整行语义匹配（忽略首尾空白差异+行尾符），防子串误配
                # （gate_id 锚点命中 entry 内部会把 YAML 条目拦腰截断——锚点
                # 必须是完整行，匹配后校验目标行与锚点 strip 后全等）
                if line.rstrip("\r\n").lstrip() == norm_anchor:
                    anchor_idx = i  # 取最后一个命中
        if anchor_idx is None:
            reason = f"anchor not found: after_lines 全部未命中（共 {len(after_lines)} 个锚点）——正则失配同类风险，拒绝写入"
            return RegistryEditResult(
                False, str(target), len(orig_lines), len(orig_lines), len(blocks), reason,
                _diff_head(orig_lines, orig_lines),
            )
        insert_at = anchor_idx + 1

    new_lines = orig_lines[:insert_at]
    for b in blocks:
        new_lines.extend((b if b.endswith("\n") else b + "\n").splitlines(keepends=True))
    new_lines.extend(orig_lines[insert_at:])
    new_text = "".join(new_lines)

    # 纯插入校验（含 blocks 一致性自检）
    ok, reason, diff = verify_pure_insertion(original, new_text, blocks)
    if not ok:
        return RegistryEditResult(
            False, str(target), len(orig_lines), len(new_lines), 0, reason, diff
        )

    # YAML 双断言：两侧可解析 + 条目数只增不减
    if yaml_assert:
        n_orig = _yaml_entry_count(original)
        n_new = _yaml_entry_count(new_text)
        if n_orig is None or n_new is None:
            return RegistryEditResult(
                False, str(target), len(orig_lines), len(new_lines), 0,
                "yaml parse failed: 原文或新文本无法 yaml.safe_load（登记表必须是合法 YAML）",
                _diff_head(orig_lines, new_lines),
            )
        if n_new < n_orig:
            return RegistryEditResult(
                False, str(target), len(orig_lines), len(new_lines), 0,
                f"yaml entries shrank: {n_orig} -> {n_new}（条目数减少，疑似蒸发）",
                _diff_head(orig_lines, new_lines),
            )

    # CAS 落盘（base=读入原文 hash；磁盘被他人推进 → StaleWriteRefused 拒写）
    try:
        safe_write_text(
            target,
            new_text,
            expected_base_sha256=content_sha256(original),
            repo_root=repo_root,
            newline=newline,
        )
    except Exception as e:  # noqa: BLE001 — CAS 拒写/校验失败不重试不绕过
        return RegistryEditResult(
            False, str(target), len(orig_lines), len(new_lines), 0,
            f"safe_write_text refused: {type(e).__name__}: {e}",
            "",
        )

    return RegistryEditResult(
        True, str(target), len(orig_lines), len(new_lines), len(blocks), "", ""
    )


def _parse_blocks_file(blocks_path: Path) -> list[str]:
    """块文件解析：以 "===== BLOCK N =====" 行分隔。"""
    text = blocks_path.read_text(encoding="utf-8")
    blocks: list[str] = []
    cur: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith(_BLOCK_SEP):
            if cur:
                blocks.append("".join(cur))
                cur = []
            continue
        cur.append(line)
    if cur:
        blocks.append("".join(cur))
    return blocks


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="登记表纯插入式批量编辑工具（防蒸发）")
    ap.add_argument("--file", required=True, help="登记表 YAML 路径")
    ap.add_argument("--blocks-file", help="插入块文件（===== BLOCK N ===== 分隔）")
    ap.add_argument("--after-line", action="append", default=[], help="锚点行原文（可多次；缺省=追加文件尾）")
    ap.add_argument("--verify-only", action="store_true", help="只校验纯插入可行性（对现有文件做无插入自检），零写入")
    ap.add_argument("--no-yaml-assert", action="store_true", help="跳过 YAML 条目数断言（非 YAML 文本慎用）")
    args = ap.parse_args()

    if args.verify_only:
        p = Path(args.file)
        original = p.read_text(encoding="utf-8")
        ok, reason, diff = verify_pure_insertion(original, original, blocks=[])
        print("VERIFY-ONLY:", "OK（文件自我纯插入校验通过/读入无损）" if ok else f"FAIL: {reason}\n{diff}")
        return 0 if ok else 1

    if not args.blocks_file:
        ap.error("--blocks-file 或 --verify-only 必须提供一个")
    blocks = _parse_blocks_file(Path(args.blocks_file))
    if not blocks:
        print("FAIL: 块文件解析出 0 个块")
        return 1
    result = insert_blocks(
        args.file,
        blocks,
        after_lines=args.after_line or None,
        yaml_assert=not args.no_yaml_assert,
    )
    if result.ok:
        print(
            f"OK: {result.path} | {result.original_lines} -> {result.final_lines} 行 "
            f"| 插入 {result.inserted_blocks} 块"
        )
        return 0
    print(f"REJECTED: {result.reason}")
    if result.diff_head:
        print(result.diff_head)
    return 1


if __name__ == "__main__":
    sys.exit(main())
