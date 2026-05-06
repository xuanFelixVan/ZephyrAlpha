"""
_shared/yaml_utils.py — YAML 文件加载共享工具

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）
所有 YAML 文件读取逻辑集中在此，脚本通过 import 引用。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


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
