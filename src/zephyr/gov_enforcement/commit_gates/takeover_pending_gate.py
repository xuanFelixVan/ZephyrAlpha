# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.takeover_pending_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# create-guard-not-dup: 本模块=接管待决硬阻断门禁（读接管台账拦未接管资源面的提交），非 algo_flow 解析/渲染/翻译对齐能力——docstring 锚词 "ALGO FLOW" 仅因 external 锚格式含该词，语义零交集
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)；scripts.governance.session_takeover_ledger（load_open_entries/entry_match_surface，函数内延迟 import 防循环）；zephyr.security.access_control.session_concurrency.liveness_verdict（C11 读侧活性复核单口，延迟 import）；zephyr.shared.io.audit_jsonl_writer（降级留痕）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（in_process_gate_registry.yaml YAML 驱动注册）；zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——commit 文件（repo-relative posix）命中任一 open 接管条目命中面（held_files+worktree dirty_files+staging files）时阻断，detail 含死亡证据+接管处方+--resolve 指引（下一个 AI 想绕都绕不过，必须先按清单接管——00_orchestration.md §2.2 L3 门禁显化）；tests/ 豁免；台账缺失/损坏行/ledger 模块不可达 fail-open（logger.warning 检测器失效）；检出命中 fail-closed 阻断；C11 活性复核（统筹裁定 2026-10-12）——仅"提交人 sid＝条目属主 sid 且 liveness_verdict∈{alive,degraded}"降级 warn＋逐次留痕（.runtime/session_registry_audit/takeover_self_block.jsonl），死会话/他班条目一律照拦，verdict 不可达＝unreadable 保守照拦（读失败不当活证）
# [MODIFY-GUARD] gate_id="TAKEOVER-PENDING"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；判据/命中面变更须与 scripts/governance/session_takeover_ledger.py 同批
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——ledger 读取/import 异常降级为 fail-open（passed=True，logger.warning）；检出命中 fail-closed 阻断（passed=False）
# [TESTS] tests/gov/governance/test_session_takeover_ledger.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/takeover_pending_gate.yaml
takeover_pending_gate.py — 接管待决硬阻断门禁（TAKEOVER-PENDING，接管显化 L3）

病根（00_orchestration.md §2.2）：AI 施工队会话中途死亡 → 暂存区/worktree/claim/死袋
全成无主黑箱；下一个 AI 想提交触碰同面文件时没有任何强制显化点 → 无主资源堆积。

治本：commit 时把 open 接管条目（.runtime/takeover_ledger.jsonl，由
scripts/governance/session_takeover_ledger.py L1+L2 生成）当作硬阻断面——
commit 清单命中条目命中面（held_files / worktree dirty_files / staging files）
→ 阻断并打印死亡证据+接管处方+``--resolve`` 指引。接管完成（按处方处置后
``--resolve <sid> --by <接管者>``）条目迁 resolved/ → 门自动放行。

设计权衡
--------
1. **命中面=具体文件集合**（非 impacted_modules 目录前缀）：目录级匹配会误伤
   同域无关文件；只有具体文件重叠才是真冲突信号（held_files 是 registry 真源）。
2. **fail-open on 台账不可达**：台账缺失/JSON 损坏行/模块 import 失败=显化设施
   失效，不阻断无辜提交（与 ast 类 gate 同契约）；显化恢复后 --scan 即补账。
3. **priority=160**：治理簇尾（PERM-TRIGGER 155/HIGH-COMPLEXITY 156/
   DEPGRAPH-PRE-REGISTRATION 157 之后、registry_mass_deletion 200 之前）。
4. **tests/ 豁免**：测试 fixture 常命中假条目路径，豁免真源=is_test_exempt。
5. **C11 活性复核只放开"自挡"一格**（2026-10-12 统筹裁定）：崩溃静默期 `--scan` 会把
   当时在跑的多会话批量立案，而本门历史上**不看活性是否已恢复** ⇒ 复岗的活班被自己的
   死班形态长期硬拦（实测 10-12 当日 23 枚 TAKEOVER 死袋里 14 枚是自挡）。降级条件三重
   收窄：①只认"提交人＝条目属主 sid"；②只认在册单口 `liveness_verdict` 的 alive/degraded；
   ③每次降级必落一行留痕。他班条目与死会话条目**零放宽**（跨班保护面不缩一寸）。

Usage::

    from zephyr.gov_enforcement.commit_gates.takeover_pending_gate import make_takeover_pending_gate

    # 经 in_process_gate_registry.yaml 自动注册（gate_auto_registrar），无需手工 register
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_takeover_pending_gate"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注


