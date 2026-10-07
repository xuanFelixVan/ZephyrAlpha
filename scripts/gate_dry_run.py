# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/gate_prerun.py | §全门链本地干跑组合器
# [MODULE] scripts.gate_dry_run
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.gate_prerun（进程内全量 GateSpec 链真源复用）；scripts.governance.enqueue_preflight（权威入队预检真源复用）；scripts.commit_queue（登记三族判定真源复用）；zephyr.gov_enforcement.rule_bridge.git_commit_gateway（真门）
# [CONSUMERS] 命令行（施工会话入队/提交前标准一步）；调度车道回执 verification 段
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯组合器零新判据——三段判定全部 import 既有真源（gate_prerun.run_specs 全量 GateSpec 链 / enqueue_preflight.run_enqueue_preflight 权威入队预检 / commit_queue._run_registration_gate 登记三族），本件只做编排与聚合报文，禁自带任何第二判定；只读干跑——绝不 commit、绝不改业务文件（唯一副作用=可选 claim 前移写 .ailocks，--no-claim 可关）；一次跑全链报全部硬拦（禁 fail-fast——车道要一次拿全修复清单）；登记三族段 audit_event=gate_dry_run 落 preflight_events.jsonl 留审计
# [MODIFY-GUARD] 三段判据变更须回各自真源件改（gate_prerun/enqueue_preflight/commit_queue），本件禁新增判定分支；ENV_SIGNAL_GATES 增删随 gate_prerun 同批
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=三段全绿（无硬拦）；1=任一段有硬拦或设施异常（假绿=事故，异常按硬拦计）；2=用法/环境错误（清单为空/gateway 不可达/message 文件缺失）；库层不抛，单段异常折叠进该段报文
# [TESTS] 红蓝留痕=st-govfix-g2-20261007 回执 verification 段（红腿=已知违规清单必须报硬拦；蓝腿=干净清单必须全绿）；报红能力自检透传 --self-check 到 gate_prerun
# [A_module] module_id=MOD-INF-005 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 车道按需调用的 permanent CLI 干跑器（非 cron/非 daemon/非常驻服务），由施工会话显式触发
"""gate_dry_run — 全门链本地干跑：对 --files 清单一次跑完三段门链，报全部硬拦。

为什么需要它（F6，st-govfix-g2-20261007）
------------------------------------------
既有面各管一段：`enqueue_preflight.run_enqueue_preflight` 管入队口脚本级预检、
`commit_queue._run_registration_gate` 管登记三族（CREATE-GUARD/TTL-METADATA/
TRANSLATION-COVERAGE）、`gate_prerun.run_specs` 管进程内全量 GateSpec——车道要跑
三处、拼三份报文，实战中经常一处都不跑（死信由此来）。本件把三段编成一个命令、
一次报全部硬拦（禁 fail-fast），车道照单全修后再入队。

净零声明（宪法 §4）：本件=组合器，零新判据；三段真源不变，判据变更回真源件改。

用法 / Usage::

    # 标准一步（入队前）：会话 + 清单 + message
    python scripts/gate_dry_run.py --session <sid> --files "a.py,b.yaml" --message-file msg.md

    # 只看机读汇总
    python scripts/gate_dry_run.py --session <sid> --files "a.py" --json out.json

    # 报红能力自检（透传 gate_prerun）
    python scripts/gate_dry_run.py --self-check

退出码 / Exit codes:
    0 = 三段全绿；1 = 任一段有硬拦或设施异常；2 = 用法/环境错误
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
for _p in (str(_REPO_ROOT / "src"), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_EXIT_PASS = 0
_EXIT_HARD = 1
_EXIT_USAGE = 2

#: 汇总面标题宽（排版参数非治理阈值，不接 SSoT）
_REPORT_WIDTH = 70


def section_enqueue_preflight(
    worktree_root: Path, files: list[str], session_id: str, message: str
) -> dict[str, object]:
    """第一段：权威入队预检（真源=enqueue_preflight.run_enqueue_preflight，只读）。"""
    from scripts.governance.enqueue_preflight import run_enqueue_preflight  # noqa: PLC0415

    t0 = time.monotonic()
    prescription = run_enqueue_preflight(worktree_root, files, session_id, message)
    return {
        "section": "enqueue_preflight",
        "hard": bool(prescription),
        "detail": str(prescription or ""),
        "seconds": round(time.monotonic() - t0, 1),
    }


def section_registration_gate(
    worktree_root: Path, files: list[str], session_id: str, message: str
) -> dict[str, object]:
    """第二段：登记三族（真源=commit_queue._run_registration_gate，audit_event=gate_dry_run）。"""
    import scripts.commit_queue as _cq  # noqa: PLC0415

    t0 = time.monotonic()
    try:
        findings, _deg, _face = _cq._run_registration_gate(  # noqa: SLF001 — 同仓在册判定复用
            worktree_root,
            list(files),
            session_id,
            message,
            audit_event="gate_dry_run",
        )
    except Exception as exc:  # noqa: BLE001 — 设施异常按硬拦计（假绿=事故）
        findings = [f"登记三族判定设施异常（按硬拦计）: {type(exc).__name__}: {exc}"]
    return {
        "section": "registration_gate",
        "hard": bool(findings),
        "detail": "\n".join(findings),
        "seconds": round(time.monotonic() - t0, 1),
    }


def section_inprocess_gates(
    gateway: object, files: list[str], session_id: str, message: str, *, claim: bool, project_root: Path
) -> dict[str, object]:
    """第三段：进程内全量 GateSpec 链（真源=gate_prerun，同锁内真调用形）。"""
    from scripts.governance.meta import gate_prerun  # noqa: PLC0415

    cfg = gate_prerun.GatePrerunConfig(
        session_id=session_id,
        files=files,
        flags={
            "allow_overlap": False,
            "allow_promote": True,
            "commit_message": message,
            "allow_derived_deletion": False,
            "allow_non_worktree": False,
            "allow_multi_domain": False,
            "allow_tracked_drift": False,
        },
        claim=claim,
        adopt_prior_work=True,
        verbose=True,
    )
    t0 = time.monotonic()
    outcome = gate_prerun.run_specs(gate_prerun.collect_specs(gateway), gateway, cfg)
    # claim 前移（gate_prerun 坑②同款）；返回值是成功清单，差集才是失败者（坑③）
    unclaimed = gate_prerun.claim_for_prerun(gateway, cfg) if claim else []
    hard = list(outcome.hard_fail) + list(outcome.errors)
    if unclaimed:
        hard.append("claim_files 未成功的文件（差集）: " + ", ".join(unclaimed))
    return {
        "section": "inprocess_gates",
        "hard": bool(hard),
        "detail": "\n".join(hard) if hard else "",
        "total_specs": outcome.total_specs,
        "env_signals": len(outcome.env_fail),
        "seconds": round(time.monotonic() - t0, 1),
        "project_root": str(project_root),
    }


def render_report(sections: list[dict[str, object]]) -> None:
    """人读聚合报文：逐段硬拦全列（禁 fail-fast），末尾给一段式修复清单头。"""
    print("\n" + "=" * _REPORT_WIDTH)
    total_hard = 0
    for s in sections:
        hard = bool(s.get("hard"))
        total_hard += int(hard)
        tag = "HARD" if hard else "PASS"
        extra = f" specs={s.get('total_specs')}" if "total_specs" in s else ""
        print(f"[{tag}] {s.get('section')} ({s.get('seconds', '?')}s{extra})")
        detail = str(s.get("detail") or "")
        if detail:
            print(f"--- {s.get('section')} 明细 ---\n{detail}")
    print("=" * _REPORT_WIDTH)
    print(
        f"[gate_dry_run] 硬拦段数 {total_hard}/{len(sections)}"
        + ("——照单全修后重跑本命令至全绿再入队" if total_hard else "（全绿，可入队）")
    )


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：三段编排 + 聚合报文，退出码只由硬拦决定。"""
    ap = argparse.ArgumentParser(
        prog="gate_dry_run.py",
        description="全门链本地干跑：对 --files 清单一次跑完入队预检/登记三族/进程内全量门，报全部硬拦",
    )
    ap.add_argument("--session", default="", help="会话 ID（缺身份会让 SESSION/WORKTREE 类门伪红，故必填）")
    ap.add_argument("--files", default="", help="逗号分隔的仓相对路径清单（与 git_commit.py --files 同值）")
    ap.add_argument("--message", default="", help="commit message（内容型 message 门依赖它）")
    ap.add_argument("--message-file", default="", help="从 UTF-8 文件读 message（与 --message 二选一）")
    ap.add_argument("--worktree-root", default="", help="工作区根（默认 cwd）")
    ap.add_argument("--no-claim", action="store_true", help="不做 claim 前移（会触发 CLAIM-REQUIRED 伪红）")
    ap.add_argument("--json", default="", help="把三段结果写 JSON（机读，回执贴用）")
    ap.add_argument("--self-check", action="store_true", help="只自检报红能力（透传 gate_prerun），不跑真门")
    args = ap.parse_args(argv)

    if args.self_check:
        from scripts.governance.meta import gate_prerun  # noqa: PLC0415

        return gate_prerun.self_check()

    files = [f.strip().replace("\\", "/") for f in args.files.split(",") if f.strip()]
    if not args.session:
        print("FAIL: 缺 --session（无身份会让 SESSION/WORKTREE 类门伪红）", file=sys.stderr)
        return _EXIT_USAGE
    if not files:
        print("FAIL: 缺 --files（逗号分隔仓相对路径清单）", file=sys.stderr)
        return _EXIT_USAGE
    message = args.message
    if args.message_file:
        p = Path(args.message_file)
        if not p.exists():
            print(f"FAIL: --message-file 不存在: {p}", file=sys.stderr)
            return _EXIT_USAGE
        message = p.read_text(encoding="utf-8").strip()

    worktree_root = Path(args.worktree_root) if args.worktree_root else Path.cwd()
    try:
        from scripts.governance.meta import gate_prerun  # noqa: PLC0415

        gateway = gate_prerun.make_gateway(worktree_root)
    except Exception as exc:  # noqa: BLE001 — 环境不可达=用法错误，非内容违规
        print(f"FAIL: gateway/门禁注册表不可达: {type(exc).__name__}: {exc}", file=sys.stderr)
        return _EXIT_USAGE

    print(f"[gate_dry_run] session={args.session} files={len(files)} worktree={worktree_root}")
    sections: list[dict[str, object]] = []
    sections.append(section_enqueue_preflight(worktree_root, files, args.session, message))
    sections.append(section_registration_gate(worktree_root, files, args.session, message))
    sections.append(
        section_inprocess_gates(
            gateway, files, args.session, message, claim=not args.no_claim, project_root=worktree_root
        )
    )
    render_report(sections)
    if args.json:
        Path(args.json).write_text(
            json.dumps(
                {"exit_code": 1 if any(s.get("hard") for s in sections) else 0, "sections": sections},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    return _EXIT_HARD if any(s.get("hard") for s in sections) else _EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
