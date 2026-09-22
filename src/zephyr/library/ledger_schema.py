# [BLUEPRINT] MOD-LIB-001 | docs/03_modules/_domain_library/blueprint.md | §1
# [MODULE] zephyr.library.ledger_schema
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] (stdlib only)
# [CONSUMERS] zephyr.library.registry; zephyr.library.lookup; zephyr.library.collectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 仅 DDL 常量与纯函数，零 IO 零时钟；SQL MUST 模块级常量（NO-BARE-SQL）；字段冻结 v1.0（08 字段词典），新增列=增枝制
# [MODIFY-GUARD] gate_id 不适用（非 gate）；变更走 08 §6 增枝制
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯函数仅对非法参数抛 ValueError
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-LIB-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ledger_schema.py — 总账 DDL 常量与身份派生纯函数（MOD-LIB-001）。

字段真源：docs/_working/ultimate_library/08_field_dictionary_v0_1.md（冻结 v1.0）。
表前缀 ``lib_``，承载于 PG 资产总线（depgraph 库共生）。
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/ledger_schema.yaml
"""

from __future__ import annotations

from typing import Final

ASSET_KINDS: Final[frozenset[str]] = frozenset(
    {
        "module",
        "file",
        "table",
        "registry",
        "doc",
        "task",
        "mcp_tool",
        "backup",
        "pipeline_node",
        "factor_strategy",
        "prompt_agent",
        "infra",
    }
)

STATUSES: Final[frozenset[str]] = frozenset({"active", "stale", "orphan", "archived", "deceased", "ghost", "blind"})

ACTIONS: Final[frozenset[str]] = frozenset({"register", "read", "update", "move", "delete", "audit"})

_ACTIONS_REQUIRING_AUTHORITY: Final[frozenset[str]] = frozenset({"delete"})

_KIND_PREFIX: Final[dict[str, str]] = {
    "module": "MOD",
    "file": "FILE",
    "table": "TBL",
    "registry": "REG",
    "doc": "DOC",
    "task": "TASK",
    "mcp_tool": "TOOL",
    "backup": "BAK",
    "pipeline_node": "PIPE",
    "factor_strategy": "FCT",
    "prompt_agent": "PRA",
    "infra": "INF",
}

_SQL_ENSURE_ASSETS = """
CREATE TABLE IF NOT EXISTS lib_assets (
  asset_id text PRIMARY KEY,
  kind text NOT NULL,
  home text NOT NULL,
  family_id text,
  fingerprint_sha256 text,
  fingerprint_aux jsonb,
  built_at timestamptz NOT NULL DEFAULT now(),
  generation integer NOT NULL DEFAULT 1,
  status text NOT NULL DEFAULT 'active',
  owner_domain text,
  retention_class text NOT NULL DEFAULT 'long',
  disposition_authority text,
  registered_at timestamptz NOT NULL DEFAULT now(),
  registered_by text,
  title text,
  one_liner text,
  ai_contract text,
  tags text[] NOT NULL DEFAULT '{}',
  ext jsonb NOT NULL DEFAULT '{}'
);
"""

_SQL_ENSURE_EVENTS = """
CREATE TABLE IF NOT EXISTS lib_events (
  event_id bigserial PRIMARY KEY,
  asset_id text NOT NULL,
  action text NOT NULL,
  actor text,
  gate_passed boolean NOT NULL DEFAULT true,
  ts timestamptz NOT NULL DEFAULT now(),
  detail jsonb NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS lib_events_asset_idx ON lib_events (asset_id);
"""

_SQL_UPSERT_ASSET = """
INSERT INTO lib_assets (
  asset_id, kind, home, fingerprint_sha256, fingerprint_aux, status,
  owner_domain, retention_class, title, ai_contract, tags, registered_by
) VALUES (
  %s, %s, %s, %s, %s::jsonb, COALESCE(%s, 'active'),
  %s, %s, %s, %s, %s::text[], %s
)
ON CONFLICT (asset_id) DO UPDATE SET
  kind = EXCLUDED.kind,
  home = EXCLUDED.home,
  fingerprint_sha256 = COALESCE(EXCLUDED.fingerprint_sha256, lib_assets.fingerprint_sha256),
  fingerprint_aux = COALESCE(EXCLUDED.fingerprint_aux, lib_assets.fingerprint_aux),
  built_at = now(),
  generation = lib_assets.generation + 1,
  status = EXCLUDED.status,
  title = COALESCE(EXCLUDED.title, lib_assets.title),
  ai_contract = COALESCE(EXCLUDED.ai_contract, lib_assets.ai_contract),
  tags = EXCLUDED.tags
"""

_SQL_MARK_DECEASED = """
UPDATE lib_assets SET status = 'deceased', disposition_authority = %s
WHERE asset_id = %s
"""

_SQL_INSERT_EVENT = """
INSERT INTO lib_events (asset_id, action, actor, gate_passed, detail)
VALUES (%s, %s, %s, %s, %s::jsonb)
"""

_SQL_LOOKUP = """
SELECT asset_id, kind, home, status, title, built_at
FROM lib_assets
WHERE asset_id ILIKE %s OR home ILIKE %s OR title ILIKE %s
ORDER BY asset_id
LIMIT %s
"""

# 组合过滤子句（T5 两轴过滤器；全部模块级常量，NO-BARE-SQL——由 Librarian.lookup 按
# 传入过滤器拼接在 _SQL_LOOKUP 的 WHERE 之后；limit 占位符由 _SQL_LOOKUP 自带时不可
# 拼接，故过滤态改用 _SQL_LOOKUP_COMPOSED 基座）
_SQL_LOOKUP_COMPOSED: Final[str] = """
SELECT asset_id, kind, home, status, title, built_at
FROM lib_assets
WHERE (asset_id ILIKE %s OR home ILIKE %s OR title ILIKE %s)
"""
_SQL_LOOKUP_FILTER_KIND: Final[str] = " AND kind = %s"
_SQL_LOOKUP_FILTER_OWNER: Final[str] = " AND owner_domain = %s"
_SQL_LOOKUP_FILTER_STATUS: Final[str] = " AND status = %s"
_SQL_LOOKUP_FILTER_TAG: Final[str] = " AND %s = ANY(tags)"
_SQL_LOOKUP_FILTER_HOME_PREFIX: Final[str] = " AND home LIKE %s"
_SQL_LOOKUP_TAIL: Final[str] = " ORDER BY asset_id LIMIT %s"


def _has_call_number(content: str) -> bool:
    """检查文件头部 30 行是否含索书号（asset_id 键或 # asset: 注释）。

    Args:
        content: 文件全文。

    Returns:
        True=有索书号。
    """
    for line in content.splitlines()[:30]:
        stripped = line.strip()
        if stripped.startswith("asset_id:") or stripped.startswith("# asset:"):
            return True
    return False


def derive_asset_id(kind: str, home: str) -> str:
    """由 kind+home 派生稳定 asset_id（纯函数；永不复用纪律由登记层保证）。

    Args:
        kind: ASSET_KINDS 之一。
        home: 物理定位（路径/表名/任务名），统一正斜杠。

    Returns:
        ``PREFIX:home`` 形式的稳定 ID。

    Raises:
        ValueError: kind 不在 ASSET_KINDS 或 home 为空。
    """
    if kind not in ASSET_KINDS:
        raise ValueError(f"unknown kind: {kind}")
    if not home:
        raise ValueError("home must be non-empty")
    prefix = _KIND_PREFIX[kind]
    return f"{prefix}:{home.replace(chr(92), '/')}"


def validate_action(action: str, authority: str | None) -> None:
    """校验动作合法性；delete 必须携带处置预授权（注销权，08 §3.1）。

    Args:
        action: ACTIONS 之一。
        authority: 处置预授权批件号（delete 时必填）。

    Raises:
        ValueError: 未知动作，或 delete 无 authority。

    """
    if action not in ACTIONS:
        raise ValueError(f"unknown action: {action}")
    if action in _ACTIONS_REQUIRING_AUTHORITY and not (authority or "").strip():
        raise ValueError("注销权：delete 必须携带处置预授权 authority（08 §3.1 死亡证明）")
