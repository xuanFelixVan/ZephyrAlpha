# Subsystem Health Report - 2026-04-16 17:57

## 摘要

- 磁盘子目录总数: 21
- Canonical（已登记活跃）: 19
- Planned（规划中）: 0
- 幽灵子系统（未登记）: 2
- 残留子系统（应已清理）: 0

## 幽灵子系统（需立即在 subsystem-registry.yaml 中登记或清理）

- `docs/06_ARCHIVE` (38 文件)  ← 功能域重叠: ['archive']
- `docs/07_RESEARCH` (15 文件)  ← 功能域重叠: ['research']

## 建议行动

1. 每个**幽灵子系统**：在 `docs/subsystem-registry.yaml` 中登记（canonical 或 deprecated）
2. 每个**残留子系统**：按 `docs/09_AUDIT/STATE/subsystem-dedup-decisions-20260416.md` 执行合并
3. 新建目录**前**：先查阅注册表确认无功能重叠