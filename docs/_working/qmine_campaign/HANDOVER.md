---
ttl: task_bound
title: QMine 战役交接书（下一对话第一读）
session: st-qmine-20260925
---

# QMine 交接书（下一班第一读，读完本篇即可接手）

> 前置阅读顺序：本文 → docs/_working/qmine_campaign/00_skeleton_overview.md（总谱）→ 需要细节再翻各环节 workbook.md。
> QCure 前役背景：docs/_working/qcure_campaign/00_skeleton_overview.md + docs/_working/qcure_commit_queue_plan.md。

## 1. 项目背景三句话

ZephyrAlpha=全 AI 开发的量化交易系统。所有 AI 会话的代码成果经"提交传送带"（bag→队列→daemon 验货→dev 分支）落地，验货官=门禁链。前役 QCure（2026-09-25）治了"合法袋死在队里"的证据不同源病（入队预检/同源化/审批语言统一/快照自验/死因处方，全部已落 HEAD）；本役 QMine 开发其登记的 15 座长尾优化矿。

## 2. 本役已交付（全部在 HEAD，勿重做）

| 交付 | commit | 内容 |
|------|--------|------|
| A1 合并器治本 | 9cc5191df3 | 合并器三层身份键：unique_key 声明驱动（36/71 册）+dict passthrough（6 册 14 块活雷解除）+侧内判等去重（33% 死因消除）+env 逃逸口封堵+gates 相位计时 |
| C 队列健壮 | ac7cc5d540 | 级联标记影子文件（pending/.stale O_EXCL，四幽灵补丁根因治理）+requeue_lineage 审计 |
| D blobs 治理 | 2106e18ec2 | blob_gc.py 七桶账本+dry-run 默认+可逆归档（实弹已跑：孤儿 6413/1.24GB 待 --archive） |
| E 观测面 | 026fd1fbea | trigger 注入校验+预检 sha 缓存（15493ms→88ms）+schtasks 对账件（首报绿27黄2红7漂移16） |
| G1 门禁超时 | 3bfeb4b174 | ARCH-REFERENCE git show 10s→30s+重试（1.75MB 大册负载峰冤杀根治） |
| G2 名册标量 | 407c399a8c | total_gates 102→103 对齐（fresh 探针死锁解除） |
| F-ps1 | 392616e1d2 | Deadman 第 6 路（仪表盘心跳监控，manual 不假警） |
| 登记批 | 4b4a537a69/c014f958fc | 11 token+6 翻译+3 depgraph 节点（15208298-300） |
| 文档 | 23832f8ff4 同款载体 | qmine_campaign 7 件（总谱+六作业簿）已随并行战线入 HEAD |

验证基线：八套件 244×2 连续零失败；红蓝 R1-R4（R4 终局零残留）；三新工具实弹首跑全出真数。

## 3. 遗留任务清单（按优先级，含完整处方）

### ①【P0·盘面就绪待落】candidate 007 重编号+容量治标批
- 盘面已改好的文件（requeue 即落，但先看③的坑）：docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml（CAND-GOVTEST-005 撞号已重编号 007）+ scripts/data/audit_news_publish_time.py、scripts/data/audit_technical_indicator_columns.py（git mv 迁移）+ script-manifest.yaml + docs/03_modules/path_ownership_map.yaml + tests/scripts/test_audit_news_publish_time.py
- 命令：`python scripts/git_commit.py --session <新sid> --files "<上述清单逗号分隔>" --message "..." --enqueue --allow-non-worktree --allow-multi-domain`
- **坑**：candidate 册在 HEAD 有 CAND-GOVTEST-005 撞号双条→队列合并器 ours 侧必死→**只能直连**（`--allow-non-worktree --no-auto-enqueue`，锁忙会静默改道入队必死）；直连又可能撞 capability 册他会话 WIP 痕迹（FOREIGN_CHANGE）→ 等 capability 册平静窗（grep 无新 staged 差异时）或 allow_overlap 配额（24h 5 次滚动）刷新后带 `--allow-overlap --adopt-prior-work`。

### ②【P0·盘面就绪待落】api_server 心跳+门禁清障批
- 盘面文件：src/zephyr/frontend/dashboard/api_server.py（心跳事件有界版+any-abuse 9 处/ruff 5 处/naive datetime+time.time 18 处全清+ALGO_FLOW 锚）+ docs/03_modules/_domain_frontend/algo_flow/api_server.yaml（token 已入 HEAD ✓）
- 命令：同上形态 `--files "src/zephyr/frontend/dashboard/api_server.py,docs/03_modules/_domain_frontend/algo_flow/api_server.yaml"`。此前三连死于该文件被 3+ 会话并发编辑（快照驮他方半成品）——**等 grep 确认 api_server 无他会话新 staged 差异时再投**。
- 顺手件（同文件、可同批）：budget/schedulegate 路由注册在 `__main__` 守卫之后永不生效（真功能缺陷）——把路由注册段移到守卫前或抽 init 函数。

