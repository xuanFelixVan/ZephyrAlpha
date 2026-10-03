# [BLUEPRINT] MOD-DATENG-003 | docs/03_modules/_domain_data_eng/quality_sla_breach_predictor/blueprint.md
# [MODULE] zephyr.data.quality.archive_sla_burnrate
# [DOMAIN] D_DATA
# noqa: m11-perm-manual-legitimate  M11豁免: 本件=库面函数+运维手动补跑 CLI（python -m），非常驻服务、
#   无自循环无 sleep-loop；argparse/__main__ 仅为运维手动巡检与留痕通道（同族 cleaning_anomaly_hosting
#   先例）；未来挂调度腿=事件触发族规接线，判据值届时迁承载册 YAML
# [DEPENDENCIES] zephyr.data.quality.sla_breach_predictor（预测核，唯一算法真源）; stdlib json/pathlib
# [CONSUMERS] 运维 CLI（python -m zephyr.data.quality.archive_sla_burnrate 手动巡检）;
#   库面调用方（返回 dict 摘要）——挂调度排班前须先立承载册 YAML（同 cleaning_anomaly_rules 族规）
# [STARTUP] manual
# [MATURITY] trial
# [INVARIANTS] manifest 缺失/空=not_run 不冒绿（诚实四态族规，禁把"没得测"当"测过干净"）;
#   损坏行跳过并计数不中断; 窗口归属判定确定性（UTC，archived_at 解析失败=损坏行）;
#   判据值（target/window_days/windows）=本件默认参数且调用方可注入覆盖，挂调度前须迁承载册;
#   SLA 口径=manifest 窗口内有已验证归档记录占比（不读 CH 不触库不触网，manifest=F08 链自产品）;
#   告警仅回调不阻断; 同输入必同输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入非法（windows<2/window_days<1/target∉(0,1)）->QualitySlaPredictorError;
#   manifest 缺失/全损坏=返回 not_run 摘要（不抛）
# [TESTS] tests/zephyr/data/quality/test_archive_sla_burnrate.py
# [TTL] permanent
"""F08 冷归档链 SLA burn-rate 消费面（T1-B1 融合接线，2026-09-30）。

背景（NB1-B1 裁定卡 + F127 案卷缺口"无 gate 保证归档计划被执行"）：
scripts/ch/archiver.py（F08 链）是冷储唯一现役真源，其 append-only
manifest（archive_manifest.jsonl）是归档行为的自产品账本。本件把该
账本变成 SLA 观测序列——按时间窗统计"窗口内有已验证归档记录"的达成
率，喂给 sla_breach_predictor 做 burn-rate 违约预测：归档节奏劣化时
提前告警，而不是等发现数据断冷才救。

边界声明：本件只读 manifest 文件（F08 链的自产品），不读 CH、不触
data/databases、不执行归档（执行=archiver.py 四命令，各归其位）；
判据值真源现阶段=本件默认参数（调用方注入覆盖），升级挂调度时按
族规迁承载册 YAML。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: manifest 路径（默认=F08 ARCHIVE_ROOT 镜像常量，测试做同源断言防漂移）
# - id: I2
#   name: 判据参数 target/window_days/windows（调用方可注入）
# 层: 处理
# - id: P1
#   name: load_manifest_records（JSONL 逐行解析，损坏行跳过计数；缺失=空表）
# - id: P2
#   name: build_weekly_attainment（近 windows 个 window_days 窗，窗口内有
#     verified 归档记录=1.0 否则=0.0，UTC 确定性归属）
# - id: P3
#   name: predictor.forecast（burn-rate 外推，CRITICAL/EXHAUSTED 回调告警）
# 层: 输出
# - id: O1
#   name: 摘要 dict（status=ran|not_run + level/burn_rate/breach_at/损坏行数）
# 边:
# I1 -> P1 -> P2 -> P3 -> O1
# I2 -> P2 -> P3
"""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.data.quality.sla_breach_predictor import (
    BreachForecast,
    QualitySlaBreachPredictor,
    QualitySlaPredictorError,
    SloPoint,
)

__all__: Final = [
    "DEFAULT_MANIFEST_PATH",
    "SLO_NAME",
    "build_weekly_attainment",
    "load_manifest_records",
    "run_archive_sla_burnrate",
]

# F08 链 manifest 镜像常量（真源=scripts/ch/archiver.py ARCHIVE_ROOT/MANIFEST_PATH；
# scripts/ 非 importable 包，故镜像并由测试 test_manifest_path_mirror 做同源断言防漂移）
DEFAULT_MANIFEST_PATH: Final = Path("F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl")
SLO_NAME: Final = "archive_manifest_freshness"


def load_manifest_records(manifest_path: Path) -> tuple[list[dict[str, Any]], int]:
    """读归档 manifest（JSONL），返回 (records, 损坏行数)。

    缺失文件=([], 0)（not_run 语义，不抛）；损坏行（非 JSON/非 dict）跳过计数。
    """
    if not manifest_path.exists():
        return [], 0
    records: list[dict[str, Any]] = []
    corrupt = 0
    with open(manifest_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                corrupt += 1
                continue
            if isinstance(obj, dict):
                records.append(obj)
            else:
                corrupt += 1
    return records, corrupt


def _parse_archived_at(value: object) -> datetime.datetime | None:
    """解析 archived_at（ISO 格式）；失败返回 None（按损坏观测处理）。

    manifest 记录为 JSON 反序列化产物，字段真类型未知——入参 object +
    isinstance 收窄（真类型化，禁裸 Any per ANY-ABUSE）。
    """
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.UTC)
    return parsed


