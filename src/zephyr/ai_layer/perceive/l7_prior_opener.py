# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [MODULE] zephyr.ai_layer.perceive.l7_prior_opener
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.perceive.search_orders (SearchOrderJournal/SearchOrderDraft);
#                zephyr.ai_layer.heritage.priors (HeritagePriors prior_for/apply_exclusion/daily_share_exceeded——duck 注入);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] L1 开单链 l7_prior 路径（施工项 9 消费面：Owner/挖矿 SOP 按富矿先验开单时调用）;
#             tests/ai_layer/perceive/test_l7_prior_opener.py（假 priors 注入）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 纯开单翻译面（L7 DESIGN §2.4：消费触发=每次开单时调用，纯只读无事件依赖）;
#              trigger 恒='l7_prior'（白名单内），priority 恒=V3 prior_factor（越界由 priors 层拒收）;
#              排除词表只滤词不灭矿脉（apply_exclusion 每单保底 1 组，机检在本模块调用面）;
#              l7_prior 日占比超限=当日拒开（refused_l7_daily_share 留痕，非异常）;
#              先验格缺席=1.0 空先验正常开单（非错误）;
#              禁 datetime.now()/time.time()，一律 now_utc（可注入）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.4/§2.6（D-L7-03）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 日占比超限→返回 {"ok": False, "reason": "refused_l7_daily_share"}（不开单非异常）;
#                  keyword_groups 全空→ValueError（开单必须有词）; priors/ DB 不可达→异常上抛（不吞）
# [TESTS] tests/ai_layer/perceive/test_l7_prior_opener.py
# [TTL] permanent

"""l7_prior_opener — L1 施工项 9 消费面：L7 先验 → 定向搜索任务单（l7_prior 开单路径）。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md`` §2.4（L1 先验字段）+
§2.6（D-L7-03 防近亲繁殖）。L7 定稿（design_final）解锁本消费面：开单时读 V3 富矿因子
落 priority、读 V4 排除词表过滤 keyword_groups（保底 1 组）、日占比 ≤50% 闸（超限拒开留痕）。
priors 服务 duck 注入（测试零 DB）；journal 复用 SearchOrderJournal（开单即校验）。

# [ALGO_FLOW] external: docs/03_modules/_domain_ai_layer/algo_flow/l7_prior_opener.yaml
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Any, Final

from zephyr.ai_layer.heritage.priors import apply_exclusion, daily_share_exceeded
from zephyr.ai_layer.perceive.search_orders import SearchOrder, SearchOrderDraft, SearchOrderJournal
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = ["open_l7_prior_order", "l7_prior_daily_share_state"]

_L7_TRIGGER: Final = "l7_prior"


def l7_prior_daily_share_state(
    journal: SearchOrderJournal,
    priors: Any,  # noqa: any-abuse  priors服务duck注入缝位(头注DEPENDENCIES明示,测试零DB假体注入),非根实现Any
    *,
    now: datetime | None = None,
) -> tuple[bool, int, int]:
    """当日 l7_prior 占比判据（DESIGN §2.6 约束 2：≤50%/日）。返回 (超限?, l7 单数, 当日总数)。"""
    moment = now or now_utc()
    day_prefix = moment.strftime("%Y%m%d")
    todays = [o for o in journal.list_orders() if str(o.order_id).startswith(day_prefix)]
    l7_n = sum(1 for o in todays if o.trigger == _L7_TRIGGER)
    return daily_share_exceeded(l7_n, len(todays), priors.policy), l7_n, len(todays)


def open_l7_prior_order(
    journal: SearchOrderJournal,
    priors: Any,  # noqa: any-abuse  priors服务duck注入缝位(头注DEPENDENCIES明示,测试零DB假体注入),非根实现Any
    *,
    domain_id: str,
    mechanism_family: str,
    vein_id: str,
    trigger_ref: str,
    keyword_groups: Sequence[Sequence[str]],
    source_scope: Sequence[str] = (),
    budget: dict[str, int] | None = None,
    staging_path: str = "",
    expected_cards: int = 0,
    now: datetime | None = None,
    ttl_days: int = 7,
) -> dict[str, Any]:
    """L7 先验开单正门：读 V3/V4 → 过滤词组（保底 1 组）→ trigger='l7_prior' 单落 journal。

    返回 {"ok": True, "order": SearchOrder, "prior": 响应, "dropped_groups": [...]}；
    日占比超限 → {"ok": False, "reason": "refused_l7_daily_share", ...}（不开单留痕）。
    入参 keyword_groups=组级形态（L7 §2.6 约束 3 过滤语义）；落单前拍平为 L1 §2.3 扁平词表。
    """
    groups = [[str(w) for w in group] for group in keyword_groups]
    if not groups:
        raise ValueError("keyword_groups 空：l7_prior 开单必须有词")
    exceeded, l7_n, total_n = l7_prior_daily_share_state(journal, priors, now=now)
    if exceeded:
        log.warning("l7_prior 日占比超限拒开: %s/%s", l7_n, total_n)
        return {"ok": False, "reason": "refused_l7_daily_share", "l7_n": l7_n, "total_n": total_n}
    prior = priors.prior_for(domain_id, mechanism_family)
    kept, dropped = apply_exclusion(groups, prior.get("exclusion_keywords") or [])
    flat: list[str] = []
    for group in kept:
        for word in group:
            if word not in flat:
                flat.append(word)
    order: SearchOrder = journal.open_draft(
        SearchOrderDraft(
            vein_id=vein_id,
            vein_family=mechanism_family,
            trigger=_L7_TRIGGER,
            trigger_ref=trigger_ref,
            keyword_groups=flat,
            source_scope=tuple(str(s) for s in source_scope),
            budget=budget,
            priority=float(prior["prior_factor"]),
            staging_path=staging_path,
            expected_cards=expected_cards,
            now=now,
            ttl_days=ttl_days,
        )
    )
    log.info(
        "l7_prior 开单: %s domain=%s family=%s factor=%s frozen=%s dropped=%d",
        order.order_id,
        domain_id,
        mechanism_family,
        prior["prior_factor"],
        prior.get("frozen"),
        len(dropped),
    )
    return {"ok": True, "order": order, "prior": prior, "dropped_groups": dropped}
