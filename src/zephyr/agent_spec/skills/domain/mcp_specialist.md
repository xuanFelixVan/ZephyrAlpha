---

skill_id: SKILL-DOM-MCP-001
name: mcp-specialist
description: "MCP server/tool/protocol implementation"
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


# Domain Skill: MCP Specialist

## CRITICAL Rules

1. All MCP servers MUST be registered in REG-MOD-001
2. Transport layer: stdio for local, SSE for remote
3. Every tool MUST have input schema validation
4. Rate limiting MUST be implemented per server
5. OWASP MCP Top 10 compliance required

## Core Operations

- MCP server creation and registration
- Tool definition with JSON schema
- Resource and prompt provider implementation
- Transport layer configuration (stdio/SSE)
- Server health check and monitoring

## Unique Constraints

- stdio transport: single-client only
- SSE transport: requires HTTP server lifecycle
- Tool names must be globally unique across servers
- Response size limit: 4MB per message

## Common Error Patterns

- Tool not found → check tool registration in server
- Transport mismatch → verify client/server transport config
- Schema validation failure → input does not match tool schema
- Rate limit exceeded → implement backoff strategy

## Checklist

- [ ] Register new MCP server in module registry
- [ ] Define all tools with JSON schema
- [ ] Implement rate limiting
- [ ] Add health check endpoint
- [ ] Pass OWASP MCP Top 10 audit

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| MAX_MESSAGE_SIZE | 4194304 | Max MCP message size (4MB) |
| DEFAULT_RATE_LIMIT | 100/min | Default rate limit per server |
| TRANSPORT_STDIO | stdio | Local process transport |
| TRANSPORT_SSE | sse | Remote HTTP transport |

## References (L3, on-demand)

- MCP protocol specification
- OWASP MCP Top 10
- server template guide