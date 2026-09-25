---
ttl: task_bound
title: 接续收口册02 — 进化点火三缺清单（Owner 门位逐条证据）
lane: m4_ai_layer
session: st-ailayer-fullflow-ai
date: 2026-09-25
status: mined
---

# 02 — 进化点火三缺清单（F86-F96 收口，Owner high 门位）

> **一句话**：进化主循环（外扫→收集→清洗→对比→排产→切换→传承，七段一常数，Owner 2026-09-17 夜批定稿）代码面 690 passed 全绿，但点火被三缺卡死：**缺①落地（8 族 untracked+接线批蒸发）、缺②部署（PG 三 schema 未建+两库空转）、缺③触发（常驻/节拍/回流三阀全关）**——三缺全部 Owner high 门位，逐条证据如下。
> 口径来源：总筹册 §四 M4 行"进化点火三缺＝Owner high 门位"；本册为该三字的首份逐条取证册。

## 一、环节定义与边界

取证对象=AI 层进化引擎从"件就绪"到"阀开循环"之间的全部缺口。真源：`docs/_working/ai_layer_vision/`（README v2.0 active+P1 三报告+LEDGER_final）+当日 git/PG 实测。上游=F94/F95 设计面；下游=施工排产（种子→I7 生成器）、仪表盘投影、heritage 回流闭环。

## 二、六向台账

| 向 | 实测证据 |
|---|---|
| 上游输入 | 11 本 DESIGN 全 design_done；v2 落地清单 117 件（P1_resume_files_v2）；夜报 Owner 11 项+R2 接线批 8 项 |
| 下游消费 | 进化主循环七段消费链；月检生成器（checkups 双轨）；仪表盘四路由；heritage 回流（L1 先验消费接口等待侧） |
| 自动化触发 | 现状自动常驻仅两处半（redline 三 gate/运行时拦截器/perceive 内监——后者挂既有事件源）；主循环零触发器在岗（见缺③） |
| 真源与注册表 | 进化循环骨架=ai_layer_vision/README §1（七段一常数）；落地清单=P1_resume_files_v2.txt；判据=风险分层 risk_tier_registry（DDL 部署/常驻启动=Owner） |
| 门禁与质量尺 | 今日复测 `pytest tests/ai_layer -q`＝**690 passed / 0 failed（33.42s，2026-09-25）**；PG 实测=information_schema ai% 枚举 |
| 当前运行状态 | **红（相对点火而言）**：代码绿+账面与 git 态严重背离（HEAD 仅 7 件 vs 盘面 62 .py/9 族+根） |

## 三、三缺逐条（现象/证据/Owner 门位/解锁动作）

### 缺① 落地缺——"8 族不在 HEAD，接线批已蒸发"

| 项 | 内容 |
|----|------|
| 现象 | v4/ailayer 战役全部施工成果停在 untracked 态；R2 接线批声称 staged 的件从暂存区消失，部分实体文件已随 .runtime 24h TTL 蒸发 |
| 当日实测 | ①`git ls-tree HEAD src/zephyr/ai_layer`=**7 件**（仅根 `__init__`+intake 族 6 件）；②8 族（perceive/cleaning/comparator/scheduling/switch_engine/heritage/redline/tools，**55 .py**）+`config/ai_source_registry.yaml`+`config/evolution_schedule_seeds.yaml`+`scripts/ai_layer/` 8 件 untracked（另 2 件已随 intake 批在 HEAD）+tests/ai_layer 全族+capability 卡 9 张=**全部 `??` untracked**（ai 相关 31 个顶层 untracked 条目）；③最近 ai_layer commit 仍是 84007a1d6a（intake 第 3 批），此后零落地 |
| 蒸发清单（新实锤） | `.runtime/sessions/st-ailayer-final-20260924/staging/` 仅剩 1 文件（wiring/test_negative_list_gates.py）+空目录树；**已蒸发**：api_server 四路由补丁、L5 C9 前端三路由补丁、L6 S6 promotion 双补丁+WIRING_NOTES、token_batch_rows.yaml（9 行）、OBJ_R S3 提案 `obj_r_s3_proposal.md`（202 行/76 常量，全仓 find 零命中，仅终报引用存活）、capability 卡暂存副本；④矿脉三挂点：`generate_project_depgraph.py`/`align_all.py`/`strategy_factory_map_gate.py` 三文件 HEAD 干净且零 vein 引用（grep 实测 0 命中）——R2 项5 声称的 staged 挂点件已不存在 |
| Owner 门位 | ailayer 车道协议：v2 117 件批随"队列畅通"广播触发（呈批-1 已认 v2 生效，LEDGER_final:49），**禁旁人代投**（清单=P1_resume_files_v2.yaml） |
| 解锁动作 | 队列畅通广播→按 P1_final_report 要素三四步序列落地（幂等补暂存→会话活性→git_commit.py 单命令→主区 pytest 复核+`git log -1 --name-only` 防吸收核验）；蒸发件（补丁×4/S3 提案/token 批）须先重铸或改道重做 |
| 工作量 | 落地=1 批次；重铸蒸发件≈0.5-1 批次（S3 提案与补丁有完整上下文可重建） |

### 缺② 部署缺——"PG 侧三 schema 未建，两库空转，两残留待清"

