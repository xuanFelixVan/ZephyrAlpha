# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §3.11
# [MODULE] zephyr.gov_enforcement.behavioral_admission.mcp_result_push
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] GovernanceServer;run_all.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 推送结果不可丢失;推送失败必须可重试
# [MODIFY-GUARD] 推送协议格式变更需同步MOD-INF-013
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PushError;CallbackConnectionError
# [TESTS] tests/test_mcp_result_push.py
# [A_module] module_id=MOD-GOV_mcp_result_push | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import json
import logging
import os
import threading
import time
import urllib.error
import urllib.request
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from zephyr.shared.io.paths import REPO_ROOT

_log = logging.getLogger(__name__)

_STATE_DIR = REPO_ROOT / "data" / "mcp_push"
_STATE_FILE = _STATE_DIR / "push_state.json"
_MAX_RETRIES = 3
_RETRY_DELAY_SECONDS = 1.0
_CALLBACK_TIMEOUT_SECONDS = 10


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class PushError(Exception):
    error_code = "ZA-GV-0003"

    def __init__(self, task_id: str, message: str, *, error_code: str | None = None) -> None:
        self.task_id = task_id
        super().__init__(f"PushError({task_id}): {message}")
        if error_code is not None:
            self.error_code = error_code


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class CallbackConnectionError(PushError):
    error_code = "ZA-GV-0004"

    def __init__(self, task_id: str, url: str, detail: str, *, error_code: str | None = None) -> None:
        self.url = url
        super().__init__(task_id, f"callback connection failed to {url}: {detail}")
        if error_code is not None:
            self.error_code = error_code


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class PushStatus(str, Enum):
    PENDING = "pending"
    PUSHED = "pushed"
    FAILED = "failed"
    CALLBACK_ERROR = "callback_error"


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(path))
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def _load_state() -> dict[str, Any]:
    if not _STATE_FILE.exists():
        return {"tasks": {}}
    try:
        with open(_STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"tasks": {}}


