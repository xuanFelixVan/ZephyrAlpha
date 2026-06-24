---
module_id: KE-002
title: 4. 编码安全（唯一始终生效的硬规则）
category: agent_instruction
---

# 4. 编码安全（唯一始终生效的硬规则）

4. 编码安全（唯一始终生效的硬规则）

> **§6.17 Canonical 物理位置铁律**：本节为编码安全规则的 **canonical SSoT**（版本 v4.19.0）。下游派生文件 [GOV-DOC-005 trae_028_doc_structure_naming.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml) 标注 `derived_from: AGENTS.md §4`，提供扩展阅读和修复流程。

| # | 规则 | 强/弱 | 对标 |
|---|------|:---:|------|
| 1 | 禁止 PowerShell `echo`/`Out-File` 默认参数写 `.md` 文件——必须用 `[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)` | 🔴 硬 | Unicode §2.5 / W3C Character Model |
| 2 | Python `open(path, 'w')` 禁止省略 `encoding`——必须显式 `encoding='utf-8'` | 🔴 硬 | PEP 8 §Source File Encoding |
| 3 | Trae 编辑器：`files.autoGuessEncoding` 必须为 `false`，`files.encoding` 必须为 `utf8` | 🔴 硬 | ITIL Change Control（计划外变更风险） |
| 4 | 禁止在 Cursor 和 Trae 中同时打开同一文件编辑 | 🔴 硬 | — |
| 5 | 扫描器/校验脚本产生异常大量错误报告时，先暂停并检查扫描器本身——可能是正则表达式或校验逻辑写错了，而非文件真的有问题（KE-001：3587 个误报源于一个多余反斜杠） | 🟡 检查 | — |
| 6 | **源码-测试同步铁律**：任何 `src/zephyr/` 下源码修改（重命名类/函数/变量、变更函数签名、修改返回值类型、重组目录结构、变更数据模型/Schema/字段默认值），必须在同一 session 内：①同步更新所有受影响的测试文件 ②跑通全量测试 `python -m pytest tests/ -q` ③确认零失败。禁止"先把源码改了，测试以后再说"。Pre-commit GATE-18 为自动化执行层。 | 🔴 硬 | ITIL Change Enablement |
| 7 | **AI 对话文件锁协议**：任何文件写入操作（创建/修改/删除/重命名）前 MUST 执行：① `python scripts/lock_files.py check <file>` → 被锁则 STOP；② `python scripts/lock_files.py acquire <file> <session_id> --task "<简述>"` → 获取失败则 STOP；③ 操作完成后 `python scripts/lock_files.py release <file> <session_id>`。禁止跳过任何一步。禁止 check LOCKED 后强行写入。完整协议见 [.trae/rules/project_rules.md](file:///D:/ZephyrAlpha/.trae/rules/project_rules.md) RULE-ZERO。 | 🔴 硬 | K8s ResourceQuota / etcd 分布式锁 |
| 8 | **MCP 文件命名 vs server_id 不一致**：`doc_guard_server.py` 的 server_id 是 `session_handoff`，`sentinel_server.py` 的 server_id 是 `intent_router`。这是已知差异，不可"修正"文件名——server_id 是 MCP 协议契约中的标识，不可更改。所有引用这两个模块的地方 MUST 使用 server_id 而非文件名作为协议标识。 | 🔴 硬 | MCP MOD-INF-013 §2 |
| 9 | **临时文件零残留铁律（Zero-Residue Mandate）**：任何 AI session 在施工过程中创建的 `_temp*` / `_check*` / `_fix*` / `_phase_*` / `_deep*` / `_construction*` / `_rebuild*` / `_audit*` 等前缀临时文件，MUST 在 session 结束前执行二选一：①有保留价值 → 归档到标准目录（`scripts/governance/` / `tests/` / `src/zephyr/`）并注册到 `script-manifest.yaml`；②无保留价值 → 物理删除。**禁止保留在根目录或任何非标准位置。** 对标 §5.2.2 维度 E、IRN-011 ZR-003/ZR-005/ZR-007/ZR-008。Session 结束清单第 5 条为自动化执行层。违反 = 阻断级（P0），不可关闭 session。 | 🔴 硬 | IRN-011 / Unix 哲学 |

> **大白话**：改源码的时候必须同时改测试，改完立刻跑一遍确认全绿。不要"先改源码，测试以后补"——跟借高利贷一样，拖越久利息越高。
>
> **大白话（锁协议）**：改任何文件之前，先问问"有没有其他 AI 在改这个文件？"——用 `python scripts/lock_files.py check <file>` 查。如果有人，你就碰不得。没人，你就抢锁——`python scripts/lock_files.py acquire <file> <你的编号>`。改完，还锁——`python scripts/lock_files.py release <file> <你的编号>`。跟机场行李柜一样：你开柜的时候别人开不了，你关柜了别人才开。跳过这三步 = 编码损坏，屡试不爽。
>
> **大白话（临时文件零残留）**：每次干活时随手建的 `_temp*` / `_check*` 临时脚本，干完活必须处理：①有用 → 放到正规目录（`scripts/governance/` / `tests/` / `src/zephyr/`）并登记；②没用 → 直接删。**绝对不能留在根目录。** 就像吃完饭必须洗碗——碗要么洗干净放碗柜（归档），要么是一次性碗直接扔（删除）。堆在水池里的脏碗（根目录临时文件），下一个来吃饭的人就得替你洗——但 AI 永远不会主动替你洗。你今天留下的临时文件，就是明天的磁盘垃圾。
