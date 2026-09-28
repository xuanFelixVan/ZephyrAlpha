# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/reconcile_gate_rosters.py | §
# [MODULE] scripts.governance.d3_metadata.reconcile_gate_rosters
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
# [CONSUMERS] docs/_working/commit_speedup_campaign/90_verification/t14_roster_report.yaml
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读对账——永不写两册（in_process_gate_registry.yaml / gate_registry.yaml）；改册是 Owner 门位（注册表净增/净删），本工具只产证据；漂移判定全机械（扫描面与 generate_gate_registry.py 同源同则）
# [MODIFY-GUARD] 漂移类型分类表（DRIFT_TYPES）与 pending_owner 判据；gate_id 提取正则与生成器 _RE_GATE_ID 保持一致
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 两册任一缺失/不可解析 → stderr 报错 + exit EXIT_ERROR(2)；正常对账 exit EXIT_PASS(0)/EXIT_FINDINGS(1)
# [TESTS] docs/_working/commit_speedup_campaign/30_gate_census/t14_roster_report.yaml（对账跑批产物即验证面）
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 只读对账 CLI（--check 漂移取证），会话/CI 按需 manual 触发即设计语义；不内建 sleep/Timer/cron（宪法 §9.3）
"""
reconcile_gate_rosters.py — 门禁名册三方对账生成器（T14 治本：三册不同步取证）

三方对账面：
1. **模块面**：src/zephyr/gov_enforcement/commit_gates/**.py 的 GateSpec 声明
   （gate_id 提取正则与 generate_gate_registry.py 同源）+ make_* 工厂函数清单。
2. **in_process 名册**：in_process_gate_registry.yaml（gate_auto_registrar 装载真源）。
3. **统一册**：gate_registry.yaml（generate_gate_registry.py 三源合并产物）。

产出每门一行对账行（模块存在?/in_process 在册?/统一册在册?/own_scope 值/漂移类型），
外加册级自洽检查（total_gates 标量 vs gates 列表长度——统一册"队列合并器丢标量"
形态复发在案）与 own_scope 待 Owner 清单（不可机械判定者）。

本工具不自动改册（宪法 §9.5 静态清单生成器产出 + Owner 门位）——只产证据。

Usage::

    python scripts/governance/d3_metadata/reconcile_gate_rosters.py            # stdout 打印摘要
    python scripts/governance/d3_metadata/reconcile_gate_rosters.py --check \
        --out docs/_working/commit_speedup_campaign/30_gate_census/t14_roster_report.yaml
    # --check：发现漂移 exit 1（供 CI/gate 消费）；--out：落 yaml 报告 + 同名 .md 摘要
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

__manifest__ = """
dimensions: [D3]
priority: P1
timeout_seconds: 30
args:
  - {flag: --check, type: bool, description: "对账模式：发现漂移 exit 1"}
  - {flag: --out, type: str, description: "yaml 报告落盘路径（自动附同名 .md 摘要）"}
  - {flag: --root, type: str, description: "仓库根（默认脚本定位推导，支持 worktree）"}
  - {flag: --note, type: str, description: "附注行（可重复，写入 .md 摘要）"}
  - {flag: --evidence-file, type: str, description: "证据文件路径（可重复，全文嵌入 .md 附录）"}
warn_only: true
description: >
  门禁名册三方对账（模块面 vs in_process 名册 vs 统一册），只读取证不改册。
