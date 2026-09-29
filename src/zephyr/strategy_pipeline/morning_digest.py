# [BLUEPRINT] MOD-BT-232 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.morning_digest
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.promotion_advisory(ADVISORY_DIR/ROOT 常量与 ADV 包结构真源，只 import 不改);
#   zephyr.shared.io.file_utils(safe_write_text CAS 落盘); zephyr.shared.utils.time_utils(now_utc)
# [CONSUMERS] zephyr.strategy_pipeline.promotion_advisory（run_promotion_advisory_due 尾挂刷新，fire-and-forget）;
#   Owner 晨读面 data/reports/morning_digest.md（F74 堵点3 裁定：晨报承接，唯一人工门触达）
# [STARTUP] imported+event（随 promotion_advisory_due 执行体尾刷新，无独立触发方式，禁 cron）
# [MATURITY] experimental
# [INVARIANTS] 纯函数渲染与 I/O 分离（事件列表→文本，零隐藏读）；摘要只读建议包目录，
#   零写回 advisory 面；写文件走 safe_write_text（热文件铁律同款 CAS），路径可注入（测试 tmp_path）；
#   advisory 目录空/缺=静默跳过（combo gate 同款，处女链不白跑不告警）；
#   刷新任何失败不反噬建议产出与拍板执行（尾挂 fire-and-forget，双重 try/except 防御）；
#   前端横幅（/api/ops-notifications）与 data/failures 落盘现状零改动（本件是纯增量触达面）；
#   事件传动非 cron（宪法 §9.3）；不注册任何计划任务（schtasks=Owner 门位）
# [MODIFY-GUARD] tests/strategy_pipeline/test_morning_digest.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 顶层函数永不外抛：收集/渲染/落盘的读缺失与写失败一律折进返回 dict
#   {"ok": false, "reason": ...} 或 skipped/written 三态；仅非法目录类型等编程错误可抛
# [TESTS] tests/strategy_pipeline/test_morning_digest.py
# [A_module] module_id=MOD-BT-232 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""morning_digest — 转正建议晨报摘要渲染器（F74 堵点3"通知通道"落地面）。

裁定背景（Owner 2026-09）：唯一人工门无带外触达（飞书/SMTP 已裁撤，唯一出口=前端
#promotion 横幅+data/failures 落文件），Owner 不开屏=建议无限期滞留。三选一裁定取
**晨报承接**：不复活 SMTP/飞书、不加新推送组件，promotion advisory 落盘事件写入固定
晨报摘要面 data/reports/morning_digest.md——Owner 每天醒来必看处。

形态：函数式纯渲染（输入事件列表→输出文本）+ 薄落盘。advisory due 执行体尾部挂一次
digest 刷新（fire-and-forget，失败只 warning 不反噬主流程——复用 combo gate 传动同款
防御形态）；前端横幅与 data/failures 落盘现状零改动。

# [ALGO_FLOW] external: docs/03_modules/_domain_strategy_pipeline/algo_flow/morning_digest.yaml
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

#: 组合门一页报告目录（摘要尾指针，只指路不复制内容）
COMBO_REPORT_DIR = "docs/_working/pipeline-research/promotion-reports"
#: 已决墓碑后缀（advisory decide 落 decision 台账后包名追加）
_DECISION_TAIL = ".decision.json"
#: 结论→建议动作一句话（与 promotion_advisory 推送词表同口径）
_ACTION_TEXT: Final[dict[str, str]] = {
    "promote": "建议批准进整装（sim→production），前端 #promotion 页拍板",
    "demote": "建议降档 shelved，前端 #promotion 页拍板",
}


def _advisory_dir_default() -> Path:
    """惰性取 advisory 目录真源（避免模块加载期硬依赖 promotion_advisory 导入序）。"""
    from zephyr.strategy_pipeline.promotion_advisory import ADVISORY_DIR

    return ADVISORY_DIR


def _digest_path_default() -> Path:
    """摘要面默认落点=仓根 data/reports/morning_digest.md（惰性构造，ROOT 随仓走）。"""
    from zephyr.strategy_pipeline.promotion_advisory import ROOT

    return ROOT / "data/reports/morning_digest.md"


