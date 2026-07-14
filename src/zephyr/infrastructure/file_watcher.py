# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.file_watcher
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.blueprint_decomposer; zephyr.shared.__init__
# [CONSUMERS] auto_runtime_core.py; blueprint_decomposer.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 轮询间隔>=10s; 哈希比对用MD5; 变更事件必须包含path+event_type+timestamp
# [MODIFY-GUARD] auto_runtime_core.py; blueprint_decomposer.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileWatcherError on invalid watch_dir; silent skip on permission denied
# [TESTS] tests/file/test_file_watcher.py
# [A_module] module_id=MOD-INF_file_watcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import hashlib
import importlib
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


from zephyr.shared.io.paths import REPO_ROOT
logger = logging.getLogger(__name__)

__all__: list[str] = ["FileChangeEvent", "FileChangeType", "FileWatcher"]


class FileChangeType(str, Enum):
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"


@dataclass
class FileChangeEvent:
    path: Path
    event_type: FileChangeType
    timestamp: float = field(default_factory=time.time)

    @property
    def suffix(self) -> str:
        return self.path.suffix.lower()


class FileWatcherError(Exception):
    error_code = "ZA-IF-0004"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


class FileWatcher:
    def __init__(
        self,
        watch_dir: Path,
        *,
        patterns: list[str] | None = None,
        poll_interval: float = 30.0,
        on_change: Callable[[FileChangeEvent], None] | None = None,
    ) -> None:
        if not watch_dir.is_dir():
            raise FileWatcherError(f"watch_dir does not exist: {watch_dir}")
        if poll_interval < 10.0:
            raise FileWatcherError(f"poll_interval must be >= 10s, got {poll_interval}")

        self._watch_dir = watch_dir
        self._patterns = patterns or [".md", ".yaml", ".yml", ".py"]
        self._poll_interval = poll_interval
        self._on_change = on_change
        self._snapshot: dict[Path, str] = {}
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._snapshot = self._build_snapshot()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True, name="FileWatcher")
        self._thread.start()
        self._started = True
        logger.info(
            "FileWatcher started: dir=%s patterns=%s interval=%.0fs tracked=%d",
            self._watch_dir,
            self._patterns,
            self._poll_interval,
            len(self._snapshot),
        )

    def stop(self) -> None:
        if not self._started:
            return
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self._started = False
        logger.info("FileWatcher stopped: dir=%s", self._watch_dir)

    @property
    def is_running(self) -> bool:
        return self._started and not self._stop_event.is_set()

    @property
    def tracked_count(self) -> int:
        with self._lock:
            return len(self._snapshot)

    def scan_once(self) -> list[FileChangeEvent]:
        with self._lock:
            current = self._build_snapshot()
            events = self._diff(self._snapshot, current)
            self._snapshot = current
        return events

    def _build_snapshot(self) -> dict[Path, str]:
        snapshot: dict[Path, str] = {}
        try:
            for p in self._watch_dir.rglob("*"):
                if not p.is_file():
                    continue
                if p.suffix.lower() not in self._patterns:
                    continue
                try:
                    md5 = hashlib.md5(p.read_bytes()).hexdigest()
                    snapshot[p] = md5
                except PermissionError:
                    continue
                except OSError:
                    continue
        except OSError:
            logger.warning("Failed to scan directory: %s", self._watch_dir)
        return snapshot

    def _diff(self, old: dict[Path, str], new: dict[Path, str]) -> list[FileChangeEvent]:
        events: list[FileChangeEvent] = []
        old_keys = set(old.keys())
        new_keys = set(new.keys())

        for p in new_keys - old_keys:
            events.append(FileChangeEvent(path=p, event_type=FileChangeType.CREATED))

        for p in old_keys - new_keys:
            events.append(FileChangeEvent(path=p, event_type=FileChangeType.DELETED))

        for p in old_keys & new_keys:
            if old[p] != new[p]:
                events.append(FileChangeEvent(path=p, event_type=FileChangeType.MODIFIED))

        return events

    def _poll_loop(self) -> None:
        while not self._stop_event.wait(timeout=self._poll_interval):
            try:
                events = self.scan_once()
                for event in events:
                    logger.info("File change detected: %s %s", event.event_type.value, event.path)
                    if self._on_change:
                        try:
                            self._on_change(event)
                        except Exception:
                            logger.exception("on_change callback failed for %s", event.path, exc_info=True)
            except Exception:
                logger.exception("FileWatcher poll loop error", exc_info=True)


