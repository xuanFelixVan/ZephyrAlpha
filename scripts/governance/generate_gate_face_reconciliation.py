# [BLUEPRINT] MOD-GATE_ENGINE | src/zephyr/gov_enforcement/rule_bridge/gate_auto_registrar.py | §装载面
# [MODULE] scripts.governance.generate_gate_face_reconciliation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.file_utils; scripts.governance._shared.encoding; zephyr.gov_enforcement.rule_bridge.gate_auto_registrar; zephyr.gov_enforcement.rule_bridge.commit_gate_registry; zephyr.shared.io.paths (REPO_ROOT 仓根唯一真源); zephyr.shared.infra.process_pool (run_subprocess_hidden); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 触发面三列对账表生成器（波 1A.3，2026-09-27 st-chief4x-govtool-20260927）：机生禁手改（宪法 §9.5 静态清单禁手工维护），一张表收敛三悬案——名册声明 vs 进程内实载（103/104 vs 99 悬案）、CREATE-GUARD files_trigger 空每链全跑（实测 1519 次/19186s）、密钥门死触发（预跑器自打印 files_trigger 死触发）。行=名册（in_process_gate_registry.yaml）每台门：①名册声明（gate_id+enabled）②进程内实载（auto_register_gates 真装载进 CommitGateRegistry，fail-closed 异常捕获后仍清点 list_gate_ids）③files_trigger 在 HEAD 树命中文件数（四路语义真源=commit_gate_registry._files_trigger_hit，单条目移植=gate_auto_registrar._trigger_hit，禁本地重写防语义漂移）。红名单三态：R1 声明 enabled 而实载 0；R2 files_trigger 空（每链全跑）；R3 files_trigger 声明而 HEAD 树命中 0（死触发）。enabled=false=声明禁用 informational 段不进红名单；实载有名册无（逆向面）非空即红。对账表=只读报告件，禁据此改任何门禁 enabled 态（flag 翻转=Owner 门位）。计数一律字段承载禁写死散文（宪法 §4.3）
# [MODIFY-GUARD] gate_id="N/A"（只读报告生成器，非门禁）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 名册缺失/损坏=GateAutoRegistrationError 透传 rc=2（fail-closed 对齐裁定#351）；git 面不可用（ls-tree 失败）=rc=2 拒绝出表（命中数列失真即表失真，禁降级出坏表）；写文件走 atomic_write_if_changed（内容未变不落盘，幂等可复算）
# [TESTS] tests/governance/test_generate_gate_face_reconciliation.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
generate_gate_face_reconciliation.py — 触发面三列对账表生成器（波 1A.3）

一张表同时收敛三个悬案（10_wave_plan.md §1A.3）：
1. 名册声明 vs 进程内实载（名册 103/104 vs 实载 99）
2. CREATE-GUARD 因 files_trigger 空 每链全跑（实测 1519 次/19186s）
3. 密钥门 files_trigger 路径子串匹配恒零命中（死触发）

三列口径
--------
- 名册声明：docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml
  每 entry（gate_id / enabled / files_trigger 声明）。
- 进程内实载：gate_auto_registrar.auto_register_gates 真装载（import→getattr→factory→register）
  进 CommitGateRegistry 后 list_gate_ids()；fail-closed 异常捕获记录、仍清点已装载集合。
- files_trigger HEAD 命中：git ls-tree -r HEAD 全树 × 名册声明 pattern（四路语义复用真源移植）。

红名单（--check 红非空 rc=1）：R1 声明有实载 0｜R2 触发面空（每链全跑）｜R3 死触发（命中 0）。

Usage::

    python scripts/governance/generate_gate_face_reconciliation.py            # 出表（md+yaml）
    python scripts/governance/generate_gate_face_reconciliation.py --check    # 只判红，rc 语义
    python scripts/governance/generate_gate_face_reconciliation.py --output-dir DIR

退出码：0=红名单空；1=红名单非空；2=环境/真源错误。产出为只读报告件，
禁据此改任何门禁 enabled 态（flag 翻转=Owner 门位，宪法 §5）。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

