# [BLUEPRINT] MOD-INF-054 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §4 Phase 1（06号文 P1-1~P1-4 触发式考试调度器）
# [MODULE] zephyr.intelligence.model_profiling.exam_trigger_scheduler
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.capability_passport(CapabilityPassport/QuickProfile); zephyr.intelligence.model_profiling.model_discovery(ModelDiscovery)
# [CONSUMERS] 待统筹接线（06号文 Phase 2：dispatch 链门控钩子 + ModelDiscovery 定时扫描挂点）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 触发器只产「建议/QuickProfile」（Quick 自动；Standard/Deep 始终人工确认 human_gated，本模块无任何 Standard/Deep 调用路径）; 新模型判定=无护照且无 QuickProfile 且未入 seen 快照; 复核建议只发不执行（连续 low_accuracy 超阈 -> 建议落盘+告警）; 单模型考试失败不中断批量（降级留痕）; 可变容器 typing.Final 禁重新赋值
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ExamTriggerError(ZA-IT-0011)：阈值非法/快照文件损坏 fail-closed; discovery/runner 异常不抛 -> 报告 errors 字段留痕，批量不中断
# [TESTS] tests/model/test_exam_trigger_scheduler.py
# [A_module] module_id=MOD-INF-054 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
exam_trigger_scheduler — 触发式考试调度器（06号文 §4 Phase 1，P1-1~P1-4）
================================================================================

两条触发链：

1. **新模型入库触发**（P1-2）：ModelDiscovery 发现新模型（无护照 + 无 QuickProfile +
   未入 seen 快照）-> 自动 Quick 考试（注入 runner，测试用假 runner）->
   QuickProfile 落盘 data/brain/quick_profiles/。考试结果无论成败都记 seen，
   避免失败模型每次扫描重复触发。

2. **门控拦截复核触发**（P1-3）：TaskGate 连续 low_accuracy 拦截计数超阈值 ->
   发出复核考试建议（建议落盘 JSONL + 告警日志）。**只发建议**——
   Standard/Deep 考试始终人工确认后执行（对齐 capability_passport.py /
   exam_orchestrator.py 头部 AI_AUTONOMY=human_gated，本模块无其调用路径）。

用法
----
    sched = ExamTriggerScheduler()
    report = sched.trigger_quick_exams()          # 扫描+自动 Quick 考试
    ok, reason = sched.check_and_record(gate, "qwen3:8b", "code_fix")  # dispatch 钩子
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from zephyr.intelligence.model_profiling.capability_passport import (
    CapabilityPassport,
    QuickProfile,
)
from zephyr.intelligence.model_profiling.model_discovery import ModelDiscovery

__all__: Final = [
    "DEFAULT_LOW_ACCURACY_THRESHOLD",
    "ExamTriggerError",
    "ExamTriggerScheduler",
]

_log = logging.getLogger(__name__)

DEFAULT_LOW_ACCURACY_THRESHOLD: Final[int] = 3  # 连续 low_accuracy 拦截次数阈值（超阈发复核建议）
_SUGGESTED_REVIEW_MODE: Final[str] = "standard"  # 复核建议级别（执行始终人工确认 human_gated）
_LOW_ACCURACY_PREFIX: Final[str] = "low_accuracy"


class ExamTriggerError(Exception):
    """触发式考试调度器错误（阈值非法/快照损坏 fail-closed）。"""

    error_code = "ZA-IT-0011"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


def _default_quick_exam_runner(model_id: str) -> QuickProfile:
    """生产 Quick 考试执行器：OllamaChat + ExamOrchestrator.run_quick_exam（延迟导入）。

    测试注入假 runner，本路径不被单测触及（LLM 全 mock 纪律）。
    """
    from zephyr.integration.local_model.ollama_chat import OllamaChat
    from zephyr.intelligence.model_profiling.exam_orchestrator import ExamOrchestrator

    chat = OllamaChat(model=model_id)
    orch = ExamOrchestrator(chat, model_id=model_id)
    return orch.run_quick_exam()


