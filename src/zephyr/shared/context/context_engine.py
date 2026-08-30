# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.context.context_engine
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未注册 slot/非法规则分层/未知调整目标 → ValueError
# [TESTS] tests/context/test_context_engine.py; tests/context/test_context_engine_pipeline.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Context Engine — AI 上下文组装与 Token 预算管理。

依据：
    蓝图 MOD-TASK_SYSTEM §2.2.1 + v0.3.0
    任务卡 TASK-INF-0006 + TASK-INF-0105

功能：
    - context_assembly: 根据 task_id 组装最小上下文
    - token_budget_tracker: 限制 context 不超过 max_tokens
    - pipeline M1-M11 集成验证
    - 支持 context_assembly_manifest 路径索引

蓝图补齐（2026-08-23，MOD-CONTEXT_ENGINE "造了一半"收口）：
    按 _cross_layer/context_engine 蓝图 + _b_track_interfaces/context_engine_interface.md
    补齐轻量核心方法（同步、零重依赖实现，VMS/LLM/MCP 真接线留注入位）：
    - build/compress/validate/inject 四段流水线（slot 语义分槽 + 预算分配 +
      DEGRADE-002 llm_summary→rule_based 降级 + 静态 IDE 能力矩阵路由）
    - register_rules: 三层规则注入（HOT/DOMAIN/COLD，code_dedup W3-8 消费位）
    - adjust_strategy: FLE 反馈通道（slot 预算动态调整 + TTL 到期回默认）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: context_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: max_tokens 参数
#   fields: 参数 max_tokens（无注解）
#   code: context_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: now 参数
#   fields: 参数 now（无注解）
#   code: context_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ContextEngine
#   name_en: ContextEngine
#   intro: class ContextEngine 源码 L116-L549
#   desc: 公共方法（定义序）: budget, max_tokens, project_root, assemble_context, check_token_budget, validate_pipeline_modules,…
#   inputs: project_root max_tokens now
#   outputs: 返回值
#   （注：A1 之后另有 9 个公共定义未列入（含 9 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（10 定义）
#   name_en: public defs
#   intro: ContextEngine
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final

DEFAULT_MAX_TOKENS: Final[int] = 20000


@dataclass
class ContextSlice:
    file_path: str
    content: str
    token_estimate: int
    reason: str


@dataclass
class ContextAssembly:
    task_id: str
    slices: list[ContextSlice]
    total_tokens: int
    max_tokens: int
    budget_remaining: int
    truncated: bool = False


@dataclass
class TokenBudget:
    max_tokens: int
    used_tokens: int
    reserve_tokens: int
    over_budget: bool = False


