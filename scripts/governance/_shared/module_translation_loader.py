# [BLUEPRINT] SH-MODULE_TRANSLATION-001 | scripts/governance/_shared/module_translation_loader.py | §
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
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "module_translation_registry.yaml"
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
# 通用简介检测——识别被多个模块共用的模板化简介（治本跨节点重复，2026-08-02）
# ============================================================================
_GENERIC_PLAIN_CACHE: set[str] | None = None
_GENERIC_DESC_CACHE: set[str] | None = None


def _compute_generic_sets() -> tuple[set[str], set[str]]:
    """预计算通用简介集合：被 >1 个模块共用的模板化 plain_zh / desc_zh 文本。

    模块翻译注册表中部分条目填了相同的模板化简介（如"提供包入口和模块加载功能"），
    导致多个不同模块节点显示相同简介——跨节点重复。本函数预计算这些通用文本，
    供生成器调用 is_generic_plain_zh / is_generic_desc_zh 检测后回退到包感知描述。

    Returns:
        ``(generic_plain_set, generic_desc_set)``；YAML 不可用时返回两个空 set
    """
    global _GENERIC_PLAIN_CACHE, _GENERIC_DESC_CACHE
    if _GENERIC_PLAIN_CACHE is not None and _GENERIC_DESC_CACHE is not None:
        return _GENERIC_PLAIN_CACHE, _GENERIC_DESC_CACHE
    cache = _ensure_loaded()
    plain_counter: dict[str, set[str]] = {}
    desc_counter: dict[str, set[str]] = {}
    for mp, trans in cache.items():
        p = (trans.get("plain_zh") or "").strip()
        if p:
            plain_counter.setdefault(p, set()).add(mp)
        d = (trans.get("desc_zh") or "").strip()
        if d:
            desc_counter.setdefault(d, set()).add(mp)
    _GENERIC_PLAIN_CACHE = {t for t, paths in plain_counter.items() if len(paths) > 1}
    _GENERIC_DESC_CACHE = {t for t, paths in desc_counter.items() if len(paths) > 1}
    return _GENERIC_PLAIN_CACHE, _GENERIC_DESC_CACHE


def is_generic_plain_zh(plain: str) -> bool:
    """检测 plain_zh 是否为被多个模块共用的通用模板简介。

    Args:
        plain: 待检测的 plain_zh 文本

    Returns:
        True 表示该文本被 >1 个模块共用（应回退到包感知描述）；False 表示唯一
    """
    if not plain:
        return False
    generic_plain, _ = _compute_generic_sets()
    return plain.strip() in generic_plain


def is_generic_desc_zh(desc: str) -> bool:
    """检测 desc_zh 是否为被多个模块共用的通用模板简介。

    Args:
        desc: 待检测的 desc_zh 文本

    Returns:
        True 表示该文本被 >1 个模块共用；False 表示唯一
    """
    if not desc:
        return False
    _, generic_desc = _compute_generic_sets()
    return desc.strip() in generic_desc


# 通用后缀缓存：name_zh 前缀剥离后的后缀被多个模块共用（模板化后缀）
_GENERIC_SUFFIX_CACHE: set[str] | None = None


def _compute_generic_suffix_set() -> set[str]:
    """预计算通用后缀集合：plain_zh 去掉模块自身 name_zh 前缀后的后缀，被 >1 模块共用。

    治本场景：name_zh 前缀唯一（如不同模块名），但 plain_zh = "{name_zh}，定义本模块的异常类型"
    后缀"定义本模块的异常类型"被多个模块共用 → 跨节点重复。全串检测（is_generic_plain_zh）
    因前缀不同而漏判，需剥离前缀检测后缀。

    Returns:
        被多个模块共用的后缀文本集合；YAML 不可用时返回空 set
    """
    global _GENERIC_SUFFIX_CACHE
    if _GENERIC_SUFFIX_CACHE is not None:
        return _GENERIC_SUFFIX_CACHE
    cache = _ensure_loaded()
    suffix_counter: dict[str, set[str]] = {}
    for mp, trans in cache.items():
        plain = (trans.get("plain_zh") or "").strip().rstrip("。.，, ")
        name_zh = (trans.get("name_zh") or "").strip()
        if not plain or not name_zh:
            continue
        # 剥离 name_zh 前缀（plain 以 name_zh 开头时）
        if plain.startswith(name_zh):
            suffix = plain[len(name_zh):].strip("，,。.、：: ")
            if suffix and len(suffix) >= 4:
                suffix_counter.setdefault(suffix, set()).add(mp)
    _GENERIC_SUFFIX_CACHE = {t for t, paths in suffix_counter.items() if len(paths) > 1}
    return _GENERIC_SUFFIX_CACHE


