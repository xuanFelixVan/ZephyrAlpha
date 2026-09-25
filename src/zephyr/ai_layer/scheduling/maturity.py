# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] zephyr.ai_layer.scheduling.maturity
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.utils.time_utils (now_utc);
#                zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.ai_layer.scheduling.order_daemon (T0 门闸挂接);
#             zephyr.ai_layer.scheduling.dispatcher（held_maturity 工单重评唤醒入口，事件触发非轮询）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 阈值只读自 config/schedule_gate_policy.yaml（尺子=治理层资产，AI 层不持尺；改动走
#              OBJ_R 四步流水线，DESIGN §2.2）；fail-closed 加载（缺文件/缺节→SchedulingPolicyError，绝不给
#              静默默认值）；判定=纯函数（now 可注入，判据可全枚举）；新鲜度超龄→计数清零重攒
#              （陈旧胜利不开门，DESIGN M3）；白名单缺席=零区域开闸（M4 冷启动诚实语义，
#              L5-#2 待 Owner 点头）；held_maturity 转正=区域新 experiment archived 事件重评触发
#              （事件唤醒非轮询）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md §2.2（D-L5-03 设计真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] policy 缺文件/缺节/坏 YAML→SchedulingPolicyError；stats 缺键→ValueError（调用方契约）；
#                  collect_region_stats 只读（conn 注入，异常上抛不吞）
# [TESTS] tests/ai_layer/scheduling/test_maturity.py（M1-M4 全枚举：单胜不开/胜率线/样本下限/
#         draw 不计分母/超龄清零/白名单缺席零开闸/policy fail-closed/SQL 渲染含域聚合/
#         held_maturity 转正留痕）
# [TTL] permanent
"""maturity — L5 区域成熟度门闸（D-L5-03，T0 门闸）：M1-M4 可配置判定 + 区域聚合 + 挂起转正。

区域=候选卡/实验卡既有 ``domain_id`` 词表（L2 入库登记口径），不新造区域分类学；
OBJ_M/OBJ_T/OBJ_R 各算一个专域，七段骨架自身=骨架域（永远走 Owner 门，router R3 管辖）。

四阈值（初值全部收进 policy 常量层，Owner 夜批追认；DESIGN §5.2 反省：设计定值非实测标定）::

    M1 区域 win 计数 ≥ 2        单胜不开闸（防噪声单点）
    M2 对比胜率 ≥ 60%           win/(win+loss)；draw 不计分母；样本下限 N_total ≥ 3
    M3 证据新鲜度 ≤ 90 天        超龄区域计数清零重攒（陈旧胜利不开门）
    M4 区域白名单               冷启动 Owner 点头清单（本班结构落位置空，L5-#2 治理立案保留）

触发时点：T0 门闸在胜者到达时评一次（不过=工单 held_maturity 挂起）；区域每有新 experiment
archived 事件重算，过线即自动转 pending——事件唤醒非轮询（宪法 §9.3）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final, Mapping

import yaml

from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = [
    "DEFAULT_POLICY_PATH",
    "SchedulingPolicyError",
    "SchedulingGateVerdict",
    "load_gate_policy",
    "evaluate_region",
    "region_aggregation_sql",
    "collect_region_stats",
    "promote_held_orders",
]

DEFAULT_POLICY_PATH: Final = REPO_ROOT / "config" / "schedule_gate_policy.yaml"

REQUIRED_SECTIONS: Final[tuple[str, ...]] = (
    "policy_id",
    "maturity",
    "priority",
    "quota",
    "compute_classes",
    "dispatch",
    "order_states",
)
REQUIRED_MATURITY_KEYS: Final[tuple[str, ...]] = (
    "m1_min_wins",
    "m2_min_win_rate",
    "m2_min_samples",
    "m3_freshness_max_days",
    "m4_first_batch_whitelist",
)


class SchedulingPolicyError(Exception):
    """门闸常量层残缺/畸形（fail-closed：宁可不开闸，不可错开闸）。

    :param details: 敏感上下文（路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


def load_gate_policy(path: Path | str | None = None) -> dict[str, Any]:
    """加载 L5 门闸常量层（只读）。缺文件/缺节/坏 YAML 一律 SchedulingPolicyError，不给静默默认。

    :param path: 常量文件路径（缺省=config/schedule_gate_policy.yaml；测试注入 tmp_path）
    """
    target = Path(path) if path else DEFAULT_POLICY_PATH
    if not target.exists():
        raise SchedulingPolicyError("schedule_gate_policy 缺文件", details={"path": str(target)})
    try:
        raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SchedulingPolicyError(f"schedule_gate_policy 坏 YAML:{exc}") from exc
    if not isinstance(raw, Mapping):
        raise SchedulingPolicyError(f"schedule_gate_policy 顶层需映射，得:{type(raw).__name__}")
    missing = [s for s in REQUIRED_SECTIONS if s not in raw]
    if missing:
        raise SchedulingPolicyError(f"schedule_gate_policy 缺节:{','.join(missing)}")
    maturity = raw["maturity"]
    if not isinstance(maturity, Mapping) or any(k not in maturity for k in REQUIRED_MATURITY_KEYS):
        got = sorted(dict(maturity or {}))
        raise SchedulingPolicyError(f"maturity 节残缺（需 M1-M4 五键），得:{got}")
    return dict(raw)


@dataclass(frozen=True)
class SchedulingGateVerdict:
    """单区域门闸判决（passed + 未过阈值码清单 + 逐项细节）。"""

    domain_id: str
    passed: bool
    failed_codes: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


