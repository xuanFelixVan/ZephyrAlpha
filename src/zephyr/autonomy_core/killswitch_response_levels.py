# [BLUEPRINT] MOD-AU-004 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/16_ai_security_ops.md | §4.4-P2-3
# [MODULE] zephyr.autonomy_core.killswitch_response_levels
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.kill_switch_orchestrator
# [CONSUMERS] tests/autonomy_core/test_killswitch_response_levels.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 策略层不持有开关状态(全经 MOD-AU-002 编排器公开 API 消费,其源文件零改动); 三级复位须 approver 非空(Owner 批准,15号文 §4.1 S0.3),approver 为空拒绝且状态零改变; level_3 系统级全局熔断+交易级联动(传播未覆盖交易域时策略层显式兜底拉 trading 域),收敛状态一致无「只停次要回路」
# [MODIFY-GUARD] Owner approval required; 变更须同步 16号文 §3.4 映射口径与 §3.13 术语裁定(Q7)
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] respond()/reset_response()/consistency_report() 永不抛异常; 失败收入 ResponseResult.errors; write_killswitch_md author 为空抛 ValueError; 错误/原因消息零 session_id
# [TESTS] tests/autonomy_core/test_killswitch_response_levels.py
# [A_module] module_id=MOD-AU-004 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""



KillSwitchResponseLayer — KILLSWITCH 三级响应策略层（MOD-AU-004）.

设计真源：16号文（16_ai_security_ops.md）§3.4/§3.13/§4.4 P2-3 + 15号文 §3.4/§4.1 S0.3：
- 分层框架：策略层（本层，只裁决「这次事件该停什么」）→ 路由层（MOD-AU-002 两级
  编排器）→ 执行机构层（5 套 Kill Switch）。本层一个开关都不直接碰，全部动作经
  KillSwitchOrchestrator 公开 API 组合下单，其源文件零改动。
- 映射口径（16号文 §3.4 + §3.13 Q7 术语裁定 2026-08-18）：
  level_1 P1(high) → 自治降级（暂降 IM 模式=auto_guard，读/查询放行写操作人审）
  +技能熔断（编排器域级拉闸）；
  level_2 P0(critical) → IM 基线上叠加系统级单 Agent 阻断
  （VR-009 manual_trip_agent 粒度，不全局熔断）；
  level_3 global_critical → 系统级全局熔断+交易级联动（编排器传播未覆盖交易域时
  策略层显式兜底拉 trading 域）+收敛一致性检查（无「只停次要回路」）。
- 自治降级载体=注入式 downgrader 钩子：AutonomyRegressor 无执行 API 且 IM 模式是
  运行时动态覆盖（§3.13 Q7），缺省只产降级指令落审计，不虚报「已执行」。
- 复位不变量（15号文 §4.1 S0.3）：三级复位统一 approver 非空（Owner 批准），
  approver 为空拒绝且状态零改变。
- 留痕：响应/复位动作按 16号文 §4.2 P0-1 统一事件 schema 写
  .runtime/audit/killswitch_response_levels.jsonl（source_domain=access_control）；
  KILLSWITCH.md 变更写 killswitch_md_change 事件（§3.13）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: orchestrator 参数
#   fields: 参数 orchestrator（无注解）
#   code: killswitch_response_levels.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: runtime_dir 参数
#   fields: 参数 runtime_dir（无注解）
#   code: killswitch_response_levels.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: system_switch 参数
#   fields: 参数 system_switch（无注解）
#   code: killswitch_response_levels.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: downgrader 参数
#   fields: 参数 downgrader（无注解）
#   code: killswitch_response_levels.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① render_killswitch_md
#   name_en: render_killswitch_md
#   intro: 渲染 KILLSWITCH.
#   desc: 渲染 KILLSWITCH.md 全文（16号文 §3.13 开放标准 8 要素对标+三级定义+复位不变量）.；源码 L162-L164
#   inputs: 无参数
#   outputs: str
# - id: A2
#   name_zh: ② KillSwitchResponseLayer
#   name_en: KillSwitchResponseLayer
#   intro: KILLSWITCH 三级响应策略层.
#   desc: KILLSWITCH 三级响应策略层. 用法:: layer = KillSwitchResponseLayer( orchestrator=orch, runtime_dir=…；公共方法（定义序）: respond…
#   inputs: orchestrator runtime_dir system_switch downgrader
#   outputs: 返回值
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy_core/test_killswitch_response_levels.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final

logger = logging.getLogger(__name__)

