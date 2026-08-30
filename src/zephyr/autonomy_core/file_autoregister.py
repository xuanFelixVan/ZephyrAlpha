# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.file_autoregister
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: manifest_path 参数
#   fields: 参数 manifest_path（无注解）
#   code: file_autoregister.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FileAutoRegister
#   name_en: FileAutoRegister
#   intro: class FileAutoRegister 源码 L57-L89
#   desc: 公共方法（定义序）: register；源码 L57-L89
#   inputs: manifest_path
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: FileAutoRegister
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import os
from pathlib import Path
from typing import Any

import yaml

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


class FileAutoRegister:
    def __init__(self, manifest_path: Path | None = None):
        self.manifest_path = (
            manifest_path
            or REPO_ROOT
            / "scripts"
            / "script-manifest.yaml"  # #51 裁定：登记真源连字符版（原指向不存在的 governance/script-manifest.yaml 死引用）
        )

    def register(self, file_path: str, module: str = "unknown") -> dict[str, Any]:
        script_name = Path(file_path).stem
        with open(self.manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f) or {}

        manifest.setdefault("scripts", {})
        manifest["scripts"][script_name] = {
            "path": file_path,
            "module": module,
            "registered_by": "file_autoregister",
        }

        tmp_path = f"{self.manifest_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                yaml.dump(manifest, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            os.replace(tmp_path, self.manifest_path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

        return {"script_name": script_name, "registered": True}


__all__ = ["FileAutoRegister"]
