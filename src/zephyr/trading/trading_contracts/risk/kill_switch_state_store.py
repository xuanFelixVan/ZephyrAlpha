# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.kill_switch_state_store
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.trading_contracts.risk.trading_kill_switch; zephyr.shared.io.paths
# [CONSUMERS] trading_kill_switch.trigger/reset（同包持久化钩子）; 交易会话启动侧 rebuild_from_disk（G2b/G5 sim 部署接线点）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 落盘纪律=paper_hedge state 同款（data/runtime/ gitignored+原子写 tmp→os.replace）;
#  save fail-open（内存态已生效=主保护在手，落盘失败 CRITICAL 留痕不回滚熔断）;
#  rebuild 纯加闸不加放（auto_reenable 且冷却已过→不重臂交自然复评，其余 active 一律重臂）;
#  状态文件永不入库；本模块不持有第二真源状态（唯一真源=KILL_SWITCHES 内存态，本件只是其磁盘影子）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] save 失败不抛（CRITICAL 日志留痕）；rebuild 文件缺失=零重臂返回空表
# [TESTS] tests/trading/test_kill_switch_state_store.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""五级熔断触发态持久化（live O-6/S-3，admission G9 缺口闭环）。

病根：trading_kill_switch.KILL_SWITCHES 的 active 旗标为纯进程内存态，
交易进程重启后 active_switches() 恒空=熔断态蒸发（DAILY_LOSS"当日不再恢复"
语义在重启后失守）。本件把触发/复位落成磁盘影子，进程重启后 rebuild_from_disk()
重臂在飞熔断（纸面纪律对标 zephyr.risk.paper_hedge_leg 的 data/runtime state 文件）。

# [ALGO_FLOW] external: docs/03_modules/_domain_trading/algo_flow/kill_switch_state_store.yaml

用法（接线方视角）::

    from zephyr.trading.trading_contracts.risk import trading_kill_switch as tks
    from zephyr.trading.trading_contracts.risk import kill_switch_state_store as store

    tks.trigger(tks.KillSwitchLevel.DAILY_LOSS)      # 内部已自动落盘
    armed = store.rebuild_from_disk()                # 进程启动时重臂（返回重臂级别）
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

logger = logging.getLogger(__name__)

DEFAULT_STATE_RELATIVE: Final = "data/runtime/trading_kill_switch_state.json"
_STATE_VERSION: Final = 1


def default_state_path() -> Path:
    from zephyr.shared.io.paths import REPO_ROOT

    return Path(REPO_ROOT) / DEFAULT_STATE_RELATIVE


def save_state(state_path: Path | None = None, *, now: datetime | None = None) -> bool:
    """把 KILL_SWITCHES 内存态快照落盘（原子写 tmp→os.replace）。

    Returns:
        True=落盘成功；False=失败（CRITICAL 已留痕，调用方不回滚内存态）。
    """
    from zephyr.trading.trading_contracts.risk.trading_kill_switch import KILL_SWITCHES

    path = state_path or default_state_path()
    triggered_at = (now or datetime.now(tz=UTC)).isoformat()
    payload = {
        "version": _STATE_VERSION,
        "saved_at": triggered_at,
        "switches": {
            ks.level.value: {"active": bool(ks.active)} for ks in KILL_SWITCHES.values()
        },
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=1)
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return True
    except Exception as exc:  # noqa: BLE001 — save fail-open（见 INVARIANTS）
        logger.critical("KILL_SWITCH_STATE_SAVE_FAILED 落盘失败 path=%s error=%s", path, exc)
        return False


def rebuild_from_disk(
    state_path: Path | None = None,
    *,
    now: datetime | None = None,
) -> list[str]:
    """进程启动重臂：读磁盘影子，把仍应生效的熔断级 re-trigger。

    纯加闸不加放：auto_reenable=True 且 (now-saved_at) ≥ cooldown 的级别不重臂
    （交自然复评），其余 active 级别一律重臂（DAILY_LOSS 等非自恢复级跨重启维持）。
    文件缺失/损坏=零重臂（返回空表，CRITICAL 留痕——不阻断启动，主保护在逐单闸门）。

    Returns:
        重臂的级别名列表（如 ["DAILY_LOSS"]）。
    """
    from zephyr.trading.trading_contracts.risk.trading_kill_switch import (
        KILL_SWITCHES,
        trigger,
    )

    path = state_path or default_state_path()
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        switches = payload.get("switches") or {}
        saved_at = datetime.fromisoformat(payload.get("saved_at"))
    except Exception as exc:  # noqa: BLE001 — 损坏影子不阻断启动
        logger.critical("KILL_SWITCH_STATE_REBUILD_CORRUPT 影子损坏 error=%s", exc)
        return []

    now_dt = now or datetime.now(tz=UTC)
    rearmed: list[str] = []
    for level_name, snap in switches.items():
        if not snap.get("active"):
            continue
        ks = KILL_SWITCHES.get(level_name)  # type: ignore[arg-type]
        if ks is None:
            continue
        if ks.auto_reenable:
            elapsed = (now_dt - saved_at).total_seconds()
            if elapsed >= ks.cooldown_seconds > 0:
                logger.info(
                    "KILL_SWITCH_REBUILD_SKIP auto_reenable 冷却已过 level=%s elapsed=%.0fs",
                    level_name,
                    elapsed,
                )
                continue
        trigger(ks.level)
        rearmed.append(level_name)
        logger.warning("KILL_SWITCH_REARM 重臂 level=%s（跨重启维持熔断）", level_name)
    return rearmed
