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
# [A_module] module_id=MOD-DATA_GOV-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-DATA-GOV Metadata Registry——元数据管理。

提供统一的元数据存储，支持按 key 注册、查询、前缀搜索。
用于记录表/因子/策略/信号的描述性元数据。

用法：
    reg = MetadataRegistry()
    reg.register("table.market.kline_daily", {
        "source": "tushare", "frequency": "daily", "rows": 5000000
    })
    meta = reg.get("table.market.kline_daily")
    tables = reg.search("table.")  # 前缀搜索

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 元数据注册请求 函数入参
#   fields: key唯一键 + value元数据字典 + category分类
#   code: register(key,value,category)
# - id: I2
#   name: 查询/搜索请求 函数入参
#   fields: key / field / prefix / category
#   code: get/get_value/search/list_by_category参数
# 层: 算法
# - id: A1
#   name_zh: ① 幂等注册
#   name_en: MetadataRegistry.register
#   intro: 把元数据拷贝成frozen条目按key存进内存字典，重复注册即更新
#   desc: MetadataEntry(key, dict(value), category) → _entries[key]=entry
#   inputs: I1
#   outputs: MetadataEntry
#   invariant: key唯一; 注册幂等; 值不可变
# - id: A2
#   name_zh: ② 键查询与字段取值
#   name_en: get/get_value/has
#   intro: 按key查条目，未注册抛KeyError，单字段缺失可给默认值
#   desc: key in _entries判定 → 无则KeyError/有则返回 → get_value取entry.value.get(field, default)
#   inputs: I2
#   outputs: MetadataEntry/字段值/布尔
# - id: A3
#   name_zh: ③ 前缀搜索与分类过滤
#   name_en: search/list_by_category
#   intro: 按key前缀或category过滤返回匹配条目列表
#   desc: k.startswith(prefix) 或 e.category==category 列表推导过滤
#   inputs: I2
#   outputs: MetadataEntry列表
# - id: A4
#   name_zh: ④ 移除与计数
#   name_en: remove/count
#   intro: 按键删除条目返回是否成功，或返回总条目数
#   desc: key存在则del返回True否则False → count=len(_entries)
#   inputs: I2
#   outputs: 布尔/整数
# 层: 输出
# - id: O1
#   name_zh: 元数据条目及查询结果 MetadataEntry
#   name_en: MetadataEntry
#   intro: 表/因子/策略/信号的描述性元数据条目或条目列表
#   invariant: frozen dataclass不可变
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# I2 --> A3
# I2 --> A4
# A1 --> O1
# A2 --> O1
# A3 --> O1
# A4 --> O1
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

    def register(self, key: str, value: dict[str, Any], category: str = "") -> MetadataEntry:
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

    def get_value(self, key: str, field: str, default: object = None) -> object:
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
        return [e for e in self._entries.values() if e.category == category]

    def search(self, prefix: str) -> list[MetadataEntry]:
        """前缀搜索。返回所有 key 以 prefix 开头的条目。"""
        return [e for k, e in self._entries.items() if k.startswith(prefix)]

    def remove(self, key: str) -> bool:
        """移除元数据条目。返回是否成功。"""
        if key not in self._entries:
            return False
        del self._entries[key]
        return True

    def count(self) -> int:
        """返回已注册条目数。"""
        return len(self._entries)
