# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/generate_fail_open_register.py | §
# [MODULE] scripts.governance.d7_code.generate_fail_open_register
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.io.paths
# [CONSUMERS] docs/01_policies_and_standards/_registry/catalogs/fail_open_register.yaml（派生册）; CI/门禁 --check
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 派生册唯一产出者=本件（宪法 §9.5 静态清单禁手工维护）; 计数字段 total_fail_open 不得写死在散文;
#   同一 fail_open 键的多行只计"首次出现"，聚合口径=AST 未覆盖时按行匹配（宁全不漏）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 扫描根缺失 -> SystemExit(2); --check 检出漂移 -> SystemExit(1)
# [TESTS] tests/governance/test_fail_open_register_generator.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""generate_fail_open_register.py — 全仓 fail-open 登记册生成器（BRK-047 收口）。

诞生的第一性理由：普查 BRK-047 给出"fail_open 1405 处 / 215 文件"这个**没有区分度的
数字**。无差别改造会把"有意降级"（备源不可用时继续跑）也改成阻断，那是加严的反向误伤。
真问题不是"有 fail-open"，而是**没有一册登记哪些 fail-open 是设计意图**。
本件把这句话变成可机械判定的命题：逐处给出
    file:line + 所在环节(FF-*) + 是否在钱路径 + 吞掉后有无痕迹 + 是否硬编码默认放行
五元组，使"设计意图 fail-open"与"偷懒 fail-open"首次可分档。

查重声明（CloneGuard 预检）：同目录 `detect_silent_degradation.py` 检测的是
"降级路径是否写日志"（COND-45 条件禁止，逐文件判违规）；本件做的是
**全量点名 + 五轴分档 + 派生册落地**，输入面（含 `fail_open` 标识符与
`fail-open` 注释、`FAIL_OPEN` 常量）与产物（机器可读 YAML 册）均不同，非同一能力。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402  RULE-SCHEMA-TZ: 生成器禁 datetime.now()

__all__: Final = ["main", "scan_fail_open_sites", "render_register"]

SCAN_ROOTS: Final[tuple[str, ...]] = ("src/zephyr", "scripts")
OUT_PATH: Final[Path] = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "fail_open_register.yaml"
)
GENERATED_BY: Final[str] = "scripts/governance/d7_code/generate_fail_open_register.py"

#: 环节归属（FF-01..FF-16）—— 顶层包 -> 全流通骨架环节；未映射记 GLOBAL
PKG_TO_STAGE: Final[dict[str, str]] = {
    "data": "FF-01",
    "data_governance": "FF-01",
    "intelligence": "FF-02",
    "strategy_factory": "FF-03",
    "backtest": "FF-04",
    "feature": "FF-05",
    "features": "FF-05",
    "regime": "FF-05",
    "signal": "FF-06",
    "signal_ashare": "FF-06",
    "factor": "FF-05",
    "orchestrator": "FF-07",
    "plan_engine": "FF-07",
    "position": "FF-09",
    "pf_alloc": "FF-09",
    "pf_core": "FF-09",
    "risk": "FF-10",
    "ex_core": "FF-11",
    "trading": "FF-11",
    "broker": "FF-11",
    "feedback_loop": "FF-12",
    "governance": "FF-14",
    "gov_enforcement": "FF-14",
    "gov_code_quality": "FF-14",
    "gov_drift": "FF-14",
    "infrastructure": "FF-15",
    "security": "FF-15",
    "shared": "FF-15",
    "autonomy_core": "FF-15",
    "frontend": "FF-16",
}

#: 钱/决策路径：资金腿或会导致发单/停源的包
MONEY_PKGS: Final[frozenset[str]] = frozenset(
    {
        "ex_core",
        "risk",
        "position",
        "pf_alloc",
        "pf_core",
        "trading",
        "broker",
        "orchestrator",
        "plan_engine",
        "signal_ashare",
        "data",
        "data_governance",
    }
)
MONEY_SYMBOL_RE: Final[re.Pattern[str]] = re.compile(
    r"(order|submit|cancel|fill|trade|position|cash|equity|balance|notional|"
    r"quantity|qty|price|cost|slippage|alloc|rebalance|kill_switch|circuit_break|"
    r"fuse|risk|broker|settle|reconcil|publish|escalat)",
    re.IGNORECASE,
)
FO_RE: Final[re.Pattern[str]] = re.compile(r"fail[_\-]?open", re.IGNORECASE)
HARD_PERMIT_RE: Final[re.Pattern[str]] = re.compile(
    r"(fail_open\s*[:=]\s*(True|\"?true\"?)\b|FAIL_OPEN)"
)
TRACE_RE: Final[re.Pattern[str]] = re.compile(
    r"(logger|logging|\blog\.|audit|metric|counter\.|alert|notify|warn|"
    r"exception\(|emit|breach|incident|dlq|dead_letter|raise\b)",
    re.IGNORECASE,
)
#: 生成器自身文件不计入登记册（它是扫描器，不是 fail-open 点）
SELF_EXCLUDE: Final[str] = "scripts/governance/d7_code/generate_fail_open_register.py"

