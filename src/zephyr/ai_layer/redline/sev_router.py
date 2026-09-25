# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_sev_router
# [MODULE] zephyr.ai_layer.redline.sev_router
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.shared.utils.time_utils (now_utc)（信号供给=注入 provider，
#                上游已有模块：gov_audit.integrity.IntegrityVerifier.verify_chain（SEV-1）/
#                trading.trading_contracts.risk.trading_kill_switch（SEV-2）/
#                security.access_control.kill_switch（SEV-3）/
#                check_tick_duplication+sim 账本校验（SEV-4）——真源引用不复制）
# [CONSUMERS] OBJ_S 前端面板段落; OpsAlertFeed 通知板（发布器注入接线，批 S6）;
#             L6 切换段（SEV-1 停写降级只读建议消费方）; Owner 通知链
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] "项目安全"可度量定义（DESIGN §3）=四类探针观察窗内开放（未处置）事件数=0
#              且审计链验证绿（mismatch=0，known_loss 除外）——is_project_safe 机械判定；
#              零新建刹车：四类信号全部挂已有模块输出，本模块只做"聚合+分级路由"；
#              降档/告警类工具只产建议不动手（五永不触碰避让铁律）：SEV-1 熔断建议=
#              建议字段（KillSwitch manual_trip_global 调用权=纠察/Owner），SEV-2 原生动作
#              归 trading_kill_switch 五级自身（REDUCE_ONLY/.../AUTO_KILL 不经本模块），
#              SEV-3 BLOCK_AGENT=建议字段（record_event 由信号源侧执行）；发布器注入
#              （默认无发布=纯聚合；生产接线 OpsAlertFeed.publish）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §3
# [STABILITY] new
# [SAFETY] M（聚合路由面：建议+通知，不执行熔断/不停写/不改状态）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] provider 探针抛异常 → 该类记 1 条保守开放信号（fail-closed：探针坏了
#                  按"未验证"计数，不静默绿）；畸形 sev/负数 open_count 记跳过计数；
#                  aggregate/route 纯函数不落盘不外呼
# [TESTS] tests/ai_layer/redline/test_sev_router.py（四级事件样例各一聚合开放事件数/
#         项目安全=0 开放+链绿判定/探针异常保守计数/畸形 sev 跳过/分级路由动作字段/
#         建议不动手断言（route 不调 KillSwitch 不改状态）/发布器注入）
"""sev_router — SEV 探针聚合分级路由（OBJ_S 施工项 S6，DESIGN §3）。

四类安全事件 → 聚合成"开放事件数" → 分级路由（告警链+自动动作建议+Owner 通知）：

- SEV-1 审计断链：verify_chain mismatch>0（非 known_loss）/writer 停写超窗/era 覆盖缺口
  → 停写类操作降级只读（建议）+KillSwitch manual_trip_global（建议）+Owner 通知。
- SEV-2 资金异常：trading_kill_switch 五级任一触发/模拟盘组合回撤越 §4 降档线
  → 五级熔断原生动作（trading 侧自持，本模块只上行告警+Owner 通知，解锁=Owner）。
- SEV-3 权限逃逸：protected path 拒绝计数异常升/permission_boundary_probe 达阈值/
  env 白名单外密钥访问（S1 拒绝日志）/NL-2 命中 → BLOCK_AGENT（KillSwitch 原生级联）。
- SEV-4 数据损坏：判重异常率越限/CH 写失败率越限/sim 账本自愈校验不一致
  → 停写+restore 流程建议+RULE-DATA-OPS 三步验证复盘。

可度量定义：项目安全 = 开放事件数=0 且 verify_chain 绿。验收标准（红蓝 R1-F4）：
四级事件样例各一可聚合成"开放事件数"。
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Final

from zephyr.shared.utils.time_utils import now_utc

SEV1_AUDIT_CHAIN: Final = "sev1"
SEV2_FUNDS: Final = "sev2"
SEV3_PERMISSION: Final = "sev3"
SEV4_DATA: Final = "sev4"

SEV_CLASSES: Final[tuple[str, ...]] = (SEV1_AUDIT_CHAIN, SEV2_FUNDS, SEV3_PERMISSION, SEV4_DATA)

SEV_TITLES: Final[dict[str, str]] = {
    SEV1_AUDIT_CHAIN: "审计断链",
    SEV2_FUNDS: "资金异常",
    SEV3_PERMISSION: "权限逃逸",
    SEV4_DATA: "数据损坏",
}

# 分级路由动作建议表（DESIGN §3 表逐行编码；全部为"建议/上行"字段，执行权在原生系统）
ROUTE_ACTION_BY_SEV: Final[dict[str, str]] = {
    SEV1_AUDIT_CHAIN: "suggest_readonly_degrade+killswitch_trip_suggestion",
    SEV2_FUNDS: "defer_to_trading_five_level_native_actions",
    SEV3_PERMISSION: "block_agent_via_killswitch_record_event",
    SEV4_DATA: "suggest_stop_write_and_restore",
}

NotifyFunc = Callable[[dict[str, Any]], None]
ProbeFunc = Callable[[], Sequence["SevSignal"]]


@dataclass(frozen=True)
class SevSignal:
    """单条 SEV 信号（探针输出；open_count>0 且 is_open=True=存在未处置开放事件）。"""

    sev: str
    source: str
    open_count: int
    detail: str = ""
    is_open: bool = True


@dataclass(frozen=True)
class RouteDirective:
    """分级路由指令（建议+通知载荷，零状态变更）。"""

    sev: str
    open_count: int
    action: str
    notify_owner: bool = True
    notes: tuple[str, ...] = field(default_factory=tuple)


def aggregate_open_events(signals: Sequence[SevSignal]) -> dict[str, int]:
    """纯函数核：信号 → {sev1..sev4: 开放事件数}（畸形 sev/负数计数跳过留痕于 skipped）。"""
    open_events = {sev: 0 for sev in SEV_CLASSES}
    skipped = 0
    for signal in signals:
        if signal.sev not in SEV_CLASSES or signal.open_count < 0:
            skipped += 1
            continue
        if signal.is_open:
            open_events[signal.sev] += signal.open_count
    open_events["skipped"] = skipped
    return open_events


def is_project_safe(open_events: Mapping[str, int], *, chain_mismatch_count: int = 0) -> bool:
    """可度量定义（DESIGN §3）：四类开放事件数=0 且审计链验证绿（mismatch=0）。

    known_loss era 的 mismatch 由探针侧归零后传入（IntegrityVerifier 口径），
    本函数只看入参计数——不做 era 语义二次解释。
    """
    return all(open_events.get(sev, 0) == 0 for sev in SEV_CLASSES) and chain_mismatch_count == 0


def collect_signals(probes: Mapping[str, ProbeFunc]) -> tuple[list[SevSignal], dict[str, str]]:
    """跑全部探针 provider → (信号清单, 探针异常表)。

    探针抛异常 → 记 1 条保守开放信号（sev 取 probe key，fail-closed 不静默绿），
    异常表 {probe_key: 异常摘要} 供 Owner 通知面。
    """
    signals: list[SevSignal] = []
    errors: dict[str, str] = {}
    for probe_key, probe in probes.items():
        try:
            signals.extend(probe())
        except Exception as exc:  # noqa: BLE001 — 探针异常保守计数（ERROR_CONTRACT）
            errors[probe_key] = f"{type(exc).__name__}: {exc}"
            sev = probe_key if probe_key in SEV_CLASSES else SEV1_AUDIT_CHAIN
            signals.append(SevSignal(sev=sev, source=f"probe:{probe_key}", open_count=1, detail="probe error"))
    return signals, errors


def route_signals(
    signals: Sequence[SevSignal],
    *,
    probe_errors: Mapping[str, str] | None = None,
    notify: NotifyFunc | None = None,
) -> list[RouteDirective]:
    """分级路由：开放信号 → 指令清单（建议+Owner 通知；notify 注入时逐条发布）。"""
    open_events = aggregate_open_events(signals)
    directives: list[RouteDirective] = []
    for sev in SEV_CLASSES:
        count = open_events.get(sev, 0)
        if count <= 0:
            continue
        notes: list[str] = []
        if sev == SEV1_AUDIT_CHAIN:
            notes.append("建议：停写类操作降级只读；纠察行使 KillSwitch manual_trip_global 建议权")
        elif sev == SEV2_FUNDS:
            notes.append("五级熔断原生动作自持（REDUCE_ONLY/CANCEL_ALL+DISABLE_NEW/DISCONNECT/FULL_SHUTDOWN/AUTO_KILL）；解锁=Owner（资金域 high 门位）")
        elif sev == SEV3_PERMISSION:
            notes.append("建议：record_event→BLOCK_AGENT（KillSwitch 原生级联：≥3 agent→全局 TRIPPED）")
        else:
            notes.append("建议：停写+走 restore 流程（档 B 墓碑/备份可回切）；RULE-DATA-OPS 三步验证复盘")
        for probe_key, err in (probe_errors or {}).items():
            if probe_key == sev:
                notes.append(f"探针异常（保守计数）: {err}")
        directive = RouteDirective(
            sev=sev,
            open_count=count,
            action=ROUTE_ACTION_BY_SEV[sev],
            notify_owner=True,
            notes=tuple(notes),
        )
        directives.append(directive)
        if notify is not None:
            notify(
                {
                    "key": f"obj_s_sev_{sev}",
                    "severity": "critical" if sev in (SEV1_AUDIT_CHAIN, SEV2_FUNDS) else "warning",
                    "title": f"OBJ_S {SEV_TITLES[sev]}（SEV-{sev[-1]}）",
                    "message": f"开放事件 {count} 条；动作={directive.action}",
                    "source": "obj_s_sev_router",
                    "labels": {"sev": sev, "open_count": count},
                }
            )
    return directives


def sev_snapshot(
    signals: Sequence[SevSignal],
    *,
    chain_mismatch_count: int = 0,
) -> dict[str, Any]:
    """看板/周报快照：开放事件数分布+项目安全判定（S7 sev_incidents 字段来源）。"""
    open_events = aggregate_open_events(signals)
    skipped = open_events.pop("skipped", 0)
    return {
        "snapshot_at": now_utc().isoformat(),
        "sev_incidents": {sev: open_events.get(sev, 0) for sev in SEV_CLASSES},
        "chain_mismatch_count": chain_mismatch_count,
        "project_safe": is_project_safe(open_events, chain_mismatch_count=chain_mismatch_count),
        "skipped_signals": skipped,
    }
