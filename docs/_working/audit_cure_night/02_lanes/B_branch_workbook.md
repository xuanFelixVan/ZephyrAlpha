---
ttl: task_bound
title: 车道 B（l8 分支内容落地）作业簿——裁定#490 A 段
session: st-acure-b1
created: 2026-10-08
completes_when: L8 两 .md 随投影快照 v90+ 物化入 HEAD 且分支 session/st-mastertc-l8 归档
---

# 车道 B 作业簿：session/st-mastertc-l8 六文件差异面内容等价落地

> 总包授权=裁定#490（已落册）。分支 tip=cf5b6ddcf7（四提交：9c37e38775/f4910d5b03/9094d25f55/cf5b6ddcf7），
> 差异面=6 文件 +242/-1（git diff --stat cd6ad4f7d0..session/st-mastertc-l8 实测核对一致）。
> 禁 merge/checkout/restore（他会话在飞+主区脏面，merge 三拒在案）；一切状态变更走 git_commit.py 正门。

## 一、逐文件六向台账（verdict+哈希+核验）

### 1. docs/_working/master_tc_night/lanes/L8_retire_ai/00_workbook.md — 落地=留盘待 v90 物化
- **六向**：①分支新建件（+112）②HEAD 无此件、无 L8_retire_ai 目录；已 `git show` 直出落盘，blob sha256=`219ad3939f6fff751e18b64f49f8d542ae374c56d2207c715d817e7871d4f87e` 与分支逐一相等 ③上游=L8 车道 13 卡台账真源 ④下游=7 张卡 HEAD 无落地面状态解除的载体 ⑤冲突面=CREATE-GUARD 读 HEAD+staged 快照册，token 不在 committed 册面即拦 ⑥残余=快照 v90 物化后随袋提交（PG 意图已登记，回执见 §二）。
- **登记回执**：PG `registry_ledger` 意图 API register(token=l8-retire-ai-lane-workbook-00-workbook-20261007)=OK_NOOP（同键同指纹幂等）；created_by=st-mastertc-l8（分支 verbatim），登记会话=st-acure-b1。

### 2. docs/_working/master_tc_night/lanes/L8_retire_ai/b_class_map.md — 落地=留盘待 v90 物化
- **六向**：①分支新建件（+39）②落盘 blob sha256=`01a7f653ee7633f9589710e2b46adf114d364c7eb41847509be11af929adcdf3` 与分支相等 ③上游=W-168 出口判据（四行映射表）④下游=OBJ_R 修订窗排期移交 ⑤冲突面=同上 ⑥残余=同上。
- **登记回执**：register(token=l8-retire-ai-lane-workbook-b-class-map-20261007)=**OK**（新建）。

### 3. docs/_working/ai_layer_vision/HANDOFF_wave2_closeout.md — **落地（已入队 q-20261008-st-acure-b1-0001）**
- **六向**：①分支新建件（+50）②落盘 blob sha256=`e969c6bfef8d0b757cb5a3ef5a7c399d74314395b682d073c1b302fddafe9cb2` 与分支相等 ③上游=92 册交接卡骨架+C96 双层蒸发判 ④下游=收尾班/继任棒 ⑤冲突面=无（token c314-… 已在 HEAD 册=他队先行落地，交叉验证逐字一致含 merge_evaluation）⑥残余=§七两件"待勾"归收尾班（分支卷内自记）。

### 4. strategy_registry.yaml — **落地（同袋）**
- **六向**：①分支两 hunk=九态块+entry_schema 注释行 ②HEAD 锚点（unique_key/entry_schema）与分支 base 逐字吻合、无脏面；worktree patch 与分支 patch **逐字相等**（`git diff` 去 index 行 sha256 对拍=PATCH_EQUIV）；safe_write_text CAS（before=4e6bd242…→after=d952c393…）纯插入零删改 ③上游=裁定#398/#399+04_lifecycle_fsm §二3.6 ④下游=registry_state_vocab.MACHINE_READABLE_FIELD 消费（落地义务"YAML 块待总筹落地"兑现）⑤冲突面=无 ⑥残余=0。
- **一致性核验**：进程外 yaml.safe_load，lifecycle_status_values==[candidate,backtest,sim,paper,live,monitoring,decayed,retired,shelved] ✓。

### 5. migration_registry.yaml — **落地（同袋）**
- **六向**：①分支尾部 +11 候选行 ②HEAD 尾锚（evidence 行）吻合、无脏面；PATCH_EQUIV 对拍通过；CAS（81cc9e50…→d9c56fe4…）纯追加 ③上游=#488 通道+B11/ae952d32 文件头注记 ④下游=退役排班窗（Owner 门位）⑤冲突面=无 ⑥残余=物理删除三段式另批。
- **一致性核验**：yaml.safe_load 后 retirement_schedule.windows_service_file_retire.candidate==src/zephyr/trading/windows_service.py、status==deprecated_marked ✓。

