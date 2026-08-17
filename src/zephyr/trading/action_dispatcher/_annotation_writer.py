# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §5.150.7
# [MODULE] MOD-INF-035 | zephyr.trading.action_dispatcher._annotation_writer
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.action_dispatcher (facade module: _facade_mod.REPO_ROOT/_BRAIN_MARKER/_read_text/ActionReport; facade ref: _extract_module_name/_find_module_file/_find_capability_card/_find_blueprint_file/_find_file_by_name/_version_backup/_build_py_brain_block/_insert_brain_block/_update_brain_block)
# [CONSUMERS] zephyr.trading.action_dispatcher.ActionDispatcher.__init__ (构造 _annotation 实例)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 注释写入器——annotate_py_file/tag_module/annotate_blueprint；通过 facade ref 访问 patchable 实例方法以支持 patch.object(d, "_method", ...) 测试；文件不存在/无 tags/无 points→skipped；内容不变→skipped
# [MODIFY-GUARD] 公共方法 annotate_py_file/tag_module/annotate_blueprint 签名变更需同步 facade thin wrapper 与测试
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件不存在/无法读取→skipped/error；dry_run 模式不写盘；yaml.safe_load 失败降级为空 dict
# [TESTS] tests/action/test_action_dispatcher.py (TestActionDispatcherAnnotatePyFile + TestActionDispatcherTagModule)
# [A_module] module_id=MOD-INF-035 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

注释注解写入器（从 ActionDispatcher._annotate_py_file/_tag_module/_annotate_blueprint 提取）。

职责簇：Python 文件 BRAIN 注释、YAML capability card 标签、Blueprint 摘要。
通过 facade 引用访问 patchable 实例方法（_extract_module_name/_find_module_file/_version_backup 等）。
通过 _facade_mod 访问 patchable 模块级常量（REPO_ROOT/_BRAIN_MARKER/_read_text）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 推理结果与原文
#   fields: source_text 原文 / result 字典（category、names、tags、result.points）
#   code: annotate_py_file L49 / tag_module L86 / annotate_blueprint L131 函数参数
# - id: I2
#   name: facade 可补丁方法与模块常量
#   fields: _extract_module_name/_find_module_file/_build_py_brain_block 等实例方法 + REPO_ROOT/_BRAIN_MARKER/_read_text/ActionReport
#   code: _facade_mod 引用 L33
# 层: 算法
# - id: A1
#   name_zh: ① Python 文件 BRAIN 注释写入
#   name_en: AnnotationWriter.annotate_py_file
#   intro: 把分类/命名结果写进目标 .py 文件的 # BRAIN 注释块
#   desc: 提取模块名→定位文件→按 field 构建 brain_block→已有标记则更新否则插入→内容不变跳过→版本备份后写盘（dry_run 不写）
#   inputs: I1 I2
#   outputs: ActionReport(modified/skipped/error)
#   invariant: 文件不存在/无法读取/内容不变 → skipped 或 error；dry_run 不落盘
# - id: A2
#   name_zh: ② capability card 标签补全
#   name_en: AnnotationWriter.tag_module
#   intro: 把新标签去重后合并进 YAML 卡片的 brain_tags 字段
#   desc: 找 capability card→yaml.safe_load（失败降级空 dict）→与现有 tags/brain_tags 求差集→yaml.dump 写回→备份后落盘
#   inputs: I1 I2
#   outputs: ActionReport(modified/skipped/error)
#   invariant: 空 tags/无卡片/全部已存在 → skipped
# - id: A3
#   name_zh: ③ Blueprint 摘要同步
#   name_en: AnnotationWriter.annotate_blueprint
#   intro: 把摘要要点写成 blueprint YAML 顶部的 # brain-summary 注释行
#   desc: 找 blueprint（回退 architecture_model 目录）→无要点跳过→正则替换旧摘要块或前置插入→备份后写盘
#   inputs: I1 I2
#   outputs: ActionReport(modified/skipped/error)
#   invariant: 无 points/蓝图不存在/内容不变 → skipped
# 层: 输出
# - id: O1
#   name_zh: 动作执行报告
#   name_en: ActionReport
#   intro: target/capability/status/detail 四元组，回给外观层聚合统计
#   downstream: ActionDispatcher 外观 MOD-INF-035（[CONSUMERS] 头：构造 _annotation 实例）
# - id: O2
#   name_zh: 磁盘文件副作用
#   name_en: file writes
#   intro: .py 的 BRAIN 块、capability card 的 brain_tags、blueprint 的 brain-summary 注释
#   downstream: 无下游/内部使用（直接写盘，经 _version_backup 留版本链）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I2 --> A1
# I2 --> A2
# I2 --> A3
# A1 --> O1
# A2 --> O1
# A3 --> O1
# A1 --> O2
# A2 --> O2
# A3 --> O2
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.trading.action_dispatcher import ActionDispatcher

from zephyr.trading import action_dispatcher as _facade_mod

_log = logging.getLogger(__name__)


