---
ttl: task_bound
---

# 全流通挖矿战役 · 总筹册（00_orchestration）

> 立册 2026-09-25 凌晨 ｜ 总筹：st-commitspeed-tbl-20260924 ｜ Owner 终局令授权"线内先挖后干、线间并行流水，挖干即开工，无需逐条点头"。
> 本册＝挖矿战役的编排真源：模板、挖干判据、车道注册表、状态。**接手者先读本册再读各车道作业簿。**

## 一、目标（Owner 原话锚点）
1. 提交链支持未来 20+ 并发子代理多车道：不再堵塞/死亡/覆盖/蒸发/卡死，且速度必须提上去（当前 ~30s/笔仍嫌慢，门禁能合并的合并，持续自问还有什么能提）。
2. 全项目所有业务块+新建任务的所有链路全部打通：全模块、全通道、全管线灌水可运行。
3. 交付纪律：循环检查至连续两轮问题=0 → 红蓝对抗（出问题直接修）→ 零遗留/零待办/零待裁定 → 端到端交付。

## 二、作业簿模板（每环节一册；子类目可再开子册；放本目录各车道子文件夹）
```yaml
册头: frontmatter ttl: task_bound；文件名小写 snake；禁 .json 用 .yaml
一、环节定义与边界: 一句话+上下游（谁是供料方/谁是消费方）
二、六向台账: 上游输入 | 下游消费 | 自动化触发(cron/事件/daemon/计划任务) | 真源与注册表 | 门禁与质量尺 | 当前运行状态(绿/黄/红+实测证据命令)
三、子模块清单: 逐个 是什么/入口file:line/状态（用 ls+grep+注册表交叉验证穷尽，禁凭记忆）
四、堵点与病灶: 每条 现象/根因/修法草案/预估工作量/是否属本车道可修
五、提速与合并机会: Owner 令"能合并的合并"——重复册/重复脚本/可派生清单/同真源多消费
六、自审闸三态: 挖干可施工 | 待挖(列缺什么) | 待裁(问题+选项+建议)
七、复核命令: 别人如何 10 分钟内复核本册
```

## 三、挖干判据（三态裁决规则）
- **挖干可施工**：六向台账每向有实证（file:line 或可复跑命令输出）；子模块清单经两源交叉验证无缺；堵点有根因+修法；三态结论明确。
- **待挖**：任一向证据缺失→列出缺口清单继续挖（可再派子代理），不算完。
- **待裁**：判据语义/净删退役/资金/架构级取舍→按模板写入本车道 `pending_rulings.md`（一行一案：问题/已试路径/选项/建议），总筹先裁；总筹裁不了的留 Owner 晨报。

