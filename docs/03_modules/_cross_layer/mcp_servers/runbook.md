---
blueprint_id: DOM-GOV-001
title: Runbook
module_id: MOD-011---

# MCP Runbook

> 运维操作手册 — MOD-INF-013 Phase 8 (8 incident scenarios)

## Incident Scenarios

### S1: Server OOM — P0
- **Severity**: P0 (Critical)
- **Symptom**: MCP Server process exits, OS kill signal, `out of memory` in logs
- **Diagnostic**: `python scripts/mcp/status_all.py` → check process RSS via `ps aux`
- **Response**:
  1. `python scripts/mcp/launcher.py` → restart server
  2. Check `logs/mcp_audit/tools_call.jsonl` for memory-intensive queries
  3. Add `max_result_size` limit if needed
- **Rollback**: reduce tool result cap → restart

### S2: ChromaDB Unreachable — P1
- **Severity**: P1 (High)
- **Symptom**: knowledge_base.search returns connection error
- **Diagnostic**: `curl http://localhost:8000/api/v1/heartbeat`
- **Response**:
  1. Check if ChromaDB process running: `pgrep chroma`
  2. Restart: `chroma run --path ./data/chromadb`
  3. After recovery: `knowledge_base.rebuild_index` to reindex
- **Rollback**: KB falls back to SQLite-only mode (search disabled)

### S3: SQLite Locked — P1
- **Severity**: P1 (High)
- **Symptom**: task_manager create/update returns `database is locked`
- **Diagnostic**: `lsof | grep data/databases/governance.db` → check writer count
- **Response**:
  1. Wait 5s → retry (WAL mode auto-recovery)
  2. If persists: kill stale writer → restart task_manager
- **Rollback**: restore from `data/databases/governance.db-wal` checkpoint

### S4: Stdin Hang — P1
- **Severity**: P1 (High)
- **Symptom**: AI agent timeout, no response from MCP
- **Diagnostic**: `echo '{"jsonrpc":"2.0","id":1,"method":"ping"}' | python -m zephyr.mcp.knowledge_base_server`
- **Response**:
  1. Check parent process STDIN state
  2. Kill and restart server via launcher
- **Rollback**: gateway degrades away from hung server

### S5: OLLAMA Timeout — P2
- **Severity**: P2 (Medium)
- **Symptom**: embedding generation hangs, search returns degraded results
- **Diagnostic**: `ollama list` → check model availability
- **Response**:
  1. Restart Ollama: `ollama serve`
  2. Pull model if missing
- **Rollback**: keyword-only search fallback (no vector)

### S6: Tool Registration Drift — P1
- **Severity**: P1 (High)
- **Symptom**: `tools/list` returns different count than expected
- **Diagnostic**: `python scripts/governance/validate_tool_contracts_consistency.py`
- **Response**:
  1. Compare `tool_contracts.yaml` vs `register_tool` calls
  2. Sync mismatch → restart affected server
- **Rollback**: `git checkout -- src/zephyr/mcp/tool-contracts.yaml`

### S7: Memory Leak — P1
- **Severity**: P1 (High)
- **Symptom**: RSS grows monotonically over 8h soak test
- **Diagnostic**: `tracemalloc` snapshot comparison at startup vs +8h
- **Response**:
  1. Identify leaking object via `tracemalloc`
  2. Add TTL cache cleanup / LRU eviction
  3. Restart server to reset
- **Rollback**: deploy fix → restart

### S8: Gateway Circuit Breaker Open — P0
- **Severity**: P0 (Critical)
- **Symptom**: All tools from a downstream server return -32003
- **Diagnostic**: `mcp_gateway.health_status` → check circuit_breakers state
- **Response**:
  1. Verify downstream server status
  2. If healthy → wait 30s for auto-recovery (HALF_OPEN)
  3. If unhealthy → fix root cause → CB auto-closes
- **Rollback**: restart gateway → CB state reset

## Severity Classification

| Level | Response Time | Example |
|-------|:---:|---------|
| P0 | <5 min | Server OOM, Gateway CB open |
| P1 | <30 min | DB unreachable, SQLite lock, memory leak |
| P2 | <2h | Model timeout, config drift |
