# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §commit navigation guide
# [MODULE] scripts.governance.generators.generate_commit_guide
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib(argparse/hashlib/pathlib/re/sys); yaml; zephyr.shared.io.file_utils(safe_write_text); zephyr.shared.utils.time_utils(now_utc)
# [CONSUMERS] docs/01_policies_and_standards/sop/governance_sop/commit_navigation_playbook.md (机生产物), scripts/governance/d3_metadata/batch_creation_tokens.py (递送接口), scripts/git_commit.py (死因锚点)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 指南唯一产出通道（禁手写第二真源）——正文全部由四源机生：in_process_gate_registry.yaml(在册台目真源)+gate_digest_registry.yaml(判据蒸馏层)+file_type_checklists_registry.yaml(类型清单层)+death_cases_registry.yaml(死因案例层)；硬校验三道——①gate_refs/案例 gate 必须在（in_process 注册表 ∪ digest ∪ 已知钩子阶段名）否则生成失败；②digest entry 的 source_file 必须实存否则生成失败；③source_sha256 与现源不符的台目在指南顶部出"待重蒸馏"横幅+逐台 ⚠（机生新鲜度闸，指南永不无声过期）；在册但无 digest 条目的台目自动列入附录"待蒸馏清单"（覆盖面完整可见）；输出经 safe_write_text 原子写；--check 校验模式零写盘（CI 可挂）；--refresh-hashes 蒸馏确认后同步哈希（纯插入文本编辑，不动既有行）
# [MODIFY-GUARD] gate_id="COMMIT-GUIDE-GENERATOR"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验失败 exit 1 并逐条列出问题；永不半写（safe_write_text 原子）；源 YAML 解析失败直接抛出（带文件名定位）
# [TESTS] tests/governance/generators/test_generate_commit_guide.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""generate_commit_guide — 提交指路指南机生器（拦截成本前移为指引成本）。

病根（2026-09-22/23 死信战役实证，112 封死信 P50 损失 10.8min/封）：
门禁判据散落在 116 个 gate 源码 docstring + 注册表 YAML 里，AI 会话不预读
→撞墙后才从死信文案学判据 →同一类墙反复撞（chainpile basename 三连死、
k4 搬移三连死、sweep no-lookup reason 两连死）。Owner 定调：
「规范从事后拦截前移为事前导航，指南由门禁配置机生、禁手写第二真源」。

用法::

    # 生成/刷新指南（校验+写盘）
    python scripts/governance/generators/generate_commit_guide.py

    # 只校验不写盘（CI/入队前自检）
    python scripts/governance/generators/generate_commit_guide.py --check

    # 蒸馏确认后同步判据源哈希（人工核对 digest 内容后执行）
    python scripts/governance/generators/generate_commit_guide.py --refresh-hashes

递送接口（②）：
- batch_creation_tokens.py --emit-guide <path>：按路径类型打印对应 checklist 段
- git_commit.py 预检失败：死因文案附带指南锚点（gate 名 → 指南章节）

锚点约定：指南内 gate 卡片标题为纯 ASCII 的 `### <GATE_ID>`，
类型节标题为 `## FT-<type_id>`；接口方按子串检索定位，不依赖 URL slug。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[3]
_SOURCES_DIR = _REPO / "docs/01_policies_and_standards/sop/governance_sop/commit_guide_sources"
_REGISTRY_PATH = _REPO / "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml"
_OUTPUT_PATH = _REPO / "docs/01_policies_and_standards/sop/governance_sop/commit_navigation_playbook.md"
# 非注册台但真实存在的钩子阶段/机制名（死因文案里出现，允许被引用）
_EXTRA_KNOWN_GATES = {"GATE-PRECOMMIT-RUN", "QUEUE-MECHANICS"}
_GENERATE_CMD = "python scripts/governance/generators/generate_commit_guide.py"


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _sha256_of(path: Path) -> str:
    """判据源新鲜度锚=HEAD 已提交字节（在途未提交编辑不触发漂移横幅）；git 失败回退盘面。"""
    rel = path.relative_to(_REPO).as_posix()
    head_bytes = _head_blob_bytes(rel)
    data = head_bytes if head_bytes is not None else path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def _head_blob_bytes(rel: str) -> bytes | None:
    import subprocess  # noqa: PLC0415

    flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
    try:
        r = subprocess.run(  # noqa: bare-subprocess  HEAD blob 只读取直取带 NO_WINDOW 防弹窗，非 spawn python
            ["git", "show", f"HEAD:{rel}"],
            capture_output=True,
            cwd=str(_REPO),
            creationflags=flags,
        )
        if r.returncode == 0:
            return r.stdout
    except Exception:  # noqa: BLE001 — git 不可达回退盘面哈希
        return None
    return None


