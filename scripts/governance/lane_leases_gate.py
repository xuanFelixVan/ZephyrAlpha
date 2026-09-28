# [BLUEPRINT] MOD-INF-094 | docs/_working/fullflow_chief_closeout/s52_dynamic_lanes_v1.md | §shadow-mode plan
# [MODULE] scripts.governance.lane_leases_gate
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.lane_leases；scripts.governance._shared.encoding
# [CONSUMERS] 人工/会话独立自检（影子期不入 commit gate 链——入链须走 gate registry 净零流程，v2 另批）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 租约影子审计门（S5② 动态车道 v1，2026-09-28）：给定落盘文件清单+session，对
#   ①文件落在该 session 活租约之外（含无租约）②同一文件被两个活租约同时覆盖——产出 WARNING
#   审计信号。**影子纪律：永不阻断**——只打印告警+退出码 0/2（2=有告警，供人眼/巡检识别；
#   本工具不注册进 gate_registry，不挂 commit 链，硬阻断=v2 影子 3 天后另批）。判定复用
#   lane_leases 的段边界前缀语义与活租约判定（单真源，不复制语义）；注册表缺失/损坏=按
#   load_registry 的重建语义降级为"全员无租约告警"，绝不异常炸栈。
# [MODIFY-GUARD] gate_id="N/A"（影子审计器，未注册 gate_registry；升格入册=v2 事）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯读（不写任何文件）；输入异常（坏清单/坏路径）=计入 findings 或 rc=2 用法错误，
#   绝不部分判读后静默；--json 全输出机器可读；退出码 0=无告警 / 2=有告警或用法错误（影子语义：
#   退出码只作信号，消费方不得据其阻断提交）。
# [TESTS] tests/governance/test_lane_leases.py
# [A_module] module_id=MOD-INF-094 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# create-guard-not-dup: 本模块=租约影子审计门（WARN-only 独立自检工具，不入 gate 链不注册 gate_registry），命中词为通用函数名/纪律短语（audit_files/_print_human/永不阻断），非各命中 gate 的重复实现
# [TTL] permanent
"""
lane_leases_gate.py — 租约影子审计门（WARN-only，永不阻断）

职责边界
--------
- 输入：``--session SID`` + 落盘文件清单（--files "a,b,c" / 多次 --file / --files-file F）。
- 判定（复用 lane_leases 单真源语义）：
  ① ``no-lease``       —— session 无活租约（所有文件计警一次）。
  ② ``outside-lease``  —— 文件不落在 session 活租约任何前缀内。
  ③ ``cross-lease-overlap`` —— 文件同时被 ≥2 个活租约（含本 session 与他 session、
     或两个他 session）覆盖——多 chief / 双写病类的直接信号。
- 输出：WARNING 行 + 摘要；退出码 0=无告警，2=有告警/用法错误。
- **绝不阻断**：本工具不注册进 commit gate 链（v1 影子；v2 硬阻断须影子数据 3 天
  复盘后走 gate registry 净零流程另批）。

Usage::

    python scripts/governance/lane_leases_gate.py --session X --files a,b,c
    python scripts/governance/lane_leases_gate.py --session X --file a --file b --json
    python scripts/governance/lane_leases_gate.py --session X --files-file list.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_leases as ll  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

__manifest__ = """
dimensions: [D1]
priority: P3
timeout_seconds: 30
args:
  - {flag: --session, type: str, description: "session id（必填）"}
  - {flag: --files, type: str, description: "逗号分隔落盘文件清单"}
  - {flag: --file, type: list, description: "单文件（可重复）"}
  - {flag: --files-file, type: str, description: "清单文件路径（逐行）"}
  - {flag: --leases, type: str, description: "租约注册表路径（默认仓根 .runtime/lane_leases.json）"}
  - {flag: --json, type: bool, description: "机器可读 JSON 输出"}
warn_only: true
"""


def collect_files(args: argparse.Namespace) -> list[str]:
    items: list[str] = []
    if args.files:
        items.extend(ll.read_file_list(args.files))
    for f in args.file or []:
        items.extend(ll.read_file_list(f))
    if args.files_file:
        p = Path(args.files_file)
        if p.exists() and p.is_file():
            items.extend(ll.read_file_list(str(p)))
        else:
            items.extend(ll.read_file_list(args.files_file))
    seen: list[str] = []
    for x in items:
        n = ll.normalize_prefix(x)
        if n and n not in seen:
            seen.append(n)
    return seen


def audit_files(registry_path: Path, session: str, files: list[str]) -> dict:
    """影子审计核心（纯读）。findings 非空 ⇒ rc=2（仅信号，永不阻断）。"""
    now = ll._now()
    registry, rebuilt = ll.load_registry(registry_path)
    registry = ll.prune_expired(registry, now)
    leases = registry.get("leases", {})
    own = leases.get(session)
    own_live = own is not None and ll._lease_is_live(own, now)
    findings: list[dict] = []

    if not own_live:
        findings.append(
            {
                "type": "no-lease",
                "severity": "WARN",
                "session": session,
                "files": files,
                "message": f"session={session} 无活租约：落盘文件全部在租约体系之外（影子告警，不阻断）",
            }
        )

    for f in files:
        if own_live and not any(ll.prefix_covers(p, f) for p in own.get("prefixes", [])):
            findings.append(
                {
                    "type": "outside-lease",
                    "severity": "WARN",
                    "session": session,
                    "file": f,
                    "own_prefixes": own.get("prefixes", []),
                    "message": f"文件 {f} 落在 session={session} 活租约之外（影子告警，不阻断）",
                }
            )
        covering = sorted(
            sid
            for sid, lease in leases.items()
            if ll._lease_is_live(lease, now) and any(ll.prefix_covers(p, f) for p in lease.get("prefixes", []))
        )
        if len(covering) >= 2:
            findings.append(
                {
                    "type": "cross-lease-overlap",
                    "severity": "WARN",
                    "file": f,
                    "covering_sids": covering,
                    "message": f"文件 {f} 被多个活租约覆盖：{covering}（多 chief/双写病类信号，影子告警不阻断）",
                }
            )
    return {
        "ok": True,
        "rc": 2 if findings else 0,
        "warn_only": True,
        "session": session,
        "files": files,
        "findings": findings,
        "rebuilt_registry": rebuilt,
        "note": "影子模式：本门永不阻断提交；硬阻断=v2（影子 3 天复盘后另批）",
    }


def _print_human(payload: dict) -> None:
    for f in payload["findings"]:
        print(f"WARNING [{f['type']}] {f['message']}")
    if not payload["findings"]:
        print(f"CLEAN session={payload['session']} 全部文件在租约域内且无跨租约相交")
    else:
        print(f"SUMMARY warn_only=true findings={len(payload['findings'])} rc={payload['rc']}（影子告警，不阻断）")


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="租约影子审计门（WARN-only 永不阻断；不入 commit gate 链）")
    parser.add_argument("--session", required=True, help="session id")
    parser.add_argument("--files", default="", help="逗号分隔文件清单")
    parser.add_argument("--file", action="append", default=[], help="单文件（可重复）")
    parser.add_argument("--files-file", default="", help="清单文件路径（逐行）")
    parser.add_argument("--leases", default="", help="租约注册表路径覆盖")
    parser.add_argument("--json", action="store_true", help="机器可读输出")
    args = parser.parse_args(argv)
    registry_path = ll._leases_path(ll.REPO_ROOT, args.leases or None)
    files = collect_files(args)
    payload = audit_files(registry_path, args.session, files)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_human(payload)
    return int(payload["rc"])


if __name__ == "__main__":
    sys.exit(main())
