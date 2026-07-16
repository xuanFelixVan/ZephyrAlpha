# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/yaml_utils.py | §
# [MODULE] scripts.governance._shared.yaml_utils
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
_shared/yaml_utils.py — YAML 文件加载共享工具

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）
所有 YAML 文件读取逻辑集中在此，脚本通过 import 引用。

本文件同时 re-export src/zephyr/shared/io/yaml_utils.py 的真源函数
（load_vocabulary_values / load_vocabulary_deprecated_map / load_decision_tree / evaluate_ttl），
让 scripts/ 下消费者通过 ``from _shared.yaml_utils import evaluate_ttl`` 获取真源，
无需每个脚本自己 bootstrap sys.path（向内收：扩展已有，不创造新文件）。
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path
from typing import Any

import yaml

# ── 一次性 bootstrap：加 src/ 到 sys.path，re-export 真源函数 ──
# 约束：N 值对本文件固定（scripts/governance/_shared/ → repo root = parents[3]），仅此一次
from _shared.constants import REPO_ROOT
_REPO_ROOT = REPO_ROOT
_SRC = str(_REPO_ROOT / "src")
if _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)

# re-export 真源函数（SSoT：src/zephyr/shared/io/yaml_utils.py）
from zephyr.shared.io.yaml_utils import (  # noqa: E402,F401
    evaluate_ttl,
    load_decision_tree,
    load_vocabulary_deprecated_map,
    load_vocabulary_entries,
    load_vocabulary_values,
)


def load_yaml(file_path: str | Path) -> Any:
    """加载 YAML 文件，返回解析后的任意类型对象。

    Args:
        file_path: YAML 文件的绝对路径

    Returns:
        yaml.safe_load() 的结果（dict / list / str 等）

    Raises:
        FileNotFoundError: 文件不存在
        yaml.YAMLError: YAML 解析失败
    """
    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"YAML 文件不存在: {p}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_yaml_safe(file_path: str | Path) -> dict:
    """graceful 变体：文件缺失或解析结果非 dict 时返回 {} 而非 raise。

    供防御性调用方使用（如评分脚本对可选配置文件做容错加载）。
    与 load_yaml 的契约差异：缺失返回 {}（非 raise）；非 dict 返回 {}（非原值）。
    """
    p = Path(file_path)
    if not p.is_file():
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}
