# [BLUEPRINT] MOD-RESCHED-CALIB | docs/03_modules/_cross_layer/measure_calibration/blueprint.md | §
# [MODULE] zephyr.infrastructure.system_telemetry.measure_calibration
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] yaml; zephyr.shared.io.file_utils;
#   zephyr.infrastructure.system_telemetry.resource_sampler（样本流/注册表读侧 + P90 与内存
#   margin 口径的唯一真源，本模块不重写第二份）;
#   .runtime/logs/resource_samples/<task_id>.jsonl(**只读**);
#   config/resource_profile_registry.yaml(**只读**——申报值与 measured.* 都不碰)
# [CONSUMERS] scripts/governance/generators/generate_resource_morning_report.py（校准 flag 摘要段）;
#   docs/_working/resource_schedule/calibration_report.yaml（本报告落盘）;
#   晨审/AI 会话（读报告决定申报值校正批）;
#   tests/infrastructure/system_telemetry/test_measure_calibration.py
# [STARTUP] manual（CLI one-shot；无自拉起——校准产出是人在环的"建议校正批"，不自动改申报值）
# [MATURITY] testing
# [INVARIANTS] **只读侧纪律**——本模块绝不写注册表：measured.* 写权归 resource_sampler.writeback，
#   两处写=同一实测两个口径（双写方事故）；proposed_corrections 是建议不是指令;
#   时长实测取 lifetime_deviation_report（从样本流重算 P90，不依赖 writeback 是否跑过）；内存实测
#   取 max×(1+margin%)（与 writeback 同口径——批测/挖矿是尖刺负载，P90 对尖刺失真）;
#   零样本实体 status="样本不足"、数值一律 null（禁编造）；申报缺值/常驻（est=0）判
#   not_comparable，不硬算比值；RSS 全零样本判 no_rss_evidence，不拿 0 当实测;
#   flag 判据=|实测-申报|/申报 > tolerance_pct（严格大于，默认 30%）：低估=实测>申报（班次会压到
#   下一班）、高估=实测<申报（白占预算）——与 sampler.lifetime_deviation_report 的 match 容差同边界;
#   路径全注入（构造参数 / CLI --root），报告只落 docs/_working/resource_schedule/（_working 契约
#   禁 .json，故 YAML）；输出带 GENERATED 头（静态清单生成器产出红线，禁手工增删条目）
# [MODIFY-GUARD] flag 阈值/口径变更须同步晨报"校准 flag 摘要"段与本模块测试断言
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表缺失=FileNotFoundError 上抛（fail-closed，不假装"无实体"）；样本流损坏行
#   经 sampler.read_samples 计数降级；报告写出 CAS 冲突=StaleWriteRefused 上抛（不静默覆盖）
# [TESTS] tests/infrastructure/system_telemetry/test_measure_calibration.py
# [A_module] module_id=MOD-RESCHED-CALIB | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""measure_calibration — p90 实测校准器（MOD-RESCHED-CALIB，资源排班 v2 / P5）。

病灶（v2 方案 §4-P5）：注册表申报值（est_duration_min / peak_mem_gb）是冲突闸与内存
天花板的输入——申报漂了，闸就是在对错误的账做判定。P3 第一轮重排班吃的仍是申报值，
"实测反校申报"这条线一直没人跑（sampler 的 lifetime_deviation_report 早在 L-1 就
明言"供 P5 p90 校准器复用"，本模块就是那个消费方）。

三段（全部只读，产出一份建议报告）：

1. ``MeasureCalibrator.calibrate`` — 逐实体两轴对账：
   - 时长轴：申报 ``est_duration_min`` vs 样本流 ``process_elapsed_seconds`` 的 P90
     （经 ``ResourceSampler.lifetime_deviation_report``，口径零复制）；
   - 内存轴：申报 ``peak_mem_gb`` vs 样本流 RSS max × (1+margin%)（与 writeback 同口径）。