def _checklist_ref_problems(known: set[str], checklists: dict) -> list[str]:
    """类型清单 gate 引用校验（universal + file_types）。"""
    problems: list[str] = []
    uni = checklists.get("universal", {}) or {}
    for ref in uni.get("gate_refs", []) or []:
        if ref not in known:
            problems.append(f"universal.gate_refs 引用未在册 gate: {ref}")
    for sec in checklists.get("file_types", []):
        for ref in sec.get("gate_refs", []) or []:
            if ref not in known:
                problems.append(f"file_types[{sec.get('type_id')}].gate_refs 引用未在册 gate: {ref}")
        for death in sec.get("common_deaths", []) or []:
            g = death.get("gate")
            if g and g not in known:
                problems.append(f"file_types[{sec.get('type_id')}].common_deaths 引用未在册 gate: {g}")
    return problems


def _collect_validation_problems(
    registry_ids: set[str],
    digest_gates: list[dict],
    checklists: dict,
    cases: list[dict],
) -> list[str]:
    """三道硬校验，返回问题清单（空=通过）。"""
    known = registry_ids | {g["gate_id"] for g in digest_gates} | _EXTRA_KNOWN_GATES
    problems = _checklist_ref_problems(known, checklists)
    for case in cases:
        g = case.get("gate")
        if g and g not in known:
            problems.append(f"death_cases[{case.get('case_id')}].gate 引用未在册 gate: {g}")
    for entry in digest_gates:
        src = _REPO / entry.get("source_file", "")
        if not src.exists():
            problems.append(f"gate_digest[{entry.get('gate_id')}].source_file 不存在: {entry.get('source_file')}")
    return problems


def _freshness_report(digest_gates: list[dict]) -> tuple[list[str], list[str]]:
    """返回 (drifted_gate_ids, unhashed_gate_ids)。"""
    drifted: list[str] = []
    unhashed: list[str] = []
    for entry in digest_gates:
        src = _REPO / entry.get("source_file", "")
        if not src.exists():
            continue
        recorded = entry.get("source_sha256")
        if not recorded:
            unhashed.append(entry["gate_id"])
        elif recorded != _sha256_of(src):
            drifted.append(entry["gate_id"])
    return drifted, unhashed


def _invalidate_hashes(digest_path: Path) -> None:
    """把全部 source_sha256 改写为占位（配合 --refresh-hashes --force 全量重锚）。"""
    from zephyr.shared.io.file_utils import safe_write_text

    text = digest_path.read_text(encoding="utf-8")
    new_text, n = re.subn(r"^(\s*source_sha256: )([0-9a-f]{64})$", r"\1pending-refresh", text, flags=re.M)
    if n:
        safe_write_text(digest_path, new_text)


def _needs_hash(entry: dict) -> bool:
    recorded = entry.get("source_sha256")
    return not (recorded and re.fullmatch(r"[0-9a-f]{64}", str(recorded)))


def _flush_pending_hash(out: list[str], state: dict, targets: dict) -> int:
    """entry 块结束：待补哈希且块内未补 → 块尾补插。"""
    gid = state["gid"]
    if gid and not state["patched"] and gid in targets:
        out.append(f"{state['indent']}  source_sha256: {targets[gid][1]}")
        return 1
    return 0


def _patch_hash_line(line: str, state: dict, targets: dict, out: list[str]) -> int:
    """单行哈希补丁状态机（_refresh_hashes helper）。

    gate_id 行=切换 entry 并刷新 state；哈希行=无效时就地替换；其余行原样透传。
    """
    m = re.match(r"^(\s*)- gate_id: (\S+)\s*$", line)
    if m:
        patched = _flush_pending_hash(out, state, targets)
        state["gid"] = m.group(2)
        state["indent"] = m.group(1)
        state["patched"] = False
        out.append(line)
        return patched
    gid = state["gid"]
    if gid and not state["patched"] and gid in targets and re.match(r"^\s*source_sha256:", line):
        out.append(re.sub(r"^(\s*)source_sha256:.*$", rf"\1source_sha256: {targets[gid][1]}", line))
        state["patched"] = True
        return 1
    out.append(line)
    return 0


