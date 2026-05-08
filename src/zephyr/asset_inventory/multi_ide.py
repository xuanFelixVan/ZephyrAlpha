"""MOD-INF-026 §24 — 多 IDE 兼容规则文件生成器。

MultiIDERuleGenerator: 从 asset_inventory 配置生成多 IDE 规则文件。
支持: Cursor (.cursorrules) / Trae (.trae/rules/) / VSCode (.github/copilot-instructions.md) / JetBrains (.idea/asset-inventory.xml)
一次生成，随时更新——不从 LLM 推理，直接从配置映射。
"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


class MultiIDERuleGenerator:

    def __init__(self, project_root: Path) -> None:
        self._root = project_root

    def _collect_project_rules(self) -> str:
        rules_path = self._root / ".trae" / "rules" / "project_rules.md"
        if not rules_path.exists():
            return "# No project_rules.md found"

        try:
            content = rules_path.read_text(encoding="utf-8")
            return f"# --- project_rules.md ---\n{content[:8000]}\n"
        except (OSError, PermissionError):
            return "# project_rules.md read error"

    def _header(self) -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    def _asset_rules_block(self) -> str:
        return (
            "# --- 自动盘点安全规则 ---\n"
            "# 以下规则由 MOD-INF-026 自动生成\n"
            "# 文件创建前查 registry-of-registries.yaml\n"
            "# 敏感文件不扫描 (.env, .secrets, token)\n"
            "# 超大文件跳过 (>50MB)\n"
        )

    def _atomic_write(self, target: Path, content: str) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = f"{target}.{os.getpid()}.tmp"
        tmp_path = Path(tmp)
        tmp_path.write_text(content, encoding="utf-8")
        os.replace(tmp, str(target))
        return target

    def generate_cursor_rules(self, output_path: Optional[Path] = None) -> Path:
        target = output_path or (self._root / ".cursorrules")
        template = f"""# ZephyrAlpha Cursor Rules — 自动生成于 {self._header()}
# 来源: MOD-INF-026 Asset Inventory + project_rules.md
# 不要手工编辑——运行 python -m zephyr.asset_inventory cursor-rules 重新生成

{self._collect_project_rules()}

{self._asset_rules_block()}
"""
        return self._atomic_write(target, template)

    def generate_trae_rules(self, output_path: Optional[Path] = None) -> Path:
        target = output_path or (self._root / ".trae" / "rules" / "asset_inventory_rules.md")
        template = f"""# ZephyrAlpha Trae Rules — 自动生成于 {self._header()}
# 来源: MOD-INF-026 Asset Inventory + project_rules.md
# 不要手工编辑——运行 python -m zephyr.asset_inventory trae-rules 重新生成

{self._collect_project_rules()}

{self._asset_rules_block()}
"""
        return self._atomic_write(target, template)

    def generate_vscode_rules(self, output_path: Optional[Path] = None) -> Path:
        target = output_path or (self._root / ".github" / "copilot-instructions.md")
        template = f"""# ZephyrAlpha Copilot Instructions — 自动生成于 {self._header()}
# 来源: MOD-INF-026 Asset Inventory + project_rules.md
# 不要手工编辑——运行 python -m zephyr.asset_inventory vscode-rules 重新生成

{self._collect_project_rules()}

{self._asset_rules_block()}
"""
        return self._atomic_write(target, template)

    def generate_jetbrains_rules(self, output_path: Optional[Path] = None) -> Path:
        target = output_path or (self._root / ".idea" / "asset-inventory.xml")
        rules_content = self._collect_project_rules()
        asset_block = self._asset_rules_block()
        escaped_rules = rules_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        escaped_asset = asset_block.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        template = f"""<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="AssetInventoryRules">
    <option name="generatedAt" value="{self._header()}" />
    <option name="source" value="MOD-INF-026 Asset Inventory + project_rules.md" />
    <option name="projectRules" value="{escaped_rules.strip()}" />
    <option name="assetRules" value="{escaped_asset.strip()}" />
  </component>
</project>
"""
        return self._atomic_write(target, template)

    def generate_all(self) -> dict[str, Path]:
        results: dict[str, Path] = {}
        try:
            results["cursor"] = self.generate_cursor_rules()
        except Exception:
            pass
        try:
            results["trae"] = self.generate_trae_rules()
        except Exception:
            pass
        try:
            results["vscode"] = self.generate_vscode_rules()
        except Exception:
            pass
        try:
            results["jetbrains"] = self.generate_jetbrains_rules()
        except Exception:
            pass
        return results
