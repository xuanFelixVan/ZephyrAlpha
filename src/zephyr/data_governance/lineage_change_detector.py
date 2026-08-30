# [BLUEPRINT] MOD-DATA_GOV-010 | docs/03_modules/_domain_data_governance/lineage_change_detector/blueprint.md
# [MODULE] zephyr.data_governance.lineage_change_detector
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] 无（纯内存；与 core/lineage_tracker 边语义对齐；clock/notifier 全注入）
# [CONSUMERS] 运行时装配批（drift 检测器注册表挂载 / 下游依赖方通知路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 边=(source,target,transformation) 三元组词表闭合; 快照指纹 sha256 与边序无关; 改向配对按 source 分组确定性排序; 影响集合 DFS 结果排序去重; detect 后基线前进; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_governance/lineage_change_detector/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] LineageChangeError(占位 ZA-DATA-UNREGISTERED-LINEAGE-CHANGE)——空detector_id/非法边/自环/基线缺失时抛
# [TESTS] tests/data_governance/test_lineage_change_detector.py
# [A_module] module_id=MOD-DATA_GOV-010 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



lineage_change_detector — 血缘变更检测器（MOD-DATA_GOV-010）。

B10-02319（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATGOV-007，A1 M8-S07；
canonical 承接 CAND-DATGOV-012 归并）：血缘图快照 diff——周期快照（边集合
指纹）+ 新增/删除/**改向边**检测 + 下游影响集合计算（DFS）+ 变更报告生成 +
下游依赖方**通知回调**，接入 drift 检测器注册语义（detector_id/schedule 元
数据）。

查重分工（蓝图 §0）：core/lineage_tracker=血缘图本体（本件不复用其存储，仅
对齐 (source,target,transformation) 边语义做周期快照 diff）；本件不改图本
体，只消费边集合快照。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: detector_id 参数
#   fields: 参数 detector_id（无注解）
#   code: lineage_change_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: schedule 参数
#   fields: 参数 schedule（无注解）
#   code: lineage_change_detector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: lineage_change_detector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: notifier 参数
#   fields: 参数 notifier（无注解）
#   code: lineage_change_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LineageChangeDetector
#   name_en: LineageChangeDetector
#   intro: 血缘变更检测器（基线快照 + diff + DFS 影响集合 + 通知回调）。
#   desc: 血缘变更检测器（基线快照 + diff + DFS 影响集合 + 通知回调）。；公共方法（定义序）: detector_id, schedule, baseline, fingerprint_of, downstrea…
#   inputs: detector_id schedule clock notifier
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: LineageChangeDetector
#   downstream: 运行时装配批（drift 检测器注册表挂载 / 下游依赖方通知路由）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import hashlib
import logging
from dataclasses import dataclass
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "EdgeSnapshot",
    "LineageChangeDetector",
    "LineageChangeError",
    "LineageChangeReport",
    "RedirectedEdge",
]

#: 血缘边三元组 (source, target, transformation)
Edge = tuple[str, str, str]


class LineageChangeError(Exception):
    """血缘变更检测输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DATA-UNREGISTERED-LINEAGE-CHANGE。
    """


@dataclass(frozen=True)
class EdgeSnapshot:
    """周期快照：排序去重后的边集合 + sha256 指纹 + 采样时刻（frozen）。"""

    edges: tuple[Edge, ...]
    fingerprint: str
    taken_at: datetime.datetime


@dataclass(frozen=True)
class RedirectedEdge:
    """改向边：同 source 由 old_target 改向 new_target。"""

    source: str
    old_target: str
    new_target: str
    transformation: str = ""


@dataclass(frozen=True)
class LineageChangeReport:
    """变更报告（新增/删除/改向 + 下游影响集合 + 前后指纹，frozen）。"""

    detector_id: str
    detected_at: datetime.datetime
    added: tuple[Edge, ...]
    removed: tuple[Edge, ...]
    redirected: tuple[RedirectedEdge, ...]
    impacted_downstream: tuple[str, ...]
    fingerprint_before: str
    fingerprint_after: str


class LineageChangeDetector:
    """血缘变更检测器（基线快照 + diff + DFS 影响集合 + 通知回调）。"""

    def __init__(
        self,
        *,
        detector_id: str,
        schedule: str | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        notifier: Callable[[LineageChangeReport], None] | None = None,
    ) -> None:
        if not detector_id:
            raise LineageChangeError("detector_id 为空")
        self._detector_id = detector_id
        self._schedule = schedule
        self._clock = clock or datetime.datetime.now
        self._notifier = notifier
        self._baseline: EdgeSnapshot | None = None

    @property
    def detector_id(self) -> str:
        return self._detector_id

    @property
    def schedule(self) -> str | None:
        return self._schedule

    @property
    def baseline(self) -> EdgeSnapshot | None:
        return self._baseline

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(edges: Iterable[Edge]) -> tuple[Edge, ...]:
        """边集合校验 + 排序去重（确定性）。"""
        norm: set[Edge] = set()
        for edge in edges:
            if len(edge) != 3:
                raise LineageChangeError(f"非法边(须三元组): {edge!r}")
            source, target, transformation = edge
            if not source or not target:
                raise LineageChangeError(f"边端点为空: {edge!r}")
            if source == target:
                raise LineageChangeError(f"自环边非法: {source!r}")
            norm.add((source, target, transformation))
        return tuple(sorted(norm))

    @staticmethod
    def fingerprint_of(edges: Iterable[Edge]) -> str:
        """边集合指纹（sha256；与输入顺序无关）。"""
        norm = LineageChangeDetector._normalize(edges)
        h = hashlib.sha256()
        for source, target, transformation in norm:
            h.update(f"{source}->{target}|{transformation}\n".encode())
        return h.hexdigest()

    @staticmethod
    def downstream_impact(edges: Iterable[Edge], seeds: Iterable[str]) -> tuple[str, ...]:
        """下游影响集合：从 seeds 沿新图 DFS（迭代式，邻居按字典序，结果排序去重）。"""
        adjacency: dict[str, list[str]] = {}
        for source, target, _ in LineageChangeDetector._normalize(edges):
            adjacency.setdefault(source, []).append(target)
        for source in adjacency:
            adjacency[source].sort()
        impacted: set[str] = set()
        seed_set = set(seeds)
        for seed in sorted(seed_set):
            stack = list(adjacency.get(seed, ()))
            while stack:
                node = stack.pop()
                if node in impacted:
                    continue
                impacted.add(node)
                stack.extend(reversed(adjacency.get(node, ())))
        return tuple(sorted(impacted))

    # ── 快照与检测 ────────────────────────────────────────────────────────

    def take_snapshot(self, edges: Iterable[Edge]) -> EdgeSnapshot:
        """采集周期快照并设为基线。"""
        snap = EdgeSnapshot(
            edges=self._normalize(edges),
            fingerprint=self.fingerprint_of(edges),
            taken_at=self._clock(),
        )
        self._baseline = snap
        _log.debug("血缘快照: detector=%s edges=%d fp=%s", self._detector_id, len(snap.edges), snap.fingerprint[:12])
        return snap

    def detect(self, edges: Iterable[Edge]) -> LineageChangeReport:
        """diff 新边集合 vs 基线：新增/删除/改向 + 下游影响 + 通知 + 基线前进。"""
        if self._baseline is None:
            raise LineageChangeError("基线快照缺失（须先 take_snapshot）")
        new_edges = self._normalize(edges)
        old = set(self._baseline.edges)
        new = set(new_edges)
        added: set[Edge] = new - old
        removed: set[Edge] = old - new

        # 改向配对：按 source 分组；先剔除同 target 对（transformation 变更仍按
        # 删除+新增呈现），剩余按 (target,transformation) 排序索引配对。
        removed_by_src: dict[str, list[Edge]] = {}
        added_by_src: dict[str, list[Edge]] = {}
        for edge in removed:
            removed_by_src.setdefault(edge[0], []).append(edge)
        for edge in added:
            added_by_src.setdefault(edge[0], []).append(edge)
        redirected: list[RedirectedEdge] = []
        for source in sorted(removed_by_src.keys() & added_by_src.keys()):
            rem = sorted(removed_by_src[source], key=lambda e: (e[1], e[2]))
            add = sorted(added_by_src[source], key=lambda e: (e[1], e[2]))
            # pass 1：同 target 对（transform 更新）不属改向，保留在 added/removed
            rem_keep: list[Edge] = []
            add_keep: list[Edge] = []
            i = j = 0
            while i < len(rem) and j < len(add):
                if rem[i][1] == add[j][1]:
                    i += 1
                    j += 1
                elif rem[i][1] < add[j][1]:
                    rem_keep.append(rem[i])
                    i += 1
                else:
                    add_keep.append(add[j])
                    j += 1
            rem_keep.extend(rem[i:])
            add_keep.extend(add[j:])
            # pass 2：剩余索引配对为改向（多余者保留在 added/removed，下方统一重算）
            paired = min(len(rem_keep), len(add_keep))
            for k in range(paired):
                redirected.append(
                    RedirectedEdge(
                        source=source,
                        old_target=rem_keep[k][1],
                        new_target=add_keep[k][1],
                        transformation=add_keep[k][2],
                    )
                )
        # 重算最终 added/removed：剔除被配对为改向的边
        redirected_old = {(r.source, r.old_target) for r in redirected}
        redirected_new = {(r.source, r.new_target) for r in redirected}
        final_removed = tuple(sorted(e for e in removed if (e[0], e[1]) not in redirected_old))
        final_added = tuple(sorted(e for e in added if (e[0], e[1]) not in redirected_new))
        final_redirected = tuple(sorted(redirected, key=lambda r: (r.source, r.old_target, r.new_target)))

        seeds: set[str] = set()
        for edge in final_added + final_removed:
            seeds.add(edge[0])
            seeds.add(edge[1])
        for r in final_redirected:
            seeds.add(r.source)
            seeds.add(r.old_target)
            seeds.add(r.new_target)
        impacted = self.downstream_impact(new_edges, seeds)

        report = LineageChangeReport(
            detector_id=self._detector_id,
            detected_at=self._clock(),
            added=final_added,
            removed=final_removed,
            redirected=final_redirected,
            impacted_downstream=impacted,
            fingerprint_before=self._baseline.fingerprint,
            fingerprint_after=self.fingerprint_of(new_edges),
        )
        self._baseline = EdgeSnapshot(
            edges=new_edges, fingerprint=report.fingerprint_after, taken_at=report.detected_at
        )
        if self._notifier is not None and (final_added or final_removed or final_redirected):
            try:
                self._notifier(report)
            except Exception:  # noqa: BLE001 — 通知不阻断检测
                _log.exception("notifier 通知失败: detector=%s", self._detector_id)
        _log.info(
            "血缘变更: detector=%s +%d -%d ~%d impacted=%d",
            self._detector_id,
            len(final_added),
            len(final_removed),
            len(final_redirected),
            len(impacted),
        )
        return report
