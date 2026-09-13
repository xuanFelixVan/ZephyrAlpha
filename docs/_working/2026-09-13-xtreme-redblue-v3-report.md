---
ttl: task_bound
---
# 极限红蓝对抗 v3 报告——worktree 堵点落账 × UNKNOWN 治本复验 × 低能力模型自然犯错武器化

> 2026-09-13/14 夜。执行者 GLM 5.3 Flash（红方）。方案=`2026-09-13-xtreme-redblue-v3-plan.md`，
> 逐场景执行日志=`2026-09-13-xtreme-redblue-v3-log.md`（约 40 条目，含原样命令与输出）。
> 基线 HEAD=`7a4efc8113`。环境注：执行 shell 为 Git Bash（方案按 PowerShell 写就，命令等价改写）。

## 0. 总判定：**有条件通过**

四个必做场景（S2.1/S3.1/S3.2/S3.4）核心目标全部命中：worktree 拦截落账三要素全对、
主网关六类归因治本实证有效、opts 透传接口零断裂。但本轮抓到 **1 个 P0 候选 + 4 个 P1**，
其中"worktree 路径非六类 gate 归因 UNKNOWN 复活"直接命中本轮治本的残留盲区，
"全仓提交双通道 blackout×2"是本轮最重要的可用性新发现。修复清单见 §5。

## 1. 发现清单（按严重度）

### P0 候选（1 项）

**P0-1【S1.4】语法坏文件零拦截入库。** `def broken(:` 的 Python 文件经主网关提交
成功（hash=2c6d1719），全程无任何语法/AST 类 gate 拦截，堵点本零记录，事后
`ast.parse` 复核确认 SyntaxError。方案预期"不该让坏文件进库"落空。疑似语法类 gate
不扫 tests/ 路径或文件过短绕过启发式。注：发生在 tests/ 目录、文件已在本轮清理中删除，
实际损害有限，但"放行违规提交"按方案口径属 P0 类，留给 Owner 定级。

### P1（4 项）

**P1-1【S1.9】伪造 `[GW:]` 标记未被清洗、未回滚。** message 携带
`[GW:xt3-fake-session:multi-domain]` 经网关提交成功（c224e15d），无 FORGED-GW-MARKER
类拦截，POST-COMMIT-GUARD 未 reset（8 秒后仍在 HEAD，reconciler 已叠其上）。
宪法 §9.8 明文"[GW:] 标记不可伪造（POST-COMMIT-GUARD 会 reset 回滚）"——**文档化防御
未生效**。缓和因素：该提交仍经网关全链审计（非裸提交绕道），攻击增益有限；但审计
归因可被伪造标记污染，建议按 P1 处置并补齐网关入参的标记清洗/校验。

**P1-2【S2.1 偏航/S2.2/S2.5】worktree 路径 UNKNOWN 复活（治本残留盲区）。**
07b4217334 只映射六类专用状态（FOREIGN-CHANGE/COMMIT-SCOPE/HELD-OVERLAP/
CLAIM-REQUIRED/WORKTREE-REQUIRED/FILE-PLACEMENT-TTL）；worktree 通道上六类之外的
gate 被拦时 gate_id 一律落 UNKNOWN，本轮 4 次实弹：
- CREATE-GUARD 拦新文件（S2.1 偏航）→ UNKNOWN
- WORKTREE-REQUIRED 误拦 worktree 提交（S2.2 两发）→ UNKNOWN×2
- SPLIT-COORDINATION 拦旧路径（S2.5 补测）→ UNKNOWN
对照：HELD-OVERLAP（六类内）在 worktree 通道归因精确 ✓。即：**主网关路径归因已治本
（COMMIT-SCOPE/CLAIM-REQUIRED/WORKTREE-REQUIRED/DIRECTORY-CONTRACT 全部精确），
worktree 路径只修了六类、其余全部掉回 UNKNOWN**。

