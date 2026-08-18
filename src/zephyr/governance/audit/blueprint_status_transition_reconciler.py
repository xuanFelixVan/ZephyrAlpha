# [BLUEPRINT] MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §P1-d 蓝图状态单调推进检测

# [MODULE] zephyr.governance.audit.blueprint_status_transition_reconciler

# [DOMAIN] D_GOV_AUDIT

# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec, SQL_CREATE_DRIFT_AUDIT_FINDINGS, SQL_INSERT_DRIFT_AUDIT_FINDING); zephyr.governance.audit._git_helpers (git_show_file); stdlib (logging, os, re, sqlite3, uuid)

# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway

# [STARTUP] imported

# [MATURITY] production

# [INVARIANTS] post-commit 事件触发（仅当 staged .py 文件含 [STABILITY] 或 [MATURITY] 头部标记时触发）；reconciler 永不抛异常（异常降级为 warn）；只读 git show HEAD~1:path 获取旧版本（不修改工作区）；后向状态转换（如 stable→evolving, production→design）持久化到 governance.db drift_audit_findings 表（severity=HIGH）；正则提取头部标记（不解析整文件）；非 Zephyr 项目 skip [ARCH-MM-002 两档化]

# [MODIFY-GUARD] _GATE_ID / _PRIORITY / _STABILITY_ORDER / _MATURITY_ORDER

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] reconcile 永不抛异常——git/正则/DB 异常降级为 ReconcileResult(action="warn")

# [TESTS] tests/governance/audit/test_blueprint_status_transition_reconciler.py

# [A_module] module_id=MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable  # noqa: blueprint-amodule-cross-check [BLUEPRINT]==[A_module] same module

# [TTL] permanent

# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)

