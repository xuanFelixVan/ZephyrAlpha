# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §3.1
# [MODULE] zephyr.integration.local_model.embedding_router
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.local_model.ollama_embedding
# [CONSUMERS] zephyr.autonomy_core.skills.skill_router; zephyr.integration.vector_memory.in_process_vector_memory; zephyr.integration.pipeline_orchestrator; zephyr.integration.local_model.local_model_scheduler; zephyr.integration.local_model.__init__; zephyr.trading.auto_runtime_core; tests.unit.vector_memory.test_vector_memory
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-042 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
    BGE-M3 加载失败 -> 全局降级为 bge-small
    bge-small 也失败 -> InMemoryBackend（零向量兜底）
"""

from __future__ import annotations

from typing import Final
import hashlib
import logging
import time
from pathlib import Path
from typing import Any, Literal, Protocol, runtime_checkable

import numpy as np

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# EmbeddingRouterProtocol — DI 注入契约（5.133.8 专项工程，2026-07-06）
# ---------------------------------------------------------------------------
# 目的：消除 EmbeddingRouter 在 5 处散点硬编码实例化，改为构造函数注入。
# 使用方可注入任意实现此 Protocol 的对象（如测试 mock），无需依赖具体类。
# 现有懒初始化兜底逻辑保留，确保向后兼容。
# ---------------------------------------------------------------------------


@runtime_checkable
class EmbeddingRouterProtocol(Protocol):
    """嵌入路由器协议——DI 注入契约。

    任何实现此协议的对象均可注入到 skill_router / vector_memory /
    pipeline_orchestrator / local_model_scheduler / auto_runtime_core。
    """

    @property
    def bge_m3_available(self) -> bool: ...

    @property
    def bge_small_available(self) -> bool: ...

    @property
    def bge_m3_dim(self) -> int: ...

    @property
    def bge_small_dim(self) -> int: ...

    @property
    def fallback_mode(self) -> str: ...

    @property
    def backend(self) -> str: ...

    def warmup(self) -> None: ...

    def embed(self, text: str, collection_name: str) -> np.ndarray: ...

    def embed_batch(self, texts: list[str], collection_name: str) -> np.ndarray: ...

    def health_check(self) -> dict[str, Any]: ...

    def shutdown(self) -> None: ...

MODEL_DIR_BGE_M3: Final[Path] = Path("data/models/local_model/bge-m3")
MODEL_DIR_BGE_SMALL: Final[Path] = Path("data/models/local_model/paraphrase-multilingual-MiniLM-L12-v2")

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
        backend: Literal["local", "ollama"] = "ollama",
        max_loaded_models: int = 2,
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
        self._max_loaded_models: int = max_loaded_models
        self._model_last_used: dict[str, float] = {}

    @property
    def max_loaded_models(self) -> int:
        return self._max_loaded_models

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

    def _loaded_model_count(self) -> int:
        """当前已加载模型数。"""
        count = 0
        if self._bge_m3_model is not None:
            count += 1
        if self._bge_small_model is not None:
            count += 1
        return count

    def _touch_model(self, model_key: str) -> None:
        """更新模型最后使用时间戳。"""
        self._model_last_used[model_key] = time.time()

    def _evict_lru(self) -> None:
        """当已加载模型数超过 max_loaded_models 时，淘汰最久未用的模型。"""
        if self._loaded_model_count() <= self._max_loaded_models:
            return

        loaded_keys: list[str] = []
        if self._bge_m3_model is not None:
            loaded_keys.append("m3")
        if self._bge_small_model is not None:
            loaded_keys.append("small")

        if not loaded_keys:
            return

        lru_key = min(loaded_keys, key=lambda k: self._model_last_used.get(k, 0.0))

        if lru_key == "m3":
            _logger.info("EmbeddingRouter: LRU 淘汰 BGE-M3 (释放显存)")
            if hasattr(self._bge_m3_model, "shutdown"):
                self._bge_m3_model.shutdown()
            self._bge_m3_model = None
            self._bge_m3_available = False
        elif lru_key == "small":
            _logger.info("EmbeddingRouter: LRU 淘汰 bge-small (释放显存)")
            if hasattr(self._bge_small_model, "shutdown"):
                self._bge_small_model.shutdown()
            self._bge_small_model = None
            self._bge_small_available = False

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

        if self._bge_m3_available:
            self._touch_model("m3")
        if self._bge_small_available:
            self._touch_model("small")

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
                    "EmbeddingRouter: BGE-M3 embed %s -> %s (%dd, %.1fms)",
                    text[:30],
                    collection_name,
                    vec.shape[0],
                    elapsed,
                )
                self._touch_model("m3")
                return vec
            elif self._bge_small_available:
                _logger.warning(
                    "EmbeddingRouter: BGE-M3 不可用，降级为 bge-small (%dd) -> %s", self._bge_small_dim, collection_name
                )
                vec = self._embed_bge_small(text)
                self._touch_model("small")
                return vec
            else:
                raise RuntimeError("无可用嵌入模型")

        if collection_name in BGE_SMALL_COLLECTIONS:
            if self._bge_small_available:
                start = time.perf_counter()
                vec = self._embed_bge_small(text)
                elapsed = (time.perf_counter() - start) * 1000
                _logger.debug(
                    "EmbeddingRouter: bge-small embed %s -> %s (%dd, %.1fms)",
                    text[:30],
                    collection_name,
                    vec.shape[0],
                    elapsed,
                )
                self._touch_model("small")
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
            self._touch_model("m3" if self._bge_m3_model is model else "small")
        elif collection_name in BGE_SMALL_COLLECTIONS:
            if self._bge_small_model is None:
                raise RuntimeError("bge-small 模型不可用")
            embeddings = self._bge_small_model.encode(texts, normalize_embeddings=True, batch_size=BGE_SMALL_BATCH_SIZE)
            self._touch_model("small")
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
            "max_loaded_models": self._max_loaded_models,
            "loaded_model_count": self._loaded_model_count(),
            "model_last_used": dict(self._model_last_used),
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
        self._model_last_used.clear()
        _logger.info("EmbeddingRouter: 已关闭")
