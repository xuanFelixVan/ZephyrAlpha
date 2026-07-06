# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §3.1
# [MODULE] zephyr.integration.governance.embedding_router
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.integration.local_model.ollama_embedding
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
# [A_module] module_id=MOD-GOV_embedding_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
EmbeddingRouter — MOD-INF-011 双嵌入维度路由
==============================================
蓝图 §3.1 · V-VMS-505/507 · 按 Collection 路由到对应模型

路由规则
--------
    BGE-M3 1024d ← decisions / code_context / lessons / knowledge / rules
    bge-small (384d/512d) ← blueprints / session_snapshots / execution_traces

后端支持
--------
    local : SentenceTransformer 本地加载（默认，从 models/ 目录或 HuggingFace）
    ollama: Ollama HTTP API（复用已有模型，零额外下载）

降级链
------
    BGE-M3 加载失败 → 全局降级为 bge-small
    bge-small 也失败 → InMemoryBackend（零向量兜底）
"""

from __future__ import annotations

from typing import Final
import hashlib
import logging
import time
from pathlib import Path
from typing import Any, Literal

import numpy as np

_logger = logging.getLogger(__name__)

MODEL_DIR_BGE_M3: Final[Path] = Path("models/bge-m3")
MODEL_DIR_BGE_SMALL: Final[Path] = Path("models/bge-small-zh-v1.5")

BGE_M3_COLLECTIONS: Final[frozenset[str]] = frozenset(
    {
        "decisions",
        "code_context",
        "lessons",
        "knowledge",
        "rules",
    }
)
BGE_SMALL_COLLECTIONS: Final[frozenset[str]] = frozenset(
    {
        "blueprints",
        "session_snapshots",
        "execution_traces",
    }
)

BGE_M3_BATCH_SIZE: Final[int] = 16
BGE_SMALL_BATCH_SIZE: Final[int] = 32

OLLAMA_BGE_M3_MODEL: Final[str] = "BGE-M3:latest"
OLLAMA_BGE_SMALL_MODEL: Final[str] = "qllama/bge-small-en-v1.5:latest"


def l2_normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm < 1e-12:
        return vec
    return vec / norm


def verify_model_checksum(model_dir: Path, expected_sha256: str | None = None) -> bool:
    if not model_dir.exists():
        return False
    onnx_files = sorted(model_dir.glob("*.onnx"))
    if not onnx_files:
        return True
    if expected_sha256 is None:
        return True
    sha = hashlib.sha256()
    for f in onnx_files:
        sha.update(f.read_bytes())
    actual = sha.hexdigest()
    if actual != expected_sha256:
        _logger.warning("模型 SHA256 不匹配: 期望 %s, 实际 %s", expected_sha256[:16], actual[:16])
        return False
    return True


class EmbeddingRouter:
    """双嵌入模型路由器——支持 local(SentenceTransformer) 和 ollama 两种后端。"""

    def __init__(
        self,
        model_dir_bge_m3: Path | str = MODEL_DIR_BGE_M3,
        model_dir_bge_small: Path | str = MODEL_DIR_BGE_SMALL,
        *,
        backend: Literal["local", "ollama"] = "local",
    ) -> None:
        self._backend: str = backend
        self._model_dir_bge_m3 = Path(model_dir_bge_m3)
        self._model_dir_bge_small = Path(model_dir_bge_small)
        self._bge_m3_model: Any | None = None
        self._bge_small_model: Any | None = None
        self._bge_m3_dim: int = 0
        self._bge_small_dim: int = 0
        self._bge_m3_available: bool = False
        self._bge_small_available: bool = False
        self._fallback_mode: str = "none"

    @property
    def bge_m3_available(self) -> bool:
        return self._bge_m3_available

    @property
    def bge_small_available(self) -> bool:
        return self._bge_small_available

    @property
    def bge_m3_dim(self) -> int:
        return self._bge_m3_dim

    @property
    def bge_small_dim(self) -> int:
        return self._bge_small_dim

    @property
    def fallback_mode(self) -> str:
        return self._fallback_mode

    @property
    def backend(self) -> str:
        return self._backend

    def warmup(self) -> None:
        _logger.info("EmbeddingRouter: 开始预热双嵌入模型 (backend=%s)...", self._backend)
        self._load_bge_m3()
        self._load_bge_small()

        if not self._bge_m3_available and not self._bge_small_available:
            _logger.critical("EmbeddingRouter: 双模型均不可用，进入 InMemory 降级模式")
            self._fallback_mode = "in_memory"
            return

        if self._bge_m3_available:
            try:
                vec = self._embed_bge_m3("hello world warmup")
                self._bge_m3_dim = int(vec.shape[0])
                if self._bge_m3_dim > 0 and not np.any(np.isnan(vec)):
                    _logger.info("EmbeddingRouter: BGE-M3 预热成功 (%dd, backend=%s)", self._bge_m3_dim, self._backend)
                else:
                    raise ValueError(f"输出维度异常: dim={self._bge_m3_dim}, 期望>0")
            except Exception:
                _logger.warning("EmbeddingRouter: BGE-M3 预热失败，降级", exc_info=True)
                self._bge_m3_available = False

        if self._bge_small_available:
            try:
                vec = self._embed_bge_small("hello world warmup")
                self._bge_small_dim = int(vec.shape[0])
                if self._bge_small_dim > 0 and not np.any(np.isnan(vec)):
                    _logger.info(
                        "EmbeddingRouter: bge-small 预热成功 (%dd, backend=%s)", self._bge_small_dim, self._backend
                    )
                else:
                    raise ValueError(f"输出维度异常: dim={self._bge_small_dim}, 期望>0")
            except Exception:
                _logger.warning("EmbeddingRouter: bge-small 预热失败", exc_info=True)
                self._bge_small_available = False

        if not self._bge_m3_available and not self._bge_small_available:
            self._fallback_mode = "in_memory"

    def _load_bge_m3(self) -> None:
        if self._backend == "ollama":
            self._load_ollama("m3")
        else:
            self._load_local("m3")

    def _load_bge_small(self) -> None:
        if self._backend == "ollama":
            self._load_ollama("small")
        else:
            self._load_local("small")

    def _load_ollama(self, model_key: str) -> None:
        try:
            from zephyr.integration.local_model.ollama_embedding import OllamaEmbedder

            model_name = OLLAMA_BGE_M3_MODEL if model_key == "m3" else OLLAMA_BGE_SMALL_MODEL
            embedder = OllamaEmbedder(model=model_name)
            if not embedder.available:
                if model_key == "m3":
                    _logger.warning("EmbeddingRouter: Ollama BGE-M3 (%s) 不可用", model_name)
                    self._bge_m3_available = False
                else:
                    _logger.warning("EmbeddingRouter: Ollama bge-small (%s) 不可用", model_name)
                    self._bge_small_available = False
                return

            if model_key == "m3":
                self._bge_m3_model = embedder
                self._bge_m3_dim = embedder.dim
                self._bge_m3_available = True
                _logger.info("EmbeddingRouter: Ollama BGE-M3 就绪 (%s, %dd)", model_name, embedder.dim)
            else:
                self._bge_small_model = embedder
                self._bge_small_dim = embedder.dim
                self._bge_small_available = True
                _logger.info("EmbeddingRouter: Ollama bge-small 就绪 (%s, %dd)", model_name, embedder.dim)
        except Exception as e:
            if model_key == "m3":
                _logger.warning("EmbeddingRouter: Ollama BGE-M3 加载失败: %s", e, exc_info=True)
                self._bge_m3_available = False
            else:
                _logger.warning("EmbeddingRouter: Ollama bge-small 加载失败: %s", e)
                self._bge_small_available = False

    def _load_local(self, model_key: str) -> None:
        model_path = self._model_dir_bge_m3 if model_key == "m3" else self._model_dir_bge_small
        try:
            if not model_path.exists():
                if model_key == "m3":
                    _logger.warning("EmbeddingRouter: BGE-M3 模型目录不存在: %s，尝试 HuggingFace", model_path)
                else:
                    _logger.warning("EmbeddingRouter: bge-small 模型目录不存在: %s，尝试 HuggingFace", model_path)

            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(str(model_path), device="cpu")
            if model_key == "m3":
                self._bge_m3_model = model
                self._bge_m3_available = True
                _logger.info("EmbeddingRouter: BGE-M3 本地模型加载成功 (%s)", model_path)
            else:
                self._bge_small_model = model
                self._bge_small_available = True
                _logger.info("EmbeddingRouter: bge-small 本地模型加载成功 (%s)", model_path)
        except Exception as e:
            if model_key == "m3":
                _logger.warning("EmbeddingRouter: BGE-M3 本地加载失败: %s", e, exc_info=True)
                self._bge_m3_available = False
                if not self._bge_small_available:
                    self._fallback_mode = "bge_small_only"
            else:
                _logger.warning("EmbeddingRouter: bge-small 本地加载失败: %s", e)
                self._bge_small_available = False

    def _embed_bge_m3(self, text: str) -> np.ndarray:
        if self._bge_m3_model is None:
            raise RuntimeError("BGE-M3 模型未加载")
        embedding = self._bge_m3_model.encode(text, normalize_embeddings=True)
        return np.asarray(embedding, dtype=np.float32)

    def _embed_bge_small(self, text: str) -> np.ndarray:
        if self._bge_small_model is None:
            raise RuntimeError("bge-small 模型未加载")
        embedding = self._bge_small_model.encode(text, normalize_embeddings=True)
        return np.asarray(embedding, dtype=np.float32)

    def embed(self, text: str, collection_name: str) -> np.ndarray:
        if self._fallback_mode == "in_memory":
            return np.zeros(self._bge_small_dim or 384, dtype=np.float32)

        if collection_name in BGE_M3_COLLECTIONS:
            if self._bge_m3_available:
                start = time.perf_counter()
                vec = self._embed_bge_m3(text)
                elapsed = (time.perf_counter() - start) * 1000
                _logger.debug(
                    "EmbeddingRouter: BGE-M3 embed %s → %s (%dd, %.1fms)",
                    text[:30],
                    collection_name,
                    vec.shape[0],
                    elapsed,
                )
                return vec
            elif self._bge_small_available:
                _logger.warning(
                    "EmbeddingRouter: BGE-M3 不可用，降级为 bge-small (%dd) → %s", self._bge_small_dim, collection_name
                )
                return self._embed_bge_small(text)
            else:
                raise RuntimeError("无可用嵌入模型")

        if collection_name in BGE_SMALL_COLLECTIONS:
            if self._bge_small_available:
                start = time.perf_counter()
                vec = self._embed_bge_small(text)
                elapsed = (time.perf_counter() - start) * 1000
                _logger.debug(
                    "EmbeddingRouter: bge-small embed %s → %s (%dd, %.1fms)",
                    text[:30],
                    collection_name,
                    vec.shape[0],
                    elapsed,
                )
                return vec
            else:
                raise RuntimeError("bge-small 模型不可用")

        raise KeyError(f"未知 Collection: {collection_name}")

    def embed_batch(self, texts: list[str], collection_name: str) -> np.ndarray:
        if self._fallback_mode == "in_memory":
            return np.zeros((len(texts), self._bge_small_dim or 384), dtype=np.float32)

        if collection_name in BGE_M3_COLLECTIONS:
            model = self._bge_m3_model if self._bge_m3_available else self._bge_small_model
            if model is None:
                raise RuntimeError("无可用嵌入模型")
            embeddings = model.encode(texts, normalize_embeddings=True, batch_size=BGE_M3_BATCH_SIZE)
        elif collection_name in BGE_SMALL_COLLECTIONS:
            if self._bge_small_model is None:
                raise RuntimeError("bge-small 模型不可用")
            embeddings = self._bge_small_model.encode(texts, normalize_embeddings=True, batch_size=BGE_SMALL_BATCH_SIZE)
        else:
            raise KeyError(f"未知 Collection: {collection_name}")

        return np.asarray(embeddings, dtype=np.float32)

    def health_check(self) -> dict[str, Any]:
        return {
            "bge_m3_available": self._bge_m3_available,
            "bge_small_available": self._bge_small_available,
            "fallback_mode": self._fallback_mode,
            "backend": self._backend,
            "bge_m3_dim": self._bge_m3_dim,
            "bge_small_dim": self._bge_small_dim,
        }

    def shutdown(self) -> None:
        if self._bge_m3_model is not None and hasattr(self._bge_m3_model, "shutdown"):
            self._bge_m3_model.shutdown()
        if self._bge_small_model is not None and hasattr(self._bge_small_model, "shutdown"):
            self._bge_small_model.shutdown()
        self._bge_m3_model = None
        self._bge_small_model = None
        self._bge_m3_available = False
        self._bge_small_available = False
        _logger.info("EmbeddingRouter: 已关闭")
