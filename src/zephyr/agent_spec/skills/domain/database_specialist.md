---

skill_id: SKILL-DOM-DBS-001
name: database-specialist
description: "DB schema migration and ATM transaction management"
allowed-tools: [Read, Write, SearchReplace, Grep, Glob, RunCommand]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Database Specialist

## CRITICAL Rules

1. All schema changes MUST use ATM (Atomic Transaction Manager) migrations
2. Never execute raw DDL outside of migration files
3. Every migration MUST have a rollback script
4. Schema changes require G3 gate approval before execution
5. SQLite WAL mode is the default journal mode

## Core Operations

- Schema migration creation via ATM
- Migration rollback and verification
- DB integrity checks and vacuum
- Query optimization for SQLite
- Foreign key enforcement (PRAGMA foreign_keys=ON)

## Unique Constraints

- SQLite single-writer limitation: all writes serialized
- WAL mode required for concurrent read/write
- No ALTER COLUMN support: must recreate table
- Migration files stored in `data/migrations/`

## Common Error Patterns

- Missing rollback script → blocked by G3 gate
- Foreign key violation → check PRAGMA foreign_keys
- Database locked → another process holding write lock
- Schema drift → migration not applied in correct order

## Checklist

- [ ] Verify migration has corresponding rollback
- [ ] Check foreign key constraints are enabled
- [ ] Run integrity_check after migration
- [ ] Pass G3 gate validation

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DEFAULT_JOURNAL_MODE | WAL | Default SQLite journal mode |
| MIGRATION_DIR | data/migrations/ | Migration file storage |
| DB_PATH | data/zalpha_metadata.db | Primary metadata database |

## References (L3, on-demand)

- ATM migration guide
- SQLite best practices
- G3 gate specification