### 6. capability_canonical_file_registry.yaml — verdict=**跳过直改（投影制迁移期），意图 API 补账完成**
- **六向**：①分支增量=3 条 token 行 ②C314 行已在 HEAD 逐字在册（他队落地=交叉验证通过）；L8 两行不在 ③真源已迁移=PG 账本投影（REG-YAML-PARSE 门判"私改投影册无效"，改动须意图 API+生成器重打）④下游=快照发布器（v89=2026-10-07 23:42+08，落后于本夜登记）⑤冲突面=本夜热面连发物化一次（会话 01:0x 直插两行被投影重打洗掉；监视 90s 稳定窗后二次补插又被 render 覆盖——投影制下直改注定无效，停止直改）⑥残余=v90 物化两行后 L8 双件随袋即落。
- **处置链**：意图 API register ×2（§一.1/2 回执）→ `registry_projection_generator.py --render`（PG wins，ledger_revision=88）→ rendered 对拍 HEAD：token 12446→12444 **丢 2 条**（private-key-exempt-registry-…/govfix-g2-dryrun-gate-…，G4/G2 今夜 HEAD 件，PG 基线未吸收）→ **放弃提交投影面**（会落地丢条目册=regression，绝不由本车道代拍）。
- **过程披露**：三次提交尝试（1:CREATE-GUARD 拦 L8 双件；2:SESSION-REQUIRED+CREATE-GUARD；3:REGISTRY-YAML-PARSE 拦投影私改）——按"单项 3 次不通=登记+跳过"纪律转意图 API 登记+分期落地。

## 二、提交面

- **袋 A（已入队 q-20261008-st-acure-b1-0001，files=3）**：HANDOFF_wave2_closeout.md + strategy_registry.yaml + migration_registry.yaml。落地哈希见 §一；commit 后归属核实=git log -1 --name-only（恰 3 文件）。
- **留盘待 v90 批（与 00_orchestration.md 同款在途态）**：L8 双 .md + 本台账 + 本台账 token（PG 意图：file=docs/_working/audit_cure_night/02_lanes/B_branch_workbook.md，capability=acure-lane-b，created_by=st-acure-b1）。
- batch_creation_tokens.py 直写通道已被投影制废止（工具仍直改 YAML）——本车道 token 登记全部改走 PG 意图 API，机制替代披露如上。

## 三、OPEN_QUESTIONS（呈总筹/维护班/Owner）

1. **投影快照发布滞后**：v89（23:42）落后于 PG 账本现存登记（含本车道 2 条）；v90 发布+render 前，一切新 .md 的 CREATE-GUARD 过门依赖 committed 册面=被卡。建议维护班尽快基线对账+发布 v90（先吸收 G4/G2 两条 HEAD 存量 token 防 regression，再物化增量）。
2. **PG 基线缺 2 条 HEAD token**：private-key-exempt-registry-…（G4/7d4079cf63）、govfix-g2-dryrun-gate-…（G2）——PG 落后 HEAD 实证；render 若先于基线补账提交=丢条目。已在本台账留痕，未代修（owner=维护班）。
3. **L8 分支归档建议**：本车道落地完成（v90 批入 HEAD）后，`session_worktree.py merge` 已无必要——分支内容全部由内容等价落地覆盖（三 .md blob 相等+两册 PATCH_EQUIV+capability 三 token 行两在册一在 PG 账本）。届时归档：`session_worktree.py archive st-mastertc-l8`（死判→存证→prune→branch -d）。
4. **C314 token 行在册归属性**：HEAD 册已有分支版 C314 条目（created_by=st-mastertc-l8）——由他会话（G 系或 L3 并集批）先行落地，本车道按任务单跳过规则跳过=交叉验证通过，无重复登记。

## 四、DONE_SUMMARY

- 分支四提交内容全部有着落：3 .md blob 级等价（2 在盘待 v90、1 已入队）；2 册 PATCH_EQUIV 级等价（已入队）；capability 3 token 行=1 在 HEAD（他队）+2 在 PG 账本（本车道意图登记）。
- 红线遵行：禁 merge/checkout/restore ✓；safe_write_text CAS 双册 ✓；意图 API 走 DatabaseService/registry_ledger ✓；零裸 duckdb、零危险 git、零 .runtime 根直写（临时件在 .runtime/tmp/st-acure-b1/）✓；单命令时限内 ✓。