2. ``_axis_row`` — 统一偏差判据：ratio=(实测-申报)/申报；|ratio|>tolerance% 才 flag，
   方向=低估/高估（申报被低估=班次会被压到下一班；申报被高估=白占并发预算）。
3. ``render_yaml`` + ``write_report`` — 报告落
   ``docs/_working/resource_schedule/calibration_report.yaml``（CAS safe_write_text），
   晨报经 ``read_calibration_report`` 读摘要段。

边界（不做的事）：
- **不写注册表**（measured.* 写权=sampler.writeback；申报值人填字段更不归本模块动）；
- 不做阈值判定/阻断（那是 MOD-RESCHED-GATE）；不采样（那是 sampler）；
- 不做 UI（晨报才是 UI）。

CLI:
  python -m zephyr.infrastructure.system_telemetry.measure_calibration
  python -m zephyr.infrastructure.system_telemetry.measure_calibration --root <tmp> --print
  python -m zephyr.infrastructure.system_telemetry.measure_calibration --tolerance 30 --tasks a,b
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Final

import yaml

from zephyr.infrastructure.system_telemetry.resource_sampler import (
    DEFAULT_DURATION_PERCENTILE,
    DEFAULT_MEM_MARGIN_PCT,
    ResourceSampler,
    registry_path as default_registry_path,
    samples_dir as default_samples_dir,
)
from zephyr.shared.io.file_utils import content_sha256, safe_write_text

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_DEVIATION_TOLERANCE_PCT",
    "FIELD_DURATION",
    "FIELD_MEMORY",
    "DEFAULT_REPORT_RELPATH",
    "MeasureCalibrator",
    "calibrate",
    "read_calibration_report",
    "report_path",
]

# P5 校准阈值（v2 方案 §4-P5 原话"偏差>30% 自动 flag"）。sampler 侧的 20% 是 L-1
# 首刀默认值（其头注自陈"真校准归 P5"），两者不是一回事，故本模块自带默认值。
DEFAULT_DEVIATION_TOLERANCE_PCT: Final = 30.0

FIELD_DURATION: Final = "est_duration_min"
FIELD_MEMORY: Final = "peak_mem_gb"

# 报告落点（docs/_working 契约禁 .json → YAML）
DEFAULT_REPORT_RELPATH: Final = Path("docs/_working/resource_schedule/calibration_report.yaml")

# 中文方向标签（报告给人/AI 读）与 sampler 英文码并行：机器键对齐 sampler 词汇，
# 免得同一件事在两个模块里叫两个名字
_DIRECTION_ZH: Final = {"underdeclared": "低估", "overdeclared": "高估"}

_GENERATED_HEADER: Final = (
    "# [GENERATED] 本文件由 zephyr.infrastructure.system_telemetry.measure_calibration 产出"
    "——禁手工增删条目（静态清单生成器产出红线）。\n"
    "# 只出报告不写注册表：measured.* 写权归 resource_sampler.writeback（双写方=同一实测两个口径）。\n"
    "# proposed_corrections 是建议清单，改申报值须经人在环校正批（P3/P5 流程）。\n"
)


def _utc_now_iso(now_fn: Callable[[], float] | None = None) -> str:
    return datetime.fromtimestamp((now_fn or time.time)(), tz=timezone.utc).isoformat(timespec="seconds")


def report_path(root: str | Path | None = None) -> Path:
    """报告缺省落点：--root 注入优先，否则仓根 docs/_working。"""
    if root:
        return Path(root) / DEFAULT_REPORT_RELPATH
    from zephyr.shared.io.paths import REPO_ROOT

    return REPO_ROOT / DEFAULT_REPORT_RELPATH


def read_calibration_report(path: str | Path | None = None) -> dict[str, Any] | None:
    """读校准报告（晨报消费口）。缺失/损坏 → None（晨报如实写"未生成"，不编造摘要）。"""
    p = Path(path) if path else report_path()
    if not p.exists():
        return None
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        logger.warning("measure_calibration: 报告不可解析 %s: %s", p, exc)
        return None
    return data if isinstance(data, dict) else None