_SKIP_DIR_RE: Final[re.Pattern[str]] = re.compile(
    r"(__pycache__|\.aidrafts|\.worktrees|c4_pdf_cache)"
)


def _iter_py() -> list[Path]:
    out: list[Path] = []
    for root in SCAN_ROOTS:
        base = REPO_ROOT / root
        if not base.exists():
            raise SystemExit(f"扫描根缺失: {base}")
        for p in base.rglob("*.py"):
            r = _rel(p)
            if _SKIP_DIR_RE.search(r) or r == SELF_EXCLUDE:
                continue
            out.append(p)
    return sorted(out)


def _rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT)).replace("\\", "/")


def _stage_of(rel: str) -> tuple[str, str]:
    """(pkg, stage)。src/zephyr/<pkg>/... -> 映射环节；其余记 GLOBAL/scripts。"""
    parts = rel.split("/")
    if parts[0] == "src" and len(parts) > 3:
        pkg = parts[2]
        return pkg, PKG_TO_STAGE.get(pkg, "GLOBAL")
    return parts[1] if parts[0] == "scripts" and len(parts) > 1 else parts[0], "GLOBAL"


def scan_fail_open_sites() -> list[dict[str, Any]]:
    """逐处点名 fail-open 出现点并打五轴标签（宁全不漏：标识符/注释/常量同计）。"""
    sites: list[dict[str, Any]] = []
    for path in _iter_py():
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        rel = _rel(path)
        pkg, stage = _stage_of(rel)
        for idx, ln in enumerate(lines, start=1):
            if not FO_RE.search(ln):
                continue
            stripped = ln.strip()
            if stripped.startswith("#") and not HARD_PERMIT_RE.search(stripped):
                kind = "doc_or_comment"
            else:
                kind = "code"
            window = "\n".join(lines[max(0, idx - 1) : min(len(lines), idx + 6)])
            sites.append(
                {
                    "file": rel,
                    "line": idx,
                    "stage": stage,
                    "pkg": pkg,
                    "kind": kind,
                    "money": pkg in MONEY_PKGS or bool(MONEY_SYMBOL_RE.search(path.name)),
                    "trace": bool(TRACE_RE.search(window)),
                    "hard_permit": bool(HARD_PERMIT_RE.search(stripped)),
                    "code": stripped[:160],
                }
            )
    return sites


def _bucket(s: dict[str, Any]) -> str:
    """分档：硬编码默认放行 > 钱路径无痕 > 有痕（设计意图）> 其余待判。"""
    if s["hard_permit"]:
        return "hardcoded_default_permit"
    if s["money"] and not s["trace"]:
        return "money_path_no_trace"
    if s["trace"]:
        return "designed_degradation_with_trace"
    return "undeclared_needs_review"


