---
ttl: task_bound
title: 深度审查作业簿——CH DDL部署器
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：CH DDL部署器（I25）

- 状态: **已审**
- 级别: P2｜类型: 基础设施
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `scripts/ch/apply_market_tables_ddl.py:1084`（_EXPECTED_ENGINES 矩阵尾段；apply() :1131，verify() :1197）
- 生产调用方: 手动/部署流程（STARTUP=manual，[CONSUMERS] 空）
- 测试文件: 无（头注 [TESTS] none）
- 备注: **他会话在途改动（git status=MM：staged 40 行删除+unstaged 40 行插入，内容=D3 宏观六表+D4 油价链三表 import 块，st-datapack-20260918）——本报告按当前工作区状态审，收口时需重验**

## 1 对象快照

- 审查范围：部署器主流程（apply/verify/main + _MIGRATIONS 93 条 + 探针子进程机制），DDL 常量区只抽查结构不逐表核（73 张 _ALL_DDL / 72 张引擎矩阵，均为 schemas/categories/*.py DDL-as-Code 导入）。
- 排除项：schemas/categories/*.py 各 DDL 内容正确性（列级口径归数据表 schema 对象群）；apply_rbac.py。
- 测试覆盖概况：零测试（[TESTS] none）——部署器无自动化验证，依赖人跑 verify。
- 材料包缺项：生产 CH 实际引擎/列实况未取证（只读未授权）；假成功前科的历史事故记录未全文调阅。
- 变更热力：41 次提交，高热区（几乎每波数据扩表都触达，逐表手改模式）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| E 对抗 | **CREATE TABLE 循环仍是无条件 ✓**：`ch_writer.query(ddl)` 返回值被忽略（ch_writer 契约=失败返回空串不抛），建表循环逐张打印 ✓——假成功前科（:1149-1151 注释自认"ch_writer 吞错+无条件 ✓ 曾致多批假成功"）只治了迁移段（探针）没治建表段 | apply_market_tables_ddl.py:1143-1146 vs :1149-1151 | P2 | 造一张语法坏 DDL 注入 _ALL_DDL 跑 apply()，观察 ✓ 照打 |
| A 深度 | 兜底网有洞：建表失败只能被 verify() 事后抓住，且仅当表在 _EXPECTED_ENGINES——实测 `daban_engine_load` 在 _ALL_DDL 而不在引擎矩阵（全量对比，唯一漏网）：该表建表失败将静默 | apply_market_tables_ddl.py:1131-1194 vs :1040-1126（矩阵）；本报告实测对比 | P3 | 补 daban_engine_load 入矩阵或跑 verify 看其不在输出 |
| A 深度 | 迁移探针正则只认 `ADD COLUMN IF NOT EXISTS`（probe_py :1159-1163），其余类型（MODIFY/ADD INDEX/ORDER BY 调整）走 "OK-noprobe"=无探针无条件信——与假成功前科同型的残余面；且 sort key MODIFY 的异步 mutation 特性（apply_timezone_migration.py:213 在案）探针恒不覆盖 | apply_market_tables_ddl.py:1156-1171 | P2 | grep _MIGRATIONS 非 ADD COLUMN 条目清单，抽一条人工对 system.columns 复核 |
| B 上游 | try/except ImportError→内联 fallback DDL（tick/l2_tick/kline_daily/etf_daily/auction_book/sector_snapshot/cross_validation_log/hog_* 八处）：导入失败=静默切第二真源（模式 #4 双份承载）——JOB-077 治本只修了 sys.path 使 import 成功，fallback 分支仍在且 verify 只核引擎不核列，schema 漂移不可检 | apply_market_tables_ddl.py:59-96, 123-154 等 vs :52-53（"fallback 成为事实运行时——真源漂移温床"自认） | P2 | 临时改名 schemas/categories/intraday/market_tick.py 跑脚本，确认静默走内联且无任何 warning 输出 |
| E 对抗 | 迁移 SQL 经 subprocess argv 传递（[sys.executable, "-c", probe_py, sql, table]）：93 条实测无换行（本报告验证），但 Windows argv 长度上限 ~32k+特殊字符转义是隐爆点；未来长 ALTER 会炸 | apply_market_tables_ddl.py:1175-1179 | P3 | code review（当前无 multiline 条目=未爆） |
| D 旁系 | _EXPECTED_ENGINES 手工维护静态清单（72 条，逐条带日期注释）：与运维红线 §9.5"条目列表+计数清单必须生成器产出"冲突——每波扩表手加两处（_ALL_DDL+矩阵）已现 1 条漏网（上条）；clippy 式生成器（从 system.tables 反向 diff）缺位 | apply_market_tables_ddl.py:1027-1126 | P3 | 收口方裁定是否豁免（部署脚本 vs 常设清单） |
| A 深度 | ensure_database fail-visible 路线 B（:1134-1140）+迁移子进程隔离（Code 62 通道污染治本）+探针核实=三层事故教训均已成文化——正向确认 | apply_market_tables_ddl.py:1133-1140, 1148-1152 | — | — |
| C 下游 | 在途改动（D3/D4 十表 import 块）工作区 MM 状态：若他会话中途中止，staged 删除+unstaged 插入的错位状态会让下次提交丢失整块——收口前必须处理 | git status MM + 本报告 diff 抽查 | P3 | `git diff --cached` vs `git diff` 对比确认归属 |
| A 深度(测试) | [TESTS] none：73 表×93 迁移的部署器零自动化测试，探针逻辑本身（正则/verdict 解析）无单测——探针是治本件，自身却是裸奔件 | apply_market_tables_ddl.py:15 | P3 | grep tests/ 无对应文件 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 版本化迁移 vs 幂等重跑式部署（Flyway/Sqitch 元数据表+checksum vs IF NOT EXISTS 全量重放） | **立卡候选**：业界主流=版本化迁移（每变更加版本号+元数据表追踪+checksum 防漂移）；本对象="全量幂等重放+探针"模式，93 条 _MIGRATIONS 无执行台账（每次 apply 全部重放，靠 IF NOT EXISTS 幂等）——已现痛点：无法回答"哪条迁移哪天在哪台执行过"。立卡：轻量迁移台账表（migration_id/apply_time/verify 状态）即可，不必引入 Flyway 全家桶 | Bytebase: Top Database Schema Migration Tools, bytebase.com, 2026：https://www.bytebase.com/blog/top-database-schema-change-tool-evolution/ ；Flyway vs Sqitch 对比, stackshare.io, 存档：https://stackshare.io/stackups/flyway-vs-sqitch |
| DDL-as-Code（schema 真源=代码文件，部署脚本引用） | **对等已有**：与 Liquibase formatted SQL / atlas schema-as-code 同思路，且真源单向（schemas→deployer）设计正确；短板只在 fallback 双源残留（D-4） | 同上 Bytebase 分组中的 declarative/diff 类工具叙述 |
| 部署后验证（verify 步骤） | **对等已有偏强**：Sqitch 内建 verify 思想同源，本对象 verify 核引擎+列缺失不核（见 D-4）——建议 verify 增加「列集合对账」（system.columns vs schema 文件列清单） | Stack Overflow: Sqitch verify/revert vs Flyway, stackoverflow.com, 2017 存档：https://stackoverflow.com/questions/43921401/ |

## 4 缺陷清单

1. **D-1（P2）建表段无条件 ✓（假成功前科残余）**
   - 现状→证据：:1143-1146 忽略 ch_writer.query 返回值；前科修复只覆盖迁移段。
   - 影响：新建表 DDL 失败（权限/语法/cluster）静默，若表恰不在引擎矩阵（如 daban_engine_load）则 verify 也不报——双重漏洞叠加=真实假成功窗口。
   - 建议修法：`ok = ch_writer.query(ddl)`，空返回即计失败；或建表段也走探针（system.tables 存在性核实，一行 SQL）。同批补 daban_engine_load 入矩阵。
   - 验证法：坏 DDL 注入实验（轴 E 行）；修后 apply 对失败表打 ✗ 并退出码非 0。
2. **D-2（P2）探针覆盖面仅 ADD COLUMN**：非 ADD COLUMN 迁移（MODIFY 等）无核实；建议按迁移类型注册探针模板（MODIFY→system.columns.type 比对），覆盖不了的显式打 "UNVERIFIED" 而非 "OK-noprobe"。
3. **D-3（P2）ImportError fallback 双源残留**：fallback 触发时至少 log.warning+stderr 提示（可见化）；中期删除 fallback（导入失败就 fail-visible，路径治本已完成）。
4. **D-4（P3）引擎矩阵手工静态清单**：生成器化或裁定豁免登记。
5. **D-5（P3）零测试**：探针 verdict 解析逻辑提取为可测函数补 3-5 个单测。
6. **D-6（P3）在途 MM 状态收口义务**：他会话（st-datapack-20260918）改动需先落定，本报告发现按基线过期重验。

## 5 挂起疑问

- daban_engine_load 表是历史遗留还是漏登记（不在矩阵=从未被 verify 检查过，其实际引擎/存在性未证）。
- 93 条 _MIGRATIONS 是否曾在生产全量成功（探针 2026-09-14 前的旧批假成功表有多少已被 verify/人工补救）——需迁移台账才能回答（立卡 D-3 动机）。
- 他会话在途块与本审查基线的最终归属（收口方处置）。

## 6 完备性自评

- 六轴全查：A（探针正则/argv/覆盖率）、B（ch_writer 吞错契约+fallback 双源）、C（无下游消费方=部署入口；在途状态风险）、D（手工清单红线+schemas 真源单向）、E（假成功三问：静默失败=建表段、假阳性=OK-noprobe、重跑=幂等安全）、F（三源带 URL）。
- 长尾：73 张 DDL 列级口径未逐表核（归 schemas 对象群）；RBAC apply_rbac.py 未审；_MIGRATIONS 各条 SQL 语义未逐条核（抽查 5 条 ADD COLUMN 形态正常）。
