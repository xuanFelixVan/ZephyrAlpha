# [BLUEPRINT] SH-MODULE-TRANSLATION-001 | scripts/governance/_shared/module_translation_loader.py | §
# [MODULE] scripts.governance._shared.module_translation_loader
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants (REPO_ROOT); docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml (模块翻译真源)
# [CONSUMERS] generate_domain_doc.py; 其他需模块级双语标签的生成器
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] YAML 是模块翻译真源;两级降级(YAML→空);调用方签名稳定零回归;中文在前英文在后
# [MODIFY-GUARD] 修改需通过任务卡
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] YAML 缺失→降级返回 None(不崩溃);条目缺 module_path→跳过
# [TESTS] tests/test_module_translation_loader.py (规划中)
# [TTL] permanent
"""module_translation_loader.py — 模块级翻译共享加载器（SSoT 真源）

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）+ SSoT 真源分类铁律（TRAE-062）：
模块级翻译属规则数据 → 真源是 ``module_translation_registry.yaml``（YAML 文件），
本模块是统一加载入口，生成器禁止各自硬编码模块翻译字典。

与现有翻译体系的分工（粒度不同，互补不重叠）：
- ``terminology_glossary.yaml``（术语级）：图示术语翻译（边类型/构建状态/作用域 等）
  → 真源加载器：``terminology_loader.py``
- ``functional_domain_registry.yaml``（域级）：D_XXX 域中文名（如 D_GOV_RULE → 规则治理）
  → 真源加载器：``domain_name_mapping.py``
- ``module_translation_registry.yaml``（模块级，本模块）：每个 .py 文件的中英文名+
  功能简介中英文（如 gate_types.py → 门禁类型定义 / Gate Types）
  → 真源加载器：本模块

#ARCH-SSOT-GLOSSARY-MERGE-001 把域级中文名从术语词汇表合并到功能域注册表后，
模块级翻译真源仍缺失（terminology_glossary 无 module 类别，functional_domain_registry
不含模块条目）。本注册表 + 本加载器补齐该缺口，使所有生成器共用同一模块级翻译真源。

参考架构：``terminology_loader.py`` 的两级降级（YAML→硬编码 fallback）。
模块翻译过于特化（每个 .py 文件独立条目），无跨生成器共享的硬编码 fallback，
故降级为 YAML → None（调用方自行决定回退策略，如读取 docstring 首行）。

用法 / Usage:
    from _shared.module_translation_loader import (
        get_module_translation,
        get_module_name_bilingual,
        get_module_desc_bilingual,
    )

    # 完整查询（返回 dict 或 None）
    trans = get_module_translation("src/zephyr/.../gate_types.py")
    if trans:
        # trans = {"name_zh": "门禁类型定义", "name_en": "Gate Types",
        #          "desc_zh": "...", "desc_en": "..."}
        ...

    # 直接取双语名称（中文在前 / English）
    name_bi = get_module_name_bilingual("src/zephyr/.../gate_types.py")
    # → "门禁类型定义 / Gate Types"

    # 直接取双语简介（中文在前 / English，无英文则仅中文）
    desc_bi = get_module_desc_bilingual("src/zephyr/.../gate_types.py")
    # → "GateType 枚举与 gate 相关 dataclass"
"""

from __future__ import annotations

import sys
from pathlib import Path

# 一次性 bootstrap：定位 _shared 父目录加入 sys.path（与同目录其他 _shared 模块一致，
# 使本模块可被直接 import 测试，亦对消费者已 bootstrap 的场景幂等）
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402

# 模块翻译 YAML 真源路径（SSoT：规则数据真源是 YAML 文件）
_REGISTRY_YAML = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry"
    / "catalogs" / "module_translation_registry.yaml"
)

# 模块级缓存：None=未加载，dict=已加载（module_path → {name_zh, name_en, desc_zh, desc_en}）
# 加载失败回退空 dict（无硬编码 fallback——模块翻译无跨生成器共享类别）
_PATH_CACHE: dict[str, dict[str, str]] | None = None


