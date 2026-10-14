---
ttl: task_bound
---
# 维护七班 99_delivery 终账（车道A｜st-maint7-20261014）

统筹 10-14 午收口令第②③项产物。接手真源＝本册＋班账 `00_ledger.md`＋队列 blobs，**不依赖对话记忆**。
证据等级标注：【落】＝已在 HEAD（只认 `git show HEAD:<件>`）；【飞】＝在队未落；【未】＝本班未闭合（附前提缺口）。

## 一、交付清单与证据等级

| # | 交付 | 状态 | 判据 |
|---|---|---|---|
| 1 | P0-2① CREATE-GUARD 撕裂读→HEAD 稳定面兜底 | 【落】0004 | C1 |
| 2 | P0-2② REGISTRY-YAML-PARSE 差集→PG 真源逐条对账 | 【落】0004 | C2 |
| 3 | 扩面：投影双向一致性告警（甲/乙两向） | 【落】0005 | C3 |
| 4 | 班账 §一–§八 | 【落】0009 | C4 |
| 5 | P0-1 甲：perm_trigger 补 m10 逐件声明解析 | 【落】0034／c7ef3e7e53 | C5 |
| 6 | `_make_noqa_pattern` 分隔符仅限水平空白（堵跨行借理由）＋m11／syntax-fixture 两处收编 | 【落】0034／c7ef3e7e53 | C6/C7 |
| 7 | 守卫件消除 HEAD 级目录收集错（**换装载点版**，非 B 版字节——原因见班账 §11.3 三面对表） | 【落】0035／97c5d6fc22 | C8 |
| 8 | 测试桩修复（消除 §九 已知红＋"桩必被调"硬断言） | 【落】0035／97c5d6fc22 | C9＋C12 |
| 9 | 班账 §九「已知红」四要素自诊表＋§十 收口与交接卡 | 【飞】本册随袋（0020/0022/0025/0033 四轮连坐未落） | C10 |
| 10 | 班账 §十一（钮在 HEAD 不在进程＋守卫三面对表）＋§十二（落地逐字读回终账＋数据班就绪锚） | 【飞】本册随袋 | C13 |

判据命令集中在此（表格里不嵌 `|`，防渲染打断；每条**本班 13:3x 原样抽出实跑过**，
"落地期望"列＝实跑读数不是脑估值——旧版把 C5 期望写成"＝1"是凭印象写的，见班账 §12.4 自曝；
别把"当前 0"读成"没做"，也别把"期望"读成"已落"）：

```bash
G="git show HEAD:"
D=src/zephyr/gov_enforcement/commit_gates
GV=src/zephyr/governance/registry_projection
T=tests/gov/governance/commit_gates
L=docs/_working/maint7_campaign/00_ledger.md
# C1 CREATE-GUARD 稳定面｜当前 3 ｜落地期望 ≥3
$G$D/create_guard.py | grep -c _read_registry_head_text
# C2 PG 真源逐条对账｜当前 2 ｜期望 ≥2
$G$D/registry_yaml_parse_gate.py | grep -c _pg_endorsed_token_ids
# C3 双向一致性告警｜当前 5 ｜期望 ≥5（$G 以冒号结尾，其后变量须以不带斜杠的路径开头）
$G$GV/projection_generator.py | grep -c token_two_way_diff
# C4 班账 §一–§八 存在｜当前 OK ｜期望 OK
$G$L > /dev/null && echo OK
# C5 甲落地判据｜期望 ≥1（实跑＝3：定义 1＋新建支 1＋修改支 1）
$G$D/perm_trigger_gate.py | grep -c _has_m10_exemption
# C6 正则收紧（水平空白分隔符字面量）｜期望 ≥1（实跑＝1）
$G$D/_diff_helpers.py | grep -cF 'noqa:[ \t]'
# C7 m11 收编进同一单点｜期望 ≥1（实跑＝4）
$G$D/manual_only_permanent_gate.py | grep -c _make_noqa_pattern
# C8 守卫件为换装载点版｜期望 ≥1（实跑＝3；旧版此处写"B 版文本"已作废，见班账 §11.3）
$G$T/test_strategy_card_lifecycle_map_gate.py | grep -c importorskip
# C9 测试桩修复判别串｜期望 3（该串修复前在 HEAD＝0，具判别力；实跑＝3）
$G$T/test_registry_yaml_parse_watch_extension.py | grep -cF 桩未生效
# C10 班账 §九/§十 两节｜期望 2（本册随袋落地后＝2；正则只吃"十、"不吃"十一、"，勿误读成漏计）
$G$L | grep -cE '^## (九|十)、'
# C12 落地面 §九 已知红闭合｜0035 落地前实跑＝1 failed/17 passed｜落地后实跑＝18 passed RC=0
python -m pytest $T/test_registry_yaml_parse_watch_extension.py \
  $T/test_create_guard_registry_cache.py --basetemp="$LOCALAPPDATA/Temp/land7"
# C13 班账 §十一/§十二 存在｜期望 2（本册随袋落地后）
$G$L | grep -cE '^## (十一|十二)、'
```

