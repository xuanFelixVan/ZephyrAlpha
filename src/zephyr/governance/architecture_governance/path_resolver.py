# [BLUEPRINT] SRC-016 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.architecture_governance.path_resolver
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_path_resolver | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
PathResolver — 模块路径解析器
解决蓝图路径漂移 + AI 幻觉双重问题

设计原则：
  - task card 仍写死路径（防止 AI 幻觉）
  - 施工前 PathResolver 校验路径是否匹配当前项目结构
  - 不匹配时自动建议正确路径，并要求更新 task card
"""

import os
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class PathResolution:
    expected: str
    exists_at_expected: bool = False
    found_exact_elsewhere: list = field(default_factory=list)
    found_fuzzy: list = field(default_factory=list)
    suggested_path: str | None = None
    status: str = "UNKNOWN"


class PathResolver:
    """
    维护 src/zephyr/ 目录树索引，提供路径解析和校验。
    每次实例化时重新扫描，保证索引是最新的。
    """

    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.src_root = os.path.join(self.project_root, "src", "zephyr")
        self._file_index = defaultdict(list)
        self._dir_index = set()
        self._module_map = {}  # module_name → [directories]
        self._build_index()

    def _build_index(self):
        ignore = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".tox",
            "dist",
            "build",
            "egg-info",
            "node_modules",
            ".venv",
            "venv",
        }

        for root, dirs, files in os.walk(self.src_root):
            dirs[:] = [d for d in dirs if d not in ignore and not d.startswith(".")]

            rel_dir = os.path.relpath(root, self.src_root)

            for d in dirs:
                full = os.path.join(root, d)
                self._dir_index.add(full)
                normalized = d.lower().replace("_", "-").replace(" ", "-")
                if full not in self._module_map.get(d, []):
                    self._module_map.setdefault(d, []).append(full)
                if normalized != d and full not in self._module_map.get(normalized, []):
                    self._module_map.setdefault(normalized, []).append(full)

            for f in files:
                full = os.path.join(root, f)
                self._file_index[f.lower()].append(full)

    def resolve_module(self, module_name: str) -> list:
        """
        根据模块名查找其在项目中的实际目录。
        module_name 可以是简称（"rollback"）、完整名（"governance/rollback"）、
        或模块ID（"MOD-INF-021"）。
        返回所有匹配的目录路径列表，governance/ 和 infrastructure_runtime_integration/ 下的优先。
        """
        normalized = module_name.lower().replace("_", "-").replace(" ", "-")

        matches = []

        # Direct match
        if normalized in self._module_map:
            matches = self._module_map[normalized]

        # Reverse-lookup: check if module_name is a substring of any dir
        if not matches:
            for dir_path in self._dir_index:
                dir_basename = os.path.basename(dir_path).lower()
                if normalized in dir_basename or dir_basename in normalized:
                    matches.append(dir_path)

        # Sort: governance/ and infrastructure_runtime_integration/ first (they're the canonical locations)
        def _priority(p):
            rel = os.path.relpath(p, self.src_root)
            if "governance" in rel or "infrastructure_runtime_integration" in rel:
                return 0
            return 1

        return sorted(matches, key=_priority) if matches else []

    def resolve_path(self, module_name: str, filename: str) -> str | None:
        """
        给定模块名 + 文件名，返回应该落盘的完整路径。
        模块有多处存在时优先 governance/ 或 infrastructure_runtime_integration/。
        """
        dirs = self.resolve_module(module_name)
        if not dirs:
            return None

        return os.path.join(dirs[0], filename)

    def validate_path(self, expected_path: str, module_hint: str = "") -> PathResolution:
        """
        校验一个预期的 downstream_output 路径是否合理。

        返回 PathResolution 包含：
          - 是否在原路径存在
          - 是否有同名文件在其他地方
          - 是否有高度相似的文件
          - 建议的正确路径
        """
        result = PathResolution(expected=expected_path)
        result.exists_at_expected = os.path.exists(expected_path)

        if result.exists_at_expected:
            result.status = "OK"
            result.suggested_path = expected_path
            return result

        basename = os.path.basename(expected_path)
        if not basename:
            result.status = "NO_BASENAME"
            return result

        key = basename.lower()

        # Search for exact match elsewhere
        exact_elsewhere = [
            fp for fp in self._file_index.get(key, []) if os.path.normcase(fp) != os.path.normcase(expected_path)
        ]
        result.found_exact_elsewhere = exact_elsewhere

        # Search for fuzzy matches
        from difflib import SequenceMatcher

        fuzzy = []
        for idx_name, idx_paths in self._file_index.items():
            ratio = SequenceMatcher(None, key, idx_name).ratio()
            if ratio >= 0.80:
                for fp in idx_paths[:2]:
                    fuzzy.append((fp, ratio))
        fuzzy.sort(key=lambda x: -x[1])
        result.found_fuzzy = fuzzy

        # Determine suggested path
        if exact_elsewhere:
            result.suggested_path = exact_elsewhere[0]
            result.status = "PATH_DRIFT"
        elif fuzzy and fuzzy[0][1] >= 0.90:
            result.suggested_path = fuzzy[0][0]
            result.status = "NAME_VARIANT"
        elif module_hint:
            resolved = self.resolve_path(module_hint, basename)
            if resolved:
                result.suggested_path = resolved
                result.status = "MODULE_RESOLVED"
            else:
                result.status = "MISSING"
        else:
            result.status = "MISSING"

        return result

    def resolve_downstream(self, task_card_content: str) -> dict:
        """
        解析一整张任务卡的 downstream_outputs，返回：
          {resolved: bool, corrections: [{old, new, status}], updated_content: str}
        """
        import re as re_mod

        lines = task_card_content.split("\n")
        corrections = []
        new_lines = list(lines)
        all_resolved = True

        in_downstream = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("downstream_outputs:"):
                in_downstream = True
                continue
            if in_downstream:
                if stripped.startswith("- path:"):
                    pm = re_mod.search(r'path:\s*"([^"]+)"', stripped)
                    if pm:
                        expected = pm.group(1)
                        resolution = self.validate_path(expected)

                        if resolution.status == "OK":
                            corrections.append({"old": expected, "new": expected, "status": "OK"})
                        elif resolution.suggested_path:
                            new_line = line.replace(f'"{expected}"', f'"{resolution.suggested_path}"')
                            new_lines[i] = new_line
                            corrections.append(
                                {"old": expected, "new": resolution.suggested_path, "status": resolution.status}
                            )
                        else:
                            all_resolved = False
                            corrections.append({"old": expected, "new": None, "status": resolution.status})
                elif (stripped.startswith("- ") or not stripped.startswith(" ")) and not stripped.startswith("- path:"):
                    in_downstream = False

        return {"resolved": all_resolved, "corrections": corrections, "updated_content": "\n".join(new_lines)}

    def dump_module_tree(self) -> dict:
        """导出模块树，供蓝图和任务卡生成时参考"""
        tree = {}
        for root, dirs, files in os.walk(self.src_root):
            rel = os.path.relpath(root, self.src_root)
            if rel == ".":
                continue
            parts = rel.split(os.sep)
            current = tree
            for part in parts:
                current = current.setdefault(part, {})
            py_files = [f for f in files if f.endswith(".py") and f != "__init__.py"]
            if "__files__" not in current:
                current["__files__"] = []
            current["__files__"].extend(py_files)
        return tree


def reslove_path(module: str, filename: str, project_root: str = None) -> str | None:
    """快捷函数：解析模块路径"""
    root = project_root or os.environ.get("ZEPHYR_ROOT", os.getcwd())
    pr = PathResolver(root)
    return pr.resolve_path(module, filename)


if __name__ == "__main__":
    # Self-test
    resolver = PathResolver(r"D:\ZephyrAlpha")

    print("Module resolution test:")
    for mod in [
        "rollback",
        "agent-rbac",
        "audit-trail",
        "code_dedup_engine",
        "escalation",
        "budget-enforcer",
        "drift-detector",
        "a2a",
        "pipeline",
        "context-engine",
        "feedback-loop",
        "kb",
    ]:
        dirs = resolver.resolve_module(mod)
        print(f"  {mod:25s} → {[os.path.relpath(d, resolver.project_root) for d in dirs[:2]]}")

    print("\nPath validation test:")
    test_paths = [
        r"D:\ZephyrAlpha\src\zephyr\agent-rbac\phase_executor.py",
        r"D:\ZephyrAlpha\src\zephyr\governance\audit-trail\anomaly.py",
        r"D:\ZephyrAlpha\src\zephyr\rollback\result_types.py",
        r"D:\ZephyrAlpha\src\zephyr\kb\reranker.py",
        r"D:\ZephyrAlpha\src\zephyr\nonexistent\fake_file.py",
    ]
    for tp in test_paths:
        r = resolver.validate_path(tp)
        print(f"  {os.path.relpath(tp, resolver.project_root)}")
        print(
            f"    status={r.status}, suggested={os.path.relpath(r.suggested_path, resolver.project_root) if r.suggested_path else 'None'}"
        )