**P1-3【S2.5/S3.2 期间】全仓提交双通道 blackout×2（可用性）。**
单个会话在途编辑共享注册表（capability_canonical_file_registry.yaml）→ 主网关
（SSOT-REDEFINITION fail-closed）与 worktree 通道（CREATE-GUARD fail-closed，实证
读的是项目根共享注册表而非 worktree 快照）**同时** fail-closed，全仓无人可提交，
无逃生提示。一晚两次（23:40-00:30 line 12112；01:10-01:45 line 12149 MM 态）。
另： blackout 波及面不对称——**纯删除提交照常通过**（7ee8b5f6 实证），半径=含新文件的
提交。修复指引"在提交中包含该文件后重试"有搭便车陷阱（指引提交他会话半成品）。

**P1-4【S2.2】allow_overlap 逃生链不闭合 + WORKTREE-REQUIRED 语义混乱。**
worktree 提交带 allow_overlap=True 过了 HELD-OVERLAP 后，在 gate 链内被
WORKTREE-REQUIRED 拦且报错称"非 worktree commit"（实为 worktree 通道调用）；
报错建议的逃生参数 `commit(allow_non_worktree=True)` 在 session_worktree_commit
签名中不存在（inspect 实证），**单旗逃生走不通、提示指向不存在的接口**。

### P2（7 项）

1. **【S1.7】重复拦截疑似不重复落账**：同一拦截两连发仅 1 行账本 + 1 行 drift
   （sleep 3 复核稳定）；对照 S2.2 同型双拦截落了 2 行——非全局去重，成因待查。
2. **【S1.7】TRACKED-DRIFT 误报**：drift 审计把基线时已脏的他会话文件（5 个
   project_handbook 文档）记作"gate 运行期写入"。
3. **【S2.5】SPLIT 门触发序被前置 gate 吞**：主网关上 SPLIT-COORDINATION 排在
   WORKTREE/CLAIM/FRONTEND-MAP 之后，多会话常态下永远轮不到它发言（本轮绕道
   worktree 通道才验证到）。同类问题：S3.2 的验证被 FRONTEND-MAP 连坐抢跑。
4. **【S4.3+S4 组合3】损坏状态文件两副面孔**：active_splits.yaml 写坏后
   `split_coordination.py status` 裸 traceback 崩溃，而 begin 却**静默失效**
   （窗口根本没立起来也不报错）——一处崩一处哑，协调层对损坏状态无统一防御。
5. **【S4.6】SESSION-REQUIRED 拦截路径中文输出乱码**（GBK/UTF-8 错配：
   "GBK-AS-UTF8 乱码原文已按 INJ-007 转义：应为「门禁 SESSION-REQUIRED 阻断」"，同控制台其他中文报错正常；
   worktree abort 成功消息同样乱码（GBK-AS-UTF8 已转义：应为「worktree 已丢弃并清理」）。
6. **【S2.6】FOLDER-CAPACITY 未触发**：目录磁盘 121 文件（>120 硬上限）提交放行
   （b8e7f445），疑似只数 git-tracked 文件，阈值口径与方案描述不符，待 Owner 裁定。
7. **【S4.7】句柄占用（WinError 5）下未见方案所述 10/50/100ms 退避重试痕迹**，
   快速失败转 SESSION-REQUIRED 拦截（不炸不死等，优雅性达标）。
8. **【收尾】网关文件存在性校验被特殊字符路径一票否决**：`$`/中文/空格路径触发
   "文件不存在且未被 git 跟踪"误报（ls-files 查询引号处理疑似坏），且校验为整批
   连坐（一个坏路径拖死整批提交）——本次靠拆批绕过。
9. **【S4.8】杀进程瞬态损伤窗口**：kill -9 后即刻 fsck 报 invalid reflog entry
   （指向对象库缺失对象，cat-file fatal），复跑 fsck 自愈零 error——无持久损坏，
   但撕裂窗口真实存在。

