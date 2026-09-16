---
ttl: task_bound
completes_when: 八分包超级长城任务全线端到端交付完成后，本方案归档为整合施工真源（终验证据与裁定链可溯）。
---

# 超级长城任务·八分包全线端到端整合方案 v1.0（2026-09-16 通宵班）

> 总包：st-overseer-20260916。Owner 睡前授权令全文生效（执行+循环检查+红蓝+GitCommitGateway 落地+零遗留）。
> 编制：8 个分包 → 按文件冲突矩阵合并为 11 个执行车道（GW1-GW11），波次派发（并发额度 2-3 实测上限）。

## 一、分包编制与终态总表

| 车道 | 承接分包 | 终态 | 核心凭据（commit） |
|---|---|---|---|
| GW1 Kronos 微调全链 | 分包一 | ✅ 全链贯通：CH→prep→pkl(17 标的/16948 训练窗)→tokenizer→predictor→换装→adapter 冒烟；val loss tok 0.0155→0.0140、pred 3.409→3.353（MOD-BT-204 双验收达成）；26 测试×2 绿 | 3c63409a+vendor fdeae5c |
| GW2 资源排班 B1-B4 | 分包二 | ✅ 一库一器一闸一图全落地：58 实体×18 字段注册表+零侵入采样器+三码冲突闸(own-scope)+周历视图+ops 通道告警桥；backtest-run 接 E0 实盘冒烟；端到端六环节全 PASS；52 测试×2 绿 | aa253167/6ed8b2bb/9521af65/6be45220/3cde9547 |
| GW3 治理加减乘除收官 | 分包三 | ✅ A2 告警接 promotion 页(15/15 E2E)+A1 nssm 废弃归档+M1 孵化即登记+M2 水位门+M3 收割闭环+M4 llama 崩溃溯源+VRAM 预算门；裁定#255/#256；两轮 257 passed | a6cf1aad/8a8d0654/6044c47f/a164befb/79faf9a9 |
| GW4 量化七裁定 | 分包四+五⑪ | ✅ 北向停两任务留表+chip 量纲治本回 trial(VWAP 界内率 0→5272/5272)+pf_alloc 挂触发+daban 地基 P0+ALG-01 重做(检出力分位 12.6→99.6)+WYF-1 复验 SC=4；WYF-3 按裁定前置条件跳过（产能耗尽，诚实登记）；2235 测试×2 绿；裁定#257 | 59f45690/3dcfe9dd/d285958c/4c218369/0c5f691a |
| GW5 metamorphic+mutation | 分包五⑬ | ✅ 63 条不变式测试（价格缩放/置换/四闸置换/效应量-p 单调）三轮全绿；mutation 手写 12 变异体杀伤率 50%→整改 100%；F-1 缺陷特征化移交 | 30a8c433 |
| GW6 全景图收口 | 分包六+五⑫ | ✅ 僵尸处置（R1 三库退役+R3 三库归档+PAN-BUILT 死对象）+数据质量子环节落图+主索引 44→55 对账清零+R5-R7 登记；裁定#258-#263；align_all 连续三轮硬 0 | 35ffcb91/6966e258/be7898e9/487607f8 |
| GW7 ALGO_FLOW 批9 | 分包七 | ✅ 批9 三笔 707 文件（354/354 源码锚，总包预审计发现"票B 从未执行"后补做）+出仓器两代 bug 治本+ALGO-FLOW-LINK 新门禁；域测试 49+2777+449+2423 全绿 | a1322846/a68a71ff/9a36c094/0e6ae5c7/906496b8 |
| GW8 F-06 收尾 | 分包八 | ✅ 批7 落地+红蓝补刀（dispatcher 排空兜底）+原挂点 full_lifecycle_e2e 33 passed EXIT=0 根治实证 | 641c5bd5/f5cab615 |
| GW9 测试基建稳定化 | 总包移交 | ✅ infrastructure 子进程泄漏治本（boot_hooks 孵化 launcher 泄漏+9/boot）→全量首破 1968/1983×2 轮 EXIT=0 reaper 零击杀；audit 事件循环泄漏治本→4 轮 1615 passed 0 失败；GW8 跳过#1/#3 销账 | 2bb55319 |
| GW10 orchestrator 域 | 分包七 T4 | ✅ 73=73=73 全对齐出仓（148 文件）+同族映射雷批级预判修复；红蓝双向实证门禁；482/495×2 绿 | 36de8a4c/249a430c |
| GW11 分包七三小项 | 分包七 T5/26 | ✅ events.jsonl 三步验证后登记不执行（活哈希链+既存 37845 处损伤取证保全）+PANORAMA-ALIGNMENT 独立复核（晨班已修，正反例验证）+ALGO-NOTE-SYNC 超窗归因治本（8 单测+2452 零回归+实弹） | 16befe06/cc386251/c19a61f0 |