class AnnotationWriter:
    """注释注解写入器。

    负责三类注解操作：Python 文件 BRAIN 注释块写入、YAML capability card 标签补全、
    Blueprint 摘要同步。
    """

    def __init__(self, dry_run: bool, facade: ActionDispatcher | None = None) -> None:
        self._dry_run = dry_run
        self._facade = facade

    def annotate_py_file(self, source_text: str, result: dict, field: str = "category"):
        """将分类/命名结果写入 Python 文件的 BRAIN 注释块。"""
        # Use facade methods (patchable in tests)
        module_name = self._facade._extract_module_name(source_text)
        py_file = self._facade._find_module_file(module_name)
        if py_file is None:
            return _facade_mod.ActionReport(
                module_name, "task_classification", "skipped", f"file not found for: {module_name}"
            )

        original = _facade_mod._read_text(py_file)
        if original is None:
            return _facade_mod.ActionReport(module_name, "task_classification", "error", "cannot read file")

        if field == "category":
            value = result.get("category", "unknown")
            brain_block = self._facade._build_py_brain_block({"classification": value, **result})
        elif field == "names":
            names = result.get("names", [])
            brain_block = self._facade._build_py_brain_block({"naming_candidates": names})
        else:
            value = str(result.get(field, result))
            brain_block = self._facade._build_py_brain_block({"brain_tag": value})

        if _facade_mod._BRAIN_MARKER in original:
            new_content = self._facade._update_brain_block(original, brain_block)
        else:
            new_content = self._facade._insert_brain_block(original, brain_block)

        if new_content == original:
            return _facade_mod.ActionReport(module_name, "task_classification", "skipped", "unchanged")

        self._facade._version_backup(py_file)
        if not self._dry_run:
            py_file.write_text(new_content, encoding="utf-8")

        _log.info("BrainHands: %s <- %s=%s", py_file.name, field, str(value)[:60])
        return _facade_mod.ActionReport(py_file.name, "task_classification", "modified", f"{field}={str(value)[:40]}")

    def tag_module(self, source_text: str, result: dict):
        """将标签补全到模块的 capability card YAML 中。"""
        module_name = self._facade._extract_module_name(source_text)
        tags = result.get("tags", [])
        if not tags:
            return _facade_mod.ActionReport(module_name, "tag_completion", "skipped", "empty tags")

        card_file = self._facade._find_capability_card(module_name)
        if card_file is None:
            return _facade_mod.ActionReport(module_name, "tag_completion", "skipped", "no card found")

        content = _facade_mod._read_text(card_file)
        if content is None:
            return _facade_mod.ActionReport(module_name, "tag_completion", "error", "cannot read card")

        import yaml

        try:
            data = yaml.safe_load(content)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            data = {}

        if not isinstance(data, dict):
            data = {}

        existing_tags = set(data.get("tags", []) or [])
        brain_tags = data.get("brain_tags", []) or []
        new_tags = [t for t in tags if t not in existing_tags and t not in brain_tags]
        if not new_tags:
            return _facade_mod.ActionReport(module_name, "tag_completion", "skipped", "all tags exist")

        brain_tags.extend(new_tags)
        data["brain_tags"] = brain_tags

        new_yaml = yaml.dump(data, allow_unicode=True, sort_keys=False)
        if not new_yaml.endswith("\n"):
            new_yaml += "\n"

        self._facade._version_backup(card_file)
        if not self._dry_run:
            card_file.write_text(new_yaml, encoding="utf-8")

        _log.info("BrainHands: %s +tags=%s", card_file.name, new_tags)
        return _facade_mod.ActionReport(
            card_file.name, "tag_completion", "modified", f"added {len(new_tags)} tags: {new_tags}"
        )

    def annotate_blueprint(self, source_text: str, result: dict):
        """将摘要同步到模块的 blueprint YAML 中。"""
        module_name = self._facade._extract_module_name(source_text)
        bp_file = self._facade._find_blueprint_file(module_name)
        if bp_file is None:
            bp_file = self._facade._find_file_by_name(module_name, [_facade_mod.REPO_ROOT / "architecture_model"])

        points = result.get("result", {}).get("points", [])
        if not points:
            return _facade_mod.ActionReport(module_name, "summary_extraction", "skipped", "no points")

        if bp_file is None:
            return _facade_mod.ActionReport(module_name, "summary_extraction", "skipped", "blueprint not found")

        original = _facade_mod._read_text(bp_file)
        if original is None:
            return _facade_mod.ActionReport(module_name, "summary_extraction", "error", "cannot read")

        summary_block = "\n".join(f"# brain-summary: {p}" for p in points)
        summary_block += f"\n# brain-summary-generated: {datetime.now(UTC).isoformat()}\n"

        if "# brain-summary:" in original:
            new_content = re.sub(
                r"(?:# brain-summary:.*\n)*# brain-summary-generated:.*\n?",
                summary_block,
                original,
            )
        else:
            new_content = summary_block + "\n" + original

        if new_content == original:
            return _facade_mod.ActionReport(module_name, "summary_extraction", "skipped", "unchanged")

        self._facade._version_backup(bp_file)
        if not self._dry_run:
            bp_file.write_text(new_content, encoding="utf-8")

        _log.info("BrainHands: %s <- summary (%d points)", bp_file.name, len(points))
        return _facade_mod.ActionReport(
            bp_file.name, "summary_extraction", "modified", f"added {len(points)} summary points"
        )