_SCRIPTS_GOVERNANCE = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_GOVERNANCE))

# _SRC_BOOTSTRAP 只为 import 定位本 worktree 的包面（防 editable 安装把 zephyr 硬锚主仓），
# 仓根本身**不在此重算**——REPO_ROOT 真源=zephyr.shared.io.paths（SSOT-REDEFINITION 对症）。
_SRC_BOOTSTRAP = _SCRIPTS_GOVERNANCE.parents[1] / "src"
if _SRC_BOOTSTRAP.exists() and str(_SRC_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_SRC_BOOTSTRAP))

from _shared.encoding import ensure_utf8_stdout  # noqa: E402
from _shared.file_utils import atomic_write_if_changed  # noqa: E402

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry  # noqa: E402
from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import (  # noqa: E402
    GateAutoRegistrationError,
    _head_tracked_relpaths,
    _read_roster,
    _trigger_hit,
    auto_register_gates,
)
from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: E402  trae_067 铁律2 无窗子进程统一入口
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓根唯一真源（原为本地 parents 重定义）
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

__manifest__ = """
dimensions: [D1, D5]
priority: P2
timeout_seconds: 120
args:
  - {flag: --check, type: bool, description: "只判红名单不出表（rc 1=红非空）"}
  - {flag: --output-dir, type: str, description: "输出目录（默认 docs/01_policies_and_standards/_registry/reports）"}
  - {flag: --json, type: bool, description: "stdout 附机器可读 JSON 摘要"}
warn_only: false
"""

OUTPUT_REL_DIR = Path("docs/01_policies_and_standards/_registry/reports")
OUTPUT_MD = OUTPUT_REL_DIR / "gate_face_reconciliation.md"
OUTPUT_YAML = OUTPUT_REL_DIR / "gate_face_reconciliation.yaml"
GENERATOR_REL = "scripts/governance/generate_gate_face_reconciliation.py"

#: 红名单三态标识（口径唯一真源=本表，判据=10_wave_plan.md §1A.3）
RED_DECLARED_NOT_LOADED = "R1-declared-but-not-loaded"
RED_TRIGGER_EMPTY = "R2-trigger-empty-always-run"
RED_TRIGGER_DEAD = "R3-trigger-dead-zero-hit"
RED_LOADED_NOT_DECLARED = "R0-loaded-but-not-declared"


def _head_commit(repo_root: Path) -> str:
    """HEAD 全 sha（表头溯源用）；git 面不可用=unknown（命中数另有拒出表闸，见 main）。

    BARE-SUBPROCESS 治本：改走 process_pool.run_subprocess_hidden（trae_067 铁律2
    CREATE_NO_WINDOW 统一入口）。该入口默认 capture_output=True + text=True，stdout
    已是 str——原写法是 bytes 再 decode，取值逐字相同（rev-parse 仅一行 sha）。
    """
    out = run_subprocess_hidden(["git", "rev-parse", "HEAD"], cwd=str(repo_root), timeout=15)
    return (out.stdout or "").strip() if out.returncode == 0 else "unknown"


def build_rows(
    entries: list[dict[str, Any]],
    loaded_ids: set[str],
    tracked: set[str],
) -> list[dict[str, Any]]:
    """组行：每台门一行三列（名册声明/进程内实载/HEAD 命中数）。行序=名册物理序（裁定时间序惯例）。"""
    rows: list[dict[str, Any]] = []
    for entry in entries:
        gate_id = str(entry.get("gate_id", "?"))
        enabled = bool(entry.get("enabled", True))
        patterns = [p for p in entry.get("files_trigger") or [] if isinstance(p, str)]
        per_pattern = {p: sum(1 for rel in tracked if _trigger_hit(p, rel)) for p in patterns}
        hit_files = len({rel for rel in tracked if any(_trigger_hit(p, rel) for p in patterns)}) if patterns else 0
        rows.append(
            {
                "gate_id": gate_id,
                "enabled": enabled,
                "loaded_in_process": gate_id in loaded_ids,
                "files_trigger": patterns,
                "trigger_mode": "conditional" if patterns else "always-run",
                "head_hit_files": hit_files,
                "per_pattern_hits": per_pattern,
                "dead_trigger": bool(patterns) and hit_files == 0,
            }
        )
    return rows


