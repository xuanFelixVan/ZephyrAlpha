# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.ce_file_lister
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
list_ce_files.py — CE 文件清单生成器
=====================================
Task ID : MOD-CONTEXT_ENGINE-TASK-011
Priority: P2 (beta)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ce_file_lister.py
# 层: 算法
# - id: A1
#   name_zh: ① collect_files
#   name_en: collect_files
#   intro: collect_files() 源码 L78-L88
#   desc: 源码 L78-L88
#   inputs: 无参数
#   outputs: dict[str, list[dict[str, str]]]
# - id: A2
#   name_zh: ② generate_manifest
#   name_en: generate_manifest
#   intro: generate_manifest() 源码 L91-L98
#   desc: 源码 L91-L98
#   inputs: 无参数
#   outputs: str
# 层: 输出
# - id: O1
#   name_zh: dict[str, list[dict[str, str]]]
#   name_en: dict[str, list[dict[str, str]]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

import json
from pathlib import Path
from typing import Final

CE_ROOT: Final[Path] = Path(__file__).resolve().parent

CATEGORIES: Final[set] = {
    "source": "*.py",
    "config": "config/**/*.yaml",
    "data": "*.json",
    "other": "*.yaml",
}


def collect_files() -> dict[str, list[dict[str, str]]]:
    manifest: dict[str, list[dict[str, str]]] = {}
    for category, pattern in CATEGORIES.items():
        entries: list[dict[str, str]] = []
        for file_path in sorted(CE_ROOT.glob(pattern)):
            if file_path.name.startswith("_"):
                continue
            rel = str(file_path.relative_to(CE_ROOT))
            entries.append({"path": rel, "size_kb": f"{file_path.stat().st_size / 1024:.1f}"})
        manifest[category] = entries
    return manifest


def generate_manifest() -> str:
    data = {
        "module_id": "MOD-CONTEXT_ENGINE",
        "root": str(CE_ROOT),
        "files": collect_files(),
        "total_py_files": sum(1 for _ in CE_ROOT.glob("*.py") if not _.name.startswith("_")),
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    print(generate_manifest())
