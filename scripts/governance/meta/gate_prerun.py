# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/gate_prerun.py | §gate_prerun 入队前进程内门禁预跑
# [MODULE] scripts.governance.meta.gate_prerun
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway (GitCommitGateway)；
#   zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)；stdlib（argparse/json/sys/time/traceback）
# [CONSUMERS] 全流通/规则审计战役各施工车道（入队前标准一步，见
#   docs/_working/fullflow_campaign/CONSTRUCTION_DISCIPLINE.md §2）；
#   tests/governance/test_gate_prerun.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读预跑——绝不 commit、绝不改工作区业务文件（唯一副作用=可选 claim 前移，写 .ailocks）；
#   判据与 GitCommitGateway 锁内链同源：同一 spec.check(gateway, files, **flags) 调用形，
#   flags 键集与 gateway 锁内实调一致（含 session_id）；spec 清单真源=gw._gate_registry.specs_sorted()，
#   本件永不自带第二份判据；退出码只由"内容硬阻断 + gate 异常"决定，环境信号默认不计失败；
#   --self-check 双跑（注入违规腿必须红 / 干净腿必须绿），任一条不符即 exit 3（"不能红的检查器=没有检查器"）
# [MODIFY-GUARD] ENV_SIGNAL_GATES 成员增删须同步本文件 docstring 坑①说明与 tests/governance/test_gate_prerun.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 0=预跑通过（无内容硬阻断、无 gate 异常）；1=存在内容硬阻断或 gate 异常；
#   2=用法/环境错误（文件清单为空、gateway 或门禁注册表不可达、--message-file 缺失）；
#   3=--self-check 自检失败（预跑器失去"报红"能力，属工具自身缺陷，禁止继续依赖其 PASS 结论）。
#   库层不抛异常给调用方：单个 gate 的异常被收进 outcome.errors 并计入非零退出码
# [TESTS] tests/governance/test_gate_prerun.py
# [A_module] module_id=MOD-INF-005 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 车道按需调用的 permanent CLI 预跑器（入队前标准一步，非 cron/非 daemon/非常驻服务），由施工会话显式触发
"""gate_prerun — 入队/提交前本地预跑**进程内**门禁链（只读，不 commit）。

为什么需要它（真源：全流通战役 MAX_EXECUTE_LIST B19 / 台账 R-065a、R-069b、Q-7）
------------------------------------------------------------------------------
`scripts/governance/run_gate_chain.py` 只聚合**脚本型**子门禁，**预跑不到**本役任何一条
死因门——它们都是进程内 `GateSpec`（`src/zephyr/gov_enforcement/commit_gates/`）。
本件遍历 **`gateway._gate_registry.specs_sorted()` 的全部 GateSpec**，按 gateway 锁内的
**真调用形** `spec.check(gateway, files, **flags)` 只读预跑，把死信在入队前清到 0。
实弹背景：`batch_creation_tokens.py` 曾整条吃掉他道刚入 HEAD 的 4 行 token 并自报
"落盘 True (CAS)"，**只有进程内门预跑抓到**（脚本型 `run_gate_chain.py` 抓不到）
⇒ 预跑器不是"锦上添花"，是当前唯一能拦住热册蒸发的观测面。

三条使用坑（务必读完再动手，B19 原文）
--------------------------------------
① **不传 `session_id` ⇒ 四类伪红**：`SESSION-REQUIRED` / `WORKTREE-REQUIRED` /
   `HELD-OVERLAP` / `CLAIM-REQUIRED` 会全部报红。它们不是内容违规，是"预跑器没带身份"。
   → 本件强制要求 `--session`（缺失即 exit 2，不给它报红的机会）。
   环境信号型门（默认 `ENV_SIGNAL_GATES`）单独归类为 `[ENV ]`，不计入失败；
   要连环境信号一起判红用 `--strict-env`。
② **不调 `claim_files` ⇒ `CLAIM-REQUIRED` 伪红**：归属类门读 gateway 的 held_files/基线快照，
   没有 claim 就判"未持有"。→ 本件默认在预跑前做一次 claim 前移（`--no-claim` 可关）。
③ **`claim_files` 返回的是"成功清单"**（docstring 原话：claim 失败的文件从返回列表**排除**），
   **不是**冲突清单。把返回值读成"被冲突的文件"会得出完全相反的结论。
   → 本件按 `set(files) - set(returned)` 计算"未 claim 成功"的差集并打印，不转述语义。

用法 / Usage::

    # 标准一步（入队前）：具名清单 + 会话 + 本批 message
    python scripts/governance/meta/gate_prerun.py \\
        --session <sid> --files "a.py,b.yaml" --message-file .runtime/tmp/<sid>/msg.md

    # 只看单条门 / 跳过某条门；机读结果
    python scripts/governance/meta/gate_prerun.py --session <sid> --files "a.py" \\
        --only CREATE-GUARD --json .runtime/tmp/<sid>/prerun.json

    # 自检（证明这台预跑器真的能红；exit 3 = 预跑器失效，别再信它的 PASS）
    python scripts/governance/meta/gate_prerun.py --self-check

退出码 / Exit codes:
    0 = 预跑通过（无内容硬阻断、无 gate 异常）
    1 = 有内容硬阻断或有 gate 抛异常
    2 = 用法/环境错误（清单为空、gateway/注册表不可达、message 文件缺失）
    3 = --self-check 失败（预跑器失去报红能力）
"""

