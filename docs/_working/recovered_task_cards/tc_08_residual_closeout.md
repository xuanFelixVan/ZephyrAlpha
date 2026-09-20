---
card_id: TC-08
title: 残余挂账战役收尾（pipeline_events 接线 / cohort 表 / E6 对冲腿 / E7 告警 / Q1Q2）
verdict: 变形（置信度高：核心建造件已被 fullflow 战役落地进 HEAD——E6/E7/cohort builder 都在；但"已收工归档"声称被证伪：形式收口三件零记录、总簿仍 campaign_running、接线批只在 G 盘冷库、6 个 staged 删除挂着、四个待裁项无裁定号）
category: E类-施工批（pf_alloc 车道）+ D类裁定项
priority: P1
size: 中
source: 任务原文见 C:\Users\fanzi\Desktop\新建 文本文档 (2).txt 第 653-685 行（"八："节，原 st-resume-20260920 续班令）
investigated_at: 2026-09-21
head_at_investigation: c968ad6042
ttl: task_bound
completes_when: 全部卡执行完毕并归档后转 archived
---

# TC-08 残余挂账战役收尾

## 0. 一句话结论

交接令的世界观已过时：原文 T1-T6 的核心代码被平行战役 fullflow（residG 分包）吸收落地——E6 纸面对冲腿（2a80340b51）、E7 告警机器（0808dd8757）、cohort builder 与四套测试全在 HEAD。但 TC-11 交接簿声称的"residual 战役已收工归档（C1 解除）"**被证伪**：归档盒里的总簿 frontmatter 仍 campaign_running、九个节点七个还是空框、形式收口三件（复审报告/施工方案/起床报告）全历史零记录。真正欠着的硬活=pipeline_events 接线（成品只在 G 盘冷库，主仓 grep=0）、apply 三常量注册、tasks.yaml cohort 任务、B20 日期修复，以及**绝不能落的** crisis_gate 红队 +31/-7 加固（fullflow R-072a 已改判"不落"，落了会激活 CRISIS_SHRINKAGE_FLOOR 改配额闸）。

## 1. 背景与来龙去脉

残余挂账战役（危机闸+归因+cohort 台账）主战收工后归档，续班令要求：第一阶段复审（R1-R4）、第二阶段施工方案（T1-T8）、执行（接线批重做/cohort 建表/E6/E7/Q1 循环检查/Q2 收尾）+待裁定清单（O1/O2/O-1/凭据）。执行期间 fullflow 战役的 residG 分包实际承接了 T1-T6 的施工。

## 2. 调查结论（2026-09-21 实测）

