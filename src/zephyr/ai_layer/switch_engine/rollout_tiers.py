# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.ai_layer.switch_engine.rollout_tiers
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.intelligence.switch_engine.switch_engine (规则对象 canary=warn 档/promote=block 档同线);
#             ruling_registry（裁定登记挂接=本班只产出登记载荷，写入走正式通道）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 灰度三档出厂通用路径（DESIGN §②-G，EXEMPT-ZONE-FM 先例升格）：
#              shadow(只记录)->warn(留痕+审计+通知不阻断)->block(阻断)；升档机检=最短驻留
#              月度窗+误报=0+Owner 知情，warn->block 另须 Owner 门位+裁定登记+渐进收敛
#              grandfather 强制（存量豁免、新引入阻断）；降档（放松）同走 Owner 门位；
#              每档进出留痕（TierLedger 只追加，禁改写删除）；flag 出厂翻转只产载荷
#              建议不经本模块执行（Owner 门位）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-G/§④-S8
# [STABILITY] new
# [SAFETY] M（block 档涉阻断语义——本模块只登记与校验，不触发 flag 翻转）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 跳档/反向升级->ValueError（fail-closed）；驻留窗不足/误报非零/缺 Owner
#                  知情/缺裁定登记->ValueError 拒升；降档缺 owner_ack->ValueError；
#                  grandfather 输入含非字符串->ValueError
# [TESTS] tests/ai_layer/switch_engine/test_rollout_tiers.py（shadow->warn 驻留+误报机检/
#         warn->block 五前置缺一拒/跳档拒/降档须 owner_ack 且留痕可回退/ledger 只追加/
#         grandfather 存量豁免新引入阻断/升档载荷含 ruling_ref）
# [TTL] permanent
"""rollout_tiers — 灰度三档执行件（S8 施工件）：升降档机检+渐进收敛校验+裁定登记载荷。

把 EXEMPT-ZONE-FM 真实路径（post-commit warn reconciler->pre-commit 阻断 gate+渐进收敛）
升格为一切新约束的出厂通用路径。规则类对象的 canary 期即复用本表：gate 类 canary=warn
档，promote=block 档——灰度三档与状态机在规则对象上是同一条线（DESIGN §②-G 尾注）。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Final

from zephyr.shared.utils.time_utils import now_utc

TIER_SHADOW: Final[str] = "shadow"
TIER_WARN: Final[str] = "warn"
TIER_BLOCK: Final[str] = "block"
_TIER_ORDER: Final[dict[str, int]] = {TIER_SHADOW: 0, TIER_WARN: 1, TIER_BLOCK: 2}

TIER_BEHAVIORS: Final[dict[str, str]] = {
    TIER_SHADOW: "record_only（只记录不动作，触发率/误报统计积累）",
    TIER_WARN: "audit_notify_only（留痕+审计+通知，不阻断）",
    TIER_BLOCK: "block（阻断；出厂翻转=Owner 门位）",
}
MIN_MONTHLY_WINDOWS: Final[int] = 1  # 每档最短驻留=1 个月度体检窗（config/switch_criteria.yaml）

RULING_ACTION_UPGRADE: Final[str] = "rollout_tier_upgrade"
RULING_ACTION_DOWNGRADE: Final[str] = "rollout_tier_downgrade"


class TierLedger:
    """三档台账：每档进出留痕（只追加禁改写），升级/降档全走机检。"""

    def __init__(
        self,
        object_ref: str,
        *,
        start_tier: str = TIER_SHADOW,
        sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        if start_tier not in _TIER_ORDER:
            raise ValueError(f"非法起始档 {start_tier!r}")
        self._object_ref = object_ref
        self._entries: list[dict[str, Any]] = []
        self._sink = sink
        self._tier = start_tier

    @property
    def tier(self) -> str:
        return self._tier

    @property
    def entries(self) -> list[dict[str, Any]]:
        """进出留痕只读视图（深拷贝防篡改；验收锚：升级有留痕）。"""
        import copy

        return copy.deepcopy(self._entries)

    def upgrade_to(
        self,
        new_tier: str,
        *,
        evidence_ref: str,
        windows_in_tier: int,
        false_positives: int,
        owner_ack: bool,
        ruling_ref: str,
        grandfather_enforced: bool,
    ) -> dict[str, Any]:
        """升档机检：顺序+驻留+误报+知情，warn->block 五前置缺一拒。"""
        if new_tier not in _TIER_ORDER:
            raise ValueError(f"非法目标档 {new_tier!r}")
        if _TIER_ORDER[new_tier] != _TIER_ORDER[self._tier] + 1:
            raise ValueError(
                f"升档只许逐级：{self._tier} -> {new_tier} 跳档/反向（合法下一档="
                f"{self._next_tier()}）"
            )
        if windows_in_tier < MIN_MONTHLY_WINDOWS:
            raise ValueError(f"驻留不足：{windows_in_tier} < {MIN_MONTHLY_WINDOWS} 个月度体检窗")
        if false_positives != 0:
            raise ValueError(f"误报非零（{false_positives}），升档条件=误报=0")
        if not owner_ack:
            raise ValueError("升档缺 Owner 知情确认（owner_ack）")
        if not evidence_ref:
            raise ValueError("升档缺 evidence_ref（留痕不可空）")
        if new_tier == TIER_BLOCK:
            if not ruling_ref:
                raise ValueError("warn -> block 缺裁定登记（ruling_registry 挂接载荷必附 ruling_ref）")
            if not grandfather_enforced:
                raise ValueError("warn->block 缺渐进收敛 grandfather 强制（存量豁免条款）")
        entry = self._append(
            action=RULING_ACTION_UPGRADE,
            from_tier=self._tier,
            to_tier=new_tier,
            evidence_ref=evidence_ref,
            ruling_ref=ruling_ref,
        )
        self._tier = new_tier
        return entry

    def downgrade_to(
        self, new_tier: str, *, evidence_ref: str, owner_ack: bool
    ) -> dict[str, Any]:
        """降档（放松）同走 Owner 门位：owner_ack 必附；留痕后即回退（可回退验收锚）。"""
        if new_tier not in _TIER_ORDER:
            raise ValueError(f"非法目标档 {new_tier!r}")
        if _TIER_ORDER[new_tier] >= _TIER_ORDER[self._tier]:
            raise ValueError(f"downgrade_to 只收放松方向：{self._tier} -> {new_tier}")
        if not owner_ack:
            raise ValueError("降档（放松）同走 Owner 门位：缺 owner_ack 拒降")
        if not evidence_ref:
            raise ValueError("降档缺 evidence_ref（每档进出留 ruling 痕）")
        entry = self._append(
            action=RULING_ACTION_DOWNGRADE,
            from_tier=self._tier,
            to_tier=new_tier,
            evidence_ref=evidence_ref,
            ruling_ref="",
        )
        self._tier = new_tier
        return entry

    def _append(
        self, *, action: str, from_tier: str, to_tier: str, evidence_ref: str, ruling_ref: str
    ) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "object_ref": self._object_ref,
            "action": action,
            "from_tier": from_tier,
            "to_tier": to_tier,
            "at": now_utc().isoformat(),
            "evidence_ref": evidence_ref,
            "ruling_ref": ruling_ref,
        }
        self._entries.append(entry)
        if self._sink is not None:
            self._sink(entry)
        return entry

    def _next_tier(self) -> str:
        return TIER_WARN if self._tier == TIER_SHADOW else TIER_BLOCK


@dataclass(frozen=True)
class GrandfatherResult:
    """渐进收敛校验结果（git ls-tree HEAD 先例：存量跳过允许维护，新引入阻断）。"""

    allowed_existing: list[str] = field(default_factory=list)
    blocked_new: list[str] = field(default_factory=list)

    @property
    def all_clear(self) -> bool:
        return not self.blocked_new


def grandfather_filter(
    violations: list[str], baseline_inventory: set[str]
) -> GrandfatherResult:
    """存量豁免/新引入阻断二分（baseline=封存时点的 ls-tree 现值清单）。"""
    allowed: list[str] = []
    blocked: list[str] = []
    for item in violations:
        if not isinstance(item, str):
            raise ValueError(f"违规项须为字符串：{item!r}")
        (allowed if item in baseline_inventory else blocked).append(item)
    return GrandfatherResult(allowed_existing=allowed, blocked_new=blocked)
