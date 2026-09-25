# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_freedom_weekly_report
# [MODULE] zephyr.ai_layer.redline.freedom_weekly_report
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] OBJ_S 前端面板段落（周报 YAML 消费）; Owner 一屏周审（md 双格式）;
#             L1 内监慢周期（周频点火=接线批）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 负面清单制的对价=透明（DESIGN §5）：AI 每周交"我用了哪些自由"报告，
#              Owner 只看一屏；生成=生成器产出（禁手工写）；schema 与 DESIGN §5 逐字段一致
#              （week_id/free_domain_usage/near_miss_events/negative_list_hits/
#              quota_consumption/sev_incidents/owner_calls/degradation_events/
#              next_week_proposals）；owner_calls 终局校验 KPI ≤4（主文档 §六）随报输出
#              （越线只标 kpi_breach 不拦——周报是透明面不是执法面）；审计 jsonl 输入
#              fail-open（坏行跳过计数）；next_week_proposals 上会前置=负面清单预检（流程字段，
#              本生成器不执行预检）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §5
# [STABILITY] new
# [SAFETY] L（只读聚合+报告落参数指定目录）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 审计 jsonl 缺文件 → 该源计 0（fail-open，周报诚实记 sources_missing）；
#                  坏行跳过计数；week_id 推导用 now_utc（禁 datetime.now）；
#                  写盘失败抛 OSError（调用方处置）
# [TESTS] tests/ai_layer/redline/test_freedom_weekly_report.py（样例周报含自由使用/擦边/
#         配额三节/week_id ISO 格式/hits 按 rule_id 聚合/owner_calls KPI 越线标记/
#         md+yaml 双格式落盘回读/坏行跳过）
# [TTL] permanent
"""freedom_weekly_report — 自由域透明度周报生成器（OBJ_S 施工项 S7，DESIGN §5）。

负面清单制的对价=透明。每周一份"我用了哪些自由"报告（生成器产出，禁手工写），
交付=前端面板段落+md 双格式，Owner 只看一屏：

- free_domain_usage：自由域实际使用（新增自动化能力无需审批故全部留痕）；
- near_miss_events：擦边（负面清单检查 warn 命中但未构成阻断，判据说明随条）；
- negative_list_hits：机检阻断计数（by rule_id 汇总）；
- quota_consumption：配额池实际 vs 配额（token/GPU 档/提交数/子代理槽）；
- sev_incidents：§3 四类开放事件；degradation_events：双指标降档触发次数；
- owner_calls：Owner 被叫次数（终局校验 KPI ≤4）；
- next_week_proposals：下周想新增的自由（自动过负面清单预检后才上会）。
"""

from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

DEFAULT_OUT_DIR: Final = REPO_ROOT / "docs" / "_working" / "ai_layer_vision" / "OBJ_S_perimeter" / "reports"
OWNER_CALLS_KPI: Final = 4
REPORT_KEY: Final = "freedom_weekly_report"


@dataclass(frozen=True)
class WeeklyInput:
    """周报输入载荷（各供给方聚合后注入；生成器不外呼不连库）。"""

    week_id: str
    free_domain_usage: tuple[dict[str, Any], ...] = ()
    near_miss_events: tuple[dict[str, Any], ...] = ()
    negative_list_hits: tuple[dict[str, Any], ...] = ()
    quota_consumption: tuple[dict[str, Any], ...] = ()
    sev_incidents: dict[str, int] = field(default_factory=dict)
    owner_calls: int = 0
    degradation_events: int = 0
    next_week_proposals: tuple[str, ...] = ()


def week_id_for(as_of: datetime | None = None) -> str:
    """ISO 周标识 YYYY-Wnn（周一为首日；缺省 now_utc）。"""
    moment = as_of or now_utc()
    iso_year, iso_week, _ = moment.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def collect_hits_by_rule(
    audit_paths: Sequence[Path],
    *,
    action: str = "block",
    count_key: str = "blocks",
) -> list[dict[str, Any]]:
    """从 gate 审计 jsonl 聚合 [{rule_id, <count_key>}]（fail-open：缺文件/坏行跳过留痕）。

    action="block" → negative_list_hits（count_key="blocks"）；
    action="near_miss_warn" → 擦边源（count_key="warns"，S8 年审探测口②同源）。
    """
    counts: dict[str, int] = {}
    missing: list[str] = []
    for path in audit_paths:
        if not path.exists():
            missing.append(path.as_posix())
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict) or record.get("action") != action:
                continue
            rule_id = str(record.get("rule_id", "unknown"))
            counts[rule_id] = counts.get(rule_id, 0) + 1
    if missing:
        logger.info("周报审计源缺席（fail-open 计 0）: %s", ", ".join(missing))
    return [{"rule_id": rule_id, count_key: count} for rule_id, count in sorted(counts.items())]