| 原文声称 | 实测现状 | 证据 | 等级 |
|---|---|---|---|
| 产出 residual_resume/ 三件（复审/方案/起床报告） | **全无**：目录盘上不存在，git log --all 零记录（从未存在过） | ls + git log --all | A |
| 归档区六件+index | 存在且齐，但 index.md 是机器生成件（status: active 非收工标记） | ls archive/2026-09/residual_construction/ | A |
| 总簿状态回写完成 | **未做**：归档盒内 00_master_ledger.md frontmatter 仍 status: campaign_running；环节表 E1/E2/E4/E5=已建待落地、E6/E7/Q1/Q2=空框（表落后实际：FF-10/FF-16 已把 E6/E7 落地但总簿没回写） | Read 归档总簿:1-66 | A |
| T1① 旧路径 6 个 staged D 随手提交 | **仍挂着**：git status --porcelain -- docs/_working/residual_construction/ =6 个 D，该路径 09-19 后零 commit | git status | A |
| T1② 红队加固 +31/-7 代提交 | 加固仍在工作区（git diff --stat 恰 +31/-7）**但已被 fullflow 裁定 R-072a 改判"不落"**——落了会激活 CRISIS_SHRINKAGE_FLOOR=0.05（regime_meta_allocator.py:109/426）成改配额闸；只保持防蒸发，备份在 .runtime/tmp/ff-recon/backup_last/ 与 G 盘 | git diff + COORDINATION_LEDGER 第 6.20 节 | A |
| T1③ 接线批按新版重做 | **未落地**：pipeline_events.py（已被他会话 BT-P1-031=9098c65245 重写）grep crisis_block_check=0；residG 车道 33 行接线被三次收割回退，成品只在 G 盘冷库（G:/zephyr_cold/30_corpus/fullflow_harvest/20260918-194729/worktree/）；死会话遗产处置（A5 案卷）待 Max 裁定未决。接线曾暴露的 8 条测试红随回滚消失——"测试变绿不是被修好，是缺陷证据面消失了" | grep + 冷库实测 | A |
| T1③ apply 补两表注册 | **未恢复**：apply_market_tables_ddl.py 里 CRISIS_GATE_LOG_DDL/SIM_ATTRIBUTION_DAILY_DDL/COHORT_DAILY_LEDGER_DDL 三常量全缺 | grep=0 | A |
| R1 四 commit | 全部 HEAD 祖先（572b9a5550/32431d66/2fd61ca135/e1a975b158）；四套测试文件均在 HEAD 树 | merge-base 逐一 | A |
| T2 cohort 建表+任务 | 半落地：schema（schemas/categories/cohort_daily_ledger.py:51 DDL，2fd61ca135）+builder（src/zephyr/alt_data/cohort_daily_ledger.py，FF-07）+13 测试在 HEAD；但 tasks.yaml 无 cohort 任务、apply 无注册、CH 表未验（禁连库） | git ls-files/grep | A |
| T3 E6 纸面对冲腿 | **已落地（变形）**：2a80340b51（FF-10）落 src/zephyr/risk/paper_hedge_leg.py（600 行，消费 hedge_execution_skill）+config/paper_hedge.yaml（index_code: IM=O2 预裁、beta×0.5、real_channel_locked: true 代码侧拒绝翻转）——比例进的是 paper_hedge.yaml 非 crisis_gate.yaml，实质等价 | git show --stat + config/paper_hedge.yaml | A |
| T4 E7 告警 | **已落地**：0808dd8757（FF-16）落 src/zephyr/data/alert_webhook_dispatch.py（712 行）+config/alert_webhook.yaml（enabled: false 缺省 fail-closed）+触发源闭合（failures/*.json CRITICAL 或 kill_switch）+459 行测试 | git show --stat | A |
| T5/Q1 两轮+红蓝 | 变形执行：fullflow R-072 做了"连续两轮 16 目录 0 失败+红队 R-055..R-074"，但自认口径瑕疵——两轮跑的是工作区字节（含 3 个 pf_alloc 未提交在途件），严格 HEAD 复跑（B21）至今未做 | COORDINATION_LEDGER 第 6.20 节 | A/B |
| O-1/O1/O2/凭据裁定 | **全部无裁定号**：ruling_registry grep 老蔡/对冲合约/warning 阈值/凭据 = 零命中；O2 仅有 paper_hedge.yaml 注释级预裁 | grep | A |

### 病根

1. **任务被平行战役吸收但无人回写**：residG 分包承接 T1-T6、E6/E7 落地，但 fullflow 收口转冷库后 residual 总簿、起床报告、状态回写全部悬空——两个战役台账各记半截，TC-11 交接簿只看 git log 就写出"已收工"，是台账间 SSOT 断裂的典型事故。
2. **共享热文件三杀**：pipeline_events.py 接线三次落地三次被回滚，最终只剩 G 盘冷库单点副本；C1 独占裁定与"收工解除"声称互相矛盾。
3. **裁定体系漏登记**：O-1/O1/O2/凭据四项只在战役文件里以"预裁/待 Owner"形态存在。

## 3. 上下游

- 前置依赖：fullflow 冷库（接线成品/补丁备份，落前先验哈希）；Max 案卷（A5/B20/B21/R-072a）；两本战役台账。
- 下游消费方：pf_alloc 日线管线（L1 危机短路）；cohort 日任务（依赖四条数据增量任务）；E6/E7 已建成、等 L1 触发链闭合才真正通电。

## 4. 剩余工作清单（可执行）

| 步骤 | 做什么 | 涉及文件全路径 | 验收判据 | 路由 |
|---|---|---|---|---|
| 1 | A5 裁定：死会话（residG）冷库接线遗产是否可代落 | src/zephyr/strategy_pipeline/pipeline_events.py（成品在 G:/zephyr_cold/30_corpus/fullflow_harvest/20260918-194729/worktree/） | Max 出裁定号；按 BT-P1-031 后新版重排两段接线——L1=crisis_block_check 短路、不落 marker、判读异常 fail-closed；attribution_daily=SIM_DAILY_KINDS FIFO 末位+--day 业务日 resolve_pf_alloc_trade_date | Max 裁定，Flash 施工 |
| 2 | apply 三常量注册恢复 | scripts/ch/apply_market_tables_ddl.py；真源 schemas/categories/ 下 crisis_gate_log.py、sim_attribution_daily.py、cohort_daily_ledger.py | grep 三常量命中；apply 干跑通过 | Flash |
| 3 | tasks.yaml 加 cohort_ledger_daily 任务 | src/zephyr/data/config/tasks.yaml | schedule=daily_capital 尾部+deps 四增量任务；admin 建 cohort_daily_ledger 表（CH EXISTS=1） | Flash+Owner（建表） |
| 4 | B20 一行日期修复单独落（**勿动 +31/-7**，R-072a 不落仍有效） | src/zephyr/pf_alloc/crisis_gate.py（备份 .runtime/tmp/ff-recon/backup_last/） | log_crisis_gate_row 用 date 对象入 Date 列；变异测试打红 | Flash |
| 5 | 6 个 staged D 落地 | docs/_working/residual_construction/ 旧路径 | git status 该路径清零 | Flash（正门 git_commit.py） |
| 6 | B21 严格 HEAD 两轮复跑+六环节端到端补课 | 测试体系 | 连续两轮 0 问题且口径=HEAD | Flash |
| 7 | 收尾形式件：总簿回写（归档盒版本）+收工报告按原文六要素（环节×状态×hash/红蓝轮次证据/端到端实录含失败/遗留=0 声明或逐条案由/待裁定清单/清理确认）+Q2 清理两小件（清全仓 *.tmp.* 残留与 .runtime/tmp 一次性件；claims 全 release --release-only）+五项登记裁定号（O-1 老蔡日期映射/O1 warning 阈值/O2 对冲合约/E7 推送凭据/**真实期货通道解锁**——纸面≥3 次演练+Owner 实盘门位） | docs/_working/archive/2026-09/residual_construction/00_master_ledger.md；ruling_registry.yaml | 台账节点翻转带 hash；registry 出五裁定号；*.tmp.* 清零；claims 清零 | Flash+Max/Owner 门位 |
| 8 | 长尾矿脉 M-1~M-11"登记不动工"落册防失传（原文整块，首次入卡）：M-1 机构 de-risking 参数引文/M-2 期货分钟线/M-3 盘中实时危机感知（挂 WO-5 三期）/M-4 期权腿/M-5 情景参数校准/M-6 散户偏差修正学术法/M-7 ETF 份额源/M-8 产业资本数据/M-9 chip 筹码落表/M-10 seat_type 词表扩展（数据线 A7）/M-11 Brinson 多层归因升级——11 条各带一句状态落一份登记台账，只登记不开工 | docs/_working/residual_resume/（新建登记件；若该目录仍不存在则落归档盒 docs/_working/archive/2026-09/residual_construction/） | 11 条全数在册、各带状态一行 | Flash（登记件） |

## 5. 与其他任务卡的关系

- **TC-11：其交接簿"residual 已收工"声称正是本卡证伪的对象**——两卡记录须统一到本卡口径。
- TC-04：执行指针/registry 回写同池，建议同批走。
- TC-06：A5/B20 与其裁定题同族，可并案出卡。
- TC-02/TC-03：.runtime/tmp 备份面共享；6 个 staged D 是"全量 add 连坐雷"，任何会话做全量 staged 清点时要知悉。

## 6. 风险与避让红线

1. **谁若按原文执行"红队加固代提交"将直接违反 R-072a 并激活 CRISIS_SHRINKAGE_FLOOR 改配额——+31/-7 必须继续不落**（只防蒸发）。
2. 接线成品唯一副本在 G 盘冷库：落前先验哈希。
3. 当前测试绿含"缺陷证据面消失"假象：勿以绿判收工。
4. 三共享文件（pipeline_events/tasks.yaml/apply_ddl）是多会话热区：动前必 acquire。
5. 全程禁连生产库写操作；建表走 admin 通道+Owner 门位。

## 7. 执行冷启动提示

按 AGENTS.md 第 0 节冷启动；CH 表操作走 DatabaseService/admin；测试禁写生产路径（tmp_path fixture）；队列死信读 dead_reason 修复后 requeue。
