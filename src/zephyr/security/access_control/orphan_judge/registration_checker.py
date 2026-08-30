# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §L0
# [MODULE] zephyr.security.access_control.orphan_judge.registration_checker
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.judge
# [CONSUMERS] orphan-judge.judge._run_layer L0
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 检查文件是否出现在项目的注册表(yaml/__init__/manifest)中; 不修改任何文件
# [MODIFY-GUARD] 修改注册表扫描范围必须同步 blueprint.md §3.1
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表文件不可读时返回 is_registered=False,不抛异常
# [TESTS] tests/orphan-judge/test_registration_checker.py
# [A_module] module_id=MOD-INF-029 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[BLUEPRINT] MOD-INF-029 — L0 注册检查器

扫描项目注册表，判断文件是否已登记在册。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: registration_checker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RegistrationChecker
#   name_en: RegistrationChecker
#   intro: class RegistrationChecker 源码 L85-L140
#   desc: 公共方法（定义序）: check；源码 L85-L140
#   inputs: project_root
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: RegistrationChecker
#   downstream: orphan-judge.judge._run_layer L0
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from zephyr.security.access_control.orphan_judge.judge import LayerResult

logger = logging.getLogger(__name__)

__all__ = [
    "RegistrationChecker",
]

_REGISTRY_CANDIDATES = [
    "docs/registry_of_registries.yaml",
    "scripts/script-manifest.yaml",
    "src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml",
    "src/zephyr/agent-spec/_registry.yaml",
    "src/zephyr/kb/_registry.yaml",
    "src/zephyr/audit-orchestrator/_registry.yaml",
    "src/zephyr/security/access_control/orphan_judge/_registry.yaml",
    "src/zephyr/semantic-auditor/_registry.yaml",
    "src/zephyr/runtime/_registry.yaml",
    "src/zephyr/db/_registry.yaml",
    "src/zephyr/mcp/_registry.yaml",
    "src/zephyr/governance/_registry.yaml",
    "data/asset_index/unified-asset-index.yaml",
    "data/asset_index/project-entity-depgraph.yaml",
]

_INIT_ALL_RE = re.compile(r"__all__\s*=\s*\[(.*?)\]", re.DOTALL)
_STR_VALUE_RE = re.compile(r'"([^"]+)"')


class RegistrationChecker:
    def __init__(self, project_root: str | Path = ".") -> None:
        self._root = Path(project_root).resolve()

    def check(self, path: str) -> LayerResult:
        file_path = self._root / path
        rel_path = str(file_path.relative_to(self._root)).replace("\\", "/")

        registered_in: list[str] = []

        for reg_rel in _REGISTRY_CANDIDATES:
            reg_path = self._root / reg_rel
            if not reg_path.exists():
                continue
            try:
                content = reg_path.read_text(encoding="utf-8")
            except OSError:
                continue
            if path in content or rel_path in content or file_path.name in content:
                registered_in.append(reg_rel)

        if not registered_in:
            init_registered = self._check_init_exports(file_path)
            if init_registered:
                registered_in.append("__init__.py (__all__ export)")

        is_registered = len(registered_in) > 0
        return LayerResult(
            layer="L0",
            passed=is_registered,
            detail=f"Registered in {len(registered_in)} registries" if is_registered else "Not found in any registry",
            data={
                "is_registered": is_registered,
                "registered_in": registered_in,
            },
        )

    def _check_init_exports(self, file_path: Path) -> bool:
        pkg_dir = file_path.parent
        init_path = pkg_dir / "__init__.py"
        if not init_path.exists():
            return False
        try:
            content = init_path.read_text(encoding="utf-8")
        except OSError:
            return False
        module_name = file_path.stem
        if module_name in content:
            return True
        all_match = _INIT_ALL_RE.search(content)
        if all_match:
            all_block = all_match.group(1)
            names = _STR_VALUE_RE.findall(all_block)
            if module_name in names:
                return True
        return False