## 四、车道注册表（状态：待派|挖矿中|挖干|施工中|完工）
| 车道 | 环节域 | 产出目录 | 状态 |
|---|---|---|---|
| M0 骨架 | 全环节总册（交叉验证 TDM/ROOR/capability/SOP九族，找漏项） | 00_skeleton_fullflow.md | **收卷：76 环节/八段；覆盖 52/76→采纳后 75/76；待挖=扩展项未挖（各车道补挖波处理）；3 项待裁已由总筹裁掉（研究域不编入/管线路由 M4M5 互引）** |
| M1 数据链 | 采集→清洗→CH/PG/冷储→TDM 交叉轴 | m1_data/ | **挖干可施工**（7 册 12/12 环节；271 采集任务/252 CH 表/89.5 亿 tick 实测；历史病灶闭环核验过）；施工 C1（#ARCH-351 miniQMT 清退 tranche，裁定 #376 已授权）已派；待裁 8 案多属净删 Owner 门位留晨报；清洗三引擎零接线+CH 表三数互斥+影子表退役通道＝全流通缺口已记录 |
| M2 回测模拟链 | AutoRuntime/回测/模拟盘/GPU 矩阵/T0/IBT/成本门 | m2_backtest_sim/ | **挖干可施工**（9 册 59 子环节；待裁 6 案总筹已裁：①GPU 规模口径勘误留晨报请 Owner 确认 ③池基悬空=T2 冻结至池基修复 ②⑤文档口径采纳 ⑥双真源留晨报 ④词表已在 Owner 案）；活体假绿 2 处（kline_sector_intraday 假 SUCCESS 自 09-10→转 M1 波处置；GPU 巡检口径矛盾→T1 完赛后修）；GPU T1 在跑（PID 30924）禁中动 |
| M3 治理门禁链 | 非 commit 侧门禁+运行时拦截器+注册表族（commit 链侧引用 commit_speedup 战役 00_skeleton 已挖的 23环节/115子环节，不重挖） | m3_governance/ | **挖干可施工**（四分册全实证；覆盖真空 top3：裸 duckdb 无运行时拦/删除原语 in-process 仅5入口/LLM 拦截仅4库+python -c 死路径；3 项 Owner 门位待裁＝KillSwitch 持久化/env 单因子信任绑定/死工厂与75%手工册净删内收）；施工 C1（duckdb 拦截）已派 |
| M4 AI层挖矿链 | ai_layer 六族/capability/LSG/PG meta_question | m4_ai_layer/ | **挖干**（4 册；redline 之谜解＝9 HEAD+63 staged 未落地→落地 worktree import 失败，0021 死信族同根；v4 187 件 100% 在盘 690 passed 零丢失，卡 ailayer 车道协议等队列畅通广播，禁旁人代投；矿脉三挂点缺位须考古；进化点火三缺＝Owner high 门位；ai_compare/ai_tools DDL 未部署）；零自动施工项，晨报列 Owner 清单 |
| M5 调度常驻链 | 计划任务/belt/daemon 群/reaper/订单与结算常驻/监控自动化 | m5_scheduling/ | **挖干可施工**（49 计划任务+13 常驻族四向双源实证；05_master_health_table.md 22 行健康总表；地雷 top3：PostSettlement 注册脚本被 bc76efe3bf 覆盖回退/tilib 夜回填住 tmp 夜夜 exit1/SimBridge 09-24 静默断链嫌疑）；施工 S123 已派；补挖项（备份冷储 3-2-1/FBL/环境启动链/性能水位台账；管线路由调度属性）留补挖波；order_daemon 建成未接线＝全流通缺口已记录 |
| M6 前端API链 | dashboard/api_server/panel 缓存 | m6_frontend/ | **挖干可施工**（3 册：47 路由逐条/16 缓存全清单/54 页 loader 面；【红】AI 层两新页三层三断点→施工 C1 已派；【黄】api↔前端契约无机检、CH 单连接全局锁串行）；待裁 3 案（app_panel 退役时点/CH 连接池化=DatabaseService 域/miniqmt retire 口径）留晨报；补挖项（报告生成）留补挖波 |
| M7 实盘执行链 | QMT 桥/kill switch 交易面/仓位/卖出/ex_core 打板族/ex_sor/合规门（M0 空洞收编，总筹已批；**绝对禁触真实交易**） | m7_live_execution/ | **挖干可施工**（7/7 环节 6 册+总览；P0＝合规门全家族 12 件码成闸空零注入，接线前置=Owner 须先人工报送程序化报告回填 broker_ack，fail-closed 正确——留晨报 Owner 清单；SimBridgeExecute 调用的 bridge-execute 子命令提交史中从未存在=09-23 首单来自丢失的未提交工作区→S3 取证结案线索；Saga vs 直连双编排待裁）；零自动施工项 |
| M8 堵点深挖 | 全仓堵点本/事故档/decisions 日志的根因综合+未修清单 | m8_bottlenecks/ | **收卷**（00_root_cause_synthesis.md 185 行+01_open_wounds.md 106 行在盘；晨报引用其根因 top10 与开放伤口三档清单） |

