---
ttl: task_bound
title: QMine 战役环节总谱（骨架·封矿版 v1.0）
session: st-qmine-20260925
---

# QMine 战役环节总谱（未来优化矿 15 座 → 7 环节）

> 挖矿 SOP 合规：母节点=QCure 长尾矿全量开发；六向寻路按 mining_sop_policy §2；
> 封矿判据=矿脉枯竭；自审闸三态=施工/挂起排期/方案封矿。
> 基线=QCure 战役 10 本作业簿（docs/_working/qcure_campaign/，已落 HEAD）。
> 六路挖矿代理产出七本作业簿（本目录各子目录 workbook.md）。

## 1. 环节清单与三态裁定汇总

| # | 环节 | 作业簿 | 裁定 | 今晚施工范围 |
|---|------|--------|------|------------|
| 1 | 热册合并器内核（头号矿） | 01_hot_registry_merge/ | 施工分两批 | 批1=合并器改造+对账器+env逃逸口+gates计时；批2=数据heal（撞号裁定） |
| 2 | 登记册数据卫生 | 02_registry_hygiene/ | 施工（收缩范围） | 0x08脏字节直连+枚举合法化+severity映射；字段改名486条挂起（消费方未审）；ruling decided 9条挂起（保护册） |
| 3 | 队列健壮性 | 03_queue_robust/ | ②③施工①挂起 | requeue_lineage审计+环境逃逸封堵+级联标记影子文件MVP；depends_on排序锁挂起（等生产者规约） |
| 4 | blobs 退役通道 | 04_blobs_gc/ | 施工 phase1 | blob_gc.py（Z类孤儿∧>7d→归档，dry-run默认，~880MB） |
| 5 | 观测面 | 05_observability/ | 施工×4 | gates相位计时+trigger注入校验+预检sha缓存+schtasks对账件 |
| 6 | 业务扶正 | 06_business_revive/ | ②③施工①明示 | 仪表盘心跳+DeadmanSwitch第6路+QMT判据移交；AutoRuntime维持手动+宪法明示（常驻化双裁定封存Owner窗口） |
| 7 | 文档漂移 | 06_business_revive/ §④⑤ | 施工（议题批文） | 新立#ARCH-AGENTS-SSOT-DRIFT-001修AGENTS.md三处（8子命令/commit_queue 6子命令/仪表盘真源） |

## 2. 挖矿重大发现（超出矿单的新矿）

1. **36/71 册自带 unique_key 声明而合并器零消费**——身份键规范的 SSOT 一直躺在册里（治本=声明驱动）。
2. **6 册 14 块 dict 形态活雷**（{tags:[...]}/{scan_roots:[...]} 首字段非标量）——现行代码触册即死。
3. **HEAD 在册 2 个撞号真雷**（REG-DATAFLOW-001×2、CAND-GOVTEST-005×2）——触册必死。
4. **infrastructure_registry 0x08 脏字节**致整册解析失败（HIGH）。
5. **38 笔环境类失败经 generic 分支绕过全部计数闸**（逃逸口）。
6. **capability 107 处多 token 全部合法**（QCure 疑虑解除）；精确重复全仓=0（排雷验证通过）。
7. schtasks 对账件首扫即见红：DailyBackup=267014、ProcessReaper=1 等四处（RULE-GUARDIAN 承重件需核处方语义）。

## 3. 施工线编排（文件所有权互斥）

| 线 | 所有权 | 交付物 |
|----|--------|--------|
| A1 | scripts/governance/commit_queue_landing.py | 合并器三层身份键（unique_key声明驱动+dict passthrough+侧内判等去重）+render自检+env逃逸口封堵+gates相位计时 |
| A2 | scripts/governance/registry_dedup_audit.py（新）+2撞号数据heal | 对账器（--heal-equal/--report）+2撞号裁定治愈 |
| C | scripts/commit_queue.py | requeue_lineage审计字段+级联标记影子文件（.stale/ O_EXCL）MVP |
| D | scripts/governance/blob_gc.py（新） | blobs退役通道 phase1 |
| E | scripts/governance/gate_auto_registrar.py + commit_preflight.py + scheduled_task_reconcile.py（新） | 注入校验+预检sha缓存+schtasks对账件 |
| F | src/zephyr/frontend/dashboard/** + deadman 相关 + AGENTS.md + architecture_issue_registry.yaml | 仪表盘心跳+Deadman第6路+AGENTS.md三漂移修正（议题批文） |
| G | infrastructure_registry.yaml + strategy/rule_catalog等册schema注释 + severity映射批 | 0x08直连+枚举合法化+severity 141映射 |

**落地顺序**：token批（全部新文件）→文档批→G直连件（0x08）→代码批并行→红蓝→收敛。

## 4. 明确不施工（本战役裁定）

- AutoRuntime 常驻化：维持手动+宪法明示——常驻≠自动交易（sim 链已全自动），启用看门狗有双裁定封存的 Owner 窗口（CAND-GOVSEC-002①+注册 Disabled），翻开路径写入作业簿待 Owner 窗口。
- #410 续期：到期自动收紧为安全默认；已建对账面可见，续期须 Owner 裁定（10-08 前）。
- 字段改名 486 条：消费方未审计，盲改=破坏读者；挂起待消费方审计专包。
- ruling decided/void 9+2 条：protected 册+消费者语义（resolver 认 active），数据合法化随枚举立法下批。
- depends_on 排序锁：设计定稿，等生产者规约（M3.4）合流后排期。
- files_trigger 死触发 3 门 6 条（password/api_key 零命中）：需 Owner 定性守卫对象，登记不擅动。

## 5. 验收口径

1. 全部施工件测试绿+连续两轮全量收敛零失败。
2. 红蓝对抗至零残留。
3. 0x08 修复后 infrastructure_registry 可解析；2 撞号治愈后触册袋不再死。
4. blob_gc dry-run 报告与挖矿账本对拍；schtasks 对账件出三色首报。
5. GitCommitGateway 全部落地+临时文件清零。
