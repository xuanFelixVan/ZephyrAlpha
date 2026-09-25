---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: F20 车道G·全网搜索进货（从胃点菜）——六向台账与三态结论
date: 2026-09-25
module_ref: MOD-AUTO-E1G-001
map_node: FAC-E1G
---

# F20 · 车道G-全网搜索进货

## 一、环节定义与边界
一句话：消化 L3 胃（intel_harvester，MOD-AUTO-L3-001）的收件箱摘要（docs/_working/automation/inbox/intel-*.md），本地 qwen3:8b（经 LSG）每篇抽 0-2 条可检验 A 股假说，url 级 seen log 防重考，LLM 失败条目不标 seen 下一班自愈，带出生证（url 进 birth_source）卸 lane_g_candidates.csv。
上游供料=胃收件箱（骨架 F96 胃·搜索消化设备，业务线代建 v0）；下游消费=E2 预审（G 渠道）。红线分工：只搜不入册由胃侧守住，本车道侧进货不打分。

## 二、六向台账
| 向 | 实证 |
|----|------|
| 上游输入 | docs/_working/automation/inbox/intel-*.md——实测现存 **1 份**（intel-20260916.md，index.md 加 1 件）；格式真源=intel_harvester.render_inbox（`## N. 标题`+`- 链接:`+`- 摘要:`，parse_inbox_entries :66-88） |
| 下游消费 | lane_g_candidates.csv（**0 行**，仅表头）+lane_g_seen_urls.csv（5 行：batch=E1G-20260917-070016，n_candidates 全 0）；编排 E2 消费源 G（factory_intake_pipeline.py:141-143） |
| 自动化触发 | **事件接线未挂**（图9 自认：收件箱落新班自动触发未挂=partial）；现态=纯 manual CLI；schtasks 零接线实证 |
| 真源与注册表 | MOD-AUTO-E1G-001 暂编号（挂单 H-01 解冻后重编，头注 :1-2）；tests/backtest/test_lane_g_stomach_intake.py 在盘；git d75df06d4c=09-17 落地班；图9 FAC-E1G build_status=partial |
| 门禁与质量尺 | 出生证机器写入（url+title 进 birth_source :156-158）；内容寻址 id（E1G 域前缀）跨批去重；seen log 原子语义（成功消化含空数组才标 seen，失败不标自愈重试 :193-217）；解析复用 B 车道（CLONE-GUARD 委托决议 :239-242）；严禁硬凑（EXTRACTION_SYSTEM：给不出假说输出空数组，冰淇淋式宁缺） |
| 当前运行状态 | **黄（本体绿/供给断流）**。唯一一班=2026-09-17 07:00：消化 5 条目→0 假说（5 篇研究均给不出可检验假说——空数组诚实记账）；此后收件箱无新班（胃侧 09-16 后无 intel-*.md 落盘），车道 G 全链停滞 |

## 三、子模块清单
| 是什么 | 入口 file:line | 状态 |
|--------|---------------|------|
| 收件箱解析 parse_inbox_entries（纯函数零 IO） | scripts/backtest/lane_g_stomach_intake.py:66-88 | built |
| 收件箱扫描 collect_inbox_entries（文件名排序确定性） | 同上:122-130 | built |
| 消化主流程 run_intake（seen 过滤→LLM→去重→卸货+记账） | 同上:163-236 | built |
| seen log 台账 | data/strategy_intake/lane_g_seen_urls.csv | built（5 行实证） |
| 假说台账 | data/strategy_intake/lane_g_candidates.csv | built 表头/**零数据行** |
| 收件箱落新班→自动消化的事件接线 | — | **missing**（图9 自认） |
| 上游胃侧搜索班次（intel-*.md 增量） | docs/_working/automation/（AI 层 L3 域） | **停摆**（09-16 后零新班，属 AI 层/骨架 F96 域非本车道） |

## 四、堵点与病灶
1. **上游断流使 G 空转**：唯一 inbox 件已消化，胃侧无新班——G 的断点不在本件而在 F96 胃的搜索班次停摆（骨架记"业务线代建 v0，升级归 AI 层"）；修法=催 AI 层车道 F96 升级+常态化搜索班；跨组依赖，**待裁/移交 KS-AI 组**。
2. **事件接线未挂**：即使胃恢复，G 仍靠人工跑；修法=inbox 目录文件落盘哨兵（watchdog/计划任务检新文件→lane_g_stomach_intake run）——注意"事件触发禁定时器"口径下，"新文件到达"是合法事件；0.5-1 天；本车道可修（触发器口径与 F14 断点①同裁）。
3. **零假说班的先验风险**：首班 0/5——若系统性 0 产出说明抽取 prompt 过苛或胃源学术化偏重（研究摘要→日频 A 股信号本就低产）；修法=连续 N 班 0 产出时回看 prompt 召回率（抽取率 KPI），避免车道名存实亡；观察项非施工。
4. **MCTS 同名陷阱**：lane_c3_candidates.csv 与 G 无关但同属"声明未出货车道"族——口径对齐见 F17。

## 五、提速与合并机会
- 解析/去重/出生证全部委托 B 车道实现（零克隆，正确）；无合并点。
- 若事件接线落地，可与 F14 事件触发器共用同一"收盘后事件总线"（一次施工两处受益）。

## 六、自审闸三态
- **三态结论：partial**（消化本体+seen 自愈语义 built；事件接线缺+上游断流）。
- **差什么才算 built**：①新班事件接线挂通（或与 F14 触发器合并裁定）；②上游胃侧恢复班次并产出首条非零假说落 lane_g_candidates.csv（首条出货即本体闭环实证）。

## 七、复核命令
```bash
ls docs/_working/automation/inbox/intel-*.md | wc -l    # 收件箱库存
python -c "import csv;print(sum(1 for _ in csv.DictReader(open('data/strategy_intake/lane_g_seen_urls.csv',encoding='utf-8-sig'))))"  # seen=5
python scripts/backtest/lane_g_stomach_intake.py run --dry-run   # 幂等演练（应全 seen 跳过）
python -m pytest tests/backtest/test_lane_g_stomach_intake.py -q
```