class ContextEngine:
    CHARS_PER_TOKEN = 4

    def __init__(
        self,
        project_root: Path | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._project_root = project_root or Path.cwd()
        self._max_tokens = max_tokens
        self._budget = TokenBudget(
            max_tokens=max_tokens,
            used_tokens=0,
            reserve_tokens=int(max_tokens * 0.1),
        )
        self._now = now or datetime.now
        self._rules: dict[str, list[ContextRule]] = {tier: [] for tier in RULE_TIERS}
        self._slot_overrides: dict[str, tuple[dict[str, float], datetime]] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def budget(self):
        """只读：budget（Stage 4 公共化）。"""
        return self._budget

    @budget.setter
    def budget(self, value):
        """写入：budget（Stage 4 公共化）。"""
        self._budget = value

    @property
    def max_tokens(self):
        """只读：max_tokens（Stage 4 公共化）。"""
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value):
        """写入：max_tokens（Stage 4 公共化）。"""
        self._max_tokens = value

    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def assemble_context(
        self,
        task_id: str,
        manifest: list[dict[str, str]],
        truncate: bool = True,
    ) -> ContextAssembly:
        slices: list[ContextSlice] = []
        total_tokens = 0
        available = self._budget.max_tokens - self._budget.reserve_tokens

        # 5.106.5 修复: x.get("reason", "") 仅在 key 缺失时返回 default,
        # key 存在但值为 None 时 None 与 str 比较抛 TypeError。改为 `or ""` 兼容 None。
        sorted_manifest = sorted(manifest, key=lambda x: x.get("reason") or "")

        for entry in sorted_manifest:
            file_path = entry.get("file_path", "")
            reason = entry.get("reason", "")

            if not file_path:
                continue

            full_path = self._project_root / file_path
            content = ""
            if full_path.exists():
                content = full_path.read_text(encoding="utf-8")

            token_estimate = len(content) // self.CHARS_PER_TOKEN

            if truncate and total_tokens + token_estimate > available:
                remaining = available - total_tokens
                if remaining > 100:
                    content = content[: remaining * self.CHARS_PER_TOKEN]
                    token_estimate = remaining
                else:
                    break

            total_tokens += token_estimate

            slices.append(
                ContextSlice(
                    file_path=file_path,
                    content=content,
                    token_estimate=token_estimate,
                    reason=reason,
                )
            )

        return ContextAssembly(
            task_id=task_id,
            slices=slices,
            total_tokens=total_tokens,
            max_tokens=self._budget.max_tokens,
            budget_remaining=self._budget.max_tokens - total_tokens,
            truncated=total_tokens > available,
        )

    def check_token_budget(self, content: str) -> TokenBudget:
        token_estimate = len(content) // self.CHARS_PER_TOKEN
        used = self._budget.used_tokens + token_estimate
        over = used > self._budget.max_tokens - self._budget.reserve_tokens

        return TokenBudget(
            max_tokens=self._budget.max_tokens,
            used_tokens=used,
            reserve_tokens=self._budget.reserve_tokens,
            over_budget=over,
        )

    def validate_pipeline_modules(self, module_names: list[str]) -> dict[str, bool]:
        pipeline_map = {
            "M1": "context_assembly",
            "M2": "task_parsing",
            "M3": "validation",
            "M4": "generation",
            "M5": "unit_testing",
            "M6": "integration_testing",
            "M7": "audit_and_coverage",
            "M8": "rollback_preparation",
            "M9": "governance_compliance",
            "M10": "artifact_collection",
            "M11": "journal_checkpoint",
        }

        return {name: name in pipeline_map for name in module_names}

    def estimate_task_tokens(self, task_card: dict[str, Any]) -> int:
        estimated = 0
        manifest = task_card.get("context_assembly_manifest", [])
        for entry in manifest:
            file_path = entry.get("file_path", "")
            full_path = self._project_root / file_path
            if full_path.exists():
                estimated += full_path.stat().st_size // self.CHARS_PER_TOKEN
        return estimated

    # ────────────────────────────────────────────────────────────────
    # 蓝图补齐：四段流水线 build/compress/validate/inject（轻量同步实现）
    # ────────────────────────────────────────────────────────────────

    def build(
        self,
        task_id: str,
        manifest: list[dict[str, str]],
        *,
        slot_overrides: dict[str, float] | None = None,
    ) -> ContextBundle:
        """build 段：按 slot 语义分槽汇聚上下文（文件系统源；VMS 源留注入位）。

        manifest 条目支持 slot 键（缺省 code_refs）；slot 预算 = 生效比例 × 可用额度，
        槽内按 reason 排序累加，超槽预算截断末片。源缺失不阻塞（记 degraded_sources）。
        """
        budgets = dict(self.slot_budgets())
        if slot_overrides:
            for slot, ratio in slot_overrides.items():
                if slot in budgets:
                    budgets[slot] = max(0.0, float(ratio))
        available = self._budget.max_tokens - self._budget.reserve_tokens

        grouped: dict[str, list[dict[str, str]]] = {}
        for entry in manifest:
            slot = entry.get("slot") or "code_refs"
            grouped.setdefault(slot, []).append(entry)

        slots: dict[str, SlotContent] = {}
        total_tokens = 0
        degrade_reasons: list[str] = []

        for slot, entries in grouped.items():
            cap = int(budgets.get(slot, budgets.get("code_refs", 0.3)) * available)
            items: list[ContextSlice] = []
            traces: list[str] = []
            degraded_sources: list[str] = []
            used = 0
            for entry in sorted(entries, key=lambda x: x.get("reason") or ""):
                file_path = entry.get("file_path", "")
                reason = entry.get("reason", "")
                if not file_path:
                    continue
                full_path = self._project_root / file_path
                if full_path.exists():
                    content = full_path.read_text(encoding="utf-8")
                else:
                    content = ""
                    degraded_sources.append(file_path)
                    degrade_reasons.append(f"source_missing: {file_path}")
                tokens = len(content) // self.CHARS_PER_TOKEN
                if used + tokens > cap:
                    remaining = cap - used
                    if remaining > 0 and content:
                        content = content[: remaining * self.CHARS_PER_TOKEN]
                        tokens = remaining
                    else:
                        degrade_reasons.append(f"slot_budget_drop: {file_path}")
                        continue
                used += tokens
                items.append(ContextSlice(file_path=file_path, content=content, token_estimate=tokens, reason=reason))
                traces.append(f"file://{file_path}")
            slots[slot] = SlotContent(
                slot=slot,
                items=items,
                token_count=used,
                source_traces=traces,
                degraded_sources=degraded_sources,
            )
            total_tokens += used

        digest = hashlib.sha256(
            json.dumps({s: [i.file_path for i in c.items] for s, c in slots.items()}, sort_keys=True).encode("utf-8")
        ).hexdigest()
        return ContextBundle(
            request_id=f"ce-{digest[:16]}",
            task_id=task_id,
            slots=slots,
            total_token_count=total_tokens,
            token_budget=self._budget.max_tokens,
            compression_ratio=None,
            bundle_hash=digest,
            degraded=bool(degrade_reasons),
            degrade_reasons=degrade_reasons,
        )

    def compress(
        self,
        bundle: ContextBundle,
        token_budget: int,
        *,
        strategy: str = "rule_based",
    ) -> ContextBundle:
        """compress 段：压到 token_budget 内。llm_summary 无本地 LLM 注入位 →
        DEGRADE-002 降级 rule_based（首尾保留）；仍超 → DEGRADE-002b truncate。"""
        degrade_reasons = list(bundle.degrade_reasons)
        if strategy == "llm_summary":
            degrade_reasons.append("DEGRADE-002: llm_summary 无本地 LLM 接线，降级 rule_based")
            strategy = "rule_based"
        if token_budget <= 0:
            raise ValueError(f"token_budget 必须为正: {token_budget}")

        total = bundle.total_token_count
        if total <= token_budget:
            return ContextBundle(
                request_id=bundle.request_id,
                task_id=bundle.task_id,
                slots=bundle.slots,
                total_token_count=total,
                token_budget=token_budget,
                compression_ratio=1.0,
                bundle_hash=bundle.bundle_hash,
                degraded=bundle.degraded,
                degrade_reasons=degrade_reasons,
            )

        factor = token_budget / total
        new_slots: dict[str, SlotContent] = {}
        new_total = 0
        for slot, content in bundle.slots.items():
            items: list[ContextSlice] = []
            used = 0
            slot_cap = int(content.token_count * factor)
            for item in content.items:
                target = min(item.token_estimate, slot_cap - used)
                if target <= 0:
                    continue
                keep_chars = target * self.CHARS_PER_TOKEN
                text = item.content
                if len(text) > keep_chars and strategy == "rule_based":
                    half = keep_chars // 2
                    text = text[:half] + text[-half:] if half > 0 else text[:keep_chars]
                else:
                    text = text[:keep_chars]
                tokens = len(text) // self.CHARS_PER_TOKEN
                used += tokens
                items.append(
                    ContextSlice(file_path=item.file_path, content=text, token_estimate=tokens, reason=item.reason)
                )
            new_slots[slot] = SlotContent(
                slot=slot,
                items=items,
                token_count=used,
                source_traces=content.source_traces,
                degraded_sources=content.degraded_sources,
            )
            new_total += used

        if new_total > token_budget:
            degrade_reasons.append("DEGRADE-002b: rule_based 仍超预算，执行 truncate")
            overflow = new_total - token_budget
            for slot in reversed(list(new_slots)):
                if overflow <= 0:
                    break
                content = new_slots[slot]
                items = list(content.items)
                while items and overflow > 0:
                    dropped = items.pop()
                    overflow -= dropped.token_estimate
                    new_total -= dropped.token_estimate
                new_slots[slot] = SlotContent(
                    slot=slot,
                    items=items,
                    token_count=sum(i.token_estimate for i in items),
                    source_traces=content.source_traces,
                    degraded_sources=content.degraded_sources,
                )

        return ContextBundle(
            request_id=bundle.request_id,
            task_id=bundle.task_id,
            slots=new_slots,
            total_token_count=new_total,
            token_budget=token_budget,
            compression_ratio=(new_total / total) if total else 1.0,
            bundle_hash=bundle.bundle_hash,
            degraded=True,
            degrade_reasons=degrade_reasons,
        )

    def validate(self, bundle: ContextBundle) -> ValidationReport:
        """validate 段：token 预算 + file:// 源可解析性。只报告不修正。"""
        violations: list[str] = []
        token_within = bundle.total_token_count <= bundle.token_budget
        if not token_within:
            violations.append(f"token_overflow: {bundle.total_token_count} > budget {bundle.token_budget}")
        for content in bundle.slots.values():
            for trace in content.source_traces:
                if trace.startswith("file://"):
                    if not (self._project_root / trace[len("file://") :]).exists():
                        violations.append(f"unresolvable_source: {trace}")
        return ValidationReport(
            passed=token_within and not violations,
            token_within_budget=token_within,
            violations=violations,
        )

    def inject(self, bundle: ContextBundle, *, ide_id: str = "generic_mcp") -> InjectResult:
        """inject 段：按静态 IDE 能力矩阵路由通道（MCP 真接线留注入位，本方法产出通道计划）。

        路由规则：prompts 全 IDE 兜底；resources 承载 architecture/code_refs/runtime_state/
        task_history；tools 承载 guardrails。不支持/未知通道记 channels_skipped。
        """
        matrix = IDE_CAPABILITY_MATRIX.get(ide_id, IDE_CAPABILITY_MATRIX["generic_mcp"])
        channels_used = ["prompts"]
        channels_skipped: list[tuple[str, str]] = []

        resource_slots = {"architecture", "code_refs", "runtime_state", "task_history"}
        if any(s in bundle.slots for s in resource_slots):
            level = matrix.get("resources", "unknown")
            if level in ("full", "partial", "read_only"):
                channels_used.append("resources")
            else:
                channels_skipped.append(("resources", f"ide={ide_id} capability={level}，降级 prompts"))
        else:
            channels_skipped.append(("resources", "无 architecture/code_refs/runtime_state/task_history 槽"))

        if "guardrails" in bundle.slots:
            level = matrix.get("tools", "unknown")
            if level in ("full", "partial"):
                channels_used.append("tools")
            else:
                channels_skipped.append(("tools", f"ide={ide_id} capability={level}，降级 prompts"))
        else:
            channels_skipped.append(("tools", "无 guardrails 槽"))

        channels_skipped.append(("sampling", "轻量实现不接 sampling 通道"))
        return InjectResult(channels_used=channels_used, channels_skipped=channels_skipped)

    # ────────────────────────────────────────────────────────────────
    # 蓝图补齐：规则注入（code_dedup W3-8 消费位）
    # ────────────────────────────────────────────────────────────────

    def register_rules(self, tier: str, rules: list[dict[str, str]]) -> None:
        """按 HOT/DOMAIN/COLD 三层注册注入规则。非法分层 → ValueError。"""
        if tier not in RULE_TIERS:
            raise ValueError(f"规则分层必须是 {RULE_TIERS} 之一: {tier}")
        for rule in rules:
            self._rules[tier].append(
                ContextRule(rule_id=str(rule.get("rule_id", "")), text=str(rule.get("text", "")), tier=tier)
            )

    def rules_for(self, tier: str) -> list[ContextRule]:
        return list(self._rules.get(tier, []))

    # ────────────────────────────────────────────────────────────────
    # 蓝图补齐：FLE 反馈通道 adjust_strategy（slot 预算动态调整 + TTL）
    # ────────────────────────────────────────────────────────────────

    def slot_budgets(self) -> dict[str, float]:
        """当前生效的 slot 预算比例（默认 + 未过期 override；TTL 到期自动回默认）。"""
        budgets = dict(DEFAULT_SLOT_BUDGETS)
        now = self._now()
        expired = [k for k, (_, exp) in self._slot_overrides.items() if now >= exp]
        for key in expired:
            del self._slot_overrides[key]
        for _, (override, _) in self._slot_overrides.items():
            budgets.update(override)
        return budgets

    def adjust_strategy(self, task_id: str, signal: dict[str, Any]) -> AdjustResult:
        """FLE 反馈入口：downweight/upweight 某 slot，其他 slot 按比例吸收（Σ=1 守恒）。

        signal 键：suggested_action / target_slot / adjustment_magnitude / ttl_minutes。
        未知 slot / 未知动作 → ValueError。
        """
        action = str(signal.get("suggested_action", ""))
        target = str(signal.get("target_slot", ""))
        if target not in DEFAULT_SLOT_BUDGETS:
            raise ValueError(f"未知 slot: {target}")
        if action not in ("downweight_slot", "upweight_slot"):
            raise ValueError(f"不支持的动作: {action}")
        magnitude = float(signal.get("adjustment_magnitude", 0.1))
        ttl_minutes = int(signal.get("ttl_minutes", 60))

        budgets = self.slot_budgets()
        delta = magnitude if action == "upweight_slot" else -magnitude
        budgets[target] = min(0.9, max(0.01, budgets[target] + delta))
        others_sum = sum(v for k, v in budgets.items() if k != target)
        if others_sum > 0:
            scale = (1.0 - budgets[target]) / others_sum
            for key in budgets:
                if key != target:
                    budgets[key] *= scale

        expiry = self._now() + timedelta(minutes=ttl_minutes)
        self._slot_overrides[task_id] = (budgets, expiry)
        return AdjustResult(applied=True, new_slot_budgets=dict(budgets))