def _axis_row(field: str, declared: float | None, measured: float | None,
              tolerance_pct: float, unit: str) -> dict[str, Any]:
    """单轴偏差判定（时长/内存共用一条数学，避免两套口径）。

    ratio 符号即方向：>0 实测更大=申报被低估；<0 实测更小=申报被高估。
    declared<=0（常驻实体 est_duration_min=0 / 未申报）不做比值——分母为零的"偏差"是
    编造，判 not_comparable 并留原因。
    """
    row: dict[str, Any] = {
        "field": field,
        "unit": unit,
        "declared": declared,
        "measured_p90": measured,
        "deviation_ratio": None,
        "direction": None,
        "direction_code": None,
        "flagged": False,
        "verdict_zh": "",
    }
    if measured is None:
        row["direction_code"] = "no_measurement"
        row["verdict_zh"] = "无实测样本，不判偏差（禁编造）"
        return row
    if declared is None:
        row["direction_code"] = "undeclared"
        row["verdict_zh"] = "有实测无申报=校准器最该补的洞"
        return row
    if declared <= 0:
        row["direction_code"] = "not_comparable"
        row["verdict_zh"] = "申报为 0/负（常驻或占位），比值分母为零不可算"
        return row
    ratio = (measured - declared) / declared
    row["deviation_ratio"] = round(ratio, 4)
    if abs(ratio) * 100.0 <= tolerance_pct:  # 与 sampler match 容差同边界（严格大于才 flag）
        row["direction_code"] = "match"
        row["verdict_zh"] = f"申报与实测偏差在 {tolerance_pct}% 容差内"
        return row
    code = "underdeclared" if ratio > 0 else "overdeclared"
    row["direction_code"] = code
    row["direction"] = _DIRECTION_ZH[code]
    row["flagged"] = True
    row["verdict_zh"] = ("建议上调申报值（实测更长/更大，班次会压到下一班）"
                         if code == "underdeclared"
                         else "建议下调申报值（实测更短/更小，白占并发预算）")
    return row


def _as_float(raw: Any) -> float | None:
    """None 安全取数（申报缺值与实测缺值都不能被 float() 炸成 None→异常）。"""
    return None if raw is None else float(raw)


def _memory_axis(declared: float | None, measured: float | None, n_samples: int,
                 zero_rss: int, tolerance_pct: float) -> dict[str, Any]:
    """内存轴：max×margin 实测 + "全零 RSS≠实测为 0"的降级判定。"""
    axis = _axis_row(FIELD_MEMORY, declared, measured, tolerance_pct, "GB")
    if zero_rss and measured is None and n_samples:
        axis["direction_code"] = "no_rss_evidence"
        axis["flagged"] = False
        axis["verdict_zh"] = (f"样本 {n_samples} 条全为 0 RSS（psutil 缺席/采样瞬间进程消失）"
                              "：无内存证据，不拿 0 当实测")
    return axis


def _correction_rows(tid: str, flagged_axes: list[dict[str, Any]], margin_pct: float) -> list[dict[str, Any]]:
    """flag 轴 → 建议校正条目（消费方=P3 重排班/晨报；改申报值仍须人在环）。"""
    return [
        {
            "task_id": tid,
            "field": a["field"],
            "declared": a["declared"],
            # 键名两轴共用 measured_p90（内存轴实为 max+margin 口径，非分位数）——
            # 消费方按同一键取值，口径差异由 caliber_zh 自解释，不开第二个键名
            "measured_p90": a["measured_p90"],
            "caliber_zh": ("样本 elapsed P90" if a["field"] == FIELD_DURATION
                           else f"样本 RSS max×(1+{margin_pct}%) margin"),
            "deviation_ratio": a["deviation_ratio"],
            "direction": a["direction"],
            "direction_code": a["direction_code"],
            "unit": a["unit"],
            "verdict": a["verdict_zh"],
        }
        for a in flagged_axes
    ]