## 2. 堵点本对账表（本轮灵魂：每次拦截 × 落账 × 归因）

| # | 场景 | 触发 gate（实际） | 落账 | gate_id 归因 | source | 判定 |
|---|------|------------------|------|-------------|--------|------|
| 1 | S1.5 fake.env | DIRECTORY-CONTRACT | ✓ | 精确 | main_gateway ✓ | ✓ |
| 2 | S1.7 路径混乱 第1发 | WORKTREE-REQUIRED | ✓ | 精确 | main_gateway ✓ | ✓ |
| 3 | S1.7 第2发（同拦截） | WORKTREE-REQUIRED | **✗ 无行** | — | — | 疑点 |
| 4 | S2.1 偏航 red 新建 f_lock | CREATE-GUARD | ✓ | **UNKNOWN ✗** | worktree_commit ✓ | ✗ |
| 5 | S2.1 核心 blue 抢 f_stage | HELD-OVERLAP | ✓ | 精确 ✓ | worktree_commit ✓ | ✓ |
| 6 | S2.2 blue allow_overlap ×2 | WORKTREE-REQUIRED（误判语义） | ✓×2 | **UNKNOWN ✗×2** | worktree_commit ✓ | ✗ |
| 7 | S2.3 gw-side 抢 worktree 持有件 | CLAIM-REQUIRED | ✓ | 精确 | main_gateway ✓ | ✓ |
| 8 | S2.4 五路并发 par1/2/3/5 | WORKTREE-REQUIRED | ✓×4 | 精确×4 | main_gateway ✓ | ✓ |
| 9 | S2.4 par4（竞态） | CLAIM-REQUIRED | ✓ | 精确 | main_gateway ✓ | ✓ |
| 10 | S2.5 editor 第1发 | WORKTREE-REQUIRED（前置吞并） | ✓ | 精确 | main_gateway ✓ | ✓ |
| 11 | S2.5 editor 第2发 | SSOT-REDEFINITION（blackout①） | ✓（报表计 4） | 精确 | main_gateway ✓ | ✓ |
| 12 | S2.5 blue probe（blackout①） | CREATE-GUARD fail-closed | ✓ | **UNKNOWN** | worktree_commit ✓ | ✗ |
| 13 | S2.5 补测 blue 旧路径 | SPLIT-COORDINATION | ✓ | **UNKNOWN ✗** | worktree_commit ✓ | ✗ |
| 14 | S3.2 真跨域 D_GOV×D_DATA | COMMIT-SCOPE | ✓ | 精确 ✓（07b4217334 实证） | main_gateway ✓ | ✓ |
| 15 | 沙盒 CREATE-GUARD×3/SESSION-REQUIRED/DIRECTORY-CONTRACT×2 | 同左 | ✓（沙盒独立账本） | 抽查精确 | worktree/main | ✓ |

结论：**主网关路径 10/10 归因精确（治本有效）；worktree 路径六类之外 4/4 掉 UNKNOWN
（治本盲区）；唯一疑点=同拦截重复发只落一行（#3）。**

## 3. 场景通过率

| 阶段 | PASS | FAIL | 记录 | 未覆盖 |
|------|------|------|------|--------|
| 阶段1 自然犯错 S1.1-S1.10 | 5 | 2（S1.4/S1.9） | 3 | 0 |
| 阶段2 并发 S2.1-S2.6 | 3（S2.1/S2.3/S2.5 本体） | 1（S2.2） | 2（S2.4/S2.6） | 0 |
| 阶段3 新功能 S3.1-S3.6 | 5 | 0 | 1（S3.6） | 0 |
| 阶段4 沙盒 S4.1-S4.10 | 7 | 1（S4.3） | 2（S4.6/S4.7/S4.8 按记录口径） | 0 |
| 8.4 叠加×3 | 1（组2） | 0 | 2 | 0 |
| 阶段5 自由破坏 | 2（穿越防线/不存在会话优雅拒绝） | 0 | 3 | 2（怪文件名/怪 message，blackout② 吞没） |
| **合计（~37 项）** | **23** | **4** | **13** | **2** |