总包直接施工：8d65b8e1（注册表同步尾代提）、a3de2601（GW8 跳过#2 计数测试治本）、33b9593a（F-1 修复+depgraph 梯子转正）、4453bf16（整合批①）、f299d2fa（整合批②）。

## 二、五角星接线拓扑（八任务成果互联方式）

五角星=任意两任务成果互相可达。今夜建成的跨线线路（每条含证据）：

1. **Kronos×资源排班**：训练重活 manual_kronos_finetune 入画像注册表（GPU/gpu_default 互斥组，GW1 实测口径，4453bf16）+reaper keep 三条保护面对齐采样器观测面。训练排班从此过闸、可被采样、可与 FactoryLaneC/C4 考试互斥检重。
2. **Kronos×治理守护**：训练进程受 reaper keep 保护，而 reaper 收割闭环（M3）只杀超寿未登记进程——保护面/收割面同一真源；换装冒烟指标（sharpness/pit_ks）留证给 E4 考尺裁定（结论权在考尺，微调线不越权）。
3. **资源排班×治理告警**：B4 冲突告警桥写 ops_alert_feed 通知板（GW3 A2 建的通道）→/api/ops-notifications→promotion 页横幅+晨审直读；水位门 SpawnWaterGate 阈值引用 resource_optimization.yaml 不收编（单一真源）。
4. **资源排班×E0 闸×工厂**：backtest-run 端点接 classify_window（交易日盘中拒重算，6ed8b2bb 实盘冒烟）→"面板隐藏重算入口"盲区关闭；工厂 16 计划任务+数据 21 槽位全部入画像（ps1 触发器解析器）。
5. **治理孵化闭环四层合围**：M1 孵化即登记（父 PID/寿命/进程树）→M2 水位门（≥85% 等待/≥90% 拒孵）→M3 收割（超寿树杀+回写）→M4 VRAM 预算门（llama 0xc0000005 同族崩溃防护）。四层消费同一登记 ledger，零 cron 零 sleep-loop（事件触发）。
6. **量化裁定×TDM×注册表**：chip 四处声明面回 trial、pf_alloc 三触发条件挂起、北向两任务停用——代码/注册表/TDM 注记三面同 commit 原子（裁定#257⑤②⑧）。
7. **量化×ALGO_FLOW**：GW4 修 TDM 注记被 GW7 批9b 吸收→GW7 9c 恢复归属并推进 note_confirmed（共享暂存区吸收现象的正面处置实例）；ALGO-NOTE-SYNC 归因窗缺陷由 GW5/GW4 实证、GW11 治本（cc386251）。
8. **审查方法论×量化真源**：GW5 metamorphic 不变式钉 pattern_evidence_certifier→mutation 试点暴露 F-1 边界缺陷→总包治本（33b9593a）——审查发现→施工修复→测试转正的完整闭环。
9. **全景图×全部**：GOMAP 再生收录今夜全部新模块（f299d2fa0d）；align_all 六维硬 0=全图全库对齐终验；僵尸库归档死链 grep 举证（良性残留全部留痕）。
10. **ALGO_FLOW×门禁**：427 个 external 锚（354+73）受 ALGO-FLOW-LINK own-diff 硬校验，GW10 红蓝双向实证（yaml 丢失/坏块→BLOCKED）。
11. **测试基建×全线**：批7 fail-open+dispatcher 排空兜底（GW8）+infrastructure 子进程保收（GW9 conftest）→全量 tests/infrastructure 单进程首破；audit 循环保收→顺序噪声归零。GW8 三跳过项全部销账。
12. **资源排班×测试基建**：GW9 红蓝抓到资源车道在途中间态 import 错（等其落定后两轮零失败）；GW2 e2e 管道句柄泄漏被总包治本（4453bf16）——车道间互相红蓝、互相收敛。

