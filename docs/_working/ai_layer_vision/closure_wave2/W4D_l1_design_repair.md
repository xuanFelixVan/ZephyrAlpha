---
ttl: task_bound
volume: W4D_l1_design_repair
session: st-ailayer-final-20260924
creation_token: w4d-l1-design-repair-20260926
---

# W4-D 车道案卷：L1 DESIGN 正文错配事实钉死与归位修复（含 11 本 DESIGN 自洽扫描）

> 派单真源=`docs/_working/fullflow_mining/94_chief_rulings_wave2.md` §三"AI-2 L1 DESIGN 正文实为 L4 稿"行
> （总筹判=文档矛盾事故，宪法 §4.3）；提出方=`docs/_working/ai_layer_vision/closure_wave2/AI2_scheduling_host_confirm.md` §五.1。
> 作业规范=`docs/_working/fullflow_mining/92_chief_command_wave2.md` §一（零提交/零入队/只写自己路径/禁触热册）。
> 工作面=worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`（分支 `ai/st-ailayer-final-20260924/fullflow-closure`）。
> 本卷性质＝案卷（非裁定）；未自赋任何裁定号，未写 Owner 署名。

## 一、11 本 DESIGN 自洽性扫描表（机械三问，非肉眼）

扫描法：问 A＝frontmatter `title` 声明 vs 正文 H1/本文性质主题；问 B＝正文施工项编号前缀 vs 目录归属；
问 C＝与同族其它 DESIGN 是否字节级重复（sha256 全表）；问 D＝该段骨架卡（README §状态）描述 vs DESIGN 正文。

| # | 文件 | title 声明 | 正文主题 | 施工项前缀 | sha256(前 8) | 行数 | 判定 |
|---|------|-----------|---------|-----------|-------------|------|------|
| 1 | `L1_perceive/DESIGN.md` | 改前=L4 对比段／**改后=L1 感知段** | 改前=L4 通用对比器／**改后=L1 外扫+内监** | 改前 C1-C8／改后 1-9 | 改前 ebd7269a→**改后 2ff581c5(基底)+追加** | 改前 211→**改后 328** | **不自洽（唯一一处）＝L4 稿整档覆盖 L1 稿** |
| 2 | `L2_intake_library/DESIGN.md` | L2 收集段 | L2 原材料库 | T 系（L2 自有） | 68b5b591 | 281 | 自洽 |
| 3 | `L3_cleaning/DESIGN.md` | L3 清洗段 | L3 强模型消化 | 本稿项内自指 | 4a848ee7 | 241 | 自洽 |
| 4 | `L4_compare/DESIGN.md` | L4 对比段 | L4 通用对比器（**停在 R2 旧版**） | C1-C8 | b1734c99→**改后含 2 行销账+归位记录** | 211→223 | 主题自洽；**版本落后＝第二处病灶（同根，已归位）** |
| 5 | `L5_schedule_gate/DESIGN.md` | L5 排产段 | L5 门闸与派工 | 本稿项内自指 | 7a517cb8 | 289 | 自洽 |
| 6 | `L6_ab_switch/DESIGN.md` | L6 切换段 | L6 影子运行 | ①-⑥ 节序 | beadb8ed | 278 | 自洽 |
| 7 | `L7_heredity/DESIGN.md` | L7 传承段 | L7 传承库 | 引用 C8 为他稿交叉 | 965049c6 | 291 | 自洽；`status: design_final`（2026-09-26 翻转，注释内自带出处） |
| 8 | `OBJ_M_models/DESIGN.md` | OBJ_M 模型对象线 | M1-M5+接线图 | M1-M5 | 9e49ad99 | 415 | 自洽 |
| 9 | `OBJ_R_rules_standards/DESIGN.md` | OBJ_R 标准与规则线 | 历史重放器 | S3/R 系 | f966e820 | 246 | 自洽 |
| 10 | `OBJ_S_perimeter/DESIGN.md` | OBJ_S 红线与自由域 | 负面清单机检 | S1-S6 | 9053508b | 307 | 自洽 |
| 11 | `OBJ_T_tools/DESIGN.md` | OBJ_T 工具对象线 | T1-T6+接线图 | T1-T6 | 9602345d | 329 | 自洽 |

**扫描结论**：
1. **正文错配＝1 处**（L1 路径挂 L4 稿）；sha256 全 11 本互不相同，无第二对"一本稿挂两名"。
2. **同型错配的另一种形态＝版本错配 1 处**：L4 自家文件缺 2026-09-24 的两行更新（那两行只存在于
   被误写到 L1 路径的副本里）——即"稿的新版住在错的家里"。已同批归位（见 §四）。
3. 其余 9 本 A/B/C/D 四问全过；各段 README 骨架卡 `status: design_done` 与 DESIGN 存在性一致（唯一
   不一致的就是改前的 L1：README §状态 明文描述"源注册表 v1 十二源/9 施工项"，正文却是 L4——本项即
   错配的独立第二证据）。

## 二、事实钉死（逐 commit 取证，不顺着上一车道叙述写）

对 `L1_perceive/DESIGN.md` 与 `L4_compare/DESIGN.md` 两个路径按提交序取字节指纹（`git show <c>:<path> | sha256sum`）：

| 提交 | 日期 | L1 路径内容 | L4 路径内容 |
|------|------|------------|------------|
| `fc3e1e2e5f` L1 作业簿挖干 | 2026-09-17 | `ab2738f1` / 250 行 / title=L1 感知段 | （彼时 L4 件已由 `18226c4881` 建：`547d5ff6` / 195 行） |
| `18e472b0e2` 红蓝 R1 | 2026-09-17 | `e931eb2a` / 263 行 / title=L1 | `ea692712` / 207 行 / title=L4 |
| `c0f5cc47b8` 红蓝 R2 | 2026-09-17 | `3baf17e6` / 272 行 / title=L1 | `b1734c99` / 211 行 / title=L4 |
| `9e612ba38d` 红蓝 R3 | 2026-09-17 | **`2ff581c5` / 272 行 / title=L1（本次复原基底）** | `b1734c99`（未变） |
| `30505c93f6` AI 层 P1 终局大单 678 件 | 2026-09-26 | **`ebd7269a` / 211 行 / title=L4＝正文被 L4 稿整档覆盖** | `b1734c99`（未变） |

**是哪一段的稿**：L1 路径在 `30505c93f6` 起的正文＝**L4 对比段稿的较新版本**——与 `L4_compare/DESIGN.md`
逐行 diff 只差 2 行（第 32 行 §1 受阻记录、第 112 行 §2.5 三查③），且 L1 路径那 2 行带
"销账：2026-09-24 实网核验完成"字样＝L4 稿 09-24 修订后**写进了错误路径**。

**肇事提交面**：`git show --name-only 30505c93f6 | grep ai_layer_vision/.*DESIGN` 全仓仅命中
`L1_perceive/DESIGN.md` 一件（同批未碰其它 DESIGN）＝单文件写错路径，非目录级重排。

**取证通道现状（已亲测，非引用记忆）**：LEDGER_final.md 在册"staging 母本 36 件覆盖（masters 最新真值）"
同型事故家族提示机制可能是蒸发抢救期用错母本/路径；但主区 `.runtime/sessions/*/staging/` 实测
`find -name DESIGN.md -path *staging*` 与 `find -path *L1_perceive*` **双双零命中**＝母本已被 purge，
**机制层面不可证**，本案只对"事实链＋归属"负责，不对"谁按错了哪个键"下结论。

## 三、意图核验：判"事故"而非"有意双稿"（四条反证＋一条支持）

判"有意双稿/待迁移"需要台账记录；实测**查无**：
- `LEDGER_final.md`、`P1_full_construction_inventory.md`、`P1_final_report_20260924.md`、
  `closure_wave2/AI1-AI4` 四册 grep `双稿|挂 L1|误挂|错挂|待迁移`＝零命中；
- 反向证据 ①`L1_perceive/README.md` §状态："2026-09-17 深挖完成：真源设计稿=DESIGN.md（源注册表 v1
  十二源五轨…9 施工项…）"——骨架卡描述的对象与 L4 正文无一处对得上；
- ②`ai_layer_closure_report.md`（2026-09-24 只读结案）逐节点名实证当时该路径是**完整 L1 稿**
  （§2.1 12 源注册表/§2.2 五探测器接线图/§2.3 任务单 schema/§四 9 施工项/§六 自审闸"施工 8+挂起 1"）；
- ③代码侧消费者按 L1 语义读它：`src/zephyr/ai_layer/perceive/__init__.py` 头注"设计真源：
  docs/_working/ai_layer_vision/L1_perceive/DESIGN.md"；`scripts/ai_layer/gen_search_veins.py:32` 同款声明，
  且 `:140-141` 直接取该文件 frontmatter `title` 作 `VEIN-AI-L1` 的 `name_zh`/`keyword_seed`；
- ④登记面：`capability_canonical_file_registry.yaml` 能力条目 `ai_perceive_l1`（:5065-5074）把该路径
  登记为 L1 能力真源；同册 :28247 的 token 条目亦以该路径归 `ai_layer_vision` 能力族。

**支持"事故"的量化后果（非臆测，可复核）**：`config/ai_search_veins.yaml` 现值 `VEIN-AI-L1.name_zh`
仍是正确 L1 标题（＝污染未落地，是错配期的旧派生），但**任何一次重跑矿脉生成器都会把 L1 矿脉改名成
L4 标题**（AI2 车道 §一 异常披露已 dry-run 复现并回退）；下班若按 L1 路径施工会拿到 L4 的 C1-C8 清单。
⇒ 与总筹"文档矛盾＝事故"判性一致；**无需停手上报项**。

## 四、修法与改动清单（最小改写：git 逐字节回置＋纯追加，判据零改动）

| 文件 | 改法 | 机械证据 |
|------|------|---------|
| `docs/_working/ai_layer_vision/L1_perceive/DESIGN.md` | ①正文＝`git show 9e612ba38d:<该路径>` **逐字节回置**（零重写）；②文末**纯追加**两节：§七 施工项现状对账（9 项逐条实测出处＋缺位判据）、§八 错配事故与复原记录；③修订记录表补 1 行（1.0.1 复原+对账） | 对 git 基底 diff＝**0 行删除 / 56 行新增**（`diff <(git show 9e612ba38d:…) <文件>`）；行数 211→328；`title` 实测=L1 感知段真源设计稿 v1；基底 sha256 前缀 `2ff581c5` 复现 |
| `docs/_working/ai_layer_vision/L4_compare/DESIGN.md` | 把只存在于 L1 路径的两行 L4 新版内容（EX-R1 销账，2026-09-24）**原样搬回本路径**＋追加"归位记录"一节（含实证 `too_good.py:148 SPEC_GAMING_CITATION` 与待总筹的 creation_token 一行） | `git diff --numstat`＝**14 增 / 2 删**；未改任何判据/阈值/触发线（G1-G5、α、K、q、ICIR 等原样） |
| `docs/_working/ai_layer_vision/closure_wave2/W4D_l1_design_repair.md` | 本案卷（新建） | 本文件 |

**未做的事（纪律边界）**：未改 `config/**`（含 `ai_search_veins.yaml` 的再生）、未改 `src/**`（含
`perceive/__init__.py` 里重复出现两次的 `from . import translator` 这处可疑瑕疵，见 §五.末）、
未碰 `docs/01_policies_and_standards/_registry/catalogs/**`、零 git add/commit/enqueue、未动任何 DESIGN 的
判据数值与状态行（L1 仍 `design_v1`、L4 仍 `design_v1`；翻转与否是总筹/Owner 的动作）。

## 五、L1 应有内容的实件核对（§七 取数底稿；全部盘上实测，禁凭记忆清单）

施工项 1-9 对账（详表已落 L1 DESIGN §七，此处只记核对方法与意外发现）：

| 项 | 现态 | 实测方法 |
|----|------|---------|
| 1 源注册表 | 主体已落（`config/ai_source_registry.yaml` 166 行：`sources` 12 slug＋`longtail_candidates` 2 条）；**ROOR 挂接缺位**（`docs/registry_of_registries.yaml` grep `ai_source_registry` 零命中） | `wc -l`＋`grep -n "slug:"`＋ROOR grep |
| 2 配额同步器 | 已落 `scripts/ai_layer/sync_ai_source_quota.py`（179 行）＋测试 `tests/ai_layer/perceive/test_quota_sync.py` | `ls`＋`grep -l ai_intake_source_quota` |
| 3 矿脉生成器 | 已落 `scripts/ai_layer/gen_search_veins.py`（318 行）→ `config/ai_search_veins.yaml`（416 行，REG-AIVEIN-001，27 脉全 active）；**ROOR 挂接缺位** | 同上 |
| 4 骨架即地图触发 | **缺位**：派生腿在件内（`:121-146`），但全仓 `gen_search_veins` 调用方只有 3 件（生成器自身＋月度体检＋tick），无"地图变更→自动再生"事件挂接 | `grep -rln` 调用面枚举 |
| 5 搜索任务单 | 已落 `perceive/search_orders.py`（400 行，`TRIGGERS` 含 `l7_prior`，`:76`） | `grep -n` |
| 6 内监翻译器 | 已落 `perceive/translator.py`（362 行） | `ls` |
| 7 外扫节拍宿主 | **半落不启用**：`scripts/register_ai_l1_scan_task.ps1`（94 行，工作区 `A`）双前置 fail-closed——`config/resource_profile_registry.yaml` 无 `ops_ai_l1_external_scan`、`ruling_registry.yaml` 无 `L1_EXTERNAL_SCAN_HOST` 标记（两 grep 均实测零命中）⇒ 与 94 册"不填节拍值/注册留 Owner 一行"一致，本车道未填值 | 两 grep＋AI2 册在册 exit 2 实测 |
| 8 月度体检生成器 | 已落 `scripts/ai_layer/gen_ai_layer_monthly_checkup.py`（371 行）＋测试 | `ls` |
| 9 L7 先验消费 | **实现缺位、解锁条件已成文**：`../L7_heredity/DESIGN.md:7 status: design_final`；`translator.py:18` 明文 l7_prior 不在射程；矿脉 `priority` 仍为常量 `VEIN_PRIORITY_DEFAULT`（`gen_search_veins.py:105/144`，产出面 27 条全 `priority: 1.0`） | `grep -n`＋`grep -c "priority: 1.0"` |

**顺带发现（不改，登记给代码车道/总筹）**：`src/zephyr/ai_layer/perceive/__init__.py` 内
`from . import translator  # noqa: F401` **重复两行**（一行为 ORPHAN 静态可见边补注，一行原样重复）——
疑为 30505c93f6 同批"重插"残留；属代码面且他道在途件，本车道零触碰。

## 六、待登项（交总筹单点落地，本车道零登记面写权）

1. **落地袋归属**：本车道 3 件产物（2 改 1 新建）需与 AI2/AI3 车道同族件同袋或独立袋，由总筹定；
   本车道零 `git add`。
2. **creation_token**：`W4D_l1_design_repair.md` 用 token `w4d-l1-design-repair-20260926`；
   L1/L4 两 DESIGN 的登记在册 token 仍是 `ai-layer-vision-design-20260916`（路径未变＝无需换绑，
   但 L4 DESIGN §5.3 第 4 项"DESIGN.md creation_token 补登"仍未销，见 L4 归位记录末行）。
3. **ROOR 挂接缺位两条**（`config/ai_source_registry.yaml`、`config/ai_search_veins.yaml`/REG-AIVEIN-001）＝
   登记面动作，禁本车道写 `catalogs/**` 与 ROOR。
4. **矿脉再生一行**（DESIGN 复原后使 L1 矿脉派生重新指真）：
   `python scripts/ai_layer/gen_search_veins.py --force`（属 `config/**` 写＝总筹窗口内执行）。
5. **depgraph**：本车道无新 .py 模块，无设计节点新增；两 DESIGN 为既有节点内容变更，
   待总筹在窗口内按 `RULE-DEPGRAPH` 判定是否需 `--force` 重建。
6. **翻译册**：无新模块，`module_translation_registry.yaml` 零需求。
7. **引用面回访（建议，非本案改动）**：`docs/_working/archive/2026-09/kimi_audit/lane_reports/C2.md`
   对 `L1_perceive/DESIGN.md:75-90 / :156-163 / :195` 的行锚在失配期悬空、复原后重新对位；
   archive 件为历史归档，本车道不回改。

## 七、复核命令（Windows PowerShell / Git Bash 均可，只读）

```
cd D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924
# 1) L1 正文＝git 基底的纯追加（期望 0 行删除 / 56 行新增）
git show 9e612ba38d:docs/_working/ai_layer_vision/L1_perceive/DESIGN.md > $env:TEMP\base_l1.md
git diff --no-index --numstat $env:TEMP\base_l1.md docs/_working/ai_layer_vision/L1_perceive/DESIGN.md
# 2) 两路径不再同稿（期望 sha 不同、title 各指本段）
sha256sum docs/_working/ai_layer_vision/L1_perceive/DESIGN.md docs/_working/ai_layer_vision/L4_compare/DESIGN.md
grep -m1 "^title:" docs/_working/ai_layer_vision/L1_perceive/DESIGN.md
grep -m1 "^title:" docs/_working/ai_layer_vision/L4_compare/DESIGN.md
# 3) L1 正文主题含 §四 9 施工项与 §七 对账（期望命中）
grep -n "源注册表 v1 定稿\|骨架即地图\|施工项现状对账" docs/_working/ai_layer_vision/L1_perceive/DESIGN.md | head
# 4) 矿脉派生现值仍是 L1 标题（污染未落地）
grep -n -A2 "^- vein_id: VEIN-AI-L1" config/ai_search_veins.yaml
# 5) 全 11 本 DESIGN 自洽扫描（title 与目录名互证）
for f in $(find docs/_working/ai_layer_vision -name DESIGN.md | sort); do echo "$f :: $(grep -m1 '^title:' $f)"; done
# 6) 改动面（期望仅 3 件，零代码零配置零登记）
git status --porcelain -- docs/_working/ai_layer_vision/L1_perceive docs/_working/ai_layer_vision/L4_compare docs/_working/ai_layer_vision/closure_wave2
```

## 八、三态结论

**完工**（本案指名面已闭环）：错配事实钉死＋11 本全扫＋L1 正文按 git 真源归位＋L4 新版两行归位＋案卷落盘。
**待挖**：施工项 4（地图变更→矿脉再生的事件挂接）与施工项 9（L7 先验消费的 priority/排除词表读取件）
＝代码面工单，本车道只出判据不出施工；ROOR 两条挂接缺位待登记班核。
**待裁**：净增 0——本案不涉四类 high 门位（未动生产流转/未净删注册表/未翻 flag/未碰资金）；
外扫节拍值与宿主注册仍按 94 册留 Owner 一行的原样，本车道未填任何数值。
