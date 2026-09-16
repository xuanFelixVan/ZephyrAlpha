# [BLUEPRINT] MOD-RESCHED-SAMPLER | docs/03_modules/_cross_layer/resource_sampler/blueprint.md | §
# [MODULE] zephyr.infrastructure.system_telemetry.resource_sampler
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] psutil(可选，缺席降级空扫描); yaml; zephyr.shared.io.file_utils
# [CONSUMERS] scripts/governance/generators/generate_resource_week_view.py（measured 段入图）;
#   zephyr.gov_enforcement.commit_gates.resource_schedule_gate（内存天花板实测口径）;
#   晨审（.runtime/logs/resource_samples/ 样本流）;
#   tests/infrastructure/test_resource_sampler.py
# [STARTUP] manual（CLI one-shot / --loop 周期；采样是 reaper 兄弟进程式，无常驻自拉起）
# [MATURITY] testing
# [INVARIANTS] 零侵入——只读进程表，不杀不启不改任何进程（收割=reaper，本模块永不 kill）;
#   样本 append-only JSONL（.runtime/logs/resource_samples/<task_id>.jsonl）;
#   回写只动注册表 measured.* 段（人填字段零触碰，CAS safe_write_text）;
#   psutil 缺席/扫描异常降级为空样本（fail-safe 不抛）;
#   观测目录/注册表路径可注入（测试隔离禁写生产路径）;
#   样本字段名 Prometheus 命名纪律（zephyr_resource_ 前缀 + base unit 后缀）
# [MODIFY-GUARD] config/resource_profile_registry.yaml measured 段结构变更须同步本模块+生成器
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RegistryNotFound(FileNotFoundError); psutil 缺席=空扫描; JSONL 损坏行跳过并计数
# [TESTS] tests/infrastructure/test_resource_sampler.py
# [A_module] module_id=MOD-RESCHED-SAMPLER | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 注册表实体清单
#   fields: config/resource_profile_registry.yaml（路径可注入）
#   code: load_entities / derive_patterns
# - id: I2
#   name: 进程表快照
#   fields: psutil 全表（pid/cmdline/create_time/cpu_times）
#   code: _ps_snapshot（scanner 注入点=测试 stub 主通道）
# 层: 算法
# - id: A1
#   name_zh: ① 观测模式推导
#   name_en: derive_patterns
#   intro: schedule_truth_source→cmdline 正则（ps1 抽被调脚本基名/静态表/宿主共享跳过）
#   desc: ps1 真源解析 _PS1_SCRIPT_RE；schedule.yaml 槽位=宿主共享 v1 不归因；手动实体走 STATIC_OBSERVE_PATTERNS
#   inputs: I1
#   outputs: dict[task_id, compiled_regex]
# - id: A2
#   name_zh: ② 扫描记样本
#   name_en: scan_once
#   intro: 正则命中→GNU time 口径样本→append-only JSONL（Prometheus 命名字段）
#   desc: cpu_ratio=生存期均值（%P 口径）；resident=瞬时 RSS（跨轮 max 由回写聚合）
#   inputs: I1, I2
#   outputs: .runtime/logs/resource_samples/<task_id>.jsonl
# - id: A3
#   name_zh: ③ 实测回写
#   name_en: writeback
#   intro: memory=实测 max+15% margin（尖刺不失真）、duration=P90，CAS 只动 measured 四键
#   desc: VPA margin 口径；safe_write_text CAS；人填字段零触碰
#   inputs: A2
#   outputs: 注册表 measured.peak_mem_gb/p90_duration_min/samples/last_at
# 层: 输出
# - id: O1
#   name_zh: 画像实测闭环
#   name_en: measured feedback loop
#   intro: 人申报初值→采样器实测回写→闸内存天花板/重叠判定消费实测口径
#   downstream: zephyr.gov_enforcement.commit_gates.resource_schedule_gate; generate_resource_week_view
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""resource_sampler — 资源实测采样器（MOD-RESCHED-SAMPLER，B1 器）。

资源排班全景四件套之"器"（方案 docs/_working/resource_schedule/
resource_schedule_panorama_plan_v1.md §2.2）。与 process_reaper 同款技术：
cmdline 模式匹配观察进程表，零侵入（不改任何脚本调用点、不杀进程）。

三段：
1. ``scan_once`` — 扫描进程表：注册表 active 实体 → 观测模式（cmdline 正则）
   → 命中者记样本（GNU time 口径：resident bytes、cpu_ratio=生存期平均 CPU%、
   elapsed_seconds）→ append 到 ``.runtime/logs/resource_samples/<task_id>.jsonl``
   （Prometheus 命名字段）。