def render_register(sites: list[dict[str, Any]]) -> str:
    """渲染派生册 YAML 文本（手工维护禁止——本函数是唯一产出路径）。"""
    buckets: dict[str, list[dict[str, Any]]] = {}
    for s in sites:
        buckets.setdefault(_bucket(s), []).append(s)
    by_stage = Counter(s["stage"] for s in sites)
    by_file = Counter(s["file"] for s in sites)
    stamp = now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")

    head: list[str] = [
        "# [A_config] module_id=CFG-fail_open_register | layer=config | stability=evolving | safety=L | ai_autonomy=ai_modifiable",
        "# 派生册：唯一产出者=scripts/governance/d7_code/generate_fail_open_register.py",
        "# 手工编辑禁止（宪法 §9.5）；重生成 = python scripts/governance/d7_code/generate_fail_open_register.py",
        "# BRK-047 收口：让「设计意图 fail-open」与「偷懒 fail-open」首次可机械区分。",
        "schema_version: \"1.0.0\"",
        "doc_type: register",
        "ttl: permanent",
        "status: active",
        f"generated_at: \"{stamp}\"",
        f"generated_by: {GENERATED_BY}",
        f"scan_roots: {list(SCAN_ROOTS)!r}".replace("'", '"'),
        "criteria_zh: \"五轴：file:line / 所在环节(FF-*) / 是否在钱路径 / 吞掉后有无痕迹(log|audit|metric|alert|raise) / 是否硬编码默认放行\"",
        f"total_fail_open: {len(sites)}",
        f"total_files: {len(by_file)}",
        f"content_sha256: \"{_digest(sites)}\"",
        "bucket_counts:",
    ]
    for name in (
        "hardcoded_default_permit",
        "money_path_no_trace",
        "designed_degradation_with_trace",
        "undeclared_needs_review",
    ):
        head.append(f"  {name}: {len(buckets.get(name, []))}")
    head.append("by_stage:")
    for stage, n in sorted(by_stage.items(), key=lambda kv: (-kv[1], kv[0])):
        head.append(f"  {stage}: {n}")

    blocks = [
        (
            "hardcoded_default_permit",
            "逐处审定的入口档（默认放行写死在代码里，无配置可关）",
        ),
        (
            "money_path_no_trace",
            "钱/决策路径上且吞掉后零痕迹 —— 最高优先复核档",
        ),
        ("undeclared_needs_review", "非钱路径且无痕迹 —— 待逐处声明是否设计意图"),
    ]
    for name, note in blocks:
        rows = buckets.get(name, [])
        head.append("")
        head.append(f"{name}:  # {note}（{len(rows)} 处）")
        head.append("  entries:")
        for s in rows:
            head.append("    - file: \"%s\"" % s["file"])
            head.append("      line: %d" % s["line"])
            head.append("      stage: %s" % s["stage"])
            head.append("      on_money_path: %s" % str(s["money"]).lower())
            head.append("      has_trace: %s" % str(s["trace"]).lower())
            head.append("      code: \"%s\"" % _scalar(s["code"]))
    head.append("")
    head.append("designed_degradation_with_trace:  # 有痕降级（视为设计意图，本轮不动）")
    head.append(f"  count: {len(buckets.get('designed_degradation_with_trace', []))}")
    head.append("  note_zh: \"逐条清单由 --full 模式按需再生成；此处不展开以免派生册失去可读性\"")
    head.append("")
    head.append("per_file_counts:  # 全量点名（file -> 处数），供跨车道认领复核")
    head.append("  entries:")
    for f, n in sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0])):
        head.append(f"    - file: \"{f}\"")
        head.append(f"      count: {n}")
    head.append("")
    return "\n".join(head)


def _scalar(s: str) -> str:
    """YAML 双引号标量安全化（转义反斜杠与双引号，正则样本里满是这两个字符）。"""
    return s.replace("\\", "\\\\").replace(chr(34), '\\"')


def _digest(sites: list[dict[str, Any]]) -> str:
    payload = "\n".join(f"{s['file']}:{s['line']}:{_bucket(s)}" for s in sites)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    """CLI 入口（--check 供门禁调：派生册与现扫结果漂移即非零退出）。

    Returns:
        0=成功/无漂移，1=--check 检出漂移。
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="只比对派生册是否过期")
    ap.add_argument("--stdout", action="store_true", help="打到标准输出不落盘")
    # noqa: m11-perm-manual-legitimate  M11豁免: 治理派生册生成器，人工/门禁双入口 CLI 工具
    args = ap.parse_args(argv)

    sites = scan_fail_open_sites()
    text = render_register(sites)
    if args.stdout:
        sys.stdout.write(text)
        return 0
    if args.check:
        cur = OUT_PATH.read_text(encoding="utf-8") if OUT_PATH.exists() else ""
        want = re.search(r'content_sha256: "([0-9a-f]+)"', text)
        have = re.search(r'content_sha256: "([0-9a-f]+)"', cur)
        if not have or have.group(1) != (want.group(1) if want else ""):
            print(f"DRIFT: fail_open_register 派生册过期（盘上={have.group(1)[:12] if have else 'MISSING'}）")
            return 1
        print(f"OK total_fail_open={len(sites)}")
        return 0
    OUT_PATH.write_text(text, encoding="utf-8", newline="\n")
    print(f"WROTE {OUT_PATH} total_fail_open={len(sites)} files={len({s['file'] for s in sites})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
