# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.blueprint_tools.architecture_context_loader
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_architecture_context_loader | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
architecture_context_loader — 加载 ``generate_architecture_context.py`` 产出的预编译 JSON

真源文件默认路径：与本包同目录下的 ``architecture-context.json``（由脚本生成）。
"""

from typing import Final

import json
from pathlib import Path
from typing import Any

DEFAULT_ARCH_CONTEXT_PATH: Final[Path] = Path(__file__).resolve().parent / "architecture-context.json"

__all__ = [
    "DEFAULT_ARCH_CONTEXT_PATH",
    "format_architecture_context_excerpt",
    "load_architecture_context_dict",
]


def load_architecture_context_dict(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_ARCH_CONTEXT_PATH
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def format_architecture_context_excerpt(data: dict[str, Any], *, max_chars: int = 12_000) -> str:
    """将 JSON 压成可注入 prompt 的摘录（避免整文件撑爆 token）。"""
    if not data:
        return ""
    inv = data.get("invariants") or {}
    slim: dict[str, Any] = {
        "generated_at": data.get("generated_at"),
        "version": data.get("version"),
        "schema": data.get("schema"),
        "contracts": data.get("contracts"),
        "invariants": {
            "total": inv.get("total"),
            "items": (inv.get("items") or [])[:8],
        },
        "layers": (data.get("layers") or [])[:24],
        "gate_registry": data.get("gate_registry"),
    }
    s = json.dumps(slim, ensure_ascii=False, indent=2)
    if len(s) > max_chars:
        s = s[: max_chars - 10] + "\n…[truncated]"
    return "--- ZEPHYR_ARCH_CONTEXT ---\n" + s
