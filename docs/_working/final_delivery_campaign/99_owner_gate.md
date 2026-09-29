---
ttl: task_bound
title: "Owner 门位台账（宪法§5，只登记不代裁）"
session: st-finaldel-chief-20260929
---

# Owner 门位台账（99_owner_gate）

> 各矿道登记汇总；宪法§5 优先于"不留待裁"指令。醒后按序批即可，全部不阻塞链路。

| # | 事项 | 来源 | 建议 | 批复结果（日期/裁定/执行状态） |
|---|---|---|---|---|
| 1 | 4 台 disabled 门翻 enabled（CAPABILITY-OVERLAP/GATE-VOCAB/PERMANENT-SYSTEM-TRIGGER/ALGO-FLOW-LINK；红五簇撞号已被 98ce6370c5 治愈） | M2 特别核验 | 技术阻力已消，可批翻 | | 2026-09-30／裁定#431 第①项／已翻 enabled（in_process 册 4 台 true，st-finaldel-ownr1 队列落地） |
| 2 | CH 实弹批：#20 换源实弹/intake_ledger_recon rebuild/apply_market_tables_ddl --apply | M4 | CH 已存活，批后按 DATA-OPS 三步验证执行 | | 2026-09-30／裁定#431 第④项／已批三件，数据车道按三步验证执行（本道只登记不代执行） |
| 3 | W-178 板块宇宙真源裁定+gap134 补齐 | M4 | 波12 点火硬前置 | | 2026-09-30／裁定#431 第⑥项／真源已落册=UNI-SECTOR-880-001（universe_registry v1.2.4：880+881 行业主轴 729=601+128，概念 375 独立族不混）；gap134 补齐归 M4 车道施工 |
| 4 | T1 定稿拍板（3700 格 manifest 已全 pass，计数前置已消化） | M4 | 只差 Owner 签 | | 2026-09-30／裁定#431 第⑦项／定稿已签（w61_t1_scorecard 叶簿注记+93_owner_menu §② 闭合） |
| 5 | C266 终局§4 约 60 项清单源文件三处皆无（源文档 Owner 令删+备份 TTL 已过） | M5 | 需 Owner 重供或授权按桌面总清单重建 | | 2026-09-30／裁定#431 第⑭项／已授权按桌面总清单重建（重建施工归 M5 车道） |
| 6 | C148 rules_integrity_db 出库（Owner 已批②，处方已立含再注册白名单前提） | M5 | 批后 C2 波执行 | | 不在裁定#431 十六项逐项清单内（未获本批新授权）——维持原依据"Owner 已批②"，C2 波按原处方执行 |
| 7 | 退役执行类/级联立法/C96 凭据/C108 执法通电等 12 项 | M5 | 见 workorders_docs_misc §OWNER_GATE；**执行回填(2026-09-30 st-finaldel-retire)**：C267 非币圈面已执行、C22 已销账（详见 §执行回填）；C55/F51 币圈挂起归 G 道 | | 2026-09-30／裁定#431 第③⑩⑪⑫项／已批：C108 通电；C96 证据追认补录=裁定#434；C187 追认=裁定#433；C163/C25/C83/C295/C267 非币圈退役=先归档后删（执行面=下节 st-finaldel-retire 回填）；C55/C169/C328/C343 不在逐项清单内维持原门位 |
| 8 | C25/C98/C27/C115/C163/C427 治理门位 6 项 | M2 | 见 workorders_governance | | 2026-09-30／裁定#431 第⑫⑮⑯项／已批：C25/C163 非币圈退役=先归档后删；C98/C115=出清单待 Owner 勾选（清单出后勾选权在 Owner）；C27/C427 不在逐项清单内维持原门位 |
| 9 | C344 补 4 日期数据/C324 EV 施工令/C439 补 134 生产写 | M4 | 数据门位 | | 2026-09-30／裁定#431 第⑤⑧项／补数批（C344 补 4 日期+C439 补 134）已批；EV-02~06 施工令签发已批（C324 为其工单载体），执行归 M4 车道 |
| 10 | C355/C408/C444 提交链门位 3 项 | M3 | 见 workorders_commit_clean；**执行回填(2026-09-30 st-finaldel-retire)**：C444 已封矿（2733 件→G:/zephyr_cold/dead_archive_final/，详见 §执行回填）；C355/C408 非本道 | | 2026-09-30／裁定#431 第⑨⑫⑬项／C408 追认=裁定#432（79 件解除未登暂缓）；C444 封矿已批（退役道已执行回填见下节）；C355 非币圈退役=先归档后删 |


