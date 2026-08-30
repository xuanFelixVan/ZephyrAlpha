# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.redup_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); zephyr.clone_guard.engines.echo_guard_adapter (Finding); subprocess; json; shutil; logging; pathlib
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Adapter 模式——封装 reDUP CLI 调用，统一 detect() 接口；CLI 不可用时返回空 + degraded；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect() 永不抛异常——CLI 失败/超时/未安装返回 ([], degraded=True)
# [TESTS] tests/clone_guard/test_redup_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
RedupAdapter — reDUP 深度分析引擎适配器（Phase B 补齐）。

封装 reDUP CLI 的 scan 命令，对编排层暴露统一 detect() 接口。
reDUP 职责：六层语义克隆检测（T1/T2/T3/T4）+ 重构规划 + 影响评分 + 跨项目比较。
与 Echo-Guard 互补——Echo-Guard 主 T1/T2 AST 哈希，reDUP 强 T3/T4 语义克隆。

双模式（由 config.redup_mode 控制）：
  - "changed-only"（L1 pre-commit）：``redup scan <repo> --format json --changed-only --base-ref <ref> --min-sim <thr>``
  - "semantic"（L2 audit）：``redup scan <repo> --format json --semantic --semantic-threshold <thr>``

输出结构（真实，见 tests/fixtures/redup_sample.json）::

    {"project_path", "stats", "summary",
     "groups": [{"id", "type", "normalized_name", "similarity_score",
                 "occurrences", "saved_lines_potential", "impact_score",
                 "fragments": [{"file", "line_start", "line_end", "function_name", "class_name"}],
                 "metadata": {"actionability": "refactor|review|generated"}}],
     "refactor_suggestions": [{"group_id", "action", "new_module", "function_name", "rationale"}]}

每个 group 的 N 个 fragments → 生成 N-1 个 Finding（首 fragment 为 source，其余为 existing）。

降级策略（守 blueprint §5.2）：
  - reDUP 未安装 → degraded=True, 返回空列表
  - 超时 → degraded=True, 返回空列表
  - CLI 崩溃 → degraded=True, 返回空列表
  - 正常执行 → 返回 Finding 列表

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: repo_root 参数
#   fields: 参数 repo_root（无注解）
#   code: redup_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: redup_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RedupAdapter
#   name_en: RedupAdapter
#   intro: reDUP 深度分析引擎适配器。
#   desc: reDUP 深度分析引擎适配器。 封装 reDUP CLI 调用，对编排层暴露统一 detect() 接口。 引擎升级/替换不影响编排层（Adapter 模式）。；公共方法（定义序）: health_check, de…
#   inputs: repo_root config
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: RedupAdapter
#   downstream: zephyr.clone_guard.orchestrator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess  # noqa: bare-subprocess  reDUP CLI 调用需要 subprocess
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

logger = logging.getLogger(__name__)

__all__ = ["RedupAdapter"]

# reDUP metadata.actionability → CloneGuard severity 映射
# actionability 是 reDUP 自身对克隆组的处置建议，直接采信（验证后集成纪律）
_ACTIONABILITY_MAP: dict[str, str] = {
    "refactor": "extract",  # reDUP 建议重构提取 → 硬阻断（3+ 副本或高影响）
    "review": "review",  # reDUP 建议人工复核 → 警告（2 副本）
    "generated": "acknowledged",  # 已确认为生成代码 → 跳过
}


