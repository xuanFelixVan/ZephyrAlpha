# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.table_registry
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.io.paths
# [CONSUMERS] zephyr.data.scheduler; zephyr.data.implementations.*_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] business_data_categories.yaml 是表名/品类唯一真源; TableRegistry.table() 返回 "{database}.{table}" 全限定名; validate_tasks_yaml 仅 WARN 不阻断（渐进式收紧 Phase 2）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] yaml 文件不存在->log warning+返回空注册表(开发环境友好); table() 查不到 category_id->raise KeyError(fail-closed,禁止凭记忆编表名)
# [TESTS] tests/zephyr/data/test_table_registry.py
# [A_module] module_id=MOD-GOV-table_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase 2）。

背景：
    business_data_categories.yaml 是业务数据品类唯一真源（声明态规则数据，真源是 YAML），
    含 98 条品类记录。但改造前 0 行代码消费它——所有 provider/scheduler 直接硬编码表名
    字符串，与 tasks.yaml 形成双真源。长期漂移必然发生（改名只改一处，另一处遗忘）。

    裁定 #ARCH-CH-024 第一性原理根因：SSoT 真源已建立声明闭环（YAML 存在），但消费闭环
    未建立（代码不 import 真源）、强制闭环未建立（commit gate 不阻断绕过）。表名属于声明态
    规则数据（trae_062 SSoT 分类铁律：表名是 schema 声明而非 DB 实例），真源是 YAML。

治本原则（裁定 #ARCH-CH-024）：
    - business_data_categories.yaml 是表名/品类唯一真源（规则数据）
    - 代码 MUST 通过 TableRegistry.table(category_id) 派生表名，禁止硬编码字符串
    - TableRegistry 启动时加载 YAML，构建 category_id -> "{database}.{table}" 映射
    - validate_tasks_yaml() 校验 tasks.yaml.table ⊆ registry，不一致仅 WARN（不阻断，
      渐进式收紧；Phase 4 commit gate 将升级为 block）

公共接口：
    - TableRegistry.table(category_id) -> str: 返回全限定表名（查不到抛 KeyError）
    - TableRegistry.all_tables() -> list[str]: 返回所有已注册全限定表名
    - TableRegistry.is_registered(table) -> bool: 判断全限定表名是否已注册
    - TableRegistry.validate_tasks_yaml(tasks) -> list[str]: 校验 tasks.yaml 与 registry 一致性
    - get_registry() -> TableRegistry: 返回单例（幂等加载）

Phase 2 范围（本次落地）：
    - 新建本模块（TableRegistry 消费层）
    - scheduler._load_config() 末尾调用 validate_tasks_yaml() WARN 校验

Phase 5 长期方向（不实施，登记为后续）：
    - 240 处硬编码表名替换为 TableRegistry.table() 常量引用
    - commit gate（GATE-TABLE-NAME-REGISTRY）升级为 block

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: categories 参数
#   fields: 参数 categories（无注解）
#   code: table_registry.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TableRegistry
#   name_en: TableRegistry
#   intro: 表名/品类注册表消费层。
#   desc: 表名/品类注册表消费层。 启动时加载 business_data_categories.yaml，构建： _by_category: category_id -> "{datab…；公共方法（定义序）: table…
#   inputs: categories
#   outputs: 返回值
# - id: A2
#   name_zh: ② get_registry
#   name_en: get_registry
#   intro: 返回 TableRegistry 单例（幂等加载，线程安全）。
#   desc: 返回 TableRegistry 单例（幂等加载，线程安全）。；源码 L238-L247
#   inputs: 无参数
#   outputs: TableRegistry
# - id: A3
#   name_zh: ③ reset_registry_singleton
#   name_en: reset_registry_singleton
#   intro: 重置单例（仅供测试使用，确保测试间隔离）。
#   desc: 重置单例（仅供测试使用，确保测试间隔离）。；源码 L250-L254
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: TableRegistry
#   name_en: TableRegistry
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.scheduler; zephyr.data.implementations.*_provider
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path

import yaml

from zephyr.shared.io.paths import REPO_ROOT

log = logging.getLogger(__name__)

# 品类注册表 YAML 真源路径（business_data_categories.yaml）
_CATEGORIES_PATH: Path = (
    REPO_ROOT / "docs" / "03_modules" / "_cross_layer" / "database" / "business_data_categories.yaml"
)

# 单例锁（幂等加载）
_load_lock = threading.Lock()
_singleton: TableRegistry | None = None


