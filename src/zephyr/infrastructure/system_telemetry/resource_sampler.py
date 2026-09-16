# [BLUEPRINT] MOD-RESCHED-SAMPLER | docs/03_modules/_cross_layer/resource_sampler/blueprint.md | §
# [MODULE] zephyr.infrastructure.system_telemetry.resource_sampler
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] psutil(可选，缺席降级空扫描); yaml; zephyr.shared.io.file_utils;
#   .runtime/process_incubator/ledger.jsonl(L-1 孵化台账，**只读**——观测器永不写他人台账)
# [CONSUMERS] scripts/governance/generators/generate_resource_week_view.py（measured 段入图）;
#   zephyr.gov_enforcement.commit_gates.resource_schedule_gate（内存天花板实测口径）;
#   晨审（.runtime/logs/resource_samples/ 样本流）;
#   P5 p90 校准器（lifetime_deviation_report 函数级 API，2026-09-17 L-1）;
#   tests/infrastructure/test_resource_sampler.py
# [STARTUP] manual（CLI one-shot / --loop 周期；采样是 reaper 兄弟进程式，无常驻自拉起）
# [MATURITY] testing
# [INVARIANTS] 零侵入——只读进程表，不杀不启不改任何进程（收割=reaper，本模块永不 kill）;
#   样本 append-only JSONL（.runtime/logs/resource_samples/<task_id>.jsonl）；L-1 新键
#   只能"新增可选"，历史行不回写（R-B）;
#   回写只动注册表 measured.* 段（人填字段零触碰，CAS safe_write_text）；零样本实体
#   **只记原因不记数值**（measured.no_sample_reason_zh，禁编造）;
#   L-1 归因铁律=**唯一命中才下判**：pid 复用多记录/一台账名对多实体/正则链与台账链
#   互指不同实体 → 一律判歧义不写样本（错一次归因比零归因危险，measured 是闸的实测口径）;
#   psutil 缺席/扫描异常降级为空样本（fail-safe 不抛）；台账缺失/损坏=降级为仅 cmdline 归因;
#   观测目录/注册表/台账路径可注入（测试隔离禁写生产路径）;
#   样本字段名 Prometheus 命名纪律（zephyr_resource_ 前缀 + base unit 后缀）
# [MODIFY-GUARD] config/resource_profile_registry.yaml measured 段结构变更须同步本模块+生成器
#   （2026-09-17 L-1 增第 5 子键 no_sample_reason_zh：生成器 _base_entity 骨架已同步）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RegistryNotFound(FileNotFoundError); psutil 缺席=空扫描; JSONL 损坏行跳过并计数
# [TESTS] tests/infrastructure/test_resource_sampler.py
# [A_module] module_id=MOD-RESCHED-SAMPLER | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
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

三段（+L-1 起多一条独立证据链与一份对账输出）：
1. ``scan_once`` — 扫描进程表：注册表 active 实体 → 观测模式（cmdline 正则）
   → 命中者记样本（GNU time 口径：resident bytes、cpu_ratio=生存期平均 CPU%、
   elapsed_seconds）→ append 到 ``.runtime/logs/resource_samples/<task_id>.jsonl``
   （Prometheus 命名字段）。
2. ``writeback`` — 实测回写：读样本流 → memory 取实测 max+15% margin（VPA
   recommendationMarginFraction 口径，不取分位数——批测/挖矿是尖刺负载，P90 对
   尖刺失真）、duration 取 P90 → CAS 写回注册表 measured.* 段。
3. ``run_loop`` — 周期模式（CLI --loop），one-shot 为默认。
4. **L-1** ``lifetime_deviation_report`` — 申报寿命（est_duration_min / 台账
   expected_lifetime_s）vs 实测寿命（样本 elapsed P90 / 台账 exited-spawned）对账，
   函数级 API 供 P5 p90 校准器复用（本模块不做 UI）。

观测模式推导（schedule_truth_source → cmdline 正则）：
- *.ps1 真源：解析 ps1 文本中被调脚本名（-File x.ps1 / python y.py）→ 基名匹配；
- 手动/动态实体：本模块 STATIC_OBSERVE_PATTERNS 静态表（reaper 白名单同范式，
  进程匹配知识归采样器所有）；