"""

COMMIT_GATES_SUBDIR = Path("src/zephyr/gov_enforcement/commit_gates")
IN_PROCESS_YAML = Path("docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml")
UNIFIED_YAML = Path("docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml")

# 与 generate_gate_registry.py 同源（[MODIFY-GUARD] gate_id 与 GateSpec gate_id 一致的既有约定）
_RE_GATE_ID = re.compile(r'gate_id\s*=\s*"([^"]+)"')
_RE_PRIORITY = re.compile(r"priority\s*=\s*(\d+)")
_RE_FACTORY = re.compile(r"^def (make_\w+)", re.MULTILINE)

_HELPER_FILES = {"__init__.py", "_diff_helpers.py", "_reference_helpers.py"}

DRIFT_TYPES = (
    "MODULE_NOT_IN_IN_PROCESS",  # 模块面有 GateSpec，in_process 名册无条目
    "IN_PROCESS_MODULE_MISSING",  # 名册条目的 module_path 无对应文件
    "MODULE_PATH_MISMATCH",  # 名册 module_path 与实际扫描路径不一致
    "FACTORY_NOT_IN_MODULE",  # 名册 factory_function 不在模块 def 清单
    "MODULE_NOT_IN_UNIFIED",  # 模块面有 GateSpec，统一册无条目
    "UNIFIED_CG_NO_MODULE",  # 统一册 source=commit-gate 但模块面缺失
    "OWN_SCOPE_MISSING",  # 统一条目缺 own_scope 字段（完备性缺口）
    "IN_PROCESS_DISABLED",  # enabled=false（informational，非漂移阻断项）
    "PRECOMMIT_SCRIPT_MISSING",  # pre-commit 条目无可定位脚本（待 Owner 佐证）
    "DUPLICATE_GATE_ID",  # 同 gate_id 出现在多个模块文件
)


def _repo_root(cli_root: str | None) -> Path:
    """解析仓库根：CLI 优先，缺省从脚本位置上溯（parents[3]=scripts/governance/d3_metadata 上三级）。"""
    if cli_root:
        return Path(cli_root).resolve()
    return Path(__file__).resolve().parents[3]


def scan_module_face(root: Path) -> tuple[dict[str, dict], int, int]:
    """扫描 commit_gates/**.py 提取模块面（gate_id → 工厂/标记/路径）。

    Returns:
        (gate_id -> face dict, 辅助模块数（无 GateSpec）, 扫描文件总数)
    """
    faces: dict[str, dict] = {}
    helpers = 0
    total = 0
    gates_dir = root / COMMIT_GATES_SUBDIR
    if not gates_dir.is_dir():
        return faces, helpers, total
    for py in sorted(gates_dir.rglob("*.py")):
        if py.name in _HELPER_FILES:
            continue
        total += 1
        text = py.read_text(encoding="utf-8", errors="replace")
        m_id = _RE_GATE_ID.search(text)
        rel = py.relative_to(root).as_posix()
        dotted = rel[len("src/") : -len(".py")].replace("/", ".")
        factories = _RE_FACTORY.findall(text)
        if not m_id:
            helpers += 1
            continue
        gate_id = m_id.group(1)
        m_pri = _RE_PRIORITY.search(text)
        face = {
            "file": rel,
            "module_path": dotted,
            "factories": factories,
            "own_scope_marker": "_build_own_scope" in text,
            "priority": int(m_pri.group(1)) if m_pri else None,
        }
        if gate_id in faces:
            faces[gate_id].setdefault("_dup_files", []).append(rel)
        else:
            faces[gate_id] = face
    return faces, helpers, total


def _load_roster(root: Path, rel: Path) -> dict:
    """读册（yaml.safe_load），缺失/损坏抛 FileNotFoundError/ValueError 由 main 兜底。"""
    path = root / rel
    if not path.is_file():
        raise FileNotFoundError(f"名册缺失: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("gates"), list):
        raise ValueError(f"名册结构异常（缺 gates 列表）: {path}")
    return data


def _locate_precommit_script(root: Path, entry: str) -> tuple[str | None, str | None]:
    """定位 pre-commit entry 的脚本文件（任意 .py 路径 token 或 python -m 模块解析）。

    Returns:
        (resolved 相对路径 或 None, 未定位原因 或 None)
    """
    for tok in entry.split():
        if tok.endswith(".py"):
            cand = root / tok
            if cand.is_file():
                return tok, None
            return None, f"entry 内脚本路径不存在: {tok}"
    m = re.search(r"-m\s+([\w.]+)", entry)
    if m:
        mod = m.group(1)
        for cand in (f"src/{mod.replace('.', '/')}.py", f"src/{mod.replace('.', '/')}/__main__.py"):
            if (root / cand).is_file():
                return cand, None
        return None, f"python -m 模块无可定位源文件: {mod}"
    return None, "entry 无 .py 路径且无 -m 模块（内联/pytest 形态）"


def reconcile(root: Path) -> dict:
    """三方对账主逻辑：产出报告 dict（含 summary/roster/pending_owner）。"""
    faces, helpers, total_py = scan_module_face(root)
    in_proc = _load_roster(root, IN_PROCESS_YAML)
    unified = _load_roster(root, UNIFIED_YAML)
    ip_index = {g.get("gate_id"): g for g in in_proc["gates"]}
    uf_index = {g.get("gate_id"): g for g in unified["gates"]}

    # 册级自洽：标量 total_gates vs 列表长度（统一册丢标量形态复发在案）
    scalar = {
        "in_process": {"scalar": in_proc.get("total_gates"), "list_len": len(in_proc["gates"])},
        "unified": {"scalar": unified.get("total_gates"), "list_len": len(unified["gates"])},
    }

    roster: list[dict] = []
    drift_counter: Counter[str] = Counter()
    own_scope_counter: Counter[str] = Counter()
    own_scope_pending: list[dict] = []

    all_ids = sorted(set(faces) | set(ip_index) | set(uf_index))
    for gid in all_ids:
        face = faces.get(gid)
        ip = ip_index.get(gid)
        uf = uf_index.get(gid)
        drifts: list[str] = []

        if face and not ip:
            drifts.append("MODULE_NOT_IN_IN_PROCESS")
        if ip and not face:
            drifts.append("IN_PROCESS_MODULE_MISSING")
        if face and ip:
            if ip.get("module_path") != face["module_path"]:
                drifts.append("MODULE_PATH_MISMATCH")
            if ip.get("factory_function") not in face["factories"]:
                drifts.append("FACTORY_NOT_IN_MODULE")
        if face and not uf:
            drifts.append("MODULE_NOT_IN_UNIFIED")
        if uf and not face and uf.get("source") == "commit-gate":
            drifts.append("UNIFIED_CG_NO_MODULE")
        if face and face.get("_dup_files"):
            drifts.append("DUPLICATE_GATE_ID")

        uf_source = uf.get("source") if uf else None
        uf_own = uf.get("own_scope") if uf else None
        if uf:
            if "own_scope" not in uf:
                drifts.append("OWN_SCOPE_MISSING")
                own_scope_counter["missing"] += 1
            elif uf_own is None:
                # 显式 null=生成器已评估但不可机械判定（内联 -c / pytest / 墓碑形态）
                own_scope_counter["null"] += 1
                own_scope_pending.append(
                    {"gate_id": gid, "source": uf_source, "reason": "显式 null：无可定位执行体源码，不可机械判定"}
                )
            else:
                own_scope_counter["true" if uf_own else "false"] += 1
            if "own_scope" not in uf:
                # 待 Owner 判据：manual 源（墓碑/机制条目）或 pre-commit 无可定位脚本
                reason = None
                if uf_source == "manual":
                    reason = "manual 源（重定向锚点/机制实名登记），无执行体可机械判定"
                elif uf_source == "pre-commit":
                    script, why = _locate_precommit_script(root, str(uf.get("entry", "")))
                    if script is None:
                        reason = why
                if reason:
                    own_scope_pending.append({"gate_id": gid, "source": uf_source, "reason": reason})
            if uf_source == "pre-commit":
                script, why = _locate_precommit_script(root, str(uf.get("entry", "")))
                if script is None:
                    drifts.append("PRECOMMIT_SCRIPT_MISSING")
        if ip and ip.get("enabled") is False:
            drifts.append("IN_PROCESS_DISABLED")

        for d in drifts:
            drift_counter[d] += 1
        row = {
            "gate_id": gid,
            "module": (
                {
                    "present": True,
                    "path": face["file"],
                    "module_path": face["module_path"],
                    "factories": face["factories"],
                    "own_scope_marker": face["own_scope_marker"],
                }
                if face
                else {"present": False}
            ),
            "in_process": (
                {
                    "present": True,
                    "module_path": ip.get("module_path"),
                    "factory_function": ip.get("factory_function"),
                    "enabled": ip.get("enabled"),
                }
                if ip
                else {"present": False}
            ),
            "unified": (
                {
                    "present": True,
                    "source": uf_source,
                    "status": uf.get("status"),
                    "own_scope": uf_own if "own_scope" in uf else "ABSENT",
                }
                if uf
                else {"present": False}
            ),
            "drift": drifts,
        }
        roster.append(row)

    drift_found = bool(drift_counter) or any(v["scalar"] != v["list_len"] for v in scalar.values())
    return {
        "summary": {
            "root": str(root),
            "module_py_total": total_py,
            "module_gate_count": len(faces),
            "module_helper_count": helpers,
            "in_process_count": len(in_proc["gates"]),
            "unified_count": len(unified["gates"]),
            "drift_found": drift_found,
        },
        "scalar_consistency": scalar,
        "drift_distribution": dict(sorted(drift_counter.items())),
        "own_scope_distribution": dict(own_scope_counter),
        "roster": roster,
        "pending_owner": {
            "own_scope_undecidable": sorted(own_scope_pending, key=lambda x: x["gate_id"]),
            "note": "改册（净增/净删）是 Owner 门位；本工具只产证据，不自动改两册。",
        },
    }


def _render_md(report: dict, notes: list[str], evidences: list[tuple[str, str]]) -> str:
    """渲染 .md 摘要（人读面；数字全部引用报告字段，禁散文写死计数）。"""
    s = report["summary"]
    sc = report["scalar_consistency"]
    lines = [
        "---",
        "ttl: task_bound",
        "---",
        "",
        "# T14 门禁名册三方对账摘要",
        "",
        "- 生成器: `scripts/governance/d3_metadata/reconcile_gate_rosters.py`（只读取证，不改两册）",
        f"- 对账根: `{s['root']}`",
        f"- 模块面: {s['module_py_total']} 个 .py，其中 GateSpec 门 {s['module_gate_count']}、辅助模块 {s['module_helper_count']}",
        f"- in_process 名册: {s['in_process_count']} 条（标量 {sc['in_process']['scalar']} / 列表 {sc['in_process']['list_len']}）",
        f"- 统一册: {s['unified_count']} 条（标量 {sc['unified']['scalar']} / 列表 {sc['unified']['list_len']}）",
        f"- own_scope 分布: {report['own_scope_distribution']}",
        "",
        "## 漂移类型分布",
        "",
        "| 类型 | 条数 |",
        "|---|---|",
    ]
    for k, v in report["drift_distribution"].items():
        lines.append(f"| {k} | {v} |")
    if not report["drift_distribution"]:
        lines.append("| (无漂移) | 0 |")
    lines += ["", "## own_scope 待 Owner（不可机械判定）", ""]
    for p in report["pending_owner"]["own_scope_undecidable"]:
        lines.append(f"- `{p['gate_id']}`（{p['source']}）：{p['reason']}")
    if notes:
        lines += ["", "## 附注", ""]
        lines += [f"- {n}" for n in notes]
    for name, text in evidences:
        lines += ["", f"## 证据附录: {name}", "", "```", text.rstrip("\n"), "```"]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    """CLI 入口：对账 → stdout 摘要 / --out 报告落盘 / --check 漂移即 exit 1。"""
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="门禁名册三方对账（只读取证）")
    parser.add_argument("--check", action="store_true", help="发现漂移 exit 1（供 CI/gate 消费）")
    parser.add_argument("--out", type=str, help="yaml 报告落盘路径（自动附同名 .md 摘要）")
    parser.add_argument("--root", type=str, help="仓库根（默认脚本定位推导，支持 worktree）")
    parser.add_argument("--note", action="append", default=[], help="附注行（可重复，写入 .md 摘要）")
    parser.add_argument("--evidence-file", action="append", default=[], help="证据文件路径（可重复，嵌入 .md 附录）")
    args = parser.parse_args()

    root = _repo_root(args.root)
    try:
        report = reconcile(root)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return EXIT_ERROR

    s = report["summary"]
    print(
        f"模块面 {s['module_gate_count']} 门（{s['module_py_total']} py / {s['module_helper_count']} 辅助）"
        f" | in_process {s['in_process_count']} | 统一册 {s['unified_count']}"
    )
    print(
        f"own_scope: {report['own_scope_distribution']} | 待 Owner: "
        f"{len(report['pending_owner']['own_scope_undecidable'])}"
    )
    for k, v in report["drift_distribution"].items():
        print(f"DRIFT {k}: {v}")
    for name, vv in report["scalar_consistency"].items():
        if vv["scalar"] != vv["list_len"]:
            print(f"SCALAR-DRIFT {name}: total_gates={vv['scalar']} != len(gates)={vv['list_len']}")

    if args.out:
        report["generated_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        report["generated_by"] = "scripts/governance/d3_metadata/reconcile_gate_rosters.py"
        report["mode"] = "check" if args.check else "report"
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # 首行 ttl: task_bound frontmatter（docs/_working TTL 约定；yaml 双文档形态，读取用 safe_load_all）
        body = yaml.safe_dump(report, allow_unicode=True, default_flow_style=False, sort_keys=False)
        out_path.write_text("---\nttl: task_bound\n---\n" + body, encoding="utf-8")
        evidences: list[tuple[str, str]] = []
        for ev in args.evidence_file:
            ev_path = Path(ev)
            evidences.append((ev_path.name, ev_path.read_text(encoding="utf-8", errors="replace")))
        md_path = out_path.with_suffix(".md")
        md_path.write_text(_render_md(report, args.note, evidences), encoding="utf-8")
        print(f"报告落盘: {out_path} + {md_path}")

    return EXIT_FINDINGS if (args.check and s["drift_found"]) else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
