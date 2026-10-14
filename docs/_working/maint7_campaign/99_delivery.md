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
| 5 | P0-1 甲：perm_trigger 补 m10 逐件声明解析 | 【飞】0025 | C5 |
| 6 | `_make_noqa_pattern` 分隔符仅限水平空白（堵跨行借理由）＋m11／syntax-fixture 两处收编 | 【飞】0025 | C6 |
| 7 | 守卫件（**B 版字节** `importorskip`）消除 HEAD 级目录收集错 | 【飞】0025 | C7 |
| 8 | 测试桩修复（消除 §九 已知红＋“桩必被调”硬断言） | 【飞】0025 | C8 |
| 9 | 班账 §九「已知红」四要素自诊表＋§十 收口与交接卡 | 【飞】0025 | C9 |

判据命令集中在此（表格里不嵌 `|`，防渲染打断；每条**本班 12:2x 原样抽出实跑过**，
当前值与落地期望值分列——别把"当前 0"读成"没做"，也别把"期望"读成"已落"）：

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
# C5 甲落地判据｜当前 0 ｜0025 落地后期望 1
$G$D/perm_trigger_gate.py | grep -c _has_m10_exemption
# C6 正则收紧（水平空白分隔符）｜当前 0 ｜期望 ≥1
$G$D/_diff_helpers.py | grep -cF 'noqa:[ \t]'
# C7 守卫件为 B 版文本｜当前 0 ｜期望 ≥1
$G$T/test_strategy_card_lifecycle_map_gate.py | grep -c importorskip
# C8 测试桩修复｜当前 0 ｜期望 3（该串修复前在 HEAD＝0，具判别力）
$G$T/test_registry_yaml_parse_watch_extension.py | grep -cF 桩未生效
# C9 班账 §九/§十 两节｜当前 0 ｜期望 2（0025 落地后）
$G$L | grep -cE '^## (九|十)、'
# C10 落地面终验（两支 P0-2 测试件）｜当前 1 failed（§九 已知红）｜0025 落地后期望 18 passed
python -m pytest $T/test_registry_yaml_parse_watch_extension.py \
  $T/test_create_guard_registry_cache.py --basetemp="$LOCALAPPDATA/Temp/land7"
```

数据班复投前置（甲落地后即刻生效）：声明格式 `# noqa: m10-time-trigger  <理由≥10 字>`，
**同行两空格**、禁独占一行（跨行不计数）；判据本体未变（时间触发＋无订阅仍违规）；
验收＝`python .runtime/tmp/st-datalane2-20261012/probe_perm_trigger_fix_acceptance.py`
三形态齐（拦/拦/放）且 RC=0——**跑它别接管道**（`$?` 会量到 tail）。



## 二、本班袋账（真值，四态目录 manifest 口径，非自报）

- 【落】done 8 只：0003 0004 0005 0006 0007 0009 0011 0014
- 【死】dead 16 只：0001 0002 0008 0010 0012 0013 0015 0016 0017 0018 0019 0020 0021 0022 0023 0024
- 【飞】0025（收口重投袋 10 件）＋本册随投袋
- 死因分布：**一只**死于真门禁内容（0001＝孤儿件目录收集错，已拆雷）；**其余全部死于机械面**
  ——`cascade_stale`（同会话小袋先落→后钉旧 base 的大袋整袋连坐）与被其连坐带走的自我超集吸收。

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

## 五、环境事实（影响一切"车道内验证"，务必转告全队）

`zephyr` 在解释器启动时由 usercustomize 从**主区**预热（206 个模块）＋`DistutilsMetaFinder`
把包名硬绑 `D:\ZephyrAlpha\src`（finder 先于 `sys.path`）⇒ 车道里 `sys.path.insert`/`cd 车道`
**全部无效**，跑的是主区码。正解＝`ZEPHYR_ALPHA_ROOT=<worktree>`（`usercustomize.py:27-34`
唯一认的开关；本班实测设钮即解析到 worktree）。序列化侧导出该钮＝0021 一系的工作，
**实测至今未落**（`git show HEAD:scripts/governance/commit_queue_landing.py | grep -c ZEPHYR_ALPHA_ROOT` ＝0）。
副作用：车道内 PG 不可达（`REPO_ROOT` 随模块位置落车道，无 `config/.env.postgres`）
⇒ 依赖 PG 的门在车道里静默退化成"照拦"；PG 相关测试一律打桩并断言"桩被调到"。

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

## 七、收口动作留痕（②序列，逐项）

- release claim：`python scripts/git_commit.py --session st-maint7-20261014 --release-only`
- 守护按 PID 精确停（禁按镜像名，`/IM` 全杀曾扫掉 14 班心跳）：见 §八 的 PID 清单，逐个 `taskkill /PID <n> /F`
- 注销会话→归档车道：`python scripts/session_worktree.py archive --execute`（含会话壳与影子指令面）；
  **若撞保护区死锁＝留命令交下一班，禁硬闯**
- reaper keep 行：本班**未写** `data/runtime/process_reaper_keep.txt`（grep 本 sid 零命中）⇒ 无撤项
- 心跳保活授权：本班曾按正门 `register_heartbeat_keepalive` 两次（01:27 ttl1800、01:58 ttl7200）——
  会话注销后即失效，无需 revoke；如需显式撤，写一条 `revoke` 事件进 `keepalive.jsonl`

## 八、交接位（新总指挥要的一眼可查面）

- 车道：`D:\ZephyrAlpha\.aidrafts\st-maint7-20261014`（分支 `session/st-maint7-20261014`）；
  同 sid 另有**并发第二实例** `D:\ZephyrAlpha\.worktrees\st-maint7-20261014`
  （分支 `ai/st-maint7-20261014/task-maint7-gate-symmetry`）——统筹已定"分道并档收场，不合并 sid"。
- 在飞袋：`q-20261014-st-maint7-20261014-0025`（10 件）＋本册袋。
- 未落地字节唯一存活处＝队列 blobs（`/tmp` 与 `.runtime` 都会被清）；本班临时件在
  `.runtime/tmp/st-maint7-20261014/`（含探针、驱动、突变备份、三面差脚本）。