- 共享宿主槽位（schedule.yaml 21 槽跑在 DataScheduler 单进程内）：**L-1 起走台账
  pid join 归因**——台账真给出该槽位的 child_pid 才归因（并解锁出 host_shared_skipped），
  给不出则仍不归因（按宿主 RSS 逐槽回填=N 倍重复计数宿主），measured 留 null 且
  在 no_sample_reason_zh 记如实原因，禁编造。

边界：不做收割（reaper）、不做阈值判定（闸）、不做水位门（process_incubator
SpawnWaterGate）。memory_emergency_percent 等全局压力阈值真源在
config/resource_optimization.yaml——本模块不收编。

CLI:
  python -m zephyr.infrastructure.system_telemetry.resource_sampler scan
  python -m zephyr.infrastructure.system_telemetry.resource_sampler writeback
  python -m zephyr.infrastructure.system_telemetry.resource_sampler deviations --all
  python -m zephyr.infrastructure.system_telemetry.resource_sampler scan --loop --interval 60
# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/resource_sampler.yaml
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
from typing import Callable, Final, Iterable

import yaml

from zephyr.shared.io.file_utils import safe_write_text

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_DURATION_PERCENTILE",
    "DEFAULT_MEM_MARGIN_PCT",
    "ENV_LEDGER",
    "ENV_REGISTRY",
    "ENV_SAMPLES_DIR",
    "LIFETIME_ALIVE_SUFFIX",
    "STATIC_OBSERVE_PATTERNS",
    "TASK_ID_PREFIXES",
    "IncubationLedger",
    "IncubationRecord",
    "ResourceSampler",
    "Sample",
    "ledger_path",
    "registry_path",
    "samples_dir",
    "task_ids_for_record",
]

# 环境变量重定向（测试隔离主通道；生产缺省路径只在未注入时生效）
ENV_SAMPLES_DIR = "ZEPHYR_RESOURCE_SAMPLES_DIR"
ENV_REGISTRY = "ZEPHYR_RESOURCE_PROFILE_REGISTRY"
ENV_LEDGER = "ZEPHYR_INCUBATION_LEDGER"  # L-1：孵化台账路径重定向（单测合成 fixture 主通道）

DEFAULT_SAMPLES_DIRNAME = "resource_samples"
DEFAULT_REGISTRY_PATH = Path("config/resource_profile_registry.yaml")
# 孵化台账真源（process_incubator 写、本模块**只读**——零侵入纪律：观测器永不写他人台账）
DEFAULT_LEDGER_PATH = Path(".runtime/process_incubator/ledger.jsonl")

# 回写口径（方案 §2.2 裁决，可调）
DEFAULT_MEM_MARGIN_PCT = 15.0  # VPA recommendationMarginFraction 同款
DEFAULT_DURATION_PERCENTILE = 90  # VPA target percentile
# L-1 偏差对账容差：申报 vs 实测 偏差在此百分比内判 match（首刀默认值，真校准归 P5
# p90 校准器——它复用本模块 API 并可重定此阈值，本模块不越权定终值）
DEFAULT_DEVIATION_TOLERANCE_PCT = 20.0

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


def ledger_path() -> Path:
    """L-1 孵化台账路径：环境变量可重定向（单测合成 fixture），缺省生产 .runtime 台账。"""
    env = os.environ.get(ENV_LEDGER, "")
    if env:
        return Path(env)
    from zephyr.shared.io.paths import REPO_ROOT

    return REPO_ROOT / DEFAULT_LEDGER_PATH


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Sample:
    """一条进程样本（字段名 Prometheus 纪律：zephyr_resource_ 前缀+base unit）。

    L-1 追加三个**可选归因溯源键**（缺省 None）：老样本行没有它们也照常解析——
    样本流 append-only（R-B），永不回写历史行，故新键只能"新增可选"而不能改语义。
    """

    sample_time_seconds: float
    task_id: str
    pid: int
    process_resident_bytes: int
    process_cpu_ratio: float
    process_elapsed_seconds: float
    exit_code: int | None = None
    e0_gate_result: str | None = None
    attribution: str | None = None  # "pattern" | "ledger" | "pattern+ledger"（L-1 归因证据链）
    ledger_record_id: str | None = None  # 命中的台账 record_id（可回溯到孵化事件）
    parent_pid: int | None = None  # 台账 parent_pid——宿主/子进程分层计数靠它（防 N 倍重复）

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


