---
module_id: KE-3024
status: active
title: 2.1 JSON Schema（权威）
category: session_log
ttl: permanent
---

# 2.1 JSON Schema（权威）

2.1 JSON Schema（权威）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "schemas/session-carryover-v1.schema.json",
  "title": "SessionCarryover",
  "type": "object",
  "required": ["schema_version", "session_id", "ended_at", "open_tasks"],
  "properties": {
    "schema_version": {
      "type": "string",
      "const": "1.0.0",
      "description": "Schema 版本，强制校验"
    },
    "session_id": {
      "type": "string",
      "pattern": "^sess-[0-9]{8}-[0-9]{6}-[a-f0-9]{6}$",
      "description": "Session 唯一 ID，格式：sess-YYYYMMDD-HHMMSS-<6-char hex>"
    },
    "started_at": {"type": "string", "format": "date-time"},
    "ended_at": {"type": "string", "format": "date-time"},
    "ended_reason": {
      "type": "string",
      "enum": ["normal_shutdown", "user_command", "crash", "idle_timeout", "ide_close"]
    },
    "ide_info": {
      "type": "object",
      "properties": {
        "ide_id": {"enum": ["cursor", "trae", "claude_desktop", "generic_mcp"]},
        "ide_version": {"type": "string"},
        "os": {"type": "string"}
      }
    },
    "open_tasks": {
      "type": "array",
      "items": {"$ref": "#/definitions/OpenTask"}
    },
    "blockers": {
      "type": "array",
      "items": {"$ref": "#/definitions/Blocker"}
    },
    "hallucination_events": {
      "type": "array",
      "items": {"$ref": "#/definitions/HallucinationEvent"}
    },
    "context_state": {"$ref": "#/definitions/ContextState"},
    "token_budget": {"$ref": "#/definitions/TokenBudget"},
    "artifacts_pending_review": {
      "type": "array",
      "items": {"type": "string", "description": "文件路径"}
    },
    "user_intentions": {
      "type": "array",
      "items": {"type": "string"},
      "description": "用户在 Session 中显式表达的下一步意图（从对话中抽取）"
    },
    "environment_snapshot": {"$ref": "#/definitions/EnvironmentSnapshot"}
  },

  "definitions": {
    "OpenTask": {
      "type": "object",
      "required": ["task_id", "status", "summary"],
      "properties": {
        "task_id": {"type": "string", "description": "来自 Orchestrator 的 task_id"},
        "status": {
          "type": "string",
          "enum": ["draft", "queued", "assigned", "running", "blocked", "reviewing"]
        },
        "summary": {"type": "string", "maxLength": 300},
        "files_in_scope": {"type": "array", "items": {"type": "string"}},
        "last_observation": {"type": "string", "maxLength": 500},
        "next_action_hint": {"type": "string", "maxLength": 300}
      }
    },
    "Blocker": {
      "type": "object",
      "required": ["task_id", "reason", "requires_user"],
      "properties": {
        "task_id": {"type": "string"},
        "reason": {"type": "string", "maxLength": 500},
        "requires_user": {"type": "boolean"},
        "suggested_prompt": {"type": "string", "description": "建议下次 Session 开场白"}
      }
    },
    "HallucinationEvent": {
      "type": "object",
      "required": ["event_id", "task_id", "rule_triggered", "evidence"],
      "properti