SCHEMA_VERSION: Final[str] = "1.0"
SOURCE_DOMAIN: Final[str] = "access_control"

# IM 模式（仅人工介入模式）目标取值：读/查询放行、写操作人审（16号文 §3.13 Q7 术语）
TARGET_MODE_IM: Final[str] = "auto_guard"

TRADING_DOMAIN: Final[str] = "trading"


class ResponseLevel(str, Enum):
    """三级响应级别（16号文 §3.4 映射口径）."""

    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"


# severity 别名 → (响应级别, 归一化 severity)：P1=high / P0=critical / global_critical
_SEVERITY_MAP: Final[dict[str, tuple[ResponseLevel, str]]] = {
    "p1": (ResponseLevel.LEVEL_1, "high"),
    "high": (ResponseLevel.LEVEL_1, "high"),
    "p0": (ResponseLevel.LEVEL_2, "critical"),
    "critical": (ResponseLevel.LEVEL_2, "critical"),
    "global_critical": (ResponseLevel.LEVEL_3, "global_critical"),
}


@dataclass(frozen=True)
class ResponseIncident:
    """响应事件入参（探针/真实事故统一载体）."""

    severity: str  # P1/high | P0/critical | global_critical
    agent_id: str
    reason: str
    skill_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResponseResult:
    """单次响应/复位动作结果（不可变；动作面永不抛异常，失败收入 errors）."""

    success: bool
    level: str = ""
    target_mode: str = ""
    tripped: tuple[str, ...] = ()
    actions: tuple[str, ...] = ()
    approver: str = ""
    errors: dict[str, str] = field(default_factory=dict)
    event_id: str = ""
    timestamp: str = ""


def _level_value(level: str | ResponseLevel) -> str:
    """归一化 level 入参为字符串（兼容 ResponseLevel 枚举）."""
    return level.value if isinstance(level, ResponseLevel) else str(level).strip().lower()


def render_killswitch_md() -> str:
    """渲染 KILLSWITCH.md 全文（16号文 §3.13 开放标准 8 要素对标+三级定义+复位不变量）."""
    return _KILLSWITCH_MD_TEMPLATE


