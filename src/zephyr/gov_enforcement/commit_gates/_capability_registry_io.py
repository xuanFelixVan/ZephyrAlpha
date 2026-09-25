# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates._capability_registry_io
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.create_guard (_load_capability_registry); zephyr.gov_enforcement.commit_gates.ssot_redefinition_gate (_load_registry_yaml); zephyr.gov_enforcement.commit_gates.capability_overlap_gate (_load_registry_data)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只共享读入不改判定——(normcase 路径, mtime_ns, size) 键控进程级单条缓存，六台读同一 2.68MB capability 册收敛为一次 yaml.safe_load；mtime/size 任一变化即失效重解析（写后陈旧不可能）；解析失败不缓存（下次真读）；判据零变化（同一文件同一字节同一解析器，T8 簇1 st-commitspeed-pkg8-20260925）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] parse 失败返回 (None, exc) 不抛穿；path stat 失败同口径；永不写盘
# [TESTS] tests/governance/commit_gates/test_capability_registry_io.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""_capability_registry_io.py — capability 册共享解析缓存（T8 簇1 共册解析）

一句话：读同一册的多台 commit gate 共享一次 ``yaml.safe_load``。

病根（卷宗 docs/_working/commit_speedup_campaign/30_gate_census/C1_gate_dossier.md 簇1）
-------------------------------------------------------------------------------------
capability_canonical_file_registry.yaml 2.7MB/万条，create_guard(60)/
ssot_redefinition(65)/capability_overlap(200) 同一提交链各全量 safe_load 一次
（实测单次 3.6-4.2s）。同真源可派生→必并（内收判据 w5_1）。

形态
----
"一次解析＋多条判据数据"：各台判定逻辑零变化，只把"读入＋解析"下沉到本模块；
``(normcase 路径, mtime_ns, st_size)`` 键控进程级单条缓存——册未变零解析
（实测 2.16s→0.2ms），写后任一字节变化（mtime/size）即失效。键含 normcase
路径：不同 worktree/测试 tmp 册同 (mtime,size) 不串台。

Usage::

    from zephyr.gov_enforcement.commit_gates._capability_registry_io import (
        parse_capability_registry_cached,
    )

    data, err = parse_capability_registry_cached(REGISTRY_YAML, reader=my_reader)
    if err is not None: ...  # 各台保留自己的 fail-open/fail-closed 语义

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/c/capability_registry_io.yaml
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Callable, Final

logger = logging.getLogger(__name__)

__all__: Final = ["parse_capability_registry_cached", "reset_parse_cache", "cache_key_of"]

# 进程级单条缓存：{"key": (normcase_path, mtime_ns, size) | None, "data": parsed | None}
# 历史名延续 create_guard._REGISTRY_CACHE（st-commitspeed-tbl-20260924 引入，pkg8 下沉共享）。
_PARSE_CACHE: dict = {"key": None, "data": None}


def _default_reader(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def cache_key_of(yaml_path: Path) -> tuple[str, int, int]:
    """缓存键 = (normcase 绝对路径, mtime_ns, size)。stat 失败向上抛（调用方定语义）。"""
    st = Path(yaml_path).stat()
    return (os.path.normcase(str(Path(yaml_path).absolute())), st.st_mtime_ns, st.st_size)


def parse_capability_registry_cached(
    yaml_path: Path, *, reader: Callable[[Path], str] | None = None
) -> tuple[dict | None, Exception | None]:
    """读入＋解析 capability 册（进程级单条缓存）。返回 ``(data, exc)``。

    - 命中（同 normcase 路径 + 同 mtime_ns + 同 size）→ 返回缓存 data，**不重读文件**。
    - 未命中 → ``reader(yaml_path)``（默认 ``read_text(utf-8)``）+ ``yaml.safe_load``；
      成功回填缓存；失败**不缓存**（撕裂读下一链自动真读）。
    - 永不抛异常：stat/读/解析任何异常都以 ``(None, exc)`` 返回，语义归调用方门禁。

    判据零变化论证：同一文件同一字节经同一 ``yaml.safe_load``，缓存只去掉重复
    解析耗时，不改变任何一台门的输入。
    """
    path = Path(yaml_path)
    read = reader or _default_reader
    try:
        key = cache_key_of(path)
    except OSError as e:  # noqa: PERF203 — 单条路径，无循环
        return None, e
    if _PARSE_CACHE["key"] == key and _PARSE_CACHE["data"] is not None:
        return _PARSE_CACHE["data"], None
    try:
        import yaml

        data = yaml.safe_load(read(path))
    except Exception as e:  # noqa: BLE001 — 解析失败不缓存，交调用方 fail-open/fail-closed
        return None, e
    _PARSE_CACHE["key"] = key
    _PARSE_CACHE["data"] = data
    return data, None


def reset_parse_cache(key: object = None, /, *, data: object = None) -> None:
    """测试/进程内复位（默认清空）。保留 dict 容器身份——外部持引用仍可见。"""
    _PARSE_CACHE["key"] = key
    _PARSE_CACHE["data"] = data
