# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates._capability_registry_io
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.create_guard (_load_capability_registry); zephyr.gov_enforcement.commit_gates.ssot_redefinition_gate (_load_registry_yaml); zephyr.gov_enforcement.commit_gates.capability_overlap_gate (_load_registry_data); zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate (parse_registry_text_cached)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只共享读入不改判定——(normcase 路径, mtime_ns, size) 键控进程级单条缓存，六台读同一 2.68MB capability 册收敛为一次 yaml.safe_load；mtime/size 任一变化即失效重解析（写后陈旧不可能）；解析失败不缓存（下次真读）；判据零变化（同一文件同一字节同一解析器，T8 簇1 st-commitspeed-pkg8-20260925）；st-perfz2-20261015 P0-1 扩面：容器增 text_sha256 槽（命中前 sha256 校验，盘面字节≠请求文本绝不复用）+ parse_registry_text_cached 文本喂入口（REGISTRY-YAML-PARSE 的 staged 字节与 CREATE-GUARD 的盘面字节同册共析——staged≠盘面时只返回不回填，防 staged 数据毒化盘面真源条目；回填前读盘面 sha 比对，同字节才可入 (path,mtime,size) 键）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] parse 失败返回 (None, exc) 不抛穿；path stat 失败同口径；永不写盘
# [TESTS] tests/governance/commit_gates/test_capability_registry_io.py; tests/gov/governance/commit_gates/test_registry_parse_shared_text_cache.py
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

st-perfz2-20261015 P0-1 扩面（staged 字节共析）
----------------------------------------------
REGISTRY-YAML-PARSE(54) 手上只有 **staged 字节**（git show :path），历史上自己
safe_load 一遍（96,697 行册单次 ~4.8s），与 CREATE-GUARD 的**盘面字节**解析互不
共享。本模块新增 ``parse_registry_text_cached(path, text)``：调用方持文本喂入，
键仍=(盘面 path, mtime_ns, size)；命中前多一道 **sha256 校验**（缓存 data 的
text_sha256 == 请求文本的 sha）——staged 与盘面字节不一致时**只返回新解析结果、
绝不回填**（防 staged 数据毒化盘面真源条目，create_guard 下游读到错字节）；
未命中时解析请求文本后**读盘面字节比对 sha，同字节才回填**（盘面比对 ≈30ms，
对比一次 safe_load ~4.8s 可忽略）。容器新增 ``text_sha256`` 槽；缺槽（旧测试
fixture 注入的双键容器）＝sha 未知＝按未命中处理，行为保守不串台。

