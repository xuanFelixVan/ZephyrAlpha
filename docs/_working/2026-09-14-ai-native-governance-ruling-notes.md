---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：治理档案（裁定/对质记录），长期保留。处置=**保留**。**
>
> **✅ 已完成（4 条，摘录）**
> - L9: > Ollama 生产部署），检索来源附文末。该施工的已施工，该提交的已提交。
> - L18: - **处置：不动，等 st-chinfra 自行落地。** 我的 7 个提交内容安全在 HEAD；兼容性已验证
> - L27: scripts/register_ollama_serve_task.ps1，家规样式）。注册后即实战验证：旧进程死→
> - L30: ## 裁定三：下一班工作清单 → **其中两件今天就该施工（已施工），两件维持事件门控**
>
> **⚠️ 未完成（2 条，逐条摘录）**
> - L44: ## 附：100% AI 开发治理发现（研究对照，含一条宪法级建议=留 Owner）
> - L52: **建议（宪法级，留 Owner 裁定，本班不擅改）**：重申 worktree 默认纪律，或将"降级直改"
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 1 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 架构裁定记录——四条披露的第一性处理 + 100% AI 开发治理发现

> 2026-09-14 策略工厂后端施工班（st-facbe-20260914）。应 Owner"客观专业架构师/第一性原理/
> 长远期战略"审查令而作；研究底稿=三路全网检索（因子挖掘赛道 / 多智能体编码治理 /
> Ollama 生产部署），检索来源附文末。该施工的已施工，该提交的已提交。

## 裁定一：他会话在途重构（5 文件）→ **放手不吸收**（归属已实锤）

- 排查证据：`.runtime/session_registry.json` 中 `st-chinfra-20260914`（PID 37752）**活跃在册**
  ——"chinfra"=CH 基础设施班，5 文件改动（裸 Client 构造→`ch_writer.get_client_strict()`）
  是其在途的 CH 客户端统一化批次的一部分（同签名改动遍布其名下更多文件）。
- 第一性原理：100% AI 开发中"会话"即员工，员工在岗时动其未提交的手稿=抢笔。项目宪法
  "他会话 WIP 不代修不吸收"在本例完全适用；原披露里"死会话遗产风险"已被活跃注册表证伪。
- **处置：不动，等 st-chinfra 自行落地。** 我的 7 个提交内容安全在 HEAD；兼容性已验证
  （以其改后盘面跑 56/56 测试全绿）。

## 裁定二：Ollama 进程随会话终端存活 → **已永久化治本**（施工完毕）

- 第一性原理：工厂 E2/E1B 依赖的本地 LLM 是常驻基础设施，其生命周期系于某个 AI 会话的
  shell = 违反"永久系统四要素"。业界标准答案（ollama/ollama#10713：Windows 版无
  services.msc 服务项）= Task Scheduler 任务跑 `ollama serve`，第二次启动端口冲突自退=天然幂等。
- **处置：`ZephyrAlpha_OllamaServe` 计划任务已注册**（AtLogOn 触发，无时限，
  scripts/register_ollama_serve_task.ps1，家规样式）。注册后即实战验证：旧进程死→
  Start-ScheduledTask 拉起→11434 返回 200。

## 裁定三：下一班工作清单 → **其中两件今天就该施工（已施工），两件维持事件门控**

| 项 | 裁定 | 理由（第一性） |
|---|---|---|
| v2 自定义算子批 | **今日施工 ✅** | 纯函数、独立、直接补齐 gplearn 缺失的量化标准积木（横截面排名/时序差分/标准化/滚动相关）——挖矿机的能力短板，留着=夜窗量产用残缺积木 |
| 公式预审"机制自述"提示词 | **今日施工 ✅** | E2 首战 7 条公式杀 6 条的根因=假说文本没给预审员可审的机制材料；供给端补释义=误杀率下降且不放松标准 |
| AlphaGen 立项 | **今日完成立项申请 ✅** | 检索实证赛道已换代（AlphaAgent/AlphaMuse/Chain-of-Alpha），立项书按"LLM 智能体挖矿轨"重新划界，等 Owner 批 P0/P1 |
| E7 模拟盘前哨 | **维持事件门控，不施工** | 向内收三原则：全厂尚无 E4 幸存者（双窗及格 1 条且已在他线 sim），E7 现在施工=无货可检的空转；触发事件=本管线产出首个 E4 及格策略。这不是拖延，是消灭空转 |

## 裁定四：记忆档案在 git 外 → **维持设计不变**

ZCode 记忆目录=跨会话工作记忆，git 仓库=工程真源，两者语义不同层。本班全部工程知识
已双写：仓库侧=设计稿+裁定记录（本文件），记忆侧=factory-backend-shift-20260914.md。

## 附：100% AI 开发治理发现（研究对照，含一条宪法级建议=留 Owner）

多智能体编码社区的 2026 共识（AugmentCode 六协调模式/VS Code 多智能体/ Simon Willison
并行智能体实践/Vibe Kanban）：**worktree 每会话隔离是标准答案**，共享工作树直改是公认
事故源。对照本项目：宪法（worktree 隔离施工默认条款）本就规定 worktree 隔离为**默认**，但实践中
多会话（含本班）走 `--allow-non-worktree` 直改主区降级通道——本次 5 文件跨会话改写、
docs/_working 文件被删、热文件四连坏，全部属于同一事故类：**共享工作树上的无锁直改**。