class MeasureCalibrator:
    """申报 vs 实测 校准器（只读，产出建议校正批）。

    Args:
        registry_path: 注册表路径覆盖；None 走 sampler 的 registry_path()（环境变量可重定向）。
        samples_dir: 样本流目录覆盖；None 走 sampler 的 samples_dir()。
        ledger_path: 孵化台账路径覆盖（本模块只透传给 sampler，不作第二判据）。
        root: 仓根注入（CLI --root 主通道）；给出时按仓根解析注册表/样本目录缺省值。
        now_fn: 时间函数注入（报告 generated_at 可测）。
    """

    def __init__(
        self,
        registry_path: str | Path | None = None,
        samples_dir: str | Path | None = None,
        ledger_path: str | Path | None = None,
        root: str | Path | None = None,
        now_fn: Callable[[], float] | None = None,
    ):
        self._now_fn = now_fn
        root_p = Path(root) if root else None
        self._registry_path = Path(registry_path) if registry_path else (
            root_p / "config" / "resource_profile_registry.yaml" if root_p else default_registry_path())
        self._samples_dir = Path(samples_dir) if samples_dir else (
            root_p / ".runtime" / "logs" / "resource_samples" if root_p else default_samples_dir())
        self._ledger_path = Path(ledger_path) if ledger_path else None
        # 复用采样器读侧：注册表装载、样本流解析（坏行降级）、P90 口径全部同源
        self._sampler = ResourceSampler(
            registry_path=self._registry_path,
            samples_dir=self._samples_dir,
            ledger_path=self._ledger_path,
            now_fn=now_fn,
        )

    # ── 内存轴 ──

    def _measured_peak_mem_gb(self, task_id: str, margin_pct: float) -> tuple[float | None, int, int]:
        """样本 RSS max×(1+margin%) → GB（与 sampler.writeback 同口径）。

        返回 (实测|None, 样本数, 零 RSS 样本数)。全零 RSS=psutil 缺席/进程瞬时消失，
        拿 0 当实测会把"申报高估"判成假阳性，故判无证据。
        """
        samples, bad = self._sampler.read_samples(task_id)
        if bad:
            logger.warning("measure_calibration: %s 样本流 %d 坏行跳过", task_id, bad)
        if not samples:
            return None, 0, 0
        rss = [s.process_resident_bytes for s in samples]
        live = [r for r in rss if r > 0]
        if not live:
            return None, len(samples), len(samples)
        peak_gb = (max(live) / (1024**3)) * (1 + margin_pct / 100.0)
        return round(peak_gb, 4), len(samples), len(rss) - len(live)

    def _entity_row(self, entity: dict, dev: dict[str, Any], tolerance_pct: float,
                    duration_percentile: float, margin_pct: float) -> dict[str, Any]:
        """单实体校准行：两轴判定 + 建议校正条目（零样本→"样本不足"，不编数值）。"""
        tid = str(entity.get("task_id") or "")
        declared_dur = entity.get(FIELD_DURATION)
        # 时长实测走 sampler 的 L-1 对账 API（P90 口径真源），本模块只取其结论不重算
        measured_min = dev.get("measured_p90_duration_min")
        dur_axis = _axis_row(FIELD_DURATION, _as_float(declared_dur), _as_float(measured_min),
                             tolerance_pct, "min")
        mem_measured, n_samples, zero_rss = self._measured_peak_mem_gb(tid, margin_pct)
        mem_axis = _memory_axis(_as_float(entity.get(FIELD_MEMORY)), mem_measured,
                                n_samples, zero_rss, tolerance_pct)
        sample_count = int(dev.get("samples") or 0) or n_samples
        insufficient = sample_count == 0
        status = str(entity.get("status") or "active")
        retired = status in ("retired", "orphaned_source")
        axes = [dur_axis, mem_axis]
        corrections = ([] if retired else
                       _correction_rows(tid, [a for a in axes if a["flagged"]], margin_pct))
        return {
            "task_id": tid,
            "status": status,
            "calibration_status": ("已退役不计" if retired
                                   else ("样本不足" if insufficient else "已校准")),
            "samples": sample_count,
            "confidence": dev.get("confidence", "none"),
            "duration_percentile": duration_percentile,
            "mem_margin_pct": margin_pct,
            "axes": axes,
            "flags": [a["field"] for a in corrections],
            "proposed_corrections": corrections,
            "note_zh": ("样本流无该实体记录：只记状态不记数值（申报值未经实测检验，禁据本报告校正）"
                        if (insufficient and not retired) else ""),
        }

    def calibrate(
        self,
        task_ids: list[str] | None = None,
        tolerance_pct: float = DEFAULT_DEVIATION_TOLERANCE_PCT,
        duration_percentile: float = DEFAULT_DURATION_PERCENTILE,
        margin_pct: float = DEFAULT_MEM_MARGIN_PCT,
    ) -> dict[str, Any]:
        """全量对账，产出报告 dict（含 totals / rows / proposed_corrections 扁平清单）。"""
        entities = [e for e in self._sampler.load_entities() if isinstance(e, dict)]
        dev_rows = {
            str(r.get("task_id")): r
            for r in self._sampler.lifetime_deviation_report(
                task_ids=task_ids, duration_percentile=duration_percentile,
                tolerance_pct=tolerance_pct, include_no_evidence=True)
        }
        rows: list[dict[str, Any]] = []
        for e in entities:
            tid = str(e.get("task_id") or "")
            if not tid or (task_ids is not None and tid not in task_ids):
                continue
            rows.append(self._entity_row(e, dev_rows.get(tid) or {}, tolerance_pct,
                                        duration_percentile, margin_pct))
        flat = [c for r in rows for c in r["proposed_corrections"]]
        totals = {
            "entities": len(rows),
            "calibrated": sum(1 for r in rows if r["calibration_status"] == "已校准"),
            "insufficient_samples": sum(1 for r in rows if r["calibration_status"] == "样本不足"),
            "flagged_entities": sum(1 for r in rows if r["flags"]),
            "flagged_fields": len(flat),
            "低估": sum(1 for c in flat if c["direction_code"] == "underdeclared"),
            "高估": sum(1 for c in flat if c["direction_code"] == "overdeclared"),
        }
        return {
            "schema_version": "1.0.0",
            "doc_type": "report",
            "ttl": "task_bound",
            "title": "资源画像 p90 实测校准报告（申报 vs 实测偏差 flag）",
            "status": "active",
            "generated_at": _utc_now_iso(self._now_fn),
            "generator": "src/zephyr/infrastructure/system_telemetry/measure_calibration.py",
            "registry": str(self._registry_path),
            "samples_dir": str(self._samples_dir),
            "counting_rule": "totals.flagged_fields=proposed_corrections 条目数（同实体可两轴各一条）",
            "caliber_zh": [
                f"时长：样本 process_elapsed_seconds 的 P{int(duration_percentile)}（经 sampler "
                "lifetime_deviation_report，口径真源）",
                f"内存：样本 RSS max×(1+{margin_pct}%) margin（尖刺负载不取分位数，与 writeback 同口径）",
                f"flag 判据：|实测-申报|/申报 > {tolerance_pct}%（严格大于）；零样本实体判『样本不足』不编数值",
            ],
            "tolerance_pct": tolerance_pct,
            "duration_percentile": duration_percentile,
            "mem_margin_pct": margin_pct,
            "totals": totals,
            "proposed_corrections": flat,
            "rows": rows,
        }

    def render_yaml(self, report: dict[str, Any]) -> str:
        """报告 → YAML 文本（GENERATED 头 + 保序 + 中文不转义）。"""
        return _GENERATED_HEADER + yaml.safe_dump(report, allow_unicode=True, sort_keys=False, width=120)

    def write_report(self, report: dict[str, Any], output: str | Path) -> Path:
        """CAS 落盘（docs/_working 契约：YAML，禁 .json）。"""
        out = Path(output)
        out.parent.mkdir(parents=True, exist_ok=True)
        text = self.render_yaml(report)
        expected = content_sha256(out.read_text(encoding="utf-8")) if out.exists() else None
        safe_write_text(out, text, expected_base_sha256=expected)
        return out