def _load_from_yaml() -> dict[str, dict[str, str]]:
    """从 module_translation_registry.yaml 加载 module_path → 翻译 dict 映射。

    YAML 是模块翻译的主真源（SSoT）。失败时返回空 dict（调用方回退到 docstring 等）。

    Returns:
        ``{module_path: {name_zh, name_en, desc_zh, desc_en}}``；
        文件缺失/解析失败/无 entries 时返回空 dict。
    """
    try:
        import yaml  # type: ignore[import-untyped]
        if not _REGISTRY_YAML.exists():
            return {}
        data = yaml.safe_load(_REGISTRY_YAML.read_text(encoding="utf-8")) or {}
        result: dict[str, dict[str, str]] = {}
        for entry in data.get("entries", []) or []:
            if not isinstance(entry, dict):
                continue
            path = entry.get("module_path")
            if not path:
                continue
            # 规范化路径为正斜杠（Windows 路径兼容）
            norm_path = str(path).replace("\\", "/")
            result[norm_path] = {
                "name_zh": str(entry.get("name_zh") or ""),
                "name_en": str(entry.get("name_en") or ""),
                "desc_zh": str(entry.get("desc_zh") or ""),
                "desc_en": str(entry.get("desc_en") or ""),
                "plain_zh": str(entry.get("plain_zh") or ""),
            }
        return result
    except Exception:  # noqa: BLE001 — YAML 不可用时静默降级
        return {}


def _ensure_loaded() -> dict[str, dict[str, str]]:
    """加载并缓存模块翻译映射：YAML 优先，失败返回空 dict。

    模块级缓存避免重复 IO。YAML 加载成功用 YAML；失败/为空返回空 dict
    （无硬编码 fallback——模块翻译无跨生成器共享类别，调用方自行回退）。

    Returns:
        ``{module_path: {name_zh, name_en, desc_zh, desc_en}}``（可能为空 dict）
    """
    global _PATH_CACHE
    if _PATH_CACHE is not None:
        return _PATH_CACHE
    _PATH_CACHE = _load_from_yaml()
    return _PATH_CACHE


def _normalize_path(module_path: str) -> str:
    """规范化模块路径为正斜杠（Windows 路径兼容 + 去除前后空白）。"""
    if not module_path:
        return ""
    return str(module_path).replace("\\", "/").strip()


def get_module_translation(module_path: str) -> dict[str, str] | None:
    """查询模块的完整翻译数据。

    Args:
        module_path: 模块相对路径（如 ``"src/zephyr/.../gate_types.py"``）；
                     Windows 反斜杠路径会自动规范化

    Returns:
        ``{"name_zh", "name_en", "desc_zh", "desc_en"}`` dict；
        未登记或 YAML 不可用返回 ``None``（调用方自行回退）
    """
    norm = _normalize_path(module_path)
    if not norm:
        return None
    cache = _ensure_loaded()
    return cache.get(norm)


def get_module_name_bilingual(module_path: str, sep: str = " / ") -> str:
    """返回模块双语名称（中文在前 / English）。

    遵循"中文在前英文在后"约定（用户偏好，便于阅读）。
    仅有中文返回中文；仅有英文返回英文；都无返回空串。

    Args:
        module_path: 模块相对路径
        sep: 分隔符，默认 ``" / "``

    Returns:
        ``"中文名 / English"`` / ``"中文名"`` / ``"English"`` / ``""``
    """
    trans = get_module_translation(module_path)
    if not trans:
        return ""
    name_zh = trans.get("name_zh", "")
    name_en = trans.get("name_en", "")
    if name_zh and name_en:
        return f"{name_zh}{sep}{name_en}"
    return name_zh or name_en


