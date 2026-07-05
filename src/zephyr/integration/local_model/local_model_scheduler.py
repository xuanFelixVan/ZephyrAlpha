# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §3.1
# [MODULE] zephyr.integration.local_model.local_model_scheduler
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.lifecycle.resource_optimization_engine; zephyr.integration.local_model.embedding_router; zephyr.integration.local_model.ollama_chat
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
# [A_module] module_id=MOD-INT_local_model_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
LocalModelScheduler — L2 本地模型 24/7 调度循环
================================================
后台守护线程，轮询本地任务队列，自动分派到 EmbeddingRouter 或 OllamaChat。

架构
----
    TaskCard → LocalModelScheduler.enqueue(task)
                  │
                  ├─ vector_embedding   → EmbeddingRouter (BGE-M3 1024d)
                  ├─ semantic_search    → EmbeddingRouter + ChromaDB
                  ├─ reranking          → Reranker (bge-reranker-v2-m3)
                  ├─ task_classification → OllamaChat (qwen3:8b)
                  ├─ tag_completion      → OllamaChat (qwen3:8b)
                  ├─ summary_extraction  → OllamaChat (qwen3:8b)
                  ├─ anomaly_triage      → OllamaChat (qwen3:8b)
                  ├─ query_rewrite       → OllamaChat (qwen3:8b)
                  └─ naming_suggest      → OllamaChat (qwen3:8b)

用法
----
    scheduler = LocalModelScheduler(embedding_router, ollama_chat)
    scheduler.start()
    scheduler.enqueue(task_id="T-001", capability="vector_embedding", payload=...)
    result = scheduler.wait_result("T-001", timeout=30)
    scheduler.stop()
