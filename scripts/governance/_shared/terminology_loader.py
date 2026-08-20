# [BLUEPRINT] SH-TERM-001 | scripts/governance/_shared/terminology_loader.py | §
# [MODULE] scripts.governance._shared.terminology_loader
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants (REPO_ROOT); docs/01_policies_and_standards/_registry/catalogs/terminology_glossary.yaml (术语真源)
# [CONSUMERS] generate_decision_diagram.py; generate_dataflow_diagram.py; generate_data_acquisition_flow.py; generate_data_inventory.py; generate_navigation_index.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] YAML 是术语翻译真源;三级降级(YAML→硬编码 fallback→空);调用方签名稳定零回归
# [MODIFY-GUARD] 修改需通过任务卡
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] YAML 缺失→降级硬编码 fallback(不崩溃);条目缺 category/en/zh→跳过
# [TESTS] tests/test_generate_decision_diagram.py; tests/test_generate_dataflow_diagram.py (间接覆盖)
# [TTL] permanent
"""terminology_loader.py — 架构文档术语词汇表共享加载器（SSoT 真源）

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）+ SSoT 真源分类铁律（TRAE-062）：
术语词汇表属规则数据 → 真源是 ``terminology_glossary.yaml``（YAML 文件），
本模块是统一加载入口，生成器禁止各自硬编码中文术语字典。

参考架构：domain_name_mapping.py 的三级降级（DB→YAML→硬编码 fallback）。
本模块对应术语翻译场景的三级降级：
1. ``terminology_glossary.yaml``（主真源，全量 ~200 条，10+ 类别）
2. 硬编码 fallback（仅跨生成器共享类别 ~25 项：edge_type/build_status/maturity/
   pit_policy/trigger_type/scope，YAML 缺失时降级，保证生成器不崩溃）
3. 返回空串 / 原文（最终降级，generator 显示 en-only）

与 domain_name_mapping.py 的分工：
- domain_name_mapping.py：功能域规范名（D_XXX，含遗留图示用名）的 SSoT，
  读 functional_domain_registry.yaml / DB。
- 本模块：图示术语翻译（边类型/构建状态/作用域/实体名/数据源/表名 等），
  不含域中文名——域中文名真源归 functional_domain_registry.yaml
  （#ARCH-SSOT-GLOSSARY-MERGE-001），原 domain_id_display 类别已从本词汇表删除。

用法 / Usage:
    from _shared.terminology_loader import get_category_map, get_flat_map, get_zh, get_en_zh

    # 按类别取整张映射（生成器替换硬编码字典）
    _EDGE_TYPE_ZH = get_category_map("edge_type")
    _ZH_MAP = get_flat_map(["edge_type", "build_status", "scope", ...])

    # 单条查询
    zh = get_zh("triggering", "edge_type")            # → "触发"
    label = get_en_zh("triggering", "edge_type")      # → "triggering / 触发"
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

# 术语词汇表 YAML 真源路径（SSoT：规则数据真源是 YAML 文件）
_GLOSSARY_YAML = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "terminology_glossary.yaml"
)

# 模块级缓存：None=未加载，dict=已加载（category → {en: zh}）
# 加载失败回退硬编码 fallback，故缓存永不为 None（首次调用后）
_CATEGORY_CACHE: dict[str, dict[str, str]] | None = None


# ── 硬编码 fallback（仅跨生成器共享类别，YAML 缺失时降级）──────────────────────
# 不含生成器专用大类别（entity_name/table_name/data_source/decision_domain_short/
# layer_name_short）——这些类别 YAML 缺失时返回空，generator 显示 en-only。
# 仅覆盖 edge_type/build_status/maturity/pit_policy/trigger_type/scope 6 类共享术语。
_HARDCODED_FALLBACK: dict[str, dict[str, str]] = {
    "edge_type": {
        "triggering": "触发",
        "informing": "告知",
        "approving": "批准",
        "feedback": "反馈",
        "portfolio_target": "仓位目标",
        "risk_check": "风控检查",
        "produces": "产出",
        "consumed by": "被消费于",
    },
    "build_status": {
        "design": "设计",
        "generated": "已生成",
    },
    "maturity": {
        "design": "设计",
        "production": "生产",
    },
    "pit_policy": {
        "strict": "严格",
        "loose": "宽松",
        "none": "无",
    },
    "trigger_type": {
        "event_driven": "事件驱动",
        "scheduled": "定时",
        "manual": "手动",
        "stream": "流式",
    },
    "scope": {
        "production": "生产",
        "backtest_internal": "回测内部",
    },
}


def _load_from_yaml() -> dict[str, dict[str, str]]:
    """从 terminology_glossary.yaml 加载 category → {en: zh} 映射。

    YAML 是术语翻译的主真源（SSoT）。失败时返回空 dict（调用方回退硬编码 fallback）。

    Returns:
        ``{category: {en: zh}}``；文件缺失/解析失败/无 entries 时返回空 dict。
    """
    try:
        import yaml  # type: ignore[import-untyped]

        if not _GLOSSARY_YAML.exists():
            return {}
        data = yaml.safe_load(_GLOSSARY_YAML.read_text(encoding="utf-8")) or {}
        result: dict[str, dict[str, str]] = {}
        for entry in data.get("entries", []) or []:
            if not isinstance(entry, dict):
                continue
            cat = entry.get("category")
            en = entry.get("en")
            zh = entry.get("zh")
            if cat and en and zh:
                result.setdefault(str(cat), {})[str(en)] = str(zh)
        return result
    except Exception:  # noqa: BLE001 — YAML 不可用时静默降级
        return {}


def _ensure_loaded() -> dict[str, dict[str, str]]:
    """加载并缓存术语映射：YAML 优先 → 硬编码 fallback。

    模块级缓存避免重复 IO。YAML 加载成功（非空）用 YAML；失败/为空回退硬编码 fallback。

    Returns:
        ``{category: {en: zh}}``（永不为空 dict——至少含硬编码 fallback 的 6 类共享术语）
    """
    global _CATEGORY_CACHE
    if _CATEGORY_CACHE is not None:
        return _CATEGORY_CACHE
    yaml_data = _load_from_yaml()
    _CATEGORY_CACHE = yaml_data if yaml_data else _HARDCODED_FALLBACK
    return _CATEGORY_CACHE


def get_category_map(category: str) -> dict[str, str]:
    """获取整个类别的 en→zh 映射（替换生成器硬编码字典的入口）。

    用于 ``_EDGE_TYPE_ZH = get_category_map("edge_type")`` 这类一次性加载。
    返回副本，防止调用方意外修改缓存。

    Args:
        category: 类别名，如 ``"edge_type"`` / ``"table_name"``

    Returns:
        ``{en: zh}`` dict；类别不存在时返回空 dict（调用方显示 en-only）
    """
    cache = _ensure_loaded()
    return dict(cache.get(category, {}))


def get_flat_map(categories: list[str] | None = None) -> dict[str, str]:
    """合并多个类别为扁平 en→zh dict（兼容 dataflow 的跨类别 _ZH_MAP 模式）。

    用于 dataflow 原有 ``_ZH_MAP``（跨类别扁平 dict，``_zh(en)`` 按 key 查无 category 参数）。
    指定 categories 可限定合并范围，避免全类别合并导致意外匹配（如某个 en 值碰巧
    命中 decision_domain_short）。categories=None 合并全部类别。

    同一 en 在多类别出现且 zh 一致时合并幂等（如 design/build_status 与 maturity 均→设计）；
    若 zh 不一致，后处理类别覆盖（实践中无此冲突）。

    Args:
        categories: 要合并的类别列表；None=合并全部

    Returns:
        扁平 ``{en: zh}`` dict
    """
    cache = _ensure_loaded()
    cats = categories if categories is not None else list(cache.keys())
    result: dict[str, str] = {}
    for cat in cats:
        result.update(cache.get(cat, {}))
    return result


def get_zh(en: str | None, category: str) -> str:
    """单条 en→zh 查询。未找到或 en 为空返回空串。

    Args:
        en: 英文术语，如 ``"triggering"``
        category: 类别名，如 ``"edge_type"``

    Returns:
        中文翻译；未找到返回 ``""``
    """
    if not en:
        return ""
    cache = _ensure_loaded()
    return cache.get(category, {}).get(en, "")


def get_en_zh(en: str | None, category: str, sep: str = " / ") -> str:
    """英文 + 中文并列（如 ``'triggering / 触发'``）。

    与 dataflow ``_en_zh`` 约定一致：en 为 None/空返回 ``"-"``；
    有中文返回 ``f"{en}{sep}{zh}"``；无中文返回原 en。

    Args:
        en: 英文术语
        category: 类别名
        sep: 分隔符，默认 ``" / "``

    Returns:
        ``"en / zh"`` / ``"en"`` / ``"-"``（en 为空时）
    """
    if not en:
        return "-"
    zh = get_zh(en, category)
    return f"{en}{sep}{zh}" if zh else en


def preload() -> dict[str, dict[str, str]]:
    """预加载缓存到内存（批量场景调用一次，避免首次调用延迟）。

    安全调用：YAML 不可用时静默回退硬编码 fallback。
    """
    return _ensure_loaded()
