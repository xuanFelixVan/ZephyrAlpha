# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.registry_adapter
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_registry_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MOD-INF-026 §17 — 24 个异构注册表统一解析适配器。

RegistryAdapter 抽象基类 + 7 个适配器实现 + RegistryManager。
对标 ETL 管道 + abc.ABC 抽象基类模式。
"""

import csv
from zephyr.shared.io.sqlite_factory import get_db_connection
import io
import re
from abc import ABC, abstractmethod
from pathlib import Path

from zephyr.infrastructure.asset_inventory.models import ClassifiedAsset, RegistryEntry

# 5.66.3 修复：表名白名单，防止 f-string 拼接表名的 SQL 注入风险。
# SqliteAdapter 读取 governance.db（zalpha_metadata.db）各表，白名单覆盖全部已知表名。
_ALLOWED_TABLES = frozenset(
    {
        "tasks",
        "events",
        "knowledge",
        "gate_runs",
        "circuit_breaker_state",
        "task_files",
        "_schema_version",
        "slow_queries",
        "tx_idempotency",
        "task_events",
        "task_snapshots",
        "fle_metrics",
        "fle_alerts",
        "fle_dispatch_log",
        "task_reviews",
        "f5_state",
    }
)


def _validate_table_name(table: str) -> str:
    """5.66.3 修复：白名单校验表名，仅允许已知表名用于 SQL 拼接。"""
    if table not in _ALLOWED_TABLES:
        raise ValueError(f"table name not in whitelist: {table!r}")
    return table


# === 裁定#217 Tier2 P3 Extract Method 重构（2026-07-15）===
# 原 YamlListAdapter._parse_dict 84 行 McCabe=42（3 分支：tiers/dict-value/list-item，
# dict-value 和 list-item 路径提取逻辑重复）。治本：提取为 2 个模块级 helper（均 McCabe≤15），
# _parse_dict 简化为 dispatcher（McCabe≈5）。行为等价：tiers/dict/list 分支顺序不变，
# asset_path 提取 fallback 链不变（asset_key→physical_path→path→look_like_path→first_str），
# extra dict 过滤规则不变。


def _parse_tiers_registries(data: dict, registry_id: str) -> list[RegistryEntry]:
    """解析 registry_of_registries.yaml 的 tiers 结构（registry_id 缺省时回退 registry_id 参数）。"""
    entries: list[RegistryEntry] = []
    for tier in data["tiers"]:
        for reg in tier.get("registries", []):
            phys = reg.get("physical_path", "")
            if phys:
                entries.append(
                    RegistryEntry(
                        registry_id=reg.get("registry_id", registry_id),
                        registry_path="",
                        entry_path=phys,
                        extra={k: v for k, v in reg.items() if v is not None and k != "physical_path"},
                    )
                )
    return entries


def _extract_asset_path(item: dict, asset_key: str) -> str | None:
    """从 dict 条目提取 asset_path（3 步 fallback 链，与原 _parse_dict 行为一致）。

    1. item[asset_key] or item["physical_path"] or item["path"]
    2. 第一个 looks_like_path 的 str 值
    3. 第一个 str 值
    无命中返回 None。
    """
    asset_path = item.get(asset_key) or item.get("physical_path") or item.get("path")
    if not asset_path:
        for vv in item.values():
            if isinstance(vv, str) and vv and ("/" in vv or "." in vv or "\\" in vv):
                asset_path = vv
                break
    if not asset_path:
        for vv in item.values():
            if isinstance(vv, str):
                asset_path = vv
                break
    return asset_path if asset_path else None


def _build_entry_extra(item: dict, asset_path: str) -> dict:
    """构造 RegistryEntry.extra（过滤 None + asset_path + physical_path，与原行为一致）。"""
    return {
        k: v
        for k, v in item.items()
        if v is not None and k != asset_path and k != "physical_path"
    }


def _extract_dict_entry(item: dict, asset_key: str, registry_id: str) -> RegistryEntry | None:
    """从 dict 条目提取 asset_path 并构造 RegistryEntry（dict-value 和 list-item 共用）。"""
    asset_path = _extract_asset_path(item, asset_key)
    if not asset_path:
        return None
    return RegistryEntry(
        registry_id=registry_id,
        registry_path="",
        entry_path=str(asset_path),
        extra=_build_entry_extra(item, asset_path),
    )


def _resolve_list_asset_path(item: dict, effective_key: str, candidates: tuple[str, ...]) -> str:
    """从 list item 中三级 fallback 解析资产路径。"""
    asset_path = ""
    if effective_key:
        asset_path = item.get(effective_key, "")
    if not asset_path:
        for candidate in candidates:
            v = item.get(candidate)
            if v and isinstance(v, str) and ("/" in v or "." in v or "\\" in v):
                asset_path = v
                break
    if not asset_path:
        if effective_key:
            asset_path = str(item.get(effective_key, ""))
        else:
            for candidate in candidates:
                v = item.get(candidate)
                if v and isinstance(v, str):
                    asset_path = v
                    break
    return asset_path


class RegistryParseError(Exception):
    error_code = "ZA-IF-0006"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


class RegistryAdapter(ABC):
    @abstractmethod
    def parse(self, raw_content: str) -> list[RegistryEntry]: ...

    @abstractmethod
    def can_handle(self, file_path: str) -> bool: ...

    @property
    @abstractmethod
    def registry_id(self) -> str: ...


class YamlListAdapter(RegistryAdapter):
    def __init__(
        self, registry_id: str, path_pattern: str, asset_key: str = "relative_path", id_key: str = "registry_id"
    ) -> None:
        self._registry_id = registry_id
        self._path_pattern = path_pattern
        self._asset_key = asset_key
        self._id_key = id_key

    @property
    def registry_id(self) -> str:
        return self._registry_id

    def can_handle(self, file_path: str) -> bool:
        fp_lower = file_path.lower()
        return fp_lower.endswith(self._path_pattern)

    _ASSET_KEY_CANDIDATES = ("relative_path", "path", "physical_path", "file", "module_id", "gate_id", "script_path")

    def parse(self, raw_content: str) -> list[RegistryEntry]:
        import yaml

        try:
            data = yaml.safe_load(raw_content)
        except yaml.YAMLError as e:
            raise RegistryParseError(f"YAML parse error in {self._registry_id}: {e}") from e

        if data is None:
            return []

        if not isinstance(data, list):
            return self._parse_dict(data)

        entries: list[RegistryEntry] = []
        effective_key = self._asset_key if self._asset_key != "relative_path" else ""
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                continue
            asset_path = _resolve_list_asset_path(item, effective_key, self._ASSET_KEY_CANDIDATES)
            if not asset_path:
                continue
            entries.append(
                RegistryEntry(
                    registry_id=self._registry_id,
                    registry_path="",
                    entry_path=str(asset_path),
                    extra={k: v for k, v in item.items() if v is not None and k != asset_path},
                )
            )
        return entries

    def _parse_dict(self, data: dict) -> list[RegistryEntry]:
        # 裁定#217 Tier2 P3：提取为 _parse_tiers_registries + _extract_dict_entry 模块级 helper，
        # 本方法简化为 dispatcher（McCabe≈12）。行为等价契约见 helper docstring。
        if data is None:
            return []
        if "tiers" in data:
            return _parse_tiers_registries(data, self._registry_id)
        entries: list[RegistryEntry] = []
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and self._looks_like_path(value):
                    entries.append(
                        RegistryEntry(
                            registry_id=self._registry_id,
                            registry_path="",
                            entry_path=value,
                            extra={"key": key},
                        )
                    )
                elif isinstance(value, dict):
                    e = _extract_dict_entry(value, self._asset_key, self._registry_id)
                    if e is not None:
                        entries.append(e)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            e = _extract_dict_entry(item, self._asset_key, self._registry_id)
                            if e is not None:
                                entries.append(e)
        return entries

    @staticmethod
    def _looks_like_path(value: str) -> bool:
        return bool(value and ("/" in value or "." in value or "\\" in value))


class YamlDictAdapter(RegistryAdapter):
    def __init__(self, registry_id: str, path_pattern: str, asset_key: str = "physical_path") -> None:
        self._registry_id = registry_id
        self._path_pattern = path_pattern
        self._asset_key = asset_key

    @property
    def registry_id(self) -> str:
        return self._registry_id

    def can_handle(self, file_path: str) -> bool:
        fp_lower = file_path.lower()
        return fp_lower.endswith(self._path_pattern)

    def _parse_scripts_array(self, data: dict) -> list[RegistryEntry]:
        """解析 REG-SCRIPT-001 scripts 数组。"""
        if self._registry_id != "REG-SCRIPT-001":
            return []
        entries: list[RegistryEntry] = []
        for item in data.get("scripts", []):
            if isinstance(item, dict):
                path_val = item.get("path", "")
                entries.append(
                    RegistryEntry(
                        registry_id=self._registry_id,
                        registry_path="",
                        entry_path=str(path_val),
                        extra={
                            k: v
                            for k, v in item.items()
                            if v is not None and k not in (self._asset_key, "physical_path", "path", "id")
                        },
                    )
                )
        return entries

    def _parse_dict_entries(self, data: dict) -> list[RegistryEntry]:
        """解析通用 dict 条目（value 为 dict 的 key）。"""
        entries: list[RegistryEntry] = []
        for value in data.values():
            if not isinstance(value, dict):
                continue
            path_val = value.get(self._asset_key) or value.get("physical_path")
            if not path_val:
                continue
            entries.append(
                RegistryEntry(
                    registry_id=self._registry_id,
                    registry_path="",
                    entry_path=str(path_val),
                    extra={
                        k: v
                        for k, v in value.items()
                        if v is not None and k not in (self._asset_key, "physical_path")
                    },
                )
            )
        return entries

    def parse(self, raw_content: str) -> list[RegistryEntry]:
        import yaml

        try:
            data = yaml.safe_load(raw_content)
        except yaml.YAMLError as e:
            raise RegistryParseError(f"YAML parse error in {self._registry_id}: {e}") from e

        if data is None:
            return []

        entries: list[RegistryEntry] = []
        if isinstance(data, dict):
            entries.extend(self._parse_scripts_array(data))
            entries.extend(self._parse_dict_entries(data))
        return entries


class MarkdownTableAdapter(RegistryAdapter):
    TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")

    def __init__(self, registry_id: str, filename: str, path_column: int = 0) -> None:
        self._registry_id = registry_id
        self._filename = filename
        self._path_column = path_column

    @property
    def registry_id(self) -> str:
        return self._registry_id

    def can_handle(self, file_path: str) -> bool:
        return Path(file_path).name == self._filename

    def parse(self, raw_content: str) -> list[RegistryEntry]:
        entries: list[RegistryEntry] = []
        lines = raw_content.split("\n")
        header: list[str] = []
        line_num = 0

        for line in lines:
            line_num += 1
            m = self.TABLE_ROW_RE.match(line.strip())
            if not m:
                continue
            cells = [c.strip() for c in m.group(1).split("|")]
            if not header:
                header = cells
                continue
            if all(c.strip(" -") == "" for c in cells):
                continue
            if len(cells) < self._path_column + 1:
                continue

            asset_path = cells[self._path_column]
            if not asset_path or asset_path.startswith("---"):
                continue

            metadata: dict = {}
            for i, h in enumerate(header):
                if i < len(cells):
                    metadata[h.strip()] = cells[i]

            entries.append(
                RegistryEntry(
                    registry_id=self._registry_id,
                    registry_path="",
                    entry_path=asset_path,
                    extra=metadata,
                )
            )
        return entries


class FrontmatterAdapter(RegistryAdapter):
    YAML_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

    def __init__(self, registry_id: str, filename: str) -> None:
        self._registry_id = registry_id
        self._filename = filename

    @property
    def registry_id(self) -> str:
        return self._registry_id

    def can_handle(self, file_path: str) -> bool:
        return Path(file_path).name == self._filename

    def parse(self, raw_content: str) -> list[RegistryEntry]:
        import yaml

        m = self.YAML_FRONTMATTER_RE.match(raw_content)
        if not m:
            return []

        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            raise RegistryParseError(f"Frontmatter YAML parse error in {self._registry_id}: {e}") from e

        if fm is None:
            return []

        entries: list[RegistryEntry] = []
        if isinstance(fm, dict):
            for key, value in fm.items():
                if isinstance(value, str) and ("/" in value or "." in value):
                    entries.append(
                        RegistryEntry(
                            registry_id=self._registry_id,
                            registry_path="",
                            entry_path=value,
                            extra={"key": key},
                        )
                    )
        return entries


class CsvAdapter(RegistryAdapter):
    def __init__(self, registry_id: str, path_column: str = "path") -> None:
        self._registry_id = registry_id
        self._path_column = path_column

    @property
    def registry_id(self) -> str:
        return self._registry_id

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith(".csv")

    def parse(self, raw_content: str) -> list[RegistryEntry]:
        entries: list[RegistryEntry] = []
        reader = csv.DictReader(io.StringIO(raw_content))
        if reader.fieldnames is None:
            return entries

        for idx, row in enumerate(reader):
            asset_path = row.get(self._path_column, "")
            if not asset_path:
                continue
            entries.append(
                RegistryEntry(
                    registry_id=self._registry_id,
                    registry_path="",
                    entry_path=asset_path,
                    extra=dict(row),
                )
            )
        return entries


# === 裁定#217 Tier2 P3 Extract Method 重构（2026-07-15）===
# 原 TomlAdapter.parse 67 行 McCabe=34（list/dict 双分支 + 路径提取重复）。
# 治本：提取为 3 个模块级 helper（均 McCabe≤15），parse 简化为 import+loads+dispatch（McCabe≈9）。
# 行为等价：list/dict 分支顺序不变，asset_path fallback 链不变（relative_path→path→physical_path→look_like_path），
# extra 过滤规则不变（仅过滤 None + asset_path，不过滤 physical_path）。
# 注意：TomlAdapter 的 path 检查是 "/" or "." 不含 "\\"，与 YamlListAdapter 不同，故独立实现。


def _extract_toml_asset_path(item: dict) -> str | None:
    """从 TOML dict 条目提取 asset_path（relative_path→path→physical_path→look_like_path fallback）。"""
    asset_path = item.get("relative_path") or item.get("path") or item.get("physical_path")
    if not asset_path:
        for v in item.values():
            if isinstance(v, str) and ("/" in v or "." in v):
                asset_path = v
                break
    return asset_path or None


def _parse_toml_list(target: list, registry_id: str) -> list[RegistryEntry]:
    """解析 TOML list target（每个 item 为 dict，提取 asset_path 构造 RegistryEntry）。"""
    entries: list[RegistryEntry] = []
    for item in target:
        if not isinstance(item, dict):
            continue
        asset_path = _extract_toml_asset_path(item)
        if asset_path:
            entries.append(
                RegistryEntry(
                    registry_id=registry_id,
                    registry_path="",
                    entry_path=str(asset_path),
                    extra={k: v for k, v in item.items() if v is not None and k != asset_path},
                )
            )
    return entries


def _parse_toml_dict(target: dict, registry_id: str) -> list[RegistryEntry]:
    """解析 TOML dict target（str value→path entry，dict value→extract asset_path）。"""
    entries: list[RegistryEntry] = []
    for key, value in target.items():
        if isinstance(value, str) and ("/" in value or "." in value):
            entries.append(
                RegistryEntry(
                    registry_id=registry_id,
                    registry_path="",
                    entry_path=value,
                    extra={"key": key},
                )
            )
        elif isinstance(value, dict):
            asset_path = _extract_toml_asset_path(value)
            if asset_path:
                entries.append(
                    RegistryEntry(
                        registry_id=registry_id,
                        registry_path="",
                        entry_path=str(asset_path),
                        extra={k: v for k, v in value.items() if v is not None and k != asset_path},
                    )
                )
    return entries


class TomlAdapter(RegistryAdapter):
    def __init__(self, registry_id: str, key: str = "assets") -> None:
        self._registry_id = registry_id
        self._key = key

    @property
    def registry_id(self) -> str:
        return self._registry_id

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith(".toml")

    def parse(self, raw_content: str) -> list[RegistryEntry]:
        # 裁定#217 Tier2 P3：提取为 _extract_toml_asset_path/_parse_toml_list/_parse_toml_dict
        # 模块级 helper，本方法简化为 import+loads+dispatch（McCabe≈9）。行为等价。
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                return []
        try:
            data = tomllib.loads(raw_content)
        except Exception:
            return []
        if not isinstance(data, dict):
            return []
        target = data.get(self._key, data)
        if isinstance(target, list):
            return _parse_toml_list(target, self._registry_id)
        if isinstance(target, dict):
            return _parse_toml_dict(target, self._registry_id)
        return []


class SqliteAdapter(RegistryAdapter):
    # 5.176 修复：标识符白名单正则（表名/列名仅允许字母/数字/下划线）
    _IDENT_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    def __init__(self, registry_id: str, db_path: str, table: str, path_column: str = "relative_path") -> None:
        # 5.176 修复：表名/列名白名单校验，防 f-string SQL 注入
        if not isinstance(table, str) or not self._IDENT_RE.match(table):
            raise ValueError(f"非法表名: {table!r}（仅允许字母/数字/下划线）")
        if not isinstance(path_column, str) or not self._IDENT_RE.match(path_column):
            raise ValueError(f"非法列名: {path_column!r}（仅允许字母/数字/下划线）")
        # 5.66.3 修复：白名单校验表名，仅允许已知表名用于 SQL 拼接
        _validate_table_name(table)
        self._registry_id = registry_id
        self._db_path = db_path
        self._table = table
        self._path_column = path_column

    @property
    def registry_id(self) -> str:
        return self._registry_id

    def can_handle(self, file_path: str) -> bool:
        return file_path.lower().endswith(".db")

    def parse(self, raw_content: str) -> list[RegistryEntry]:
        import sqlite3

        entries: list[RegistryEntry] = []
        try:
            conn = get_db_connection(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(f"SELECT * FROM {self._table}")
            for idx, row in enumerate(cursor.fetchall()):
                d = dict(row)
                asset_path = d.get(self._path_column, "")
                entries.append(
                    RegistryEntry(
                        registry_id=self._registry_id,
                        registry_path=self._db_path,
                        entry_path=str(asset_path),
                        extra=d,
                    )
                )
            conn.close()
        except Exception as e:
            raise RegistryParseError(f"SQLite parse error in {self._registry_id}: {e}") from e
        return entries


class RegistryManager:
    """管理所有注册表的解析——从 registry_of_registries.yaml 自动发现 + 损坏隔离"""

    def __init__(self, project_root: Path) -> None:
        self._root = project_root
        self._init_defaults()

    def _init_defaults(self) -> None:
        self._known: dict[str, RegistryAdapter] = {}

        self._known["docs/registry_of_registries.yaml"] = YamlListAdapter(
            "REG-TIER-000", "registry_of_registries.yaml", asset_key="physical_path"
        )

        self._known["docs/03_modules/module-registry.yaml"] = YamlListAdapter(
            # 历史遗留 ID：名字含 ALPHA_SIGNAL_DOMAIN 但实际管辖整个 module-registry.yaml
            # 改名涉及 6 文件+depgraph 节点迁移，待后续重构统一为 REG-MOD-001
            "REG-MOD-ALPHA_SIGNAL_DOMAIN", "module-registry.yaml", asset_key="module_id"
        )
        self._known["docs/03_modules/blueprint_registry.yaml"] = YamlListAdapter(
            "REG-BP-001", "blueprint_registry.yaml", asset_key="blueprint_id"
        )
        self._known["src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml"] = YamlListAdapter(
            "REG-GATE-001", "_registry.yaml", asset_key="gate_id"
        )
        self._known["scripts/script-manifest.yaml"] = YamlDictAdapter("REG-SCRIPT-001", "script-manifest.yaml")
        self._known["config/risk_register.yaml"] = YamlListAdapter(
            "REG-RISK-001", "risk_register.yaml", asset_key="risk_id"
        )
        self._known["config/asset_inventory.yaml"] = YamlListAdapter(
            "REG-ASSET-001", "asset_inventory.yaml", asset_key="relative_path"
        )
        self._known["config/embedding_model_registry.yaml"] = YamlListAdapter(
            "REG-EMBED-001", "embedding_model_registry.yaml", asset_key="model_id"
        )
        self._known["src/zephyr/pipeline/routemanifest.yaml"] = YamlListAdapter(
            "REG-PIPE-001", "routemanifest.yaml", asset_key="route_id"
        )
        self._known["config/tech_stack_manifest.yaml"] = YamlListAdapter(
            "REG-CAP-001", "tech_stack_manifest.yaml", asset_key="tech_id"
        )

        self._known["docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml"] = YamlListAdapter(
            "REG-DIR-001", "directory_registry.yaml", asset_key="path"
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/document-metadata-index-registry.yaml"] = (
            YamlListAdapter("REG-DOC-001", "document-metadata-index-registry.yaml", asset_key="path")
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml"] = (
            YamlListAdapter("REG-CROSS-002", "cross_module_dependency_registry.yaml", asset_key="from_module")
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml"] = YamlListAdapter(
            "REG-GATE-CAT-001", "gate_registry.yaml", asset_key="gate_id"
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml"] = YamlListAdapter(
            "REG-INFRA-001", "infrastructure_registry.yaml", asset_key="component_id"
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/task_card_meta_registry.yaml"] = YamlListAdapter(
            "REG-TASK-META-001", "task_card_meta_registry.yaml", asset_key="subsystem_id"
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml"] = (
            YamlListAdapter("REG-FRONTMATTER-001", "frontmatter_field_registry.yaml", asset_key="field_name")
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/registry_consistency_contract.yaml"] = YamlListAdapter(
            "REG-CROSS-001", "registry_consistency_contract.yaml", asset_key="field_name"
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/knowledge_article_registry.yaml"] = (
            YamlListAdapter("REG-KB-001", "knowledge_article_registry.yaml", asset_key="article_id")
        )

        self._known["src/zephyr/drift-detector/_detector-registry.yaml"] = YamlListAdapter(
            "REG-DRIFT-001", "_detector-registry.yaml", asset_key="detector_id"
        )
        self._known["src/zephyr/agent-spec/skill-registry.yaml"] = YamlListAdapter(
            "REG-SKILL-001", "skill-registry.yaml", asset_key="skill_id"
        )

    def _find_adapter(self, file_path: str) -> RegistryAdapter | None:
        normalized = file_path.replace("\\", "/")
        for known_path, adapter in self._known.items():
            if normalized.endswith(known_path) or normalized == known_path:
                return adapter

        ext = Path(file_path).suffix.lower()
        name = Path(file_path).name.lower()
        fp_lower = file_path.lower()

        if name == "_index.yaml":
            return MarkdownTableAdapter("REG-RULE-001", "_index.yaml", path_column=0)
        if ext == ".csv":
            return CsvAdapter("REG-AUTO-CSV")

        if ext in (".yaml", ".yml"):
            if "_registry" in fp_lower or "registry" in name or "manifest" in name:
                return YamlListAdapter("REG-AUTO", name, asset_key="relative_path")
            return YamlListAdapter("REG-AUTO", name)

        return None

    def discover_registry_files(self) -> list[Path]:
        paths: list[Path] = []
        main_reg = self._root / "docs" / "registry_of_registries.yaml"
        if main_reg.exists():
            paths.append(main_reg)

        import yaml

        try:
            data = yaml.safe_load(main_reg.read_text(encoding="utf-8"))
            if data and "tiers" in data:
                for tier in data["tiers"]:
                    for reg in tier.get("registries", []):
                        phys = reg.get("physical_path", "")
                        if phys:
                            full = self._root / phys
                            if full.exists():
                                paths.append(full)
        except Exception:
            pass

        candidates = [
            self._root / "src" / "zephyr" / "gates" / "_registry.yaml",
            self._root / "scripts" / "script-manifest.yaml",
            self._root / "docs" / "03_modules" / "module-registry.yaml",
            self._root / "docs" / "03_modules" / "blueprint_registry.yaml",
            self._root / "config" / "capacity" / "risk-register.yaml",
            self._root / "config" / "capacity" / "asset-inventory.yaml",
        ]
        for c in candidates:
            if c.exists() and c not in paths:
                paths.append(c)

        return paths

    def load_all(self) -> tuple[list[RegistryEntry], list[str]]:
        entries: list[RegistryEntry] = []
        skipped: list[str] = []

        for file_path in self.discover_registry_files():
            adapter = self._find_adapter(str(file_path))
            if adapter is None:
                skipped.append(str(file_path))
                continue

            try:
                # 5.59.1 修复：原 encoding="utf-8" 不剥离 BOM；若 CSV 由 Excel 生成带 BOM，
                # csv.DictReader 把首列名读成 \ufeffpath 而非 path，row.get("path", "") 对所有行返回空字符串，
                # 所有资产条目被静默丢弃。改为 utf-8-sig 自动剥离 BOM。
                raw = file_path.read_text(encoding="utf-8-sig")
                file_entries = adapter.parse(raw)
                for e in file_entries:
                    e.registry_path = str(file_path.relative_to(self._root))
                entries.extend(file_entries)
            except RegistryParseError:
                skipped.append(adapter.registry_id)
                continue
            except Exception:
                continue

        return entries, skipped

    def cross_match_asset(self, asset: ClassifiedAsset, registry_entries: list[RegistryEntry]) -> bool:
        asset_path = asset.relative_path
        for entry in registry_entries:
            if entry.entry_path == asset_path:
                return True
        return False


# ============================================================================
# ARCH-053: discover_all_registries() — AI 发现全部 registry 的统一入口
# ============================================================================

def discover_all_registries() -> list[dict]:
    """读取 registry_master_index.yaml，返回全部 registry 的元数据列表。

    ARCH-053 裁定：AI 代码启动时调用此函数即可发现项目全部 25+ 个 registry，
    不再依赖硬编码路径或 AGENTS.md 提示。

    Returns:
        list[dict]: 每个元素含 registry_id/name/category/physical_path/format/
                    maintenance/entry_count/status

    Example:
        >>> regs = discover_all_registries()
        >>> print(f"项目共 {len(regs)} 个 registry")
        >>> infra = [r for r in regs if 'infrastructure' in r['name']]
        >>> print(f"基础设施相关: {infra}")
    """
    import yaml
    from zephyr.shared.io.paths import REPO_ROOT

    # registry_master_index.yaml 是自动生成的总索引（reconciler 维护）
    # P1 修复：使用 REPO_ROOT 绝对路径，禁止相对路径（硬约束）
    master_path = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry_master_index.yaml"
    if not master_path.exists():
        return []

    data = yaml.safe_load(master_path.read_text(encoding="utf-8"))
    if not data or "registries" not in data:
        return []

    return data["registries"]
