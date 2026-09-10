# [BLUEPRINT] INDUSTRY-GRAPH-FIELD-DICTIONARY | (Owner 2026-09-10 方案 A 字段标准单一真源) | §
# [TTL] permanent
# [MODULE] scripts.industry_graph.vocab_loader
# [DOMAIN] D_DATA
# [DEPENDENCIES] PyYAML; docs/01_policies_and_standards/_registry/catalogs/industry_graph_field_dictionary.yaml (词表唯一真源)
# [CONSUMERS] websearch_ingest.py (写入校验词表); graph_quality_check.py (引擎检查词表); ths_import.py (category 词表); tests/industry_graph/test_field_dictionary_alignment.py (四方对齐)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 词表唯一真源=industry_graph_field_dictionary.yaml vocab 段——改词表只改 YAML, 工具/引擎 import 本 loader 自动一致(消灭"同 commit 人肉同步三处"纪律); 缓存进程级单例; YAML 缺失/损坏 fail-closed 抛异常(禁止静默回退旧常量=双真源复活); 词表值顺序即展示序(function_roles 八值/roles 五值)
# [MODIFY-GUARD] docs/01_policies_and_standards/_registry/catalogs/industry_graph_field_dictionary.yaml
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] YAML 不可达/解析失败->抛异常(fail-closed, 上层工具/引擎终止)
# [TESTS] tests/industry_graph/test_field_dictionary_alignment.py 四方对齐(YAML↔DDL↔工具↔引擎)
# [TTL] permanent
"""产业链图谱词表加载器（字段字典单一真源的消费入口，Owner 2026-09-10 方案 A）。

用法::

    from industry_graph.vocab_loader import load_vocab
    v = load_vocab()
    v["tiers"]["values"]          # -> ["上游","中游","下游"]
    v["roles_std"]["values"]      # -> ["龙头","核心","主要","参与","提及"]

对齐先例：alert_threshold_registry（改阈值先改表，tests 强制注册表↔代码一致）。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

DICT_PATH = Path(__file__).resolve().parents[2] / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "industry_graph_field_dictionary.yaml"
_CACHE: dict[str, Any] | None = None


def load_vocab() -> dict[str, Any]:
    """加载字段字典 vocab 段（进程级缓存单例；fail-closed 禁静默回退）。"""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    import yaml

    if not DICT_PATH.is_file():
        raise FileNotFoundError(f"字段字典真源缺失(fail-closed): {DICT_PATH}")
    data = yaml.safe_load(DICT_PATH.read_text(encoding="utf-8")) or {}
    vocab = data.get("vocab")
    if not isinstance(vocab, dict) or not vocab:
        raise ValueError(f"字段字典 vocab 段缺失或为空(fail-closed): {DICT_PATH}")
    _CACHE = vocab
    return _CACHE


def load_tables() -> dict[str, Any]:
    """加载字段字典 tables 段（逐表逐字段标准；对齐测试消费）。"""
    import yaml

    if not DICT_PATH.is_file():
        raise FileNotFoundError(f"字段字典真源缺失(fail-closed): {DICT_PATH}")
    data = yaml.safe_load(DICT_PATH.read_text(encoding="utf-8")) or {}
    tables = data.get("tables")
    if not isinstance(tables, dict) or not tables:
        raise ValueError(f"字段字典 tables 段缺失或为空(fail-closed): {DICT_PATH}")
    return tables
