---
ttl: task_bound
completes_when: Owner 醒后按本包 §四 菜单逐项转裁；§三 两处更正被确认接收；三袋＋本包落地核验完成
---
# 终清波三·晨间裁定包（通宵令 §六 三段式，sid=st-fclean3-20261012）

> 令源＝Owner 2026-10-12 01:15 通宵连续执行令。波三节＝"案卷全出品、机械面清零、孤儿壳影子归档在跑"；
> 大面实际处置（aidrafts/quarantine 实删实归档）令文原话"等晨间裁定，今夜只出案卷"⇒ **本班今夜零动大面**。
> 北极星对照（§〇）：本波服务于"附属物 63.4 GB 存量每面有主有据"。自评分：**"有主有据"今夜从 44 面推到 101 面**，
> 其余缺口与原因见 §四 M11。全夜**无一袋假落地**（三袋入队后仍 pending，本班不称其完成，见 §一-7）。

## 一、执行了什么（逐项＋红绿证锚点）

| # | 动作 | 锚点／实测凭据 | 态 |
|---|---|---|---|
| 1 | 全域总账（149 面一次遍历，含件数/字节/静默/家族/空壳/散件/staging） | `wave3/20_wave3_p1_census.yaml`（机生）＋`21_wave3_p1_firstbag.md` | 已投队 q-0001 |
| 2 | 工令 §1 六处基线差因取证 | 同上 §一（`.aidrafts` 286,575 件/4.04GB 非"13 件"；quarantine 主体 drift_\* 7,434 枚占 97% 字节；staging 实测 3 会话；未跟踪 `-uall` 558；dead 袋/非袋件口径；E 墓园 3 项一致） | 统筹 01:0x 已全采 |
| 3 | **真删：46 个零文件目录** | 清单 sha256 `0b0cae988df22cca4767662b0f01a1e882a7ababb6b03ec8868fc42008065f7a`；手法自底向上 `os.rmdir`（非 rmtree/非 shell rm）；删前逐件复验文件数=0；回执 `out/p2_delete_receipt.json`：deleted=46／failed=0／复存=0 | 已执行（盘面事实） |
| 4 | `.runtime` 根 22 枚散件**内容证据冻结**（防 7d TTL 无声吃掉） | `out/p2_root_files_content_evidence.json`（22 件 name/bytes/lines/sha256/mtime/head/tail，合计 19,614,760 B 的元数据，未复制大体积正文） | 已执行 |
| 5 | 归档器**影子点火 round1-3**（幂等自证） | `out/shadow_round{1,2,3}.json`：三轮 `mode=shadow／scanned=466／would=288／errors=[]／suspected=[]`；**三轮点名集逐轮全等（new=∅∧gone=∅）**；与 `list_active_readonly()` 交叉核**三轮命中在飞＝0** | 已执行 |
| 6 | 影子日检**交接卡**（交周期班/维护三班，非本班会话） | `wave3/23_wave3_shadow_daily_handoff.md`；日检脚本本班实跑通过（day1 合格），判据四件齐，不齐即不计当日并暂停转正 | 已投队 q-0003 |
| 7 | 六条只读车道案卷 | `wave3/lanes/`：`lane_quarantine`(260)／`lane_tmp_lanes`(224)／`lane_deadletter`(251)／`lane_consumers`(20K 级)／`lane_aidrafts`(441)／`lane_untracked_audit`(437)／`lane_face_ownership`(361)，合计 7 份 | q-0001/0002/0004 |
| 8 | aidrafts **唯一字节抢救** | `.runtime/quarantine/fclean3_safety/aidrafts_irreplaceable/MANIFEST.jsonl` 25 行：23 件 `byte_copy`（sha 回验全等，111,428 B）＋2 件 `hash_only_manifest`（密钥，**未复制第三份明文**） | 已执行 |
| 9 | 本班工具链复用（未新建第二套判据） | `out/p1_census.json`／`p2_mechanical.json` 等生成器在 `.runtime/tmp/st-fclean3-20261012/tools/`；字节对拍调波二 `scan_dev_delta.py` 四函数（**importlib 仅导入，未执行该文件**） | 已执行 |