def _refresh_hashes(digest_path: Path) -> int:
    """把现源哈希写进 digest 各 entry：entry 块内已有哈希行就地替换，否则块尾补插（CAS 保护）。"""
    from zephyr.shared.io.file_utils import safe_write_text

    data = _load_yaml(digest_path)
    targets: dict[str, tuple[str, str]] = {}
    for entry in data.get("gates", []):
        src = _REPO / entry.get("source_file", "")
        if src.exists() and _needs_hash(entry):
            targets[entry["gate_id"]] = (str(src), _sha256_of(src))
    lines = digest_path.read_text(encoding="utf-8").split("\n")
    out: list[str] = []
    patched = 0
    state: dict = {"gid": None, "indent": "", "patched": False}
    for line in lines:
        patched += _patch_hash_line(line, state, targets, out)
    patched += _flush_pending_hash(out, state, targets)
    safe_write_text(digest_path, "\n".join(out))
    return patched


def _render_gate_card(entry: dict, drifted: set[str]) -> list[str]:
    gid = entry["gate_id"]
    flag = " ⚠️待重蒸馏(判据源已漂移)" if gid in drifted else ""
    mode = {"block": "硬阻断", "warn": "warn-only", "conditional": "分级/条件"}.get(
        entry.get("block_or_warn", ""), entry.get("block_or_warn", "")
    )
    lines = [
        f"### {gid}{flag}",
        "",
        f"- 强度: {mode}",
        f"- 触发面: {entry.get('trigger', '')}",
        f"- 判据: {entry.get('enforce', '')}",
        f"- 豁免: {entry.get('exempt', '')}",
        f"- 处方: {entry.get('fix', '')}",
        f"- 判据源: `{entry.get('source_file', '')}`",
        "",
    ]
    return lines


class _RenderCtx:
    """渲染上下文（四源装载+校验+新鲜度一次性计算）。"""

    def __init__(self) -> None:
        registry = _load_yaml(_REGISTRY_PATH)
        digest = _load_yaml(_SOURCES_DIR / "gate_digest_registry.yaml")
        self.checklists = _load_yaml(_SOURCES_DIR / "file_type_checklists_registry.yaml")
        cases_doc = _load_yaml(_SOURCES_DIR / "death_cases_registry.yaml")
        self.registry_gates = registry["gates"]
        self.registry_ids = {g["gate_id"] for g in self.registry_gates}
        disabled = {g["gate_id"] for g in self.registry_gates if g.get("enabled") is False}
        if disabled:
            raise SystemExit(
                f"指南生成校验失败: 注册表存在 enabled:false 死门: {sorted(disabled)}（蒸馏面与死门必须显式分家）"
            )
        self.digest_gates = digest["gates"]
        self.cases = cases_doc.get("cases", [])
        problems = _collect_validation_problems(self.registry_ids, self.digest_gates, self.checklists, self.cases)
        if problems:
            raise SystemExit(
                "指南生成校验失败（禁手写第二真源——请修源头册而非指南）:\n" + "\n".join(f"  - {p}" for p in problems)
            )
        self.drifted, self.unhashed = _freshness_report(self.digest_gates)
        self.drifted_set = set(self.drifted)
        digest_ids = {g["gate_id"] for g in self.digest_gates}
        self.pending = sorted(self.registry_ids - digest_ids)
        self.digest_by_id = {g["gate_id"]: g for g in self.digest_gates}
        self.ordered = [g for g in self.registry_gates if g["gate_id"] in self.digest_by_id]

    def gate_card(self, gate_id: str) -> list[str]:
        entry = self.digest_by_id.get(gate_id)
        return _render_gate_card(entry, self.drifted_set) if entry else []


