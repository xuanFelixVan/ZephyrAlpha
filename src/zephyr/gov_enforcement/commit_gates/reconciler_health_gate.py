# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.reconciler_health_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.governance.audit.reconciliation_registry (_check_recent_blocks, _check_recent_critical_warns)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] dual-level——block_next 级别失败硬阻断 commit，critical_warn 级别失败打印警告不阻断；fail-open（governance.db 缺失/查询失败时放行）；复用 reconciliation_registry._check_recent_blocks/_check_recent_critical_warns（不复制 SQL，消除真源分裂）；always-on（reconciler 健康与本次 commit 文件无关，是项目整体状态检查）
# [MODIFY-GUARD] gate_id="RECONCILER-HEALTH"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] governance.db 缺失/查询异常 -> 放行(True, detail)；block_next 记录存在 -> 阻断(False, detail)；critical_warn 记录存在 -> 放行(True) + 打印 WARNING
# [TESTS] tests/governance/commit_gates/test_reconciler_health_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
reconciler_health_gate.py — reconciler 健康度门禁（#ARCH-DATAQUALITY-V1.7）

治本目标
--------
将 reconciler 健康检查从 ad-hoc banner（_print_block_banner/_print_critical_warn_banner
直接在 GitCommitGateway.commit 中调用）提升为正式 CommitGateRegistry gate。

问题（防御前移）
----------------
- session_worktree_commit 通过 _run_pre_commit_gates 调用 check_all()，运行所有注册 gate
- 但 _print_block_banner/_print_critical_warn_banner 是在 GitCommitGateway.commit 中直接
  调用的，不走 gate registry —— session_worktree_commit 路径不会触发 reconciler 健康检查
- 后果：session_worktree_commit 可以绕过 reconciler 健康检查（与 #ARCH-DEPGRAPH-RECONCILER-FAILSILENT
  Phase 4.2 的"block_next 硬阻断"设计意图冲突）

治本方案
--------
创建正式 gate 并注册到 CommitGateRegistry：
  1. 复用 _check_recent_blocks / _check_recent_critical_warns（不复制 SQL，消除真源分裂）
  2. block_next -> 硬阻断（与 _print_block_banner 语义一致）
  3. critical_warn -> 打印警告不阻断（与 _print_critical_warn_banner 语义一致）
  4. fail-open：governance.db 缺失/查询失败时放行（与现有 banner 一致）

设计权衡
--------
1. **复用而非复制**：import _check_recent_blocks/_check_recent_critical_warns，
   不复制 SQL 查询逻辑（消除多真源）。
2. **priority=64**：在 UNSAFE-DICT-SPREAD(65)/DEPGRAPH-FRESHNESS(67) 之前——先检查
   reconciler 整体健康度，再检查 depgraph 新鲜度（reconciler 故障比 depgraph 过期更紧急）。
3. **always-on**：reconciler 健康与本次 commit 文件无关，是项目整体状态检查。
4. **与现有 banner 共存**：_print_block_banner 仍在 GitCommitGateway.commit 中直接调用
   （向后兼容），本 gate 在 session_worktree_commit 路径补齐检查。两条路径都有
   block_next 检查，但这是有意的冗余（defense in depth）——gate 是统一入口，
   banner 是 GitCommitGateway 专用补充。

Usage::

    from zephyr.gov_enforcement.commit_gates.reconciler_health_gate import make_reconciler_health_gate
    registry.register(make_reconciler_health_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: reconciler_health_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_reconciler_health_gate
#   name_en: make_reconciler_health_gate
#   intro: 构造 reconciler 健康度门禁 GateSpec（dual-level，阻断型）。
#   desc: 构造 reconciler 健康度门禁 GateSpec（dual-level，阻断型）。 Returns: GateSpec(gate_id="RECONCILER-HEALT…；源码 L144-L240
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.governance.audit.reconciliation_registry import (
    _check_recent_blocks,
    _check_recent_critical_warns,
)

check_recent_critical_warns = _check_recent_critical_warns  # public alias（Stage 4 公共化）

check_recent_blocks = _check_recent_blocks  # public alias（Stage 4 公共化）


logger = logging.getLogger(__name__)

__all__ = ["make_reconciler_health_gate"]

# T5 告警卫生（2026-08-14，#ARCH-RECONCILER-AUTO-DELETE-GOV-001 裁定5）：
# critical_warn 横幅 24h dedup——同一告警内容签名 24h 内只打印一次，
# 新增/变化的告警照常打印（真告警不被淹没，恒定噪音不刷屏）。
_WARN_DEDUP_SECONDS = 24 * 3600


def _warn_signature(warns: list[dict]) -> str:
    """告警内容签名（gate_id+detail 排序哈希）——内容不变=同一条告警。"""
    parts = sorted(f"{w.get('gate_id', '?')}|{w.get('detail', '')}" for w in warns)
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]


def _should_print_warn(project_root, sig: str) -> bool:
    """24h dedup 判定：同签名 24h 内已打印→False；否则记录并放行打印。

    状态落盘 .runtime/reconciler_health_warn_dedup.json（gitignored 运行区）。
    fail-open：任何 IO 异常都允许打印（告警可见性优先于降噪）。
    """
    state_path = Path(str(project_root)) / ".runtime" / "reconciler_health_warn_dedup.json"
    # epoch 秒比较：now_utc().timestamp() 替代 time.time()（DATETIME-NOW-FORBIDDEN 对齐）
    from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415 — 避免模块级循环

    now = now_utc().timestamp()
    try:
        st = json.loads(state_path.read_text(encoding="utf-8"))
        if st.get("sig") == sig and now - float(st.get("ts", 0)) < _WARN_DEDUP_SECONDS:
            return False
    except Exception:  # noqa: BLE001 — 状态缺失/损坏=首次打印
        pass
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"sig": sig, "ts": now}), encoding="utf-8")
    except Exception:  # noqa: BLE001 — 落盘失败不阻断打印
        pass
    return True


