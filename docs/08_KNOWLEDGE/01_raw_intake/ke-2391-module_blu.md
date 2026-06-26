---
module_id: KE-2296
title: 5.2 参数约定
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 5.2 参数约定

5.2 参数约定

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--dimensions` / `-d` | list[str] | 全部 | 指定运行的维度（如 `d1,d3,d5`） |
| `--list` / `-l` | flag | — | 列出所有已注册脚本及描述 |
| `--dry-run` | flag | — | 只列出将执行的脚本，不真正运行 |
| `--verbose` / `-v` | flag | — | 输出每条Finding的详细信息 |
| `--warn-only` | flag | — | 退出码 ≤ 1（不因ERROR阻断——用于审计查看） |
| `--output` / `-o` | path | stdout | 输出文件路径 |
| `--tags` / `-t` | list[str] | — | 按标签选择脚本（如 `--tags Security,Quick`）。§3.6 定义合法标签 |
| `--depth` / `-dp` | enum | `full` | 验证深度：`quick`（快速扫描，<5s）/ `full`（标准扫描）/ `deep`（深度扫描，含知识分析） |