class KillSwitchResponseLayer:
    """KILLSWITCH 三级响应策略层.

    用法::

        layer = KillSwitchResponseLayer(
            orchestrator=orch, runtime_dir=Path(".runtime"),
            system_switch=system_switch, downgrader=hook,
        )
        result = layer.respond(ResponseIncident(severity="P1", agent_id="a", reason="..."))
        layer.reset_response(ResponseLevel.LEVEL_1, approver="Owner", skill_ids=("s1",))

    本层不持有任何开关状态：拉闸/复位全经编排器公开 API；自治降级经注入式
    downgrader 钩子（缺省只产指令落审计）。动作面永不抛异常。
    """

    def __init__(
        self,
        orchestrator: Any,
        runtime_dir: str | Path,
        system_switch: Any = None,
        downgrader: Any = None,
    ) -> None:
        self._orchestrator = orchestrator
        self._runtime_dir = Path(runtime_dir)
        self._audit_path = self._runtime_dir / "audit" / "killswitch_response_levels.jsonl"
        self._system_switch = system_switch
        self._downgrader = downgrader

    # ── 响应 ──────────────────────────────────────────────────

    def respond(self, incident: ResponseIncident) -> ResponseResult:
        """按 severity 裁决响应级别并执行动作链（永不抛异常，fail-closed）."""
        errors: dict[str, str] = {}
        actions: list[str] = []
        tripped: list[str] = []
        target_mode = ""
        mapped = _SEVERITY_MAP.get(str(incident.severity).strip().lower())
        if mapped is None:
            errors["severity"] = f"未知 severity 拒收（fail-closed 零动作）: {incident.severity!r}"
            result = self._result(False, "", errors=errors)
            self._trace("killswitch_response", result, incident=incident, severity="unknown")
            return result
        level, severity = mapped
        lvl = level.value
        try:
            if level is ResponseLevel.LEVEL_1:
                self._respond_level1(incident, actions, tripped, errors)
                target_mode = TARGET_MODE_IM
            elif level is ResponseLevel.LEVEL_2:
                self._respond_level2(incident, actions, tripped, errors)
                target_mode = TARGET_MODE_IM
            else:
                self._respond_level3(incident, actions, tripped, errors)
                target_mode = TARGET_MODE_IM
        except Exception as exc:  # noqa: BLE001 — ERROR_CONTRACT：永不抛异常
            errors["response_layer"] = repr(exc)
        result = self._result(
            not errors,
            lvl,
            target_mode=target_mode,
            tripped=tripped,
            actions=actions,
            errors=errors,
        )
        self._trace("killswitch_response", result, incident=incident, severity=severity)
        return result

    def _respond_level1(
        self,
        incident: ResponseIncident,
        actions: list[str],
        tripped: list[str],
        errors: dict[str, str],
    ) -> None:
        """level_1：技能熔断（编排器域级拉闸）+ 自治降级暂降 IM 模式."""
        for skill_id in incident.skill_ids:
            self._call_orchestrator(
                "trip",
                f"skills_trip:{skill_id}",
                errors,
                "domain",
                f"skills:{skill_id}",
                incident.reason,
                actions=actions,
                tripped=tripped,
                tripped_name=f"skills:{skill_id}",
            )
        self._downgrade_to_im(incident, actions, errors)

    def _respond_level2(
        self,
        incident: ResponseIncident,
        actions: list[str],
        tripped: list[str],
        errors: dict[str, str],
    ) -> None:
        """level_2：IM 基线上叠加系统级单 Agent 阻断（VR-009 粒度，不全局熔断）."""
        self._downgrade_to_im(incident, actions, errors)
        if self._system_switch is None:
            errors["system_switch"] = "系统级单 Agent 阻断开关未注入"
            return
        try:
            self._system_switch.manual_trip_agent(incident.agent_id)
            actions.append(f"system_block_agent:{incident.agent_id}")
        except Exception as exc:  # noqa: BLE001
            errors["system_switch"] = repr(exc)

    def _respond_level3(
        self,
        incident: ResponseIncident,
        actions: list[str],
        tripped: list[str],
        errors: dict[str, str],
    ) -> None:
        """level_3：系统级全局熔断 + 交易级联动（传播漏网显式兜底）+ IM 基线."""
        self._downgrade_to_im(incident, actions, errors)
        orch_result = self._call_orchestrator(
            "trip",
            "system_trip:global",
            errors,
            "system",
            "global",
            incident.reason,
            actions=actions,
            tripped=tripped,
            tripped_name="system",
        )
        if orch_result is not None:
            for name in getattr(orch_result, "tripped", ()) or ():
                if name != "system" and name not in tripped:
                    tripped.append(name)
            for key, value in (getattr(orch_result, "errors", {}) or {}).items():
                errors.setdefault(f"orchestrator:{key}", str(value))
        # 交易级联动双保险：编排器传播跳过 trading 域时策略层显式兜底拉起
        skipped = set(getattr(orch_result, "skipped", ()) or ()) if orch_result else set()
        if TRADING_DOMAIN in skipped:
            fallback = self._call_orchestrator(
                "trip",
                "trading_link:explicit_fallback",
                errors,
                "domain",
                TRADING_DOMAIN,
                f"交易级联动显式兜底: {incident.reason}",
                actions=actions,
                tripped=tripped,
                tripped_name=TRADING_DOMAIN,
            )
            if fallback is not None:
                for key, value in (getattr(fallback, "errors", {}) or {}).items():
                    errors.setdefault(f"orchestrator:{key}", str(value))
        elif TRADING_DOMAIN in tripped:
            actions.append("trading_link:orchestrator_propagation")

    def _downgrade_to_im(
        self,
        incident: ResponseIncident,
        actions: list[str],
        errors: dict[str, str],
    ) -> None:
        """自治降级：暂降 IM 模式（读/查询放行写操作人审）；缺省只产指令落审计."""
        if self._downgrader is None:
            actions.append(f"downgrade_im_instruction:{incident.agent_id}")
            return
        try:
            self._downgrader(incident.agent_id, TARGET_MODE_IM, incident.reason)
            actions.append(f"downgrade_im:{incident.agent_id}")
        except Exception as exc:  # noqa: BLE001
            errors["downgrader"] = repr(exc)

    def _call_orchestrator(
        self,
        method: str,
        action: str,
        errors: dict[str, str],
        *args: Any,
        actions: list[str],
        tripped: list[str],
        tripped_name: str,
    ) -> Any:
        """编排器调用包装：异常/失败收入 errors，单点失败不阻断动作链."""
        try:
            result = getattr(self._orchestrator, method)(*args)
        except Exception as exc:  # noqa: BLE001
            errors[tripped_name] = repr(exc)
            return None
        actions.append(action)
        if not getattr(result, "success", True):
            for key, value in (getattr(result, "errors", {}) or {}).items():
                errors.setdefault(f"{tripped_name}:{key}", str(value))
        elif tripped_name not in tripped:
            tripped.append(tripped_name)
        return result

    # ── 复位（15号文不变量：Owner 批准） ───────────────────────

    def reset_response(
        self,
        level: str | ResponseLevel,
        approver: str = "",
        agent_id: str = "",
        skill_ids: tuple[str, ...] = (),
    ) -> ResponseResult:
        """三级复位：approver 非空（Owner 批准）才执行，为空拒绝且状态零改变."""
        lvl = _level_value(level)
        approver_str = str(approver or "").strip()
        errors: dict[str, str] = {}
        actions: list[str] = []
        tripped: list[str] = []
        if not approver_str:
            errors["approver"] = "复位须 Owner 批准：approver 不能为空"
            result = self._result(False, lvl, approver="", errors=errors)
            self._trace("killswitch_response_reset", result, severity="info")
            return result
        try:
            if lvl == ResponseLevel.LEVEL_1.value:
                for skill_id in skill_ids:
                    self._call_orchestrator(
                        "reset",
                        f"skills_reset:{skill_id}",
                        errors,
                        "domain",
                        f"skills:{skill_id}",
                        approver_str,
                        actions=actions,
                        tripped=tripped,
                        tripped_name=f"skills:{skill_id}",
                    )
            elif lvl == ResponseLevel.LEVEL_2.value:
                if self._system_switch is None:
                    errors["system_switch"] = "系统级单 Agent 阻断开关未注入"
                else:
                    try:
                        self._system_switch.owner_release_agent(agent_id)
                        actions.append(f"system_release_agent:{agent_id}")
                    except Exception as exc:  # noqa: BLE001
                        errors["system_switch"] = repr(exc)
            elif lvl == ResponseLevel.LEVEL_3.value:
                self._call_orchestrator(
                    "reset",
                    "system_reset:global",
                    errors,
                    "system",
                    "global",
                    approver_str,
                    actions=actions,
                    tripped=tripped,
                    tripped_name="system",
                )
            else:
                errors["level"] = f"未知响应级别: {level!r}"
        except Exception as exc:  # noqa: BLE001 — ERROR_CONTRACT：永不抛异常
            errors["response_layer"] = repr(exc)
        result = self._result(
            not errors,
            lvl,
            tripped=tripped,
            actions=actions,
            approver=approver_str,
            errors=errors,
        )
        self._trace("killswitch_response_reset", result, severity="info")
        return result

    # ── 收敛一致性（无「只停次要回路」） ───────────────────────

    def consistency_report(self) -> dict[str, Any]:
        """两级收敛状态一致性检查（委托编排器 check_consistency；永不抛异常）."""
        try:
            report = self._orchestrator.check_consistency()
            if isinstance(report, dict):
                return report
            return {"consistent": False, "errors": {"orchestrator": f"非法报告: {report!r}"}}
        except Exception as exc:  # noqa: BLE001
            return {"consistent": False, "errors": {"orchestrator": repr(exc)}}

    # ── KILLSWITCH.md 落盘（§3.13，变更写审计链） ─────────────

    def write_killswitch_md(self, path: str | Path, author: str) -> Path:
        """落盘 KILLSWITCH.md 并写 killswitch_md_change 审计事件；author 必填留痕."""
        author_str = str(author or "").strip()
        if not author_str:
            raise ValueError("write_killswitch_md 须署名：author 不能为空（审计链留痕）")
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_killswitch_md(), encoding="utf-8")
        self._trace(
            "killswitch_md_change",
            self._result(True, "", actions=[f"write_killswitch_md:{target.name}"]),
            severity="info",
            author=author_str,
            path=str(target),
        )
        return target

    # ── 内部实现 ──────────────────────────────────────────────

    @staticmethod
    def _result(
        success: bool,
        level: str,
        target_mode: str = "",
        tripped: list[str] | None = None,
        actions: list[str] | None = None,
        approver: str = "",
        errors: dict[str, str] | None = None,
    ) -> ResponseResult:
        return ResponseResult(
            success=success,
            level=level,
            target_mode=target_mode,
            tripped=tuple(tripped or ()),
            actions=tuple(actions or ()),
            approver=approver,
            errors=dict(errors or {}),
            event_id=uuid.uuid4().hex[:12],
            timestamp=datetime.now(UTC).isoformat(),
        )

    def _trace(
        self,
        event_type: str,
        result: ResponseResult,
        severity: str,
        incident: ResponseIncident | None = None,
        author: str = "",
        path: str = "",
    ) -> None:
        """动作留痕（16号文 §4.2 P0-1 统一事件 schema；IO 失败不阻断动作）."""
        try:
            record: dict[str, Any] = {
                "schema_version": SCHEMA_VERSION,
                "event_id": result.event_id,
                "timestamp": result.timestamp,
                "source_domain": SOURCE_DOMAIN,
                "event_type": event_type,
                "threat_category": "killswitch_response",
                "severity": severity,
                "session_id": "",
                "level": result.level,
                "target_mode": result.target_mode,
                "success": result.success,
                "actions": list(result.actions),
                "tripped": list(result.tripped),
                "errors": dict(result.errors),
            }
            if incident is not None:
                record["agent_id"] = incident.agent_id
                record["reason"] = incident.reason
                record["skill_ids"] = list(incident.skill_ids)
            if result.approver:
                record["approver"] = result.approver
            if author:
                record["author"] = author
            if path:
                record["path"] = path
            self._audit_path.parent.mkdir(parents=True, exist_ok=True)
            with self._audit_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as exc:
            logger.warning("killswitch_response_levels 审计留痕写入失败（动作仍生效）: %r", exc)