r"""

blueprint_status_transition_reconciler.py — 蓝图状态单调推进 reconciler（P1-d，2026-07-21）。



post-commit 事件触发，当 staged ``.py`` 文件含 ``[STABILITY]`` 或 ``[MATURITY]`` 头部

标记时，提取新版本（HEAD）与旧版本（HEAD~1）的 stability/maturity 值，检测后向

状态转换（即"降级"——如 ``stable→evolving`` / ``production→design``），命中则

warn 并持久化到 ``governance.db`` 的 ``drift_audit_findings`` 表（severity=HIGH）。



治本动机（第一性原理）

--------------------

12 维度审计 P1-d 维度："蓝图状态单调推进检测"——原属 uncovered-but-gatable。

STABILITY 词表（``stability_vocabulary.yaml``）定义单调推进序列：

``volatile → evolving → stable → frozen``，后向转换意味"降级"——通常是治本回退

或元数据失真（如 architecture_issue_registry.yaml 中记录的"5 个模块

[MATURITY] production→design"事件）。



post-commit reconciler 检测此类后向转换，warn + 持久化，AI 可查

``drift_audit_findings`` 表发现历史降级事件，追溯原因（治本回退？测试删除？

还是元数据漂移？）。



设计权衡

--------

1. **post-commit warn-only（非 block）**：后向转换可能是合法治本回退（如发现模块

   不达标，从 ``production`` 退回 ``design`` 重新打磨）。reconciler 无法区分

   "合法回退"vs"非法降级"。warn+持久化让 AI 后续可查，不阻断合法回退。

2. **正则提取头部标记**：``[STABILITY]`` / ``[MATURITY]`` 是文件头部注释标记，

   正则 ``^#\s*\[(STABILITY|MATURITY)\]\s*(\w+)`` 提取（不解析整文件 AST，

   快速且足够）。

3. **git show HEAD~1:path 获取旧版本**：post-commit 时 HEAD 已是新 commit，HEAD~1

   是旧版本。新增文件（无 HEAD~1）不检测（首次创建无漂移可言）。

4. **fail-open**：git/正则/DB 任一异常降级为 warn（不阻断，不丢日志）。

5. **priority=825**：晚于 blueprint_frontmatter(135)、cross_layer_contract(215)，

   在 workspace_hygiene(890) 之前——状态转换检测应在 frontmatter 同步之后

   （frontmatter 可能修改 STABILITY/MATURITY 字段，需先同步再检测）。



合法状态序列（单调推进，禁止后向）

----------------------------------

- STABILITY: ``volatile`` → ``evolving`` → ``stable`` → ``frozen``

- MATURITY: ``design`` → ``production`` [ARCH-MM-002 两档化]



后向转换（如 ``stable→evolving``, ``production→design``, ``frozen→stable``)

触发 warn + 持久化。



Usage

-----

::



    from zephyr.governance.audit.blueprint_status_transition_reconciler import (

        make_blueprint_status_transition_reconciler,

    )



    registry.register(make_blueprint_status_transition_reconciler(gateway))

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: post-commit 提交文件列表 committed_files
#   fields: 本次 commit 的 staged 文件路径列表
#   code: _reconcile(committed_files) L553
# - id: I2
#   name: 工作区新版源码头部标记
#   fields: [STABILITY]/[MATURITY] 值（HEAD 状态全文）
#   code: open(f) 读全文 L523-525
# - id: I3
#   name: HEAD~1 旧版源码
#   fields: 旧版本文件全文（含旧头部标记）
#   code: git_show_file(project_root, rel, "HEAD~1") L537
# - id: I4
#   name: 状态单调推进词表
#   fields: STABILITY volatile0-evolving1-stable2-frozen3；MATURITY design0-production1
#   code: _STABILITY_ORDER/_MATURITY_ORDER L193-215
# 层: 算法
# - id: A1
#   name_zh: ① commit 触发判定
#   name_en: _trigger
#   intro: 只读每个 .py 前 20 行，含 STABILITY/MATURITY 头部标记才触发
#   desc: _safe_relpath 归一化 + 读前 20 行 + _HEADER_RE 搜索；非 .py 与 OSError 跳过
#   inputs: I1
#   outputs: 是否触发 reconcile
# - id: A2
#   name_zh: ② 新旧版本头部标记提取
#   name_en: _extract_status_markers + _check_single_file_markers
#   intro: 正则提取新旧两版的 STABILITY/MATURITY 值，任一侧缺标记即跳过
#   desc: 正则 ^#\s*\[(STABILITY|MATURITY)\]\s*(\w+) 取首匹配；新增文件/无标记返回 None
#   inputs: I1 I2 I3
#   outputs: (rel, old_markers, new_markers) 三元组
# - id: A3
#   name_zh: ③ 后向降级转换检测
#   name_en: _detect_backward_transition + _check_field_transition
#   intro: 用词表序号比对，新值序号小于旧值即判降级
#   desc: order_map[new] < order_map[old] → 后向；值不在词表/同级/前向均不报
#   inputs: A2 I4
#   outputs: 降级描述字符串
#   invariant: 状态单调推进禁止后向
# - id: A4
#   name_zh: ④ 降级事件持久化
#   name_en: _persist_drift_finding
#   intro: 命中降级写 governance.db drift_audit_findings 表 severity=HIGH
#   desc: finding_id=bt-+uuid12，类型 BLUEPRINT_STATUS_BACKWARD；DB 异常仅记日志 fail-open
#   inputs: A3
#   outputs: drift_audit_findings 行记录
# - id: A5
#   name_zh: ⑤ reconcile 编排汇总
#   name_en: _reconcile
#   intro: 遍历全部提交文件按双字段检测，汇总为 warn/clean 结果
#   desc: STABILITY+MATURITY 双字段循环；detail 截断前 3 条；任何异常降级 warn 永不抛出
#   inputs: I1 A2 A3
#   outputs: ReconcileResult(action=warn/clean)
#   invariant: reconciler 永不抛异常
# 层: 输出
# - id: O1
#   name_zh: 对账结果 ReconcileResult
#   name_en: ReconcileResult
#   intro: warn=检出后向降级（gate_id=GATE-BLUEPRINT-STATUS-TRANSITION），clean=无降级
#   downstream: GitCommitGateway MOD-INF-035
# - id: O2
#   name_zh: 降级事件数据库记录
#   name_en: drift_audit_findings 记录
#   intro: 后向转换历史落库，供 AI 事后追溯降级原因
#   downstream: governance.db drift_audit_findings 表（AI 查询）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# I3 --> A2
# A2 --> A3
# I4 --> A3
# A3 --> A4
# A3 --> A5
# A1 --> A5
# A4 --> O2
# A5 --> O1
"""