### ③【P1·需日间规程】AGENTS.md 三漂移修正
- 三处漂移已实测（数据集成器实为 8 子命令/commit_queue 实为 6 个/仪表盘真源 api_server 弃 app_panel）；议题 #ARCH-AGENTS-SSOT-DRIFT-001 已在册（HEAD 议题册可查）。
- 坑：AGENTS.md 受 RULES-INTEGRITY 金哈希双保险，夜战三次投递全死于该门禁（已回退盘面还原 HEAD）。正道=日间按 validate_rules_integrity 的清单再生规程走（找到金哈希再生入口→更新→带 [ARCH-APPROVAL:ARCH-AGENTS-SSOT-DRIFT-001] 提交）。

### ④【P1·新雷重放】snapself 层+EV 护栏被 F1 旧袋回退
- 范围：dbf5ee8a6c 的 assert_snapshot_selfconsistent/_witness_stale_carry/ATK-2 from-bag 基底 + EV-02 的 _DESTRUCTIVE_GIT_VERBS 打穿护栏族——代码在 HEAD 已不存在，其测试盘面留红（test_commit_queue_snapshot_selfconsistency 6 红、test_evaporation_cure_lane_ev 4 红）。
- 处方：按 dbf5ee8a6c/EV 号文原样重放（同 QMine 考古合并手法：git show 历史版逐块移植到当前 HEAD+测试即契约）。**注意与①③在 landing.py 的接缝**（QMine 考古合并批落地后 HEAD 又前进，须再三方）。

### ⑤【P2·执行类】blob_gc 实弹 --archive
- `python scripts/governance/blob_gc.py`（dry-run 已跑）→ 确认后 `--archive`（5803 块/960MB 挪 blobs_archive/，manifest 可逆，无删除）。

### ⑥【P2·登记待 Owner】
- #410 approved_paths 2026-10-08 到期续期裁定；severity 变体 22 条（P1中/P0高）定性；files_trigger 死触发 3 门 6 条（password/api_key 零命中）定性；AutoRuntime 常驻化 Owner 窗口（CAND-GOVSEC-002①+注册 Disabled 双前置）；candidate_modules 报告生成器刷新（CAND-GOVTEST-007 引用同步）。

### ⑦【长尾·已登记防遗失】
总谱 §7 全清单（docs/_working/qmine_campaign/00_skeleton_overview.md）：depends_on 排序锁（设计定稿待生产者规约）、pending sidecar 完整方案、字段改名 486 条（消费方未审）、ruling decided/void 枚举立法、blobs phase2（D 类 9133 块）、gate 链 residual 段计时二期、api_server 路由注册缺陷（若②未顺手修）。

## 4. 关键配方（血泪浓缩，接手必读）

1. **登记册拉锯死锁**：册内 ours 侧精确复合键/脏字节重复→队列合并器对一切触册袋必死→唯一解=gateway 直连（`--allow-non-worktree --no-auto-enqueue`；**锁忙会静默改道入队必死**）。
2. **token 先行**：新文件 token 未进 HEAD 时，同源预检拒收→token 批必须**真落地**（非仅入队）后再投业务批；或注册表∈袋（落地仿真自洽）。
3. **热文件 CAS 三连**：safe_write_text+content_sha256 必配 retry 循环（晨会并发期 StaleWriteRefused 常态）；写后进程外复核。
4. **门禁格式全家桶**（新 .py）：ruff format/check、复杂度≤15（_cyclomatic_complexity 复算）、BLUEPRINT MOD-* 头、裸 Any→object、SSOT 符号禁自建、naive datetime/time.time 禁（perf_counter/tz-aware 替代）、MSG-EXPOSURE（路径走属性）、src/ 新模块加 ALGO_FLOW external 锚+卡片 yaml 同批。
5. **PERM-TRIGGER 豁免正解**：门禁不解析 noqa——改写为事件有界等待（stop_event.wait）。
6. **外来 staged 连坐**：REGISTRY-MASS-DELETION 等全索引扫描门被他会话 staged 件触发时——git add 刷新我方文件到盘面态、或临时 unstage 挡道件（用后还原）。
7. **会话 ID 撞名**：st-qmine-20260925 与晨会 LANE-LAND 撞名（seq/审计混流）——新班起独占新 ID。
8. **claim 正道**：FOREIGN_CHANGE 时 release-only→全新 acquire→免 overlap 旗直连；allow_overlap 24h 配额 5 次省着用。

## 5. 队列/管现终态（交接时点）

pending=0、daemon 健康（多次纪元换血均为设计内）；dead 存量已带处方字段；NightlySentiment 红灯已清（result=0）；全流通面=QCure 三色表绿 8/黄 3（QMine 已消化仪表盘心跳与 QMT 确认）/红 0。
