---
module_id: KE-4318---------sql--i-002
title: DB-025-0053：AP1 防护——禁止手动SQL文件init
category: module_blueprint
ttl: permanent
---

# DB-025-0053：AP1 防护——禁止手动SQL文件init

DB-025-0053：AP1 防护——禁止手动SQL文件init

§18.3 AP1: 禁止手动 SQL 文件 init。强制使用 `__init__.py` 确保 `python -m zephyr.db init` 作为统一入口。
