"""
lazy_loader.py - Lazy module loading registry
==============================================

SSoT: MOD-INF-032 resource-optimization-engine/blueprint.md §7.3

Design:
  - Register modules with import paths and metadata
  - Load on first access via importlib.import_module()
  - Core modules list: loaded at startup
  - Non-core modules: loaded on demand
  - Track which modules are loaded and their load times
"""

from __future__ import annotations

import importlib
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Optional

__all__ = ["LazyModuleRegistry", "ModuleEntry"]

logger = logging.getLogger(__name__)


@dataclass
class ModuleEntry:
    name: str
    import_path: str
    is_core: bool = False
    loaded: bool = False
    module: Any = None
    load_time_s: float = 0.0
    loaded_at: float = 0.0


class LazyModuleRegistry:
    def __init__(self, core_modules: list[str] | None = None) -> None:
        self._entries: dict[str, ModuleEntry] = {}
        self._core_modules = set(core_modules or [])
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        import_path: str,
        is_core: bool = False,
    ) -> None:
        with self._lock:
            self._entries[name] = ModuleEntry(
                name=name,
                import_path=import_path,
                is_core=is_core or name in self._core_modules,
            )

    def load(self, name: str) -> Any:
        with self._lock:
            entry = self._entries.get(name)
            if entry is None:
                raise KeyError(f"module '{name}' not registered")
            if entry.loaded:
                return entry.module

        start = time.monotonic()
        try:
            module = importlib.import_module(entry.import_path)
        except Exception:
            logger.exception("LazyModuleRegistry: failed to load '%s' from '%s'", name, entry.import_path)
            raise
        elapsed = time.monotonic() - start

        with self._lock:
            entry.loaded = True
            entry.module = module
            entry.load_time_s = round(elapsed, 3)
            entry.loaded_at = time.monotonic()

        logger.info(
            "LazyModuleRegistry: loaded '%s' from '%s' in %.3fs",
            name, entry.import_path, elapsed,
        )
        return module

    def is_loaded(self, name: str) -> bool:
        with self._lock:
            entry = self._entries.get(name)
            return entry is not None and entry.loaded

    def is_registered(self, name: str) -> bool:
        return name in self._entries

    def get(self, name: str) -> Any:
        with self._lock:
            entry = self._entries.get(name)
            if entry is None:
                raise KeyError(f"module '{name}' not registered")
            if not entry.loaded:
                raise RuntimeError(f"module '{name}' not yet loaded — call load() first")
            return entry.module

    def load_core_modules(self) -> int:
        loaded = 0
        for name, entry in list(self._entries.items()):
            if entry.is_core and not entry.loaded:
                try:
                    self.load(name)
                    loaded += 1
                except Exception:
                    logger.warning("LazyModuleRegistry: core module '%s' failed to load", name)
        return loaded

    def unload(self, name: str) -> bool:
        with self._lock:
            entry = self._entries.get(name)
            if entry is None or not entry.loaded:
                return False
            entry.loaded = False
            entry.module = None
            entry.load_time_s = 0.0
            return True

    def list_entries(self) -> list[ModuleEntry]:
        with self._lock:
            return list(self._entries.values())

    def stats(self) -> dict[str, Any]:
        with self._lock:
            total = len(self._entries)
            loaded = sum(1 for e in self._entries.values() if e.loaded)
            core = sum(1 for e in self._entries.values() if e.is_core)
            return {
                "total_registered": total,
                "total_loaded": loaded,
                "core_modules": core,
                "lazy_modules": total - core,
                "pending": total - loaded,
            }
