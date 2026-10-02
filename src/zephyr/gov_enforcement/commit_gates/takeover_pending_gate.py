# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.takeover_pending_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# create-guard-not-dup: 本模块=接管待决硬阻断门禁（读接管台账拦未接管资源面的提交），非 algo_flow 解析/渲染/翻译对齐能力——docstring 锚词 "ALGO FLOW" 仅因 external 锚格式含该词，语义零交集
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)；scripts.governance.session_takeover_ledger（load_open_entries/entry_match_surface，函数内延迟 import 防循环）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar（in_process_gate_registry.yaml YAML 驱动注册）；zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——commit 文件（repo-relative posix）命中任一 open 接管条目命中面（held_files+worktree dirty_files+staging files）时阻断，detail 含死亡证据+接管处方+--resolve 指引（下一个 AI 想绕都绕不过，必须先按清单接管——00_orchestration.md §2.2 L3 门禁显化）；tests/ 豁免；台账缺失/损坏行/ledger 模块不可达 fail-open（logger.warning 检测器失效）；检出命中 fail-closed 阻断
# [MODIFY-GUARD] gate_id="TAKEOVER-PENDING"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；判据/命中面变更须与 scripts/governance/session_takeover_ledger.py 同批
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——ledger 读取/import 异常降级为 fail-open（passed=True，logger.warning）；检出命中 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/test_session_takeover_ledger.py
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

Usage::

    from zephyr.gov_enforcement.commit_gates.takeover_pending_gate import make_takeover_pending_gate

    # 经 in_process_gate_registry.yaml 自动注册（gate_auto_registrar），无需手工 register
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_takeover_pending_gate"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注


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

        # 3. 归一化 commit 文件为 repo-relative posix，逐条目求命中
        def _norm(f: str) -> str:
            return Path(f).as_posix()

        commit_files = {_norm(f) for f in files or []}
        commit_files = {f for f in commit_files if not is_test_exempt(f)}
        if not commit_files:
            return True, ""

        hits: list[tuple[dict, list[str]]] = []
        for entry in open_entries:
            surface = ledger.entry_match_surface(entry)
            matched = sorted(commit_files & surface)
            if matched:
                hits.append((entry, matched))

        # 4. 硬阻断：命中即 fail-closed
        if hits:
            detail = _format_block_detail(hits)
            logger.error("TAKEOVER-PENDING gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="TAKEOVER-PENDING", check=_check, priority=160)
