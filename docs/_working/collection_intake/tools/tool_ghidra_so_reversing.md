---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# Ghidra 做 .so 逆向——工具存档笔记 2026-09-20

> 判定 D（存档）：当前无在办闭源 SDK 分析需求；触发场景出现时直接按本笔记开工。

## 工具事实 `[外部]`

- Ghidra（NSA 开源）最新版 **12.1.3**（2026-08-18 发布，官方 GitHub releases；官网 ghidra-sre.org 偶发 403，以 GitHub 为准）。
- ELF/.so 支持为内置核心能力：`ElfLoader`（Ghidra/Features/Base/.../opinion/ElfLoader.java）+ Android 专用 ELF 重定位（AndroidElfRelocationOffset 等）+ oat 等 Android 格式；能力=反汇编、反编译、函数调用图、脚本化。

## 使用要点（剪报内容，与官方能力对得上）

- .so=Linux/Android 共享库 ELF 二进制；可直接加载分析。
- **通常无符号表**：需手动识别函数、恢复结构体；工作量取决于混淆和加壳情况。

## 项目触发场景（预设）

- 券商/行情终端闭源 SDK 的接口行为核实（如 miniqmt/QMT 桥替代通道分析、同花顺数据接口行为验证）。
- 合规边界：仅分析与本项目数据接入相关的自有授权软件；不得用于规避授权或破解。
- 配套：分析产物（函数签名/结构体恢复）落 docs/_working 子目录，登记 token。