# ---------------------------------------------------------------------------
# L-1 孵化台账 × 采样流 pid join（v2 方案 L-1，2026-09-17 P1-a）
# 病灶：采样器过去只认 cmdline 正则，两类实体因此永久零样本——
#   ① 21 个 data_slot_* 槽位跑在 DataScheduler **单进程内**（APScheduler 线程），
#      进程表里没有槽位级 pid，按宿主 RSS 逐槽回填=N 倍重复计数（v1 因此直接跳过）；
#   ② 被孵化池拉起/转手的子进程，cmdline 常不含真源脚本名（python -m 形式/包装层改写），
#      正则看不见它，实测就此断线。
# 治法：进程侧多一条独立证据链——孵化台账（process_incubator 的 append-only JSONL，
# 含 child_pid/parent_pid/root_pid/ancestor_chain/name/owner/cmd/spawned_at/
# expected_lifetime_s/exited_at）。按 **pid↔台账 join** 把样本挂回实体，宿主与子进程
# 用父子链分开计（宿主只算宿主，槽位只在台账真给出该槽位 pid 时才归因）。
# 纪律：join **只在唯一命中时下判**——同 pid 被多条台账记录（Windows pid 复用是真的）
# 或一个台账名对上多个实体时，一律判歧义不写样本（宁可少一个样本，不可把 A 的 RSS 记到
# B 头上——measured 是闸的内存天花板实测口径，错一次归因比零归因危险）。
# ---------------------------------------------------------------------------

# 台账里的任务名前缀惯例（与生成器 _snake/sch_ 命名口径同源）——用于反推实体 task_id。
# 这是**命名约定知识**不是实体清单副本（实体清单真源=注册表），故可硬编码；新增前缀
# 时须同步生成器实体命名臂。
TASK_ID_PREFIXES: tuple[str, ...] = ("sch_", "ops_", "manual_", "data_slot_", "event_", "dynamic_")

# 台账仍存活记录的"寿命下界"标记：exited_at=null 时实测寿命只能取"至少跑了多久"，
# 对账时方向性明确（ underestimate 而非编造）。
LIFETIME_ALIVE_SUFFIX: Final = "_alive_ge"


@dataclass(frozen=True)
class IncubationRecord:
    """孵化台账一行（未知键忽略，缺键取默认——台账结构演进不得炸观测器）。"""

    record_id: str
    child_pid: int
    parent_pid: int
    root_pid: int
    name: str
    owner: str
    cmd: str
    spawned_at: float
    expected_lifetime_s: float | None = None
    exited_at: float | None = None
    exit_code: int | None = None
    reaped: bool = False
    ancestor_chain: tuple[int, ...] = ()

    @property
    def actual_lifetime_s(self) -> float | None:
        """台账侧实测寿命（秒）；exited_at 缺失=仍存活 → None（由调用方按"下界"处理）。"""
        if self.exited_at is None or self.spawned_at <= 0:
            return None
        return max(0.0, self.exited_at - self.spawned_at)