## 三、挖矿 SOP 自审（挖后自审闸，三态=施工已执行）

- **终局全貌量尺**：Owner 终局只做四类事（账号/API 申请/充值/转正审批）。今夜产出全部朝零人工收敛：微调全链自动化（含换装回滚保险）、排班冲突自动阻断+告警、进程孵化-收割全自动、门禁归因自动化。残留人工点=Owner 门位级（Ollama 升级/注册表扩行/审计链取证后处置），符合分级设计。
- **过度工程审查**：整合未建任何新系统——全部接线复用既有通道（ops_alert_feed 板/keep 清单/depgraph 梯子/gate own-scope 模式）；采样器零侵入（reaper 同款 cmdline 匹配）；拒绝项=不建 Prometheus 服务器/不做分布式调度（方案 §5 封矿留痕维持）。
- **三态裁定**：整合段需施工项（F-1/Kronos 入册/GOMAP 收敛）全部施工；需 Owner 门位项（Ollama 升级、审计链取证冻结、蓝图 AUTOGEN 模板治本归属维护班）全部登记不越权；无挂起待裁项新增。

## 四、终验证据（总包终验，2026-09-16 晨）

- align_all 六维硬 0（domain_mismatches/ghost_anchors/frontend_map/decision_map/factory_map/gomap）。
- 跨线 E2E：ops_alert_feed 15+资源排班 e2e 1=16 passed；AutoRuntime Core+E2E 37 passed（atexit 收割干净）。
- 计数一致性 9 passed；资源注册表 --check 无漂移（58 实体）；reaper 存活 killed=0。
- 全部 60+ 笔提交经 GitCommitGateway 落地，逐笔 git log -1 --name-only 归属核实（各车道汇报+总包抽查）。

## 五、移交清单（非遗留，均为登记留痕的门位/维护班项）

1. **审计链取证**（GW11 新发现）：data/audit_trail/events.jsonl 自事件 #26810 起 HMAC 失配 26,909 条+#35156/#53721 起链断裂，疑多写方并发 append 互踩——取证完成前冻结一切轮转（16befe06 留痕）。
2. **Ollama 版本升级**：M4 归因根因修复，软件安装=Owner 门位（a164befb 报告 §5）。
3. **蓝图 AUTOGEN 模板治本**：28 个既有蓝图同款模板 bug（失效 AGENTS 编号引用循环重建），根治在 sync_blueprint_code_index 模板=维护班（GW2 ⑥）。
4. **transport blueprint_id 落位**：机制性阻断（唯一约束+三轨制），94 号批 MOD 转正时随扫描落位（裁定#262）。
5. **外来在途件**：daban auto-mount/intake 报告 staged+probe 卫生提交（3e1ff4c/78cf40f/35d792c）属 commit-pipeline 外来车道，按 §3.4 不代修。
6. WYF-3 阈值重校（裁定#257⑥ P2 搭车未触发）、daban 四引擎应用层（#257⑤ 挂起）、RSC-2 口径——均按裁定登记，非欠账。