def collect_pending_advisories(advisory_dir: Path | None = None) -> list[dict[str, Any]]:
    """扫 advisory 目录收集**未决**建议包（渲染输入事件列表；已决=有 decision 台账者跳过）。

    只读扫描零判定；坏包跳过不抛（与 list_advisories 同款降级）；目录空/缺=空表由上层判跳过。
    """
    target = advisory_dir if advisory_dir is not None else _advisory_dir_default()
    if not target.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(target.glob("ADV-*.json")):
        if path.name.endswith(_DECISION_TAIL):
            continue
        try:
            adv = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            logger.warning("建议包解析失败（晨报跳过）: %s", path.name, exc_info=True)
            continue
        if (target / f"{path.stem}{_DECISION_TAIL}").exists():
            continue  # 已决建议不进待办区（台账即墓碑，拍板后晨报自然摘除）
        out.append(
            {
                "advisory_id": str(adv.get("advisory_id") or path.stem),
                "strategy_id": str(adv.get("strategy_id") or "?"),
                "lifecycle_now": str(adv.get("lifecycle_now") or "?"),
                "recommendation": str(adv.get("recommendation") or "?"),
                "generated_at": str(adv.get("generated_at") or ""),
                "report_ref": path.as_posix(),
            }
        )
    return out


def render_digest(
    events: list[dict[str, Any]],
    *,
    date_str: str | None = None,
    report_dir: str = COMBO_REPORT_DIR,
) -> str:
    """纯渲染：未决建议事件列表→晨报 markdown 文本（零 I/O，同输入同输出）。

    每条=策略/结论/建议动作/报告文件路径指针；空列表=无待办行（仍出报，Owner 见面即安心）。
    """
    day = date_str or now_utc().strftime("%Y-%m-%d")
    lines: list[str] = [f"# 晨报摘要 · {day}", "", "## 转正建议书待办区", ""]
    if not events:
        lines.append("（无待办——当前无未决转正建议包）")
    for ev in events:
        rec = ev.get("recommendation") or "?"
        action = _ACTION_TEXT.get(rec, "到前端 #promotion 页查看并拍板")
        lines.append(
            f"- **{ev.get('strategy_id')}**（{ev.get('lifecycle_now')}）结论 **{rec}** — {action} — "
            f"报告: `{ev.get('report_ref')}`"
        )
    lines += [
        "",
        f"完整报告见 {report_dir}/（最新 promotion-report-*.md）；拍板入口=前端 #promotion 页。",
        "",
    ]
    return "\n".join(lines)


def refresh_morning_digest(
    advisory_dir: Path | None = None,
    digest_path: Path | None = None,
    *,
    date_str: str | None = None,
) -> dict[str, Any]:
    """刷新晨报摘要：收集→渲染→safe_write_text 落盘（advisory due 尾挂入口）。

    目录空/缺=静默跳过（combo gate 同款）；收集/读包/落盘任何失败折进返回 dict 不外抛
    ——调用方（run_promotion_advisory_due）再包一层 try/except，双重防御保主流程零反噬。
    """
    try:
        target = advisory_dir if advisory_dir is not None else _advisory_dir_default()
        if not target.is_dir() or not any(target.glob("ADV-*.json")):
            return {"ok": True, "rc": 0, "skipped": "advisory_dir_empty_or_missing"}
        out_path = digest_path if digest_path is not None else _digest_path_default()
        events = collect_pending_advisories(target)
        text = render_digest(events, date_str=date_str)
        r = safe_write_text(out_path, text, newline="\n")
        if not getattr(r, "written", True):
            return {"ok": False, "rc": -1, "reason": "digest_write_unconfirmed"}
        logger.info("晨报摘要已刷新: %s（待办 %d 条）", out_path, len(events))
        return {"ok": True, "rc": 0, "written": str(out_path), "pending": len(events)}
    except Exception as exc:  # noqa: BLE001  刷新失败绝不反噬建议产出（F74 堵点3 防御形态）
        logger.warning("晨报摘要刷新失败（不反噬主流程）", exc_info=True)
        return {"ok": False, "rc": -1, "reason": f"{type(exc).__name__}: {exc}"}
