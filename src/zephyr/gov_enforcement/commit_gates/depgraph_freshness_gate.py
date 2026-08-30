# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.depgraph_freshness_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.governance.audit.pg_probe (pg_offline_beyond/log_db_failopen，#ARCH-119 延迟 import); stdlib(json, datetime, logging)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] dual-threshold——depgraph 新鲜度 >30min WARNING(打印告警不阻断)，>24h 阻断 commit；数据源 .runtime/depgraph_scan_cache.json 的 _meta.saved_at 字段(generate_project_depgraph.py 写入，反映整体同步完成时间，优于 PG MAX(last_verified)——后者是单节点级时间戳，无法代表整体快照新鲜度)；fail-open——cache 文件缺失/JSON 解析失败/saved_at 缺失时放行(不阻断 commit，因 depgraph 同步可能是首次启动或新环境)
# [MODIFY-GUARD] gate_id="DEPGRAPH-FRESHNESS"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件缺失/JSON 解析失败/saved_at 缺失 -> 放行(True, detail)；>24h -> 阻断(False, detail)；>30min -> 放行(True) + 打印 WARNING；时钟漂移(saved_at 在未来) -> 视为 fresh 放行
# [TESTS] tests/governance/commit_gates/test_depgraph_freshness_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
depgraph_freshness_gate.py — depgraph 新鲜度门禁（dual-threshold，#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3.1）

治本目标（fail-silent 三要素之「可阻断」补强）：
  - Phase 2/3/4.2/4.3 已实现持久化 + 可发现 + 严重错误 block_next 硬阻断
  - 本 gate 补强 depgraph 同步新鲜度的「可阻断」——超 24h 未同步直接阻断 commit

病根（防御前移）
-----------------
- depgraph 是依赖关系唯一真源，但 sync 是 reconciler 异步触发
- 若 reconciler 触发链断裂（如 session_worktree_commit 绕过 GitCommitGateway），
  depgraph 长期不刷新，AI 在过期快照上做设计 = 幻觉温床（详见 L2 铁律）
- P4.3 已修复 session_worktree_commit 触发断链（治本根因A）
- 本 gate 在 commit 前再加一道防线——depgraph 太旧就阻断，强制 AI 先 sync

设计决策
--------
1. **dual-threshold 而非单一阈值**：
   - >30min WARNING（不阻断）：日常开发中 depgraph 短期过期无伤大雅，强阻断会过度
   - >24h 阻断：超 24h = 长期失同步，AI 在过期快照上设计 = 幻觉温床，必须阻断
2. **数据源 .runtime/depgraph_scan_cache.json _meta.saved_at**：
   - saved_at 是 generate_project_depgraph.py 写入的同步完成时间戳
   - 不读 PostgreSQL depgraph.last_verified —— 那是单节点级时间戳，不是整体快照时间
3. **fail-open 而非 fail-closed**：
   - cache 文件缺失（首次启动/新环境）-> 放行，因为阻断会导致首次 commit 无法进行
   - JSON 解析失败 -> 放行 + WARNING，避免 gate 自身故障阻塞开发
   - saved_at 字段缺失 -> 放行 + WARNING
4. **priority=67**：在 UNSAFE-DICT-SPREAD(66) 之后、PURE-SHIM(68) 之前——
   先校验基础结构（目录契约/ttl/...），再做架构新鲜度检查（depgraph），
   最后校验 [BLUEPRINT] 头部格式等元数据。原 adjudication 拟定 68，与 PURE-SHIM
   冲突，迁移到 67（同属"代码结构/架构"层级，语义无冲突）。
5. **always-on**：不限文件类型，每次 commit 都检查（depgraph 新鲜度与本次 commit 的
   文件无关，是项目整体状态检查）