class RedupAdapter:
    """reDUP 深度分析引擎适配器。

    封装 reDUP CLI 调用，对编排层暴露统一 detect() 接口。
    引擎升级/替换不影响编排层（Adapter 模式）。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or CloneGuardConfig()

    def health_check(self) -> bool:
        """检查 reDUP 是否可用（CLI 存在）。reDUP 无需预建索引，scan 即时分析。"""
        return shutil.which("redup") is not None

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """检测给定文件的语义克隆。

        Args:
            files: 待检测文件路径列表（相对路径）。reDUP 的扫描范围由 --changed-only /
                --semantic 决定，files 仅用于空值守卫（空列表短路）。
            timeout: 超时秒数（None 时使用配置默认值）。

        Returns:
            (findings, degraded) 元组：
            - findings: Finding 列表（检测失败时为空列表）
            - degraded: True 表示 reDUP 不可用/超时/崩溃
        """
        if not files:
            return [], False

        if not self._config.redup_enabled:
            logger.debug("reDUP 已在配置中禁用，跳过检测")
            return [], True

        # 检查 CLI 可用性
        if shutil.which("redup") is None:
            logger.debug("RedupAdapter: reDUP CLI 未安装，跳过检测")
            return [], True

        timeout_sec = timeout or self._config.pre_commit_timeout_sec
        cmd = self._build_command()

        try:
            result = subprocess.run(  # noqa: bare-subprocess  reDUP CLI scan 调用
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
            )
        except FileNotFoundError:
            logger.warning("RedupAdapter degraded: reDUP CLI 未安装")
            return [], True
        except subprocess.TimeoutExpired:
            logger.warning("RedupAdapter degraded: reDUP scan 超时(%ds)", timeout_sec)
            return [], True
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("RedupAdapter degraded: reDUP scan 异常(%s: %s)", type(e).__name__, e)
            return [], True

        # reDUP exit codes: 0=无发现, 1=有发现, 其他=错误
        if result.returncode not in (0, 1):
            logger.warning(
                "RedupAdapter degraded: reDUP scan 退出码=%d, stderr=%s",
                result.returncode,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        # 解析 JSON 输出
        try:
            data = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError as e:
            logger.warning("RedupAdapter degraded: JSON 解析失败(%s)", e)
            return [], True

        findings = self._parse_findings(data)
        return findings, False

    def _build_command(self) -> list[str]:
        """构造 reDUP scan 命令（依据 config.redup_mode 选择 L1/L2 模式）。

        真实 CLI（核实自 semcod/redup）：
          redup scan <repo> --format json [--changed-only --base-ref <ref> --min-sim <thr>]
                                   [--semantic --semantic-threshold <thr>] [--max-groups <n>]
        """
        cmd: list[str] = ["redup", "scan", str(self._repo_root), "--format", "json"]
        if self._config.redup_mode == "semantic":
            # L2 全量语义模式
            cmd.extend(["--semantic", "--semantic-threshold", str(self._config.redup_min_sim)])
        else:
            # L1 changed-only 增量模式（默认）——需 --base-ref 指定对比基
            cmd.extend(
                [
                    "--changed-only",
                    "--base-ref",
                    self._config.redup_base_ref,
                    "--min-sim",
                    str(self._config.redup_min_sim),
                ]
            )
        # 限制组数（0=不限，由 fail_on_severity 判阻断）
        if self._config.redup_max_groups > 0:
            cmd.extend(["--max-groups", str(self._config.redup_max_groups)])
        return cmd

    def _parse_findings(self, data: dict) -> list[Finding]:
        """将 reDUP JSON 输出解析为 Finding 列表。

        解析 ``groups[]``，每个 group 的 N 个 fragments → N-1 个 Finding。
        ``refactor_suggestions`` 按 group_id 匹配，生成 import_suggestion。
        """
        groups = data.get("groups", []) or []
        if not isinstance(groups, list):
            return []

        # 建立 group_id → refactor_suggestion 索引
        suggestions: dict[str, dict] = {}
        for s in data.get("refactor_suggestions", []) or []:
            if isinstance(s, dict) and s.get("group_id"):
                suggestions[str(s["group_id"])] = s

        findings: list[Finding] = []
        for group in groups:
            try:
                findings.extend(self._parse_group(group, suggestions))
            except (KeyError, TypeError, ValueError, AttributeError) as e:
                gid = group.get("id", "?") if isinstance(group, dict) else "?"
                logger.debug("跳过无法解析的 reDUP group: %s (%s)", gid, e)
        return findings

    def _parse_group(self, group: dict, suggestions: dict[str, dict]) -> list[Finding]:
        """解析单个 group 为 N-1 个 Finding（首 fragment=source，其余=existing）。"""
        fragments = group.get("fragments", []) or []
        if len(fragments) < 2:
            return []  # 单 fragment 无克隆对

        group_id = str(group.get("id", ""))
        similarity = float(group.get("similarity_score", 0.0))
        clone_type = str(group.get("type", "unknown"))  # 透传 reDUP 的 type（exact/structural）
        occurrences = int(group.get("occurrences", len(fragments)))
        actionability = ""
        metadata = group.get("metadata") or {}
        if isinstance(metadata, dict):
            actionability = str(metadata.get("actionability", ""))

        severity = self._severity_for(actionability, occurrences, similarity)
        import_suggestion = self._build_import_suggestion(group_id, suggestions)

        source = fragments[0]
        source_file = self._to_relative_path(source.get("file", ""))
        source_function = str(source.get("function_name", "unknown"))
        source_lineno = int(source.get("line_start", 0))

        findings: list[Finding] = []
        for idx, existing in enumerate(fragments[1:], start=1):
            existing_file = self._to_relative_path(existing.get("file", ""))
            existing_function = str(existing.get("function_name", "unknown"))
            existing_lineno = int(existing.get("line_start", 0))

            finding_id = f"RD-{group_id}-{idx}" if group_id else f"RD-{source_file}-{existing_file}-{idx}"

            findings.append(
                Finding(
                    finding_id=finding_id,
                    severity=severity,
                    clone_type=clone_type,
                    similarity=similarity,
                    source_file=source_file,
                    source_function=source_function,
                    source_lineno=source_lineno,
                    existing_file=existing_file,
                    existing_function=existing_function,
                    existing_lineno=existing_lineno,
                    import_suggestion=import_suggestion,
                )
            )
        return findings

    @staticmethod
    def _severity_for(actionability: str, occurrences: int, similarity: float) -> str:
        """severity 判定——优先采信 reDUP 的 actionability，fallback 按副本数/相似度。"""
        if actionability in _ACTIONABILITY_MAP:
            return _ACTIONABILITY_MAP[actionability]
        # fallback：无 actionability 字段时按副本数 + 相似度推断
        if occurrences >= 3 or similarity >= 0.95:
            return "extract"  # 3+ 副本或极高相似 → 硬阻断
        return "review"  # 2 副本 → 警告

    @staticmethod
    def _build_import_suggestion(group_id: str, suggestions: dict[str, dict]) -> str | None:
        """从 refactor_suggestions 构造 import_suggestion（按 group_id 匹配）。"""
        if not group_id:
            return None
        sug = suggestions.get(group_id)
        if not sug:
            return None
        new_module = str(sug.get("new_module", "")).strip()
        function_name = str(sug.get("function_name", "")).strip()
        if not new_module or not function_name:
            return None
        # "src/validators.py" → "from src.validators import validate_input"
        module_path = new_module
        if module_path.endswith(".py"):
            module_path = module_path[:-3]
        module_path = module_path.replace("/", ".").replace("\\", ".")
        return f"from {module_path} import {function_name}"

    def _to_relative_path(self, file_path: str) -> str:
        """将绝对路径转为相对仓库根目录的路径（归一化斜杠）。"""
        try:
            p = Path(file_path)
            if p.is_absolute():
                rel = p.relative_to(self._repo_root)
                return str(rel).replace("\\", "/")
            return file_path.replace("\\", "/")
        except ValueError:
            return file_path.replace("\\", "/")
