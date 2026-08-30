# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.model_discovery
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.provider_data
# [CONSUMERS] MOD-INF-034;MOD-INF-009
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 模型发现;Ollama本地模型;远程API模型
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md;src/zephyr/intelligence/model_profiling/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DiscoveryError;ConnectionError
# [TESTS] tests/test_model_profiler/
# [A_module] module_id=MOD-INF-034 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ollama_url 参数
#   fields: 参数 ollama_url（无注解）
#   code: model_discovery.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: timeout_s 参数
#   fields: 参数 timeout_s（无注解）
#   code: model_discovery.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DiscoveredModel
#   name_en: DiscoveredModel
#   intro: class DiscoveredModel 源码 L85-L98
#   desc: 公共方法（定义序）: size_gb；源码 L85-L98
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② ModelDiscovery
#   name_en: ModelDiscovery
#   intro: 模型发现器——枚举所有可用模型（本地 Ollama + 远程 API）。
#   desc: 模型发现器——枚举所有可用模型（本地 Ollama + 远程 API）。；公共方法（定义序）: timeout, url, discover_ollama, discover_remote, discover_all,…
#   inputs: ollama_url timeout_s
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DiscoveredModel, ModelDiscovery
#   downstream: MOD-INF-034;MOD-INF-009
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Final

_log = logging.getLogger(__name__)

# DEFAULT_OLLAMA_URL 已下沉到 zephyr.shared.foundation.constants（§5.160 SSoT）
# 延迟导入：模块级导入会触发 constants→schemas→task_types 循环死锁


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
        ollama_url: str | None = None,
        timeout_s: float = 15.0,
    ) -> None:
        if ollama_url is None:
            from zephyr.shared.foundation.constants import DEFAULT_OLLAMA_URL

            ollama_url = DEFAULT_OLLAMA_URL
        self._url = ollama_url.rstrip("/")
        self._timeout = timeout_s

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def timeout(self):
        """只读：timeout（Stage 4 公共化）。"""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """写入：timeout（Stage 4 公共化）。"""
        self._timeout = value

    @property
    def url(self):
        """只读：url（Stage 4 公共化）。"""
        return self._url

    @url.setter
    def url(self, value):
        """写入：url（Stage 4 公共化）。"""
        self._url = value

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
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return False