数据班复投前置（甲已落地，即刻生效）：声明格式 `# noqa: m10-time-trigger  M10豁免: <理由≥10 字>`
（**同行两空格**、禁独占一行——跨行不计数；`M10豁免:` 前缀按真源册 `reason_format` 体例写，
解析面按"理由≥10 字"判定、不强制前缀）；判据本体未变（时间触发＋无订阅仍违规）；
验收＝`python .runtime/tmp/st-datalane2-20261012/probe_perm_trigger_fix_acceptance.py`
三形态齐（拦/拦/放）且 RC=0——**跑它别接管道**（`$?` 会量到 tail）。
本班 13:3x 落地面实跑原文尾行＝`门修是否已落地且具三判别力： 是 ⇒ 可复投六件套`，
且该探针自带面自证行 `磁盘=6fcd7fbcd88b HEAD=6fcd7fbcd88b 同面=True`。



## 二、本班袋账（真值，四态目录 manifest 口径，非自报）

- 【落】done 14 只：0003 0004 0005 0006 0007 0009 0011 0014 0026 0027 0028 0031 0034 0035
- 【死】dead 21 只：0001 0002 0008 0010 0012 0013 0015 0016 0017 0018 0019 0020 0021 0022 0023 0024 0025 0029 0030 0032 0033
- 【飞】无（pending/processing 全空）；本册随袋落地后本节改为终数
- 口径说明：本 sid 当日有**两个实例**（统筹裁定"分道并档收场、不合并 sid"），四态目录按 sid 取数＝两lane 合并账，
  本班车道A 名下落地件＝0004 0005 0009 0027 0034 0035；其余为并发第二实例（车道B）名下。
- 死因分布（逐族，实测 dead_reason 非归类推断）：真门禁内容 1 只（0001＝孤儿件目录收集错，本班已拆雷）；
  `cascade_stale` 整袋连坐 2（0015/0018）；基底钉旧致"非注册表族件双侧皆改真冲突"5（0020/0022/0023/0024/0025）；
  同件同 sha 自撤让位 3（0012/0013/0032）；钩子 `rc>=2` 拦 3（0008/0030＝零收集 rc=5；0033＝码面指向主区 rc=2）；
  GATE-SCRIPT-Q 报"hook 改了文件"1（0029）；其余见各袋 dead_reason。**其余全部死于机械面，不是内容面。**

**处方（值得进死信族谱）**：同会话内"小袋先落＋后袋仍钉旧 base"⇒ 整袋连坐，会把袋内
**无人动过的增量一起带走**。三条规避：①后袋剔除已落地件；②大袋早于小袋投；
③投后袋前 `git log -1 -- <件>` 复核基底是否已被自身推进。

## 三、判别力与自证存档（防后人重跑我验过的东西）

- 甲三形态：修前基线（主区未修面）拦/拦/拦 RC=1；修后（车道码面，在册探针原文）拦/拦/放 RC=0。
- 突变自证：还原旧正则 ⇒ 6 failed／140 passed；还原两支门件 ⇒ 6 failed／12 passed；
  还原生成器 ⇒ 5 failed／10 passed；抽掉测试桩 ⇒ 1 failed／10 passed。复原后全部字节哈希与备份全等。
- 真实字节回放（主区为根进程，PG 真连）：今晚拦袋那条真实身份⇒放行；
  正对照 HEAD 取 8 条在册复合键⇒8/8 照拦（尺未钝）。
- 全目录爆破：commit_gates 2614 passed／15 failed，15 条红在**纯 HEAD 面同面复现**⇒属既有红，非本班引入。
- 终验读数：本袋面 157 passed／1 skipped；ruff check＋format 净。

## 四、本班自纠（三条，供新总指挥定标尺）

1. **凭印象写期望值**：交付命令里写"期望 20 passed"，原样跑到实测＝18——第四次复发同一坑，
   这次被"复核命令必须抽出原样跑"拦住，未出门。