def calibrate(
    root: str | Path | None = None,
    registry_path: str | Path | None = None,
    samples_dir: str | Path | None = None,
    task_ids: list[str] | None = None,
    tolerance_pct: float = DEFAULT_DEVIATION_TOLERANCE_PCT,
    duration_percentile: float = DEFAULT_DURATION_PERCENTILE,
    margin_pct: float = DEFAULT_MEM_MARGIN_PCT,
    now_fn: Callable[[], float] | None = None,
) -> dict[str, Any]:
    """便捷入口：MeasureCalibrator(...).calibrate(...)（函数级 API，测试/晨报可直调）。"""
    cal = MeasureCalibrator(registry_path=registry_path, samples_dir=samples_dir,
                            root=root, now_fn=now_fn)
    return cal.calibrate(task_ids=task_ids, tolerance_pct=tolerance_pct,
                        duration_percentile=duration_percentile, margin_pct=margin_pct)


def main(argv: list[str] | None = None) -> int:
    """CLI：算偏差 → 落 YAML 报告（不写注册表）。"""
    ap = argparse.ArgumentParser(
        description="p90 实测校准器（申报 vs 实测偏差 flag，只出报告不写注册表，MOD-RESCHED-CALIB）")
    ap.add_argument("--root", default="", help="仓根注入（测试/E2E；缺省用生产注册表+样本目录）")
    ap.add_argument("--registry", default="", help="注册表路径覆盖（优先于 --root 推导）")
    ap.add_argument("--samples-dir", default="", help="样本流目录覆盖（优先于 --root 推导）")
    ap.add_argument("--output", default="", help=f"报告落点（缺省 {DEFAULT_REPORT_RELPATH}）")
    ap.add_argument("--tasks", default="", help="逗号分隔 task_id 限列（空=全部）")
    ap.add_argument("--tolerance", type=float, default=DEFAULT_DEVIATION_TOLERANCE_PCT,
                    help=f"flag 阈值百分比（默认 {DEFAULT_DEVIATION_TOLERANCE_PCT}）")
    ap.add_argument("--percentile", type=float, default=DEFAULT_DURATION_PERCENTILE,
                    help=f"时长分位数（默认 {DEFAULT_DURATION_PERCENTILE}）")
    ap.add_argument("--margin", type=float, default=DEFAULT_MEM_MARGIN_PCT,
                    help=f"内存 margin 百分比（默认 {DEFAULT_MEM_MARGIN_PCT}）")
    ap.add_argument("--no-write", action="store_true", help="只打印不落盘（体检/演练）")
    ap.add_argument("--print", dest="do_print", action="store_true", help="stdout 打 JSON 摘要")
    args = ap.parse_args(argv)

    root = args.root or None
    cal = MeasureCalibrator(registry_path=args.registry or None, samples_dir=args.samples_dir or None,
                            root=root, now_fn=time.time)
    report = cal.calibrate(
        task_ids=[t for t in args.tasks.split(",") if t] or None,
        tolerance_pct=args.tolerance, duration_percentile=args.percentile, margin_pct=args.margin)
    out = cal.write_report(report, args.output or report_path(root)) if not args.no_write else None
    summary = {"ok": True, "report": str(out) if out else "未落盘(--no-write)", "totals": report["totals"]}
    if args.do_print:
        summary["proposed_corrections"] = report["proposed_corrections"]
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
