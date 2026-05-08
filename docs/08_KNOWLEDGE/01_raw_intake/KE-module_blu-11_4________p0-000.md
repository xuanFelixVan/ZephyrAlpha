---
module_id: KE-module_blu-11_4________p0-000
title: 11.4 并发与持久化 P0
category: module_blueprint
---

# 11.4 并发与持久化 P0

11.4 并发与持久化 P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-P1 | 多进程并发 sync 不冲突 | 空库 | 3 进程各 100 docs sync | filelock 正常，无重复 chunk，总量正确 |
| P0-P2 | 重启后持久化正常 | ingest 10 docs 后杀进程 | 重启 search | 查询结果与重启前一致 |
| P0-P3 | reindex blue_green 不阻塞查询 | 持续 search QPS=5 + 触发 reindex | 检查期间错误率 | < 0.1% |
