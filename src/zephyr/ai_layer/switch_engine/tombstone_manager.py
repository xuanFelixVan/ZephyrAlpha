# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.ai_layer.switch_engine.tombstone_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.intelligence.switch_engine.switch_engine (SwitchEngine, retired->tombstone 边);
#                zephyr.intelligence.switch_engine.switch_registry (SwitchRegistryStore);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.ai_layer.switch_engine.revert_drill (tombstone 抽样演练);
#             L1 内监 regime 信号（复活裁判，接线批挂接，本班只交付生成器）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 退役不删（墓碑制）：封存=git tag+status=tombstone+registry deprecated 链不删
#              （计数含 deprecated 全量），物理文件零删除；git tag 永不清（本模块无任何
#              untag/delete API）；封存必填项 fail-closed——failed_regime 与
#              revival_conditions 缺一拒封（DESIGN §②-D①"何种 regime/场景下失效"必填）；
#              复活≠直提：复活工单 route 恒 shadow_recheck（回 shadow 重走对比）；
#              TTL 清理=Owner 净删门（high human_gate），AI 永远只提案——本模块零清理
#              执行器（L6-#2 避让，见模块尾"提案注意"）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-D/§④-S5
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] failed_regime/revival_conditions 空->ValueError（拒封）；当前态非 retired
#                  ->SwitchTransitionError（封存只认 retired->tombstone 边）；非法复活触发器
#                  ->ValueError；git_runner 失败异常上抛（封存不落半态：先 tag 后落库）
# [TESTS] tests/ai_layer/switch_engine/test_tombstone_manager.py（封存全链 tag+状态+tombstone
#         字段非空/缺 regime 或条件拒封/非 retired 态拒封/复活工单 route=shadow_recheck/
#         非法触发器拒/退役件可查询/ttl_deadline 记录）
# [TTL] permanent
"""tombstone_manager — 墓碑管理器（S5 施工件）：封存登记 / 复活复检工单生成。

墓碑三问（DESIGN §②-D）：封存哪=git tag ``tombstone/<object_ref>/<yyyymmdd>``+registry
status=tombstone（模型走 OBJ_M model_registry 对接、文档走 docs/_archive/，本模块管
switch_registry 侧）；何时复活=四触发条件①regime 轮换②负载形态漂移③champion 同型失效
④Owner 手递卡，任一触发生成复检工单（L1 regime 门当复活裁判，接线批挂接）；何时清=
TTL 清理提案只提案不执行（见下）。

**提案注意（L6-#2 避让声明）**：TTL 清理判据（满 2 个月度体检窗+depgraph 反向依赖=0+
期间零复活动量）确认为 Owner 待办；注册表净删=high human_gate（宪法 §5），AI 永远只
提案。本模块 ttl_deadline 仅作 schema 完整性字段记录（初值取 config/switch_criteria.yaml
tombstone.ttl_windows，标注待追认），不消费、不触发、不建任何清理执行逻辑。
"""

from __future__ import annotations

from zephyr.shared.infra.process_pool import run_subprocess_hidden

import json
import subprocess
from collections.abc import Callable, Sequence
from datetime import timedelta
from pathlib import Path
from typing import Any, Final

from zephyr.intelligence.switch_engine.switch_engine import (
    SwitchTransitionError,
    SwitchEngine,
)
from zephyr.intelligence.switch_engine.switch_registry import (
    SwitchRegistryRecord,
    SwitchRegistryStore,
)
from zephyr.shared.utils.time_utils import now_utc

GIT_TAG_PREFIX: Final[str] = "tombstone/"
REVIVAL_TRIGGERS: Final[tuple[str, ...]] = (
    "regime_recurrence",        # ①regime 轮换：封存时登记的 regime 重现
    "load_shape_shift",         # ②负载/规模形态变化越阈（L1 内监信号）
    "champion_same_failure",    # ③champion 暴露同型失效
    "owner_manual",             # ④Owner 手递复活卡
)
REVIVAL_ROUTE: Final[str] = "shadow_recheck"
DEFAULT_TTL_WINDOWS: Final[int] = 2  # 仅 schema 完整性记录（L6-#2 避让，不消费不触发）
DAYS_PER_MONTH: Final[int] = 30      # 月度窗->日换算（记录用途，非清理计时器）


