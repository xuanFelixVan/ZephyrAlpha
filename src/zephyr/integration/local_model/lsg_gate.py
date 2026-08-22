# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §3.1
# [MODULE] zephyr.integration.local_model.lsg_gate
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.gateway; zephyr.shared.contracts.security.security_decision; zephyr.shared.utils.async_utils
# [CONSUMERS] ollama_chat.py; deepseek_chat.py; local_model_scheduler.py; embedding_router.py; tests.model.test_local_model_lsg_gate
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-closed: LSG 不可用/判决 BLOCK/DENY -> 抛 LSGBlockedError 且不发起 LLM API 调用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LSG 判决 BLOCK/DENY 或 LSG 不可用 -> 抛 LSGBlockedError(RuntimeError)
# [TESTS] tests/model/test_local_model_lsg_gate.py
# [A_module] module_id=MOD-INF-042 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
lsg_gate.py — local_model 包 LSG 统一注入闸门（09号文 §4.2 P0-1）
=================================================================

L2/L3 运行时 LLM 客户端（OllamaChat / DeepSeekChat / LocalModelScheduler /
EmbeddingRouter）构造点的统一安全闸门：所有本地模型调用在发起 API 请求前
必经 LSGSecurityGateway 判决，判决记录落 L6 审计——三通道同一闸门，无旁路。

原则
----
- fail-closed：LSG 不可用或扫描异常 -> 抛 LSGBlockedError，不发起 API 调用
  （蓝图 D-INF014-01：宁可停服不可裸奔）。
- 开关默认开：构造参数 ``lsg_enabled`` > 环境变量
  ``ZEPHYR_LSG_LOCAL_MODEL_ENABLED``（"0"/"false"/"off"/"no" 关闭）> 默认开。
  关闭仅供测试/应急，不改变默认安全姿态。
- 性能：L1/L2 为本地正则/模式匹配、L5 为计数器检查，扫描耗时微秒~毫秒级；
  网关进程内单例复用，不拖慢调用。每次判决的 elapsed_ms 写入 L6 审计留痕。

用法
----
    from zephyr.integration.local_model.lsg_gate import (
        LSGBlockedError,
        enforce_input,
        enforce_output,
        resolve_lsg_enabled,
    )

    self._lsg_enabled = resolve_lsg_enabled(lsg_enabled)   # 构造点解析开关
    enforce_input(prompt_text, source="OllamaChat", enabled=self._lsg_enabled)
