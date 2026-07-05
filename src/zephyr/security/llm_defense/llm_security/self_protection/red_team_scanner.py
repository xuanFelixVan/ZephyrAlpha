# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.self_protection.red_team_scanner
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.gateway; zephyr.security.llm_defense.llm_security.payloads.__init__; zephyr.security.llm_defense.llm_security.protocol
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_red_team_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

import asyncio
import threading
import time
from collections import defaultdict
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway
from zephyr.security.llm_defense.llm_security.gateway import ScanMode as GWScanMode
from zephyr.security.llm_defense.llm_security.payloads import load_red_team_payloads
from zephyr.security.llm_defense.llm_security.protocol import SecurityDecision
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界


class ScanMode(str, Enum):
    QUICK = "quick"
    FULL = "full"
    ADVERSARIAL = "adversarial"


class ScanTarget(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    BOTH = "both"


class PayloadResult(BaseModel):
    payload_id: str
    name: str
    category: str
    severity: str
    variant: str
    decision: str
    blocked: bool
    reason: str = ""
    latency_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class ScanReport(BaseModel):
    scan_id: str = ""
    mode: str = ScanMode.FULL.value
    target: str = ScanTarget.BOTH.value
    total_payloads: int = 0
    total_variants: int = 0
    blocked: int = 0
    allowed: int = 0
    errors: int = 0
    block_rate_pct: float = 0.0
    avg_latency_ms: float = 0.0
    by_category: dict[str, dict[str, int]] = Field(default_factory=dict)
    by_severity: dict[str, dict[str, int]] = Field(default_factory=dict)
    failures: list[PayloadResult] = Field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    duration_seconds: float = 0.0


class RedTeamScanner:
    """L7 Red Team 对抗扫描器.

    功能:
    - 加载 red-team-payloads.yaml 中的 200+ 攻击载荷
    - 三种扫描模式: quick（采样）/ full（全量）/ adversarial（迭代变异）
    - 每个载荷通过 LSG 网关输入侧、输出侧或双向验证
    - 按 OWASP LLM01-LLM10 分类统计阻断率
    - 按严重级别（critical/high/medium/low）统计覆盖率
    - 发现漏过（allowed）载荷 → 自动登记到 failures 列表
    - 生成结构化 ScanReport 供 CI/Gate 消费
    """

    _PAYLOADS_CACHE: dict[str, Any] | None = None
    _CACHE_LOCK = threading.Lock()

    def __init__(self, mode: ScanMode = ScanMode.FULL, target: ScanTarget = ScanTarget.INPUT):
        self._mode = mode
        self._target = target
        self._results: list[PayloadResult] = []
        self._lock = threading.Lock()
        self._started_at: float = 0.0
        self._completed_at: float = 0.0

    @classmethod
    def _load_payloads(cls) -> dict[str, Any]:
        with cls._CACHE_LOCK:
            if cls._PAYLOADS_CACHE is None:
                cls._PAYLOADS_CACHE = load_red_team_payloads()
            return cls._PAYLOADS_CACHE

    def run(self) -> ScanReport:
        self._started_at = time.time()
        payloads_data = self._load_payloads()
        payloads = payloads_data.get("payloads", [])

        if self._mode is ScanMode.QUICK:
            payloads = self._sample_payloads(payloads, max_per_category=3)

        total_payloads = len(payloads)
        total_variants = 0
        gateway = LSGSecurityGateway()

        variants_to_scan: list[tuple] = []
        for entry in payloads:
            variant_list = entry.get("variants", [])
            if not variant_list:
                continue
            subset = variant_list[:2] if self._mode is ScanMode.QUICK else variant_list
            for variant in subset:
                variants_to_scan.append((entry, variant))

        total_variants = len(variants_to_scan)
        total_scanned = total_variants

        async def _run_all():
            input_results = []
            output_results = []
            if self._target in (ScanTarget.INPUT, ScanTarget.BOTH):
                input_variants = [(e, v) for e, v in variants_to_scan]
                input_results = await self._scan_input_batch(gateway, input_variants)
            if self._target in (ScanTarget.OUTPUT, ScanTarget.BOTH):
                output_variants = [(e, v) for e, v in variants_to_scan]
                output_results = await self._scan_output_batch(gateway, output_variants)
            return input_results, output_results

        try:
            asyncio.get_running_loop()
            has_loop = True
        except RuntimeError:
            has_loop = False

        if has_loop:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(lambda: run_sync(_run_all()))
                input_results, output_results = future.result()
        else:
            input_results, output_results = run_sync(_run_all())

        with self._lock:
            self._results.extend(input_results)
            self._results.extend(output_results)

        if self._target is ScanTarget.BOTH:
            total_scanned = total_variants * 2

        self._completed_at = time.time()
        return self._build_report(total_payloads, total_scanned)

    async def _scan_input_batch(self, gateway: LSGSecurityGateway, variants: list[tuple]) -> list[PayloadResult]:
        results: list[PayloadResult] = []
        for entry, variant in variants:
            t0 = time.time()
            try:
                scan_result = await gateway.scan_input(
                    variant,
                    source="red_team_scanner",
                    metadata={"request_id": f"rt_{entry.get('id', 'unknown')}"},
                    mode=GWScanMode.INPUT_ONLY,
                )
                blocked = scan_result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK)
                pr = PayloadResult(
                    payload_id=entry.get("id", "unknown"),
                    name=entry.get("name", "unknown"),
                    category=entry.get("category", "unknown"),
                    severity=entry.get("severity", "medium"),
                    variant=variant[:200],
                    decision=scan_result.decision.value,
                    blocked=blocked,
                    reason=scan_result.blocked_by or "scanned",
                    latency_ms=(time.time() - t0) * 1000,
                )
            except Exception as e:
                pr = PayloadResult(
                    payload_id=entry.get("id", "unknown"),
                    name=entry.get("name", "unknown"),
                    category=entry.get("category", "unknown"),
                    severity=entry.get("severity", "medium"),
                    variant=variant[:200],
                    decision="error",
                    blocked=False,
                    reason=str(e)[:500],
                    latency_ms=(time.time() - t0) * 1000,
                )
            results.append(pr)
        return results

    async def _scan_output_batch(self, gateway: LSGSecurityGateway, variants: list[tuple]) -> list[PayloadResult]:
        results: list[PayloadResult] = []
        for entry, variant in variants:
            t0 = time.time()
            try:
                scan_result = await gateway.scan_output(
                    variant,
                    source="red_team_scanner",
                    metadata={"request_id": f"rt_{entry.get('id', 'unknown')}"},
                    mode=GWScanMode.OUTPUT_ONLY,
                )
                blocked = scan_result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK)
                pr = PayloadResult(
                    payload_id=entry.get("id", "unknown"),
                    name=entry.get("name", "unknown"),
                    category=entry.get("category", "unknown"),
                    severity=entry.get("severity", "medium"),
                    variant=variant[:200],
                    decision=scan_result.decision.value,
                    blocked=blocked,
                    reason=scan_result.blocked_by or "scanned",
                    latency_ms=(time.time() - t0) * 1000,
                )
            except Exception as e:
                pr = PayloadResult(
                    payload_id=entry.get("id", "unknown"),
                    name=entry.get("name", "unknown"),
                    category=entry.get("category", "unknown"),
                    severity=entry.get("severity", "medium"),
                    variant=variant[:200],
                    decision="error",
                    blocked=False,
                    reason=str(e)[:500],
                    latency_ms=(time.time() - t0) * 1000,
                )
            results.append(pr)
        return results

    def _build_report(self, total_payloads: int, total_variants: int) -> ScanReport:
        blocked = sum(1 for r in self._results if r.blocked)
        allowed = sum(1 for r in self._results if not r.blocked and r.decision != "error")
        errors = sum(1 for r in self._results if r.decision == "error")
        block_rate = (blocked / max(total_variants, 1)) * 100
        avg_latency = sum(r.latency_ms for r in self._results) / max(len(self._results), 1)

        by_category: dict[str, dict[str, int]] = defaultdict(lambda: {"blocked": 0, "allowed": 0, "total": 0})
        by_severity: dict[str, dict[str, int]] = defaultdict(lambda: {"blocked": 0, "allowed": 0, "total": 0})
        failures: list[PayloadResult] = []

        for r in self._results:
            cat = r.category
            by_category[cat]["blocked"] += 1 if r.blocked else 0
            by_category[cat]["allowed"] += 0 if r.blocked else (1 if r.decision != "error" else 0)
            by_category[cat]["total"] += 1

            sev = r.severity
            by_severity[sev]["blocked"] += 1 if r.blocked else 0
            by_severity[sev]["allowed"] += 0 if r.blocked else (1 if r.decision != "error" else 0)
            by_severity[sev]["total"] += 1

            if not r.blocked and r.decision != "error":
                failures.append(r)

        return ScanReport(
            scan_id=f"rt_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            mode=self._mode.value,
            target=self._target.value,
            total_payloads=total_payloads,
            total_variants=total_variants,
            blocked=blocked,
            allowed=allowed,
            errors=errors,
            block_rate_pct=round(block_rate, 2),
            avg_latency_ms=round(avg_latency, 2),
            by_category=dict(by_category),
            by_severity=dict(by_severity),
            failures=failures,
            started_at=datetime.fromtimestamp(self._started_at, tz=UTC).isoformat(),
            completed_at=datetime.fromtimestamp(self._completed_at, tz=UTC).isoformat(),
            duration_seconds=round(self._completed_at - self._started_at, 3),
        )

    @staticmethod
    def _sample_payloads(payloads: list[dict], max_per_category: int) -> list[dict]:
        seen: dict[str, int] = defaultdict(int)
        sampled: list[dict] = []
        for p in payloads:
            cat = p.get("category", "unknown")
            if seen[cat] < max_per_category:
                sampled.append(p)
                seen[cat] += 1
        return sampled

    @property
    def results(self) -> list[PayloadResult]:
        return list(self._results)

    @property
    def mode(self) -> ScanMode:
        return self._mode

    @property
    def target(self) -> ScanTarget:
        return self._target