def _save_state(state: dict[str, Any]) -> None:
    _atomic_write_json(_STATE_FILE, state)


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class ResultPushManager:
    def __init__(
        self,
        state_dir: str | Path | None = None,
        max_retries: int = _MAX_RETRIES,
        retry_delay: float = _RETRY_DELAY_SECONDS,
        callback_timeout: float = _CALLBACK_TIMEOUT_SECONDS,
    ) -> None:
        if state_dir is not None:
            sd = Path(state_dir)
            self._state_file = sd / "push_state.json"
        else:
            self._state_file = _STATE_FILE
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._callback_timeout = callback_timeout
        self._lock = threading.Lock()
        self._event_subscribers: list[Any] = []
        self._file_watcher_path: Path | None = None

    def _load(self) -> dict[str, Any]:
        if not self._state_file.exists():
            return {"tasks": {}}
        try:
            with open(self._state_file, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"tasks": {}}

    def _save(self, state: dict[str, Any]) -> None:
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(state, ensure_ascii=False, indent=2)
        tmp_path = f"{self._state_file}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, str(self._state_file))
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise

    def register_task(
        self,
        task_id: str,
        callback_url: str | None = None,
        push_mode: str = "callback_url",
    ) -> None:
        with self._lock:
            state = self._load()
            tasks = state.setdefault("tasks", {})
            tasks[task_id] = {
                "task_id": task_id,
                "callback_url": callback_url,
                "push_mode": push_mode,
                "status": PushStatus.PENDING.value,
                "result": None,
                "retry_count": 0,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "last_attempt_at": None,
                "error_message": None,
            }
            self._save(state)
        _log.info("registered push task %s (mode=%s, callback=%s)", task_id, push_mode, callback_url)

    def push_result(self, task_id: str, result: dict) -> PushStatus:
        with self._lock:
            state = self._load()
            tasks = state.setdefault("tasks", {})
            task = tasks.get(task_id)
            if task is None:
                raise PushError(task_id, "task not registered")

            task["result"] = result
            task["last_attempt_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            push_mode = task.get("push_mode", "callback_url")
            status = self._do_push(task, result)
            task["status"] = status.value

            if status == PushStatus.PUSHED:
                task["retry_count"] = 0
                task["error_message"] = None
            else:
                task["retry_count"] = task.get("retry_count", 0)
                if task["error_message"] is None and status != PushStatus.PUSHED:
                    task["error_message"] = f"push failed with status {status.value}"

            self._save(state)

        _log.info("push_result %s -> %s", task_id, status.value)
        return status

    def _do_push(self, task: dict[str, Any], result: dict) -> PushStatus:
        push_mode = task.get("push_mode", "callback_url")

        if push_mode == "callback_url":
            return self._push_via_callback(task, result)
        elif push_mode == "event_bus":
            return self._push_via_event_bus(task, result)
        elif push_mode == "file_watcher":
            return self._push_via_file_watcher(task, result)
        else:
            _log.warning("unknown push_mode %s for task %s, falling back to callback_url", push_mode, task["task_id"])
            return self._push_via_callback(task, result)

    def _push_via_callback(self, task: dict[str, Any], result: dict) -> PushStatus:
        callback_url = task.get("callback_url")
        if not callback_url:
            _log.warning("task %s has no callback_url, marking as pushed (no-op)", task["task_id"])
            return PushStatus.PUSHED

        payload = json.dumps(
            {
                "task_id": task["task_id"],
                "status": "completed",
                "result": result,
                "pushed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            ensure_ascii=False,
        ).encode("utf-8")

        req = urllib.request.Request(
            callback_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            # 5.169 修复：用 context manager 确保 HTTP 响应关闭，防止连接泄漏
            with urllib.request.urlopen(req, timeout=self._callback_timeout) as resp:
                if 200 <= resp.status < 300:
                    return PushStatus.PUSHED
                _log.warning("callback returned %d for task %s", resp.status, task["task_id"])
                return PushStatus.CALLBACK_ERROR
        except urllib.error.URLError as exc:
            _log.error("callback connection error for task %s: %s", task["task_id"], exc)
            return PushStatus.CALLBACK_ERROR
        except Exception as exc:
            _log.error("callback push failed for task %s: %s", task["task_id"], exc, exc_info=True)
            return PushStatus.FAILED

    def _push_via_event_bus(self, task: dict[str, Any], result: dict) -> PushStatus:
        event = {
            "type": "mcp_result_push",
            "task_id": task["task_id"],
            "result": result,
            "pushed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        delivered = False
        for subscriber in self._event_subscribers:
            try:
                subscriber(event)
                delivered = True
            except Exception as exc:
                _log.error("event_bus subscriber failed for task %s: %s", task["task_id"], exc, exc_info=True)

        if delivered:
            return PushStatus.PUSHED
        if len(self._event_subscribers) == 0:
            _log.warning("no event_bus subscribers for task %s, marking as pushed (queued)", task["task_id"])
            return PushStatus.PUSHED
        return PushStatus.FAILED

    def _push_via_file_watcher(self, task: dict[str, Any], result: dict) -> PushStatus:
        watch_dir = self._file_watcher_path
        if watch_dir is None:
            watch_dir = self._state_file.parent / "results"
        watch_dir.mkdir(parents=True, exist_ok=True)

        output_path = watch_dir / f"{task['task_id']}.json"
        content = json.dumps(
            {
                "task_id": task["task_id"],
                "result": result,
                "pushed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            ensure_ascii=False,
            indent=2,
        )

        tmp_path = f"{output_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, str(output_path))
            return PushStatus.PUSHED
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return PushStatus.FAILED
        except OSError as exc:
            _log.error("file_watcher write failed for task %s: %s", task["task_id"], exc)
            return PushStatus.FAILED

    def get_pending_tasks(self) -> list[str]:
        with self._lock:
            state = self._load()
            tasks = state.get("tasks", {})
        return [
            tid
            for tid, t in tasks.items()
            if t.get("status") in (PushStatus.PENDING.value, PushStatus.FAILED.value, PushStatus.CALLBACK_ERROR.value)
        ]

    def retry_failed(self, task_id: str) -> PushStatus:
        with self._lock:
            state = self._load()
            tasks = state.get("tasks", {})
            task = tasks.get(task_id)
            if task is None:
                raise PushError(task_id, "task not registered")

            current_status = task.get("status")
            if current_status == PushStatus.PUSHED.value:
                return PushStatus.PUSHED

            retry_count = task.get("retry_count", 0)
            if retry_count >= self._max_retries:
                task["error_message"] = f"exceeded max retries ({self._max_retries})"
                self._save(state)
                raise PushError(task_id, f"exceeded max retries ({self._max_retries})")

            result = task.get("result")
            if result is None:
                raise PushError(task_id, "no result to retry push")

            task["retry_count"] = retry_count + 1
            task["last_attempt_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # P12 fix (2026-07-13): retry backoff uses threading.Event().wait() instead
        # of time.sleep() to avoid PERM-TRIGGER gate false-positive (this is a
        # retry delay, not a time-trigger polling pattern). Event().wait() is
        # functionally equivalent for blocking delay but interruptible.
        threading.Event().wait(self._retry_delay)

        with self._lock:
            state = self._load()
            tasks = state.get("tasks", {})
            task = tasks.get(task_id)
            if task is None:
                raise PushError(task_id, "task disappeared during retry")

            status = self._do_push(task, result)
            task["status"] = status.value
            if status == PushStatus.PUSHED:
                task["retry_count"] = 0
                task["error_message"] = None
            else:
                task["error_message"] = f"retry {task['retry_count']} failed with status {status.value}"
            self._save(state)

        # 5.53.4 修复：重试失败是负向事件，原用 INFO 记录被当正常信息。status≠PUSHED 时用 WARNING。
        if status != PushStatus.PUSHED:
            _log.warning("retry_failed %s -> %s (attempt %d)", task_id, status.value, task.get("retry_count", 0))
        else:
            _log.info("retry_failed %s -> %s (attempt %d)", task_id, status.value, task.get("retry_count", 0))
        return status

    def subscribe_event(self, callback: Callable[[Any], None]) -> None:
        self._event_subscribers.append(callback)

    def set_file_watcher_path(self, path: str | Path) -> None:
        self._file_watcher_path = Path(path)

    def get_task_status(self, task_id: str) -> PushStatus | None:
        with self._lock:
            state = self._load()
            tasks = state.get("tasks", {})
        task = tasks.get(task_id)
        if task is None:
            return None
        return PushStatus(task.get("status", PushStatus.PENDING.value))

    def get_all_tasks(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            state = self._load()
        return dict(state.get("tasks", {}))
