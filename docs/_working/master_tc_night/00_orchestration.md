---
ttl: task_bound
completes_when: 总包夜战战役(master_tc_night)归档收尾
---

# 总包夜战 orchestration（st-mastertc-20261006）

> **Owner 授权**：2026-10-06/07 对话令——全部未关闭任务开工、五大队并行、遇阻自裁、不中断直至全绿交付；裁定落册见 `rulings_master.md`（RULE-RULING 同 commit 原子）。
> **输入**：桌面《未完成任务施工清单_2026-09-29.md》2026-10-06 复核版（126 条 = ❌56/🔶38/⏳32）+《遗留任务全量核验总清单》（复核后 136 行）。
> **基线**：HEAD `014ccf5b18`（2026-10-07 03:04，开战时点）。

## 一、执行序（线内先挖后干、线间并行流水）

1. **W0 总包底座**（本文件+token 批+裁定册批+免死登记）——总包直办。
2. **W1 挖矿 chief**：产 `01_skeleton/00_环节总表.md`（全流通环节 taxonomy：环节数/父子模块/上下游），并复核 126 卡分类无遗漏；发现新缺口即立卡（不扩 Owner 面）。
3. **W2 并行施工车道 L1-L11**：每车道一册作业簿（模板见 §四），卡卡过六向台账+自审闸三态；**GREEN 即施工**，WAIT 挂依赖，RED 登记+跳过。不等总包逐卡点头。
4. **W3 循环检查**： impacted 域 pytest + align_all + gate 自洽，修复后复跑，**连续两轮 0 失败=过**。
5. **W4 红蓝对抗**：复用 tests/governance/redblue_* 框架对本夜 diff 面（own-diff 作用域）打一轮，问题即修。
6. **W5 收尾交付**：队列 drain 状态、总包临时文件清理（只清自家）、`99_delivery/交付报告.md`、向 Owner 端到端汇报。

## 二、车道分工（126 卡全量分派，卡号=施工清单卡）

| 车道 | session | 卡 |
|---|---|---|
| L1 治理A | st-mastertc-l1 | C97 X01 C157 C244 C323 C245 C128 C27 |
| L2 治理B | st-mastertc-l2 | C268 C346 C443 C461 C304 C338 C150 C202 |
| L3 提交链 | st-mastertc-l3 | C02 C05 C147 C152 C248 C300 C330 |
| L4 文档终报 | st-mastertc-l4 | C30 C61 C129 C192 C247 C226 C341 C342 C419 C430 C453 C266 |
| L5 数据库 | st-mastertc-l5 | C11 C122 C156 C241 C242 C378 C324 C120 C121 C299 |
| L6 工厂 | st-mastertc-l6 | C46 C75 C232 C234 C235 C252 C253 C383 C400 C106 C191 |
| L7 回测 | st-mastertc-l7 | C33 C34 C216 C236 C237 C238 C239 C288 C452 C107 C199 C205 C233 C251 C70 |
| L8 退役+AI | st-mastertc-l8 | C267 C412 C169 C301 C394 C462 C475 C39 C84 C85 C96 C136 C314 |
| L9 清洁+FMS | st-mastertc-l9 | C161 C28 C127 C473 C62 C189 C183 C325 C343 C440 |
| L10 裁定台 | st-mastertc-l10 | ⏳ 全量：C19 C21 C24 C36 C37 C38 C45 C63 C65 C81 C82 C102 C103 C109 C287 C320 C398 C445 C490 C441 C410 |
| L11 测试重收编 | st-mastertc-l11 | C263 C16 C56 C155 C10（与 st-tests-chief 协调） |

## 三、硬纪律（所有车道，违者产出作废）

