# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §3.1
# [MODULE] zephyr.integration.local_model.ollama_embedding
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_ollama_embedding | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
OllamaEmbedder — 通过 Ollama HTTP API 生成文本嵌入
=====================================================
替代 SentenceTransformer 本地加载，使用 Ollama 已有的 BGE-M3 等模型。
零额外下载，复用 Ollama 基础设施。

用法
----
    embedder = OllamaEmbedder(model="BGE-M3:latest")
    vec = embedder.encode("hello world")           # → np.ndarray (1024,)
    vecs = embedder.encode(["a", "b", "c"])         # → np.ndarray (3, 1024)
    dim = embedder.dim                              # → 1024
"""

from __future__ import annotations

from http import HTTPStatus

import logging
import os
from typing import Any

import numpy as np

_log = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


class OllamaEmbedder:
    """Ollama 嵌入客户端——封装 /api/embed，兼容 SentenceTransformer.encode() 接口。"""

    def __init__(
        self,
        model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "BGE-M3:latest"),
        ollama_url: str = DEFAULT_OLLAMA_URL,
        normalize: bool = True,
        timeout_s: float = 60.0,
    ) -> None:
        self._model = model
        self._url = ollama_url.rstrip("/")
        self._normalize = normalize
        self._timeout = timeout_s
        self._dim: int | None = None
        self._verified = False

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._verify()
        return self._dim or 0

    @property
    def available(self) -> bool:
        try:
            self._verify()
            return self._dim is not None and self._dim > 0
        except Exception:
            return False

    def encode(
        self,
        texts: str | list[str],
        *,
        normalize_embeddings: bool | None = None,
        batch_size: int | None = None,
        **_: Any,
    ) -> np.ndarray:
        single_input = isinstance(texts, str)
        inputs = [texts] if single_input else list(texts)
        if not inputs:
            return np.empty((0, 0), dtype=np.float32)

        import requests

        try:
            resp = requests.post(
                f"{self._url}/api/embed",
                json={"model": self._model, "input": inputs},
                timeout=self._timeout,
            )
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:
            _log.error("OllamaEmbedder.encode failed for model=%s: %s", self._model, exc)
            raise

        embeddings_list = payload.get("embeddings", [])
        if not embeddings_list:
            raise RuntimeError(f"Ollama returned empty embeddings for model={self._model}")

        result = np.asarray(embeddings_list, dtype=np.float32)
        if self._dim is None and result.ndim == 2 and result.shape[1] > 0:
            self._dim = result.shape[1]
            self._verified = True

        do_normalize = normalize_embeddings if normalize_embeddings is not None else self._normalize
        if do_normalize:
            norms = np.linalg.norm(result, axis=1, keepdims=True)
            norms = np.where(norms < 1e-12, 1.0, norms)
            result = result / norms

        return result[0] if single_input else result

    @staticmethod
    def quick_alive(url: str = DEFAULT_OLLAMA_URL, timeout_s: float = 2.0) -> bool:
        try:
            import requests

            resp = requests.get(f"{url.rstrip('/')}/api/tags", timeout=timeout_s)
            return resp.status_code == HTTPStatus.OK
        except Exception:
            return False

    def _verify(self) -> None:
        if self._verified:
            return
        if not self.quick_alive(self._url):
            raise RuntimeError(f"Ollama not reachable at {self._url}")
        try:
            vec = self.encode("ollama health check", normalize_embeddings=False)
            if vec.ndim == 1 and vec.shape[0] > 0:
                self._dim = int(vec.shape[0])
                self._verified = True
                _log.info("OllamaEmbedder: %s verified (%dd)", self._model, self._dim)
        except Exception as exc:
            _log.warning("OllamaEmbedder verification failed for %s: %s", self._model, exc)
            raise

    def shutdown(self) -> None:
        self._verified = False
        self._dim = None
