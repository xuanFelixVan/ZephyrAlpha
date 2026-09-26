---
ttl: task_bound
completes_when: 九个施工道全部落 HEAD 且每道红证在案+落地面两轮回归问题 0
---

# 波 13 执行台账（总筹唯一实况位，机读优先，禁散文叙述代替读数）

> 用法：每道交付后由总筹填「落地」列；**判"落地"只认 `git show HEAD:<path>` 的实现符号计数**，车道自述/队列回执/commit message 都不算证据（宪法级判读铁律）。
> 状态字母：⬜未交 → 📥已收（在车道工作树，未进 HEAD）→ 🔩登记中（token/翻译/depgraph 已补）→ 🚚在队 → ✅在 HEAD（附 HEAD 短码+逐件命中数）→ ❌红（附死因签名）。

## 一、道次实况

| 道 | 会话 | 包 | 首报 | 落地 | 红点/待办 |
|---|---|---|---|---|---|
| 甲 | `st-zmaster2-20260926`（总筹） | 方案册+落地+热册唯一写手 | 20:5x 方案册成文 | ⬜ 未 add | — |
| 乙 | `st-p1-gate` | 13.1 CREATE-GUARD 查功能关键词 | 🔄在飞 | ⬜ | L527 git grep 批量化等价性（100 笔重放） |
| 丙 | `st-p1b-libr` | 13.2 图书馆自动更新真接通 | 🔄在飞 | ⬜ | 投影页"生成但不落地面"这颗钉子 |
| 丁 | `st-p2-cens` | 13.3 九族消费面普查自动化 | 🔄在飞 | ⬜ | wiring_registry 假生成器（指 .runtime/digest_p2） |
| 戊 | `st-p3-matrix` | 13.4 全连接矩阵（=W-154） | 🔄在飞 | ⬜ | 应连侧两轴无声明 ⇒ NO_DECLARED_EDGE 单列 |
| 己 | `st-m1-leaf` | 挖矿叶子层（族×W-xx 叶簿） | 🔄在飞 | ⬜ | 骨架册 §四 长尾② 自认未挖 |
| 庚 | `st-m2-seal` | 挖矿封矿完整性独立复核 | 🔄在飞 | ⬜ | 「文档说全 = 实测不全」是本仓头号失败形态 |
| 巳 | `st-p4-bridge` | TRD-A10 桥客户端两缺陷 | 🔄在飞 | ⬜ | 红测先行未证 ⇒ 不算修 |
| 午 | `st-p5-chart` | 波10 G-A 图形信号接考试轴 | 🔄在飞 | ⬜ | 禁点火；DDL 只呈批 |
| 未 | `st-p6-t1top` | T1 Top-46 条件共性 → state_matrix 供数 | 🔄在飞 | ⬜ | INSUFFICIENT 必须如实留空 |

**并发基线**：机器 20 逻辑核（i7-12700KF）/ 64GB。起批前 `commit_pct` 54.27% → 九道起后 67.92%（20:5x）。**熔断阈值**：>82% 停起新批、D 盘可用 <25G 停大批落地、<15G 停一切写批（现 37G）。

## 二、与在途道的边界（防撞实据）

| 时点 | 读数 | 含义 |
|---|---|---|
| 20:30 | `st-final-build-20260926` 心跳 15s 内 + 4 个门禁子进程在跑 | 判活：它正在提交，不是死道 |
| 20:40:53 | 它落 `3eeb935743`（骨架册族 14 W-163..W-180 + 波次表波 9.5/10/11/12 + 八件 ext 终审件 + 40 条 token） | 波 1A/1B/2 与两本总册归它，本役一律不碰 |
| 20:30–今 | 队列 `pending=0 processing=0 done 729→730 dead=700`，lease 不存在，daemon online | 链活而无在途袋；700 封死信属波 6 面，非本役 |
| 全程 | 主区脏项 460（含 `capability_canonical_file_registry.yaml` 被 `st-final-build` claim） | 禁在总仓 index 上做任何"顺手清"；本役全部写在自己车道 |

## 三、登记待办（各道 manifest 收齐后由总筹一次性合批，禁多道同写热册）

- [ ] `creation_token`：波 13 全部新 .md / 新 .py（逐条 `--merge-evaluation` 净零对价）
- [ ] `module_translation`（plain_zh ≥8 字，**必须在主仓跑**，worktree 跑必判"无 plain_zh"）
- [ ] `apply_depgraph --add-design-node`
- [ ] `_EXTERNAL_SPEC_MODULES` 清单行（丙/丁各一条，一处插入）
- [ ] `wiring_registry.yaml` 生成器声明改指真生成器
- [ ] 骨架册族 15 + 波次表波 13 并回（**必须等 `st-final-build` 交还这两本册**，见 §五）
- [ ] `92_acceptance_rulers.md` 追加本波尺 G-77..

## 四、终态判据（本役自有的七条，逐条要读数）

1. 三件机械基建每件：实现符号在 `git show HEAD:` 命中 + 能红测试在 HEAD + 红蓝证据在案。
2. 图书馆"自动更新"从声明变强制：投影页盘-HEAD 键集合差 = 0（当前实测 = 7 页落后 4 天）。
3. 消费面普查九族全部有机器读者（禁再造一份"写了没人看"的 `indicator_usage_ledger` 型死账）。
4. `connection_matrix.csv` 在 HEAD 且 `--check` rc 有定义，缺口分「该连未连」与「无声明边」两数，禁合并成一个吓人数。
5. 落地面两轮回归问题数 = 0（冻车道后在 HEAD 面复跑；活树上两轮一致不算认证）。
6. 红蓝两轮零 FAIL，攻击面含：伪装非重复声明绕过、投影页假更新、孤岛漏计、矩阵假精度。
7. 临时件清零、claim 全释放、车道全收尾（禁悬挂 worktree/分支）。