## 四·补2、凌晨战况续记（07:1x，总筹）
- **队列曾清零又再投**：M3-C1b 五批全落 HEAD（duckdb 运行门出厂 warn 态上生产，dev 9/9 绿）；B5(0030)/S1(0031)/前端接线(0032)/T14-a(0033)/0038/0040(ARCH351 tasks切换)/0041(S2)/0046/0048/0059/0062 落地；死信现行 8 封待处方：**0036 replay内容批死于 GATE-VOCAB 词表**（须修词或改标识符）/0034 T14 死于翻译缺条/0039 死于注册表三向合并（requeue 刷新基底即可）/0035 T13 文档 25 件死于 token（按既定推迟包15 统一落）/0049+0050+0051 P3 链死于级联（0037 两注册条目被后续 stale 落地抹除——重注册 0063/0064 已投，守望器 csx_watch_rereg.py 在岗，双落即 requeue 49/50/51）。
- **重放基线收束**：预算帽 6h 到，覆盖 30 笔（verdicts.jsonl 在盘 .runtime/tmp/csx_replay_verify/replay100/）；包8 after 对照用同 30 笔 pinned 区间。
- **新预检处方（qcure 夜里上线）**：WORKTREE-REQUIRED=他会话活跃时必须 worktree 内 cwd 入队＋--queue-root 显式主区（否则误锚 scratch 触发 OPS-GUARD）；COMMIT-SCOPE=按域拆包+--depends-on 链（队列无逃生旗，跨域旗属网关 CLI）。
- M3-C1b 遗留登记：B1 sitecustomize 引导接线另批；token 换绑迁移预检误报 18 条（工具盲区报维护班）；合并器双册丢袋 bug（qcure 2394e956b8 在治）。
**九车道全部收卷：M0-M8 挖矿完成，骨架 76+ 环节全覆盖，进入"挖干即施工"流水期。**
施工袋全景（本会话 session=st-commitspeed-tbl-20260924，队列共 ~15 袋）：
0030(B5退避)/0031(S1逆转)/0032(前端接线)/0033+0034(T14两批)/0035(T13文档25件)/0036(replay内容)/0037(P3注册)/0039+0040(ARCH351计划册+tasks切换)/0041(S2 tilib ps1)/0042(S3取证+pending_rulings)。
**P3 内容批已备在 csx-p3b**（0037 落地即投，守望器 csx_watch_0037.py 在岗）；**包5（D2 步2/3）候 P3 落地后施工**（设计已读毕，真源 10_d1_d2/D2_env_flag_leak.md）；**包8/9/7 候重放基线**（.runtime/tmp/csx_replay_verify/replay100/ 跑至 6h 预算帽，after 对照用 pinned 区间，r1_design §4）。
在飞代理：M3-C1b（duckdb 拦截续完，worktree csx-m3c1 有前任红测待实现）。
M1-C1 收卷要点：只切 kline_cb_incremental（miniqmt→akshare）1 任务，40+3 留登附硬证据（桥 tick 薄 5-100 倍/TickSubscriber 实为 xtdata 模式）；移交六项中最急=G3 ex_dividend_event 换源立卡（akshare 无同构 capability）。
Owner 门位晨报清单（勿自动施工）：M7 合规门接线前置（人工报送程序化报告）/ M4 进化点火三缺+187 件 v4 批（ailayer 协议）/ M2 GPU 规模口径确认+池基悬空 T2 冻结 / M1 净删三案+清洗三引擎接线+G3 换源 / M3 KillSwitch 持久化等三案 / M6 app_panel 退役+CH 池化 / 双编排收敛 / S2 bat 收编 PROTECTED-PATHS 裁定 / .aidrafts/lane_ff_* 三份未提交 sim-bridge 重建件蒸发风险警示（他会话在途勿代管）。

