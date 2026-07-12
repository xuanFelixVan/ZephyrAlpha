# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.ai_construction_detectors
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.gov_drift.drift_models
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detector_core/bridges/__init__.py; tests/ai/test_ai_construction_detectors.py (+3 more)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] AI施工检测不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_ai_construction_detectors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §

Drift Detector AI 施工检测器 — ai_construction_detectors.py

module_id: MOD-INF-023 (SRC-0032)

AI 生成代码的质量/安全检测：幻觉导入、死代码、损坏逻辑、重复功能、

会话风格漂移、知识污染、跨会话修复冲突。

从 drift_engine.py 提取，对标 blueprint.md §5.1。"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime

from .drift_models import DriftEvent, DriftState


def _read_single_source(fp: str) -> tuple[str, str] | None:
    try:
        with open(fp, encoding="utf-8") as fh:
            return (os.path.basename(fp), fh.read())
    except (UnicodeDecodeError, OSError):
        return None


def _batch_read_module_sources(module_dir: str) -> dict[str, str]:
    sources: dict[str, str] = {}
    if not os.path.isdir(module_dir):
        return sources
    file_paths = [
        os.path.join(module_dir, f) for f in os.listdir(module_dir) if f.endswith(".py") and f != "__init__.py"
    ]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_read_single_source, fp): fp for fp in file_paths}
        for future in as_completed(futures):
            result = future.result()
            if result:
                sources[result[0]] = result[1]
    return sources


