# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.winfs_defense
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_winfs_defense | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
WinFS Defense — Windows NTFS 编码鲁棒性 (盲点 #35)
特性：
  - 路径规范化：正斜杠/反斜杠统一
  - 长路径前缀自动添加 \\?\
  - 在环境初始化阶段执行
"""

import os
import sys


class WinFSDefense:
    """
    Windows 文件系统防御 (盲点 #35)
    """

    def __init__(self):
        self._long_path_enabled = False

    def enable_long_paths(self):
        if sys.platform == "win32":
            self._long_path_enabled = True

    def normalize_path(self, path: str) -> str:
        normalized = os.path.normpath(path)
        if self._long_path_enabled and sys.platform == "win32":
            if len(normalized) > 260 and not normalized.startswith("\\\\?\\"):
                normalized = "\\\\?\\" + os.path.abspath(normalized)
        return normalized

    def safe_open(self, filepath: str, mode: str = "r", encoding: str = "utf-8"):
        safe_path = self.normalize_path(filepath)
        return open(safe_path, mode, encoding=encoding)

    def check_filesystem(self) -> dict:
        data_dir = os.path.join(os.getcwd(), "data")
        cwd_exists = os.path.exists(os.getcwd())
        data_exists = os.path.exists(data_dir)
        return {
            "cwd": os.getcwd(),
            "cwd_exists": cwd_exists,
            "data_dir_exists": data_exists,
            "long_path_enabled": self._long_path_enabled,
            "platform": sys.platform,
        }
