---
ttl: task_bound
completes_when: 总筹消化本 facts 批（并入 F2 挂载/内收对审证据位）后，本件转归档
title: 图9 策略工厂 车道F3 facts 抽取报告
owner: ZephyrAlpha-Owner
session: st-map9-f3-20261003
---

# 图9 策略工厂 车道F3 facts 抽取报告

> 会话 `st-map9-f3-20261003`｜2026-10-03｜前置门已验：`fac9_01_mount_candidates.yaml` 在 HEAD（db394dfb23）。
> 产出：`fac9_03_facts.yaml`（trigger_facts 磁盘实测 + 8 条 DB 查询处方 + 330 台消费面扫描 + 零/弱消费三节）+ 本报告。
> 纪律合规：全程零 DB 连接/零裸 SQL/零 duckdb——只有文件读与文本扫描；DB 计数全部以查询处方成节移交总筹代跑。

## 一、计数（与 yaml counts 一致）

- 范围 330 台（verdict 1/2/3）；有 py 指针已扫 256；无 py 指针未扫 74（cfg:/域册/纯册面，清单在 yaml）。
- 消费面分布：**零消费 89｜仅测试消费 62｜弱消费≤2 64｜活消费≥3 41**。
- trigger_facts 三组 21 项磁盘实测；DB 处方 8 条。

## 二、trigger_facts 要点（磁盘实测，每个数带来源指针于 yaml）

**进货侧（E1 车道量能）**：raw_manifest=598 行（车道A 社区货源，吻合图9 注"已收 597 条"）；lane_b=16｜lane_c=17｜lane_c2=9｜lane_chain=11｜three_high=41｜**lane_f=3701（F06 网格量产主力）**｜lane_g=1（+seen_urls=6）；grid 批次 29 个、manifest 合并 24667 行、negatives 阴性在案；translated_manifest=6｜constructed_manifest=2｜c4_deferrals=322（缓考队列）；screen_c2=598。

**考试/在库侧（E4-E7 量能）**：runs/ 批目录 191（SCR-C4×31、SCR-DEV×54、SCR-SIMGOV×53、SCR-OUTPOST×20、SCR-LIFE×3、VAL-×24、E4-×4）；父目录 bt-*.json=60+bt-fw=27+bt-tick=2；fw-auto=6；drills=4；league 判断文件=4；t0_rule_engine=266 文件。strategy_registry.yaml=**161 条**（lifecycle: candidate 151/backtest 8/**sim 仅 2**；status: active 19/candidate 139/deprecated 3）；trial_ledger=8 runs；管线事件journal=1 行（排水后近空，事件机制在跳）。

**内收证据位（零触发实锤）**：`factor_casebook.db` 盘面**零命中**——MOD-L02-027 病历册有蓝图无实例（§3 完备性红）；MOD-BT-195 kronos_adapter 零消费+图9 自注"网络恢复后激活"=登记性停机。**E7 咽喉量能警示：sim 生命周期仅 2 台 + OUTPOST 批 20 次**——E6→E7 的转正漏斗几乎没流过水。

## 三、DB 查询处方（8 条，禁直连已守；交总筹代跑）

`c1_backtest.strategy_screen`（E4 主台账）/`hypothesis_precheck`（E2）/`sim_daily_report`（E7）/`regime_snapshot_history`（E8 输入）/`alloc_budget_daily`（E8 sleeve）/`decision_daily`（BT-212）——完整 SQL 在 yaml `db_prescriptions` 节，每条带 note（过滤建议+列名实勘提醒）。特别提醒：`strategy_registry` 是 **YAML 册非 DB 表**（intake.py/registry_writer.py 直写 yaml，ROOR REG-STR-001），勿开 DB 查它。

## 四、consumers 扫描——先读判读口径再读数字

**口径**：语料=src/scripts/tests/config 的 py+yaml（9390 文件），已剔除 6 张地图文件（挂载指针不算消费）；匹配=import 全路径/父包导入/同包相对导入/路径字面引用/同目录平铺 import；tests 单列不计入"活"判据。

**关键判读（防误杀）**——零消费 89 台分三种形态，处置完全不同：
1. **翻译件/验收集族（~70 台：BT-043..075、102..186 等）零 import=预期形态**：它们是被 c4 批测 runner 按 manifest 调度的考卷件，不被人 import；触发证据=translated_manifest/screen_c2=598 行/SCR-C4×31 批。内收对审时**不该按零消费判退**，应按验收集扩容/退役策略走 E3 域规则。
2. **CLI 入口脚本零 import=预期形态，但触发要看产物**：lane_b(16 行货)/lane_c(17)/090 三高(41)/F 车道(3701+29 批)=**有货即活**；反向实锤=MOD-BT-195（登记停机）、league_judge（league 判断仅 4 文件，月度机制刚起步）、replay_drill/crisis_drill（drills=4，演练低频）。
3. **src 库件零 import=真内收红**：本次仅 **1 台——`src/zephyr/pf_alloc/core/sector_distribution_comparator.py`（板块分布比较选优，PA 家族）**：全仓（src+scripts+config+tests）零引用，纯孤岛。E8 族唯一实锤内收候选。

**headline 消费面**（活消费 top，完整在 yaml）：回测引擎机械面 af:vectorized_engine=51 引用（src21/scripts10/tests20）——E4 真主干；**LSG（MOD-LLM_SECURITY）手工补扫=97 文件引用（LSGSecurityGateway 直接引用 67 处）**——判据3 高置信直接坐实；MOD-BT-151 算力闸=9 引用（config×2+src3+scripts3）跨域被排班族消费；MOD-BT-154 进货编排=1（被 lane_g 编排调用，CLI 链）。

**MOD-BT-086 synergy_dedup 实测=仅 1 测试消费**（rg 复核：全仓只有 self+config 设施件+tests+1 个 tmp 残留）——图9 FAC-E5 唯一已挂机制是"考卷造出来还没接进流水线"状态，E5 环节血肉最薄（行数也最少：4 台），内收对审重点位。

## 五、移交总筹

1. **内收对审直接证据**：零消费三形态清单（yaml 三节）+真红 1 台（sector_distribution_comparator）+casebook 无实例+kronos 登记停机+E7 漏斗近乎无流量。
2. DB 处方 8 条代跑后回填 yaml `trigger_facts` 对应位（建议总筹把查询结果以附注落回本件，保持"机生+附注"一体）。
3. 74 台无 py 指针未扫清单在 yaml `modules` 节（note 字段）——多为 cfg:/域册/病历册面，其消费面=挂载关系本身，建议内收对审按 F1 verdict 面处置，不补扫。
4. 判读口径（§四）建议随 facts 件一起进 F2 施工单，防"零消费=判退"机械误杀考卷件族。