2. ``writeback`` — 实测回写：读样本流 → memory 取实测 max+15% margin（VPA
   recommendationMarginFraction 口径，不取分位数——批测/挖矿是尖刺负载，P90 对
   尖刺失真）、duration 取 P90 → CAS 写回注册表 measured.* 段（只动四键）。
3. ``run_loop`` — 周期模式（CLI --loop），one-shot 为默认。

观测模式推导（schedule_truth_source → cmdline 正则）：
- *.ps1 真源：解析 ps1 文本中被调脚本名（-File x.ps1 / python y.py）→ 基名匹配；
- 手动/动态实体：本模块 STATIC_OBSERVE_PATTERNS 静态表（reaper 白名单同范式，
  进程匹配知识归采样器所有）；
- 共享宿主槽位（schedule.yaml 21 槽跑在 DataScheduler 单进程内）：v1 不做槽位级
  进程归因（会 N 倍重复计数宿主），扫描摘要记 host_shared_skipped，蓝图 §限制。

边界：不做收割（reaper）、不做阈值判定（闸）、不做水位门（process_incubator
SpawnWaterGate）。memory_emergency_percent 等全局压力阈值真源在
config/resource_optimization.yaml——本模块不收编。

CLI:
  python -m zephyr.infrastructure.system_telemetry.resource_sampler scan
  python -m zephyr.infrastructure.system_telemetry.resource_sampler writeback
  python -m zephyr.infrastructure.system_telemetry.resource_sampler scan --loop --interval 60
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import yaml

from zephyr.shared.io.file_utils import safe_write_text

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_DURATION_PERCENTILE",
    "DEFAULT_MEM_MARGIN_PCT",
    "ENV_REGISTRY",
    "ENV_SAMPLES_DIR",
    "STATIC_OBSERVE_PATTERNS",
    "Sample",
    "ResourceSampler",
    "registry_path",
    "samples_dir",
]

# 环境变量重定向（测试隔离主通道；生产缺省路径只在未注入时生效）
ENV_SAMPLES_DIR = "ZEPHYR_RESOURCE_SAMPLES_DIR"
ENV_REGISTRY = "ZEPHYR_RESOURCE_PROFILE_REGISTRY"

DEFAULT_SAMPLES_DIRNAME = "resource_samples"
DEFAULT_REGISTRY_PATH = Path("config/resource_profile_registry.yaml")

# 回写口径（方案 §2.2 裁决，可调）
DEFAULT_MEM_MARGIN_PCT = 15.0  # VPA recommendationMarginFraction 同款
DEFAULT_DURATION_PERCENTILE = 90  # VPA target percentile

# 手动/动态实体观测表（进程匹配知识归采样器；task_id 须与生成器 §3.C 种子一致）
STATIC_OBSERVE_PATTERNS: dict[str, str] = {
    "manual_factory_grid_executor": r"factory_grid_executor|grid_executor\.py",
    "manual_kronos_adapter": r"kronos_adapter",
    "manual_run_sentiment_batch": r"run_sentiment_batch",
    "manual_run_sft_train": r"run_sft_train",
    "manual_convert_gguf": r"convert_gguf",
    "manual_lane_c_agentic_miner": r"lane_c2_agentic_miner|agentic_miner\.py",
    "manual_repair_kline_tz": r"repair_kline_tz",
}

# ps1 文本中抽取被调脚本名（-File scripts\x.ps1 / python scripts\y.py）
_PS1_SCRIPT_RE = re.compile(r"(?:-File\s+|python(?:\.exe)?\s+)[^\r\n]*?([A-Za-z0-9_\-]+\.(?:ps1|py))", re.IGNORECASE)


def samples_dir() -> Path:
    """样本流目录：环境变量可重定向（测试隔离），缺省生产 .runtime 路径。"""
    env = os.environ.get(ENV_SAMPLES_DIR, "")
    if env:
        return Path(env)
    from zephyr.shared.io.paths import REPO_ROOT

    return REPO_ROOT / ".runtime" / "logs" / DEFAULT_SAMPLES_DIRNAME


def registry_path() -> Path:
    """注册表路径：环境变量可重定向，缺省 config/resource_profile_registry.yaml。"""
    env = os.environ.get(ENV_REGISTRY, "")
    if env:
        return Path(env)
    from zephyr.shared.io.paths import REPO_ROOT

    return REPO_ROOT / DEFAULT_REGISTRY_PATH


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Sample:
    """一条进程样本（字段名 Prometheus 纪律：zephyr_resource_ 前缀+base unit）。"""

    sample_time_seconds: float
    task_id: str
    pid: int
    process_resident_bytes: int
    process_cpu_ratio: float
    process_elapsed_seconds: float
    exit_code: int | None = None
    e0_gate_result: str | None = None

    def to_json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)