## 五·补、包5 半场收口与下一棒交接（2026-09-25 晚，总筹亲施）
- **包5 已完成半场并入队**：步1=commit() 签名收 internal_call 声明位（袋 0120）；步2=landing W1 全局 env 置位/还原退役＋两调用点 internal_call=True＋_trusted_git_env 显式 C2 pop＋docstring 订正（袋 0121，depends-on 0120）；静态红绿 4/4、gateway 套件 105/106（唯一失败=已 A/B 定案的环境性锁测试）、ruff/语法净。
- **W2/W3（gateway :3603 set/:3650 裸 pop）留给下一棒**：结构=跨函数对（set 在 commit() 成功尾、pop 在 _commit_locked_finalize(3616) 尾，:3073 调用），修复需 prev 捕获后**传参**给 finalize 做 prev-aware 还原（不能各自为政）；**T2 已定性=存在进程内消费者（ops_guard:583 _is_gateway_marked=A1 后提交域判定；git_guard:140 stash 逃生有 FORCE_STASH 显式替代）⇒ 按设计 §4 步3 条款"禁删只修"**，整对删除留 Owner 登记。下一棒直接按此结构施工，勿再穷举。
- **落地/死信终态**：今夜共入队 ~60 袋、落地 40+；死信全部逐因处方完毕（最后一批 0074→0082 v2 重投全落地；0080/0081 p13+T14 计划册系 redline 窗口病，重试至 0116/0117 在队）。**redline 未落地包（ailayer 车道 63 件 staged）是全队列落地环境的间歇病根，晨报首条。**
- **下一棒顺序**：包8（三簇合并，before=verdicts.jsonl 30 笔在 .runtime/tmp/csx_replay_verify/replay100/，after 用同区间 pinned 对照）→包9（own-tree，15 台全索引门分道）→包7（缓存键）→包14 红蓝 7 场景→包15 终报（回收测算：单文件链 64s→<15s、件数/日 158→<60、p99 实测）+清洁（scratch worktrees 全谱 remove+release claim 读 .ailocks 判成）。
- **新预检/队列处方（本夜实测）**：活跃会话期间入队=worktree 内 cwd+`--queue-root` 显式主区；跨域手术=按域拆包+--depends-on；热册 stale 基底死=「HEAD 整册回插+块界断言针」配方（三次实战零失败）；重投熔断 2 次即拒=换新袋号重投（B5 上线后生效）；[STARTUP] 值禁自造（GATE-VOCAB 词表先查）；永久系统脚本 TTL 禁 permanent+manual 组合（PERMANENT-SYSTEM-TRIGGER）。
- 提交链自身（此前的 commit_speedup 战役）= 多车道目标的**地基车道**，其批次链（P3/包5/包8/9/7/10/11/14/15）继续按 CAMPAIGN_STATE_SNAPSHOT.md 推进，本战役不重复挖它。
- 施工并发纪律：挖矿车道只读+写本目录作业簿（**零 commit、零 enqueue、零主区写入**），不占提交队列；施工车道（含两个已在跑的包10/包13 子代理）才占队列。全局子代理并发≈10（含施工 2-3），reaper watermark 兜底。
- 铁律继承：禁任何 worktree 跑 test_ops_guard_red_team.py；禁 kill belt；禁插队；热文件 CAS。

## 六、晨报应收口径（Owner 醒来第一读）
本册状态表刷新 + 各车道三态汇总（挖干 N / 待挖 N / 待裁 N）+ 提交链批次落地进度 + 红蓝结果 + 零遗留声明（或遗留清单+已试路径）。

## 六、恢复作业书（2026-09-25 晚审计后——下一棒第一优先，机械执行）
**审计结论**：P3 链/replay/T14 曾落地后被他会话 stale 袋再度回退（VI 顶部提交已是他道收割批）。包5 两袋未落（无断裂态）。113 个挖矿作业簿 staged 未落（主区 index 蒸发风险）。
**恢复序**（全部用 worktree 现存内容，勿重写）：
1. 0083（P3a gateway+ledger）前置=ledger depgraph 节点未登记（死因 NEW-FILE-DEPGRAPH）→ 先 apply_depgraph.py --add-design-node（参照 duckdb 门 node=15174363 形态）→ requeue 0083 --worktree-root .worktrees/csx-p3b。
2. 0083 落地后 requeue 0084（P3b）→ 0085（P3c）→ 0082（replay，ORPHAN 已被 HEAD 登记行治愈，可立即 requeue --worktree-root .worktrees/csx-replay）→ 0122（T14，requeue 前 git grep 验翻译册在册）。
3. 0118/0119=P3 链重编号残件，弃。
4. 防再回退：全落地后跑 9 探针（csx_watch_final.py 的 PROBES 表）每 30 分×3 轮；回退即再 requeue（内容永存各 scratch worktree）。根治=ailayer 63 件 staged 落地后 stale 袋自然消失。
5. 挖矿 113 件 staged：补 token（batch_creation_tokens.py --prefix 逐件）后拆 3-4 袋入队（防合并器丢袋）。
6. 之后：包8（代理在飞）→包9→包7→包14→包15。
**0120(CloneGuard) 处方**：gateway:493↔duckdb:130 error_code 异常惯用法平凡 __init__ 同构——工厂化（抽公共基类双侧继承）后再投 D2 半场（internal_call+landing W1 退役，内容全存 .worktrees/csx-pkg5b）。