def get_module_desc_bilingual(module_path: str, sep: str = " / ") -> str:
    """返回模块双语功能简介（中文在前 / English）。

    遵循"中文在前英文在后"约定。仅有中文返回中文；仅有英文返回英文；
    都无返回空串（调用方回退到 docstring 首行等）。

    Args:
        module_path: 模块相对路径
        sep: 分隔符，默认 ``" / "``

    Returns:
        ``"中文简介 / English"`` / ``"中文简介"`` / ``"English"`` / ``""``
    """
    trans = get_module_translation(module_path)
    if not trans:
        return ""
    desc_zh = trans.get("desc_zh", "")
    desc_en = trans.get("desc_en", "")
    if desc_zh and desc_en:
        return f"{desc_zh}{sep}{desc_en}"
    return desc_zh or desc_en


def preload() -> dict[str, dict[str, str]]:
    """预加载缓存到内存（批量场景调用一次，避免首次调用延迟）。

    安全调用：YAML 不可用时静默返回空 dict。
    """
    return _ensure_loaded()


def get_module_plain(module_path: str) -> str:
    """返回模块的大白话解释（plain_zh，纯中文）。

    大白话解释覆盖：模块做什么用、目的、解决什么问题、如何实现。
    用于 Mermaid 节点标签——比 desc 更易懂、面向非开发读者。
    未登记或无 plain_zh 时返回空串（调用方决定是否回退到 desc_zh）。

    Args:
        module_path: 模块相对路径

    Returns:
        大白话解释字符串，或 ``""``
    """
    trans = get_module_translation(module_path)
    if not trans:
        return ""
    return trans.get("plain_zh", "")


# ============================================================================
# battle_map_steps 段——作战地图环节叙事真源（BM-INV-003）
# ============================================================================
# 与 module_path 翻译并列的第二个真源段：环节级叙事。生成器
# (generate_trading_flow_diagram.py) MUST 经此加载器读取环节叙事，禁止硬编码。
#
# 与 DB battle_map_steps.indicators JSONB 分工：
#   - 本段（YAML）：叙事文案 name_zh/name_en/plain_zh/mechanism_zh/indicators_zh
#   - DB indicators JSONB：结构化6件套 trigger/consumes/params/data_flow/code_mapping/degradation
#
# step_id 格式 BM-<阶段缩写>-<序号>（如 BM-BUY-04），与 DB step_id / narrative_ref 对齐。
# ============================================================================

# 环节叙事缓存：None=未加载，dict=已加载（step_id → 叙事 dict）
_STEP_CACHE: dict[str, dict[str, str]] | None = None


def _load_battle_map_steps_from_yaml() -> dict[str, dict[str, str]]:
    """从 module_translation_registry.yaml 的 battle_map_steps 段加载环节叙事。

    YAML 是环节叙事主真源（SSoT，规则数据分类 TRAE-062）。失败/缺失返回空 dict
    （调用方回退到 DB step_name 或空串）。

    Returns:
        ``{step_id: {flow_stage, name_zh, name_en, plain_zh, mechanism_zh, indicators_zh}}``；
        文件缺失/解析失败/无 battle_map_steps 段时返回空 dict。
    """
    try:
        import yaml  # type: ignore[import-untyped]
        if not _REGISTRY_YAML.exists():
            return {}
        data = yaml.safe_load(_REGISTRY_YAML.read_text(encoding="utf-8")) or {}
        steps = data.get("battle_map_steps") or []
        result: dict[str, dict[str, str]] = {}
        for entry in steps:
            if not isinstance(entry, dict):
                continue
            sid = entry.get("step_id")
            if not sid:
                continue
            result[str(sid)] = {
                "step_id": str(sid),
                "flow_stage": str(entry.get("flow_stage") or ""),
                "name_zh": str(entry.get("name_zh") or ""),
                "name_en": str(entry.get("name_en") or ""),
                "plain_zh": str(entry.get("plain_zh") or ""),
                "mechanism_zh": str(entry.get("mechanism_zh") or ""),
                "indicators_zh": str(entry.get("indicators_zh") or ""),
            }
        return result
    except Exception:  # noqa: BLE001 — YAML 不可用时静默降级
        return {}