class AIConstructionDetectors:
    def detect_ai_hallucination_import(self, module_dir: str) -> list[DriftEvent]:
        """检测 AI 幻觉导入 — 导入不存在或无法解析的模块。





        扫描目录下所有 .py 文件，对每个 import / from-import 使用


        ``importlib.util.find_spec`` 验证模块是否真实存在。跳过


        标准库、相对导入和 ``__future__``/``builtins`` 等安全前缀。





        Args:


            module_dir: 待扫描的 Python 模块目录路径。





        Returns:


            list[DriftEvent]: 每个幻觉导入对应一个 DETECTED 状态的事件。


        """

        events: list[DriftEvent] = []

        if not os.path.isdir(module_dir):
            return events

        stdlib = sys.stdlib_module_names if hasattr(sys, "stdlib_module_names") else set()
        safe_prefixes = ("__future__", "builtins")

        sources = _batch_read_module_sources(module_dir)
        for fname, source in sources.items():
            try:
                tree = ast.parse(source, filename=fname)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split(".")[0]

                        if top in stdlib or top.startswith(".") or top.startswith(safe_prefixes):
                            continue

                        if importlib.util.find_spec(top) is None:
                            events.append(
                                DriftEvent(
                                    event_id=uuid.uuid4(),
                                    module_id="MOD-INF-023",
                                    detector_id="ai_hallucination_import",
                                    drift_dimension="AI_import_hallucination",
                                    baseline_version="0.1.0",
                                    state=DriftState.DETECTED,
                                    created_at=datetime.now(UTC),
                                    updated_at=datetime.now(UTC),
                                    resolution_detail=f"Hallucinated import: {alias.name} in {fname}",
                                )
                            )

                if isinstance(node, ast.ImportFrom):
                    if node.module is None:
                        continue

                    if node.level and node.level > 0:
                        continue

                    top = node.module.split(".")[0]

                    if top in stdlib or top in ("__future__",):
                        continue

                    if importlib.util.find_spec(top) is None:
                        events.append(
                            DriftEvent(
                                event_id=uuid.uuid4(),
                                module_id="MOD-INF-023",
                                detector_id="ai_hallucination_import",
                                drift_dimension="AI_import_hallucination",
                                baseline_version="0.1.0",
                                state=DriftState.DETECTED,
                                created_at=datetime.now(UTC),
                                updated_at=datetime.now(UTC),
                                resolution_detail=f"Hallucinated from import: {node.module} in {fname}",
                            )
                        )

        return events

    def detect_ai_dead_code(self, module_dir: str) -> list[DriftEvent]:
        """检测 AI 死代码 — 函数体或类体仅含 ``pass``/``...``。





        遍历目录下所有 .py 文件，收集顶层函数/类定义，将正文只有


        ``pass`` 或 ``Ellipsis`` 的函数和类标记为死代码。





        Args:


            module_dir: 待扫描的 Python 模块目录路径。





        Returns:


            list[DriftEvent]: 每个死代码定义对应一个 DETECTED 状态的事件。


        """

        events: list[DriftEvent] = []

        if not os.path.isdir(module_dir):
            return events

        defined_classes: set[str] = set()

        defined_funcs: set[str] = set()

        sources = _batch_read_module_sources(module_dir)
        for fname, source in sources.items():
            try:
                tree = ast.parse(source, filename=fname)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    defined_classes.add(node.name)

                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_"):
                        defined_funcs.add(node.name)

                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and all(
                    isinstance(s, ast.Pass)
                    or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is Ellipsis)
                    for s in node.body
                ):
                    events.append(
                        DriftEvent(
                            event_id=uuid.uuid4(),
                            module_id="MOD-INF-023",
                            detector_id="ai_dead_code",
                            drift_dimension="AI_dead_code",
                            baseline_version="0.1.0",
                            state=DriftState.DETECTED,
                            created_at=datetime.now(UTC),
                            updated_at=datetime.now(UTC),
                            resolution_detail=f"Dead code: {node.name}() body is only pass/... in {fname}",
                        )
                    )

                if isinstance(node, ast.ClassDef) and all(
                    isinstance(s, ast.Pass)
                    or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is Ellipsis)
                    for s in node.body
                ):
                    events.append(
                        DriftEvent(
                            event_id=uuid.uuid4(),
                            module_id="MOD-INF-023",
                            detector_id="ai_dead_code",
                            drift_dimension="AI_dead_code",
                            baseline_version="0.1.0",
                            state=DriftState.DETECTED,
                            created_at=datetime.now(UTC),
                            updated_at=datetime.now(UTC),
                            resolution_detail=f"Dead code: class {node.name} body is only pass/... in {fname}",
                        )
                    )

        return events

    def detect_ai_broken_logic(self, module_dir: str) -> list[DriftEvent]:
        """检测 AI 损坏逻辑 — 高 TODO 密度或上下文截断信号。





        两个检测维度：


        1. 单文件中 TODO 注释占比 >5% -> 未完成逻辑过多。


        2. 函数参数 >5 但函数体行数 <3 -> AI 生成时的上下文截断痕迹。





        Args:


            module_dir: 待扫描的 Python 模块目录路径。





        Returns:


            list[DriftEvent]: 每个检测到的损坏逻辑信号对应一个事件。


        """

        events: list[DriftEvent] = []

        if not os.path.isdir(module_dir):
            return events

        sources = _batch_read_module_sources(module_dir)
        for fname, source in sources.items():
            try:
                tree = ast.parse(source, filename=fname)
            except SyntaxError:
                continue

            lines = source.split("\n")

            total_lines = len(lines)

            todo_lines = sum(1 for line in lines if "TODO" in line.upper())

            if total_lines > 0 and todo_lines / total_lines > 0.05:
                evt = DriftEvent(
                    event_id=uuid.uuid4(),
                    module_id="MOD-INF-023",
                    detector_id="ai_broken_logic",
                    drift_dimension="AI_broken_logic",
                    baseline_version="0.1.0",
                    state=DriftState.DETECTED,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    resolution_detail=f"High TODO ratio {todo_lines}/{total_lines} in {fname}",
                )

                events.append(evt)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    arg_count = len(node.args.args)

                    body_count = len(node.body)

                    if arg_count > 5 and body_count < 3:
                        evt = DriftEvent(
                            event_id=uuid.uuid4(),
                            module_id="MOD-INF-023",
                            detector_id="ai_broken_logic",
                            drift_dimension="AI_broken_logic",
                            baseline_version="0.1.0",
                            state=DriftState.DETECTED,
                            created_at=datetime.now(UTC),
                            updated_at=datetime.now(UTC),
                            resolution_detail=f"Context truncation: {node.name}({arg_count} args, {body_count} lines) in {fname}",
                        )

                        events.append(evt)

        return events

    def detect_ai_duplicate_functionality(self, module_dir: str) -> list[DriftEvent]:
        """检测 AI 重复功能 — 跨文件存在 AST 完全相同的函数体。





        对每个函数体的 AST dump 计算 SHA-256 哈希，不同文件中相同


        函数名且相同哈希视为 AI 重复生成（排除 dunder 方法）。





        Args:


            module_dir: 待扫描的 Python 模块目录路径。





        Returns:


            list[DriftEvent]: 每对重复函数定义对应一个 DETECTED 状态的事件。


        """

        events: list[DriftEvent] = []

        if not os.path.isdir(module_dir):
            return events

        file_funcs: dict[str, list[tuple[str, str, str]]] = {}

        sources = _batch_read_module_sources(module_dir)
        for fname, source in sources.items():
            try:
                tree = ast.parse(source, filename=fname)
            except SyntaxError:
                continue

            file_funcs[fname] = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body_hash = hashlib.sha256(ast.dump(node, annotate_fields=False).encode()).hexdigest()[:12]

                    file_funcs[fname].append((node.name, body_hash, fname))

        for fname, funcs in file_funcs.items():
            for other_fname, other_funcs in file_funcs.items():
                if fname >= other_fname:
                    continue

                for fn, fh, _ in funcs:
                    for ofn, ofh, _ in other_funcs:
                        if fn == ofn and fh == ofh and fn not in ("__init__", "__repr__", "__str__", "__post_init__"):
                            events.append(
                                DriftEvent(
                                    event_id=uuid.uuid4(),
                                    module_id="MOD-INF-023",
                                    detector_id="ai_duplicate_functionality",
                                    drift_dimension="AI_duplicate_functionality",
                                    baseline_version="0.1.0",
                                    state=DriftState.DETECTED,
                                    created_at=datetime.now(UTC),
                                    updated_at=datetime.now(UTC),
                                    resolution_detail=f"Duplicate: {fn}() identical AST in {fname} and {other_fname}",
                                )
                            )

        return events

    def detect_ai_session_style_drift(self, module_dir: str) -> list[DriftEvent]:
        """检测 AI 会话间风格漂移 — 同一模块混用不兼容的编码风格。





        检测两种典型模式：


        1. ``@dataclass`` 装饰器与显式 ``__init__`` 并存 -> 风格冲突。


        2. ``async def`` 与 ``def`` 混用 -> 异步/同步风格不一致。





        Args:


            module_dir: 待扫描的 Python 模块目录路径。





        Returns:


            list[DriftEvent]: 每种风格漂移模式对应一个事件。


        """

        events: list[DriftEvent] = []

        if not os.path.isdir(module_dir):
            return events

        has_dataclass = False

        has_direct_init = False

        has_async = False

        has_sync_equivalent = False

        sources = _batch_read_module_sources(module_dir)
        for fname, source in sources.items():
            try:
                tree = ast.parse(source, filename=fname)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Name) and dec.id == "dataclass":
                            has_dataclass = True

                    if any(isinstance(n, ast.FunctionDef) and n.name == "__init__" for n in node.body):
                        has_direct_init = True

                if isinstance(node, ast.AsyncFunctionDef):
                    has_async = True

                if isinstance(node, ast.FunctionDef):
                    has_sync_equivalent = True

        if has_dataclass and has_direct_init:
            events.append(
                DriftEvent(
                    event_id=uuid.uuid4(),
                    module_id="MOD-INF-023",
                    detector_id="ai_session_style_drift",
                    drift_dimension="AI_style_drift",
                    baseline_version="0.1.0",
                    state=DriftState.DETECTED,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    resolution_detail="Style drift: dataclass and __init__ mixed",
                )
            )

        if has_async and has_sync_equivalent:
            events.append(
                DriftEvent(
                    event_id=uuid.uuid4(),
                    module_id="MOD-INF-023",
                    detector_id="ai_session_style_drift",
                    drift_dimension="AI_style_drift",
                    baseline_version="0.1.0",
                    state=DriftState.DETECTED,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    resolution_detail="Style drift: async/sync mixed",
                )
            )

        return events

    def detect_ai_knowledge_pollution(self, module_dir: str) -> list[DriftEvent]:
        """检测 AI 知识污染 — 命名冲突与命名约定不一致。





        两种检测：


        1. 同一文件中类名与函数名重名 -> 命名空间污染。


        2. 同一文件同时出现 snake_case 和 CamelCase 函数命名 ->


           AI 在不同会话中使用了冲突的命名约定。





        Args:


            module_dir: 待扫描的 Python 模块目录路径。





        Returns:


            list[DriftEvent]: 每个命名污染或约定冲突对应一个事件。


        """

        events: list[DriftEvent] = []

        if not os.path.isdir(module_dir):
            return events

        sources = _batch_read_module_sources(module_dir)
        for fname, source in sources.items():
            try:
                tree = ast.parse(source, filename=fname)
            except SyntaxError:
                continue

            func_names: set[str] = set()

            class_names: set[str] = set()

            snake_case = 0

            camel_case = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_names.add(node.name)

                    if "_" in node.name and node.name.lower() == node.name:
                        snake_case += 1

                    elif node.name[0].isupper():
                        camel_case += 1

                if isinstance(node, ast.ClassDef):
                    class_names.add(node.name)

            if class_names & func_names:
                common = class_names & func_names

                detail = f"Name collision between class and function: {', '.join(common)} in {fname}"

                events.append(
                    DriftEvent(
                        event_id=uuid.uuid4(),
                        module_id="MOD-INF-023",
                        detector_id="ai_knowledge_pollution",
                        drift_dimension="AI_knowledge_pollution",
                        baseline_version="0.1.0",
                        state=DriftState.DETECTED,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                        resolution_detail=detail,
                    )
                )

            if snake_case > 0 and camel_case > 0:
                detail = (
                    f"Naming convention conflict: {snake_case} snake_case + {camel_case} CamelCase funcs in {fname}"
                )

                events.append(
                    DriftEvent(
                        event_id=uuid.uuid4(),
                        module_id="MOD-INF-023",
                        detector_id="ai_knowledge_pollution",
                        drift_dimension="AI_knowledge_pollution",
                        baseline_version="0.1.0",
                        state=DriftState.DETECTED,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                        resolution_detail=detail,
                    )
                )

        return events

    def detect_cross_session_repair_conflict(self, active_events: list[DriftEvent]) -> list[DriftEvent]:
        """检测跨会话修复冲突 — 多个会话对同一 DriftEvent 重复修复。





        对活跃事件按 ``detector_id:drift_dimension:resolved_by`` 分组，


        同一 key 出现超过 1 次表示多个 AI 会话"修复"了同一问题。





        Args:


            active_events: 当前活跃的 DriftEvent 列表。





        Returns:


            list[DriftEvent]: 每个冲突的 key 对应一个 DETECTED 状态的事件。


        """

        events: list[DriftEvent] = []

        seen: dict[str, int] = {}

        for evt in active_events:
            key = f"{evt.detector_id}:{evt.drift_dimension}:{evt.resolved_by or 'none'}"

            seen[key] = seen.get(key, 0) + 1

        for key, count in seen.items():
            if count > 1:
                evt = DriftEvent(
                    event_id=uuid.uuid4(),
                    module_id="MOD-INF-023",
                    detector_id="cross_session_repair_conflict",
                    drift_dimension="D5_cross_session_conflict",
                    baseline_version="0.1.0",
                    state=DriftState.DETECTED,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    resolution_detail=f"Cross-session conflict: {key} repaired by {count} sessions",
                )

                events.append(evt)

        return events
