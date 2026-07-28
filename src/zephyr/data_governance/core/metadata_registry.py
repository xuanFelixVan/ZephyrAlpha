# [BLUEPRINT] MOD-DATA_GOV-003 | docs/03_modules/_domain_data_governance/blueprint.md
# [MODULE] zephyr.data_governance.core.metadata_registry
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] key唯一; 注册幂等(重复注册更新); 值不可变(frozen dataclass)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] key不存在->KeyError; 前缀搜索无匹配->返回空列表
# [TESTS] tests/data_governance/test_metadata_registry.py
# [TTL] permanent
"""D-DATA-GOV Metadata Registry——元数据管理。

提供统一的元数据存储，支持按 key 注册、查询、前缀搜索。
用于记录表/因子/策略/信号的描述性元数据。

用法：
    reg = MetadataRegistry()
    reg.register("table.market.kline_daily", {
        "source": "tushare", "frequency": "daily", "rows": 5000000
    })
    meta = reg.get("table.market.kline_daily")
    tables = reg.search("table.")  # 前缀搜索
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MetadataEntry:
    """元数据条目。

    Attributes:
        key: 唯一键 (如 "table.market.kline_daily")
        value: 元数据字典
        category: 分类 (如 "table", "factor", "strategy")
    """

    key: str
    value: dict[str, Any]
    category: str = ""


class MetadataRegistry:
    """元数据注册表——内存级 key-value 存储。

    支持注册、查询、前缀搜索、分类过滤。
    注册幂等（重复注册同一 key 会更新）。
    """

    def __init__(self) -> None:
        self._entries: dict[str, MetadataEntry] = {}

    def register(
        self, key: str, value: dict[str, Any], category: str = ""
    ) -> MetadataEntry:
        """注册或更新元数据条目。

        Args:
            key: 唯一键
            value: 元数据字典
            category: 分类标签

        Returns:
            注册的 MetadataEntry
        """
        entry = MetadataEntry(key, dict(value), category)
        self._entries[key] = entry
        return entry

    def get(self, key: str) -> MetadataEntry:
        """获取元数据。未注册抛 KeyError。"""
        if key not in self._entries:
            raise KeyError(f"元数据 key '{key}' 未注册")
        return self._entries[key]

    def get_value(self, key: str, field: str, default: Any = None) -> Any:
        """获取元数据中的单个字段值。"""
        entry = self._entries.get(key)
        if entry is None:
            return default
        return entry.value.get(field, default)

    def has(self, key: str) -> bool:
        """判断 key 是否已注册。"""
        return key in self._entries

    def list_keys(self) -> list[str]:
        """返回所有已注册的 key。"""
        return list(self._entries.keys())

    def list_by_category(self, category: str) -> list[MetadataEntry]:
        """按分类过滤。"""
        return [
            e for e in self._entries.values() if e.category == category
        ]

    def search(self, prefix: str) -> list[MetadataEntry]:
        """前缀搜索。返回所有 key 以 prefix 开头的条目。"""
        return [
            e for k, e in self._entries.items() if k.startswith(prefix)
        ]

    def remove(self, key: str) -> bool:
        """移除元数据条目。返回是否成功。"""
        if key not in self._entries:
            return False
        del self._entries[key]
        return True

    def count(self) -> int:
        """返回已注册条目数。"""
        return len(self._entries)