class IncubationLedger:
    """孵化台账只读索引：pid → 记录（时间窗消歧，歧义不判）。"""

    def __init__(self, records: list[IncubationRecord] | None = None,
                 bad_lines: int = 0, source: str | None = None):
        self.records: list[IncubationRecord] = list(records or [])
        self.bad_lines = int(bad_lines)
        self.source = source
        self._by_pid: dict[int, list[IncubationRecord]] = {}
        for r in self.records:
            self._by_pid.setdefault(r.child_pid, []).append(r)
        for pid in self._by_pid:
            self._by_pid[pid].sort(key=lambda r: r.spawned_at)

    def __len__(self) -> int:
        return len(self.records)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "IncubationLedger":
        """读台账 JSONL（缺失=空账本不抛；坏行计数跳过——与样本流同一降级纪律）。"""
        p = Path(path) if path else ledger_path()
        if not p.exists():
            logger.debug("sampler L-1: 孵化台账不存在 %s（降级为仅 cmdline 归因）", p)
            return cls([], source=str(p))
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            logger.warning("sampler L-1: 台账不可读 %s: %s", p, exc)
            return cls([], source=str(p))
        out: list[IncubationRecord] = []
        bad = 0
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                out.append(
                    IncubationRecord(
                        record_id=str(obj.get("record_id") or ""),
                        child_pid=int(obj["child_pid"]),
                        parent_pid=int(obj.get("parent_pid") or 0),
                        root_pid=int(obj.get("root_pid") or 0),
                        name=str(obj.get("name") or ""),
                        owner=str(obj.get("owner") or ""),
                        cmd=str(obj.get("cmd") or ""),
                        spawned_at=float(obj.get("spawned_at") or 0.0),
                        expected_lifetime_s=(float(obj["expected_lifetime_s"])
                                             if obj.get("expected_lifetime_s") is not None else None),
                        exited_at=(float(obj["exited_at"]) if obj.get("exited_at") is not None else None),
                        exit_code=(int(obj["exit_code"]) if obj.get("exit_code") is not None else None),
                        reaped=bool(obj.get("reaped")),
                        ancestor_chain=tuple(int(x) for x in (obj.get("ancestor_chain") or [])),
                    )
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                bad += 1
        if bad:
            logger.warning("sampler L-1: 台账 %s 坏行 %d 已跳过", p, bad)
        return cls(out, bad_lines=bad, source=str(p))

    def records_for_pid(self, pid: int) -> list[IncubationRecord]:
        """该 pid 的全部台账记录（按 spawned_at 升序；pid 复用时>1 条）。"""
        return list(self._by_pid.get(int(pid)) or [])

    def attribute_pid(self, pid: int, at_ts: float | None = None
                      ) -> tuple[IncubationRecord | None, str]:
        """pid → 唯一台账记录。返回 (记录|None, 判定码)。

        判定码：``ok`` 唯一命中 / ``unledgered`` 台账无此 pid /
        ``ambiguous_pid_reuse`` 多条记录且时间窗无法定唯一（pid 复用跨观测点）——
        后两者调用方**不得**下归因判（宁缺勿错）。
        """
        recs = self.records_for_pid(pid)
        if not recs:
            return None, "unledgered"
        if len(recs) == 1:
            return recs[0], "ok"
        if at_ts is not None:  # 多记录=pid 复用嫌疑：只在时间窗能定唯一时下判
            live = [r for r in recs if r.spawned_at <= at_ts and (r.exited_at is None or r.exited_at >= at_ts)]
            if len(live) == 1:
                return live[0], "ok"
        return None, "ambiguous_pid_reuse"

    def live_span(self, pid: int) -> tuple[float | None, float | None]:
        """该 pid 的台账寿命区间 (spawned_at, exited_at)；多记录/无记录 → (None, None)。"""
        recs = self.records_for_pid(pid)
        if len(recs) != 1:
            return None, None
        return recs[0].spawned_at, recs[0].exited_at


def _norm_family(raw: str) -> str:
    """台账 name/owner → 比较用规范形（kebab/camel → snake，小写）。"""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(raw or ""))
    return re.sub(r"[^0-9a-z]+", "_", s.lower()).strip("_")


def task_ids_for_record(rec: IncubationRecord, known_task_ids: Iterable[str]) -> list[str]:
    """台账记录 → 注册表候选 task_id（**机械命名约定推导，无实体清单副本**）。

    name/owner 规范化后与 task_id 去前缀形比对（`ollama-serve` → `ollama_serve` ↔
    `sch_ollama_serve`）。两侧同规范化（_norm_family）→ 匹配对大小写/连字符不敏感：
    注册表若出现非 snake_case 的 task_id，不做归一化就会 0 命中，被误判成"画像不认得
    →移交补画像"，那是静默漏归因（比错归因隐蔽）。
    返回升序候选：0=台账认得但画像不认得（移交补画像），≥2=一名多实体（歧义，调用方不判）。
    """
    fams = {f for f in (_norm_family(rec.name), _norm_family(rec.owner)) if f}
    if not fams:
        return []
    hits: set[str] = set()
    for tid in known_task_ids:
        t = str(tid)
        raws = {t}
        for pref in TASK_ID_PREFIXES:
            if t.startswith(pref):
                raws.add(t[len(pref):])
        stems = {f for f in (_norm_family(r) for r in raws) if f}
        if fams & stems:
            hits.add(t)
    return sorted(hits)


