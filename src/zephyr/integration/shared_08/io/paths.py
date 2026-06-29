# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.io.paths
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_paths | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
paths.py — 项目路径常量 SSoT（Single Source of Truth）

对标 AGENTS.md §6.4（最有利于 AI 施工的选择）
         AGENTS.md §6.9（架构数据 Canonical SSoT 铁律）

根因修复：此前 7 个文件各自通过 Path(__file__).parents[N] 独立计算
REPO_ROOT，导致：
  1. 目录层级调整需改 7 处
  2. DB_PATH 大小写冲突（state vs STATE）因无 SSoT 未被发现
  3. 路径常量分散定义，漂移风险极高

本文件是 src/zephyr/ 下所有路径常量的唯一真源。
任何需要 REPO_ROOT / DB_PATH / 路径常量的模块，必须从此处导入。

对标：
  - scripts/governance/_shared/constants.py（治理脚本侧的路径 SSoT）
  - Google Style Guide: "Define constants in one place"（常量只在一处定义）
  - Terraform: provider 配置集中定义，模块引用而非重定义
"""

from pathlib import Path

# find_repo_root / REPO_ROOT 真源为 zephyr.shared.io.paths（project_memory 钦定唯一真源）。
# 本模块 re-export 以保持 15+ 消费者 import 路径不变，消除算法重复实现（治本：单真源）。
from zephyr.shared.io.paths import REPO_ROOT, find_repo_root

DB_DIR: Path = REPO_ROOT / "data"

import importlib as _il

_mod = _il.import_module("zephyr.data.persistence.sqlite_schema")
DB_PATH = _mod.DB_PATH

GATES_DIR: Path = REPO_ROOT / "src" / "zephyr" / "gates"
SNAPSHOTS_DIR: Path = REPO_ROOT / ".runtime" / "snapshots"
RATIONALE_LOG_PATH: Path = REPO_ROOT / "docs" / "02_enterprise_architecture" / "architecture-rationale-log.md"

VECTOR_INDEX_DIR: Path = REPO_ROOT / ".audit_cache" / "vector_index"
MODELS_CACHE_DIR: Path = REPO_ROOT / ".audit_cache" / "models"

__all__ = [
    "DB_DIR",
    "DB_PATH",
    "GATES_DIR",
    "MODELS_CACHE_DIR",
    "RATIONALE_LOG_PATH",
    "REPO_ROOT",
    "SNAPSHOTS_DIR",
    "VECTOR_INDEX_DIR",
    "find_repo_root",
]