1. **冷启动**：PATH=Python312；动手前 `python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status`。
2. **claim→改→commit→release**：改前 `lock_files.py acquire <file> <本车道sid>`；锁冲突（他队在途）=该文件 RED 登记+跳过，禁抢禁等死。提交唯一正门 `python scripts/git_commit.py --session <sid> --files <清单>`；失败带 `--adopt-prior-work` 重试；仍忙走 `python scripts/commit_queue.py --enqueue`（换新袋号）。commit 后 `git log -1 --name-only` 核实归属。
3. **新建文件**：working 区统一放 `docs/_working/master_tc_night/`（token 已批覆盖）；其他位置新文件须先 `batch_creation_tokens.py` 登记 token（tests/ 豁免）。
4. **热册**（*_registry*.yaml、ROOR、ruling_registry、宪法、trackers）：必 `safe_write_text`（src/zephyr/shared/io/file_utils.py）。
5. **禁区**：不碰他会话 staged/modified 文件（git status 里非本车道 claim 的）；不碰 st-tests-chief 的 tests/ 重排中间态（L11 除外，须先 list 锁）；不删任何物理文件/目录/表（标记+隔离制）；不翻 flags（L10 裁定台除外，按裁定附表）；禁裸 git reset/checkout--/restore；禁直写 .runtime 根；测试输出走 tmp_path。
6. **裁定**：车道无法裁 → 写入本车道 `OPEN_QUESTIONS` 段并跳下一卡；只有 L10 可登记裁定（取号器 `--claim --session st-mastertc-l10` + ruling_registry safe_write_text + 同 commit）。
7. **数据库**：一切 SQL 经 DatabaseService；破坏性操作三步验证；本夜禁新 DROP（已批 D1 清单除外）。

## 四、作业簿模板（每车道 lanes/LX/00_workbook.md）

每卡一小节：**六向台账**（①卡面处方 ②HEAD 现状实证(命令+结果) ③上游依赖 ④下游消费者 ⑤冲突面(锁/staged/他队) ⑥残余与移交）+ **自审闸**（GREEN 挖干施工 / WAIT 等依赖 / RED 冲突登记跳过）+ **施工记录**（commit 哈希、测试读数）。车道尾部：`OPEN_QUESTIONS`、`CONFLICT_LEDGER`、`DONE_SUMMARY`。

## 五、Owner 保留门位（本夜禁代裁，登记即关账）

实盘资金/生产流转三件：C63 实盘拒单启用、C287 实盘准入 live。物理删除三段式三件：C109 F 盘 716G 摘除、C410 清盘真删、C267 剩余 0 字节库真删（归档+留档可做）。VM 依赖两件：C36/C37（VM 离线）、C45 intake_ledger_recon rebuild。以上按「登记+跳过」处置，晨会呈 Owner。

## 六、其余 ⏳ 代裁基准（L10 落册用，依据=宪法§9.11 通道+Owner 对话授权）

C81 L07-C03→收编唯一（HANDOVER_INSTRUCTION 建议）；C82 L08-C03→接线（有注入点）；C398 F119→双引擎并存至 10-08 继任窗复核；C102 排产账本→TTL 面+PG 外镜像；C103 OrderFileStore→quarantine 语义（隔离可恢复）；C19 severity 变体→维持 warn+登记台账；C21 AutoRuntime→维持封存；C24 ROOR 8 候选→仅批带 successor 且零消费者的净删候选，余维持；C38 D 盘→维持现状+周报；C65 余菜单→按 99 册建议逐条批；C320 图15 human_gate→按 risk_tier_registry 默认 medium 落册；C445 相位判别器→AI 侧施工，判据暂记"判不出=记红不拒单"；C490 镜像树迁移批 W0+165GiB 豁免按归档处方批，8 候选并入 C24 口径；C441 词表门 block→判据已改写（BLOCK_FLIP_CLEAN_STREAK=20）批准翻转；immutable_tree 24h 实测汇报补成册；AI 进化点火维持封存至 W6 窗；C300 commit_queue_interactive→维持现状（已 enabled）+窗口=下维护窗；C410/C109/C63/C287/C36/C37/C45→Owner 保留（§五）。

## 七、挖干判据与交付判据

- **挖干**=该卡作业簿六向台账齐+自审闸三态有裁定。
- **完工**=代码/文档落 HEAD（正门 commit 哈希）+ 相关 pytest 绿 + 台账回填。
- **全绿**=循环检查连续两轮 0 失败 + 红蓝一轮 own-diff 面零未修复项。
- **交付**=`99_delivery/交付报告.md`：车道汇总、裁定清单、Owner 保留清单、残余（应为 0 或已登记移交）、队列/锁/临时文件终态。
