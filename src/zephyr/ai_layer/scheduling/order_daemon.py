# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] zephyr.ai_layer.scheduling.order_daemon
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.scheduling.scheduling_events (SchedulingJournal/SchedulingEvent);
#                zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc);
#                zephyr.shared.infra.process_pool (is_pid_alive——belt 同款僵尸检测)
# [CONSUMERS] 排产值守入口（journal 唯一真源消费者，非施工会话所有——对标 belt 常驻消费者设计）;
#             zephyr.ai_layer.scheduling.dispatcher（dispatched 段消费 order_dispatch_due）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] events journal=唯一真源（红蓝 R1-B10 附带二裁定：watchdog 不扫目录，降级为 journal
#              补偿读指针——守护重启/漏事件时在队事件天然重放，last_read_offset 断点续读+截断回卷守卫）；
#              单例锁 PID+TTL 600s+僵尸检测（belt_daemon 机械照用，作用对象=journal）；
#              零定时器零轮询（胜者到达事件触发 process_once，宪法 §9.3）；§2.1 映射表全实现；
#              必填机检任一缺失=held_incomplete+堵点本，禁静默降级；criteria_hash 缺失/不匹配=拒派
#              （L4 §2.3① 指名义务）；工单生成器对 definition_of_done 只读引用（附录 C #5 自我放大闸）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md §2.1（字段映射表=契约真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] journal 消费失败→事件保留 attempts+1（重试跨唤醒）；锁被持=让位（返回 yielded）；
#                  锁设施异常=放弃本轮（fail-safe）；evidence 必要键缺失→ValueError（emit 层白名单先行）；
#                  堵点本写入 OSError→上抛（不静默丢告警）
# [TESTS] tests/ai_layer/scheduling/test_order_daemon.py（order_id 格式/映射表全字段/必填机检
#         held_incomplete/criteria_hash 缺失不匹配拒派/单例锁让位与僵尸接管/offset 断点续读/
#         堵点本 append 形态；全部 tmp_path 注入零生产路径）
# [TTL] permanent
"""order_daemon — L5 工单生成守护：胜者证据包→任务书自动套模板（D-L5-02）。

事件源（红蓝 R1 裁定）：胜者落库即 emit ``evolution_winner_due``（SchedulingJournal）→ 本守护
只消费 journal（尾随+last_read_offset 断点续读），无常驻轮询无 cron。watchdog 双通道合并裁定：
不独立扫 winners/ 目录，降级为 journal 的**补偿读指针**——守护重启/漏事件时在队事件天然重放
（消费=成功才出队的事务语义），offset 另担截断/回卷守卫。

字段映射表（DESIGN §2.1，胜者证据包→任务书附录 A schema v0）逐字段在
:func:`build_task_order` 实现；``provenance`` 独立字段=真待 Owner（L5-#3，附录级变更），
本版按 DESIGN 两可方案退化为 objective 内嵌引用（experiment_id/evidence_ref 进 objective 尾注）。
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Final, Mapping

from zephyr.ai_layer.scheduling.scheduling_events import (
    KIND_EVOLUTION_WINNER_DUE,
    SchedulingJournal,
)
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "LOCK_NAME",
    "LOCK_TTL_SECONDS",
    "SCHEMA_VERSION",
    "OrderDaemonError",
    "next_order_id",
    "build_task_order",
    "missing_required_fields",
    "check_criteria_hash",
    "append_bottleneck",
    "OrderDaemon",
]

LOCK_NAME: Final = "order_daemon.lock"
LOCK_TTL_SECONDS: Final = 600.0  # belt_daemon 同款 TTL
OFFSET_NAME: Final = "last_read_offset.json"
DEFAULT_LEDGER: Final = REPO_ROOT / ".runtime" / "audit" / "bottleneck_ledger.jsonl"
SCHEMA_VERSION: Final = "0.1"
ORDER_ID_PREFIX: Final = "WO"

Sink = Callable[[dict[str, Any]], dict[str, Any]]


class OrderDaemonError(Exception):
    """工单生成契约违约（必填证据键缺失/裁决词表外）。"""


def next_order_id(day: str, seq: int) -> str:
    """纯函数：WO-YYYYMMDD-NNN（全局唯一由日期+当日序号构成，seq 从 1 起）。"""
    return f"{ORDER_ID_PREFIX}-{day}-{seq:03d}"


def _require_winner_evidence(evidence: Mapping[str, Any]) -> None:
    """必填三元校验（verdict/domain_id/evidence_ref）。"""
    required = ("verdict", "domain_id", "evidence_ref")
    missing_evidence = [k for k in required if not evidence.get(k)]
    if missing_evidence:
        raise OrderDaemonError(f"evidence_missing_keys:{','.join(missing_evidence)}")


def _build_definition_of_done(experiment_id: str, criteria_hash: str) -> dict[str, Any]:
    """DoD 块：判据引用 + L6 回执字段白名单。"""
    return {
        "criteria_ref": f"{experiment_id}#{criteria_hash}" if experiment_id else "",
        "l6_receipt_fields": [
            "work_order_id",
            "module_id",
            "challenger_branch",
            "criteria_yaml_ref",
            "criteria_hash",
            "domain",
            "tier_action",
        ],
    }


def _build_red_lines(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """红线块：champion 冻结/永不触碰清单/域禁改。"""
    return {
        "champion_freeze": f"champion_ref={evidence.get('champion_ref') or ''} 反查 depgraph 文件清单冻结（老组不动）",
        "never_touch": "附录 C 永不触碰清单",
        "domain_forbidden": [],
    }


def _build_budget(dispatch: Mapping[str, Any], compute_class: str, resource_class: str, policy: Mapping[str, Any]) -> dict[str, Any]:
    """预算块：时限/算力档/提交帽/子代理配额。"""
    return {
        "timebox_hours": int(dispatch["timebox_by_class_hours"].get(resource_class, 4)),
        "compute_class": compute_class,
        "max_commits": int(dispatch["max_commits"]),
        "subagent_quota": int(policy["quota"]["q2_subagent_max"]),
    }


def build_task_order(
    evidence: Mapping[str, Any],
    policy: Mapping[str, Any],
    order_seq: int,
    day: str,
    pre_rulings: list[dict[str, Any]] | None = None,
    owner_gate: bool = False,
) -> dict[str, Any]:
    """纯函数：胜者证据包→任务书（DESIGN §2.1 字段映射表逐行实现）。

    :param evidence: evolution_winner_due payload（verdict/domain_id/evidence_ref 必填已由
                     journal 白名单保证；experiment_id/criteria_hash/significance/starred/
                     title/labor_killed/card_id/champion_ref/compute_class 可选）
    :param policy: schedule_gate_policy 加载产物（dispatch/compute_classes 节消费）
    :param order_seq: 当日工单序号（从 1 起）
    :param day: YYYYMMDD（now_utc 由调用方取，本函数零取时）
    :param pre_rulings: ruling_registry 按域预查命中项（调用方注入，生成器只读引用）
    :param owner_gate: 分流器判定（router.route 产物）
    """
    _require_winner_evidence(evidence)
    dispatch = policy["dispatch"]
    compute_class = str(evidence.get("compute_class") or "local")
    resource_class = policy["compute_classes"]["e0_class_to_resource"].get(compute_class, "light")
    experiment_id = str(evidence.get("experiment_id") or "")
    criteria_hash = str(evidence.get("criteria_hash") or "")
    title = str(evidence.get("title") or evidence.get("mechanism") or "").strip()
    objective = str(
        evidence.get("objective")
        or f"{evidence.get('mechanism') or title}（利弊对照见证据包 {evidence['evidence_ref']}）"
    ).strip()
    if not experiment_id:
        # 库外对象（verdict='win' 直达）无 experiment 卡：objective 内嵌引用兜底（L5-#3 两可方案）
        objective = f"{objective} [source_event=evolution_winner_due card_id={evidence.get('card_id') or 'n/a'}]"
    review_tier = str(dispatch["reviewer_model_tier"])
    return {
        "schema_version": str(dispatch["schema_version"]),
        "order_id": next_order_id(day, order_seq),
        "title": title,
        "domain_id": str(evidence["domain_id"]),
        "contractor": {"session": "", "model_tier": "pending_dispatch", "lane": "B4"},
        "objective": objective,
        "definition_of_done": _build_definition_of_done(experiment_id, criteria_hash),
        "red_lines": _build_red_lines(evidence),
        "budget": _build_budget(dispatch, compute_class, resource_class, policy),
        "pre_rulings": list(pre_rulings or []),
        "acceptance": {
            "mechanical": ["own_scope", "gate_green", "regression_green"],
            "reviewer": {"session": "异会话", "model_tier": review_tier},
            "owner_gate": bool(owner_gate),
        },
        "rollback": {"plan": "worktree abort（施工失败回切，champion 不动）", "l6_ref": "L6 回切引用"},
        "constitution_discipline": {"discipline": "宪法 L0 十二硬规则全程适用；工单禁改验收判据（附录 C #5）"},
        "honesty_clause": {"clause": "进度/失败如实回执；禁静默降级禁谎报"},
        "experiment_id": experiment_id,
        "criteria_hash": criteria_hash,
        "significance": str(evidence.get("significance") or ""),
        "labor_killed": str(evidence.get("labor_killed") or ""),
        "starred": str(evidence.get("verdict")) == "win_starred",
        "state": "pending",
        "audit_log": [
            {"ts": "", "action": "order_created", "detail": f"source={evidence['evidence_ref']}"}
        ],
    }


def missing_required_fields(order: Mapping[str, Any]) -> list[str]:
    """纯函数：必填字段机检（附录 A"机检 gate 校验必填"同款）。任一缺失=held_incomplete。"""
    missing: list[str] = []
    for key in ("order_id", "title", "objective", "domain_id"):
        if not str(order.get(key) or "").strip():
            missing.append(key)
    dod = order.get("definition_of_done") or {}
    if not str(dod.get("criteria_ref") or "").strip():
        missing.append("definition_of_done.criteria_ref")
    for key in ("red_lines", "budget", "acceptance"):
        body = order.get(key)
        if not isinstance(body, Mapping) or not body:
            missing.append(key)
    return missing


def check_criteria_hash(criteria_ref: str, frozen_hash: str) -> tuple[bool, str]:
    """纯函数：criteria_hash 机检（缺失/不匹配=拒派，L4 §2.3① 指名义务）。

    :param criteria_ref: experiment_id#criteria_hash 锚点
    :param frozen_hash: experiment 卡 frozen 值（调用方查库注入；空串=卡缺席）
    """
    if "#" not in criteria_ref:
        return False, "criteria_ref_missing_hash"
    stated = criteria_ref.split("#", 1)[1].strip()
    if not stated:
        return False, "criteria_hash_missing"
    if not frozen_hash:
        return False, "frozen_hash_absent"
    if stated != frozen_hash:
        return False, "criteria_hash_mismatch"
    return True, "ok"


def append_bottleneck(ledger_path: Path, record: Mapping[str, Any]) -> None:
    """堵点本 append（{ts, kind, order_id, reason, protocol:'专人专事'} 实档 schema 同款）。"""
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(dict(record), ensure_ascii=False)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


class OrderDaemon:
    """工单生成守护：journal 唯一真源消费 + 单例锁 + 断点续读（belt 机械照用）。"""

    def __init__(
        self,
        journal: SchedulingJournal,
        policy: Mapping[str, Any],
        *,
        ledger_path: Path | None = None,
        lock_dir: Path | None = None,
        sink: Sink | None = None,
    ) -> None:
        self.journal: Final = journal
        self.policy: Final = policy
        self.ledger_path: Final = ledger_path or DEFAULT_LEDGER
        self.lock_path: Final = (lock_dir or journal.state_dir) / LOCK_NAME
        self.offset_path: Final = journal.state_dir / OFFSET_NAME
        self._sink: Final = sink  # 工单持久化 sink（缺省=dry-run 只回执不落库）

    # ── 单例锁（belt_daemon 机械照用：PID+TTL 600s+僵尸检测）─────────────────
    def _acquire_singleton(self) -> bool:
        try:
            import zephyr.shared.infra.process_pool as pp  # noqa: PLC0415

            if self.lock_path.exists():
                data = json.loads(self.lock_path.read_text(encoding="utf-8"))
                pid = int(data.get("pid") or 0)
                ts = float(data.get("ts") or 0.0)
                if pid > 0 and pp.is_pid_alive(pid) and (time.monotonic() - ts) < LOCK_TTL_SECONDS:
                    return False
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)
            self.lock_path.write_text(
                json.dumps({"pid": os.getpid(), "ts": time.monotonic()}), encoding="utf-8"
            )
            return True
        except Exception:  # noqa: BLE001——锁设施异常=放弃本轮启动（fail-safe，belt 同款）
            log.warning("order_daemon 单例锁异常", exc_info=True)
            return False

    def _release_singleton(self) -> None:
        try:
            self.lock_path.unlink(missing_ok=True)
        except OSError:
            pass

    # ── 断点续读（补偿读指针：截断/回卷守卫）───────────────────────────────
    def _read_offset(self) -> int:
        if not self.offset_path.exists():
            return 0
        try:
            return int(json.loads(self.offset_path.read_text(encoding="utf-8")).get("offset") or 0)
        except (OSError, json.JSONDecodeError, ValueError):
            return 0

    def _checkpoint_offset(self) -> int:
        """记录 journal 当前字节长度（消费后检查点）；截断/回卷时回卷为 0 并告警。"""
        try:
            size = self.journal.journal_path.stat().st_size if self.journal.journal_path.exists() else 0
        except OSError:
            size = 0
        prior = self._read_offset()
        if size < prior:
            log.warning("journal 截断/回卷（offset %s > size %s），回卷重读", prior, size)
            size = 0
        self.journal.state_dir.mkdir(parents=True, exist_ok=True)
        self.offset_path.write_text(
            json.dumps({"offset": size, "ts": now_utc().isoformat()}, ensure_ascii=False),
            encoding="utf-8",
        )
        return size

    # ── 胜者→工单（evolution_winner_due 消费体）───────────────────────────
    def handle_winner(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """evolution_winner_due → 建单 + 必填机检；缺字段=held_incomplete+堵点本（禁静默降级）。"""
        now = now_utc()
        order = build_task_order(
            payload,
            self.policy,
            order_seq=1,
            day=now.strftime("%Y%m%d"),
            pre_rulings=[],
            owner_gate=False,
        )
        # 序号冲突由 sink 落库时裁决（全局唯一约束）；此处单事件生成立即可机检
        missing = missing_required_fields(order)
        if missing:
            order["state"] = "held_incomplete"
            order["held_reason"] = f"missing:{','.join(missing)}"
            append_bottleneck(
                self.ledger_path,
                {
                    "ts": now.isoformat(),
                    "kind": "held_incomplete",
                    "order_id": order["order_id"],
                    "reason": f"必填机检缺失:{','.join(missing)}",
                    "protocol": "专人专事：高模型维护班清账",
                },
            )
        if self._sink is not None:
            self._sink(order)
        return {"order_id": order["order_id"], "state": order["state"], "missing": missing}

    def process_once(self, max_events: int = 20) -> dict[str, Any]:
        """单轮消费（事件触发调用，非轮询）：单例锁→drain→offset 检查点→放锁。"""
        if not self._acquire_singleton():
            return {"yielded": True, "reason": "singleton_lock_held"}
        try:
            self._read_offset()  # 断点续读守卫（截断回卷在 _checkpoint_offset 内处置）
            receipt = self.journal.drain(max_events=max_events, handler=self._route_event)
            receipt["read_offset"] = self._checkpoint_offset()
            return receipt
        finally:
            self._release_singleton()

    def _route_event(self, raw: dict[str, Any]) -> dict[str, Any]:
        """journal drain 路由：winner→建单；其余 kind 交 journal 缺省消费体（回执线留痕）。"""
        kind = str(raw.get("kind") or "")
        if kind == KIND_EVOLUTION_WINNER_DUE:
            return self.handle_winner(dict(raw.get("payload") or {}))
        return self.journal.default_handler(raw)