**三袋落地状态（如实，不称完成）**：`q-...-0001/0002/0003` 02:0x 仍 `state=pending`（前面 12/29/32 袋，头袋等待约 1h）⇒ **dev 上尚无 wave3 目录**（`git ls-tree -r dev` 零命中已核）。本包为第四袋。

## 二、自裁了什么（逐条＋证据＋依据授权矩阵哪一格）

1. **S3 散件 22 枚今夜零删除**（依据＝授权矩阵"不可自裁：物理不可逆删除"＋工令 §0 真删仅两类）。逐件分档已定：14 枚在飞锁/缓存（mtime 0.02–0.12d∧读者＞0）、5 枚零读者但**查无写者**（`algoflow_progress/skipped`、`predictions_v1_backup_1971`、`board_idx_offset`、`workspace_drift_warn`）⇒ **无写者＝不可证"机器可再生"，故不落态①**、1 枚有独有字节（见 §3-a）。
2. **46 个空壳目录判可清并执行**（依据＝"预签＞既定默认＞最保守"中的**既定默认**：工令 §2 机械面例外＋统筹点名授权这三面）。判据合取四件：零文件∧无进程句柄∧不被 reaper keep∧代码面读者 grep=0；进程表探不到时**一律判不可清**（禁 fail-open）。
3. **影子口径以机制自算为准**（would=288 vs 本班手工代理 268）——依据＝"跨班争议/口径不可自改"取保守侧：不改机制判据，只登记差因不硬合（Owner 追认纪律"量出结构约束停下呈报非硬合"）。
4. **7 天日检执行方改为周期班/维护三班**（依据＝统筹原话"注册计划任务随转正一并定"⇒ 影子期不注册；本班会话不可依赖）。本班不自建 cron、不自注册任务。
5. **密钥二份只登记不处置**（依据＝Owner 六面之"物理不可逆"＋禁"出域"），并且**主动不复制第三份明文**——这是比"照单存证"更保守的一格，理由：明文密钥多一份副本就多一处泄漏面。
6. **Q3（382.8MB 投影独有字节）不自裁**，转册主车道（依据＝"新协议口径/跨班争议不可自裁"＋在册禁"重打投影袋"）。
7. `.aidrafts` 16 棵工作树今夜**零动**（含零 `worktree remove`）——即使车道实测"真不可再生仅 25 件/0.11MiB"，令文写明"大面实际处置等晨间裁定"⇒ 执行边界按令，不按性价比。

## 三、⚑ 两处更正（另起一节，旧案卷原文不动——Owner 追认纪律）

**a) `list_active()` 的杀伤面比本班先前写的大；先前那句"结构上不可能"作废。**
P1 册 §五-3 我曾写："`_save()` 语义是 merge-upsert（只增改、永不删）⇒ 本班那次 register 在结构上不可能逐出他人条目"。**该论断的方向正确但对象选错了**：逐出不走 `_save`，走 `list_active()`——而本班 00:37 的诊断脚本尾部**确实调用过 mutating 版 `list_active()`**。三处 file:line 现已确证：
- `session_concurrency.py:1516` `list_active(*, mutating=True)`，其 INVARIANTS（同文件第 10 行）原文"缺省 mutating=True＝**判死即写接管台账＋超宽限分片物理收割**……72 处调用方依赖这套副作用面……要'只看不写'必须显式 `mutating=False` 或走 `list_active_readonly()`"；
- `:1552-1559` 收割循环：`if expired and mutating:` → `_salvage_takeover_ledger(...)` → `_delete_shard(sid)`；
- `:1048-1054` `_delete_shard()` = 删片 **＋ `legacy.pop(sid)` ＋ `_write_legacy_raw(legacy)`** ⇒ **兼容副本确实会被整表缩小**；宽限 `_REAP_GRACE_SECONDS=900s`。
**归因做到证据允许的底**：时刻吻合（我调用 00:37:45，其前副本 15、其后瞬时 6/8、再后 14→17 自愈）；但 `_write_legacy_raw` 走自研 tmp+`os.replace`、**不经 `safe_write_text` ⇒ 无写者审计面**，且同窗内 reconciler/门链/网关收割链这些 mutating 调用方都在跑 ⇒ **无法事后证明那 9 条是我那次删的**。结论＝**机制确证、事实可疑、计数不可追认**，维持"未决归因"但把嫌疑面从"不可能"改为"本班也是候选写者之一"。
**后果实测仍为零**：00:35 后 `dead/` 无新死信（0002 册 §八 已记）；被收侧 30s 内由各自守护自愈重写。
**纪律升级（已写进交接口 §二 与后续任务书）**：`list_active()` ＝**写操作**，只读车道/巡检/探针一律 `list_active_readonly()`；`session_registry.json` 单文件只可用于兼容读路径，禁作判活源。

