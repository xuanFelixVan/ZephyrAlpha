---
module_id: KE-835--------------n-02-005
status: active
title: 2.8 技术栈专有名词版本白名单（N-02 豁免）
category: governance
---

# 2.8 技术栈专有名词版本白名单（N-02 豁免）

2.8 技术栈专有名词版本白名单（N-02 豁免）

业界存在大量"技术产品真实版本号"的文件名需求（如 `pydantic-v2` 结构化契约对比 `pydantic-v1`，`python-v3` 迁移指南等）。这类命名语义核心是**产品版本差异**而非作者迭代，应豁免。

**豁免机制**：文件名（小写后）**包含**以下任一 token 时，N-02 不触发：

| Token | 示例 |
|---|---|
| `pydantic-v` | `adr-0040-pydantic-v2-structured-contracts.md` |
| `python-v` / `node-v` / `go-v` / `rust-v` | 语言版本迁移文档 |
| `numpy-v` / `pandas-v` | 数据栈版本对比 |
| `postgres-v` / `mysql-v` / `sqlite-v` / `redis-v` | 数据库版本 |
| `django-v` / `flask-v` / `fastapi-v` | Python Web 框架版本 |
| `typescript-v` / `react-v` / `vue-v` / `next-v` | 前端栈版本 |
| `kubernetes-v` / `docker-v` / `terraform-v` / `ansible-v` | 基础设施版本 |
| `http-v` / `tls-v` / `oauth-v` | 协议版本 |

完整清单维护在 `scripts/governance/check_naming_convention.py::TECH_VERSION_TOKENS`，新增产品需同步更新两处（本文件 + 脚本常量）。

**非豁免判定**（必须整改）：`round1` / `iteration2` / `-v1-draft` / `-v2-final` 等作者草稿迭代式版本后缀**一律不豁免**，必须改用 frontmatter `version` 字段。

---
