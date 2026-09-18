# [BLUEPRINT] MOD-INF-052 | docs/03_modules/_domain_integration/lsg_gate/blueprint.md | §
# [MODULE] zephyr.integration.local_model.lsg_gate
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.gateway; zephyr.shared.contracts.security.security_decision; zephyr.shared.utils.async_utils; zephyr.security.llm_defense.llm_security.layers.l6_observability
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
# [A_module] module_id=MOD-INF-052 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Final, Protocol

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


_BYPASS_LEDGER: dict[str, int] = {}
_bypass_lock = threading.Lock()


def lsg_bypass_ledger() -> dict[str, int]:
    """只读快照：LSG **未参与**的调用计数（键="方向|source"）。

    红队加严（st-ff-rb-safe-20260918 攻面二④⑤）：环境变量
    `ZEPHYR_LSG_LOCAL_MODEL_ENABLED=0` 会一次性旁路三通道全部输入/输出闸门，
    而此前该路径**零审计零日志**——llm_call_log 里 status=ok 的行与"LSG 真放行"
    逐字段不可区分，于是"所有 LLM 调用必经 LSG"既无载体可证伪、也无法事后
    反推哪天没扫。本台账 + 首见 WARNING 就是这个载体（不改任何放行语义）。
    """
    with _bypass_lock:
        return dict(_BYPASS_LEDGER)


def _record_bypass(direction: str, source: str) -> None:
    """记"闸门未参与"——只出声，不判放行/拦截（放行语义逐字不变）。"""
    key = f"{direction}|{source}"
    with _bypass_lock:
        first_seen = key not in _BYPASS_LEDGER
        _BYPASS_LEDGER[key] = _BYPASS_LEDGER.get(key, 0) + 1
    gw = _gateway  # 仅在网关已构造时借道 L6；绝不为记旁路去构造网关（防递归/防开销）
    if gw is not None:
        try:
            layer = gw.get_layer("l6_observability")
            if layer is not None:
                layer.log_security_event(
                    event_type="lsg_local_model_gate_bypass",
                    message=f"local_model {direction} 闸门未参与 source={source} "
                            f"（LSG enabled=False，本次调用未经安全扫描）",
                    severity="HIGH",
                )
        except Exception:  # noqa: BLE001 — 审计失败不得改变放行语义
            _log.debug("lsg_gate: 旁路审计记录失败（不阻断）", exc_info=True)
    if first_seen:
        _log.warning(
            "LSG %s 闸门未参与（enabled=False, source=%s）——该通道调用未经安全扫描",
            direction, source,
        )


def _bypass_guard(direction: str, source: str, *, enabled: bool, text: str) -> bool:
    """闸门跳过判决的统一前置（红队 st-ff-rb-safe2-20260918 收口 CloneGuard）。

    返回 True ⇒ 调用方直接 return（不进 L0-L5 / L3-L6 链）。
    两条语义与前手逐字一致：enabled=False → 记一次"闸门未参与"后放行；
    空文本 → 静默放行（不记旁路，旁账面只承载"闸被关"这一种失真）。
    抽成单一前置是因为 `enforce_input`/`enforce_output` 各写一份同形前置
    会构成 extract 级克隆（RULE-CLONEGUARD 无逃生，裁定口径=合并而非登记豁免）。

    Args:
        direction: "input" | "output"（进旁路台账的键，也进 WARNING 文案）。
        source: 调用侧通道标识。
        enabled: LSG 总闸开关（False=旁路）。
        text: 待检文本。

    Returns:
        True=本次不经安全扫描，调用方应立即返回。
    """
    if not enabled:
        _record_bypass(direction, source)
        return True
    return not text


@dataclass(frozen=True)
class _GateDirection:
    """一个方向上 LSG 闸门**唯一真实存在**的两点文案差异（其余流水线共用）。

    Attributes:
        label: 报错文案中的方向名词（"输入"/"输出"）。
        refusal: BLOCK/DENY 判决的处置动作——入向=调用不得发起，出向=响应不得返回。
    """

    label: str
    refusal: str