def build_report(weekly: WeeklyInput) -> dict[str, Any]:
    """组装 DESIGN §5 schema 全字段（纯函数；schema 漂移=改 DESIGN 走 OBJ_R）。"""
    return {
        "week_id": weekly.week_id,
        "free_domain_usage": [dict(item) for item in weekly.free_domain_usage],
        "near_miss_events": [dict(item) for item in weekly.near_miss_events],
        "negative_list_hits": [dict(item) for item in weekly.negative_list_hits],
        "quota_consumption": [dict(item) for item in weekly.quota_consumption],
        "sev_incidents": dict(weekly.sev_incidents),
        "owner_calls": weekly.owner_calls,
        "degradation_events": weekly.degradation_events,
        "next_week_proposals": list(weekly.next_week_proposals),
        "owner_calls_kpi": {
            "limit": OWNER_CALLS_KPI,
            "breach": weekly.owner_calls > OWNER_CALLS_KPI,
            "note": "终局校验 KPI ≤4（主文档 §六）；越线只标记不拦——周报是透明面不是执法面",
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    """一屏 md（自由域使用/擦边/负面清单命中/配额/SEV/降档/下周提案 七段）。"""
    lines: list[str] = [
        f"# 自由域透明度周报 {report['week_id']}",
        "",
        f"- Owner 被叫：{report['owner_calls']} 次（KPI ≤{report['owner_calls_kpi']['limit']}"
        + ("，**越线**）" if report["owner_calls_kpi"]["breach"] else "）"),
        f"- SEV 开放事件：{report['sev_incidents']}",
        f"- 双指标降档触发：{report['degradation_events']} 次",
        "",
        "## 自由域使用",
        "",
    ]
    if report["free_domain_usage"]:
        for item in report["free_domain_usage"]:
            lines.append(
                f"- {item.get('capability', '?')}（domain={item.get('domain', '?')}, "
                f"first_used={item.get('first_used', '?')}, runs={item.get('runs', 0)}）"
            )
    else:
        lines.append("- （本周零新增自由域使用）")
    lines += ["", "## 擦边事件（warn 未阻断）", ""]
    if report["near_miss_events"]:
        for item in report["near_miss_events"]:
            lines.append(
                f"- [{item.get('rule_id', '?')}] {item.get('what', '?')}——"
                f"why_warn_not_block: {item.get('why_warn_not_block', '?')}（count={item.get('count', 0)}）"
            )
    else:
        lines.append("- （本周零擦边）")
    lines += ["", "## 负面清单机检阻断", ""]
    if report["negative_list_hits"]:
        for item in report["negative_list_hits"]:
            lines.append(f"- {item.get('rule_id', '?')}: {item.get('blocks', 0)} 次")
    else:
        lines.append("- （本周零阻断）")
    lines += ["", "## 配额消耗", ""]
    if report["quota_consumption"]:
        for item in report["quota_consumption"]:
            lines.append(
                f"- {item.get('resource', '?')}: {item.get('used', 0)}/{item.get('quota', 0)}"
                f"（{item.get('pct', 0):.0%}）"
            )
    else:
        lines.append("- （本周零配额消耗上报）")
    lines += ["", "## 下周新增自由提案", ""]
    if report["next_week_proposals"]:
        for proposal in report["next_week_proposals"]:
            lines.append(f"- {proposal}")
    else:
        lines.append("- （无）")
    lines.append("")
    return "\n".join(lines)


def write_report(report: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    """双格式落盘：`freedom_weekly_<week_id>.yaml` + `.md`（目录不存在创建）。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    yaml_path = out_dir / f"freedom_weekly_{report['week_id']}.yaml"
    md_path = out_dir / f"freedom_weekly_{report['week_id']}.md"
    yaml_path.write_text(yaml.safe_dump(report, sort_keys=False, allow_unicode=True), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return yaml_path, md_path


def main(argv: list[str] | None = None) -> int:  # noqa: ARG001 — CLI 预留（周报由供给方注入数据，暂无独立 CLI 面）
    raise SystemExit(
        "freedom_weekly_report 由供给方注入 WeeklyInput 后调 build_report/write_report；"
        "独立 CLI=接线批随 L1 慢周期一并交付"
    )


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班/人工点火, 非自动常驻任务
    main()
