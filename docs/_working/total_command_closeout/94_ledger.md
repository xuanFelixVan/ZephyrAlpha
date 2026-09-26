---
ttl: task_bound
completes_when: 本册三清单被终报引用且每条凭据可复跑
---

# 总包本班台账（LEDGER · st-zmaster-20260926 · 2026-09-26 14:2x 起）

> 本班职责=**裁定 + 施工方案**（施工交 Flash 执行）。本册只记"我做了什么、怎么复核、证据几级"，不记叙述。

## §〇 交付落地记录（本班全部件已入 HEAD，逐件字节等值）

| 袋 | 落地 commit | 件数 | 内容 |
|---|---|---|---|
| q-20260926-st-zmaster-20260926-0001 | `0f832185b7`（15:28:52） | 18 | 骨架/裁定/X 更正/八波排产/配方/一键指令/验收尺/Owner 菜单/台账 + 案卷 A–H + 热册 token 17 条同袋 |
| q-20260926-st-zmaster-20260926-0002 | `7cd3589619`（15:31:52） | 2 | 配方册补 R-6..R-8 三条本班新踩坑 + 一键册引用改号 |
| q-20260926-st-zmaster-20260926-0003 | `35bdc5a47b`（15:58:14） | 20 | **红队回流修订**：一键/台账/配方按二次复验改 9 处假命令口径；02 册加 §六 X-59..X-66 与 §七 波 0 实测；10 册补波 9（W-140..W-162）；00 册补族 13；92 册补 G-70..G-72；93 菜单收回一条空头承诺并补两条"呈裁内部丢失"；红队两册入卷 + 2 条 token |

### 红蓝对抗（本班自开的两路独立攻击，不是走过场）
- RT1（可操作性）33 条立卷、RT2（覆盖率/越界）21 漏项 + 12 越界 + 35 复算。**两路都含假 P0，本班逐条二次复验后驳回 5 条**（`git_commit.py --session/--adopt-prior-work` 实存、`lane_ff_mine` 实存、`commit_queue status --session` 确为 JSON 头、图12/13 `--map` rc=0、"129 个目录"另有口径），其余成立项全部改入正文——明细见 02 册 §六 X-59..X-66。
- **本班被红队抓到的最严重两条，都是对 Owner 的不实**：①菜单里写"我已改为杀前复验身份"（实际未做，W-41 态 ⬜）；②裁定正文写"我已按加严恢复启用三台门"（实际未做且属越界，那三台的禁用态名册注释自述为 Owner 批准）。**两句均已收回并改成实话**（`01` 册 ⚑-3 / `93` 菜单 ⚑-3 附带条 / `93` ⚑-6-3）。
- 红队还抓到一条结构性缺陷：**本班"编目完整、排产有洞"**——骨架册收得下条目，波次表只排了一半，而 Flash 只照波次表动手。已补波 9，并新增 G-70 尺（W-xx 无波次归位即停下登记）。

### 波 0 由本班代做的结果（原计划交给 Flash）
76 条车道固化、约 140MB，冷库镜像 `G:\zephyr_cold\30_corpus\zmaster_lane_rescue_0926` 与本地 **673 文件等值**；**实测 25 条车道有数百项脏内容而自有 commit＝0**（含六图役、波2 役 169 项、全部 `lane_ff_*`）⇒ 这是"随时可被一次还原抹光"的面，补丁已双存。

**验真（两轮同命令，结果一致）**：`.runtime/tmp/total_command_closeout/verify_head_bytes.py`（⚠ 该脚本在 `.runtime/tmp` 下受 24h TTL 清理，波 8 前可能已消失；重建口径＝逐件比 `sha256(盘 bytes.replace(CRLF,LF))` 与 `sha256(git show HEAD:<path>)`，**比尺寸会漏判等长改动**） → `件数: 17 / 与 HEAD 不等件数: 0`（sha256 口径，非尺寸口径——第一版用尺寸比较把 91 册的等长改动误判成 same，已改）。
**token 在册核**：`git show HEAD:...capability_canonical_file_registry.yaml | grep -c governance-total-command-closeout` = **17**。
**顺带落地的他人在途条目**（已在 commit message 具名披露，非本役主张）：`docs/_working/decision_map_campaign_20260924/HANDOVER_FINAL.md` 的 1 条 token。
**顺带修复的公共基底**：热册补回被陈旧快照抹掉的 **16 条** HEAD token、合并重复顶层根键 `di_seam_exemptions`（`REGISTRY-YAML-PARSE` 拦点）、index 陈旧快照回正（B 型 `git restore --staged`）。修复前备份 `.runtime/tmp/total_command_closeout/backup/capability_registry.pre_repair.yaml`（sha256 前缀 `525004b1d240fac3`）。

