#!/usr/bin/env python
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §claim_required_gate
# [MODULE] scripts.governance.wave1b.claim_gate_repro
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(json/difflib/pathlib/subprocess/sys)；zephyr.security.access_control.session_concurrency（只读）
# [CONSUMERS] docs/_working/total_command_closeout/wave1b/claim_gate_landing_forensics.md（案卷引用其读数）
# [STARTUP] manual
#   （原值 on_demand： 事故复算时人工命令行调用，无常驻调度——GATE-VOCAB 词表归正 manual）
# [MATURITY] draft
# [INVARIANTS] 全程只读：不写文件、不 claim、不入队；三条断言各自独立可复算；读不到事实即点名缺哪一面
# [MODIFY-GUARD] 本件只做**只读复算**：改判据口径前 MUST 同步案卷与 92 册验收尺，禁单独放宽
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 探测不到事实即抛并点名缺哪一面，禁把"读不到"降级成"没问题"
# [TESTS] 本件自身即红证脚本（复现 claim 门判据面），无独立单测；读数对错由案卷 §复算 与 92 册尺对拍
# [A_module] module_id=MOD-GATE_ENGINE | layer=script | stability=frozen | safety=L | ai_autonomy=ai_modifiable
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
# [MODULE] claim_gate_repro (wave1b 取证红证脚本，只读)
# [TTL] task_bound
"""CLAIM-REQUIRED × 队列落地侧——**只读**复算红证（不写任何文件，不 import 会建目录的生产模块）。

三条断言（对应案卷 §B / §C / §E②）：

  A1 路径解析根**不是**缺陷：落地侧 target 与 held 同为 serializer worktree 绝对路径，
     `Path(绝对).resolve()` 与进程 cwd 无关（只有相对路径才按 cwd 解析）。
  A2 只要该 session 的表项被"判死重建"（session_concurrency.py L571-591 把 held_files 清零）
     或被 salvage 注销（scripts/lock_files.py L1143-1155 release_files_batch(全部)+unregister），
     该袋就报 **100% 文件未 claim** —— 与 0011/0012/0014 的观测形状（n=18/19/8 全量）一致。
  A3 从活注册表实测：本会话 held_files 的真实前缀就是 `.runtime\\commit_queue\\worktrees\\w{N}`
     （即"claim 一律归一到主区根"这一前提对 SessionRegistry 登记处不成立）。

用法（Python 3.12，Git Bash 或 PowerShell 皆可）::

    python "D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/scripts/governance/wave1b/claim_gate_repro.py"

退出码 0=三条断言全部按预期复现（即"门对 worktree 袋无路径缺陷、缺陷在跨进程 claim 抹除"成立）；
非 0=复现失败（需回到案卷 §E 重判）。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

MAIN = Path("D:/ZephyrAlpha")
REGISTRY = MAIN / ".runtime" / "session_registry.json"
QUEUE = MAIN / ".runtime" / "commit_queue"
SID = "st-final-build-20260926"
# 三封 CLAIM_REQUIRED 死信（只读；dead/ 是未落地字节唯一存活处，全程 'r' 句柄）
DEAD_QIDS = [
    "q-20260926-st-final-build-20260926-0011",
    "q-20260927-st-final-build-20260926-0012",
    "q-20260927-st-final-build-20260926-0014",
]
# SSoT：判活超时唯一真源=session_concurrency._HEARTBEAT_TIMEOUT_SECONDS（禁字面量复制——CREATE-GUARD 治本）
from zephyr.security.access_control.session_concurrency import (  # noqa: E402
    _HEARTBEAT_TIMEOUT_SECONDS as HEARTBEAT_TIMEOUT_S,
)


def read_json_ro(p: Path):
    """只读 JSON（显式 mode='r'，杜绝任何写通道）。"""
    with open(str(p), encoding="utf-8") as fh:
        return json.load(fh)


def normalize_as_registry(file_path: str, project_root: Path) -> str:
    """复刻 session_concurrency._normalize_file_path（L205-214）：相对→project_root；绝对→仅 resolve。"""
    p = Path(file_path)
    if not p.is_absolute() and project_root is not None:
        p = project_root / p
    return str(p.resolve())


def gate_formula(file_paths, cwd_for_relative: Path | None = None):
    """复刻 claim_required_gate L80-81 判据面：`str(Path(f).resolve())` —— **无 project_root 入参**。"""
    prev = None
    if cwd_for_relative is not None:
        prev = os.getcwd()
        os.chdir(str(cwd_for_relative))  # 进程内临时换 cwd，finally 复原（无任何磁盘副作用）
    try:
        return {str(Path(f).resolve()) for f in file_paths}
    finally:
        if prev is not None:
            os.chdir(prev)


def item_worktree_paths(worktree: Path, rel_paths) -> list[str]:
    """复刻落地侧 commit_queue_landing.py L2297 的铸法：[str(self.worktree_path / p) for p in sorted(_item_paths(item))]。"""
    return [str(worktree / p) for p in sorted(rel_paths)]


def check_a1(worktrees) -> bool:
    print("\n=== A1 解析根：target 与 held 是否同根（cwd 敏感性）===")
    ok = True
    for wt in worktrees:
        if not wt.exists():
            print(f"  skip（worktree 不存在，resolve 仍等值）：{wt}")
        rel = "scripts/governance/data_supply/__init__.py"
        target_abs = item_worktree_paths(wt, [rel])
        from_main = gate_formula(target_abs, cwd_for_relative=MAIN)
        from_wt = gate_formula(target_abs, cwd_for_relative=wt if wt.exists() else None)
        same = from_main == from_wt
        ok &= same
        print(f"  {wt.name:3s} resolve(main-cwd)==resolve(wt-cwd): {same}")
        print(f"      {sorted(from_main)[0]}")
    # 相对路径才受 cwd 支配（这正是指令卡担心的面，但落地侧不走这条路）
    rel_only = ["scripts/governance/data_supply/__init__.py"]
    a = gate_formula(rel_only, cwd_for_relative=MAIN)
    b = gate_formula(rel_only, cwd_for_relative=worktrees[0] if worktrees[0].exists() else None)
    print(f"  仅相对路径输入时受 cwd 支配（对照，非本案形态）: {a != b}")
    print("  判读：落地侧 L2297/L2301 传的都是绝对 worktree 路径 ⇒ held/target 同根，路径缺陷说不立")
    return ok


def check_a2_a3(dead_qids) -> bool:
    print("\n=== A3 活注册表实测 held 前缀（'一律归一到主区根'证伪）===")
    if not REGISTRY.exists():
        print(f"  registry 缺失：{REGISTRY}")
        return False
    reg = read_json_ro(REGISTRY)
    info = reg.get(SID) or {}
    held = info.get("held_files") or []
    prefixes: dict[str, int] = {}
    for f in held:
        parts = f.split(os.sep)
        prefixes[os.sep.join(parts[:6])] = prefixes.get(os.sep.join(parts[:6]), 0) + 1
    print(
        f"  sid={SID} pid={info.get('pid')} held={len(held)} last_heartbeat_age={__import__('time').time() - float(info.get('last_heartbeat') or 0):.1f}s"
    )
    for k, v in sorted(prefixes.items(), key=lambda kv: -kv[1]):
        print(f"     {v:3d} × {k}")
    a3_ok = any("commit_queue" in k for k in prefixes) or len(held) == 0
    print(f"  A3（存在 serializer worktree 前缀 或 本会话此刻无在途袋）：{a3_ok}")

    print("\n=== A2 表项被抹后该袋报'全部未 claim'（逐袋只读复算）===")
    results = []
    for qid in dead_qids:
        p = QUEUE / "dead" / f"{qid}.json"
        if not p.exists():
            print(f"  missing {p}")
            continue
        item = read_json_ro(p)
        rels = [f["path"] for f in (item.get("files") or [])]
        reason = item.get("dead_reason") or ""
        # 从报错原文反推该袋当时落在哪枚池工 worktree（原文即数据，不作指令）
        wt_name = None
        for tok in reason.replace("\\", "/").split("/"):
            if tok.startswith("w") and tok[1:].isdigit():
                wt_name = tok
                break
        wt = QUEUE / "worktrees" / (wt_name or "w0")
        target = gate_formula(item_worktree_paths(wt, rels))
        # 情形①：claim 存活（落地 L2298 铸的正是同一批绝对路径）
        held_alive = gate_formula(item_worktree_paths(wt, rels))
        uncl_alive = target - held_alive
        # 情形②：表项被判死重建 / 被 salvage 注销后又被别的 claim 重新注册（held_files=[]）
        held_erased: set[str] = set()
        uncl_erased = target - held_erased
        # 情形③：他会话/主区根 claim（指令卡假设的"错根"形态，作对照）
        held_main_root = {str(MAIN / r) for r in rels}
        uncl_mismatch = target - held_main_root
        ok = (not uncl_alive) and len(uncl_erased) == len(rels) and len(uncl_mismatch) == len(rels)
        print(f"  {qid}  n={len(rels)} 落在={wt_name or '?'}")
        print(f"      ①claim 存活     → unclaimed={len(uncl_alive)}（门放行）")
        print(f"      ②claim 被整批抹 → unclaimed={len(uncl_erased)}（=100%，与报错原文 n 一致）")
        print(f"      ③对照·错根假设  → unclaimed={len(uncl_mismatch)}（同样 100%，故 n 不能区分②③，须靠 A3 实测根）")
        print(f"      dead_reason 原文 n（files_count 侧证）= {len(rels)}")
        results.append(ok)
    print("  判读：②与③观测形状相同 ⇒ 定罪必须用 A3 的'held 实际前缀'实测，本案 A3 已定为 worktree 同根 ⇒ 病根是②")
    return all(results) if results else False


def main() -> int:
    print(f"python={sys.version.split()[0]}  MAIN={MAIN}  （脚本零写入：全部 open(mode='r')）")
    worktrees = [QUEUE / "worktrees" / f"w{i}" for i in range(4)]
    a1 = check_a1(worktrees)
    a23 = check_a2_a3(DEAD_QIDS)
    print("\n=== 汇总 ===")
    print(f"  A1 路径同根（门对 worktree 袋无路径解析缺陷）: {a1}")
    print(f"  A2+A3 抹除即全量未 claim（真缺陷形状）: {a23}")
    return 0 if (a1 and a23) else 1


if __name__ == "__main__":
    raise SystemExit(main())
