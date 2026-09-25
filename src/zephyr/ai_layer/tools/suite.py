# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_tools
# [MODULE] zephyr.ai_layer.tools.suite
# [DOMAIN] D_GOVERNANCE
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md §3.5
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] （见正文/DESIGN）
# [TESTS] tests/ai_layer/（对应段测试目录）
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.tools (ORGANS/ToolBenchError); zephyr.ai_layer.tools.scoring
#                (PolicyConstants/TaskOutcome/judge_pair/aggregate_organ/load_policy_constants);
#                zephyr.shared.utils.time_utils (now_utc); zephyr.shared.io.paths (REPO_ROOT);
#                docs/_working/ai_layer_vision/OBJ_T_tools/tool_benchmark_suite_v0.yaml（考卷真源）;
#                config/tool_exam_policy.yaml（判据常量真源，draft 提案稿）
# [CONSUMERS] L4 comparator.venue_tool_bench（RULER 指针预期契约 suite_criteria()/suite_run；
#             指针改接=后续授权批一处常量改动，接线现状见包 docstring）;
#             T3 转正流（基准实测子集消费，设计预留）; T4 配对（pairing_record 消费面，挂起 H1）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 考卷真源=OBJ_T 目录 YAML（L4 §2.1 契约兑现："基准任务集真源=OBJ_T 目录"），
#              本件只装载校验不自造题（D-L4-01 对偶：考尺不自产考卷）;
#              fail-closed：考卷/判据缺文件、sha256 不匹配、schema 违例一律 SuiteError 拒考
#              （调不到考卷=拒考是 C4 验收标准）;
#              哈希锁：criteria_sha256=canonical JSON{version,seed,tasks} sha256，装载即重算比对
#              （L4 公平性机检消费；改题=哈希变=须换 task_suite_version）;
#              陷阱题机制：trap⇒red_line（结构校验强制），红线题不过=整体 fail（DESIGN §3.5），
#              全对且含陷阱题=too_good_suspect 置旗（喂 L4 G3 三查，本件不定罪）;
#              执行面注入：suite_run 的 runner/champion_runner 必须由调用方注入，缺席=拒跑
#              （零真实外呼入单测；同版本双跑制式=OBJ_M dual_run 骨架复用，判据 Tier B）;
#              version 锁：payload.suite_version != 考卷版本=拒跑（同版本双跑，fairness 同源）;
#              policy 现状=draft 提案稿（OBJ_T-#1 避让：治理层资产 AI 只有提案权，正式化走
#              OBJ_R）——所有产出携带 policy_status 痕，禁当正式考纲消费
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md §3（考卷/判据真源；
#                改题先改 DESIGN 提案再走 OBJ_R；本件结构校验词表随 §2.1/§3 同步）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 考卷/判据缺文件或 schema 违例→SuiteError（fail-closed 拒考）；
#                  criteria_sha256 不匹配→SuiteError（哈希锁）；version 不匹配→SuiteError；
#                  runner 未注入→SuiteError:runner_not_injected（fail-closed 拒跑，非静默空跑）；
#                  runner 单题抛异常→该题记 failed+note 留痕（记账不炸，一场考完整记账）
# [TESTS] tests/ai_layer/tools/test_suite.py（装载校验全枚举/哈希锁/陷阱⇒红线结构强制/
#         venue 契约形态 criteria()["venue"]/version 锁/runner 注入双跑判分红线 fail/
#         runner 异常记账不炸/缺 runner 拒跑——全部 tmp_path 假考卷零真实外呼）
"""suite — T2 工具基准考尺：考卷装载（fail-closed）+venue_tool_bench 契约对齐（C3/C4）。

设计真源：``docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md`` §3（考卷 21 题真源落
OBJ_T 目录 YAML）+L4 DESIGN §2.1 工具行（同基准任务集版本双跑，判成功率/速度/成本，
小样本 Tier B 诚实条款）。

venue_tool_bench 指针契约（对齐验收，本件形态即指针接通后的被调面）::

    suite_criteria() -> {venue: "venue_tool_bench", task_suite_version, criteria_sha256,
                         organ_composition, trap_task_ids, policy_status, criteria_constants}
    suite_run({tool_ref, suite_version, ...}, runner=..., champion_runner=...)
        -> L4 格式证据包（organ_score+wilson 全宽+verdict+too_good_suspect）

考纲现状（诚实声明）：考卷与判据常量均为**提案稿**（OBJ_T-#1 治理立案避让，AI 不持尺）
——本件全部产出携带 policy_status=draft / suite_status=draft 痕；正式化走 OBJ_R 四步流水线。
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Callable, Final, Mapping, Sequence

import yaml

from zephyr.ai_layer.tools import ORGANS, ToolBenchError
from zephyr.ai_layer.tools.scoring import (
    PolicyConstants,
    TaskOutcome,
    aggregate_organ,
    judge_pair,
    load_policy_constants,
)
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__: Final = [
    "SuiteError",
    "DEFAULT_SUITE_PATH",
    "DEFAULT_POLICY_PATH",
    "SUITE_ID",
    "load_suite",
    "suite_criteria",
    "suite_run",
]

SUITE_ID: Final = "venue_tool_bench"
DEFAULT_SUITE_PATH: Final = (
    REPO_ROOT / "docs" / "_working" / "ai_layer_vision" / "OBJ_T_tools" / "tool_benchmark_suite_v0.yaml"
)
DEFAULT_POLICY_PATH: Final = REPO_ROOT / "config" / "tool_exam_policy.yaml"
_TASK_REQUIRED: Final = ("task_id", "organ", "task_desc", "criteria", "criteria_kind")
_CRITERIA_KINDS: Final = ("mechanical", "review")
RunnerFn = Callable[[Mapping[str, Any]], Mapping[str, Any]]


class SuiteError(ToolBenchError):
    """考尺失败（fail-closed：考卷/判据缺文件、schema/哈希/version 违例、runner 缺席）。"""


def _canonical_payload(doc: Mapping[str, Any]) -> str:
    """哈希锁输入域：{task_suite_version, seed, tasks} canonical JSON（键序稳定）。"""
    payload = {
        "task_suite_version": doc.get("task_suite_version"),
        "seed": doc.get("seed"),
        "tasks": doc.get("tasks"),
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)


def _validate_tasks(tasks: Any) -> list[dict[str, Any]]:
    """考卷结构校验（fail-closed；陷阱⇒红线结构强制；organ/判据词表校验）。"""
    if not isinstance(tasks, list) or not tasks:
        raise SuiteError("考卷 tasks 缺席或空（禁空考卷）")
    seen: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise SuiteError("考卷 task 非映射")
        missing = [k for k in _TASK_REQUIRED if not str(task.get(k) or "").strip()]
        if missing:
            raise SuiteError(f"task 缺字段 {missing}: {task.get('task_id')!r}")
        tid = str(task["task_id"])
        if tid in seen:
            raise SuiteError(f"task_id 重复: {tid}")
        seen.add(tid)
        if task["organ"] not in ORGANS:
            raise SuiteError(f"organ 词表外: {tid}:{task['organ']}")
        if task["criteria_kind"] not in _CRITERIA_KINDS:
            raise SuiteError(f"criteria_kind 词表外: {tid}:{task['criteria_kind']}")
        if task.get("trap") and not task.get("red_line"):
            raise SuiteError(f"陷阱题必须红线题(trap⇒red_line): {tid}")
    return tasks


def load_suite(path: Path = DEFAULT_SUITE_PATH) -> dict[str, Any]:
    """装载考卷（fail-closed）：schema 校验+criteria_sha256 重算比对（哈希锁）。"""
    if not path.is_file():
        raise SuiteError("考卷缺文件", details={"path": str(path)})
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SuiteError(f"考卷 YAML 畸形: {exc}") from exc
    if not isinstance(doc, dict):
        raise SuiteError("考卷结构畸形（非映射）")
    if doc.get("doc_type") != "benchmark_suite":
        raise SuiteError(f"doc_type 非考卷: {doc.get('doc_type')!r}")
    if not str(doc.get("task_suite_version") or "").strip():
        raise SuiteError("缺 task_suite_version")
    if doc.get("seed") is None:
        raise SuiteError("缺 seed（可复现制式，DESIGN §3.1）")
    tasks = _validate_tasks(doc.get("tasks"))
    recomputed = hashlib.sha256(_canonical_payload(doc).encode("utf-8")).hexdigest()
    recorded = str(doc.get("criteria_sha256") or "")
    if recorded != recomputed:
        raise SuiteError(f"criteria_sha256 不匹配（改题须换版本）: recorded={recorded[:12]}…")
    doc["tasks"] = tasks
    return doc


def load_policy(path: Path = DEFAULT_POLICY_PATH) -> PolicyConstants:
    """装载判据常量（fail-closed；真源=config/tool_exam_policy.yaml，现=draft 提案稿）。"""
    if not path.is_file():
        raise SuiteError("判据常量缺文件", details={"path": str(path)})
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SuiteError(f"判据常量 YAML 畸形: {exc}") from exc
    if not isinstance(doc, dict):
        raise SuiteError("判据常量结构畸形（非映射）")
    return load_policy_constants(doc)


def suite_criteria(
    *, suite_path: Path = DEFAULT_SUITE_PATH, policy_path: Path = DEFAULT_POLICY_PATH
) -> dict[str, Any]:
    """考卷快照（venue_tool_bench 契约面：criteria()["venue"]==VENUE_ID，考尺建成即生效）。"""
    doc = load_suite(suite_path)
    consts = load_policy(policy_path)
    organ_comp: dict[str, int] = {organ: 0 for organ in ORGANS}
    trap_ids: list[str] = []
    for task in doc["tasks"]:
        organ_comp[str(task["organ"])] += 1
        if task.get("trap"):
            trap_ids.append(str(task["task_id"]))
    return {
        "venue": SUITE_ID,
        "task_suite_version": doc["task_suite_version"],
        "criteria_sha256": doc["criteria_sha256"],
        "suite_status": str(doc.get("status") or "unknown"),
        "organ_composition": organ_comp,
        "trap_task_ids": trap_ids,
        "policy_status": consts.policy_status,
        "criteria_constants": {
            "effect_win_pp": consts.effect_win_pp,
            "noninferior_pp": consts.noninferior_pp,
            "min_judgeable_n": consts.min_judgeable_n,
            "wilson_z": consts.wilson_z,
        },
    }


def _run_side(
    tasks: Sequence[Mapping[str, Any]], runner: RunnerFn, side: str
) -> list[TaskOutcome]:
    """单方执行面：逐题调注入 runner，异常/坏返回记 failed 留痕（记账不炸，一场考完整）。"""
    outcomes: list[TaskOutcome] = []
    for task in tasks:
        tid = str(task["task_id"])
        passed, note, latency, cost = False, "", None, None
        try:
            res = runner(task)
            if isinstance(res, Mapping):
                passed = bool(res.get("passed", False))
                note = str(res.get("note", "") or "")
                raw_lat = res.get("latency_s")
                raw_cost = res.get("cost_usd")
                latency = float(raw_lat) if isinstance(raw_lat, (int, float)) else None
                cost = float(raw_cost) if isinstance(raw_cost, (int, float)) else None
            else:
                note = f"bad_runner_return:{type(res).__name__}"
        # 单题翻车记账不炸（DESIGN 工具层故障不伤数据）
        except Exception as exc:  # noqa: BLE001
            passed, note = False, f"runner_exception:{type(exc).__name__}:{exc}"
        outcomes.append(TaskOutcome(
            task_id=tid, passed=passed, is_red_line=bool(task.get("red_line")),
            latency_s=latency, cost_usd=cost, note=f"[{side}]{note}",
        ))
    return outcomes


def suite_run(
    payload: Mapping[str, Any],
    runner: RunnerFn | None = None,
    champion_runner: RunnerFn | None = None,
    *,
    suite_path: Path = DEFAULT_SUITE_PATH,
    policy_path: Path = DEFAULT_POLICY_PATH,
    secondary_not_worse: bool = True,
) -> dict[str, Any]:
    """同版本双跑记账（venue_tool_bench op=suite_run 的被调面；L4 §2.1 制式）。

    :param payload: {tool_ref, suite_version[, organ]}——suite_version 与考卷不符=拒跑。
    :param runner: 挑战方执行面（注入；缺席=SuiteError 拒跑，零真实外呼）。
    :param champion_runner: 冠军同场重考执行面（缺席=只出成绩不出裁决）。
    :param secondary_not_worse: 非劣保留的时延/成本不劣旗（DESIGN §3.5 第 4 行）。
    :returns: L4 格式证据包（task_suite_version/criteria_sha256/organ 聚合/wilson/verdict）。
    """
    doc = load_suite(suite_path)
    consts = load_policy(policy_path)
    tool_ref = str(payload.get("tool_ref") or "").strip()
    if not tool_ref:
        raise SuiteError("payload 缺 tool_ref")
    suite_version = str(payload.get("suite_version") or "").strip()
    if suite_version != str(doc["task_suite_version"]):
        raise SuiteError(f"suite_version 不匹配: {suite_version!r}!={doc['task_suite_version']!r}")
    if runner is None:
        raise SuiteError("runner_not_injected:实跑执行面须注入（fail-closed 拒跑）")
    organ = payload.get("organ")
    tasks = [t for t in doc["tasks"] if organ is None or t["organ"] == organ]
    if not tasks:
        raise SuiteError(f"organ 无可判题: {organ!r}")
    outcomes = _run_side(tasks, runner, "challenger")
    suite_has_trap = any(t.get("trap") for t in doc["tasks"])
    by_organ: dict[str, list[TaskOutcome]] = {}
    for out in outcomes:
        organ_of = next(str(t["organ"]) for t in tasks if str(t["task_id"]) == out.task_id)
        by_organ.setdefault(organ_of, []).append(out)
    aggregates = {
        org: aggregate_organ(organ_outcomes, suite_has_trap=suite_has_trap, consts=consts)
        for org, organ_outcomes in sorted(by_organ.items())
    }
    verdict_block: dict[str, Any] = {"verdict": None, "reason": "champion_not_run:同场重考缺席"}
    if champion_runner is not None:
        champion_outcomes = _run_side(tasks, champion_runner, "champion")
        verdict_block = judge_pair(outcomes, champion_outcomes, consts=consts,
                                   secondary_not_worse=secondary_not_worse)
    overall_too_good = all(a["too_good_suspect"] for a in aggregates.values()) if aggregates else False
    overall_fail = any(a["red_line_violation"] for a in aggregates.values())
    return {
        "venue": SUITE_ID,
        "op": "suite_run",
        "tool_ref": tool_ref,
        "task_suite_version": doc["task_suite_version"],
        "criteria_sha256": doc["criteria_sha256"],
        "suite_status": str(doc.get("status") or "unknown"),
        "policy_status": consts.policy_status,
        "organ_scores": aggregates,
        "verdict": verdict_block,
        "red_line_violation": overall_fail,
        "too_good_suspect": overall_too_good,
        "recorded_at": now_utc().isoformat(),
        "notes": "考卷/判据均为提案稿（OBJ_T-#1 避让），产出禁当正式考纲结论消费",
    }