2. **错判据**：曾用 `calls["n"]` 判"测试修复是否已落 HEAD"——该串修复前就有 4 处。
   换成只存在于修复版的字面（HEAD＝0／修复版＝3）后结论才成立。
3. **假绿被抓于落地面**：车道 PG 不可达＋测试漏装桩＝两件事互相掩盖，车道全绿、落地面红。
   修法＝打桩类用例一律加"桩确实被调过"硬断言；已在册。
4. **期望值仍是脑估（同类第五次）**：§一 表把甲的判据期望写成"＝1"（按"一个函数定义"心算），
   落地实跑＝**3**（定义＋新建支＋修改支）。前一条自纠写的是"被抽出原样跑拦住了 20→18"，
   说明**跑的是"实测列"，期望列仍在凭印象写**——本册 13:3x 版已把两列合成"实跑读数"单列，
   并把 C1–C13 逐条抽出原样跑过；今后交付表只写实测值，不写"应该是几"。

## 五、环境事实（影响一切"车道内验证"，务必转告全队）

`zephyr` 在解释器启动时由 usercustomize 从**主区**预热（206 个模块）＋`DistutilsMetaFinder`
把包名硬绑 `D:\ZephyrAlpha\src`（finder 先于 `sys.path`）⇒ 车道里 `sys.path.insert`/`cd 车道`
**全部无效**，跑的是主区码。正解＝`ZEPHYR_ALPHA_ROOT=<worktree>`（`usercustomize.py:27-34`
唯一认的开关；本班实测设钮即解析到 worktree）。序列化侧导出该钮＝0021 一系的工作，
**实测至今未落**（`git show HEAD:scripts/governance/commit_queue_landing.py | grep -c ZEPHYR_ALPHA_ROOT` ＝0）。
副作用：车道内 PG 不可达（`REPO_ROOT` 随模块位置落车道，无 `config/.env.postgres`）
⇒ 依赖 PG 的门在车道里静默退化成"照拦"；PG 相关测试一律打桩并断言"桩被调到"。

**13:3x 更正（另起留旧案卷，旧段不回改）**：上段"序列化侧导出该钮＝实测至今未落（HEAD 计数＝0）"
已是滞后读数——车道B 的 `q-...-0026` 于 **12:34:16** 把钮落进 HEAD，现值
`git show HEAD:scripts/governance/commit_queue_landing.py | grep -c ZEPHYR_ALPHA_ROOT` ＝ **3**。
但**钮落进文件不等于落进执行体**：落地执行体 `commit_belt_daemon` PID 43080 起于当日 05:08:46，
内存态仍是 12:34 之前的 landing 码 ⇒ 本班 0033（13:02:37 死）仍被"钩子子进程读主区磁盘码面"打中。
取证与三面对表见班账 §十一；本班不重启共享进程（＝全队落盘链门位），改走"码先行袋＋测后继袋"正道。

## 六、未闭合项（③类：等他班前提／等 Owner 批）

1. P1 两条 HEAD 级 pytest 挂死地雷——归车道B（其 0003 已落，0016/0017 判死），本班按并发避让未双写。
2. P2「存量接管条目刷新出口」立法——取证三条在班账 §六（192 条 open 全未关账；立案含 idle 0.3s 级；
   TAKEOVER-PENDING 咬活会话 19 次）；判据本体须与 `session_concurrency.py`＋
   `test_takeover_pid_false_positive.py`＋`session_takeover_ledger.py` 的 `death_evidence` 字段面同批。
3. P-9 定义本班不可得（六班册仅一次且无定义，全仓 6 处命中分属 5 个不相干战役）——需指明册位。
4. 撕裂读**写侧**根因（热册被非 CAS 直改，班账 §二.1）＝根宪法 §1 第 13 条执法面，本班只做门侧兜底。
5. `.aidrafts_pool/pool-20260919202729-c433` worktree 注册指向已消失目录 ⇒ 待 prune（本班未动共享 git 元数据）。
6. 无主 claim 1 枚（属主 st-wkcure-chief-20261013 已不在注册表）——本班不代解他班锁。
7. GATE-SELFDOC 上限（≤10 行）实测**未顶破**（最大豁免 2 行），无需净零扩面；但 3 册带标记却零命中＝死标记，可择机清。
8. **belt daemon 纪元落后 HEAD**（本班 13:3x 实锤，见班账 §十一）：交下一班一条命令——
   在无在飞袋正跑门禁段时重启 `commit_belt_daemon`（现 PID 43080，起于 05:08:46），重启后
   "码＋测同袋"这一合法形态即恢复，本队的拆袋绕行不再需要；**本班未执行**（共享落盘链＝新总指挥门位）。