Usage::

    from zephyr.gov_enforcement.commit_gates._capability_registry_io import (
        parse_capability_registry_cached,
        parse_registry_text_cached,
    )

    data, err = parse_capability_registry_cached(REGISTRY_YAML, reader=my_reader)
    if err is not None: ...  # 各台保留自己的 fail-open/fail-closed 语义

    # staged 字节喂入（REGISTRY-YAML-PARSE）：
    data, err = parse_registry_text_cached(registry_path, staged_text)

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/c/capability_registry_io.yaml
"""

from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
from typing import Callable, Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "parse_capability_registry_cached",
    "parse_registry_text_cached",
    "reset_parse_cache",
    "cache_key_of",
    "text_sha256_of",
]

# 进程级单条缓存：{"key": (normcase_path, mtime_ns, size) | None, "data": parsed | None,
#                  "text_sha256": str | None}
# 历史名延续 create_guard._REGISTRY_CACHE（st-commitspeed-tbl-20260924 引入，pkg8 下沉共享）。
# text_sha256 槽（st-perfz2-20261015 P0-1）：缓存 data 对应的字节指纹——命中前校验，
# 缺槽（None/旧双键容器）＝sha 未知＝按未命中处理（保守不串台）。
_PARSE_CACHE: dict = {"key": None, "data": None, "text_sha256": None}


def _default_reader(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def text_sha256_of(text: str) -> str:
    """文本字节指纹（utf-8 编码后 sha256 hex 前 24 位——24 位对单册比对足够，省键长）。"""
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:24]


def cache_key_of(yaml_path: Path) -> tuple[str, int, int]:
    """缓存键 = (normcase 绝对路径, mtime_ns, size)。stat 失败向上抛（调用方定语义）。"""
    st = Path(yaml_path).stat()
    return (os.path.normcase(str(Path(yaml_path).absolute())), st.st_mtime_ns, st.st_size)


def _cache_hit_for_text(key: tuple, text_sha: str) -> bool:
    """带 sha 校验的命中判定：键同 + data 在 + 缓存 sha 与请求文本 sha 一致。

    缓存 sha 缺失（旧双键容器/历史回填）＝未知＝不命中（保守——宁可重解析，
    不可把 A 字节解析出的 data 当 B 字节的判据输入）。
    """
    return (
        _PARSE_CACHE["key"] == key
        and _PARSE_CACHE["data"] is not None
        and bool(_PARSE_CACHE.get("text_sha256"))
        and _PARSE_CACHE.get("text_sha256") == text_sha
    )


def _store(key: tuple, data: object, text: str) -> None:
    _PARSE_CACHE["key"] = key
    _PARSE_CACHE["data"] = data
    _PARSE_CACHE["text_sha256"] = text_sha256_of(text)


def parse_capability_registry_cached(
    yaml_path: Path, *, reader: Callable[[Path], str] | None = None
) -> tuple[dict | None, Exception | None]:
    """读入＋解析 capability 册（进程级单条缓存）。返回 ``(data, exc)``。

    - 命中（同 normcase 路径 + 同 mtime_ns + 同 size）→ 返回缓存 data，**不重读文件**。
    - 未命中 → ``reader(yaml_path)``（默认 ``read_text(utf-8)``）+ ``yaml.safe_load``；
      成功回填缓存（st-perfz2 P0-1 起同时记录 text_sha256 指纹，供文本喂入口 sha 校验）；
      失败**不缓存**（撕裂读下一链自动真读）。
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
    # 盘面读路径保持既有命中契约：键命中（同 normcase+mtime_ns+size）即返回缓存，
    # **不重读文件**（test_hit_same_key_no_reread_same_object 钉死）。sha 校验只在
    # 文本喂入口（parse_registry_text_cached）做——那里字节不保证来自盘面。
    if _PARSE_CACHE["key"] == key and _PARSE_CACHE["data"] is not None:
        return _PARSE_CACHE["data"], None
    try:
        text = read(path)
    except Exception as e:  # noqa: BLE001 — 读失败不缓存，交调用方 fail-open/fail-closed
        return None, e
    try:
        import yaml

        data = yaml.safe_load(text)
    except Exception as e:  # noqa: BLE001 — 解析失败不缓存，交调用方 fail-open/fail-closed
        return None, e
    _store(key, data, text)
    return data, None


def parse_registry_text_cached(yaml_path: Path, text: str) -> tuple[dict | None, Exception | None]:
    """调用方已持文本（如 REGISTRY-YAML-PARSE 的 staged 字节）的共析入口。

    键=(盘面 path, mtime_ns, size)，与 ``parse_capability_registry_cached`` 同一条目——
    CREATE-GUARD 先解析过盘面（staged==盘面的常态）时本入口 **零解析** 直接命中
    （sha 校验把关）。返回 ``(data, exc)``，永不抛异常：

    - 命中（键同 + sha 同）→ 缓存 data，零解析零读盘。
    - 未命中 → ``yaml.safe_load(text)``；解析失败不缓存（与既有语义一致）。
    - 回填判据：**盘面现值字节 == 请求文本字节** 才回填（读盘 sha 比对，~30ms）——
      staged≠盘面（worktree 盘面陈旧/撕裂窗）时只返回解析结果，**绝不入缓存**，
      防 staged 数据以盘面键毒化 CREATE-GUARD/SSOT/OVERLAP 下游。
    - stat 失败（盘面不可达）→ 照常解析返回，不缓存。
    """
    path = Path(yaml_path)
    text_sha = text_sha256_of(text)
    try:
        key = cache_key_of(path)
    except OSError:
        key = None  # 盘面 stat 不可达：解析照常，缓存放弃（键缺失无失效判据）
    if key is not None and _cache_hit_for_text(key, text_sha):
        return _PARSE_CACHE["data"], None
    try:
        import yaml

        data = yaml.safe_load(text)
    except Exception as e:  # noqa: BLE001 — 解析失败不缓存，交调用方 fail-open/fail-closed
        return None, e
    if key is not None:
        try:
            disk_text = _default_reader(path)
        except OSError:
            disk_text = None
        if disk_text is not None and text_sha256_of(disk_text) == text_sha:
            _store(key, data, text)
    return data, None


def reset_parse_cache(key: object = None, /, *, data: object = None, text: str | None = None) -> None:
    """测试/进程内复位（默认清空）。保留 dict 容器身份——外部持引用仍可见。

    text 给定时同步记录 sha（回填的 data 有完整指纹，文本喂入口可命中）；
    text=None（历史调用形态）＝sha 未知＝文本喂入口按未命中处理（保守不串台）。
    """
    _PARSE_CACHE["key"] = key
    _PARSE_CACHE["data"] = data
    _PARSE_CACHE["text_sha256"] = text_sha256_of(text) if text is not None else None
