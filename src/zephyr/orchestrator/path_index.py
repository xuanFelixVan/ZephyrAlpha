"""文件路径索引（Path Index）——Module→__init__.py→蓝图→任务卡→配置的完整映射。"""

from __future__ import annotations

PATH_INDEX: dict[str, list[str]] = {}

class PathIndex:
    def lookup(self, module: str) -> list[str]:
        return PATH_INDEX.get(module, [])

    def register(self, module: str, paths: list[str]) -> None:
        PATH_INDEX[module] = paths