**b) `_delete_shard` 存在 ⇒ 本包 §一-5 之外，"merge-upsert 永不删"这句在 `lane_face_ownership.md` 被实测推翻**（该车道同时实测片数随 `list_active_readonly()` 读数 18→20→18 同步涨落，且累积面实为 **8 枚 `.tmp` 崩溃残件（27.6%，零读者、无清理代码）**）。⇒ P1/P2 两册凡引用"永不删"处，以本节为准；晨间菜单 M10 据此新增一条 `.tmp` 残件收敛项。

## 四、等裁什么（编号菜单＋证据＋本班建议默认；Owner 醒后一次转统筹裁）

| # | 待裁项 | 证据 | **建议默认**（不点即按此保守停） |
|---|---|---|---|
| M1 | `.runtime` 根 22 枚散件处置 | §二-1 三档；内容证据 `p2_root_files_content_evidence.json` | **不动**。其中 3 枚（`reconcile_launch.lock` 10-13 02:39、`task_board.db`/`archive_watchlist.json` 10-15/10-18）将被 GATE-RUNTIME-CLEANUP 7d TTL **无声吃掉** ⇒ 建议优先裁"无声消失要否留痕"，而非裁删 |
| M2 | `.aidrafts` 16 棵注册工作树实处置 | 零 JUNCTION（327,702 节点 reparse=0）；冗余 98.7%；ahead>0 仅 `deadcure2`=2/`mineloop`=1；真不可再生 25 件已存证 | **今夜零动已执行**；晨裁建议＝先 `git worktree remove`（禁裸 rm）＋ ahead 分支解绑＋25 件先走正门落册，再谈退役 |
| M3 | quarantine 处置方案 Q1-Q5 | `lane_quarantine.md` 全集零抽样：A 450/B 228/C1 7,328/C2 1,382；REDUNDANT 仅 2.0% 字节；去重 −39.4% 枚数只 −14.7% 字节；写者 watchdog 自带 30d retention | 采 Q1（REDUNDANT 保留窗 30d→7d，仍由 watchdog 清）＋Q2（内容寻址去重）；Q4 字节预算 1GB 属**改判据**不自裁，需明示批准 |
| M4 | Q3：382.8MB GENERATED 投影独有字节定性 | 占独有面 65%（`capability_canonical` 270.5MB＋`module_translation` 112.2MB）；证它需跑 `--render`（写面）＋PG `registry_snapshot` 逐版对拍 | **交册主车道出证**（统筹 01:5x 已点头，此条改为"催办"而非"待裁"） |
| M5 | `gate_audit` 1.28GB／`audit` 478MB | 读者实读行号钉死 `commit_gateway_abuse_monitor_reconciler.py:488/:493-494/:502`＋`since_7d`@:749＋调用位:773 ⇒ `.1/.2/.3` 轮转段对读者**零可见**；外推 90d≈4.5-5.0GB；⚑ **取证窗仅 ops_guard_delete ~3.7d／feature_flags ~0.7d** | **先扩取证窗再缩容**（缩容需 F 冷库归档＋G 侧第二验证副本＋Owner 批文才删源）；禁动 `obj_s_ai_exposure_forbidden.jsonl` 与 `create_guard_keyword_dup_warn.jsonl` 前 50 行 |
| M6 | only-copy 死信 1,425 袋/2.61GB（dedup 1.10GB）＋ tmp C2 业务资产 49.88 GiB | `lane_deadletter.md` 字节级对拍（only_copy 88.74% 条目级）；与在册「C-2 49.89GiB」差 0.01 | **Owner 门位**，本班只登记；建议与死信四班出货后合裁（T12 待重对） |
| M7 | T8 第二份未纳管明文密钥（`config/.env.{clickhouse,postgres}`，与主仓 sha 全等，git 未跟踪） | MANIFEST 2 条 `hash_only_manifest`（596B/451B） | **有权道处置**；删除前先核该车道是否仍有路径读本地 `.env`；建议加"密钥文件禁止进车道/工棚"的净零合并案（不新建门禁，扩既有 SECRETS 三道 gate 的覆盖面） |
| M8 | T7 `takeover_ledger` 主表比其 tmp 前像**少 75 条**死亡取证（10-06～10-07） | 逐行对拍 169 vs 91/75 独有；存证 sha `5dcd7d66…` | 归因＋是否回填＝维护面裁（与通宵令维护三班节"队列完整性簇"同域，建议并案） |
| M9 | 双轨收敛四组 | `.runtime/locks`(215)↔根 `.ailocks`(95)；兼容副本↔分片真源；`.aidrafts`↔`.worktrees`（每轮净增≈297MiB/20,540 件）；`audit/write_audit.jsonl`↔`.runtime/write_audit/` | 逐组出"谁内收进谁"的裁定；本班**未自落任何一条**（改他班真源面须册主车道出袋） |
| M10 | 新增：`.runtime/session_registry/*.tmp` 8 枚崩溃残件（占片目录 27.6%，零读者、无清理代码） | `lane_face_ownership.md` 实测；本包 §三-b | 建议并入"队列完整性/`.tmp` 残件"簇统一处置，不单开清理器（净零） |
| M11 | 4 条悬挂 creation_token（波三改名 `L_*→lane_*` 遗留） | P1 册 §六 已给完整 retire 坐标（`REG-CAPCAN-001/creation_tokens/…`，version 均 1） | 通宵令 §五 已写明归维护三班 ⇒ 本班只催办 |
| M12 | 影子转正（7 天零异常后 `--execute`）＋归档器计划任务注册 | 三轮幂等自证＋三轮在飞命中 0（§一-5）；日检已交周期班 | 建议按日检满 7 个自然日后**一次批**"转正＋注册任务"两事，避免二次等待 |
| M13 | 面覆盖缺口：`.runtime` 现存 102 面，波三"有主有据"建到 **101 面**（44 census＋24 consumers＋57 六列去重） | `lane_face_ownership.md` §8 剩余申报：6 面件级写者未定位；`locks` 58 件降幅未区分 TTL 与 `lock_files.py cleanup`（两把候选并存）；17 面短窗 Δ=0 未外推 | 建议晨间给"6 面写者未定位"点一条唯一纠正出口（车道或维护三班），本班不猜（在册教训：猜出来的 file:line 会污染后续归因） |

