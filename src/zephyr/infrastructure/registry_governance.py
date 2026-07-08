# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §3
# [MODULE] zephyr.infrastructure.registry_governance
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] scripts/scaffold.py;scripts/governance/d5_architecture/checkers/check_ssot_uniqueness.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 功能域注册表是功能域声明的唯一真源;SSoT门禁检查不可跳过;注册表不可被AI直接修改
# [MODIFY-GUARD] docs/03_modules/_domain-governance/registry-governance/blueprint.md;docs/01_policies_and_standards/_registry/catalogs/functional-domain-registry.yaml
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FunctionalDomainOverlap->阻断创建;RegistryLoadError->降级为WARNING
# [TESTS] tests/infrastructure/test_registry_governance.py
# [A_module] module_id=MOD-INF_registry_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Registry Governance — MOD-INF-037

Functional domain registry management + SSoT gate + consistency checks.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

import yaml

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("docs/01_policies_and_standards/_registry/catalogs/functional-domain-registry.yaml")



@dataclass
class DomainEntry:
    domain: str
    subdomain: str
    ssot_module: str
    ssot_path: str
    covers: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    change_policy: str = "evolving"
    modification_permission: str = "human_gated"


@dataclass
class OverlapResult:
    has_overlap: bool = False
    overlapping_entries: list[DomainEntry] = field(default_factory=list)
    overlap_details: list[str] = field(default_factory=list)


class FunctionalDomainRegistry:
    def __init__(self, registry_path: Path | str | None = None):
        if registry_path is None:
            self._path = REPO_ROOT / REGISTRY_PATH
        else:
            self._path = Path(registry_path)
        self._entries: list[DomainEntry] = []
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        if not self._path.exists():
            logger.warning("Functional domain registry not found: %s", self._path)
            self._loaded = True
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            entries_raw = data.get("entries", [])
            self._entries = []
            for e in entries_raw:
                self._entries.append(
                    DomainEntry(
                        domain=e.get("domain", ""),
                        subdomain=e.get("subdomain", ""),
                        ssot_module=e.get("ssot_module", ""),
                        ssot_path=e.get("ssot_path", ""),
                        covers=e.get("covers", []),
                        aliases=e.get("aliases", []),
                        change_policy=e.get("change_policy", e.get("stability", "evolving")),
                        modification_permission=e.get("modification_permission", e.get("ai_autonomy", "human_gated")),
                    )
                )
            self._loaded = True
            logger.info("Loaded %d functional domain entries", len(self._entries))
        except Exception as exc:
            logger.error("Failed to load functional domain registry: %s", exc, exc_info=True)
            self._loaded = True

    def query_domain(self, domain: str, subdomain: str | None = None) -> list[DomainEntry]:
        self.load()
        results = []
        for e in self._entries:
            if e.domain == domain:
                if subdomain is None or e.subdomain == subdomain:
                    results.append(e)
        return results

    def check_overlap(
        self,
        domain: str,
        subdomain: str,
        covers: list[str] | None = None,
        name: str = "",
        description: str = "",
    ) -> OverlapResult:
        self.load()
        result = OverlapResult()

        for e in self._entries:
            exact_match = e.domain == domain and e.subdomain == subdomain
            if exact_match:
                result.has_overlap = True
                result.overlapping_entries.append(e)
                result.overlap_details.append(
                    f"Exact domain/subdomain overlap: {e.domain}/{e.subdomain} -> {e.ssot_module}"
                )
                continue

            if covers and e.covers:
                overlap_covers = set(covers) & set(e.covers)
                if overlap_covers:
                    result.has_overlap = True
                    result.overlapping_entries.append(e)
                    result.overlap_details.append(f"Cover overlap with {e.ssot_module}: {overlap_covers}")

        if not result.has_overlap and (name or description):
            query_text = f"{name} {description}".lower()
            for e in self._entries:
                for alias in e.aliases:
                    if alias.lower() in query_text:
                        result.has_overlap = True
                        result.overlapping_entries.append(e)
                        result.overlap_details.append(
                            f"Alias match '{alias}' -> {e.domain}/{e.subdomain} ({e.ssot_module})"
                        )
                        break
                if result.has_overlap:
                    break

        return result

    def register(
        self,
        domain: str,
        subdomain: str,
        ssot_module: str,
        ssot_path: str,
        covers: list[str] | None = None,
        aliases: list[str] | None = None,
        change_policy: str = "evolving",
        modification_permission: str = "human_gated",
    ) -> None:
        self.load()
        overlap = self.check_overlap(domain, subdomain, covers)
        if overlap.has_overlap:
            detail = "; ".join(overlap.overlap_details)
            raise ValueError(f"Functional domain overlap detected: {detail}. Resolve overlap before registering.")

        new_entry = DomainEntry(
            domain=domain,
            subdomain=subdomain,
            ssot_module=ssot_module,
            ssot_path=ssot_path,
            covers=covers or [],
            aliases=aliases or [],
            change_policy=change_policy,
            modification_permission=modification_permission,
        )
        self._entries.append(new_entry)
        self._write_registry()

    def _write_registry(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {
            "registry_id": "REG-FUNC-DOMAIN-001",
            "name": "功能域注册表",
            "description": "模块/脚本功能域声明的唯一真源。创建新模块/脚本时SSoT门禁检查功能域重叠。",
            "owner": "MOD-INF-037",
            "tier": "tier_1_governance",
            "status": "Active",
            "version": "0.1.0",
            "unique_key": ["domain", "subdomain"],
            "entries": [],
        }
        for e in self._entries:
            data["entries"].append(
                {
                    "domain": e.domain,
                    "subdomain": e.subdomain,
                    "ssot_module": e.ssot_module,
                    "ssot_path": e.ssot_path,
                    "covers": e.covers,
                    "aliases": e.aliases,
                    "change_policy": e.change_policy,
                    "modification_permission": e.modification_permission,
                }
            )

        tmp_path = f"{self._path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            os.replace(tmp_path, str(self._path))
            logger.info("Wrote functional domain registry: %d entries", len(self._entries))
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise

    def list_domains(self) -> list[str]:
        self.load()
        return sorted(set(e.domain for e in self._entries))

    def list_subdomains(self, domain: str) -> list[str]:
        self.load()
        return sorted(e.subdomain for e in self._entries if e.domain == domain)

    @property
    def entry_count(self) -> int:
        self.load()
        return len(self._entries)


__all__ = ["REGISTRY_PATH", "DomainEntry", "FunctionalDomainRegistry", "OverlapResult"]