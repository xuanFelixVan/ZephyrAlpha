# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.model_discovery
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.provider_data
# [CONSUMERS] MOD-INF-034;MOD-INF-009
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 模型发现;Ollama本地模型;远程API模型
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md;src/zephyr/intelligence/model_profiling/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DiscoveryError;ConnectionError
# [TESTS] tests/test_model_profiler/
# [A_module] module_id=MOD-RSC_model_discovery | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ModelDiscovery — 枚举所有本地 Ollama 模型 + 远程 API 模型
=========================================================
通过 Ollama HTTP API /api/tags 列出所有已拉取的本地模型，
同时合并 Budget Enforcer 中注册的外部 API 模型。

用法
----
    discovery = ModelDiscovery()
    models = discovery.discover_all()
    for m in models:
        print(f"{m.name} | {m.source} | {m.size_gb:.1f}GB")
"""

from __future__ import annotations

from typing import Final
import logging
import os
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL: Final[str] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


@dataclass
class DiscoveredModel:
    name: str
    source: str
    provider: str = ""
    size_bytes: int = 0
    parameter_size: str = ""
    quantization_level: str = ""
    family: str = ""
    available: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def size_gb(self) -> float:
        return self.size_bytes / (1024**3) if self.size_bytes else 0.0


class ModelDiscovery:
    """模型发现器——枚举所有可用模型（本地 Ollama + 远程 API）。"""

    def __init__(
        self,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        timeout_s: float = 15.0,
    ) -> None:
        self._url = ollama_url.rstrip("/")
        self._timeout = timeout_s

    def discover_ollama(self) -> list[DiscoveredModel]:
        """通过 Ollama API 列出所有本地模型。"""
        import requests

        try:
            resp = requests.get(
                f"{self._url}/api/tags",
                timeout=self._timeout,
            )
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:
            _log.warning("ModelDiscovery: Ollama /api/tags failed: %s", exc, exc_info=True)
            return []

        models: list[DiscoveredModel] = []
        for item in payload.get("models", []):
            raw = item if isinstance(item, dict) else {}
            name = raw.get("name", raw.get("model", ""))
            if not name:
                continue

            details = raw.get("details", {}) if isinstance(raw.get("details"), dict) else {}
            models.append(
                DiscoveredModel(
                    name=name,
                    source="ollama",
                    provider=name.split(":")[0] if ":" in name else name,
                    size_bytes=int(raw.get("size", 0)),
                    parameter_size=details.get("parameter_size", ""),
                    quantization_level=details.get("quantization_level", ""),
                    family=details.get("family", ""),
                    available=True,
                    metadata={
                        "modified_at": raw.get("modified_at", ""),
                        "digest": raw.get("digest", ""),
                    },
                )
            )

        _log.info("ModelDiscovery: found %d Ollama models", len(models))
        return models

    def discover_remote(self) -> list[DiscoveredModel]:
        """列出 Budget Enforcer 中注册的远程 API 模型。"""
        from zephyr.intelligence.model_profiling.provider_data import (
            DEFAULT_PROVIDERS,
            TIER_MODEL_MAP,
        )

        models: list[DiscoveredModel] = []
        seen: set[str] = set()

        for tier_models in TIER_MODEL_MAP.values():
            for full_key in tier_models:
                if full_key in seen or ":" not in full_key:
                    continue
                seen.add(full_key)
                prov, model_name = full_key.split(":", 1)
                cfg = DEFAULT_PROVIDERS.get(prov, {})

                models.append(
                    DiscoveredModel(
                        name=full_key,
                        source="remote_api",
                        provider=prov,
                        size_bytes=0,
                        parameter_size="",
                        family=prov,
                        available=True,
                        metadata={
                            "api_model": str(
                                cfg.get(
                                    model_name.split(":")[0]
                                    if ":" in model_name
                                    else list(cfg.keys())[0]
                                    if cfg
                                    else "",
                                    "",
                                )
                            ),
                            "price_per_1k_input": float(cfg.get("price_per_1k_input", 0.0)),
                            "price_per_1k_output": float(cfg.get("price_per_1k_output", 0.0)),
                            "region": str(cfg.get("cc", "")),
                        },
                    )
                )

        _log.info("ModelDiscovery: found %d remote API models", len(models))
        return models

    def discover_all(self) -> list[DiscoveredModel]:
        """发现所有可用模型（本地 + 远程）。"""
        local = self.discover_ollama()
        remote = self.discover_remote()
        return local + remote

    def ollama_available(self) -> bool:
        """检查 Ollama 服务是否运行中。"""
        import requests

        try:
            resp = requests.get(
                f"{self._url}/api/tags",
                timeout=5.0,
            )
            resp.raise_for_status()
            return True
        except Exception:
            return False
