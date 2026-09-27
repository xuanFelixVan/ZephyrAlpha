---
ttl: task_bound
completes_when: 本役案卷已在落地面复跑并逐条附命令原文
---

<!-- 本表由 scripts/governance/wave1a/ch_read_shape_ruler.py 机生，禁手改（重跑覆盖） -->
<!-- source=git HEAD tree scanned_files=129 unreadable=0 generated_at=0 findings -->

扫描面：`git HEAD tree`，129 个 .py 文件；命中 0 处（判据路径 0、非判据路径 0、豁免面 0）。

| 分级 | 文件 | 行 | 模式 | 命中原文 | 建议补丁位置 |
|---|---|---|---|---|---|

补丁口径统一＝把字符串读接口换成立即可用的严格通道：`ch_reader.query_rows()` / `count_strict()` / `query_rows_table()`（W-180.1），判据类一次性读数走 `scripts/governance/data_supply/ch_probe.py（注：施工方案原指 `scripts/data/`，实测该目录被 .gitignore 第 603 行整体排除，故改道）`（W-180.4）。