from __future__ import annotations

import logging
import os
import re
import sqlite3
import uuid
from pathlib import Path

from zephyr.governance.audit._git_helpers import git_show_file
from zephyr.governance.audit.reconciliation_registry import (
    SQL_CREATE_DRIFT_AUDIT_FINDINGS,
    SQL_INSERT_DRIFT_AUDIT_FINDING,
    ReconcileResult,
    ReconcilerSpec,
)
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)



_GATE_ID = "GATE-BLUEPRINT-STATUS-TRANSITION"

# priority=825: 晚于 cross_layer_contract(215)，早于 workspace_hygiene(890)

_PRIORITY = 825



# STABILITY 单调推进序列（stability_vocabulary.yaml 真源）

# 索引越大表示越稳定；后向转换（new_index < old_index）触发 warn

_STABILITY_ORDER: dict[str, int] = {

    "volatile": 0,

    "evolving": 1,

    "stable": 2,

    "frozen": 3,

}



# MATURITY 单调推进序列（maturity_vocabulary.yaml 真源）

_MATURITY_ORDER: dict[str, int] = {

    "design": 0,

    "production": 1,

}



# 头部标记正则：匹配 `# [STABILITY] evolving` 或 `# [MATURITY] production`（ARCH-MM-002 两档化）

_HEADER_RE = re.compile(r"^#\s*\[(STABILITY|MATURITY)\]\s*(\w+)", re.MULTILINE)





def _extract_status_markers(source: str) -> dict[str, str]:

    """从源码头部提取 [STABILITY] 和 [MATURITY] 标记值。



    Args:

        source: Python 源码字符串。



    Returns:

        dict 如 ``{"STABILITY": "stable", "MATURITY": "production"}``；

        无标记返回空 dict（如非 Zephyr 项目文件）。

    """

    markers: dict[str, str] = {}

    for m in _HEADER_RE.finditer(source):

        key = m.group(1)

        value = m.group(2)

        # 只取第一次匹配（文件头标记，避免误匹配后续注释）

        if key not in markers:

            markers[key] = value

    return markers





def _detect_backward_transition(

    old_value: str,

    new_value: str,

    order_map: dict[str, int],

) -> bool:

    """检测状态转换是否为后向（降级）。



    Args:

        old_value: 旧状态值。

        new_value: 新状态值。

        order_map: 状态→序号映射（如 _STABILITY_ORDER）。



    Returns:

        True=后向转换（降级）；False=前向转换或同级或值不在词表中。

    """

    if old_value not in order_map or new_value not in order_map:

        # 值不在词表中（可能是 typo 或新词未登记），不报漂移（由其他 gate 检测）

        return False

    return order_map[new_value] < order_map[old_value]





def _persist_drift_finding(

    project_root: Path,

    file_path: str,

    field: str,

    old_value: str,

    new_value: str,

) -> None:

    """持久化状态降级到 governance.db drift_audit_findings 表。



    fail-open：DB 异常只记日志不抛出（reconciler 永不抛异常）。



    Args:

        project_root: 仓库根路径。

        file_path: 漂移文件相对路径。

        field: 字段名（STABILITY / MATURITY）。

        old_value: 旧值。

        new_value: 新值。

    """

    db_path = os.path.join(str(project_root), "data", "databases", "governance.db")

    try:

        conn = sqlite3.connect(db_path, timeout=30.0)

        try:

            conn.execute(SQL_CREATE_DRIFT_AUDIT_FINDINGS)

            finding_id = f"bt-{uuid.uuid4().hex[:12]}"

            detail = f"{field} 后向转换 {old_value}→{new_value}（疑似降级，需仲裁）"

            conn.execute(

                SQL_INSERT_DRIFT_AUDIT_FINDING,

                (finding_id, now_utc(),

                 "BLUEPRINT_STATUS_BACKWARD", "HIGH",

                 file_path, detail),

            )

            conn.commit()

        finally:

            conn.close()

    except Exception as e:  # noqa: BLE001 — fail-open

        logger.warning("blueprint_status_transition: persist finding failed: %s", e)





