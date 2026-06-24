"""GitCommitGateway全项目唯一合法git commit入口，全局串行锁+选择性stash+受限commit，根治幽灵提交"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

__all__: list[str] = ["GitCommitGateway"]


class GitCommitGateway:
    """Git Commit Gateway 占位类——全项目唯一合法 git commit 入口。

    完整实现待后续补全（全局串行锁+选择性stash+受限commit）。
    当前仅提供占位以通过 zephyr.governance.__init__ 的 import。
    """

    def __init__(self, project_root=None) -> None:
        self._project_root = project_root

    def commit(self, message: str, files: list[str] | None = None) -> bool:
        """占位 commit 方法。"""
        logger.warning("GitCommitGateway.commit: 占位实现，未实际执行")
        return False


def main() -> None:
    """入口——待实现。"""
    pass


if __name__ == "__main__":
    main()
