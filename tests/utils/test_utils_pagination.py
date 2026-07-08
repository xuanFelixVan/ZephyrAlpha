# [A_test] module_id: SRC-TST-1775 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_utils_pagination

# [INVARIANTS] OffsetPagination验证offset>=0/limit1-1000;Page计算属性一致

# [MODIFY-GUARD] pagination.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] ValueError on invalid offset/limit

# [TESTS] pytest tests/test_utils_pagination.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.utils.pagination import (
    CursorPage,
    CursorPagination,
    OffsetPagination,
    Page,
    paginate,
    paginate_cursor,
)


class TestOffsetPagination:
    def test_defaults(self):
        p = OffsetPagination()
        assert p.offset == 0
        assert p.limit == 20

    def test_valid_values(self):
        p = OffsetPagination(offset=10, limit=50)
        assert p.offset == 10
        assert p.limit == 50

    def test_negative_offset_raises(self):
        with pytest.raises(ValueError, match="offset"):
            OffsetPagination(offset=-1)

    def test_zero_limit_raises(self):
        with pytest.raises(ValueError, match="limit"):
            OffsetPagination(limit=0)

    def test_limit_above_1000_raises(self):
        with pytest.raises(ValueError, match="limit"):
            OffsetPagination(limit=1001)

    def test_limit_boundary_1(self):
        p = OffsetPagination(limit=1)
        assert p.limit == 1

    def test_limit_boundary_1000(self):
        p = OffsetPagination(limit=1000)
        assert p.limit == 1000


class TestCursorPagination:
    def test_defaults(self):
        p = CursorPagination()
        assert p.cursor is None
        assert p.limit == 20

    def test_with_cursor(self):
        p = CursorPagination(cursor="abc123", limit=10)
        assert p.cursor == "abc123"
        assert p.limit == 10

    def test_invalid_limit_raises(self):
        with pytest.raises(ValueError, match="limit"):
            CursorPagination(limit=0)

    def test_limit_above_1000_raises(self):
        with pytest.raises(ValueError, match="limit"):
            CursorPagination(limit=1001)


class TestPage:
    def test_total_pages(self):
        page = Page(items=[1, 2, 3], total=25, offset=0, limit=10)
        assert page.total_pages == 3

    def test_total_pages_exact(self):
        page = Page(items=[1, 2], total=20, offset=0, limit=10)
        assert page.total_pages == 2

    def test_current_page(self):
        page = Page(items=[], total=50, offset=20, limit=10)
        assert page.current_page == 3

    def test_has_next_true(self):
        page = Page(items=[1], total=20, offset=0, limit=10)
        assert page.has_next is True

    def test_has_next_false(self):
        page = Page(items=[1], total=10, offset=0, limit=10)
        assert page.has_next is False

    def test_has_previous_true(self):
        page = Page(items=[1], total=30, offset=10, limit=10)
        assert page.has_previous is True

    def test_has_previous_false(self):
        page = Page(items=[1], total=30, offset=0, limit=10)
        assert page.has_previous is False

    def test_next_offset(self):
        page = Page(items=[1], total=30, offset=0, limit=10)
        assert page.next_offset == 10

    def test_next_offset_none(self):
        page = Page(items=[1], total=10, offset=0, limit=10)
        assert page.next_offset is None

    def test_previous_offset(self):
        page = Page(items=[1], total=30, offset=20, limit=10)
        assert page.previous_offset == 10

    def test_previous_offset_none(self):
        page = Page(items=[1], total=30, offset=0, limit=10)
        assert page.previous_offset is None

    def test_zero_limit_total_pages(self):
        page = Page(items=[], total=0, offset=0, limit=0)
        assert page.total_pages == 0


class TestCursorPage:
    def test_defaults(self):
        page = CursorPage(items=[1], total=10, limit=5)
        assert page.next_cursor is None
        assert page.previous_cursor is None
        assert page.has_more is False

    def test_with_cursors(self):
        page = CursorPage(
            items=[1, 2],
            total=10,
            limit=5,
            next_cursor="next_abc",
            previous_cursor="prev_xyz",
            has_more=True,
        )
        assert page.next_cursor == "next_abc"
        assert page.previous_cursor == "prev_xyz"
        assert page.has_more is True


class TestPaginate:
    def test_creates_page(self):
        items = [1, 2, 3]
        p = paginate(items, total=100, pagination=OffsetPagination(offset=0, limit=10))
        assert p.items == items
        assert p.total == 100
        assert p.offset == 0
        assert p.limit == 10


class TestPaginateCursor:
    def test_truncates_to_limit(self):
        items = list(range(15))
        p = paginate_cursor(items, total=100, pagination=CursorPagination(limit=10))
        assert len(p.items) == 10
        assert p.has_more is True

    def test_within_limit_no_truncation(self):
        items = [1, 2, 3]
        p = paginate_cursor(items, total=3, pagination=CursorPagination(limit=10))
        assert len(p.items) == 3
        assert p.has_more is False

    def test_with_next_cursor(self):
        items = [1, 2]
        p = paginate_cursor(
            items,
            total=10,
            pagination=CursorPagination(cursor="abc", limit=10),
            next_cursor="def",
        )
        assert p.next_cursor == "def"
        assert p.previous_cursor == "abc"