## 五、净零与自犯申报（本包补记）

- **新增永久面＝0**；本包未新建门禁/规则/注册表/第二套判据。车道生成器一律 `importlib` 导入波二原语，**未执行任何在册工具**（头号红线全夜守住：无一支 `--help` 裸跑）。
- 本班自犯**四起**全部留案（P1 §五 三起＋本包 §三-a 一起，均为 mutating 探针族）：
  ① 只读探测触发 22/27 支无 argparse 工具的主逻辑（误删他人分支，已按存证 sha 复原且为 dev 祖先；793 枚受保护存证被幂等覆写，788/788 sha 全等，mtime 证据受损）；
  ② 把兼容副本滞后误判为"本班整表写逐出他人会话"；
  ③ 用 mutating `list_active()` 探针，且先前以"结构上不可能"为其开脱（**本包 §三-a 作废该句**）；
  ④ 一次 `lock_files.py release` 参数序写反得 NOT FOUND（已纠正为 `release <file> <owner>`）。
- 车道自报并本班复核的两起：`lane_face_ownership` 增速初版被 `os.replace` 刷 ctime 骗（3.37MB/日作废，改双采样 Δ 后实为 +55KB/日）；"根散件正被删 2,151 次"系分桶口径错，重切后**仅 1 次**。
- 上下文/时长：01:15–02:1x 连续执行，未中途求 Owner；所有需要选择处按"预签＞既定默认＞最保守"自处并全数落在本包 §二/§四。
