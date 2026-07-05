# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.pagination
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-SHR_pagination | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
pagination.py —— 通用分页工具（Phase 9 新增 | 盲点 B18 修复）

痛点修复：每个消费模块都自己定义 page/limit/offset → AI 跨模块容易搞混——
  1. 有的用 offset+limit，有的用 page+page_size，有的用 cursor
  2. 分页响应格式不一致 → 前端/消费者解析一团乱

设计对标：
  - GitHub API（Link header + per_page + page）
  - Stripe API（cursor-based pagination + has_more）
  - Spring Data Page<T>（content + totalElements + totalPages）

设计原则：
  - 统一 Page[T] 和 CursorPage[T] 两种分页模型
  - Generic——适配任何数据类型
  - 零依赖——仅 Python 标准库 + typing

AI 施工约定：
  - 任何返回列表的 API MUST 使用本模块的分页类型
  - cursor-based 用于实时流数据（数据持续追加）/ offset-based 用于静态数据集

SSoT: MOD-INF-016 §2.17 shared-pagination
Version: 0.1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

__all__ = [
    "CursorPage",
    "CursorPagination",
    "OffsetPagination",
    "Page",
    "paginate",
    "paginate_cursor",
]

T = TypeVar("T")


@dataclass
class OffsetPagination:
    offset: int = 0
    limit: int = 20

    def __post_init__(self) -> None:
        if self.offset < 0:
            raise ValueError(f"offset must be >= 0, got {self.offset}")
        if self.limit < 1 or self.limit > 1000:
            raise ValueError(f"limit must be 1-1000, got {self.limit}")


@dataclass
class CursorPagination:
    cursor: str | None = None
    limit: int = 20

    def __post_init__(self) -> None:
        if self.limit < 1 or self.limit > 1000:
            raise ValueError(f"limit must be 1-1000, got {self.limit}")


@dataclass
class Page(Generic[T]):
    """基于 offset/limit 的分页响应。

    Usage::

        data = list[T](...)
        total = len(all_items)
        page = paginate(data, total, OffsetPagination(offset=0, limit=20))
        print(page.total_pages)
        print(page.has_next)
    """

    items: list[T]
    total: int
    offset: int
    limit: int

    @property
    def total_pages(self) -> int:
        if self.limit == 0:
            return 0
        return (self.total + self.limit - 1) // self.limit

    @property
    def current_page(self) -> int:
        if self.limit == 0:
            return 0
        return self.offset // self.limit + 1

    @property
    def has_next(self) -> bool:
        return self.offset + self.limit < self.total

    @property
    def has_previous(self) -> bool:
        return self.offset > 0

    @property
    def next_offset(self) -> int | None:
        if self.has_next:
            return self.offset + self.limit
        return None

    @property
    def previous_offset(self) -> int | None:
        if self.has_previous:
            return max(0, self.offset - self.limit)
        return None


@dataclass
class CursorPage(Generic[T]):
    """基于 cursor 的分页响应——适合实时数据流。

    Usage::

        page = paginate_cursor(items, total, CursorPagination(cursor="abc", limit=20))
        next_page = paginate_cursor(next_items, total, CursorPagination(cursor=page.next_cursor))
    """

    items: list[T]
    total: int
    limit: int
    next_cursor: str | None = None
    previous_cursor: str | None = None
    has_more: bool = False


def paginate(
    items: list[T],
    total: int,
    pagination: OffsetPagination,
) -> Page[T]:
    return Page(
        items=items,
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


def paginate_cursor(
    items: list[T],
    total: int,
    pagination: CursorPagination,
    *,
    next_cursor: str | None = None,
) -> CursorPage[T]:
    has_more = len(items) > pagination.limit
    displayed = items[: pagination.limit]
    return CursorPage(
        items=displayed,
        total=total,
        limit=pagination.limit,
        next_cursor=next_cursor,
        previous_cursor=pagination.cursor,
        has_more=has_more,
    )