def make_blueprint_status_transition_reconciler(gateway: "object") -> ReconcilerSpec:

    """构造 GATE-BLUEPRINT-STATUS-TRANSITION post-commit 蓝图状态单调推进 reconciler。



    Args:

        gateway: GitCommitGateway 实例（用其 project_root）。



    Returns:

        ReconcilerSpec(gate_id=_GATE_ID, priority=_PRIORITY)。

        trigger 仅当 staged .py 文件含 [STABILITY] 或 [MATURITY] 头部标记时返回 True。

    """

    project_root = gateway.project_root



    def _safe_relpath(f: str) -> str:

        try:

            return os.path.relpath(f, str(project_root)).replace("\\", "/")

        except (ValueError, OSError):

            return f.replace("\\", "/")



    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:

            rel = _safe_relpath(f)

            if not rel.endswith(".py"):

                continue

            # 快速检查：只读文件前 20 行（BLUEPRINT 头部在前几行）

            try:

                with open(f, "r", encoding="utf-8", errors="replace") as fh:

                    head = "".join(fh.readline() for _ in range(20))

            except OSError:

                continue

            if _HEADER_RE.search(head):

                return True

        return False



    def _check_field_transition(

        rel: str,

        field: str,

        old_markers: dict[str, str],

        new_markers: dict[str, str],

        order_map: dict[str, int],

    ) -> str | None:

        """检测单个字段（STABILITY / MATURITY）的后向转换。



        Returns:

            后向转换描述字符串（命中时）；None=无后向转换或字段缺失。

        """

        if field not in new_markers or field not in old_markers:

            return None

        old_v = old_markers[field]

        new_v = new_markers[field]

        if old_v == new_v:

            return None

        if not _detect_backward_transition(old_v, new_v, order_map):

            return None

        _persist_drift_finding(project_root, rel, field, old_v, new_v)

        return f"{rel}: {field} {old_v}→{new_v}（后向降级）"



    def _check_single_file_markers(

        f: str,

    ) -> tuple[str, dict[str, str], dict[str, str]] | None:

        """读取单文件的新旧版本 status markers。



        Returns:

            (rel, old_markers, new_markers) 三元组（命中可比对时）；None=跳过

            （非 .py / 无新标记 / 新增文件 / 旧版本无标记）。

        """

        rel = _safe_relpath(f)

        if not rel.endswith(".py"):

            return None

        try:

            with open(f, "r", encoding="utf-8", errors="replace") as fh:

                new_source = fh.read()

        except OSError:

            return None

        new_markers = _extract_status_markers(new_source)

        if not new_markers:

            return None  # 无 STABILITY/MATURITY 标记，skip

        old_source = git_show_file(str(project_root), rel, "HEAD~1")

        if old_source is None:

            return None  # 新增文件，无旧版本可比对

        old_markers = _extract_status_markers(old_source)

        if not old_markers:

            return None  # 旧版本无标记（可能从未登记到已登记）

        return rel, old_markers, new_markers



    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        try:

            drift_details: list[str] = []

            for f in committed_files:

                markers = _check_single_file_markers(f)

                if markers is None:

                    continue

                rel, old_markers, new_markers = markers

                # 检测 STABILITY + MATURITY 后向转换（单文件可能两类都命中）

                for field, order_map in (

                    ("STABILITY", _STABILITY_ORDER),

                    ("MATURITY", _MATURITY_ORDER),

                ):

                    hit = _check_field_transition(

                        rel, field, old_markers, new_markers, order_map

                    )

                    if hit:

                        drift_details.append(hit)



            if drift_details:

                summary = "; ".join(drift_details[:3])

                if len(drift_details) > 3:

                    summary += f" (还有 {len(drift_details) - 3} 个文件)"

                return ReconcileResult(

                    action="warn",

                    detail=f"蓝图状态后向转换 {len(drift_details)} 处: {summary}",

                    gate_id=_GATE_ID,

                )

            return ReconcileResult(

                action="clean",

                detail="无蓝图状态后向转换",

                gate_id=_GATE_ID,

            )



        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常

            logger.warning("blueprint_status_transition: reconcile failed: %s", e)

            return ReconcileResult(

                action="warn",

                detail=f"blueprint_status_transition reconcile error: {e}",

                gate_id=_GATE_ID,

            )



    return ReconcilerSpec(

        gate_id=_GATE_ID,

        trigger=_trigger,

        reconcile=_reconcile,

        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),

    )

