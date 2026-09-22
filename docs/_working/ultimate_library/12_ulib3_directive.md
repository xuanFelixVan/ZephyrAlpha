---
title: "终极图书馆 · st-ulib3 自动化收尾+治理升级总班施工指令（防漂移锚点）"
ttl: task_bound
completes_when: 本指令全部任务落地+验收通过（两轮零）+红蓝对抗两轮零+会话收尾
date: "2026-09-22"
owner: "ZephyrAlpha-Owner"
session: "st-ulib3-20260922"
status: "directive_active"
---

# st-ulib3-20260922 施工指令（自用锚点，防幻觉防漂移）

> 来源=Owner 2026-09-22 通宵令原文+会话讨论三项增量裁定（已全批）。执行全程不问不停、自裁授权（架构师第一性原理）。本文件是唯一任务真源，漂移时以此为准。

## §0 授权与铁律

- Owner 已"全批"任务 1-4 与讨论增量（词表方案 B/日志抽屉方案 A/按表查资产并入任务5）。
- 提交配方（全部如此）：`python scripts/git_commit.py --session st-ulib3-20260922 --files <清单> --enqueue --allow-non-worktree --allow-overlap --allow-multi-domain`
- 热注册表（capability/translation）编辑+入袋必须同链或原生显式字节通道（`from scripts.commit_queue import enqueue_item; enqueue_item(sid,msg,[(path,bytes)])`）。
- 死信读 `.runtime/commit_queue/dead/q-*.json`；新 .py 必办 design node+翻译册+token 前置批（token 与新文件不同批=recipe⑤）。
- 净零铁律：扩展现有字段/闸，禁立平行登记表。
- 多车道在飞（taskcards/workclean/tilib-b10/dloop-v2）：勿碰他车道 staged 文件。
- 工作区现状：677 脏件多为他车道在飞+接手批余件；只动本任务清单内文件，脏件不肉眼判罚。

## §1 任务清单（12 项，含讨论增量标注）

1. **修宪落地**：AGENTS.md 草稿已在暂存区（检索序加图书馆入口+存储地图，2 处等长替换 140→140 行）。已批，带标记 `[ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]` 走队列落地。落地后 `git log -1 --name-only` 核实归属。
2. **备份馆**：PG depgraph 账本（lib_assets/lib_events）定时备份→G:/backup+F 镜像+每月自动恢复演练（恢复到临时库核行数出报告）。事件触发优先，reaper 类逻辑禁 cron/sleep-loop（schtasks 定时任务属系统级调度，可登记 process_reaper_keep）。
3. **he-session 催收编**：盲册首散件（a5_delivery_report.md 等）逐件判定：收编入册或签死亡证明（authority 必填）。
4. **post-commit 刷新钩子**：提交钩子自动跑"增量采集→指纹刷新→馆页重生成→对账"（事件触发，消灭手动 regen）。
5. **lookup 两轴过滤器**：src/zephyr/library/lookup.py + librarian._SQL_LOOKUP 扩展 kind（12 枚举）/owner_domain（83 域）/tags/status 组合筛选 + STARTUP 自动化形态。schema 零改动。**增量A：回测产物 CLI 查询面**（按策略/日期段查 data/backtest_artifacts 产物+关联日志路径，挂 result_repository API 套 CLI）。
6. **查重闸升级**：commit_preflight.py CAPABILITY-LOOKUP-REQUIRED 预检升级：业务关键词必查图书馆+查重结果进提交留痕（治编排器惨案）。
7. **标签词库固化**：新建 library_tag_vocabulary.yaml（标准词+别名层，别名挂唯一标准词，起步 ~200 词按域分组）+ 新闸 TAG-VOCAB（tags 非枚举即拦/别名孤儿即拦）+ 新词只准馆员/裁定增补。**方案 B 增量**：收编 15 份 catalog 内联"v2.0 标签词表"（~58 标签，同域重复簇必并，各 catalog 改引用）+ 2 个 governance_metadata JSON 派生快照退役 + 词表统一查询入口（词表总目录层，不并物理文件）；其余 ~44 词表各守其域不并（跨域不同对象）。
8. **血肉闸+SOP**（优先级最前，与 7 并行）：仿 TRANSLATION-COVERAGE 建"新资产登记必填血肉"闸（title_zh/plain_zh/tags 枚举/别名）+ SOP 文档 docs/01_policies_and_standards/sop/library_sop/blood_flesh_cataloging_sop.md（doc_type=policy，CREATE-GUARD 登记）。千问苦力班前置件。
9. **藏书规程页+月度卫生命令**：规程馆页由 DIRECTORY-CONTRACT 真源生成器产出（禁手写）；卫生命令一条跑出"临时区 30 天+结案闭合+无引用"候选清单。**增量B：日志保留期候选纳入**（logs/ 现 464 件无 TTL 机制；只出清单 Owner 月批，禁自动删除）。
10. **日志抽屉入馆（方案 A，Owner 定案）**：日志不逐件入册；registry_of_logs.yaml（98 条，路径/写入方/retention）作日志族 SSOT 与图书馆连线，族级资产指向存放大盘。**Owner 目标：每个模块的回测日志都必须有抽屉且图书馆查得到**——核验 registry_of_logs 覆盖缺口（回测/研究类族），缺的补登记，全量核验出报告。
11. **按表查资产收口**：ch_collector/pg_collector 采集时从 data_asset_registry.yaml（DS-109~220）反查回填 owner_domain/tags（治 TBL 条目 owner_domain=None 空壳+两册无 ID 关联）；check_library_coverage.py 对账口径扩 kind=table（现只核 file/module/doc/registry 四类）。
12. **可选 W+1**：量化机构文件管理实践全网挖矿（EDMC/BCBS239/DORA/SRE 文件管理细则层），产出喂藏书规程页。

## §2 验收判据（缺一不可）

- 全任务落地（12 可选）；coverage blind=0/ghost=0 连续两轮（含 table+日志抽屉口径）；pytest tests/library 全绿；红蓝对抗两轮零。
- 日志抽屉全覆盖核验报告（每模块回测日志有抽屉）。
- 全部经 GitCommitGateway 落地；临时文件清零；会话收尾序列（release claims→handoff→汇报）。

## §3 关键事实底账（讨论实测，勿再重查）

- 词表类库共 ~61 处：41 枚举词表 + 3 翻译/术语册 + 状态词表 2 处 + 15 份内联标签簇（同源复制）+ 2 派生 JSON。
- 表资产：kind=table（前缀 TBL），ch_collector 直读 CH system.tables（asset_id=TBL:ch:<db>.<table>，owner_domain=None、tags=['ch']）；data_asset_registry.yaml 220 DS 条目含 produced_by_job/module_id 但与 TBL 无 ID 关联；总 ~300 表。
- coverage 闸 scripts/governance/generators/check_library_coverage.py:39-43 只核四类。
- lookup _SQL_LOOKUP（ledger_schema.py:134-140）仅 3 个 ILIKE 维度（asset_id/home/title），lib_assets 有 tags text[] 无 aliases 字段。
- 日志四存放地：logs/ 464 件、data/backtest_artifacts/ 716 件（已入册 kind=file）、.runtime/（gitignored）、F 盘冷库只存 CH parquet（回测数据家不在冷库=红线）。
- 回测产物 API：src/zephyr/backtest/io/result_repository.py get_artifact/list_artifact；无 CLI。
- registry_of_logs.yaml：docs/01_policies_and_standards/_registry/catalogs/，98 条。
- 上一班 14 条门禁配方见 11_handoff_next_session.md §9（热文件同链/token 先行批/队列序/own-scope 等）。