def _percentile(values: list[float], pct: float) -> float:
    """线性插值分位数（空表返回 0.0）。"""
    if not values:
        return 0.0
    vs = sorted(values)
    if len(vs) == 1:
        return vs[0]
    k = (len(vs) - 1) * (pct / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(vs) - 1)
    frac = k - lo
    return vs[lo] * (1 - frac) + vs[hi] * frac


class ResourceSampler:
    """零侵入进程采样器：观察→记样本→实测回写画像（reaper 兄弟式）。

    Args:
        registry_path: 注册表路径；None 走 registry_path()（环境变量可重定向）。
        samples_dir: 样本流目录；None 走 samples_dir()。
        patterns: task_id → cmdline 正则注入（E2E 探针主通道）；None 时自动推导。
        scanner: 进程快照函数注入（测试 stub 主通道，测试禁真启重活进程）。
            签名 -> list[dict]，每 dict 含 pid/cmdline(str)/create_time/cpu_time_seconds。
        now_fn: 时间函数注入（时钟回拨红蓝测试用）。
    """

    def __init__(
        self,
        registry_path: str | Path | None = None,
        samples_dir: str | Path | None = None,
        patterns: dict[str, str] | None = None,
        scanner: Callable[[], list[dict]] | None = None,
        now_fn: Callable[[], float] | None = None,
    ):
        self._registry_path = Path(registry_path) if registry_path else None
        self._samples_dir = Path(samples_dir) if samples_dir else None
        self._patterns_override = patterns
        self._scanner = scanner
        self._now_fn = now_fn or time.time

    # ── 注册表 ──

    def _reg_path(self) -> Path:
        return self._registry_path if self._registry_path else registry_path()

    def load_entities(self) -> list[dict]:
        """读注册表实体清单（缺失 fail-closed 抛 FileNotFoundError；损坏抛 YAML 异常）。"""
        p = self._reg_path()
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return list(data.get("entities") or [])

    def _sdir(self) -> Path:
        return self._samples_dir if self._samples_dir else samples_dir()

    def samples_file(self, task_id: str) -> Path:
        """实体样本流路径：<samples_dir>/<task_id>.jsonl。"""
        return self._sdir() / f"{task_id}.jsonl"

    # ── 观测模式推导 ──

    def derive_patterns(self, entities: list[dict]) -> tuple[dict[str, re.Pattern], list[str]]:
        """schedule_truth_source → cmdline 正则。返回 (编译表, 宿主共享不可观测 task_ids)。"""
        patterns: dict[str, re.Pattern] = {}
        host_shared: list[str] = []
        for e in entities:
            if not isinstance(e, dict):
                continue
            tid = str(e.get("task_id") or "")
            if not tid or str(e.get("status") or "active") == "retired":
                continue
            if self._patterns_override and tid in self._patterns_override:
                try:
                    patterns[tid] = re.compile(self._patterns_override[tid])
                except re.error:
                    logger.warning("sampler: 非法正则 %s（task=%s）跳过", self._patterns_override[tid], tid)
                continue
            src = str(e.get("schedule_truth_source") or "")
            low = src.replace("\\", "/").lower()
            if low.endswith(".ps1"):
                pats = self._patterns_from_ps1(src)
                if pats:
                    patterns[tid] = re.compile("|".join(pats), re.IGNORECASE)
            elif low.endswith("schedule.yaml"):
                host_shared.append(tid)  # 共享宿主槽位：v1 不做槽位级归因（防 N 倍计数）
            elif tid in STATIC_OBSERVE_PATTERNS:
                try:
                    patterns[tid] = re.compile(STATIC_OBSERVE_PATTERNS[tid], re.IGNORECASE)
                except re.error:
                    logger.warning("sampler: 静态正则非法（task=%s）跳过", tid)
        return patterns, host_shared

    def _patterns_from_ps1(self, rel_src: str) -> list[str]:
        """从 ps1 真源抽被调脚本基名（reaper 同款 cmdline 子串思想，零硬编码）。"""
        try:
            from zephyr.shared.io.paths import REPO_ROOT

            text = (REPO_ROOT / rel_src).read_text(encoding="utf-8", errors="replace")
        except OSError:
            logger.debug("sampler: ps1 真源不可读 %s", rel_src)
            return []
        names = set(_PS1_SCRIPT_RE.findall(text))
        # 自身注册脚本排除（register_x.ps1 是登记器不是被观察负载）
        return sorted(n for n in names if not n.lower().startswith("register_"))

    # ── 扫描 ──

    def _ps_snapshot(self) -> list[dict]:
        """psutil 进程快照（缺席/异常降级空表——观测器绝不成为负载）。"""
        try:
            import psutil
        except ImportError:
            logger.warning("sampler: psutil 不可用，本轮空扫描")
            return []
        me = psutil.Process()
        mine = {me.pid}
        parent = me.parent()
        if parent is not None:
            mine.add(parent.pid)
        out: list[dict] = []
        for proc in psutil.process_iter(["pid", "cmdline", "create_time"]):
            try:
                info = proc.info
                if info["pid"] in mine:
                    continue
                blob = " ".join(info["cmdline"] or [])
                if not blob:
                    continue
                ct = float(info["create_time"] or 0.0)
                try:
                    t = proc.cpu_times()
                    cpu_total = float(t.user + t.system)
                except Exception:  # noqa: BLE001 — 消失竞态按 0
                    cpu_total = 0.0
                out.append({"pid": info["pid"], "cmdline": blob, "create_time": ct, "cpu_time_seconds": cpu_total})
            except Exception:  # noqa: BLE001 — 进程消失竞态逐个跳过
                continue
        return out

    def scan_once(self, now: float | None = None) -> dict:
        """一轮扫描：命中实体记样本 append JSONL。返回摘要（供日志/测试断言）。"""
        ts = now if now is not None else self._now_fn()
        entities = self.load_entities()
        patterns, host_shared = self.derive_patterns(entities)
        procs = self._scanner() if self._scanner else self._ps_snapshot()
        matched_pids: dict[int, str] = {}
        for tid, pat in patterns.items():
            for p in procs:
                if pat.search(p["cmdline"]):
                    # 一进程多命中取先登记实体（确定性：按注册表顺序）
                    matched_pids.setdefault(p["pid"], tid)
        written: dict[str, int] = {}
        for p in procs:
            tid = matched_pids.get(p["pid"])
            if tid is None:
                continue
            elapsed = max(0.0, ts - p["create_time"]) if p["create_time"] > 0 else 0.0
            cpu_ratio = (p["cpu_time_seconds"] / elapsed) if elapsed > 1.0 else 0.0
            resident = 0
            try:
                import psutil

                resident = int(psutil.Process(p["pid"]).memory_info().rss)
            except Exception:  # noqa: BLE001 — 采样瞬间消失：记 0 字节样本（exit 隐含）
                resident = 0
            sample = Sample(
                sample_time_seconds=ts,
                task_id=tid,
                pid=int(p["pid"]),
                process_resident_bytes=resident,
                process_cpu_ratio=round(cpu_ratio, 4),
                process_elapsed_seconds=round(elapsed, 1),
            )
            self._append_sample(sample)
            written[tid] = written.get(tid, 0) + 1
        summary = {
            "ts": ts,
            "scanned_processes": len(procs),
            "observable_tasks": sorted(patterns),
            "host_shared_skipped": host_shared,
            "samples_written": written,
        }
        logger.info("sampler scan: %s", json.dumps(summary, ensure_ascii=False))
        return summary

    def _append_sample(self, sample: Sample) -> None:
        """append 单行 JSONL（单写者模型：sampler 是该文件唯一写者，O_APPEND 行写）。"""
        f = self.samples_file(sample.task_id)
        f.parent.mkdir(parents=True, exist_ok=True)
        with open(f, "a", encoding="utf-8") as fh:
            fh.write(sample.to_json() + "\n")

    def read_samples(self, task_id: str) -> tuple[list[Sample], int]:
        """读样本流（损坏行跳过并计数——JSONL 损坏降级不炸）。返回 (样本, 坏行数)。"""
        f = self.samples_file(task_id)
        if not f.exists():
            return [], 0
        out: list[Sample] = []
        bad = 0
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                out.append(
                    Sample(
                        sample_time_seconds=float(obj["sample_time_seconds"]),
                        task_id=str(obj["task_id"]),
                        pid=int(obj["pid"]),
                        process_resident_bytes=int(obj["process_resident_bytes"]),
                        process_cpu_ratio=float(obj.get("process_cpu_ratio", 0.0)),
                        process_elapsed_seconds=float(obj.get("process_elapsed_seconds", 0.0)),
                        exit_code=(int(obj["exit_code"]) if obj.get("exit_code") is not None else None),
                        e0_gate_result=(obj.get("e0_gate_result") if obj.get("e0_gate_result") is not None else None),
                    )
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                bad += 1
        return out, bad

    # ── 实测回写 ──

    def writeback(
        self,
        task_ids: list[str] | None = None,
        margin_pct: float = DEFAULT_MEM_MARGIN_PCT,
        duration_percentile: float = DEFAULT_DURATION_PERCENTILE,
    ) -> dict:
        """实测回写注册表 measured.*（CAS 只动四键；人填字段零触碰）。

        memory = 实测 max × (1+margin%)（尖刺负载不取分位数，方案 §2.2 裁决）；
        duration = elapsed P90；零样本实体跳过不动。
        """
        p = self._reg_path()
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        entities = list(data.get("entities") or [])
        updated: dict[str, dict] = {}
        for e in entities:
            if not isinstance(e, dict):
                continue
            tid = str(e.get("task_id") or "")
            if task_ids is not None and tid not in task_ids:
                continue
            samples, bad = self.read_samples(tid)
            if bad:
                logger.warning("sampler writeback: %s 样本流 %d 坏行跳过", tid, bad)
            if not samples:
                continue
            mem_max = max(s.process_resident_bytes for s in samples)
            p90 = _percentile([s.process_elapsed_seconds for s in samples], duration_percentile)
            measured = e.get("measured") if isinstance(e.get("measured"), dict) else {}
            measured["peak_mem_gb"] = round((mem_max / (1024**3)) * (1 + margin_pct / 100.0), 4)
            measured["p90_duration_min"] = int(round(p90 / 60.0))
            measured["samples"] = len(samples)
            measured["last_at"] = _utc_now_iso()
            e["measured"] = measured
            updated[tid] = dict(measured)
        if updated:
            data["entities"] = entities
            new_text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120)
            old_text = p.read_text(encoding="utf-8") if p.exists() else ""
            # 文件头注释块保全：YAML 重序列化会丢头部注释——writeback 只拥有 measured
            # 四键，无权重写文件身份声明（GENERATED 头是生成器红线，2026-09-16 实证
            # 剥离后治本：抓原文件首部连续 # 行，回写时原样前置）
            header_lines: list[str] = []
            for _ln in old_text.splitlines():
                if _ln.startswith("#"):
                    header_lines.append(_ln)
                else:
                    break
            if header_lines:
                new_text = "\n".join(header_lines) + "\n" + new_text
            expected = None
            if old_text:
                from zephyr.shared.io.file_utils import content_sha256

                expected = content_sha256(old_text)
            safe_write_text(p, new_text, expected_base_sha256=expected)
        return {"updated": updated, "registry": str(p)}

    # ── 周期模式 ──

    def run_loop(self, interval_s: float = 60.0, max_cycles: int | None = None) -> None:
        """周期扫描（CLI --loop；本进程无常驻自拉起，循环只在被显式调用时存在）。"""
        cycle = 0
        while max_cycles is None or cycle < max_cycles:
            try:
                self.scan_once()
            except Exception:  # noqa: BLE001 — 观测循环单轮异常不退出（fail-safe）
                logger.exception("sampler loop cycle failed")
            cycle += 1
            if max_cycles is not None and cycle >= max_cycles:
                break
            time.sleep(interval_s)


def main() -> int:
    """CLI：scan / writeback / scan --loop。"""
    ap = argparse.ArgumentParser(description="资源实测采样器（零侵入 cmdline 匹配，MOD-RESCHED-SAMPLER）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan", help="扫描一轮进程表记样本")
    s.add_argument("--loop", action="store_true", help="周期模式（默认 one-shot）")
    s.add_argument("--interval", type=float, default=60.0, help="周期秒数（--loop 用）")
    s.add_argument("--max-cycles", type=int, default=None, help="最大轮数（测试/演示用）")
    w = sub.add_parser("writeback", help="实测回写注册表 measured 段")
    w.add_argument("--tasks", default="", help="逗号分隔 task_id 限写（空=全部有样本者）")
    args = ap.parse_args()
    sampler = ResourceSampler()
    if args.cmd == "scan":
        if args.loop:
            sampler.run_loop(interval_s=args.interval, max_cycles=args.max_cycles)
        else:
            print(json.dumps(sampler.scan_once(), ensure_ascii=False))
        return 0
    out = sampler.writeback(task_ids=[t for t in args.tasks.split(",") if t] or None)
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