9. **落地后主区磁盘/索引停在 `HEAD~1` 的"反向待回滚"残留**（本班两次撞上：0034 后 4 件、0035 后 5 件）：
   landing 的受限收敛被无主 staged 条目挡并 fail-open 跳过 ⇒ 后继袋收集面查不到新符号＋任何带索引的提交会回滚已落修复。
   本班只收敛自己名下 9 件（谓词＝`index==HEAD~1` 先证零唯一字节丢失，再 `git checkout HEAD -- <件>`）。
   值得给 landing 补一条"收敛前把无主 staged 残留按 HEAD 复位并留证"的执法面——属他班承重，本班未改。
10. 守卫件的被测门件 `src/zephyr/gov_enforcement/commit_gates/map_family/strategy_card_lifecycle_map_gate.py`
    在 dev 树零命中／无 A/D 记录／主区仅剩无源 `.pyc` ＝**孤儿测试件**；`gate_auto_registrar` 的
    「MAP-ALIGNMENT 死触发」在册告警＝同一事实另一面。补件即自动复活，否则按墓碑制撤测试件——需属主/Owner 定性。

## 七、收口动作留痕（②序列，逐项）

- release claim：`python scripts/git_commit.py --session st-maint7-20261014 --release-only`
- 守护按 PID 精确停（禁按镜像名，`/IM` 全杀曾扫掉 14 班心跳）：见 §八 的 PID 清单，逐个 `taskkill /PID <n> /F`
- 注销会话→归档车道：`python scripts/session_worktree.py archive --execute`（含会话壳与影子指令面）；
  **若撞保护区死锁＝留命令交下一班，禁硬闯**
- reaper keep 行：**本班写过一行**（12:3x 追加式登记，子串 `wait_0033.py`——收口令②的在飞袋落地等待器，
  70 分钟长跑防误杀）⇒ 收班时必须撤。旧版本册此处写"未写／无撤项"＝滞后自报，已更正留旧案。
  撤行谓词＝按本 sid 子串删（该件是**未跟踪件**且多会话共写，绝不按行号删；本班两行位置已从 370/371 漂到 363/364 一带）。
- 收班序与"自称完成"的边界：本节只列至本册入袋前**已完成且已实测**的项；入袋后动作（release claim／
  停守护／注销会话／归档车道／撤 keep 行）由本班随后执行，本册不预自称完成——接手者请以四态目录与
  `git worktree list` 现值为准，勿按本册推断。
- 心跳保活授权：本班曾按正门 `register_heartbeat_keepalive` 两次（01:27 ttl1800、01:58 ttl7200）——
  会话注销后即失效，无需 revoke；如需显式撤，写一条 `revoke` 事件进 `keepalive.jsonl`

## 八、交接位（新总指挥要的一眼可查面）

- 车道：`D:\ZephyrAlpha\.aidrafts\st-maint7-20261014`（分支 `session/st-maint7-20261014`）；
  同 sid 另有**并发第二实例** `D:\ZephyrAlpha\.worktrees\st-maint7-20261014`
  （分支 `ai/st-maint7-20261014/task-maint7-gate-symmetry`）——统筹已定"分道并档收场，不合并 sid"。
- 在飞袋（本册入袋前实测）：pending/processing **皆空**；本班名下 0034／0035 已 done
  （`c7ef3e7e53`／`97c5d6fc22`）。本册随袋是本 sid 最后一只袋，其 qid 与落地 commit 用
  `git log -1 --format=%H -- docs/_working/maint7_campaign/99_delivery.md` 现取现用，勿背数。
- 本班起的进程（收班须按 **PID 精停**，禁按镜像名）：心跳守护 `heartbeat_daemon` PID 29460（00:59:20 起）；
  落地等待器 `.runtime/tmp/st-maint7-20261014/wait_0033.py` PID 45704／15700（13:28／13:29 起，只读轮询）。
- 复投脚手架（本班自造，收班自清）：scratch worktree `D:\ZephyrAlpha\.worktrees\st-maint7-reship-a`
  （detach 于当刻 dev，用于"以袋字节为工作面"的换基底重投；`.runtime/audit/` 系门审计副产物）。
  同根另有车道B 的 `.worktrees\st-maint7-reship`——**非本班件，勿代删**。
- 未落地字节唯一存活处＝队列 blobs（`/tmp` 与 `.runtime` 都会被清）；本班临时件在
  `.runtime/tmp/st-maint7-20261014/`（含探针、驱动、突变备份、三面差脚本）。