**表述纪律**：永不说"全绿"；只说"本轮检出 N 件通过 + 已证明能红的证据"。

## 五、阻塞与例外登记（遇门位即此条 + 跳过，不重复问 Owner）

| # | 事项 | 处置 |
|---|---|---|
| B-1 | `CAPABILITY-OVERLAP` 恢复启用属 Owner 门位（⚑-6-3），明文"禁自裁" | 不自裁；关键词判重阻断面落 CREATE-GUARD（Owner 原令即为授权），该门只加"被取代"注释，不改 enabled |
| B-2 | `07_pending_work_master_list.md`（指令卡点名的必读件）**在盘与 HEAD 双向皆无** | 指令卡前提证伪 ⇒ 以 `00_master_skeleton.md` + `10_wave_plan.md` + `19_gpu_plan_and_master_backlog.md` 为待办真源；此条入台账即为登记，不再追问 |
| B-3 | 图形信号若需 CH 加列（lineage/多周期槽）属 DDL | 只呈批不执行，写进 manifest 的门位请求节 |
| B-4 | 任何统计结论若需正式跑批 | 一律 READY_NOT_FIRED；波 12 统一窗口 + Owner 点火批准卡是唯一合法出口 |

## 六、总筹本窗实测新得（20:5x–21:0x，全部命令现跑，非转述）

| # | 实测 | 取证命令 | 处置 |
|---|---|---|---|
| Z-1 | **指令卡点名的必读件 `07_pending_work_master_list.md` 在 HEAD、盘、全部分支历史三处皆无**——不是被删，是从未存在 | `git log --all --oneline --diff-filter=AD -- <path>` 空 + `git cat-file -e 30505c93f6:<path>` 报不存在 | 指令卡前提证伪。待办真源改用 `19_gpu_plan_and_master_backlog.md`（"全量剩余工作总清单"，A-G 七栏，总池 196 项／已闭 ~40／在飞 ~12）+ 骨架册 140 中类；此条即为"登记"，不再追问 |
| Z-2 | **`EV-02~06 已批` 是假的**：裁定册 HEAD 面 `EV-0[2-6]｜蒸发治本` **0 命中**，HEAD 最大号仍是 裁定#413 | `git show HEAD:<ruling_registry> \| grep -icE "EV-0[2-6]\|蒸发治本"` → 0 | 按宪法 §5/§9.11（Owner 门位经裁定登记或正式通道生效，对话/散文"已批"不构成豁免）判 **未批**。19 号文 B4 栏的"已批"是孤儿自述 ⇒ 本役不代开施工令；EV 项已在 `93_owner_menu.md` 补位节呈裁（W-163），等 Owner |
| Z-3 | **T1→T2 自动交接腿从未落地**：`scripts/backtest/t1_t2_handover.py` 盘上 `AM`、HEAD 无；其自述 `[CONSUMERS] 30 分钟薄壳自动化（qoder cron，总筹建）` | `git cat-file -e HEAD:scripts/backtest/t1_t2_handover.py` → 不存在；`git status --porcelain` → `AM` | T2 至今未发车（`ls -d data/strategy_intake/grid_*` 最新仍 024947＝T1）。**判不发车而非判修腿**：波 12/W-179 已裁"施工全做完再一起跑"，且 W-178 板块宇宙 gap 未闭合⇒此刻发车＝烧错宇宙+切 DSR 分母。该件落地归 `st-final-build` 波 2.4（它已在波次表点名此件），本役不抢 |
| Z-4 | **图形库"零下游消费"是有裁定在案的既有事实**，不是新发现：裁定册 1776-1778 行明文——唯一真源=`candlestick_scanner`（TA-Lib CDL61+A股16，MOD-SIG-145，事件表 `market_pattern_event` 2,340 万事件+胜率闭环），消费清查=零下游（全仓 grep 仅 `reversal.py` 自家+测试），并已据此删过 `CandlestickPattern` 类 | `git show HEAD:<ruling_registry> \| grep -inE -A2 "图形技术\|TA-Lib"` | 午道（图形接线）的真验收面因此收窄且更硬：**不是"建库"也不是"补形态"，而是把已有 2,340 万事件表接出下游消费者**；验收要看下游反查计数 >0，且不得复活被裁退役的 `candle_pattern` 列 |

## 七、第二轮排产池（等九道收敛再起，内存现 67.9%）

起批前置：`commit_pct` ≤70% 且 D 盘 ≥30G。以下项经核**不在 `st-final-build` 的波 3 清单内**，不撞车：

| 项 | 出处 | 门位状态 |
|---|---|---|
| IBT-D01 双引擎成本口径对照（考尺 vs 整装） | 19 号文 C6/D5·11 号文 | AI 可自决 |
| DU-11 `daily_valuation` 部分写入病根 | 19 号文 D3·12 号文 | AI 可自决（非 DDL 面） |
| L09-C03 日刊双账合流 | 19 号文 D9 | AI 可自决 |
| L04-C02 候选池三来源接线 | 19 号文 D8（`register_pool_bundle_source` 已备） | AI 可自决（**不碰 t0 甲位**＝门后） |
| L07-C03 算法层收口 | 19 号文·SKEL L07 | AI 可自决 |
| W-119 退役策略重考 prereg **起草** | 波 11.2 | 只起草不跑（跑＝波 12 门） |
| CNS-01~14 消费面接线 | 波 11.1 | 等丁道孤岛清单产出后再排（供数先于接线） |
| L09-C01 编排器收拢 | W-167 | 🌑 施工（门后），只备证据 |