def _render_header(ctx: _RenderCtx, ts: str) -> list[str]:
    out = [
        "---",
        "ttl: permanent",
        'title: "提交指路指南（机生版）"',
        "doc_type: policy",
        "---",
        "",
        "# 提交指路指南（机生版）",
        "",
        "> **本文件由生成器产出，禁手改**——改判据请改源头册后重跑生成器。",
        f"> 生成器: `{_GENERATE_CMD}` ｜ 生成时刻: {ts}",
        "> 源册: gate_digest_registry.yaml（判据蒸馏）/ file_type_checklists_registry.yaml（类型清单）/ death_cases_registry.yaml（死因案例）/ in_process_gate_registry.yaml（在册台目）",
    ]
    banner = []
    if ctx.drifted:
        banner.append(f"**⚠️ {len(ctx.drifted)} 台判据源已漂移待重蒸馏**: {', '.join(ctx.drifted)}")
    if ctx.unhashed:
        banner.append(
            f"**{len(ctx.unhashed)} 台未记录判据源哈希**（跑 --refresh-hashes 同步）: {', '.join(ctx.unhashed)}"
        )
    if ctx.pending:
        banner.append(f"**{len(ctx.pending)} 台在册未蒸馏**（附录 B）: {', '.join(ctx.pending)}")
    if banner:
        out.extend(["", "> " + " ｜ ".join(banner)])
    out.extend(["", "锚点约定：gate 卡片标题=`### <GATE_ID>`，类型节=`## FT-<type_id>`；接口按子串检索。", ""])
    return out


def _render_universal(ctx: _RenderCtx) -> list[str]:
    uni = ctx.checklists.get("universal", {}) or {}
    out = ["## FT-universal — 每一笔提交的通用前置", ""]
    out.extend(f"1. {s}" for s in uni.get("steps", []) or [])
    out.append("")
    for ref in uni.get("gate_refs", []) or []:
        out.extend(ctx.gate_card(ref))
    out.extend(["---", ""])
    return out


def _render_one_type(ctx: _RenderCtx, sec: dict) -> list[str]:
    out = [f"## FT-{sec.get('type_id')} — {sec.get('title', '')}", "", f"判定口诀: {sec.get('match_hint', '')}", ""]
    out.extend(f"1. {s}" for s in sec.get("steps", []) or [])
    if sec.get("common_deaths"):
        out.extend(["", "**本类常见死因**（案例册全量见文末速查）:"])
        out.extend(
            f"- [{d.get('gate', '')}] {d.get('case', '')} → {d.get('prescription', '')}" for d in sec["common_deaths"]
        )
    out.append("")
    for ref in sec.get("gate_refs", []) or []:
        out.extend(ctx.gate_card(ref))
    out.extend(["---", ""])
    return out


def _render_types_and_extra(ctx: _RenderCtx) -> list[str]:
    out: list[str] = []
    for sec in ctx.checklists.get("file_types", []) or []:
        out.extend(_render_one_type(ctx, sec))
    extra = ctx.checklists.get("extra_registry", {}) or {}
    if extra:
        out.extend([f"## FT-extra-registry — {extra.get('title', '')}", ""])
        out.extend(f"- {it}" for it in extra.get("items", []) or [])
        out.extend(["", "---", ""])
    return out


def _cost_minutes(case: dict) -> float:
    """案例成本解析（cost_note 中 P50 分钟数；无数字沉底，红队 F2 治本=真数值排序）。"""
    m = re.search(r"P50\s*([0-9.]+)min", str(case.get("cost_note", "")))
    return float(m.group(1)) if m else 0.0


def _render_cases(cases: list[dict]) -> list[str]:
    out = [
        "## DEATH-CASES — 死因处方速查（按实测成本排序）",
        "",
        "成本口径=created_at 到 dead_at 分钟（含排队等待）；样本=2026-09-22/23 死信 112 封。",
        "",
    ]
    for c in sorted(cases, key=_cost_minutes, reverse=True):
        out.append(f"### CASE-{c.get('case_id')}")
        out.append("")
        out.append(f"- 症状: {c.get('symptom', '')}")
        out.append(f"- 关联门禁: {c.get('gate', '')}")
        out.append(f"- 机制: {c.get('root_cause', '')}")
        out.append(f"- 处方: {c.get('prescription', '')}")
        if c.get("cost_note"):
            out.append(f"- 实测成本: {c.get('cost_note')}")
        if c.get("evidence"):
            out.append(f"- 证据: {', '.join(c.get('evidence', []))}")
        out.append("")
    out.extend(["---", ""])
    return out