def is_generic_plain_suffix(plain: str, name_zh: str) -> bool:
    """检测 plain_zh 剥离 name_zh 前缀后的后缀是否为多模块共用模板。

    Args:
        plain: 待检测的 plain_zh 文本
        name_zh: 模块中文名（作为前缀剥离基准）

    Returns:
        True 表示后缀被 >1 模块共用（应回退到路径派生描述）；False 表示唯一或无法剥离
    """
    if not plain or not name_zh:
        return False
    p = plain.strip().rstrip("。.，, ")
    if not p.startswith(name_zh):
        return False
    suffix = p[len(name_zh):].strip("，,。.、：: ")
    if len(suffix) < 4:
        return False
    return suffix in _compute_generic_suffix_set()


# ============================================================================
# battle_map_steps 段——作战地图环节叙事真源（BM-INV-003）
# ============================================================================
# 与 module_path 翻译并列的第二个真源段：环节级叙事。生成器
# (generate_battle_map_diagram.py) MUST 经此加载器读取环节叙事，禁止硬编码。
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

    数据来源：``module_translation_registry.yaml`` 的 ``battle_map_steps`` 段
    （翻译真源，规则数据，TRAE-062），非 depgraph.nodes 列。

    .. warning::
        本函数名含 "battle_map_step_ids"，易与 BM-INV-005 设想的
        ``depgraph.nodes.battle_map_step_ids`` 派生缓存列混淆。两者完全不同：

        - **本函数**：读 YAML 翻译真源的 step_id 集合（活代码，BM-INV-003
          缺失叙事检测用，对比 DB step_id 与 YAML step_id）
        - **nodes.battle_map_step_ids 列**：BM-INV-005 设想的 depgraph 派生缓存，
          **未落地**（depgraph.nodes 无此列，2026-08-03 核实，详见
          ``battlemap_schema.py`` BM-INV-005 注释 + battle_map_positioning.md §8.4）

    Returns:
        step_id 字符串列表（已登记顺序），YAML 不可用时返回空列表
    """
    return list(_ensure_steps_loaded().keys())


# ============================================================================
# battle_map_cross_cutting 段——作战地图横切视图真源（Gap3，2026-08-01）
# ============================================================================
# 与 battle_map_steps（环节级，按流程阶段线性串联）并列的第三个真源段：
# 横切级叙事——贯穿所有阶段的全局机制（§13漏斗/§14盘中事件/§16冲突矩阵）。
# 这些内容不属任何单一阶段，由生成器渲染为 battle_map_12_cross_cutting.md。
#
# 与 battle_map_steps 的区别：steps 是流程环节（线性串联），cross_cutting 是
# 横切机制（全局适用）。两者均属规则数据（TRAE-062），真源在 YAML。
# ============================================================================

# 横切视图缓存：None=未加载，dict=已加载（category → 横切 dict）
_CROSS_CUTTING_CACHE: dict[str, dict] | None = None


def _load_battle_map_cross_cutting_from_yaml() -> dict[str, dict]:
    """从 module_translation_registry.yaml 的 battle_map_cross_cutting 段加载横切视图。

    YAML 是横切视图主真源（SSoT，规则数据分类 TRAE-062）。失败/缺失返回空 dict
    （调用方回退到空横切视图，生成器跳过横切章节）。

    保留嵌套结构（levels/event_types/pipeline/conflicts/priority_hierarchy 等），
    调用方（生成器）按 category 自行渲染为 Markdown 表。

    Returns:
        ``{category: {category, name_zh, name_en, sketch_ref, related_steps,
                      plain_zh, mechanism_zh, ...嵌套结构}}``；
        文件缺失/解析失败/无 battle_map_cross_cutting 段时返回空 dict。
    """
    try:
        import yaml  # type: ignore[import-untyped]

        if not _REGISTRY_YAML.exists():
            return {}
        data = yaml.safe_load(_REGISTRY_YAML.read_text(encoding="utf-8")) or {}
        items = data.get("battle_map_cross_cutting") or []
        result: dict[str, dict] = {}
        for entry in items:
            if not isinstance(entry, dict):
                continue
            cat = entry.get("category")
            if not cat:
                continue
            # 整段保留（含嵌套 levels/event_types/conflicts 等），生成器按 category 渲染
            result[str(cat)] = entry
        return result
    except Exception:  # noqa: BLE001 — YAML 不可用时静默降级
        return {}


def _ensure_cross_cutting_loaded() -> dict[str, dict]:
    """加载并缓存横切视图映射：YAML 优先，失败返回空 dict。

    模块级缓存避免重复 IO。与 _ensure_steps_loaded()（环节叙事）独立缓存，
    互不干扰。

    Returns:
        ``{category: 横切 dict}``（可能为空 dict）
    """
    global _CROSS_CUTTING_CACHE
    if _CROSS_CUTTING_CACHE is not None:
        return _CROSS_CUTTING_CACHE
    _CROSS_CUTTING_CACHE = _load_battle_map_cross_cutting_from_yaml()
    return _CROSS_CUTTING_CACHE


def get_cross_cutting(category: str) -> dict | None:
    """查询指定横切类别的完整数据（Gap3 真源）。

    Args:
        category: 横切类别 ID，目前支持：
            ``"funnel"``（§13 筛选漏斗）、
            ``"intraday_events"``（§14 盘中事件）、
            ``"timeline"``（§15 计算节奏与时序）、
            ``"conflict_matrix"``（§16 冲突矩阵）、
            ``"distribution_awareness"``（§1.7 分布感知增强体系）

    Returns:
        横切 dict（含 name_zh/plain_zh/mechanism_zh + 嵌套结构 levels/event_types/
        conflicts 等）；未登记或 YAML 不可用返回 ``None``（生成器跳过该横切章节）
    """
    if not category:
        return None
    return _ensure_cross_cutting_loaded().get(str(category))


def get_cross_cutting_all() -> list[dict]:
    """返回所有横切类别数据列表（按 YAML 登记顺序，用于生成器遍历）。

    Returns:
        横切 dict 列表（每项含 category/name_zh/嵌套结构），YAML 不可用返回空列表
    """
    cache = _ensure_cross_cutting_loaded()
    # 按 funnel → intraday_events → timeline → conflict_matrix → distribution_awareness 的逻辑顺序返回
    order = ["funnel", "intraday_events", "timeline", "conflict_matrix", "distribution_awareness"]
    ordered = [cache[c] for c in order if c in cache]
    # 追加未在 order 中的类别（向前兼容未来新增横切类别）
    for cat, item in cache.items():
        if cat not in order:
            ordered.append(item)
    return ordered


def preload_battle_map_cross_cutting() -> dict[str, dict]:
    """预加载横切视图缓存到内存（批量场景调用一次，避免首次调用延迟）。

    安全调用：YAML 不可用时静默返回空 dict。
    """
    return _ensure_cross_cutting_loaded()


def all_cross_cutting_categories() -> list[str]:
    """返回所有已登记横切类别的 category 列表（用于对齐校验/生成器遍历）。

    Returns:
        category 字符串列表（已登记顺序），YAML 不可用时返回空列表
    """
    return list(_ensure_cross_cutting_loaded().keys())