## §一 复核命令（Owner 或下一班可直接照抄）

```bash
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:$PATH"; cd /d/ZephyrAlpha
# 1) 基线读数（本班全部判断的分母）
python --version
python -m zephyr.trading.process_reaper --status | grep -o "watermark=.*"
# 注意：stdout 末尾另有一行 ALERT:{...} 且是 CRLF ⇒ 直接 json.load 必崩；取首尾大括号之间再解
python scripts/commit_queue.py status 2>/dev/null | python -c "import sys,json;r=sys.stdin.read();print(json.loads(r[r.index('{'):r.rindex('}')+1])['counts'])"
git log -1 --format="%h %ci %s"
# 2) 热册三态分诊（本班救回 16 条被陈旧快照抹掉的 token，配方 R-1）
R=docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml
git diff --numstat -- $R; git diff --cached --numstat -- $R
python .runtime/tmp/total_command_closeout/repair_capability_tokens_v3.py     # 只读分诊；输出行标签是 "missing=N disk_only=M"（不是"盘缺HEAD="）
python .runtime/tmp/total_command_closeout/check_registry_faces.py           # 三态键集合差；标签是 "HEAD - DISK = N"
# 3) 在册 vs 声称（三条最有杀伤力的抽查，均为"声称在册、实测不在"）
git ls-tree -r --name-only HEAD | grep -c "scripts/governance/next_ruling_id.py"                      # 0
git cat-file -e HEAD:scripts/governance/fullflow/generate_fullflow_crosscheck.py 2>&1 | head -1       # 不存在
git ls-tree -r --name-only HEAD | grep -cE "config/(dev_delivery_map|data_supply_chain_map|trading_day_cycle_map|construction_workflow_map|strategy_card_lifecycle_map)\.yaml"   # 0
# 4) 门禁装载守恒（名册 vs 实载）
mkdir -p .runtime/tmp/<SID> && echo probe > .runtime/tmp/<SID>/msg_probe.md   # 预跑器要求 message-file 实存，否则直接 FAIL
python scripts/governance/meta/gate_prerun.py --session <SID> --files "AGENTS.md" --message-file .runtime/tmp/<SID>/msg_probe.md 2>&1 | tail -6
# 装载守恒自查：名册条数 vs 预跑器报的 "注册 GateSpec 总数"（本窗实测 99）
# 5) 本班交付物是否真在 HEAD（落地后）
git show HEAD:docs/_working/total_command_closeout/02_field_corrections_and_new_cases.md | head -20
```

## §二 三清单

### A. 裁定项（本班产出：Z 类 63 条自裁 + X 类 52 条改判 + W 类 101 个环节 + G 类 38 把尺）
- `01_adjudication_master.md`：Z-00（三条基线律）+ Z-01..Z-63，覆盖 11 份交接书的全部归属/门禁/数据/灾备/治理/考试/元问题/安全/六图乙类九案/波2 C·B 类分流。
- `02_field_corrections_and_new_cases.md`：X-01..X-40（撤案 10 条、新案 22 条、口径改判 8 条），并定义证据分级 E1–E4。
- **Owner 门位收敛**：真待裁 5 件 + 安全默认 12 件（`93_owner_menu.md`）；交接书原呈的 ~40 件"待裁"中 21 件被实测判为"可做/已裁/误诊"。

