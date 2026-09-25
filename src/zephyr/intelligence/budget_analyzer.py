# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §budget_analyzer
# [MODULE] zephyr.intelligence.budget_analyzer
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.utils.time_utils (now_utc)；zephyr.infrastructure.cost_tracker（usage_records，函数内延迟 import——records 注入时零 DB 依赖）；zephyr.data.alerter（函数内延迟 import——缺位降级仅日志）
# [CONSUMERS] /api/budget-advisories（只读路由，接线点=src/zephyr/frontend/dashboard/api_server.py 新增 @app.get，供接线批挂载）；web/pages/budget.html + features/budget/budget.js（前端建议卡）；CLI `python -m zephyr.intelligence.budget_analyzer --report|--demo`
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 账户资金动作（充值/订阅类）永不代行（宪法 §5 high 门位=Owner 四类事）——本模块只产"建议+直达链接文本"，链接仅展示不承载动作端点；
#              阈值默认值镜像 config/budget_policy.yaml degradation.thresholds 现值（规则=YAML 真源不在此，D-M5-01 自裁）；
#              burn-rate 两窗 7d/30d（B14 裁定：1d 短窗噪声过高，三窗为预算升级解锁项不施工）；
#              订阅线（GLM Coding Plan）不折美元，subscription_quota_used 单列（人工台账注入，缺省 None）；
#              余额经参数注入，密钥不落本模块；禁 datetime.now()/time.time()（统一 now_utc）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §6（M5 设计：数据源/日消耗口径/建议算法/告警阈值/推送接口）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] usage_records 不可达→BudgetAnalyzerError（CLI --report fail-closed 退出码 2，绝不编造报告）；
#                  daily_limit<=0 或 window_days∉{7,30}→ValueError；alerter 缺位→ImportError 降级仅日志不炸；
#                  判据函数（predicted_30d/burn_rate/budget_verdict/recharge_advice/free_window_savings）全纯函数零 IO，可全枚举单测
# [TESTS] tests/intelligence/test_budget_analyzer.py
# [TTL] permanent
"""budget_analyzer — AI 层 M5 预算分析器（OBJ_M 模型线 C7，DESIGN §6）。

判据/IO 分层：全部判据函数是**纯函数**（输入日消耗序列/路由/牌价，输出数值与告警，零 DB 零外呼）；
``load_daily_usage`` 只负责取数（cost_tracker usage_records 按 date 聚合，或 records 注入）；
``analyze`` 组装日报告；``render_budget_advisory_payload`` 把报告投影成 API 只读载荷
（直达链接仅文本字段，无任何按钮类字段）；``emit_alerts`` 把 ERROR 及以上告警推送 Alerter
（先例=zephyr.data.alerter，缺位降级日志）；``main`` 是 CLI（--report 真数据 / --demo 假数据）。
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import timedelta
from typing import Any, Final

from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "BudgetAnalyzerError",
    "DEFAULT_DAILY_LIMIT",
    "DEFAULT_THRESHOLDS",
    "analyze",
    "budget_verdict",
    "burn_rate",
    "emit_alerts",
    "free_window_savings",
    "load_daily_usage",
    "main",
    "predicted_30d",
    "recharge_advice",
    "render_budget_advisory_payload",
]

# ── 常量（阈值镜像 budget_policy.yaml degradation.thresholds 现值，D-M5-01；真源=YAML） ──
DEFAULT_DAILY_LIMIT: Final[float] = 10.0  # budget_policy.cost_limits.daily_cost_usd
DEFAULT_THRESHOLDS: Final[dict[str, float]] = {
    "notify": 0.50,
    "warning": 0.70,
    "model_switch": 0.80,
    "halt": 1.00,
}
SHORT_WINDOW: Final[int] = 7   # B14 裁定两窗：7d
LONG_WINDOW: Final[int] = 30   # B14 裁定两窗：30d（三窗为解锁项，不施工）
RECHARGE_SAFETY_FACTOR: Final[float] = 1.2      # 建议补充额=缺口×1.2 安全系数（DESIGN §6.3）
RECHARGE_HORIZON_DAYS: Final[int] = 7           # 缺口口径=近 7 天消耗
ALERT_DISPATCH_LEVEL: Final[int] = 3            # ERROR 及以上=model_switch(3)/halt(4) 才推 Alerter
_TASK_ID: Final[str] = "budget_analyzer"
_PORTAL_LINK_TEXT: Final[str] = "https://platform.deepseek.com/usage"
_PORTAL_LINK_LABEL: Final[str] = "DeepSeek 余额与用量页（URL 纯文本展示，账户动作由 Owner 人工执行）"

# 四档告警：tier→(level 递增, 动作文案)——DESIGN §6.4 表的代码投影，顺序即输出顺序
_ALERT_TIERS: Final[tuple[tuple[str, int, str], ...]] = (
    ("notify", 1, "INFO 通知+建议"),
    ("warning", 2, "WARN+建议暂停非关键消耗"),
    ("model_switch", 3, "ERROR+自动降档建议（路由器按 M4 降档）"),
    ("halt", 4, "CRITICAL+建议暂停非关键 API"),
)


class BudgetAnalyzerError(RuntimeError):
    """usage_records 不可达等取数失败（fail-closed，绝不编造报告）。"""


# ── 取数（唯一 IO 入口；records 注入时零 DB 依赖，可单测） ──
def load_daily_usage(days: int, *, records: list[dict] | None = None) -> list[dict]:
    """读近 ``days`` 天日消耗序列，逐条 {date, usd, tokens_in, tokens_out}，date 升序。

    ``records`` 注入时直接规范化使用（测试/离线注入通道，零 DB 依赖）；为 None 时读
    cost_tracker 的 usage_records 按 date 聚合（import 放函数内，防测试依赖生产库）。
    不可达→BudgetAnalyzerError（fail-closed）。
    """
    if days <= 0:
        raise ValueError(f"days must be > 0, got {days}")
    if records is not None:
        return _normalize_daily(records)
    try:
        # 函数内 import：注入通道下本模块与 cost_tracker/sqlite 工厂零耦合
        from zephyr.shared.io.paths import DB_PATH
        from zephyr.shared.io.sqlite_factory import get_db_connection

        conn = get_db_connection(str(DB_PATH), timeout=10)
        try:
            rows = conn.execute(
                "SELECT date, SUM(CAST(estimated_cost AS REAL)) AS usd,"
                " SUM(COALESCE(tokens_in, 0)) AS tokens_in,"
                " SUM(COALESCE(tokens_out, 0)) AS tokens_out"
                " FROM usage_records GROUP BY date ORDER BY date DESC LIMIT ?",
                (int(days),),
            ).fetchall()
        finally:
            conn.close()
        daily = [dict(r) for r in rows]
    except Exception as exc:  # noqa: BLE001 — sqlite 缺表/锁/路径不可达一律 fail-closed
        raise BudgetAnalyzerError(f"usage_records unreachable: {exc}") from exc
    return _normalize_daily(daily)


def _normalize_daily(records: list[dict]) -> list[dict]:
    """规范化日消耗条目并按 date 升序（窗口切片统一取尾部=最近 N 天）。"""
    out: list[dict[str, Any]] = []
    for r in records:
        if not r.get("date"):
            raise ValueError(f"daily record missing date: {r!r}")
        out.append(
            {
                "date": str(r["date"]),
                "usd": float(r.get("usd", 0.0) or 0.0),
                "tokens_in": int(r.get("tokens_in", 0) or 0),
                "tokens_out": int(r.get("tokens_out", 0) or 0),
            }
        )
    out.sort(key=lambda x: x["date"])
    return out


# ── 判据（纯函数，零 IO，可全枚举单测） ──
def _window_mean(daily: list[dict], window_days: int) -> float:
    """最近 ``window_days`` 天均值；数据不足窗口时用现有天数（DESIGN §6.3 降级口径）。"""
    tail = daily[-window_days:]
    if not tail:
        return 0.0
    return sum(float(r.get("usd", 0.0)) for r in tail) / len(tail)


def predicted_30d(daily: list[dict]) -> float:
    """30 天消耗外推 = 0.5×mean(最近7天) + 0.5×mean(最近30天)（B14 两窗裁定，平滑防单日尖峰）。

    数据不足 7 天时两窗都用现有天数均值（自然降级，不外插补零；analyze 报告附 predicted_note 注明）。
    """
    if not daily:
        return 0.0
    return round(0.5 * _window_mean(daily, SHORT_WINDOW) + 0.5 * _window_mean(daily, LONG_WINDOW), 6)


def burn_rate(daily: list[dict], window_days: int) -> float:
    """窗口日均消耗（USD/天）：最近 ``window_days`` 天均值；窗口只允许 7|30（B14 两窗）。"""
    if window_days not in (SHORT_WINDOW, LONG_WINDOW):
        raise ValueError(f"window_days must be {SHORT_WINDOW}|{LONG_WINDOW} (B14 two-window ruling), got {window_days}")
    return round(_window_mean(daily, window_days), 6)


def budget_verdict(predicted: float, daily_limit: float, thresholds: dict[str, float]) -> list[dict[str, Any]]:
    """四档告警判定（占日预算比例：notify≥50%/warning≥70%/model_switch≥80%/halt≥100%）。

    纯函数全枚举：多档命中全返回、level 递增（1→4）；恰好等于阈值=触发（≥语义）。
    thresholds 键=档名、值=占比小数（缺档回退 DEFAULT_THRESHOLDS 同名值）。
    """
    if daily_limit <= 0:
        raise ValueError(f"daily_limit must be > 0, got {daily_limit}")
    ratio = predicted / daily_limit
    verdicts: list[dict[str, Any]] = []
    for tier, level, action in _ALERT_TIERS:
        th = float(thresholds.get(tier, DEFAULT_THRESHOLDS[tier]))
        if ratio >= th:
            verdicts.append(
                {"tier": tier, "level": level, "ratio": round(ratio, 4), "threshold": th, "action": action}
            )
    return verdicts


def recharge_advice(balance_usd: float, daily_burn_7d: float) -> dict[str, Any]:
    """补足建议（DESIGN §6.3）：预计耗尽日 T=balance/日均消耗；建议额=缺口×1.2（缺口=7天消耗−balance，为正才建议）。

    balance<=0→立即建议（T=0）；burn<=0 且 balance>0→无消耗不建议（T=None）。
    返回含 action_text 与 link_text——链接是**纯文本 URL**，账户动作由 Owner 人工执行。
    """
    balance = float(balance_usd)
    burn = float(daily_burn_7d)
    gap = round(burn * RECHARGE_HORIZON_DAYS - balance, 6)
    suggested = round(max(gap, 0.0) * RECHARGE_SAFETY_FACTOR, 6)
    if balance <= 0:
        days_left: float | None = 0.0
        advise = True
        action = f"余额已耗尽，建议立即人工补充 {suggested} USD（7 天消耗缺口 {gap}×{RECHARGE_SAFETY_FACTOR} 安全系数）"
    elif burn <= 0:
        days_left = None
        advise = False
        action = "近 7 天无消耗，暂无需补充"
    else:
        days_left = round(balance / burn, 2)
        advise = gap > 0
        action = (
            f"余额预计 {days_left} 天耗尽，建议人工补充 {suggested} USD"
            f"（7 天消耗缺口 {gap}×{RECHARGE_SAFETY_FACTOR} 安全系数）"
            if advise
            else f"余额充足（约可支撑 {days_left} 天），暂无需补充"
        )
    return {
        "advise": advise,
        "balance_usd": round(balance, 6),
        "daily_burn_7d": round(burn, 6),
        "days_to_depletion": days_left,
        "gap_usd": gap,
        "suggested_topup_usd": suggested,
        "action_text": action,
        "link_text": _PORTAL_LINK_TEXT,
    }


def free_window_savings(routes: list[dict] | None, pricing: dict[str, float] | None) -> float:
    """免费窗节省估算（DESIGN §6.3 第 3 条，纯函数）：Σ 可迁移 token 量 × economy 牌价。

    routes 条目={model, migratable_tokens}（M4 路由表里可迁往谷时/免费窗的 token 量）；
    pricing={model: economy 档牌价 USD/1k tokens}。缺条目/零牌价/未知模型一律计 0（零差价→0.0）。
    """
    if not routes or not pricing:
        return 0.0
    total = 0.0
    for r in routes:
        model = str(r.get("model", ""))
        tokens = float(r.get("migratable_tokens", 0) or 0)
        total += tokens / 1000.0 * float(pricing.get(model, 0.0))
    return round(total, 6)


# ── 组装与投影 ──
def analyze(
    daily: list[dict],
    *,
    daily_limit: float = DEFAULT_DAILY_LIMIT,
    thresholds: dict[str, float] | None = None,
    balance_usd: float | None = None,
    routes: list[dict] | None = None,
    pricing: dict[str, float] | None = None,
    subscription_quota_used: float | None = None,
) -> dict[str, Any]:
    """组装日报告：{date, daily_usd, predicted_30d, burn_7d, burn_30d, alerts, recharge, free_savings, ...}。

    subscription_quota_used=订阅线（GLM Coding Plan）配额占用，人工台账注入、缺省 None（不折美元）；
    样本不足 7 天时附 predicted_note 注明降级口径。
    """
    ths = DEFAULT_THRESHOLDS if thresholds is None else thresholds
    predicted = predicted_30d(daily)
    b7 = burn_rate(daily, SHORT_WINDOW)
    b30 = burn_rate(daily, LONG_WINDOW)
    alerts = budget_verdict(predicted, daily_limit, ths)
    if balance_usd is None:
        recharge: dict[str, Any] = {"advise": False, "reason": "balance_unavailable", "suggested_topup_usd": 0.0}
    else:
        recharge = recharge_advice(balance_usd, b7)
    note = (
        f"样本仅 {len(daily)} 天（不足 7 天窗口），两窗均按现有天数均值降级计算" if 0 < len(daily) < SHORT_WINDOW else None
    )
    return {
        "date": daily[-1]["date"] if daily else now_utc().strftime("%Y-%m-%d"),
        "daily_usd": float(daily[-1]["usd"]) if daily else 0.0,
        "daily_limit_usd": daily_limit,
        "predicted_30d": predicted,
        "burn_7d": b7,
        "burn_30d": b30,
        "sample_days": len(daily),
        "predicted_note": note,
        "alerts": alerts,
        "recharge": recharge,
        "free_savings": free_window_savings(routes, pricing),
        "subscription_quota_used": subscription_quota_used,
        "generated_at": now_utc().isoformat(timespec="seconds"),
    }


def render_budget_advisory_payload(report: dict[str, Any]) -> dict[str, Any]:
    """报告→API 只读载荷（/api/budget-advisories 投影，JSON 安全结构）。

    红线投影：无任何按钮/表单类字段；直达链接只有 kind="text" 的 url_text 展示字段（无 href/action）；
    topup 建议只带 action_text 文案与 link_text 文本，不带可执行端点。前端拿到即渲染，零提交控件。
    """
    recharge = report.get("recharge") or {}
    payload: dict[str, Any] = {
        "ok": True,
        "source": _TASK_ID,
        "schema_version": "1",
        "readonly": True,
        "disclaimer": "数据只读·支付动作永不代行——本接口只产建议与链接文本，账户动作由 Owner 人工执行",
        "date": report.get("date"),
        "daily_usd": report.get("daily_usd"),
        "daily_limit_usd": report.get("daily_limit_usd"),
        "predicted_30d_usd": report.get("predicted_30d"),
        "burn_7d_usd": report.get("burn_7d"),
        "burn_30d_usd": report.get("burn_30d"),
        "sample_days": report.get("sample_days"),
        "predicted_note": report.get("predicted_note"),
        "alerts": [
            {
                "tier": a.get("tier"),
                "level": a.get("level"),
                "ratio": a.get("ratio"),
                "threshold": a.get("threshold"),
                "action_text": a.get("action"),
            }
            for a in report.get("alerts", [])
        ],
        "topup_advice": {
            "advise": bool(recharge.get("advise", False)),
            "days_to_depletion": recharge.get("days_to_depletion"),
            "suggested_topup_usd": recharge.get("suggested_topup_usd", 0.0),
            "action_text": recharge.get("action_text", ""),
            "link_text": recharge.get("link_text", _PORTAL_LINK_TEXT),
        },
        "free_savings_usd": report.get("free_savings"),
        "subscription_quota_used": report.get("subscription_quota_used"),
        "generated_at": report.get("generated_at"),
        "links": [{"kind": "text", "label": _PORTAL_LINK_LABEL, "url_text": _PORTAL_LINK_TEXT}],
    }
    return json.loads(json.dumps(payload, ensure_ascii=False))  # JSON 安全往返（去 datetime 等不可序列化对象）


# ── 告警推送（DESIGN §6.5：ERROR 及以上走 Alerter，缺位降级日志） ──
def _alert_summary(report: dict[str, Any], alert: dict[str, Any]) -> str:
    return (
        f"budget alert tier={alert.get('tier')} ratio={alert.get('ratio')} "
        f"date={report.get('date')} predicted_30d={report.get('predicted_30d')} "
        f"daily_limit={report.get('daily_limit_usd')}"
    )


def emit_alerts(report: dict[str, Any]) -> int:
    """推送 ERROR 及以上告警（model_switch=ERROR / halt=CRITICAL）到 ``Alerter.notify``。

    import 放函数内+ImportError 降级：alerter 缺位时只记日志、不抛异常，返回已处理告警数
    （处理=推送成功或降级记日志；单条 notify 异常不阻断其余条目）。notify/warning 档只记日志不推送。
    """
    alerts = [a for a in report.get("alerts", []) if int(a.get("level", 0)) >= ALERT_DISPATCH_LEVEL]
    if not alerts:
        return 0
    try:
        from zephyr.data.alerter import Alerter  # 函数内 import：测试环境无 alerter 依赖也能跑
    except ImportError:
        log.warning("budget_analyzer: alerter 不可用，%s 条 ERROR+ 告警降级为仅日志", len(alerts))
        return len(alerts)
    alerter = Alerter()
    handled = 0
    for a in alerts:
        level = "CRITICAL" if a.get("tier") == "halt" else "ERROR"
        try:
            alerter.notify(
                task_id=_TASK_ID,
                error=_alert_summary(report, a),
                level=level,
                source=_TASK_ID,
                extra={"advisory": a, "date": report.get("date")},
            )
            handled += 1
        except Exception:  # noqa: BLE001 — 单条推送失败不阻断其余告警
            log.exception("budget_analyzer: 告警推送失败 tier=%s", a.get("tier"))
    return handled


# ── CLI ──
def _demo_daily(days: int = LONG_WINDOW) -> list[dict]:
    """内置假数据（--demo 专用，不读生产库）：近 30 天日均缓升序列。"""
    today = now_utc().date()
    return [
        {
            "date": (today - timedelta(days=days - 1 - i)).isoformat(),
            "usd": round(0.6 + 0.03 * i + (0.5 if (days - 1 - i) < SHORT_WINDOW else 0.0), 4),
            "tokens_in": 40_000 + 500 * i,
            "tokens_out": 12_000 + 200 * i,
        }
        for i in range(days)
    ]


def main(argv: list[str] | None = None) -> int:
    """CLI：``--report`` 读 usage_records 出日报告 JSON（不可达 fail-closed 退出码 2）；``--demo`` 内置假数据。"""
    parser = argparse.ArgumentParser(prog="python -m zephyr.intelligence.budget_analyzer", description="M5 预算分析器（日报告只读）")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true", help="读 cost_tracker usage_records 出日报告 JSON 到 stdout")
    group.add_argument("--demo", action="store_true", help="内置假数据出报告（不读生产库）")
    parser.add_argument("--days", type=int, default=LONG_WINDOW, help="回看天数（默认 30）")
    args = parser.parse_args(argv)
    if args.demo:
        print(json.dumps(analyze(_demo_daily(), balance_usd=5.0), ensure_ascii=False, indent=2))
        return 0
    try:
        daily = load_daily_usage(args.days)
    except Exception as exc:  # noqa: BLE001 — fail-closed：取数失败绝不编报告
        print(json.dumps({"ok": False, "error": f"usage_records unreachable: {exc}"}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(analyze(daily), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班(排班登记register_*.ps1在册)/人工点火, 非自动常驻任务
    raise SystemExit(main())