class BlueprintWatcher:
    def __init__(
        self,
        blueprints_dir: Path | None = None,
        *,
        poll_interval: float = 60.0,
        auto_decompose: bool = True,
    ) -> None:
        if blueprints_dir is None:
            blueprints_dir = REPO_ROOT / "docs" / "03_modules"
        self._blueprints_dir = blueprints_dir
        self._auto_decompose = auto_decompose
        self._watcher = FileWatcher(
            watch_dir=blueprints_dir,
            patterns=[".md"],
            poll_interval=poll_interval,
            on_change=self._on_blueprint_change,
        )

    def start(self) -> None:
        self._watcher.start()

    def stop(self) -> None:
        self._watcher.stop()

    @property
    def is_running(self) -> bool:
        return self._watcher.is_running

    def _on_blueprint_change(self, event: FileChangeEvent) -> None:
        if event.suffix != ".md":
            return
        if event.event_type is FileChangeType.DELETED:
            return
        if not self._is_blueprint(event.path):
            return
        logger.info("Blueprint change detected: %s %s", event.event_type.value, event.path)
        if self._auto_decompose:
            self._trigger_decompose(event.path)
        self._trigger_triple_alignment(event.path)

    @staticmethod
    def _is_blueprint(path: Path) -> bool:
        try:
            with open(path, encoding="utf-8") as f:
                head = f.read(500)
            return "module_id:" in head and "blueprint" in head.lower()
        except Exception:
            return False

    @staticmethod
    def _trigger_decompose(blueprint_path: Path) -> None:
        try:
            from zephyr.shared.protocols.registry import ServiceRegistry
            from zephyr.shared.blueprint_tools.blueprint_decomposer import BlueprintDecomposer

            task_repo = ServiceRegistry.get("task_repo")
            decomposer = BlueprintDecomposer(task_repo=task_repo)
            result = decomposer.decompose_blueprint(str(blueprint_path))
            logger.info(
                "Auto-decompose completed: %s -> %d tasks",
                blueprint_path.name,
                len(result.tasks) if hasattr(result, "tasks") else 0,
            )
        except Exception:
            logger.exception("Auto-decompose failed for %s", blueprint_path, exc_info=True)

    @staticmethod
    def _trigger_triple_alignment(blueprint_path: Path) -> None:
        try:
            import re

            _mod = importlib.import_module("zephyr.gov_enforcement.rule_enforcement.triple_alignment")
            check_triple_alignment = _mod.check_triple_alignment
            content = blueprint_path.read_text(encoding="utf-8")
            mid_match = re.search(r"module_id:\s*(MOD-INF-\d+|MOD-MASTER-\d+|DOM-\w+-\d+|GOV-FSTR-\d+)", content)
            if not mid_match:
                return
            module_id = mid_match.group(1)
            result = check_triple_alignment(specific_module=module_id, warn_only=False)
            if not result.passed:
                errors = [v for v in result.violations if v.severity.value == "ERROR"]
                logger.error("G-TRIPLE-ALIGN FAILED for %s: %d violations", module_id, len(errors))
            else:
                logger.info("G-TRIPLE-ALIGN PASSED for %s", module_id)
        except Exception:
            logger.exception("G-TRIPLE-ALIGN check failed for %s", blueprint_path, exc_info=True)