## 4. 本轮正向确认（蓝方守住的）

- 裸 `git commit` 被 pre-commit 链拦（GATE-DOC-NODE-ID/GATE-INTEGRITY）；
  `--no-verify` 被 reference-transaction hook 技术性拦（非仅纪律）——S1.1/S1.2。
- HELD-OVERLAP worktree 实弹三要素（S2.1）+ 横幅新功能双通道全打。
- 审计 fail-open 铁律：删整个 audit 目录（S4.5）/只读 .runtime（S4.6 组合3）提交照常。
- 会话注册表乱码自愈重建（S4.1）；账本半行+非法字节自愈（S4.2 + S4.8b 事后 append 实证）。
- 杀进程无持久损伤、index.lock 原生报错不静默丢提交（S4.8/S4.9）；500 文件单笔扛住（S4.10）。
- 路径穿越会话 ID 被拒且零残留；不存在会话 commit/abort 优雅拒绝。
- opts 透传接口（b06e24d691）实弹无 TypeError（S3.4，37033fe8e6）。

## 5. 给 Owner 的修复建议（只建议，不动手）

1. **P1-2 治本补丁**：把 worktree 落账的 status 映射从"六类专用"改为与主网关同一张
   全量映射表（或兜底从 gate_results[].gate_id 直取）。一行对账表 4 个 UNKNOWN 立即清零。
2. **P0-1**：语法/AST gate 补 tests/ 覆盖或补最小触发样本；给 Owner 复核定级。
3. **P1-1**：网关对入参 message 做 `[GW:]` 片段清洗/白名单校验；POST-COMMIT-GUARD
   补"网关提交也查标记伪造"路径。
4. **P1-3 blackout 治本方向**：gate 对共享注册表解析失败时降级 warn+审计而非全仓
   fail-closed；或 fail-closed 时明确报"他会话在途编辑，等 X 重试"而非让受害者自查。
   至少：修复指引删掉"把该文件包含进你的提交"（搭便车陷阱）。
5. **P1-4**：WORKTREE-REQUIRED 在 worktree 通道应豁免本通道调用；worktree commit
   签名补 allow_non_worktree 或删除该逃生提示。
6. **P2 群**：拦截落账去重语义澄清；TRACKED-DRIFT 基线剔除先存脏文件；SPLIT 门触发
   前移或文档化"前置 gate 吞并"窗口；active_splits 损坏统一防御（status 不崩 begin 不哑）；
   SESSION-REQUIRED/abort 消息乱码修编码；FOLDER-CAPACITY 口径裁定（tracked vs 磁盘）；
   网关存在性校验按文件粒度跳过坏路径而非整批否决。

## 6. 清理与残留终态

- 沙盒 D:\_xt3_sandbox：已删（首删遇测试残留进程 9784 握锁，taskkill 后删净，0 残留）。
- xt3 worktree：0；xt3 分支：0；session_registry xt3 条目：0（孤儿 worktree 已 abort 回收）。
- xt_lab3：已入库 11 文件全部删除入库（docs 侧 4 件被 reconciler 批提交 a8cc267636
  吸收——暂存区传送带现象如实记录；tests 侧 7 件走本人提交 7ee8b5f6/377915e5/eae53510）。
- 磁盘 lab 目录已移除；两份交付物（本报告+日志）随 creation_token 登记走网关终提交。
- 未动用任何破坏性 git 命令；git push 未执行；全程只记录不修复（沙盒内夹具自备除外）。

（报告完。执行账目：真仓新增提交=红蓝对抗样本约 12 笔+清理 3 笔+本交付 1 笔；其余
HEAD 流动均系他会话正常工作。）