def evaluate_region(
    stats: Mapping[str, Any],
    policy: Mapping[str, Any],
    now: datetime,
    domain_id: str = "",
) -> SchedulingGateVerdict:
    """纯函数：M1-M4 四阈值判定（now 可注入，判据可全枚举）。

    :param stats: 区域统计 {win, loss, draw, latest_archived_at: datetime|None, whitelisted: bool}
    :param policy: load_gate_policy 产物（maturity 节消费）
    :param now: 当前时刻（tz-aware；新鲜度计时基准）
    """
    missing = [k for k in ("win", "loss", "latest_archived_at", "whitelisted") if k not in stats]
    if missing:
        raise ValueError(f"region_stats_missing_keys:{','.join(missing)}")
    m = policy["maturity"]
    failed: list[str] = []
    details: dict[str, Any] = {}

    win = int(stats["win"])
    loss = int(stats["loss"])
    latest = stats["latest_archived_at"]
    fresh = True
    if latest is None:
        fresh = False
    else:
        if latest.tzinfo is None:
            raise ValueError("naive datetime 拒收（RULE-SCHEMA-TZ）")
        fresh = (now - latest) <= timedelta(days=int(m["m3_freshness_max_days"]))
    if not fresh:
        # M3 超龄→计数清零重攒（陈旧胜利不开门）；latest 缺席同判（无归档证据=陈旧）
        win = 0
        loss = 0
        failed.append("M3")
        details["freshness"] = "stale_or_missing_counts_reset"
    else:
        details["freshness"] = "fresh"

    if win < int(m["m1_min_wins"]):
        failed.append("M1")
    details["win"] = win

    total = win + loss  # draw 不计分母（DESIGN M2 口径）
    details["samples"] = total
    if total < int(m["m2_min_samples"]):
        failed.append("M2")
    else:
        rate = win / total
        details["win_rate"] = round(rate, 4)
        if rate < float(m["m2_min_win_rate"]):
            failed.append("M2")

    if not bool(stats["whitelisted"]):
        failed.append("M4")
    details["whitelisted"] = bool(stats["whitelisted"])

    # 去重保序（M2 可能双触发：样本不足与胜率不足）
    deduped: list[str] = []
    for code in failed:
        if code not in deduped:
            deduped.append(code)
    return SchedulingGateVerdict(domain_id=domain_id, passed=not deduped, failed_codes=deduped, details=details)


def region_aggregation_sql(schema: str) -> str:
    """纯函数：按域聚合 SQL（真源表=ai_compare.ai_comparison_experiment；只读 SELECT）。

    真源表无 archived_at 列——M3 新鲜度以 status='archived' 行的 updated_at 为归档时刻代理
    （DESIGN M3 口径的落表锚定，注释在案）。
    """
    return (
        f"SELECT domain_id, "
        f"count(*) FILTER (WHERE verdict IN ('win','win_starred')) AS win, "
        f"count(*) FILTER (WHERE verdict = 'loss') AS loss, "
        f"count(*) FILTER (WHERE verdict = 'draw') AS draw, "
        f"max(updated_at) AS latest_archived_at "
        f"FROM {schema}.ai_comparison_experiment "
        f"WHERE status = 'archived' AND domain_id IS NOT NULL "
        f"GROUP BY domain_id"
    )


def collect_region_stats(conn: Any, schema: str, whitelist: Mapping[str, bool] | None = None) -> dict[str, dict[str, Any]]:
    """执行域聚合（conn 注入，只读）→ {domain_id: evaluate_region 入参 stats}。

    :param whitelist: 区域→是否在白名单映射；缺席区域一律 False（M4 冷启动诚实语义）
    """
    wl = dict(whitelist or {})
    out: dict[str, dict[str, Any]] = {}
    cur = conn.cursor()
    cur.execute(region_aggregation_sql(schema))
    for row in cur.fetchall():
        domain_id = str(row[0])
        latest = row[4]
        if latest is not None and getattr(latest, "tzinfo", None) is None:
            raise ValueError(f"naive datetime 拒收（RULE-SCHEMA-TZ）：{domain_id} latest_archived_at")
        out[domain_id] = {
            "win": int(row[1]),
            "loss": int(row[2]),
            "draw": int(row[3]),
            "latest_archived_at": latest,
            "whitelisted": bool(wl.get(domain_id, False)),
        }
    return out


def promote_held_orders(
    orders: list[dict[str, Any]],
    verdicts: Mapping[str, SchedulingGateVerdict],
    promoted_at: str,
) -> list[dict[str, Any]]:
    """纯函数：held_maturity 工单批量重评——过线自动转 pending 并留痕（不过=原地挂起）。

    :param orders: 工单字典列表（含 order_id/domain_id/state/audit_log）
    :param verdicts: domain_id → SchedulingGateVerdict（调用方按域评好；缺域判据=原地挂起不误转）
    :param promoted_at: 转正时刻 ISO 串（now_utc 由调用方注入，本函数零取时）
    """
    out: list[dict[str, Any]] = []
    for order in orders:
        if order.get("state") != "held_maturity":
            out.append(dict(order))
            continue
        verdict = verdicts.get(str(order.get("domain_id") or ""))
        if verdict is None or not verdict.passed:
            out.append(dict(order))
            continue
        promoted = dict(order)
        promoted["state"] = "pending"
        promoted["held_reason"] = None
        audit = list(promoted.get("audit_log") or [])
        audit.append(
            {
                "ts": promoted_at,
                "action": "held_maturity_promoted",
                "detail": "M1-M4 过线（区域新 experiment archived 事件重评）",
            }
        )
        promoted["audit_log"] = audit
        out.append(promoted)
    return out
