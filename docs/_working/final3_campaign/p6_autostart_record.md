---
ttl: task_bound
completes_when: P14 终局报告落盘
---

# P6 主题五：服务自启方案 B 执行记录（裁定#374）

- 执行会话：st-maxexec-20260920（P6 续班）｜执行日期：2026-09-20
- 方案定位：裁定#374 主题五选定**方案 B**（壳兜底+看门狗族）——不建常驻计划任务，维持"壳拉起随壳退出"主通道（W4-6 备料件 §2），本批补齐开机触达面。

## 执行内容

### 1. Electron 壳 Startup 快捷方式（开机触达面）

- 新脚本：`scripts/register_desktop_shell_startup.ps1`（纯 ASCII 实测通过：`file` = ASCII text、无 BOM、2174 字节——§9.7 PowerShell GBK 红线合规）。
- 机制：WScript.Shell COM 创建 .lnk 到用户 Startup 目录；幂等（重跑=就地重建）；自带回读验证（target+workdir 逐字段比对）。
- 壳入口推断链：`tools/desktop/package.json`（main=main.js，scripts.start=`electron .`）→ `tools/desktop/main.js`（单实例锁+ensureApi 8890+ensureDocs 8765+僵尸端口检测）→ 快捷方式直指 `tools/desktop/node_modules/electron/dist/electron.exe`，Arguments=`.`，WorkingDirectory=`tools/desktop`（与 `electron .` 等价，免 npm/cmd 包装层）。
- **一条快捷方式覆盖全链**：壳启动→ensureApi 探活/拉起/复用 8890→ensureDocs 探活/拉起/复用 8765（main.js L144/L196 既有逻辑，零新开发）。

### 2. serve_docs 防误杀 keep 行补缺

- 查缺实测：`data/runtime/process_reaper_keep.txt` 原有 `zephyr.frontend.dashboard.api_server`（8890 面已覆盖）+ `python -m http.server`，**无 serve_docs 行**（grep rc=1）。
- 补行：`serve_docs`（cmdline 子串，匹配壳拉起的 `python scripts/serve_docs.py --no-regen`），带日期+裁定注释行（沿既有文件注释惯例）。
- 验证：`_load_keep_patterns()` 实测 patterns_total=79、serve_docs_present=True、模拟 docs cmdline 命中=True。

### 3. 执行红证（亲验输出）

```
CREATED: C:\Users\fanzi\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\ZephyrAlpha Dashboard.lnk
TARGET : D:\ZephyrAlpha\tools\desktop\node_modules\electron\dist\electron.exe
ARGS   : .  (app dir = D:\ZephyrAlpha\tools\desktop)
VERIFY : OK (target and working directory read back correctly)
```

## 验证汇总

| 项 | 方法 | 结果 |
|----|------|------|
| .lnk 存在性 | 脚本输出 CREATED 路径 | Startup 目录在位 |
| .lnk 内容正确性 | WScript.Shell 回读 target/args/workdir | VERIFY OK |
| .ps1 ASCII | python 字节级 decode | ASCII-OK、无 BOM |
| keep 行生效 | `_load_keep_patterns()` | 79 条含 serve_docs |
| 壳自启链完整性 | main.js ensureApi/ensureDocs 既有逻辑复用 | 零改动，快捷方式即触达 |

## 回滚

1. 删除 Startup 目录下 `ZephyrAlpha Dashboard.lnk`（或注释掉，不影响其他自启项）。
2. keep 行删除 `serve_docs` 两行（注释+条目）。
3. `scripts/register_desktop_shell_startup.ps1` 随批 git revert。

## 边界说明

- 本批不建 ZephyrAlpha_ApiServer/ServeDocs 常驻计划任务（方案 A 否决面，W4-6 §1 风险②：resident 模型回归）；看门狗扩展（端口探针+workspace_alerts 告警）不在本批范围，由后续主题视 Owner 签字册推进。