def build_weekly_attainment(
    records: list[dict[str, Any]],
    *,
    now_utc: datetime.datetime,
    window_days: int = 7,
    windows: int = 8,
) -> list[SloPoint]:
    """manifest 记录 → 近 windows 个窗口的达成率观测点（确定性）。

    口径：窗口内有 ≥1 条 verified=True 且带可解析 archived_at 的记录=1.0，
    否则=0.0；窗口按 [now - k*window_days, now - (k-1)*window_days) 倒序
    对齐（k=windows..1），输出按时间升序（predictor 契约）。
    """
    if windows < 2:
        raise QualitySlaPredictorError("windows 须 >=2（预测至少 2 观测点）")
    if window_days < 1:
        raise QualitySlaPredictorError("window_days 须 >=1")
    verified_ts: list[datetime.datetime] = []
    for rec in records:
        if rec.get("verified") is not True:
            continue
        ts = _parse_archived_at(rec.get("archived_at"))
        if ts is not None:
            verified_ts.append(ts)
    span = datetime.timedelta(days=window_days)
    points: list[SloPoint] = []
    for k in range(windows, 0, -1):
        win_end = now_utc - (k - 1) * span
        win_start = win_end - span
        attained = any(win_start <= ts < win_end for ts in verified_ts)
        # 观测点时刻=窗口终点（窗口闭合时点已知窗口内全部事实，无未来函数）
        points.append(SloPoint(observed_at=win_end, attainment=1.0 if attained else 0.0))
    return points


def run_archive_sla_burnrate(
    manifest_path: Path | str | None = None,
    *,
    target: float = 0.9,
    window_days: int = 7,
    windows: int = 8,
    clock: Callable[[], datetime.datetime] | None = None,
    alert_sink: Callable[[BreachForecast], None] | None = None,
) -> dict[str, Any]:
    """归档新鲜度 SLA burn-rate 巡检（读 manifest → 预测 → 摘要 dict）。

    返回 dict 契约：
    - status="not_run"：manifest 缺失或 verified 观测不足 2 窗（不冒绿，禁谎报）
    - status="ran"：level/burn_rate/predicted_breach_at/detail 全量透出
    判据值 target/window_days/windows 为默认参数（调用方注入覆盖），
    挂调度前须迁承载册 YAML（同 cleaning_anomaly_rules 族规）。
    """
    path = Path(manifest_path) if manifest_path is not None else DEFAULT_MANIFEST_PATH
    now = clock() if clock is not None else datetime.datetime.now(datetime.UTC)
    records, corrupt = load_manifest_records(path)
    if not records:
        return {
            "status": "not_run",
            "reason": f"manifest 缺失或空: {path}",
            "manifest_path": str(path),
            "corrupt_lines": corrupt,
        }
    points = build_weekly_attainment(records, now_utc=now, window_days=window_days, windows=windows)
    predictor = QualitySlaBreachPredictor(clock=clock, alert_sink=alert_sink)
    predictor.register_slo(SLO_NAME, target)
    observed = sum(1 for p in points if p.attainment > 0.0)
    if observed < 2:
        return {
            "status": "not_run",
            "reason": f"verified 观测窗不足: {observed}/{windows}（预测至少 2）",
            "manifest_path": str(path),
            "corrupt_lines": corrupt,
            "observed_windows": observed,
            "total_windows": windows,
        }
    fc = predictor.forecast(SLO_NAME, points)
    return {
        "status": "ran",
        "slo_name": fc.slo_name,
        "target": fc.target,
        "level": fc.level.value,
        "burn_rate": fc.burn_rate,
        "predicted_breach_at": fc.predicted_breach_at.isoformat() if fc.predicted_breach_at else None,
        "detail": fc.detail,
        "manifest_path": str(path),
        "corrupt_lines": corrupt,
        "observed_windows": observed,
        "total_windows": windows,
    }


def main() -> int:
    """CLI：python -m zephyr.data.quality.archive_sla_burnrate [--manifest PATH]。"""
    parser = argparse.ArgumentParser(description="F08 归档链 SLA burn-rate 巡检（只读 manifest）")
    parser.add_argument("--manifest", default=None, help="archive_manifest.jsonl 路径（默认 F08 链）")
    parser.add_argument("--target", type=float, default=0.9, help="SLA 达成率目标（默认 0.9）")
    parser.add_argument("--window-days", type=int, default=7, help="观测窗口天宽（默认 7）")
    parser.add_argument("--windows", type=int, default=8, help="观测窗口数（默认 8）")
    args = parser.parse_args()
    summary = run_archive_sla_burnrate(
        args.manifest, target=args.target, window_days=args.window_days, windows=args.windows
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