class ResourceSampler:
    """零侵入进程采样器：观察→记样本→实测回写画像（reaper 兄弟式）。

    Args:
        registry_path: 注册表路径；None 走 registry_path()（环境变量可重定向）。
        samples_dir: 样本流目录；None 走 samples_dir()。
        patterns: task_id → cmdline 正则注入（E2E 探针主通道）；None 时自动推导。
        scanner: 进程快照函数注入（测试 stub 主通道，测试禁真启重活进程）。
            签名 -> list[dict]，每 dict 含 pid/cmdline(str)/create_time/cpu_time_seconds。
        now_fn: 时间函数注入（时钟回拨红蓝测试用）。
        ledger: L-1 孵化台账注入（单测合成 fixture 主通道）；None 时按 ledger_path 懒加载。
        ledger_path: L-1 台账路径覆盖（None 走 ledger_path()，环境变量 ENV_LEDGER 可重定向）。
    """

    def __init__(
        self,
        registry_path: str | Path | None = None,
        samples_dir: str | Path | None = None,
        patterns: dict[str, str] | None = None,
        scanner: Callable[[], list[dict]] | None = None,
        now_fn: Callable[[], float] | None = None,
        ledger: "IncubationLedger | None" = None,
        ledger_path: str | Path | None = None,
    ):
        self._registry_path = Path(registry_path) if registry_path else None
        self._samples_dir = Path(samples_dir) if samples_dir else None
        self._patterns_override = patterns
        self._scanner = scanner
        self._now_fn = now_fn or time.time
        self._ledger_injected = ledger
        self._ledger_path_override = Path(ledger_path) if ledger_path else None
        self._ledger_cache: IncubationLedger | None = None

    # ── L-1 孵化台账 ──

    def ledger(self) -> IncubationLedger:
        """本轮归因用的孵化台账（懒加载一次；注入优先；读不动=空账本降级不抛）。"""
        if self._ledger_injected is not None:
            return self._ledger_injected
        if self._ledger_cache is None:
            self._ledger_cache = IncubationLedger.load(
                self._ledger_path_override if self._ledger_path_override else None)
        return self._ledger_cache

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
                # 共享宿主槽位：默认不观测（按宿主 RSS 逐槽回填=N 倍计数）。L-1 台账 join
                # 若真给出该槽位 child_pid 则归因成功，scan_once 会把它从本清单摘掉。
                host_shared.append(tid)
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

    def attributable_task_ids(self, entities: list[dict]) -> set[str]:
        """可归因实体全集（退役者永不归因——retired 实体不该有 measured 增量）。"""
        return {str(e.get("task_id")) for e in entities
                if isinstance(e, dict) and e.get("task_id")
                and str(e.get("status") or "active") != "retired"}

    def _ledger_attribution(self, procs: list[dict], ts: float, known: set[str]
                            ) -> tuple[dict[int, tuple[str, IncubationRecord]], dict[int, str]]:
        """L-1 台账侧归因：pid → (task_id, 记录)；另返回 pid → 歧义原因。

        只在**唯一命中**时下判：台账无此 pid / 多记录且时间窗定不了唯一（pid 复用）/
        一个台账家族对上多个实体 —— 全部进歧义表，绝不写样本。
        """
        ledger = self.ledger()
        hits: dict[int, tuple[str, IncubationRecord]] = {}
        ambiguous: dict[int, str] = {}
        if not len(ledger):
            return hits, ambiguous
        for p in procs:
            pid = int(p["pid"])
            rec, code = ledger.attribute_pid(pid, ts)
            if code != "ok" or rec is None:
                if code == "ambiguous_pid_reuse":
                    ambiguous[pid] = code
                continue
            cands = [t for t in task_ids_for_record(rec, known) if t in known]
            if len(cands) == 1:
                hits[pid] = (cands[0], rec)
            elif len(cands) > 1:
                ambiguous[pid] = f"multi_entity:{'|'.join(cands)}"
        return hits, ambiguous

    def scan_once(self, now: float | None = None) -> dict:
        """一轮扫描：命中实体记样本 append JSONL。返回摘要（供日志/测试断言）。"""
        ts = now if now is not None else self._now_fn()
        entities = self.load_entities()
        patterns, host_shared = self.derive_patterns(entities)
        procs = self._scanner() if self._scanner else self._ps_snapshot()
        # 证据链①：cmdline 正则（一进程多命中取先登记实体，确定性=按注册表顺序）
        pattern_hit: dict[int, str] = {}
        for tid, pat in patterns.items():
            for p in procs:
                if pat.search(p["cmdline"]):
                    pattern_hit.setdefault(p["pid"], tid)
        # 证据链②（L-1）：孵化台账 pid join
        known = self.attributable_task_ids(entities)
        ledger_hit, ledger_ambiguous = self._ledger_attribution(procs, ts, known)

        matched_pids: dict[int, tuple[str, str, IncubationRecord | None]] = {}
        ambiguous: dict[int, str] = dict(ledger_ambiguous)
        for pid in sorted(set(pattern_hit) | set(ledger_hit)):
            ptid = pattern_hit.get(pid)
            lh = ledger_hit.get(pid)
            if ptid and lh:
                if ptid == lh[0]:
                    matched_pids[pid] = (ptid, "pattern+ledger", lh[1])
                else:
                    # 两条独立证据链互指不同实体=必有一条错，不猜（写错比不写危险）
                    ambiguous[pid] = f"chain_conflict:pattern={ptid}/ledger={lh[0]}"
            elif ptid:
                matched_pids[pid] = (ptid, "pattern", None)
            elif lh:
                matched_pids[pid] = (lh[0], "ledger", lh[1])
        # 槽位经台账真给出 pid 才算解锁，其余仍留 host_shared_skipped（不假装归因）
        attributed_tids = {tid for tid, _src, _r in matched_pids.values()}
        host_shared = [t for t in host_shared if t not in attributed_tids]

        written: dict[str, int] = {}
        by_source: dict[str, int] = {}
        for p in procs:
            hit = matched_pids.get(int(p["pid"]))
            if hit is None:
                continue
            tid, source, rec = hit
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
                attribution=source,
                ledger_record_id=(rec.record_id if rec is not None else None),
                parent_pid=(rec.parent_pid if rec is not None else None),
            )
            self._append_sample(sample)
            written[tid] = written.get(tid, 0) + 1
            by_source[source] = by_source.get(source, 0) + 1
        summary = {
            "ts": ts,
            "scanned_processes": len(procs),
            "observable_tasks": sorted(patterns),
            "host_shared_skipped": host_shared,
            "samples_written": written,
            # L-1 观测面：归因来源分布 + 歧义明细（歧义必须可见，不得静默丢样本）
            "attribution_sources": dict(sorted(by_source.items())),
            "ambiguous_pids": {str(k): v for k, v in sorted(ambiguous.items())},
            "ledger_records": len(self.ledger()),
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
                        attribution=(obj.get("attribution") or None),
                        ledger_record_id=(obj.get("ledger_record_id") or None),
                        parent_pid=(int(obj["parent_pid"]) if obj.get("parent_pid") is not None else None),
                    )
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                bad += 1
        return out, bad

    # ── 实测回写 ──

    def _no_sample_reason(self, e: dict) -> str | None:
        """零样本实体的**如实**原因（写 measured.no_sample_reason_zh，绝不编造数值）。

        只给 active 实体记原因：planned=画像在册未排产、retired=已退役，两者的零样本由
        status 字段自证，再写一遍反而是噪音。
        """
        if str(e.get("status") or "active") != "active":
            return None
        src = str(e.get("schedule_truth_source") or "").replace("\\", "/").lower()
        if src.endswith("schedule.yaml"):
            return ("无槽位级 pid：schedule.yaml 槽位跑在 DataScheduler 单进程内（APScheduler 线程），"
                    "进程表无独立 pid；按宿主 RSS 逐槽回填=N 倍重复计数宿主，"
                    "L-1 台账 join 亦未给出该槽位记录，故 measured 留 null（禁编造）")
        if src.endswith(".ps1"):
            return "本轮进程表无匹配进程：ps1 真源在册但该班次未被触发（或采样间隔内已退出）"
        return "本轮进程表无匹配进程：无可观测真源模式（手动/事件实体须等下一次手动触发）"

    def writeback(
        self,
        task_ids: list[str] | None = None,
        margin_pct: float = DEFAULT_MEM_MARGIN_PCT,
        duration_percentile: float = DEFAULT_DURATION_PERCENTILE,
        record_no_sample_reason: bool = True,
    ) -> dict:
        """实测回写注册表 measured.*（CAS 只动 measured 段；人填字段零触碰）。

        memory = 实测 max × (1+margin%)（尖刺负载不取分位数，方案 §2.2 裁决）；
        duration = elapsed P90。零样本实体**不写数值**（禁编造），但 active 者在
        measured.no_sample_reason_zh 留如实原因：`updated` 只装真写了实测数值的实体，
        纯原因写入记在 `noted`——两键分开，"零样本跳过实测"的既有契约不破。
        """
        p = self._reg_path()
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        entities = list(data.get("entities") or [])
        updated: dict[str, dict] = {}
        noted: dict[str, str] = {}
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
                if not record_no_sample_reason:
                    continue
                reason = self._no_sample_reason(e)
                measured = e.get("measured") if isinstance(e.get("measured"), dict) else {}
                if reason and measured.get("no_sample_reason_zh") != reason:
                    # 形状稳定：数值键一律显式为 null/0（禁编造），"为什么 null" 走最后一格。
                    # 非生成器手写的表（人手工/测试）没有 measured 骨架时，这里补齐，
                    # 免得读表人只看到一个光秃秃的原因串。已有值原样保留（合并保全）。
                    skeleton = {"peak_mem_gb": None, "p90_duration_min": None,
                                "samples": 0, "last_at": None}
                    merged = {**skeleton, **{k: v for k, v in measured.items()
                                             if k != "no_sample_reason_zh"}}
                    merged["no_sample_reason_zh"] = reason
                    e["measured"] = merged
                    noted[tid] = reason
                continue
            mem_max = max(s.process_resident_bytes for s in samples)
            p90 = _percentile([s.process_elapsed_seconds for s in samples], duration_percentile)
            measured = e.get("measured") if isinstance(e.get("measured"), dict) else {}
            measured["peak_mem_gb"] = round((mem_max / (1024**3)) * (1 + margin_pct / 100.0), 4)
            measured["p90_duration_min"] = int(round(p90 / 60.0))
            measured["samples"] = len(samples)
            measured["last_at"] = _utc_now_iso()
            measured.pop("no_sample_reason_zh", None)  # 有实测=清掉陈旧的"为何没实测"解释
            e["measured"] = measured
            updated[tid] = dict(measured)
        if updated or noted:
            data["entities"] = entities
            new_text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120)
            old_text = p.read_text(encoding="utf-8") if p.exists() else ""
            # 文件头注释块保全：YAML 重序列化会丢头部注释——writeback 只拥有 measured
            # 段，无权重写文件身份声明（GENERATED 头是生成器红线，2026-09-16 实证
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
        return {"updated": updated, "noted": noted, "registry": str(p)}

    # ── L-1 申报寿命 vs 实测寿命 偏差对账（P5 p90 校准器的数据面）──

    def _ledger_groups_by_entity(self, known: set[str]) -> dict[str, list[IncubationRecord]]:
        """台账记录 → 实体分组（唯一归因才入组；歧义记录直接不入，与扫描侧同纪律）。"""
        groups: dict[str, list[IncubationRecord]] = {}
        for rec in self.ledger().records:
            cands = [t for t in task_ids_for_record(rec, known) if t in known]
            if len(cands) == 1:
                groups.setdefault(cands[0], []).append(rec)
        return groups

    def lifetime_deviation_report(
        self,
        task_ids: list[str] | None = None,
        duration_percentile: float = DEFAULT_DURATION_PERCENTILE,
        tolerance_pct: float = DEFAULT_DEVIATION_TOLERANCE_PCT,
        include_no_evidence: bool = False,
    ) -> list[dict]:
        """申报寿命 vs 实测寿命 对账（函数级 API 供 P5 校准器复用，本模块不做 UI）。

        三条独立证据轴，逐轴**如实**记取到的与取不到的：
        - A 申报：注册表 ``est_duration_min``（人填初值，闸的区间数学就吃它）；
        - B 实测：样本流 ``process_elapsed_seconds`` 的 P90 —— 直接从流重算，**不依赖
          writeback 是否跑过**（校准器要能在任何时刻取到当前事实）；
        - C 台账：``expected_lifetime_s``（孵化池申报寿命）vs ``exited_at-spawned_at``
          （实测寿命）；仍存活无 exited_at 时按**下界**处理（``*_alive_ge``），不拿
          "还活着"编造成"跑了这么久"。

        direction 语义：``underdeclared``=实测>申报（低估，班次会压到下一班）、
        ``overdeclared``=实测<申报（高估，白占预算）、``match``=容差内、
        ``no_evidence``=申报/实测缺一。
        """
        entities = self.load_entities()
        known = self.attributable_task_ids(entities)
        groups = self._ledger_groups_by_entity(known)
        rows: list[dict] = []
        for e in entities:
            if not isinstance(e, dict):
                continue
            tid = str(e.get("task_id") or "")
            if not tid or (task_ids is not None and tid not in task_ids):
                continue
            samples, _bad = self.read_samples(tid)
            declared = e.get("est_duration_min")
            declared_min = float(declared) if declared is not None else None
            measured_min = (round(_percentile([s.process_elapsed_seconds for s in samples],
                                               duration_percentile) / 60.0, 1)
                            if samples else None)
            recs = groups.get(tid) or []
            led_exp = [r.expected_lifetime_s / 60.0 for r in recs if r.expected_lifetime_s]
            led_act = [r.actual_lifetime_s / 60.0 for r in recs if r.actual_lifetime_s is not None]
            led_alive = [max(0.0, self._now_fn() - r.spawned_at) / 60.0
                         for r in recs if r.exited_at is None and r.spawned_at > 0]
            evidence: list[str] = []
            if samples:
                evidence.append("samples")
            if recs:
                evidence.append("ledger")
            deviation_min: float | None = None
            deviation_pct: float | None = None
            direction = "no_evidence"
            if declared_min is not None and measured_min is not None:
                deviation_min = round(measured_min - declared_min, 1)
                deviation_pct = (round(deviation_min / declared_min * 100.0, 1)
                                 if declared_min > 0 else None)
                if deviation_pct is None or abs(deviation_min) <= (declared_min * tolerance_pct / 100.0):
                    direction = "match"
                elif deviation_min > 0:
                    direction = "underdeclared"
                else:
                    direction = "overdeclared"
            elif declared_min is None and measured_min is not None:
                direction = "undeclared"  # 有实测无申报=校准器最该补的洞
            row = {
                "task_id": tid,
                "status": str(e.get("status") or "active"),
                "declared_est_duration_min": declared_min,
                "measured_p90_duration_min": measured_min,
                "deviation_min": deviation_min,
                "deviation_pct": deviation_pct,
                "direction": direction,
                "tolerance_pct": tolerance_pct,
                "samples": len(samples),
                "ledger_records": len(recs),
                "ledger_expected_lifetime_min": (round(max(led_exp), 1) if led_exp else None),
                "ledger_actual_lifetime_min": (round(max(led_act), 1) if led_act else None),
                "ledger_actual_lifetime_min_alive_ge": (round(max(led_alive), 1) if led_alive else None),
                "ledger_expected_vs_actual_min": (round(max(led_act) - max(led_exp), 1)
                                                  if led_act and led_exp else None),
                "evidence": evidence,
                "attribution_sources": sorted({str(s.attribution or "pattern") for s in samples}),
                "confidence": ("high" if len(samples) >= 3 else "low") if samples else (
                    "ledger_only" if recs else "none"),
            }
            if evidence or include_no_evidence:  # 有任一证据轴才出行（全量清扫由旗标显式要）
                rows.append(row)
        return rows

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
    w.add_argument("--no-reasons", action="store_true",
                   help="不给零样本实体写 measured.no_sample_reason_zh（只回写实测数值）")
    d = sub.add_parser("deviations", help="L-1 申报寿命 vs 实测寿命 偏差对账（JSON，供 P5 校准器复用）")
    d.add_argument("--tasks", default="", help="逗号分隔 task_id 限列")
    d.add_argument("--tolerance", type=float, default=DEFAULT_DEVIATION_TOLERANCE_PCT,
                   help=f"match 容差百分比（默认 {DEFAULT_DEVIATION_TOLERANCE_PCT}）")
    d.add_argument("--all", action="store_true", help="含零证据实体（全量清扫）")
    args = ap.parse_args()
    sampler = ResourceSampler()
    if args.cmd == "scan":
        if args.loop:
            sampler.run_loop(interval_s=args.interval, max_cycles=args.max_cycles)
        else:
            print(json.dumps(sampler.scan_once(), ensure_ascii=False))
        return 0
    if args.cmd == "deviations":
        rows = sampler.lifetime_deviation_report(
            task_ids=[t for t in args.tasks.split(",") if t] or None,
            tolerance_pct=args.tolerance, include_no_evidence=args.all)
        print(json.dumps({"total": len(rows), "rows": rows}, ensure_ascii=False, indent=2))
        return 0
    out = sampler.writeback(task_ids=[t for t in args.tasks.split(",") if t] or None,
                            record_no_sample_reason=not args.no_reasons)
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
