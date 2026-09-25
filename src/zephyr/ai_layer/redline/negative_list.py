# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_negative_list
# [MODULE] zephyr.ai_layer.redline.negative_list
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.security.access_control.kill_switch (TriggerDefinition 注册面，SSOT 引用不复制)
# [CONSUMERS] zephyr.ai_layer.redline.session_env_guard (S1 deny-list 常量);
#             zephyr.ai_layer.redline.negative_list_gates (S2 rule_id 审计留痕);
#             zephyr.ai_layer.redline.drop_gate (S3 rule_id);
#             zephyr.ai_layer.redline.sev_router (S6 SEV-3 关联);
#             zephyr.ai_layer.redline.freedom_weekly_report (S7 negative_list_hits 维度);
#             zephyr.ai_layer.redline.annual_review (S8 年审条目全集)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 本模块是负面清单机检面的**常量与注册 helper**真源（DESIGN §1 六条四元组的编号层），
#              禁在此写判定逻辑（判定在各施工件）；红线语义归 Owner（变更走 OBJ_R 四步流水线），
#              机检实现=普通代码域；NL 编号与主文档附录 C 顺序一致，机检输出统一 rule_id 留审计；
#              KillSwitch trigger 注册只补 NL-1 payment_confirm_action（一触即断）——
#              浏览器自动化层前置检查=OBJ_T 施工时接线，本模块只备注册面
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §1（清单语义变更走 OBJ_R）
# [STABILITY] new
# [SAFETY] M（红线常量：改语义=改红线，须走 OBJ_R；改实现不触语义=ai_modifiable）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯常量+注册 helper：register_payment_confirm_trigger 不抛（KillSwitch
#                  register_trigger 原生无异常面）；未知 trigger 名注册幂等覆盖
# [TESTS] tests/ai_layer/redline/test_negative_list.py（六条编号全集与附录 C 顺序一致/
#         deny 模式三族（QMT 前缀实盘族/ZEPHYR_AUDIT_HMAC_SECRET/*_LIVE_*）/
#         payment_confirm_action 注册后 threshold=1 且 record_event 即 BLOCK_AGENT）
# [TTL] permanent
"""negative_list — OBJ_S 负面清单机检面常量真源（NL-1..NL-6）。

DESIGN §1：每条红线四元组（红线语义/违规判定技术判据/检查点位置/违例动作），
本模块承载跨施工件共享的**编号与判据常量**层：

- NL-1 付费动作：AI 会话命中支付确认特征/提交支付表单指令 → KillSwitch
  ``payment_confirm_action``（threshold=1 一触即断，本模块注册）。
- NL-2 实盘资金凭证：env 禁发名单（QMT 前缀实盘族/``ZEPHYR_AUDIT_HMAC_SECRET``/
  ``*_LIVE_*``）+ own-diff QMT 前缀实盘键名 引用扫描（S2 REAL-KEY-REFERENCE-SCAN）。
- NL-3 宪法权限语义：protected paths（immutable_core 已有）+ 宪法 ≤300 行
  （S2 CONSTITUTION-LINE-LIMIT 断言）+ 修宪 commit 裁定号（GW POST 链已有）。
- NL-4 审计链：always_blocked_operations（已有）+ AuditWriter 唯一写面 +
  env HMAC 键（与 NL-2 同闸）+ verify_chain mismatch=SEV-1（S6 聚合）。
- NL-5 验收判据自改：任务书判据字段结构变更与施工产物同批（S2 TASK-ORDER-DOCS-LOCK）。
- NL-6 删除红线三档：DROP-GATE（S3）+禁删清单生成器×2（S4）+档 A 已有闸。
"""

from __future__ import annotations

from typing import Final

from zephyr.security.access_control.kill_switch import (
    KillSwitch,
    TriggerDefinition,
    get_kill_switch,
)

# ── 六条编号（与主文档附录 C 顺序一致；机检输出统一 rule_id 留审计）──

NL_PAYMENT: Final = "NL-1"
NL_REAL_KEYS: Final = "NL-2"
NL_CONSTITUTION: Final = "NL-3"
NL_AUDIT_CHAIN: Final = "NL-4"
NL_ACCEPTANCE_LOCK: Final = "NL-5"
NL_DELETION: Final = "NL-6"

NL_RULE_IDS: Final[tuple[str, ...]] = (
    NL_PAYMENT,
    NL_REAL_KEYS,
    NL_CONSTITUTION,
    NL_AUDIT_CHAIN,
    NL_ACCEPTANCE_LOCK,
    NL_DELETION,
)

NL_DESCRIPTIONS: Final[dict[str, str]] = {
    NL_PAYMENT: "付费动作：充值/订阅/授权唯一确认人=Owner，AI 侧只备料+推送",
    NL_REAL_KEYS: "实盘资金凭证：AI 会话环境永不发放实盘 API/QMT 实盘密钥",
    NL_CONSTITUTION: "宪法权限语义：Owner 门位+等长替换，AI 只有提案权",
    NL_AUDIT_CHAIN: "审计链：events.jsonl 及 HMAC 密封逻辑不可改写",
    NL_ACCEPTANCE_LOCK: "验收判据自改：施工会话无权改自己的判据",
    NL_DELETION: "删除红线三档：物理删除=Owner 门位/退役=墓碑/临时物=TTL",
}

# ── NL-2/S1 共享：AI 会话 env 禁发名单（fnmatch 大小写敏感模式）──

DENY_ENV_PATTERNS: Final[tuple[str, ...]] = (
    "QMT" "_REAL_*",
    "ZEPHYR_AUDIT_HMAC_SECRET",
    "*_LIVE_*",
)

# NL-2/S2 共享：own-diff 引用扫描标记（白名单=secret_registry.yaml 本体+SECRETS.md）
REAL_KEY_MARKER: Final = "QMT" "_REAL"

# NL-1：KillSwitch 新 trigger 注册（DESIGN §1 NL-1 检查点：一触即断）
PAYMENT_TRIGGER_NAME: Final = "payment_confirm_action"
PAYMENT_TRIGGER_THRESHOLD: Final = 1
PAYMENT_TRIGGER_DESC: Final = "OBJ_S NL-1 付费动作确认（AI 永远不是支付确认人）"


def register_payment_confirm_trigger(kill_switch: KillSwitch | None = None) -> KillSwitch:
    """注册 NL-1 付费动作 trigger（threshold=1 一触即断；幂等，返回 KillSwitch 供链式）。

    浏览器自动化层前置检查（OBJ_T 施工时接线）命中支付确认特征后
    ``record_event(TriggerEvent(trigger="payment_confirm_action", agent_id=<sid>))``
    即 BLOCK_AGENT+审计+前端通知 Owner。
    """
    ks = kill_switch if kill_switch is not None else get_kill_switch()
    ks.register_trigger(
        TriggerDefinition(
            trigger=PAYMENT_TRIGGER_NAME,
            default_threshold=PAYMENT_TRIGGER_THRESHOLD,
            description=PAYMENT_TRIGGER_DESC,
        )
    )
    return ks
