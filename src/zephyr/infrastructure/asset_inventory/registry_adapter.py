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


class RegistryParseError(Exception):
    pass


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

            asset_path = ""
            if effective_key:
                asset_path = item.get(effective_key, "")
            if not asset_path:
                for candidate in self._ASSET_KEY_CANDIDATES:
                    v = item.get(candidate)
                    if v and isinstance(v, str) and ("/" in v or "." in v or "\\" in v):
                        asset_path = v
                        break
            if not asset_path:
                if effective_key:
                    asset_path = str(item.get(effective_key, ""))
                else:
                    for candidate in self._ASSET_KEY_CANDIDATES:
                        v = item.get(candidate)
                        if v and isinstance(v, str):
                            asset_path = v
                            break
            if not asset_path:
                continue

            entry_id = item.get(self._id_key) or f"{self._registry_id}-{idx}"
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
        entries: list[RegistryEntry] = []
        if data is None:
            return entries

        if "tiers" in data:
            for tier in data["tiers"]:
                for reg in tier.get("registries", []):
                    phys = reg.get("physical_path", "")
                    if phys:
                        entries.append(
                            RegistryEntry(
                                registry_id=reg.get("registry_id", self._registry_id),
                                registry_path="",
                                entry_path=phys,
                                extra={k: v for k, v in reg.items() if v is not None and k != "physical_path"},
                            )
                        )
            return entries

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
                    asset_path = value.get(self._asset_key) or value.get("physical_path") or value.get("path")
                    if not asset_path:
                        for vk, vv in value.items():
                            if isinstance(vv, str) and self._looks_like_path(vv):
                                asset_path = vv
                                break
                    if not asset_path:
                        for vk, vv in value.items():
                            if isinstance(vv, str):
                                asset_path = vv
                                break
                    if asset_path:
                        entries.append(
                            RegistryEntry(
                                registry_id=self._registry_id,
                                registry_path="",
                                entry_path=str(asset_path),
                                extra={
                                    k: v
                                    for k, v in value.items()
                                    if v is not None and k != asset_path and k != "physical_path"
                                },
                            )
                        )
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            asset_path = item.get(self._asset_key) or item.get("physical_path") or item.get("path")
                            if not asset_path:
                                for vk, vv in item.items():
                                    if isinstance(vv, str) and self._looks_like_path(vv):
                                        asset_path = vv
                                        break
                            if not asset_path:
                                for vk, vv in item.items():
                                    if isinstance(vv, str):
                                        asset_path = vv
                                        break
                            if asset_path:
                                entries.append(
                                    RegistryEntry(
                                        registry_id=self._registry_id,
                                        registry_path="",
                                        entry_path=str(asset_path),
                                        extra={
                                            k: v
                                            for k, v in item.items()
                                            if v is not None and k != asset_path and k != "physical_path"
                                        },
                                    )
                                )
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

    def parse(self, raw_content: str) -> list[RegistryEntry]:
        import yaml

        try:
            data = yaml.safe_load(raw_content)
        except yaml.YAMLError as e:
            raise RegistryParseError(f"YAML parse error in {self._registry_id}: {e}") from e

        if data is None:
            return []

        entries: list[RegistryEntry] = []
        if self._registry_id == "REG-SCRIPT-001" and isinstance(data, dict):
            scripts = data.get("scripts", [])
            for idx, item in enumerate(scripts):
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

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    path_val = value.get(self._asset_key) or value.get("physical_path")
                    if path_val:
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

        entries: list[RegistryEntry] = []
        target = data.get(self._key, data)

        if isinstance(target, list):
            for idx, item in enumerate(target):
                if not isinstance(item, dict):
                    continue
                asset_path = item.get("relative_path") or item.get("path") or item.get("physical_path")
                if not asset_path:
                    for v in item.values():
                        if isinstance(v, str) and ("/" in v or "." in v):
                            asset_path = v
                            break
                if asset_path:
                    entries.append(
                        RegistryEntry(
                            registry_id=self._registry_id,
                            registry_path="",
                            entry_path=str(asset_path),
                            extra={k: v for k, v in item.items() if v is not None and k != asset_path},
                        )
                    )
        elif isinstance(target, dict):
            for key, value in target.items():
                if isinstance(value, str) and ("/" in value or "." in value):
                    entries.append(
                        RegistryEntry(
                            registry_id=self._registry_id,
                            registry_path="",
                            entry_path=value,
                            extra={"key": key},
                        )
                    )
                elif isinstance(value, dict):
                    asset_path = value.get("relative_path") or value.get("path") or value.get("physical_path")
                    if not asset_path:
                        for v in value.values():
                            if isinstance(v, str) and ("/" in v or "." in v):
                                asset_path = v
                                break
                    if asset_path:
                        entries.append(
                            RegistryEntry(
                                registry_id=self._registry_id,
                                registry_path="",
                                entry_path=str(asset_path),
                                extra={k: v for k, v in value.items() if v is not None and k != asset_path},
                            )
                        )
        return entries