def derive_red_rows(rows: list[dict[str, Any]], loaded_ids: set[str], declared_ids: set[str]) -> list[dict[str, str]]:
    """红名单：R1 声明 enabled 实载 0｜R2 触发面空｜R3 死触发｜R0 实载有名册无（逆向面）。"""
    reds: list[dict[str, str]] = []
    for r in rows:
        if r["enabled"] and not r["loaded_in_process"]:
            reds.append(
                {"gate_id": r["gate_id"], "kind": RED_DECLARED_NOT_LOADED, "detail": "声明 enabled 而进程内实载 0"}
            )
        if r["enabled"] and r["trigger_mode"] == "always-run":
            reds.append(
                {
                    "gate_id": r["gate_id"],
                    "kind": RED_TRIGGER_EMPTY,
                    "detail": "files_trigger 空=每链全跑（1A.3 悬案②同款）",
                }
            )
        if r["dead_trigger"]:
            reds.append(
                {
                    "gate_id": r["gate_id"],
                    "kind": RED_TRIGGER_DEAD,
                    "detail": f"files_trigger 声明 {len(r['files_trigger'])} 条 HEAD 树命中 0（死触发）",
                }
            )
    for gid in sorted(loaded_ids - declared_ids):
        reds.append({"gate_id": gid, "kind": RED_LOADED_NOT_DECLARED, "detail": "进程内实载有名册无（逆向面）"})
    return reds


