# [A_module] module_id=MOD-INF-PROC-INCUBATOR | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-PROC-INCUBATOR | docs/03_modules/_cross_layer/process_incubator/blueprint.md | §
# [MODULE] zephyr.shared.infra.process_incubator
# [INVARIANTS] 孵化必登记（父 PID/预期寿命/进程树缺一不可）; 登记先于返回（spawn 成功即落盘，失败不落）; 水位 emergency 拒绝/queue 线有界等待; 登记表 fail-safe（ledger 故障不阻断 spawn 本体但必须告警）; ledger 目录可注入（测试隔离禁写生产路径）
# [MODIFY-GUARD] process_pool.spawn_python_hidden 接口变更须同步本模块; config/resource_optimization.yaml 阈值键名
# [CONSUMERS] zephyr.trading.auto_runtime_core（ollama serve）; zephyr.frontend.dashboard.services_registry（服务孵化）; zephyr.governance.audit.reconcile_runner; zephyr.gov_enforcement.rule_bridge.write_audit_daemon; zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog; zephyr.trading.process_reaper（M3 收割端读 ledger）
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] WaterLevelRejected; OSError; yaml.YAMLError
# [TESTS] tests/shared/test_process_incubator.py
# [TTL] permanent

"""ProcessIncubator — 统一进程孵化入口（治理战役 M1+M2，2026-09-16）。

背景（治理挖矿地图 §4 发现 2/3 + 9-15 事故）：process_pool（孵化）与
ProcessLifecycleGateway 双轨并存、孵化不收割；9-15 事故 9 个孤儿 llama-server
≈12GB 即 detached 孵化无登记无收割的结构性缺口。本模块=统一孵化前门：

1. **孵化即登记（M1）**：每次 spawn 落盘一条登记（child_pid/parent_pid/祖先链/
   name/cmd/spawned_at/expected_lifetime_s/owner）到
   ``.runtime/process_incubator/ledger.jsonl``（safe_write_text CAS）。
   登记表=reaper（M3）收割依据，替代 cmdline 特征猜测。
2. **水位门禁（M2）**：spawn 前查内存水位（Windows=commit charge percent，
   其余=RAM percent）——≥ queue_at（85%，战役口径）→ 有界等待重试；≥ reject_at
   （引用 config/resource_optimization.yaml memory_emergency_percent，勿收编）
   → 抛 WaterLevelRejected。YAML 缺席→缺省 85/90。
3. **兼容迁移面**：``spawn_registered`` 与 process_pool.spawn_python_hidden
   同签名（附登记参数，全部有缺省）——消费方仅改 import 行即完成迁移。

进程树语义：parent_pid=os.getpid()（孵化时刻）；ancestor_chain=自父上溯至
进程树根的 pid 链（psutil，上限 16 跳防循环）；树根=root_pid。

边界：不替代 MCPProcessPool 池化语义（长驻复用进程仍走 pool）；不改
ProcessLifecycleGateway（其消费方渐进迁移至本模块）；收割本体在 reaper（M3）。
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

from zephyr.shared.io.file_utils import safe_write_text, content_sha256
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

LEDGER_DIRNAME = "process_incubator"
LEDGER_FILENAME = "ledger.jsonl"

# 水位门禁缺省（战役 M2 口径 85%；reject 线引用 resource_optimization.yaml
# memory_emergency_percent——仅引用不收编，YAML 缺席时 90 兜底）
DEFAULT_QUEUE_AT_PERCENT = 85.0
DEFAULT_REJECT_AT_PERCENT = 90.0
WATER_GATE_WAIT_S = 30.0
WATER_GATE_RETRY_INTERVAL_S = 5.0

# 祖先链上溯上限（防 pid 复用循环）
_MAX_ANCESTOR_HOPS = 16


def ledger_dir() -> Path:
    """登记表目录：环境变量可重定向（测试隔离主通道），缺省生产 .runtime 路径。"""
    env = os.environ.get("ZEPHYR_INCUBATOR_LEDGER_DIR", "")
    if env:
        return Path(env)
    return REPO_ROOT / ".runtime" / LEDGER_DIRNAME


@dataclass
class IncubationRecord:
    """一条孵化登记：进程树 + 预期寿命 + 命令面。"""

    record_id: str
    child_pid: int
    parent_pid: int
    root_pid: int
    ancestor_chain: list[int] = field(default_factory=list)
    name: str = ""
    cmd: str = ""
    spawned_at: float = 0.0
    expected_lifetime_s: float = 600.0
    owner: str = ""
    exited_at: float | None = None
    exit_code: int | None = None
    reaped: bool = False

    def expires_at(self) -> float:
        return self.spawned_at + self.expected_lifetime_s

    def is_expired(self, now: float | None = None) -> bool:
        ts = now if now is not None else time.time()
        return ts > self.expires_at()


def _ancestor_chain() -> tuple[list[int], int]:
    """自当前进程上溯祖先 pid 链（psutil 缺席降级为仅自身）。返回 (chain, root)。"""
    me = os.getpid()
    chain = [me]
    root = me
    try:
        import psutil

        proc = psutil.Process(me)
        for _ in range(_MAX_ANCESTOR_HOPS):
            parent = proc.parent()
            if parent is None:
                break
            chain.append(parent.pid)
            root = parent.pid
            proc = parent
    except Exception:  # noqa: BLE001 — 登记信息尽力而为，绝不阻断孵化
        logger.debug("ancestor_chain degraded", exc_info=True)
    return chain, root


def memory_water_percent() -> float:
    """内存水位百分比：Windows=commit charge（psutil.swap_memory=页文件+RAM 提交量，
    即 9-15 事故"commit 71.2/79.9GB"口径）；其余平台=物理内存 percent。"""
    try:
        import psutil

        if os.name == "nt":
            return float(psutil.swap_memory().percent)
        return float(psutil.virtual_memory().percent)
    except Exception:  # noqa: BLE001 — 探测失败=按无水位压力放行（fail-open，门禁不误杀）
        logger.debug("memory_water_percent probe failed", exc_info=True)
        return 0.0


def load_reject_threshold() -> float:
    """引用 config/resource_optimization.yaml 的 memory_emergency_percent（勿收编）。"""
    try:
        import yaml

        p = REPO_ROOT / "config" / "resource_optimization.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        value = (data.get("pressure_thresholds") or {}).get("memory_emergency_percent")
        return float(value) if value is not None else DEFAULT_REJECT_AT_PERCENT
    except (OSError, yaml.YAMLError, ValueError, TypeError):
        return DEFAULT_REJECT_AT_PERCENT


class WaterLevelRejected(RuntimeError):
    """水位门禁拒绝孵化（emergency 线或等待超时仍超 queue 线）。"""


class SpawnWaterGate:
    """spawn 前水位门禁：queue 线有界等待，reject 线立即拒绝。

    Args:
        queue_at_percent: 排队线（战役口径 85）。
        reject_at_percent: 拒绝线（缺省引用 resource_optimization.yaml emergency 线）。
        wait_s: queue 线上有界等待总时长（超时仍超线=拒绝）。
        probe: 水位探测函数（测试注入点）。
    """

    def __init__(
        self,
        queue_at_percent: float = DEFAULT_QUEUE_AT_PERCENT,
        reject_at_percent: float | None = None,
        wait_s: float = WATER_GATE_WAIT_S,
        retry_interval_s: float = WATER_GATE_RETRY_INTERVAL_S,
        probe=None,
    ):
        self.queue_at = queue_at_percent
        self.reject_at = reject_at_percent if reject_at_percent is not None else load_reject_threshold()
        self.wait_s = wait_s
        self.retry_interval_s = retry_interval_s
        self._probe = probe or memory_water_percent

    def check_or_wait(self) -> float:
        """检查水位：放行返回水位值；queue 线上有界等待；拒绝抛 WaterLevelRejected。"""
        level = self._probe()
        if level >= self.reject_at:
            raise WaterLevelRejected(
                f"water gate reject: memory {level:.1f}% >= reject line {self.reject_at:.1f}%"
            )
        if level < self.queue_at:
            return level
        deadline = time.monotonic() + self.wait_s
        while True:
            logger.warning(
                "water gate queue: memory %.1f%% >= queue line %.1f%%, waiting (deadline %.0fs)",
                level,
                self.queue_at,
                self.wait_s,
            )
            if time.monotonic() >= deadline:
                raise WaterLevelRejected(
                    f"water gate timeout: memory {level:.1f}% still >= queue line "
                    f"{self.queue_at:.1f}% after {self.wait_s:.0f}s wait"
                )
            time.sleep(self.retry_interval_s)
            level = self._probe()
            if level >= self.reject_at:
                raise WaterLevelRejected(
                    f"water gate reject after wait: memory {level:.1f}% >= {self.reject_at:.1f}%"
                )
            if level < self.queue_at:
                return level


class ProcessIncubator:
    """统一孵化入口：水位门禁 → spawn（process_pool）→ 孵化即登记。"""

    def __init__(self, ledger: str | Path | None = None, water_gate: SpawnWaterGate | None = None):
        self._ledger_dir = Path(ledger) if ledger else None
        self._gate = water_gate or SpawnWaterGate()
        self._lock = threading.Lock()

    # ── 登记表 ──

    def _dir(self) -> Path:
        return self._ledger_dir if self._ledger_dir else ledger_dir()

    def _ledger_path(self) -> Path:
        return self._dir() / LEDGER_FILENAME

    def _read(self) -> list[IncubationRecord]:
        p = self._ledger_path()
        if not p.exists():
            return []
        out: list[IncubationRecord] = []
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and obj.get("record_id"):
                    out.append(IncubationRecord(**{k: v for k, v in obj.items() if k in IncubationRecord.__dataclass_fields__}))
            except (json.JSONDecodeError, TypeError, ValueError):
                logger.warning("incubator ledger: skip corrupt line in %s", p)
        return out

    def _write(self, records: list[IncubationRecord]) -> None:
        p = self._ledger_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        content = "".join(json.dumps(asdict(r), ensure_ascii=False) + "\n" for r in records)
        expected = content_sha256(p.read_text(encoding="utf-8")) if p.exists() else None
        safe_write_text(p, content, expected_base_sha256=expected)

    # ── 孵化 ──

    def spawn(
        self,
        cmd: list[str],
        *,
        name: str = "",
        expected_lifetime_s: float = 600.0,
        owner: str = "",
        gate: bool = True,
        **spawn_kwargs,
    ):
        """水位门禁 → spawn_python_hidden → 孵化即登记 → 返回 Popen（或 WMI shim）。

        Args:
            cmd: 命令列表（同 spawn_python_hidden）。
            name: 孵化名（登记用，缺省取 cmd 尾段）。
            expected_lifetime_s: 预期寿命（秒）——reaper 对超寿且仍存活的进程收割（M3）。
                长驻 daemon 显式给大值（如 86400），禁止默认值当长驻用。
            owner: 孵化方标识（模块名/会话 id）。
            gate: False 跳过水位门禁（轻量短命进程可关，登记仍做）。
            **spawn_kwargs: 透传 spawn_python_hidden（cwd/env/stdout_path 等）。

        Returns:
            subprocess.Popen（或 WMI 降级 shim）。

        Raises:
            WaterLevelRejected: 水位门禁拒绝。
        """
        from zephyr.shared.infra.process_pool import spawn_python_hidden

        if gate:
            self._gate.check_or_wait()
        proc = spawn_python_hidden(cmd, **spawn_kwargs)
        chain, root = _ancestor_chain()
        record = IncubationRecord(
            record_id=uuid.uuid4().hex[:12],
            child_pid=proc.pid if proc.pid else -1,
            parent_pid=os.getpid(),
            root_pid=root,
            ancestor_chain=chain,
            name=name or Path(cmd[0] if cmd else "unknown").name,
            cmd=" ".join(str(x) for x in cmd)[:300],
            spawned_at=time.time(),
            expected_lifetime_s=expected_lifetime_s,
            owner=owner,
        )
        try:
            with self._lock:
                records = self._read()
                records.append(record)
                self._write(records)
        except Exception:  # noqa: BLE001 — INVARIANTS：登记失败不阻断孵化本体（StaleWriteRefused
            # 是 RuntimeError 非 OSError，并发 CAS 拒写必须同被吞掉——红蓝对抗 2026-09-16）
            logger.exception("incubator ledger write failed for pid=%s", record.child_pid)
        # reaper keep 自动登记（09-16 W1 取证治本：reaper 误杀 stash 回放中的 worker
        # → 共享区 tracked 修改停留 HEAD 态=大规模"编辑消失"战伤）。孵化即登记
        # keep-list（按 name 子串），幂等；登记失败不阻断孵化。
        try:
            from zephyr.shared.io.paths import anchor_main_root  # noqa: PLC0415

            keep = anchor_main_root(__file__) / "data" / "runtime" / "process_reaper_keep.txt"
            if keep.exists():
                existing = keep.read_text(encoding="utf-8")
                marker = record.name
                if marker and marker not in existing:
                    with keep.open("a", encoding="utf-8") as fh:
                        fh.write(marker + "\n")
        except Exception:  # noqa: BLE001 — keep 登记失败不阻断孵化
            logger.debug("incubator keep-list register skipped", exc_info=True)
        logger.info(
            "incubated pid=%s name=%s lifetime=%ss owner=%s ledger=%s",
            record.child_pid,
            record.name,
            record.expected_lifetime_s,
            record.owner or "-",
            record.record_id,
        )
        return proc

    # ── 对账/查询 ──

    def sweep(self, now: float | None = None) -> int:
        """对账：子进程已退出则打 exited 戳（仅本进程孵化的记录可判）。返回对账条数。

        Windows 禁 os.kill(pid,0) 探活（非 0 信号语义=TerminateProcess 真杀！）
        ——统一 psutil.pid_exists，缺席时跳过对账（fail-safe 不误标）。
        """
        ts = now if now is not None else time.time()
        try:
            import psutil
        except ImportError:
            logger.debug("sweep skipped: psutil unavailable")
            return 0
        with self._lock:
            records = self._read()
            n = 0
            for r in records:
                if r.exited_at is None and r.parent_pid == os.getpid():
                    try:
                        if not psutil.pid_exists(r.child_pid):
                            r.exited_at = ts
                            n += 1
                    except psutil.Error:
                        continue
            if n:
                try:
                    self._write(records)
                except Exception:  # noqa: BLE001 — 并发 CAS 拒写降级（红蓝 2026-09-16）
                    logger.warning("sweep ledger write refused (concurrent writer)")
                    n = 0
            return n

    def list_active(self) -> list[IncubationRecord]:
        """未退出登记（跨进程读——reaper 收割端同源）。"""
        return [r for r in self._read() if r.exited_at is None and not r.reaped]

    def mark_reaped(self, record_id: str) -> bool:
        """收割端（reaper）回写：标记已收割。"""
        with self._lock:
            records = self._read()
            for r in records:
                if r.record_id == record_id:
                    r.reaped = True
                    try:
                        self._write(records)
                    except Exception:  # noqa: BLE001 — 并发 CAS 拒写降级（红蓝 2026-09-16）
                        logger.warning("mark_reaped ledger write refused (concurrent writer)")
                    return True
            return False

    def stats(self) -> dict:
        records = self._read()
        active = [r for r in records if r.exited_at is None and not r.reaped]
        return {
            "total": len(records),
            "active": len(active),
            "expired_active": sum(1 for r in active if r.is_expired()),
            "owners": sorted({r.owner for r in active if r.owner}),
        }


_SINGLETION_LOCK = threading.Lock()
_SINGLETON: ProcessIncubator | None = None


def get_incubator() -> ProcessIncubator:
    """进程级单例（ledger 目录经环境变量可重定向）。"""
    global _SINGLETON
    with _SINGLETION_LOCK:
        if _SINGLETON is None:
            _SINGLETON = ProcessIncubator()
        return _SINGLETON


__all__ = [
    "DEFAULT_QUEUE_AT_PERCENT",
    "DEFAULT_REJECT_AT_PERCENT",
    "IncubationRecord",
    "ProcessIncubator",
    "SpawnWaterGate",
    "WaterLevelRejected",
    "get_incubator",
    "ledger_dir",
    "memory_water_percent",
]