def _default_git_runner(args: Sequence[str]) -> str:
    completed = run_subprocess_hidden(  # trae_067 CREATE_NO_WINDOW（BARE-SUBPROCESS 治本 2026-09-24）
        ["git", *args], capture_output=True, text=True, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git {args[0]} 失败：{completed.stderr.strip()}")
    return completed.stdout.strip()


def tombstone_tag(object_ref: str, sealed_at: str) -> str:
    """封存 tag 名（DESIGN §②-D）：tombstone/<object_ref>/<yyyymmdd>。"""
    return f"{GIT_TAG_PREFIX}{object_ref}/{sealed_at[:10].replace('-', '')}"


def seal(
    engine: SwitchEngine,
    switch_id: str,
    *,
    failed_regime: str,
    revival_conditions: Sequence[str],
    seal_ref: str,
    ttl_windows: int = DEFAULT_TTL_WINDOWS,
    git_runner: Callable[[Sequence[str]], str] = _default_git_runner,
) -> SwitchRegistryRecord:
    """封存：校验->git tag（永不清）->落库 status=tombstone；必填项缺失/非 retired 态拒封。"""
    if not failed_regime:
        raise ValueError("封存缺 failed_regime（DESIGN §②-D① 必填：何种 regime/场景下失效）")
    if not revival_conditions:
        raise ValueError("封存缺 revival_conditions（复活条件字段非空是封存前置）")
    record = engine.store.require(switch_id)
    if record.state != "retired":
        raise SwitchTransitionError(
            f"封存只认 retired->tombstone 边，当前 state={record.state}"
        )
    sealed_at = now_utc().isoformat()
    tag = tombstone_tag(record.object_ref, sealed_at)
    git_runner(["tag", tag, "-m", f"tombstone {switch_id} regime={failed_regime}"])
    deadline = now_utc() + timedelta(days=ttl_windows * DAYS_PER_MONTH)
    return engine.store.update_state(
        switch_id,
        "tombstone",
        f"seal:{seal_ref}",
        patches={"tombstone": {
            "sealed_at": sealed_at,
            "seal_ref": seal_ref,
            "seal_tag": tag,
            "failed_regime": failed_regime,
            "revival_conditions": list(revival_conditions),
            "ttl_deadline": deadline.isoformat(),
            "ttl_windows_recorded": ttl_windows,
        }},
    )


def revival_ticket(
    store: SwitchRegistryStore,
    switch_id: str,
    *,
    trigger: str,
    evidence_ref: str,
    out_dir: Path,
) -> dict[str, Any]:
    """复活复检工单生成（任一复活条件触发->工单；route 恒 shadow_recheck，复活≠直提）。"""
    if trigger not in REVIVAL_TRIGGERS:
        raise ValueError(f"非法复活触发器 {trigger!r}，合法={REVIVAL_TRIGGERS}")
    record = store.require(switch_id)
    if record.state not in ("retired", "tombstone"):
        raise ValueError(f"仅 retired/tombstone 可开复活工单，当前 state={record.state}")
    ticket: dict[str, Any] = {
        "ticket_id": f"REV-{switch_id}-{now_utc().strftime('%Y%m%d%H%M%S')}",
        "switch_id": switch_id,
        "object_ref": record.object_ref,
        "trigger": trigger,
        "evidence_ref": evidence_ref,
        "route": REVIVAL_ROUTE,
        "revival_not_direct_promotion": True,
        "registered_conditions": record.tombstone.get("revival_conditions", []),
        "created_at": now_utc().isoformat(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{ticket['ticket_id']}.json").write_text(
        json.dumps(ticket, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return ticket


def list_tombstones(store: SwitchRegistryStore) -> list[SwitchRegistryRecord]:
    """退役件可查询（验收锚）：全部 tombstone 态 switch 行。"""
    store.ensure_schema()
    return store.list_by_state("tombstone")