"""

from __future__ import annotations

logger = logging.getLogger(__name__)

import logging
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)

POLL_INTERVAL_S: float = 5.0
RESULT_TTL_S: float = 300.0

EMBEDDING_CAPABILITIES: frozenset[str] = frozenset(
    {
        "vector_embedding",
    }
)

SEARCH_CAPABILITIES: frozenset[str] = frozenset(
    {
        "semantic_search",
    }
)

RERANKING_CAPABILITIES: frozenset[str] = frozenset(
    {
        "reranking",
    }
)

INFERENCE_CAPABILITIES: frozenset[str] = frozenset(
    {
        "task_classification",
        "tag_completion",
        "summary_extraction",
        "anomaly_triage",
        "query_rewrite",
        "naming_suggest",
    }
)

ALL_LOCAL_CAPABILITIES: frozenset[str] = (
    EMBEDDING_CAPABILITIES | SEARCH_CAPABILITIES | RERANKING_CAPABILITIES | INFERENCE_CAPABILITIES
)


@dataclass
class LocalTask:
    task_id: str
    capability: str
    payload: object = None
    result: dict | None = None
    error: str | None = None
    status: str = "pending"
    enqueued_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    retries: int = 0
    max_retries: int = 3


class LocalModelScheduler:
    """本地模型 24/7 调度器——后台线程轮询 + 分派。"""

    def __init__(
        self,
        embedding_router: Any = None,
        ollama_chat: Any = None,
        *,
        poll_interval_s: float = POLL_INTERVAL_S,
    ) -> None:
        self._embedding_router = embedding_router
        self._ollama_chat = ollama_chat
        self._poll_interval = poll_interval_s
        self._task_queue: queue.Queue[LocalTask] = queue.Queue(maxsize=100)  # 5.16.12 修复：添加 maxsize 防止无边界积压
        self._results: dict[str, LocalTask] = {}
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._running = False
        self._stats: dict[str, int] = {"completed": 0, "failed": 0, "pending": 0}

    @property
    def running(self) -> bool:
        return self._running

    @property
    def stats(self) -> dict[str, int]:
        with self._lock:
            return dict(self._stats)

    @property
    def pending_count(self) -> int:
        return self._task_queue.qsize()

    def enqueue(
        self,
        task_id: str,
        capability: str,
        payload: Any = None,
    ) -> None:
        if capability not in ALL_LOCAL_CAPABILITIES:
            raise ValueError(f"未知本地能力: {capability}，支持: {ALL_LOCAL_CAPABILITIES}")

        task = LocalTask(task_id=task_id, capability=capability, payload=payload)
        self._task_queue.put(task)
        with self._lock:
            self._stats["pending"] = self._stats.get("pending", 0) + 1
        _log.debug("LocalModelScheduler: enqueued %s (%s)", task_id, capability)

    def wait_result(self, task_id: str, timeout: float = 60.0) -> LocalTask | None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                entry = self._results.get(task_id)
                if entry and entry.status in ("completed", "failed"):
                    return entry
            time.sleep(0.5)
        return None

    def start(self) -> None:
        # 5.16.12 修复：start() 加锁防止并发创建多个 worker 线程
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True, name="LocalModelScheduler")
            self._thread.start()
        from zephyr.shared.lifecycle.resource_optimization_engine import ResourceOptimizationEngine

        try:
            ResourceOptimizationEngine().register_daemon(
                "local-model-scheduler",
                self.start,
                self.stop,
                priority=3,
            )
        except Exception as e:
            logger.debug("suppressed error in local_model_scheduler", exc_info=True)
        _log.info("LocalModelScheduler: 后台线程已启动 (poll=%ss)", self._poll_interval)

    def stop(self) -> None:
        # 5.142.6 修复: 复用 self._lock 保护 _running 写入, join 在锁外执行避免长时间持锁 (start() 已用 self._lock 保护)
        with self._lock:
            self._running = False
            thread = self._thread
        if thread is not None:
            thread.join(timeout=10.0)
        with self._lock:
            self._thread = None
        _log.info(
            "LocalModelScheduler: 已停止 (completed=%d failed=%d)",
            self._stats.get("completed", 0),
            self._stats.get("failed", 0),
        )

    def ensure_models(self) -> None:
        if self._embedding_router is None:
            try:
                from zephyr.integration.local_model.embedding_router import EmbeddingRouter

                self._embedding_router = EmbeddingRouter(backend="ollama")
                self._embedding_router.warmup()
                _log.info("LocalModelScheduler: EmbeddingRouter 自动初始化")
            except Exception as exc:
                _log.warning("LocalModelScheduler: EmbeddingRouter 初始化失败: %s", exc, exc_info=True)

        if self._ollama_chat is None:
            try:
                from zephyr.integration.local_model.ollama_chat import OllamaChat

                self._ollama_chat = OllamaChat()
                if self._ollama_chat.available:
                    _log.info("LocalModelScheduler: OllamaChat 自动初始化")
                else:
                    _log.warning("LocalModelScheduler: OllamaChat 不可用")
                    self._ollama_chat = None
            except Exception as exc:
                _log.warning("LocalModelScheduler: OllamaChat 初始化失败: %s", exc, exc_info=True)

    def _run(self) -> None:
        self.ensure_models()
        while self._running:
            try:
                task = self._task_queue.get(timeout=self._poll_interval)
                _log.debug("LocalModelScheduler: processing %s (%s)", task.task_id, task.capability)
                self._dispatch(task)
                self._task_queue.task_done()
            except queue.Empty:
                self._cleanup_expired_results()
                continue
            except Exception as exc:
                _log.error("LocalModelScheduler: dispatch error: %s", exc, exc_info=True)

    def _dispatch(self, task: LocalTask) -> None:
        try:
            if task.capability in EMBEDDING_CAPABILITIES:
                result = self._handle_embedding(task)
            elif task.capability in SEARCH_CAPABILITIES:
                result = self._handle_search(task)
            elif task.capability in RERANKING_CAPABILITIES:
                result = self._handle_reranking(task)
            elif task.capability in INFERENCE_CAPABILITIES:
                result = self._handle_inference(task)
            else:
                result = {"error": f"unhandled capability: {task.capability}"}
                task.status = "failed"
                task.error = f"unhandled capability: {task.capability}"

            if task.status != "failed":
                task.result = result
                task.status = "completed"
                task.finished_at = time.time()
                with self._lock:
                    self._stats["completed"] = self._stats.get("completed", 0) + 1
                    self._stats["pending"] = max(0, self._stats.get("pending", 1) - 1)
            else:
                task.finished_at = time.time()
                with self._lock:
                    self._stats["failed"] = self._stats.get("failed", 0) + 1
                    self._stats["pending"] = max(0, self._stats.get("pending", 1) - 1)

        except Exception as exc:
            err_msg = str(exc)
            if self._should_retry(err_msg) and task.retries < task.max_retries:
                task.retries += 1
                backoff_s = min(2**task.retries, 15)
                _log.warning(
                    "LocalModelScheduler: %s (%s) retry %d/%d in %ds: %s",
                    task.task_id,
                    task.capability,
                    task.retries,
                    task.max_retries,
                    backoff_s,
                    err_msg, exc_info=True
                )
                time.sleep(backoff_s)
                self._task_queue.put(task)
            else:
                task.status = "failed"
                task.error = err_msg
                task.finished_at = time.time()
                with self._lock:
                    self._stats["failed"] = self._stats.get("failed", 0) + 1
                    self._stats["pending"] = max(0, self._stats.get("pending", 1) - 1)
                _log.error("LocalModelScheduler: %s (%s) failed: %s", task.task_id, task.capability, exc)

    @staticmethod
    def _should_retry(error_msg: str) -> bool:
        retry_markers = [
            "500 Server Error",
            "503 Server Error",
            "502 Server Error",
            "Read timed out",
            "ConnectionError",
            "RemoteDisconnected",
        ]
        return any(m in error_msg for m in retry_markers)

    def _handle_embedding(self, task: LocalTask) -> dict:
        if self._embedding_router is None:
            raise RuntimeError("EmbeddingRouter 未初始化")

        payload = task.payload or {}
        text = payload.get("text", "")
        collection = payload.get("collection", "knowledge")

        if not text:
            raise ValueError("embedding payload 缺少 text")

        if isinstance(text, list):
            self._embedding_router.embed_batch(text, collection)
            return {"dim": self._embedding_router.bge_m3_dim, "count": len(text)}
        vector = self._embedding_router.embed(text, collection)
        return {"dim": int(vector.shape[0]), "normalized": True}

    def _handle_search(self, task: LocalTask) -> dict:
        payload = task.payload or {}
        query = payload.get("query", "")
        top_k = payload.get("top_k", 10)

        if not query:
            raise ValueError("search payload 缺少 query")

        return {
            "query": query,
            "top_k": top_k,
            "results": [],
            "note": "semantic_search dispatch staged — ChromaDB query integration pending",
        }

    def _handle_reranking(self, task: LocalTask) -> dict:
        payload = task.payload or {}
        query = payload.get("query", "")
        documents = payload.get("documents", [])

        if not query or not documents:
            raise ValueError("reranking payload 缺少 query 或 documents")

        return {
            "query": query,
            "document_count": len(documents),
            "results": documents,
            "note": "reranking dispatch staged — Reranker integration pending",
        }

    def _handle_inference(self, task: LocalTask) -> dict:
        if self._ollama_chat is None:
            raise RuntimeError("OllamaChat 未初始化")

        payload = task.payload or {}
        text = payload.get("text", "")
        work_type = task.capability

        if not text:
            raise ValueError("inference payload 缺少 text")

        _log.info("LocalModelScheduler: inference %s → qwen3:8b", work_type)
        return self._ollama_chat.inference(work_type, text)

    def _cleanup_expired_results(self) -> None:
        now = time.time()
        with self._lock:
            expired = [
                tid for tid, t in self._results.items() if t.finished_at and (now - t.finished_at) > RESULT_TTL_S
            ]
            for tid in expired:
                del self._results[tid]