# 方向真源表：新增方向必须同时扩本表与 _enforce 的分派分支，
# 未登记方向在入口即 KeyError（任何扫描都不会发生）——fail-closed 方向不放宽。
_DIRECTIONS: Final[dict[str, _GateDirection]] = {
    "input": _GateDirection(label="输入", refusal="拒绝发起 LLM 调用"),
    "output": _GateDirection(label="输出", refusal="拒绝返回该响应"),
}


def _enforce(text: str, *, direction: str, source: str, enabled: bool = True) -> None:
    """LSG 判决闸门的**唯一一份**实现（入/出向共用，方向差异只落在 _DIRECTIONS）。

    控制流（与合并前的 enforce_input/enforce_output 逐字一致）：
      1. _bypass_guard 前置：enabled=False 记旁路后放行；空文本静默放行。
      2. 网关不可用 → 抛 LSGBlockedError（fail-closed，不发起/不返回）。
      3. 按 direction 分派 gw.scan_input / gw.scan_output，经 run_sync 取判决；
         扫描异常 → 先落 error 判决再抛 LSGBlockedError（from exc 保留链）。
      4. 正常判决落 L6 审计。
      5. 判决 BLOCK/DENY → 抛 LSGBlockedError（含 decision.value/blocked_by/source）。

    红队 st-ff-rb-safe2/3-20260918 收口说明：入/出向在扫描方法名与报错文案之外
    **没有任何结构差别**，两份同形实现即 extract 级克隆（RULE-CLONEGUARD 无逃生，
    裁定口径 R-002/R-054=合并而非豁免）。故真差异降级为数据（_DIRECTIONS），
    流水线只留一份；enforce_input/enforce_output 以 partial 绑定方向，模块内
    不再存在第二份可比对的函数体。

    Args:
        text: 待检文本（入向=prompt，出向=模型响应）。
        direction: "input" | "output"，须已在 _DIRECTIONS 登记。
        source: 调用侧通道标识。
        enabled: LSG 总闸开关（False=旁路，仍记台账）。
    """
    spec = _DIRECTIONS[direction]
    if _bypass_guard(direction, source, enabled=enabled, text=text):
        return
    gw = get_gateway()
    if gw is None:
        raise LSGBlockedError(  # noqa: MSG-EXPOSURE — source=LSG 通道标签（如 OllamaChat.qwen3），非路径/凭据/连接串
            f"LSG 不可用，fail-closed 拒绝{spec.label} (source={source})"
        )
    from zephyr.shared.contracts.security.security_decision import SecurityDecision
    from zephyr.shared.utils.async_utils import run_sync

    try:
        # 方向分派：入口 _DIRECTIONS 已保证 direction ∈ {"input","output"}，
        # 未登记方向在扫描发生前即 KeyError fail-loud（不放宽任何判据）。
        scan = gw.scan_input if direction == "input" else gw.scan_output
        result = run_sync(scan(text, source=source))
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _record_decision(gw, direction=direction, source=source, error=type(exc).__name__)
        raise LSGBlockedError(  # noqa: MSG-EXPOSURE — source=通道标签、{exc}=fail-closed 必需留痕，均非凭据面
            f"LSG {spec.label}扫描异常，fail-closed 拒绝 (source={source}): {exc}"
        ) from exc
    _record_decision(gw, direction=direction, source=source, result=result)
    if result.decision in (SecurityDecision.BLOCK, SecurityDecision.DENY):
        raise LSGBlockedError(  # noqa: MSG-EXPOSURE — source=通道标签、blocked_by=LSG 层名，均为审计定位所需非敏感枚举
            f"LSG {spec.label}判决 {result.decision.value}，{spec.refusal} "
            f"(blocked_by={result.blocked_by}, source={source})"
        )


class _Enforcer(Protocol):
    """enforce_input/enforce_output 的公开签名（partial 绑定方向后仍受静态检查）。"""

    def __call__(self, text: str, *, source: str, enabled: bool = True) -> None: ...


# 公开入口：名字与签名逐字保留（ollama_chat/deepseek_chat/local_model_scheduler/
# embedding_router/llm_runtime_gateway 五处消费者按 enforce_x(text, source=, enabled=) 调用）。
enforce_input: _Enforcer = partial(_enforce, direction="input")
enforce_output: _Enforcer = partial(_enforce, direction="output")
