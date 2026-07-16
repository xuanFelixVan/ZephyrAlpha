# [A_test] module_id: SRC-TST-2298 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] tests.db.conftest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""tests/db/ 共享 fixture — 收敛 governance.db 路径真源。

真源：zephyr.shared.io.paths.DB_PATH（SSoT）
派生：本 fixture 从 DB_PATH 派生，禁止反向修改。
"""
from __future__ import annotations

from pathlib import Path

import pytest
from zephyr.shared.io.paths import DB_PATH  # SSoT 真源


@pytest.fixture(scope="session")
def governance_db_path() -> Path:
    """返回生产 governance.db 路径（只读 E2E 测试用）。

    真源派生：zephyr.shared.io.paths.DB_PATH
    警告：仅用于只读 SELECT 测试；写入测试必须用 tmp_db fixture 隔离。
    """
    return DB_PATH