def make_reconciler_health_gate() -> GateSpec:
    """构造 reconciler 健康度门禁 GateSpec（dual-level，阻断型）。

    Returns:
        GateSpec(gate_id="RECONCILER-HEALTH", priority=64)。
        priority=64——在 UNSAFE-DICT-SPREAD(65)/DEPGRAPH-FRESHNESS(67) 之前
        （reconciler 故障比 depgraph 过期更紧急，先检查整体 reconciler 健康）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root

        # 1. 检查 block_next 级别失败——硬阻断
        # 治本（2026-08-01）：用 public alias（check_recent_blocks）而非私有引用
        # （_check_recent_blocks），使 monkeypatch 能拦截——public alias 设计初衷即为
        # 测试可注入（Stage 4 公共化）。原代码用私有引用绕过了 alias，导致测试无法 mock。
        try:
            blocks = check_recent_blocks(project_root)
        except Exception as e:  # noqa: BLE001 — fail-open: 查询异常不阻断
            logger.warning("RECONCILER-HEALTH: block_next query failed: %s", e)
            blocks = []

        if blocks:
            detail_lines = [f"RECONCILER-HEALTH: {len(blocks)} blocking reconciler failure(s) in last 24h:"]
            for b in blocks[:5]:
                detail_lines.append(f"  - [{b['logged_at']}] {b['gate_id']}: {b['detail']}")
            if len(blocks) > 5:
                detail_lines.append(f"  ... and {len(blocks) - 5} more (query governance.db)")
            detail_lines.append(
                "  Action: fix failures then run resolve_blocks() to clear. Escape: commit(allow_overlap=True)."
            )
            detail = "\n".join(detail_lines)
            logger.error("RECONCILER-HEALTH gate block:\n%s", detail)
            return False, detail

        # 2. 检查 critical_warn 级别失败——打印警告不阻断
        try:
            warns = check_recent_critical_warns(project_root)
        except Exception as e:  # noqa: BLE001 — fail-open: 查询异常不阻断
            logger.warning("RECONCILER-HEALTH: critical_warn query failed: %s", e)
            warns = []

        if warns:
            warn_lines = [f"RECONCILER-HEALTH WARN: {len(warns)} critical reconciler failure(s) in last 24h:"]
            for w in warns[:5]:
                warn_lines.append(f"  - [{w['logged_at']}] {w['gate_id']}: {w['detail']}")
            if len(warns) > 5:
                warn_lines.append(f"  ... and {len(warns) - 5} more (query governance.db)")
            warn_lines.append("  Investigate before proceeding (non-blocking warning).")
            warn_detail = "\n".join(warn_lines)
            # T5：24h dedup——同签名告警 24h 内只打印一次，仍落 logger 留痕
            if _should_print_warn(project_root, _warn_signature(warns)):
                logger.warning(warn_detail)
                # 保留 print：gate 告警需直接出现在操作员控制台（commit UX），不依赖 logging 配置
                print(f"[GATE RECONCILER-HEALTH] {warn_detail}")
            else:
                logger.info("RECONCILER-HEALTH WARN deduped (same signature within 24h)")
            return True, warn_detail

        # 2.5 T2③ 删除审计覆盖率检查（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）：
        # worker status 落盘的 ops_guard_audit_stats 中 audit_failed>0
        # = 删除动作未 100% 落审计（覆盖率缺口）→ warn 不阻断。
        try:
            import glob as _glob
            import json as _json
            import time as _time

            _cutoff = _time.time() - 24 * 3600
            _reports = _glob.glob(
                str(Path(project_root) / ".runtime" / "reconcile_reports" / "reconcile_status_*.json")
            )
            _gap_total = 0
            _judge_total = 0
            for _rp in _reports:
                try:
                    if Path(_rp).stat().st_mtime < _cutoff:
                        continue
                    _stats = _json.loads(Path(_rp).read_text(encoding="utf-8")).get("ops_guard_audit_stats")
                    if _stats:
                        _gap_total += int(_stats.get("audit_failed", 0))
                        _judge_total += int(_stats.get("judge_calls", 0))
                except Exception:  # noqa: BLE001 — 单文件损坏跳过
                    continue
            if _gap_total > 0:
                _cov_detail = (
                    f"RECONCILER-HEALTH WARN: 删除审计覆盖率缺口——24h 内 "
                    f"ops_guard 判定 {_judge_total} 次但审计落盘失败 {_gap_total} 次"
                    "（T2③ 覆盖率<100%，查 .runtime/gate_audit/ 写入权限/磁盘）"
                )
                logger.warning(_cov_detail)
                print(f"[GATE RECONCILER-HEALTH] {_cov_detail}")
        except Exception:  # noqa: BLE001 — 覆盖率检查失败不阻断
            pass

        return True, "reconciler health OK (0 block_next, 0 critical_warn in last 24h)"

    return GateSpec(gate_id="RECONCILER-HEALTH", check=_check, priority=64)