def _ensure_steps_loaded() -> dict[str, dict[str, str]]:
    """加载并缓存环节叙事映射：YAML 优先，失败返回空 dict。

    模块级缓存避免重复 IO。与 _ensure_loaded()（module 翻译）独立缓存，
    互不干扰。

    Returns:
        ``{step_id: {name_zh, name_en, plain_zh, mechanism_zh, indicators_zh}}``（可能为空 dict）
    """
    global _STEP_CACHE
    if _STEP_CACHE is not None:
        return _STEP_CACHE
    _STEP_CACHE = _load_battle_map_steps_from_yaml()
    return _STEP_CACHE


def get_step_narrative(step_id: str) -> dict[str, str] | None:
    """查询作战环节的完整叙事数据（BM-INV-003 真源）。

    Args:
        step_id: 环节 ID（如 ``"BM-BUY-04"``），与 DB battle_map_steps.step_id 对齐

    Returns:
        ``{step_id, flow_stage, name_zh, name_en, plain_zh, mechanism_zh, indicators_zh}`` dict；
        未登记或 YAML 不可用返回 ``None``（调用方回退到 DB step_name）
    """
    if not step_id:
        return None
    return _ensure_steps_loaded().get(str(step_id))


def get_step_name_bilingual(step_id: str, sep: str = " / ") -> str:
    """返回环节双语名称（中文在前 / English）。

    遵循"中文在前英文在后"约定。仅有中文返回中文；仅有英文返回英文；都无返回空串
    （调用方回退到 DB step_name）。

    Args:
        step_id: 环节 ID
        sep: 分隔符，默认 ``" / "``

    Returns:
        ``"中文名 / English"`` / ``"中文名"`` / ``"English"`` / ``""``
    """
    trans = get_step_narrative(step_id)
    if not trans:
        return ""
    name_zh = trans.get("name_zh", "")
    name_en = trans.get("name_en", "")
    if name_zh and name_en:
        return f"{name_zh}{sep}{name_en}"
    return name_zh or name_en


def get_step_plain(step_id: str) -> str:
    """返回环节大白话一句话（plain_zh，纯中文）。

    用于 Mermaid 节点标签——比机制说明更易懂、面向非开发读者。
    未登记或无 plain_zh 时返回空串（调用方回退到 name_zh）。

    Args:
        step_id: 环节 ID

    Returns:
        大白话字符串，或 ``""``
    """
    trans = get_step_narrative(step_id)
    if not trans:
        return ""
    return trans.get("plain_zh", "")


def get_step_mechanism(step_id: str) -> str:
    """返回环节机制说明（mechanism_zh，纯中文多行）。

    用于作战地图环节详情——解释这个环节怎么运转。未登记返回空串。

    Args:
        step_id: 环节 ID

    Returns:
        机制说明字符串，或 ``""``
    """
    trans = get_step_narrative(step_id)
    if not trans:
        return ""
    return trans.get("mechanism_zh", "")


def get_step_indicators_zh(step_id: str) -> str:
    """返回环节指标文案（indicators_zh，纯中文多行）。

    6件套的大段解释文案，与 DB indicators JSONB 结构化字段互补。
    用于作战地图环节详情——人读的指标说明。未登记返回空串。

    Args:
        step_id: 环节 ID

    Returns:
        指标文案字符串，或 ``""``
    """
    trans = get_step_narrative(step_id)
    if not trans:
        return ""
    return trans.get("indicators_zh", "")


def preload_battle_map_steps() -> dict[str, dict[str, str]]:
    """预加载环节叙事缓存到内存（批量场景调用一次，避免首次调用延迟）。

    安全调用：YAML 不可用时静默返回空 dict。
    """
    return _ensure_steps_loaded()


def all_battle_map_step_ids() -> list[str]:
    """返回所有已登记环节的 step_id 列表（用于对齐校验/生成器遍历）。

    Returns:
        step_id 字符串列表（已登记顺序），YAML 不可用时返回空列表
    """
    return list(_ensure_steps_loaded().keys())