def render_markdown(
    rows: list[dict[str, Any]],
    reds: list[dict[str, str]],
    disabled_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> str:
    lines: list[str] = [
        "---",
        "ttl: permanent",
        "doc_type: register",
        "module_id: RPT-GATE-FACE-RECONCILIATION",
        f"generated_by: {GENERATOR_REL}",
        "regenerate: python scripts/governance/generate_gate_face_reconciliation.py",
        "---",
        "",
        "<!-- 机生件（禁手改）：scripts/governance/generate_gate_face_reconciliation.py 产出 | 波 1A.3 触发面三列对账表 | 重算=重跑该生成器 -->",
        "# 门禁触发面三列对账表",
        "",
        "| 字段 | 值 |",
        "|---|---|",
        f"| generated_at | {summary['generated_at']} |",
        f"| head_commit | {summary['head_commit']} |",
        f"| generator | `{summary['generator']}` |",
        f"| roster | `{summary['roster_rel']}` |",
        f"| roster_entries | {summary['roster_entries']} |",
        f"| roster_declared_total_gates | {summary['roster_declared_total_gates']} |",
        f"| enabled | {summary['enabled_count']} |",
        f"| disabled | {summary['disabled_count']} |",
        f"| loaded_in_process | {summary['loaded_count']} |",
        f"| load_aggregate_error | {summary['load_aggregate_error'] or 'none'} |",
        f"| trigger_conditional | {summary['trigger_conditional_count']} |",
        f"| trigger_always_run | {summary['trigger_always_run_count']} |",
        f"| red_count | {summary['red_count']} |",
        "",
        "## 三列主表（行=名册每台门；行序=名册物理序）",
        "",
        "| gate_id | 名册声明 | 进程内实载 | files_trigger | HEAD 命中文件数 | 死触发 |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        trig = ", ".join(f"`{p}`({r['per_pattern_hits'][p]})" for p in r["files_trigger"]) or "—（空）"
        lines.append(
            f"| {r['gate_id']} | enabled={str(r['enabled']).lower()} | {'1' if r['loaded_in_process'] else '0'} | {trig} | {r['head_hit_files']} | {'YES' if r['dead_trigger'] else 'no'} |"
        )
    lines += [
        "",
        "## 红名单（判据：声明有实载 0｜触发面空｜死触发命中 0）",
        "",
    ]
    if not reds:
        lines.append("（空——三列全齐）")
    else:
        lines += ["| gate_id | 红态 | 说明 |", "|---|---|---|"]
        lines += [f"| {x['gate_id']} | {x['kind']} | {x['detail']} |" for x in reds]
    lines += [
        "",
        "## 声明禁用门（informational，不进红名单）",
        "",
    ]
    if not disabled_rows:
        lines.append("（无）")
    else:
        lines += ["| gate_id | 进程内实载 |", "|---|---|"]
        lines += [f"| {r['gate_id']} | {'1' if r['loaded_in_process'] else '0'} |" for r in disabled_rows]
    lines += [
        "",
        "> 本表=只读报告件：禁据此改任何门禁 enabled 态（flag 翻转=Owner 门位）；",
        "> 判据真源=docs/_working/total_command_closeout/10_wave_plan.md §1A.3。",
        "",
    ]
    return "\n".join(lines)


def render_yaml(
    rows: list[dict[str, Any]],
    reds: list[dict[str, str]],
    summary: dict[str, Any],
) -> str:
    doc = {
        "module_id": "RPT-GATE-FACE-RECONCILIATION",
        "doc_type": "register",
        "ttl": "permanent",
        "title": "门禁触发面三列对账表（波 1A.3）",
        "generated_by": summary["generator"],
        "generated_at": summary["generated_at"],
        "head_commit": summary["head_commit"],
        "roster": summary["roster_rel"],
        "red_criteria": [RED_DECLARED_NOT_LOADED, RED_TRIGGER_EMPTY, RED_TRIGGER_DEAD, RED_LOADED_NOT_DECLARED],
        "summary": {
            k: v for k, v in summary.items() if k not in {"generated_at", "head_commit", "generator", "roster_rel"}
        },
        "red_list": reds,
        "rows": rows,
    }
    return yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 参数定义（COMPLEXITY-GUARD 拆分件：argparse 面）。"""
    parser = argparse.ArgumentParser(description="触发面三列对账表生成器（波 1A.3，机生禁手改）")
    parser.add_argument("--check", action="store_true", help="只判红名单不出表（rc 1=红非空）")
    parser.add_argument("--output-dir", type=Path, default=None, help="输出目录（默认 _registry/reports）")
    parser.add_argument("--json", action="store_true", help="stdout 附机器可读 JSON 摘要")
    return parser.parse_args(argv)


def _load_in_process_ids(repo_root: Path) -> tuple[set[str], str]:
    """②进程内实载：真装载进独立 CommitGateRegistry，返回 (实载 gate_id 集, 聚合错误文本)。

    fail-closed 异常仅记录不抛出（仍清点已装载集合）——与原 main 内联块逐字同义。
    """
    registry = CommitGateRegistry()
    aggregate_error = ""
    try:
        auto_register_gates(registry, repo_root)
    except GateAutoRegistrationError as e:
        aggregate_error = str(e)
    return set(registry.list_gate_ids()), aggregate_error


def build_table(
    roster: dict[str, Any],
    loaded_ids: set[str],
    tracked: set[str],
    aggregate_error: str,
    head_commit: str,
) -> dict[str, Any]:
    """三列组装成一张表：{rows, reds, disabled_rows, summary}（COMPLEXITY-GUARD 拆分件）。

    判据零变化：行序=名册物理序、红名单四态经 derive_red_rows、计数字段口径与原
    main 内联块逐字一致（宪法 §4.3 计数一律字段承载）。
    """
    entries: list[dict[str, Any]] = roster.get("gates", [])
    rows = build_rows(entries, loaded_ids, tracked)
    declared_ids = {str(e.get("gate_id", "?")) for e in entries}
    reds = derive_red_rows(rows, loaded_ids, declared_ids)
    disabled_rows = [r for r in rows if not r["enabled"]]
    summary = {
        "generated_at": now_utc().isoformat(timespec="seconds"),
        "head_commit": head_commit,
        "generator": GENERATOR_REL,
        "roster_rel": "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml",
        "roster_entries": len(entries),
        "roster_declared_total_gates": roster.get("total_gates"),
        "enabled_count": sum(1 for r in rows if r["enabled"]),
        "disabled_count": len(disabled_rows),
        "loaded_count": len(loaded_ids & declared_ids),
        "load_aggregate_error": aggregate_error,
        "trigger_conditional_count": sum(1 for r in rows if r["trigger_mode"] == "conditional" and r["enabled"]),
        "trigger_always_run_count": sum(1 for r in rows if r["trigger_mode"] == "always-run" and r["enabled"]),
        "dead_trigger_count": sum(1 for r in rows if r["dead_trigger"]),
        "red_count": len(reds),
    }
    return {"rows": rows, "reds": reds, "disabled_rows": disabled_rows, "summary": summary}


def _print_json_summary(as_json: bool, table: dict[str, Any]) -> None:
    """--json：stdout 附机器可读摘要（红非空不改表产出）。"""
    if as_json:
        print(json.dumps({"summary": table["summary"], "red_list": table["reds"]}, ensure_ascii=False, indent=2))


def _print_check_report(reds: list[dict[str, str]]) -> int:
    """--check：只判红不出表（rc 语义 1=红非空/0=净面）。"""
    print(f"红名单 {len(reds)} 条（声明有实载 0 / 触发面空 / 死触发 / 实载有名册无）")
    for x in reds:
        print(f"  [{x['kind']}] {x['gate_id']}: {x['detail']}")
    return 1 if reds else 0


def _print_red_sample(reds: list[dict[str, str]]) -> None:
    """出表面的红名单前 10 条抽样（完整清单在产出表里）。"""
    for x in reds[:10]:
        print(f"  [{x['kind']}] {x['gate_id']}")
    if len(reds) > 10:
        print(f"  ...共 {len(reds)} 条（完整清单见产出表红名单段）")


def _unchanged_note(written: bool) -> str:
    """atomic_write_if_changed 语义标注：内容未变则未落盘。"""
    return "" if written else "（内容未变未落盘）"


def _write_tables(args: argparse.Namespace, repo_root: Path, table: dict[str, Any]) -> int:
    """md+yaml 落盘（atomic_write_if_changed 幂等）+ 产出面 stdout（COMPLEXITY-GUARD 拆分件）。"""
    rows, reds, disabled_rows, summary = table["rows"], table["reds"], table["disabled_rows"], table["summary"]
    out_dir = args.output_dir if args.output_dir else repo_root / OUTPUT_REL_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / OUTPUT_MD.name
    yml_path = out_dir / OUTPUT_YAML.name
    md_written = atomic_write_if_changed(md_path, render_markdown(rows, reds, disabled_rows, summary))
    yml_written = atomic_write_if_changed(yml_path, render_yaml(rows, reds, summary))
    print(
        f"红名单 {len(reds)} 条；表已产出: {md_path}{_unchanged_note(md_written)}, "
        f"{yml_path}{_unchanged_note(yml_written)}"
    )
    _print_red_sample(reds)
    return 1 if reds else 0


def main(argv: list[str] | None = None) -> int:
    """编排（COMPLEXITY-GUARD 治本：原 main 复杂度 21>15，拆为参数/装载/组表/产出四件，判据零变化）。"""
    ensure_utf8_stdout()
    args = _parse_args(argv)
    repo_root = REPO_ROOT

    roster = _read_roster(repo_root)
    if roster is None:
        print(
            f"ERROR: roster not found: {repo_root / 'docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml'}",
            file=sys.stderr,
        )
        return 2

    loaded_ids, aggregate_error = _load_in_process_ids(repo_root)

    # ③HEAD 树命中：git 面不可用=拒绝出表（禁降级出坏表）
    tracked = _head_tracked_relpaths(repo_root)
    if not tracked:
        print("ERROR: git ls-tree HEAD 不可用——命中数列失真即表失真，拒绝出表", file=sys.stderr)
        return 2

    table = build_table(roster, loaded_ids, tracked, aggregate_error, _head_commit(repo_root))
    _print_json_summary(args.json, table)
    if args.check:
        return _print_check_report(table["reds"])
    return _write_tables(args, repo_root, table)


if __name__ == "__main__":
    sys.exit(main())