from __future__ import annotations

__manifest__ = """
args:
- --session
- --files
- --message-file
description: >
  入队/提交前本地预跑全部进程内 GateSpec（只读、不 commit），按 gateway 锁内真调用形
  逐门判定，把内容死信在入队前清到 0。
dimensions:
- D11
priority: P1
timeout_seconds: 900
warn_only: false
"""

import argparse
import json
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

_GOV_DIR = next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists())
_REPO_ROOT = _GOV_DIR.parents[1]
for _p in (str(_REPO_ROOT / "src"), str(_REPO_ROOT), str(_GOV_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

# 环境信号型门（非内容违规）：缺身份/非 worktree 直跑必然命中，落地侧由 serializer/旗标处置
ENV_SIGNAL_GATES: Final[frozenset[str]] = frozenset(
    {
        "WORKTREE-REQUIRED",
        "SESSION-REQUIRED",
        "COMMIT-SCOPE",
        "TRACKED-DRIFT-READONLY",
    }
)

# 明细截断宽度=展示用排版参数，不是治理阈值（真源 thresholds.yaml 管的是判定阈值），
# 故不接 SSoT；改名避开 VOCAB-HARDCODE 的 *LIMIT 变量名模式，未登记 gate-vocab 豁免。
_DETAIL_CLIP: Final[int] = 1200


@dataclass(frozen=True)
class GatePrerunConfig:
    """预跑参数（>7 个入参按房规收进 dataclass，避 NO-LONG-PARAM-LIST）。"""

    session_id: str
    files: list[str]
    flags: dict[str, object]
    env_gates: frozenset[str] = ENV_SIGNAL_GATES
    only: tuple[str, ...] = ()
    skip: tuple[str, ...] = ()
    strict_env: bool = False
    claim: bool = True
    adopt_prior_work: bool = True
    verbose: bool = True


@dataclass
class GatePrerunOutcome:
    """预跑结果三分类（硬阻断 / 环境信号 / 门自身异常）。"""

    total_specs: int = 0
    hard_fail: list[str] = field(default_factory=list)
    env_fail: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    unclaimed: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        """退出码：内容硬阻断或门异常 → 1；否则 0（环境信号默认不计失败）。"""
        return 1 if (self.hard_fail or self.errors) else 0


def build_flags(cfg: GatePrerunConfig) -> dict[str, object]:
    """组装传给 spec.check 的 flags（键集对齐 gateway 锁内实调，缺键会让部分门 TypeError）。"""
    return dict(cfg.flags, session_id=cfg.session_id)


def run_specs(specs: list[object], gateway: object, cfg: GatePrerunConfig) -> GatePrerunOutcome:
    """只读预跑给定 GateSpec 清单，返回三分类结果（不抛异常）。

    Args:
        specs: 待跑 GateSpec（真源=注册表快照；自检时注入合成品）。
        gateway: 透传给 ``spec.check`` 的第 1 位（真门依赖其 project_root/run_git/claim 面）。
        cfg: 预跑参数。

    Returns:
        GatePrerunOutcome——调用方据 ``exit_code`` 判生死。
    """
    outcome = GatePrerunOutcome(total_specs=len(specs))
    files = cfg.files
    flags = build_flags(cfg)
    for spec in specs:
        gate_id = str(getattr(spec, "gate_id", "?"))
        if cfg.only and gate_id not in cfg.only:
            outcome.skipped.append(gate_id)
            continue
        if gate_id in cfg.skip:
            outcome.skipped.append(gate_id)
            continue
        t0 = time.monotonic()
        try:
            passed, detail = spec.check(gateway, files, **flags)  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001 — 预跑要把异常本体报出来，不能吞成 PASS
            outcome.errors.append(f"{gate_id} ({time.monotonic() - t0:.1f}s): {type(exc).__name__}: {exc}")
            _emit(cfg, f"  [ERROR ] {gate_id} {type(exc).__name__}: {exc}")
            if cfg.verbose:
                traceback.print_exc(limit=2)
            continue
        dt = time.monotonic() - t0
        if passed:
            _emit(cfg, f"  [PASS  ] {gate_id} ({dt:.1f}s)")
        elif gate_id in cfg.env_gates and not cfg.strict_env:
            outcome.env_fail.append(f"{gate_id}: {str(detail)[:300]}")
            _emit(cfg, f"  [ENV   ] {gate_id} ({dt:.1f}s) <- 环境信号，非内容违规")
        else:
            outcome.hard_fail.append(f"{gate_id}: {str(detail)[:_DETAIL_CLIP]}")
            _emit(cfg, f"  [FAIL  ] {gate_id} ({dt:.1f}s)")
    return outcome


def _emit(cfg: GatePrerunConfig, line: str) -> None:
    """verbose 开时逐门打印（关时只留汇总，避免 CI 日志被 113 行刷满）。"""
    if cfg.verbose:
        print(line)


def report(outcome: GatePrerunOutcome) -> None:
    """打印三分类汇总与逐条明细（明细是车道真正要抄的东西）。"""
    print("\n" + "=" * 70)
    print(
        f"[prerun] 内容硬阻断 {len(outcome.hard_fail)} | 环境信号 {len(outcome.env_fail)}"
        f" | gate异常 {len(outcome.errors)} | 未跑 {len(outcome.skipped)}"
        f" | 注册 GateSpec 总数 = {outcome.total_specs}"
    )
    if outcome.unclaimed:
        print(f"[prerun] ⚠ claim_files 未成功的文件（返回的是成功清单，差集才是失败者）: {outcome.unclaimed}")
    for bucket, tag in ((outcome.hard_fail, "HARD"), (outcome.env_fail, "ENV"), (outcome.errors, "GATE-EXC")):
        for line in bucket:
            print(f"\n--- {tag} ---\n{line}")


def collect_specs(gateway: object) -> list[object]:
    """取进程内门禁注册表快照（唯一真源，本件不维护第二份清单）。"""
    return list(gateway._gate_registry.specs_sorted())  # noqa: SLF001 — 注册表快照唯读，房内在册通道


def make_gateway(project_root: Path) -> object:
    """实例化 GitCommitGateway（预跑用真门，故不可 mock）。"""
    from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

    return GitCommitGateway(str(project_root))


def claim_for_prerun(gateway: object, cfg: GatePrerunConfig) -> list[str]:
    """claim 前移（坑②）；返回"未 claim 成功"的差集（坑③：返回值是成功清单）。"""
    if not cfg.claim:
        return []
    claimed = gateway.claim_files(cfg.session_id, cfg.files, adopt_prior_work=cfg.adopt_prior_work)
    claimed_norm = {str(c).replace("\\", "/") for c in claimed}
    return [f for f in cfg.files if f.replace("\\", "/") not in claimed_norm]


@dataclass(frozen=True)
class _SyntheticSpec:
    """自检用合成 GateSpec——真源仍是 GateSpec 的 (gate_id, check) 形状，不另立判据。"""

    gate_id: str
    check: object
    priority: int = 100


def self_check() -> int:
    """证明这台预跑器**真的能红**：违规腿必须判红、干净腿必须判绿。

    Returns:
        0=判别力完好；3=失去报红能力（此时它的 PASS 结论不可信）。
    """

    def _mk(gate_id: str, passed: bool, raises: bool) -> _SyntheticSpec:
        """_mk implementation."""

        def _check(_gw: object, _files: list[str], **_kw: object) -> tuple[bool, str]:
            """_check implementation."""
            if raises:
                raise RuntimeError("injected synthetic gate failure")
            return (passed, "injected synthetic violation" if not passed else "")

        return _SyntheticSpec(gate_id=gate_id, check=_check)

    clean = [_mk("SYNTH-PASS", True, False)]
    dirty = [_mk("SYNTH-FAIL", False, False), _mk("SYNTH-RAISE", True, True)]
    cfg = GatePrerunConfig(session_id="self-check", files=["synthetic.py"], flags={}, verbose=False)
    green = run_specs(clean, None, cfg)
    red = run_specs(dirty, None, cfg)
    ok = green.exit_code == 0 and red.exit_code == 1 and len(red.hard_fail) == 1 and len(red.errors) == 1
    print(
        f"[self-check] 干净腿 exit={green.exit_code}（期望 0）| 违规腿 exit={red.exit_code}"
        f"（期望 1）hard={len(red.hard_fail)} errors={len(red.errors)}"
    )
    print("[self-check] OK：预跑器具备报红能力" if ok else "[self-check] FAIL：预跑器不能红，禁止采信其 PASS 结论")
    return 0 if ok else 3


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 参数（--files 是逗号分隔单参数，与 git_commit.py 同口径）。"""
    ap = argparse.ArgumentParser(description="入队前本地预跑全部进程内 GateSpec（只读，不 commit）")
    ap.add_argument("--session", default="", help="会话名（坑①：不传会引发四类伪红，故预跑要求显式提供）")
    ap.add_argument("--files", default="", help="逗号分隔的具名文件清单（与 git_commit.py --files 同值）")
    ap.add_argument("--message", default="", help="模拟的 commit message（内容型 message 门依赖它）")
    ap.add_argument("--message-file", default="", help="从 UTF-8 文件读 message（与 --message 二选一）")
    ap.add_argument("--project-root", default=str(_REPO_ROOT), help="预跑的仓根（默认本仓）")
    ap.add_argument("--only", action="append", default=[], help="只跑这些 gate（可重复）")
    ap.add_argument("--skip", action="append", default=[], help="跳过这些 gate（可重复）")
    ap.add_argument("--env-gate", action="append", default=[], help="追加环境信号门（不计失败）")
    ap.add_argument("--strict-env", action="store_true", help="环境信号也计失败")
    ap.add_argument("--no-claim", action="store_true", help="不做 claim 前移（会触发 CLAIM-REQUIRED 伪红）")
    ap.add_argument("--no-adopt", action="store_true", help="claim 时不带 adopt_prior_work")
    ap.add_argument(
        "--allow",
        action="append",
        default=[],
        help="置真的旗标：overlap/promote/derived-deletion/non-worktree/multi-domain/tracked-drift",
    )
    ap.add_argument("--quiet", action="store_true", help="只打印汇总")
    ap.add_argument("--json", default="", help="把三分类结果写 JSON（机读）")
    ap.add_argument("--self-check", action="store_true", help="只自检报红能力，不跑真门")
    return ap.parse_args(argv)


_FLAGS_BY_ALLOW: Final[dict[str, str]] = {
    "overlap": "allow_overlap",
    "promote": "allow_promote",
    "derived-deletion": "allow_derived_deletion",
    "non-worktree": "allow_non_worktree",
    "multi-domain": "allow_multi_domain",
    "tracked-drift": "allow_tracked_drift",
}


def build_config(args: argparse.Namespace) -> GatePrerunConfig | str:
    """把 CLI 参数折成 GatePrerunConfig；不合法时返回错误串（调用方转 exit 2）。"""
    files = [f.strip().replace("\\", "/") for f in args.files.split(",") if f.strip()]
    if not args.self_check:
        if not args.session:
            return "缺 --session（坑①：无身份会让 SESSION/WORKTREE/HELD-OVERLAP/CLAIM-REQUIRED 四类伪红）"
        if not files:
            return "缺 --files（具名逗号清单，与 git_commit.py --files 同值）"
    message = args.message
    if args.message_file:
        p = Path(args.message_file)
        if not p.exists():
            return f"--message-file 不存在: {p}"
        message = p.read_text(encoding="utf-8").strip()
    flags: dict[str, object] = {
        "allow_overlap": False,
        "allow_promote": True,
        "commit_message": message,
        "allow_derived_deletion": False,
        "allow_non_worktree": False,
        "allow_multi_domain": False,
        "allow_tracked_drift": False,
    }
    for token in args.allow:
        key = _FLAGS_BY_ALLOW.get(token)
        if key is None:
            return f"--allow 未知旗标: {token}（可选 {sorted(_FLAGS_BY_ALLOW)}）"
        flags[key] = True
    return GatePrerunConfig(
        session_id=args.session,
        files=files,
        flags=flags,
        env_gates=ENV_SIGNAL_GATES | frozenset(args.env_gate),
        only=tuple(args.only),
        skip=tuple(args.skip),
        strict_env=args.strict_env,
        claim=not args.no_claim,
        adopt_prior_work=not args.no_adopt,
        verbose=not args.quiet,
    )


def dump_json(path: str, outcome: GatePrerunOutcome) -> None:
    """机读结果落盘（车道把它贴进回执）。"""
    payload = {
        "total_specs": outcome.total_specs,
        "exit_code": outcome.exit_code,
        "hard_fail": outcome.hard_fail,
        "env_fail": outcome.env_fail,
        "errors": outcome.errors,
        "skipped": outcome.skipped,
        "unclaimed": outcome.unclaimed,
    }
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run prerun chain read-only, return exit code."""
    args = parse_args(argv)
    cfg = build_config(args)
    if isinstance(cfg, str):
        print(f"FAIL: {cfg}", file=sys.stderr)
        return EXIT_ERROR
    if args.self_check:
        return self_check()
    try:
        gateway = make_gateway(Path(args.project_root))
        specs = collect_specs(gateway)
    except Exception as exc:  # noqa: BLE001 — 环境不可达=用法错误，不是内容违规
        print(f"FAIL: gateway/门禁注册表不可达: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR
    print(f"[prerun] session={cfg.session_id} files={len(cfg.files)} 注册 GateSpec 总数 = {len(specs)}")
    # 坑②：claim 前移 MUST 在跑门之前——CLAIM-REQUIRED / FOREIGN-CHANGE 读的是 held_files 与基线快照
    unclaimed = claim_for_prerun(gateway, cfg)
    outcome = run_specs(specs, gateway, cfg)
    outcome.unclaimed = unclaimed
    report(outcome)
    if args.json:
        dump_json(args.json, outcome)
    return outcome.exit_code


if __name__ == "__main__":
    sys.exit(main())
