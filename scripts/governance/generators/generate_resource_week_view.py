# [BLUEPRINT] MOD-RESCHED-VIEW | docs/03_modules/_domain_frontend/resource_week_view/blueprint.md | §
# [MODULE] scripts.governance.generators.generate_resource_week_view
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] yaml; zephyr.gov_enforcement.commit_gates.resource_schedule_gate（窗档展开+冲突检查复用）;
#   zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts（冲突→告警板，--publish-alerts）
# [CONSUMERS] src/zephyr/frontend/dashboard/web/features/resourceweek/rw-engine.js（只读渲染）;
#   src/zephyr/frontend/dashboard/web/pages/resweek.html（页面宿主）;
#   tests/scripts/test_generate_resource_week_view.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 数据全部来自生成器——rw-data.js 机生禁手改（文件头 GENERATED 标记）;
#   视图只读（无任何写端点/写路径，前端零交互写回）;
#   周窗对齐周一为界；跨日窗档按日切分；常驻实体（est=0）不渲染时间块只入清单;
#   冲突标注=闸 run_all_checks 同源复用（block 红/warn 黄，零二次判定）;
#   输出路径可注入（测试隔离禁写生产 web 树）
# [MODIFY-GUARD] rw-data.js 数据结构变更须同步 rw-engine.js 渲染契约
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表缺失=FileNotFoundError 上抛；cron 坏实体跳时间块记 skipped
# [TESTS] tests/scripts/test_generate_resource_week_view.py
# [A_module] module_id=MOD-RESCHED-VIEW | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 资源画像注册表
#   fields: config/resource_profile_registry.yaml（路径可注入）
#   code: load_registry_entities（闸模块复用）
# - id: I2
#   name: 闸 findings
#   fields: run_all_checks 输出（冲突标注真源）
#   code: run_all_checks
# 层: 算法
# - id: A1
#   name_zh: ① 周窗展开
#   name_en: build_week_slots
#   intro: 本周一起 8 天地平线展开→裁剪到周窗→跨日切分→(dow,start_min,end_min)
#   desc: 复用闸 expand_windows（零二次 cron 实现）；常驻实体入 unscheduled 清单
#   inputs: I1
#   outputs: lanes[].slots
# - id: A2
#   name_zh: ② 冲突标注
#   name_en: build_conflicts
#   intro: findings → {reason_code,severity,task_ids,detail,at} 简洁结构
#   desc: block 红/warn 黄；同源闸语义零复制
#   inputs: I2
#   outputs: conflicts[]
# - id: A3
#   name_zh: ③ 机生落盘
#   name_en: main
#   intro: window.RW_VIEW_DATA={...} 写 rw-data.js（GENERATED 头+禁手改声明）
#   desc: 输出路径缺省=dashboard web 树；--output 注入（测试/E2E）
#   inputs: A1, A2
#   outputs: features/resourceweek/rw-data.js
# 层: 输出
# - id: O1
#   name_zh: 周历全景视图数据
#   name_en: week view data
#   intro: 只读前端页渲染全部实体的唯一数据源（库+时间真源指针的视图投影）
#   downstream: rw-engine.js
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> O1
"""generate_resource_week_view — 周历全景视图生成器（MOD-RESCHED-VIEW，B3 图）。

资源排班全景四件套之"图"（方案 §2.4）：注册表+时间真源指针 → 周历网格数据
（左=实体泳道，横=周一~周日 0-24h），冲突=闸 findings 同源标注，视图只读禁手改。
前端页照抄 TDM/工厂页交互范式（页面片段+引擎拆件+manifest/frontend_map 登记，
dashboard 体系内加页——按方案 §4.5-⑥ 免 alignment_checklist §3 登记）。

用法:
  python scripts/governance/generators/generate_resource_week_view.py
  python scripts/governance/generators/generate_resource_week_view.py --output <path> --publish-alerts
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from zephyr.shared.io.file_utils import safe_write_text, content_sha256  # noqa: E402

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT = (
    REPO_ROOT / "src" / "zephyr" / "frontend" / "dashboard" / "web" / "features" / "resourceweek" / "rw-data.js"
)
DEFAULT_REGISTRY = REPO_ROOT / "config" / "resource_profile_registry.yaml"

_WEEK_MINUTES = 24 * 60


def _week_start(now: datetime | None = None) -> datetime:
    """本周一 00:00（本地语义用 Asia/Shanghai 口径；入参须 tz-aware）。"""
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("Asia/Shanghai")
    n = (now or datetime.now(timezone.utc)).astimezone(tz)
    monday = n - timedelta(days=n.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def build_week_slots(entities: list[dict], week_start: datetime) -> tuple[list[dict], list[str]]:
    """实体→周窗槽位。返回 (lanes, skipped)。常驻（est<=0）/无窗实体入 unscheduled。"""
    from zoneinfo import ZoneInfo

    from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import expand_windows

    lanes: list[dict] = []
    skipped: list[str] = []
    # 全函数统一北京 wall time（max/min 混合 tz 实例比较会产生错日切片——2026-09-16 红蓝实证）
    tz = ZoneInfo("Asia/Shanghai")
    week_start = week_start.astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    for e in entities:
        tid = str(e.get("task_id") or "")
        if not tid or str(e.get("status")) in ("retired", "orphaned_source"):
            continue
        lane = {
            "task_id": tid,
            "resource_class": e.get("resource_class"),
            "pool": e.get("pool"),
            "exclusive_group": list(e.get("exclusive_group") or []),
            "trading_sensitive": bool(e.get("trading_sensitive")),
            "peak_mem_gb": e.get("peak_mem_gb"),
            "measured_peak_mem_gb": (e.get("measured") or {}).get("peak_mem_gb"),
            "measured_p90_duration_min": (e.get("measured") or {}).get("p90_duration_min"),
            "status": e.get("status"),
            "window_type": e.get("window_type"),
            "window_expr": e.get("window_expr"),
            "est_duration_min": e.get("est_duration_min"),
            "slots": [],
            "unscheduled": False,
        }
        try:
            wins = expand_windows(e.get("window_expr"), e.get("est_duration_min"), week_start, horizon_days=8)
            parse_failed = False
        except Exception as exc:  # noqa: BLE001 — cron 坏实体跳时间块
            skipped.append(f"{tid}: {exc}")
            wins = []
            parse_failed = True
        day_slots: dict[int, list[list[int]]] = {}
        for (s, t) in wins:
            # 跨日切分（含溢出周界的裁剪）
            cur = max(s, week_start)
            while cur < t and cur < week_end:
                dow = cur.weekday()
                day0 = cur.replace(hour=0, minute=0, second=0, microsecond=0)
                start_min = int((cur - day0).total_seconds() // 60)
                next_midnight = day0 + timedelta(days=1)
                seg_end = min(t, next_midnight, week_end)
                end_min = int((seg_end - day0).total_seconds() // 60)
                if end_min > start_min:
                    day_slots.setdefault(dow, []).append([start_min, min(end_min, 1440)])
                cur = seg_end
        lane["slots"] = [{"dow": d, "ranges": _merge_ranges(rs)} for d, rs in sorted(day_slots.items())]
        # unscheduled=无可渲染时间块（无窗/常驻/手动/坏 cron）：只入泳道清单段
        lane["unscheduled"] = not lane["slots"]
        lanes.append(lane)
    return lanes, skipped


def _merge_ranges(ranges: list[list[int]]) -> list[list[int]]:
    """同 lane 重叠/相邻区间合并（高频 cron 每分钟触发产生同窗段，合并为连续块）。"""
    if not ranges:
        return []
    rs = sorted(ranges)
    out = [list(rs[0])]
    for s, e in rs[1:]:
        if s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def build_conflicts(registry_path: Path, now: datetime) -> tuple[list[dict], int]:
    """闸 findings → 视图冲突标注（同源零复制）。返回 (conflicts, block_count)。"""
    from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import run_all_checks

    findings = run_all_checks(registry_path, now)
    out = [
        {
            "reason_code": f.reason_code,
            "severity": f.severity,
            "task_ids": list(f.task_ids),
            "detail": f.detail,
            "at": f.at,
        }
        for f in findings
    ]
    return out, sum(1 for c in out if c["severity"] == "block")


def build_view_data(registry_path: Path, now: datetime | None = None) -> dict:
    """组装视图数据（纯函数，测试可断言）。"""
    now = now or datetime.now(timezone.utc)
    week_start = _week_start(now)
    data = yaml.safe_load(Path(registry_path).read_text(encoding="utf-8")) or {}
    entities = list(data.get("entities") or [])
    lanes, skipped = build_week_slots(entities, week_start)
    conflicts, n_block = build_conflicts(registry_path, now)
    reg_bytes = Path(registry_path).read_bytes()
    # registry_sha256 口径=sha256(bytes 先把 CRLF 归一为 LF)[:12]——读侧是注册表生成器
    # C-10 新鲜度自检（registry_content_sha）；行尾归一是为了不让 git/编辑器的
    # CRLF↔LF 翻转被误判成视图过期。两侧一致性由
    # tests/infrastructure/test_resource_schedule_regen_check.py 锁死，改一处必须改两处
    fingerprint = hashlib.sha256(reg_bytes.replace(b"\r\n", b"\n")).hexdigest()[:12]
    days = [(week_start + timedelta(days=i)).strftime("%m-%d 周" + "一二三四五六日"[i]) for i in range(7)]
    return {
        "generated_at": now.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "generator": "scripts/governance/generators/generate_resource_week_view.py",
        "registry": str(Path(registry_path).relative_to(REPO_ROOT)) if Path(registry_path).is_relative_to(REPO_ROOT) else str(registry_path),
        "registry_sha256": fingerprint,
        "week_start": week_start.strftime("%Y-%m-%d"),
        "days": days,
        "total_entities": len(lanes),
        "scheduled": sum(1 for l in lanes if not l["unscheduled"]),
        "block_conflicts": n_block,
        "conflicts": conflicts,
        "lanes": lanes,
        "skipped": skipped,
        "groups": data.get("groups") or {},
    }


def render_js(view: dict) -> str:
    header = (
        "/* [GENERATED] 本文件由 generate_resource_week_view.py 产出——禁手改（静态清单生成器产出红线）。\n"
        " * 刷新=重跑生成器；渲染契约见 features/resourceweek/rw-engine.js。\n"
        " */\n"
    )
    return header + "window.RW_VIEW_DATA = " + json.dumps(view, ensure_ascii=False, indent=1) + ";\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="周历全景视图生成器（MOD-RESCHED-VIEW）")
    ap.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT))
    ap.add_argument("--registry", type=str, default=str(DEFAULT_REGISTRY))
    ap.add_argument("--publish-alerts", action="store_true", help="生成后把冲突 findings 发布到 ops 告警板（B4 接线）")
    args = ap.parse_args()
    reg = Path(args.registry)
    if not reg.exists():
        print(f"FAIL: 注册表不存在 {reg}")
        return 1
    now = datetime.now(timezone.utc)
    view = build_view_data(reg, now)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    text = render_js(view)
    expected = None
    if out.exists():
        expected = content_sha256(out.read_text(encoding="utf-8"))
    safe_write_text(out, text, expected_base_sha256=expected)
    summary = {
        "ok": True,
        "output": str(out),
        "total_entities": view["total_entities"],
        "scheduled": view["scheduled"],
        "block_conflicts": view["block_conflicts"],
        "skipped": len(view["skipped"]),
    }
    if args.publish_alerts:
        from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import run_all_checks
        from zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts import publish_findings

        findings = run_all_checks(reg, now)
        r = publish_findings(findings)
        summary["alerts_ops"] = len(r.get("ops", []))
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