def _self_block_verdict(sid: str) -> tuple[str, str]:
    """C11（统筹裁定 2026-10-12）读侧活性复核的唯一尺＝在册单口 `liveness_verdict`。

    裁定#480 C-2 已把 8 套活性机制内收成一张裁决表（alive/degraded/dead/ghost），
    本门**禁止另造判据**（多真源必漂移，根宪法 RULE-SSOT）。
    读不到/异常一律返回 ("unreadable", <原因>) 并按**保守=照拦**处理，
    绝不把"读失败"当活证（与三证立法的"证据读不到=无正证"同向）。
    """
    try:
        from zephyr.security.access_control.session_concurrency import liveness_verdict

        v = liveness_verdict(sid)
        return str(v.state), str(v.authoritative_signal or "")
    except Exception as exc:  # noqa: BLE001 — 活性单口不可达=保守照拦（fail-closed）
        logger.warning("TAKEOVER-PENDING gate: liveness_verdict 不可达（保守照拦）sid=%s: %s", sid, exc)
        return "unreadable", f"verdict-unreachable:{type(exc).__name__}"


def _audit_softened(entry: dict, matched: list[str], state: str, signal: str, root: Path) -> None:
    """降级放行留痕：每次落一行 JSONL（不静默）。失败不阻断（与审计层一致）。"""
    import json as _json
    import time as _time

    try:
        from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl

        rec = {
            "ts": _time.time(),
            "event": "takeover_self_block_softened",
            "sid": entry.get("sid"),
            "liveness_state": state,
            "authoritative_signal": signal,
            "hit_files": matched[:20],
            "hit_count": len(matched),
            "death_reason_at_scan": str(((entry.get("death_evidence") or {}).get("reason")) or "")[:200],
            "policy": "C11 统筹裁定 2026-10-12：活班被自身崩溃期 open 条目连坐→warn 放行；死会话/他班照拦",
        }
        append_audit_jsonl(root / ".runtime" / "session_registry_audit", "takeover_self_block.jsonl", rec)
    except Exception:  # noqa: BLE001 — 留痕失败不得改变放行结论
        logger.warning("TAKEOVER-PENDING gate: 降级留痕写入失败（non-blocking）", exc_info=True)


