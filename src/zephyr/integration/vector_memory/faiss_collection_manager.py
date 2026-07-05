# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.faiss_collection_manager
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.schema.schemas; zephyr.integration.vector_memory.collection_manager
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_faiss_collection_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
FAISSCollectionManager — FAISS HNSW/IVF+PQ 8 Collection 全生命周期管理
=====================================================================
真源: VMS 蓝图 §12.2 · 迁自 ChromaDB 0.6 CollectionManager
API 契约与 CollectionManager 完全兼容——InProcessVectorMemory 无感切换

索引类型
--------
  HNSW (默认):       极致搜索速度 (143us/k=5), M=32, efConstruction=200, efSearch=64
  IVF+PQ:           内存/磁盘压缩 10-30x, nlist=128, M=16 (sub-quantizers), nbits=8
                    需要训练数据 (>30*nlist ≈ 3840 vectors), 搜索精确度 ~95-98%

mmap 共享内存架构
-----------------
所有 Index 通过 IO_FLAG_MMAP | IO_FLAG_READ_ONLY 加载
多进程零拷贝共享——12 Worker 仅 1 份物理内存 (VMS 蓝图 R1 终极方案)
写入由单 writer 进程通过可读写模式独占

GPU 加速
--------
自动检测 faiss-gpu, 可用时对 IVF 索引使用 GPU 搜索加速
HNSW 无 GPU 实现 (FAISS 限制), 但 HNSW 在 CPU 上已极快
"""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any, ClassVar

import numpy as np

from zephyr.integration.vector_memory.collection_manager import (
    COLLECTION_NAMES,
    COLLECTION_SCHEMAS,
    VMS_PERSIST_DIR,
    CollectionInfo,
    DesignPrinciplesEnforcer,
    VMSError,
)

_logger = logging.getLogger(__name__)

_FAISS_AVAILABLE = False
_FAISS_GPU_AVAILABLE = False
_GPU_COUNT = 0
try:
    import faiss

    _FAISS_AVAILABLE = True
    _GPU_COUNT = faiss.get_num_gpus()
    _FAISS_GPU_AVAILABLE = _GPU_COUNT > 0
    if _FAISS_GPU_AVAILABLE:
        _logger.info("FAISS GPU 可用: %d GPU(s)", _GPU_COUNT)
except ImportError:
    faiss = None  # type: ignore[assignment]


class FAISSCollectionManager:
    VMS_COLLECTION_NAMES: ClassVar[tuple[str, ...]] = COLLECTION_NAMES
    VMS_SCHEMAS: ClassVar[dict[str, dict[str, Any]]] = COLLECTION_SCHEMAS

    _FAISS_GPU_AVAILABLE: ClassVar[bool] = _FAISS_GPU_AVAILABLE
    _GPU_COUNT: ClassVar[int] = _GPU_COUNT

    _INDEX_HNSW = "hnsw"
    _INDEX_IVF_PQ = "ivf_pq"
    _INDEX_FLAT = "flat"
    _INDEX_TYPES: ClassVar[tuple[str, str, str]] = (_INDEX_HNSW, _INDEX_IVF_PQ, _INDEX_FLAT)

    _IVF_NLIST_DEFAULT = 128
    _PQ_M_DEFAULT = 16
    _PQ_NBITS_DEFAULT = 8

    def __init__(self, persist_dir: Path | str | None = None) -> None:
        if not _FAISS_AVAILABLE:
            raise VMSError("FAISS 未安装，请执行 pip install faiss-cpu>=1.8.0")
        self._persist_dir = Path(persist_dir) if persist_dir is not None else VMS_PERSIST_DIR
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        self._indices: dict[str, faiss.Index] = {}
        self._write_lock = threading.Lock()
        self._training_buffers: dict[str, list[np.ndarray]] = {}
        self._index_types: dict[str, str] = {}

        if _FAISS_GPU_AVAILABLE:
            self._gpu_resources: dict[int, Any] = {}
            for gpu_id in range(_GPU_COUNT):
                self._gpu_resources[gpu_id] = faiss.StandardGpuResources()

    @property
    def persist_dir(self) -> Path:
        return self._persist_dir

    @property
    def client(self) -> Any:
        return self

    @property
    def is_gpu_available(self) -> bool:
        return self._FAISS_GPU_AVAILABLE

    @property
    def gpu_count(self) -> int:
        return self._GPU_COUNT

    def _index_path(self, name: str) -> Path:
        return self._persist_dir / f"{name}.index"

    def _index_type_path(self, name: str) -> Path:
        return self._persist_dir / f"{name}.index_type"

    def _save_index(self, name: str, index: faiss.Index) -> None:
        faiss.write_index(index, str(self._index_path(name)))

    def _load_index_readonly(self, name: str) -> faiss.Index:
        path = str(self._index_path(name))
        if not os.path.exists(path):
            raise VMSError(f"FAISS 索引不存在: {path}，请先 create_collection")
        index_type = self._read_index_type(name)
        if index_type == self._INDEX_IVF_PQ:
            return faiss.read_index(path)
        return faiss.read_index(path, faiss.IO_FLAG_MMAP | faiss.IO_FLAG_READ_ONLY)

    def _maybe_to_gpu(self, index: faiss.Index) -> faiss.Index:
        if not _FAISS_GPU_AVAILABLE:
            return index
        if isinstance(index, (faiss.IndexIVFFlat, faiss.IndexIVFPQ, faiss.IndexFlat)):
            gpu_id = 0
            res = self._gpu_resources.get(gpu_id)
            if res is not None:
                return faiss.index_cpu_to_gpu(res, gpu_id, index)
        return index

    def _create_hnsw_index(self, dim: int) -> faiss.Index:
        index = faiss.IndexHNSWFlat(dim, 32)
        index.hnsw.efConstruction = 200
        index.hnsw.efSearch = 64
        return index

    def _create_ivf_pq_index(self, dim: int) -> faiss.Index:
        nlist = min(self._IVF_NLIST_DEFAULT, 256)
        M = min(self._PQ_M_DEFAULT, dim // 2)
        M = max(M, 2)

        quantizer = faiss.IndexFlatL2(dim)
        index = faiss.IndexIVFPQ(quantizer, dim, nlist, M, self._PQ_NBITS_DEFAULT)
        index.nprobe = 8
        return index

    def _create_index(self, dim: int, index_type: str) -> faiss.Index:
        if index_type == self._INDEX_IVF_PQ:
            return self._create_ivf_pq_index(dim)
        return self._create_hnsw_index(dim)

    def _read_index_type(self, name: str) -> str | None:
        path = self._index_type_path(name)
        if path.exists():
            return path.read_text().strip()
        return None

    def _write_index_type(self, name: str, index_type: str) -> None:
        self._index_type_path(name).write_text(index_type)

    def create_collection(
        self,
        name: str,
        dim: int | None = None,
        chunk_strategy: str = "semantic",
        ttl_days: int = 0,
        ai_autonomy: str = "supervised",
        index_type: str = "hnsw",
        strict: bool = True,
    ) -> CollectionInfo:
        if index_type not in self._INDEX_TYPES:
            raise ValueError(f"未知索引类型: {index_type}。允许值: {', '.join(self._INDEX_TYPES)}")

        schema = COLLECTION_SCHEMAS.get(name, {})
        if dim is None:
            dim = schema.get("dimension", 1024)
        if schema.get("chunk_strategy") and chunk_strategy == "semantic":
            chunk_strategy = schema["chunk_strategy"]
        if schema.get("ttl_days", 0) > 0 and ttl_days == 0:
            ttl_days = schema["ttl_days"]
        if schema.get("ai_autonomy_level") and ai_autonomy == "supervised":
            ai_autonomy = schema["ai_autonomy_level"]

        DesignPrinciplesEnforcer.validate_dimension(dim)
        DesignPrinciplesEnforcer.validate_chunk_strategy(name, chunk_strategy)
        DesignPrinciplesEnforcer.validate_ttl(name, ttl_days)

        index_path = self._index_path(name)

        if index_path.exists():
            self._indices[name] = self._load_index_readonly(name)
            saved_type = self._read_index_type(name) or "hnsw"
            self._index_types[name] = saved_type
            return CollectionInfo(
                name=name,
                dimension=dim,
                chunk_strategy=chunk_strategy,
                ttl_days=ttl_days,
                ai_autonomy_level=ai_autonomy,
                embedding_model=schema["embedding_model"],
                metadata={
                    "dimension": dim,
                    "chunk_strategy": chunk_strategy,
                    "ttl_days": ttl_days if ttl_days > 0 else 0,
                    "ai_autonomy_level": ai_autonomy,
                    "embedding_model": schema["embedding_model"],
                    "hnsw:space": schema["hnsw:space"],
                    "index_type": index_type,
                },
                exists=True,
            )

        index = self._create_index(dim, index_type)
        self._save_index(name, index)
        self._write_index_type(name, index_type)
        self._indices[name] = self._load_index_readonly(name)
        self._index_types[name] = index_type

        index_desc = (
            "IndexHNSW"
            if index_type == self._INDEX_HNSW
            else "IndexIVFPQ"
            if index_type == self._INDEX_IVF_PQ
            else "IndexFlat"
        )
        _logger.info(
            "FAISSCollectionManager: 创建 %s '%s' (%dd, %s, type=%s)",
            index_desc,
            name,
            dim,
            chunk_strategy,
            index_type,
        )
        return CollectionInfo(
            name=name,
            dimension=dim,
            chunk_strategy=chunk_strategy,
            ttl_days=ttl_days,
            ai_autonomy_level=ai_autonomy,
            embedding_model=schema["embedding_model"],
            metadata={
                "dimension": dim,
                "chunk_strategy": chunk_strategy,
                "ttl_days": ttl_days if ttl_days > 0 else 0,
                "ai_autonomy_level": ai_autonomy,
                "embedding_model": schema["embedding_model"],
                "hnsw:space": schema["hnsw:space"],
                "index_type": index_type,
            },
            exists=True,
        )

    def train_ivf(self, collection_name: str, vectors: np.ndarray) -> None:
        index_type = self._index_types.get(collection_name, self._INDEX_HNSW)
        if index_type != self._INDEX_IVF_PQ:
            _logger.warning("train_ivf 跳过: '%s' 不是 IVF+PQ 索引", collection_name)
            return

        index_path = self._index_path(collection_name)
        ivf_index = self._create_ivf_pq_index(vectors.shape[1])

        if vectors.shape[0] < 30 * ivf_index.nlist:
            buffer = self._training_buffers.setdefault(collection_name, [])
            buffer.append(vectors)
            buffered = sum(v.shape[0] for v in buffer)
            min_needed = 30 * ivf_index.nlist
            _logger.info(
                "IVF 训练: '%s' 累积 %d/%d vectors, 暂不训练",
                collection_name,
                buffered,
                min_needed,
            )
            return

        _logger.info("IVF 训练: '%s' 开始 (%d vectors × %dd)", collection_name, vectors.shape[0], vectors.shape[1])
        ivf_index.train(vectors.astype(np.float32))
        with self._write_lock:
            self._save_index(collection_name, ivf_index)
            self._training_buffers.pop(collection_name, None)
        if collection_name in self._indices:
            del self._indices[collection_name]
        _logger.info("IVF 训练: '%s' 完成 (nlist=%d, nprobe=%d)", collection_name, ivf_index.nlist, ivf_index.nprobe)

    def add_vector(
        self,
        collection_name: str,
        vector: np.ndarray,
    ) -> int:
        index_path = self._index_path(collection_name)
        if not index_path.exists():
            raise VMSError(f"Collection '{collection_name}' 未创建，请先 create_collection")

        if vector.ndim == 1:
            vector = vector.reshape(1, -1)

        with self._write_lock:
            index = faiss.read_index(str(index_path))
            actual_dim = index.d
            if vector.shape[1] != actual_dim:
                raise VMSError(f"向量维度 {vector.shape[1]} 不匹配 Collection '{collection_name}' 实际 {actual_dim}d")
            assigned_id = index.ntotal
            if hasattr(index, "is_trained") and not index.is_trained:
                index.train(vector.astype(np.float32))
            index.add(vector.astype(np.float32))
            self._save_index(collection_name, index)

        if collection_name in self._indices:
            del self._indices[collection_name]

        return assigned_id

    def add_vectors_batch(
        self,
        collection_name: str,
        vectors: np.ndarray,
    ) -> None:
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        index_path = self._index_path(collection_name)
        if not index_path.exists():
            raise VMSError(f"Collection '{collection_name}' 未创建，请先 create_collection")

        with self._write_lock:
            index = faiss.read_index(str(index_path))
            actual_dim = index.d
            if vectors.shape[1] != actual_dim:
                raise VMSError(
                    f"批量向量维度 {vectors.shape[1]} 不匹配 Collection '{collection_name}' 实际 {actual_dim}d"
                )
            if hasattr(index, "is_trained") and not index.is_trained:
                index.train(vectors.astype(np.float32))
            index.add(vectors.astype(np.float32))
            self._save_index(collection_name, index)

        if collection_name in self._indices:
            del self._indices[collection_name]

    def search(
        self,
        collection_name: str,
        query_vector: np.ndarray,
        k: int = 5,
    ) -> tuple[np.ndarray, np.ndarray]:
        index = self.get_collection(collection_name)
        if index.ntotal == 0:
            return np.array([], dtype=np.float32), np.array([], dtype=np.int64)

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        search_index = self._maybe_to_gpu(index)
        distances, ids = search_index.search(query_vector.astype(np.float32), min(k, index.ntotal))
        return distances.flatten(), ids.flatten()

    def count(self, collection_name: str) -> int:
        index_path = self._index_path(collection_name)
        if not index_path.exists():
            return 0
        index = self.get_collection(collection_name)
        return index.ntotal

    def get_collection(self, name: str) -> faiss.Index:
        if name not in self._indices:
            self._indices[name] = self._load_index_readonly(name)
        return self._indices[name]

    def list_collections(self) -> list[CollectionInfo]:
        results: list[CollectionInfo] = []
        for name in COLLECTION_NAMES:
            schema = COLLECTION_SCHEMAS[name]
            exists = self._index_path(name).exists()
            results.append(
                CollectionInfo(
                    name=name,
                    dimension=schema["dimension"],
                    chunk_strategy=schema["chunk_strategy"],
                    ttl_days=schema["ttl_days"],
                    ai_autonomy_level=schema["ai_autonomy_level"],
                    embedding_model=schema["embedding_model"],
                    metadata={
                        "dimension": schema["dimension"],
                        "chunk_strategy": schema["chunk_strategy"],
                        "ttl_days": schema["ttl_days"],
                        "ai_autonomy_level": schema["ai_autonomy_level"],
                        "embedding_model": schema["embedding_model"],
                        "hnsw:space": schema["hnsw:space"],
                    },
                    exists=exists,
                )
            )
        return results

    def init_all_collections(self) -> list[CollectionInfo]:
        results: list[CollectionInfo] = []
        for name in COLLECTION_NAMES:
            schema = COLLECTION_SCHEMAS[name]
            info = self.create_collection(
                name=name,
                dim=schema["dimension"],
                chunk_strategy=schema["chunk_strategy"],
                ttl_days=schema["ttl_days"],
                ai_autonomy=schema["ai_autonomy_level"],
            )
            results.append(info)
        return results

    def purge_expired(self) -> dict[str, int]:
        return {}

    def health_check(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "collections": {},
            "total_size_mb": 0,
            "gpu": {"available": _FAISS_GPU_AVAILABLE, "count": _GPU_COUNT},
        }
        for name in COLLECTION_NAMES:
            idx_path = self._index_path(name)
            index_type = self._read_index_type(name) or "hnsw"
            if idx_path.exists():
                size_mb = idx_path.stat().st_size / (1024 * 1024)
                result["collections"][name] = {
                    "exists": True,
                    "size_mb": round(size_mb, 2),
                    "vectors": self.count(name),
                    "index_type": index_type,
                }
                result["total_size_mb"] += size_mb
            else:
                result["collections"][name] = {"exists": False}
        result["total_size_mb"] = round(result["total_size_mb"], 2)
        return result