| 项 | 内容 |
|----|------|
| 现象 | 进化循环的持久化底座一半不存在、一半零数据 |
| 当日实测（read_only PG） | ①`ai_compare`/`ai_tools`/`ai_layer_scheduling` 三 schema **不存在**（探针 UndefinedTable×3；information_schema ai% 仅 ai_heritage/ai_intake/ai_intake_test_smoke×2/ai_layer_model）；②`ai_heritage` 9 表实存但 `ai_heritage_entry`=**0 行**（回流闭环建成未通水）；③`ai_intake.ai_cleaning_spec`=**0 行**（清洗规格卡库空转，无生产清洗流量）；④残留 `ai_intake_test_smoke`+`ai_intake_test_smoke2` 各 12 表（测试隔离违规残留，M4 分册01 已记） |
| Owner 门位 | DDL 部署=high 门（宪法 §5.2 production 流转）；DROP 残留 schema=破坏性操作三步验证（RULE-DATA-OPS）+Owner |
| 解锁动作 | ①`python -m zephyr.ai_layer.comparator.experiment_store --deploy`（ai_compare）②tools usage_stats `--deploy`（ai_tools）③`scripts/ai_layer/apply_ai_layer_scheduling_ddl.py`（ai_work_order）④smoke×2 三步验证后 DROP ⑤首单真实工单跑通后 heritage 回填种子 |
| 工作量 | ①-③幂等脚本各一条命令；④半小时含验证；⑤随首单闭环 |

### 缺③ 触发缺——"主循环三阀全关：无节拍、无常驻、无回流"

| 项 | 内容 |
|----|------|
| 现象 | 七段间数据通路件齐（E2E 测试七段全绿+复活信号回灌 L1 在盘），但三处启动阀无一开启 |
| 证据 | ①**外扫节拍**：L1 施工项 7 宿主（register_ai_l1_scan_task.ps1）未建未登记，T3 双前置（Owner 追认+裁定登记）未解锁——搜索单/矿脉生成器在盘等宿主；②**常驻排产**：`order_daemon.py` 事件驱动型常驻件无启动登记、无进程实例（M4 分册01 实测），胜者事件 `evolution_winner_due` 当前零产出；③**传承回流**：heritage 表 0 行零自动写入方，L1 项 9 先验消费接口等 L7 定稿（Owner 夜报 #10）才能接；月检=manual CLI 人工点火 |
| Owner 门位 | 外扫宿主=追认+裁定登记双前置（夜报 #9）；L7 DESIGN 状态翻转=Owner（夜报 #10）；常驻启动批准=production 流转门 |
| 解锁动作 | ①批 L1 项 7→建 ps1+resource_profile 登记+裁定号→外扫节拍上线；②翻转 L7 状态→L1 项 9 接线→heritage 侧服务已建成即可通水；③order_daemon 常驻启动登记（依 M5 车道 daemon 惯例：单例锁+TTL+僵尸检测，零定时器） |
| 工作量 | ①0.5 批次（材料齐）；②接线级；③启动登记级 |

## 四、周边 Owner 项附表（夜报 11 项按三缺归类，防漏）

| 夜报# | 项 | 归类 | 阻塞性 |
|-------|----|------|--------|
| #1 | OBJ_M-#1 路由终批（C6 提案在袋） | F95 施工单 | 不阻点火，阻模型线 |
| #2 | OBJ_S-#2 secret_registry ai_exposure 字段 | F95 施工单 | 可缓（deny-list 先行等价） |
| #3 | L4-#3 intake_exam_due 契约定向 | 缺③前置（考试边） | 不阻塞 |
| #4 | L5-#3 任务书 schema provenance | F94 施工单 | 不阻塞 |
| #5 | L6-#2 墓碑 TTL 清理判据 | F94 施工单 | 不阻塞 |
| #6 | C4 打分常数追认 | F95 施工单 | 追认即清 |
| #7 | OBJ_M §3.3 三口径互斥定稿 | F95 施工单 | 阻 OBJ_M YAML/测试合流 |
| #8 | C8 排班 --force 错峰窗 | 缺①邻接 | 一行命令候窗 |
| #9 | L1 项 7 双前置 | **缺③核心** | 阻外扫节拍 |
| #10 | L7 状态翻转 | **缺③核心** | 阻回流闭环 |
| #11 | 治理立案族（OBJ_R S3/casebook/OBJ_T 考纲沙箱/L4-C7/L7-#2/L5-#2） | F94/F95 施工单 | 按既有节奏 |

## 五、自审闸三态

**挖干可施工（清单与证据面）+待裁（三缺解锁时序归 Owner）**：
- 三缺逐条现象/当日实测/门位/解锁动作/工作量五要素齐 ✅
- 蒸发清单为本日新实锤（staging 空目录树+S3 提案全仓零命中+三挂点零引用）——对 P1 终报"✅ staging"账面的诚实修正 ✅
- 待裁：解锁顺序（建议 缺①先行——落地是一切前置；缺②三条命令可随批；缺③中 #9/#10 是纯批文动作，可与缺①并行批）——留 Owner 晨报。

## 六、复核命令

```bash
# 缺①：HEAD vs 盘面 vs untracked
git ls-tree -r HEAD --name-only src/zephyr/ai_layer | wc -l          # 7
git status --porcelain src/zephyr/ai_layer config data/capability_cards scripts/ai_layer | grep -c "^??"
find . -name "obj_r_s3_proposal*" -not -path "*/node_modules/*"      # 零命中
grep -c "vein" scripts/governance/generate_project_depgraph.py       # 0
# 缺②：PG 探针（read_only）
python -c "from zephyr.governance.depgraph_schema import get_depgraph_pg_connection as g; c=g(read_only=True); cur=c.cursor(); cur.execute(\"SELECT table_schema,count(*) FROM information_schema.tables WHERE table_schema LIKE 'ai%' GROUP BY 1\"); print(cur.fetchall()); c.close()"
# 缺③：常驻与节拍
grep -n "STARTUP" src/zephyr/ai_layer/scheduling/order_daemon.py | head -2
ls scripts/register_ai_l1_scan_task.ps1                              # 不存在
# 代码面基线
python -m pytest tests/ai_layer -q                                   # 690 passed
```