def _import_ledger_module(root: Path):
    """延迟 import 接管台账模块（repo root 不在 sys.path 时兜底插入；防循环+测试可控）。"""
    try:
        from scripts.governance import session_takeover_ledger as ledger

        return ledger
    except ImportError:
        root_str = str(root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
        from scripts.governance import session_takeover_ledger as ledger

        return ledger


def _format_block_detail(hits: list[tuple[dict, list[str]]]) -> str:
    """把 (条目, 命中文件) 列表格式化为阻断 detail（死亡证据+处方+resolve 指引）。"""
    parts: list[str] = [
        "TAKEOVER-PENDING：本次 commit 命中 open 接管条目（死会话遗留资源面）——"
        "必须先按接管处方处置再提交（接管显化 L3，00_orchestration.md §2.2）。"
    ]
    for entry, hit_files in hits:
        evidence = entry.get("death_evidence") or {}
        parts.append(
            f"\n## 死会话 sid={entry.get('sid')}（判死证据：{evidence.get('reason', 'unknown')}）\n"
            f"  命中文件 {len(hit_files)} 件：{', '.join(hit_files[:10])}"
            f"{' ...' if len(hit_files) > 10 else ''}"
        )
        for line in entry.get("prescription") or []:
            parts.append(f"  Rx: {line}")
    parts.append(
        "\n-> 接管完成后运行 python scripts/governance/session_takeover_ledger.py "
        "--resolve <sid> --by <接管者> 解除阻断；台账不可用时 --scan 重建。"
    )
    return "\n".join(parts)


def make_takeover_pending_gate() -> GateSpec:
    """构造接管待决硬阻断 GateSpec。

    Returns:
        GateSpec(gate_id="TAKEOVER-PENDING", priority=160)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 定位仓库根（gateway 真源，缺省 cwd）。
        # F3 治本（2026-10-02 红蓝审查）：serializer 落地网关 project_root=专用
        # worktree，而台账住主仓 .runtime/（gitignored 不入 worktree 检出）——
        # 按 worktree 根读恒空=queue landing 全量静默放行（T1 落地即失效实证）。
        # 经 anchor_main_root 锚主仓根再读（approval_resolver #ARCH-324 同款处方；
        # 非 worktree 根原样返回，pytest tmp 隔离库不受影响）。
        root = Path(str(getattr(gateway, "project_root", ".") or ".")).resolve()
        try:
            from zephyr.shared.io.paths import anchor_main_root  # noqa: PLC0415 — 延迟 import 防循环

            root = anchor_main_root(root)
        except Exception:  # noqa: BLE001 — 锚设施异常退回原根（保持 fail-open 面不变）
            logger.warning("TAKEOVER-PENDING gate: anchor_main_root 不可用，退回 gateway 根。", exc_info=True)

        # 2. 载入 open 条目（fail-open：台账设施不可达=检测器失效）
        try:
            ledger = _import_ledger_module(root)
            open_entries = ledger.load_open_entries(root)
        except Exception:  # noqa: BLE001 — 显化设施失效不阻断，warn 留痕
            logger.warning(
                "TAKEOVER-PENDING gate: takeover ledger 不可读，fail-open 放行（检测器失效）。",
                exc_info=True,
            )
            return True, ""
        if not open_entries:
            return True, ""

        # 3. 归一化 commit 文件为 repo-relative posix，逐条目求命中。
        # F3 第二层治本（2026-10-02 红蓝审查）：锁内链 entrypoint commit() 已把 files
        # 归一为**绝对路径**（_filter_existing_files 返回 abs），直比 as_posix 永失配
        # （HELD-OVERLAP 同类门均做 abs→rel 归一）。相对化锚=gateway 自身 project_root
        # （serializer 落地=worktree 内暂存，相对 worktree 即 repo 布局；主区直连=主仓根）；
        # 台账读取仍用上方 anchor_main_root 锚定的主仓根——两锚分工。
        gw_root = Path(str(getattr(gateway, "project_root", ".") or ".")).resolve()

        def _norm(f: str) -> str:
            p = Path(f)
            if not p.is_absolute():
                p = gw_root / p
            try:
                rp = p.resolve()
                try:
                    return rp.relative_to(gw_root).as_posix()
                except ValueError:
                    return rp.as_posix()
            except OSError:
                return p.as_posix()

        commit_files = {_norm(f) for f in files or []}
        commit_files = {f for f in commit_files if not is_test_exempt(f)}
        if not commit_files:
            return True, ""

        hits: list[tuple[dict, list[str]]] = []
        for entry in open_entries:
            # D-2 裁定（2026-10-02）：袋内文件只入台账盘点、不进门牙咬合面
            # （过咬实测数据见 ledger.bag_residue_files 文档串）。此处只读标准面。
            surface = ledger.entry_match_surface(entry)
            matched = sorted(commit_files & surface)
            if matched:
                hits.append((entry, matched))

        # 4. 硬阻断：命中即 fail-closed
        if not hits:
            return True, ""

        # 4b. C11（统筹裁定 2026-10-12）连坐前先做同源判活：
        #     仅"提交人＝该条目属主 sid 且该 sid 现判活（alive/degraded）"降级为 warn＋留痕；
        #     死会话条目、他班条目一律照拦（不放宽任何跨班保护面）。
        #     病根实测：崩溃静默期 --scan 批量立案，门原本不看活性是否已恢复
        #     ⇒ 今日 14 枚自挡死袋全部是这一形态（案卷＝维护三班台账 §十二.2）。
        committer = str(kwargs.get("session_id") or os.environ.get("ZEPHYR_SESSION_ID") or "").strip()
        blocking: list[tuple[dict, list[str]]] = []
        softened_notes: list[str] = []
        for entry, matched in hits:
            sid = str(entry.get("sid") or "")
            if committer and sid and sid == committer:
                state, signal = _self_block_verdict(sid)
                if state in ("alive", "degraded"):
                    _audit_softened(entry, matched, state, signal, root)
                    softened_notes.append(
                        f"sid={sid} 命中 {len(matched)} 件（现判活={state}/{signal}，"
                        f"判死证据={((entry.get('death_evidence') or {}).get('reason') or '')[:60]}）"
                    )
                    logger.warning(
                        "TAKEOVER-PENDING gate 降级放行（活班自挡，C11）：%s",
                        softened_notes[-1],
                    )
                    continue
            blocking.append((entry, matched))

        if blocking:
            detail = _format_block_detail(blocking)
            logger.error("TAKEOVER-PENDING gate block:\n%s", detail)
            return False, detail

        return True, "TAKEOVER-PENDING 降级放行（活班自挡，已留痕）：" + "；".join(softened_notes)

    return GateSpec(gate_id="TAKEOVER-PENDING", check=_check, priority=160)