_KILLSWITCH_MD_TEMPLATE: Final[str] = """---
ttl: permanent
---

# KILLSWITCH.md — ZephyrAlpha AI Agent 紧急停止协议

> 真源：16号文 §3.4/§3.13（KILLSWITCH.md 开放标准 8 要素对标）+ 15号文 §3.4
> （两级编排与收敛规则）+ 00号文 §3.3（三级响应策略层语义）。
> 本文件由 MOD-AU-004 `killswitch_response_levels.render_killswitch_md()` 生成；
> 每次变更经 `write_killswitch_md(author=...)` 落盘并写审计链
> （.runtime/audit/killswitch_response_levels.jsonl，event_type=killswitch_md_change）。

## 1. 标准要素对标

| 要素 | 取值/对应 | 真源 |
|---|---|---|
| cost_limit_usd | 日 50 元预算上限（LSG L5 成本熔断参数源） | 16号文 §3.12 |
| error_rate_threshold | 行为异常评分阈值（行为基线检测） | 16号文 §3.10 |
| consecutive_failures | 执行链累计调用 >100 次告警（计全部 API 调用次数，超集覆盖） | 16号文 §3.12 |
| forbidden_files_actions | 工具白名单（HB-SEC-08） | 16号文 §3.13 |
| level_1_throttle | P1(high) → 暂降 IM 模式（严于标准降速） | 16号文 §3.4 |
| level_2_pause | P0(critical) → 暂停涉事 Agent（+通知） | 16号文 §3.4 |
| level_3_shutdown | global_critical → 全局暂停（完全停止+保存状态） | 16号文 §3.4 |

## 2. 三级响应定义（策略层，2026-08-18 Owner 裁定术语 Q7）

- **level_1（P1 high）**：自治降级 + 技能熔断。暂降 IM 模式——IM 模式 = 仅人工介入模式：
  Agent 可读取数据与执行查询，但一切修改操作需人工介入审批；IM 模式是运行时执行模式
  （动态覆盖后的实际约束状态），不是静态权限类别变更，告警解除后自动恢复。
  爆炸半径限单一 Agent，系统其余部分照常。
- **level_2（P0 critical）**：IM 模式基线上叠加暂停涉事 Agent
  （系统级总开关 VR-009 单 Agent 阻断粒度，不全局熔断）。
- **level_3（global_critical）**：IM 模式基线上叠加全局暂停——所有 Agent 暂停，
  仅 Trader 可操作；系统级全局熔断 + 交易级联动，收敛状态一致（无「只停次要回路」）。

## 3. 执行机构与路由

策略层（本文件语义）→ 路由层（MOD-AU-002 两级编排器，15号文 §3.4 四条收敛规则）
→ 执行机构层（5 套 Kill Switch：系统级 VR-009 / 交易五级 / 回滚三级 / 技能熔断 / 容量保障）。

## 4. 复位不变量（15号文）

任何级别复位均须 **Owner 批准**（approver 非空）；approver 为空拒绝执行且状态零改变。
系统级 TRIPPED 时域级一致生效，域级不可单独复位。
"""


__all__ = [
    "SCHEMA_VERSION",
    "SOURCE_DOMAIN",
    "TARGET_MODE_IM",
    "KillSwitchResponseLayer",
    "ResponseIncident",
    "ResponseLevel",
    "ResponseResult",
    "render_killswitch_md",
]