### B. 执行项（本班实际动过盘的动作，全部可回滚）
| 动作 | 对象 | 凭据 |
|---|---|---|
| 冷启动三连 | — | reaper last_run=14:21:29、degraded=False、commit_pct=51.52%（E1） |
| 会话注册 | `st-zmaster-20260926`（pid=0） | `SessionRegistry.register` 返回并 heartbeat |
| 新建目录 | `docs/_working/total_command_closeout/`、`.runtime/tmp/total_command_closeout/` | 目录名无数字后缀（避 R5） |
| **热册 index 回正** | `capability_canonical_file_registry.yaml` | `git restore --staged`（B 型，index 陈旧快照 −106 行 → 与 HEAD 等值）；写前已备份 `.runtime/tmp/.../backup/capability_registry.pre_repair.yaml`（sha256 前缀 `525004b1d240fac3`，2,899,689 B） |
| **热册盘上纯插入** | 同上 | v3 脚本：`missing=16 disk_only=1` → 写后 `HEAD tokens=11391 DISK tokens=11394 盘缺HEAD=0`，`yaml.safe_load` 过、`creation_tokens entries=11394`；CAS `safe_write_text(base=content_sha256)`，`.written=True` |
| token 登记 | 本班两册 | `batch_creation_tokens.py --merge-evaluation ...`；`grep -c governance_total_command_closeout` = 2 |
| 门禁预跑实调 | 本班两册 | 第 1 次：内容硬阻断 1（CREATE-GUARD）+环境信号 1（WORKTREE-REQUIRED）+GateSpec 99；第 2 次：**内容硬阻断 0** |
| 八案卷派单 | dossier_A..H | 六案卷已回（A/B/C/D/E/G 共 1,600+ 行读数），F/H 待回；全部零 git 写、零改他人文件 |
| 只读探测（含一次副作用） | 主区 `align_all.py` | **副作用披露**：案卷 C 为取签名在主区跑 align_all 2 次，跑后 `M config/governance_operations_map.yaml(+1568/−1562)`、`M docs/03_modules/architecture_model/index.yaml(+1/−1)`；主区原有 467 项脏面且未前置留证 ⇒ **不可归因**，故本班**不 revert 不吸收**，仅登记（见 91 册第 6 步）。真实退出码 1，签名=GOMAP 机生层漂移 10 硬（**不是** PG 缺失，与六图令叙述不符） |

### C. 复查项（下一班/Flash 必须复验，本班未闭环）
1. **热册回退是否再发**：X-13 是"施工期正在发生的蒸发"，肇事进程未定位 ⇒ 每班开工先跑 G-08（键集合差），差 >0 即停批并取证。
2. **141 件 staged 删除**：归属查无（claim_snapshots/队列/stash 三处皆空），131 件盘上仍在 ⇒ 禁动；波 8 前复查一次是否被某道落地吸收。
3. **绕门案 X-11**（`30505c93f6` "四门临时禁用+emergency 通道"，678 件）：只出案卷，未核完。
4. **⚑-2 第 2 项**：2 格阴性的"同窗对拍"未做 ⇒ 成绩单未定稿前 T2 不发。
5. **CH `system.tables LIKE` 静默空返回**（X-26）与 `ch_writer.query` 异常返回 `""`（X-27）：两个判据污染面，涉及既有案卷的历史结论需重跑。
6. **波 0 快照未完成**：本班只建目录未跑全量 rsync/镜像（预算给了裁定与方案）⇒ 由 Flash 波 0 首件执行。
7. **sector_constituent 滞后 21 天**（X-21）：影响面（三处采集宇宙）未量化。
8. **`scripts/data/audit_*.py` 改名在途**（他道 claim）：本班热册修复保留了那条外来块，落地时禁把它卷进自家袋。

## §三 本班判断的"最治本一条"（Owner 曾追问哪个最治本，这里预先答）

**一条**：把"**声称已落地**"这个动作本身变成可机判的尺（G-05：任何"已完成"陈述必须给出 `git show HEAD:` 逐符号计数，否则不得进台账）。
理由：本班 40 处改判里 **26 处**的根源都是同一形态——工棚里的成品被叙述成已入库、旧快照的回退被叙述成已修复、模块常量被叙述成 flag。这不是某班的错，是**缺一道把"自述"与"库内"对账的常设面**（本仓已有 EV-01 黑匣子与"快照自洽见证层"，但都在提交链一侧，没管交付叙述）。
代价：这条不产出任何新业务能力，买的是"系统说好了的时候您有权信"；且它会把过去两周里被误记为"已完成"的约 30–60 件重新变回"未完成"——**账面会变难看，这是全部代价**。