class TableRegistry:
    """表名/品类注册表消费层。

    启动时加载 business_data_categories.yaml，构建：
        _by_category: category_id -> "{database}.{table}"
        _by_table: "{database}.{table}" -> category_id

    查询接口 fail-closed（查不到抛 KeyError，禁止凭记忆编表名）。
    """

    def __init__(self, categories: list[dict] | None = None) -> None:
        """初始化注册表。

        Args:
            categories: 预加载的品类列表（供测试注入）。None 则从 YAML 真源加载。
        """
        if categories is not None:
            self._categories = categories
        else:
            self._categories = self._load_yaml()
        # 构建 category_id -> "{database}.{table}" 映射
        self._by_category: dict[str, str] = {}
        # 构建 "{database}.{table}" -> category_id 反查映射
        self._by_table: dict[str, str] = {}
        for cat in self._categories:
            cid = cat.get("category_id")
            db = cat.get("database")
            tbl = cat.get("table")
            if not cid or not db or not tbl:
                continue
            full = f"{db}.{tbl}"
            self._by_category[cid] = full
            # 同表多品类时保留首个 category_id（反查仅用于 is_registered 判定）
            self._by_table.setdefault(full, cid)

    @staticmethod
    def _load_yaml() -> list[dict]:
        """从真源 YAML 加载品类列表。

        文件不存在时 log warning 并返回空列表（开发环境友好，
        后续 table() 查询会因空注册表抛 KeyError fail-closed）。
        """
        if not _CATEGORIES_PATH.is_file():
            log.warning("品类注册表不存在: %s（表名校验将失效）", _CATEGORIES_PATH)
            return []
        try:
            with open(_CATEGORIES_PATH, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, list):
                log.info("已加载品类注册表: %d 条品类", len(data))
                return data
            log.warning("品类注册表格式异常（非 list）: %s", _CATEGORIES_PATH)
            return []
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.error("品类注册表加载失败 %s: %s", _CATEGORIES_PATH, e)
            return []

    def table(self, category_id: str) -> str:
        """按 category_id 返回全限定表名 "{database}.{table}"。

        Args:
            category_id: 品类标识（如 market_kline_daily）。

        Returns:
            全限定表名（如 c1_market.kline_daily）。

        Raises:
            KeyError: category_id 未注册（fail-closed，禁止凭记忆编表名）。
        """
        if category_id not in self._by_category:
            raise KeyError(
                f"category_id '{category_id}' 未在 business_data_categories.yaml 注册。"
                f"请在真源 YAML 新增品类条目（禁止硬编码表名绕过真源）。"
            )
        return self._by_category[category_id]

    def all_tables(self) -> list[str]:
        """返回所有已注册全限定表名。"""
        return list(self._by_table.keys())

    def is_registered(self, table: str) -> bool:
        """判断全限定表名是否已注册。

        Args:
            table: 全限定表名（如 c1_market.kline_daily）。

        Returns:
            True=已注册；False=未注册（需在 YAML 补登）。
        """
        return table in self._by_table

    def validate_tasks_yaml(self, tasks: list[dict]) -> list[str]:
        """校验 tasks.yaml.table ⊆ registry，返回警告列表。

        比对逻辑：tasks.yaml 每条任务的 table 字段（如 c1_market.kline_daily）
        必须存在于 registry 的全限定表名集合中。不一致仅 WARN（不阻断启动，
        渐进式收紧；Phase 4 commit gate 将升级为 block）。

        Args:
            tasks: tasks.yaml 解析出的任务列表（每条含 table 字段）。

        Returns:
            警告消息列表（空列表=全部一致）。
        """
        warnings: list[str] = []
        if not self._by_table:
            warnings.append(
                "品类注册表为空，无法校验 tasks.yaml 表名一致性（business_data_categories.yaml 未加载或为空）"
            )
            return warnings
        for task in tasks:
            task_id = task.get("task_id", "<unknown>")
            table = task.get("table")
            if not table:
                continue
            if not self.is_registered(table):
                warnings.append(
                    f"task '{task_id}' table '{table}' 未在 business_data_categories.yaml 注册（双真源漂移风险）"
                )
        return warnings


def get_registry() -> TableRegistry:
    """返回 TableRegistry 单例（幂等加载，线程安全）。"""
    global _singleton
    if _singleton is not None:
        return _singleton
    with _load_lock:
        if _singleton is not None:
            return _singleton
        _singleton = TableRegistry()
        return _singleton


def reset_registry_singleton() -> None:
    """重置单例（仅供测试使用，确保测试间隔离）。"""
    global _singleton
    with _load_lock:
        _singleton = None