class ExamTriggerScheduler:
    """触发式考试调度器——新模型自动 Quick 考试 + 门控拦截复核建议。

    discovery/quick_exam_runner 支持测试注入；缺省走真实 ModelDiscovery 与
    Ollama+ExamOrchestrator 生产路径。seen_store_path/suggestion_sink_path
    为 None 时仅内存态（测试注入 tmp_path 验证落盘）。
    """

    def __init__(
        self,
        *,
        discovery: Any | None = None,
        quick_exam_runner: Any | None = None,
        low_accuracy_threshold: int = DEFAULT_LOW_ACCURACY_THRESHOLD,
        seen_store_path: Path | str | None = None,
        suggestion_sink_path: Path | str | None = None,
    ) -> None:
        if low_accuracy_threshold < 1:
            raise ExamTriggerError(f"low_accuracy_threshold 必须 >= 1: {low_accuracy_threshold}")
        self._discovery = discovery
        self._quick_exam_runner = quick_exam_runner
        self._threshold = low_accuracy_threshold
        self._seen_store_path = Path(seen_store_path) if seen_store_path is not None else None
        self._suggestion_sink_path = (
            Path(suggestion_sink_path) if suggestion_sink_path is not None else None
        )
        self._seen: set[str] = set()
        self._block_streaks: dict[tuple[str, str], int] = {}
        self._suggestions: list[dict[str, Any]] = []
        self._load_seen_store()

    # ── 快照/建议落盘 ────────────────────────────────────

    def _load_seen_store(self) -> None:
        if self._seen_store_path is None or not self._seen_store_path.exists():
            return
        try:
            data = json.loads(self._seen_store_path.read_text(encoding="utf-8"))
            seen = data.get("seen", [])
            if not isinstance(seen, list):
                raise ValueError("seen 字段非 list")
            self._seen = {str(m) for m in seen}
        except ExamTriggerError:
            raise
        except Exception as exc:  # noqa: BLE001 — 快照损坏=fail-closed（防重复触发风暴）
            raise ExamTriggerError(f"seen 快照损坏: {self._seen_store_path}: {exc}") from exc

    def _save_seen_store(self) -> None:
        if self._seen_store_path is None:
            return
        self._seen_store_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"seen": sorted(self._seen), "saved_at": datetime.now(tz=UTC).isoformat()}
        self._seen_store_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _append_suggestion_sink(self, suggestion: dict[str, Any]) -> None:
        if self._suggestion_sink_path is None:
            return
        self._suggestion_sink_path.parent.mkdir(parents=True, exist_ok=True)
        with self._suggestion_sink_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(suggestion, ensure_ascii=False) + "\n")

    # ── 链路 1：新模型 -> Quick 考试 -> QuickProfile 落盘 ──

    def _resolve_discovery(self) -> Any:
        if self._discovery is None:
            self._discovery = ModelDiscovery()
        return self._discovery

    def _resolve_runner(self) -> Any:
        if self._quick_exam_runner is None:
            self._quick_exam_runner = _default_quick_exam_runner
        return self._quick_exam_runner

    def _is_known_model(self, model_id: str) -> bool:
        """已知模型判定：有护照 / 有 QuickProfile / 已入 seen 快照（任一即非新）。"""
        if model_id in self._seen:
            return True
        if CapabilityPassport.load(model_id) is not None:
            return True
        return QuickProfile.load(model_id) is not None

    def scan_new_models(self) -> list[str]:
        """ModelDiscovery 发现新模型（source=ollama 本地模型才需 Quick 考试；远程 API 模型跳过）。"""
        discovered = self._resolve_discovery().discover_all()
        new_models: list[str] = []
        for m in discovered:
            name = getattr(m, "name", "") or ""
            source = getattr(m, "source", "") or ""
            if not name or source != "ollama":
                continue
            if not self._is_known_model(name):
                new_models.append(name)
        return new_models

    def trigger_quick_exams(self, model_ids: list[str] | None = None) -> dict[str, Any]:
        """对新模型自动跑 Quick 考试并落盘 QuickProfile（P1-2 验收点）。

        单模型失败记 errors 留痕不中断批量；成败均记 seen（防失败模型重复触发风暴）。
        返回 JSON 可序列化报告。
        """
        targets = list(model_ids) if model_ids is not None else self.scan_new_models()
        runner = self._resolve_runner()
        report: dict[str, Any] = {
            "targets": targets,
            "examined": [],
            "failed": {},
            "saved_paths": {},
        }
        for model_id in targets:
            if model_ids is None and self._is_known_model(model_id):
                continue  # scan 与执行间隙被其他链路登记 -> 不重复考试
            try:
                profile = runner(model_id)
                saved = profile.save()
                report["examined"].append(model_id)
                report["saved_paths"][model_id] = str(saved)
                _log.info("exam_trigger_scheduler: 新模型 %s QuickProfile 已落盘 %s", model_id, saved)
            except Exception as exc:  # noqa: BLE001 — 单模型失败降级不中断批量
                report["failed"][model_id] = f"{type(exc).__name__}: {exc}"
                _log.warning("exam_trigger_scheduler: 模型 %s Quick 考试失败: %s", model_id, exc)
            finally:
                self._seen.add(model_id)
        self._save_seen_store()
        return report

    # ── 链路 2：TaskGate 连续 low_accuracy -> 复核建议 ──

    def record_gate_decision(
        self,
        model_id: str,
        capability: str,
        allowed: bool,
        reason: str,
    ) -> dict[str, Any] | None:
        """登记一次门控判定；连续 low_accuracy 超阈 -> 发复核考试建议（只发建议不执行）。

        放行/非 low_accuracy 拦截 -> 计数清零。同一连续段只在触及阈值时发一次建议。
        返回建议 dict（未触发返回 None）。
        """
        key = (model_id, capability)
        if allowed or not reason.startswith(_LOW_ACCURACY_PREFIX):
            self._block_streaks.pop(key, None)
            return None
        streak = self._block_streaks.get(key, 0) + 1
        self._block_streaks[key] = streak
        if streak != self._threshold:
            return None
        suggestion: dict[str, Any] = {
            "type": "review_exam_suggestion",
            "model_id": model_id,
            "capability": capability,
            "consecutive_low_accuracy": streak,
            "suggested_mode": _SUGGESTED_REVIEW_MODE,
            "human_gated": True,  # Standard/Deep 始终人工确认——建议不自动执行（06号文 Phase 1 纪律）
            "last_block_reason": reason,
            "ts": datetime.now(tz=UTC).isoformat(),
        }
        self._suggestions.append(suggestion)
        self._append_suggestion_sink(suggestion)
        _log.warning(
            "exam_trigger_scheduler: 模型 %s 能力 %s 连续 %d 次 low_accuracy 拦截，"
            "建议人工复核考试（mode=%s, human_gated）",
            model_id,
            capability,
            streak,
            _SUGGESTED_REVIEW_MODE,
        )
        return suggestion

    def check_and_record(self, gate: Any, model_id: str, capability: str) -> tuple[bool, str]:
        """TaskGate dispatch 钩子：透传 can_dispatch 判定并登记（拦截日志含触发建议记录）。"""
        allowed, reason = gate.can_dispatch(model_id, capability)
        self.record_gate_decision(model_id, capability, allowed, reason)
        return (allowed, reason)

    @property
    def suggestions(self) -> list[dict[str, Any]]:
        """已发复核建议的只读快照。"""
        return list(self._suggestions)

    @property
    def block_streaks(self) -> dict[tuple[str, str], int]:
        """连续拦截计数的只读快照（观测/对账用）。"""
        return dict(self._block_streaks)