def _render_appendix_a(ctx: _RenderCtx) -> list[str]:
    out = ["## APPENDIX-A — 全台速查表", "", "| gate | 强度 | 触发面（一句） | 处方（一句） |", "|---|---|---|---|"]
    for g in ctx.ordered:
        e = ctx.digest_by_id[g["gate_id"]]
        fix_short = str(e.get("fix", "")).split("；")[0][:80]
        out.append(
            f"| {g['gate_id']} | {e.get('block_or_warn', '')} | {str(e.get('trigger', ''))[:60]} | {fix_short} |"
        )
    extras = [g for g in ctx.digest_gates if g.get("registry") is False or g["gate_id"] not in ctx.registry_ids]
    for e in extras:
        fix_short = str(e.get("fix", "")).split("；")[0][:80]
        out.append(
            f"| {e['gate_id']}（机制红线） | {e.get('block_or_warn', '')} | {str(e.get('trigger', ''))[:60]} | {fix_short} |"
        )
    out.append("")
    return out


def _render_appendix_bc(ctx: _RenderCtx) -> list[str]:
    out = ["## APPENDIX-B — 在册未蒸馏台目（生成器自动清点，蒸馏后重跑）", ""]
    out.extend([f"- {pid}" for pid in ctx.pending] if ctx.pending else ["（无——在册全覆盖）"])
    out.extend(["", "## APPENDIX-C — 判据源新鲜度快照", ""])
    out.append(f"- 漂移待重蒸馏: {len(ctx.drifted)} 台{('：' + ', '.join(ctx.drifted)) if ctx.drifted else ''}")
    out.append(f"- 未记录哈希: {len(ctx.unhashed)} 台{('：' + ', '.join(ctx.unhashed)) if ctx.unhashed else ''}")
    out.append(f"- 在册覆盖: {len(ctx.ordered)}/{len(ctx.registry_ids)}")
    out.append("")
    return out


def _render() -> str:
    ctx = _RenderCtx()
    from zephyr.shared.utils.time_utils import now_utc

    ts = now_utc().strftime("%Y-%m-%d %H:%M UTC")
    out: list[str] = []
    out.extend(_render_header(ctx, ts))
    out.extend(_render_universal(ctx))
    out.extend(_render_types_and_extra(ctx))
    out.extend(_render_cases(ctx.cases))
    out.extend(_render_appendix_a(ctx))
    out.extend(_render_appendix_bc(ctx))
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="提交指路指南机生器（禁手写第二真源）")
    parser.add_argument("--check", action="store_true", help="只校验+渲染，零写盘")
    parser.add_argument("--refresh-hashes", action="store_true", help="蒸馏确认后同步判据源哈希到 digest 册")
    parser.add_argument(
        "--force",
        action="store_true",
        help="与 --refresh-hashes 连用：强制重写全部哈希（哈希基底切换时用，如盘面锚改 HEAD 锚）",
    )
    parser.add_argument(
        "--confirm-redistilled",
        action="store_true",
        help="与 --force 连用：声明已逐台重蒸馏 digest 内容（防静默清零漂移横幅，红队 F3 治本）",
    )
    parser.add_argument("--output", default=str(_OUTPUT_PATH), help="输出路径（默认正式 SOP 位）")
    args = parser.parse_args(argv)
    if args.refresh_hashes:
        if args.force and not getattr(args, "confirm_redistilled", False):
            raise SystemExit(
                "--force 会把全部漂移横幅静默清零——仅限已逐台人工重蒸馏 digest 内容后使用；"
                "确认完成重蒸馏请追加 --confirm-redistilled"
            )
        if args.force:
            _invalidate_hashes(_SOURCES_DIR / "gate_digest_registry.yaml")
        patched = _refresh_hashes(_SOURCES_DIR / "gate_digest_registry.yaml")
        print(f"source_sha256 同步完成: {patched} 台")
        return 0
    text = _render()
    if args.check:
        print("校验通过，渲染 OK（--check 零写盘），长度", len(text))
        return 0
    from zephyr.shared.io.file_utils import safe_write_text

    result = safe_write_text(Path(args.output), text)
    print(f"指南已机生: {result.path} ({len(text)} 字符, written={result.written})")
    return 0


# noqa: m11-perm-manual-legitimate  M11豁免: 指南机生器=manual CLI（会话/CI 显式触发，非 cron/daemon），禁手写第二真源通道需按需重跑
if __name__ == "__main__":
    sys.exit(main())
