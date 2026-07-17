# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.data_task_completeness_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); stdlib(subprocess, re, yaml)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] warn级——不阻断commit，只提醒新增任务配置fallback_sources; 只在tasks.yaml被修改时触发; 通过git diff HEAD检测新增task_id
# [MODIFY-GUARD] gate_id="DATA-TASK-COMPLETENESS"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 始终返回passed=True（warn级）; git diff失败->跳过检测; tasks.yaml解析失败->跳过检测
# [TESTS] tests/governance/commit_gates/test_data_task_completeness_gate.py
# [A_module] module_id=MOD-GOV-data_task_completeness_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""data_task_completeness_gate.py — 数据任务完整性门禁（warn 级，提醒型）

当 AI 在 tasks.yaml 新增任务时，检测是否配置了 fallback_sources。
未配置时发出警告（不阻断 commit），提醒 AI 为数据韧性配置副数据源。

设计理念（数据韧性三层机制 §4 门禁设计）：
  - warn 级而非 block 级：某些任务（如 tick_data）天然无副源，强制阻断会过度
  - 只检测新增任务：避免对历史遗留任务大量告警
  - 通过 git diff HEAD 精确识别新增的 task_id

病根（防御前移）
-----------------
- 数据韧性三层机制依赖 fallback_sources 配置
- AI 新增任务时容易遗漏 fallback_sources（认知盲区）
- 没有门禁提醒 → 遗漏直到数据源故障时才发现无 fallback → 数据缺失

治本方案
--------
warn 级门禁在 commit 时检测新增任务，提醒配置 fallback_sources。
不阻断 commit（某些任务确实无副源），但警告信息会出现在 commit 输出中，
形成"AI 增加表 → 门禁提醒 → AI 补充 fallback_sources"的闭环。

Usage::

    from zephyr.gov_enforcement.commit_gates.data_task_completeness_gate import make_data_task_completeness_gate

    registry.register(make_data_task_completeness_gate())
"""

from __future__ import annotations

import logging
import os
import re
import subprocess

import yaml

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_data_task_completeness_gate"]

# tasks.yaml 相对路径（相对 project_root）
_TASKS_YAML_REL = "src/zephyr/data/config/tasks.yaml"

# 匹配 git diff 中新增的 task_id 行
# 格式：+  - task_id: xxx
_NEW_TASK_ID_RE = re.compile(r"^\+\s+-\s+task_id:\s+(\S+)", re.MULTILINE)


def _extract_new_task_ids(diff_output: str) -> list[str]:
    """从 git diff 输出中提取新增的 task_id。

    Args:
        diff_output: git diff HEAD -- tasks.yaml 的输出。

    Returns:
        新增的 task_id 列表。
    """
    return _NEW_TASK_ID_RE.findall(diff_output)


def _load_tasks_yaml(project_root) -> list[dict]:
    """加载 tasks.yaml 的任务列表。

    Args:
        project_root: 项目根目录 Path。

    Returns:
        任务 dict 列表。文件不存在或解析失败时返回空列表。
    """
    tasks_path = project_root / _TASKS_YAML_REL
    if not tasks_path.is_file():
        return []
    try:
        with open(tasks_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("tasks", []) or []
    except (yaml.YAMLError, OSError) as e:
        logger.warning("tasks.yaml 解析失败: %s", e)
        return []


def _check_task_has_fallback(tasks: list[dict], task_id: str) -> bool:
    """检查指定 task_id 是否配置了 fallback_sources。

    Args:
        tasks: 任务列表。
        task_id: 要检查的任务标识。

    Returns:
        True=有 fallback_sources，False=无。
    """
    for task in tasks:
        if task.get("task_id") == task_id:
            fallback = task.get("fallback_sources")
            return bool(fallback) and len(fallback) > 0
    return True  # 找不到任务（可能已删除），不告警


def make_data_task_completeness_gate() -> GateSpec:
    """构造数据任务完整性门禁 GateSpec（warn 级，提醒型）。

    Returns:
        GateSpec(gate_id="DATA-TASK-COMPLETENESS", priority=78)。
        priority=78——在 ARCH-REFERENCE(75) 之后、TEST-SOURCE-CONSISTENCY(96) 之前。
        始终返回 passed=True（warn 级，不阻断 commit）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root

        # 1. 只在 tasks.yaml 被修改时触发
        tasks_yaml_abs = str(project_root / _TASKS_YAML_REL).replace("/", os.sep)
        tasks_yaml_modified = any(
            os.path.normpath(f) == os.path.normpath(tasks_yaml_abs)
            or f.endswith("tasks.yaml")
            for f in files
        )
        if not tasks_yaml_modified:
            return True, "no tasks.yaml change, skip"

        # 2. git diff HEAD 检测新增的 task_id
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD", "--", _TASKS_YAML_REL],
                capture_output=True,
                cwd=str(project_root),
                timeout=30,
                encoding="utf-8",
                errors="replace",
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            # git diff 失败不阻断（warn 级）
            logger.warning("git diff 失败，跳过检测: %s", e)
            return True, f"git diff failed, skip: {e}"

        if result.returncode != 0:
            return True, f"git diff returncode={result.returncode}, skip"

        diff_output = result.stdout or ""
        new_task_ids = _extract_new_task_ids(diff_output)

        if not new_task_ids:
            return True, "no new task_id in tasks.yaml"

        # 3. 检查新增任务是否有 fallback_sources
        tasks = _load_tasks_yaml(project_root)
        missing = [
            tid for tid in new_task_ids
            if not _check_task_has_fallback(tasks, tid)
        ]

        if not missing:
            return True, f"all {len(new_task_ids)} new task(s) have fallback_sources"

        # 4. warn 级——返回 True（不阻断），detail 包含警告
        warning = (
            f"WARN: {len(missing)} new task(s) missing fallback_sources: "
            f"{', '.join(missing)}. "
            f"数据韧性三层机制需要 fallback_sources 配置副数据源，"
            f"请考虑在 tasks.yaml 中为这些任务添加 fallback_sources 字段。"
        )
        logger.warning(warning)
        return True, warning

    return GateSpec(
        gate_id="DATA-TASK-COMPLETENESS", check=_check, priority=78
    )
