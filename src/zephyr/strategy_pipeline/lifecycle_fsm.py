# [BLUEPRINT] MOD-BT-188 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.lifecycle_fsm
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.lifecycle.state_machine; zephyr.shared.security.secrets
#   （OwnerTokenGuard 读 ZEPHYR_OWNER_APPROVAL_TOKEN）
# [CONSUMERS] zephyr.strategy_pipeline.intake（sim 流转）; zephyr.strategy_pipeline.promotion_advisory
#   （sim→production 拍板执行器）; C6 管线状态治理
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 复用项目级 StateMachine 泛型基类；candidate→production 无直连边（A 方案治理边界：
#   Owner 门=sim→production 转换的 guard 要求 owner_token 与 secrets 键 ZEPHYR_OWNER_APPROVAL_TOKEN
#   sha256 常量时间比对（hmac.compare_digest），非空即真已废；键未配置=fail-closed 一律拒绝；
#   机器调用不带 token 必被拒）；非法转换抛 InvalidTransitionError（fail-closed）
# [MODIFY-GUARD] tests/strategy_pipeline/test_lifecycle_fsm.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTransitionError/TransitionGuardError（基类原样上抛）
# [TESTS] tests/strategy_pipeline/test_lifecycle_fsm.py
# [A_module] module_id=MOD-BT-188 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] lifecycle-fsm-mod-bt-188-20260915
"""策略生命周期 FSM——A 方案预授权状态机（挖矿真源 §2.5，复用因子版 8 态 10 转换模式）。

状态：candidate → sim → production（Owner 门）→ retired；shelved（留档侧枝）。
合法转换：
    candidate→sim        机器自动（guard=预授权三条件：§8 双窗过 ∧ BH-FDR 过 ∧ 无未决衰减预警）
    candidate→shelved    机器自动（redundant/差异化不足留档）
    shelved→candidate    机器自动（簇首退役后家族替身回补，未来批次用）
    sim→production       Owner 门（guard=owner_token 必填；机器不带 token 必拒）
    sim→shelved          机器自动（模拟盘衰减降档留档）
    production→retired   Owner 门（guard=owner_token）
    shelved→retired      机器自动
A 方案语义：candidate→sim 的 guard 三条件=Owner 已预授权的规则文本（本文件即规则真源），
逐条策略零人工；sim→production 强制 owner_token——机器流程不带 token，故天然停门。
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from dataclasses import dataclass
from typing import Any

from zephyr.shared.lifecycle.state_machine import (
    StateDefinition,
    StateMachine,
    StateMachineConfig,
    Transition,
    TransitionGuard,
)
from zephyr.shared.security.secrets import get_secret_or_default

logger = logging.getLogger(__name__)

OWNER_TOKEN_SECRET_KEY = "ZEPHYR_OWNER_APPROVAL_TOKEN"

CANDIDATE = "candidate"
SIM = "sim"
PRODUCTION = "production"
SHELVED = "shelved"
RETIRED = "retired"


@dataclass(frozen=True)
class SimPromotionContext:
    """candidate→sim 预授权三条件（guard 消费；字段均可机器验证）。"""

    dual_window_pass: bool          # §8：IS>0 ∧ 各 OOS 段>0 ∧ 衰减<0.5
    bh_fdr_pass: bool               # BH-FDR q≤0.10 批内过滤通过
    no_pending_decay_alert: bool    # decay_watch 无未决 decaying 行


class SimPromotionGuard(TransitionGuard):
    """预授权规则引擎——Owner 2026-09-15 圈定 A 方案的本体（规则文本=本类）。"""

    def check(self, source: str, target: str, context: dict[str, Any] | None = None) -> bool:
        if context is None:
            return False
        c = context.get("sim_promotion")
        if not isinstance(c, SimPromotionContext):
            return False
        return c.dual_window_pass and c.bh_fdr_pass and c.no_pending_decay_alert


class OwnerTokenGuard(TransitionGuard):
    """Owner 门——A 方案保留的人类回路：sim→production/production→retired 必带合法 owner_token。

    生产语义（S12 C4 升级，替代"非空即真"）：
    - 配置了 secrets 键 ZEPHYR_OWNER_APPROVAL_TOKEN →
      hmac.compare_digest(sha256(provided), sha256(secret)) 常量时间比对；
    - 未配置 → fail-closed（log+拒绝，绝不降级放行）；
    - 空串 token 与缺失同罪（机器流程不带 token 必拒）。
    """

    def check(self, source: str, target: str, context: dict[str, Any] | None = None) -> bool:
        token = (context or {}).get("owner_token") or ""
        if not token or not isinstance(token, str):
            return False
        secret = get_secret_or_default(OWNER_TOKEN_SECRET_KEY, "")
        if not secret:
            logger.warning("OwnerTokenGuard 拒绝 %s→%s：%s 未配置（fail-closed）",
                           source, target, OWNER_TOKEN_SECRET_KEY)
            return False
        return hmac.compare_digest(
            hashlib.sha256(token.encode("utf-8")).hexdigest(),
            hashlib.sha256(secret.encode("utf-8")).hexdigest(),
        )


def build_strategy_fsm(sid: str) -> StateMachine:
    """每策略一台 FSM 实例（对齐因子版 per-factor 模式）。"""
    config = StateMachineConfig(
        fsm_id=f"strategy_lifecycle_{sid}",
        states=[
            StateDefinition(state=CANDIDATE),
            StateDefinition(state=SIM),
            StateDefinition(state=PRODUCTION),
            StateDefinition(state=SHELVED),
            StateDefinition(state=RETIRED, is_terminal=True),
        ],
        transitions=[
            Transition(source=CANDIDATE, target=SIM, guard=SimPromotionGuard()),
            Transition(source=CANDIDATE, target=SHELVED),
            Transition(source=SHELVED, target=CANDIDATE),
            Transition(source=SHELVED, target=RETIRED),
            Transition(source=SIM, target=PRODUCTION, guard=OwnerTokenGuard()),
            Transition(source=SIM, target=SHELVED),
            Transition(source=PRODUCTION, target=RETIRED, guard=OwnerTokenGuard()),
        ],
        initial=CANDIDATE,
        owner_module="MOD-BT-188",
    )
    return StateMachine(config)