**建议（宪法级，留 Owner 裁定，本班不擅改）**：重申 worktree 默认纪律，或将"降级直改"
从自由裁量改为显式申请制（登记降级原因+自动计数+周审计）。机械执行可复用现有
register_*_task.ps1/审计基建，无需新系统。

## 检索来源

- 因子挖掘：arxiv.org/abs/2502.16789（AlphaAgent, KDD）；ojs.aaai.org/index.php/AAAI/article/view/37069（AlphaMuse）；arxiv.org/abs/2505.11122；arxiv.org/abs/2508.06312（Chain-of-Alpha）；arxiv.org/abs/2406.18394（AlphaForge）；openreview.net/pdf?id=d97Q8r7ZKZ（FAFM）；github.com/Sasha-Cui/Awesome-Applied-Agents-for-Investment；github.com/nshen7/alpha-gfn
- 多智能体治理：augmentcode.com/guides/how-to-run-a-multi-agent-coding-workspace；code.visualstudio.com/blogs/2026/02/05/multi-agent-development；simonwillison.net/2025/Oct/5/parallel-coding-agents/；Vibe Kanban（vibekanban.com）
- Ollama 部署：github.com/ollama/ollama/issues/10713；docs.ollama.com/windows；coretechnologies.com/products/AlwaysUp/Apps/OllamaWindowsService.html；dev.to/coderberry（Task Scheduler 方案）


---

# 复盘调查（2026-09-15 补）：FRONTEND-MAP/SCHEMA-FILE-EXISTS 回归指控全链取证

> 触发：Owner 驳回"自愈"结论，令补全调查与修复。结论：**两案均无主干损害、零代码修复**，
> 但调查揪出真根因（在途重组批制造的幻影违规）+ 我前轮取证方法的一处错误（诚实更正）。

## 取证链（全部机械验证）

1. **FRONTEND-MAP 4 fail**：`check_frontend_map.py` 当前 fail=0；depgraph 里 MOD-SIG-145
   已登（design/planned）、MOD-SIG-147 已 production/stable。定性=**depgraph 注册滞后窗口期
   的瞬时违规**，归属会话（图形/前端班）已在 PG 侧自愈，无 git 侧动作需要。
2. **SCHEMA-FILE-EXISTS 63 悬空（真正的根因在这）**：
   - 暂存区/HEAD 版 business_data_categories.yaml 指向平铺路径
     （schemas/categories/market_cb_iv.py 等 63 条）；
   - 工作区磁盘上这些平铺文件**已被移走**（未提交的 D：chinfra/datagov 在途重组批
     ——schema 文件按域搬子目录 market/、backtest/ 等，注册表改路径同批未提交）；
   - 因此任何"拿提交版注册表对**脏工作区磁盘**验存在"的扫描都会看见 63 条幻影悬空；
     纯 HEAD 检出下 63 条全部解析成功（HEAD 同时有旧注册表+旧平铺文件，自洽）。
   - 实锤：平铺路径磁盘不存在 + market/market_cb_iv.py 存在 + 新子目录整批在位。
3. **我前轮的取证错误（诚实更正）**：昨日"已自愈"结论用了工作区扫描（177 品类 0 悬空）
   ——扫对了结果、扫错了原因：那 0 悬空是重组批**改了注册表路径**的半成品状态，不是修复。
   教训固化：**registry-vs-disk 类核查必须指明基准（HEAD/index/工作区）并三态分开判**。

## 裁定（维持并升级）

1. **零代码修复**——HEAD 上没有任何东西坏；修"幻影"=破坏在途重组批（抢笔）。
2. **流程规则（本次真正落地的修复）**：registry-vs-disk 类回归/门禁核查必须跑在
   干净 HEAD 检出（或 worktree）上，禁用共享脏工作区作存在性基准；报告方复核顺序=
   当前 HEAD 复核 → 基准三态判定 → 再升级。
3. **移交 chinfra/重组批的一条交接注意**：schema 文件搬家后必须同批更新全部消费端
   import（已知消费端：MOD-BT-091 hypothesis_precheck / MOD-BT-095 apply_ddl 按
   `schemas.categories.backtest_hypothesis_precheck` 导入——搬家后须改
   `schemas.categories.backtest.backtest_hypothesis_precheck`，否则落地瞬间打断
   E2 预审管线；按 trae_052 跨蓝图变更通知义务执行）。


---

# 附：裁定落地记录（2026-09-15）

worktree 宪法级建议 **Owner 已采纳**：AGENTS.md §RULE-WORKTREE 两处等长修正（隔离=默认，
降级=显式申请制）+ parallel_session_coordination_policy.md v1.1.0 新增 §10 申请制三件
（登记原因/GW 标记自动计数/周审计）。智能体挖矿轨立项书全批（P2 全启用——成本核为零 token 后 Owner 撤销开关），
方法论强制=施工SOP+挖矿SOP 双走（矿机自身先被挖矿挖透）。详见立项书附二。
