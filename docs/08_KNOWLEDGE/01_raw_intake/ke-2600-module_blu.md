---
module_id: KE-2505
title: 9. 已知风险与缓解
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 9. 已知风险与缓解

9. 已知风险与缓解

| # | 风险 | 概率 | 影响 | 缓解策略 |
|---|------|:---:|:---:|------|
| R1 | **stdio 阻塞风险**——当前循环在 stdin.readline() 阻塞等待，一个慢请求阻塞所有后续请求 | 确定 | 🔴高 | Phase 4 引入 asyncio 或线程池处理并发请求 |
| R2 | **无 RBAC 强制执行**——safety_level L/M/H 在 YAML 中定义但 `_handle_tools_call` 不检查 | 确定 | 🔴高 | 在工具调用入口添加 safety_level 检查，与 MOD-INF-018 对齐 |
| R3 | **契约漂移**——tool_contracts.yaml 新增/修改后代码不同步，AI 自己写的代码可能偏离契约 | 高 | 🔴高 | pre-commit hook：代码中的 input_schema 必须与 YAML 一致 |
| R4 | **session_handoff 文件命名混乱**——文件叫 doc_guard_server.py 但 server_id 是 session_handoff | 确定 | 🟡中 | AGENTS.md 中硬约束声明此差异不可"修复" |
| R5 | **intent_router 文件命名混乱**——文件叫 sentinel_server.py 但 server_id 是 intent_router | 确定 | 🟡中 | 同上 |
| R6 | **无超时机制**——tool handler 同步执行无超时，慢 handler 永久阻塞 | 确定 | 🔴高 | `asyncio.wait_for(handler(**args), timeout=30)` |
| R7 | **4 个 skeleton Server 全部 copy-paste 同一模板**——knowledge_base/gate_engine/doc_guard/sentinel 的 `__init__` 和 `run()` 完全相同 | 确定 | 🟡中 | 重构为 `@register_tool` 装饰器 + 统一模板 |
| R8 | **idempotency 缺失**——task_manager 的 create_task tool 声明 `idempotent: true` 但 code 不检查输入 hash 缓存 | 确定 | 🟡中 | 实现输入 hash 缓存 |
| R9 | **无 Observer 告警**——MCP Server 崩溃/超时/异常无任何外部通知 | 确定 | 🔴高 | 实现 healthz/readyz + Prometheus metrics |
| R10 | **测试不执行**——CI governance.yml 只 `--collect-only`，从不 `pytest -x` | 确定 | 🔴高 | CI 中改为 `pytest tests/ -x --timeout=120` |
| R11 | **Content-Length 帧解析缺失**——MCP spec 要求 Content-Length 前缀帧格式，但 `_base_server.py` 只支持逐行读取 | 确定 | 🟡中 | 实现 Content-Length header 解析逻辑 |
| R12 | **无多 session 并发安全设计（B82）**——双 IDE 同时操作同一 task 产生数据竞争 | 中 | 🟡中 | Phase 5 Gateway 引入乐观锁 + BUSY 重试 |
| R13 | **金融合规标签缺失（B66）**——`tool_contracts.yaml` 无 financial_compliance 维度 | 中 | 🟡中 | 新增 `compliance_tags: [CN-NDA, NOT_FOR_REALTIME_TRADING]` 字段 |
| R14 | **mcp>=1.0.0 未在依赖文件中声明（B67）**——pyproject.toml / requirements.txt / requirements-dev.txt 三处均缺 | 确定 | 🔴高 | 三处同步追加 `mcp>=1.0.0`（第六轮已执行） |
| R15 | **AGENTS.md 零 MCP 内容（B68）**——v4.19.0 已新增 MCP 任务菜单条目，需持续维护 | 中 | 🔴高 | AGENTS.md §8.2 任务菜单已新增 MCP 条目 |
| R16 | **全工程无 IDE MCP 配置文件（B69）**——项目根/各 IDE 目录均无 mcp.json | 确定 | 🔴高 | 创建 `config/mcp.json` SSoT → IDE 配置生成脚本 |
| R17 | **scripts/mcp/ 目录不存在（B70）**——MCP 全生命周期无标准化脚本入口 | 确定 | 🔴高 | 创建 `scripts/mcp/start_all.py` + `stop_all.py` + `status_all.py` |
| R18 | **缺少 MCP 专项共享测试基础设施（B71）**——全局 conftest.py 无 MCP fixture | 确定 | 🟡中 | 新增 `mcp_client_factory` / `tmp_chroma` / `tmp_mcp_session` fixture |
| R19 | **ChromaDB/SQLite 多进程写入安全风险（B72）**——7 个 MCP Server 共享同一持久化目录和数据库 | 中 | 🟡中 | ChromaDB 分 collection 隔离 + SQLite busy_timeout=5000ms + Gateway 串行化 |
| R20 | **无 Makefile/Taskfile（B73）**——MCP Server 高频运维操作无标准化入口 | 中 | 🟡中 | 创建 `Makefile`，收敛 ≥15 个高频操作为标准化 targets |
| R21 | **.env.example 无 MCP 环境变量（B74）**——蓝图引用变量但 .env.example 无 | 中 | 🟡中 | 追加 MCP 专节含 `ZEPHYR_MCP_LOG_LEVEL` / `ZEPHYR_MCP_DATA_DIR` / `ZEPHYR_DEBUG_MCP` |
| R22 | **docker-compose.yml 无 MCP 服务编排（B75）**——容器化部署路径为零 | 中 | 🟡中 | 新增 8 个 MCP service 定义 + Dockerfile.mcp 基础镜像 |
| R23 | **MCP SDK 版本无锁定策略（B76）**——开放范围依赖无 pinned 版本 | 低 | 🟡中 | 锁定 `mcp==1.X.Y` + dependabot/renovate + C