# ---------------------------------------------------------------------------
# 蓝图补齐数据结构与常量（MOD-CONTEXT_ENGINE，接口规范 §3/§4/§10）
# ---------------------------------------------------------------------------

DEFAULT_SLOT_BUDGETS: Final[dict[str, float]] = {
    "task_spec": 0.10,
    "architecture": 0.25,
    "code_refs": 0.30,
    "task_history": 0.15,
    "lessons": 0.10,
    "runtime_state": 0.05,
    "guardrails": 0.05,
}
"""slot 默认 token 预算占比（接口规范 §3.1）。"""

IDE_CAPABILITY_MATRIX: Final[dict[str, dict[str, str]]] = {
    "cursor": {"tools": "full", "resources": "read_only", "prompts": "full", "sampling": "experimental"},
    "trae": {"tools": "partial", "resources": "full", "prompts": "full", "sampling": "none"},
    "claude_desktop": {"tools": "full", "resources": "full", "prompts": "full", "sampling": "full"},
    "generic_mcp": {"tools": "unknown", "resources": "unknown", "prompts": "full", "sampling": "unknown"},
}
"""IDE MCP 通道能力静态矩阵（接口规范 §3.2；探测失败兜底）。"""

RULE_TIERS: Final[tuple[str, ...]] = ("HOT", "DOMAIN", "COLD")
"""规则注入三层（HOT 热规则 / DOMAIN 域规则 / COLD 冷规则）。"""


@dataclass
class SlotContent:
    """单 slot 的内容容器（接口规范 §3.3 SlotContent 轻量版）。"""

    slot: str
    items: list[ContextSlice]
    token_count: int
    source_traces: list[str] = field(default_factory=list)
    degraded_sources: list[str] = field(default_factory=list)


@dataclass
class ContextBundle:
    """四段流水线传递的结构化上下文包（接口规范 §3.3 轻量版）。"""

    request_id: str
    task_id: str
    slots: dict[str, SlotContent]
    total_token_count: int
    token_budget: int
    compression_ratio: float | None
    bundle_hash: str
    degraded: bool = False
    degrade_reasons: list[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    """validate 段报告（只报告不修正）。"""

    passed: bool
    token_within_budget: bool
    violations: list[str] = field(default_factory=list)


@dataclass
class InjectResult:
    """inject 段通道路由计划（MCP 真接线留注入位）。"""

    channels_used: list[str]
    channels_skipped: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class ContextRule:
    """register_rules 注册的注入规则。"""

    rule_id: str
    text: str
    tier: str


@dataclass
class AdjustResult:
    """adjust_strategy 反馈调整结果。"""

    applied: bool
    new_slot_budgets: dict[str, float]
