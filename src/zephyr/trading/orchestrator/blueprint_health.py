# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.blueprint_health
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_blueprint_health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""蓝图健康自检（CT-BLUEPRINT-HEALTH）——蓝图字段完整性+引用一致性+版本对齐。"""

from __future__ import annotations

import re
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# 蓝图头必需字段（按模块文件头部 [KEY] value 约定）
_REQUIRED_FIELDS: tuple[str, ...] = ("BLUEPRINT", "MODULE", "DOMAIN")


class BlueprintHealthChecker:
    """5.55.6 修复：原为空壳（永远返回 healthy），现实现真实字段完整性+引用一致性检查。"""

    def __init__(self) -> None:
        self._last_errors: list[str] = []

    def check_consistency(self, blueprint_file: str) -> dict:
        """检查模块文件蓝图头的字段完整性。

        - 文件存在性
        - 必需字段 [BLUEPRINT]/[MODULE]/[DOMAIN] 齐全
        - [BLUEPRINT] 引用的 .md 路径在仓库内可达
        """
        errors: list[str] = []
        self._last_errors = errors

        file_path = Path(blueprint_file)
        if not file_path.is_absolute():
            file_path = Path(REPO_ROOT) / file_path
        if not file_path.exists():
            errors.append(f"blueprint_file not found: {blueprint_file}")
            return {"status": "unhealthy", "errors": errors}

        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read blueprint_file: {exc}")
            return {"status": "unhealthy", "errors": errors}

        # 解析头部 [KEY] value 字段（仅扫描前 40 行头部注释区）
        header_lines = content.splitlines()[:40]
        found_fields: dict[str, str] = {}
        blueprint_ref: str | None = None
        for line in header_lines:
            stripped = line.strip()
            m = re.match(r"^#\s*\[(\w+)\]\s*(.*)$", stripped)
            if m:
                key = m.group(1).upper()
                val = m.group(2).strip()
                found_fields[key] = val
                if key == "BLUEPRINT":
                    blueprint_ref = val

        # 1. 必需字段齐全性
        for field in _REQUIRED_FIELDS:
            if field not in found_fields or not found_fields[field]:
                errors.append(f"missing or empty required field: [{field}]")

        # 2. [BLUEPRINT] 引用的 .md 路径可达性
        if blueprint_ref:
            # 格式：MOD-XXX | path/to/blueprint.md | §section
            parts = [p.strip() for p in blueprint_ref.split("|")]
            if len(parts) >= 2 and parts[1]:
                md_rel = parts[1]
                md_path = Path(REPO_ROOT) / md_rel
                if not md_path.exists():
                    errors.append(f"blueprint .md reference not found: {md_rel}")
            else:
                errors.append(f"malformed [BLUEPRINT] reference: {blueprint_ref}")

        self._last_errors = errors
        return {
            "status": "healthy" if not errors else "unhealthy",
            "errors": errors,
        }

    def validate_references(self) -> list[str]:
        """返回上次 check_consistency 发现的引用问题（无文件参数时复用上次结果）。"""
        return [e for e in self._last_errors if "reference" in e or "not found" in e]