class SqliteAdapter(RegistryAdapter):
    # 5.176 修复：标识符白名单正则（表名/列名仅允许字母/数字/下划线）
    _IDENT_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    def __init__(self, registry_id: str, db_path: str, table: str, path_column: str = "relative_path") -> None:
        # 5.176 修复：表名/列名白名单校验，防 f-string SQL 注入
        if not isinstance(table, str) or not self._IDENT_RE.match(table):
            raise ValueError(f"非法表名: {table!r}（仅允许字母/数字/下划线）")
        if not isinstance(path_column, str) or not self._IDENT_RE.match(path_column):
            raise ValueError(f"非法列名: {path_column!r}（仅允许字母/数字/下划线）")
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
        self._known["src/zephyr/gates/_registry.yaml"] = YamlListAdapter(
            "REG-GATE-001", "_registry.yaml", asset_key="gate_id"
        )
        self._known["scripts/script-manifest.yaml"] = YamlDictAdapter("REG-SCRIPT-001", "script-manifest.yaml")
        self._known["config/risk-register.yaml"] = YamlListAdapter(
            "REG-RISK-001", "risk-register.yaml", asset_key="risk_id"
        )
        self._known["config/asset-inventory.yaml"] = YamlListAdapter(
            "REG-ASSET-001", "asset-inventory.yaml", asset_key="relative_path"
        )
        self._known["config/embedding_model_registry.yaml"] = YamlListAdapter(
            "REG-EMBED-001", "embedding_model_registry.yaml", asset_key="model_id"
        )
        self._known["src/zephyr/pipeline/routemanifest.yaml"] = YamlListAdapter(
            "REG-PIPE-001", "routemanifest.yaml", asset_key="route_id"
        )
        self._known["config/tech_stackmanifest.yaml"] = YamlListAdapter(
            "REG-CAP-001", "tech_stackmanifest.yaml", asset_key="tech_id"
        )

        self._known["docs/01_policies_and_standards/_registry/catalogs/directory-registry.md"] = YamlListAdapter(
            "REG-DIR-001", "directory-registry.md", asset_key="path"
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/document-metadata-index-registry.yaml"] = (
            YamlListAdapter("REG-DOC-001", "document-metadata-index-registry.yaml", asset_key="path")
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/cross-module-dependency-registry.yaml"] = (
            YamlListAdapter("REG-CROSS-002", "cross-module-dependency-registry.yaml", asset_key="from_module")
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml"] = YamlListAdapter(
            "REG-GATE-CAT-001", "gate_registry.yaml", asset_key="gate_id"
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/infrastructure-registry.md"] = YamlListAdapter(
            "REG-INFRA-001", "infrastructure-registry.md", asset_key="component_id"
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.md"] = YamlListAdapter(
            "REG-TASK-META-001", "task-card-meta-registry.md", asset_key="subsystem_id"
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml"] = (
            YamlListAdapter("REG-FRONTMATTER-001", "frontmatter_field_registry.yaml", asset_key="field_name")
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/registry_consistency_contract.yaml"] = YamlListAdapter(
            "REG-CROSS-001", "registry_consistency_contract.yaml", asset_key="field_name"
        )
        self._known["docs/01_policies_and_standards/_registry/catalogs/knowledge-article-registry.md"] = (
            YamlListAdapter("REG-KB-001", "knowledge-article-registry.md", asset_key="article_id")
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