"""

from __future__ import annotations

import logging
import os
import threading
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway, ScanResult

_log = logging.getLogger(__name__)

# 开关环境变量（默认开；"0"/"false"/"off"/"no" 关闭）
LSG_ENABLED_ENV: Final[str] = "ZEPHYR_LSG_LOCAL_MODEL_ENABLED"

_ENV_OFF_VALUES: Final[frozenset[str]] = frozenset({"0", "false", "off", "no"})


class LSGBlockedError(RuntimeError):
    """LSG 判决 BLOCK/DENY 或 LSG 不可用（fail-closed）——本次 LLM API 调用不得发起。

    继承 RuntimeError 以保持 OllamaChat/DeepSeekChat 既有错误契约
    （"DENY/API失败时抛 RuntimeError"）零破坏。
    """


_gateway: LSGSecurityGateway | None = None
_gateway_lock = threading.Lock()


def resolve_lsg_enabled(override: bool | None = None) -> bool:
    """解析 LSG 注入开关：构造参数 override > 环境变量 > 默认开。"""
    if override is not None:
        return bool(override)
    return os.getenv(LSG_ENABLED_ENV, "1").strip().lower() not in _ENV_OFF_VALUES


def get_gateway() -> LSGSecurityGateway | None:
    """LSG 网关懒加载进程内单例（线程安全，双重检查）。

    构造失败返回 None——由调用方按 fail-closed 处理（下次调用重试构造）。
    """
    global _gateway
    if _gateway is not None:
        return _gateway
    with _gateway_lock:
        if _gateway is None:
            try:
                from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

                _gateway = LSGSecurityGateway()
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                _log.error("lsg_gate: LSG 网关构造失败，local_model 通道 fail-closed", exc_info=True)
                return None
    return _gateway


def _record_decision(
    gw: LSGSecurityGateway,
    *,
    direction: str,
    source: str,
    result: ScanResult | None = None,
    error: str = "",
) -> None:
    """判决记录落 L6 审计（L6 为 fail-open 层：记录失败绝不阻断主流程）。

    安全纪律：只记录判决元数据（source/decision/blocked_by/elapsed_ms），
    不记录 prompt/响应原文，防止敏感内容落入审计日志。
    """
    try:
        layer = gw.get_layer("l6_observability")
        if layer is None:
            return
        from zephyr.security.llm_defense.llm_security.layers.l6_observability import AlertSeverity

        if result is not None:
            decision = result.decision.value
            blocked_by = result.blocked_by
            elapsed_ms: float = result.elapsed_ms
        else:
            decision = "error"
            blocked_by = "exception"
            elapsed_ms = -1.0
        severity = AlertSeverity.HIGH if decision in ("block", "deny", "error") else AlertSeverity.DEBUG
        layer.log_security_event(
            event_type="lsg_local_model_gate",
            message=(
                f"local_model {direction} source={source} decision={decision} "
                f"blocked_by={blocked_by or '-'} elapsed_ms={elapsed_ms} error={error or '-'}"
            ),
            severity=severity,
        )
    except Exception:  # noqa: BLE001 — L6 fail-open：审计降级不阻断
        _log.debug("lsg_gate: L6 审计记录失败（fail-open 不阻断主流程）", exc_info=True)


def enforce_input(text: str, *, source: str, enabled: bool = True) -> None:
    """LLM 调用前输入闸门：L0->L1->L2->L5 链式判决（fail-closed）。

    - enabled=False（开关关闭）或空文本：直接放行（测试/应急通道）。
    - 判决 BLOCK/DENY：抛 LSGBlockedError，调用方不得发起 API 调用。
    - LSG 不可用/扫描异常：fail-closed 抛 LSGBlockedError。
    - 每次判决（含 ALLOW）均落 L6 审计。
    """
    if not enabled or not text:
        return
    gw = get_gateway()
    if gw is None:
        raise LSGBlockedError(f"LSG 不可用，fail-closed 拒绝输入 (source={source})")
    from zephyr.shared.contracts.security.security_decision import SecurityDecision
    from zephyr.shared.utils.async_utils import run_sync

    try:
        result = run_sync(gw.scan_input(text, source=source))
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _record_decision(gw, direction="input", source=source, error=type(exc).__name__)
        raise LSGBlockedError(f"LSG 输入扫描异常，fail-closed 拒绝 (source={source}): {exc}") from exc
    _record_decision(gw, direction="input", source=source, result=result)
    if result.decision in (SecurityDecision.BLOCK, SecurityDecision.DENY):
        raise LSGBlockedError(
            f"LSG 输入判决 {result.decision.value}，拒绝发起 LLM 调用 "
            f"(blocked_by={result.blocked_by}, source={source})"
        )


def enforce_output(text: str, *, source: str, enabled: bool = True) -> None:
    """LLM 响应返回前输出闸门：L3->L6 链式判决（fail-closed）。

    语义同 enforce_input；判决 BLOCK/DENY 时抛 LSGBlockedError，
    违规输出不得返回给调用方。
    """
    if not enabled or not text:
        return
    gw = get_gateway()
    if gw is None:
        raise LSGBlockedError(f"LSG 不可用，fail-closed 拒绝输出 (source={source})")
    from zephyr.shared.contracts.security.security_decision import SecurityDecision
    from zephyr.shared.utils.async_utils import run_sync

    try:
        result = run_sync(gw.scan_output(text, source=source))
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _record_decision(gw, direction="output", source=source, error=type(exc).__name__)
        raise LSGBlockedError(f"LSG 输出扫描异常，fail-closed 拒绝 (source={source}): {exc}") from exc
    _record_decision(gw, direction="output", source=source, result=result)
    if result.decision in (SecurityDecision.BLOCK, SecurityDecision.DENY):
        raise LSGBlockedError(
            f"LSG 输出判决 {result.decision.value}，拒绝返回该响应 "
            f"(blocked_by={result.blocked_by}, source={source})"
        )
