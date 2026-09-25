# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [MODULE] scripts.ai_layer.gen_ai_layer_monthly_checkup
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.perceive.source_registry (SourceRegistry, kpi_summary 配额读数);
#                zephyr.ai_layer.perceive.search_orders (SearchOrderJournal, blocked/开单计数);
#                zephyr.infrastructure.database_service (get_depgraph_pg_connection, 可选 V3 读数);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] CLI python scripts/ai_layer/gen_ai_layer_monthly_checkup.py --period YYYY-MM [--out-dir DIR];
#             通知板呈现（OpsAlertFeed→GET /api/ops-notifications 先例——接线批，本班只落 docs 双轨）;
#             Owner（骨架级建议书一键确认接口的读者）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 月度体检=L1 内监慢周期（§2.6，迁移清单⑤）；任务宿主=施工项 8 声明的 FactoryLaneC 同构
#              登记——受 §2.4 T3 双前置约束期走降级路线（高模型维护班人工开会话执行），本 CLI 即人工点火入口;
#              建议书 schema v1 校验 fail-closed（骨架级缺 options=Owner 一键确认接口→拒落盘）;
#              血肉/骨架分流铁律：flesh（模块/参数）自动处理——可自动执行的只汇报、其余自动派工单进施工排产;
#              skeleton（段/轴/真源结构）→Owner 门（宪法 §5），AI 永远只提案（净删/结构变更零自动）;
#              考尺（定调 11）：每条 proposal 必答进化两问 better_than/labor_killed，缺一拒收;
#              数据诚实：PG 不可达/数据源未集中登记→显式 null+注记（不虚构精度）;
#              产出落 checkups/YYYY-MM.md+同名 .json（docs 双轨人读+机读），测试传 tmp_path 注入
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L1_perceive/DESIGN.md §2.6（建议书 schema）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] period 非 YYYY-MM→ValueError; proposal 缺两问/骨架缺 options→ValueError 拒落盘;
#                  commit 事件文件缺行/坏行→跳过计数留痕（fail-open）; PG 不可达→kpi 段置 None+注记（不炸）;
#                  veins 产物缺失→vein_coverage 置 None+注记（不炸——体检先于首次再生亦可用）
# [TESTS] tests/ai_layer/perceive/test_monthly_checkup.py（建议书 schema 校验/血肉骨架分流正确/
#         骨架缺 options 拒/两问缺一拒/commit 坏行跳过+窗口过滤/vein_coverage 读生成器产物/
#         markdown 渲染含 Owner 一键确认段/落盘 md+json 双件/PG 不可达 kpi=None 注记）
"""gen_ai_layer_monthly_checkup — AI 层骨架月度建议书生成器（施工项 8，DESIGN §2.6）。

设计真源：``docs/_working/ai_layer_vision/L1_perceive/DESIGN.md`` §2.6。
产出四段：kpi_summary（V3 入考率+配额+任务单受阻）/ vein_coverage（矿脉清单读数）/
detector_digest（五通道月度聚合）/ proposals[]（血肉/骨架分流+进化两问+骨架级 Owner 一键确认）。

用法::

    python scripts/ai_layer/gen_ai_layer_monthly_checkup.py --period 2026-09 --out-dir .runtime/tmp/checkups
    python scripts/ai_layer/gen_ai_layer_monthly_checkup.py --period 2026-09 --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.ai_layer.perceive.search_orders import SearchOrderJournal  # noqa: E402
from zephyr.ai_layer.perceive.source_registry import load_source_registry  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

log = logging.getLogger("ai_perceive.checkup")

SCHEMA_VERSION: Final = "1.0"
PROPOSAL_LEVELS: Final[frozenset[str]] = frozenset({"flesh", "skeleton"})
PERIOD_PATTERN: Final = r"^\d{4}-(0[1-9]|1[0-2])$"
PROPOSAL_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    "level",
    "title",
    "evidence_ref",
    "ask",
    "better_than",
    "labor_killed",
)
DIGEST_WINDOW_DAYS: Final = 30
EXIT_OK: Final = 0
EXIT_ERROR: Final = 2
DATA_NOTE_UNLOGGED: Final = "数据源未集中登记，v0 如实留空（不虚构）"
REPO_VEINS_PATH: Final = REPO_ROOT / "config" / "ai_search_veins.yaml"
REPO_COMMIT_EVENTS_PATH: Final = REPO_ROOT / ".runtime" / "audit" / "commit_block_events.jsonl"
DEFAULT_OUT_DIR: Final = REPO_ROOT / "docs" / "_working" / "ai_layer_vision" / "L1_perceive" / "checkups"


def validate_proposal(raw: dict[str, Any], index: int) -> None:
    """单条 proposal 校验：四字段全齐+进化两问+骨架级必须有 options（一键确认接口）。"""
    missing = [k for k in PROPOSAL_REQUIRED_FIELDS if not str(raw.get(k) or "").strip()]
    if missing:
        raise ValueError(f"proposals[{index}] 缺必填字段: {','.join(missing)}")
    level = str(raw["level"])
    if level not in PROPOSAL_LEVELS:
        raise ValueError(f"proposals[{index}] level 非法: {level}（白名单={sorted(PROPOSAL_LEVELS)}）")
    if level == "skeleton" and not (raw.get("options") or []):
        raise ValueError(
            f"proposals[{index}] 骨架级必须附现成 options（Owner 一键确认接口，§2.6）"
        )
    if "auto_executable" in raw and not isinstance(raw["auto_executable"], bool):
        raise ValueError(f"proposals[{index}] auto_executable 必须为 bool")


def route_proposals(proposals: list[dict[str, Any]]) -> dict[str, list[str]]:
    """血肉/骨架分流（§2.6）：flesh 可自动执行→只汇报；flesh 其余→自动派工单；skeleton→Owner 门。"""
    routing: dict[str, list[str]] = {"flesh_report": [], "flesh_dispatch": [], "skeleton_owner": []}
    for proposal in proposals:
        title = str(proposal["title"])
        level = str(proposal["level"])
        if level == "skeleton":
            routing["skeleton_owner"].append(title)
        elif proposal.get("auto_executable") is True:
            routing["flesh_report"].append(title)
        else:
            routing["flesh_dispatch"].append(title)
    return routing


def build_report(
    period: str,
    *,
    proposals: list[dict[str, Any]],
    kpi_summary: dict[str, Any] | None,
    vein_coverage: dict[str, Any] | None,
    detector_digest: dict[str, Any],
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """建议书组装 + schema 全量校验（fail-closed，坏建议书绝不落盘）。"""
    if not re.match(PERIOD_PATTERN, period):
        raise ValueError(f"period 非 YYYY-MM: {period!r}")
    for index, raw in enumerate(proposals):
        validate_proposal(raw, index)
    moment = generated_at or now_utc()
    report: dict[str, Any] = {
        "doc_type": "ai_layer_monthly_checkup",
        "schema_version": SCHEMA_VERSION,
        "period": period,
        "generated_at": moment.isoformat(),
        "kpi_summary": kpi_summary,
        "vein_coverage": vein_coverage,
        "detector_digest": detector_digest,
        "proposals": proposals,
    }
    report["routing"] = route_proposals(proposals)
    return report


def collect_vein_coverage(veins_path: Path | None) -> dict[str, Any] | None:
    """矿脉覆盖读数（读矿脉清单生成器产物）；产物缺失→None+注记（体检先于再生亦可用）。"""
    if veins_path is None or not veins_path.exists():
        return {"note": f"矿脉清单产物缺失（{veins_path}）——先跑 gen_search_veins.py；已挖/长尾/封矿未跟踪=v0 边界"}
    import yaml

    raw = yaml.safe_load(veins_path.read_text(encoding="utf-8"))
    veins = [v for v in (raw.get("veins") or []) if isinstance(v, dict)]
    archived = sum(1 for v in veins if v.get("status") == "archived")
    return {
        "total": len(veins),
        "active": len(veins) - archived,
        "archived": archived,
        "mined": None,
        "longtail": None,
        "note": "已挖/长尾/封矿数 v0 未跟踪（结构判据留 OBJ_R 立项），其余字段机读自 REG-AIVEIN-001",
    }


def collect_detector_digest(
    commit_events_path: Path | None,
    *,
    injected: dict[str, Any] | None = None,
    now: datetime | None = None,
    window_days: int = DIGEST_WINDOW_DAYS,
) -> dict[str, Any]:
    """五通道月度聚合：堵点本实读（窗口过滤+坏行跳过），其余四通道注入/如实留空。"""
    moment = now or now_utc()
    window_start = moment - timedelta(days=window_days)
    by_gate: dict[str, int] = {}
    skipped = 0
    if commit_events_path is not None and commit_events_path.exists():
        for line in commit_events_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                event = json.loads(stripped)
                occurred = datetime.fromisoformat(str(event["timestamp"]))
                if occurred.tzinfo is None:
                    occurred = occurred.replace(tzinfo=timezone.utc)
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                skipped += 1
                continue
            if occurred >= window_start and str(event.get("event")) == "commit_blocked":
                gate_id = str(event.get("gate_id") or "UNKNOWN")
                by_gate[gate_id] = by_gate.get(gate_id, 0) + 1
    merged: dict[str, Any] = dict(injected or {})
    for channel in ("e6_decay", "e9_attribution", "sim_deviation", "feedback_loop"):
        merged.setdefault(channel, None)
    return {
        "window_days": window_days,
        "commit_block_by_gate": by_gate,
        "commit_block_total": sum(by_gate.values()),
        "bad_lines_skipped": skipped,
        "channels": merged,
        "note": DATA_NOTE_UNLOGGED,
    }


def collect_order_stats(journal: SearchOrderJournal, *, now: datetime | None = None) -> dict[str, Any]:
    """任务单月度计数（blocked=受阻代理、open/collected 分布）——kpi_summary 的 L1 侧输入。"""
    by_status: dict[str, int] = {}
    for order in journal.list_orders():
        by_status[order.status] = by_status.get(order.status, 0) + 1
    return {"orders_by_status": by_status, "note": "429 逐源计数未登记，blocked 单数=受阻代理（如实）"}


def _json_safe_row(row: dict[str, Any]) -> dict[str, Any]:
    """DB 行 → JSON 可序列化（datetime→ISO 带时区；Decimal/bytes 等→str）。真实 V3 读数 2026-09-23 实证需要。"""
    safe: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            safe[key] = value.isoformat()
        elif value is None or isinstance(value, (str, int, float, bool)):
            safe[key] = value
        elif isinstance(value, (bytes, bytearray)):
            safe[key] = value.decode("utf-8", errors="replace")
        else:  # Decimal/date 等其余 DB 标量一律 str 兜底
            safe[key] = str(value)
    return safe


def collect_kpi_summary(
    schema: str = "ai_intake",
    *,
    journal: SearchOrderJournal | None = None,
    conn: Any | None = None,
    registry_path: Path | None = None,
) -> dict[str, Any]:
    """kpi_summary：V3 入考率（PG 可选，不可达=None+注记）+ 每源配额（真源）+ 任务单计数。"""
    from zephyr.ai_layer.perceive.search_orders import DEFAULT_STATE_DIR as ORDERS_DIR

    registry = load_source_registry(registry_path)
    quotas = {s.slug: s.daily_quota for s in registry.sources}
    weekly_rows: list[dict[str, Any]] | None = None
    kpi_note = "PG 不可达：V3 入考率缺席（如实留空）"
    if conn is None:
        try:
            from zephyr.infrastructure.database_service import get_depgraph_pg_connection

            conn = get_depgraph_pg_connection(read_only=True)
        except Exception:  # noqa: BLE001——体检 fail-open，PG 缺席不炸
            conn = None
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {schema}.ai_intake_kpi_weekly ORDER BY week_start DESC LIMIT 60")  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
                columns = [d[0] for d in cur.description]
                weekly_rows = [_json_safe_row(dict(zip(columns, row))) for row in cur.fetchall()]
            kpi_note = "V3 ai_intake_kpi_weekly 最近 60 行"
        except Exception as exc:  # noqa: BLE001——视图缺席/权限问题不炸体检
            kpi_note = f"V3 读取失败（{type(exc).__name__}），如实留空"
    stats = collect_order_stats(journal or SearchOrderJournal(ORDERS_DIR))
    return {
        "quota_by_source": quotas,
        "total_daily_cap": registry.total_daily_cap,
        "weekly_rows": weekly_rows,
        "orders": stats,
        "blocked_429_count": None,
        "note": kpi_note + "；429 受阻逐源计数未登记=v0 边界",
    }


def render_markdown(report: dict[str, Any]) -> str:
    """建议书 Markdown 渲染（人读轨；机读轨=同名 json）。"""
    lines: list[str] = [
        f"# AI 层骨架月度建议书 {report['period']}",
        "",
        f"> schema v{report['schema_version']}｜generated_at={report['generated_at']}｜"
        "真源=DESIGN.md §2.6｜血肉级自动/骨架级 Owner（宪法 §5）",
        "",
        "## kpi_summary",
        "",
        "```json",
        json.dumps(report["kpi_summary"], ensure_ascii=False, indent=1),
        "```",
        "",
        "## vein_coverage",
        "",
        "```json",
        json.dumps(report["vein_coverage"], ensure_ascii=False, indent=1),
        "```",
        "",
        "## detector_digest（五通道月度聚合）",
        "",
        "```json",
        json.dumps(report["detector_digest"], ensure_ascii=False, indent=1),
        "```",
        "",
        "## proposals（每条必答进化两问：比现状好在哪+消灭哪段人工）",
        "",
    ]
    for proposal in report["proposals"]:
        level_tag = "骨架级→Owner 门" if proposal["level"] == "skeleton" else "血肉级→自动"
        lines.append(f"### [{level_tag}] {proposal['title']}")
        lines.append(f"- ask: {proposal['ask']}")
        lines.append(f"- evidence_ref: {proposal['evidence_ref']}")
        lines.append(f"- 比现状好在哪: {proposal['better_than']}")
        lines.append(f"- 消灭哪段人工: {proposal['labor_killed']}")
        if proposal["level"] == "skeleton":
            lines.append("- Owner 一键确认选项:")
            for i, option in enumerate(proposal.get("options") or [], start=1):
                lines.append(f"  {i}. {option}")
        lines.append("")
    lines.append("## 分流汇总")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(report["routing"], ensure_ascii=False, indent=1))
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    """docs 双轨落盘：checkups/YYYY-MM.md（人读）+ 同名 .json（机读）。测试传 tmp_path。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{report['period']}"
    md_path = out_dir / f"{stem}.md"
    json_path = out_dir / f"{stem}.json"
    md_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return md_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI 层骨架月度建议书生成器（人工点火）")
    parser.add_argument("--period", required=True, help="体检期（YYYY-MM）")
    parser.add_argument("--out-dir", default=None, help="产出目录（默认 docs/_working/ai_layer_vision/L1_perceive/checkups）")
    parser.add_argument("--veins", default=None, help="矿脉清单路径（默认 config/ai_search_veins.yaml）")
    parser.add_argument("--commit-events", default=None, help="堵点本路径（默认 .runtime/audit/commit_block_events.jsonl）")
    parser.add_argument("--registry", default=None, help="源注册表路径（默认 config/ai_source_registry.yaml）")
    parser.add_argument("--proposal", action="append", default=[], help="proposal JSON 文件路径（可多次）")
    parser.add_argument("--dry-run", action="store_true", help="只打印路由不落盘")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        proposals: list[dict[str, Any]] = []
        for path in args.proposal:
            proposals.extend(json.loads(Path(path).read_text(encoding="utf-8")))
        veins_path = Path(args.veins) if args.veins else REPO_VEINS_PATH
        commit_path = (
            Path(args.commit_events) if args.commit_events else REPO_COMMIT_EVENTS_PATH
        )
        report = build_report(
            args.period,
            proposals=proposals,
            kpi_summary=collect_kpi_summary(registry_path=Path(args.registry) if args.registry else None),
            vein_coverage=collect_vein_coverage(veins_path),
            detector_digest=collect_detector_digest(commit_path),
        )
        if args.dry_run:
            print(json.dumps(report["routing"], ensure_ascii=False, indent=1))
            print("dry-run 零写入")
            return EXIT_OK
        out_dir = Path(args.out_dir) if args.out_dir else DEFAULT_OUT_DIR
        md_path, json_path = write_outputs(report, out_dir)
        print(f"建议书落盘: {md_path}")
        print(f"机读副本: {json_path}")
        print(json.dumps(report["routing"], ensure_ascii=False, indent=1))
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001——CLI 边界统一 fail-closed 退出码 2
        print(f"ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班/人工点火, 非自动常驻任务
    raise SystemExit(main())