Usage::

    from zephyr.gov_enforcement.commit_gates.depgraph_freshness_gate import make_depgraph_freshness_gate

    registry.register(make_depgraph_freshness_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: depgraph_freshness_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_depgraph_freshness_gate
#   name_en: make_depgraph_freshness_gate
#   intro: 构造 depgraph 新鲜度门禁 GateSpec（dual-threshold，阻断型）。
#   desc: 构造 depgraph 新鲜度门禁 GateSpec（dual-threshold，阻断型）。 Returns: GateSpec(gate_id="DEPGRAPH-FRESH…；源码 L130-L224
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

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_depgraph_freshness_gate"]

# depgraph 扫描缓存文件（generate_project_depgraph.py 写入）
_CACHE_REL = ".runtime/depgraph_scan_cache.json"

# 阈值（秒）
_WARN_SECONDS = 30 * 60  # 30 分钟 → WARNING
_BLOCK_SECONDS = 24 * 60 * 60  # 24 小时 → 阻断


def _parse_saved_at(saved_at_raw: str) -> datetime | None:
    """解析 saved_at ISO 时间戳（兼容带/不带时区）。

    generate_project_depgraph.py 用 datetime.now().isoformat() 写入（无时区），
    按本地时间解析后转 UTC 比较。

    Args:
        saved_at_raw: ISO 8601 时间戳字符串。

    Returns:
        UTC-aware datetime，或 None（解析失败）。
    """
    if not saved_at_raw:
        return None
    try:
        dt = datetime.fromisoformat(saved_at_raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        # 无时区 → 按本地时间解释，转 UTC
        dt = dt.astimezone(timezone.utc)
    return dt.astimezone(timezone.utc)


def make_depgraph_freshness_gate() -> GateSpec:
    """构造 depgraph 新鲜度门禁 GateSpec（dual-threshold，阻断型）。

    Returns:
        GateSpec(gate_id="DEPGRAPH-FRESHNESS", priority=67)。
        priority=67——在 UNSAFE-DICT-SPREAD(66) 之后、PURE-SHIM(68) 之前
        （先校验基础结构，再做架构新鲜度检查；原 adjudication 拟定 68，与
        PURE-SHIM 冲突，迁移到 67）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root: Path = gateway.project_root
        cache_path = project_root / _CACHE_REL

        # 1. 文件缺失——fail-open（首次启动/新环境）
        if not cache_path.is_file():
            return True, (f"depgraph scan cache not found ({_CACHE_REL}); skip freshness check (first-run or new env)")

        # 2. 读取 + JSON 解析——fail-open
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("depgraph scan cache parse failed: %s", e)
            return True, f"depgraph scan cache parse failed, skip: {e}"

        saved_at_raw = (data.get("_meta") or {}).get("saved_at")
        if not saved_at_raw:
            return True, "depgraph scan cache missing _meta.saved_at, skip"

        saved_at = _parse_saved_at(saved_at_raw)
        if saved_at is None:
            return True, f"depgraph scan cache _meta.saved_at unparseable: {saved_at_raw!r}"

        # 3. 计算新鲜度
        now_utc = datetime.now(timezone.utc)
        age_seconds = (now_utc - saved_at).total_seconds()

        # 容错：saved_at 在未来（时钟漂移/手工篡改）→ 视为 fresh
        if age_seconds < 0:
            logger.warning(
                "depgraph scan cache saved_at is in the future (%s vs %s); treating as fresh",
                saved_at_raw,
                now_utc.isoformat(),
            )
            return True, f"depgraph fresh (saved_at in future: {saved_at_raw})"

        # 4. dual-threshold 判定
        if age_seconds >= _BLOCK_SECONDS:
            # tracker #116 B2（#ARCH-119，报告 §1.3 联动修复）：探针证实 PG 离线
            # 超 24h 时，saved_at 停更是环境性（reconciler 无法连 PG 重建）而非
            # 施工失责——豁免阻断并留痕（critical_warn，当日同签名去重）。
            from zephyr.governance.audit.pg_probe import (  # noqa: PLC0415 延迟 import 防循环
                log_db_failopen,
                pg_offline_beyond,
            )

            if pg_offline_beyond(project_root, _BLOCK_SECONDS):
                hours_offline = int(age_seconds // 3600)
                log_db_failopen(
                    project_root,
                    "DEPGRAPH-FRESHNESS",
                    db_offline=True,
                    reason=(
                        f"探针证实 PG 离线超 24h，depgraph saved_at({saved_at_raw}) "
                        f"停更 {hours_offline}h 属环境性误伤，freshness 阻断豁免"
                    ),
                    session_id=kwargs.get("session_id", ""),
                )
                return True, (
                    f"depgraph stale {hours_offline}h but probe confirms PG offline >24h; "
                    f"freshness block exempted (tracker #116, 豁免已留痕)"
                )
            hours = int(age_seconds // 3600)
            detail = (
                f"depgraph scan stale: {hours}h since last sync "
                f"(saved_at={saved_at_raw}). "
                f"超过 24h 阈值——AI 在过期快照上设计=幻觉温床(L2铁律)。"
                f"请先运行 generate_project_depgraph.py 刷新 depgraph，再 commit。"
            )
            return False, detail

        if age_seconds >= _WARN_SECONDS:
            minutes = int(age_seconds // 60)
            detail = (
                f"WARN: depgraph scan {minutes}min since last sync "
                f"(saved_at={saved_at_raw}). 建议运行 generate_project_depgraph.py 刷新。"
            )
            logger.warning(detail)
            # 保留 print：gate 告警需直接出现在操作员控制台（commit UX），不依赖 logging 配置
            print(f"[GATE DEPGRAPH-FRESHNESS] {detail}")
            return True, detail

        return True, f"depgraph fresh (age={int(age_seconds)}s)"

    return GateSpec(gate_id="DEPGRAPH-FRESHNESS", check=_check, priority=67)