> **批复补充（2026-09-30，st-finaldel-ownr1-20260930 落册车道）**：总批复=裁定#431（ruling_registry.yaml；#432 C408 追认/#433 C187 追认/#434 C96 证据追认补录 同批在册）。表外批复状态：①FMS-HYGIENE 翻 block=达标即翻——实测连零 2/20 未达 BLOCK_FLIP_CLEAN_STREAK=20，block_flip_eligible 机读=false，维持 warn 不翻；②C22 销账口径主体在 E 盘（裁定#431 第⑮项，与下节退役道实测互证）；③C98/C115=车道出清单、Owner 勾选，不代勾。

## 执行回填（2026-09-30 st-finaldel-retire-20260930，Owner 已批"先归档后删"）

| 卡 | 执行结果 | 凭证 |
|---|---|---|
| C444 dead_archive 封矿 | 9 目录+1 jsonl=2733 件/25,979,998B 复制→逐件 sha256 双向核验（0 差异）→源删除；blob 引用 14,072 hash 留证于 MANIFEST 附录 | G:/zephyr_cold/dead_archive_final/MANIFEST.md；00_manifest/drawers.jsonl 已登记 |
| C267a F130 ml_serve 净删 | 净删面勘误：案卷 TC=0 与盘面不符——tests/ml_serve/ 4 件在册测试实消费 4 实体件，净删面=4 src+4 tests=8 件；git rm 已入队列袋（登记面 5 册 52 条 dangling 引用移交维护班：module_translation 17/candidate 10/capability_canonical 18/functional_domain 3/wiring 4） | G:/zephyr_cold/retire_c267_20260930/F130_ml_serve/MANIFEST.md（同构镜像+sha256）；双同名 clone 事实随归档留证，gov_drift 侧存活 |
| C267b 死库+空壳表 | 七 0 字节库（census 7 库非 6）只归档不删，处置移交 C 道 S-02/03；空壳表 C267 卡"8 张"=blockage:121 旧点名，wave3 strict 权威口径=13 张确证 0 行+suspend 翻案(36 行)剔除；CH VM 172.24.30.100 双端口不可达，未代开机（Ollama 先例），live 导出步移交 | G:/zephyr_cold/retire_c267_20260930/{zero_byte_dbs,shell_tables_c1_market}/；HANDOVER_TO_C_LANE.json（裁定 #311/#328 三步验证口径） |
| C22 15G 销账 | 销账口径：15G 主体=Qwen2.5-7B-Instruct 基座在 E:/ai_cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct（实测 15G，非消失）；95M 残留=models/qwen25-7b-sft-v1 项目自训 LoRA 适配器（adapter+checkpoint-800），被 ml_train/sentiment_sft_trainer.py+3 ml 脚本实消费=活资产保留，无需归档 | 本行+workorders_docs_misc C22 行尾双登记 |

## 币圈专项（2026-09-30 Owner 令）

> Owner 2026-09-30 口谕：币圈模块不建门禁系统，只在模块表头加通知；所有币圈相关删除/退役全部挂起，等 Owner 通知后再议。登记人 st-finaldel-crypto-20260930。

| # | 事项 | 状态 |
|---|---|---|
| 1 | C55 ig_equity_edge 旧表净删 | **挂起**（等 Owner 通知；出处 workorders_docs_misc §OWNER_GATE C55，本节登记不代裁） |
| 2 | F51 币圈退役（C267 退役批中币圈部分） | **挂起**（等 Owner 通知；同上不代裁） |

表头通知已加清单（2026-09-30，仅注释/引用行，零逻辑改动）：
- docs/03_modules/_domain_data/algo_flow/：crypto.yaml、crypto_event_calendar.yaml、crypto_profile_provider.yaml、crypto_universe_selector.yaml、okx_provider.yaml、okx_swap_provider.yaml、onchain_provider.yaml、sentiment_panel_provider.yaml
- docs/03_modules/_domain_execution_core/algo_flow/crypto.yaml
- docs/03_modules/_domain_frontend/acceptance/ACC-F-CRYPTO-CM-ENGINE.yaml（币圈组引擎验收单）
- src/zephyr/data/config/tasks.yaml（crypto 影子 MVP 段 / Hyperliquid D5 段 / 恐贪段三处注释横幅）
- 跳过未动：docs/_working/2026-09-11-crypto-shadow-mvp.md（工作区脏=他会话在飞，按纪律回避）
- igdrop：全仓 grep 零命中，无现存资产可挂表头
